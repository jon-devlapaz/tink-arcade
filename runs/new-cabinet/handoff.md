# Last Time handoff

Draft PR: https://github.com/jon-devlapaz/tink-arcade/pull/25

## Identity and authority
Run `new-cabinet`, ID `8de09fe4-9393-4810-aada-3f15a2743a25`, branch `claude/new-cabinet`, checkout `/Users/jondev/dev/worktrees/tink-arcade/claude-new-cabinet`.

Seed source `/Users/jondev/.local/share/tinkery/sessions/session-dI1YYi/seed-contract.md`, local snapshot `seed-contract.md`, SHA-256 `e73da9d6dbe46ed6b1179e6443293d2607b72f5aa232cf64d1051ad93693c611`. Revision r1 confirmed at `2026-10-21T04:44:57.918165+00:00`. Intake used the displayed installed Tinkery executable and retained the records and v2 binding. Original external session files were never edited by hand.

Claude operated Tinkery and approved the definition and activation gates as `Claude standing in for jondev`, explicitly authorized by `/Users/jondev/scratch/arcade-run/task.md`. This is proxy operation, not jondev personally playing or approving release. Tinkery's generated confirmation field says `operator: human`; it is a workflow label, not verified identity. Confirmation words explicitly disclaim the unasked expert probe's operator attribution and invalid evidence citations.

Verified code candidate `9bce1888342be020f977ef1327501bfaaedd90b9`, content fingerprint `c76727708578f14adbedfef9dfa4332f6dfd496a544200be9c2ca3b8f48314f2`. PR initially opened on evidence-only revision `d8c35b2b69386fbfadd6789e1a5bd95afa3065ad`. This handoff adds only run evidence. Query `python3 _system/scripts/sdlc.py status new-cabinet --json` for current freshness and the forge for the exact current PR head. No deployment or merge revision exists.

## Play
`python3 -B -m tink_last_time`, or cabinet 14 in `./play`, at least 80 x 30. Arrows set automatic cardinal motion. P pauses, R restarts, M mutes, Q/Ctrl-C exits. Optional `--seed 7 --no-color --no-sound`.

Collect sparks for one point each. Every 15 simulation seconds all completed paths loop in sync as ghosts; contact or edge swaps end the single life. Walls stop movement. The player keeps the endpoint at boundaries unless a restarting ghost overlaps it, then shifts to the nearest free cell with preferred clearance. The next recording starts at that actual cell. A fully occupied arena ends normally rather than crashing. This transition rule is visible and still needs jondev's play judgment.

## Evidence, kept separate
- Automated rules and UI evidence: 18 focused tests, no skips, under `tests/test_last_time_engine.py` and `tests/test_last_time_ui.py`. Seed activations bind specific assertions for movement/collection, 15-second timing, exact replay, all-ghost collisions, stacking, arrows/one life, score and registry.
- Legal-input replay: `scripts/replay_last_time.py` reaches round five with four ghosts and 82 sparks in 600 ticks. A separate run with no steering after its first arrow loses at round two, tick 14. No state/time injection or invulnerability.
- Actual terminal evidence: `04-test/output/terminal-transcript.txt`. Real arrow keys, actual 15-second boundary and replay death, all-clock pause and resize freeze, prior-pause preservation, restart, monochrome/color, no-sound, Q/SIGINT, terminal-mode restoration and process-group cleanup. Trace output observes state only.
- Menu integration: `scripts/check_arcade.py` launched all offline cabinets, including Last Time, muted, quit and returned to the menu. Existing numbers are preserved. Stacker's old exact-whole-list assertion was changed to its original 13-entry prefix, not removed.
- Negative controls: nine disposable-copy mutations fail by assertion for timer, replay, collisions, stacking, score, arrow mapping, registry, dark field and boundary safety; every restoration and final suite rerun passes.
- Repository suite: 572 tests pass, five existing opt-in native-audio skips. `python3 -B scripts/check_all.py` also passes actual menu launches. Python compilation and source whitespace checks pass. Captured terminal whitespace and locked seed bytes are preserved. `04-test/output/check-all.log` intentionally retains the initial Stacker-list failure; the later dry run and final verify log demonstrate its resolution.
- Proxy observations: eight distinct seed-expectation receipts in `marks/` cite the actual corresponding outputs. These attest mechanical observations, not fun, taste or listening. No fabricated human or independent reviewer.
- Final SDLC verification: `04-test/output/verification.json` and `test-log.md`. Current after committing evidence. 21/21 entries passed, comprising 13 automated checks and eight proxy attestations. No pending proposals remain. Both definition receipts and all marks are retained.
- Watch checked in Tinkery after PR creation. Correct original goal; `verified`, stage 3 approved, 21/21 passed, `0 attestations owed · 0 may need recheck`. This is not a Taste verdict.

## Remaining review and findings
Independent code-owner review, forge requirements and jondev's typed `merge` remain required. No separate review session or independent technical review is claimed. This stays a draft, not ready or merged. There is no `.github/workflows` directory here and the PR's initial check rollup was empty; local green checks do not establish remote CI.

Owed to jondev: play feel, fun, calm-to-tense pacing, fairness and transition-rule judgment, live visual comparison and sound listening. Native playback tests were not opted into. Release and usefulness acceptance remain his.

The branch includes the earlier scaffold 1.35.0 upgrade needed for --tinkery intake. Changed contracts make older approvals stale. Watch also cannot read twelve legacy runs without canonical UUIDv4 IDs; no migration or reapproval was attempted. Stacker is waiting on a decision, separate from this verified run.

Operator records remain at `/Users/jondev/scratch/arcade-run/`: five Tinkery model calls, two corrections against the baseline of ten, full corrections/findings and the Watch screen. Key frictions were an invented probe attribution, invalid line citations, the viewport expanding during confirmation and requiring another read-to-end, manual intake copying and old-run schema noise.

## Skills that changed decisions
`principle-build-the-lever` led to rerunnable legal-input, PTY and mutation scripts instead of manual-only claims. `principle-foundational-thinking` led to integer tick indices and immutable position histories for exact replay. `principle-prove-it-works` required actual menu/curses execution and negative controls, beyond compilation. `unslop` kept operator prose direct. The optional architect skill was unapproved and was not bypassed. Light-profile design is in the combined brief.
