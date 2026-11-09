# Pong independent review

Reviewed HEAD: `3ec673b34ab2e3538820bbe994077cf808c90edc`

Base: `2125a67b3ebef15e3f3a7acf292d116144fed9d6`

Result: **Changes needed: one Important finding.** This is an independent local
review for the supervised Substrate trial. It grants no human release approval.
No source, tests, prior evidence, receipts, or approvals were changed.

## Important: Space during a rally discards simulation time

Location: `tink_pong/ui.py:173-174` (the subsequent advance guard is at line 177).

The loop sets `transition = True` for every Space key before checking whether
`Game.launch()` can serve. During a rally, launch does nothing, but the loop still
skips `game.advance(dt)`. Each repeated Space therefore drops another frame of
motion. Frequent Space input freezes the ball and computer without pausing the
game; player movement remains accepted. This breaks the approved fixed-speed
rule and creates an unintended way to stop the opponent during play.

Reproduced against the reviewed HEAD in two ways:

- One second of deterministic 60 Hz loop time without input moves the ball from
  `(30, 10)` to `(52.89454083400695, 17.200000000000024)`. Space each frame leaves
  it at `(30, 10)`, with `state='playing'` and `paused=False`.
- The actual curses process, driven through the existing `Terminal` helper,
  received Space every 2 ms for 0.6 seconds after serving. Across 31 recorded
  frames the ball stayed at `(30.95393920141694, 10.300000000000002)` with
  `paused=False`. Q exited successfully and restored terminal modes. The short
  sleep here deliberately supplies sustained input; state records establish the
  result, not the sleep itself.

Minimal deterministic reproduction from the repository root:

```sh
python3 -B - <<'PY'
from unittest.mock import Mock, patch
from tink_pong.engine import Game
from tink_pong.ui import _run_loop
g = Game()
g.launch()
s = Mock()
s.getmaxyx.return_value = (30, 80)
s.getch.side_effect = [32, -1] * 60 + [ord('q')]
times = [0]
for frame in range(1, 62):
    times.extend([frame / 60, frame / 60])
with patch('tink_pong.ui.time.monotonic', side_effect=times), \
     patch('tink_pong.ui.time.sleep'):
    _run_loop(s, Mock(), g, Mock())
print(g.snapshot())
assert g.x > 30, 'Ignored Space froze an active rally'
PY
```

The assertion fails. Discard elapsed time when an input actually changes the
simulation state, including a successful serve. Add a loop regression for Space
during an active rally, retaining successful serve/pause/restart timing checks.
Return to build and refresh verification after fixing this.

## Checks and acceptance coverage

One focused review covered engine behavior, terminal input/timing, audio,
rendering, documentation, and local evidence. This small offline change did not
justify separate specialist passes. The diff leaves the existing game packages,
audio implementation, and sample credits unchanged.

- Read AGENTS, installed SDLC and stage 5 contracts, `_shared/REVIEW.md`, the
  approved brief/checklist, stage skill pick, handoff, verification receipt/log,
  new source/tests/scripts, CI workflow, README diff, and existing DESIGN.
- `sdlc.py status pong`: stage 3 approved, 6/6 checklist items passed,
  verification current. These local records do not authenticate release approval.
- `python3 -B scripts/check_pong_tests.py`: 128 tests passed; 8 Pong engine and
  8 Pong UI tests. Two opt-in native audio tests skipped as reported.
- Existing real PTY runner passed arrows/W/S, serve, pause/resume, restart,
  mute, resize in play/pause, ignored undersized input, Q/SIGINT, restored
  persistent modes, and process-group cleanup. Its output was redirected to a
  temporary directory through an in-memory OUTPUT override. Retained evidence
  was not overwritten; temporary output was removed after inspection.
- `python3 -B -m tink_pong --help` passed.
- `PYTHONPATH=. python3 -B scripts/pong_replay.py`: legal player won 7–0 in
  7,578 steps; idle player lost 0–7 in 2,598 steps. Reviewed the replay: it uses
  ordinary initialization, movement, serve and elapsed time without assigning
  scores or outcomes.
- `NEON_TETRIS_AUDIO_TESTS=1 python3 -B -m unittest discover -s tests -p
  test_native_audio.py -v`: 2 tests passed, no skips, 6.323 seconds.
- Reviewed paddle endpoints and center angles, simultaneous wall/paddle contact,
  missed paddles, swept collision ordering, fixed speed, bounded computer motion,
  delayed frames, scoring once, and stopped match/waiting/paused states. Existing
  tests exercise those paths; no additional concrete engine defect found.
- Reviewed cue routing, disabled audio, mute preservation, backend failure and
  cleanup coverage. Shared audio catches unavailable backend/sample failures;
  the game continues. Native metering does not establish listening quality.
- Actually inspected retained PNGs: `80x30-color/serve`, `80x30-color/rally`,
  `80x30-mono/pause`, `100x35-color/win`, and `100x35-mono/loss` under
  `04-test/output/captures/`. Courts and controls fit; states, scores and sound
  labels remain visible; paper/ink/jade and monochrome attributes match DESIGN.
  This sample covers both sizes/modes and all five states, not all 20 images.

The existing successful-transition test does not exercise a rejected serve in
the real loop; the input-binding test checks that no cue fires, but cannot catch
lost time. Passing checks therefore did not rule out the finding above.

## Evidence limits

Visual captures use the normal renderer with engine states produced separately;
they are not live completed terminal matches. Legal replay demonstrates reachable
outcomes, not human difficulty or enjoyment. PNG rasterization is approximate.
Human play, taste and listening remain unverified. This review did not establish
remote CI, Python 3.9 execution, Linux execution, forge approval, or deployment.
The checked-in workflow covers macOS/Linux on Python 3.11; its existence is not
a passing CI result. No new security boundary defect was identified.

## Fresh-session trial notes

- Used `control-cli` and `principle-prove-it-works`. Read their full actual
  payloads through `python3 -B _system/scripts/sdlc.py skills tink -- mount
  --json --payload NAME` before relying on them. The former led to reusing the
  existing PTY helper and state waits; the latter led to independently running
  the terminal process and confirming the timing defect there.
- The coordinator supplied the checkout/base, read-only scope, routed skill,
  known JSON/payload command shape, and human-feedback limits. No further
  coordinator intervention was needed to perform the review.
- Tools: shell/Python, Git read-only inspection, unittest, installed SDLC status
  and skill payload wrapper, POSIX PTY, and image inspection. A memory-registry
  search returned no relevant hits. No browser, external posting, approval,
  source edit, push, or installation was performed.
- Initial replay invocation omitted the documented `PYTHONPATH=.` and failed
  with `ModuleNotFoundError: tink_pong`. Reading the README supplied the exact
  command; it passed. This was a reviewer invocation error, not a product defect.
- The PTY runner prints its output relative to the repository root. For temporary
  output outside that root, the in-memory Path subclass returned its full path
  for that final display call. No checked-in helper was changed.
- The generated deployment block in AGENTS and untracked stage-5 artifacts were
  already present at review entry. Only this review file was written. No remaining
  session blocker; the Important finding requires implementation work.
