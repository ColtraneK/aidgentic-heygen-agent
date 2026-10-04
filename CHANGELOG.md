# Changelog

## Unreleased

- `hyperframes-finish`: a new skill that turns a finished Studio render into a branded motion-graphics cut (kinetic headlines, counters, UI mock-ups, checklists, captions, logo outro, no letterboxing). It reads colours, logo and fonts from the brand kit, and it's built and rendered locally with HyperFrames, so it spends no credits. `plan-video` runs it after the render when the profile's Finish says HyperFrames.
- Fixing one scene of a finished video no longer re-renders the whole thing. `swap.py` puts a single regenerated b-roll clip, or a single re-recorded avatar line, into the finish. For a new line it re-splices the narration and moves the later timings and captions to match. Only that clip or line spends credits, and edits to on-screen text are free.

## 1.0.0 · October 2026

First release, for the HeyGen community workshop in New York on October 6.

- `/video-setup`: connects HeyGen, reads your website, builds your brand kit, picks your presenter looks and voice, drafts your idea bank
- `plan-video`: beat sheets with several looks, generated b-roll and a scene of you; a cost and a yes before every render; measured credits logged after; fix one beat without redoing the rest
- `content-plan`: cadence, sources, monthly cost, queue
- `video-routine`: a scheduled task that plans, or renders under a credit cap, your next video
- HeyGen connection bundled, sign in only
