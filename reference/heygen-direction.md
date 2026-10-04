# HeyGen direction: how to build a video that looks made

Read this before planning or rendering anything. It's the craft and the mechanics. Everything here was tested through the HeyGen connection from a cloud session, so it works in Cowork and in a scheduled run.

---

## The one fact that shapes everything

**Nothing ever leaves HeyGen.** Cowork can talk to HeyGen but can't download a finished video, and can't upload a file from the person's computer to HeyGen. So every piece of a video is made inside HeyGen and assembled inside HeyGen:

- b-roll clips come from HeyGen's own video model, which returns a link HeyGen's editor can use directly
- the presenter comes from avatar looks already in their HeyGen account
- the finished video is a link to their HeyGen library

Never try to download a render, save it to the Project, or move it through Google Drive or anywhere else. The one exception is the `hyperframes-finish` skill, in a session that can download files: it downloads the finished Studio render and its captions to build an animated cut locally. Never ask them to upload a photo through the chat. Photos go into HeyGen through the HeyGen app (Avatars, then Create, then Photo avatar).

---

## Three ways to make a video

| | Quick | Directed (default) | Showpiece |
|---|---|---|---|
| What it is | One avatar take, their look on its own background, captions | Avatar beats across several looks, generated b-roll, one clip of them acting in a scene, assembled in Studio | HeyGen's Video Agent composes it, with motion graphics |
| Tools | `create_video_from_avatar` | `text_to_video`, `reference_to_video`, then `create_video_from_studio` | `create_video_agent` |
| Variety | Low | High | Medium. One look only. |
| Control | Full | Full, beat by beat | Low. It decides the visuals. |
| Time | 2 to 3 min | 3 to 5 min | 15 to 25 min |
| Same look every week | Yes | Yes | It varies |

Default to **Directed**. Offer **Quick** when they want something in a hurry, have few credits, or the source is a short message rather than a story. Offer **Showpiece** only if they ask for motion graphics or "let HeyGen decide".

---

## Measured costs (one Creator account, Oct 2026)

These come from real renders on one account. Credits come out of the account's **premium credits**; other balances didn't move. Their plan may price differently, so always check the balance before and after with `get_current_user`, and once `Video Log.md` has measured runs, use their own numbers instead of these.

| What | Measured | Rough rate |
|---|---|---|
| b-roll clip, 6 s, 9:16, 768p | 2 credits | about 0.4 credits per second |
| six b-roll clips, 36 s total | 15 credits | |
| Studio assembly, 52 s finished, 10 scenes, 4 of them avatar | 11 credits | about 0.2 credits per finished second |
| Quick avatar video, 43 s | 18 credits | about 0.4 credits per second |
| Video Agent video, 42 s | 29 credits | about 0.7 credits per second |

So a 50 to 60 second Directed video with five or six b-roll clips is about 25 to 30 credits. Say estimates as a range and call them estimates.

**Free HeyGen accounts** have a small monthly allowance and some features held back. If a call fails with a plan or billing error, say so plainly, suggest the Quick route, and don't retry.

---

## Planning the beats

A beat is one sentence or two of script with one thing on screen. The beat sheet is the plan they approve.

- **Length:** 45 to 60 seconds total is the sweet spot. About 140 to 150 spoken words per minute. Count the words and check the total before you show the plan.
- **Beats:** 8 to 11 for a minute. No beat longer than about 12 seconds of speech; split at a sentence end.
- **The presenter is on screen for 40% of beats at most.** Use them for the hook, the turn and the call to action. Everything else is b-roll that shows what they're saying.
- **Rotate looks.** Never the same look twice in a row. With three or more looks, use at least three.
- **One "you in a scene" beat per video.** The presenter acting in a generated scene, without speaking. It's the moment people remember. Put it where the script describes something the presenter does: approving, explaining, reviewing, greeting, at work.
- **One idea per video.** One source, one angle, one promise.
- **Open on something that happened or is true,** a number, a before and after, a specific moment. Not on advice.

Beat types:

| Type | On screen | Voice |
|---|---|---|
| `avatar` | a look, talking to camera, with a gesture | their voice, lip-synced |
| `b-roll` | a generated clip that shows the line | their voice over it |
| `you-in-scene` | a generated clip of them doing something, from their own look | their voice over it |
| `end-card` | a generated clip that reveals their web address, or a final avatar beat | their voice |

---

## Generating b-roll (`text_to_video`)

One call per b-roll beat. Run them all at once, then poll each with `get_model_video` about every 30 seconds. Each takes about a minute.

Settings: `aspectRatio` to match the video (`9:16` vertical, `16:9` landscape, `1:1` square), `resolution: "768p"`, `duration` 5 to 8 seconds (a little longer than the line it covers; it loops), and a fixed `seed` per beat (any number, recorded in the plan) so a clip can be changed one clause at a time later.

**Write a few hundred words per prompt, in this order:**

1. **Subject and action.** Who or what, doing what, in one clear motion. "A woman in her late twenties closes her laptop, leans back and lifts her coffee."
2. **Setting.** Where, what's around, time of day.
3. **Camera.** Name a real camera and lens and keep it still: "shot on ARRI Alexa Mini LF with a 50mm lens at T2, locked-off static camera, shallow depth of field".
4. **Light and grade.** "soft window light from the left, warm natural colour grade".
5. **Brand colour, woven in.** Put their accent colour into the scene (a lit screen, a notebook, a beam of light) rather than over it.
6. **The no-text line, every time:** "No logos, brand names, printed words or badges anywhere in frame."
7. **Audio.** Name the room tone and one or two sounds, then "No dialogue. No music."

The model is least reliable on hands doing detailed work, long text, and soft organic motion like hair and paper. A static camera with one clear action is the most reliable shot there is.

---

## The "you in a scene" clip (`reference_to_video`)

The presenter, generated acting in a scene. Use one of their portrait looks as the reference.

1. Call `get_avatar_look` for the look and take its `preview_image_url`. Fetch it fresh each time; these links expire.
2. Call `reference_to_video` with `referenceImages: [{"type": "url", "url": <preview_image_url>}]`, `aspectRatio` to match, `duration` 5 to 7, `resolution: "768p"`, a seed.
3. Prompt: start with "Keep the person from the reference image exactly as they appear: same face, hair and clothing." Then one action, the setting, camera, light, "They do not speak.", the no-text line, and audio with "No dialogue. No music."

Good actions: reading something and giving one small nod of approval, walking into a bright office and smiling, pointing at a whiteboard of shapes, shaking hands with a client whose face is not visible. Keep it to one action.

---

## The end card

Two options. Pick the first only if the web address is short.

- **A text reveal clip** with `text_to_video`: a plain surface, a beam of their accent colour sweeps across and reveals the address. Spell it out letter by letter in the prompt and name it as the only lettering in frame. **Check the spelling on the finished video.** Text is the model's weakest spot. If it's wrong, regenerate that clip only.
- **A final avatar beat** saying the call to action, with captions carrying the address.

---

## Avatar beats

- Use their chosen looks from `Video Profile.md`. Prefer portrait looks for vertical videos; landscape looks get cropped to the middle.
- **Engine:** Avatar IV by default (`{"type": "avatar_iv"}`). Check `supported_api_engines` on the look before using Avatar V. If a call rejects the engine, fall back to Avatar IV.
- **Gesture:** `motion_prompt` with one or two plain gestures tied to words in the line: "holds up three fingers on 'three people', then a small smile." For photo looks on Avatar IV, also set `expressiveness` (`medium` by default, `high` for a hook). If a motion prompt is rejected, drop it and keep going.
- **Voice:** always the `voice_id` from `Video Profile.md`. Never fall back to a look's default voice without checking it's the same voice.
- Pauses: put `<break time="0.3s" />` between sentences if a line feels rushed. Don't promise a slower read with voice speed settings.

---

## Assembling in Studio (`create_video_from_studio`)

One call, all beats in order.

- Avatar beat:
  `{"type": "avatar_video", "input": {"type": "avatar", "avatar_id": <look id>, "engine": {"type": "avatar_iv"}, "expressiveness": "medium", "motion_prompt": "...", "script": "...", "voice_id": <voice id>}}`
- b-roll, "you in a scene", and end-card beats:
  `{"type": "video", "source": {"type": "url", "url": <video_url from get_model_video>}, "script": "...", "voice_id": <voice id>, "playback": {"mode": "loop", "volume": 0.2}}`
  Keep the clip's own sound under the voice, at 0.15 to 0.3. An end card can go higher, 0.5 to 0.6.
- Top level: `aspectRatio` to match, `resolution: "1080p"`, `caption: {"style": "default"}`, and a `title` like "[Business] · [angle] · [date]".

The narration sets each scene's length; clips loop under it. Avatar beats in Studio take a solid colour background only, so the look's own photo background is what shows. That's fine. The b-roll brings the variety.

Then poll `get_video` about every 30 seconds. It usually finishes in about 2 minutes. When it's done, give them `video_page_url`, and tell them the captions are on the captioned version (toggle captions on that page). After 5 minutes still processing, give them the link and say it'll finish on its own.

---

## Fixing one beat

When they like the video but one beat is off, don't re-render everything:

- **A b-roll or scene clip is wrong:** change one clause of that prompt, keep its seed, regenerate that clip only, then reassemble. Costs about one clip plus the assembly.
- **An avatar line is wrong:** change the line and reassemble. Costs the assembly.
- **The end card is misspelled:** regenerate that clip with a new seed, or swap it for an avatar beat.

Every reassembly is a new render, so it still needs a yes and a cost.

When the video has a HyperFrames finish, skip the reassembly. Regenerate only the one clip, or render only the one avatar line with `create_video_from_avatar`, and swap it into the finish locally (see the `hyperframes-finish` skill). The cost is that clip or line alone.

---

## When something fails

| What happened | Say | Do |
|---|---|---|
| A clip fails a content check | "One clip got flagged, probably [the likely cause]." | Rewrite that prompt more plainly, ask, regenerate that one |
| Plan or billing error | "Your HeyGen plan doesn't cover [this] right now." | Offer the Quick route. Don't retry. |
| Engine rejected | nothing | Switch that beat to Avatar IV |
| Motion prompt rejected | nothing | Drop it for that beat |
| Studio fails | "The assembly failed: [plain reason]." | Fix and ask before resubmitting |
| A clip link stopped working | nothing | Call `get_model_video` again for a fresh link |
| Still processing after 5 minutes | "It's still rendering. Here's the link, it'll finish on its own." | Stop polling |

Never resubmit a render just to check on it.
