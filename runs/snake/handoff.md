# Snake planning handoff

## State

Stage 1 planning is complete as a proposal. `brief.md` and `checklist.json` define the light-profile stage-3 review. No approval, code change, run creation, commit, or stage advancement was performed by this planning session. Seed confirmation remains intake authority only.

This fresh planning session read AGENTS.md, the installed SDLC guide, stage-1 CONTEXT, run metadata and confirmed seed contract from files. It inspected Tetris's design, renderer, input loop, CLI, audio interface, native backend and sample credits; native audio/UI tests; Breakout's engine, renderer, test runner and real PTY harness; and installed verification configuration. It did not rely on previous game implementation chat. A fresh build session should read those same run artifacts and its build-stage instructions after the coordinator records actual approval and opens the stage.

## Decisions and tools

- Tetris, rather than Breakout, supplies the paper palette and layout style. Reuse `KeyboardAudio` directly and preserve all sample files/credits.
- The required `principle-build-the-lever` skill was read in full through the installed serialized wrapper. It led to executable checklist checks and narrowly adapting the existing test/PTY runners during build. Planning writes only these three approved artifact files; no test script was created early.
- Optional stage-open pick `ai-native-sdlc` (confidence .51) was attempted through the wrapper. The documented mount shape lacked the installed CLI's required `--json`; the corrected call returned `unapproved`. No library approval was invented. Its payload was unavailable and was not relied on; installed `_system/SDLC.md` and stage CONTEXT govern instead.
- The compiled `.tink/.active/principle-build-the-lever/SKILL.md` pointer was absent; the wrapper delivered the approved library payload. Record this as a tooling gap for the coordinator, not a reason to change factory files during Snake.

## Next and limits

Present the brief for Jon's actual stage-3 definition decision. Board size, speed, scoring, queue, layout and cue choices are proposed together and may be amended before approval. No separate consequential choice remains unresolved in planning.

No Snake tests, terminal harness, implementation, visual capture, native playback or listening were run in this stage. The proposed Snake scripts do not exist yet. Existing native tests meter real rendered output; they cannot establish subjective sound quality. The visual/listening checklist item must stay pending until actual observations exist. Do not infer that Jon has seen or heard the result. The build must report a missing listening observer honestly.

Current project verification only checks Breakout help. The proposed checked items carry full-suite, Snake PTY, CLI and guarded macOS native tests. Their exact commands and timeouts are in checklist.json. Passing automatic checks does not replace the visual/listening item, independent release review, or Jon's merge decision.

Avoidable stops found so far: mount syntax drift; an unapproved optional routed skill; a missing compiled skill pointer. Installed runtime guidance and the approved required-skill payload allowed planning to continue. Keep later evidence and delivery observations with this run; do not mark delivery complete from this plan.

Planning checks: `sdlc.py walk --json` passed all seven structural checks; status parsed the checklist with the definition gate still pending. After coordinator review, removed the redundant Breakout PTY command because it writes to the previous run's transcript. Existing regression unit tests remain in the full suite. Final checklist: six items, four automatic checks and two attestations. AGENTS.md already contained the launcher's planning-skillset change when this session began; it was not edited here.
