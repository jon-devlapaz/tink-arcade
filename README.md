# Tink arcade

Offline terminal games using Python's standard library.

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
`neon_tetris/sounds/credits.json`. Unavailable audio leaves the game playable.

Run `python3 -B scripts/check_snake_tests.py` for all game tests and
`python3 -B scripts/check_snake_terminal.py` for real terminal checks. The latter
plays sounds when audio is available and writes only Snake's transcript under
`runs/snake/04-test/output/`. Native sample metering requires macOS and
`NEON_TETRIS_AUDIO_TESTS=1`. Metering does not replace listening.

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
Sample credits remain in `neon_tetris/sounds/credits.json`.

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
