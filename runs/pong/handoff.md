# Pong handoff

## Current status

Jon accepted the brief and checklist. The coordinator recorded stage 3 approval
and opened build. Build and formal verification are complete. Status reports stage 3 approved,
6/6 checklist items passed, and current verification. No release approval or human play/listening feedback has been claimed.

## Planning history

Read `brief.md` and `checklist.json`. They propose solo Pong to 7, a limited-speed
computer, a direct court with Space to serve, paper/jade visuals, and the current
keyboard sounds. They are defaults for the user's request to run another arcade
game from start to finish and observe it, not previously confirmed user choices.
Seed Me execution triage intentionally avoided a new interview or fabricated seed.

This stage wrote only planning artifacts. No application implementation, test
execution, receipt, approval, stage launch, or commit was performed by this agent.
`status pong` accepts the six-item checklist: four executable checks, two attested
observations; stage 3 remains pending. The launcher/coordinator must obtain actual
human acceptance of this brief and checklist before opening build.

## Fresh-session pointers

Read root `AGENTS.md`, `_system/SDLC.md`, the installed build contract, and these
planning files. Use the existing engine/UI separation and test scripts as examples.
`_system/verification.json` currently checks only Breakout help; the Pong checklist
therefore requires an all-game suite, actual Pong PTY check, Pong help, native
sample playback, visual inspection and accurate documentation. The proposed new
commands do not exist until build. Do not mistake present planning status for proof.

## Trial observations

- Read Substrate README/start guide, installed router/stage contract, run metadata,
  current README/DESIGN, Snake UI/entrypoint, shared audio, Breakout engine outline,
  and Snake test/PTY runners. Existing files supplied concrete implementation and
  evidence patterns without needing a capability search or coordinator decisions.
- Shell tools used: `cat`, `rg`, `sed`, `command -v`, `git status/diff`, installed
  `sdlc.py status`, `tink --help`, `tink mount --help`, the SDLC Tink wrapper, and
  Python to write structured checklist definitions. A memory-registry search had
  no relevant hits. No browser, paid model, audio playback, or PTY was used in plan.
- Required `principle-build-the-lever` changed the verification plan: require
  rerunnable Pong suite and PTY scripts, rather than narrative-only checks. Their
  implementation belongs to build; this stage has not claimed to create them.
- First skill read failed: the generated `.tink/.active/.../SKILL.md` pointer did
  not exist. Mount help advertised `--payload` but did not show that it requires
  `--json`. `sdlc.py skills tink -- mount principle-build-the-lever --payload`
  failed with `required arguments ... --json`. Retried using the reported form:
  `python3 _system/scripts/sdlc.py skills tink -- mount --json --payload principle-build-the-lever`.
  This returned the complete skill payload from the home library with
  `mounted:false`; the skill has no scripts. Recovery needed no human approval.
- No stage-1 pick receipt existed. No routed skill was invented or assumed.
  Initial file inventory used two incorrect guessed package names (`neon_snake`,
  `neon_breakout`); README supplied the actual `tink_snake`/`tink_breakout` paths.
- Coordinator clarified reuse of sound without mandatory subjective listening
  and called out the thin shared verification config and immediate-entry design
  principle. The brief reflects those points. No unresolved planning blocker.

## Evidence still to obtain

All implementation checks, terminal captures, native playback, independent review,
and release remain future work. Human difficulty and listening quality must be
reported honestly if not observed. Neither is fabricated as a verification claim.
Keep future tooling and tests outside `runs/`; save only run evidence here.


## Build and verification observations

The builder read root AGENTS, `_system/SDLC.md`, stage 03/04 contracts, the approved
brief/checklist, status, and existing Snake/Breakout engine, UI, entry point,
tests and PTY scripts. The existing source provided enough patterns to implement
Pong without a new dependency or a second capability search. Shared games, audio,
sample credits, factory files and old run evidence were left unchanged.

The first status was stale. The coordinator found that the planning agent had
edited the brief after approval. The builder made no implementation writes until
the coordinator restored the displayed approved version. Status then returned
approved without inventing a new human decision. Only the builder wrote the
checkout after the coordinator resolved that overlap.

Skills read through `sdlc.py skills tink -- mount --json --payload` were
`control-cli`, `principle-build-the-lever`, `unslop`, and
`principle-prove-it-works`. The stage-open control-cli pick led to adapting the
existing PTY runner with state-based waits. Build-the-lever led to committed
Pong suite, terminal, replay and capture scripts. Prove-it-works required running
the real curses loop and native audio. Unslop guided README and these notes.
The known JSON/payload form worked on the first build attempt. No mount payload
was assumed from a skill name alone. No new model or service was used.

Tools used were shell commands through exec, Python file edits and unittest,
Git status/diff, the installed SDLC CLI and serialized Tink wrapper, curses,
POSIX PTY/termios/signals, subprocess, macOS Quick Look, and image inspection.
A memory-registry search had no relevant hits. No browser, deployment, package
installation, or external messages were needed. A local Pillow probe failed
because it was absent; no package was installed.

Direct checks passed before formal verification. The all-game suite ran 128 tests
with 8 Pong engine and 8 Pong UI cases. Only the two opt-in native audio tests
skipped there; both passed separately on macOS with their opt-in enabled.
The ordinary legal player replay wins 7-0 in 7,578 steps. The idle replay loses
0-7 in 2,598 steps. These use legal moves, serve and elapsed time, with no injected
match result. Physics tests separately inject boundary positions to test contacts,
corners, score-once behavior, timing caps and match freezing.

The real PTY check passed arrows/W/S, serve, pause/resume, restart, mute,
undersized input rejection, resizing while playing and paused, Q and SIGINT.
It compared state snapshots and persistent terminal modes, and confirmed that
the game process group exited. The transcript records the actual observed states.
The coordinator requested a Pong CI workflow using the existing macOS/Linux
matrix. It runs help, suite and PTY checks. CI itself has not been run locally.

### Visual evidence

`04-test/output/captures/` contains 20 real curses cell captures covering
80x30 and 100x35, color and monochrome, and serve/rally/pause/win/loss. The capture
script invokes the normal renderer in a PTY, reads actual cells and attributes,
and retains JSON, ANSI output and SVG. Legal replays produce final match states.
PNG previews use Quick Look and approximate terminal font rasterization.

The initial Quick Look export clipped the larger canvas at its own viewport.
The supervisor caught it. Constraining the SVG display width to 700 while keeping
the full viewBox fixed the export; no game layout change was needed. Initial
previews also showed raster cell seams. PNG rendering is an inspection aid, not
proof of a particular user's terminal font appearance.

The supervisor actually inspected these PNG samples:
- 80x30-color/serve, rally and loss
- 80x30-mono/pause
- 100x35-color/win and serve
- 100x35-mono/loss

All are under `04-test/output/captures/` with `.svg.png` suffixes. The supervisor
found full courts and paddles, visible controls, clear winner/scores, and paper,
ink and jade consistent with DESIGN. Both sizes/modes and all five states were
covered by the inspected sample set; nobody claimed to inspect all 20 images.
The builder also inspected 80x30 color serve and corrected 100x35 color win.
This is agent visual inspection. Human taste, live difficulty and enjoyment remain
unverified, as does listener-perceived sound. Native playback proves rendering
and metering only. Independent review and release remain the coordinator's next
steps after current formal verification.


## Final verification

Candidate code was committed as `f8f3cae` before the final SDLC run. Both attested
items were marked before verification. `python3 _system/scripts/sdlc.py verify pong`
passed, and a fresh status reported current verification and 6/6 checklist items.
The generated `04-test/output/test-log.md` records 128 suite tests, the two default
native skips, real PTY success, Pong help, and the separate 2/2 native playback
check without skips. `verification.json` binds that result to the candidate.
Only run evidence was committed afterward. No push, PR, stage launch or approval
was performed by the builder. Independent review remains next.

Git whitespace checking found only raw terminal output whitespace in retained
ANSI/transcript evidence. Those bytes were preserved; source files passed the
whitespace check. The final verification refreshed the transcript with its own
observed states.

## Independent review repair

The independent reviewer found that pressing Space during an active rally skipped
elapsed time even though serve was ignored. A regression through the real loop
reproduced it: after 60 frames the ball remained at x=30 rather than x=52.89454.
The failing output is retained in `04-test/output/noop-space-before-fix.txt`.
The initial review is preserved in `05-deploy/output/REVIEW-initial.md`.

The loop now compares game state and pause state before and after each key. It
skips old elapsed time only for an actual transition. Repeated Space, an unknown
key, and mute are each checked across 60 frames against ordinary elapsed-time
advancement. Existing pause, restart, serve and resize transition checks still
pass. The real PTY check now sends Space on 20 successive observed rally frames
and requires ball movement on each one. Its transcript retains those snapshots.

The repaired suite passes 129 tests, including 9 Pong UI cases. The same two
opt-in native audio tests skip in the default suite. Renderer and rules are
unchanged, so the inspected visual captures still describe this candidate's
layout. README still matches behavior; this repair makes ignored Space behave
as documented. No new human play or listening claim is made.

Repair code was committed as `7226093` before rerunning formal SDLC verification.
That verification passed all configured checks, including 129 suite tests, the
extended real PTY check, help, and separate native audio with no skips. The two
default suite skips remain explicitly reported. Final status is checked again
after this evidence-only commit. Independent rereview remains next.


## Independent review and PR

The fresh reviewer rechecked eca10ff0d86032314ba89f66238913a4c9955050 and found
no remaining Important issues. The original repeated-Space reproduction, extended
real-terminal checks and 129-test suite passed. REVIEW-initial.md preserves the
failed review; REVIEW-findings.md records the repaired candidate and remaining
limits. This final change saves review evidence only.

Delivery PR: https://github.com/jon-devlapaz/tink-arcade/pull/5. GitHub checks must
be read at the latest head; local review is not human merge approval. The
coordinator will save a separate local archive and retrospective after CI passes.

## CI terminal-check repair

Pong CI run 37241686148 failed on macOS because the new Space check incorrectly
required x and y to increase on every observed frame. Its saved failure shows
valid leftward motion after a computer-paddle return, from x=58.6888 to x=58.2218.
The game was playing normally. This was a test assertion defect, not evidence
that the earlier Space freeze remained. The full log is retained in
`04-test/output/ci-pong-initial-failure.txt`.

The check now requires changed ball position, game state or score, with no pause.
This accepts bounces, point completion and a subsequent serve. It no longer waits
only for the transient playing state, and later pause/resize checks start a fresh
match so they do not assume the Space sample ended mid-rally. No direction or
wall-clock distance is assumed. The deterministic 60-frame loop regression still
checks exact elapsed-time progress.

The revised PTY check passed locally. To test its ability to reject the original
bug, the builder made a temporary isolated copy of Pong/audio and the revised
terminal script, restored only the old transition guard in that copy, and ran it.
It failed on unchanged x/y and state at the new assertion. Output is retained in
`04-test/output/noop-space-old-guard-pty.txt`. The temporary copy was removed;
production code was not weakened.

Existing Snake CI run 37241686099 also failed on macOS while waiting for an exact
two-turn queue state. The log shows the snake subsequently traveled left and hit
a wall, while the queue was empty. That transient-observation failure is retained
in `04-test/output/ci-snake-initial-failure.txt`. Snake is outside this repair and
was not modified. Local Pong verification does not claim that either failed CI
run has become green. The coordinator must inspect fresh CI and handle the
separate Snake failure before making release claims.
