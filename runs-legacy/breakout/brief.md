# Breakout change brief

## Problem and outcome

Add solo, offline terminal Breakout to tink-arcade and test whether a fresh agent can continue from saved files. Jon's priorities are reliable play, earned progression, and interesting boards. Deliver a reviewable PR; merge remains a separate human decision.

Scope comes from [the confirmed run seed](seed-contract.md), selected and hashed by [run.json](run.json). The repository-root `seed-contract.md` describes another game and is not this run's input. This brief proposes implementation choices for review; it does not approve them.

## Acceptance criteria

1. `python3 -m tink_breakout` starts a playable game with one paddle, one ball, visible score, remaining lives, board number, and controls. Help works without a terminal; non-terminal play fails with a useful message. Play uses no network or paid model calls.
2. There are exactly three distinct handcrafted boards. A board advances only after its last brick breaks; clearing board three wins. A brick breaks and scores exactly once, including simultaneous contacts. Proposed scoring: 10 points per brick, no time or speed bonuses.
3. Start with three lives for the entire run. Crossing the bottom costs exactly one life; cleared bricks and score survive that loss. At zero lives, gameplay stops with `GAME OVER`. Restart restores board one, every brick, three lives, zero score, and the initial ball/paddle state. Won and lost games accept restart and quit.
4. Paddle contact sends the ball upward; its contact position changes the outgoing angle so aiming is meaningful. Wall, paddle edge, brick face, and corner contacts behave consistently without embedding, repeated scoring, or passing through a brick between updates. No automatic speed increase between boards.
5. Pause and an undersized terminal stop simulation. Restoring size discards accumulated elapsed time and preserves an existing pause. Neither pause nor resize recovery costs a life or changes bricks/score. Quit and Ctrl-C restore terminal settings and leave no child processes behind.
6. Boards have different occupied-cell patterns and aiming routes. A deterministic replay using the actual simulation and legal paddle controls clears every brick on each board; directly deleting bricks or repositioning a flying ball does not count. Jon's judgment of difficulty, layout interest, and fairness is recorded separately from automated results.
7. A fresh continuation agent identifies scope, permission, evidence limits, and next work from [handoff.md](handoff.md) and its links. Record omissions or repeated work and whether Jon needed to supply context. Do not build a new substrate workflow or shared Seed Me view.

## Approach

### Proposed game and interface choices

Use a separate standard-library Python package: `tink_breakout/engine.py` for deterministic rules, `layouts.py` for board data, `ui.py` for curses input/rendering/timing, and `__main__.py` for launch/help/terminal cleanup. Keep Tetris available at its current entry point. Inspect its existing code before reusing small terminal-handling patterns; avoid a shared-engine refactor. Sound is not required for this slice.

Propose a fixed 60-column by 20-row playfield inside an 80-by-30 minimum terminal canvas. Larger windows add margins; resize never changes physics. Use readable ASCII with a monochrome option (`--no-color`), the existing paper/ink visual conventions where useful, and persistent control hints. Controls: arrows or A/D move, Space launches a waiting ball, P pauses, R restarts, Q or Ctrl-C quits. Letter keys accept either case. A new life and a new board wait for Space, avoiding an unseen immediate serve. Restart returns to that same waiting state. While undersized, ignore gameplay input and keep quit available.

Use a fixed simulation step with elapsed-time limits and collision handling that accounts for the whole traveled segment. Resolve the earliest contact, consume remaining step time, and bound repeated contacts. Resolve tied contacts deterministically and count each brick once. Reject invalid time inputs. Keep speed fixed across boards and constrain paddle deflection away from near-horizontal trajectories. Choose numeric speed, paddle width, and angle bounds during build, document them, and cover their edge cases; they are tuning choices rather than accepted proof of enjoyable difficulty.

Propose these 12-column by 6-row brick patterns (`#` brick, `.` gap), placed above the paddle with side clearance. Each brick is one hit; no indestructible barriers or power-ups. The builder must preserve the three distinct aiming ideas and verify every brick is reachable. Material layout changes require review of this brief.

```text
1. Gate          2. Chevron       3. Islands
############     #..........#     ###..##..###
###......###     .#........#.     ###..##..###
###......###     ..#......#..     ............
###......###     ...#....#...     ..###..###..
###......###     ....#..#....     ..###..###..
............     .....##.....     ............
```

Gate offers a central opening between side groups; Chevron invites angled shots along its diagonals; Islands separates targets into clusters and channels. These are design hypotheses. Replay reachability proves clearability, not that the boards are fun.

### Work and permission boundaries

The observed isolated checkout is `/Users/jondev/dev/active/product/tink-arcade-breakout`, branch `feat/breakout`, based at `c83dd829aa47c1b4e8baf2f3833327e6cfd77e7a` on 2026-10-04. Recheck Git state and the intended PR base before implementing or opening a PR. Do not alter the two existing game branches or their PRs. Do not update `_shared/`, stage contracts, or factory runtime as part of this feature.

This light run has one human definition gate at stage 3. A real decision accepting this brief and [checklist.json](checklist.json) must be recorded before implementation. Seed confirmation alone does not satisfy it. The launcher then opens the build stage in the selected isolated checkout and starts a fresh session; the builder reads its stage contract and required skills before acting.

Implement engine/layout tests first, then the terminal integration and a repeatable PTY check. Put test infrastructure under `scripts/` and `tests/`, never under `runs/`. Configure project-owned `_system/verification.json` with `python3 -B -m tink_breakout --help` (10 s) to check the entry point; the checklist runs the complete suite and PTY harness. Preserve the managed factory files. The checklist contains executable proof commands and the two evidence records requiring an explicit written assessment.

## Risks and verification

All commands below run from the Breakout checkout. Future scripts and Breakout tests are planned work, not current passing evidence.

- `python3 -B scripts/check_breakout_tests.py` (120 s): create a small runner that discovers the complete `tests` suite, requires nonzero Breakout engine, layout, and UI cases, runs existing tests too, reports counts/skips, and fails on missing groups, failures, or errors. This prevents an empty discovery run from looking successful. The checklist runs this command during SDLC verification. Explicitly report platform/audio skips.
- `python3 -B scripts/check_breakout_terminal.py` (45 s): create a POSIX PTY harness driving the actual `python3 -m tink_breakout --no-color`. Wait for concrete screen/state observations with bounded deadlines. Exercise paddle movement, launch, pause/resume, restart, quit, Ctrl-C, 80x30 and larger sizes, shrink to 40x12, then restore. Assert frozen state during pause/undersizing and no catch-up movement on recovery; include resize while already paused. Capture a sanitized transcript and fail on crashes, timeouts, wrong state, terminal-mode leakage, or unreaped children. Use an explicit test seam only if necessary for observing state; it must not replace the real terminal loop or physics. Clean up in `finally`.
- Engine cases: high-speed crossing, corner and simultaneous brick contacts, repeated contact, paddle center/edges, one life lost per bottom crossing, last-brick transition, no transition while any brick remains, final win, zero-life loss, and restart from playing/paused/won/lost states. For each, assert score, lives, remaining bricks, board index, and ball direction as relevant. Include bounded simulation under large elapsed time and deterministic replay results.
- Layout cases: exactly three unique patterns, bounds/nonoverlap, full legal clear replay for each using actual collision and paddle rules, and score equal to ten times destroyed bricks. Keep the paddle input sequence or deterministic controller reproducible and record step limits. Failure to clear is not proof of impossibility, but it fails the required clearability evidence.
- UI cases: all controls and case variants, monochrome, non-terminal error/help, safe clipping, timing freeze/resume, pause preserved through resize, and cleanup. Use both deterministic UI tests and the real PTY run; terminal text alone does not prove frozen physics.
- `python3 -m tink_breakout`: Jon plays and reports unfair deaths, tedious targets, whether progress feels earned, and which layouts need adjustment. Record the feedback and resulting changes. If this has not happened, label game feel unverified in the handoff and PR; do not replace Jon's judgment with a test pass. The evidence-record checklist item may pass with that honest pending status, but that is not human acceptance of play quality.
- After the real gate, implementation, attested marks, and code commit: `python3 _system/scripts/sdlc.py verify breakout`. Expect current verification for the candidate. Refresh `python3 _system/scripts/sdlc.py status breakout --json`; only current passing evidence supports a verification claim. Follow the stage-5 contract for independent review and a reviewable PR. Do not merge.

Current status is always obtained with `python3 _system/scripts/sdlc.py status breakout --json`, not inferred from this brief. The checklist defines scope; only SDLC commands write its evidence.
