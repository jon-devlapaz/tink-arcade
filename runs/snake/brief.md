# Classic Snake — build brief

## Problem and outcome

Add solo, offline terminal Snake to tink-arcade. Jon's priority is that it looks and sounds like Tetris: warm paper, carbon ink, jade accents, restrained ASCII panels, and the existing mechanical-key recordings. Walls, food, growth, and collision define classic play.

Source: confirmed `seed-contract.md` revision 3. This is a proposal for the light-profile definition gate; no implementation approval has been recorded. All Snake dimensions, timing, scoring, and interaction details below are proposed defaults. Tetris's palette, 80 × 30 canvas, two-column cells, audio API, and existing cue priorities are inspected facts.

## Proposed game and controls

- Fixed 20 × 20 cells, each two columns by one row. Begin immediately with a three-cell snake facing right near the center: head (10, 10), body (9, 10), tail (8, 10), using zero-based coordinates.
- Start at one step per 180 ms. Every five foods reduce the interval by 15 ms, to a minimum of 75 ms: `max(75, 180 - 15 * (foods // 5))`. The new interval applies after the eating step. Keep the render/input loop near Tetris's 60 Hz target; movement uses elapsed time, not frame count. Cap a delayed frame's elapsed contribution at one movement interval so a stall cannot cause a burst of unseen moves.
- One food at a time, selected uniformly from free cells with an injected seeded random generator. Eating grows by one cell and adds 10 points. No wraparound or obstacles. Entering a wall or occupied body cell ends play; entering the tail's departing cell on a non-growth step is legal.
- Filling the board produces `BOARD COMPLETE`, no further food, and frozen play. Session best survives restart and disappears on exit.
- Arrows or WASD steer, accepting either letter case. Queue at most two legal direction changes; consume at most one per movement step. Validate each against the last queued direction, or current direction if empty. Reject reversals and duplicate directions. Ignore new turns when the queue is full. This allows right → up → left across successive steps without reversing in one step.
- P pauses/resumes; R restarts; M mutes/unmutes; Q or Ctrl-C quits. Pause clears pending turns and freezes movement time; resumed play waits the remaining interval. Restart clears turns, score, speed, pause and end state, preserves session best and mute state, and repeats the food sequence when `--seed` was supplied.
- Below 80 × 30, freeze simulation and timers, clear pending turns, show the resize message, and permit mute/quit only. Recovery preserves any prior pause and discards time spent undersized. Restart and mute remain usable on normal-size pause/end overlays.
- Entry point: `python3 -B -m tink_snake`, with `--seed INT`, `--no-color`, and `--no-sound`. A nonterminal invocation gets a useful error; `--help` works without a terminal. No launcher installation is required in this slice.

## Presentation and sound

Use Tetris as the reference, not Breakout's cyan-on-black renderer. Retain the fixed centered 80 × 30 canvas, title/subtitle placement, paper background and palette indices 230/233/29/240/245, eight-color fallback, monochrome attributes, and light `+ - |` boundaries.

Proposed canvas positions (zero-based, before centering): board border at column 3, row 4, width 42, height 22; board interior at column 4, row 5. Right-side SESSION panel begins at column 49, row 4, width 27 and shows SCORE, SPEED (steps/second), LENGTH, and SESSION BEST. Place feedback, sound status and a head/body/food legend below it. Use rows 27 and 28 for persistent controls. No hold or next-piece panels.

Use directional ASCII head marks `>>`, `<<`, `^^`, `vv` in bold jade reverse video; body `[]` in carbon reverse video; food `()` in bold jade without reverse video; empty cells ` .` in graphite. These shapes remain distinct without color. Center pause, game-over and board-complete overlays over the board while retaining statistics and controls. Reuse Tetris's short copy where appropriate: `A fresh page.`, `Take a breath.`, `Turn a fresh page.` Title: `. socratink / paper snake`.

Import `neon_tetris.audio.KeyboardAudio` directly, preserving recordings and `sounds/credits.json`. Do not introduce another backend, copy WAVs, or rewrite the shared framework. Mapping:

| Snake event | Existing cue | Sample |
| --- | --- | --- |
| Direction actually changes on a movement step | move | tactile.wav |
| Food eaten, including final food | clear | clear.wav |
| Wall/self collision transition | over | enter.wav |
| Pause/resume, restart, unmute | switch | mx-blue.wav |
| Automatic straight movement, rejected input, mute, quit | none | silent |

Keep the backend's one-cue-per-batch priorities and 150 ms expiry; food beats a turn, collision beats a turn. Service `audio.tick()` every frame, including paused/undersized frames, and stop pending/active audio on entering the small-window state. Close audio on normal exit, Ctrl-C and exceptions. `--no-sound` prevents backend setup for the whole run; M cannot override it. Show the existing on/muted/off/unavailable status and report backend errors after terminal restoration. No music or new sounds.

## Acceptance criteria and approach

1. Implement a small `tink_snake` package: pure deterministic engine, curses UI/controller, and CLI. Keep existing Tetris/Breakout behavior unchanged. Reuse the audio API; mirror the small palette/clipping helpers without changing Tetris or creating a general framework.
2. Deterministic tests prove movement, growth, score, speed boundaries/cap, seeded restart, food exclusion, tail departure, both collision types, full-board completion, direction queue ordering/overflow/rejections, timer pause, delayed-frame cap, restart, and terminal-size state transitions.
3. UI tests prove bindings, theme colors/fallback, ASCII layout bounds at 80 × 30 and 100 × 35, head/body/food distinction in monochrome, overlay controls, status text, successful-event cue mapping, silent rejected actions, mute, disabled/unavailable audio, frame polling and cleanup on every exit path.
4. A real POSIX pseudoterminal test drives Snake through arrows/WASD, queued turns, pause/resume, restart, shrink/recovery while paused and playing, initial undersize, mute, Q and SIGINT. Assert state observations and restored terminal modes, no traceback, no surviving child group. Label SIGINT coverage accurately: it simulates Ctrl-C's signal. Retain a transcript. Test observations must not control normal gameplay.
5. Compare actual Tetris and Snake terminal renderings at 80 × 30 and 100 × 35 in color and monochrome, including play, pause and game over. Record viewed captures, sizes, modes, and concrete findings. Automated palette/layout assertions support this comparison but do not replace it.
6. Run the existing macOS native tests with real sample playback and metering; all selected tests must execute without skips. They establish advancing playback and nonzero rendered signal across spaced repeats and mute/resume. Add Snake integration tests for rapid cue coalescing, failures, and cleanup. A separate listening note records output device, repeated/rapid turns, eating, collision, pause/restart and mute/unmute. Record who actually listened and their observation; if no listener is available, leave listening unverified and do not invent approval.
7. Keep licensed samples unchanged and document launch, controls, rules, tuning and reuse in the project README/design documentation. Retain the existing regression suite. Do not rerun the Breakout PTY script in this run: it overwrites the prior run's transcript.

## Verification

`checklist.json` contains the repeatable commands and two observation-based items. Create `scripts/check_snake_tests.py` and `scripts/check_snake_terminal.py` during build; neither exists at planning time. The test runner must reject missing/empty Snake engine and UI groups, load all existing tests, fail import/discovery errors, and report skips explicitly. The terminal runner should adapt the existing Breakout harness narrowly, with its own `TINK_SNAKE_TRACE` and `runs/snake/04-test/output/terminal-transcript.txt`.

Commands from this checkout:

```sh
python3 -B scripts/check_snake_tests.py
python3 -B scripts/check_snake_terminal.py
python3 -B -m tink_snake --help
```

The checklist additionally gives an exact guarded command for the existing native audio suite. On macOS it sets `NEON_TETRIS_AUDIO_TESTS=1`, requires the native tests to exist and execute, and refuses skips. Hardware/backend failure is a failed check, not a pass. Visual comparison and listening are recorded separately before verification. After actual gate approval, build, commit and attest observed items, run `python3 _system/scripts/sdlc.py verify snake`; then obtain independent review and a reviewable PR. Merge remains Jon's decision.

## Boundaries, risks and open decisions

No multiplayer, online service, persistent leaderboard, obstacle board, unrelated factory changes, or changes to existing game rules. The current verification config only invokes Breakout help; the Snake checklist adds the real checks without changing factory policy files.

Main risks are losing fast direction changes, making the wider board look unlike Tetris, and audio calls succeeding without audible output. The queue tests, same-size visual comparison, real native metering and separate listening address those risks. Reusing a Tetris-owned audio module is an intentional small dependency; imports must remain free of curses initialization.

For the definition review, Jon can accept or amend the proposed 20 × 20 board, 180-to-75 ms speed schedule, two-turn queue, 10-point food scoring, layout/marks, and cue mapping together. No additional design question blocks a concrete review. Subjective visual/audio acceptance remains work for build validation; there is no user playtest or listening evidence yet.
