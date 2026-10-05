# Retrospective: crossing (dogfood, paused at menu-on-mac)

Outcome: branch `crossing` (code first committed in 4abe880) adds `tink_crossing`, a menu entry,
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
2. Retracted after independent review. `verify` did run every configured and
   checklist check (see `test-log.md`) and only then refused on the pending
   attested item; the operator read only the final error line. What remains: the
   receipt says `failed`, and text `status` then prints "implement the approved
   brief" instead of the reason, which the JSON `next_action` carries.
3. Mounted folders that block deletes break git's lock protocol; the failure shows
   up as a stale `index.lock`, not as a permission error.
4. `scripts/check_arcade.py` requires `key sound on`, so it fails without an
   audio player. It stops at the first failure (Tetris); it never reached Crossing.
5. `_system/verification.json` runs the full unittest discovery twice and checks
   only Breakout `--help`; it does not include new games unless each brief adds
   checks.
6. `sdlc.py status` with no run prints only slugs, no state.

7. How a run ends was unclear to the operator, who proposed a new `close`
   command. Review found Substrate already defines the end: `closure.md` plus
   `archive --phase closure` (`docs/finish-a-change.md`). The gap is that
   tink-sdlc's SDLC.md says "close the run and strip" without pointing there.

## Independent review
A separate model (Sonnet) reviewed the branch read-only: ACCEPT WITH FIXES, no
engine bugs. Fixed here: README overstated the maximum score (deaths can add row
points); the PTY mute steps passed vacuously without audio and now print SKIP.
Left as noted: level multipliers are rounded to whole steps (1.48-1.5x rather than
exactly 1.5x); a hop into a wall still scores row 0 before the life is lost.

## Smallest justified next step
Jon runs the menu check on macOS (this also exercises real mute); the operator
marks `menu-on-mac`, reruns `verify`, and opens a PR. After Jon merges, write
`closure.md` (PR URL, merge revision, outcome) and archive with `--phase closure`.
