import contextlib
import curses
import io
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

from arcade_common.theme import PaperRenderer
from tink_stacker.ui import Controller, Renderer, run, _run_loop, MAX_KEYS
from tink_stacker.__main__ import main


class StackerUITests(unittest.TestCase):
    def frame(self, c, keys='', dt=.01, rows=30, columns=80, audio=None):
        return c.frame(c.last + dt, rows, columns, [ord(k) for k in keys], audio)

    def test_lock_uses_displayed_position_once_per_input_batch(self):
        c = Controller(0)
        self.frame(c, dt=.24)
        self.assertEqual(c.game.x, 1)
        self.frame(c, ' \r\n ' * 10, dt=.24)
        self.assertEqual(c.game.rows, [(1, 2, 3)])
        self.assertEqual(c.game.x, 4)
        self.assertTrue(c.discard_input)
        self.frame(c, dt=.228)
        self.assertEqual(c.game.x, 3)
        for key in ('\r', '\n', ' '):
            c = Controller(0); self.frame(c, key)
            self.assertEqual(len(c.game.rows), 1)

    def test_pause_and_small_terminal_freeze_without_catchup(self):
        c = Controller(0)
        self.frame(c, dt=.12)
        self.frame(c, 'p ')
        before = c.game.snapshot()
        self.frame(c, ' ', dt=10)
        self.assertEqual(c.game.snapshot(), before)
        self.frame(c, 'p ', dt=10)
        self.assertEqual(c.game.snapshot(), before)
        self.frame(c, dt=.12)
        self.assertEqual(c.game.x, 1)
        self.frame(c, rows=12, columns=40)
        before = c.game.snapshot()
        self.frame(c, ' rp ', dt=10, rows=12, columns=40)
        self.assertEqual(c.game.snapshot(), before)
        self.frame(c, ' ', dt=10)
        self.assertEqual(c.game.snapshot(), before)

    def test_resize_recovery_preserves_prior_pause(self):
        for paused in (False, True):
            c = Controller(0)
            if paused: self.frame(c, 'P')
            before = c.game.snapshot()
            self.frame(c, rows=12, columns=40)
            self.frame(c, 'Pr ', dt=10, rows=12, columns=40)
            self.frame(c, 'r ', dt=10, rows=35, columns=100)
            self.assertEqual(c.paused, paused)
            self.assertEqual(c.game.snapshot(), before)

    def test_end_states_ignore_placement_and_restart_is_available(self):
        for state in ('won', 'lost'):
            c = Controller(0); c.game.state = state
            before = c.game.snapshot()
            self.frame(c, ' P ')
            self.assertEqual(c.game.snapshot(), before)
            self.frame(c, 'R ')
            self.assertEqual(c.game.snapshot(), Controller(0).game.snapshot())
            self.assertFalse(c.paused)
        c = Controller(0); self.frame(c, 'p'); self.frame(c, 'r')
        self.assertFalse(c.paused)

    def test_bounded_input_does_not_starve_update_or_render(self):
        c = Controller(0)
        screen = Mock(); screen.getmaxyx.return_value = (30, 80)
        screen.getch.side_effect = [ord('x')] * MAX_KEYS + [ord('q'), -1]
        renderer, audio = Mock(), Mock(status='key sound off')
        with patch('tink_stacker.ui.time.monotonic', side_effect=[.24, .24, .48, .48]), patch('tink_stacker.ui.time.sleep'):
            _run_loop(screen, renderer, c, audio)
        self.assertEqual(renderer.draw.call_count, 2)
        self.assertEqual(audio.tick.call_count, 2)
        self.assertEqual(c.game.x, 1)

    def test_small_terminal_keeps_mute_and_quit_available(self):
        for key in 'qQ' + chr(3):
            c = Controller(0); a = Mock()
            self.frame(c, 'm' + key, rows=12, columns=40, audio=a)
            self.assertTrue(c.quit); a.toggle.assert_called_once()

    def test_palette_states_clipping_and_monochrome(self):
        self.assertTrue(issubclass(Renderer, PaperRenderer))
        for colors, pairs in ((0, 0), (8, 4), (8, 5), (256, 5)):
            screen = Mock(); screen.getmaxyx.return_value = (30, 80)
            with patch('curses.has_colors', return_value=bool(colors)), patch('curses.start_color'), patch('curses.init_pair') as init, patch('curses.color_pair', side_effect=lambda n: n << 8), patch('curses.COLORS', colors, create=True), patch('curses.COLOR_PAIRS', pairs, create=True):
                renderer = Renderer(screen)
                self.assertEqual(init.call_count, 4 if colors >= 8 and pairs >= 5 else 0)
                renderer.draw(Controller(0))
        for rows, columns in ((30, 80), (35, 100)):
            screen = Mock(); screen.getmaxyx.return_value = (rows, columns)
            with patch('curses.has_colors') as color:
                renderer = Renderer(screen, no_color=True); color.assert_not_called()
            c = Controller(0); c.game.lock_row()
            for state, label in (('playing', 'Aim for the top'), ('won', 'YOU WIN'), ('lost', 'GAME OVER')):
                c.game.state = state; screen.reset_mock(); renderer.draw(c)
                text = ' '.join(call.args[2] for call in screen.addnstr.call_args_list)
                for expected in ('paper stacker', 'PLAY / PAPER', 'HEIGHT', 'BLOCKS', '[]', 'Space / Enter', 'Q quit', label):
                    self.assertIn(expected, text)
            c.paused = True; screen.reset_mock(); renderer.draw(c)
            self.assertIn('PAUSED', ' '.join(call.args[2] for call in screen.addnstr.call_args_list))
            screen.reset_mock(); renderer.text(rows - 1, columns - 1, 'x'); screen.addnstr.assert_not_called()
            screen.addnstr.side_effect = curses.error
            renderer.draw(c)

    def test_cli_flags_nonterminal_and_warning(self):
        result = subprocess.run([sys.executable, '-B', '-m', 'tink_stacker', '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        for flag in ('--no-color', '--no-sound'): self.assertIn(flag, result.stdout)
        result = subprocess.run([sys.executable, '-B', '-m', 'tink_stacker'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1); self.assertIn('interactive terminal', result.stderr)
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), patch('curses.wrapper', return_value='no output device') as wrapper, contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main(['--no-color', '--no-sound']), 0)
            wrapper.assert_called_once_with(run, True, True)
            self.assertIn('no output device', err.getvalue())
