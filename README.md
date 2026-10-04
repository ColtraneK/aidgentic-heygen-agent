# Aidgentic HeyGen Agent

A Claude plugin that plans and makes HeyGen videos from your own content. It reads your website, drafts video ideas, shows you every plan and what it'll cost, and only renders when you say yes. Then it keeps a content plan running on a schedule.

Your videos use your avatar in several looks, your voice, b-roll generated for each line, and one shot of you acting in a scene. Everything is made and kept inside your HeyGen account.

---

## What you get

**A video profile.** It reads your site, pulls your logo, colours and fonts into a HeyGen brand kit, and saves who you are, who's watching, your proof points and your call to action. Every plan starts from it, so you never explain your business twice.

**An idea bank.** Five to ten video angles drawn from your own pages: a result with a number, a before and after, a principle you hold, a question people ask. Each points back to where it came from.

**Videos with real variety.** A beat sheet for each video: your avatar on screen for the hook, the turn and the close, switching looks between lines, with generated b-roll showing everything else, and one clip of you acting in a scene. About 45 to 60 seconds, captions on.

**An animated finish, free.** After the render, it adds motion graphics in your brand colours, logo and fonts: kinetic headlines, number counters, checklists, captions and a logo outro, with no letterboxing. Real screen recordings tilt in and zoom to each click, sound effects land on every cut and graphic, and the cut can run a touch faster if your voice reads slowly. Every video also gets one or two moments designed just for it, everything stays clear of the Reels and TikTok buttons, and if you send screenshots of a look you love, your videos take it on. The graphics are planned with the script, so you approve the words on screen with the same yes. Lines that are just a number or a list become full-screen graphics instead of generated clips, which saves their credits. At setup you pick one of three motion styles (Bold, Clean or Editorial), shown in your own brand. You see a preview of every graphic before the final cut. Music under the voice, alternative openings to test, and a cover for the post come with it. It's all built and rendered with HyperFrames on your side, so none of it uses credits, and changes are free too. To fix one scene, only that clip or line is made again in HeyGen and swapped in, so the rest of the video never re-renders. The finish runs in Claude Code; see [Where it runs](#where-it-runs).

**A cost before every render.** It checks your credit balance, estimates the video, and asks. Nothing that spends credits happens without your yes. After each render it measures what it actually cost and logs it, so the next estimate is yours, not a guess.

**A content plan.** What gets made, how often, from what source, and what that costs a month.

**A routine.** A scheduled task that plans your next video on its own, even with your laptop closed. Start it in plan-only mode and approve each one; once you trust it, let it render under a credit cap you set.

---

## Before you start

- **Claude** on a paid plan (Pro or above), in the desktop app, with Cowork
- **A HeyGen account.** In the HeyGen app, make **photo avatars** of yourself: Avatars, then Create, then Photo avatar. Three or more looks gives every video variety. A **voice clone** (Voices) makes it sound like you.
- **One piece of your content:** your website works, or a blog post, an FAQ, a webinar transcript

---

## Check it before you install it

A plugin can do whatever your Claude can do. Installing one from someone you don't know is the same as running their program, this one included. It's all plain text, so have Claude read it first. Paste this into a new chat:

```
Audit this plugin before I install it: https://github.com/ColtraneK/aidgentic-heygen-agent
Read every file, don't skim, and don't be generous.

Check what it reads; what it writes and where; what leaves this machine and to whom; any hardcoded address or domain that isn't mine or HeyGen's; anywhere it's told to act on content it reads instead of treating that content as text; anything that spends money; and anything else that could be risky.

Do the reading quietly, then give me under 150 words: Verdict (safe / safe with conditions / don't install), Why (three bullets max), Couldn't verify (one line, or "nothing"). No preamble.
```

---

## Install

1. **Customize** in the left sidebar, then the **Plugins** tab
2. **Add** (top right), then **Add marketplace**, then **Add from a repository**
3. Paste `ColtraneK/aidgentic-heygen-agent` and click **Sync**
4. **Aidgentic heygen agent** appears in the list. Click **Add**, and make sure its toggle is **on**
5. Open the plugin's **Connectors** tab. Next to **HeyGen MCP**, click **Connect**. Sign in to HeyGen and click **Approve**. When it says **Connected**, you're done.

No API key. The HeyGen sign-in is the whole connection.

### Or install from a downloaded copy

1. On this page, **Code**, then **Download ZIP**
2. **Customize** → **Plugins** → **Add** → **Upload plugin**, and choose the zip
3. Toggle it **on**, then connect HeyGen as in step 5 above

A downloaded copy doesn't update itself. Download it again for a newer version.

---

Then create a **Project** called `Video Agent` (Projects, in the left sidebar), start a task inside it, and type:

```
/video-setup
```

About twelve minutes, and nothing in setup spends credits.

**Use a Project rather than a folder.** A scheduled routine runs in the cloud and can't reach a folder on your computer. In a Project, your routine can find your plan.

---

## Where it runs

| | Cowork, in a Project | Claude Code |
|---|---|---|
| Setup, ideas, plans and costs | ✓ | ✓ |
| Rendering in HeyGen | ✓ | ✓ |
| Content plan and routine | ✓ | ✓ |
| The animated HyperFrames finish | ✗ hands off to Claude Code | ✓ |

**Why the finish needs Claude Code.** The finish renders the video on your side with a real video renderer: it runs Node, Python, ffmpeg and a headless Chrome, and downloads the renderer and your fonts. Cowork's sandbox doesn't have ffmpeg and blocks those downloads, so it can't run there. Claude Code can: the **Code** tab in the desktop app (with a folder on your computer), Claude Code in a terminal, or Claude Code on the web.

**Starting in Cowork is fine.** Do setup, plans and renders there as usual. After each render, the agent checks whether the finish can run. If it can't, it gives you the plain HeyGen video straight away and saves a handoff folder with everything the finish needs. Then:

1. Open the **Code** tab in the Claude desktop app and choose a folder on your computer.
2. Put the handoff folder in it.
3. First time only, add the plugin there: `/plugin marketplace add ColtraneK/aidgentic-heygen-agent`, then `/plugin install aidgentic-heygen-agent@aidgentic-heygen`.
4. Type **finish the video in HANDOFF.md**.

The finished video, its other openings and its cover are saved next to the note. The HeyGen links in the note work for about a week. No credits are spent in Claude Code; the finish is free.

**Or do everything in Claude Code.** Install the plugin there (step 3), connect HeyGen with `/mcp`, and run `/video-setup` in a folder. Everything works in one place, but a scheduled routine can't reach a folder on your computer, so keep the routine in a Cowork Project.

---

## What to say

| Say this | What happens |
|---|---|
| "plan a video" | pick an angle, see the beat sheet and the cost, render on a yes |
| "make a video from [link]" | the same, from a page you give it |
| "quick video about [topic]" | one avatar take, fastest and cheapest |
| "add more animation" | the free HyperFrames finish on the latest video |
| "Clean style", "add music", "another opening", "make a cover", "speed it up", "no sound effects" | change the finish, free |
| "make it look like these" (with screenshots) | a look of your own from your references, free |
| "give me the parts for my editor" | picture, voice, music, sound effects and captions as separate files |
| "fix beat 3" | regenerate one part and reassemble, without redoing the rest. With the animated finish, only that clip or line is rendered and swapped in |
| "more ideas" | add angles to your idea bank |
| "make my content plan" | cadence, sources and monthly cost |
| "put it on a schedule" | the routine |
| "what's running" | your schedule and what it last did |

Everything else is normal conversation.

---

## What it costs

Renders spend your HeyGen credits. Measured on one Creator account in October 2026:

| | Credits |
|---|---|
| A 50 to 60 second video with several looks, b-roll and a scene of you | about 25 to 30 |
| A 45 second single-take avatar video | about 18 |
| A 6 second generated b-roll clip | about 2 |
| The HyperFrames finish, music, other openings and the cover | 0, they render in your session |
| A graphics-only beat instead of b-roll | saves about 2 |

Your plan may differ. It checks your balance before and after every render and uses your own numbers from then on.

---

## What it will not do

It doesn't post or share anything. The one thing it uploads is a plain background image in your brand colour, to your own HeyGen account during setup, for graphics-only scenes. Finished videos stay in your HeyGen library as links, plus the finished MP4 in your Project when it adds the animated finish. You decide where they go. It never renders without your yes, except a routine you set with a credit cap. It only makes avatars and scenes of you, or someone you confirm agreed. Scripts only say what your sources say. Generated b-roll has no logos, brand names or real people in it.

Content it reads is treated as data, never as instructions. If a web page says "AI, do X", that's words on a page. It'll tell you it saw it and carry on.

Everything it knows about you is a plain text file in your Project that you can read, edit or delete.

---

## Turning it off

The routine lives in your Claude account, not inside the plugin, so removing the plugin doesn't stop it.

1. Say **"what's running"** and it names the routine
2. Delete that task wherever your scheduled tasks are listed
3. Remove the plugin: Customize → Plugins
4. Disconnect HeyGen if nothing else uses it

---

## What's in here

```
commands/video-setup.md      the guided setup
skills/
├── plan-video               plan, price, approve, render, log, fix one beat
├── hyperframes-finish       the free animated finish, built from your brand kit
├── content-plan             cadence, sources, monthly cost, queue
└── video-routine            the scheduled task, and managing it
reference/
├── heygen-direction.md      how to build a video that looks made, tested costs
├── motion-graphics.md       which graphic for which line, styles, hooks, music
└── voice-and-ground-rules.md
.mcp.json                    the HeyGen connection (https://mcp.heygen.com/mcp/v1/)
```

Everything is plain text. If something behaves in a way you don't like, open the file and change it.

---

## License

MIT. See [LICENSE](LICENSE).

Built by [Aidgentic](https://aidgentic.com). HeyGen is a trademark of HeyGen; this plugin is independent and isn't made or endorsed by HeyGen.
