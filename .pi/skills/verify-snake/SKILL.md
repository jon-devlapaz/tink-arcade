---
name: verify-snake
description: Verify Paper Snake terminal controls, resize recovery and cleanup through its real POSIX pseudoterminal script.
---

# Verify Snake

## Launch

From the repository root run `python3 -B -m tink_snake --help`. No build or package
installation is needed. Each drive creates its own terminal and child process.
Interactive launch is `python3 -B -m tink_snake --seed 1` in an 80 by 30 terminal.
Quit with Q. The scripted drive owns and closes its child processes.

## Doctor

Run `python3 -B -m tink_snake --help`. Require exit 0 and the Snake description,
seed, no-color and no-sound options. No shared server, port, or save file exists.

## Drive

Read `features/README.md`. Run `python3 -B scripts/check_snake_terminal.py`.
The script sends real arrows, letters and resize events. It observes game traces
without setting game state. It asserts output text, movement, timers and terminal
restoration. Each run uses separate temporary traces. Avoid concurrent executions
in one checkout because the retained transcript has a fixed destination.

## Evidence

Retain `runs/snake/04-test/output/terminal-transcript.txt`. It records actions,
resulting observed state and sanitized actual terminal output. A successful run
must also report original terminal modes restored and no surviving child group.
This script does not establish visual quality or listener-perceived sound. Inspect
color and monochrome captures separately; record actual listening separately.

## Cleanup

The script closes its own PTYs, kills only a child group it started if still alive,
reaps the process and removes temporary trace files. Its retained transcript survives
cleanup. Confirm that file exists after the drive. Never kill by process name.

## Helpers

Run `python3 -B scripts/check_snake_tests.py` for rules, UI and existing regressions.
Run `python3 -B scripts/check_snake_terminal.py` for all mapped terminal features.
Keep the map current with `/maintain-verification-skill` when controls change.
