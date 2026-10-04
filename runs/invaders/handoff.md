# Invaders planning handoff

## State and next action

Planning proposal completed on 2026-10-04. Read [brief.md](brief.md) and [checklist.json](checklist.json), then check `python3 _system/scripts/sdlc.py status invaders --json`. The stage-3 definition gate is pending. The coordinator must read the final brief and obtain one actual human decision before opening a fresh build stage. No implementation, approval, test lock, commit, push or merge occurred in this planning session.

Space Invaders, three shared lives, three waves and numeric rules are proposed defaults. Jon's optional game-selection answer was not supplied; the coordinator is proceeding with this working assumption for review. Do not describe these as confirmed user answers. There is no Seed Me contract for this run. The primary goal is to exercise Substrate end to end and write a retrospective using observed events.

Checkout: `/Users/jondev/dev/active/product/tink-arcade-invaders`; branch `feat/space-invaders`; observed base `773a2dcc1c3fb8c5f585854b5584c4cc03908cbc`. Intended PR base: `fix/arcade-check-evidence`; checker PR #6 is separate and no merge is implied. Recheck live state before delivery. AGENTS.md already contained the launcher's planning rules when this session began; it was not edited here. The coordinator reports the dashboard now points to this run; this planning session did not independently inspect the dashboard.

## Sources and decisions

This fresh planning session read AGENTS.md, installed `_system/SDLC.md`, stage-1 CONTEXT, run metadata/status, DESIGN.md, earlier brief/checklist/handoff examples, the existing Snake engine/UI/CLI/audio interface, native audio checks, test runners and PTY helpers. It inspected the current project verification policy and helper `--output` support. Existing game examples inform implementation patterns, not authority or this run's seed.

- Required `principle-build-the-lever` was read in full through `python3 _system/scripts/sdlc.py skills tink -- mount principle-build-the-lever --json --payload`. It led to planned repeatable full-suite/replay and real PTY helpers. No implementation helper was written before approval; realizing that skill's script artifact is build work, not a completed planning claim.
- Features and Futures and its SDLC integration guide were read from `/Users/jondev/.agents/skills/features-and-futures/`. It led to one complete small game, an engine-first playable slice, a pause to inspect real evidence, and no speculative shared game framework.
- The installed guidance still shows mount without `--json`; prior coordinator context supplied the correct shape, so no failed call was needed here. The compiled `.tink/.active/principle-build-the-lever/SKILL.md` pointer was absent; the wrapper successfully returned the approved library payload. No runtime/pointer repair was attempted.
- No stage-1 routed-skill receipt was present in this run. No extra router call or library approval was invented.
- Existing helper output support is already in the base. New PTY invocations explicitly select this run's transcript; review must choose another path. Preserve partial transcripts on failures and test the helper's behavior.
- Existing verification config only checks Breakout help. Preserve it; this run's executable checklist adds the full suite, legal replay, PTY, Invaders help and guarded native audio check. Do not confuse existing help coverage with game verification.

## Evidence limits and retrospective notes

No Invaders implementation, gameplay, replay, terminal capture or audio check has run. The proposed new scripts do not exist yet. Stage status parsing and structural lint are planning checks only. Human game feel remains unobserved until Jon plays; native metering cannot stand in for listening.

Record actual visual inspection, audio observations and human feedback separately. The observation-record item explicitly allows honest pending listening/play feedback; it does not award human acceptance. Do not carry the previous game's listening gate into this run by accident.

The coordinator specifically requested a repeated-Space regression check from earlier Pong work: input must not freeze the simulation. This session has not independently reproduced that historical defect, so it is a supplied regression concern, not a finding about the current checkout.

Continue this handoff with: outcome, evidence and limits, learning, concrete changeability problem if any, decision (proceed/consolidate/re-scope/stop and repair), and next work. Record where a fresh session needed chat context, manual command corrections, approval delays, repeated work or missing evidence. The retrospective should report process failures even if the game passes. Do not edit factory files or open a separate improvement task without user direction.

Planning checks: status parsed all six checklist definitions (four automatic, two attested) with stage 3 still pending. Structural walk passed all seven checks. Only brief, checklist and this handoff were written by this session.
