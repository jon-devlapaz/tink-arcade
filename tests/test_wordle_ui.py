import curses
import unittest

from tink_wordle.engine import Game
from tink_wordle.ui import handle_key


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


if __name__ == '__main__':
    unittest.main()
