# Paper Pong

## Problem and outcome

Add another useful offline terminal arcade game: solo Pong against a computer.
The user asked to run another game from start to finish and observe the process.
Pong, the rules below, the shared appearance, and sound reuse are proposed defaults,
not recorded user choices. This light brief and checklist need human acceptance
before implementation. No confirmed Seed Me contract exists for this run.

## Acceptance criteria

1. `python3 -B -m tink_pong` runs with Python 3.9+ on macOS/Linux, using the
   standard library and a terminal of at least 80 columns by 30 rows. `--help`
   works without a terminal; `--no-color` and `--no-sound` work as documented.
   A nonterminal launch returns a useful error. No network or new framework.
2. Player at left, computer at right; first to 7 wins. Use a fixed 60 by 20
   playing field and five-cell paddles. Up/down arrows or W/S move the player
   1.5 cells per key event, clamped to the field; letter controls accept either
   case. Space serves the centered ball at match start and after each point.
   The first serve travels toward the computer; subsequent serves alternate
   direction. Use a modest fixed diagonal on serve, alternating its vertical sign.
3. Ball speed stays at 24 cells/second. Top and bottom bounce; a paddle return
   aims according to contact position, at most 60 degrees from horizontal,
   with a small nonzero vertical component on a center return. Passing either
   paddle and crossing its end boundary awards exactly one point to the other
   side. No motion or further scoring occurs while waiting or after the match.
   The winner, both scores, and restart/quit controls remain visible.
4. The computer follows the ball's current height, moves at most 6 cells/second,
   stays in bounds, and cannot teleport or predict future bounces. It moves only
   during a rally. Reset both paddles to center between points. An executable
   replay using only legal player input and elapsed time must show a player win
   from an ordinary new match; a second run with an idle player must show a
   computer win. This proves both outcomes are reachable, not that human
   difficulty has been validated.
5. P pauses/resumes; R resets the match to 0–0 and a waiting serve; Q or Ctrl-C
   exits cleanly. Pause freezes both paddles and the ball; restart remains usable.
   Shrinking below the minimum freezes gameplay, ignores gameplay keys, and
   shows resize guidance. M and quit still work. Restoring size preserves a
   prior pause and resumes an active rally without catching up elapsed time.
   Restart preserves mute. Quit restores terminal settings and cleans up audio.
6. Match the existing Tetris/Snake paper, ink, and jade presentation: legible
   court, paddles, ball, score, serve/pause/winner state, controls, and sound
   status at 80x30 and 100x35 in color and monochrome. Keep the current games'
   behavior intact; avoid a shared-renderer refactor in this change.
7. Reuse `neon_tetris.audio.KeyboardAudio` and its credited samples: paddle
   contacts use `move`, points use `clear`, match loss uses `over`, and serve,
   pause/restart/unmute use `switch`. Match win may use `clear`. Wall bounces
   and automatic paddle movement are silent. M toggles mute; `--no-sound`
   disables it for the session. Missing/failed audio leaves the game playable.
   Stop queued audio on pause, restart, resize freeze, mute, and exit. Existing
   sample credits remain unchanged. No new samples or music.
8. README describes launch, controls, exact rules, platform limits, and evidence.
   The handoff records tools used, helpful instructions, actual failures and
   recoveries, coordinator help, and unverified limits without invented feedback.

## Approach

Add a small `tink_pong` package with a terminal-independent engine, curses UI,
and module entry point, following the existing games. Reuse the current audio
module. Keep this change to Pong, its tests/check scripts, README, and run notes.
Use bounded simulation steps and swept paddle/wall/end-boundary checks so delayed
frames cannot skip contacts. Cap accepted delayed-frame time at 0.1 seconds;
transition frames discard old elapsed time. Test those boundaries directly.

Add `tests/test_pong_engine.py`, `tests/test_pong_ui.py`,
`scripts/check_pong_tests.py`, and `scripts/check_pong_terminal.py`. The first
runner discovers all existing tests and fails if either Pong group is missing,
empty, fails, or has discovery errors; report every skip. Put any additional
reusable test tooling outside `runs/`. The PTY runner launches the actual game,
sends keys/resizes/signals, and saves its Pong-only transcript and state evidence
under `runs/pong/04-test/output/`. An optional state trace may observe the real
loop but must never inject or change gameplay. Do not rewrite older run evidence.

The checklist defines the executable checks and attested observations. Commands
naming new files are implementation requirements, not claims that those files
exist today. No implementation or approval has occurred at planning time.

## Risks and verification

- Terminal input repeats vary. Document event-based player motion; prove clamp,
  responsiveness, computer speed bound, legal win/loss replays, rally contacts,
  corner contacts, delayed frames, scoring once, and both completed-match states.
  Keep playtesting judgment separate from these checks.
- Test pause, waiting serve, match end, restart, mute, resize while playing and
  paused, ignored small-window input, transition timing, Q, and SIGINT. PTY
  evidence must compare actual states and persistent terminal settings and check
  process cleanup, not merely search for printed labels.
- Inspect retained actual terminal captures for the two supported sizes and
  color/monochrome, including serve, rally, pause, win and loss. Compare with an
  existing game's presentation and record concrete observations.
- Test cue routing and unavailable audio with controlled backends. Run existing
  native audio tests on this macOS trial host to establish real playback/metering;
  require nonempty tests and no skips for that check. Metering does not establish
  listener-perceived sound. No user hearing/device statement is required to
  finish verification; report listening as unverified if nobody listened.
- Run all game tests; preserve sample credits and existing launch behavior.
  CI results, independent review, release approval and actual human play feedback
  remain distinct from local automated evidence.

Excluded: multiplayer, difficulty menus, power-ups, saved scores, networking,
new dependencies, changing factory contracts, and unrelated game/audio refactors.
