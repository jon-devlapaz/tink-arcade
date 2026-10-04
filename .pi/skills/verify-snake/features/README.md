# Snake verification map

Use a POSIX host with Python curses. The script launches each instance in its own
PTY. It needs no authentication, ports, game-state fixtures or external service.
Audio is optional for terminal checks; native playback has its own required check.

- [Steering](steering.md) covers arrows, WASD, queued turns and collision.
- [Pause and resize](pause-resize.md) covers frozen timers and recovery.
- [Session controls](session.md) covers restart, mute, quit and terminal restoration.

Run `python3 -B scripts/check_snake_terminal.py` from the checkout root for every
entry. Evidence stays in `runs/snake/04-test/output/terminal-transcript.txt`.
Report failed or unreachable paths instead of treating another path as proof.
