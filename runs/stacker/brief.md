# Stacker change brief

## Problem and outcome

Add an offline Stacker cabinet to tink-arcade. Players lock a horizontally moving row onto the row below, lose overhang, and aim for the top. Keep the shared paper presentation and mechanical keyboard feedback.

Run `stacker`, ID `5688403e-f9e7-4cf2-a076-b6f7c7714986`, uses the existing light profile. This brief combines intent, design and implementation planning for the stage-3 definition gate. The coordinator reports that the operator said "yes" to starting a build at 2026-10-18T15:28:42Z. That instruction permits preparing this definition; it is not a recorded approval of these new definitions. No decision has been recorded.

The unchanged confirmed r1 input is `seed-contract.md`, SHA-256 `533a1cdc3ca6649d2f8f7e52ed05782c5b0f8a83b729559f87405f1c3c23162a`. Its operator-confirmed definitions remain in `seed-checks.json`. The original session remains read-only. Confirmation binds content, not authenticated identity or implementation approval.

## Acceptance criteria

1. Register exactly one noncredentialed cabinet titled `Stacker`, module `tink_stacker`, path `.`. The unchanged seed-1 command must eventually print `PASS Stacker`, launch, mute and return to the menu. A separate registration assertion must catch omitted registration; the existing menu check alone cannot.
2. Use `PaperRenderer` and the shared paper/ink/jade palette, ASCII blocks, persistent controls, clear progress and terminal-state messages. Seed-2 remains an actual operator style judgment, not a screenshot or worker assertion.
3. Use shared `KeyboardAudio` and existing credited samples. Successful lock uses `place`, loss uses `over`, top completion uses `clear`, and pause/resume/restart use `switch`. Automatic horizontal travel is silent. Sound starts enabled; mute cancels pending/active cues, unmute confirms, and `--no-sound` prevents backend creation. Audio failure must not stop play. Service audio on every frame, including paused, undersized and end-state frames, and close resources on every exit path. Seed-3 remains provisional until its actual prerequisites and activation evidence exist.
4. Horizontal movement and placement are skill-based and deterministic. Retain only the intersection with the previous row, discard overhang, lose on zero overlap, and automatically start the next moving row after successful placement. Reaching the top wins. No checkpoint, minor-win choice, payout, adaptive odds or hidden placement adjustment. Seed-4 remains provisional until its actual prerequisites and activation evidence exist.
5. Support Space/Enter to lock, P to pause/resume, R to restart, M to mute, and Q/Ctrl-C to quit. Start immediately without a start menu. Freeze under 80 x 30, allow mute/quit while small, preserve pause on recovery, and discard elapsed catch-up time. Restart preserves mute. Accept `--no-color`, `--no-sound` and nonterminal `--help`.

### Proposed calibration for definition review

These are new implementation proposals, not facts established by seed r1 or a claim of exact commercial-machine calibration. Use a 7-column, 15-row playfield, two character columns per block, initially three contiguous moving blocks. The first row locks without a supporting-row constraint. Thereafter carry forward only the surviving overlap width; do not add scheduled block loss. Begin each new row at an edge, alternate its initial travel direction by height, and reflect at board edges. Move one column per simulation interval, initially 240 ms, reduced by 12 ms per completed row to a 72 ms minimum. The interval depends only on height. Keep fractional elapsed time, accept at most one placement per input batch, lock the currently displayed position, and discard stalls above 250 ms rather than simulating unseen travel. Height and surviving blocks are the visible progress indicators; no currency or persistent score.

The operator must review these dimensions, speed curve, width rule and placement semantics. If later reference research contradicts the approved behavior, return a revised definition rather than silently changing gameplay. Recognizable feel and difficulty remain human observations.

## Constraints and exclusions

- Keep everything local on `claude/stacker-intake` in this isolated clone. No push, PR, merge or deployment at any point in this run. The coordinator's latest amendment supersedes the earlier draft-PR instruction.
- No product model calls, credentials, network-dependent play, new recordings, microphone access or loopback capture. Reuse bundled audio. Native playback progress and sample-level metering are not recordings; they still require an available intended output device and separate listening.
- Do not alter the locked seed proposals, expectations or session files. A later provisional activation adds only `activation: {cmd, cwd, evidence}` to the relevant imported item. Its original `expect` stays byte-for-byte unchanged as a string.
- Do not modify factory templates, verification policy, unrelated games, shared audio internals or sound assets as incidental work. Return shared-code changes for review if actually required.
- Do not fabricate decisions, operator observations or passes. Initial definition approval does not approve nonexistent activations or replace final seed-2/expect judgments.

## Approach

### Module boundaries

- `tink_stacker/engine.py`: rules only, no curses, audio, filesystem, network or wall clock. `Game` owns locked rows as ordered immutable tuples of occupied column indices, active row position/width/direction, fractional movement time, completed height and `playing/lost/won` state. Expose `advance(elapsed_seconds)`, `lock_row()` returning a placement result, `restart()` and a read-only snapshot. Placement results distinguish ordinary placement, loss and win; the UI maps them to cues. A single UI loop owns all mutations.
- `tink_stacker/ui.py`: `Controller.frame(now, rows, columns, keys, audio)` owns elapsed time, pause, resize and bounded input. `Renderer(PaperRenderer)` draws a centered 80 x 30 canvas, board, height/block indicators, visible sound state and overlays without hiding controls. Use a 60 Hz target and at most 32 input keys per frame. `run()` owns the `KeyboardAudio` context and returns a warning for reporting after curses exits.
- `tink_stacker/__main__.py`: CLI flags, terminal checks, curses wrapper and cleanup/error reporting. Keep an empty package initializer.
- `arcade_menu/games.json`: add Stacker with no credential requirement. `README.md` and `DESIGN.md`: describe the reviewed rules, controls, layout, audio mapping and evidence limitations.
- `scripts/check_stacker_tests.py`: rerunnable test-discovery tool. Default runs all repository tests, requires nonempty Stacker engine/UI/audio groups and all named required tests to pass, and reports existing opt-in native skips. `--rules` selects the required Stacker rule tests; `--sounds --require-native` selects the required Stacker audio and native integration tests, requires macOS and native opt-in, and fails on missing tests, import errors, unavailable audio or any skipped required test. Never treat zero discovery or native skips as acceptance.
- `scripts/check_stacker_terminal.py`: POSIX PTY exercise of the real CLI, normal controls, pause, undersizing/recovery, restart, mute, Q and SIGINT, terminal restoration and menu-compatible presentation. No injected game state or clock; default no-sound mode for nonhardware checks, with mocked audio coverage separately. Retain transcript under this run's output directory, not another run.

### Ordered slices and stops

1. Write this definition and worker checklist; dry-run them now; stop for actual definition review. Missing proposed modules, runners and registration are expected dry-run failures, not a test-first success claim.
2. Only after a current operator-recorded stage-3 approval, open stage 3 in the isolated checkout. Write deterministic rule and sound regression tests before implementation. Retain the initial missing-implementation failures. Build the smallest engine slice for overlap, overhang and zero-overlap loss; run it before adding progression or UI.
3. Add automatic progression and deterministic timing, then the shared renderer/controller/audio integration, CLI and registration. Preserve other cabinets and shared APIs. Reassess failures before extending the next slice rather than changing the accepted contract to fit code.
4. Prove regression sensitivity by temporarily reverting overhang retention, auto-advance, Stacker cue dispatch and per-frame audio servicing independently. Each corresponding test must fail for its assertion, not an import/setup error. Restore protection, rerun and retain logs/diffs. An absent module on the first red run does not replace these meaningful red probes.
5. Once prerequisites really exist, present actual proposed activation objects, exact commands, results and red-probe evidence for seed-3 and seed-4. Add only reviewed activation fields and stop for renewed definition approval because activation changes the gate digest. No activation is installed by this brief. Also request the operator's seed-2 comparison with existing cabinets, actual sound listening on the intended output device, seed-1 expected-output observation and seed-4 recognizable-play observation. Never make those observations on the operator's behalf.
6. Only after renewed definition approval and real operator observations, have the operator record required seed attestations. Complete worker marks with actual evidence, commit candidate changes when authorized, and run `python3 _system/scripts/sdlc.py verify stacker`. Verify must execute seed-1 and both activated commands plus the worker/configured checks, and require seed-1-expect, seed-2, seed-3-expect and seed-4-expect attestations. Pending proposals are not complete acceptance evidence. Missing sound hardware or listening evidence blocks completion; no skip-based substitute. Stop locally, with no push or PR.

## Proposed provisional activations for review only

The following commands and tests do not exist yet. These are precise proof targets for definition review, not activations, prerequisite evidence or execution claims. Preserve the original record's `kind`, `missing`, `source`, `statement`, `cwd` and `expect`. At the later activation gate, supply real `evidence` naming files and retained observed red/green output. Do not insert a placeholder evidence string into `seed-checks.json`.

### Seed-3, sounds

Proposed activation command and cwd, with the unchanged locked expectation shown for review:

```json
{
  "cmd": "env -u TYPESAFE_API_KEY NEON_TETRIS_AUDIO_TESTS=1 python3 -B scripts/check_stacker_tests.py --sounds --require-native",
  "cwd": ".",
  "expect": "Successful Stacker actions produce appropriate audible mechanical cues across repeated plays; mute and --no-sound suppress playback as specified; unavailable audio does not prevent play; resources are released on exit. Repeated playback advances and sample levels are nonzero; listening confirms quality on the intended output device."
}
```

`expect` above is not an activation key or an automated output matcher. It remains the original seed expectation and requires a real operator attestation for `seed-3-expect`.

Required file `tests/test_stacker_audio.py`, class `StackerAudioTests`:
- `test_lock_loss_and_win_dispatch_shared_cues`
- `test_automatic_travel_and_frozen_gameplay_are_silent`
- `test_audio_tick_runs_each_frame_including_pause_resize_and_end_states`
- `test_mute_cancels_pending_and_active_cues_and_unmute_confirms`
- `test_no_sound_never_creates_backend_and_m_cannot_enable_it`
- `test_unavailable_audio_keeps_game_playable_and_reports_warning`
- `test_audio_closes_on_quit_sigint_and_exception`
- `test_restart_preserves_mute_without_reloading_samples`

Required file `tests/test_stacker_native_audio.py`, class `NativeStackerAudioTests`:
- `test_stacker_action_cues_advance_and_meter_on_spaced_repeats`
- `test_stacker_action_cues_advance_and_meter_on_rapid_repeats`
- `test_stacker_playback_resumes_after_mute_and_closes_voices`

Native tests must drive the Stacker controller's real action-to-KeyboardAudio path and its frame servicing, not call a disconnected generic sample player. Check playback position advances and peak sample level exceeds -80 dB on repeated cues, using bundled samples and AVAudioPlayer metering, without recording. Removing Stacker cue dispatch must fail a cue test; removing frame `audio.tick()` must fail the servicing test and the native action-path check. Native mode must fail, not skip, when prerequisites are absent. The operator names the intended output device and listens separately; metering is not listener acceptance.

### Seed-4, real-game play

Proposed activation command and cwd, with the unchanged locked expectation shown for review:

```json
{
  "cmd": "env -u TYPESAFE_API_KEY python3 -B scripts/check_stacker_tests.py --rules",
  "cwd": ".",
  "expect": "Moving rows lock according to fair skill-based timing; only overlapping blocks survive, overhang is lost, zero overlap ends the run, and successful rows progress automatically toward the top without a take-the-minor-win choice. Deterministic regression assertions cover these behaviors, and play inspection confirms recognizable Stacker feel."
}
```

`expect` remains the original seed expectation and requires a real operator attestation for `seed-4-expect`.

Required file `tests/test_stacker_engine.py`, class `StackerRuleTests`:
- `test_first_row_locks_without_support`
- `test_moving_row_reflects_at_both_edges`
- `test_lock_retains_only_overlap_and_discards_overhang`
- `test_next_row_width_equals_surviving_blocks`
- `test_zero_overlap_loses_without_advancing`
- `test_successful_lock_automatically_starts_next_row`
- `test_top_row_wins_without_checkpoint_or_payout_choice`
- `test_height_only_speed_curve_and_identical_elapsed_inputs_repeat`
- `test_restart_restores_initial_state`
- `test_legal_timed_input_replay_reaches_top`

Required file `tests/test_stacker_ui.py`, class `StackerUITests`:
- `test_lock_uses_displayed_position_once_per_input_batch`
- `test_pause_and_small_terminal_freeze_without_catchup`
- `test_resize_recovery_preserves_prior_pause`
- `test_end_states_ignore_placement_and_restart_is_available`
- `test_bounded_input_does_not_starve_update_or_render`

Use explicit column sets for overlap expectations, timed legal inputs for a full climb, and independent expected positions at boundaries. Reject a solution that changes placement odds based on history, wins or target completion. The targeted overhang and auto-progression reversions must fail their named tests. Human play inspection remains necessary to accept recognizable feel; no claim of exact physical-cabinet timing is made.

## Risks and verification

- The external Stacker reference mentioned by the seed has no supplied URL and has not been read. The calibration above is offered for operator review, not reconstructed reference evidence. Reject or revise it at this gate if it does not match the intended game.
- Real output-device availability is unknown. Default mock tests cannot prove audible sound. Seed-3 activation will require usable macOS native playback here or a reviewed replacement command/environment; no microphone or real audio recording is permitted.
- The existing menu check can pass without a Stacker cabinet. The worker registration assertion deliberately fails that omission. Existing menu checks also expect enabled audio, so unavailable audio may be an environment blocker rather than a Stacker defect.
- Existing `_system/verification.json` runs general unittest discovery twice and Breakout help. Preserve it; add Stacker-specific coverage through the worker checklist and seed activations rather than weakening that policy. No project lint/type-check configuration was found in the root discovery.
- `checklist.json` contains supporting checks and attested engineering work only. Locked seed checks and actual operator judgments remain separate and stronger acceptance obligations.
- No source or test code is changed before this definition-review stop. Read `checklist-dry-run.log` as a preimplementation diagnostic, never as verification or approval.

## Definition review

Review this whole brief, `checklist.json`, unchanged `seed-contract.md` and `seed-checks.json`, and the generated `checklist-dry-run.log`. Specifically accept or change the proposed calibration/controls, module boundaries, side effects and timeouts of every command, the exact seed activation proof targets above, hardware/listening requirements, expected missing-implementation failures, the light profile, and the local-only scope. Do not approve unknown actual activation evidence now.

Only the actual operator records the stage-3 definition decision with their own reviewer name, real review reference and reason. The worker must not invoke `decide`. After actual activations are added, this definition gate must be renewed before verification.
