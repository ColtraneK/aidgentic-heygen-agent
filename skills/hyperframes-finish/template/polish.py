#!/usr/bin/env python3
"""The last pass on a rendered finish: sound effects, then the speed.

  python3 polish.py WORK --in finish.mp4 --out final.mp4
  python3 polish.py WORK --in finish.mp4 --out final.mp4 --speed 1.1
  python3 polish.py WORK --sound pop=URL_OR_FILE [--sound whoosh=...]   swap in a sound, then polish as usual
  python3 polish.py WORK --in finish.mp4 --stems OUTDIR                  the parts, for someone finishing it in an editor

Sound effects come from WORK/sfx-cues.json, which build.py writes on every
build: a whoosh on each cut and screen recording, a pop when a word, chip or
tick lands, a click on each click, a chime on a check, the result and the logo.
Run polish.py straight after rendering each cut, because each opening has its
own cues. The sounds live in WORK/sfx/. Any that are missing are made here
from scratch; --sound replaces one with a file or URL, such as one from
HeyGen's sound library.

The speed comes from --speed, else finish.json's "speed", else 1. It speeds up
picture and voice together without changing the pitch: 1.1 sounds natural for a
voice clone that reads slowly. finish.json's "sfx": "off" leaves sounds out.

--stems writes the pieces separately, at the render's own speed, for anyone who
would rather do the sound, music and timing themselves: the picture with no
sound, the voice, the music bed, the sound effects alone, and the captions.
"""
import argparse, array, json, os, re, shutil, subprocess, urllib.request

SOUNDS = ("whoosh", "pop", "click", "chime")

# Made from scratch so the finish never depends on a download. Each is short and quiet.
SYNTH = {
    "pop": ["-f", "lavfi", "-i", "aevalsrc='0.7*sin(2*PI*(420+1600*exp(-t*38))*t)*exp(-t*30)':s=48000:d=0.16"],
    "click": ["-f", "lavfi", "-i", "aevalsrc='(0.55*sin(2*PI*2400*t)+0.35*sin(2*PI*5200*t))*exp(-t*260)':s=48000:d=0.05"],
    "chime": ["-f", "lavfi", "-i", "aevalsrc='0.32*sin(2*PI*1318.5*t)*exp(-t*4.2)+0.22*sin(2*PI*1975.5*t)*exp(-t*5.5)+0.1*sin(2*PI*2637*t)*exp(-t*7)':s=48000:d=1.1"],
    "whoosh": ["-f", "lavfi", "-i", "anoisesrc=d=0.6:c=pink:r=48000:a=0.6",
               "-af", "highpass=f=350,lowpass=f=4500,afade=t=in:d=0.36:curve=exp,afade=t=out:st=0.36:d=0.24:curve=exp"],
}

def run(cmd):
    return subprocess.run(cmd, check=True, text=True, capture_output=True)

def sound_path(work, name):
    return os.path.join(work, "sfx", f"{name}.wav")

def set_sound(work, name, src):
    """Replace one sound with a file or URL, normalised to a short mono WAV."""
    os.makedirs(os.path.join(work, "sfx"), exist_ok=True)
    raw = src
    if re.match(r"https?://", src):
        raw = os.path.join(work, "sfx", f"{name}-download")
        with urllib.request.urlopen(src) as r, open(raw, "wb") as f:
            shutil.copyfileobj(r, f)
    # Trim the silence at the start and anything past two seconds.
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-t", "2", "-af",
         "silenceremove=start_periods=1:start_threshold=-50dB,afade=t=out:st=1.7:d=0.3",
         "-ac", "1", "-ar", "48000", sound_path(work, name)])
    if raw != src:
        os.remove(raw)
    print(f"sound {name}: {src}")

def ensure_sounds(work):
    os.makedirs(os.path.join(work, "sfx"), exist_ok=True)
    for name in SOUNDS:
        if not os.path.exists(sound_path(work, name)):
            run(["ffmpeg", "-y", "-loglevel", "error", *SYNTH[name], "-ac", "1", "-ar", "48000", sound_path(work, name)])

def peak(path):
    """Seconds from the start of a sound to its loudest moment, so that moment lands on the cue."""
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", "8000", "-"],
                         check=True, capture_output=True).stdout
    a = array.array("h", pcm)
    if not a:
        return 0.0
    i = max(range(len(a)), key=lambda k: abs(a[k]))
    return i / 8000

def stems(work, inp, outdir):
    os.makedirs(outdir, exist_ok=True)
    assets = os.path.join(work, "project", "assets")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", inp, "-an", "-c:v", "copy", os.path.join(outdir, "picture (no sound).mp4")])
    made = ["picture (no sound).mp4"]
    for src, name in (("narration.m4a", "voice.m4a"), ("music.m4a", "music.m4a")):
        if os.path.exists(os.path.join(assets, src)):
            shutil.copy(os.path.join(assets, src), os.path.join(outdir, name))
            made.append(name)
    cues_path = os.path.join(work, "sfx-cues.json")
    cues = json.load(open(cues_path, encoding="utf-8"))["cues"] if os.path.exists(cues_path) else []
    if cues:
        ensure_sounds(work)
        dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", inp]).stdout)
        ins, graph = [], []
        for k, c in enumerate(cues):
            ins += ["-i", sound_path(work, c["sound"])]
            ms = max(0, int((c["at"] - peak(sound_path(work, c["sound"]))) * 1000))
            graph.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms},volume={c['volume']}[s{k}]")
        graph.append("".join(f"[s{k}]" for k in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,apad=whole_dur={dur:.3f}[out]")
        run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(graph), "-map", "[out]", "-t", f"{dur:.3f}",
             os.path.join(outdir, "sound effects.wav")])
        made.append("sound effects.wav")
    subs = os.path.join(work, json.load(open(os.path.join(work, "scenes.json"), encoding="utf-8")).get("subs") or "subs.srt")
    if os.path.exists(subs):
        shutil.copy(subs, os.path.join(outdir, "captions.srt"))
        made.append("captions.srt")
    print(f"stems in {outdir}: {', '.join(made)} (at the render's own speed; the picture already has its captions drawn in)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("--in", dest="inp", help="the rendered cut, e.g. WORK/finish.mp4")
    ap.add_argument("--out", help="where the polished cut goes")
    ap.add_argument("--speed", type=float, help="1 is as rendered; 1.05 to 1.15 for a slow voice")
    ap.add_argument("--stems", metavar="OUTDIR", help="write the picture, voice, music, sound effects and captions separately")
    ap.add_argument("--sound", action="append", default=[], metavar="NAME=URL_OR_FILE",
                    help=f"replace a sound: one of {', '.join(SOUNDS)}")
    a = ap.parse_args()
    work = os.path.abspath(a.work)

    for s in a.sound:
        name, _, src = s.partition("=")
        if name not in SOUNDS or not src:
            raise SystemExit(f"--sound takes NAME=URL_OR_FILE, with NAME one of {', '.join(SOUNDS)}")
        set_sound(work, name, src)
    if not a.inp:
        if a.sound:
            return
        raise SystemExit("pass --in and --out")
    if a.stems:
        return stems(work, a.inp, a.stems)
    if not a.out:
        raise SystemExit("pass --out")

    fin = json.load(open(os.path.join(work, "finish.json"), encoding="utf-8"))
    speed = a.speed or float(fin.get("speed", 1) or 1)
    if not 0.5 <= speed <= 2:
        raise SystemExit("speed must be between 0.5 and 2")
    cues_path = os.path.join(work, "sfx-cues.json")
    cues = []
    if str(fin.get("sfx", "auto")).lower() != "off":
        if not os.path.exists(cues_path):
            raise SystemExit("no sfx-cues.json: run build.py first")
        cues = json.load(open(cues_path, encoding="utf-8"))["cues"]

    inputs, graph = ["-i", a.inp], []
    if cues:
        ensure_sounds(work)
        used = sorted({c["sound"] for c in cues})
        for k, name in enumerate(used, start=1):
            inputs += ["-i", sound_path(work, name)]
            group = [c for c in cues if c["sound"] == name]
            off = peak(sound_path(work, name))
            outs = "".join(f"[{name}{j}]" for j in range(len(group)))
            graph.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit={len(group)}{outs}" if len(group) > 1
                         else f"[{k}:a]aformat=sample_rates=48000:channel_layouts=stereo[{name}0]")
            for j, c in enumerate(group):
                ms = max(0, int((c["at"] - off) * 1000))
                graph.append(f"[{name}{j}]adelay={ms}|{ms},volume={c['volume']}[{name}d{j}]")
        mixed = "".join(f"[{c}d{j}]" for c in used for j in range(sum(1 for x in cues if x["sound"] == c)))
        graph.append(f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo[main]")
        graph.append(f"[main]{mixed}amix=inputs={len(cues) + 1}:normalize=0:duration=first[mix]")
        audio = "[mix]"
    else:
        graph.append("[0:a]anull[mix]")
        audio = "[mix]"
    if speed != 1:
        graph.append(f"[0:v]setpts=PTS/{speed}[v]")
        graph.append(f"{audio}atempo={speed}[au]")
        vmap, amap = "[v]", "[au]"
    else:
        vmap, amap = "0:v", audio
    vcodec = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30"] if speed != 1 else ["-c:v", "copy"]
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(graph), "-map", vmap, "-map", amap,
         *vcodec, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out])
    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.out]).stdout)
    print(f"polished: {len(cues)} sound effects, speed {speed}, {dur:.1f}s -> {a.out}")

if __name__ == "__main__":
    main()
