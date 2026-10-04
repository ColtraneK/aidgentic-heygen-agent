#!/usr/bin/env python3
"""Prepare a HeyGen Studio render for the HyperFrames finish.

Downloads the render and its subtitle file, finds the scene cuts, cuts one clip
per scene (avatar scenes are cropped out of their letterbox), extracts the
narration, and installs GSAP, the brand fonts and the logo locally. The
renderer's headless Chrome can't reach CDNs, so everything must be local.

Usage:
  python3 prep.py --video URL --subs URL --avatar 1,4,8 [--graphic 5] --out WORKDIR \
      [--logo URL] [--heading-font "Inter"] [--mono-font "Geist Mono"]

--avatar lists the presenter's talking beats and --graphic the graphics-only
beats (a plain plate in the render), by 1-based scene number. Everything else
is b-roll.

Writes WORKDIR/project/assets/* and WORKDIR/scenes.json.
"""
import argparse, json, os, re, shutil, subprocess, urllib.request

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)

def fetch(url, path):
    with urllib.request.urlopen(url) as r, open(path, "wb") as f:
        shutil.copyfileobj(r, f)

def kebab(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def install_font(family, weights, work, assets):
    """Copy latin woff2 files for a Google font from @fontsource. Returns the family used."""
    pkg = f"@fontsource/{kebab(family)}"
    try:
        run(["npm", "i", "--silent", "--prefix", work, pkg])
    except subprocess.CalledProcessError:
        if family == "Inter":
            raise
        print(f"font {family!r} not on @fontsource, falling back to Inter")
        return install_font("Inter", weights, work, assets)
    src = os.path.join(work, "node_modules", pkg, "files")
    os.makedirs(os.path.join(assets, "fonts"), exist_ok=True)
    got = []
    for w in weights:
        f = f"{kebab(family)}-latin-{w}-normal.woff2"
        if os.path.exists(os.path.join(src, f)):
            shutil.copy(os.path.join(src, f), os.path.join(assets, "fonts", f))
            got.append(w)
    return {"family": family, "file_prefix": kebab(family), "weights": got}

def install_assets(work, logo_url, heading_font, mono_font):
    """GSAP, the brand fonts and the logo, all local. Returns (fonts, logo path, logo plate)."""
    assets = os.path.join(work, "project", "assets")
    os.makedirs(assets, exist_ok=True)
    run(["npm", "i", "--silent", "--prefix", work, "gsap@3"])
    shutil.copy(os.path.join(work, "node_modules", "gsap", "dist", "gsap.min.js"), assets)
    fonts = {"heading": install_font(heading_font, [500, 600, 700, 800, 900], work, assets),
             "mono": install_font(mono_font, [500, 700], work, assets)}
    logo = None
    if logo_url:
        ext = os.path.splitext(logo_url.split("?")[0])[1] or ".png"
        logo = f"assets/logo{ext}"
        fetch(logo_url, os.path.join(work, "project", logo))
    # A dark logo vanishes on a dark background: measure it over black and
    # give it a light plate when it reads dark. Check the result in a snapshot.
    plate = "none"
    if logo:
        stats = subprocess.run(["ffmpeg", "-hide_banner", "-f", "lavfi", "-i", "color=black:s=64x64", "-i",
                                os.path.join(work, "project", logo), "-filter_complex",
                                "[1]scale=64:64[l];[0][l]overlay,signalstats,metadata=print", "-frames:v", "1",
                                "-f", "null", "-"], text=True, capture_output=True).stderr
        m = re.search(r"YAVG=([0-9.]+)", stats)
        if m and float(m.group(1)) < 60:
            plate = "light"
    return fonts, logo, plate

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--subs", required=True)
    ap.add_argument("--avatar", default="", help="1-based scene numbers that are avatar beats")
    ap.add_argument("--graphic", default="", help="1-based scene numbers that are graphics-only beats")
    ap.add_argument("--out", required=True)
    ap.add_argument("--logo")
    ap.add_argument("--heading-font", default="Inter")
    ap.add_argument("--mono-font", default="Geist Mono")
    ap.add_argument("--threshold", type=float, default=0.3)
    a = ap.parse_args()

    work = os.path.abspath(a.out)
    assets = os.path.join(work, "project", "assets")
    os.makedirs(assets, exist_ok=True)
    render = os.path.join(work, "render.mp4")
    fetch(a.video, render)
    fetch(a.subs, os.path.join(work, "subs.srt"))

    dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", render]).stdout)
    w, h = map(int, run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", render]).stdout.strip().split(","))
    det = subprocess.run(["ffmpeg", "-hide_banner", "-i", render, "-vf", f"select='gt(scene,{a.threshold})',showinfo",
                          "-an", "-f", "null", "-"], text=True, capture_output=True).stderr
    cuts = [0.0] + [float(x) for x in re.findall(r"pts_time:([0-9.]+)", det)] + [dur]
    avatar = {int(x) for x in a.avatar.split(",") if x.strip()}
    graphic = {int(x) for x in a.graphic.split(",") if x.strip()}

    # A landscape look in a portrait Studio render sits in a centred 16:9 strip.
    strip_h = round(w * 9 / 16 / 2) * 2
    strip_y = (h - strip_h) // 2
    card_w = round(strip_h * 1.25 / 2) * 2
    scenes = []
    for i in range(1, len(cuts)):
        s, e = cuts[i - 1], cuts[i]
        clip = f"s{i}.mp4"
        kind = "avatar" if i in avatar else "graphic" if i in graphic else "broll"
        if kind == "graphic":
            # Nothing from the render shows: the finish draws the whole frame.
            scenes.append({"n": i, "start": round(s, 3), "end": round(e, 3), "kind": kind, "clip": None})
            continue
        if kind == "avatar":
            vf = f"crop={w}:{strip_h}:0:{strip_y},crop={card_w}:{strip_h}:{(w - card_w)//2}:0,scale=1080:864:flags=lanczos"
        else:
            vf = "scale=1080:1920"
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{s}", "-i", render, "-t", f"{e - s:.3f}", "-an", "-vf", vf,
             "-r", "30", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", os.path.join(assets, clip)])
        scenes.append({"n": i, "start": round(s, 3), "end": round(e, 3), "kind": kind, "clip": f"assets/{clip}"})
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", render, "-vn", "-c:a", "aac", "-b:a", "192k",
         os.path.join(assets, "narration.m4a")])

    fonts, logo, plate = install_assets(work, a.logo, a.heading_font, a.mono_font)
    out = {"duration": round(dur, 3), "scenes": scenes, "fonts": fonts, "logo": logo, "logoPlate": plate, "subs": "subs.srt"}
    json.dump(out, open(os.path.join(work, "scenes.json"), "w"), indent=2)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
