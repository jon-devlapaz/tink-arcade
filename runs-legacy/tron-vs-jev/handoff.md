# Tron vs Jev — build handoff

Built from the approved brief (r1). Branch `tron-vs-jev` is stacked on `tron` (unmerged); rebase onto `main` after the Tron PR merges.

## Not done, and why

- **No live call to real Jev has been made.** Everything automated uses a fixture client. The route length (16), the early-request threshold (10 steps left), the route cap and the 90 ms step are the brief's proposed defaults and are **untuned**. Checklist item `jev-live-latency` is for a measured run, with Jon's go-ahead, and must not be marked without real numbers.
- **Nobody has played against real Jev**, so `jev-play-feel` is unmarked. Whether a slow reply costs Jev rounds, and whether that feels fair, is unknown until then. If measured latency is longer than any sensible route, the brief says to stop and bring it to Jon rather than add a fallback.

## Deviations from the brief (for review)

1. **Turn steps are {2, 4, 6, 8, 10}, not {2…12}.** With 12 included there are up to 73 candidates, over the cap of 60, and truncating would silently drop the late-turn routes. With five turn steps the maximum is 51, so nothing is cut.
2. **"Open cells reachable" does not count the cycle's own end cell** (it is occupied).
3. **Prefetch of the next opening route:** requested as soon as a round ends (while the result shows) and again at match start/restart. This is how the "round waits for the opening route" rule stays cheap; the brief described the wait, not the prefetch.
4. **Engine hook:** `Game(opponent=...)` and a `round_id` counter were added so an external opponent can steer and replies can be matched to a round. Existing behaviour is unchanged (all earlier Tron tests pass untouched).
5. **`--level` default moved from `'normal'` to `None`** so `--versus-jev` can refuse an explicit `--level`; solo still resolves to normal.

## Findings

- The first draft of the pilot tests hung: the human cycle drove into Jev's straight route and the round ended, so a loop waiting on the plan never finished. The rig now parks the human cycle, and loops are bounded.
- Mutation checks on the pilot (10 deliberate bugs: late route applied without checking the anchor, stale epoch steering, no early replan, cost skipped, a scripted dodge, no opening wait, retry that never clears, silent auto-retry, prefetch after match end, stale opening stored): all caught. One survivor (stale opening for a past round) was defensive code; a direct test now pins it.
- The PTY check was mutation-tested too (no opening wait; no prefetch): both caught.
- `neon_tetris/jev.py` changed in one place only: the prompt is now a parameter whose default is the existing text. A test compares it to the literal Tetris prompt copied from `main`.
- The fixture client is installed by the PTY check script replacing `tink_tron.__main__.make_client`; no flag or environment variable in the shipped program selects it.

## Cost

The estimate shown uses the existing input-token price for `jev-1.13.0` ($0.042 per million input tokens). A prompt carries up to 60 route descriptions plus the board, roughly one request every 1.4 s of play. Likely small, unmeasured, uncapped.
