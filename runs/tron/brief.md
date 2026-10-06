# Tron light cycles — build brief r1

## Problem and outcome

Add offline, terminal Tron to tink-arcade: two light cycles leave solid trails on a grid, and the one that crashes first loses the round. The player faces a machine opponent by default, or a second human on the same keyboard. Deliver a review-ready PR.

Source: Jon chose "Two-player Tron light cycles" in chat as the test run for tink-sdlc 1.20.0. This is a proposal for the light-profile definition gate; no approval is recorded. All dimensions, timing and AI details are proposed defaults, for Jon to change at review.

Scope choice: the opponent is a local, deterministic AI. A live-model opponent like "Tetris vs Jev" is out of scope because it needs an API key and makes billed calls.

## Proposed game and controls

- Fixed 38 × 20 cell grid, each cell two columns by one row, so it fits the 80 × 30 canvas used by Snake. Cycles start facing each other on the middle row: left at (6, 10) moving right, right at (31, 10) moving left. Coordinates are zero-based.
- Both cycles advance one cell per tick, simultaneously, every 90 ms, and leave a trail in every cell they leave. The tick uses elapsed time, not frame count, and a delayed frame contributes at most one tick so a stall cannot cause a burst of unseen moves.
- Collision is resolved after both cycles move. A cycle dies if its new cell is outside the grid or already holds any trail or the other cycle's head. If both die in the same tick, including a head-on or swap, the round is a draw and nobody scores.
- A match is best of five rounds: first to three round wins. A draw does not score and does not count as a win; a round replays after a draw. After each round, pause for a brief result overlay, then wait for Space to start the next.
- Player 1: arrows or WASD. In two-player mode, Player 1 uses WASD and Player 2 uses arrows. Reversal into one's own trail in one tick is illegal and ignored. Queue at most one buffered turn per tick per player, so two quick key presses cannot reverse the cycle.
- P pauses and resumes, R restarts the match, M mutes, Q or Ctrl-C quits. Below 80 × 30, simulation and timers freeze, queued turns are cleared and the resize message shows; recovery discards time spent undersized.
- Entry point: `python3 -B -m tink_tron`, with `--two-player`, `--level easy|normal|hard`, `--seed INT`, `--no-color` and `--no-sound`. Add a Tron entry to `arcade_menu/games.json`. A nonterminal invocation gets a useful error; `--help` works without a terminal.

## The machine opponent (the "advanced" part)

All levels are pure, seedable functions of the board, with no network and no randomness except seeded tie-breaks.

- **easy:** moves to a random safe neighbouring cell, never into immediate death while a safe move exists.
- **normal:** picks the safe move that leads to the largest flood-filled reachable region, so it avoids sealing itself into a small pocket.
- **hard:** scores each safe move by Voronoi territory, meaning the count of cells it reaches before the opponent does, with flood-fill size as the tiebreak. It prefers cutting the opponent off.
- No level sees the player's pending key press; the AI reacts to the board state only.

## Presentation and sound

Follow Snake and Tetris: fixed centered 80 × 30 canvas, paper background, carbon ink and jade palette, eight-color fallback, monochrome attributes, `+ - |` boundaries, and the shared `arcade_common` renderer and `KeyboardAudio`. The two cycles must stay distinguishable without color: Player 1 head `##` and trail `==`, Player 2 head `@@` and trail `::`. A right-hand panel shows round score, level, mode and controls. Reuse existing cues only: turn → move, round win → clear, crash → over, pause/restart/unmute → switch. Straight movement and rejected input are silent. `--no-sound` prevents backend setup for the whole session.

## Acceptance criteria and approach

1. Implement a small `tink_tron` package: a pure deterministic engine, AI module, curses UI and CLI. Existing games' behavior is unchanged; shared modules are reused, not rewritten.
2. Deterministic engine tests prove start positions, simultaneous movement, trail, wall and trail collisions, head-on and swap draws, round and match scoring, draw replay, reversal rejection, turn queue limits, delayed-frame cap and restart.
3. AI tests prove that every level never moves into immediate death when a safe move exists. A constructed position proves normal chooses the larger pocket; another proves hard prefers the move that wins more territory. A seeded AI-versus-AI match always terminates and replays identically.
4. UI tests prove key bindings, both control schemes, palette fallback, layout bounds at 80 × 30 and 100 × 35, head and trail distinction in monochrome, cue mapping, mute, `--no-sound`, and cleanup on every exit path.
5. A real POSIX pseudoterminal check drives a match through steering, pause, restart, a shrink-and-recover, mute, Q and SIGINT, asserting restored terminal modes and no surviving child group. Retain the transcript.
6. Docs: README section covering launch, controls, rules and levels, and the Tron cabinet in the menu. The existing full check (`python3 -B scripts/check_all.py`) passes.

## Risks and verification

- A real-time two-key keyboard game is sensitive to terminal key repeat. Mitigation: the turn queue is per tick, and the PTY check exercises rapid presses.
- The Voronoi AI could be slow on a 38 × 20 grid. Mitigation: tests assert a per-decision time bound, and a flood-fill implementation on at most 760 cells is expected to be fast.
- "Feels fun" and sound quality are subjective. Those are attested items for a human, and no listening or play-feel result will be invented.

`checklist.json` holds the repeatable commands. Commands reference tests and scripts created during build; none exist at planning time.
