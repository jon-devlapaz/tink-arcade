# Closure: crossing

Resumed after Jon's macOS menu check. This file is finalised after merge.

## State (2026-10-05)
- `menu-on-mac`: Jon reported `scripts/check_arcade.py` "all passed" on macOS
  at 7294c9c; marked as attested from his report.
- `verify`: current. Checklist 7/7 (4 proven by check, 3 attested). Status notes
  `visual-review` was attested before later changes; those changes touched
  README, the PTY checker and run notes, not the rendered UI.
- Independent review (Sonnet, read-only): ACCEPT WITH FIXES; fixes applied.
- Follow-ups filed: tink-sdlc #45 (closure record in SDLC.md), #46 (text status
  hides the verify failure reason).

## Remaining
1. Jon pushes `crossing` to origin (the operator sandbox has no GitHub
   credentials); the operator opens the PR.
2. Jon reviews and merges.
3. Record here: PR URL, merge revision, outcome. Then `archive --phase closure`
   from a host with tink-substrate installed.
