#!/usr/bin/env python3
"""Build the HyperFrames composition for the finish.

Reads WORK/scenes.json (from prep.py) and WORK/finish.json (brand + overlays,
written per video), and writes WORK/project/index.html plus the project files.

Usage: python3 build.py WORKDIR
"""
import html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
work = os.path.abspath(sys.argv[1])
scn = json.load(open(os.path.join(work, "scenes.json")))
fin = json.load(open(os.path.join(work, "finish.json")))
brand = fin["brand"]
TOTAL = scn["duration"]
scenes = scn["scenes"]

E, T = [], []
r3 = lambda x: round(float(x), 3)
esc = html.escape

def ts(s):
    h, m, rest = s.split(":"); sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000

subs = []
for blk in open(os.path.join(work, scn["subs"])).read().strip().split("\n\n"):
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

def rise(wid, n, t0, step=0.07):
    for k in range(n):
        T.append(f'tl.fromTo("#{wid}{k}", {{y:50, opacity:0, rotation:4}}, {{y:0, opacity:1, rotation:0, duration:0.45, ease:"back.out(2)"}}, {r3(t0 + k * step)});')

def pop(sel, at, frm="scale:0.5, y:40, opacity:0", to="scale:1, y:0, opacity:1", dur=0.5, ease="back.out(2.4)"):
    T.append(f'tl.fromTo("{sel}", {{{frm}}}, {{{to}, duration:{dur}, ease:"{ease}"}}, {r3(at)});')

def block(eid, start, end, inner, track=5):
    E.append(f'<div id="{eid}" class="clip ov" data-start="{r3(start)}" data-duration="{r3(end - start)}" data-track-index="{track}">{inner}</div>')

# ---------- scenes ----------
for s in scenes:
    i, st, d = s["n"], s["start"], r3(s["end"] - s["start"])
    if s["kind"] == "avatar":
        E.append(f'<div id="bg{i}" class="clip avbg" data-start="{st}" data-duration="{d}" data-track-index="1"></div>')
        E.append(f'<div id="glow{i}" class="clip glow" data-start="{st}" data-duration="{d}" data-track-index="2"></div>')
        E.append(f'<video id="v{i}" class="clip avvid" src="{s["clip"]}" muted playsinline data-start="{st}" data-duration="{d}" data-track-index="3"></video>')
        pop(f"#v{i}", st, "scale:0.86, y:60, opacity:0", "scale:1, y:0, opacity:1", 0.55, "expo.out")
        T.append(f'tl.to("#v{i}", {{scale:1.04, duration:{r3(max(d - 0.55, 0.1))}, ease:"none"}}, {r3(st + 0.55)});')
        T.append(f'tl.fromTo("#glow{i}", {{x:-260, opacity:0}}, {{x:260, opacity:0.55, duration:{d}, ease:"sine.inOut"}}, {st});')
    else:
        E.append(f'<video id="v{i}" class="clip brvid" src="{s["clip"]}" muted playsinline data-start="{st}" data-duration="{d}" data-track-index="3"></video>')
        E.append(f'<div id="sh{i}" class="clip shade" data-start="{st}" data-duration="{d}" data-track-index="4"></div>')
        T.append(f'tl.fromTo("#v{i}", {{scale:1.12}}, {{scale:1.0, duration:{d}, ease:"power1.out"}}, {st});')
    if i > 1:
        E.append(f'<div id="fl{i}" class="clip flash" data-start="{r3(st - 0.08)}" data-duration="0.45" data-track-index="10"></div>')
        T.append(f'tl.fromTo("#fl{i}", {{opacity:0.45}}, {{opacity:0, duration:0.37, ease:"power2.out"}}, {st});')

# ---------- persistent chrome ----------
outro_start = next((o["start"] for o in fin["overlays"] if o["type"] == "outro"), TOTAL)
block("chrome", 0, outro_start, f'<div class="brandtag">{logo_html()}<span>{esc(brand.get("name", "").upper())}</span></div><div class="prog"><div id="progfill"></div></div>', track=9)
T.append(f'tl.fromTo("#progfill", {{scaleX:0}}, {{scaleX:1, duration:{TOTAL}, ease:"none"}}, 0);')
pop("#chrome .brandtag", 0.1, "y:-40, opacity:0", "y:0, opacity:1", 0.6, "expo.out")

# ---------- overlays ----------
for n, o in enumerate(fin["overlays"]):
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
            else:
                rise(f"{oid}l{li}_", cnt, line["at"], line.get("step", 0.15))
        block(oid, st, en, f'<div class="head {o.get("pos", "top")}">{"<br>".join(rows)}</div>')
        em = o.get("emphasize")
        if em:
            on_acc, acc = brand.get("onAccent", brand["bg"]), brand["accent"]
            T.append(f'tl.to("#{oid}l{em["line"]}_{em["word"]}", {{color:"{on_acc}", backgroundColor:"{acc}", duration:0.15}}, {r3(em["at"])});')
    elif t == "reveal":
        block(oid, st, en, f'<div class="head top"><div class="kicker" id="{oid}k">{esc(o["kicker"])}</div><div class="reveal">{logo_html("logo big-logo")}<span class="rtitle" id="{oid}t">{esc(o["title"])}</span></div></div>')
        pop(f"#{oid}k", o["kickerAt"], "x:-80, opacity:0", "x:0, opacity:1", 0.6, "expo.out")
        pop(f"#{oid} .big-logo", o["titleAt"] - 0.1, "scale:0, rotation:-90", "scale:1, rotation:0", 0.6, "back.out(2.2)")
        pop(f"#{oid}t", o["titleAt"], "x:-60, opacity:0", "x:0, opacity:1", 0.5, "expo.out")
    elif t == "counter":
        reels = "".join(
            '<span class="comma">' + esc(ch) + '</span>' if not ch.isdigit() else
            f'<span class="dg"><span class="reel" id="{oid}r{k}">' + "".join(f"<span>{d}</span>" for d in range(10)) + "</span></span>"
            for k, ch in enumerate(o["value"]))
        pills = "".join(f'<span class="pill" id="{oid}p{k}">{esc(p["text"])}</span>' for k, p in enumerate(o.get("pills", [])))
        block(oid, st, en, f'<div class="counter"><div class="num">{reels}</div><div class="label">{esc(o.get("label", "").upper())}</div><div class="pills">{pills}</div></div>')
        pop(f"#{oid} .counter", o["at"] - 0.15, "scale:0.7, opacity:0", "scale:1, opacity:1", 0.45, "back.out(2)")
        dk = 0
        for k, ch in enumerate(o["value"]):
            if ch.isdigit():
                T.append(f'tl.fromTo("#{oid}r{k}", {{y:0}}, {{y:-{int(ch) * 300}, duration:{r3(1.4 + dk * 0.25)}, ease:"power3.out"}}, {r3(o["at"])});')
                dk += 1
        for k, p in enumerate(o.get("pills", [])):
            pop(f"#{oid}p{k}", p["at"], "y:40, scale:0.5, opacity:0", "y:0, scale:1, opacity:1", 0.5, "back.out(2.5)")
    elif t == "search":
        ticks = "".join(f'<div class="tick" id="{oid}t{k}"><b>✓</b> {esc(x["text"])}</div>' for k, x in enumerate(o.get("ticks", [])))
        foot = o.get("footer")
        foot_html = f'<div class="upfront" id="{oid}f">{esc(foot["text"].upper())}</div>' if foot else ""
        block(oid, st, en, f'''<div class="search" id="{oid}s"><svg viewBox="0 0 24 24" class="mag"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M15.5 15.5L21 21" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg><div class="stext"><span class="ph" id="{oid}ph">{esc(o["placeholder"])}</span><span class="typed" id="{oid}ty">{esc(o["typed"])}</span><span class="caret" id="{oid}c"></span></div><span class="kbd">⌘K</span></div><div class="ticks">{ticks}{foot_html}</div>''')
        pop(f"#{oid}s", st + 0.05, "y:-80, opacity:0, scale:0.9", "y:0, opacity:1, scale:1", 0.55, "expo.out")
        T.append(f'tl.to("#{oid}ph", {{opacity:0, duration:0.15}}, {r3(o["typeAt"] - 0.05)});')
        T.append(f'tl.fromTo("#{oid}ty", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{o.get("typeDur", 1.0)}, ease:"steps({max(len(o["typed"]), 1)})"}}, {r3(o["typeAt"])});')
        T.append(f'tl.fromTo("#{oid}c", {{opacity:1}}, {{opacity:0, duration:0.4, repeat:{int((en - st) / 0.4)}, yoyo:true, ease:"steps(1)"}}, {r3(st + 0.1)});')
        for k, x in enumerate(o.get("ticks", [])):
            pop(f"#{oid}t{k}", x["at"], f"x:{-120 if k % 2 == 0 else 120}, opacity:0", "x:0, opacity:1", 0.5, "back.out(2)")
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
            if k and o.get("joiner"):
                pop(f"#{oid}j{k}", c["at"] - 0.4, "opacity:0", "opacity:1", 0.3, "none")
    elif t == "check":
        block(oid, st, en, f'<div class="head top"><div class="nothing"><span class="ok" id="{oid}ok">✓</span><span id="{oid}tx">{esc(o["text"])}</span></div></div>')
        pop(f"#{oid}ok", o["at"], "scale:0, rotation:-180", "scale:1, rotation:0", 0.5, "back.out(2.5)")
        pop(f"#{oid}tx", o["at"] + 0.1, "x:40, opacity:0", "x:0, opacity:1", 0.45, "expo.out")
    elif t == "rail":
        block(oid, st, en, f'<div class="head top"><div class="kicker" id="{oid}k">{esc(o["kicker"].upper())}</div><div class="huge" id="{oid}h">{esc(o["title"])}</div></div><div class="track" id="{oid}tr"><span class="node nA"></span><div class="rail"><div class="railfill" id="{oid}rf"></div></div><span class="node nB" id="{oid}nB"></span><div class="tl tlA">{esc(o["left"].upper())}</div><div class="tl tlB">{esc(o["right"].upper())}</div></div>')
        pop(f"#{oid}k", o.get("kickerAt", st), "opacity:0, y:-20", "opacity:1, y:0", 0.4, "expo.out")
        pop(f"#{oid}h", o["titleAt"], "scale:0.6, opacity:0", "scale:1, opacity:1", 0.5, "back.out(2)")
        pop(f"#{oid}tr", st + 0.15, "opacity:0", "opacity:1", 0.3, "none")
        T.append(f'tl.fromTo("#{oid}rf", {{scaleX:0}}, {{scaleX:1, duration:{o.get("fillDur", 1.5)}, ease:"power2.inOut"}}, {r3(o["fillAt"])});')
        done = o["fillAt"] + o.get("fillDur", 1.5)
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
        if res:
            pop(f"#{oid}res", res["at"], "y:30, opacity:0", "y:0, opacity:1", 0.45, "back.out(2)")
    elif t == "outro":
        lines = "".join(f"<div>{esc(x)}</div>" for x in o["lines"])
        block(oid, st, en, f'<div class="endtop" id="{oid}l">{logo_html("logo end-logo")}</div><div class="endbot" id="{oid}b">{lines}</div>')
        pop(f"#{oid}l", o.get("logoAt", st + 0.1), "scale:0, rotation:-120, opacity:0", "scale:1, rotation:0, opacity:1", 0.7, "back.out(2)")
        pop(f"#{oid}b", o.get("linesAt", st + 0.45), "y:60, opacity:0", "y:0, opacity:1", 0.6, "expo.out")
        T.append(f'tl.fromTo("#fade", {{opacity:0}}, {{opacity:1, duration:0.35, ease:"none"}}, {r3(o.get("fadeAt", TOTAL - 0.38))});')
    else:
        sys.exit(f"unknown overlay type {t!r}")

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
css = face + vars_css + open(os.path.join(HERE, "style.css")).read()
page = f'''<!doctype html>
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
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
<audio id="vo" src="assets/narration.m4a" data-start="0" data-duration="{TOTAL}" data-track-index="0" data-volume="1"></audio>
{chr(10).join(E)}
<div id="fade" class="clip fx" data-start="0" data-duration="{TOTAL}" data-track-index="11"></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(T)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
'''
proj = os.path.join(work, "project")
open(os.path.join(proj, "index.html"), "w").write(page)
json.dump({"paths": {"assets": "assets"}, "media": {"autoProxy": True}}, open(os.path.join(proj, "hyperframes.json"), "w"), indent=2)
json.dump({"id": "finish", "name": "finish"}, open(os.path.join(proj, "meta.json"), "w"), indent=2)
print(f"wrote {proj}/index.html: {len(E)} elements, {len(T)} tweens, {ci} captions")
