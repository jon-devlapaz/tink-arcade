import io
import json
import unittest
from unittest.mock import Mock, patch

from tink_pacman.engine import Game
from tink_pacman.ui import handle_key, run, _run_loop


class TerminalIntegrationTests(unittest.TestCase):
    def test_mute_and_twist_cues(self):
        game, audio = Game(), Mock()
        handle_key(game, ord('M'), audio)
        audio.toggle.assert_called_once()
        handle_key(game, ord(' '), audio)
        audio.play.assert_called_once_with('rotate')

    def test_no_sound_and_trace_cleanup_on_failure(self):
        trace, screen, audio = io.StringIO(), Mock(), Mock()
        audio.__enter__ = Mock(return_value=audio)
        audio.__exit__ = Mock(return_value=False)
        with patch('tink_pacman.ui.curses.curs_set'), patch('tink_pacman.ui.curses.set_escdelay'), \
                patch('tink_pacman.ui.os.environ', {'TINK_PACMAN_TRACE': 'trace.jsonl'}), \
                patch('tink_pacman.ui.open', return_value=trace), \
                patch('tink_pacman.ui.KeyboardAudio', return_value=audio) as factory, \
                patch('tink_pacman.ui._run_loop', side_effect=RuntimeError('render failed')):
            with self.assertRaisesRegex(RuntimeError, 'render failed'):
                run(screen, no_color=True, no_sound=True)
            factory.assert_called_once_with(enabled=False)
        self.assertTrue(trace.closed)
        audio.__exit__.assert_called_once()

    def test_small_window_freezes_and_mute_still_works(self):
        screen, renderer, audio = Mock(), Mock(), Mock()
        audio.status = 'key sound muted [M]'
        screen.getmaxyx.return_value = (12, 40)
        screen.getch.side_effect = [ord('M'), ord('r'), ord(' '), ord('e'), -1, ord('q')]
        game, trace = Game(), io.StringIO()
        with patch('tink_pacman.ui.time.sleep'), patch('tink_pacman.ui.time.monotonic', return_value=0):
            _run_loop(screen, renderer, game, audio, trace)
        state = json.loads(trace.getvalue())
        self.assertTrue(state['small'])
        self.assertEqual(state['pacman'], list(game.maze.start))
        self.assertTrue(state['bookmark_available'] and state['eraser_available'])
        audio.toggle.assert_called_once()
        audio.stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()
