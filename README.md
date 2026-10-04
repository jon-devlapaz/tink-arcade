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
