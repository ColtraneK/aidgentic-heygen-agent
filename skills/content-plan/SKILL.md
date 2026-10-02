---
name: content-plan
description: Build the person's video content plan, covering what gets made, how often, from which sources, and what it costs in HeyGen credits each month, then offer to put it on a schedule. Use when they say "make my content plan", "content plan", "how often should I post", "what would this cost", "plan my month", "video calendar", or "what should I make next".
---

# Content plan

A one-page plan they can keep: what gets made, on what cadence, from what source, and what it costs to run.

Read first: `${CLAUDE_PLUGIN_ROOT}/reference/voice-and-ground-rules.md`, then `Video Profile.md`, `Content Angles.md` and `Video Log.md` in their Project. No profile: point them to `/video-setup` and stop.

---

## 1. Three quick choices

All clickable, one at a time.

1. **How often?** Once a week / Twice a week / Every weekday / Twice a month
2. **From what?** Offer the sources you can see: their site's pages, their blog, a document they've shared, a list of FAQs, webinar or podcast transcripts. Multi-select, plus "something else" (typed).
3. **Which kind of video?** Directed (several looks, b-roll, a scene of you) / Quick (one take) / A mix: Directed for the main weekly piece, Quick for the rest

## 2. Work out the cost

Use measured costs from `Video Log.md` if there are any. Otherwise use the rates in `${CLAUDE_PLUGIN_ROOT}/reference/heygen-direction.md` and say they're estimates until the first renders are measured.

Call `get_current_user` for their plan and balance. Then:

- credits per video × videos per month = credits per month
- compare to their balance and what their plan gives each period
- if it doesn't fit, say so plainly and give the two ways to make it fit: fewer videos, or more Quick ones

## 3. Fill the queue

Line up the next 4 to 8 angles from `Content Angles.md` in a sensible order: the strongest proof first, alternating story, principle and how-to so the feed doesn't repeat itself. If there aren't enough, draft more from their sources first.

## 4. Write `Content Plan.md`

````markdown
# Content Plan

**Cadence:** [e.g. one Directed video every Tuesday]
**Sources:** [list, with links]
**Format:** [9:16 / 16:9 / 1:1], [length]
**Cost:** about [n] credits per video, [n] per month. Plan gives [n] per period. Balance on [date]: [n].

## Queue
| Order | Angle | Source | Route | Status |
|---|---|---|---|---|

## Routine
**Mode:** [Plan only / Render under a cap / Not scheduled]
**Runs:** [day and time, timezone]
**Caps:** [n] credits per video · [n] per month   *(render mode only)*

## Where these go
[Where they'll post or use them. They decide; this plugin never posts.]
````

Show it, then one question:

> Want this to run on its own? I'd set it to plan the next video every [day] and leave it for you to approve. Nothing renders until you say so.
>
> - **Yes, plan on a schedule**
> - **Yes, and let it render under a credit cap**
> - **Not now**

On either yes, run the `video-routine` skill. On "Not now", record it under **Already decided** in `Video Profile.md` and stop.
