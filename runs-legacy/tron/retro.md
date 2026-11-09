# Tron — retro

## Outcome
Added offline terminal Tron to tink-arcade: best-of-five light cycles against a three-level machine opponent, or a second human with `--two-player`. Menu cabinet, README and DESIGN docs included. PR: filled in at delivery (see `closure.md` for the merge). This run was also the first real use of tink-sdlc 1.20.0 in tink-arcade.

## Evidence and its limits
**Automated (all passed in `verify`, receipt under `04-test/output/`):** 52 new tests (engine 27, machine opponent 10, UI 15) and a real-terminal check; the full arcade suite is 293 tests with 2 pre-existing skips; every cabinet passes the menu check. Mutation checks: changing the win threshold is caught by the terminal check; a machine that never steers was *not* caught by my first tests and is now caught by a new engine test.

**Human (Jon, reported in chat, not independently verified):** played single player and said it felt "pretty good, like genuinely good", later that both games were good; answered "yes" when asked if he listened to the sound. Which levels and modes he played, which device he listened on and what he heard were not stated, so both attested marks carry those limits in their evidence.

**Not measured:** level strength beyond a simulation I ran (hard beat normal and easy 600-0 each, normal beat easy 583-17, side-swapped, mirrored start). That hard may be too strong for people is untested. No fresh-machine run.

## Failures and repairs
- First draft of the AI-vs-AI test ran 43 s and never finished: two identical machines from mirrored starts draw every round. The test now pits different levels; it does not affect play.
- Round header said the *next* round while a result was showing; fixed with a test.
- Layout: the approved 38x20 grid takes 78 of 80 columns, so the proposed right-hand panel could not fit. Kept the grid, replaced the panel with a scoreboard row, recorded in `handoff.md` and DESIGN.md. This is a deviation from the approved brief.
- A pre-created local branch named `tron` made `stage tron 3` refuse; renamed it. The launcher's message named the cause.
- A scratch `sed -i` ran without a suffix on macOS and a mutation test silently did not run; redone with Python.

## Manual interventions
Two human gates held as designed: Jon approved the brief in chat (receipt recorded with his words as the source), and no mark was recorded for the two attested items until he reported on them. I did not approve or mark anything on his behalf.

## tink-sdlc 1.20.0 in practice
- **#46 (status next-action):** exercised for real. A genuine `verify` failure on unmarked attested items printed `Next: Checklist incomplete: ...` instead of "implement the approved brief".
- **#47 (early delivery warning):** *did not fire*, because this checkout has `origin` and a signed-in `gh`. So the incident it was built for is still unexercised outside the unit tests.
- **#45 (closure record):** this retro and `closure.md` follow the substrate guide it now points at.
- Upgrading tink-arcade to 1.20.0 left eight earlier runs reading stale. That is by design, but a completed run reading "stale" is noise.

## What made the next change harder or easier
Easier: the Snake harness (PTY check, trace file, renderer base) made the terminal check cheap. Harder: unittest import quirks across the suite (some modules only import in discover mode), which cost a hung test and later a broken checklist command in the follow-on run.

## Smallest justified next step
Merge, then play more: especially the `hard` level, which may need an easier setting between normal and hard. No workflow change is justified by one successful run; the stale-after-upgrade noise is worth an issue only if it recurs.
