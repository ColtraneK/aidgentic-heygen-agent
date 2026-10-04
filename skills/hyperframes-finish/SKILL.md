---
name: hyperframes-finish
description: Add a motion-graphics finish to a finished HeyGen Studio render, built and rendered locally with HyperFrames in the person's brand colours, logo, fonts and motion style, with optional music, alternative openings and a cover, at no credit cost. Runs after plan-video's render when the profile's Finish says HyperFrames, or when they say "add animation", "more visual pop", "HyperFrames", "make it pop", "finish it", "recut it", "change the style", "add music", "another hook" or "make a cover".
---

# HyperFrames finish

Turn a finished HeyGen Studio render into a branded motion-graphics cut. It adds kinetic headlines, number counters, UI mock-ups, checklists, word-by-word captions, cut transitions and a logo outro. The presenter sits in a rounded card instead of being letterboxed, and graphics-only beats are drawn whole. Real screen recordings tilt in with click zooms and highlights, sound effects land on every cut and graphic, and the final cut can run a little faster than the voice was recorded. Music, alternative openings and a cover for the post are optional. Everything is built and rendered on this computer with HyperFrames, so **it spends no HeyGen credits** and needs no render yes. Re-edits are free too.

Read first:
- `${CLAUDE_PLUGIN_ROOT}/reference/voice-and-ground-rules.md`
- `${CLAUDE_PLUGIN_ROOT}/reference/motion-graphics.md`
- `Video Profile.md`, and the video's plan in `Video Plans/`

## When it can run

The finish needs Node, Python, ffmpeg and a headless Chrome, and it downloads the render, GSAP, fonts and the renderer. **Claude Code** can do all of that: the Code tab in the desktop app with a folder on their computer, Claude Code in a terminal, or Claude Code on the web. **Cowork** usually can't, even in a Project: its sandbox has no ffmpeg or blocks those downloads. Everything before the finish (setup, plans, renders, the content plan, the routine) works in Cowork.

Check first, with the render's `video_url`:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/hyperframes-finish/template/preflight.py --video "<video_url>"
```

**READY:** carry on here.

**HAND OFF:** don't try to install things or work around the sandbox. Write the handoff note (below), hand over the plain HeyGen video so they have something now, and tell them how to finish it in Claude Code:

> Your video's ready in HeyGen: [video_page_url]. The animated finish needs Claude Code, because it runs a video renderer this session can't. I've saved everything it needs in `Finish handoff/[date] [angle]/`. To finish it:
>
> 1. Open the **Code** tab in the Claude desktop app and choose a folder on your computer (any empty folder is fine).
> 2. Put the `Finish handoff/[date] [angle]` folder in it.
> 3. First time only: add the plugin there, by typing `/plugin marketplace add ColtraneK/aidgentic-heygen-agent` and then `/plugin install aidgentic-heygen-agent@aidgentic-heygen`.
> 4. Type: **finish the video in HANDOFF.md**
>
> The HeyGen links in it work for about a week.

Give the steps once per person. After the first time, the line *"The finish is waiting in `Finish handoff/[date] [angle]/`: open it in Claude Code and say 'finish the video in HANDOFF.md'"* is enough.

### The handoff note

Write `Finish handoff/[date] [angle]/HANDOFF.md`, and copy `Video Profile.md` and the plan from `Video Plans/` beside it. Claude Code reads only what's in that folder, and it may not have HeyGen connected, so the note carries everything, in this shape:

````markdown
# Finish handoff: [title]

Read this, `Video Profile.md` and `[plan].md`, then run the `hyperframes-finish` skill from the aidgentic-heygen-agent plugin, starting at step 2. Everything from step 1 is below; HeyGen isn't needed. Save the results in this folder.

- **Render:** [video_url] (expires about [date + 7 days])
- **Captions:** [subtitle_url]
- **HeyGen page:** [video_page_url]
- **Scenes:** avatar [1,4,8] · graphics-only [5] · the rest b-roll
- **Brand:** bg [hex] · fg [hex] · accent [hex] · on accent [hex] · logo [url] · heading font [name] · mono font [name]
- **Style:** [style] · **Look:** [none, or the CSS file copied here] · **Speed:** [1] · **Sound effects:** [on/off]
- **Music:** [audio_url from search_audio_sounds, or none]
- **Graphics, other openings and custom moments:** in the plan's beat sheet
- **Screen recordings:** [files copied here, or none]

If a link has expired: with HeyGen connected here, get fresh ones with `get_video` on [video_id]; otherwise ask for them in the original Project.
````

Pick the music track before handing off, while HeyGen is connected, so Claude Code needs nothing from HeyGen. Log the render in `Video Log.md` as usual, with the finish as `handed off to Claude Code`.

### Running from a handoff note

In Claude Code, when they say "finish the video in HANDOFF.md", take step 1's inputs from the note and the files beside it, and do steps 2 to 6 there. Save the results next to the note (or into their Project's `Videos/` if this session can reach it) and tell them where. If preflight fails here too, say which check failed. A missing ffmpeg is fixed by installing it (`brew install ffmpeg` on a Mac, `winget install ffmpeg` on Windows).

Tell them what's happening and that it's free: *"Now I'm adding the motion graphics here. This part doesn't use credits and takes a few minutes."*

## 1. Gather the inputs

- **The render:** `get_video` on the Studio video ID. Take `video_url` and `subtitle_url` (signed links, valid about a week). Use the uncaptioned `video_url`; the finish draws its own captions.
- **The brand:** `get_brand_kit` with the ID in `Video Profile.md`. Take the darkest colour as `bg`, a light colour as `fg`, the strongest brand colour as `accent`, and whichever of `bg`/`fg` reads best on the accent as `onAccent`. Take the primary logo URL and the font names. Never invent a colour, logo or font the kit doesn't have; with no logo the template draws a letter monogram.
- **The plan:** from the beat sheet, the 1-based scene numbers of the avatar beats and the graphics-only beats, each beat's Graphic, the other hooks, and the style and music. A plan made before graphics were planned has no Graphic column: pick them now from `motion-graphics.md`.
- **Style and music:** the plan's, else the profile's **Finish** section. No style anywhere means Bold, and no music means none.
- **Their look, if they have one:** the **Look** line under **Finish** names a CSS file in `Video Styles/Looks/`, made from reference images they sent (see *A look from their references*). Copy it into `WORK/` and set `look` in the spec. No look: the style alone.

## 2. Prepare

Copy `${CLAUDE_PLUGIN_ROOT}/skills/hyperframes-finish/template/` to a scratch folder; call it `TPL`. Then:

```bash
python3 TPL/prep.py --out WORK --video "<video_url>" --subs "<subtitle_url>" --avatar 1,4,8 --graphic 5 \
  --logo "<logo url>" --heading-font "<kit heading font>" --mono-font "<kit body or mono font>"
```

It downloads the render, finds the scene cuts, and cuts one clip per scene. Avatar beats become the presenter's card: a landscape look is cut out of its letterbox, and a portrait look (one that fills the frame) is framed from just below the top so the face, not the chest, sits in the card. Each avatar scene in `scenes.json` says which (`"fit"`). If a portrait look's card still shows too much sky or too much chest, rerun with `--face-y 0.16` (lower) or `0.11` (higher); if the letterbox isn't detected, force it with `--avatar-fit strip`. Graphics-only beats get no clip. It extracts the narration and installs GSAP and the fonts from npm. It downloads the logo and decides whether a dark logo needs a light plate. Then it writes `WORK/scenes.json`. Check that the number of scenes matches the beat sheet. If it doesn't, rerun with `--threshold 0.2` (more cuts) or `0.4` (fewer).

The renderer's headless Chrome can't reach CDNs or Google Fonts, so everything has to be local. That's why prep installs them.

**Music**, if the plan has it: search HeyGen's library with `search_audio_sounds` (`type: "music"`) using the mood, and pick a track at least as long as the video if one fits. Then:

```bash
python3 TPL/music.py WORK --music "<audio_url>"          # --level 0.15 quieter, 0.3 louder
```

It loops or trims the track to the video, fades it, and ducks it under the voice. The first time music goes in, say once that what they can do with the track is between them and HeyGen.

## 3. Write the spec

Write `WORK/finish.json`. `TPL/finish.example.json` shows every field. Times are in seconds on the render's own clock: read them from `scenes.json` and `WORK/subs.srt` so each word lands as it's said.

- `brand`: `name`, `bg`, `fg`, `accent`, `onAccent`, and optionally `logoPlate` (`light`, `dark` or `none`) to override prep's guess.
- `style`: `bold`, `clean` or `editorial`. With a look, the style still sets how things move.
- `look`: optional, `{"name": "...", "css": "look.css"}`. Its CSS is laid over the base style.
- `captionScenes`: the scenes that get word-by-word captions. Leave out scenes whose overlay already says the line.
- `overlays`: the plan's graphics, one or two per scene, placed as `motion-graphics.md` says. On a graphics-only scene a headline can use `"pos": "center"`.
- `hooks`: the other openings, if the plan has them. Each has a `name` (`B`, `C`) and its `overlays` for the first beat. Optionally it has `until`, the time up to which its overlays replace the main ones (the end of scene 1 by default).
- `cover`: optional. Its fields are `lines` (default: the hook headline), `footer` (default: the outro's words), `scene` (default: the first avatar scene) and `size`.
- `speed`: optional, from the plan or the profile. `1` plays as rendered; `1.05` to `1.15` tightens a voice that reads slowly, without changing its pitch. Applied by `polish.py` after the render, so every time in the spec stays on the render's clock.
- `sfx`: `"auto"` (the default) or `"off"`. With auto, `build.py` places a whoosh on each cut and screen recording, a pop as words, chips, ticks and rows land, a click on each click and typed search, and a chime on a check, a result and the logo. Bold gets all of them, Clean fewer, Editorial only the quiet ones. Any overlay can add its own with `"sfx": [{"sound": "pop", "at": 12.4}]`.

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
| `screen` | a real screen recording: a click path, a setting, the product working. It tilts in, and can zoom to `clicks` and box `highlights` |
| `raw` | a custom scene, for one-off moments the types above can't make: `elements` (HTML clips) and `tweens` (GSAP on `tl`) |

A `screen` overlay takes `file` (a path in the work folder or a URL; any common video, trimmed and re-encoded for you), `from` (seconds into the recording to start at), and `pos` (`center`, `top` or `bottom`). `clicks` is a list of `{"at", "x", "y"}` and `highlights` a list of `{"at", "x", "y", "w", "h"}`, with `x`, `y`, `w` and `h` as shares (0 to 1) of the recording's own width and height, so they stay put wherever the card sits. Set `"zoom": false` to keep the card still on clicks. Find click positions by looking at a frame of the recording (`ffmpeg -ss <t> -i rec.mp4 -frames:v 1 f.png`). On an avatar beat a recording only fits as a short wide strip above the presenter's card, so crop tall recordings to the part that matters first.

Every word on screen follows ground rule 4: it comes from the script or the source, word for word for numbers and names. Keep each overlay to a few words. The narration carries the detail.

### Custom moments

Every video gets one or two moments designed from scratch for it, on top of the graphic types, so no two videos look alike. Don't ask about them; they appear in the preview sheet like any other graphic, and they change them the same way.

- Pick the one or two lines that carry the video: the surprising number, the thing they should do, the before and after. Prefer graphics-only and b-roll beats, where the whole frame is free.
- Picture the idea before building it, in a sentence: what's on screen and what the camera does ("a dial for the setting, pushing in as it turns off"; "ten bars growing from zero, the tallest one lit in the accent"). Name the move: push in, pull out, pan, static with things fading in. "Make it cinematic" isn't a direction.
- Build it as a `raw` overlay, 4 to 10 seconds, in the brand's colours and fonts (`var(--bg)`, `var(--fg)`, `var(--accent)`, `var(--heading)`, `var(--mono)`) and the person's look if they have one. Each element is a top-level clip with a unique `id`, `class="clip"`, `data-start`, `data-duration` and a `data-track-index` from 20 up; its tweens are GSAP calls on `tl` at absolute times. Add `sfx` cues for its key moments.
- Same rules as every graphic: words from the script or source, nothing over a face, everything that has to be read inside the safe zones.
- Images they gave you (a product shot, a cut-out PNG) can go in it: copy them into `WORK/project/assets/` and use `assets/<name>`.

The toggle that flips to OFF in the first "AI training privacy switch" video is one: a pill and a knob, the knob sliding over as the pill dims, a ring pulsing out and "OFF" slamming in, with a click on the flip.

## 4. Build and preview

```bash
python3 TPL/build.py WORK --cover --guides
cd WORK/project
npx --yes hyperframes@0.8.115 lint                       # 0 errors before going on
npx --yes hyperframes@0.8.115 snapshot --at "$(cat ../preview-times.txt)" --no-end --describe false
```

`build.py` writes `preview-times.txt`: the moment each graphic has fully landed, plus every scene without one. The snapshot command saves one frame per moment and a contact sheet in `snapshots/`. If `snapshot` or `render` says Chrome is missing, run `npx --yes hyperframes@0.8.115 browser ensure` once.

Look at every frame yourself first. `--guides` tints the top, bottom and right edges, where Reels, TikTok and Shorts put their own buttons, names and captions. Check that no word, number or logo sits in the tint (a face or a background running under it is fine), then check for text running off the frame, a graphic over a face, the logo readable against the background, and every word spelled right. Fix the spec and rebuild until it's clean. For a video that won't be posted to a vertical feed (a website, a course), skip the tint check.

Then rebuild without `--guides` (`python3 TPL/build.py WORK --cover`) and snapshot again for them: the tint is only for you. Show them the contact sheet. Save it as `Video Plans/[date] [angle] preview.jpg` and ask, clickable:

> Here's every graphic in your finish, in order. It's free to change anything now.
>
> - **Render it**
> - **Change something** (tell me what: "bigger number in frame 4", "Clean style", "no music")

Changes are edits to `finish.json` (or `--style`, or `music.py --off`), a rebuild and a new sheet. In a scheduled run there's no one to ask, so skip the question and render.

## 5. Render and polish

Say that rendering takes a few minutes, plus a few more for each other opening. Then, from `WORK/project`:

```bash
npx --yes hyperframes@0.8.115 render -f 30 -q high -o ../finish.mp4
python3 TPL/polish.py WORK --in WORK/finish.mp4 --out WORK/final.mp4                                          # sound effects + speed
python3 TPL/build.py WORK --hook B && npx --yes hyperframes@0.8.115 render -f 30 -q high -o ../finish-B.mp4 \
  && python3 TPL/polish.py WORK --in WORK/finish-B.mp4 --out WORK/final-B.mp4                                 # each hook
python3 TPL/build.py WORK                                                                                    # back to the main cut
cd ../cover && npx --yes hyperframes@0.8.115 snapshot --at 0.5 --no-end --describe false
```

Polish each cut straight after rendering it: each opening has its own sound cues, and `build.py` rewrites them on every build. The cover is `WORK/cover/snapshots/frame-00-at-0.5s.png`.

**Sounds.** `polish.py` makes four short sounds (whoosh, pop, click, chime) itself, so it never waits on a download. For richer ones, search HeyGen's library with `search_audio_sounds` for each, and pass the ones you like once: `python3 TPL/polish.py WORK --sound whoosh="<url>" --sound pop="<url>"`. They're kept in `WORK/sfx/` and travel with the source, so later fixes sound the same. Like music, what they can do with a library sound is between them and HeyGen.

## A look from their references

If they send reference images (screenshots, a Pinterest board, frames from videos they like), or say "make it look like" something, make them a look. Never ask for references; setup only mentions they can send them.

1. Study the images: the palette, the type (weight, width, case, spacing), shapes and corners, texture and depth (flat, glass, grain, paper), how busy the frame is, and how things probably move. If they name a visual language (data-journalism charts, glassy Apple-style panels, luxury fashion, a clean startup look, slow documentary call-outs), use what that's known for.
2. Write it as CSS over the base style: `Video Styles/Looks/[name].css`, with a short `[name].md` beside it saying what it took from which image. Keep their brand colours and logo unless they ask otherwise; a look changes the treatment, not the brand. It can restyle any class in `style.css`, and its custom moments can use its own motifs.
3. Preview it in one frame with their words: `python3 TPL/sample.py LOOK --look "Video Styles/Looks/[name].css" --style [closest base] ...` (the same brand arguments as setup). Show `LOOK/look.png`.
4. On a yes, write it to **Finish** in the profile: `**Look:** [name] (Video Styles/Looks/[name].css), over [style]`. They can keep several and name one per video ("use the glass look").

## For someone finishing it themselves

Only when they ask (they have an editor, or want to do the sound and timing by hand): after rendering, `python3 TPL/polish.py WORK --in WORK/finish.mp4 --stems "Videos/[date] [angle] - parts"`. It writes the picture without sound, the voice, the music, the sound effects alone and the captions, at the render's own speed.

If they want particular sounds ("a soft click, not a pop", "a camera shutter on the numbers"), search HeyGen's library with `search_audio_sounds` and swap them in with `polish.py --sound`. Named sounds beat generic ones.

## 6. Hand it over

Save to their Project:

- `Videos/[date] [angle].mp4`, the main cut (`final.mp4`, the polished one)
- `Videos/[date] [angle] - opening B.mp4` (and C), if there are other openings (`final-B.mp4`)
- `Videos/[date] [angle] cover.png`
- `Videos/[date] [angle] source.tar.gz`: the work folder without `node_modules`, `render.mp4` and the rendered cuts (`tar --exclude=node_modules --exclude=render.mp4 --exclude='finish*.mp4' --exclude='final*.mp4' -czf ... -C WORK .`), so later fixes start from it instead of a new HeyGen render

Keep a copy of `finish.json` with the plan in `Video Plans/`.

> **[Title], finished** is ready: [file link]. [length] seconds, built here, no credits used. Openings B and C are beside it: the same video with a different first line on screen, to test which one stops more people. The cover for the post is [cover link]. The plain HeyGen version is still at [video_page_url].

Leave out the openings sentence when there are none. Log it in `Video Log.md` with 0 credits and route `Directed + HyperFrames finish ([style])`. Then one next step: *"Want me to change anything in it, or plan the next one?"*

## Changing it later

Start from the saved source: unpack `[date] [angle] source.tar.gz` into a work folder. Nothing gets re-rendered in HeyGen unless a new clip is needed, and never the whole video.

- **On-screen words, colours, timing, an overlay, the cover:** edit `finish.json`, rebuild, re-render. Free, so no yes needed.
- **The style or the look:** `build.py WORK --style clean`, or set `style` or `look` in `finish.json`. Free.
- **One graphic or custom moment:** change only that overlay and keep everything else as it is. Several changes go one at a time, each checked in a snapshot. Free.
- **Faster or slower, louder or no sound effects:** `speed` and `sfx` in `finish.json`, or a sound swapped with `polish.py --sound`. Re-polish the rendered cut; no re-render needed unless the graphics changed. Free.
- **A screen recording:** add or change a `screen` overlay, rebuild and re-render. Free.
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

After any swap: run `build.py WORK` from the same template folder, lint, snapshot the changed scene and the one after it, then render and polish. Save over the video and its source, and log the fix in `Video Log.md` with the credits that one clip cost (0 for a finish-only change). `swap.py` keeps the previous files in `WORK/before-swap-N/` in case they want the old version back.

A change that runs through most of the video (a new script, a different presenter) is a new video. That goes back through plan-video.
