# Paper Invaders retrospective

## Outcome

Delivered [PR 7](https://github.com/jon-devlapaz/tink-arcade/pull/7): a solo terminal game with three lives and three earned formations, using the existing paper/jade style and sounds. It depends on checker-fix PR 6. Neither PR was merged by this run. Human play, difficulty and listening remain pending.

The approved scope passed all six installed tink-sdlc checks. The full suite passed 153 tests with two declared opt-in audio skips; both native playback checks passed separately. Actual terminal checks and twenty inspected reconstructions of curses cells passed. The independent reviewer found no actionable defects, reran the software, terminal and native checks, completed twenty legal winning replays, and checked 60,000 randomized UI frames. Linux and macOS CI passed at reviewed head eaaab79. Final delivery status is also saved with the independent archive.

## What worked

- The planner finished before the one human approval. The builder used the accepted brief without a stale-approval repair.
- Fresh planning, building and review sessions continued from saved files. Independent checks used their own output paths and preserved build evidence.
- Real terminal capture caught a resume-key race after initial tests had passed. The fix and regression are committed; failed capture evidence remains available.
- Existing style and audio were reused without changing other games or introducing a shared game framework.

## What still needed help

The coordinator opened stages, supplied the installed skill command's missing JSON flag, resolved contradictory stage-4 instructions, inspected captures, copied review evidence, opened the PR, selected dashboard work and archived the run. This demonstrates supervised delivery, not a self-contained or unattended factory.

The optional routed skill was refused as unapproved. No payload was read and no trust setting was changed; installed SDLC contracts governed the work. Arcade PR 6 and the local Substrate dashboard fixes were used. Tink PR 94 and SDLC draft PR 43 were not installed, so this run does not validate those repairs in use.

The HTML capture sheet introduced dark row gaps absent from the actual curses cells. Visual inspection caught the evidence-display error; regenerating HTML from unchanged cells corrected it. A preview can be wrong even when the application is correct. These captures do not establish native Terminal font/palette behavior. Audio metering does not establish perceived sound quality.

## Decision and next step

Consolidate the existing fixes before adding another layer to Substrate. Review and reconcile the pending source patches, then test a deliberate dependency refresh in a separate change. Preserve the small saved-file handoffs and separate review outputs. This trial does not justify importing every used skill, adding a dispatcher or rewriting the workflow.

Jon's next step is to play and review PR 7. Merging its dependency, retargeting and rechecking the game PR remain separate delivery work requiring merge authority. Save this run independently for later comparison; do not overwrite earlier trials.
