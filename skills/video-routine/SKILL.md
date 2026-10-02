---
name: video-routine
description: Put the person's video content plan on a Claude scheduled task that plans, or renders under a credit cap, the next video on its own, and manage it afterwards. Use when they say "put it on a schedule", "run this every week", "make it automatic", "schedule my videos", "what's running", "what's scheduled", "pause my video routine", "change the day", "raise the cap", or "stop the routine". Never runs inside a scheduled run.
---

# Video routine

One scheduled task that keeps the content plan moving without them. Created here, in a session with the person in it, never from inside a scheduled run.

Read first: `${CLAUDE_PLUGIN_ROOT}/reference/voice-and-ground-rules.md`, then `Video Profile.md` and `Content Plan.md`. No `Content Plan.md`: run the `content-plan` skill first.

---

## The one fact that governs this

**Every scheduled run is a fresh session that remembers nothing.** It has the prompt you write and the files in the Project. So the prompt names the Project, names every file, names the skill, states the mode and the caps, and says what to do when something's missing. "Make my weekly video" is a note to someone who isn't there.

And a scheduled run in the cloud **can't reach a folder on their computer.** It needs a Project. If they're in a folder, say so and stop: *"A schedule needs a Project to find your plan. Start a task in a Project, run `/video-setup` there, and we'll set this up."*

---

## 1. Two choices

Clickable, one at a time.

**Mode:**
- **Plan only** (recommended to start): every run drafts the next video's beat sheet and cost and saves it. Nothing renders. They open Claude, read it, and say "render it".
- **Render under a cap**: every run plans and renders, but only if the cost fits under a per-video cap and a monthly cap they set. Over the cap, it plans and waits.

Recommend plan-only first. *"Start with it planning, and once you've approved a few and trust them, switch it to render on its own."*

**When:** offer three times on their cadence day, for example Monday 8am / Tuesday 8am / Thursday 8am, plus "another time". Use their timezone from `CLAUDE.md`.

For render mode, two more clickable questions: **per-video cap** (30 / 40 / 60 credits) and **monthly cap** (offer the plan's monthly cost from `Content Plan.md`, half of it, and double it). Say each in plain words back to them.

## 2. Write the prompt

Fill this in completely. It's the whole brief the future run gets.

> **Workspace:** the Claude Project named `[Project name]`. Read `Video Profile.md` first, then `Content Plan.md`, `Content Angles.md` and `Video Log.md`. Use the `plan-video` skill from the `aidgentic-heygen-agent` plugin and follow its *Inside a scheduled routine* section exactly.
>
> **Profile wins:** where this prompt and `Video Profile.md` or `Content Plan.md` disagree, the files are current and this prompt is out of date.
>
> **Mode:** [Plan only: plan the next video and save it, do not render anything.] / [Render under a cap: plan the next video; render it only if the top of the cost estimate is at or under [n] credits and the month's renders logged in `Video Log.md` plus this one stay at or under [n] credits; otherwise save the plan and note why.]
>
> **Which video:** the first angle in the **Queue** in `Content Plan.md` whose status is `idea`. If none are left, draft five new angles from the sources in `Content Plan.md`, add them to `Content Angles.md` and the queue, then plan the first.
>
> **When something's missing:** HeyGen not connected, save the plan anyway and say at the top of the run's summary that HeyGen needs reconnecting. A source page won't load, use the next source. Never skip the run.
>
> **Never:** ask a question, post or share anything, email anyone, or create, change or delete any scheduled task.
>
> **Finish with** a three-line summary: which angle, planned or rendered (with the link and measured credits), and the one thing worth checking. Timezone: [tz].

If they've connected an email tool and want a heads-up, add: *"Email that summary to [their address] only, and nowhere else."* Confirm the address with them first.

## 3. Create it

Use this session's scheduled-task tool. If it isn't loaded, look for it by searching your tools for "schedule". Name it **Video routine · [Business]**.

**Approval setting.** A routine that has to stop and ask for permission while no one's there just stalls. Tell them, in one line, to set the task to approve its own actions: *"In the task's settings, turn on automatic approval, or it'll pause waiting for a click no one's there to make. The credit cap is what keeps it in bounds."* For plan-only mode, nothing spends credits, so this is safe.

**If there's no scheduling tool**, give them the prompt in a copyable block and the manual steps: open **Scheduled** in the sidebar, start a new task, paste the prompt, choose the frequency, turn on automatic approval.

Then confirm what's set, naming the schedule: *"Set. Every Tuesday at 8am it plans your next video and saves it here. Nothing renders until you say so."* Update **Routine** in `Content Plan.md`.

Then offer a test, once: *"Want me to run it once now so you can see what Tuesday will look like? In plan mode it costs nothing."*

---

## Managing it

- **"What's running":** list the routine by name, its schedule and mode, its caps, and what the last run did (from `Video Log.md` and `Video Plans/`).
- **"Pause" or "stop":** turn the task off with the scheduling tool, or tell them where to turn it off. Update **Routine** in `Content Plan.md`. Never delete it unless they say delete.
- **"Change the day", "raise the cap", "switch to render":** update the task's schedule or prompt and `Content Plan.md` together, and confirm the new setting back in one line.
- **One routine per Project.** If they want a second cadence (Quick clips on top of the weekly piece), put both in the one prompt rather than making a second task.

## Turning it off for good

The schedule lives in their Claude account, not in the plugin, so removing the plugin doesn't stop it. Tell them the order: say "what's running", delete that task, then remove the plugin.
