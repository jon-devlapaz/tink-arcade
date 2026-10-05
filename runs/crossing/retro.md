# Retrospective: crossing (dogfood, paused at menu-on-mac)

Outcome: branch `crossing` (commit 4abe880) adds `tink_crossing`, a menu entry,
README section, 22 tests, a legal-input win/loss replay, a PTY check and 20
captures. The four checked items pass when run directly. `verify` has not passed:
it refuses while the attested `menu-on-mac` item is unmarked. No PR yet; the
sandbox has no `gh`.

## Human decisions
- "approve" for the brief and 7-item checklist (stage 3 receipt).
- Delete permission on the mounted checkout, to clear git's lock file.
- Pending: run `python3 -B scripts/check_arcade.py` on the Mac, then PR and merge.

## What made this easier
- The Pong run was a complete template: engine/ui split, test runner, PTY
  checker and capture script all adapted with small edits. The PTY check passed
  first time.
- Integer-cell lanes made the win replay a small breadth-first search instead of
  a physics problem; the whole win replays in about a second.
- Captures caught a real readability bug (walls and cars shared `#`).

## What made this harder (system findings)
1. `sdlc.py stage` hard-requires a git identity and only offers worktrees. An
   operator whose filesystem view differs from the owner's (sandbox, container,
   remote agent) gets a worktree path that is wrong on the host. A `--clone PATH`
   option, or a documented clone fallback, would fit this case.
2. `verify` checks attested items before it runs any automated check, so one
   pending human item hides whether the code passes. Running checks first and then
   reporting the incomplete checklist would give earlier evidence.
3. Mounted folders that block deletes break git's lock protocol; the failure shows
   up as a stale `index.lock`, not as a permission error.
4. `scripts/check_arcade.py` assumes a working audio player, so `check_all.py`
   fails on Linux without audio for reasons unrelated to the change.
5. `_system/verification.json` runs the full unittest discovery twice and checks
   only Breakout `--help`; it does not include new games unless each brief adds
   checks.
6. `sdlc.py status` with no run prints only slugs, no state.

## Smallest justified next step
Jon runs the menu check on macOS and reports the result; the operator marks
`menu-on-mac`, reruns `verify`, and opens a PR for Jon to review and merge.
