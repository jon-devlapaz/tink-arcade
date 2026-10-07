# Review findings: breakout-session-best (stage 5)

Reviewer: independent model reviewer (advisory; not human approval, not code-owner approval).
PR: https://github.com/jon-devlapaz/tink-arcade/pull/19 (branch `breakout-session-best`, base `main`).
Reviewed HEAD: `8d9949f`. Code commit `ec3816a`; the later commits only touch `runs/breakout-session-best/`.
Compared against: `runs/breakout-session-best/brief.md` (approved, decision 3), `_shared/REVIEW.md`.

## Verdict

**Important findings: none.** The feature matches the approved brief. There are 3 Nits, and none of them blocks release review.

## Review scope

The diff is low risk: one counter in the engine, one HUD line, a new trace key and a README line. It touches no I/O, adds no new file writes and has no security boundary. A single combined pass covered logic and edge cases, security boundaries and acceptance criteria. I skimmed the bundled SDLC 1.21.0 upgrade separately but did not review it line by line.

## Acceptance criteria

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | HUD shows `SESSION BEST nnn`, starting at 000 | Met | `tink_breakout/ui.py:72`; real-PTY transcript at 80x30 shows `SESSION BEST 000     three boards, three lives.` on the subtitle row |
| 2 | Best rises with score, never lowered; R keeps it | Met | `tink_breakout/engine.py:31` sets `best` before `restart()`; `engine.py:113` uses `max()`; `restart()` (`engine.py:34-37`) does not touch `best`; covered by the engine and UI tests |
| 3 | Memory only, nothing written to disk | Met | No new file I/O. `best` reaches disk only through the existing opt-in `TINK_BREAKOUT_TRACE` (`ui.py:121-142`), the same as Snake's trace |
| 4 | `snapshot()` includes `best`; physics/restart checks pass | Met | `engine.py:58`. `test_bounded_elapsed_and_restart` still holds because it sets `score` directly, so `best` stays 0. The PTY script compares only `GAME_KEYS` |
| 5 | README says session best lasts until exit | Met | `README.md:57` (see Nit 1) |
| 6 | Local checks pass | Met | See "What I ran" |

## Edge cases checked

- **Board advance** (`engine.py:118-120`) calls `_serve()`, not `restart()`, so score and best carry over. This is correct.
- **Life loss** keeps score and best. This is correct.
- **Maximum score** is 760, so `{best:03}` always fits in 3 digits. `SESSION BEST nnn` spans `ox+9` to `ox+24`, and the subtitle starts at `ox+30`, so the two never overlap.
- **Snapshot comparisons:** pause and resize tests compare snapshots within one game, and `best` stays constant across those comparisons.
- **Audio cue:** `cues_for` (`ui.py:91-108`) ignores `best`, so the new key does not change cue behaviour.
- **Update timing:** the brief asked for live update ("updated when a game ends"); the human approved live update as default 1. At game end both rules give the same value.

## Challenge to the attested checklist mark (`hud-looks-right-at-80x30`)

- **What the mark used:** a `Mock` 30x80 screen calling `Renderer.draw`. That is the same technique as the unit test `test_hud_shows_session_best`, so it is not an independent look. The checklist's own `verify` asked for a real `python3 -B -m tink_breakout` run at 80x30, or a read of the terminal-transcript frame.
- **My independent check:** I ran `scripts/check_breakout_terminal.py` (real PTY, 80x30) and read the transcript it wrote. It shows `SESSION BEST 000` on the same row as the subtitle, with a 5-column gap, and the SCORE line unchanged below it.
- **Conclusion:** the mark's claim holds, but its evidence is weaker than the checklist described (Nit 2). The transcript only shows best = 000; the mark's Mock render covered a non-zero value.

## Findings

### Important

None.

### Nit

1. **The README contradicts itself.** `README.md:55` still says "restarting resets everything", and the new line at `README.md:57` says session best lasts until exit, so best survives restart. Suggested wording: "restarting resets everything except session best", or fold the two lines together. Snake's section (`README.md:124`) handles this in one sentence. The stage 3-4 handoff already noticed this and left it alone because the brief specified only one line.
2. **The attested HUD mark used a Mock screen instead of the real terminal or transcript the checklist named.** The mark is in `runs/breakout-session-best/marks/hud-looks-right-*.json`; the checklist item is in `checklist.json`. My PTY transcript confirms the layout, so this is about the strength of the evidence, not the behaviour.
3. **SDLC upgrade (not the feature):** the `ui-pr` trigger in `stages/05-deploy/TRIGGERS.json` (`paths` regex) matches only web file types (`tsx|jsx|css|scss|html|vue|svelte`). A curses UI change like `tink_breakout/ui.py` can never fire `visual-pr` in this terminal-games repo. It did not fire here, which is consistent with the table as written. Raise it upstream with tink-sdlc if terminal UI should count.

## What I ran

Tests ran via a `/bin/sh` script that unsets `PYTHONDONTWRITEBYTECODE` and uses pyenv 3.13.12 directly. All commands ran in the checkout.

| Command | Result |
|---------|--------|
| `python3 -B -m unittest discover -s tests -p 'test*.py'` | OK (skipped=2) |
| The four new test ids by name | Ran 4, OK |
| `python3 -B scripts/check_breakout_tests.py` | Total 333, skips 2 (audio, env-gated) |
| `python3 -B scripts/check_breakout_terminal.py` | PASS: real PTY input, launch, pause, resize, restart, quit, Ctrl-C; terminal restored |
| `python3 -B -m tink_breakout --help` | exit 0 |
| `python3 -B _system/scripts/sdlc.py walk` | 8 passed, 0 warned, 0 failed (incl. W8 triggers-locked) |
| SDLC wrapper `status breakout-session-best --json` | `verification_status: current`, result passed, candidate tree `3c0061b…`, checklist 7/7 (6 checked, 1 attested), next action "independent PR review and release checks" |
| `ast.parse` of `_system/scripts/stations.py` and `sdlc.py` | OK |
| Grep of both scripts for `shell=True`, `eval`, `exec`, network calls | None. The existing `unlink`/`rmtree` are on temp and log paths only |

The terminal script rewrote the tracked `runs/breakout/04-test/output/terminal-transcript.txt`. I read it for the HUD check above, then restored it with `git checkout --`. `git status` was clean apart from this file.

## Remaining uncertainty and gates

- I checked the SDLC 1.21.0 upgrade (`stations.py` is new, 649 lines; `sdlc.py` has 298 changed lines) only structurally, by running `walk`, a parse and a grep. I did not review it line by line.
- There is no forge CI in this repo (removed in 883e31e), so the "current required CI" release gate cannot be met by CI. Code-owner approval and the merge decision stay with the human (Jon). This file approves nothing.
