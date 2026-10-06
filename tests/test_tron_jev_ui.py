import curses
import io
import json
import os
import tempfile
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, patch

from neon_tetris.jev import JevClient, Worker
from tests.test_tron_engine import tick
from tests.tron_jev_fixture import FixtureClient
from tink_tron.__main__ import main
from tink_tron.engine import Game, STEP
from tink_tron.jev_match import JevPilot, TronClient
from tink_tron.jev_ui import _run_loop, handle_jev_key, hold_banner, run_jev
from tink_tron.ui import Renderer

UP = (0, -1)
REAL_SLEEP = time.sleep  # the module's `time` is the global one, so patching it must not call itself


def rig(**fixture):
    client = FixtureClient(**fixture)
    pilot = JevPilot(Worker(TronClient(client)))
    game = Game(1, opponent=pilot)
    return client, pilot, game


def settle(pilot, game):
    deadline = time.monotonic() + 3
    while pilot.worker.busy and time.monotonic() < deadline:
        pilot.collect(game)
        time.sleep(0.002)
    pilot.collect(game)


def frame(game, pilot, rows=30, cols=80):
    screen = Mock()
    screen.getmaxyx.return_value = rows, cols
    title, hint = hold_banner(pilot, game)
    Renderer(screen, True).draw(game, False, 'key sound muted [M]',
                                (pilot.status(game), pilot.cost.display(pilot.worker.busy), title, hint))
    return [c.args for c in screen.addnstr.call_args_list]


class TronJevUITests(unittest.TestCase):
    def test_screen_names_jev_shows_status_and_cost_and_stays_in_bounds(self):
        for rows, cols in ((30, 80), (35, 100)):
            client, pilot, game = rig()
            pilot.maybe_request(game); settle(pilot, game)
            calls = frame(game, pilot, rows, cols)
            for y, x, text, width, attr in calls:
                self.assertTrue(text.isascii())
                self.assertTrue(0 <= y < rows and 0 <= x and x + len(text) <= cols, (y, x, text))
            texts = [c[2] for c in calls]
            self.assertTrue(any('JEV' in t for t in texts))
            self.assertTrue(any('Jev following a route' in t and 'Est. $0.0000042' in t for t in texts), texts[:6])
            self.assertFalse(any('MACHINE' in t for t in texts))
            self.assertNotIn('WAITING FOR JEV', texts)

    def test_waiting_and_error_overlays_with_the_right_controls(self):
        client, pilot, game = rig(fail=(1,))
        texts = [c[2] for c in frame(game, pilot)]
        self.assertIn('WAITING FOR JEV', texts)
        self.assertTrue(any('Waiting for Jev' in t for t in texts))
        pilot.maybe_request(game); settle(pilot, game)
        texts = [c[2] for c in frame(game, pilot)]
        self.assertIn('JEV ERROR', texts)
        self.assertIn('Enter retry   R restart   Q quit', texts)
        self.assertTrue(any('Jev request failed or timed out.' in t for t in texts))
        self.assertNotIn('M mute   Q quit   Ctrl-C exit', texts)

    def test_enter_retries_only_an_error_and_turns_wait_for_jev(self):
        client, pilot, game = rig(fail=(1,))
        audio = Mock()
        handle_jev_key(game, pilot, ord('w'), audio)
        self.assertEqual(game.pending, [None, None])  # held: no turn queued
        handle_jev_key(game, pilot, 10, audio)
        self.assertEqual(pilot.error, '')
        pilot.maybe_request(game); settle(pilot, game)
        self.assertTrue(pilot.error)
        handle_jev_key(game, pilot, 10, audio)
        self.assertEqual(pilot.error, '')
        pilot.maybe_request(game); settle(pilot, game)
        handle_jev_key(game, pilot, ord('w'), audio)
        self.assertEqual(game.pending[0], UP)

    def test_restart_resets_match_and_pilot_and_quit_returns_false(self):
        client, pilot, game = rig()
        pilot.maybe_request(game); settle(pilot, game)
        game.scores = [1, 1]
        epoch = pilot.epoch
        audio = Mock()
        self.assertTrue(handle_jev_key(game, pilot, ord('R'), audio))
        self.assertEqual((game.scores, pilot.epoch, len(pilot.plan)), ([0, 0], epoch + 1, 0))
        audio.play.assert_called_with('switch')
        for key in (ord('q'), 3):
            self.assertFalse(handle_jev_key(game, pilot, key, audio))

    def test_the_loop_waits_for_jev_then_plays_and_asks_for_more(self):
        client, pilot, game = rig()
        screen = Mock(); screen.getmaxyx.return_value = (30, 80)
        screen.getch.side_effect = [-1] * 40 + [ord('q')]
        clock = iter(i * 0.05 for i in range(10000))
        deadline = time.monotonic() + 3
        with patch('tink_tron.jev_ui.time.monotonic', side_effect=lambda: next(clock)), patch('tink_tron.jev_ui.time.sleep',
                                                                                                  side_effect=lambda s: REAL_SLEEP(0.003)):
            _run_loop(screen, Mock(), game, pilot, Mock())
        self.assertGreater(len(client.calls), 1)  # the opening route, then an early request while it ran
        self.assertGreater(len(game.trails), 2)  # play began only after the route arrived

    def test_run_closes_audio_and_reports_cost_on_every_exit(self):
        for error in (None, KeyboardInterrupt(), ValueError('render')):
            backend, screen = Mock(ready=True), Mock()
            with patch('curses.curs_set'), patch('curses.set_escdelay'), patch('tink_tron.jev_ui.Renderer'), \
                 patch('tink_tron.jev_ui._run_loop', side_effect=error), patch('arcade_common.audio._make_backend', return_value=backend):
                if error:
                    with self.assertRaises(type(error)):
                        run_jev(screen, 1, True, False, FixtureClient())
                else:
                    warning, summary = run_jev(screen, 1, True, False, FixtureClient())
                    self.assertIn('Tron vs Jev: unfinished, 0-0. Est. $0.00000000', summary)
            backend.close.assert_called_once()

    def test_the_key_never_reaches_the_screen_or_the_trace(self):
        client = JevClient('SECRET-KEY-123')
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'trace.jsonl')
            screen = Mock(); screen.getmaxyx.return_value = (30, 80)
            screen.getch.side_effect = [-1] * 30 + [ord('q')]
            drawn = []
            def fake_draw(self_, game, small, sound, jev=None):
                drawn.append(repr(jev))
            with patch.dict(os.environ, {'TINK_TRON_TRACE': path}), patch('curses.curs_set'), patch('curses.set_escdelay'), \
                 patch('http.client.HTTPSConnection', side_effect=OSError('SECRET-KEY-123 refused')), \
                 patch('tink_tron.jev_ui.Renderer.draw', fake_draw), patch('tink_tron.jev_ui.time.sleep', side_effect=lambda s: REAL_SLEEP(0.003)), \
                 patch('arcade_common.audio._make_backend', return_value=Mock(ready=True)):
                warning, summary = run_jev(screen, 1, True, True, client)
            with open(path) as trace:
                text = trace.read()
        self.assertTrue('Jev worker failed' in text or 'Jev request failed' in text, 'the error should reach the trace')
        self.assertNotIn('SECRET', text + summary + ' '.join(drawn))

    def test_cli_needs_the_key_refuses_mixed_modes_and_prints_the_cost(self):
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
             patch.dict(os.environ, {}, clear=False), patch('curses.wrapper') as wrapper, redirect_stderr(io.StringIO()) as err:
            os.environ.pop('TYPESAFE_API_KEY', None)
            self.assertEqual(main(['--versus-jev']), 1)
            wrapper.assert_not_called()
        self.assertIn('TYPESAFE_API_KEY', err.getvalue())
        for extra in (['--two-player'], ['--level', 'hard']):
            with redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit) as exit_:
                main(['--versus-jev', *extra])
            self.assertEqual(exit_.exception.code, 2)
            self.assertIn('cannot be combined', err.getvalue())
        fixture = FixtureClient()
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
             patch.dict(os.environ, {'TYPESAFE_API_KEY': 'k'}), patch('tink_tron.__main__.make_client', return_value=fixture), \
             patch('curses.wrapper', return_value=('', 'Tron vs Jev: unfinished, 0-0. Est. $0.00000000')) as wrapper, \
             patch('builtins.print') as printed:
            self.assertEqual(main(['--versus-jev', '--seed', '3', '--no-color', '--no-sound']), 0)
        args = wrapper.call_args.args
        self.assertEqual(args[1:], (3, True, True, fixture))
        printed.assert_called_with('Tron vs Jev: unfinished, 0-0. Est. $0.00000000')

    def test_help_lists_the_flag_and_warns_about_billing(self):
        with redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit):
            main(['--help'])
        self.assertIn('--versus-jev', out.getvalue())
        self.assertIn('billed', out.getvalue())

    def test_solo_and_two_player_never_touch_jev(self):
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
             patch('tink_tron.__main__.make_client') as maker, patch('curses.wrapper', return_value='') as wrapper:
            self.assertEqual(main(['--no-sound']), 0)
            self.assertEqual(main(['--two-player']), 0)
        maker.assert_not_called()
        self.assertEqual(wrapper.call_args_list[0].args[3], 'normal')


if __name__ == '__main__':
    unittest.main()
