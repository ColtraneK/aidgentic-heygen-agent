# Motion graphics

How to plan the on-screen graphics of a video that gets the HyperFrames finish. Plan them along with the script, not after the render: the person approves the words on screen with the same yes as the script, b-roll prompts can leave room for them, and a beat that's only a number or a list doesn't need a generated clip at all.

Every word on screen follows ground rule 4. It comes from the script or the source, and numbers and names are copied word for word.

---

## Picking a graphic for a line

Read each beat's line and pick at most one graphic for it. A beat with no graphic gets word-by-word captions.

| The line... | Graphic | On screen |
|---|---|---|
| opens the video (the hook) | `headline` | the hook in 6 to 12 words, one word on the accent |
| names the product for the first time | `reveal` | a kicker ("Introducing") and the name with the logo |
| has a number in it | `counter` | the number rolling up, a 1 to 3 word label, up to 3 pills |
| is about finding or choosing something | `search` | a search bar typing what they'd search for, 2 or 3 ticks |
| offers options or inputs ("a link or a file") | `chips` | a short line and 2 or 3 chips |
| reassures ("nothing to install") | `check` | a tick and the reassurance, 2 to 5 words |
| goes from one state to another, or talks about speed | `rail` | a line that fills from start to finish, a 1 to 3 word title |
| lists proof or steps | `checklist` | 2 to 4 rows that tick, then a result badge |
| is the promise or the turn | `headline` (`slam`) | 2 to 4 big words, one on the accent |
| is the call to action | `headline` then `outro` | the call to action, then the logo and the same words |

Keep words short. A headline line is at most about 18 characters at `big` and 12 at `slam`. Captions carry the rest, and the narration carries the detail.

## Where graphics can go

- **Avatar beats:** only graphics that sit at the top, above the presenter's card: `headline`, `reveal`, `chips`, `check`, and `rail` when it's short. Never a `counter`, `search`, `checklist` or a bottom `headline`: those cover the face.
- **B-roll beats:** anything. The prompt for a beat with a top graphic asks for a calm top third (see *B-roll that leaves room*).
- **Graphics-only beats:** anything, and a `headline` can sit in the middle (`"pos": "center"`).
- At most two graphics on one beat, and never two that both sit at the top.

## Graphics-only beats

When a line is really just a number, a list or a comparison, a generated clip adds little. Make the beat graphics-only instead: the finish draws the whole frame in the brand colours, and HeyGen renders only the voice over a plain plate. That saves the clip, about 2 credits.

- Up to two per video, never two in a row, never the hook or the close.
- In the beat sheet, its *On screen* is "graphics", its *Look or shot* is "full screen, no clip", and its *Graphic* is the graphic.
- In Studio it's an `image` scene of the brand's plain plate (the asset ID under **Finish** in `Video Profile.md`) with the line as its script. The plain HeyGen version shows the plate there; the finish fills it.
- No plate in the profile, or no finish: make it a b-roll beat as usual.

## B-roll that leaves room

For a b-roll beat with a top graphic, add this to the prompt's camera part: "Frame the subject in the middle and lower part of the frame and keep the top third calm and uncluttered, plain wall or sky." For a bottom graphic, swap top and bottom.

---

## The three styles

The style is set once in `Video Profile.md` under **Finish**. Any single video can change it.

| Style | Feels | Moves | Good for |
|---|---|---|---|
| **Bold** | loud, fast, social | words pop and bounce, a white flash at every cut, highlight blocks | launches, social feeds, younger audiences |
| **Clean** | calm, product-like | words rise and settle, no flash or spin, the accent word turns the accent colour | software, services, explainers |
| **Editorial** | considered, premium | slower, medium weights, outlines instead of fills, the accent word underlines | consulting, finance, health, anything with trust at stake |

## Alternative hooks

Most people start a social video with the sound off, so the on-screen first line is the hook they actually see. One render can carry two or three openings at no cost: the same spoken hook with different words or a different graphic on screen.

- Plan one main hook and up to two others in the beat sheet. Each one is a different graphic, or different words from the script or source, for the first beat only.
- Each one renders as its own MP4, free. Every extra opening adds a few minutes of rendering.
- Name them A, B and C, and log which one was posted where, if they say.

## Music

A music bed under the narration, faded and ducked under the voice. It's free.

- Search HeyGen's library with `search_audio_sounds` (`type: "music"`) from the mood in the profile, like "calm piano", "warm lo-fi" or "upbeat electronic". Pick a track at least as long as the video if one fits, or one that loops cleanly.
- Or use a track they give you. What they're allowed to do with a track is between them and HeyGen or the track's owner. Say that once, the first time music goes in.
- The default level is 0.22 before ducking. Raise it for a video with little talking, lower it for a dense script.

## The cover

A still for the post's cover or thumbnail: the hook headline, the presenter's card (or the hook's b-roll), the logo and the call to action. By default it reuses the hook's words. Make it with `--cover`; it's free.

---

## What to ask, and when

Suggest, don't quiz. The beat sheet shows the graphics already chosen, and they change what they like. Ask a question only when the answer changes the video and you can't tell from the source:

- **Which number is the big moment?** Ask only if the source has several and they'd make different videos.
- **Which hook should lead?** Only if two are equally strong. Otherwise lead with the one that has a number.

Setup asks once for the style and the music mood. Don't ask again per video unless they bring it up.
