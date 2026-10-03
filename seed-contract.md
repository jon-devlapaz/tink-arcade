# Seed contract r1 — Play Tetris against Jev

## You are confirming

- **Goal:** take a real hunch through the existing tink-sdlc flow to a PR ready for your review.
- **Build:** live, side-by-side Tetris against Jev, first to 20 cleared lines, in the terminal game's own repository.
- **Exclude:** garbage attacks, online human multiplayer, a replacement learning app, leaderboards, automatic merge or deployment, and a new tink-substrate framework in this trial.
- **Choices:** 6 suggestions accepted unchanged; 5 choices supplied or selected by you. The play-quality assessment was first delegated, then accepted. This counts the direction, endpoint, feature, and gameplay decisions, not technical facts.
- **Unknown:** real Jev strength and latency, final layout and action strategy, API access, and GitHub destination. These must be resolved or plainly reported before the relevant delivery step. No earlier gameplay decision is reversed.

Originator: Jon. Revision: r1. Status: seed contract — confirmed for intake; not approved for implementation. Prepared from this Seed Me session; this is discovery input, not implementation approval.

## Problem and outcome

You want to play against Jev in the existing Socratink / Paper Tetris terminal game. The matching app lives at `/Users/jondev/dev/active/product/neon-tetris`, separate from the Socratink learning app. It currently has one game board and no Git repository. The existing suite passes, but there is no multiplayer or live-opponent proof.

The result is a playable race and a review-ready PR with changes, verification evidence, and remaining uncertainty explained. The trial should also show whether another agent can continue from the seed, run artifacts, and working files without the user reconstructing context.

## Accepted decisions and authority

All are user choices in this conversation:

- Start with tink-sdlc's existing flow; simplify only where the trial supplies evidence.
- Deliver a PR ready for review. Merge and deployment remain separate decisions.
- Implement the user's hunch: play the terminal Tetris game against Jev.
- Show both boards live, side by side.
- Race to 20 cleared lines. Reaching or exceeding the target wins; filling the board loses. No garbage attacks.
- Give the game its own repository. No repository name, hosting account, or visibility has been selected.
- On a failed or timed-out Jev request, pause both boards, show the problem, and offer retry or quit.
- Show cost in the game; no spending cap. Live calls stay relevant to this work; this is not a request for indefinite background testing.
- Assess responsive controls, readable boards, and an engaging opponent making real Jev decisions. This assessment began as an assistant hypothesis, was delegated by the user, and was then accepted with “agreed.” Balance remains untested.

## Proposed defaults — not individually confirmed

- Same piece sequence and existing gravity/scoring rules for both players. Ordinary Jev thinking time does not pause the human's board. No artificial speed handicap is assumed.
- Manual pause and restart affect the whole match; solo play remains available.
- Display estimated USD spend for the app session, including rematches. Derive it from reported usage and the actual model's known price. Missing usage and uncertain charges must be marked incomplete, never silently counted as zero.
- Network work must not block human controls or drawing. Stop issuing calls when paused or finished; handle any already-running request explicitly. Responses from an old match cannot change a restarted match. If both finish in the same game update, report a draw rather than letting board update order choose a winner.
- Keep the existing paper/ink presentation and sound behavior. Pause safely when the terminal is too small for two readable boards; choose and document that size during design.

## Acceptance checks

These checks are proposals until adopted by downstream planning. Only the first command has run today.

### Existing solo behavior

Run the existing game suite from the game checkout.

cmd: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`
expect: exit 0 with no failures. Current baseline: 78 tests, 2 skipped. Record and explain skips; don't present skipped native-audio checks as proof.

### Race and failure behavior

Use deterministic provider fixtures to exercise two games, the target crossing, top-out, simultaneous finish, pause, restart, error, timeout, and late replies.

provisional: the new race tests must be implemented first.
cmd: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_race*.py'`
expect: nonzero tests discovered, all pass; neither game advances during a failure pause; a late reply cannot move a new match; winner is not determined by render/update ordering.

### Visible and honest cost

Verify session totals across retries and rematches, tiny fractional charges, missing usage, and unknown model pricing.

provisional: new cost-accounting tests must be implemented first.
cmd: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_jev_cost*.py'`
expect: nonzero tests discovered, all pass; valid usage is counted once and unknown cost is visibly incomplete. No cap ends the match.

### Real terminal match

Exercise the running game using the actual service, with an API key supplied outside source control.

provisional: `--versus-jev` is a suggested launch flag, not an existing interface; replace with the real command once implemented.
cmd: `python3 -m neon_tetris --versus-jev --seed 1`
expect: readable side-by-side boards; responsive controls while requests run; progress toward 20; visible estimated cost; working pause, restart, resize recovery, and clean exit. Capture the resolved model, commands, observations, and sanitized failure evidence. No actual match has run yet. User playtesting determines whether the opponent is enjoyable; no numeric fun score is invented.

### Factory verification and second-agent continuation

provisional: install the existing factory in the authorized game checkout, select its profile through its normal workflow, configure the actual checks, and create the named run before this command exists.
cmd: `python3 _system/scripts/sdlc.py verify play-against-jev`
expect: current verification for the exact reviewed candidate, with meaningful configured checks; a fresh agent can identify purpose, chosen rules, evidence limits, and next action from the run and linked files. Record whether the user had to repeat context. Agent assignment is a downstream workflow decision, not a fabricated result.

All provisional commands are proposed acceptance intentions, not settled interfaces or proof. The implementation plan replaces them with actual commands and expected results. Definition changes follow tink-sdlc's existing approval rules.

## Risks and knowledge map

**Known with proof:** `DESIGN.md:1,53-82,185-203` identifies the game, single-board layout, launch and test commands; `neon_tetris/engine.py:97-122,229-248` owns restart, gravity, line clearing and top-out; `neon_tetris/ui.py:230-259` owns the nonblocking input/render loop. Current Git inspection found no repository. The baseline command above passed. Recheck source and baseline before build or if files change.

Official API evidence: <https://docs.typesafe.ai/sdk/python/api/types/responses.md> documents nullable input/output token usage; <https://docs.typesafe.ai/models.md> lists Jev 1.13.0 at $0.042 per million input tokens, output free, when inspected. Recheck model and price before implementation and display a price basis; this is not an invoice guarantee.

**Known unknowns:** the implementation agent must investigate legal-action representation, response pacing, timeout duration, credential availability, actual cost accounting, and playable terminal geometry. Do not hide a scripted opponent behind the Jev label. The user decides any consequential compromise to the selected game rules. The user also confirms the GitHub destination and visibility before publication; own-repository preference is not public-release permission.

**What we have not read:** the full test implementations and all audio internals were not reviewed during this interview. The build agent reads relevant tests and owning modules before edits. No need to rewrite audio merely to add an opponent.

**Probes:**

- Pre-mortem — why might a correctly implemented race disappoint? Answer: poor pacing or strength, stalled controls, repeated pauses, or unreadable boards. Assistant hypothesis under delegation, then accepted by the user. Changed: real gameplay and legibility are part of the evidence, not inferred from unit tests.
- Counter-example — when must normal autonomous match progress stop? A failed request, manual pause, completed match, or undersized terminal. Existing solo behavior and the user's pause decision supply the basis. Changed: explicitly exercise pause/restart/stale-response behavior.
- Outside view — what would an experienced integration reviewer ask? Whether a result belongs to the current board state and whether unavailable usage looks like zero cost. Assistant inference from the asynchronous API boundary and nullable usage, not independent external review. Changed: include late-response and incomplete-accounting cases.
- Recoverability — no deletion or relocation is selected. Preserve the source folder and existing launcher; inspect backups and repository setup before any later proposed move.

**Where we did not look:** no live Jev gameplay, no alternate terminal/platform testing, no current account/billing access, and no actual two-agent continuation.

## Suggested first slice and handoff

Proposed first command, from the existing game directory: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`. Re-establish the baseline in the isolated build checkout before adding two-board orchestration and a fake provider. Keep the scope one complete human-versus-Jev race, then connect and test the real service. Reuse the existing tink-sdlc flow; this seed does not preselect a profile or approve a stage.

The confirmed file is intended for `/Users/jondev/dev/active/product/neon-tetris/seed-contract.md` (currently absent), then for the game's own repository. The ledger is interview history, not an extra required runtime input. Preserve solo play, source provenance, licenses, and meaningful tests. The separate Socratink learning app and tink-substrate implementation are outside this game PR.

Intake acceptance: Jon said “begin” after the displayed r1 and next-step summary. This is contextual acceptance, not a verbatim revision-label response; no teach-back was supplied. Next owner: the SDLC planning agent prepares the build brief for review. After confirmation, the selected SDLC workflow owns planning, repository setup, implementation, checks, and PR creation under its actual authority. Resolve the hosting destination before external publication. Stop at a review-ready PR; do not infer merge or deployment authority.
