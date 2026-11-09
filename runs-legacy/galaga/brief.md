# Solo Galaga-style game

## Problem and outcome
Add a playable offline formation shooter to tink-arcade. Use the entire path from hunch to PR to learn where tink-substrate helps and where it needs improvement. Jon selected solo first on 2026-10-04. The goal is the workflow trial, with a complete small game as its real output.

## Acceptance criteria
- `python3 -m tink_galaga` launches an original terminal shooter. Left/right or A/D moves; space fires; P pauses; R restarts; Q or Ctrl-C quits. Help works without a terminal.
- Enemies form rows, move, dive toward the player and fire. Player shots destroy enemies and increase score. Hits consume lives; brief respawn protection prevents repeated loss from one hit. Clearing a wave advances to a harder wave. Running out of lives shows game over and allows restart.
- Seeded runs repeat. Pause, small terminals, and slow frames do not secretly advance game time. The screen explains how to recover from a terminal smaller than 80 by 30.
- It works offline with Python 3.11+ and standard-library modules. Tetris behavior and its tests remain unchanged. No Jev costs or credentials.
- Automated model tests and a real pseudo-terminal check cover gameplay, input, pause, resize, restart, and clean exit. CI runs tests against the PR head. Human enjoyment remains unverified until Jon plays.
- The substrate record links the seed, branch, run, handoff, and PR when they exist. The run handoff and substrate antipattern log distinguish actual issues from proposals and name the next step.

## Approach
Light workflow, one combined definition and one implementation gate. Add separate `tink_galaga` engine, curses UI and CLI modules. Use original ASCII visuals and a fixed simulation timestep. Start with three lives and rising waves; tuning is reversible. Keep Tetris source unchanged. Create deterministic tests and `scripts/check_galaga_terminal.py` as a rerunnable terminal check. Add a README with both launch commands, original-art provenance, and a GitHub Actions test job. Work on feat/galaga from main, independent of the open Tetris PR.

The checklist contains the verification commands. Commit implementation before final workflow verification. Open a PR and leave merging to Jon. Do not mistake local checks, dashboard status, or a model review for merge approval.

## Risks and verification
Run `python3 -B -m unittest discover -s tests` and `python3 -B scripts/check_galaga_terminal.py`. The configured runner rejects empty test discovery. Cover bullet collisions, enemy kills, player damage and invulnerability, wave transition, game over, restart, and stable stepping. Run the actual curses app through a PTY including undersize and restored size. Record test limits, skipped native-audio tests, and any unobserved product outcome. Review the candidate independently under the installed workflow before PR delivery.

Record substrate problems with observed trigger, consequence, change tried, and next check. Do not build speculative dashboard features to finish this game.
