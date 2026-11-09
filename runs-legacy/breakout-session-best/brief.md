# Change brief

## Problem and outcome

Breakout forgets how well you did: restart (R) wipes the score and nothing remembers the best run.
Outcome: `tink_breakout` shows `SESSION BEST` in the HUD, kept across restarts within one run of the
program, and never saved to disk, copying `tink_snake` (engine `best` attribute set before `restart()`,
`max(best, score)`, `SESSION BEST` in the HUD, `best` in the trace). Request from the user: deliver this
one behavior, check it, and stop. No new orchestration, approvals, or refactors.

Not in scope: saved scores, other games, any change outside tink-arcade. The SDLC 1.21.0 upgrade
already rides in this PR (user-authorized `--upgrade-sdlc`).

## Acceptance criteria

1. The Breakout HUD shows `SESSION BEST nnn`, starting at 000.
2. Best rises with the score and is never lowered; pressing R resets the score but keeps best.
3. Best lives only in memory for one program run; nothing is written to disk.
4. `Game.snapshot()` (the trace) includes `best`; existing physics/restart checks still pass.
5. README Breakout section says session best lasts until exit.
6. Local checks below pass. There is no GitHub Actions CI (removed in 883e31e), so verification is local.

## Approach

Files to change: `tink_breakout/engine.py`, `tink_breakout/ui.py`, `tests/test_breakout_engine.py`,
`tests/test_breakout_ui.py`, `README.md` (Breakout section). Nothing else.

- engine.py: `Game.__init__` sets `self.best = 0` before `restart()`; where a brick adds 10 to the score
  in `_step`, also `self.best = max(self.best, self.score)`; add `best=self.best` to `snapshot()`.
- ui.py: in `Renderer.draw`, one extra line `SESSION BEST {g.best:03}` at row `oy + 2`, column `left`.
- Tests mirror Snake's (`tests/test_snake_engine.py` lines 14 and 74): two engine tests, two UI tests.
- README: one line in the Breakout section, matching Snake's "Session best lasts until exit."

Defaults (the coordinator's proposals, not the user's decisions; please confirm or change):

1. **Default: live update.** `best = max(best, score)` each time a brick scores, as Snake does, not only
   at game end. The request said "updated when a game ends" but also "follow Snake's pattern"; Snake
   updates live. At game end both give the same number.
2. **Default: HUD placement.** `SESSION BEST nnn` (3 digits, like SCORE) on row `oy + 2`, left-aligned
   with the HUD line, because appending to the existing HUD line would overflow the 62-column play box.
   Row `oy + 2` also holds the subtitle at column `ox + 30`; the new text spans columns `ox + 9` to `ox + 24`, so they do not overlap.
3. **Default: trace.** Add `best` to `Game.snapshot()`, as Snake's trace does.
4. **Default: README.** One line in the Breakout section, Snake's wording.

## Risks and verification

Risks are small: a new key in `snapshot()` (the existing restart test compares `snapshot()` to a fresh
`Game().snapshot()`, which still matches because best only changes when a brick scores; the terminal
script compares only its own `GAME_KEYS`) and a crowded HUD row (checked by the UI test and a human
look at 80x30). The skill pull sheet fired no skills; none changed a decision.

Checks, run locally (no CI): the checklist items in `checklist.json` (four new unittest ids, a README
check, both Breakout scripts, one attested HUD look); the project checks in `_system/verification.json`
(full `unittest` discovery twice with different loaders, and `python3 -B -m tink_breakout --help`); and
the README's local checks, `python3 -B scripts/check_breakout_tests.py` and
`python3 -B scripts/check_breakout_terminal.py`.
