"""Regression baseline for checker behavior; no game implementation is replaced.

Queue fixtures come from the real Snake loop with a controlled frame clock.
The checker consumes the resulting complete trace, including consumed turns.
CLI checks run disposable copies so the unfixed scripts cannot overwrite evidence.
"""
import curses
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

from tink_snake.engine import Game
from tink_snake.ui import _run_loop

ROOT = Path(__file__).resolve().parents[1]


def checker(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'check_{name}_terminal.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def queue_trace(keys, delayed=True):
    screen = Mock()
    screen.getmaxyx.return_value = (30, 80)
    screen.getch.side_effect = [-1, *keys, -1, -1, -1, ord('q')]
    audio = Mock(status='key sound unavailable')
    trace = io.StringIO()
    # Initial frame, input frame, and two more frames. A delayed input frame
    # consumes UP before the trace write; an early frame retains both turns.
    input_time = .18 if delayed else .02
    clock = [0, 0, 0, input_time, input_time, .36, .36, .54, .54, .72]
    with patch('tink_snake.ui.time.monotonic', side_effect=clock), patch('tink_snake.ui.time.sleep'):
        _run_loop(screen, Mock(), Game(1), audio, trace)
    return [json.loads(line) for line in trace.getvalue().splitlines()]


class QueueComplete(Exception):
    pass


class SnakeQueueCheckerTests(unittest.TestCase):
    def run_queue(self, states):
        module = checker('snake')

        class Replay(module.Terminal):
            def __init__(self, directory, *args, **kwargs):
                self.observed = states[:1]
                self.notes = []
                self.proc = Mock()
                self.proc.poll.return_value = None

            def states(self):
                return self.observed

            def pump(self):
                pass

            def expect(self, value):
                pass

            def send(self, data, predicate, label):
                if data == b'\x1bOA\x1bOD':
                    start = len(self.states())
                    self.observed = states
                    return self.wait(predicate, label, start)
                if data == b'S':
                    raise QueueComplete()
                raise AssertionError(f'Unexpected input before queue check completed: {data!r}')

            def transcript(self):
                return '\n'.join(self.notes)

            def close(self):
                pass

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(module, 'Terminal', Replay), patch.object(module, 'OUTPUT', Path(directory) / 'trace.txt'), \
                    patch.object(sys, 'argv', ['check_snake_terminal.py']), \
                    patch.object(module.time, 'monotonic', side_effect=iter(range(1000))):
                module.main()

    def test_early_input_is_accepted(self):
        states = queue_trace([curses.KEY_UP, curses.KEY_LEFT], delayed=False)
        self.assertTrue(any(s['turns'] == [[0, -1], [-1, 0]] for s in states))
        with self.assertRaises(QueueComplete):
            self.run_queue(states)

    def test_consumed_first_turn_is_accepted(self):
        states = queue_trace([curses.KEY_UP, curses.KEY_LEFT])
        self.assertFalse(any(s['turns'] == [[0, -1], [-1, 0]] for s in states))
        self.assertEqual([s['snake'][0] for s in states[:3]], [[10, 10], [10, 9], [9, 9]])
        self.assertEqual([s['direction'] for s in states[1:3]], [[0, -1], [-1, 0]])
        with self.assertRaises(QueueComplete):
            self.run_queue(states)

    def test_missing_or_wrong_order_turns_are_rejected(self):
        for keys in ([curses.KEY_UP], [curses.KEY_LEFT, curses.KEY_UP], []):
            with self.subTest(keys=keys), self.assertRaises(AssertionError):
                self.run_queue(queue_trace(keys))


class TranscriptDestinationTests(unittest.TestCase):
    def test_explicit_external_destination_preserves_existing_evidence(self):
        for game in ('snake', 'breakout'):
            with self.subTest(game=game), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / 'checkout'
                for package in ('scripts', 'tink_snake', 'tink_breakout', 'neon_tetris', 'arcade_common'):
                    shutil.copytree(ROOT / package, root / package, ignore=shutil.ignore_patterns('__pycache__'))
                old = root / f'runs/{game}/04-test/output/terminal-transcript.txt'
                old.parent.mkdir(parents=True)
                old.write_text('Retained evidence sentinel\n')
                destination = Path(directory) / 'review output' / f'{game}.txt'
                result = subprocess.run([sys.executable, '-B', str(root / f'scripts/check_{game}_terminal.py'),
                                         '--output', str(destination)], cwd=directory,
                                        capture_output=True, text=True, timeout=45)
                self.assertEqual(old.read_text(), 'Retained evidence sentinel\n', result.stdout + result.stderr)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(destination.is_file(), result.stdout + result.stderr)
                self.assertIn('Sanitized terminal output:', destination.read_text())
                self.assertIn('original terminal settings restored', destination.read_text())


if __name__ == '__main__':
    unittest.main()
