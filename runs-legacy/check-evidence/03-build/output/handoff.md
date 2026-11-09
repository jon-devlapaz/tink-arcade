# Build and verification handoff

Candidate commit: `f03e20d` on `fix/arcade-check-evidence`.

## Changes

- Snake's arrow check reads trace history from the input checkpoint. It requires the first two observed head movements to be one cell up and then one cell left, with matching directions. It no longer requires both pending turns to appear together in a trace frame.
- Both terminal scripts parse `--output PATH`, create parent directories, resolve relative paths from the caller's working directory, and print the full destination. Omitting the option keeps the original file destinations. Failure transcripts still use the existing cleanup path.
- README documents separate external review destinations.
- The accepted baseline file is unchanged. Supplemental tests reject actual left-then-up movement and direction changes without movement, exercise real default/relative PTYs in temporary copies, check help/errors, and inject a terminal assertion to check failure output and nonzero exit.

## Evidence

`python3 -B -m unittest discover -s tests -p 'test_terminal_check*.py' -v`
passed all nine focused tests. See `04-test/output/focused-tests.txt`.
The first attempt is retained separately. Its four failures came from the new
test comparing `/var` with macOS's resolved `/private/var` path. The scripts
completed those PTYs successfully. The test now compares resolved paths.

`python3 _system/scripts/sdlc.py verify check-evidence` passed after the candidate
commit. The accepted baseline passed all four tests. Both full runners passed
121 tests, with two optional native-audio tests skipped in each. Both real PTY
scripts passed their existing controls, pause, restart, resize, applicable mute
and collision checks, Q/SIGINT, terminal restoration, and child-group cleanup.
See `04-test/output/test-log.md`, the two terminal transcripts, and
`04-test/output/verification.json`.

The attested compatibility item records the actual focused test and scope
inspection results. `04-test/output/scope-check.txt` records unchanged hashes for
the original Snake and Breakout transcripts and the locked baseline. Game
packages, installed contracts, verification policy, and CI workflows are unchanged.
Status after verification reports stage 3 approved, checklist 6/6, verification
current, and independent review next.

## Limits and follow-up

These runs were on macOS. Linux remains for CI. The controlled real-loop tests
prove the delayed-trace case, not a measured live scheduling failure rate.
Native-audio playback tests were skipped and were outside this helper repair.
Failure-output coverage injects an assertion after starting a real child game.
It does not cover every operating-system or filesystem failure.

Pong is absent from this base revision. Its output option remains a dependent
follow-up after PR 5 is available in an authorized checkout. This run did not
change PR 5, push, open a PR, merge, or enter stage 5. The coordinator owns the
independent review and PR steps.

## Skills

All skills were read through the serialized SDLC wrapper with `--json --payload`.
`principle-build-the-lever`, also the stage-open pick, led to the committed
supplemental tests so reviewers can repeat the compatibility and negative checks.
`principle-prove-it-works` led to real PTY runs, explicit transcript inspection,
and SDLC verification against the committed candidate. `unslop` guided the README
and this handoff toward plain descriptions of behavior and limits. No skill or
installed workflow contract was rewritten.
