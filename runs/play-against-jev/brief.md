# Play against Jev — build brief r1

## Problem and outcome

Play the existing terminal Tetris game against a real Jev opponent, side by side.
First to clear 20 lines wins; topping out loses. Deliver a review-ready PR.
Source: `seed-contract.md`, accepted in chat when Jon said “begin”.

Proposed workflow: light, one combined review of this brief and `checklist.json`.
This is a bounded feature in a small local game. No approval receipt has been recorded.

## Acceptance criteria

- Preserve solo launch, existing keyboard controls, paper/ink styling, and audio.
- Add `python3 -m neon_tetris --versus-jev --seed 1`. Show two full boards, hold/next
  information, each player's progress toward 20, match status, and estimated cost.
- Both games use one shared seed and the existing gravity/scoring rules. If no seed
  is supplied, generate one once for the match. Ordinary Jev thinking does not pause play.
- Reaching 20 wins; topping out loses. Simultaneous completion is a draw. Resolve
  events consistently rather than giving the first board updated an advantage.
- P pauses both; R restarts the match; Q quits. An error or timeout pauses both,
  shows a useful error, and offers explicit retry or quit. Resizing too small freezes
  play without catch-up when size recovers. Restart discards old gameplay replies.
- Network calls cannot block input or rendering. At most one request remains in
  flight; restarting cannot create accumulating workers. No hidden automatic retries.
- Jev chooses its moves. A fixture provider is for tests only; do not substitute a
  scripted player when the service is unavailable. Invalid replies use the error path.
- Show cumulative estimated USD for the app session, including rematches and retries.
  Count each completed response once even if its gameplay result is stale. Missing
  usage, uncertain failed-request charges, or unknown pricing make the estimate
  visibly incomplete. Display enough precision for small charges. Impose no cap.
- No credentials or private request data in Git or evidence logs. Use an environment
  variable for the API key. Keep the selected model and price basis visible/documented.
- Real terminal and live-service evidence must accompany the PR. Passing unit tests
  does not establish that Jev is a fun or balanced opponent; Jon judges that by playing.

## Approach

Reuse `Game` for both boards. Keep network work outside the engine and curses thread.
Proposed additions:

- `race.py`: `Race` owns two games, match state, update order, pause/restart, and
  request identity. The main thread is the only writer of game state.
- `jev.py`: an HTTP client accepts a copied board snapshot and returns a validated
  decision plus model/usage information. A single worker exchanges immutable results
  through a queue. Requests have a finite timeout; quitting must not wait for one.
- `race_ui.py`: two-board rendering and controls, reusing existing drawing primitives
  where useful. Start with an 80-by-30 layout and check actual readability; document
  any larger minimum before calling the feature complete.
- `__main__.py`: opt into versus mode; solo continues through its existing path.

First implementation experiment: Jev chooses a target rotation and column, then
normal engine operations move and drop the piece. Enumerate valid choices without
ranking them heuristically; Jev makes the choice. Validate against the current board
and piece before applying. A request belongs to a match and piece generation, so a
piece that locked while waiting cannot receive its predecessor's action. Recheck the
actual API and measure this approach before committing to it; revisit the brief if
playability requires changing the accepted rules. Hold remains available to both.

Use a controllable fake provider to prove pause, delayed response, restart, and
failure behavior first. Then integrate the real service and test a terminal match.
No networking framework, new dependency manager, plugin system, leaderboard, garbage
attacks, online human multiplayer, or tink-substrate runtime in this change.

## Work and checks

1. Add the match controller and deterministic race tests.
2. Add the provider boundary, honest cost accounting, and delayed/error fixtures.
3. Add the terminal layout and CLI, then test input and resize behavior.
4. Connect real Jev, record sanitized live evidence, and fix demonstrated problems.
5. Commit the candidate, run factory verification, and deliver the PR after the
   GitHub destination and visibility are chosen. Merge remains a separate decision.

Baseline in this worktree: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`
passes 78 tests with 2 native-audio skips. Existing audio files are unchanged.
The configured factory check rejects zero discovered tests. New race/cost/UI checks
in `checklist.json` are proposals and will fail until those test modules exist.
Final command: `python3 _system/scripts/sdlc.py verify play-against-jev`.

## Risks and evidence limits

No live Jev call or terminal race has run. Actual model quality, latency, pricing,
credential availability, and screen readability remain to be checked. A timeout or
failed call may have incurred charges; do not label it free. Validate the price for
the resolved model using official TypeSafe documentation before enabling estimates.

The first useful slice is a functioning two-board race with a fixture provider;
it answers whether match control and screen layout work. Real Jev follows within
this same approved scope. Keep provider replacement possible through one small
boundary; add no general agent abstraction. Reassess only demonstrated friction.

For the factory trial, record whether a fresh reviewer can identify scope, state,
and next steps from these files. Structural lint alone cannot prove that. Independent
review is still needed; no reviewer or human acceptance is fabricated.

## Handoff

Original game: `/Users/jondev/dev/active/product/neon-tetris`, main baseline `c83dd82`.
Build: `/Users/jondev/dev/active/product/neon-tetris-jev`, branch `feat/play-against-jev`.
The installed `socratink-tetris` launcher still points at the original game.
GitHub owner/name/visibility are not selected; no remote or publication exists.

Features and Futures kept this to one playable feature and one provider boundary.
Named planning helper skills were not found in the local skill locations searched;
no optional skill fetch or routing call was made. The plan and proof commands here
are explicit rather than depending on an unavailable helper.

Next: Jon reviews the proposed light workflow, this brief, and checklist. Only then
record the real stage-3 decision and begin implementation.
