# Tron — build handoff

Built from the approved brief (r1). All automated checklist items run in `verify`; two attested items need a human.

## Deviations from the brief (for review)

1. **No right-hand panel.** The brief proposed a 38 x 20 grid (78 columns with border) *and* a right-hand panel. Those cannot both fit in 80 columns. I kept the approved grid size and replaced the panel with a scoreboard row above the grid (marks, round wins, round number, level) and the legend and sound status on row 26. Documented in `DESIGN.md`.
2. **Menu has one Tron cabinet.** The menu check requires each cabinet's title to match its screen title, so two-player is reached with `--two-player`, not a second menu entry.
3. **Round label.** While a round's result is on screen the header keeps that round's number; a draw replays its number. (The first draft showed the next round's number; fixed with a test.)

## Findings worth knowing

- Two identical machines from the mirrored start play symmetrically and draw every round, so the AI-vs-AI termination test pits `hard` against `easy`. This does not affect human play.
- `choose()` receives only the board and the machine's own direction, so the machine structurally cannot see the player's pending key.
- Mutation checks: changing the win threshold is caught by the PTY check; a machine that never steers is caught by a new engine test (the first draft of the tests missed it).

## Not verified by me

- **Play feel** (checklist `tron-play-feel`) and **sound** (`tron-listening`): no human has played or listened. Do not mark them without a real observation.
- Level strength is untested beyond the unit tests: I have not measured hard against normal over many matches.
