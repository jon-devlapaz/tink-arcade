status: confirmed for intake
# Seed: Create and register an original tink-arcade cabinet titled “Last Time”.
revision: r1
Confirmed by: "I confirm this seed for Last Time: arrow-key light movement, collectible sparks as the score, one life, exact synchronized replay of every completed 15-second path, stacking ghosts and fatal ghost contact. Start with no ghosts and prevent unavoidable transition deaths. No extra enemies or mechanics. Implementation details and runnable checks still belong to the builder, and fun, feel and visual taste remain for jondev. I answered only the pre-mortem; the other quoted probe is a drafting inference, not another operator answer. The invalid line citations are not verified evidence. This confirms the seed, not build approval." (revision r1, 2026-10-21). Not approved for implementation.
date: 2026-10-20

## You are confirming
Goal: Create and register an original tink-arcade cabinet titled “Last Time”.
What gets built: A dark arena game where a small light collects sparks, rounds last 15 seconds, prior timed paths replay as synchronized stacking ghosts, touching a ghost ends the game, arrow keys control movement, one life is used, and the score counts sparks collected.
What does not: No added enemies or mechanics; the only enemy is the player's past actions.
Proposed first slice: Inspect the closest engine and UI tests, then implement a deterministic replay slice.
Unknowns: Exact implementation design, arena presentation, spark placement, movement tuning, and new test names.

## Problem statement
Last Time needs to be added as an original tink-arcade cabinet where the player's past actions are the only enemy. The intended experience starts calm in a dark arena and becomes tense as synchronized ghost paths accumulate.

## Proposed outcome
A registered Last Time cabinet lets a small light collect sparks with arrow keys. Rounds end every 15 seconds; each completed round is replayed exactly as a ghost in subsequent rounds; ghosts stack; touching one ends the player's single life; and the score counts collected sparks.

## Acceptance criteria

A small light can collect sparks in a dark arena.
not yet runnable: A Last Time implementation and behavior-specific assertion do not yet exist.

Each round ends every 15 seconds.
not yet runnable: A Last Time engine test and confirmed repository invocation do not yet exist.

The previous round replays exactly as a ghost.
not yet runnable: A deterministic replay assertion and invocation do not yet exist.

Touching any ghost ends the game.
not yet runnable: A ghost-collision regression assertion and invocation do not yet exist.

Ghosts stack across rounds.
not yet runnable: A stacking regression assertion and invocation do not yet exist.

The player uses arrow keys and has one life.
not yet runnable: Arrow-key and one-life assertions and a confirmed invocation do not yet exist.

The score counts sparks collected.
not yet runnable: A score-specific regression assertion and invocation do not yet exist.

The cabinet is registered like the other cabinets.
not yet runnable: The Last Time package and registry entry do not yet exist.

## Affected users and systems
Players use the registered Last Time cabinet through the arcade menu. The new package will follow the repository's terminal-cabinet structure and connect to arcade_menu/games.json.

## Constraints and boundaries
The cabinet uses arrow keys, one life, and a score equal to sparks collected. It starts with no ghosts; each completed 15-second round records the exact timed path, and past paths replay in sync as ghosts. Touching a ghost ends the game. No added enemies or mechanics are proposed.

## Decisions (from the ledger)
- goal [user] Create and register an original tink-arcade cabinet titled “Last Time”. Why: The game should start calm and become tense as ghosts stack, with the only enemy being the player's past actions. Done when: A small light can collect sparks in a dark arena; each round ends every 15 seconds; the previous round replays exactly as a ghost; Touching any ghost ends the game; Ghosts stack across rounds; the player uses arrow keys and has one life; the score counts sparks collected; the cabinet is registered like the other cabinets. Must: use arrow keys. Must: have one life. Must: make the score sparks collected. Must: build and register it the way the other cabinets are. (source: Goal confirmed in Tinkery with typed confirm and Enter; caller-declared attribution: not declared; typed confirm at this terminal; declaration is not verified identity; goal only, not seed or implementation approval.)
- probe-pre-mortem [user] The replay rules might feel unfair or not match what I actually did. Preserve the exact timed path of each completed 15-second round, replay all past rounds in sync each following round, and make touching a ghost clearly end the one life. Avoid unavoidable deaths at round transitions. Keep the controls and sparks readable, including without color. Start calm with no ghosts and let the accumulating past paths create the tension, not added enemies or mechanics. (source: the operator's own answer, typed in Tinkery Shape)
- read-structure [evidence] The repository says a new game is a package with engine.py, ui.py, and __main__.py, and that adding an entry to arcade_menu/games.json adds the cabinet. (source: read-only investigation in Tinkery Shape)
- read-stacker [evidence] Stacker separates deterministic rules in engine.py, terminal presentation/input in ui.py, and interactive startup in __main__.py. (source: read-only investigation in Tinkery Shape)
- read-menu [evidence] The registry is a JSON array of cabinet objects containing title, tagline, about, controls, path, and module fields; the existing Stacker entry follows this shape. (source: read-only investigation in Tinkery Shape)
- read-tests [evidence] The repository has cabinet-specific check scripts that discover tests, require named cases, and report missing or failing required tests. (source: read-only investigation in Tinkery Shape)
- inference-blast [evidence] The change will likely touch a new cabinet package, the arcade registry, cabinet-specific tests, and possibly a cabinet-specific check script; these areas could break registration, deterministic rules, terminal input, rendering, or required-test discovery. (source: read-only investigation in Tinkery Shape)
- unknown-tests [evidence] This investigation has not established the exact new test cases, CI invocation, or whether an existing generic checker can verify Last Time. (source: read-only investigation in Tinkery Shape)

## Assumed (not confirmed by you)
- none

## Knowledge map
What we know, with proof: the confirmed goal and operator answers establish the Last Time title, controls, one life, sparks scoring, 15-second rounds, exact replay, stacking ghosts, and registration requirement (observed 2026-10-21; re-check if the confirmed ledger changes). README.md documents that a new cabinet uses an engine.py, ui.py, __main__.py, and an arcade_menu/games.json entry (observed 2026-10-21; re-check if repository conventions change). Stacker demonstrates the nearby terminal-cabinet structure and test pattern (observed 2026-10-21; re-check if the package structure changes).

What we know we do not know: the exact implementation design and new regression-test names are not established; the implementer owns those decisions and should inspect existing engine/UI tests before coding.

What we have not read: the complete repository test suite, CI configuration, and every cabinet implementation.

What could surprise us: Probe: Imagine this shipped and turned out wrong. What is the most likely reason? — answer: The replay rules might feel unfair or not match what I actually did; preserve exact timed paths, synchronized replay, readable controls and sparks, and avoid transition deaths — changed: the draft requires timed-path preservation, synchronized ghosts, readable non-color-dependent presentation, and safe transitions. Probe: What would someone who has built replay-based games ask that we have not? — answer: How are timing, input sampling, and round-boundary synchronization represented so replay remains exact across frame-rate variation? — changed: the first slice and verification must cover deterministic timed replay rather than only visual behavior. A concrete signal that this is wrong is a replay diverging from the recorded path or a death occurring at a round transition.
Where we did not look: full test/CI coverage and every cabinet's registration details.

## Evidence and uncertainty
Grounded in:
- README.md
- arcade_menu/games.json
- scripts/check_stacker_tests.py

Provenance unavailable: reported reads do not verify filesystem origins or unrecorded reads. Some recorded findings have no attributable read path.

Checked by read-only file tools in /Users/jondev/dev/worktrees/tink-arcade/claude-new-cabinet:
- README.md:8-15: The repository says a new game is a package with engine.py, ui.py, and __main__.py, and that adding an entry to arcade_menu/games.json adds the cabinet. (observation; scope: repository cabinet conventions) (observed 2026-10-21)
Checked by read-only file tools in /Users/jondev/dev/worktrees/tink-arcade/claude-new-cabinet; citation not found: tink_stacker/engine.py has 56 lines, not 58:
- tink_stacker/engine.py:1-58; tink_stacker/ui.py:1-146; tink_stacker/__main__.py:1-35: Stacker separates deterministic rules in engine.py, terminal presentation/input in ui.py, and interactive startup in __main__.py. (observation; scope: nearby cabinet implementation) (observed 2026-10-21)
Checked by read-only file tools in /Users/jondev/dev/worktrees/tink-arcade/claude-new-cabinet:
- arcade_menu/games.json:1-151: The registry is a JSON array of cabinet objects containing title, tagline, about, controls, path, and module fields; the existing Stacker entry follows this shape. (observation; scope: cabinet registry) (observed 2026-10-21)
- scripts/check_stacker_tests.py:1-113: The repository has cabinet-specific check scripts that discover tests, require named cases, and report missing or failing required tests. (observation; scope: existing verification convention) (observed 2026-10-21)
Checked by read-only file tools in /Users/jondev/dev/worktrees/tink-arcade/claude-new-cabinet; citation not found: tink_stacker/engine.py has 56 lines, not 58:
- README.md:8-15; tink_stacker/engine.py:1-58; tink_stacker/ui.py:1-146; tink_stacker/__main__.py:1-35; arcade_menu/games.json:1-151; scripts/check_stacker_tests.py:1-113: The change will likely touch a new cabinet package, the arcade registry, cabinet-specific tests, and possibly a cabinet-specific check script; these areas could break registration, deterministic rules, terminal input, rendering, or required-test discovery. (inference; scope: likely Last Time change surface; limits: This does not establish the final file list or prove that no other integration files will be needed.; supported by: read-structure, read-stacker, read-menu, read-tests) (observed 2026-10-21)
Checked by read-only file tools in /Users/jondev/dev/worktrees/tink-arcade/claude-new-cabinet:
- tests/:1-200; scripts/:1-100: This investigation has not established the exact new test cases, CI invocation, or whether an existing generic checker can verify Last Time. (unknown; scope: repository verification coverage) (observed 2026-10-21)

## Suggested first slice
Proposal only: from the repository root, inspect the closest engine and UI test files before implementation with `sed -n '1,260p' tests/test_stacker_engine.py && sed -n '1,260p' tests/test_stacker_ui.py`. This is a discovery command, not authorization to implement.

## Risks and verification
Key risks are replay drift, unfair round-boundary collisions, unreadable sparks or ghosts without color, accidental extra lives or enemies, and failure to register the cabinet. Mitigations are deterministic timed-path recording, synchronized replay, explicit transition handling, monochrome-readable symbols, engine-level tests, UI checks, and a menu-registration check.
Probe: Imagine this shipped and turned out wrong. What is the most likely reason? — answer: The replay rules might feel unfair or not match what I actually did; preserve exact timed paths, synchronized replay, readable controls and sparks, and avoid transition deaths — changed: replay and transition fairness are explicit verification targets.
Probe: What would someone who has built replay-based games ask that we have not? — answer: How are timing, input sampling, and round-boundary synchronization represented so replay remains exact across frame-rate variation? — changed: deterministic timing and boundary synchronization are explicit verification targets.
Where we did not look: full test/CI coverage and every cabinet's registration details.

## Open questions and deferrals
No operator-only blocker remains. Implementation details such as the arena dimensions, spark placement, movement speed, rendering layout, and test names remain agent-owned and should be chosen consistently with repository conventions.

## Owners and next steps
The implementer owns the new engine, UI, entry point, registration entry, and regression checks. First inspect the closest engine/UI tests, then implement the smallest deterministic replay slice, register the cabinet, and run the confirmed checks. The operator retains review of the proposed checks and the resulting play experience.

## Downstream handoff
The session folder is the handoff: seed-contract.md, ledger.json, seed-confirmation.json, and seed-checks.json. A consumer can inspect it with tinkery seed status --json <session>. This is discovery input, not an implementation plan or approval to build.

