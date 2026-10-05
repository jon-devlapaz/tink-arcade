import curses
import io
import itertools
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from tink_crossing.engine import BAYS, Game, HOME, START
from tink_crossing.ui import HOPS, Renderer, _run_loop, cell, handle_key
from tink_crossing.__main__ import main

ROOT = Path(__file__).resolve().parents[1]


def texts(screen):
    return [c.args[2] for c in screen.addnstr.call_args_list]


class CrossingUITests(unittest.TestCase):
    def test_hop_bindings_both_cases(self):
        expected = {(-1, 0): 'wW', (1, 0): 'sS', (0, -1): 'aA', (0, 1): 'dD'}
        for move, letters in expected.items():
            keys = [ord(k) for k in letters]
            keys.append({(-1, 0): curses.KEY_UP, (1, 0): curses.KEY_DOWN,
                         (0, -1): curses.KEY_LEFT, (0, 1): curses.KEY_RIGHT}[move])
            for key in keys:
                self.assertEqual(HOPS[key], move)

    def test_actions_and_cues(self):
        g, a = Game(), Mock()
        self.assertTrue(handle_key(g, curses.KEY_LEFT, a))
        a.play.assert_called_with('move')
        for key in 'pP':
            a.reset_mock()
            handle_key(g, ord(key), a)
            a.stop.assert_called()
            a.play.assert_called_with('switch')
        g.col = 3
        handle_key(g, ord('R'), a)
        self.assertEqual(g.snapshot(), Game().snapshot())
        for key in 'mM':
            handle_key(g, ord(key), a)
        self.assertEqual(a.toggle.call_count, 2)
        for key in (ord('q'), ord('Q'), 3):
            self.assertFalse(handle_key(g, key, a))
        g.state = 'over'
        a.reset_mock()
        handle_key(g, ord('p'), a)
        handle_key(g, ord('w'), a)
        a.play.assert_not_called()

    def test_cells(self):
        g = Game()
        self.assertEqual(cell(g, HOME, 0), ('^', 'rule'))
        self.assertEqual(cell(g, HOME, BAYS[0][0]), (' ', 'ink'))
        g.bays[0] = True
        self.assertEqual(cell(g, HOME, BAYS[0][0]), ('*', 'accent'))
        self.assertEqual(cell(g, START, 0), ('_', 'rule'))
        self.assertIn(cell(g, 1, 0)[0], '=~')
        self.assertIn(cell(g, 9, 0)[0], '#.')

    def test_layout_states_sizes_bounds(self):
        labels = {'playing': 'HOP', 'paused': 'PAUSED / P resume',
                  'won': 'YOU WIN / R restart / Q quit', 'over': 'GAME OVER / R restart / Q quit'}
        for rows, cols in ((30, 80), (35, 100)):
            for state, label in labels.items():
                g = Game()
                g.state = 'playing' if state == 'paused' else state
                g.paused = state == 'paused'
                s = Mock()
                s.getmaxyx.return_value = (rows, cols)
                Renderer(s, True).draw(g, False, 'key sound on [M]')
                for y, x, text, width, attr in (c.args for c in s.addnstr.call_args_list):
                    self.assertTrue(text.isascii())
                    self.assertTrue(0 <= y < rows and 0 <= x and x + len(text) <= cols)
                t = texts(s)
                for want in (label, 'key sound on [M]', '. socratink / paper crossing',
                             ' PLAY / PAPER ', 'SCORE  0', 'LIVES  3', 'LEVEL  1 / 3', 'BAYS   0 / 5'):
                    self.assertIn(want, t)
                self.assertEqual(t.count('@'), 0 if state == 'won' else 1)

    def test_small_terminal(self):
        s = Mock()
        s.getmaxyx.return_value = (12, 40)
        Renderer(s, True).draw(Game(), True, 'key sound off')
        self.assertIn('Resize terminal to at least 80 x 30.', texts(s))

    def run_frames(self, keys, sizes):
        """Drive _run_loop with 5 s between frames; keys per frame, then Q."""
        g, audio, screen = Game(), Mock(status='', warning=None), Mock()
        seq = iter([k for frame in keys for k in ((frame,) if frame == -1 else (frame, -1))] + [ord("q")])
        screen.getch.side_effect = lambda: next(seq)
        screen.getmaxyx.side_effect = iter(sizes + [sizes[-1]] * 10)
        with patch('time.monotonic', side_effect=itertools.count(0, 5)), patch('time.sleep'):
            _run_loop(screen, Mock(), g, audio)
        return g

    def test_loop_caps_delay_and_discards_transition_and_resize_time(self):
        self.assertEqual(self.run_frames([-1, -1], [(30, 80)]).counters[3], 24)
        self.assertEqual(self.run_frames([ord('p')], [(30, 80)]).counters, Game().counters)
        g = self.run_frames([-1, -1], [(12, 40), (30, 80)])
        self.assertEqual(g.counters, Game().counters)

    def test_cli(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertRaises(SystemExit) as done:
            main(['--help'])
        self.assertEqual(done.exception.code, 0)
        self.assertIn('--no-sound', out.getvalue())
        err = io.StringIO()
        with patch('sys.stdin.isatty', return_value=False), redirect_stderr(err):
            self.assertEqual(main([]), 1)
        self.assertIn('interactive terminal', err.getvalue())
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
                patch('curses.wrapper', return_value=None) as wrapper:
            self.assertEqual(main(['--no-color', '--no-sound']), 0)
            self.assertEqual(wrapper.call_args.args[1:], (True, True))

    def test_menu_entry(self):
        games = json.loads((ROOT / 'arcade_menu/games.json').read_text())
        entry = next(g for g in games if g['module'] == 'tink_crossing')
        self.assertEqual((entry['title'], entry['path']), ('Crossing', '.'))


if __name__ == '__main__':
    unittest.main()
