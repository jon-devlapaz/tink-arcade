"""Additional movement and CLI checks, with all output in temporary directories."""
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import test_terminal_checkers as baseline

ROOT = Path(__file__).resolve().parents[1]


class OrderedMovementTests(unittest.TestCase):
    def test_both_turns_in_wrong_order_are_rejected(self):
        states = baseline.queue_trace([])
        # Deliberately model a broken game: it moves left, then up. Both
        # directions occur, but accepting their unordered presence is wrong.
        states = deepcopy(states[:3])
        states[1]['snake'][0] = [9, 10]
        states[1]['direction'] = [-1, 0]
        states[2]['snake'][0] = [9, 9]
        states[2]['direction'] = [0, -1]
        with self.assertRaises(AssertionError):
            baseline.SnakeQueueCheckerTests().run_queue(states)

    def test_directions_without_movement_are_rejected(self):
        states = deepcopy(baseline.queue_trace([])[:3])
        for state in states:
            state['snake'][0] = [10, 10]
        states[1]['direction'] = [0, -1]
        states[2]['direction'] = [-1, 0]
        with self.assertRaises(AssertionError):
            baseline.SnakeQueueCheckerTests().run_queue(states)


class CheckerCompatibilityTests(unittest.TestCase):
    def copy_checkout(self, directory):
        root = Path(directory) / 'checkout'
        for package in ('scripts', 'tink_snake', 'tink_breakout', 'neon_tetris'):
            shutil.copytree(ROOT / package, root / package,
                            ignore=shutil.ignore_patterns('__pycache__'))
        return root

    def test_default_and_relative_destinations(self):
        for game in ('snake', 'breakout'):
            with self.subTest(game=game), tempfile.TemporaryDirectory() as directory:
                root = self.copy_checkout(directory)
                script = root / f'scripts/check_{game}_terminal.py'
                default = root / f'runs/{game}/04-test/output/terminal-transcript.txt'
                for args, destination in (([], default),
                        (['--output', 'relative output/transcript.txt'],
                         Path(directory) / 'relative output/transcript.txt')):
                    with self.subTest(args=args):
                        result = subprocess.run([sys.executable, '-B', str(script), *args],
                            cwd=directory, capture_output=True, text=True, timeout=45)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertIn(f'Transcript: {destination.resolve()}', result.stdout)
                        self.assertIn('original terminal settings restored', destination.read_text())
                        if not args:
                            retained = default.read_bytes()
                        else:
                            self.assertEqual(default.read_bytes(), retained)

    def test_help_and_argument_errors(self):
        for game in ('snake', 'breakout'):
            for args, code in ((['--help'], 0), (['--output'], 2), (['--unknown'], 2)):
                with self.subTest(game=game, args=args), tempfile.TemporaryDirectory() as directory:
                    result = subprocess.run([sys.executable, '-B',
                        str(ROOT / f'scripts/check_{game}_terminal.py'), *args],
                        cwd=directory, capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, code)
                    self.assertIn('--output', result.stdout + result.stderr)
                    self.assertEqual(list(Path(directory).iterdir()), [])

    def test_failure_writes_selected_transcript_and_exits_nonzero(self):
        for game in ('snake', 'breakout'):
            with self.subTest(game=game), tempfile.TemporaryDirectory() as directory:
                root = self.copy_checkout(directory)
                default = root / f'runs/{game}/04-test/output/terminal-transcript.txt'
                default.parent.mkdir(parents=True)
                default.write_text('Retained evidence\n')
                destination = Path(directory) / 'failure output' / 'trace.txt'
                # Run a real child game, then fail its first text assertion.
                # main's normal finally blocks must retain output and close it.
                script = root / f'scripts/check_{game}_terminal.py'
                code = """import runpy, sys
module = runpy.run_path(sys.argv[1])
def fail(self, value):
    raise AssertionError('injected terminal assertion')
module['Terminal'].expect = fail
sys.argv = [sys.argv[1], '--output', sys.argv[2]]
module['main']()
"""
                result = subprocess.run([sys.executable, '-B', '-c', code,
                    str(script), str(destination)], cwd=directory,
                    capture_output=True, text=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('injected terminal assertion', result.stderr)
                self.assertIn('Sanitized terminal output:', destination.read_text())
                self.assertEqual(default.read_text(), 'Retained evidence\n')


if __name__ == '__main__':
    unittest.main()
