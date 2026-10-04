---
name: plan-video
description: Plan and make one HeyGen video from the person's own content, showing the beat sheet and the credit cost and rendering only on an explicit yes. Use when they say "plan a video", "make a video", "make a video from this", "turn this into a video", "quick video about", "render it", "fix beat 3", "redo that clip", "more ideas", or name an angle from their idea bank. Also runs inside a scheduled routine to draft the next plan.
---

# Plan a video

Turn one piece of their content into one finished video. Plan it, price it, get a yes, render it, log it.

Read first, every time:
- `${CLAUDE_PLUGIN_ROOT}/reference/voice-and-ground-rules.md`
- `${CLAUDE_PLUGIN_ROOT}/reference/heygen-direction.md`
- `Video Profile.md`, `Video Log.md` and `Content Angles.md` in their Project
- `${CLAUDE_PLUGIN_ROOT}/reference/motion-graphics.md`, when the profile's **Finish** says HyperFrames

If `Video Profile.md` doesn't exist: *"Let's set you up first. Type `/video-setup`. It takes about ten minutes and nothing in it spends credits."* Then stop.

---

## 1. Pick what it's about

- **They gave a link or a document:** read it. That's the source.
- **They named an angle:** use it.
- **Neither:** offer the three best `idea` angles from `Content Angles.md` as clickable options, plus "something else". Skip anything `Video Log.md` shows as made.

If they ask for **more ideas**, add 5 angles to `Content Angles.md` from their sources, show them, and stop.

## 2. Pick the route

Directed by default. Offer it as one click only if there's a reason to: low credits, they said "quick", or they asked for motion graphics.

- **Directed** (default): several looks, generated b-roll, one shot of them in a scene
- **Quick:** one look, one take, captions. Fastest and cheapest.
- **Showpiece:** HeyGen's Video Agent decides the visuals. Slower, varies week to week.

## 3. Write the script

- 45 to 60 seconds: about 110 to 150 words. Count them.
- First person, their voice rules from `Video Profile.md`.
- Open on something that happened or is true, ideally with a number from the source.
- One idea. Close on their call to action, word for word.
- Every fact comes from the source. If a name, number or result isn't in it, leave it out or ask.

## 4. Build the beat sheet

Split the script into 8 to 11 beats and assign each one per `heygen-direction.md`:

- presenter on screen for 40% of beats at most, never the same look twice in a row
- one `you-in-scene` beat where the line describes something they do
- b-roll beats that show the line, each with a full prompt (subject, setting, camera, light, brand colour, the no-text line, audio)
- an end card

**With the HyperFrames finish** (the profile's **Finish** says so), plan the graphics now, from `motion-graphics.md`:

- a **Graphic** for each beat that needs one: its type and its exact words, taken from the line or the source
- up to two **graphics-only** beats where the line is just a number, a list or a comparison. They need no generated clip, so they save its credits. Skip this when the profile has no graphics plate.
- up to two **other hooks** for the first beat: different words or a different graphic on screen over the same spoken line
- a calm top third in the prompt of any b-roll beat with a top graphic
- one or two **custom moments**: the lines that carry the video get a graphic designed for them alone, written in the Graphic column as `custom:` and the idea in a few words (see `motion-graphics.md`)
- a **screen** graphic for any line that walks through something on a screen (a setting, a click path, the product). Ask for that recording with the plan, as `motion-graphics.md` says

Show it as a table they can read in thirty seconds. Keep the prompts out of the table; summarize each shot in a few words. Leave out the Graphic column when there's no finish.

| # | Line | On screen | Look or shot | Graphic |
|---|---|---|---|---|
| 1 | "If you run a small business..." | You, talking | City skyline look, three-finger gesture | headline: "Three people. One inbox." |
| 3 | "We build AI agents..." | b-roll | Small team around a laptop, lime flowchart on the wall | captions |
| 5 | "Four hours became thirty minutes." | graphics | full screen, no clip | rail: 4 hours to 30 minutes |
| 8 | "Every system has a human approval step..." | You, in a scene | At your desk, approving something on your laptop | check: "A human signs off." |

Under the table, one line for the other hooks (*"Other openings: B, a counter: 4 hours to 30 minutes. C, a headline: 'Your inbox, handled.'"*) and one for the style, music, sound and speed (*"Clean style, warm and upbeat music, sound effects on, 1.1x speed."*). They change anything they like with the same reply.

## 5. Price it and ask

Call `get_current_user` for their balance. Estimate the cost from `Video Log.md` if it has measured runs, otherwise from the table in `heygen-direction.md`. Give a range.

Then ask, clickable:

> This one's about [length] with [n] shots of you across [n] looks and [n] generated clips. Estimated **[x to y] credits**. You have [balance].
> The animated finish, its [n] graphics-only beats, the other openings, the music and the cover are free. The graphics-only beats save about [2 × n] credits.
>
> - **Render it**
> - **Change something** (tell me what)
> - **Save the plan for later**

**Only "Render it" renders.** Anything else, adjust or save, and ask again. "Looks good" to the script is not a yes to render; ask the render question.

Save the plan either way to `Video Plans/[date] [angle].md`, with the script, the beat table (with its graphics), the other hooks, the style and music, every prompt, every seed, the look and voice IDs, and the estimate. Set the angle's status to `planned` in `Content Angles.md`.

## 6. Render

Say what's happening and how long: *"Making your clips now, about a minute each, all at once. Then I'll assemble it, about two more minutes."*

1. Generate every b-roll and end-card clip with `text_to_video`, and the scene clip with `reference_to_video` (fresh `preview_image_url` from `get_avatar_look`). Start them all, then poll `get_model_video` about every 30 seconds. Graphics-only beats need no clip.
2. If a clip fails, say which and why in plain words. Don't regenerate it without asking; offer to reword it or drop the beat.
3. Assemble with `create_video_from_studio`, captions on. A graphics-only beat is an `image` scene: the graphics plate's asset ID from the profile as its `source`, with its line as `script` and their `voice_id`. Poll `get_video` about every 30 seconds.
4. When it's done, call `get_current_user` again for the real cost.

**Quick route:** one `create_video_from_avatar` call with their best portrait look, Avatar IV, their voice, captions on, the right aspect ratio.

**Showpiece route:** `create_video_agent` in `chat` mode with their look, voice and brand kit ID, the script word for word, and a shot plan in the prompt that asks for the presenter on screen under half the time and a visual change every few seconds. Share the session link. When it pauses for input, show them the choices.

## 6b. The finish

If `Video Profile.md` has a **Finish** section saying HyperFrames, or they ask for more animation, follow the `hyperframes-finish` skill once the Studio render completes, with the graphics, hooks, style and music from the plan. It's built and rendered on this computer and spends no credits, so it needs no render yes. It shows them a preview sheet before the final cut. Hand over the finished file and the HeyGen link together, using that skill's hand-over in place of step 7's first two lines.

## 7. Hand it over

> **[Title]** is ready: [video_page_url]. [length] seconds, [credits] credits.
> Turn on captions on that page for the captioned version.

Then the one thing to check: the end card's spelling, the scene shot's likeness, or a crop on a landscape look, whichever applies.

Log it in `Video Log.md`:

| Date | Angle | Route | Video | Length | Credits | Verdict |
|---|---|---|---|---|---|---|

Set the angle's status to `made`. Then one next step: *"Want me to fix anything, or plan the next one?"*

## Fixing one beat

When they say a beat is off ("fix beat 3", "the end card's wrong", "that clip looks weird"), follow *Fixing one beat* in `heygen-direction.md`. Change one clause, keep the seed, regenerate that clip, reassemble. It's still a render: say the cost and get a yes first.

If the video has a HyperFrames finish, follow *Changing it later* in the `hyperframes-finish` skill instead. Only the one clip or line gets rendered in HeyGen, and it's swapped into the finish locally with no Studio reassembly. A fix to on-screen text is free.

## Inside a scheduled routine

When a scheduled prompt runs this skill, there's no one to ask. Follow the prompt's mode:

- **Plan only:** do steps 1 to 4, pick the next `idea` angle by the order in `Content Plan.md`, save the plan with its graphics, set status `planned`, and stop. Nothing renders.
- **Render under a cap:** do steps 1 to 4, check the balance, and render only if the estimate's top end fits under both the per-video cap and what's left of the monthly cap in `Content Plan.md`. Otherwise save the plan and note why it didn't render. Log every render with measured cost.

Never ask a question in a scheduled run. Never create, change or delete a scheduled task from inside one.
