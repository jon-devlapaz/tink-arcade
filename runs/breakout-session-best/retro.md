# Retro: breakout-session-best (delivery)

## Outcome

PR https://github.com/jon-devlapaz/tink-arcade/pull/19 is open and not merged. Breakout now shows `SESSION BEST nnn` above the
SCORE line. The best updates each time a brick scores, as Snake's does. It survives R, lasts only for the
current program run, and appears in the optional trace. The PR also carries the tink-sdlc upgrade from 1.20.0
to 1.21.0 (stations), which the user authorized.

## Evidence and its limits

- The `sdlc.py verify` receipt in `04-test/output/` passed. The checklist is 7/7: 6 automated items and 1 attested HUD look.
- Independent review is in `05-deploy/output/REVIEW-findings.md`. It found no Important issues and 3 Nits.
- The repo has no GitHub Actions (they were removed in 883e31e), so `gh pr checks 19` reports no checks. All
  evidence comes from this machine. The stage-5 "current required CI" gate cannot be met here.
- The attested HUD mark used a mock 30x80 render. The reviewer also confirmed the row in the real PTY
  transcript, but only with a best of 000.
- No human playtest. The user has not looked at the HUD.

## Human decisions (separate from automated checks)

- The user authorized `--upgrade-sdlc` up front and approved it again when the auto-mode classifier blocked
  the agent. The coordinator then ran `prepare`.
- The user approved the brief with "A" (as written, including 4 coordinator defaults), relayed by the coordinator.
- Merge is pending the user's decision.

## Failures, repairs, manual interventions

- `prepare --upgrade-sdlc` was blocked by the harness permission classifier, then refused once because
  tink-skills CI was still running. It succeeded on rerun.
- `prepare` leaves the checkout on `main`. The coordinator created the run branch by hand.
- The prepared stage prompt's wrapper command only works from the package directory.
- The PATH/bytecode environment workaround (patch-log P-014) was needed for every test run.
- `scripts/check_breakout_terminal.py` dirties a tracked transcript file on every run.

## Stations (skills loaded at stage open)

Pull sheets for stages 1, 3, 4 and 5 are in `skills/`. In all four, 0 triggers fired and 0 skills were pulled.
The reasons are structural:

- The shipped tables match web file types and tags only.
- `prepare` cannot set tags.
- Stage 3 opens before any code exists.

Stations had no effect on this run, good or bad.

## What made the next change easier or harder

- Easier: copying Snake's pattern made the change four lines of code, and the planning brief was concrete
  enough that the build needed no clarification.
- Harder: the entry and stage-prompt friction listed above. That friction is recorded in the factory
  patch log, not fixed here.

## Smallest justified next step

Merge or not, as the user decides. Optionally, a one-line README fix for the "restarting resets everything"
wording (review Nit 1), shown to the user first. No workflow change in this repo is justified by this run.
