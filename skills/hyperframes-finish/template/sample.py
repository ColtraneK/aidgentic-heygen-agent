#!/usr/bin/env python3
"""Preview the three motion styles in someone's brand, before any video exists.

  python3 sample.py OUT --name "Brand" --bg "#101418" --fg "#ffffff" --accent "#3b82f6" \
      [--on-accent "#ffffff"] [--logo URL] [--heading-font Inter] [--mono-font "Geist Mono"] \
      [--headline "Two short lines|from their site"] [--number "1,250"] [--label "customers"] \
      [--pills "Two things|they offer"]
  python3 sample.py OUT ... --look LOOK.css [--style clean]     one frame in a look made from their references


Builds one graphics-only frame per style (Bold, Clean, Editorial) with a
headline and a number from their own site, snapshots each, and writes
OUT/style-bold.png, style-clean.png, style-editorial.png and, side by side,
OUT/styles.jpg. Nothing touches HeyGen.
"""
import argparse, glob, json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
from prep import install_assets

HF = ["npx", "--yes", "hyperframes@0.8.115"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--name", required=True)
    ap.add_argument("--bg", required=True)
    ap.add_argument("--fg", required=True)
    ap.add_argument("--accent", required=True)
    ap.add_argument("--on-accent")
    ap.add_argument("--logo")
    ap.add_argument("--heading-font", default="Inter")
    ap.add_argument("--mono-font", default="Geist Mono")
    ap.add_argument("--headline", default="Your words,|in motion.", help="two lines split by |")
    ap.add_argument("--number", default="1,250")
    ap.add_argument("--label", default="a number from your site")
    ap.add_argument("--pills", default="", help="up to three short words from their site, split by |")
    ap.add_argument("--look", help="a look's CSS file: preview just that look, over --style")
    ap.add_argument("--style", default="clean", help="with --look: the base style it moves like")
    a = ap.parse_args()

    work = os.path.abspath(a.out)
    os.makedirs(work, exist_ok=True)
    fonts, logo, plate = install_assets(work, a.logo, a.heading_font, a.mono_font)
    dur = 4.6
    json.dump({"duration": dur, "scenes": [{"n": 1, "start": 0, "end": dur, "kind": "graphic", "clip": None}],
               "fonts": fonts, "logo": logo, "logoPlate": plate, "subs": None},
              open(os.path.join(work, "scenes.json"), "w"), indent=2)
    lines = [x.strip() for x in a.headline.split("|") if x.strip()][:2]
    last = len(lines) - 1
    json.dump({"brand": {"name": a.name, "bg": a.bg, "fg": a.fg, "accent": a.accent, "onAccent": a.on_accent or a.bg},
               "captionScenes": [],
               **({"look": {"name": "look", "css": os.path.abspath(a.look)}} if a.look else {}),
               "overlays": [
                   {"type": "headline", "start": 0, "end": dur, "size": "big",
                    "lines": [{"text": t, "at": 0.15 + 0.7 * k, "step": 0.12} for k, t in enumerate(lines)],
                    "emphasize": {"line": last, "word": len(lines[last].split()) - 1, "at": 1.4}},
                   {"type": "counter", "start": 0.6, "end": dur, "value": a.number, "label": a.label, "at": 1.0,
                    "pills": [{"text": t.strip(), "at": 2.4 + 0.3 * k} for k, t in enumerate(a.pills.split("|")[:3]) if t.strip()]}]},
              open(os.path.join(work, "finish.json"), "w"), indent=2)

    shots = []
    for style in ((a.style,) if a.look else ("bold", "clean", "editorial")):
        subprocess.run([sys.executable, os.path.join(HERE, "build.py"), work, "--style", style], check=True)
        snaps = os.path.join(work, "project", "snapshots")
        shutil.rmtree(snaps, ignore_errors=True)
        subprocess.run(HF + ["snapshot", "--at", "4.2", "--no-end", "--describe", "false"],
                       cwd=os.path.join(work, "project"), check=True, capture_output=True)
        png = sorted(glob.glob(os.path.join(snaps, "frame-*.png")))[0]
        dest = os.path.join(work, "look.png" if a.look else f"style-{style}.png")
        shutil.copy(png, dest)
        shots.append(dest)
    if a.look:
        print(f"wrote {work}/look.png")
        return
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *sum((["-i", p] for p in shots), []), "-filter_complex",
                    "[0]scale=540:960[a];[1]scale=540:960[b];[2]scale=540:960[c];[a][b][c]hstack=3",
                    "-q:v", "3", os.path.join(work, "styles.jpg")], check=True)
    print(f"wrote {work}/styles.jpg (left to right: Bold, Clean, Editorial) and one PNG per style")

if __name__ == "__main__":
    main()
