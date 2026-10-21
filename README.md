# Tink arcade

Offline terminal games using Python's standard library.

## Arcade menu

Start every game from one menu:

```sh
./play            # or: python3 -m arcade_menu
```

Link it onto your PATH to run it from anywhere:

```sh
ln -sf "$PWD/play" ~/.local/bin/tink-arcade
```

Games are listed in `arcade_menu/games.json`; add an entry to add a cabinet.

### Adding a game

Shared pieces live in `arcade_common/`: `PaperRenderer` (palette, `text`, `box`)
and `KeyboardAudio` with the bundled sounds. A new game is a package with an
`engine.py` (rules, no curses), a `ui.py` whose `Renderer` subclasses
`PaperRenderer`, and a `__main__.py`. Then add it to `arcade_menu/games.json`.
Run every check locally with `python3 -B scripts/check_all.py`.
Tetris vs Jev needs `TYPESAFE_API_KEY` and makes billed API calls.

## Last Time

```sh
python3 -B -m tink_last_time        # or select cabinet 14 in ./play
python3 -B -m tink_last_time --seed 7 --no-color --no-sound
```

Steer a light with the arrow keys and collect `*` sparks. Every 15 seconds,
all your completed paths replay in sync as `()` ghosts. Touch any ghost and
your one life ends. Score is sparks collected. There are no other enemies.
The first round has no ghosts; by round five there are four.

Arrows set automatic movement, one cell every 100 ms. Walls stop you without
killing. Past paths loop at each round boundary while you keep your endpoint.
If a restarting ghost overlaps you, the light shifts to the nearest free cell,
preferring clearance from the next ghost step. This shift is recorded as the
next path's origin, not replay drift or immunity. A completely ghost-occupied
arena has no safe shift and ends the game.

P pauses, R restarts, M mutes, Q or Ctrl-C exits. Restart repeats a supplied
seed and preserves mute and session best. Scores are not saved. The fixed
30 by 18 arena needs an 80 by 30 terminal; larger windows add margins. Pause
and undersizing freeze all game clocks. Recovery preserves pause and discards
catch-up time. Mute and quit remain available while small. Stalls above 250 ms
are discarded. Player `<>`, sparks `*` and ghosts `()` differ without color.
The arena is the shared paper grid, like the other cabinets. Existing
keyboard cues mark sparks, death and pause/restart; travel is silent.

```sh
python3 -B scripts/check_last_time.py
python3 -B scripts/replay_last_time.py
python3 -B scripts/check_last_time_terminal.py
python3 -B scripts/check_last_time_red_probes.py
python3 -B scripts/check_all.py
```

The legal-input replay reaches round five with four ghosts and 82 sparks.
A second replay leaves the light at its first endpoint and loses to that path.
The real PTY check covers arrows, an actual 15-second transition and ghost
death, pause, resize, restart, color/monochrome, Q/SIGINT and terminal cleanup.
Mutation probes require assertion failures and restored green tests. These
checks do not establish fun, pacing, visual taste or perceived audio quality.
Those remain owed to jondev. Native-audio tests are opt-in and skip by default.
The game is offline, standard-library-only, and makes no API calls.

## Paper Stacker

```sh
python3 -m tink_stacker                 # or select Stacker from the arcade menu
python3 -m tink_stacker --no-color --no-sound
```

Stacker is appended as cabinet 13, preserving every existing cabinet's number.
Select it with Up/Down or `j`/`k` and Enter; digit shortcuts stop at 9.

Space or Enter locks the moving row. Only blocks overlapping the previous row
survive; no overlap ends the run. Successful placements automatically start the
next row. Reach row 15 to win. P pauses, R restarts, M toggles sound, and Q or
Ctrl-C quits. There is no checkpoint, payout, minor-win choice or hidden odds.

The 7-column board starts with three blocks. Motion reflects at each edge and
speeds up only with height, from 240 ms per column by 12 ms per completed row,
with a 72 ms minimum. A placement uses the currently displayed position, once
per input batch. These are this cabinet's reviewed rules, not an exact timing
claim about a commercial machine. No randomness or seed option is needed.

The shared paper/ink/jade canvas needs 80 x 30. Smaller windows freeze the game;
recovery preserves pause and discards catch-up time. Mute and quit work while
small. Restart preserves mute. `--no-sound` prevents audio setup for the session.
Shared bundled keyboard cues mark placement, loss, completion and pause/restart;
automatic travel is silent. Missing audio does not prevent play.

```sh
python3 -B scripts/check_stacker_tests.py
python3 -B scripts/check_stacker_tests.py --rules
python3 -B scripts/check_stacker_terminal.py --no-sound
NEON_TETRIS_AUDIO_TESTS=1 python3 -B scripts/check_stacker_tests.py --sounds --require-native
NEON_TETRIS_AUDIO_TESTS=1 python3 -B scripts/check_stacker_red_probes.py --native
```

The default test runner runs repository regressions and requires the named
Stacker engine/UI/mocked-audio tests to pass. Opt-in native checks require macOS,
play bundled samples through Stacker's action path and meter playback progress
and levels. They fail on absent prerequisites or skipped required tests. They do
not record audio or establish listener-perceived quality. Operator listening,
visual comparison and play judgment remain required. The PTY checker restores
terminal modes and writes only Stacker's transcript under
`runs/stacker/04-test/output/`. Red probes mutate disposable copies, require
assertion-level failures, restore protections and require green reruns.

## Breakout

Run from this checkout with Python 3.9 or newer on macOS or Linux:

```sh
python3 -m tink_breakout
```

Use a terminal at least 80 columns by 30 rows. `--no-color` selects monochrome;
`--help` also works outside a terminal. Native Windows is not supported.

| Key | Action |
| --- | --- |
| Left/right arrows or A/D | Move paddle |
| Space | Launch the waiting ball |
| P | Pause or resume |
| R | Restart from board one |
| Q or Ctrl-C | Quit |

Letter keys accept either case. A new life or board waits for Space. Shrinking the
terminal freezes play; enlarging it preserves an existing pause. Gameplay keys
are ignored while undersized. Quit still works.

Clear Gate, Chevron, then Islands. Each brick is worth 10 points. Progress requires
clearing every brick, for a total of 760 points. Three lives cover the entire run.
Losing a life keeps your score and cleared bricks; restarting resets everything.
There are no power-ups, sound, saved scores, network requests, or speed increases.
Session best lasts until exit.

The field is fixed at 60 by 20 cells. The paddle is nine cells wide and moves two
cells per key event. The ball travels 18 cells per second, with simulation steps
of 1/120 second and at most 0.1 seconds accepted from a delayed frame. Paddle
contacts aim up to 60 degrees from vertical. A center hit is vertical. The ball is
a point for collisions; its `o` and brick outlines are ASCII approximations.

Collision checks cover the whole traveled segment. Tied brick contacts break each
contacted brick once; a corner reflects both velocity components. Extremely large
injected velocities stop consuming time after 32 contacts in a step. Normal play
uses a fixed speed far below that limit.

Jon's play feedback is pending. Automated clearing proves the boards can be
cleared; difficulty, fairness, and layout interest still need human playtesting.

## Verification

```sh
python3 -B scripts/check_breakout_tests.py
python3 -B scripts/check_breakout_terminal.py
```

The first command runs all Tetris and Breakout tests and requires nonempty
Breakout engine, layout, and UI groups. It reports skipped tests. The full-clear
replay starts a normal game and only moves the paddle, launches, and advances
simulation time. Its fixed seed is 20261004 and its limit is 180,000 steps.
It clears all boards in 31,475 steps with three lives and 760 points.

The second command runs the real curses application through a POSIX pseudo
terminal. It tests movement, launch, pause, resize, restart, quit, and the SIGINT
signal produced by Ctrl-C. It compares physics snapshots during freezes and on
recovery, then checks persistent terminal modes and process cleanup. On macOS,
the transient PENDIN input-retype flag is excluded from mode comparisons.

`TINK_BREAKOUT_TRACE=/path/to/file.jsonl` enables an optional observation stream
from the real terminal loop. It only records state, never changes it. The PTY
check creates a temporary trace and saves a readable transcript at
`runs/breakout/04-test/output/terminal-transcript.txt`. CI runs both checks on
macOS and Linux and uploads that transcript. Local evidence does not establish
that CI has passed.

The existing Tetris native audio checks are opt-in and skipped by default. Run
those separately on macOS with `NEON_TETRIS_AUDIO_TESTS=1` if audio testing is
wanted. Breakout does not use audio.

## Paper Wordle

```sh
python3 -m tink_wordle
```

Find the five-letter word in six tries. Type letters, use Backspace to edit, and press Enter to submit. Green means the letter is in the right place; jade means it appears elsewhere; dim means it is absent. The on-screen keyboard keeps each guessed letter's best-known state. `--seed` repeats answer selection, `--no-color` uses monochrome, and `--no-sound` disables audio. F2 restarts, F3 mutes, and Escape quits, so every A-Z key remains typeable. Wordle uses the shared paper, ink and jade palette and keyboard cues.

## Existing Tetris

```sh
python3 -m neon_tetris
```

Its controls and sounds are unchanged. See `python3 -m neon_tetris --help`.

## Paper Snake

Run `python3 -B -m tink_snake` in a terminal at least 80 columns by 30 rows.
Use `--seed 42` for repeatable food placement, `--no-color` for monochrome, or
`--no-sound` to disable audio for the whole session.

Arrows or WASD steer. P pauses, R restarts, M mutes, and Q or Ctrl-C exits.
Letter controls accept either case. Two turns can wait in the queue; each move
uses one turn. Reverse turns, repeated directions, and extra queued turns are ignored.

Eat food to grow and earn 10 points. Walls and your body end the game. Moving
into the departing tail cell is allowed. Filling the 20 by 20 board completes it.
Movement starts every 180 ms and speeds up by 15 ms per five foods, down to 75 ms.
Session best lasts until exit. Restart resets the game and repeats a supplied seed,
while preserving session best and mute. Shrinking below the minimum freezes play;
only mute and quit work until the terminal is large enough again.

Snake uses Tetris's paper, ink and jade palette and its existing keyboard recordings.
Automatic movement is silent. Turns click, food uses the clear cue, collision uses
enter, and pause/restart/unmute use the switch cue. Credits remain in
`arcade_common/sounds/credits.json`. Unavailable audio leaves the game playable.

Run `python3 -B scripts/check_snake_tests.py` for all game tests and
`python3 -B scripts/check_snake_terminal.py` for real terminal checks. The latter
plays sounds when audio is available and writes only Snake's transcript under
`runs/snake/04-test/output/`. Native sample metering requires macOS and
`NEON_TETRIS_AUDIO_TESTS=1`. Metering does not replace listening.

## Paper Pac-Man

Run `python3 -B -m tink_pacman` or select Pac-Man from `./play`. It requires
an **80 x 40** terminal, taller than the other games' 80 by 30 minimum.
Use Up/Down or `j`/`k` to select Pac-Man, cabinet 12 in the menu; digit shortcuts stop at 9.

Arrows or WASD steer automatically moving Pac-Man. Space places a Bookmark;
E erases the wall directly ahead when it is a thin, unprotected interior wall.
Each mechanic has one charge per life. Bookmark lasts four simulation seconds
or until a ghost reaches it, attracting chasing and scattering ghosts but not
frightened ghosts or eyes. Erased walls stay open until the level ends. Charges
refill after losing a life, not after clearing a level.

Eat dots and energizers, avoid live ghosts, and clear the maze to start the next
level. You have three lives and no extra lives. Dots score 10, energizers 50,
and frightened ghosts score 200, 400, 800 and 1600 in a chain. Restart resets
the run while preserving session best and mute. Scores are not saved.

`--classic` disables Bookmark and Eraser and hides their charges. `--seed 42`
repeats frightened-ghost choices, `--no-color` selects monochrome, and
`--no-sound` disables audio setup. `--help` works without a terminal. P pauses,
R restarts, M mutes, and Q or Ctrl-C quits. Letter keys accept either case.
Below 80 x 40, play freezes and only mute and quit work. Recovery discards
elapsed resize time and preserves an existing pause.

```sh
python3 -B -m unittest tests.test_pacman_maze tests.test_pacman_engine tests.test_pacman_ghosts tests.test_pacman_twist tests.test_pacman_ui tests.test_pacman_terminal tests.test_pacman_integration
python3 -B scripts/check_pacman_terminal.py
python3 -B scripts/check_arcade.py
```

The PTY check exercises steering, both mechanics, pause, restart, resize, mute,
classic/no-sound modes, Q and SIGINT, then checks terminal restoration and
process cleanup. It keeps a transcript at
`runs/pacman/04-test/output/terminal-transcript.txt`; `--output PATH` selects
another location. `TINK_PACMAN_TRACE` enables observation-only loop snapshots.
These checks do not establish visual quality, ghost-rule fidelity or remote CI
results; those still need review.

## Paper Tron

Run `python3 -B -m tink_tron` in a terminal at least 80 columns by 30 rows. By default
you play player 1 against a machine; add `--two-player` for a second human on the same
keyboard. `--level easy|normal|hard` picks the machine (default normal), `--seed 42`
repeats its tie-breaks, `--no-color` selects monochrome and `--no-sound` disables audio
for the whole session.

Both cycles move one cell every 90 ms on a 38 by 20 grid and leave a trail. A cycle that
leaves the grid or enters any trail or head loses the round. If both crash on the same
step, including a head-on or a swap, the round is a draw: nobody scores and it replays.
The match is best of five (first to three round wins). Space starts the next round.

Solo, arrows or WASD steer you. In two-player, WASD steers player 1 and arrows steer
player 2. One turn can wait per cycle per step, so two quick presses cannot reverse you
into your own trail. P pauses, R restarts the match, M mutes, and Q or Ctrl-C exits.
Shrinking below 80 by 30 freezes play until the terminal is large enough again.

The machine is offline and deterministic. It reads only the board, never your pending key.
Easy takes a random safe move. Normal takes the safe move with the largest reachable room,
so it avoids sealing itself in. Hard counts the cells it can reach before you can (a
Voronoi territory count) and takes the move that claims the most, using reachable room as
the tiebreak. No level moves into a wall or trail while a safe move exists.

Player 1 is `##` heads and `==` trails in jade; player 2 is `@@` heads and `::` trails in
ink, so the players differ without color. Audio reuses the existing cues: turns click, a
round win uses the clear cue, a loss or draw uses enter, and pause/restart use switch.

Run `python3 -B -m unittest tests.test_tron_engine tests.test_tron_ai tests.test_tron_ui`
for the rules, machine and presentation tests and `python3 -B scripts/check_tron_terminal.py`
for the real-terminal check, which writes only Tron's transcript under
`runs/tron/04-test/output/`.

### Tron vs Jev

```sh
python3 -B -m tink_tron --versus-jev --seed 1
```

Jev steers player 2. It needs `TYPESAFE_API_KEY` in your environment (never in source control) and every
match makes billed API calls, shown as an estimated session cost. It cannot be combined with `--two-player` or
`--level`; solo and two-player stay offline. Python 3.11 or newer is needed for the Jev client.

A model call takes seconds and a step is 90 ms, so Jev does not choose each move. The app lists up to 60 clear
16-step routes from Jev's cycle, with neutral facts (turns, open room at the end, distance to your head and to a
wall), and Jev picks one. The next route is requested while 10 steps of the current one remain and starts where it
ends. Nothing ranks the routes.

Jev's thinking time counts as play time. If a route runs out before the next reply arrives, Jev's cycle goes
straight, and if that is blocked it crashes: there is no scripted dodge, so a slow reply can lose a round. The
one exception is the start of a round, which waits for Jev's opening route (fetched while the previous result is
on screen) so Jev is never beaten before the first step. The subtitle shows what Jev is doing and the running cost.

A failed request holds both cycles and shows a short message; Enter retries, R restarts, Q quits. Nothing retries
silently. Replies that arrive after a restart or a new round never steer, but their reported usage still counts.
Only board state and route facts are sent; the key is read from the environment and never printed or traced.
Costs use the same input-token price as Tetris vs Jev, with no spending cap; unknown usage shows `+ unknown`.

`python3 -B scripts/check_tron_jev_terminal.py` drives the real program with a fixture client (no network, no key).
It never calls real Jev. Opponent strength and pacing need human playtesting.

## Paper Pong

Run `python3 -B -m tink_pong` with Python 3.9+ on macOS or Linux in an 80 by 30
or larger terminal. The court opens immediately. `--no-color` uses monochrome;
`--no-sound` disables sound for the session. `--help` works outside a terminal.
Native Windows is not supported. No dependencies or network access are needed.

Up/down arrows or W/S move the left paddle 1.5 cells per key event. Letter keys
accept either case. Space serves, P pauses or resumes, R restarts, M mutes, and
Q or Ctrl-C exits. Restart preserves mute. Pause freezes both paddles and ball.
Shrinking below 80 by 30 freezes the game and ignores gameplay keys. M and quit
still work. Restoring the size preserves a prior pause and discards elapsed time
from the resize. Quit restores terminal settings and closes audio.

First to seven wins. Each point resets both paddles and the ball to center and
waits for Space. The first serve goes toward the computer; later serves alternate
direction and vertical sign. The court is 60 by 20 cells with five-cell paddles.
The computer follows the ball's current height at no more than six cells per
second. It moves only during a rally and does not predict future bounces.

The ball travels at 24 cells per second. Top and bottom walls bounce it; a missed
ball crossing an end boundary scores one point. Paddle contact sets the angle,
up to 60 degrees from horizontal. A center hit keeps a small vertical component.
Physics uses a point ball, whole-segment contact checks, steps of 1/120 second,
and at most 0.1 seconds from a delayed frame. ASCII cells approximate these
continuous positions. Both scores, winner, and restart/quit controls remain visible
at match end; physics stops until restart.

Pong uses the same paper, ink and jade palette and credited keyboard sounds as
Snake and Tetris. Paddle contacts use `move`, points and wins use `clear`, final
loss uses `over`, and serve/pause/restart/unmute use `switch`. Wall bounces and
computer movement are silent. Missing or failed audio leaves the game playable.
Sample credits remain in `arcade_common/sounds/credits.json`.

### Pong checks

```sh
python3 -B scripts/check_pong_tests.py
python3 -B scripts/check_pong_terminal.py
PYTHONPATH=. python3 -B scripts/pong_replay.py
python3 -B scripts/capture_pong.py
```

The test runner checks every game's tests and requires nonempty Pong engine/UI
groups. The repeatable player wins 7–0 in 7,578 physics steps; an idle player loses
0–7 in 2,598 steps. Both start ordinary new matches and use only player input and
time. This establishes reachable outcomes, not human difficulty or enjoyment.

The terminal check launches the actual game through a POSIX pseudo terminal and
compares states during movement, serve, pause, resize, restart and mute. It checks
Q/SIGINT exit, persistent terminal modes and process cleanup. It saves only Pong's
transcript at `runs/pong/04-test/output/terminal-transcript.txt`. The optional
`TINK_PONG_TRACE=/path/to/file.jsonl` records loop state without changing gameplay.
The Pong CI workflow runs help, tests and terminal checks on macOS and Linux.
Local checks do not establish a CI result.

The capture script uses the actual curses renderer in a pseudo terminal, reads
its cells/attributes, and exports JSON, raw terminal output, and SVGs for both
sizes and color modes. Win/loss screens come from legal replays; these are render
checks, not live human matches. On macOS, `qlmanage -t -s 1600 -o OUTPUT FILE.svg`
can make PNG previews. They approximate terminal font rasterization.

Native playback/metering passes separately on this macOS trial host with
`NEON_TETRIS_AUDIO_TESTS=1`. Those two tests skip in the default suite. Metering
does not establish listener-perceived sound. Human play and listening remain
unverified.

### Save terminal checks separately

Both terminal checkers accept `--output PATH`. Relative paths use your current
working directory. Missing parent directories are created. Without this option,
Snake keeps its transcript under `runs/snake/04-test/output/` and Breakout under
`runs/breakout/04-test/output/`, both named `terminal-transcript.txt`.

For an independent review, choose files outside the checkout to preserve the
original run evidence:

```sh
python3 -B scripts/check_snake_terminal.py --output '/tmp/arcade review/snake.txt'
python3 -B scripts/check_breakout_terminal.py --output '/tmp/arcade review/breakout.txt'
```

On a failed terminal assertion, the selected file still contains the transcript
collected before cleanup, and the command exits with a nonzero status.

## Paper Invaders

```sh
python3 -B -m tink_invaders --seed 7
```

Clear Ranks, Wings and Islands with three lives shared across all waves. Every
one-hit enemy is worth 10 points; clearing all 34 enemies scores 340 and wins.
A wave advances only after its last enemy is destroyed. Losing a life preserves
survivors and score, resets their positions, clears shots and waits for Space.
If the ship and final enemy are hit together, the life loss applies first. Zero
lives always loses. Restart begins a new three-life run and retains mute.

Use Left/Right or A/D to move, Space to start or fire, P to pause, R to restart,
M to mute, and Q or Ctrl-C to quit. Letters accept either case. The first Space
starts without firing. Pause and undersizing freeze shots and every game clock.
Resize recovery preserves pause and discards catch-up time. While undersized,
only mute and quit work. A terminal of at least 80 by 30 is required; larger
windows add margins around the same 60 by 20 field.

`--no-color` uses monochrome. `--no-sound` prevents audio setup and cannot be
reversed with M. `--seed N` repeats the enemy attack sequence on restart.
Unavailable sound leaves gameplay intact and reports its warning on normal exit.
Movement uses the existing `move` click, fire uses `rotate`, life loss uses `over`,
wave clear and win use `clear`, and pause/restart use `switch`. The same audio
priority, samples, credits and native playback code serve the other games.

### Rules and timing

The ship moves one column at most every 55 ms, within columns 1 through 58.
There is one player shot, a 220 ms firing cooldown, and at most three enemy
shots. Player shots travel 32 rows per second; enemy shots travel 8. The formation
marches one column every 700 ms, reversing and descending one row at an edge.
Every 1.1 seconds a seeded choice of a surviving bottom enemy fires if the shot
cap permits it. All waves use that same pace. Formation columns start at
10, 17, 24, 31, 38 and 45; rows start at 2, 4 and 6. The ship is on row 18.

The simulation uses 1/60-second steps and accepts at most 100 ms per delayed
frame. Negative elapsed time is discarded; non-finite time is rejected. Whole
path collision checks include formation movement during the step. Opposing shots
pass through. A shot hits at most one enemy; several simultaneous ship hits cost
one life. The loop reads at most 32 keys per frame, so repeated Space cannot
starve time or drawing. No network, new dependencies, saved scores, bosses,
extra lives, bunkers or power-ups are involved.

### Invaders checks and captures

```sh
python3 -B scripts/check_invaders_tests.py
python3 -B scripts/replay_invaders.py
python3 -B scripts/check_invaders_terminal.py --output '/tmp/invaders-review/terminal.txt'
NEON_TETRIS_AUDIO_TESTS=1 python3 -B -m unittest discover -s tests -p test_native_audio.py
python3 -B scripts/capture_invaders.py --output '/tmp/invaders-review/80x30-color' --color
python3 -B scripts/capture_invaders.py --output '/tmp/invaders-review/100x35-mono' --columns 100 --rows 35
```

The full-suite checker requires successfully executed, nonempty Invaders engine
and UI groups and the legal full-run replay; skipped required cases fail it.
Existing opt-in native audio skips are listed. The replay uses seed 7 and a
36,000-step limit. Its deterministic controller only moves, fires, starts waiting
states and advances time. The observed engine run wins in 1,528 steps with three
lives and 340 points. This proves one clearable run, not enjoyable difficulty.

The terminal checker requires an explicit output path and retains partial failure
transcripts. It runs the actual curses process in color and monochrome, at 80x30,
100x35 and an undersized 40x12, checking clocks, input, recovery, Q/SIGINT and
terminal/process cleanup. SIGINT stands in for Ctrl-C because the PTY slave has
no controlling owner. macOS's transient PENDIN bit is excluded from mode checks.
CI runs the software suite and PTY on Linux and macOS; current local results do
not establish remote CI results. Native sample metering is a separate macOS check.

Captures use legal keys to reach ready, play, pause, win and loss in the actual
loop. The loss controller deliberately steers into normal enemy shots. An
optional `TINK_INVADERS_TRACE` path records state; `TINK_INVADERS_CAPTURE=1` adds
actual curses screen cells on state changes. Neither accepts game state or time
controls. Capture output includes raw ANSI, screen cells, a readable transcript
and an HTML contact sheet. HTML uses standard xterm colors and assumed dark
monochrome defaults; it does not reproduce a user's terminal font or palette.
Native metering is not listening. Jon's play feedback and actual listening remain
pending, so fairness, difficulty and sound quality remain unobserved.

## Paper Crossing

```sh
python3 -m tink_crossing            # --no-color, --no-sound, --help
```

Hop a marker from the bottom row through five road lanes, rest on the median,
then ride logs across five river lanes into one of five home bays. Needs 80 x 30.

| Key | Action |
| --- | --- |
| Arrows or WASD | Hop one cell |
| P | Pause or resume |
| R | Restart at level 1 with three lives |
| M | Mute or unmute |
| Q or Ctrl-C | Quit |

The board is 13 rows by 40 columns. Lanes are fixed patterns that wrap around and
alternate direction; there is no randomness. Lanes move one whole cell at a time
at 2-5 cells per second, checked every 1/120 s, so nothing can skip a cell. A car,
open water, being carried off either edge, or hopping into a filled bay or the
`^` wall costs a life and returns you to the start. Logs (`=`) carry you.

Each new furthest row in an attempt scores 10, a bay 50, and five bays clear the
level for 100. Levels 2 and 3 run every lane 1.25x and 1.5x faster. Clearing level
3 wins; three lives cover the whole game. A win without losing a life scores
2850; lost lives can add row points, because each attempt scores its rows again.

Checks: `python3 -B scripts/check_crossing_tests.py` (all tests, nonempty Crossing
groups), `python3 -B scripts/crossing_replay.py` (a legal-input win and loss),
`python3 -B scripts/check_crossing_terminal.py` (real curses process in a PTY; it
prints a SKIP line for mute when no audio player is available).
`scripts/capture_crossing.py` saves screens for visual review. Human playtesting
of difficulty has not happened yet.

## Formation shooter

```sh
python3 -m tink_galaga
```

Move with left/right arrows or A/D. Space fires. P pauses or resumes, R restarts, and Q or Ctrl-C quits. The game starts immediately. Hold a key to use your terminal's key repeat.

Shoot the rows of enemies and avoid their shots and diving attacks. You have three lives. A hit gives two seconds of protection, shown by a blinking ship. Clearing the formation starts a harder wave. Formation enemies award 100 points; diving enemies award 150. Game over shows your final score and lets you restart.

```sh
python3 -m tink_galaga --seed 17 --no-color
python3 -m tink_galaga --help
```

A seed repeats enemy choices for the same sequence of inputs and simulation ticks. Restart uses that seed again. Timing still depends on when you press keys. The game freezes when the terminal is too small, and tells you how to resize it. Long rendering stalls are discarded so the game does not simulate unseen time. Scores last only for the current game.

The game uses original ASCII graphics and newly written rules inspired by formation shooters such as Galaga. It includes no arcade ROMs, copied sprites, sound recordings, or third-party game code. It has no network calls, model charges, or credential requirements.

## Tetris

```sh
python3 -m neon_tetris
python3 -m neon_tetris --help
```

The existing Tetris game and its source remain unchanged by the formation-shooter work. The separate Tetris-versus-Jev feature is under review in PR 1 and is not included on this branch.

## Checks

```sh
python3 -B -m unittest discover -s tests
python3 -B scripts/check_galaga_terminal.py
```

The tests cover deterministic gameplay and input rules alongside the existing Tetris tests. The terminal script launches the actual curses application in a pseudo-terminal. It exercises keyboard input, pause, resize, resume, restart, and both exit paths. The GitHub Actions job runs both commands on the PR head with Python 3.11 and 3.14. Existing native-audio tests skip where the macOS backend is unavailable.

These checks establish behavior, not whether the game is enjoyable. Jon's play test remains needed for difficulty, controls, and visual taste.

## Current work

The Galaga trial's purpose, decisions, and evidence are under `runs/galaga/`. Start with its `handoff.md`; consult the installed runtime for current verification state:

```sh
python3 _system/scripts/sdlc.py status galaga
```

The shared tink-substrate view tracks this work separately. Its labels do not authorize a merge.

## Tetris vs Jev

Use Python 3.11 or newer on macOS or Linux and a terminal at least 80 columns by
30 rows. The game uses Python's standard library. No package installation is needed.

```sh
python3 -m neon_tetris
python3 -m neon_tetris --versus-jev --seed 1
```

Versus mode requires `TYPESAFE_API_KEY` in your environment. Set it through your
usual secret manager or shell setup; never put it in source control. Solo mode
works offline. Add `--no-sound` or `--no-color` if desired.

Both players receive the same sequence of pieces. First to clear 20 lines wins;
topping out loses. A simultaneous finish in the same update is a draw. Jev's
thinking time counts as play time. There is no artificial speed adjustment.

| Key | Action |
| --- | --- |
| Left/right or A/D | Move |
| Down or S | Soft drop |
| Up or X / Z | Rotate clockwise / counterclockwise |
| Space | Hard drop |
| C | Hold |
| P | Pause both boards |
| R | Restart both boards with the same seed |
| Enter | Retry after a Jev error |
| M | Toggle sound |
| Q or Ctrl-C | Quit |

A failed Jev request pauses both boards and shows an error. Retry is explicit.
An undersized terminal freezes both boards until it is large enough. Restarted
matches ignore earlier replies, but their reported usage still counts toward cost.

### Jev and cost

The opponent uses the TypeSafe API with the pinned `jev-1.13.0` model. Jev receives
only game state and legal moves. The app enumerates placements and describes their
results; Jev selects a move. There is no scripted fallback opponent.

The game displays estimated USD for the current app session, including rematches.
The estimate uses reported input tokens and the published rate of $0.042 per million
input tokens, with free output, checked on 2026-10-03. See the
[official model pricing](https://docs.typesafe.ai/models.md).
Prices may change; update the price table when adopting a new price or model.

There is no spending cap. Unknown usage or model pricing displays `+ unknown`;
an in-flight request displays `+ pending`. The final line after quitting includes
that uncertainty. Exiting does not guarantee cancellation of an already sent
request. Estimates are not invoice totals.

Opponent strength and pacing need human playtesting. Automated correctness checks
cannot tell us whether this is a good race.

### Check the game

```sh
python3 -B -m unittest discover -s tests
python3 -B scripts/check_terminal.py
# Calls real Jev and incurs usage:
python3 -B scripts/check_terminal.py --live
```

The terminal script exercises the actual curses program in a pseudo-terminal,
including input, pause, resize, restart, and exit. Native-audio integration tests
are opt-in; their skips are reported. Sound sample credits and CC0 provenance are
in `arcade_common/sounds/credits.json`.

### Work in progress

This feature is the first hunch-to-PR trial for tink-substrate. Current work and
remaining checks are in [the handoff](runs/play-against-jev/handoff.md).
The [build brief](runs/play-against-jev/brief.md) records the reviewed proposal;
its historical statements are not live status. Query current workflow evidence with:

```sh
python3 _system/scripts/sdlc.py status play-against-jev
```

The original solo design is recorded in [DESIGN.md](DESIGN.md).

Paper Wordle accepts guesses from the vendored [5-Letter-Words list](https://github.com/darkermango/5-Letter-words),
licensed under MIT; its notice is in [licenses/5-letter-words-MIT.txt](licenses/5-letter-words-MIT.txt).
The secret-answer list remains curated in `tink_wordle/engine.py`.

The installed workflow files in `_system`, `_shared`, `stages`, and the skillset
pins come from [tink-sdlc](https://github.com/jon-devlapaz/tink-sdlc), scaffold
1.35.0. The upgrade changes stage contracts, so older runs' approval receipts
read as stale until re-reviewed. Its [MIT notice](licenses/tink-sdlc-MIT.txt) applies to those files.
