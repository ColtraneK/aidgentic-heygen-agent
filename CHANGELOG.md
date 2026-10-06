# Changelog

## 1.2.2 · October 2026

- Setup checks HeyGen in the same message as the welcome. If HeyGen isn't connected, the four connect steps appear right away instead of waiting to be asked. It also searches for HeyGen tools that load lazily before deciding they're missing.
- Less dead time in setup: independent calls run together, looks, voices and brand kits are pulled in the background during Step 1 so Step 3 is instant, and the website question is asked in the first message.
- Before any slow step, setup says so and hands over one useful thing to do meanwhile in HeyGen (check the plan, add a look, find the first source, think about the audience).

## 1.2.1 · October 2026

- Where it runs: the README has a table of what works in Cowork and in Claude Code. Everything works in Cowork except the HyperFrames finish, which needs Claude Code (Node, Python, ffmpeg, a headless Chrome and downloads that Cowork's sandbox blocks).
- Handoff: the finish checks the session first (`preflight.py`). Where it can't run, it hands over the plain HeyGen video and saves `Finish handoff/[date] [angle]/HANDOFF.md` with everything the finish needs, plus three steps: make a folder, open it in Claude Code, say "finish the video in HANDOFF.md". Claude Code then needs no HeyGen connection and no plugin install; it fetches the finish from this repo itself, says what it downloads (about 400 MB, in user cache folders) and asks before installing ffmpeg or Node.
- Windows: the finish scripts read and write their files as UTF-8, so a non-UTF-8 Windows setup no longer breaks on symbols like ⌘ or emoji, and preflight finds `npx.cmd`. The README says how to remove what the finish downloads.
- The graphics plate is made without ffmpeg (`plate.py`), so Cowork setups get graphics-only beats too.

## 1.2.0 · October 2026

The polish from the first hand-finished videos, now built into every finish.

- Screen recordings: a `screen` graphic puts a real recording (a click path, a setting, the product) in a framed card that tilts in, zooms to each click with a ring, and boxes the thing to look at. `plan-video` asks for the recording with the plan.
- Sound effects: `build.py` places a whoosh, pop, click or chime on every cut and graphic, tuned to the style, and the new `polish.py` mixes them under the voice. Four sounds are made locally; HeyGen library sounds can replace them with `--sound`.
- Speed: a `speed` setting (1.05 to 1.15 for a slow-reading voice) speeds up picture and voice together without changing pitch.
- Portrait looks: avatar cards from a look that fills the frame are now framed on the face. Before, they were cut from the middle of the frame and showed the chest. `prep.py` detects the letterbox per scene; `--face-y` and `--avatar-fit` adjust it, and `swap.py` frames re-recorded lines the same way.
- Custom moments: every video gets one or two moments designed from scratch for its own lines, built as a `raw` overlay (hand-written HTML clips and GSAP tweens), shown in the preview sheet with everything else. No new questions.
- Safe zones: the layout keeps words, numbers and logos out of the areas Reels, TikTok and Shorts cover (top 160px, bottom 380px, right 120px). Captions, bottom headlines and the end card moved up to match. `build.py --guides` tints those areas for checking the preview.
- Looks from references: send screenshots of a look you love and the finish makes a CSS look from them, laid over the base style, previewed with `sample.py --look`. Never asked for; setup mentions it once.
- Parts for an editor: `polish.py --stems` writes the picture without sound, the voice, the music, the sound effects alone and the captions, on request.

## 1.1.0 · October 2026

- `hyperframes-finish`: a new skill that turns a finished Studio render into a branded motion-graphics cut (kinetic headlines, counters, UI mock-ups, checklists, captions, logo outro, no letterboxing). It reads colours, logo and fonts from the brand kit, and it's built and rendered locally with HyperFrames, so it spends no credits. `plan-video` runs it after the render when the profile's Finish says HyperFrames.
- Motion graphics are planned with the script. The beat sheet gets a Graphic column with each graphic's exact words, so they're approved with the same yes. `reference/motion-graphics.md` says which graphic suits which line and where it can go.
- Graphics-only beats: a line that's just a number or a list becomes a full-screen graphic over a plain brand plate instead of a generated clip, saving about 2 credits a beat.
- Three motion styles, Bold, Clean and Editorial. Setup previews them in the person's brand with `sample.py`, uploads the graphics plate, and asks for a music mood.
- A preview sheet of every graphic before the final cut, from `build.py`'s preview times.
- Free extras from one render: a music bed from HeyGen's library, ducked under the voice (`music.py`); alternative openings rendered as their own MP4s (`hooks`, `build.py --hook`); and a cover still for the post (`build.py --cover`).
- Fixing one scene of a finished video no longer re-renders the whole thing. `swap.py` puts a single regenerated b-roll clip, or a single re-recorded avatar line, into the finish. For a new line it re-splices the narration and moves the later timings and captions to match. Only that clip or line spends credits, and edits to on-screen text are free.

## 1.0.0 · October 2026

First release, for the HeyGen community workshop in New York on October 6.

- `/video-setup`: connects HeyGen, reads your website, builds your brand kit, picks your presenter looks and voice, drafts your idea bank
- `plan-video`: beat sheets with several looks, generated b-roll and a scene of you; a cost and a yes before every render; measured credits logged after; fix one beat without redoing the rest
- `content-plan`: cadence, sources, monthly cost, queue
- `video-routine`: a scheduled task that plans, or renders under a credit cap, your next video
- HeyGen connection bundled, sign in only
