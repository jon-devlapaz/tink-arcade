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
