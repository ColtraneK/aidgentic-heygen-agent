#!/usr/bin/env python3
"""Lay a music bed under the finish, ducked under the voice.

  python3 music.py WORK --music URL_OR_FILE [--level 0.22]
  python3 music.py WORK --off

The track is looped or trimmed to the video, faded in and out, and pushed down
whenever the narration speaks. build.py picks up WORK/project/assets/music.m4a
on the next build. swap.py re-fits it when a new line changes the length.
"""
import argparse, json, os, re, shutil, subprocess, urllib.request

def mix(work, level=None):
    assets = os.path.join(work, "project", "assets")
    src, out = os.path.join(assets, "music-src.m4a"), os.path.join(assets, "music.m4a")
    cfg_path = os.path.join(work, "music.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    if level is not None:
        cfg["level"] = level
    level = cfg.setdefault("level", 0.22)
    json.dump(cfg, open(cfg_path, "w"), indent=2)
    dur = json.load(open(os.path.join(work, "scenes.json")))["duration"]
    fade_out = max(dur - 1.5, 0)
    narration = os.path.join(assets, "narration.m4a")
    bed = f"[0:a]atrim=0:{dur:.3f},asetpts=N/SR/TB,volume={level},afade=t=in:d=0.6,afade=t=out:st={fade_out:.3f}:d=1.5"
    if os.path.exists(narration):
        # Sidechain: the voice pushes the music down while it speaks.
        graph = f"{bed}[m];[m][1:a]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[out]"
        cmd = ["-stream_loop", "-1", "-i", src, "-i", narration, "-filter_complex", graph, "-map", "[out]"]
    else:
        cmd = ["-stream_loop", "-1", "-i", src, "-filter_complex", f"{bed}[out]", "-map", "[out]"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *cmd, "-t", f"{dur:.3f}", "-ac", "2", "-ar", "48000",
                    "-c:a", "aac", "-b:a", "160k", out], check=True)
    print(f"music bed: {dur:.2f}s at level {level}, ducked under the voice -> {out}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--music", help="the track: a URL (e.g. from HeyGen's search_audio_sounds) or a local file")
    ap.add_argument("--level", type=float, help="music volume before ducking, 0 to 1 (default 0.22)")
    ap.add_argument("--off", action="store_true", help="remove the music bed")
    a = ap.parse_args()
    work = os.path.abspath(a.work)
    assets = os.path.join(work, "project", "assets")
    if a.off:
        for f in ("music-src.m4a", "music.m4a"):
            if os.path.exists(os.path.join(assets, f)):
                os.remove(os.path.join(assets, f))
        print("music bed removed; rebuild to drop it from the cut")
        return
    if a.music:
        raw = os.path.join(work, "music-download")
        if re.match(r"https?://", a.music):
            with urllib.request.urlopen(a.music) as r, open(raw, "wb") as f:
                shutil.copyfileobj(r, f)
        else:
            shutil.copy(a.music, raw)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-vn", "-ac", "2", "-ar", "48000",
                        "-c:a", "aac", "-b:a", "192k", os.path.join(assets, "music-src.m4a")], check=True)
        os.remove(raw)
    if not os.path.exists(os.path.join(assets, "music-src.m4a")):
        raise SystemExit("no track yet: pass --music URL_OR_FILE")
    mix(work, a.level)

if __name__ == "__main__":
    main()
