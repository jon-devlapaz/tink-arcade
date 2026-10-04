# Steering

Arrows and WASD steer with two queued turns. Walls end play.

## Sub-features

Arrows and WASD steer with two queued turns. Walls end play.

## How to get to it (user POV)

Launch `python3 -B -m tink_snake --seed 1`. Arrow up then left; uppercase S; lowercase w.

## Driving it with the terminal script

Preconditions: Python curses and a POSIX host.

Run `python3 -B scripts/check_snake_terminal.py`. The transcript shows the first and second queued directions on separate moves, then WASD movement and GAME OVER.

## Gotchas

Reverse turns do not move immediately. Automatic straight movement is silent.
