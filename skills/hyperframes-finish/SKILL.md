---
name: hyperframes-finish
description: Add a motion-graphics finish to a finished HeyGen Studio render, built and rendered locally with HyperFrames in the person's brand colours, logo and fonts, at no credit cost. Runs after plan-video's render when the profile's Finish says HyperFrames, or when they say "add animation", "more visual pop", "HyperFrames", "make it pop", "finish it" or "recut it".
---

# HyperFrames finish

Turn a finished HeyGen Studio render into a branded motion-graphics cut: kinetic headlines, number counters, UI mock-ups, checklists, word-by-word captions, flash cuts, a logo outro, and the presenter in a rounded card instead of letterboxed. Everything is built and rendered on this computer with HyperFrames, so **it spends no HeyGen credits** and needs no render yes. Re-edits are free too.

Read first:
- `${CLAUDE_PLUGIN_ROOT}/reference/voice-and-ground-rules.md`
- `Video Profile.md`, and the video's beat sheet in `Video Plans/`

## When it can run

It needs a session that can download files and run Node, Python and ffmpeg (a cloud or Project session can). Check with `node -v && python3 -V && ffmpeg -version`. If any is missing, say once: *"The animated finish needs a Project session. Here's your HeyGen video as it is."* Then hand over the HeyGen link and stop.

Tell them what's happening and that it's free: *"Now I'm adding the motion graphics here. This part doesn't use credits and takes a few minutes."*

## 1. Gather the inputs

- **The render:** `get_video` on the Studio video ID. Take `video_url` and `subtitle_url` (signed links, valid about a week). Use the uncaptioned `video_url`; the finish draws its own captions.
- **The brand:** `get_brand_kit` with the ID in `Video Profile.md`. Take the darkest colour as `bg`, a light colour as `fg`, the strongest brand colour as `accent`, and whichever of `bg`/`fg` reads best on the accent as `onAccent`. Take the primary logo URL and the font names. Never invent a colour, logo or font the kit doesn't have; with no logo the template draws a letter monogram.
- **Avatar beats:** from the beat sheet, the 1-based scene numbers of the presenter's talking beats.

## 2. Prepare

Copy `${CLAUDE_PLUGIN_ROOT}/skills/hyperframes-finish/template/` to a scratch work folder, then run:

```bash
python3 prep.py --out WORK --video "<video_url>" --subs "<subtitle_url>" --avatar 1,4,8 \
  --logo "<logo url>" --heading-font "<kit heading font>" --mono-font "<kit body or mono font>"
```

It downloads the render, finds the scene cuts, cuts one clip per scene (avatar beats are cropped out of the letterbox), extracts the narration, installs GSAP and the fonts from npm, downloads the logo and decides whether a dark logo needs a light plate. Then it writes `WORK/scenes.json`. Check that the number of scenes matches the beat sheet. If it doesn't, rerun with `--threshold 0.2` (more cuts) or `0.4` (fewer).

The renderer's headless Chrome can't reach CDNs or Google Fonts, so everything has to be local. That's why prep installs them.

## 3. Write the spec

Write `WORK/finish.json`. `template/finish.example.json` shows every overlay type. Times are in seconds on the render's own clock: read them from `scenes.json` and `WORK/subs.srt` so each word lands as it's said.

- `brand`: `name`, `bg`, `fg`, `accent`, `onAccent`, and optionally `logoPlate` (`light`, `dark` or `none`) to override prep's guess.
- `captionScenes`: the scenes that get word-by-word captions. Leave out scenes whose overlay already says the line.
- `overlays`: one or two per scene, chosen from the line:

| Type | Use it for |
|---|---|
| `headline` | the hook, a promise, the call to action. Sizes `big`, `mid`, `huge`, `slam`; `emphasize` puts one word on the accent colour |
| `reveal` | introducing the product: kicker, logo spin, name |
| `counter` | any number in the line: rolling digits, a label, optional pills |
| `search` | finding or choosing something: search bar, typed text, ticks |
| `chips` | options or inputs: a line plus chips |
| `check` | a reassurance: check mark plus short line |
| `rail` | from A to B: a progress line that fills |
| `checklist` | proof or process: rows that tick, then a result badge |
| `outro` | the end card: logo, call to action, fade out |

Every word on screen follows ground rule 4: it comes from the script or the source, word for word for numbers and names. Keep each overlay to a few words. The narration carries the detail.

## 4. Build, check, render

```bash
python3 build.py WORK
cd WORK/project
npx --yes hyperframes@0.8.115 lint                       # 0 errors before going on
npx --yes hyperframes@0.8.115 snapshot --at 2,8,15,... --no-end --describe false
npx --yes hyperframes@0.8.115 render -f 30 -q high -o ../finish.mp4
```

If `render` says Chrome is missing, run `npx --yes hyperframes@0.8.115 browser ensure` once.

Look at the snapshots before rendering, one per scene. Check for text running off the frame, an overlay hiding a face, the logo readable against the background, and every word spelled right. Fix the spec, rebuild and re-snapshot. Rendering takes a few minutes. Say so before starting.

## 5. Hand it over

Save `finish.mp4` to `Videos/[date] [angle].mp4` in their Project, and tar the `WORK/project` folder (without `node_modules`) beside it so later tweaks start from it. Keep `finish.json` with the plan in `Video Plans/`.

> **[Title], finished** is ready: [file link]. [length] seconds, built here, no credits used. The plain HeyGen version is still at [video_page_url].

Log it in `Video Log.md` with 0 credits and route `Directed + HyperFrames finish`. Then one next step: *"Want me to change anything in it, or plan the next one?"*

## Changing it later

A change to the finish (a word, a colour, timing, an overlay) is an edit to `finish.json`, a rebuild and a re-render. It's free, so it needs no yes. A change to what's said or shown underneath needs a new HeyGen render, which goes back through plan-video's cost and yes.
