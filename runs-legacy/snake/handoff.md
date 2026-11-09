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

## Fresh build continuation, 2026-10-04

A new build session read the root instructions, installed SDLC guide, stages 03/04,
run metadata, confirmed seed, approved brief/checklist and this handoff from files.
It verified the recorded stage-3 approval before implementation. The launcher had
already opened the stage in this isolated Snake checkout. The proposal wording
above describes historical planning, not the current gate.

Implemented `tink_snake` with deterministic rules, two-turn input queue, seeded
food, timing, paper renderer, CLI and direct `KeyboardAudio` reuse. Existing game
source, sample recordings, credits, factory files and Breakout evidence remain
unchanged. Added Snake tests, PTY script, README/design notes, CI and the local
`.pi/skills/verify-snake` recipe. No PR, release approval or merge was performed.

Skills read through the serialized installed wrapper:

- `principle-build-the-lever` led to the repeatable test and real terminal scripts.
- `principle-prove-it-works` required a live PTY run and actual native playback checks.
- `unslop` guided the README and continuation text.
- The stage-open `create-verification-skill` pick was available. It led to the small
  local verification recipe and three feature pages, with actual doctor/drive/cleanup
  execution. No library approval was created or inferred.

Evidence so far:

- Full suite passes 112 tests. It explicitly skips the two opt-in native tests.
- Separate guarded macOS native suite passes both tests without skips. It plays and
  meters real samples across spaced repeats and mute/resume; it does not prove anyone
  heard them or liked their sound.
- Real Snake PTY passes arrows, WASD, queued turns, pause/timer freeze, initial and
  mid-game undersize, recovery while paused/playing, restart, mute, wall collision,
  Q and SIGINT. Original terminal modes restore; child process groups are gone.
  SIGINT simulates Ctrl-C's signal. Transcript is in `04-test/output/`.
- CLI help passes without a terminal; unit tests check the terminal-required error.
- Structural walk passes all seven checks.
- Coordinator viewed all 24 Tetris/Snake comparison frames. Actual ANSI PTY output
  was reconstructed with pyte in HTML. See `04-test/output/visual/observations.md`
  for concrete findings and rendering limits. Captures disabled sound.

Remaining gate: `visual-listening` is pending because no actual listening observer
or output-device observation exists. Do not mark it passed from native metering,
mock calls or visual captures. The coordinator has requested listening evidence.
After actual observations, mark that item honestly and rerun installed SDLC verify.
Independent review and Jon's merge decision remain separate.

Avoidable stops: no new skill approval or mount problem occurred in build. The
native Terminal UI was unavailable to the coordinator, so the saved comparison
explicitly records its ANSI reconstruction method. No factory change was needed.

Final build result: candidate committed as `b804f58`. The installed SDLC verify
command ran all configured checks, the full suite, Snake PTY, CLI help and guarded
native playback successfully, then exited 1 with `Checklist incomplete:
visual-listening`. This is the expected honest result until actual listening is
recorded. `docs-continuation` is attested with its evidence receipt. The generated
verification record and log retain the attempt; do not report overall verification
as passed. Commit-only changes to run evidence do not change application contents.

## Human playtest acceptance — 2026-10-04

After receiving the playable command and the request for listening feedback, Jon
reported “it works. call this done.” The coordinator treats this as acceptance of
the delivered playtest and an instruction to finish, rather than requesting more
audio details. Output device and individual sound-event observations were not
supplied; they remain unknown. This does not claim a detailed listening protocol
was performed. Together with saved visual inspection and real native playback
checks, this resolves the human observation at Jon's direction. Independent
review and PR delivery remain; no merge is authorized by this note.

## Delivery review — 2026-10-04

Independent review at ccf52bd found no Important defects or PR-readiness blockers.
The reviewer independently reran the full suite, native playback and real terminal
checks without overwriting prior evidence. See 05-deploy/output/REVIEW-findings.md.
PR 4: https://github.com/jon-devlapaz/tink-arcade/pull/4. GitHub macOS/Ubuntu checks
passed on that reviewed revision; the final evidence-only commit needs its own CI.
Jon accepted the playtest. Merge remains a separate decision.
