# Session controls

Restart resets play; mute changes sound; Q and SIGINT restore the terminal.

## Sub-features

Restart resets play; mute changes sound; Q and SIGINT restore the terminal.

## How to get to it (user POV)

Launch `python3 -B -m tink_snake --seed 1`. R or r; M or m; Q or q; Ctrl-C.

## Driving it with the terminal script

Preconditions: Python curses and a POSIX host.

Run `python3 -B scripts/check_snake_terminal.py`. The transcript shows seeded restart, mute status, exit code 0, original terminal modes, and no surviving child group.

## Gotchas

The script sends SIGINT directly to simulate Ctrl-C because the PTY slave has no controlling session. An unavailable audio status is not playback proof.
