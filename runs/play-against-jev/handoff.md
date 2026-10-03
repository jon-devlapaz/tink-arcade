# Tetris versus Jev: current handoff

Updated 2026-10-03. This file reports progress. The approved brief records the
proposal as it stood at review; its future-tense statements are historical.
Use `python3 _system/scripts/sdlc.py status play-against-jev` for current receipts.

## Goal and location

A live side-by-side race to 20 lines against Jev, ending in a review-ready PR.
Jon chose the GitHub repository name `tink-arcade`; private visibility was retained
from the presented proposal. Owner is the authenticated account `jon-devlapaz`.

The original solo game remains at `/Users/jondev/dev/active/product/neon-tetris`.
The feature worktree is `/Users/jondev/dev/active/product/neon-tetris-jev`, branch
`feat/play-against-jev`. The local folder and Python module names remain unchanged
so the existing launcher keeps working. Use the feature checkout command to try
versus mode before merge. No changes to the Socratink learning app.

## Current implementation

- Match rules, request identity, pause/restart, winner and draw live in `race.py`.
- `jev.py` sends one real TypeSafe request at a time. A daemon worker isolates it
  from input. A deadline closes the connected socket, including a slow response.
- `race_ui.py` displays two full boards at 80 by 30, controls, errors, model and cost.
- Solo still uses the original path. The only engine addition identifies a newly
  spawned piece, including successive pieces with the same shape.
- Session cost survives restarts and accounts for stale replies. Unknown charges
  and in-flight usage stay visible. API keys come only from the environment.

## Evidence observed

- Original baseline: 78 tests, 2 skipped. Current suite after the timeout fix:
  110 tests, 2 skipped. Native audio checks are opt-in, not proven by those skips.
- First live call: `jev-1.13.0`, 971 input tokens, 0.222 seconds. A legal move applied.
- Actual curses PTY exercise passed input, pause, resize, resume, restart and quit.
  First successful run displayed an estimated $0.00187732 for that app session.
  This is not total development spend or an invoice figure.
- Live seed-1 observation with no human moves: the first prompt topped out after
  20 pieces and zero cleared lines in 4.76 seconds, 20 responses, estimated $0.00143661.
- Adding factual placement outcomes improved one seed-1 observation to 6 cleared
  lines and 47 pieces before top-out in 10.16 seconds, 47 responses, estimated
  $0.00538167. Options describe column heights, covered empty cells and top-out;
  the application does not rank them or choose a fallback move.
- Official API request/response shape and pricing rechecked from
  https://docs.typesafe.ai/primitives/choice.md,
  https://docs.typesafe.ai/sdk/python/api/types/responses.md and
  https://docs.typesafe.ai/models.md on 2026-10-03.

- Final live PTY rerun after the deadline fix also exercised a complete match by
  forcing the human board to top out. It displayed `Jev wins`, exited 0 and reported
  an estimated $0.00176278 for that session. Solo PTY smoke exited 0 as well.
  Failure recovery uses controlled fixtures; a real service outage was not induced.

## Independent review and continuation

Jon explicitly authorized a read-only reviewer. A fresh agent with no conversation
history read this checkout and correctly identified the feature, current approval,
remaining work, and evidence limits without asking Jon to reconstruct context.
The reviewer ran 108 tests with 2 skips before the timeout fix.

It reproduced one P2: the original socket inactivity timeout allowed a server to
keep a request alive by slowly sending bytes. The client now applies a whole-call
socket deadline; a local slow-server regression verifies termination. The reviewer
also identified stale prose in the approved brief. This handoff supplies current
state without editing the approved definition merely to report progress.

The first review covered a changing working tree, not the final commit. A follow-up
review must check the timeout fix and final candidate before closing review findings.
Automated review is advisory; it is not independent human release approval.

## Limits and next work

- Jev is still a weak opponent in observed play. These few runs do not establish
  consistent improvement, fairness, or enjoyment. Jon's competitive playtest remains.
- Tests simulate request errors, missing usage, stale replies and pause/retry.
  Real-service outages were not deliberately caused.
- A request already sent may still be charged after quitting. The final cost line
  reports pending usage. DNS resolution is provided by the operating system;
  the socket deadline interrupts connected I/O, not an unresponsive OS resolver.
- The checklist's real-terminal mark should cite the final rerun. Fresh orientation
  is demonstrated above. Commit the candidate, mark real observations, run factory
  verification, and inspect current status before opening the PR.
- Merge is not authorized. CI and the human PR review remain separate from local checks.

## Workflow learning

The pinned helper skills existed under `~/.tink-library/skills`; the earlier search
used older locations and incorrectly reported them missing. `tink library fetch`
confirmed unchanged installed copies. Required build/proof/writing helpers were read.
Build the Lever and Prove It Works led to the rerunnable PTY check and slow-server
regression. Features and Futures kept opponent experiments within one provider
boundary, without adding a general agent framework.
