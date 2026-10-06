# Tron vs Jev — retro

## Outcome
Added `--versus-jev` to Tron: Jev steers player 2 by choosing among app-enumerated 16-step routes while both cycles keep moving; thinking time counts, with no scripted fallback. Reuses `neon_tetris.jev`; "Tron vs Jev" menu cabinet flagged as billed. Stacked on the Tron run (PR #16). PR and merge: see `closure.md`.

## Evidence and its limits
**Automated (passed in `verify`):** 36 new tests (routes 11, pilot 15, UI/CLI 10) and a real-PTY check with a fixture client; the full suite is 329 tests with the same 2 pre-existing skips; Tetris vs Jev is unchanged and its prompt is compared byte-for-byte to the text on `main`. Mutation checks: 10 deliberate pilot bugs plus 2 PTY-check bugs were injected; all caught (one defensive guard needed a direct test first).

**Live measurement (with Jon's go-ahead, 2026-10-05):** 6 sequential requests to real `jev-1.13.0` built from realistic boards: all valid, 0.19-0.29 s (median 0.23 s) against a 0.90 s early-request budget and a 1.44 s route, about 3x margin, so the constants were left as proposed. Cost about $0.0008 for the six. Limits: one machine, a small sequential sample, and reported input tokens took only two distinct values across six different payloads, which I could not explain, so the cost estimate may not track payload size. It says nothing about the quality of Jev's moves.

**Human (Jon, chat):** said both Tron games are good and agreed to record that. He did not say whether he played against real Jev, which levels he used, or whether slow replies cost Jev rounds, so the attested mark says only that.

## Failures and repairs
- My first pilot tests hung: the human cycle drove into Jev's straight route and the round ended, so a loop waiting on the plan never finished. The rig parks the human cycle and loops are bounded.
- A checklist command I wrote into the *approved* brief was wrong (the Tetris race tests only import in discover mode). Fixing it meant editing an approved definition, which made the approval stale; Jon re-approved the one-line change, and nothing else in the checklist moved.
- The result overlay said "THE MACHINE" for Jev; found by writing the PTY check, fixed.
- Test-harness mistakes (patching `time.sleep` globally, replacing `sys.stdout` after patching it) cost a few iterations; none touched product code.

## Manual interventions
Jon approved the brief, re-approved the checklist fix, and authorised the live calls; the marks for play feel and latency carry exactly what he said or what was measured.

## Deviations from the approved brief
Turn steps {2,4,6,8,10} instead of up to 12 (12 would exceed the 60-route cap and silently drop routes); room count excludes the cycle's own cell; next-round opening is prefetched while the result shows. All listed in `handoff.md`.

## What made the next change harder or easier
Easier: the shared Jev client, worker and cost classes were reusable with a one-parameter change. Harder: drafting checklist commands without running them first. A command that does not run cannot be fixed without re-approval.

## Smallest justified next step
Merge, then play more against real Jev to see whether it wins rounds on merit or by the other cycle's mistakes, and whether a longer or shorter route changes that. Possible small tooling idea, not yet justified by a second occurrence: a way to dry-run checklist `check` commands before the approval gate.
