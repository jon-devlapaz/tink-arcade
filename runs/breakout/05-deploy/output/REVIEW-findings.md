# Breakout independent review

Date: 2026-10-04

## Result

No actionable Important findings in the reviewed candidate. This is an agent review, not human release approval.

Reviewed HEAD `c778a750606ac8fc48ffb690ce0a9f90471ea448` against local `origin/main` `c83dd829aa47c1b4e8baf2f3833327e6cfd77e7a` in the separate review checkout. Remote freshness and forge status were not checked. Existing Tetris source and tests have no changes relative to that base.

## Scope and evidence

Read the root instructions, stage-5 contract, review policy, installed SDLC guide, selected skill receipt, approved brief/checklist, handoff, and live runtime status. Reviewed the engine, layouts, input/timing/rendering, launcher, tests, PTY harness, CI workflow, documentation, and candidate diff. One focused review covered this small offline game; no additional reviewers were dispatched.

Live status at both the beginning and end reported stage 3 approved, verification current, and no errors. All four checklist items passed: two automated and two attested. The two attestations predate the latest candidate and are flagged for possible rechecking. Their actual text still correctly records pending human playtesting and the builder's saved-file continuation; neither constitutes human game-quality acceptance.

Checks rerun on macOS 27.0.1 arm64 with Python 3.14.7:

- `python3 -B scripts/check_breakout_tests.py`: 93 tests passed, with two existing opt-in native-audio tests skipped. Required groups contained nine engine, two layout, and four UI tests. The deterministic replay cleared Gate, Chevron, and Islands at step indexes 16548, 19078, and 31474, with 760 points and three lives.
- The actual PTY harness passed movement, arrow input, launch, pause, resize while paused and playing, restart, quit, SIGINT, terminal restoration, and process-group cleanup. To preserve existing stage-4 evidence, the harness was loaded and executed in memory with only its transcript destination and final destination-print statement redirected to a temporary directory. No assertions or game behavior were changed; the temporary directory was removed afterward.
- An additional replay drove `Controller.frame` using only A/D and Space, retaining normal game physics and every brick. At 60 frames per second it won after tick 15737; at 30 frames per second it won after tick 11719. Both runs earned 760 points and retained three lives. This checks that clearability is not dependent on calling the engine's movement method at 120 Hz.

The added controller check used the existing replay's seed and aiming rule: seed 20261004; choose an offset uniformly from -3.8 to 3.8 whenever downward flight becomes upward flight; predict the paddle-height landing with wall reflection; issue A or D only when the target differs from the paddle by more than one cell; launch waiting balls. Each frame advances by exactly 1/60 or 1/30 second, with a 90,000-frame limit. No ball position, velocity, bricks, score, or lives were assigned by the controller.

Collision inspection and existing executable cases cover swept brick intersections, shared faces, corners, walls, paddle center/edges, high-speed crossings, one-time scoring, life loss, earned board changes, win/loss, and restart. Layout data matches the approved three patterns. Pause/undersize handling discards accumulated time and preserves an existing pause. The observation stream records state and does not supply simulation commands.

## Limits and release requirements

- Jon has not played this candidate. Difficulty, fairness, aiming feel, and layout interest remain unverified.
- Linux and GitHub-hosted CI were not executed in this review. The workflow selects Ubuntu and macOS with Python 3.11; local results use Python 3.14.7. Inspected the existing native-audio unit tests: they mock the Apple bridge rather than loading Apple frameworks during normal discovery. This inspection is not a Linux pass.
- The PTY harness sends SIGINT directly because its subprocess has no controlling terminal. It verifies signal handling and restoration, not physical Ctrl-C delivery by every terminal emulator.
- Full clearing was verified through the engine and input controller. The real PTY check exercises controls and lifecycle but does not play every board to completion.
- The review did not run native audio, check external branch protection or code-owner approval, merge, deploy, or inspect deployment health. Current required CI and independent human release approval remain external requirements.

## Skills and preserved state

Read `principle-prove-it-works` and the stage-picked `ai-native-sdlc` in full after mounting their missing ignored payloads with the installed serialized wrapper. The former led to rerunning the real terminal process and controller-level replay. The latter kept workflow evidence separate from release authority. Its older shell entry points were resolved against the installed guide: live status used `python3 _system/scripts/sdlc.py status breakout --json`.

No application code, stage-4 evidence, decisions, marks, or policy files were edited. The review checkout already contained the stage launcher's generated AGENTS.md change and stage-5 outputs. This findings file is the sole review deliverable; the checkout is preserved for the parent to transfer it.
