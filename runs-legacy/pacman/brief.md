# Pac-Man for tink-arcade: build brief r1

Input: the confirmed seed, `runs/pacman/seed-contract.md` (revision r2, sha256 in `run.json`). The seed is discovery input, not approval. This brief is a proposal for the one definition gate (stage 3). No approval is recorded.

## Problem and outcome

Add offline, one-player Pac-Man to tink-arcade as `tink_pacman`: a faithful take on the arcade rules on an original maze, with one twist made of two mechanics, Bookmark and Eraser. It matches the Socratink paper theme, plays endless levels, and appears in the menu as one entry.

Seed decisions this brief obeys: classic-proportion maze on a taller terminal (D1); both mechanics (D2); on by default, `--classic` turns them off (D3); endless levels and a paper-theme look (D4); the twist applies in every ghost mode (D5); simple, lightweight, deterministic where it should be (D6, C4, C5).

### Departures from the seed (for you to accept or change at the gate)

The seed left these to the brief. Each replaces an assumption in the seed.

- **Minimum terminal is 80 x 40, not 80 x 38.** Arithmetic: 28 x 31 cells is 56 x 31 characters; add a 2-column, 2-row border (58 x 33); the title takes rows 1-2, the box starts at row 4 and ends at row 36, row 37 holds the legend and sound status, rows 38-39 hold controls. That is 40 rows (indices 0-39), and the 80 columns hold the 58-wide box at column 3 and a 16-wide panel at column 62. This is my arithmetic, not yet run; the UI bounds test proves it.
- **No extra life in v1.** The source says nothing about it (seed, E6). Three lives, then game over.
- **Eraser works only on one-tile-thick interior walls.** A wall tile can be erased only if it has at least two open neighbours, so erasing never makes a dead end. One function owns that rule (`can_erase`).

## Game rules (what the tests will pin)

Ghost and wave rules come from the Pac-Man Dossier through two WebFetch summaries (2026-10-06), not from a direct read of the page. A reviewer should spot-check the ghost targets and the junction rule against it.

- **Maze.** 28 x 31 cells, original layout, mirror-symmetric, one wrap tunnel row, a ghost house with a door, four energizers. Dot count comes from the layout, not from a constant. Validator tests reject: asymmetry, unreachable dots, a dead end, a missing tunnel or house, an energizer count other than four, and fewer than 8 erasable wall tiles (my number; it keeps Eraser useful).
- **Pac-Man.** Moves on its own in its current direction until a wall blocks it. One buffered turn is held until it fits at a junction. Eating every dot and energizer clears the level.
- **Ghosts, chase.** Blinky targets Pac-Man's tile. Pinky targets 4 tiles ahead of Pac-Man. Inky doubles the vector from Blinky through the tile 2 ahead of Pac-Man. Clyde targets Pac-Man when 8 or more tiles away, else his corner. At each junction a ghost takes the open exit nearest its target by straight-line distance, never reverses, and breaks ties in the order up, left, down, right. The arcade's "up" bug for Pinky and Inky is not copied.
- **Ghosts, scatter.** Each ghost heads for its own corner: Blinky top-right, Pinky top-left, Inky bottom-right, Clyde bottom-left.
- **Waves.** Scatter 7, chase 20, scatter 7, chase 20, scatter 5, chase 20, scatter 5, then chase for good. Same schedule on every level in v1 (a simplification). Ghosts reverse when the mode flips and when frightened starts, but not when frightened ends. The timer pauses while frightened.
- **Energizers.** Ghosts turn frightened: they pick a random non-reverse exit at each junction (seeded) and move slower. Eating them scores 200, 400, 800, 1600 in a chain that resets with each energizer. An eaten ghost becomes eyes, returns to a tile above the house door, revives, and leaves.
- **House release.** Pinky leaves at once, Inky after 30 dots and Clyde after 60 on level 1, all at once from level 2 up; a 4-second timer with no dot eaten forces the next ghost out. Counters reset on each new life (a simplification).
- **Touch and lives.** Touching a live ghost costs a life; positions reset and dots stay. Pac-Man and a ghost swapping tiles in one step counts as a touch. Three lives. Dots score 10, energizers 50.
- **Endless levels.** After a clear the maze is restored and the next level starts. Speeds and frightened time follow the table below and stop changing at the last row. (From the source: Pac-Man 80%, 90%, 100%, then 90% of top speed; ghosts 75%, 85%, 95%; tunnel 40-50%; frightened ghosts 50-60%.)

| Level | Pac-Man | Ghost | Ghost in tunnel | Ghost frightened | Frightened time |
|---|---|---|---|---|---|
| 1 | 80% | 75% | 40% | 50% | 6 s |
| 2-4 | 90% | 85% | 45% | 55% | 5 s |
| 5-8 | 100% | 95% | 50% | 60% | 4 s |
| 9-16 | 100% | 95% | 50% | 60% | 2 s |
| 17-20 | 100% | 95% | 50% | 60% | none (the energizer scores 50 and ghosts reverse) |
| 21+ | 90% | 95% | 50% | 60% | none |

The 4 s, 2 s and the merged rows are my simplification of the source's ranges. Top speed is 10 tiles per second (my number; the base step is 0.1 s).

- **Timing.** The engine advances by elapsed time. Each actor gathers progress at its speed and moves one whole tile when it reaches 1. One frame never moves an actor more than one tile, so a stall cannot cause a burst of unseen moves.

### The twist

- **Bookmark.** Space drops a bookmark on Pac-Man's tile. For 4 seconds, or until a ghost reaches it, ghosts in scatter or chase mode use the bookmark's tile as their target. Frightened ghosts keep wandering and eyes keep going home. One per life.
- **Eraser.** `E` erases the wall tile directly in front of Pac-Man if `can_erase` allows it: interior, at least two open neighbours, not part of the border, ghost house, door or tunnel row. The tile stays open until the level ends. Ghosts use it too. One per life.
- **`--classic`.** Both keys do nothing and the panel hides their charges.
- Pac-Man keeps its two charges after a level clear; they refill only on a new life.

## Presentation and sound

Follow Snake: centered canvas, paper, carbon ink and jade, the shared `PaperRenderer` and `KeyboardAudio`, `+ - |` borders, ASCII only, eight-color fallback, monochrome attributes, `--no-color`, `--no-sound`. The title row reads `. socratink  /  paper pac-man`, the box is titled `PLAY / PAPER`, and the sound line starts `key sound on`. `scripts/check_arcade.py` expects exactly those strings.

Marks are proposals; slice 5 settles them and you judge them (check `pacman-look`). Rules: ASCII, two columns per cell, and every actor distinct in monochrome.

| Thing | Proposal |
|---|---|
| Pac-Man | `O` with an arrow for its facing, bold jade, reverse video |
| Ghosts | two-letter initials, ink, reverse video (`Bl`, `Pk`, `In`, `Cl`) |
| Frightened ghost | `~~`, dim |
| Eyes | `oo` |
| Dot / energizer | ` .` ink / `()` bold jade |
| Wall | ink, not reverse |
| Bookmark | `[]` in jade |

Cues (existing samples only): energizer eaten `switch`, ghost eaten `clear`, level clear `clear`, Bookmark `rotate`, Eraser `place`, life lost `over`, game over `over`. Dots and ordinary movement are silent. The cue map is mine; change it at the gate if you want a dot sound.

Keys: arrows or WASD steer, Space bookmark, `E` erase, `P` pause, `R` restart, `M` mute, `Q` or Ctrl-C quit. Below 80 x 40 the simulation freezes with a resize message, buffered turns clear, and recovery discards elapsed time.

## Approach

New package `tink_pacman/`: `maze.py` (layout and validator), `ghosts.py` (target and junction functions, pure), `engine.py` (rules, no curses), `ui.py` (renderer, input loop), `__main__.py` (CLI). One `games.json` entry appended as entry 11, titled "Pac-Man". README and DESIGN.md get a Pac-Man section that names the 80 x 40 exception. Tests first in each slice, written to fail for the right reason before the code exists.

Two changes to shared files, both needed and both small:
1. `scripts/check_arcade.py`: it forces a 32 x 90 terminal (line 20), too short for Pac-Man's freeze rule, so the PTY becomes 42 x 90, and it selects a game with `j` presses instead of digits. The menu's digit keys only cover entries 1-9 (`arcade_menu/ui.py:153`), so entry 11 cannot be reached by digit.
2. `arcade_menu/games.json`: one appended entry.

Existing games and the menu's behavior stay unchanged.

### Slices (features and futures)

After each slice, run its checks, inspect the diff, and choose proceed, consolidate, re-scope or stop and repair. Record the choice in the handoff.

1. **Maze and Pac-Man.** `maze.py` with validator tests, movement, buffered turn, tunnel, dots, level clear, and a bare renderer that draws the maze, Pac-Man and dots in the paper theme at 80 x 40 (no ghosts, no sound, no menu entry). You look at it before slice 2 starts. Future to protect: one owner for "which tiles are open".
2. **Ghosts.** First, read the Dossier page directly and write down any difference from the fetch summaries before coding the rules. Then `ghosts.py` targets and junction rule, waves, house release, touch, lives. Future to protect: one function picks a target; the twist later overrides it in one place.
3. **Energizers and levels.** Frightened mode, chain, eyes, the speed table, endless levels.
4. **Twist.** Bookmark first, then Eraser, each its own step with its own tests. `--classic`.
5. **Polish the UI; CLI, menu, docs, real-terminal check.** Marks, panel and messages are finished here; the bare renderer from slice 1 is the starting point.

Determinism: the engine, ghosts, maze and every test are deterministic. Randomness is only frightened-ghost junction choice, from `random.Random(seed)`, so `--seed` repeats a run. The wall clock exists only in the UI loop. No model calls, no network, no new dependency.

## Acceptance criteria

Each item in `checklist.json` has a command unless it needs a human. A passing command proves only what its tests exercise.

1. `pacman-maze`: validator rejects every defect listed above and accepts the shipped layout.
2. `pacman-engine`: movement, buffered turn, wrap, dots, scoring, lives, restart, delayed-frame cap, level clear and the speed table.
3. `pacman-ghosts`: each ghost's target, the junction rule with each tie-break, no reverse, wave schedule, reversal on mode change, house release, frightened chain, eyes, seeded wandering that repeats.
4. `pacman-twist`: Bookmark target override and expiry, Eraser rule (accepts a thin wall; rejects border, house, door, tunnel and thick walls), one per life, `--classic` inert.
5. `pacman-ui`: palette pairs equal Snake's in 256 and 8 colors, ASCII only, bounds at 80 x 40 and 100 x 45, undersize freeze and recovery, the strings the menu check needs, cue map, mute, `--no-sound`, terminal restored on every exit path.
6. `pacman-terminal`: real pseudo-terminal run through steering, Bookmark, Eraser, pause, restart, shrink and recover, mute, Q and SIGINT, with terminal modes restored; the transcript is kept.
7. `pacman-cli`: `--help` works without a terminal.
8. `pacman-menu`: the menu launches Pac-Man and returns, with the updated `check_arcade.py`.
9. `pacman-docs`: README and DESIGN.md mention `tink_pacman`, `--classic` and the 80 x 40 minimum.
10. `pacman-no-regressions`: the full local check passes.
11. `pacman-look` (human): you compare Pac-Man with Snake at the minimum size, in color and monochrome, and judge it matches the paper theme and is not ugly. First look after slice 1, final look at the end. Nothing here proves this.
12. `pacman-fidelity` (human): you or a reviewer spot-check the ghost targets, junction rule and wave times against the Dossier page.

## Risks and verification

- **80 x 40 may not fit your terminal.** The game freezes with a resize message. Check at exactly 80 x 40 and larger.
- **Look and feel are the stated failure risk (seed D4).** Tests cannot judge it; `pacman-look` is yours. Marks are proposals until then.
- **Fidelity rests on fetch summaries.** Two summaries agree, but neither is the page. `pacman-fidelity` covers it.
- **An original maze may play badly.** The validator checks structure, not fun. Expect to revise the layout after you play it.
- **Eraser changes connectivity.** Mitigated by `can_erase` (no dead ends, protected tiles) and by testing the ghost rules on an erased maze.
- **Shared-script change.** `check_arcade.py` serves every game. The change is additive and `pacman-no-regressions` reruns it.
- **Known limits, left alone:** the menu's digit keys stop at 9; three near-identical real-terminal scripts now exist (Snake, Tron, Pac-Man). Consolidating them is a future, not this run's job.
- **Not run:** nothing has been built or checked. Every command above is provisional until its file exists.

Commands in `checklist.json` reference tests and scripts created during the build; none exist at planning time.
