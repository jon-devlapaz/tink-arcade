import contextlib
import curses
import io
import json
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch
from tink_invaders.engine import Enemy, Shot, STEP, SHIP_Y
from tink_invaders.ui import Controller, Renderer, run, _run_loop, MAX_KEYS
from tink_invaders.__main__ import main
from arcade_common.audio import KeyboardAudio


class UITests(unittest.TestCase):
    def frame(self, c, keys=(), rows=30, cols=80, dt=STEP, audio=None):
        return c.frame(c.last + dt, rows, cols, [ord(k) if isinstance(k, str) else k for k in keys], audio)

    def playing(self):
        c = Controller(0, 7)
        self.frame(c, ' ')
        return c

    def test_bindings_and_start_does_not_fire(self):
        for key, offset in ((curses.KEY_LEFT, -1), ('a', -1), ('A', -1),
                            (curses.KEY_RIGHT, 1), ('d', 1), ('D', 1)):
            c = self.playing()
            self.assertIsNone(c.game.player_shot)
            self.frame(c, [key]); self.assertEqual(c.game.ship, 30 + offset)
        for key in 'qQ' + chr(3):
            c = Controller(0); self.frame(c, key); self.assertTrue(c.quit)
        for key in 'mM':
            audio = Mock(); self.frame(Controller(0), key, audio=audio)
            audio.toggle.assert_called_once()

    def test_repeated_space_cannot_freeze_clocks(self):
        c = self.playing()
        for _ in range(50):
            self.frame(c, ' ' * 32)
        self.assertGreater(c.game.enemies[0].x, 10)
        self.assertGreater(c.game.attack_timer, .7)
        self.assertTrue(c.game.player_shot is None or c.game.player_shot.y < SHIP_Y - 1)

    def test_pause_freezes_every_clock_and_suppresses_queued_input(self):
        for pause, resume in (('p', 'P'), ('P', 'p')):
            c = self.playing(); self.frame(c, ' ')
            self.frame(c, pause + ' ad  ')
            before = c.game.snapshot()
            for _ in range(20): self.frame(c, ' ad ', dt=1)
            self.assertEqual(c.game.snapshot(), before)
            result = self.frame(c, resume + 'd ', dt=100)
            self.assertEqual(c.game.snapshot(), before)
            self.assertEqual(result['advanced'], 0)
            self.frame(c)
            self.assertNotEqual(c.game.snapshot(), before)

    def test_resize_freezes_and_preserves_pause(self):
        for paused in (False, True):
            c = self.playing(); self.frame(c, ' ')
            if paused: self.frame(c, 'p')
            before = c.game.snapshot()
            audio = Mock()
            self.frame(c, 'rPd a ', 12, 40, dt=2, audio=audio)
            for _ in range(5): self.frame(c, 'rPd a ', 12, 40, dt=3)
            self.assertEqual(c.game.snapshot(), before)
            self.frame(c, 'M', 12, 40, audio=audio)
            audio.toggle.assert_called_once()
            result = self.frame(c, 'r d ', dt=100)
            self.assertEqual(c.game.snapshot(), before)
            self.assertEqual(result['advanced'], 0)
            self.assertEqual(c.paused, paused)
        c = Controller(0)
        self.frame(c, ' ', 12, 40)
        self.frame(c, ' ')
        self.assertEqual(c.game.state, 'ready')

    def test_frozen_idle_frames_do_not_discard_fresh_resume_keys(self):
        c = self.playing()
        self.frame(c, 'p')
        self.assertTrue(c.discard_input)
        self.frame(c)
        self.assertFalse(c.discard_input)
        self.frame(c, 'p')
        self.assertFalse(c.paused)
        self.assertTrue(c.discard_input)
        self.frame(c, rows=12, cols=40)
        self.assertTrue(c.discard_input)
        self.frame(c, rows=12, cols=40)
        self.assertFalse(c.discard_input)

    def test_restart_from_every_state_keeps_mute(self):
        for state in ('ready', 'playing', 'won', 'lost', 'paused'):
            for key in 'rR':
                c = self.playing()
                audio = KeyboardAudio(enabled=False)
                audio.muted = True
                c.game.state = 'playing' if state == 'paused' else state
                c.paused = state == 'paused'
                c.game.lives = 1; c.game.score = 50
                self.frame(c, key, audio=audio)
                self.assertEqual(c.game.snapshot(), Controller(0, 7).game.snapshot())
                self.assertFalse(c.paused); self.assertTrue(audio.muted)

    def test_end_states_ignore_gameplay(self):
        for state in ('won', 'lost'):
            c = self.playing(); c.game.state = state
            before = c.game.snapshot()
            self.frame(c, 'aAdD pP ')
            self.assertEqual(c.game.snapshot(), before)
            self.assertFalse(c.paused)

    def test_cue_mapping_and_blocked_actions(self):
        c = self.playing(); audio = Mock()
        self.frame(c, 'd', audio=audio); audio.play.assert_called_with('move')
        audio.reset_mock(); self.frame(c, 'd', audio=audio); audio.play.assert_not_called()
        self.frame(c, ' ', audio=audio); audio.play.assert_called_with('rotate')
        self.frame(c, 'p', audio=audio); audio.play.assert_called_with('switch')
        audio.reset_mock(); self.frame(c, 'd ', audio=audio); audio.play.assert_not_called()
        self.frame(c, 'p', audio=audio)
        c.game.enemy_shots = [Shot(c.game.ship, SHIP_Y - .01)]
        self.frame(c, audio=audio); audio.play.assert_called_with('over')
        self.frame(c, ' ', audio=audio)
        c.game.enemies = [Enemy(0, 0, 10, 5)]
        c.game.player_shot = Shot(10, 5.1)
        self.frame(c, audio=audio); audio.play.assert_called_with('clear')
        self.frame(c, 'r', audio=audio); audio.play.assert_called_with('switch')
        self.assertGreater(audio.tick.call_count, 0)

    def test_palette_and_safe_clipping(self):
        for colors, pairs in ((0, 0), (8, 1), (8, 5), (256, 5)):
            screen = Mock(); screen.getmaxyx.return_value = (30, 80)
            with patch('curses.has_colors', return_value=bool(colors)), patch('curses.start_color'), \
                    patch('curses.init_pair') as init, patch('curses.color_pair', side_effect=lambda n: n << 8), \
                    patch('curses.COLORS', colors, create=True), patch('curses.COLOR_PAIRS', pairs, create=True):
                renderer = Renderer(screen)
                self.assertEqual(init.call_count, 4 if colors >= 8 and pairs >= 5 else 0)
                renderer.draw(Controller(0))
            renderer.text(-1, 0, 'off'); renderer.text(0, 80, 'off')
            screen.reset_mock(); renderer.text(29, 79, 'off'); screen.addnstr.assert_not_called()
            renderer.text(0, -2, 'hello'); screen.addnstr.assert_called_with(0, 0, 'llo', 80, 0)
            screen.addnstr.side_effect = curses.error
            renderer.text(0, 0, 'resize')
        with patch('curses.has_colors') as colors:
            Renderer(Mock(), no_color=True); colors.assert_not_called()

    def test_layout_contains_states_stats_and_distinct_marks(self):
        for rows, cols in ((30, 80), (35, 100)):
            screen = Mock(); screen.getmaxyx.return_value = (rows, cols)
            renderer = Renderer(screen, no_color=True)
            c = self.playing(); c.game.start_or_fire(); c.game.enemy_shots = [Shot(5, 7)]
            for state, label in (('ready', 'READY'), ('playing', 'Clear every'), ('won', 'YOU WIN'), ('lost', 'GAME OVER')):
                c.game.state = state; screen.reset_mock(); renderer.draw(c)
                text = ' '.join(call.args[2] for call in screen.addnstr.call_args_list)
                for value in (label, 'SCORE', 'LIVES', 'WAVE', '[W]', '/^\\', '^', 'v', 'Q quit'):
                    self.assertIn(value, text)
            c.paused = True; screen.reset_mock(); renderer.draw(c)
            self.assertIn('PAUSED', ' '.join(call.args[2] for call in screen.addnstr.call_args_list))

    def test_bounded_input_loop_draws_and_updates(self):
        c = self.playing(); screen = Mock(); screen.getmaxyx.return_value = (30, 80)
        screen.getch.side_effect = [ord(' ')] * MAX_KEYS + [ord('q'), -1]
        trace, renderer, audio = io.StringIO(), Mock(), Mock(status='off')
        with patch('tink_invaders.ui.time.monotonic', side_effect=[1, 1, 2, 2]), patch('tink_invaders.ui.time.sleep'), patch('curses.flushinp'):
            _run_loop(screen, renderer, c, audio, trace)
        self.assertEqual(renderer.draw.call_count, 2)
        self.assertGreater(json.loads(trace.getvalue().splitlines()[0])['attack_timer'], 0)

    def test_run_cleanup_normal_and_error_disabled_and_unavailable_audio(self):
        for fails in (False, True):
            for disabled in (False, True):
                screen = Mock()
                backend = Mock(); backend.ready = True
                with patch('curses.curs_set'), patch('curses.set_escdelay'), patch('tink_invaders.ui.Renderer'), \
                     patch('arcade_common.audio._make_backend', return_value=backend) as make, \
                     patch('tink_invaders.ui._run_loop', side_effect=RuntimeError('drawing failed') if fails else None):
                    if fails:
                        with self.assertRaises(RuntimeError): run(screen, no_sound=disabled)
                    else:
                        self.assertEqual(run(screen, no_sound=disabled), '')
                    if disabled: make.assert_not_called()
                    else: backend.close.assert_called_once()
        with patch('curses.curs_set'), patch('curses.set_escdelay'), patch('tink_invaders.ui.Renderer'), \
                patch('arcade_common.audio._make_backend', side_effect=OSError('no backend')), patch('tink_invaders.ui._run_loop'):
            self.assertEqual(run(Mock()), 'no backend')

    def test_cli_help_nonterminal_options_and_warning(self):
        result = subprocess.run([sys.executable, '-B', '-m', 'tink_invaders', '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        for flag in ('--seed', '--no-color', '--no-sound'): self.assertIn(flag, result.stdout)
        result = subprocess.run([sys.executable, '-B', '-m', 'tink_invaders'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1); self.assertIn('interactive terminal', result.stderr)
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
                patch('curses.wrapper', return_value='device missing') as wrapper, contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main(['--seed', '7', '--no-color', '--no-sound']), 0)
            wrapper.assert_called_once_with(run, 7, True, True)
            self.assertIn('device missing', err.getvalue())
