
$ ["python3", "-B", "-m", "tink_breakout", "--help"]
usage: python3 -m tink_breakout [-h] [--no-color]

Offline terminal Breakout: clear three boards with three lives.

options:
  -h, --help  show this help message and exit
  --no-color  use monochrome rendering

Requires an 80 x 30 terminal. Arrows or A/D move; Space launches; P pauses; R
restarts; Q or Ctrl-C quits.

# checklist item rules-ui-replay
$ ["python3", "-B", "scripts/check_invaders_tests.py"]
Invaders engine: 14 tests
Invaders ui: 13 tests
..........................................................................................................ss.............................................
----------------------------------------------------------------------
Ran 153 tests in 26.732s

OK (skipped=2)
Legal full-clear replay: seed=20261004, steps=31475, boards=[(0, 16548, 360, 3), (1, 19078, 480, 3), (2, 31474, 760, 3)]
Legal replay: seed=7, steps=1528/36000, score=340, lives=3
SKIP test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples
SKIP test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples
Total: 153; skips: 2

# checklist item real-terminal
$ ["python3", "-B", "scripts/check_invaders_terminal.py", "--output", "runs/invaders/04-test/output/terminal-transcript.txt"]
PASS: actual PTY controls, shots, clocks, freezes, recovery, color/mono, Q/SIGINT and cleanup.
Transcript: /Users/jondev/dev/active/product/tink-arcade-invaders/runs/invaders/04-test/output/terminal-transcript.txt

# checklist item cli
$ ["python3", "-B", "-m", "tink_invaders", "--help"]
usage: python3 -m tink_invaders [-h] [--seed SEED] [--no-color] [--no-sound]

Clear three waves with three shared lives on a paper terminal canvas.

options:
  -h, --help   show this help message and exit
  --seed SEED  repeat the same enemy attack sequence on restart
  --no-color   use monochrome rendering
  --no-sound   disable audio for the entire session

Requires 80 x 30. Arrows/A/D move; Space starts or fires; P pauses; R
restarts; M mutes; Q or Ctrl-C quits.

# checklist item native-playback
$ ["python3", "-B", "-c", "import os,sys,unittest; sys.platform == 'darwin' or sys.exit('Native playback requires macOS'); os.environ['NEON_TETRIS_AUDIO_TESTS']='1'; suite=unittest.defaultTestLoader.discover('tests', pattern='test_native_audio.py'); suite.countTestCases() >= 2 or sys.exit('Missing native tests'); result=unittest.TextTestRunner(verbosity=2).run(suite); sys.exit(0 if result.wasSuccessful() and result.testsRun >= 2 and not result.skipped else 1)"]
test_each_sample_renders_on_repeated_spaced_plays (test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays) ... ok
test_replay_after_mute_and_resume (test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume) ... ok

----------------------------------------------------------------------
Ran 2 tests in 6.347s

OK
