# Baseline review: check-evidence

Decision: **ACCEPT** the baseline as a reproduction of the reported checker defects.
Reviewer: independent Codex agent `patch_baseline_review`, 2026-10-04.
This accepts the test baseline only. It is not human brief approval or release approval.

## Evidence

Reviewed the root instructions, installed SDLC baseline rules, stage 01 context, brief, checklist, test file, retained failure log, and relevant checker and game-loop source. Independently ran:

```sh
python3 -B -m unittest discover -s tests -p test_terminal_checkers.py -v
```

At HEAD `2125a67b3ebef15e3f3a7acf292d116144fed9d6`: exit 1, four tests, three failures, 8.452 seconds. The early-input case and negative controls pass. The delayed-input case fails at the queued-turn snapshot assertion despite real-loop heads `[10,10]`, `[10,9]`, `[9,9]`. Both full PTY scripts report success but replace the sentinel at their default output path. These are the intended failures, matching the retained log.

## Assessment and limits

- Meaningful: the queue trace comes from the real game loop and engine under a controlled clock; it preserves the full trace. The output tests execute actual scripts and check that existing evidence survives.
- The replay keeps the existing `Terminal.wait` behavior and arrow-input interface. Its synthetic terminal and `QueueComplete` stop isolate the queue check; they do not prove a live scheduling failure or all later terminal behavior. This small interface coupling is acceptable for this repair, but should not be mistaken for implementation-independent coverage of any future checker design.
- Negative controls reject missing input and up-only movement. Reversed keys also become up-only movement because the game rejects the initial reverse turn. They do **not** prove rejection of a trace containing both movements in the wrong order. Add a separate supplemental wrong-order trace check during final verification, without editing this accepted baseline, and inspect that movement observations are after input and ordered.
- The test is self-contained for locking: its clock, fixtures, replay, and runner entrypoint are in `tests/test_terminal_checkers.py`; it imports production game code, not an editable external fixture helper. Preserve the game packages as required by the brief. The checker files remain repair targets, not locked test helpers.
- Destination coverage includes an absolute external path with spaces and missing parents. Default/relative paths, argument errors, and failure transcripts remain separate checklist work.
- Side effects are contained in temporary copies and temporary trace destinations. The two real PTY runs confirmed terminal restoration and process-group cleanup. No retained game transcripts, production files, test files, or approval records were changed by this review.

Required skill: `principle-build-the-lever`; the existing rerunnable baseline was used as the review artifact. No additional review framework was needed.

## SHA-256

| File | Digest |
| --- | --- |
| `tests/test_terminal_checkers.py` | `8cffa5d26fbff6a751c8c9ea2f1ae88f84a55a215fe884f93c2b1018627a216a` |
| `runs/check-evidence/01-plan/output/baseline.txt` | `cf41174a98e0860d270c6c4d049e0a4ddb84446faa4ace611f8f5dd24941bde1` |
| `scripts/check_snake_terminal.py` | `22e479398523c91aea848a1eec69b73f41c4f8421ee4b14e5c55710a33a5c207` |
| `scripts/check_breakout_terminal.py` | `5346f2bd42dae81337b2343f5b50c5cf1468cef0d9116837f3c40540cda24c11` |
| `tink_snake/engine.py` | `59cecfa78b27c724df773e8c31c5fce0ec484ba3f7753b99605bb2096b504e49` |
| `tink_snake/ui.py` | `d16d5cc6c5384980903d63cc045c10dbfbe2d4fa4de6f4059855edc2175e9e5e` |
