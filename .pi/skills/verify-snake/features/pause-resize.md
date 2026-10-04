# Pause and resize

Pause and undersize freeze the snake and remaining timer.

## Sub-features

Pause and undersize freeze the snake and remaining timer.

## How to get to it (user POV)

Launch `python3 -B -m tink_snake --seed 1`. P or p; resize below 80 by 30; restore to 80 by 30 or 100 by 35.

## Driving it with the terminal script

Preconditions: Python curses and a POSIX host.

Run `python3 -B scripts/check_snake_terminal.py`. The transcript shows unchanged snake and timer across pause and shrink, preserved pause on recovery, and resumed movement.

## Gotchas

Only mute and quit work below the minimum. Time spent undersized must not cause catch-up.
