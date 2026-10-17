import unittest
from tink_wordle.engine import Game, MAX_GUESSES


class WordleEngineTests(unittest.TestCase):
    def test_seed_is_repeatable_and_restart_resets(self):
        a, b = Game(seed=7), Game(seed=7)
        self.assertEqual(a.answer, b.answer)
        for letter in 'arise':
            a.add_letter(letter)
        a.submit()
        a.restart()
        self.assertEqual(a.answer, b.answer)
        self.assertEqual((a.guesses, a.current, a.status), ([], '', 'playing'))

    def test_duplicate_scoring_uses_available_letters(self):
        game = Game(answer='allee')
        for letter in 'eerie':
            game.add_letter(letter)
        result = game.submit()
        self.assertEqual(result, ('present', 'absent', 'absent', 'absent', 'correct'))

    def test_letter_states_record_absent_and_keep_best_feedback(self):
        game = Game(answer='arise')
        for letter in 'paper':
            game.add_letter(letter)
        game.submit()
        for letter in 'laser':
            game.add_letter(letter)
        game.submit()
        self.assertEqual(game.letter_states['p'], 'absent')
        self.assertEqual(game.letter_states['l'], 'absent')
        self.assertEqual(game.letter_states['s'], 'present')

        game = Game(answer='arise')
        for letter in 'raise':
            game.add_letter(letter)
        game.submit()
        for letter in 'arise':
            game.add_letter(letter)
        game.submit()
        self.assertEqual(game.letter_states['a'], 'correct')
        self.assertEqual(game.letter_states['r'], 'correct')
        self.assertEqual(game.letter_states['e'], 'correct')

    def test_guess_validation_and_letter_bounds(self):
        game = Game(answer='arise')
        self.assertFalse(game.remove_letter())
        for letter in 'zzzzz':
            self.assertTrue(game.add_letter(letter))
        self.assertFalse(game.add_letter('z'))
        self.assertEqual(game.current, 'zzzzz')
        self.assertIsNone(game.submit())
        self.assertIn('recognized word', game.message)
        self.assertTrue(game.remove_letter())
        self.assertEqual(game.current, 'zzzz')

    def test_common_five_letter_guess_outside_answer_list_is_accepted(self):
        game = Game(answer='arise')
        for letter in 'which':
            game.add_letter(letter)
        self.assertIsNotNone(game.submit())
        self.assertEqual(game.guesses, ['which'])

    def test_win_and_loss_stop_input(self):
        game = Game(answer='arise')
        for letter in 'arise':
            game.add_letter(letter)
        self.assertEqual(game.submit(), ('correct',) * 5)
        self.assertEqual(game.status, 'won')
        self.assertFalse(game.add_letter('x'))
        game = Game(answer='arise')
        for _ in range(MAX_GUESSES):
            for letter in 'audio':
                game.add_letter(letter)
            game.submit()
        self.assertEqual(game.status, 'lost')
        self.assertEqual(len(game.guesses), MAX_GUESSES)
        self.assertFalse(game.remove_letter())


if __name__ == '__main__':
    unittest.main()
