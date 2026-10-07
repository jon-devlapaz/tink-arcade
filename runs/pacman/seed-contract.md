status: confirmed for intake
# Seed contract: Pac-Man for tink-arcade
revision: r2        date: 2026-10-06   (r1 was displayed but never confirmed; r2 adds D6, C4 and the slice plan)
Confirmed by: "Chat: 'approved and confirmed. proceed with a watchful eye over issues.' in reply to the r2 display" (revision r2, 2026-10-06). Not approved for implementation.
Session ledger: ledger.json

## You are confirming
- Goal: a faithful terminal take on Pac-Man in tink-arcade, plus one twist.
- What gets built: package `tink_pacman` (pure engine, curses UI, CLI), one `games.json` entry, DESIGN.md/README sections. Classic-proportion maze on a taller terminal (D1). Four ghosts with fixed targets, waves, energizers, tunnel, lives, endless levels with a capped speed ramp (D4). The twist, Bookmark plus Eraser, on by default (D2, D3, D5).
- What does not: bonus fruit, intermissions, kill screen, the arcade's Pinky/Inky "up" bug, no-up-turn zones, Cruise Elroy, saved high scores, attract mode, new sound samples.
- Build spirit (new in r2): simple and lightweight; deterministic where it should be, non-deterministic where it should be; features-and-futures guides every slice (D6).
- Accepted unchanged: 1 of 3 suggestions (chosen by you: 5 of 6 decisions, counting your probe answers and D6).
- Still unknown: starting lives and extra-life rule; whether 80 x 38 is the right minimum; how the twist feels; whether `scripts/check_arcade.py` sets a terminal size.
- Reverses an earlier decision: DESIGN.md:56 fixed 80x30 canvas, for this game only (D1).

## Now
- Settled: D0-D5. - Uncertain: see Still unknown. - Needs you next: confirm this revision.

## Goal
G [user] Add a faithful terminal take on Pac-Man to tink-arcade, plus one twist. — chat: "it looks good" (goal only)

## Decisions
D1 [user] Taller minimum terminal so the classic-proportion maze fits (option B). Breaks the fixed 80x30 rule for this game only. — chat: "B". I suggested a compact maze (A); you chose against it.
D2 [user] The twist includes both mechanics, Bookmark and Eraser. — chat: "both" / "both mechanics". The agent reads this as ONE combined twist; the goal still says "one twist". I suggested Bookmark only; you chose against it.
D3 [user] Twist on by default; `--classic` turns it off. One menu entry. — chat: "A" (my suggestion, accepted unchanged)
D4 [user] Levels are not limited; the look must match the Socratink paper theme. — chat, pre-mortem probe: "it was ugly and didnt match the socraintk paper theme. also it only had limited levels."
D6 [user] Keep the build simple and lightweight; deterministic in the right places, non-deterministic in the right places; features-and-futures is "the spirit of all AI generated code". — chat, your last message
D5 [user] The twist applies in play: Bookmark and Eraser work in every ghost mode. — chat: "i think the twist should be aplied. it would make it fun"
F1 [evidence] The menu and every existing game assume 80x30 (arcade_menu/ui.py:8-9; DESIGN.md:56). Pac-Man is the first to need more rows.

## Assumed (not confirmed by you)
S1 [agent] Package `tink_pacman`; engine.py has no curses; tests first; built in a separate worktree. — from your instructions.
S2 [agent] Existing sound cues only: move, rotate, place, switch, clear, over (arcade_common/audio.py:11-18).
S3 [agent] Space drops a Bookmark; E erases a wall. One use of each per life.
S4 [agent] Bookmark: 4 s or until a ghost touches it; scatter and chase ghosts target it; frightened ghosts still wander; eyes still go home. (4 s and the mode rules are my numbers and reading of D5.)
S5 [agent] Eraser: one interior wall cell in front of Pac-Man; never the border, ghost house or tunnel; stays open until level end.
S6 [agent] The five core rules as drafted in chat (self-moving Pac-Man with buffered turn; four fixed ghost targets and the junction rule; scatter/chase waves; energizers with 200/400/800/1600 chain and eyes; touch rule, scoring, dot-count house release). You said "it looks good"; I record this as an assumption, not a per-rule choice.
S7 [agent] 3 lives; extra-life rule decided in the brief. The source is silent on both.
S8 [agent] Minimum terminal 80 x 38 (my number). Original maze layout and text graphics, not the arcade's sprites; package and menu title follow the existing Galaga precedent.
S9 [agent] Endless levels: frightened time shrinks and ghost speed rises with level, both capped (curve set in the brief).

## Constraints and exclusions
C1 [user] No commit or push until you say so. The agent approves no gate.
C2 [user] Code in a separate worktree, tests first, no curses in engine.py, follow the existing game layout.
C3 [agent] Existing games' behavior is unchanged; shared modules are reused, not rewritten.
C4 [user] Per D6: no new framework, no new dependency, no speculative extension points. One owner per invariant (for example, one function picks a ghost's target). Slices stay small and each is checked before the next. Source: /Users/jondev/.agents/skills/features-and-futures/SKILL.md (read this session).
C5 [agent] Where it is deterministic: the whole engine, ghost targets, waves, scoring, Bookmark and Eraser rules, and every test. Same inputs give the same game. Where it is not: frightened-ghost wandering (seeded by `--seed`, so it repeats on request), the wall clock in the UI loop, and the human judgement in A7. No model calls, no network.

## Acceptance checks
A1 [agent] Engine rules: movement, buffered turn, tunnel wrap, dots, energizers, lives, ghost chain, endless levels.
   provisional: needs tests/test_pacman_engine.py
   cmd: `python3 -B -m unittest tests.test_pacman_engine` | expect: OK with a nonzero test count | cwd: worktree root
A2 [agent] Ghost targets, junction rule, waves, house release, Bookmark and Eraser rules (including that Eraser never removes border, house or tunnel cells).
   provisional: needs tests/test_pacman_ai.py
   cmd: `python3 -B -m unittest tests.test_pacman_ai` | expect: OK with a nonzero test count | cwd: worktree root
A3 [agent] UI matches the paper theme: same palette pairs as Snake in 256 and 8 colors, ASCII-only marks, bounds at the minimum size and a larger size, undersize freeze, cue mapping, mute, `--no-sound`.
   provisional: needs tests/test_pacman_ui.py
   cmd: `python3 -B -m unittest tests.test_pacman_ui` | expect: OK with a nonzero test count | cwd: worktree root
A4 [agent] Real pseudoterminal run: steering, pause, restart, shrink and recover, mute, Q, SIGINT, terminal modes restored.
   provisional: needs scripts/check_pacman_terminal.py
   cmd: `python3 -B scripts/check_pacman_terminal.py` | expect: exit 0 and a saved transcript | cwd: worktree root
A5 [agent] CLI help works without a terminal and names `--classic`.
   provisional: needs tink_pacman/__main__.py
   cmd: `python3 -B -m tink_pacman --help` | expect: usage text containing --classic | cwd: worktree root
A6 [agent] Whole arcade still passes. Not run this session.
   cmd: `python3 -B scripts/check_all.py` | expect: last line "All checks passed." (scripts/check_all.py:main) | cwd: worktree root
A7 [agent] A human compares Pac-Man with Snake at the minimum size, in color and monochrome, and judges "not ugly, matches the paper theme" (D4). No command; attested by you. Passing tests do not prove this.

## Open questions
(none blocking)
Deferred, non-blocking: exact speeds, wave timings per level, extra-life rule, maze layout. Reason: brief-stage design work. Revisit when: the brief is written.

## Knowledge map
- **What we know, with proof:** E1-E6 below, all observed 2026-10-06.
- **What we know we don't know:** starting lives and extra-life rule (source silent) — owner: you, in the brief. Whether `scripts/check_arcade.py` forces a terminal size — owner: build stage, `grep` and run it. Whether 80 x 38 fits your terminal — owner: you.
- **What we have not read:** root `seed-contract.md`; `scripts/check_snake_terminal.py` internals (215 lines); `scripts/check_arcade.py` body; the Pac-Man Dossier page itself (only a fetch summary). Who reads them: the stage 1 planner.
- **What could surprise us:**
  Probe: Imagine this shipped and turned out wrong; what is the likeliest reason? — answer: "it was ugly and didnt match the socraintk paper theme. also it only had limited levels." — changed: added D4, acceptance check A3 and A7, and endless levels (S9).
  Probe: Give one case where this should not apply. — answer: "i think the twist should be aplied. it would make it fun" — changed: added D5; twist applies in all ghost modes (S4).
  Probe: What would someone who has done this before ask that we have not? — answered from evidence, NOT independent: asked after the finding. Likeliest: does the maze hold a 28-wide board plus panel at the minimum size, and is the real-terminal check sized for 38 rows? — changed: A4 and S8 name the minimum size; menu check size is an open unknown.
  Teach-back: you wrote "we are building pac man for tink arcade." That matches the goal but names no exclusions, so I could not check what-will-not-be-built. Recorded as partial; the You are confirming box carries the exclusions.
  Where we did not look: other terminals, other operating systems, real play feel, audio on the output device, trademark or naming review.
  We would know we were wrong if: you compare it with Snake and call it ugly again, or a level ends and play stops.

## Evidence
E1 [evidence] "WIDTH = HEIGHT = 20" (tink_snake/engine.py:5) — observed 2026-10-06; re-check if Snake changes
E2 [evidence] fixed 80x30 canvas (DESIGN.md:56) — observed 2026-10-06; re-check if DESIGN.md changes
E3 [evidence] "MIN_COLUMNS = 80" / "MIN_ROWS = 30" (arcade_menu/ui.py:8-9) — observed 2026-10-06
E4 [evidence] CUES: move, rotate, place, switch, clear, over (arcade_common/audio.py:11-18) — observed 2026-10-06
E5 [evidence] `pending` is false with `--here`, so stage 1 does not commit (_system/scripts/sdlc.py:1412); `tink-route` is skipped when absent from PATH (sdlc.py:1306-1307) — observed 2026-10-06
E6 [evidence] Ghost targets, junction rule, wave times, chain values, house release: WebFetch summary of pacman.holenet.info, not the page itself — observed 2026-10-06; re-check against the page before the brief
Grounded in: AGENTS.md, DESIGN.md, README.md, arcade_menu/games.json, arcade_menu/registry.py, arcade_menu/ui.py, arcade_common/audio.py, arcade_common/theme.py, tink_snake/{engine,ui,__main__}.py, tink_tron/engine.py, tests/test_snake_engine.py, tests/test_snake_ui.py (first 60 lines), _system/SDLC.md, _system/scripts/sdlc.py (1119-1180, 1302-1484), _system/verification.json, scripts/check_all.py, stages/01-plan/CONTEXT.md, runs/snake/seed-contract.md (first 40 lines), runs/tron/brief.md (first 80 lines).

## Suggested slices (proposal only; the brief owns the final plan)
Pause after each slice to ask: did a future get spent? Proceed, consolidate, re-scope, or stop and repair (features-and-futures section 4).
1. Maze, self-moving Pac-Man, buffered turn, dots, tunnel. Checks: A1 subset.
2. Four ghosts, junction rule, waves, house release, touch and lives. Checks: A2 subset.
3. Energizers, frightened chain, eyes, endless levels.
4. Twist: Bookmark, then Eraser, each its own step. `--classic` turns both off.
5. UI, CLI, menu entry, docs, real-terminal check. Checks: A3-A7.

## Suggested first slice (proposal only)
cwd: the new worktree. `python3 -B -m unittest tests.test_pacman_engine` — write the failing slice-1 tests first, then `tink_pacman/engine.py`.

## Risks
- The twist may make the game too easy; Eraser changes maze connectivity and widens the test list (D2, against my suggestion).
- 80 x 38 may not fit every terminal; the game freezes with a resize message below it.
- Faithfulness rests on a fetch summary; verify against the Dossier before the brief.
- Look and feel are subjective; A7 is yours to judge, and nobody has run any check yet.
