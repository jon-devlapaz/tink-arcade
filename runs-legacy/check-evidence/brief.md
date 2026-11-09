# Reliable terminal checks and separate review evidence

## Problem and outcome

Owner: **tink-arcade**. This light bug run, `check-evidence`, starts from
`2125a67b3ebef15e3f3a7acf292d116144fed9d6` in the isolated
`product/tink-arcade-check-evidence` checkout.

Snake's terminal check requires an intermediate trace containing both queued
turns. The real loop handles input, advances the game, then writes its trace.
When the input frame advances, the first turn has already been consumed. The
snake correctly moves up and then left, yet the checker times out. The saved
macOS CI attempt failed at this assertion; its last state had moved left to the
wall. That log supports an intermittent false rejection but does not establish
the exact scheduling of that CI process.

Both Snake and Breakout terminal scripts write to fixed paths under the original
game runs. Reviewers cannot select another destination through the CLI. An
unrecognized `--output` is currently silently ignored and the retained transcript
is overwritten. A successful review check should write only its selected file.

Outcome: keep the existing game behavior and meaningful checks, make the queued
turn check judge ordered movement, and allow an explicit transcript destination.
No game feature, audio, rendering, SDLC runtime, or shared template change.

## Acceptance criteria

1. Real up/left arrow input remains exercised. The queue check accepts correct
   up-then-left movement whether both pending turns appear in a trace or the
   first turn was already consumed. It requires ordered observations after input
   and rejects missing or incorrectly ordered turns; merely removing the queue
   assertion or accepting any movement is insufficient.
2. Both scripts accept `--output PATH`. Absolute paths outside the checkout and
   paths containing spaces work; relative paths follow the caller's working
   directory. Create missing destination parents. Print the actual destination
   without requiring that it be inside the checkout. Existing failure transcript
   writing and nonzero exit behavior remain intact.
3. Omitting the option preserves each script's current transcript location and
   existing CI usage. An explicit path leaves any existing default transcript
   unchanged. Document the option and an external review example.
4. Preserve the existing PTY checks for controls, pause, restart, resize,
   mute where present, collision where present, Q/SIGINT, terminal restoration,
   and process cleanup. Keep all existing game tests. No changes to game packages
   are planned or needed.
5. The accepted regression baseline passes after the fix, with its negative
   controls still rejecting bad turn sequences. Full tests and real terminal
   checks pass. Linux/macOS CI remains the cross-platform check; local macOS
   results alone do not establish Linux behavior.

## Approach

- Independently review `tests/test_terminal_checkers.py` and its recorded failure
  before the coordinator locks the accepted baseline. Do not implement before
  the human definition gate and accepted test baseline are recorded.
- Make the smallest change to `scripts/check_snake_terminal.py` that verifies
  ordered up/left movement from post-input states. Use trace history and head
  positions/directions; avoid another required transient queue snapshot.
- Add ordinary argument parsing to the two scripts for `--output PATH`, keeping
  their default paths. Keep failure output in the existing cleanup path. Avoid
  introducing a shared evidence framework for two small CLI changes.
- Add focused supplemental tests for relative/default paths, help/errors, and
  failure output if the implementation needs them. Do not edit the locked
  baseline after acceptance. Keep any added test helpers in `tests/` or `scripts/`.
- Run the approved checklist using run-specific output files. Review the diff
  for preserved existing assertions and unchanged game packages.

Pong is absent from this main revision. PR 5 remains a separate open game change.
Port the output option to its checker as a dependent follow-up after that code
is available in an authorized checkout. This run does not modify or merge it.

## Reproduction and evidence

Inspected: root `AGENTS.md`, `_system/SDLC.md`, `stages/01-plan/CONTEXT.md`,
`_system/verification.json`, both terminal and test runners, Snake engine and UI
loop, existing Snake UI tests, both workflow files, and `sdlc.py status
check-evidence` (stage 3 pending; no verification).

Source observations:
- `/Users/jondev/dev/active/factory/tink-substrate/docs/trials/pong.md`
- `/Users/jondev/.local/share/tink-substrate/notes/tink-arcade/pong/2026-10-04-snake-ci-37242009844-attempt1.txt`

Rerun from the checkout root:

```sh
python3 -B -m unittest discover -s tests -p test_terminal_checkers.py -v
```

Observed on the unfixed source: 4 tests, 3 failures in 8.579 seconds. Saved output:
`runs/check-evidence/01-plan/output/baseline.txt`.
- Delayed input frame: real Snake loop yields heads `[10,10]`, `[10,9]`, `[9,9]`.
  No frame contains both pending turns. Existing checker rejects it at the same
  queued-turn assertion as the saved CI failure.
- Early input frame passes the current checker. Missing/up-only/wrong-order
  input controls are rejected.
- Each full PTY script reports success in a disposable checkout, but overwrites
  the default evidence sentinel instead of honoring the requested external path.
  Original checkout transcripts remain untouched.

The queue reproduction controls frame time and replays the resulting full trace
through the existing checker's `main` and `Terminal.wait`. It does not fake game
rules or discard trace frames. It is not a deterministic live-PTY reproduction
of the historical scheduler, a measured flake frequency, or a cross-platform
proof. Real terminal checks remain required after repair.

## Risks and verification

A weaker movement assertion could hide lost/reordered keys. Keep the negative
controls and independently challenge the final checker. The baseline replay
uses the current script's queue-check interface; the builder should keep that
small interface or raise any incompatibility before changing locked tests.

The project verification config only runs Breakout help, so the checklist adds
actual suites and both PTY scripts. Default-output compatibility must be tested
in a disposable checkout so retained run evidence is not overwritten. Human
play feel or audio-device approval is not required for this test-helper repair.

Required skill used: `principle-build-the-lever`, obtained with
`tink mount principle-build-the-lever --payload --json` because the generated
active-file pointer was absent. It led to the rerunnable baseline test file.
No skill state, factory reference, game code, or approval receipt was changed.
