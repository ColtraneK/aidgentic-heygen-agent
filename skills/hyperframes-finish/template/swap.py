#!/usr/bin/env python3
"""Swap one scene of a finished cut, without re-rendering anything in HeyGen.

Two kinds of fix:

  Picture only (b-roll, a scene clip): the new clip replaces scene N's picture.
  The narration and every timing stay as they are; the clip is cropped to fill
  the frame and looped or trimmed to the scene's length.

    python3 swap.py WORK --scene 3 --video URL_OR_FILE

  A new line (--line): the new clip brings its own voice (for a graphics-only
  scene, an audio file is enough). Its picture and
  sound replace scene N, the narration is re-spliced, and everything after the
  scene moves by the difference in length: later scenes, finish.json timings
  and the captions. Pass the new clip's captions with --subs to caption it.

    python3 swap.py WORK --scene 4 --video URL_OR_FILE --line [--subs URL_OR_FILE]

The previous files are kept in WORK/before-swap-N/. Rebuild with build.py and
re-render after a swap; for --line, re-time the overlays inside scene N.
"""
import argparse, json, os, re, shutil, subprocess, sys, urllib.request

def run(cmd):
    return subprocess.run(cmd, check=True, text=True, capture_output=True)

def get(src, path):
    if re.match(r"https?://", src):
        with urllib.request.urlopen(src) as r, open(path, "wb") as f:
            shutil.copyfileobj(r, f)
    else:
        shutil.copy(src, path)

def probe_dur(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout)

def ts(s):
    h, m, rest = s.split(":"); sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000

def fmt(t):
    t = max(t, 0); ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

def read_srt(path):
    cues = []
    for blk in open(path).read().strip().split("\n\n"):
        lines = blk.strip().split("\n")
        if len(lines) >= 3 and " --> " in lines[1]:
            a, b = lines[1].split(" --> ")
            cues.append([ts(a), ts(b), "\n".join(lines[2:])])
    return cues

def write_srt(path, cues):
    with open(path, "w") as f:
        for k, (a, b, text) in enumerate(cues, 1):
            f.write(f"{k}\n{fmt(a)} --> {fmt(b)}\n{text}\n\n")

def shift(node, after, delta):
    """Move every time at or after `after` by `delta`, anywhere in finish.json."""
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool) and (k in ("start", "end") or k == "at" or k.endswith("At")):
                if v >= after - 1e-3:
                    node[k] = round(v + delta, 3)
            else:
                shift(v, after, delta)
    elif isinstance(node, list):
        for v in node:
            shift(v, after, delta)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--scene", type=int, required=True, help="1-based scene number from scenes.json")
    ap.add_argument("--video", required=True, help="the new clip: a URL or a local file")
    ap.add_argument("--line", action="store_true", help="the clip is a new spoken line; use its sound and timing")
    ap.add_argument("--subs", help="captions for the new line (.srt), with --line")
    a = ap.parse_args()

    work = os.path.abspath(a.work)
    proj = os.path.join(work, "project")
    scn = json.load(open(os.path.join(work, "scenes.json")))
    sc = next((s for s in scn["scenes"] if s["n"] == a.scene), None)
    if not sc:
        raise SystemExit(f"no scene {a.scene}; scenes.json has 1 to {len(scn['scenes'])}")
    old_len = sc["end"] - sc["start"]
    if sc["kind"] == "graphic" and not a.line:
        raise SystemExit(f"scene {a.scene} is graphics only, so it has no clip to swap. Edit its overlay in finish.json.")

    keep = os.path.join(work, f"before-swap-{a.scene}")
    os.makedirs(keep, exist_ok=True)
    for f in ["scenes.json", "finish.json", scn["subs"], os.path.join("project", sc.get("clip") or "-"),
              os.path.join("project", "assets", "narration.m4a"), os.path.join("project", "assets", "music.m4a")]:
        p = os.path.join(work, f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(keep, os.path.basename(f)))

    raw = os.path.join(work, f"swap-{a.scene}-src.mp4")
    get(a.video, raw)
    new_len = probe_dur(raw) if a.line else old_len

    # A graphics-only scene takes just the new voice; its picture is drawn by the finish.
    # Avatar scenes sit in a 1080x864 card; anything else fills the 1080x1920 frame.
    # Crop to cover, keeping the top of the frame where faces usually are.
    W, H = (1080, 864) if sc["kind"] == "avatar" else (1080, 1920)
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
          f"crop={W}:{H}:(iw-{W})/2:(ih-{H})*{0.3 if sc['kind'] == 'avatar' else 0.5}")
    if sc.get("clip"):
        run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", raw, "-t", f"{new_len:.3f}", "-an",
             "-vf", vf, "-r", "30", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
             os.path.join(proj, sc["clip"])])

    if a.line:
        delta = round(new_len - old_len, 3)
        nar = os.path.join(proj, "assets", "narration.m4a")
        old_nar = os.path.join(keep, "narration.m4a")
        parts = []
        for k, (args, inp) in enumerate([(["-t", f"{sc['start']}"], old_nar), ([], raw),
                                         (["-ss", f"{sc['end']}"], old_nar)]):
            if (k == 0 and sc["start"] <= 0) or (k == 2 and sc["end"] >= scn["duration"] - 0.01):
                continue
            p = os.path.join(work, f"swap-part{k}.wav")
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", inp, *args, "-vn", "-ac", "2", "-ar", "48000", p])
            parts.append(p)
        lst = os.path.join(work, "swap-parts.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
             "-c:a", "aac", "-b:a", "192k", nar])

        subs_path = os.path.join(work, scn["subs"])
        cues = [c for c in read_srt(subs_path) if not (sc["start"] - 1e-3 <= c[0] < sc["end"])]
        for c in cues:
            if c[0] >= sc["end"] - 1e-3:
                c[0] += delta; c[1] += delta
        if a.subs:
            tmp = os.path.join(work, f"swap-{a.scene}.srt")
            get(a.subs, tmp)
            cues += [[sc["start"] + x, sc["start"] + min(y, new_len), t] for x, y, t in read_srt(tmp)]
        write_srt(subs_path, sorted(cues))

        old_end = sc["end"]
        for s in scn["scenes"]:
            if s["n"] == a.scene:
                s["end"] = round(s["start"] + new_len, 3)
            elif s["start"] >= old_end - 1e-3:
                s["start"] = round(s["start"] + delta, 3); s["end"] = round(s["end"] + delta, 3)
        scn["duration"] = round(scn["duration"] + delta, 3)
        fin_path = os.path.join(work, "finish.json")
        if os.path.exists(fin_path):
            fin = json.load(open(fin_path))
            shift(fin, old_end, delta)
            json.dump(fin, open(fin_path, "w"), indent=2)
        json.dump(scn, open(os.path.join(work, "scenes.json"), "w"), indent=2)
        for p in parts + [lst]:
            os.remove(p)
        if os.path.exists(os.path.join(proj, "assets", "music-src.m4a")):
            # The video got longer or shorter, so re-fit the music bed to it.
            sys.dont_write_bytecode = True
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import music
            music.mix(work)
        print(f"scene {a.scene}: {old_len:.2f}s -> {new_len:.2f}s; later scenes moved {delta:+.2f}s; "
              f"total {scn['duration']:.2f}s. Re-time the overlays inside scene {a.scene} in finish.json.")
    else:
        print(f"scene {a.scene}: picture replaced, {old_len:.2f}s, timings unchanged.")
    os.remove(raw)

if __name__ == "__main__":
    main()
