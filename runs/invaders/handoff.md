# Invaders run handoff

## Delivery update

Independent review at eaaab79 found no actionable defects; see
`05-deploy/output/REVIEW-findings.md` and its separate logs. All twelve reported
CI jobs passed on that head (push and PR jobs across Linux/macOS).
[PR 7](https://github.com/jon-devlapaz/tink-arcade/pull/7) delivers this run against
`fix/arcade-check-evidence`. The retrospective is `retro.md`. Human play/listening
and merge remain pending. Build/planning reports below preserve their original
observations; their future review/CI instructions are now historical.

## Build state and authority

Fresh build session began on 2026-10-04 in the existing isolated checkout
`/Users/jondev/dev/active/product/tink-arcade-invaders`, branch
`feat/space-invaders`. The current stage-3 receipt records Jon's actual "agreed"
after reviewing this run's brief/checklist. Live status reported approved before
implementation. The planning text below is historical and its pending-approval
statement no longer describes current authority. No definition or numeric rule
was changed in the approved brief/checklist.

Implementation and required local verification are complete. Candidate `cf629a1`
is committed; both attested marks are recorded. The actual SDLC verification
passed, and live status reports current evidence with all six checklist items
passed. See the final result below. The coordinator owns the next fresh stage-5
review session and PR against `fix/arcade-check-evidence`, observed at `773a2dc`.
Checker PR #6 remains separate. The builder will not open a PR, push, merge or
launch stage 5. Human merge authority remains separate.

## Implemented scope

- `tink_invaders/engine.py` owns the three approved formations, shared lives,
  timers, seeded attacks, whole-path collisions and life-before-progression rule.
- `ui.py` owns the fixed paper canvas, input batches, freeze/recovery behavior,
  audio cues and optional read-only state/screen observation. `__main__.py` owns
  CLI options and useful nonterminal errors. KeyboardAudio is reused unchanged.
- `scripts/replay_invaders.py` retains a deterministic legal-input controller.
  Seed 7 wins in 1,528 steps out of a 36,000-step limit, score 340, three lives.
  It never assigns game state, disables attacks or jumps waves.
- `check_invaders_tests.py` refuses absent/skipped/failed required groups and
  replay. `check_invaders_terminal.py` uses the actual curses process and requires
  an explicit output. `capture_invaders.py` reaches win and loss using legal keys.
  README and DESIGN document constants, use, captures and limits. The new CI job
  runs software/PTY checks on Linux and macOS; remote results remain unobserved.
- Other games, their tests, sound files/credits, other run evidence, factory
  runtime, verification policy and shared templates were preserved. AGENTS.md's
  generated rules came from the launcher's stage open, not a builder edit.

## Actual evidence and limits

Latest full-suite development run passed 153 tests in 26.903 seconds with two
explicit opt-in native audio skips. The guarded native suite then ran separately
on macOS and passed both repeated-sample/mute-resume metering tests without skips.
Final SDLC verification must repeat those required checks after the candidate is
committed; development results do not substitute for its receipt.

`04-test/output/terminal-fixed.txt` records a passing actual PTY run after the
resume-input repair. It checks actual movement, shot creation/motion, repeated
Space with clocks/marching still advancing, pause, restart, mute/unmute, color and
monochrome, 80x30/100x35, 40x12 freeze, recovery while playing/already paused,
initial undersizing, Q and SIGINT, restored persistent modes and no child group.
SIGINT stands in for Ctrl-C because the slave has no controlling owner. The
transient macOS PENDIN bit is excluded from terminal mode comparisons. All physics
fields, including cooldowns and partial-step time, are compared during freezes.

Four `04-test/output/captures/current-*` directories contain actual curses cell
arrays, raw ANSI, transcripts and HTML sheets. Each shows ready/play/pause/win/loss
at 80x30 or 100x35 in color or monochrome. Captures came from the real CLI loop;
win used the legal controller and loss steered into normal enemy shots. The
coordinator actually viewed all twenty frames through browser screenshots. It
reported readable labels/controls, unclipped borders, appropriate margins,
paper/carbon/jade styling and distinguishable ship/enemy marks in monochrome.
Win shows 340 points and wave three; loss shows zero lives. No visual blocker was
reported. Its screenshots are retained in `04-test/output/visual-review/`.

These are HTML reconstructions of actual curses screen cells, not native Terminal
pixel captures. Font metrics and customized palettes are not captured. Playing
frames were recorded before visible projectiles, so their appearance is covered
by renderer tests and actual PTY shot observations, not a claimed visual finding.
The builder did not independently view the browser screenshots; visual attestation
uses the coordinator's actual observations. Jon's play feedback and actual human
listening remain pending. Metered signal does not establish perceived sound
quality, and automated wins do not establish fair or enjoyable difficulty.

## Failures, corrections and workflow observations

1. The optional stage-3 pick named `ai-native-sdlc`, but the serialized mount
   refused it as unapproved. No payload was delivered or read; no approval,
   upgrade or library repair was attempted. Installed local contracts governed.
2. Stage-4 CONTEXT suggests a new stage launch, while installed SDLC.md says
   verification belongs inside the stage-3 session. The coordinator had already
   resolved that conflict in favor of same-session verification. No stage-4
   launcher was invoked. This was supplied context a fresh builder needed.
3. Initial actual PTY checks passed, then the first capture run timed out on
   resume. Flushing input on every paused frame could discard a fresh resume key.
   The fix flushes only transitions/recovery. A regression test checks this
   decision, and complete actual captures plus PTY passed afterward. Failed
   capture output remains in `captures/80x30-mono`; `80x30-mono-fixed` records the
   successful first repair run. The `current-*` captures use the final game code.
4. Inspection identified the need to sweep both enemy and shot motion during a
   march/descent step. The collision implementation and boundary tests now cover
   that path. The legal replay still produces the same complete win.
5. The coordinator saw dark horizontal gaps in the first color HTML sheets.
   They came from the contact sheet's background between text rows. The helper
   now gives color sheets a paper background; HTML was regenerated from unchanged
   actual cells. This was a capture-display correction, not a game rendering fix.
6. Native system Python lacked Pillow and pyte. No dependency was installed.
   Curses cell observation and HTML provided repeatable captures. The coordinator
   supplied actual visual inspection through its browser tools. This manual
   observation handoff is recorded rather than credited to the builder.
7. The installed mandatory skills were loaded through the serialized wrapper
   with `--json --payload`: principle-build-the-lever produced committed replay,
   checker and capture tools; principle-prove-it-works required actual PTY/native
   playback; unslop kept prose direct. Features and Futures informed the rules
   first, terminal second work order and the pause to repair observed evidence.
   No speculative shared arcade framework or factory change was added.

## Feedback loop and next work

Outcome: approved local Invaders behavior is implemented. Human game feel remains
unobserved. Evidence: engine/UI/helper tests, full legal replay, actual PTY and
native metering passed in development, with capture observations as above.
Learning: a normal short PTY pass missed the resume race that a longer capture
workflow exposed. Testing the observation tooling also mattered; the first HTML
misrepresented row backgrounds. No broader game-code restructuring is justified.
Decision: proceed to the existing verification/review boundary once final
candidate evidence is current. Next: coordinator starts fresh independent review, prepares the reviewable PR
and final retrospective.
No completed delivery, release approval or human acceptance is claimed here.

---

# Historical planning handoff

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


## Final build verification result

On 2026-10-04, `python3 _system/scripts/sdlc.py verify invaders` passed against
committed candidate `cf629a1`. Live status subsequently reported verification
`current`, stage 3 `approved`, and all six checklist items passed, four automated
and two attested. `04-test/output/test-log.md` and `verification.json` are the
runtime-generated evidence. The full suite ran 153 tests with two disclosed
opt-in native skips; the separate required native check ran both tests with no
skips. Real terminal, CLI and existing configured Breakout help checks passed.

The evidence-only commit following this result does not change candidate code.
The coordinator should re-read live status, open the fresh independent review
checkout with the launcher, and target `fix/arcade-check-evidence` for the PR.
Use separate output paths for review commands. No push, PR, stage-5 launch or
merge was performed by the builder. Remote CI and human play/listening remain
unobserved. This is verified local build evidence, not release approval.
