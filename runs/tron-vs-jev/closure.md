# Tron vs Jev — closure

## Outcome
Merged. PR: https://github.com/jon-devlapaz/tink-arcade/pull/17 ("Add Tron vs Jev"), stacked on #16 and retargeted to `main` after #16 merged. Merge revision: `3c752f6f90c4f77bb895c3d7792ec72b7e416ec7` (merge commit on `main`). Delivery archive: `~/.local/share/tink-substrate/archive/tink-arcade/tron-vs-jev/` (phase `delivery`). The earlier delivery archive is not revised.

## Observed checks
- No CI exists for tink-arcade. Gate was the local SDLC run: checklist 8/8, `Verification: current` at delivery, and it still reads current on merged `main`.
- Live measurement before merge (Jon's go-ahead, 2026-10-05): 6 real `jev-1.13.0` requests, all valid, 0.19-0.29 s against a 0.90 s budget, est. cost about $0.0008 (`04-test/output/live-latency.json`).
- On merged `main` at `3c752f6`: `scripts/check_all.py` passed, 329 tests OK, 2 pre-existing skips; Tetris vs Jev unchanged.

## Human feedback
Jon said both Tron games are good and agreed to record that. He did not say whether he played against real Jev, which levels, or whether slow replies cost Jev rounds.

## Remaining limits
- The live sample is six sequential calls from one machine; reported input tokens took only two distinct values across six different payloads (unexplained), so cost may not track payload size.
- Nothing measures Jev's move quality or whether it wins on merit. No long-session cost data; there is no spending cap.
- Not exercised: a real Jev error or timeout in play (covered only with the fixture client).

## Follow-ups
Play more against real Jev and watch whether slow replies ever lose it a round; revisit the route length only if they do. A way to dry-run checklist `check` commands before the approval gate is a possible small tooling idea, not justified by a single occurrence.
