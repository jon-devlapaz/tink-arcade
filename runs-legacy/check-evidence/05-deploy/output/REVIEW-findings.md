# Independent review: check-evidence

Result: **clean — no actionable defects found.**

Reviewed on 2026-10-04 at HEAD `8f9e888`, against base `2125a67`.
Implementation: `f03e20d`; verification/handoff: `a101b43`.
One review covered logic, acceptance criteria, output paths, and cleanup. The change
is limited to two terminal checkers, documentation, tests, and run evidence, so
separate specialist passes were not warranted.

## What was checked

- Read root instructions, installed SDLC rules, stage 05 contract, review policy,
  approved brief/checklist, accepted baseline review, test lock, handoff, and current
  verification. Status reports stage 3 approved, all six checklist items passed,
  and current verification.
- Inspected the complete implementation diff. Game packages, workflows, installed
  contracts, and verification policy are unchanged. Existing terminal assertions
  and cleanup remain in place.
- Confirmed the accepted baseline SHA-256 is still
  `8cffa5d26fbff6a751c8c9ea2f1ae88f84a55a215fe884f93c2b1018627a216a`.
- Reviewed the movement predicate: it checks the first two head movements from
  the input checkpoint, requires one cell up followed by one cell left, and checks
  matching directions. It does not require the transient pending-turn snapshot.
- Supplemental tests explicitly contain left-then-up head movement and reject it.
  They also reject direction changes without movement. The original baseline's
  early/delayed cases and missing-turn controls remain intact.

## Independent verification

`python3 -B scripts/check_snake_tests.py` passed all 121 tests in 26.744 seconds,
with two expected optional native-audio skips. This discovery includes all nine
checker tests: the four locked baseline tests and five supplemental tests.
Output: `review-tests.txt` in this directory.

Both full terminal scripts passed, each invoked with `--output` pointing to a
separate file in this review directory:

- `review-snake-terminal.txt`
- `review-breakout-terminal.txt`

Their transcripts confirm Q/SIGINT exit, restored terminal settings, and no
remaining child process group, along with their existing gameplay checks.
The original Snake and Breakout transcripts still match the base revision byte
for byte.

The compatibility tests run default, relative, and external paths with spaces
and missing parents in temporary copies. They check preservation of the default
file, help and invalid arguments, and nonzero exit with a retained transcript
on an injected assertion. An additional independent failure probe started each
real child game, injected the first text-assertion failure, and verified that
cleanup reaped the child and removed its process group while retaining the
selected transcript. Output: `review-failure-cleanup.txt`.

## Limits and skills

These checks ran on macOS. Linux CI and independent human code-owner approval
remain external release requirements. Native-audio playback was skipped. This
review does not measure live scheduling failure frequency or prove every possible
filesystem failure. Pong remains the separate follow-up described in the brief.

Read `principle-prove-it-works` and the stage pick `principle-build-the-lever`
through the serialized wrapper with `--json --payload`. They led to rerunning the
committed tests and real terminal checks, preserving separate review output, and
checking failure cleanup directly. No implementation, existing evidence, approval,
or other worktree was changed; no commit, push, PR, or merge was performed.
