import curses
import unittest
from unittest.mock import Mock, call, patch

from tink_wordle.engine import Game
from tink_wordle.ui import Renderer, handle_key


class FakeAudio:
    def __init__(self):
        self.actions = []

    def toggle(self):
        self.actions.append('toggle')

    def stop(self):
        self.actions.append('stop')

    def play(self, name):
        self.actions.append(name)


class WordleInputTests(unittest.TestCase):
    def test_every_letter_is_typeable_including_shortcut_letters(self):
        game = Game(answer='arise')
        audio = FakeAudio()
        for letter in 'rmqai':
            self.assertTrue(handle_key(game, ord(letter), audio))
        self.assertEqual(game.current, 'rmqai')
        self.assertNotIn('toggle', audio.actions)
        self.assertNotIn('stop', audio.actions)

    def test_enter_submits_through_key_handler_and_updates_states(self):
        game = Game(answer='arise')
        audio = FakeAudio()
        for letter in 'raise':
            handle_key(game, ord(letter), audio)
        self.assertTrue(handle_key(game, curses.KEY_ENTER, audio))
        self.assertEqual(game.guesses, ['raise'])
        self.assertEqual(game.letter_states['r'], 'present')
        self.assertEqual(game.letter_states['a'], 'present')

    def test_shortcuts_are_off_letter_keys(self):
        game = Game(answer='arise')
        audio = FakeAudio()
        self.assertTrue(handle_key(game, curses.KEY_F2, audio))
        self.assertIn('stop', audio.actions)
        self.assertIn('switch', audio.actions)
        self.assertTrue(handle_key(game, curses.KEY_F3, audio))
        self.assertIn('toggle', audio.actions)
        self.assertFalse(handle_key(game, 27, audio))

    def test_keyboard_states_have_distinct_rendering_without_color(self):
        screen = Mock()
        screen.getmaxyx.return_value = (30, 80)
        game = Game(answer='arise')
        for letter in 'paper':
            game.add_letter(letter)
        game.submit()
        renderer = Renderer(screen, True)
        attrs = renderer._state_attrs()
        self.assertEqual(len(set(attrs.values())), 3)
        renderer.draw(game, False, 'key sound on [M]')
        calls = {call.args[2]: call.args[4] for call in screen.addnstr.call_args_list
                 if call.args[2] in 'PLR'}
        self.assertEqual(calls['P'], attrs['absent'])
        self.assertEqual(calls['L'], renderer.ink)
        self.assertEqual(calls['R'], attrs['present'])

    def test_keyboard_legend_names_wrong_place_as_yellow(self):
        screen = Mock()
        screen.getmaxyx.return_value = (30, 80)
        renderer = Renderer(screen, True)
        renderer.draw(Game(answer='arise'), False, 'key sound on [M]')
        self.assertIn('YELLOW wrong place', [call.args[2] for call in screen.addnstr.call_args_list])

    def test_color_renderer_adds_wordle_yellow_pair(self):
        with (patch('tink_wordle.ui.curses.has_colors', return_value=True),
              patch('tink_wordle.ui.curses.start_color'),
              patch('tink_wordle.ui.curses.COLORS', 256, create=True),
              patch('tink_wordle.ui.curses.COLOR_PAIRS', 64, create=True),
              patch('tink_wordle.ui.curses.init_pair') as init_pair,
              patch('tink_wordle.ui.curses.color_pair', side_effect=lambda n: n << 8)):
            Renderer(Mock(), False)
        self.assertIn(call(5, 226, 230), init_pair.call_args_list)

    def test_keyboard_fits_session_box_at_minimum_size(self):
        screen = Mock()
        screen.getmaxyx.return_value = (30, 80)
        Renderer(screen, True).draw(Game(answer='arise'), False, 'key sound on [F3]')
        calls = [call.args for call in screen.addnstr.call_args_list]
        for y, x, text, width, _ in calls:
            self.assertTrue(0 <= y < 30)
            self.assertTrue(0 <= x and x + len(text) <= 80)
        keyboard = set('QWERTYUIOPASDFGHJKLZXCVBNM')
        self.assertTrue(keyboard.issubset({call[2] for call in calls}))

    def test_controls_use_function_keys_and_escape(self):
        screen = Mock()
        screen.getmaxyx.return_value = (30, 80)
        renderer = Renderer(screen, True)
        renderer.draw(Game(answer='arise'), True, 'key sound on [F3]')
        small_texts = [call.args[2] for call in screen.addnstr.call_args_list]
        self.assertIn('F3 mute  Esc quit  Ctrl-C exit', small_texts)
        screen.reset_mock()
        game = Game(answer='arise')
        game.submit()  # invalid empty submission keeps the renderer in playing state
        game.status = 'won'
        game.message = 'Solved!'
        renderer.draw(game, False, 'key sound on [F3]')
        texts = [call.args[2] for call in screen.addnstr.call_args_list]
        self.assertIn('F2 restart   Esc quit', texts)
        self.assertNotIn('R restart   Q quit', texts)


if __name__ == '__main__':
    unittest.main()
