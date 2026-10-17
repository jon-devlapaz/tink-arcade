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

    def test_color_renderer_adds_filled_wordle_state_pairs(self):
        with (patch('tink_wordle.ui.curses.has_colors', return_value=True),
              patch('tink_wordle.ui.curses.start_color'),
              patch('tink_wordle.ui.curses.COLORS', 256, create=True),
              patch('tink_wordle.ui.curses.COLOR_PAIRS', 64, create=True),
              patch('tink_wordle.ui.curses.init_pair') as init_pair,
              patch('tink_wordle.ui.curses.color_pair', side_effect=lambda n: n << 8)):
            Renderer(Mock(), False)
        self.assertIn(call(5, 233, 178), init_pair.call_args_list)
        self.assertIn(call(6, 15, 29), init_pair.call_args_list)

    def test_all_wordle_state_colors_meet_contrast_requirement(self):
        # These are the effective foreground/background colors after filled blocks
        # (including the reverse-video shared states) are rendered.
        states = {
            'correct': (15, 29),
            'present': (233, 178),
            'absent': (230, 240),
        }

        def xterm_rgb(index):
            if index < 16:
                return ((0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
                        (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192, 192),
                        (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0),
                        (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255))[index]
            if index >= 232:
                value = 8 + (index - 232) * 10
                return (value, value, value)
            cube = index - 16
            levels = (0, 95, 135, 175, 215, 255)
            return (levels[cube // 36], levels[(cube // 6) % 6], levels[cube % 6])

        def luminance(index):
            channels = []
            for channel in xterm_rgb(index):
                value = channel / 255
                channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
            return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

        for state, (foreground, background) in states.items():
            lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
            contrast = (lighter + 0.05) / (darker + 0.05)
            self.assertGreaterEqual(contrast, 4.5, state)

    def test_keyboard_fits_play_box_at_minimum_size(self):
        screen = Mock()
        screen.getmaxyx.return_value = (30, 80)
        Renderer(screen, True).draw(Game(answer='arise'), False, 'key sound on [F3]')
        calls = [call.args for call in screen.addnstr.call_args_list]
        for y, x, text, width, _ in calls:
            self.assertTrue(0 <= y < 30)
            self.assertTrue(0 <= x and x + len(text) <= 80)
        keyboard = set('QWERTYUIOPASDFGHJKLZXCVBNM')
        keyboard_calls = [call for call in calls if call[2] in keyboard and 18 <= call[0] <= 20]
        self.assertTrue(keyboard.issubset({call[2] for call in keyboard_calls}))
        self.assertTrue(all(4 < call[0] < 24 and 8 < call[1] < 42 for call in keyboard_calls))
        self.assertIn('INK    unused letter', {call[2] for call in calls})

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
