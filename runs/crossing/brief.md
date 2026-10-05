# Paper Crossing

## Problem and outcome

Add an eighth arcade cabinet: a lane-crossing game in which the player hops a
marker up through road traffic and across a river on drifting logs into home bays.
Jon asked the operator (Claude, in Cowork) to dogfood the workflow end to end on
tink-arcade. The game choice, name and rules below are operator-proposed defaults,
not previously confirmed user choices. No Seed Me contract exists for this run.

## Acceptance criteria

1. `python3 -B -m tink_crossing` runs with Python 3.9+ on macOS/Linux using only the
   standard library in a terminal of at least 80 x 30. `--help` works without a
   terminal; `--no-color` and `--no-sound` work. A nonterminal launch exits 1 with a
   useful message. No network, no new dependency.
2. Board is 13 rows by 40 columns. Row 0 is the home row with 5 bays at fixed
   columns; rows 1-5 are river; row 6 is a safe median; rows 7-11 are road; row 12
   is the start. Lanes have fixed, deterministic patterns and speeds (at most 8
   cells/second), alternate direction, and wrap around. No randomness.
3. Arrows or WASD hop one cell (one row, or one column), clamped to the board;
   letters accept either case. A hop is instant. Touching a car, landing in water
   off a log, being carried off either edge, or hopping into a filled bay or the
   wall between bays costs a life and returns the marker to the start. Standing on
   a log carries the marker with it.
4. Scoring: +10 for each new furthest row reached in the current attempt; +50 for
   filling an empty bay. Filling all 5 bays clears the level (+100); levels 2 and 3
   run every lane at 1.25x and 1.5x speed. Clearing level 3 wins. Three lives cover
   the whole game. The score, lives, level, and the win or game-over state stay
   visible with restart and quit controls.
5. Simulation uses fixed 1/120 s steps and accepts at most 0.1 s from a delayed
   frame. Collision is checked every step, so nothing tunnels at the capped speed.
   An executable replay using only legal hops and elapsed time must win the game
   from a new game; a second replay must lose all lives. This shows both outcomes
   are reachable, not that difficulty has been playtested.
6. P pauses/resumes, R restarts at level 1 with 3 lives, M toggles mute, Q or
   Ctrl-C exits cleanly. Pause freezes all motion. An undersized terminal freezes
   play, ignores gameplay keys, shows resize guidance, and resumes without
   catching up elapsed time; M and Q still work. Quit restores terminal settings.
7. Uses `arcade_common.PaperRenderer` and `arcade_common.audio.KeyboardAudio` like
   Pong: hop `move`, bay filled or level cleared `clear`, life lost and game over
   `over`, pause/restart `switch`. Missing audio leaves the game playable. No new
   samples. Title reads `socratink / paper crossing`, inside a `PLAY / PAPER` box,
   so the existing menu check recognises it.
8. `arcade_menu/games.json` gains a Crossing entry. README gets a short Crossing
   section (launch, controls, exact rules, verification). The handoff and retro
   record tools used, failures and recoveries, and operator interventions.

## Approach

Add `tink_crossing/` with `engine.py` (rules, no curses), `ui.py` (Renderer
subclassing `PaperRenderer`, input loop with an optional observation-only
`TINK_CROSSING_TRACE`), and `__main__.py`, following `tink_pong`. Add
`tests/test_crossing_engine.py`, `tests/test_crossing_ui.py`,
`scripts/check_crossing_tests.py` (all tests; refuse empty Crossing groups; report
skips), `scripts/crossing_replay.py` (legal win and loss replays), and
`scripts/check_crossing_terminal.py` (real curses process through a PTY, adapted
from the Pong checker, transcript under `runs/crossing/04-test/output/`).

Build in a separate clone on branch `crossing`; main stays untouched until Jon
merges. No changes to other games, shared modules, factory files or
`_system/verification.json`.

## Risks and verification

- Legal-win replay needs a planner that waits for safe gaps; it must use only
  public hop and advance calls. Lane patterns are chosen so a win is reachable at
  1.5x speed; the replay proves it.
- The operator's sandbox is Linux with Python 3.10 and no audio player, not the
  macOS/Codex host Substrate targets. The baseline menu check
  (`scripts/check_arcade.py`) already fails here for every game because it expects
  `key sound on`. It is therefore an attested item to run on Jon's Mac, not an
  automated check in this run.
- PTY evidence must compare real trace states and restored terminal modes, not
  just printed labels. Visual review uses retained captures at 80x30 and 100x35, in
  color and monochrome. Human playtesting and listening remain unverified unless
  Jon does them.

Excluded: timers, turtles that dive, bonus items, saved scores, two-player,
difficulty menus, refactors of shared code, and other games.
