# Seed contract: Breakout trial
status: seed contract — confirmed for intake; not approved for implementation    revision: 2    date: 2026-10-04

## You are confirming
- Goal: add Breakout to tink-arcade and test whether substrate helps agents carry work from idea to PR.
- Build: solo terminal Breakout with paddle, bricks, score, lives, and three handcrafted boards. Clear each board to advance.
- Exclude from this slice: multiplayer, paid model calls, power-ups, and automatic dispatch or a new substrate workflow.
- Accepted: Jon selected Breakout; accepted the three-board proposal unchanged; independently named reliability, earned progression, and interesting layouts as priorities.
- Unknown: enjoyable difficulty, quality of the layouts, and whether a fresh agent can continue from saved files. No earlier decision is reversed.

## Goal and decisions
G [user] Build another classic game to test substrate and add to tink-arcade.
D1 [user] “Breakout — paddle, bricks, and lives.”
D2 [user] Failure would mean “its buggy and level progressions feel unearned.”
D3 [user] “i also prefer interesting designs of the board.” Jon then accepted three distinct handcrafted layouts, advancing only when each board is cleared.

## Assumed defaults — not confirmed individually
S1 [agent] Solo, offline terminal play, with pause, restart, and quit.
S2 [agent] Three lives across the whole run; clearing the third board wins. A lost life preserves cleared bricks; restarting resets the run.
S3 [agent] Different brick arrangements create aiming opportunities. Layout design, rather than automatic speed increases, is the first source of difficulty. No power-ups in this slice.
S4 [agent] Build on an isolated branch without merging or changing the two existing game PRs. Resolve the exact base from current Git state before implementation.

## Proposed acceptance checks
A1 [agent] The game launches, accepts paddle input, pauses, survives resize, restarts, and exits cleanly.
provisional: cmd: `python3 -B scripts/check_breakout_terminal.py` | expect: exit 0 after exercising the real terminal application | cwd: the future Breakout checkout. Script does not exist yet.
A2 [agent] Collision, scoring, life loss, and progression rules have tests, including corner hits, fast-ball brick crossings, last-brick clearing, final victory, and restart. No level advances while bricks remain; a brick scores only once.
provisional: cmd: `python3 -B -m unittest discover -s tests` | expect: exit 0 with Breakout cases discovered and existing tests preserved | cwd: the future Breakout checkout. Breakout tests do not exist yet.
A3 [agent] The three layouts are distinct and every breakable brick is reachable. Jon judges whether aiming and progression feel satisfying.
provisional: cmd: `python3 -m tink_breakout` | expect: a playable three-board run; record Jon's feedback separately from automated results | cwd: the future Breakout checkout. Module does not exist yet.
A4 [agent] A fresh agent uses only the handoff and its links to identify scope, actual permission, remaining work, and current evidence without repeating completed work. Save what it misunderstood, if anything. Proposed evaluation; no command or result exists yet.

## Knowledge map
- What we know: prior Galaga work has real terminal checks for pause, resizing, and restart. See E1. Recheck before reusing any code.
- What we do not know: collision reliability (builder will test); enjoyable layouts and progression (Jon will play); handoff sufficiency (fresh-agent trial).
- What we have not read: complete game engine, current upstream main, and the build-stage contract for the new run. The builder must inspect these before implementation; no claim of readiness is made here.
- Probe: Imagine the trial disappointed you; why? — answer [user]: buggy gameplay and unearned progression — changed: explicit collision and progression checks.
- Probe: What counterexample could defeat a passing game test? — answer [agent]: pause or terminal resize could advance unseen time and cost a life — changed: include real terminal checks. This is a hypothesis for Breakout, not an observed defect.
- Probe: What would an experienced game developer ask? — answer [agent]: can every brick be reached, and do corner impacts remain predictable? — changed: reachability and collision cases included; not independent expert testimony.
- Where we did not look: a running Breakout implementation, other terminal platforms, or human play feedback. These do not exist in this trial yet.
- We would know we were wrong if tests pass but Jon finds unfair deaths, tedious layouts, or progress that does not reflect clearing boards.

## Evidence
E1 [evidence] `expect(b'Terminal too small')` at /Users/jondev/dev/active/product/tink-arcade-galaga/scripts/check_galaga_terminal.py:67; `expect(b'PAUSED')` at line 79. Read 2026-10-04, checkout a31717385c71c2a55216a05e94df6f0fd297ce3a. Recheck if that checkout changes. Inspection is not a new execution result.

## Substrate learning
Record confusion or repeated work during delivery. Jon requested a shared Seed Me/substrate view; keep this as a follow-up proposal and record actual switching friction. Do not build that integration as part of the game by default.

## Next
Jon confirmed displayed revision 2 with “approved” on 2026-10-04. This is discovery input, not an SDLC approval receipt. The implementation workflow must inspect its actual gates and retain any required decisions. Delivery ends at a reviewable PR; merging is separate. Game feel stays unverified until played.
