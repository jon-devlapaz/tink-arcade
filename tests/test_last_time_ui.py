import contextlib
import curses
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

from arcade_common.theme import PaperRenderer
from arcade_menu.registry import load_games
from tink_last_time.__main__ import main
from tink_last_time.ui import ARROWS, Controller, MAX_KEYS, Renderer, _run_loop, run


class LastTimeUI(unittest.TestCase):
    def frame(self, controller, keys=(), dt=.1, rows=30, columns=80, audio=None):
        return controller.frame(controller.last + dt, rows, columns, keys, audio)

    def test_arrows_and_one_life(self):
        for key, delta in ((curses.KEY_UP, (0, -1)), (curses.KEY_DOWN, (0, 1)),
                           (curses.KEY_LEFT, (-1, 0)), (curses.KEY_RIGHT, (1, 0))):
            c = Controller(0, 7)
            start = c.game.player
            self.frame(c, [key])
            self.assertEqual(c.game.player, (start[0] + delta[0], start[1] + delta[1]))
            c.game.paths = [(c.game.player,) * 151]
            self.frame(c)
            self.assertEqual(c.game.state, 'lost')
            before = c.game.snapshot()
            self.frame(c, [key, ord('p')])
            self.assertEqual(c.game.snapshot(), before)
            self.frame(c, [ord('R')])
            self.assertEqual(c.game.state, 'playing')
            self.assertEqual((c.game.score, c.game.round), (0, 1))

    def test_pause_resize_and_recovery_freeze_all_clocks(self):
        for paused in (False, True):
            c = Controller(0, 7)
            self.frame(c, [curses.KEY_RIGHT], dt=.05)
            if paused:
                self.frame(c, [ord('p')])
            before = c.game.snapshot()
            self.frame(c, rows=12, columns=40)
            self.frame(c, [ord('r'), ord('p'), curses.KEY_DOWN], dt=20, rows=12, columns=40)
            self.assertEqual(c.game.snapshot(), before)
            self.frame(c, [curses.KEY_LEFT, ord('r')], dt=20, rows=35, columns=100)
            self.assertEqual(c.game.snapshot(), before)
            self.assertEqual(c.paused, paused)
            self.assertTrue(c.discard_input)
            if paused:
                self.frame(c, [ord('P')], dt=20)
                self.assertEqual(c.game.snapshot(), before)
            self.frame(c, dt=.05)
            self.assertEqual(c.game.player, (16, 9))
        c = Controller(0, 7)
        self.frame(c, [ord('p')])
        before = c.game.snapshot()
        self.frame(c, [curses.KEY_DOWN], dt=40)
        self.assertEqual(c.game.snapshot(), before)

    def test_audio_lifecycle_cues_and_restart_preserves_best(self):
        c, audio = Controller(0, 7), Mock()
        c.game.sparks = {(16, 9), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4)}
        self.frame(c, [curses.KEY_RIGHT], audio=audio)
        audio.play.assert_called_once_with('clear')
        audio.reset_mock()
        c.game.paths = [((17, 9),) * 151]
        self.frame(c, audio=audio)
        audio.play.assert_called_once_with('over')
        self.frame(c, [ord('M'), ord('R')], audio=audio)
        audio.toggle.assert_called_once()
        self.assertEqual((c.best, c.game.score), (1, 0))
        self.assertEqual(audio.tick.call_count, 2)
        audio.reset_mock()
        self.frame(c, [ord('p')], audio=audio)
        self.frame(c, audio=audio)
        audio.play.assert_called_once_with('switch')
        self.frame(c, [ord('m'), ord('q')], rows=12, columns=40, audio=audio)
        audio.toggle.assert_called_once()
        self.assertTrue(c.quit)
        self.assertGreaterEqual(audio.stop.call_count, 2)
        for key in (ord('q'), ord('Q'), 3):
            c = Controller(0)
            self.frame(c, [key], rows=1, columns=1)
            self.assertTrue(c.quit)

    def test_dark_arena_symbols_and_states_in_all_palette_modes(self):
        self.assertTrue(issubclass(Renderer, PaperRenderer))
        for rows, columns in ((30, 80), (35, 100)):
            for colors, pairs, no_color in ((256, 256, False), (8, 8, False), (8, 4, False), (0, 0, True)):
                screen = Mock()
                screen.getmaxyx.return_value = (rows, columns)
                with patch('curses.has_colors', return_value=bool(colors)), patch('curses.start_color'), patch('curses.init_pair') as init, patch('curses.color_pair', side_effect=lambda n: n << 8), patch('curses.COLORS', colors, create=True), patch('curses.COLOR_PAIRS', pairs, create=True):
                    renderer = Renderer(screen, no_color)
                self.assertEqual(init.call_count, 4 if colors and pairs >= 5 and not no_color else 0)
                c = Controller(0, 7)
                c.game.paths = [((0, 0),) * 151]
                for paused, state, label in ((False, 'playing', '<> you'), (True, 'playing', 'PAUSED'), (False, 'lost', 'GAME OVER')):
                    c.paused, c.game.state = paused, state
                    screen.reset_mock()
                    renderer.draw(c)
                    calls = screen.addnstr.call_args_list
                    text = ' '.join(call.args[2] for call in calls)
                    for expected in ('paper last time', 'PLAY / PAPER', 'SCORE', 'ROUND', 'GHOSTS', 'NEXT ROUND', '<>', '* ', 'xx', 'Arrows', 'Q / Ctrl-C', label):
                        self.assertIn(expected, text)
                    field = [call for call in calls if call.args[2] == ' ' * 60]
                    self.assertEqual(len(field), 18)
                    self.assertTrue(all(call.args[4] & curses.A_REVERSE for call in field))
                screen.reset_mock()
                renderer.text(rows - 1, columns - 1, 'x')
                screen.addnstr.assert_not_called()
                screen.addnstr.side_effect = curses.error
                renderer.draw(c)
        screen = Mock(); screen.getmaxyx.return_value = (12, 40)
        c = Controller(0); self.frame(c, rows=12, columns=40)
        Renderer(screen, True).draw(c)
        self.assertIn('Resize terminal', ' '.join(call.args[2] for call in screen.addnstr.call_args_list))

    def test_bounded_input_and_stall_discard(self):
        c = Controller(0, 7)
        screen = Mock(); screen.getmaxyx.return_value = (30, 80)
        screen.getch.side_effect = [curses.KEY_RIGHT] * MAX_KEYS + [ord('q'), -1]
        renderer, audio = Mock(), Mock(status='key sound off')
        with patch('tink_last_time.ui.time.monotonic', side_effect=[.1, .1, .2, .2]), patch('tink_last_time.ui.time.sleep'):
            _run_loop(screen, renderer, c, audio)
        self.assertEqual(renderer.draw.call_count, 2)
        self.assertEqual(audio.tick.call_count, 2)
        self.assertEqual(c.game.tick, 1)
        before = c.game.snapshot()
        self.frame(c, dt=10)
        self.assertEqual(c.game.snapshot(), before)

    def test_registry_and_cli(self):
        games = load_games()
        self.assertEqual(games[-1].title, 'Last Time')
        self.assertEqual(games[-1].module, 'tink_last_time')
        self.assertEqual(games[-2].title, 'Stacker')
        self.assertFalse(games[-1].requires_env)
        for name in ('engine.py', 'ui.py', '__main__.py'):
            self.assertTrue(Path('tink_last_time', name).is_file())
        result = subprocess.run([sys.executable, '-B', '-m', 'tink_last_time', '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        for flag in ('--seed', '--no-color', '--no-sound'):
            self.assertIn(flag, result.stdout)
        result = subprocess.run([sys.executable, '-B', '-m', 'tink_last_time'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('interactive terminal', result.stderr)
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), patch('curses.wrapper', return_value='no output device') as wrapper, contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main(['--no-color', '--no-sound', '--seed', '7']), 0)
            wrapper.assert_called_once_with(run, True, True, 7)
            self.assertIn('no output device', err.getvalue())
        with patch('tink_last_time.ui.KeyboardAudio') as audio, patch('tink_last_time.ui.Renderer'), patch('tink_last_time.ui._run_loop', side_effect=RuntimeError('test failure')), patch('curses.curs_set'), patch('curses.set_escdelay'):
            with self.assertRaisesRegex(RuntimeError, 'test failure'):
                run(Mock(), True, True, 7)
            audio.assert_called_once_with(enabled=False)
            audio.return_value.__exit__.assert_called_once()
