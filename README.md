# Tink arcade

Small terminal games for Python 3.11 or newer. Play offline in a terminal at least 80 columns wide and 30 rows tall. macOS and Linux provide the required standard-library curses support.

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
