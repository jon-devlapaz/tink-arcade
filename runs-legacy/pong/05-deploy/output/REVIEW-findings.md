# Pong focused review of terminal-test repair

Reviewed HEAD: `7d26e522711208e8968c783b712825a0dcd0e618`

Previous reviewed HEAD: `eca10ff0d86032314ba89f66238913a4c9955050`

Result: **No Important findings in this repair.** The revised terminal check
accepts normal changes of direction and still detects the original freeze.
Game code, unit tests, renderer and audio are unchanged since the prior review.
This is local advisory review, not human release approval or a passing CI claim.

## Independent checks

- Read the exact diff, the retained Pong CI failure, the builder's old-guard
  reproduction, updated handoff, and current SDLC status. Status reports current
  verification and 6/6 passed. The only executable change is the PTY helper.
- Parsed the actual two states from the failed CI log. The ball moved left from
  x `58.68882589231052` to `58.2217608291302` with negative velocity. The revised
  assertion accepts those exact states; it no longer requires rightward or
  downward movement.
- Ran the complete revised PTY helper against this candidate with its transcript
  redirected to temporary output. All checks passed, including 20 Space samples,
  pause/resume, restart, mute, resize, Q/SIGINT, terminal settings and cleanup.
- Independently copied only the Pong/audio packages into a temporary directory,
  restored the original broken transition guard there, and ran the current
  unmodified helper against that copy. It failed with `No-op Space froze rally`
  on identical consecutive playing states at x `31.144727041700328`,
  y `10.360000000000003`. Thus the corrected check still rejects the original
  bug. The production checkout was not modified; temporary files were removed.
- The new comparison accepts changed ball coordinates, a scored point or a serve
  state change. It still rejects an unchanged rally and requires an unpaused
  state. The reset/serve after sampling ensures later pause checks start in a
  rally even if a point ended the sampled rally. Existing later control checks
  remain in place. The deterministic 60-frame exact-progress regression remains
  unchanged and complements the direction-independent terminal observation.

## Limits and process

The prior review below remains applicable to unchanged game behavior and evidence.
The earlier claim that the new PTY assertion passed was accurate locally, but that
run did not encounter the bounce exposed in CI. The retained CI failure is a
harness defect, not evidence that the ball froze. The separate existing Snake CI
failure was read as context; Snake is unchanged and was not reviewed or repaired
here. Fresh remote CI must still be inspected by the coordinator.

Used the previously read `control-cli` and `principle-prove-it-works` skills to
run both the real candidate and an isolated broken control. Tools were read-only
Git inspection, Python, SDLC status and the existing PTY helper. The coordinator
advanced the checkout and supplied the CI failure context. No additional session
blocker, skill mount, installation, external posting, source/test/receipt edit,
commit, push or approval occurred. Only this review file was updated.

---

## Preserved prior review (eca10ff)

# Pong independent review after repair

Reviewed HEAD: `eca10ff0d86032314ba89f66238913a4c9955050`

Original reviewed HEAD: `3ec673b34ab2e3538820bbe994077cf808c90edc`

Original base: `2125a67b3ebef15e3f3a7acf292d116144fed9d6`

Result: **No remaining Important findings.** The original timing defect is
resolved. This local advisory review is complete; it grants no human release
approval and establishes no remote CI or deployment result.

## Resolved finding

The initial finding and reproduction are retained in `REVIEW-initial.md`.
Previously, every Space key skipped elapsed time even when serving was rejected
during an active rally. The loop now compares game state and pause state around
each input and skips elapsed time only after an actual state change.

Independent rechecks on the exact HEAD above:

- The original deterministic reproduction now passes. After 60 frames with Space
  each frame, the ball reaches `(52.89454083400695, 17.200000000000024)` and the
  computer reaches `15.950000000000085`, matching the original no-input result.
  The match remains playing and unpaused.
- Reviewed the added regression: Space, unknown input and mute are each compared
  with ordinary elapsed-time advancement over 60 frames. It checks ball and both
  paddle positions plus accumulated fractional time.
- `python3 -B scripts/check_pong_tests.py`: 129 tests passed in 0.614 seconds,
  with 8 Pong engine and 9 Pong UI tests. The two opt-in native audio tests
  skipped with their reasons printed.
- Reran the extended real PTY runner. It passed 20 successive Space inputs during
  a rally, along with its existing serve, arrows/W/S, pause/resume, restart, mute,
  resize, Q/SIGINT, terminal-mode restoration and process cleanup checks.
- Independently repeated sustained Space input in the actual terminal process.
  Across 31 frames, x advanced from `30.95393920141694` to `45.0722393823879`
  and y from `10.300000000000002` to `14.74000000000004`; all frames remained
  unpaused. Q restored terminal settings and removed the process group.
- Inspected transition behavior: a successful serve, pause/resume and restart
  from a rally still mark a transition. Restart while already waiting remains
  frozen because the engine is waiting. A transition flag remains set across
  multiple inputs in the same frame. No further concrete timing defect found.
- Fresh `sdlc.py status pong`: stage 3 approved, 6/6 checklist items passed,
  verification current. The older visual attestation is flagged for relevance;
  the renderer is unchanged, so its layout observations still apply.

## Scope and evidence limits

Inspected all changes since the original review. Application changes are limited
to the input transition guard; other changes are its unit/PTY regressions and run
evidence. Prior review coverage of engine contacts, speed, scoring, legal win/loss
replays, audio failure behavior, documentation and presentation remains applicable.
The renderer, audio implementation, other games, and sample credits are unchanged.

The original review actually inspected five retained PNGs spanning both sizes,
color/monochrome, and all five game states. Those observations are retained in
`REVIEW-initial.md`; no new visual inspection is claimed here. Original native
playback checks passed 2/2 without skips. The repaired candidate's formal log
records another native pass; this focused recheck did not replay native audio.

Human play, taste and listening remain unverified. Legal engine replays establish
reachable outcomes, not human difficulty. Captures exercise the renderer with
separately produced states and approximate terminal font rasterization. This
review did not establish Python 3.9 or Linux execution, remote CI, authenticated
code-owner approval, or deployment. No additional security-boundary concern was
introduced by the narrow fix.

## Fresh-session and tool notes

The same independent reviewer performed this recheck. The coordinator advanced
the detached review checkout to the repaired candidate and preserved the original
report as `REVIEW-initial.md`. No source, tests, receipts, or prior evidence were
changed by the reviewer. Only this current report was updated.

Skills actually used remain `control-cli` and `principle-prove-it-works`, whose
full payloads were read during the initial review through the installed SDLC
wrapper with `mount --json --payload`. Their guidance led to reuse of the local
PTY runner and an independent real-process reproduction rather than trusting
passing tests alone. Tools used here: read-only Git inspection, Python/unittest,
SDLC status, and POSIX PTY input/state inspection. No new skill, installation,
external message, push or approval was needed.

Terminal output was redirected in memory to temporary paths and removed after
inspection. The runner's final relative-path display was adapted in memory; no
helper file was edited. One sustained-input probe initially demanded more than
20 frames in a fixed 0.6-second window and got exactly 20 despite clear motion.
That reviewer assertion was too strict for scheduling and undrained terminal
output. Repeating with output drainage and a movement-based assertion passed
across 31 frames. The deterministic exact-time comparison also passed. No product
failure or unresolved review blocker remains.
