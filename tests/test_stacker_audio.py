import unittest
from unittest.mock import Mock, patch

from arcade_common.audio import KeyboardAudio, SOUND_DIR
from tink_stacker.ui import Controller, run


class StackerAudioTests(unittest.TestCase):
    def frame(self, c, audio, keys='', rows=30, columns=80):
        return c.frame(c.last + .01, rows, columns, [ord(k) for k in keys], audio)

    def test_lock_loss_and_win_dispatch_shared_cues(self):
        c = Controller(0); a = Mock()
        self.frame(c, a, ' '); a.play.assert_called_once_with('place')
        a.reset_mock(); self.frame(c, a, ' '); a.play.assert_called_once_with('over')
        c = Controller(0)
        for _ in range(14): c.game.x = 0; c.game.lock_row()
        c.game.x = 0
        a.reset_mock(); self.frame(c, a, ' '); a.play.assert_called_once_with('clear')
        for key in 'ppr':
            c = Controller(0); a.reset_mock()
            self.frame(c, a, key); a.play.assert_called_once_with('switch')

    def test_automatic_travel_and_frozen_gameplay_are_silent(self):
        a = Mock(); c = Controller(0)
        c.frame(.24, 30, 80, [], a)
        a.play.assert_not_called()
        self.frame(c, a, 'p'); a.reset_mock()
        self.frame(c, a, ' '); a.play.assert_not_called()
        self.frame(c, a, ' ', rows=12, columns=40); a.play.assert_not_called()
        for state in ('won', 'lost'):
            c = Controller(0); c.game.state = state; a.reset_mock()
            self.frame(c, a, ' '); a.play.assert_not_called()

    def test_audio_tick_runs_each_frame_including_pause_resize_and_end_states(self):
        c = Controller(0); a = Mock()
        for state, small, paused in (('playing', False, False), ('playing', False, True), ('playing', True, False), ('won', False, False), ('lost', False, False)):
            c.game.state, c.paused = state, paused
            a.reset_mock()
            self.frame(c, a, rows=12 if small else 30, columns=40 if small else 80)
            a.tick.assert_called_once()

    def test_mute_cancels_pending_and_active_cues_and_unmute_confirms(self):
        backend = Mock(ready=True)
        with patch('arcade_common.audio._make_backend', return_value=backend):
            with KeyboardAudio() as a:
                c = Controller(0)
                self.frame(c, a, ' ')
                backend.play.assert_called_with(SOUND_DIR / 'enter.wav')
                a.play('clear')
                self.frame(c, a, 'm')
                self.assertEqual(a.status, 'key sound muted [M]')
                backend.stop.assert_called_once()
                self.assertIsNone(a._pending)
                self.frame(c, a, 'r ')
                self.assertEqual(backend.play.call_count, 1)
                self.frame(c, a, 'M')
                backend.play.assert_called_with(SOUND_DIR / 'mx-blue.wav')

    def test_no_sound_never_creates_backend_and_m_cannot_enable_it(self):
        with patch('arcade_common.audio._make_backend') as factory, patch('arcade_common.audio.Path.is_file') as files:
            with KeyboardAudio(enabled=False) as a:
                c = Controller(0)
                for key in (' ', 'm', 'r', 'M'): self.frame(c, a, key)
                self.assertEqual(a.status, 'key sound off')
            factory.assert_not_called(); files.assert_not_called()

    def test_unavailable_audio_keeps_game_playable_and_reports_warning(self):
        with patch('arcade_common.audio._make_backend', side_effect=OSError('no output device')):
            with KeyboardAudio() as a:
                c = Controller(0); self.frame(c, a, ' ')
                self.assertEqual(len(c.game.rows), 1)
                self.assertEqual(a.status, 'key sound unavailable')
                self.assertEqual(a.warning, 'no output device')
            with patch('curses.curs_set'), patch('curses.set_escdelay'), patch('tink_stacker.ui.Renderer'), patch('tink_stacker.ui._run_loop'):
                self.assertEqual(run(Mock()), 'no output device')

    def test_audio_closes_on_quit_sigint_and_exception(self):
        for error in (None, KeyboardInterrupt(), RuntimeError('render failed')):
            for disabled in (False, True):
                backend = Mock(ready=True)
                def loop(screen, renderer, c, a, trace):
                    self.frame(c, a, 'q')
                    self.assertTrue(c.quit)
                    if error: raise error
                with patch('curses.curs_set'), patch('curses.set_escdelay'), patch('tink_stacker.ui.Renderer'), patch('arcade_common.audio._make_backend', return_value=backend) as factory, patch('tink_stacker.ui._run_loop', side_effect=loop):
                    if error:
                        with self.assertRaises(type(error)): run(Mock(), no_sound=disabled)
                    else: self.assertEqual(run(Mock(), no_sound=disabled), '')
                if disabled: factory.assert_not_called()
                else: backend.close.assert_called_once()

    def test_restart_preserves_mute_without_reloading_samples(self):
        backend = Mock(ready=True)
        with patch('arcade_common.audio._make_backend', return_value=backend) as factory:
            with KeyboardAudio() as a:
                c = Controller(0)
                self.frame(c, a, 'm'); self.frame(c, a, 'r')
                self.assertTrue(a.muted)
                self.assertEqual(c.game.snapshot(), Controller(0).game.snapshot())
                factory.assert_called_once()
