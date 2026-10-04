---
name: hyperframes-finish
description: Add a motion-graphics finish to a finished HeyGen Studio render, built and rendered locally with HyperFrames in the person's brand colours, logo, fonts and motion style, with optional music, alternative openings and a cover, at no credit cost. Runs after plan-video's render when the profile's Finish says HyperFrames, or when they say "add animation", "more visual pop", "HyperFrames", "make it pop", "finish it", "recut it", "change the style", "add music", "another hook" or "make a cover".
---

# HyperFrames finish

Turn a finished HeyGen Studio render into a branded motion-graphics cut. It adds kinetic headlines, number counters, UI mock-ups, checklists, word-by-word captions, cut transitions and a logo outro. The presenter sits in a rounded card instead of being letterboxed, and graphics-only beats are drawn whole. Music, alternative openings and a cover for the post are optional. Everything is built and rendered on this computer with HyperFrames, so **it spends no HeyGen credits** and needs no render yes. Re-edits are free too.

Read first:
- `${CLAUDE_PLUGIN_ROOT}/reference/voice-and-ground-rules.md`
- `${CLAUDE_PLUGIN_ROOT}/reference/motion-graphics.md`
- `Video Profile.md`, and the video's plan in `Video Plans/`

## When it can run

It needs a session that can download files and run Node, Python and ffmpeg (a cloud or Project session can). Check with `node -v && python3 -V && ffmpeg -version`. If any is missing, say once: *"The animated finish needs a Project session. Here's your HeyGen video as it is."* Then hand over the HeyGen link and stop.

Tell them what's happening and that it's free: *"Now I'm adding the motion graphics here. This part doesn't use credits and takes a few minutes."*

## 1. Gather the inputs

- **The render:** `get_video` on the Studio video ID. Take `video_url` and `subtitle_url` (signed links, valid about a week). Use the uncaptioned `video_url`; the finish draws its own captions.
- **The brand:** `get_brand_kit` with the ID in `Video Profile.md`. Take the darkest colour as `bg`, a light colour as `fg`, the strongest brand colour as `accent`, and whichever of `bg`/`fg` reads best on the accent as `onAccent`. Take the primary logo URL and the font names. Never invent a colour, logo or font the kit doesn't have; with no logo the template draws a letter monogram.
- **The plan:** from the beat sheet, the 1-based scene numbers of the avatar beats and the graphics-only beats, each beat's Graphic, the other hooks, and the style and music. A plan made before graphics were planned has no Graphic column: pick them now from `motion-graphics.md`.
- **Style and music:** the plan's, else the profile's **Finish** section. No style anywhere means Bold, and no music means none.

## 2. Prepare

Copy `${CLAUDE_PLUGIN_ROOT}/skills/hyperframes-finish/template/` to a scratch folder; call it `TPL`. Then:

```bash
python3 TPL/prep.py --out WORK --video "<video_url>" --subs "<subtitle_url>" --avatar 1,4,8 --graphic 5 \
  --logo "<logo url>" --heading-font "<kit heading font>" --mono-font "<kit body or mono font>"
```

It downloads the render, finds the scene cuts, and cuts one clip per scene. Avatar beats are cropped out of the letterbox, and graphics-only beats get no clip. It extracts the narration and installs GSAP and the fonts from npm. It downloads the logo and decides whether a dark logo needs a light plate. Then it writes `WORK/scenes.json`. Check that the number of scenes matches the beat sheet. If it doesn't, rerun with `--threshold 0.2` (more cuts) or `0.4` (fewer).

The renderer's headless Chrome can't reach CDNs or Google Fonts, so everything has to be local. That's why prep installs them.

**Music**, if the plan has it: search HeyGen's library with `search_audio_sounds` (`type: "music"`) using the mood, and pick a track at least as long as the video if one fits. Then:

```bash
python3 TPL/music.py WORK --music "<audio_url>"          # --level 0.15 quieter, 0.3 louder
```

It loops or trims the track to the video, fades it, and ducks it under the voice. The first time music goes in, say once that what they can do with the track is between them and HeyGen.

## 3. Write the spec

Write `WORK/finish.json`. `TPL/finish.example.json` shows every field. Times are in seconds on the render's own clock: read them from `scenes.json` and `WORK/subs.srt` so each word lands as it's said.

- `brand`: `name`, `bg`, `fg`, `accent`, `onAccent`, and optionally `logoPlate` (`light`, `dark` or `none`) to override prep's guess.
- `style`: `bold`, `clean` or `editorial`.
- `captionScenes`: the scenes that get word-by-word captions. Leave out scenes whose overlay already says the line.
- `overlays`: the plan's graphics, one or two per scene, placed as `motion-graphics.md` says. On a graphics-only scene a headline can use `"pos": "center"`.
- `hooks`: the other openings, if the plan has them. Each has a `name` (`B`, `C`) and its `overlays` for the first beat. Optionally it has `until`, the time up to which its overlays replace the main ones (the end of scene 1 by default).
- `cover`: optional. Its fields are `lines` (default: the hook headline), `footer` (default: the outro's words), `scene` (default: the first avatar scene) and `size`.

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

## 4. Build and preview

```bash
python3 TPL/build.py WORK --cover
cd WORK/project
npx --yes hyperframes@0.8.115 lint                       # 0 errors before going on
npx --yes hyperframes@0.8.115 snapshot --at "$(cat ../preview-times.txt)" --no-end --describe false
```

`build.py` writes `preview-times.txt`: the moment each graphic has fully landed, plus every scene without one. The snapshot command saves one frame per moment and a contact sheet in `snapshots/`. If `snapshot` or `render` says Chrome is missing, run `npx --yes hyperframes@0.8.115 browser ensure` once.

Look at every frame yourself first. Check for text running off the frame, a graphic over a face, the logo readable against the background, and every word spelled right. Fix the spec and rebuild until it's clean.

Then show them the contact sheet. Save it as `Video Plans/[date] [angle] preview.jpg` and ask, clickable:

> Here's every graphic in your finish, in order. It's free to change anything now.
>
> - **Render it**
> - **Change something** (tell me what: "bigger number in frame 4", "Clean style", "no music")

Changes are edits to `finish.json` (or `--style`, or `music.py --off`), a rebuild and a new sheet. In a scheduled run there's no one to ask, so skip the question and render.

## 5. Render

Say that rendering takes a few minutes, plus a few more for each other opening. Then, from `WORK/project`:

```bash
npx --yes hyperframes@0.8.115 render -f 30 -q high -o ../finish.mp4
python3 TPL/build.py WORK --hook B && npx --yes hyperframes@0.8.115 render -f 30 -q high -o ../finish-B.mp4   # each hook
python3 TPL/build.py WORK                                                                                    # back to the main cut
cd ../cover && npx --yes hyperframes@0.8.115 snapshot --at 0.5 --no-end --describe false
```

The cover is `WORK/cover/snapshots/frame-00-at-0.5s.png`.

## 6. Hand it over

Save to their Project:

- `Videos/[date] [angle].mp4`, the main cut
- `Videos/[date] [angle] - opening B.mp4` (and C), if there are other openings
- `Videos/[date] [angle] cover.png`
- `Videos/[date] [angle] source.tar.gz`: the work folder without `node_modules` and `render.mp4` (`tar --exclude=node_modules --exclude=render.mp4 -czf ... -C WORK .`), so later fixes start from it instead of a new HeyGen render

Keep a copy of `finish.json` with the plan in `Video Plans/`.

> **[Title], finished** is ready: [file link]. [length] seconds, built here, no credits used. Openings B and C are beside it: the same video with a different first line on screen, to test which one stops more people. The cover for the post is [cover link]. The plain HeyGen version is still at [video_page_url].

Leave out the openings sentence when there are none. Log it in `Video Log.md` with 0 credits and route `Directed + HyperFrames finish ([style])`. Then one next step: *"Want me to change anything in it, or plan the next one?"*

## Changing it later

Start from the saved source: unpack `[date] [angle] source.tar.gz` into a work folder. Nothing gets re-rendered in HeyGen unless a new clip is needed, and never the whole video.

- **On-screen words, colours, timing, an overlay, the cover:** edit `finish.json`, rebuild, re-render. Free, so no yes needed.
- **The style:** `build.py WORK --style clean`, or set `style` in `finish.json`. Free.
- **Music:** `music.py WORK --music "<url>"` for a new track, `--level` to change the volume, or `--off` to remove it. Then rebuild and re-render. Free.
- **Another opening:** add it to `hooks` and render it. Free.
- **One b-roll or scene clip is wrong:** regenerate only that clip, following *Fixing one beat* in `heygen-direction.md` (change one clause, keep the seed). Say the cost of that one clip and get a yes. There's no Studio reassembly. Swap it in, keeping the narration and every timing:

  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/hyperframes-finish/template/swap.py WORK --scene 3 --video "<new clip url>"
  ```

- **One avatar line is wrong:** render just that line with `create_video_from_avatar`, using the same look, voice and orientation as the scene. That's a few seconds of avatar, not the whole video. Say its cost and get a yes. Then take `video_url` and `subtitle_url` from `get_video` and swap it in:

  ```bash
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/hyperframes-finish/template/swap.py WORK --scene 4 --video "<video_url>" --line --subs "<subtitle_url>"
  ```

  The new line's picture, voice and captions replace the scene. Everything after it moves by the difference in length: later scenes, the times in `finish.json`, the captions and the music. Re-time the overlays inside that scene to the new line's captions.

- **A line on a graphics-only beat is wrong:** only the voice is needed. Render the line alone the same way, with the same cost and yes, and swap it in with `--line`. Only its sound is used, so any look will do, and the graphics stay.

After any swap: run `build.py WORK` from the same template folder, lint, snapshot the changed scene and the one after it, then render. Save over the video and its source, and log the fix in `Video Log.md` with the credits that one clip cost (0 for a finish-only change). `swap.py` keeps the previous files in `WORK/before-swap-N/` in case they want the old version back.

A change that runs through most of the video (a new script, a different presenter) is a new video. That goes back through plan-video.
