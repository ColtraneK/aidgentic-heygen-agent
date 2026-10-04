#!/usr/bin/env python3
"""Build the HyperFrames composition for the finish.

Reads WORK/scenes.json (from prep.py) and WORK/finish.json (brand + overlays,
written per video), and writes WORK/project/index.html plus the project files.

Usage:
  python3 build.py WORKDIR                 the main cut
  python3 build.py WORKDIR --hook B        the same cut with opening "B" from finish.json's hooks
  python3 build.py WORKDIR --style clean   override finish.json's style (bold, clean, editorial)
  python3 build.py WORKDIR --cover         also write WORK/cover/, a one-frame cover for the post
  python3 build.py WORKDIR --guides        tint the areas Reels, TikTok and Shorts cover with their buttons
                                           and captions, for checking the preview sheet. Rebuild without it to render.

It also writes WORK/preview-times.txt: the moment each overlay has fully landed,
plus every scene without one, for the preview sheet, and WORK/sfx-cues.json:
where each sound effect lands, for polish.py.
"""
import argparse, hashlib, html, json, os, re, shutil, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("work")
ap.add_argument("--hook")
ap.add_argument("--style")
ap.add_argument("--cover", action="store_true")
ap.add_argument("--guides", action="store_true")
args = ap.parse_args()
work = os.path.abspath(args.work)
proj = os.path.join(work, "project")
scn = json.load(open(os.path.join(work, "scenes.json"), encoding="utf-8"))
fin = json.load(open(os.path.join(work, "finish.json"), encoding="utf-8"))
brand = fin["brand"]
TOTAL = scn["duration"]
scenes = scn["scenes"]

# Three motion styles. Bold pops and flashes; Clean drops the bounce, spin and
# flash; Editorial is calmer still, with underlines instead of highlight blocks.
STYLE = (args.style or fin.get("style", "bold")).lower()
STY = {"bold": {"flash": 0.45, "soften": 1.0, "ease": None, "slow": 1.0, "glow": 0.55},
       "clean": {"flash": 0.0, "soften": 0.3, "ease": "power3.out", "slow": 1.0, "glow": 0.3},
       "editorial": {"flash": 0.0, "soften": 0.15, "ease": "expo.out", "slow": 1.3, "glow": 0.2}}.get(STYLE)
if not STY:
    sys.exit(f"unknown style {STYLE!r}: use bold, clean or editorial")

overlays = fin["overlays"]
if args.hook:
    hook = next((h for h in fin.get("hooks", []) if h["name"] == args.hook), None)
    if not hook:
        sys.exit(f"no hook named {args.hook!r} in finish.json")
    # The variant's overlays replace everything that starts before it ends.
    until = hook.get("until", scenes[0]["end"])
    overlays = [o for o in overlays if o["start"] >= until - 1e-3] + hook["overlays"]
    if "captionScenes" in hook:
        fin["captionScenes"] = hook["captionScenes"]

E, T = [], []
r3 = lambda x: round(float(x), 3)
esc = html.escape

def ts(s):
    h, m, rest = s.split(":"); sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000

subs = []
subs_path = os.path.join(work, scn.get("subs") or "subs.srt")
for blk in (open(subs_path, encoding="utf-8").read().strip().split("\n\n") if os.path.exists(subs_path) else []):
    lines = blk.strip().split("\n")
    if len(lines) < 3:
        continue
    a, b = lines[1].split(" --> ")
    subs.append((ts(a), ts(b), " ".join(lines[2:])))

def scene_at(t):
    for s in scenes:
        if s["start"] <= t < s["end"]:
            return s
    return scenes[-1]

def logo_html(cls="logo"):
    if scn.get("logo"):
        plate = brand.get("logoPlate", scn.get("logoPlate", "none"))
        return f'<img class="{cls} plate-{plate}" src="{scn["logo"]}" alt="" />'
    return f'<span class="{cls} mono-logo">{esc(brand.get("name", "?")[:1])}</span>'

def words(text, cls, wid):
    parts = text.split()
    return "".join(f'<span class="w {cls}" id="{wid}{k}">{esc(p)}</span>' for k, p in enumerate(parts)), len(parts)

def tame(props):
    """Soften an entrance for the calmer styles: less scale, no spin."""
    if STYLE == "bold":
        return props
    props = re.sub(r"scale:([0-9.]+)", lambda m: f"scale:{r3(1 + (float(m.group(1)) - 1) * STY['soften'])}", props)
    return re.sub(r"rotation:-?[0-9.]+", "rotation:0", props)

def rise(wid, n, t0, step=0.07):
    frm = "y:50, opacity:0, rotation:4" if STYLE == "bold" else "y:36, opacity:0"
    ease = STY["ease"] or "back.out(2)"
    for k in range(n):
        T.append(f'tl.fromTo("#{wid}{k}", {{{frm}}}, {{y:0, opacity:1, rotation:0, duration:{r3(0.45 * STY["slow"])}, ease:"{ease}"}}, {r3(t0 + k * step)});')

def pop(sel, at, frm="scale:0.5, y:40, opacity:0", to="scale:1, y:0, opacity:1", dur=0.5, ease="back.out(2.4)"):
    if STYLE != "bold":
        frm, dur = tame(frm), r3(dur * STY["slow"])
        if ease.startswith("back") or ease.startswith("power4"):
            ease = STY["ease"]
    T.append(f'tl.fromTo("{sel}", {{{frm}}}, {{{to}, duration:{dur}, ease:"{ease}"}}, {r3(at)});')

def emphasize(sel, at):
    """One word on the accent colour: a block in Bold, coloured text in Clean, an underline in Editorial."""
    on_acc, acc = brand.get("onAccent", brand["bg"]), brand["accent"]
    if STYLE == "editorial":
        T.append(f'tl.set("{sel}", {{backgroundImage:"linear-gradient({acc},{acc})", backgroundRepeat:"no-repeat", backgroundPosition:"0 96%", backgroundSize:"0% 0.08em"}}, 0);')
        T.append(f'tl.to("{sel}", {{backgroundSize:"100% 0.08em", duration:0.45, ease:"expo.out"}}, {r3(at)});')
    elif STYLE == "clean" and acc.lower() != brand["fg"].lower():
        T.append(f'tl.to("{sel}", {{color:"{acc}", duration:0.2}}, {r3(at)});')
    else:
        T.append(f'tl.to("{sel}", {{color:"{on_acc}", backgroundColor:"{acc}", duration:0.15}}, {r3(at)});')

# Sound effects: (sound, time) cues on the render's clock, mixed in by polish.py.
# Each style hears a different amount: Bold all of them, Clean no pops on single
# words, Editorial only the quiet ones.
SFX_ON = str(fin.get("sfx", "auto")).lower() != "off"
SFX_STYLE = {"bold": {"whoosh": 0.35, "pop": 0.3, "click": 0.6, "chime": 0.35},
             "clean": {"whoosh": 0.25, "pop": 0.18, "click": 0.5, "chime": 0.3},
             "editorial": {"whoosh": 0.12, "pop": 0.0, "click": 0.4, "chime": 0.25}}[STYLE]
CUES = []

def cue(sound, at, minor=False):
    """A sound at a moment. Minor cues (single words popping in) are skipped outside Bold."""
    if minor and STYLE != "bold":
        return
    CUES.append((sound, r3(at)))

def block(eid, start, end, inner, track=5):
    E.append(f'<div id="{eid}" class="clip ov" data-start="{r3(start)}" data-duration="{r3(end - start)}" data-track-index="{track}">{inner}</div>')

# ---------- screen recordings ----------
def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", path], check=True, text=True, capture_output=True).stdout
    return tuple(int(x) for x in out.strip().split(",")[:2])

def screen(o, oid, st, en):
    """A real screen recording in a framed card that tilts in, with optional click rings,
    zooms and highlight boxes. Positions in clicks and highlights are shares (0 to 1) of
    the recording's own width and height, so they don't depend on where the card sits."""
    src = o["file"]
    want = f'{src}|{o.get("from", 0)}|{r3(en - st)}'
    name = f"assets/scr-{hashlib.sha1(want.encode()).hexdigest()[:10]}.mp4"
    out = os.path.join(proj, name)
    if not os.path.exists(out):
        # Trim to the overlay, drop the sound, make it a plain 30fps H.264 the renderer can seek.
        raw = src
        if re.match(r"https?://", src):
            raw = os.path.join(work, "screen-download")
            with urllib.request.urlopen(src) as r, open(raw, "wb") as f:
                shutil.copyfileobj(r, f)
        elif not os.path.isabs(src):
            raw = os.path.join(work, src)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f'{o.get("from", 0)}', "-i", raw, "-t", f"{en - st + 0.2:.3f}",
                        "-an", "-vf", "scale=trunc(min(iw\\,1600)/2)*2:-2:flags=lanczos", "-r", "30", "-c:v", "libx264", "-crf", "18",
                        "-preset", "fast", "-pix_fmt", "yuv420p", out], check=True)
    rw, rh = probe(out)
    pos = o.get("pos", "center")
    on_avatar = scene_at(st + 0.01)["kind"] == "avatar"
    # Room on screen, inside the apps' safe zones: the middle band, below a top graphic
    # and above the captions, or a band at the top or bottom. On an avatar beat only
    # the band above the card is free.
    max_h = 330 if on_avatar else 940 if pos == "center" else 600
    w = min(o.get("width", 880), 880)
    h = round(w * rh / rw)
    if h > max_h:
        h, w = max_h, round(max_h * rw / rh)
    left = 70 + (890 - w) // 2
    top = {"top": 220, "bottom": 1920 - 400 - h}.get("top" if on_avatar else pos, 560 + (940 - h) // 2)
    d = r3(en - st)
    E.append(f'<video id="{oid}v" class="clip scr" style="inset:auto;left:{left}px;top:{top}px;width:{w}px;height:{h}px" src="{name}" muted playsinline data-start="{r3(st)}" data-duration="{d}" data-track-index="13"></video>')
    marks = []
    for k, c in enumerate(o.get("clicks", [])):
        cx, cy = left + c["x"] * w, top + c["y"] * h
        marks.append(f'<div class="ring" id="{oid}r{k}" style="left:{round(cx - 60)}px;top:{round(cy - 60)}px"></div>')
    for k, b in enumerate(o.get("highlights", [])):
        marks.append(f'<div class="hl" id="{oid}h{k}" style="left:{round(left + b["x"] * w - 10)}px;top:{round(top + b["y"] * h - 10)}px;width:{round(b["w"] * w + 20)}px;height:{round(b["h"] * h + 20)}px"></div>')
    if marks:
        block(f"{oid}m", st, en, "".join(marks), track=14)
    tilt, dur = {"bold": (38, 0.9), "clean": (30, 0.9), "editorial": (16, 1.1)}[STYLE]
    T.append(f'tl.fromTo("#{oid}v", {{rotationX:{tilt}, y:260, opacity:0, transformPerspective:1600}}, {{rotationX:0, y:0, opacity:1, duration:{dur}, ease:"expo.out"}}, {r3(st + 0.04)});')
    T.append(f'tl.to("#{oid}v", {{opacity:0, y:-40, duration:0.25, ease:"power2.in"}}, {r3(en - 0.25)});')
    cue("whoosh", st)
    for k, c in enumerate(o.get("clicks", [])):
        if o.get("zoom", True):
            # Lean in towards the click, then settle back.
            T.append(f'tl.to("#{oid}v", {{scale:1.07, transformOrigin:"{round(c["x"] * 100)}% {round(c["y"] * 100)}%", duration:0.7, ease:"power2.inOut"}}, {r3(c["at"] - 0.7)});')
            T.append(f'tl.to("#{oid}v", {{scale:1, duration:0.6, ease:"power2.inOut"}}, {r3(min(c["at"] + 0.5, en - 0.9))});')
        T.append(f'tl.fromTo("#{oid}r{k}", {{scale:0.3, opacity:1}}, {{scale:2.4, opacity:0, duration:0.8, ease:"power2.out"}}, {r3(c["at"])});')
        cue("click", c["at"])
    for k, b in enumerate(o.get("highlights", [])):
        T.append(f'tl.fromTo("#{oid}h{k}", {{scale:1.12, opacity:0}}, {{scale:1, opacity:1, duration:0.4, ease:"back.out(2)"}}, {r3(b["at"])});')
        cue("pop", b["at"])

# ---------- scenes ----------
for s in scenes:
    i, st, d = s["n"], s["start"], r3(s["end"] - s["start"])
    if s["kind"] == "avatar":
        E.append(f'<div id="bg{i}" class="clip avbg" data-start="{st}" data-duration="{d}" data-track-index="1"></div>')
        E.append(f'<div id="glow{i}" class="clip glow" data-start="{st}" data-duration="{d}" data-track-index="2"></div>')
        E.append(f'<video id="v{i}" class="clip avvid" src="{s["clip"]}" muted playsinline data-start="{st}" data-duration="{d}" data-track-index="3"></video>')
        pop(f"#v{i}", st, "scale:0.86, y:60, opacity:0", "scale:1, y:0, opacity:1", 0.55, "expo.out")
        T.append(f'tl.to("#v{i}", {{scale:1.04, duration:{r3(max(d - 0.55, 0.1))}, ease:"none"}}, {r3(st + 0.55)});')
        T.append(f'tl.fromTo("#glow{i}", {{x:-260, opacity:0}}, {{x:260, opacity:{STY["glow"]}, duration:{d}, ease:"sine.inOut"}}, {st});')
    elif s["kind"] == "graphic":
        # A graphics-only beat: the brand background, a drifting glow, and the overlay fills the frame.
        E.append(f'<div id="bg{i}" class="clip avbg" data-start="{st}" data-duration="{d}" data-track-index="1"></div>')
        E.append(f'<div id="glow{i}" class="clip glow gglow" data-start="{st}" data-duration="{d}" data-track-index="2"></div>')
        T.append(f'tl.fromTo("#bg{i}", {{backgroundPosition:"0px 0px"}}, {{backgroundPosition:"0px -108px", duration:{d}, ease:"none"}}, {st});')
        T.append(f'tl.fromTo("#glow{i}", {{y:240, opacity:{r3(STY["glow"] * 0.35)}}}, {{y:-240, opacity:{r3(min(STY["glow"] * 1.1, 0.6))}, duration:{d}, ease:"sine.inOut"}}, {st});')
    else:
        E.append(f'<video id="v{i}" class="clip brvid" src="{s["clip"]}" muted playsinline data-start="{st}" data-duration="{d}" data-track-index="3"></video>')
        E.append(f'<div id="sh{i}" class="clip shade" data-start="{st}" data-duration="{d}" data-track-index="4"></div>')
        T.append(f'tl.fromTo("#v{i}", {{scale:1.12}}, {{scale:1.0, duration:{d}, ease:"power1.out"}}, {st});')
    if i > 1:
        cue("whoosh", st)
    if i > 1 and STY["flash"]:
        E.append(f'<div id="fl{i}" class="clip flash" data-start="{r3(st - 0.08)}" data-duration="0.45" data-track-index="10"></div>')
        T.append(f'tl.fromTo("#fl{i}", {{opacity:{STY["flash"]}}}, {{opacity:0, duration:0.37, ease:"power2.out"}}, {st});')

# ---------- persistent chrome ----------
outro_start = next((o["start"] for o in overlays if o["type"] == "outro"), TOTAL)
block("chrome", 0, outro_start, f'<div class="brandtag">{logo_html()}<span>{esc(brand.get("name", "").upper())}</span></div><div class="prog"><div id="progfill"></div></div>', track=9)
T.append(f'tl.fromTo("#progfill", {{scaleX:0}}, {{scaleX:1, duration:{TOTAL}, ease:"none"}}, 0);')
pop("#chrome .brandtag", 0.1, "y:-40, opacity:0", "y:0, opacity:1", 0.6, "expo.out")

# ---------- overlays ----------
for n, o in enumerate(overlays):
    oid, t, st, en = f"o{n}", o["type"], o["start"], o["end"]
    if t == "headline":
        rows = []
        for li, line in enumerate(o["lines"]):
            size = line.get("size", o.get("size", "big"))
            hw, cnt = words(line["text"], size, f"{oid}l{li}_")
            rows.append(hw)
            if size in ("slam", "huge"):
                for k in range(cnt):
                    pop(f"#{oid}l{li}_{k}", line["at"] + k * line.get("step", 0.2), "scale:2.2, opacity:0", "scale:1, opacity:1", 0.3, "power4.out")
                    cue("pop", line["at"] + k * line.get("step", 0.2), minor=True)
            else:
                rise(f"{oid}l{li}_", cnt, line["at"], line.get("step", 0.15))
        block(oid, st, en, f'<div class="head {o.get("pos", "top")}">{"<br>".join(rows)}</div>')
        em = o.get("emphasize")
        if em:
            emphasize(f'#{oid}l{em["line"]}_{em["word"]}', em["at"])
    elif t == "reveal":
        block(oid, st, en, f'<div class="head top"><div class="kicker" id="{oid}k">{esc(o["kicker"])}</div><div class="reveal">{logo_html("logo big-logo")}<span class="rtitle" id="{oid}t">{esc(o["title"])}</span></div></div>')
        pop(f"#{oid}k", o["kickerAt"], "x:-80, opacity:0", "x:0, opacity:1", 0.6, "expo.out")
        pop(f"#{oid} .big-logo", o["titleAt"] - 0.1, "scale:0, rotation:-90", "scale:1, rotation:0", 0.6, "back.out(2.2)")
        cue("chime", o["titleAt"])
        pop(f"#{oid}t", o["titleAt"], "x:-60, opacity:0", "x:0, opacity:1", 0.5, "expo.out")
    elif t == "counter":
        reels = "".join(
            '<span class="comma">' + esc(ch) + '</span>' if not ch.isdigit() else
            f'<span class="dg"><span class="reel" id="{oid}r{k}">' + "".join(f"<span>{d}</span>" for d in range(10)) + "</span></span>"
            for k, ch in enumerate(o["value"]))
        pills = "".join(f'<span class="pill" id="{oid}p{k}">{esc(p["text"])}</span>' for k, p in enumerate(o.get("pills", [])))
        block(oid, st, en, f'<div class="counter"><div class="num">{reels}</div><div class="label">{esc(o.get("label", "").upper())}</div><div class="pills">{pills}</div></div>')
        pop(f"#{oid} .counter", o["at"] - 0.15, "scale:0.7, opacity:0", "scale:1, opacity:1", 0.45, "back.out(2)")
        cue("pop", o["at"])
        dk = 0
        for k, ch in enumerate(o["value"]):
            if ch.isdigit():
                T.append(f'tl.fromTo("#{oid}r{k}", {{y:0}}, {{y:-{int(ch) * 300}, duration:{r3(1.4 + dk * 0.25)}, ease:"power3.out"}}, {r3(o["at"])});')
                dk += 1
        for k, p in enumerate(o.get("pills", [])):
            pop(f"#{oid}p{k}", p["at"], "y:40, scale:0.5, opacity:0", "y:0, scale:1, opacity:1", 0.5, "back.out(2.5)")
            cue("pop", p["at"], minor=True)
    elif t == "search":
        ticks = "".join(f'<div class="tick" id="{oid}t{k}"><b>✓</b> {esc(x["text"])}</div>' for k, x in enumerate(o.get("ticks", [])))
        foot = o.get("footer")
        foot_html = f'<div class="upfront" id="{oid}f">{esc(foot["text"].upper())}</div>' if foot else ""
        block(oid, st, en, f'''<div class="search" id="{oid}s"><svg viewBox="0 0 24 24" class="mag"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M15.5 15.5L21 21" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg><div class="stext"><span class="ph" id="{oid}ph">{esc(o["placeholder"])}</span><span class="typed" id="{oid}ty">{esc(o["typed"])}</span><span class="caret" id="{oid}c"></span></div><span class="kbd">⌘K</span></div><div class="ticks">{ticks}{foot_html}</div>''')
        pop(f"#{oid}s", st + 0.05, "y:-80, opacity:0, scale:0.9", "y:0, opacity:1, scale:1", 0.55, "expo.out")
        T.append(f'tl.to("#{oid}ph", {{opacity:0, duration:0.15}}, {r3(o["typeAt"] - 0.05)});')
        cue("click", o["typeAt"] - 0.05)
        T.append(f'tl.fromTo("#{oid}ty", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{o.get("typeDur", 1.0)}, ease:"steps({max(len(o["typed"]), 1)})"}}, {r3(o["typeAt"])});')
        T.append(f'tl.fromTo("#{oid}c", {{opacity:1}}, {{opacity:0, duration:0.4, repeat:{int((en - st) / 0.4)}, yoyo:true, ease:"steps(1)"}}, {r3(st + 0.1)});')
        for k, x in enumerate(o.get("ticks", [])):
            pop(f"#{oid}t{k}", x["at"], f"x:{-120 if k % 2 == 0 else 120}, opacity:0", "x:0, opacity:1", 0.5, "back.out(2)")
            cue("pop", x["at"])
        if foot:
            pop(f"#{oid}f", foot["at"], "scale:1.6, opacity:0", "scale:1, opacity:1", 0.4, "power4.out")
    elif t == "chips":
        chips = []
        for k, c in enumerate(o["chips"]):
            if k and o.get("joiner"):
                chips.append(f'<span class="or" id="{oid}j{k}">{esc(o["joiner"])}</span>')
            chips.append(f'<span class="chip" id="{oid}c{k}">{esc(c["text"])}</span>')
        sub = o.get("sub")
        sub_html = f'<div class="sub" id="{oid}sub">{esc(sub["text"])}</div>' if sub else ""
        block(oid, st, en, f'<div class="head top">{sub_html}<div class="chips">{"".join(chips)}</div></div>')
        if sub:
            pop(f"#{oid}sub", sub["at"], "y:30, opacity:0", "y:0, opacity:1", 0.5, "expo.out")
        for k, c in enumerate(o["chips"]):
            pop(f"#{oid}c{k}", c["at"], f"scale:0, rotation:{-12 if k % 2 == 0 else 12}", "scale:1, rotation:0", 0.5, "back.out(2.4)")
            cue("pop", c["at"])
            if k and o.get("joiner"):
                pop(f"#{oid}j{k}", c["at"] - 0.4, "opacity:0", "opacity:1", 0.3, "none")
    elif t == "check":
        block(oid, st, en, f'<div class="head top"><div class="nothing"><span class="ok" id="{oid}ok">✓</span><span id="{oid}tx">{esc(o["text"])}</span></div></div>')
        pop(f"#{oid}ok", o["at"], "scale:0, rotation:-180", "scale:1, rotation:0", 0.5, "back.out(2.5)")
        cue("chime", o["at"])
        pop(f"#{oid}tx", o["at"] + 0.1, "x:40, opacity:0", "x:0, opacity:1", 0.45, "expo.out")
    elif t == "rail":
        block(oid, st, en, f'<div class="head top"><div class="kicker" id="{oid}k">{esc(o["kicker"].upper())}</div><div class="huge" id="{oid}h">{esc(o["title"])}</div></div><div class="track" id="{oid}tr"><span class="node nA"></span><div class="rail"><div class="railfill" id="{oid}rf"></div></div><span class="node nB" id="{oid}nB"></span><div class="tl tlA">{esc(o["left"].upper())}</div><div class="tl tlB">{esc(o["right"].upper())}</div></div>')
        pop(f"#{oid}k", o.get("kickerAt", st), "opacity:0, y:-20", "opacity:1, y:0", 0.4, "expo.out")
        pop(f"#{oid}h", o["titleAt"], "scale:0.6, opacity:0", "scale:1, opacity:1", 0.5, "back.out(2)")
        pop(f"#{oid}tr", st + 0.15, "opacity:0", "opacity:1", 0.3, "none")
        T.append(f'tl.fromTo("#{oid}rf", {{scaleX:0}}, {{scaleX:1, duration:{o.get("fillDur", 1.5)}, ease:"power2.inOut"}}, {r3(o["fillAt"])});')
        done = o["fillAt"] + o.get("fillDur", 1.5)
        cue("pop", done)
        T.append(f'tl.fromTo("#{oid}nB", {{opacity:0.35}}, {{opacity:1, duration:0.2}}, {r3(done)});')
        T.append(f'tl.fromTo("#{oid}nB", {{scale:1}}, {{scale:1.6, duration:0.18, yoyo:true, repeat:1, immediateRender:false}}, {r3(done)});')
    elif t == "checklist":
        rows = "".join(f'<div class="vrow" id="{oid}r{k}"><span class="mono">0{k + 1}</span><span class="vt">{esc(r["text"])}</span><span class="vok" id="{oid}k{k}">{esc(r.get("tag", "PASS"))}</span></div>' for k, r in enumerate(o["rows"]))
        res = o.get("result")
        res_html = f'<div class="vres" id="{oid}res"><span>{esc(res["text"])}</span><span class="badge">✓ {esc(res["badge"])}</span></div>' if res else ""
        block(oid, st, en, f'<div class="vcard" id="{oid}c"><div class="vhead"><span class="dot" id="{oid}d"></span><span class="mono">{esc(o["title"].upper())}</span><span class="mono dim">{esc(o.get("meta", "").upper())}</span></div>{rows}{res_html}</div>')
        pop(f"#{oid}c", st + 0.05, "y:120, opacity:0", "y:0, opacity:1", 0.6, "expo.out")
        T.append(f'tl.fromTo("#{oid}d", {{opacity:1}}, {{opacity:0.2, duration:0.5, repeat:{int((en - st) / 0.5)}, yoyo:true, ease:"sine.inOut"}}, {r3(st + 0.15)});')
        for k, r in enumerate(o["rows"]):
            pop(f"#{oid}r{k}", r["at"] - 0.35, "x:-60, opacity:0", "x:0, opacity:1", 0.4, "expo.out")
            pop(f"#{oid}k{k}", r["at"], "scale:0, opacity:0", "scale:1, opacity:1", 0.35, "back.out(3)")
            cue("pop", r["at"])
        if res:
            pop(f"#{oid}res", res["at"], "y:30, opacity:0", "y:0, opacity:1", 0.45, "back.out(2)")
            cue("chime", res["at"])
    elif t == "outro":
        lines = "".join(f"<div>{esc(x)}</div>" for x in o["lines"])
        block(oid, st, en, f'<div class="endtop" id="{oid}l">{logo_html("logo end-logo")}</div><div class="endbot" id="{oid}b">{lines}</div>')
        pop(f"#{oid}l", o.get("logoAt", st + 0.1), "scale:0, rotation:-120, opacity:0", "scale:1, rotation:0, opacity:1", 0.7, "back.out(2)")
        cue("chime", o.get("logoAt", st + 0.1))
        pop(f"#{oid}b", o.get("linesAt", st + 0.45), "y:60, opacity:0", "y:0, opacity:1", 0.6, "expo.out")
        T.append(f'tl.fromTo("#fade", {{opacity:0}}, {{opacity:1, duration:0.35, ease:"none"}}, {r3(o.get("fadeAt", TOTAL - 0.38))});')
    elif t == "screen":
        screen(o, oid, st, en)
    elif t == "raw":
        # A custom scene: hand-written elements (each a top-level clip with its own
        # data-start, data-duration and data-track-index) and GSAP tweens on `tl`.
        E.extend(o["elements"])
        T.extend(o["tweens"])
    else:
        sys.exit(f"unknown overlay type {t!r}")
    for x in o.get("sfx", []):
        cue(x["sound"], x["at"])

# ---------- captions ----------
cap_scenes = set(fin.get("captionScenes", []))
ci = 0
for k, (a, b, text) in enumerate(subs):
    sc = scene_at(a + 0.01)
    if sc["n"] not in cap_scenes:
        continue
    nxt = subs[k + 1][0] if k + 1 < len(subs) else TOTAL
    end = min(nxt, sc["end"], b + 0.45)
    wh, cnt = words(text, "cw", f"cp{ci}_")
    block(f"cap{ci}", a, end, f'<div class="cap {"capav" if sc["kind"] == "avatar" else "capbr"}">{wh}</div>', track=7)
    span = max(b - a, 0.3)
    for j in range(cnt):
        pop(f"#cp{ci}_{j}", a + span * j / cnt, "y:24, opacity:0", "y:0, opacity:1", 0.22, "back.out(2)")
    ci += 1

# ---------- page ----------
fonts = scn["fonts"]
face = "".join(
    f'@font-face {{ font-family: "{f["family"]}"; font-weight: {w}; font-display: block; src: url("assets/fonts/{f["file_prefix"]}-latin-{w}-normal.woff2") format("woff2"); }}\n'
    for f in (fonts["heading"], fonts["mono"]) for w in f["weights"])
vars_css = (f':root {{ --bg: {brand["bg"]}; --fg: {brand["fg"]}; --accent: {brand["accent"]}; --on-accent: {brand.get("onAccent", brand["bg"])};'
            f' --heading: "{fonts["heading"]["family"]}", ui-sans-serif, system-ui, sans-serif; --mono: "{fonts["mono"]["family"]}", ui-monospace, monospace; }}\n')
css = face + vars_css + open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
# A look: the person's own visual language, from reference images they sent. It is
# CSS laid over the base style, which still decides how things move.
look = fin.get("look") or {}
if look.get("css"):
    lp = look["css"] if os.path.isabs(look["css"]) else os.path.join(work, look["css"])
    css += f"\n/* look: {look.get('name', os.path.basename(lp))} */\n" + open(lp, encoding="utf-8").read()

def page(duration, body, tweens):
    return f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/gsap.min.js"></script>
<style>
{css}
</style>
</head>
<body>
<div id="root" class="style-{STYLE}{' cover' if duration == 1 else ''}" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="1080" data-height="1920">
{body}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{tweens}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
'''

def write_project(folder, html_text, name):
    open(os.path.join(folder, "index.html"), "w", encoding="utf-8").write(html_text)
    json.dump({"paths": {"assets": "assets"}, "media": {"autoProxy": True}}, open(os.path.join(folder, "hyperframes.json"), "w", encoding="utf-8"), indent=2)
    json.dump({"id": name, "name": name}, open(os.path.join(folder, "meta.json"), "w", encoding="utf-8"), indent=2)

audio = []
if os.path.exists(os.path.join(proj, "assets", "narration.m4a")):
    audio.append(f'<audio id="vo" src="assets/narration.m4a" data-start="0" data-duration="{TOTAL}" data-track-index="0" data-volume="1"></audio>')
if os.path.exists(os.path.join(proj, "assets", "music.m4a")):
    # Mixed and ducked under the voice by music.py.
    audio.append(f'<audio id="music" src="assets/music.m4a" data-start="0" data-duration="{TOTAL}" data-track-index="12" data-volume="1"></audio>')
guides = []
if args.guides:
    # Where the apps' own buttons, names and captions sit on a 9:16 post (the union of
    # Reels, TikTok and Shorts). Nothing that has to be read should land in the tint.
    guides.append(f'<div id="safe" class="clip fx guides" data-start="0" data-duration="{TOTAL}" data-track-index="99">'
                  '<i class="g-top"></i><i class="g-bottom"></i><i class="g-right"></i></div>')
body = "\n".join(audio + E + [f'<div id="fade" class="clip fx" data-start="0" data-duration="{TOTAL}" data-track-index="11"></div>'] + guides)
write_project(proj, page(TOTAL, body, "\n".join(T)), "finish")
print(f"wrote {proj}/index.html: style {STYLE}{', look ' + look.get('name', '') if look.get('css') else ''}{', hook ' + args.hook if args.hook else ''}, {len(E)} elements, {len(T)} tweens, {ci} captions{', SAFE-ZONE GUIDES ON (do not render)' if args.guides else ''}")

# ---------- preview times: each overlay once it has fully landed, and every scene ----------
def landed(o):
    hits = []
    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, (int, float)) and (k == "at" or (k.endswith("At") and k != "fadeAt")):
                    if o["type"] == "counter" and k == "at":
                        v += 1.5 + 0.25 * sum(c.isdigit() for c in o.get("value", ""))
                    elif k == "fillAt":
                        v += o.get("fillDur", 1.5) - 0.5
                    elif k == "typeAt":
                        v += o.get("typeDur", 1.0)
                    hits.append(v + 0.8)
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(o)
    t = max(hits) if hits else (o["start"] + o["end"]) / 2
    return min(max(t, o["start"] + 0.4), o["end"] - 0.15)
moments = [landed(o) for o in overlays]
moments += [(s["start"] + s["end"]) / 2 for s in scenes if not any(s["start"] - 1e-3 <= o["start"] < s["end"] for o in overlays)]
picked = []
for t in sorted(moments):
    if not picked or t - picked[-1] > 0.3:
        picked.append(r3(t))
times = ",".join(str(t) for t in picked)
open(os.path.join(work, "preview-times.txt"), "w", encoding="utf-8").write(times + "\n")
print(f"preview times ({len(picked)}): {times}")

# ---------- sound-effect cues, for polish.py ----------
cues = []
if SFX_ON:
    last = {}
    for snd, t in sorted(CUES, key=lambda c: c[1]):
        vol = SFX_STYLE.get(snd, 0.3)
        # Nothing in the opening beat of the hook, none after the fade, no machine-gun repeats.
        if vol <= 0 or t < 0.15 or t > TOTAL - 0.2 or t - last.get(snd, -9) < 0.22:
            continue
        last[snd] = t
        cues.append({"sound": snd, "at": t, "volume": vol})
json.dump({"style": STYLE, "hook": args.hook, "cues": cues}, open(os.path.join(work, "sfx-cues.json"), "w", encoding="utf-8"), indent=1)
print(f"sound effects: {len(cues) if SFX_ON else 'off'}")

# ---------- cover: one still frame for the post ----------
if args.cover:
    cv = fin.get("cover", {})
    first = next((o for o in fin["overlays"] if o["type"] == "headline"), None)
    lines = cv.get("lines") or ([l["text"] for l in first["lines"]] if first else [brand.get("name", "")])
    em = cv.get("emphasize", first.get("emphasize") if first else None)
    sc = next((x for x in scenes if x["n"] == cv.get("scene")), None) or next((x for x in scenes if x["kind"] == "avatar"), scenes[0])
    cdir = os.path.join(work, "cover")
    shutil.rmtree(cdir, ignore_errors=True)
    shutil.copytree(os.path.join(proj, "assets", "fonts"), os.path.join(cdir, "assets", "fonts"))
    shutil.copy(os.path.join(proj, "assets", "gsap.min.js"), os.path.join(cdir, "assets"))
    if scn.get("logo"):
        shutil.copy(os.path.join(proj, scn["logo"]), os.path.join(cdir, scn["logo"]))
    parts = ['<div class="clip avbg" data-start="0" data-duration="1" data-track-index="1"></div>']
    if sc.get("clip"):
        still = os.path.join(cdir, "assets", "still.jpg")
        mid = (sc["end"] - sc["start"]) / 2
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{mid:.2f}", "-i", os.path.join(proj, sc["clip"]),
                        "-frames:v", "1", "-q:v", "2", still], check=True)
        if sc["kind"] == "avatar":
            parts.append('<div class="clip glow" data-start="0" data-duration="1" data-track-index="2"></div>')
            parts.append('<img class="clip avvid" src="assets/still.jpg" alt="" data-start="0" data-duration="1" data-track-index="3" />')
        else:
            parts.append('<img class="clip brvid" src="assets/still.jpg" alt="" data-start="0" data-duration="1" data-track-index="3" />')
            parts.append('<div class="clip shade" data-start="0" data-duration="1" data-track-index="4"></div>')
    on_acc, acc = brand.get("onAccent", brand["bg"]), brand["accent"]
    rows = []
    for li, text in enumerate(lines):
        ws = text.split()
        spans = []
        for k, wd in enumerate(ws):
            style = ""
            if em and em["line"] == li and em["word"] == k:
                style = (f' style="background-image:linear-gradient({acc},{acc});background-repeat:no-repeat;background-position:0 96%;background-size:100% 0.08em"' if STYLE == "editorial"
                         else f' style="color:{acc}"' if STYLE == "clean" and acc.lower() != brand["fg"].lower()
                         else f' style="color:{on_acc};background-color:{acc}"')
            spans.append(f'<span class="w {cv.get("size", "big")}"{style}>{esc(wd)}</span>')
        rows.append("".join(spans))
    outro = next((o for o in fin["overlays"] if o["type"] == "outro"), None)
    foot = cv.get("footer", " ".join(outro["lines"]) if outro else "")
    foot_html = f'<div class="cover-foot">{esc(foot)}</div>' if foot else ""
    parts.append(f'<div class="clip ov" data-start="0" data-duration="1" data-track-index="5"><div class="brandtag">{logo_html()}<span>{esc(brand.get("name", "").upper())}</span></div>'
                 f'<div class="head {cv.get("pos", "top")} cover-head">{"<br>".join(rows)}</div>{foot_html}</div>')
    write_project(cdir, page(1, "\n".join(parts), ""), "cover")
    print(f"wrote {cdir}/index.html: snapshot it with --at 0.5")
