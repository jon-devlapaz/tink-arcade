# Tron vs Jev — build brief r1

## Problem and outcome

Add a `--versus-jev` mode to Tron where the real Jev model steers player 2 against you, like Tetris vs Jev. Deliver a review-ready PR. Solo-vs-machine and two-player stay offline and unchanged.

Source: Jon asked for "a jev option" in chat after playing Tron, and chose "Jev picks routes; thinking time counts" for pacing. This is a proposal for the light-profile definition gate; no approval is recorded. Every number below is a proposed default to be tuned against real Jev latency.

**Depends on the Tron run.** This branches from the unmerged `tron` branch (PR for run `tron`) and must be rebased onto `main` after that merges.

## The pacing problem and the chosen answer

A model call takes seconds; a Tron step is 90 ms. Following the precedent in Tetris vs Jev ("Jev's thinking time counts as play time; no scripted fallback opponent"):

- The app enumerates candidate **routes** from Jev's cycle: fixed-length paths that stay on the grid and avoid every existing trail. Jev picks one with the existing `JevClient.choose` question format. The cycle follows the chosen route step by step.
- The app asks for the next route early, while the current one still has steps left, anchored at the cell where the current route ends, so a prompt reply arrives in time and the new route continues seamlessly.
- If a route runs out before a reply arrives, Jev's cycle keeps going straight. If straight is blocked it crashes. There is no scripted dodge. A slow Jev can lose by timing, and the on-screen status makes that visible (`Jev thinking`).
- The one exception is the start of a round: the round does not begin until Jev's opening route has arrived (or failed), so Jev is never beaten before the first step. Time spent waiting is shown, and the human is not penalised.

## Proposed rules

- `python3 -B -m tink_tron --versus-jev [--seed INT] [--no-color] [--no-sound]`. It requires `TYPESAFE_API_KEY` in the environment, never read from or written to any file. It is mutually exclusive with `--two-player` and `--level`. Menu: add a "Tron vs Jev" cabinet with `requires_env`, and a billing note, as Tetris vs Jev has. Routine checks never launch it.
- Route length 16 steps; the next request is made when 10 steps remain (so about 0.9 s at 90 ms). Candidate routes: straight, plus routes with up to two turns at steps drawn from {2, 4, 6, 8, 10, 12}, left or right, keeping only those fully clear of current trails and walls, in a stable order, capped at 60. If none are clear, Jev's cycle goes straight and the status says no safe route. Constants live in one place and are tuned after measuring latency.
- Each candidate carries only neutral facts the app computed: first-turn direction, number of turns, cells in the room reachable at the route's end, distance from the route's end to the player's head, and distance to the nearest wall. Options are not ranked or recommended. The prompt tells Jev the board orientation (x=0 left, y=0 top), that it is racing to win rounds, that crashing loses, and that the player's cycle keeps moving while it thinks.
- One request in flight at a time. A reply is applied only if it matches the current round and request identity; stale replies after restart, pause-and-restart or a new round are discarded, but their reported usage still counts toward cost.
- An error (timeout, HTTP error, malformed reply, invalid choice) pauses the game, shows a short message without secrets or response bodies, and offers Enter to retry, R to restart, Q to quit. No hidden retries.
- Match rules, scoring, controls, rendering and audio are unchanged. The scoreboard row names the opponent `JEV`, shows a status (`Jev thinking`, `Jev route ready`, or an error), and shows the session cost estimate.
- Cost display reuses `neon_tetris.jev.Cost` (price per input token at `jev-1.13.0`, with unknown/pending shown, as in Tetris vs Jev). There is no spending cap. The final line after quit reports total cost and any uncertainty.

## Acceptance criteria and approach

1. Reuse `neon_tetris.jev` (`JevClient`, `Worker`, `Reply`, `Cost`) by import. The only change to that module is making the question's `instructions` text a parameter whose default is the existing Tetris text, so Tetris vs Jev behaves exactly as before. A test proves the Tetris prompt is byte-for-byte unchanged.
2. Pure, deterministic route enumeration in a new `tink_tron/jev_routes.py`: tests prove routes never enter walls or trails, stay within the cap, are stable across calls and are fully clear; and prove the facts are computed correctly on constructed boards.
3. Engine/controller tests with a fixture provider (no network, no key): route following; early replanning anchored at the end of the current route; exhaustion goes straight and crashes with no dodge; a round waits for the opening route; stale replies are ignored but their cost counts; one request in flight; error pauses and Enter retries; pause, resize and restart behave as in the other modes; the key is never written to the trace, errors or transcript.
4. UI tests for the status text, cost display, error overlay and layout at 80 × 30 and 100 × 35, and cabinet launch refusal with a clear message when the key is missing.
5. The real PTY check drives the actual program with a fixture provider selected only by the check script (not by any user-facing flag), including an error and retry. A separate `--live` option calls real Jev and incurs usage; it is never part of the routine suite.
6. **Live measurement, with Jon's go-ahead:** before finalizing the constants, make a few real calls (each is a fraction of a cent) to record latency and token usage, then tune route length and the early-request threshold from the measurements. Record the numbers and the estimated cost in the run's evidence. Do not run live calls without Jon's say-so.
7. README and DESIGN document launch, the key requirement, billing, the pacing rule and its consequence (slow replies can lose a round), and the privacy boundary (only the board state and route facts are sent). The existing full check (`python3 -B scripts/check_all.py`) passes with Tetris vs Jev unchanged.

## Risks and verification

- **Latency decides strength.** If Jev replies slower than a route lasts, Jev loses by timing and the mode feels broken. Mitigation: the live measurement above and the early-request margin. If the measurement shows replies take longer than any sensible route, stop and bring that to Jon rather than adding a hidden fallback.
- **Cost.** Each decision sends a prompt with up to 60 candidates every ~1.4 s of play. At the published input rate this is small but unbounded over a long session. The cost line makes it visible; there is no cap. Jon decides whether to add one later.
- **Privacy.** The API receives only board state and route facts. The key stays in the environment; tests assert it never reaches the trace or transcript.
- **Whether Jev is fun or good** needs human play. Those are attested items; none will be marked without a real observation.

`checklist.json` holds the repeatable commands. Tests and scripts named here do not exist at planning time.
