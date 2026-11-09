# Invaders independent review

## Result

No actionable defects found. This review does not approve release or establish human acceptance of the game.

Reviewed on 2026-10-04 in the separate review checkout at HEAD `eaaab7918473262610a18dd13bf5955ae434bf89`, against base `773a2dcc1c3fb8c5f585854b5584c4cc03908cbc`. Application candidate is `cf629a1f817488d8b7fa903b9782d6890965701f`; subsequent commits contain run evidence. No application files differ between that candidate and review HEAD. The launcher's generated deployment rules are the only tracked working-tree change. This reviewer did not edit them.

Live status before and after testing reported stage 3 approved, six checklist items passed, and verification current. The saved verification binds candidate digest `4dd018462347f2020a6e505a57724f66dc1b19fda75ebd97ff9f489d8ca84780`. Existing verification evidence was preserved; this review did not invoke `verify` or write new approval receipts.

## Scope and independent checks

Read AGENTS.md, installed SDLC and stage-5 contracts, shared review policy, approved brief/checklist, build handoff, actual diff, engine, UI, CLI, replay, terminal helper, tests, CI workflow and documentation. One review covered this small local game. No additional reviewers were needed.

The audit challenged swept shot collisions during marches and descents; simultaneous ship/final-enemy hits; shared lives and survivor recovery; all wave transitions; bounded movement/fire; surviving bottom shooters; pause and resize clocks; repeated Space; the repaired resume-input behavior; legal replay; and helper failure handling. Existing games, sound files, factory runtime and verification policy have no changes in the diff.

Independent outputs are in `independent-review/` beside this file:

- `software.txt`: full checker passed 153 tests in 26.812 seconds, including 14 engine and 13 UI tests, legal replay, and helper rejection tests. The two opt-in native-audio skips are explicitly listed. Tests exercise missing/skipped/failed required groups, required replay, explicit output, retained partial failure transcripts, cleanup and optimized-Python assertion behavior.
- `terminal.txt`: actual curses PTY passed color/monochrome, supported/undersized dimensions, controls, moving shots, repeated Space, complete frozen-state comparisons, pause/resize recovery, restart, Q/SIGINT, terminal-mode restoration and process cleanup. This is a separate explicit output destination.
- `native-audio.txt`: independently reran both opt-in native playback tests on macOS; both passed in 6.362 seconds with no skips.
- `invariants.txt`: independently ran the legal controller with seeds 0 through 19; every run won with 340 points and three lives. Also exercised 60,000 randomized legal UI frames with movement, firing, pause, restart, mute, supported/undersized dimensions and delayed frames. Checks covered score/life/wave ranges, unique enemies, enemy/ship bounds, shot cap, terminal-state consistency and unchanged game snapshots while undersized. These bounded checks supplement the committed tests; they do not prove all possible input sequences.

The required `principle-prove-it-works` payload was read through the serialized wrapper with `--json --payload`; it led to direct PTY and native playback reruns. The optional stage-5 pick named `ai-native-sdlc`. Its wrapper mount returned `unapproved`, delivering no payload. No approval, installation or library repair was attempted; installed contracts governed this review.

## Limits and next step

The coordinator's twenty viewed HTML reconstructions of actual curses cells remain the visual evidence. This reviewer did not independently view those images and does not claim native Terminal pixel inspection. Font/palette behavior and projectile appearance retain the limits recorded in the handoff. Native metering is not human listening. Jon's play feedback, difficulty/fairness and perceived sound quality remain unobserved.

Remote CI, authenticated code-owner approval and deployment were not checked by this local review. No source, prior evidence, approval, commit, push, PR or merge was made here. The coordinator can prepare the requested PR against the confirmed base and complete the retrospective. A changed candidate requires fresh verification and review of the change; human merge authority remains separate.
