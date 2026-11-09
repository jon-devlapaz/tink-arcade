
$ ["python3", "-B", "-m", "tink_breakout", "--help"]
usage: python3 -m tink_breakout [-h] [--no-color]

Offline terminal Breakout: clear three boards with three lives.

options:
  -h, --help  show this help message and exit
  --no-color  use monochrome rendering

Requires an 80 x 30 terminal. Arrows or A/D move; Space launches; P pauses; R
restarts; Q or Ctrl-C quits.

# checklist item rules-and-regressions
$ ["python3", "-B", "scripts/check_breakout_tests.py"]
Breakout engine: 9 tests
Breakout layouts: 2 tests
Breakout ui: 4 tests
..........................................................................ss.................
----------------------------------------------------------------------
Ran 93 tests in 0.504s

OK (skipped=2)
Legal full-clear replay: seed=20261004, steps=31475, boards=[(0, 16548, 360, 3), (1, 19078, 480, 3), (2, 31474, 760, 3)]
Total: 93; skips: 2
SKIP test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples
SKIP test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples

# checklist item real-terminal
$ ["python3", "-B", "scripts/check_breakout_terminal.py"]
PASS: real PTY input, launch, pause, resize, restart, quit and Ctrl-C; terminal restored; no child group remains.
Transcript: runs/breakout/04-test/output/terminal-transcript.txt
