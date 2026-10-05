# Paper Invaders — proposed change

## Problem and outcome

Jon wants another arcade game built through Substrate from start to finish, followed by a retrospective on how well that process worked. The product should reuse the existing paper/jade presentation and keyboard sounds, offer interesting formations, and make progression earned. Keep the implementation small.

**Proposed defaults, awaiting the definition decision:** an original Space Invaders-inspired terminal game, one player, three lives shared across three waves. The coordinator proposed this game; Jon has not separately confirmed the selection. Accepting this brief would accept these defaults. All numeric choices below are proposed defaults, accepted together only through the brief decision. This is an ordinary execution request, with no confirmed Seed Me contract. Do not import another game's seed or claim a new one exists.

## Acceptance criteria

1. `python3 -m tink_invaders` launches local keyboard play. `--help` works without a terminal; nonterminal play returns a useful error. Support `--seed N`, `--no-color`, and `--no-sound`. No network, model calls, added dependencies, or persistence is needed.
2. The player moves horizontally and fires upward at enemies that march sideways, reverse and descend at a boundary, and fire downward. A shot destroys at most one enemy and awards exactly 10 points once. Three distinct formations are defined below. A wave advances only when every enemy is destroyed; clearing wave three with at least one life wins. No timer, score threshold, restart, or skipped enemy grants progression.
3. Start with three lives for the whole run. An enemy projectile hitting the ship or an enemy reaching the ship row costs one life at most per simulation step. Survivors and score remain; clear all projectiles, return the ship to center and surviving enemies to their wave's starting rows, then wait for Space. At zero lives, stop with GAME OVER. If the last enemy and ship are hit in the same step, count both hits, apply life loss first, then advance/win only if lives remain. Restart resets all waves, enemies, score, timers and lives; retain mute state.
4. Use a fixed 60-column by 20-row playfield in the existing centered 80x30 canvas. Larger terminals add margins. Show score, lives, wave, sound status and controls. Distinct ASCII marks identify the ship, enemies and both shot directions in monochrome. Reuse the paper, carbon, jade and quiet panel style from DESIGN.md, with the existing mechanical samples through `KeyboardAudio`.
5. Controls: Left/Right or A/D move; Space starts a waiting wave/life or fires during play; P pauses/resumes; R restarts; M mutes; Q or Ctrl-C exits. Letters accept either case. The first Space starts without also firing. Pause, win and loss accept restart/mute/quit; win/loss ignore movement/fire. Undersizing freezes all game timers and ignores game controls, retaining mute/quit. Resize recovery preserves pause and discards catch-up time. No input queued during a freeze takes effect afterward.
6. Shots cannot pass through targets between updates. Enemy movement, enemy fire, player fire cooldown and collision order are deterministic for a fixed seed and legal input sequence. Multiple hits cannot cost multiple lives in one step or score a destroyed enemy twice. Enemies stay in bounds when the formation reverses; enemy fire originates only from surviving enemies with no living enemy below them in the same formation column.
7. An automated full-run replay starts a normal new game and wins all three waves using only legal move/fire/start inputs and advancing time. It uses normal ship/fire limits and enemy attacks, never edits game state, removes enemies, disables damage, or jumps waves. Retain its seed, inputs or deterministic controller, step limit, score and lives. This proves one clearable run, not fair or enjoyable difficulty.
8. Preserve Tetris, Snake, Breakout, their sample files/credits, and their tests. Document launch, controls, rule constants and evidence commands. Record actual visual, audio and human play observations separately from test results. Difficulty and play feel stay unobserved until Jon plays.
9. The run handoff supports a fresh build/review session and the final Substrate retrospective: what was attempted, observed, blocked, manually corrected, repeated, and left unknown. Do not change Substrate or factory code during this game run.

## Approach

### Small game and concrete rules

Add `tink_invaders/engine.py`, `ui.py`, `__main__.py` and a small formation data module only if useful. The engine owns game rules without curses or audio; the UI owns terminal input, rendering and wall-clock timing. Reuse `neon_tetris.audio.KeyboardAudio` directly. Adapt small existing game patterns without introducing a general arcade framework or refactoring other games.

Three proposed one-hit enemy patterns, each six columns by three rows (`#` enemy, `.` gap):

```text
1. Ranks    2. Wings    3. Islands
######      #....#      ##..##
######      .#..#.      ..##..
######      ..##..      ##..##
```

Place columns with sufficient spacing for distinct lanes and give every formation room to march and descend. Ranks is a broad target; Wings shifts the exposed firing lanes as rows clear; Islands separates groups and openings. These are design hypotheses. There are 18, 6 and 10 enemies, so a clean full clear scores 340. No bunkers, bosses, bonus ships, extra lives, power-ups or music in this slice. Enemy counts need not increase; each wave must be cleared to proceed. Use a constant, documented march/fire pace across waves rather than an unreviewed difficulty ramp.

Use bounded fixed simulation steps and document movement, shot, firing and descent constants. Repeated keys cannot bypass movement/fire limits. Allow one player shot and a small fixed cap of enemy shots. Resolve whole-path collisions deterministically; opposing shots pass through each other. Discard negative elapsed time, reject non-finite values, and bound delayed-frame work. Numeric tuning belongs in build but cannot relax these rules or bypass the required legal replay.

Play begins in a visible READY state; Space starts wave one. Each new wave and replacement life waits for Space. Held or repeated Space must never restart the simulation clock, starve updates, or freeze enemy/projectile movement (the earlier Pong regression). Pause and undersizing freeze every simulation clock and projectile, including cooldowns and enemy attack timers. Resume/resize must not deliver stored volleys. Wave transitions clear projectiles and reset positions/timers without restoring lives or score.

Map successful movement to `move`, firing to `rotate`, life loss to `over`, wave clear/win to `clear`, and pause/restart to `switch`. Blocked/frozen actions stay silent. Reuse the existing cue priority, per-frame audio `tick`, mute and cleanup. `--no-sound` prevents backend setup; unavailable audio leaves play intact and reports its warning after normal exit. Preserve sound files and credits.

### Work order and boundaries

Implement the rules, boundary cases and full legal replay first. Then add the terminal renderer, audio and real PTY checks. Pause after the first playable result: inspect actual failures and feedback; consolidate only a demonstrated obstacle within this scope, otherwise proceed. Return material changes to game rules or scope for review through the existing gate.

This isolated checkout is `/Users/jondev/dev/active/product/tink-arcade-invaders`, branch `feat/space-invaders`, observed at `773a2dcc1c3fb8c5f585854b5584c4cc03908cbc`. The intended game PR base is `fix/arcade-check-evidence` (checker fix PR #6 remains separate). Recheck both before delivery; no merge is implied. The launcher already created the feature/light run and opened stage 1. Implementation requires the actual human stage-3 definition decision and a fresh build stage. No test lock is needed for this feature run.

Keep `_shared/`, stage contracts, factory runtime, other runs and existing evidence unchanged. All new test infrastructure belongs in `scripts/` and `tests/`, never `runs/`. Retained results belong under this run. The current project verification checks Breakout help; preserve it, with the executable checklist below providing Invaders checks. Do not add new gates or mandatory human listening rituals.

## Risks and verification

These are planned commands, not results. Helpers must fail on missing required cases, discovery errors, failed/skipped required tests, timeouts or missing observations. Use explicit error checks so helper failures do not disappear under optimized Python.

- `python3 -B scripts/check_invaders_tests.py` (120 s): run the entire existing suite plus nonempty Invaders engine and UI groups and at least one full-run replay case. Require actual successful execution of the required groups/replay, not only discovery of skipped tests. Report counts and skips; existing opt-in native audio skips must be explicit.
- Engine cases cover boundaries/reversal/descent; surviving bottom shooters; player/enemy rate limits; whole-path shot collision; multiple and simultaneous hits; one-time score/life loss; partial-wave nonadvance; life recovery with survivors; all wave transitions/final win; zero-life loss including final-hit tie; restart from ready/playing/paused/won/lost; seed repeatability; invalid and delayed time. Full replay uses the same engine API as the UI and checks final score, lives, wave and enemies.
- UI cases cover all bindings/case variants, Space's separate ready/fire behavior, bounded input batches, repeated Space while enemies/projectiles keep advancing, paused/undersized clocks and input suppression, pause through resize, empty color support, safe clipping, mute/disabled/unavailable audio, all cue mappings and cleanup on normal/error exits. CLI tests cover help, options and nonterminal errors.
- `python3 -B scripts/check_invaders_terminal.py --output runs/invaders/04-test/output/terminal-transcript.txt` (90 s): real POSIX PTY, actual CLI and curses loop, fixed seed. Observe movement, shot creation, pause/resume, restart, mute, color and monochrome, 80x30 and 100x35, shrink to 40x12 and recover, including already-paused recovery and initial undersizing. Assert unchanged physics and timers during freezes and no catch-up on recovery. Exercise Q and SIGINT (document if SIGINT stands in for Ctrl-C), restored terminal modes and no surviving child process group. Clean up in `finally` and retain partial failure transcripts with nonzero exit. Support explicit `--output` so review never overwrites original evidence; test path and failure behavior. If state visibility is needed, use a read-only opt-in trace from the real loop, not a substitute simulation or a state-editing test mode.
- `python3 -B -m tink_invaders --help` (10 s): entry point smoke check; the suite provides CLI assertions.
- Reuse existing guarded native audio checks on macOS to prove repeated sample playback, signal metering and mute/resume; fail that check if skipped or missing. This does not prove anyone heard the game. Linux CI runs the full software suite and PTY with graceful sound fallback; report the macOS-only evidence separately.
- Retain actual viewed color/monochrome frames at minimum/larger sizes and inspect ready/play/pause/win/loss for legibility and style consistency. Record capture method and limits. Record actual listening/play feedback if supplied, otherwise explicitly say pending; never invent a listener or acceptance. The observation-record item may pass with honest pending human feedback, which is not acceptance of game feel.
- Following implementation and actual approval, commit code, record attested items, run `python3 _system/scripts/sdlc.py verify invaders`, then refresh `status invaders --json`. Only current passing evidence supports a verification claim. A fresh independent stage-5 reviewer checks the candidate and a PR is prepared against the confirmed base. Human merge authority remains separate.

Read live authority and evidence with `python3 _system/scripts/sdlc.py status invaders --json`.
