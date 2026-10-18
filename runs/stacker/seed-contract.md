status: confirmed for intake
# Seed: I have created a Stacker game for tink-arcade.
revision: r1
Confirmed by: "I confirm" (revision r1, 2026-10-18). Not approved for implementation.
date: 2026-10-18

## You are confirming
You are confirming: Stacker available to tink-arcade, matching its style, with working sounds and real-game play.
What gets built: skill-based Stacker that automatically continues toward the top.
What does not: payout-controlled difficulty or a take-the-minor-win choice.
Accepted unchanged: 0 helper defaults; 2 operator-chosen gameplay decisions.
Still unknown: exact rules calibration and sound verification environment; no earlier decision is reversed.

## Problem statement
You want to add Stacker to tink-arcade. Earlier inspection found no Stacker implementation or registered cabinet. The work needs both recognizable stacking gameplay and integration with the existing terminal arcade.

## Proposed outcome
Stacker is available from tink-arcade, matches the tink-arcade style, has working sounds and plays like the real game, with the settled skill-based timing and “aim for top” progression. Moving rows, lost overhang blocks and climbing toward the top are the proposed gameplay interpretation; precise dimensions and timing remain implementation research, not confirmed specifications.

## Acceptance criteria

```json
[
  {
    "cmd": "python3 -B scripts/check_arcade.py",
    "cwd": ".",
    "expect": "Exit 0, including PASS Stacker for the registered Stacker cabinet, with successful launch, mute and return to menu.",
    "kind": "cmd",
    "source": "Confirmed goal; proposed invocation from scripts/check_all.py:7–12; existing behavior assertions in scripts/check_arcade.py:38–65. Prerequisite: Stacker must be registered as a noncredentialed cabinet; this check alone cannot detect omitted registration. Intended targeted red: revert Stacker mute or return handling so the existing muted or menu-return assertion fails; not run.",
    "statement": "stacker available to tink-arcade"
  },
  {
    "how_to_judge": "Play Stacker alongside existing cabinets. Inspect shared paper/ink/jade presentation, readable controls and states, consistent overlays and short mechanical feedback. Confirm the game feels part of tink-arcade rather than a neon cabinet imitation.",
    "kind": "judge",
    "source": "Confirmed goal; README.md:23–26 and DESIGN.md:134–169; earlier presentation findings remain in the ledger.",
    "statement": "matches the tink-arcade style"
  },
  {
    "cwd": ".",
    "expect": "Successful Stacker actions produce appropriate audible mechanical cues across repeated plays; mute and --no-sound suppress playback as specified; unavailable audio does not prevent play; resources are released on exit. Repeated playback advances and sample levels are nonzero; listening confirms quality on the intended output device.",
    "kind": "provisional",
    "missing": "Stacker audio integration and its behavior-specific regression assertions do not yet exist. A concrete applicable sound-test invocation and intended-device verification setup have not been established. Add checks whose assertions fail when Stacker cue dispatch or repeated-play servicing is removed, plus device listening.",
    "source": "Confirmed goal; DESIGN.md:147–165 requires successful-action feedback, mute/no-sound behavior, repeated-play advancement, nonzero sample levels and listening.",
    "statement": "has working sounds"
  },
  {
    "cwd": ".",
    "expect": "Moving rows lock according to fair skill-based timing; only overlapping blocks survive, overhang is lost, zero overlap ends the run, and successful rows progress automatically toward the top without a take-the-minor-win choice. Deterministic regression assertions cover these behaviors, and play inspection confirms recognizable Stacker feel.",
    "kind": "provisional",
    "missing": "Stacker rules implementation, verified rules calibration and behavior-specific tests are absent. Establish an exact invocation once those tests exist; overlap-retention assertions should fail under a targeted overhang-rule reversion, and progression assertions should fail if automatic advancement toward the top is removed.",
    "source": "Confirmed goal; settled stacker-fidelity answer “skill” and prize-progression answer “aim for top.” Earlier repository search found no Stacker implementation or tests.",
    "statement": "plays like the real game"
  }
]
```

## Affected users and systems
Players use the arcade menu and a new game module. Proposed changes cover a rules-only engine, PaperRenderer-based UI, module entry point, cabinet registration, documentation and Stacker regression tests. Shared rendering and audio are integration dependencies; changing those shared implementations is not yet demonstrated necessary.

## Constraints and boundaries
Preserve the confirmed goal and the ledger’s settled gameplay choices. Follow the repository’s game structure, presentation, terminal and audio contracts. This seed does not authorize implementation. Technical choices described here are proposals unless already settled in the ledger.

## Decisions (from the ledger)
- goal [user] I have created a Stacker game for tink-arcade. Why: I want to add a game to tink-arcade. Done when: stacker available to tink-arcade; matches the tink-arcade style; has working sounds; plays like the real game. (source: Goal confirmed in Tinkery with typed confirm and Enter; caller-declared attribution: declared: human; typed confirm at this terminal; declaration is not verified identity; goal only, not seed or implementation approval.)
- stacker-fidelity [user] skill (source: the operator's own answer, typed in Tinkery Shape)
- prize-progression [user] aim for top. (source: the operator's own answer, typed in Tinkery Shape)

## Assumed (not confirmed by you)
- none

## Knowledge map
What we know, with proof: the recorded findings establish the game-addition structure and menu/audio contracts. See the helper-inserted evidence and ledger rather than treating this prose as a second findings list. Earlier observations are dated in the ledger; fresh reads in this step have no independently supplied observation timestamp. Re-check integration sources before implementation if they change.

What we know we don’t know: exact Stacker dimensions, row progression and timing calibration need an implementation-agent rules investigation against the operator-supplied reference. That reference has not been read here. The implementation agent must also establish the intended audio device and runnable sound-verification environment.

What we have not read: the shared renderer/audio implementations, all existing game engines and tests, and the external Stacker reference. No close-checklist artifact or session-folder path was supplied.

What could surprise us: Probe: terminal input sampling could make apparently fair timing inconsistent. Probe: repeated audio calls could succeed without audible playback. Where we did not look: actual gameplay execution, audio hardware and external rules evidence. Signals that would show the proposal is wrong include inconsistent placement for identical engine inputs, silent repeated cues, or inability to return to the menu.

## Evidence and uncertainty
Grounded in:
- AGENTS.md
- DESIGN.md
- README.md
- _system/SDLC.md
- arcade_menu/games.json
- scripts/check_all.py
- scripts/check_arcade.py
- tink_snake/__main__.py

Provenance unavailable: reported reads do not verify filesystem origins or unrecorded reads. Some recorded findings have no attributable read path.

Checked by read-only file tools in /Users/jondev/dev/active/factory/tink-arcade-taste2:
- README.md:1–26; tink_snake/__main__.py:1–35: This is an offline Python terminal arcade. The documented addition path is a rules engine, PaperRenderer-based UI, module entry point and menu registration. A new Stacker package would touch those execution paths; terminal entry, exit and optional sound must remain reliable. (observed 2026-10-18)
- DESIGN.md:5–35, 130–170: The documented style is paper, ink and jade with short mechanical feedback, not cabinet neon or music. Shared sound conventions include mute, disabled/unavailable states and graceful audio failure. These rules guide presentation, but do not settle whether Stacker should reproduce payout-controlled behavior. (observed 2026-10-18)
- arcade_menu/games.json:1–100: The inspected registry entries launch Python modules and supply cabinet descriptions and controls. Adding Stacker will affect menu selection and launch behavior. The inspected portion contains no Stacker entry; the rest has not yet been read. (observed 2026-10-18)
- scripts/check_arcade.py:14–65; scripts/check_all.py:7–23: The existing end-to-end check launches registered noncredentialed games, expects the shared paper presentation and sound status, mutes, quits and returns to the menu. Stacker will enter this check through registration; incompatible labels, mute handling or exit behavior could break it. Unit discovery also runs through check_all. Neither check was run, and Stacker-specific rules assertions have not been identified. (observed 2026-10-18)
- AGENTS.md:1–11; _system/SDLC.md:22–30, 44–46: Repository instructions require isolated code-writing work and human-selected downstream workflow approval. This interview does not authorize implementation. (observed 2026-10-18)
- README.md:19–27: New games use a rules-only engine.py, a PaperRenderer-based ui.py, a module entry point and a menu registry entry. Stacker therefore touches rules, rendering, launch integration and documentation; shared terminal and audio behavior must remain compatible. (observed 2026-10-18)
- Repository file search **/*stack*; tests/ directory listing: No matching Stacker paths were found, and the tests directory lists no Stacker-specific tests. Rules and progression regression coverage will need to be added; no Stacker implementation or verification was established. (observed 2026-10-18)
- arcade_menu/games.json:100–175: The previously unread registry tail contains Crossing, Tron variants, Wordle and Pac-Man, then ends. Together with the earlier inspection, no Stacker cabinet is registered. Adding one exposes it to the menu launch check. (observed 2026-10-18)
- scripts/check_arcade.py:38–65; scripts/check_all.py:7–12: The existing menu check launches every noncredentialed game, asserts paper branding and sound status, mutes and quits back to the menu. Stacker could break those assertions or trap the menu if its launch, mute or quit behavior differs. The aggregate checker also discovers tests under tests/. These checks were read, not run. (observed 2026-10-18)
- DESIGN.md:134–169: The sound contract specifies short mechanical cues, visible sound state, mute and no-sound handling, graceful failures and resource cleanup. It explicitly requires repeated-play advancement and sample-level verification plus listening, rather than treating a successful playback call as proof of sound. These are integration and verification concerns, not reasons to reopen the settled skill-based choice. (observed 2026-10-18)
- README.md:19–28: New cabinets require registration and a package with rules-only engine.py, PaperRenderer-based ui.py and __main__.py. These are the proposed implementation and documentation blast radius. The documented aggregate check command is python3 -B scripts/check_all.py. (observed 2026-10-18)
- scripts/check_all.py:7–23: The aggregate checker runs unittest discovery under tests and the menu end-to-end script, reporting All checks passed. New Stacker tests will enter discovery; registration exposes Stacker to menu checks. Nothing was executed. (observed 2026-10-18)
- scripts/check_arcade.py:38–65: Every noncredentialed cabinet is launched. Assertions require shared branding, paper presentation, sound-on status, muted status and return to the arcade menu. Stacker integration could fail these assertions or leave the menu unreachable. This does not assert that Stacker exists or that its sounds are audible. (observed 2026-10-18)
- DESIGN.md:134–169: The audio contract uses short mechanical cues, successful-action feedback, mute and no-sound states, graceful failure and cleanup. It specifically requires repeated playback advancement, nonzero sample levels and listening. New Stacker audio integration must preserve these behaviors; no playback was verified. (observed 2026-10-18)

## Suggested first slice
Proposal only: first establish the repository baseline with `python3 -B scripts/check_all.py`, working directory `.`. Then investigate and specify the smallest rules-engine slice: locking a moving row, retaining overlap, losing overhang and ending on zero overlap. This is a starting point for downstream approach drafting, not implementation approval.

## Risks and verification
All checks are proposed and none were run. Existing menu assertions cover presentation tokens, visible sound state, mute and return-to-menu behavior, not audible output or correct stacking rules. Once Stacker is registered, deliberately reverting its mute handling should make the existing `muted` assertion fail; reverting its return path should make the menu-return assertion fail. These are intended red probes, not observed failures.

New deterministic regression assertions are needed for overlap, overhang loss, zero-overlap loss, skill-based placement and automatic progression to the top. Sound verification must include repeated-play advancement, nonzero sample levels and listening, not merely successful playback calls. Human inspection remains necessary for visual fit and recognizable game feel.

## Open questions and deferrals
Non-blocking implementation research: establish exact rules calibration from the supplied reference before implementing gameplay; owner: implementation agent. If that research reveals materially different player-visible interpretations beyond the settled choices, return the choice to the operator rather than silently selecting one.

Audio-device availability and native/fallback test prerequisites remain unverified; establish them before sound acceptance. Session-folder location remains unknown and must be supplied by the helper for handoff.

## Owners and next steps
Known repository conventions and operator gameplay choices map to settled evidence and decisions in the ledger. Rules calibration and audio environment are risks to investigate, not new settled defaults. The implementation agent owns reading the unread integration code, tests and reference before proposing an approach. Timing inconsistency and silent repeated playback are risks with deterministic-engine and repeated-audio guardrails respectively. The operator confirms this seed and selects the downstream workflow separately; no implementation approval is implied.

## Downstream handoff
The helper’s session folder is the handoff: `seed-contract.md`, `ledger.json`, `seed-confirmation.json` and `seed-checks.json`. A consumer checks `session.py status <session>` and requires `handoff.verified` to be true; this verifies confirmed content, not identity. This artifact is discovery input, not an implementation plan, approved specification or review receipt. Preserve accepted constraints, follow the selected workflow’s active contract and surface conflicts rather than replacing decisions. No downstream profile or stage approval is selected here.
