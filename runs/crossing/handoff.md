# Crossing handoff

## Current status

Jon replied "approve" to the brief and checklist in Cowork; the operator recorded
that as the stage 3 decision. Build is on branch `crossing` in a separate clone.
Four checked items run under `verify`. `visual-review` and `docs-handoff` are
attested by the operator. `menu-on-mac` is waiting for a result from Jon's Mac.
No release approval or human playtest has happened.

## Evidence

- `scripts/check_crossing_tests.py`: 241 tests (22 new), 2 native-audio skips that
  were already opt-in for macOS.
- `scripts/crossing_replay.py`: legal-input win (level 3, 2850 points, 3 lives,
  13.9 s simulated) and loss (3 deaths, 70 points). The planner is a breadth-first
  search over a copied lane timeline; the replay drives a fresh Game through
  `hop()` and `advance(STEP)` only.
- `scripts/check_crossing_terminal.py`: real curses process in a PTY; transcript at
  `04-test/output/terminal-transcript.txt`.
- `scripts/capture_crossing.py`: 20 captures (play, pause, life lost, win, game
  over) at 80x30 and 100x35, color and mono, under `04-test/output/captures/`.

## Visual review notes

The first captures used `#` for both the home-row walls and the cars, so the walls
looked like traffic. Walls now use `^`. In both palettes the board fits inside
`PLAY / PAPER`, the score panel sits to the right, filled bays show as jade `*`,
and the marker is a reverse-video `@`. At 80x30 the bottom six rows are blank. On
game over the marker stays where it was hit, which shows the cause. Captures show
`key sound off` because the sandbox has no audio player.

## Operator environment and interventions

Operator: Claude in Cowork, Linux sandbox, Python 3.10, no `tink`, `tink-route`,
`gh`, or audio player. Substrate targets macOS and Codex, so this is an
off-target run.

1. `sdlc.py stage crossing 3` refused: no git identity in the sandbox. Passed
   Jon's repo identity as `GIT_*` environment variables instead.
2. `stage --check` planned a worktree at a sandbox path that would not exist on
   Jon's Mac. Used the documented manual fallback: committed `runs/crossing` on
   main, then built in a separate clone on branch `crossing`.
3. The first `git add` on the mounted checkout left `.git/index.lock`, because the
   mount refused deletes. Jon granted delete permission; the stale lock (created
   by this operator) was removed.
4. Stage skills were skipped (`tink` not installed). `principle-build-the-lever`
   is reflected anyway via the replay planner and capture script; unslop was
   applied by hand to README and these notes.
5. Baseline `scripts/check_arcade.py` fails here for every game on missing
   `key sound on`; hence `menu-on-mac` is attested, for Jon to run.

## Still unverified

Human playtest of difficulty and fairness, listening to cues, the menu check on
macOS, CI, and independent review.
