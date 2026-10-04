# Breakout handoff

## Start here

Work in `/Users/jondev/dev/active/product/tink-arcade-breakout`. Read [AGENTS.md](../../AGENTS.md), [run metadata](run.json), [the run-bound seed](seed-contract.md), [brief](brief.md), and [checklist](checklist.json). The repository-root seed describes Jev/Tetris and is unrelated. The seed copy selected by `run.json` controls this run.

Get live status from this checkout:

```sh
python3 _system/scripts/sdlc.py status breakout --json
```

That command reports workflow gates and evidence from current files; it does not grant permission. This handoff's dated observations are historical evidence only. [SDLC rules](../../_system/SDLC.md) explain receipts, stale approvals, verification, and stage launch. Read the relevant [build-stage contract](../../stages/03-build/CONTEXT.md) when the launcher opens that stage; it has not been evaluated by this planning agent.

## Scope and next action

Add solo terminal Breakout: paddle, bricks, score, three lives and three handcrafted layouts, advancing only on full clear. No multiplayer, paid model calls, power-ups, new substrate workflow, or changes to the other game PRs. Delivery ends at a reviewable PR, with merge separate. Jon prioritizes reliability, earned progression and interesting boards.

The brief proposes the exact layouts, 10 points per brick, ASCII/curses interface, explicit Space-to-launch after a life or board change, fixed board geometry and speed, and reusable verification scripts. These details await the light run's single definition approval at stage 3. Seed confirmation is intake authority only. A launcher must record an actual human decision accepting the brief and checklist, then open the next stage. Never infer approval from this note or fabricate a receipt.

After the real gate: inspect current code and Git state, implement the proposed package and checks, configure the project verification command, record the attested checklist evidence, commit code, and run SDLC verification. Follow the stage-5 review procedure before presenting delivery as review ready. Human play quality remains unverified until Jon plays; a pending feedback record must say so in the PR.

## Dated planning evidence — 2026-10-04

- `git rev-parse HEAD` returned `c83dd829aa47c1b4e8baf2f3833327e6cfd77e7a`; branch was `feat/breakout`. Worktree inventory identified this as an isolated checkout of `https://github.com/jon-devlapaz/tink-arcade.git`. No remote fetch was run, so upstream freshness and the future PR base remain to be checked. Other worktrees were inventoried but not opened or modified.
- `run.json` selected profile `light`, kind `feature`, and the Breakout seed copy. Its seed digest was also present in the stage-1 skill-pick receipt. The saved seed says Jon confirmed revision 2; this agent has no independent human decision receipt.
- Before planning, brief/checklist were empty templates. After writing them, `status breakout --json` recognized four valid checklist items (two automated, two attested), reported stage 3 pending, no decisions, no verification receipt, and blocked verification. `_system/verification.json` had `require_tink: false` with an empty checks list. This is an expected unfinished configuration, not passing test evidence.
- `python3 _system/scripts/sdlc.py walk --json` exited 0: seven passes, zero warnings/failures. This proves saved links and stage structure were legible; it does not prove game correctness or continuation quality.
- Inspected the existing `DESIGN.md`, Tetris entry point and UI/test entry names to choose a separate package and compatible terminal conventions. Did not read the full engine or run the existing game suite. The planned Breakout module, tests and PTY scripts do not exist yet. No gameplay verification occurred.
- Wrote `brief.md`, `checklist.json`, and this handoff. No game code, approvals, marks, commits, run creation, or factory updates were performed. Tink mounts also created `.tink/.gitignore` and ignored local skill payloads; preserve that generated ignore file with the scaffold as appropriate.

## Saved-file continuation findings

This planner began with the saved checkout and run files, not discovery-session history. The run seed was sufficient to identify the game, priorities, exclusions, three-board progression, and PR endpoint. No user clarification was needed for planning. The following gaps were preserved rather than silently filled:

1. **Two seed files:** the root seed is an older Jev/Tetris contract. `run.json` resolved the ambiguity. Future agents should follow that pointer, not choose by filename alone.
2. **Required skill payload missing:** `AGENTS.md` linked to `.tink/.active/principle-build-the-lever/SKILL.md`, but it did not exist initially. Loaded it with `python3 _system/scripts/sdlc.py skills tink -- mount principle-build-the-lever`, then read it fully. The same wrapper mounted the selected `control-cli` skill. Both mounts succeeded. The launcher warning that `--payload` might need `--json` was supplied with the task; it was not reproduced here. Plain mount returned a path, whose `SKILL.md` was then read.
3. **Incomplete verification configuration:** no project check was configured. The brief specifies an entry-point command plus substantive checklist checks for the builder to create. No claim of test readiness follows from planning.
4. **Design choices still proposed:** lives/reset rules were seed defaults, not separate confirmed user choices. Package split, board patterns, scoring, controls, launch waits, geometry and silent gameplay were planning proposals. Numeric physics tuning, actual upstream base, platform coverage and Jon's play feedback remain unresolved or untested.
5. **Experiment limit:** this was a fresh planning read of saved files, but no handoff existed when it began. It is not yet evidence that a fresh builder can start with this handoff and finish without confusion. That later agent must record what it misunderstood, repeated, or needed from Jon, including actual friction switching between Seed Me and substrate. Do not manufacture a successful continuation result.

## Skills that affected this plan

- `principle-build-the-lever`: chose a reusable test runner and terminal harness as implementation deliverables, with executable checklist commands. The planning task remained three review documents; the launcher explicitly declined a separate plan-validation script because existing status/walk already check the structure. No lever implementation is claimed at this stage.
- `control-cli`: selected a real PTY check with observed-state waits, a retained transcript, bounded deadlines, resize/pause checks and cleanup. No checked-in terminal harness exists in this checkout. The seed's Galaga harness reference is older inspection evidence, not a file inspected or a test rerun here; a builder may inspect it before deciding whether reuse is worthwhile.

## Continuing the experiment

The fresh builder should add a dated entry here after reading the saved files: state scope, actual live permission, evidence limits and next action; list any missing information or unnecessary rereading. Link concrete test/verification and review outputs as they are produced, and retain the live status command above. Do not replace current status with a durable sentence claiming the run is approved or verified. Do not add a new process to substrate for this trial.

## Dated build continuation — 2026-10-04

A fresh build agent began with this handoff, followed its saved links, and inspected
`AGENTS.md`, both stage 3 and stage 4 contracts, the selected seed, brief,
checklist, live structured status, and the actual decision receipt. The receipt
[3-1791143101704704000-de21f1236ee044f29744f892fedda722](decisions/3-1791143101704704000-de21f1236ee044f29744f892fedda722.json)
records Jon's acceptance of the reviewed brief and checklist. Live status reported
stage 3 approved. The permitted work was implementation, verification, and PR
preparation in this isolated checkout. The parent handles stage launch, independent
review, and PR creation. No merge is authorized by local verification.

### What was built and checked

- Added the separate [Breakout package](../../tink_breakout/engine.py), approved
  layouts, curses controls, documentation, and [CI checks](../../.github/workflows/breakout.yml).
  Tetris source and tests are unchanged. The live remote main remained `c83dd82`
  when checked with `git ls-remote origin refs/heads/main`. Other worktrees were
  inventoried but not changed.
- The [complete test runner](../../scripts/check_breakout_tests.py) passed 93 tests,
  with two existing opt-in native-audio tests skipped. Breakout has nine engine,
  two layout, and four UI test methods. The tests cover each brick face, tied
  contacts, corners, fast crossings, repeated scoring, paddle edges, lives,
  earned transitions, win/loss, restart, control variants, timing and clipping.
- [Legal replay](../../tests/test_breakout_layouts.py) uses seed 20261004, only
  paddle moves bounded to two cells per command, launches, and 1/120-second
  simulation steps. It never deletes bricks or changes a flying ball. It clears
  Gate at step index 16548, Chevron at 19078, and Islands at 31474. Final score is
  760 with three lives. A second run gives identical results. The limit is
  180,000 steps. This demonstrates clearability, not human difficulty.
- The [real terminal check](../../scripts/check_breakout_terminal.py) passed with
  80x30, 100x35, and 40x12 windows. It compares actual game snapshots during pause,
  undersizing, resize while paused, and the first recovery frame. It also checks
  input, launch, restart, quit, SIGINT, restored persistent terminal modes, and
  process cleanup. Its optional trace only observes the live game loop.
  See the [terminal transcript](04-test/output/terminal-transcript.txt).
- The configured verification command checks the actual module's help output.
  The approved checklist commands run the full suite and PTY check. Final SDLC
  results belong in the generated [test log](04-test/output/test-log.md) and
  [verification receipt](04-test/output/verification.json). Refresh live status
  before relying on these files. The structural walk passed all seven checks.

### Missing evidence and next work

Jon has not played this implementation or supplied game-feel feedback. Difficulty,
fairness, and layout interest remain unverified. The play-feedback checklist item
records that pending state as expressly allowed by its approved definition; it is
not human acceptance. Native audio was not played, Windows is unsupported, and
Linux/hosted CI has not been run by this build agent. The next step after current
verification is independent stage-5 review in the parent's selected review checkout.

### What the continuation taught us

1. The handoff supplied enough context to build without asking Jon to repeat
   decisions. Its root-seed warning prevented mixing this run with Jev/Tetris.
   The dated statement that approval was pending was superseded by the linked
   decision and current status, without editing the old observation.
2. The fresh agent still had to reread the brief, checklist, stage contracts, and
   receipt to establish scope and authority. That was necessary checking, not
   repeated discovery. The existing engine and terminal code needed inspection;
   the handoff explicitly said that inspection was incomplete.
3. Required `unslop` and the routed `ai-native-sdlc` payload were initially absent
   from `.tink/.active`; the serialized mount command supplied them. The routed
   skill names older `status.sh`/`verify.sh` entry points. The installed guide and
   active contracts resolve that mismatch to `python3 _system/scripts/sdlc.py`.
   No factory file was changed to hide the discrepancy.
4. The PTY driver initially checked state before all screen bytes were drained,
   causing a false screen-readiness failure. Its failure cleanup then hung while
   the terminal stayed open. Bounded cleanup now closes descriptors before
   waiting, and text checks wait for actual output. macOS also sets transient
   `PENDIN` on restore, so only that input-retype flag is excluded from mode
   comparison. Persistent flags, speeds, and control characters are all checked.
   Ctrl-C coverage sends its actual SIGINT signal because this PTY deliberately
   has no controlling session, allowing post-exit mode inspection on macOS.
5. No shared Seed Me view or new workflow was built. This trial demonstrates one
   successful saved-file build continuation. It does not establish broader
   usability or measure Jon's friction switching between applications.

Skills that changed the work: `ai-native-sdlc` kept evidence tied to the installed
runtime; `principle-build-the-lever` led to committed, rerunnable suite and terminal
checks; `control-cli` led to observed-state waits, transcript retention and cleanup;
`principle-prove-it-works` required the actual curses process and physics snapshots;
`unslop` kept docs and this handoff direct. No additional agents were dispatched.

### Final build observation — 2026-10-04

`python3 _system/scripts/sdlc.py verify breakout` passed on code commit `69b81dc`.
A subsequent structured status read reported `verification_status: current`,
`verification.passed: true`, four passed checklist items, and no errors. The
attested items predate a one-line transcript-ending cleanup and therefore show
`needs_recheck: true`; that change does not affect pending human feedback or the
recorded fresh continuation. Those statements were reviewed and remain accurate.
The output-only evidence commit that follows does not change the game candidate.


### Delivery observation — 2026-10-04

Parent opened PR 3: https://github.com/jon-devlapaz/tink-arcade/pull/3.
Independent review of c778a75 found no actionable Important defects; see
[review findings](05-deploy/output/REVIEW-findings.md). The reviewer reran the
93-test suite and PTY harness and cleared every board through the real input
controller at both 30 and 60 FPS. Two existing native-audio tests skipped.

GitHub checks on c778a75 passed on macOS and Ubuntu. This is dated evidence;
consult PR 3 for checks on the latest delivered revision. Evidence-only changes
below do not alter reviewed game code. Jon owns the next decision: play the game
and review the PR. No merge approval is recorded. Human game feel remains pending.
