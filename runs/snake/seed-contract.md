# Seed contract: Classic Snake
status: seed contract — confirmed for intake; not approved for implementation
revision: 3
date: 2026-10-04
originator: Jon

## You are confirming
- Goal: add classic Snake to tink-arcade through tink-sdlc and test smoother Substrate delivery.
- Build: solo terminal Snake matching Tetris’s paper-and-ink presentation and mechanical-key sounds.
- Exclude: multiplayer, obstacle boards, online services, persistent leaderboards, and unrelated factory changes.
- Choices: Jon chose Snake and classic play, supplied the design priority, and accepted the sound-reuse suggestion. One of four scope choices accepted a recommendation unchanged.
- Unknown: exact board size, starting speed, and speed progression will be proposed in the build brief. Visual and audio quality require actual inspection.

## Decisions
G [user] Make another arcade game as a tink-substrate run — current conversation.
D1 [user] “classic snake” — walls, food, growing tail, and collision end the game.
D2 [user] Match Tetris’s “design and theme and style.”
D3 [user] Reuse its mechanical-key sounds — “resuing them please”.

## Proposed defaults
S1 [agent] Solo, offline terminal play; arrows/WASD, score, pause, restart, mute, and quit.
S2 [agent] Follow Tetris’s warm paper, carbon ink, jade accent, light ASCII borders, centered canvas, and visible controls. Adapt panel content to Snake rather than copying Tetris-only panels.
S3 [agent] Reuse existing sound samples and playback support, retaining their credits. Sound follows useful actions and events; automatic movement remains quiet. Plan exact cue mappings before implementation.
S4 [agent] Keep Tetris and Breakout behavior unchanged. No multiplayer, obstacle boards, online services, saved leaderboard, or shared-framework rewrite in this slice.

## Acceptance checks
A1 [agent] Deterministic tests cover growth, food on free cells, wall/self collision, reverse-direction handling, queued turns, pause, restart, and a full board. Provisional command: `python3 -B scripts/check_snake_tests.py` from the Snake checkout; the build must create a runner that rejects missing Snake tests and also runs existing regression tests.
A2 [agent] Real terminal checks cover input, pause, resize recovery, and terminal restoration. Provisional command: `python3 -B scripts/check_snake_terminal.py`; the harness does not exist yet.
A3 [agent] Compare Tetris and Snake visually at the same terminal sizes in color and monochrome, including pause and game over. Retain observed results; passing engine tests alone does not prove design consistency.
A4 [agent] Exercise repeated sound playback, mute/unmute, disabled and unavailable audio, and cleanup. Include actual macOS playback evidence, not only mocked calls; record any unverified sound quality explicitly.
A5 [agent] Use the installed tink-sdlc light workflow, reviewed brief/checklist, actual build approval, verification, independent review, and a reviewable PR. Merge remains a separate human decision. Archive evidence and record avoidable stops after delivery.

## Knowledge and risks
- Inspected: the arcade instructions, installed SDLC guide/status, Tetris design document, renderer initialization/layout, audio interface, sample credits, and relevant UI tests.
- Evidence: DESIGN.md:12 says “Paper, ink, one accent.” DESIGN.md:56 specifies a fixed 80-column by 30-row canvas. DESIGN.md:151 specifies M and --no-sound. neon_tetris/ui.py implements the indexed palette and ASCII boundaries. Observed 2026-10-04; recheck if the design or implementation changes.
- Pre-mortem: what would disappoint Jon? His answer was a mismatch with Tetris’s style. Changed: explicit presentation and sound requirements.
- Counter-example: what if color or audio is unavailable? DESIGN.md:153 and :165–169 require playable fallback and clear state. Changed: fallback is part of acceptance.
- Outside view: could successful audio calls still produce silence? DESIGN.md:159 names that actual playback risk. Changed: require real playback evidence as well as mocks.
- Not inspected: full engine/audio implementation and complete terminal harness. The planner must inspect these before choosing reuse; exact tuning remains a planning responsibility.
- Where we did not look: other terminal emulators, external player feedback, and other operating systems during discovery. No implementation checks have run.
- We would be wrong if Snake passes rule tests but looks or sounds unlike Tetris, loses inputs, or disrupts existing games.

## Next
Jon confirmed revision 3 for intake. The coordinator then continues into tink-sdlc planning under the existing request, presents the concrete brief for its required gate, and carries approved work through delivery. Seed confirmation alone is not build approval.
Teach-back: no separate restatement supplied; Jon explicitly confirmed the displayed revision.
