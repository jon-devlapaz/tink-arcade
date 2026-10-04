
$ ["python3", "-B", "-m", "tink_breakout", "--help"]
usage: python3 -m tink_breakout [-h] [--no-color]

Offline terminal Breakout: clear three boards with three lives.

options:
  -h, --help  show this help message and exit
  --no-color  use monochrome rendering

Requires an 80 x 30 terminal. Arrows or A/D move; Space launches; P pauses; R
restarts; Q or Ctrl-C quits.

# checklist item pong-rules-regressions
$ ["python3", "-B", "scripts/check_pong_tests.py"]
Pong engine: 8 tests
Pong ui: 8 tests
..........................................................................ss....................................................
----------------------------------------------------------------------
Ran 128 tests in 0.602s

OK (skipped=2)
Legal full-clear replay: seed=20261004, steps=31475, boards=[(0, 16548, 360, 3), (1, 19078, 480, 3), (2, 31474, 760, 3)]
Total: 128; skips: 2
SKIP test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples
SKIP test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples

# checklist item pong-terminal
$ ["python3", "-B", "scripts/check_pong_terminal.py"]
PASS: Pong real PTY arrows/W/S, serve, pause, restart, resize, mute, Q and SIGINT; modes restored; child groups gone.
Transcript: runs/pong/04-test/output/terminal-transcript.txt

# checklist item pong-cli
$ ["python3", "-B", "-m", "tink_pong", "--help"]
usage: python3 -m tink_pong [-h] [--no-color] [--no-sound]

Offline solo Pong. First to seven wins.

options:
  -h, --help  show this help message and exit
  --no-color  use monochrome rendering
  --no-sound  disable audio for the entire session

Requires 80 x 30. Up/down or W/S move; Space serves; P pauses; R restarts; M
mutes; Q or Ctrl-C quits.

# checklist item native-playback
$ ["python3", "-B", "-c", "import os,sys,unittest; assert sys.platform == 'darwin', 'Native playback requires this trial macOS host'; os.environ['NEON_TETRIS_AUDIO_TESTS']='1'; suite=unittest.defaultTestLoader.discover('tests', pattern='test_native_audio.py'); assert suite.countTestCases() >= 2, 'Missing native audio tests'; result=unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(0 if result.wasSuccessful() and result.testsRun >= 2 and not result.skipped else 1)"]
test_each_sample_renders_on_repeated_spaced_plays (test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays) ... ok
test_replay_after_mute_and_resume (test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume) ... ok

----------------------------------------------------------------------
Ran 2 tests in 6.367s

OK
