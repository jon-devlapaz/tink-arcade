# Handoff: breakout-session-best

## The user's request (verbatim, from the dogfood brief)

> Change: show a session-best score in tink_breakout, the way tink_snake does (`SESSION BEST`
> in the HUD, updated when a game ends, kept across restarts within one run of the program,
> not saved to disk). Follow Snake's existing pattern instead of inventing a new one.

> Use Features and Futures: deliver this one behavior, check it, and stop. Don't add new
> orchestration, approval systems or refactors.

## Constraints from the user

- Change only tink-arcade, on branch `breakout-session-best` and its PR. Merge only on the user's word.
- No saved scores (nothing written to disk), no new orchestration or refactors.
- The SDLC upgrade to 1.21.0 (stations) rides in this PR; the user authorized `--upgrade-sdlc`.

## Seed

None. Seed Me triage: an ordinary execution request with a stated spec, so no interview and no seed.
Stage 1 is opened without `--seed-contract`.

## Facts checked by the coordinator (2026-10-07)

- Snake keeps `best` on the engine: `tink_snake/engine.py:13` sets `self.best = 0` in `__init__`, before
  `restart()`, so restart keeps it; `tink_snake/engine.py:75` does `self.best = max(self.best, self.score)`
  each time the score rises. The HUD shows `SESSION BEST` (`tink_snake/ui.py:52`); the trace includes `best`
  (`tink_snake/ui.py:154`). Tests: `tests/test_snake_engine.py:14` and `:74`.
- Breakout: `tink_breakout/engine.py` `Game.__init__` calls `restart()`; score rises by 10 per brick in
  `_step`. `Controller` (`tink_breakout/ui.py`) keeps one `Game` for the whole program and calls
  `game.restart()` on R. The HUD is one line at row `oy + 3`; `snapshot()` feeds the optional trace.
- `README.md` Breakout section says "There are no ... saved scores"; Snake's section says "Session best lasts until exit."
- tink-arcade has no GitHub Actions (removed in 883e31e). Local checks: `scripts/check_breakout_tests.py`,
  `scripts/check_breakout_terminal.py`.

## Labelled defaults (coordinator's choices, not the user's; shown in the brief for approval)

1. Update rule follows Snake: `best = max(best, score)` whenever a brick scores, not only at game end.
   The user's wording said "updated when a game ends", but also "follow Snake's pattern"; Snake updates live.
   At game end both give the same number.
2. HUD placement: `SESSION BEST nnn` (3-digit, like SCORE) on row `oy + 2`, left-aligned with the HUD line,
   because appending it to the existing HUD line would overflow the 62-column play box.
3. Add `best` to `Game.snapshot()` so the trace records it, as Snake's trace does.
4. One README line in the Breakout section, matching Snake's wording.

## Log

- 2026-10-07: run prepared, setup committed (155c8e4). Stage 1 opened by the coordinator.

## Stage 1 (plan)

- Wrote `brief.md` and `checklist.json` (7 items: 4 new unittest ids, README check, both Breakout scripts, 1 attested HUD look).
- The four labelled defaults are carried into the brief as defaults, awaiting the human's approval.
- Skill pulls: 0 skills pulled (only `blast-radius` listed, not fired); no skill changed a decision.
- Checked: `oy + 2` already carries the subtitle at `ox + 30`; the new text ends at `ox + 24`, so no overlap. Existing restart test (`snapshot()` equality) is unaffected by adding `best`.
- Build must add tests: `BreakoutEngineTests.test_session_best_tracks_score_and_survives_restart`, `...test_snapshot_reports_session_best`, `BreakoutUITests.test_hud_shows_session_best`, `...test_restart_key_keeps_session_best`.
- Not approved; the human records the stage 3 gate.

## Stage 3-4 (build and test)

- Code commit ec3816a: `Game.best` (set before `restart()`), `max(best, score)` per brick, `best` in `snapshot()`, `SESSION BEST nnn` on row `oy + 2` at column `left`, README line "Session best lasts until exit." Four new tests added and confirmed failing on the unchanged code first.
- Checks: 333 tests pass under both discovery loaders (2 audio skips); `check_breakout_tests.py` and `check_breakout_terminal.py` pass; `verify` passed; 7/7 checklist items.
- HUD attestation (30x80 fake screen): row 2 holds `SESSION BEST 070` at cols 9-24 and the subtitle from col 30; row 3 SCORE line unchanged. No overlap.
- Note: `check_breakout_terminal.py` rewrites the tracked `runs/breakout/04-test/output/terminal-transcript.txt`; I restored it with `git checkout` so it is not in this change.
- README: the earlier sentence "restarting resets everything" is slightly at odds with the new line (best survives restart); left as the brief specified.
- Stage 4 pull sheet: 0 of 4 triggers fired; 0 skills pulled. No skill changed a decision.
- Not approved; independent PR review remains.
