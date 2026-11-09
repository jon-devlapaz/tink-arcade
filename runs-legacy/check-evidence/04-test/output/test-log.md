
$ ["python3", "-B", "-m", "tink_breakout", "--help"]
usage: python3 -m tink_breakout [-h] [--no-color]

Offline terminal Breakout: clear three boards with three lives.

options:
  -h, --help  show this help message and exit
  --no-color  use monochrome rendering

Requires an 80 x 30 terminal. Arrows or A/D move; Space launches; P pauses; R
restarts; Q or Ctrl-C quits.

# checklist item accepted-regressions
$ ["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_terminal_checkers.py", "-v"]
test_consumed_first_turn_is_accepted (test_terminal_checkers.SnakeQueueCheckerTests.test_consumed_first_turn_is_accepted) ... ok
test_early_input_is_accepted (test_terminal_checkers.SnakeQueueCheckerTests.test_early_input_is_accepted) ... ok
test_missing_or_wrong_order_turns_are_rejected (test_terminal_checkers.SnakeQueueCheckerTests.test_missing_or_wrong_order_turns_are_rejected) ... ok
test_explicit_external_destination_preserves_existing_evidence (test_terminal_checkers.TranscriptDestinationTests.test_explicit_external_destination_preserves_existing_evidence) ... ok

----------------------------------------------------------------------
Ran 4 tests in 8.525s

OK

# checklist item snake-and-existing-tests
$ ["python3", "-B", "scripts/check_snake_tests.py"]
Snake engine: 9 tests
Snake ui: 10 tests
..........................................................................ss.............................................
----------------------------------------------------------------------
Ran 121 tests in 26.790s

OK (skipped=2)
Legal full-clear replay: seed=20261004, steps=31475, boards=[(0, 16548, 360, 3), (1, 19078, 480, 3), (2, 31474, 760, 3)]
Total: 121; skips: 2
SKIP test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples
SKIP test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples

# checklist item breakout-tests
$ ["python3", "-B", "scripts/check_breakout_tests.py"]
Breakout engine: 9 tests
Breakout layouts: 2 tests
Breakout ui: 4 tests
..........................................................................ss.............................................
----------------------------------------------------------------------
Ran 121 tests in 26.674s

OK (skipped=2)
Legal full-clear replay: seed=20261004, steps=31475, boards=[(0, 16548, 360, 3), (1, 19078, 480, 3), (2, 31474, 760, 3)]
Total: 121; skips: 2
SKIP test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples
SKIP test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples

# checklist item snake-terminal
$ ["python3", "-B", "scripts/check_snake_terminal.py", "--output", "runs/check-evidence/04-test/output/snake-terminal.txt"]
PASS: Snake real PTY arrows/WASD, queue, pause, restart, resize, mute, wall collision, Q and SIGINT; modes restored; child groups gone.
Transcript: /Users/jondev/dev/active/product/tink-arcade-check-evidence/runs/check-evidence/04-test/output/snake-terminal.txt

# checklist item breakout-terminal
$ ["python3", "-B", "scripts/check_breakout_terminal.py", "--output", "runs/check-evidence/04-test/output/breakout-terminal.txt"]
PASS: real PTY input, launch, pause, resize, restart, quit and Ctrl-C; terminal restored; no child group remains.
Transcript: /Users/jondev/dev/active/product/tink-arcade-check-evidence/runs/check-evidence/04-test/output/breakout-terminal.txt
