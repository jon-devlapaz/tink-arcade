# Last Time

## Problem and outcome
Add an original offline cabinet. A small light collects sparks in a dark arena. Every 15 simulation seconds a completed path joins the ghosts, replaying exactly in sync with all earlier paths. Contact ends the one-life game. Score is only sparks collected. The first round has no enemies; tension comes from accumulating past actions.

The confirmed seed is `seed-contract.md`, bound by run metadata. Confirmation explicitly disclaims the unasked expert probe's operator attribution and invalid source-line citations. Those are not authority or verified repository evidence.

## Acceptance and boundaries
Preserve all eight imported acceptance records. Build `tink_last_time/engine.py`, `ui.py` with a PaperRenderer subclass, and `__main__.py`. Append the registry entry without renumbering existing games. Python standard library only, offline, no credentials, no new enemies, lives, powers, persistence or network. Human fun, feel, listening and visual taste remain owed to jondev, not automated passing claims.

## Approach and interfaces
`Game(seed=None)` owns a 30 by 18 cell arena, player tuple, direction tuple, six sparks, score, round tick, accumulator, current path and immutable completed paths. `steer(direction)`, `advance(seconds)`, `restart()` and `snapshot()` are its boundaries. It imports no curses or audio. Arrow keys set automatic cardinal movement at one cell per 100 ms. Walls stop movement without killing. The first movement waits for an arrow. One round is exactly 150 ticks; each path has the initial position plus 150 resulting positions. All past paths replay at the same tick index, never recomputed from input. Same-cell and opposing edge-swap contacts kill. Death stops every game clock until restart; no extra life or win cap.

The player normally keeps the endpoint across rounds while ghosts return to their recorded origins. If an origin overlaps the player at the boundary, relocate the player to the nearest free cell, preferring a one-cell clearance from ghost origins and their next positions. This is only transition safety, never invulnerability. If every arena cell is occupied by an origin, genuine ghost contact ends play normally rather than crashing. Record the actual new origin in the next path. Keep the rule visible in controls/help. Sparks respawn on free cells with a local seeded random generator. Each collection gives one point.

`Controller.frame(now, rows, columns, keys, audio)` owns pause, resize, bounded keys and time. Freeze all game time when paused or below 80 x 30. Preserve pause on recovery and discard catch-up time. Discard stalls above 250 ms. Arrows steer, P pauses, R restarts, M mutes, Q/Ctrl-C exits. Restart preserves mute and session best. Shared KeyboardAudio uses existing samples; automatic travel is silent, sparks use clear, death over, pause/restart switch. --seed, --no-color and --no-sound are independent CLI options.

Keep the paper canvas and shared palette. A reverse-ink rectangular arena provides the requested dark playfield with light marks. Player `<>`, sparks `* `, ghosts `xx` stay distinct in monochrome. Score, round, ghost count, countdown, sound state and controls remain visible.

## Risks and proof
The smallest first slice is deterministic recording and replay. Read Stacker rules/UI tests before coding. Add named engine tests for each seed condition, boundary relocation, swaps, restart, time validation and frame partitioning. Add UI/controller/render/CLI tests, a legal-input replay and a real POSIX PTY check for pause, resize, restart, Q, SIGINT and terminal cleanup. Add mutation probes that require assertion failures when replay, timer, collisions, stacking, scoring, arrow mapping or registration protections are removed. These scripts are the rerunnable lever, not hand-checked claims.

Run `python3 -B scripts/check_all.py`, focused tests, replay, PTY and red probes. No separate linter/type checker is configured; use Python compilation and engine import-boundary tests. Activate each provisional seed check once its tests exist, changing only its activation object, and renew definition approval before attestations and verify. Observe outputs separately for each seed expectation. Commit before final SDLC verification. Open only a draft PR; no merge or readiness authorization.

## Operator authority
Task reference `/Users/jondev/scratch/arcade-run/task.md` explicitly authorizes Claude to stand in for jondev in Tinkery and definition/activation gates. Record reviewer as `Claude standing in for jondev`. This is proxy approval, not a human playtest or independent code review.
