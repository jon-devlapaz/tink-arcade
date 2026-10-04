
$ ["python3", "-B", "-m", "tink_breakout", "--help"]
usage: python3 -m tink_breakout [-h] [--no-color]

Offline terminal Breakout: clear three boards with three lives.

options:
  -h, --help  show this help message and exit
  --no-color  use monochrome rendering

Requires an 80 x 30 terminal. Arrows or A/D move; Space launches; P pauses; R
restarts; Q or Ctrl-C quits.

# checklist item rules-ui-regressions
$ ["python3", "-B", "scripts/check_snake_tests.py"]
Snake engine: 9 tests
Snake ui: 10 tests
..........................................................................ss....................................
----------------------------------------------------------------------
Ran 112 tests in 0.566s

OK (skipped=2)
Legal full-clear replay: seed=20261004, steps=31475, boards=[(0, 16548, 360, 3), (1, 19078, 480, 3), (2, 31474, 760, 3)]
Total: 112; skips: 2
SKIP test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples
SKIP test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples

# checklist item snake-terminal
$ ["python3", "-B", "scripts/check_snake_terminal.py"]
PASS: Snake real PTY arrows/WASD, queue, pause, restart, resize, mute, wall collision, Q and SIGINT; modes restored; child groups gone.
Transcript: runs/snake/04-test/output/terminal-transcript.txt

# checklist item snake-cli
$ ["python3", "-B", "-m", "tink_snake", "--help"]
usage: python3 -m tink_snake [-h] [--seed SEED] [--no-color] [--no-sound]

Classic offline Snake on a paper terminal canvas.

options:
  -h, --help   show this help message and exit
  --seed SEED  repeat the same food sequence on restart
  --no-color   use monochrome rendering
  --no-sound   disable audio for the entire session

Requires 80 x 30. Arrows/WASD steer; P pauses; R restarts; M mutes; Q or
Ctrl-C quits.

# checklist item native-playback
$ ["python3", "-B", "-c", "import os,sys,unittest; assert sys.platform == 'darwin', 'Native playback requires macOS'; os.environ['NEON_TETRIS_AUDIO_TESTS']='1'; suite=unittest.defaultTestLoader.discover('tests', pattern='test_native_audio.py'); assert suite.countTestCases() >= 2, 'Missing native audio tests'; result=unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(0 if result.wasSuccessful() and result.testsRun >= 2 and not result.skipped else 1)"]
test_each_sample_renders_on_repeated_spaced_plays (test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays) ... ok
test_replay_after_mute_and_resume (test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume) ... ok

----------------------------------------------------------------------
Ran 2 tests in 6.329s

OK
