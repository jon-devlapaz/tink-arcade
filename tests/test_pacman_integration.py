import unittest
from unittest.mock import Mock, patch

from arcade_menu.registry import ROOT, load_games
from arcade_menu.ui import run


class PacmanIntegrationTests(unittest.TestCase):
    def test_registered_once_at_original_number_and_ready_offline(self):
        games = load_games()
        matches = [game for game in games if game.module == 'tink_pacman']
        self.assertEqual(len(matches), 1)
        game = matches[0]
        self.assertEqual(game, games[11])
        self.assertEqual(game.title, 'Pac-Man')
        self.assertTrue(game.available)
        self.assertFalse(game.requires_env)
        self.assertEqual(game.command('python3'), ['python3', '-m', 'tink_pacman'])
        self.assertEqual(game.command('python3', True), ['python3', '-m', 'tink_pacman', '--no-color'])
        self.assertIn('80 x 40', game.note)

    def test_menu_can_launch_pacman_past_the_digit_shortcuts(self):
        games = load_games()
        index = next(i for i, game in enumerate(games) if game.module == 'tink_pacman')
        self.assertGreaterEqual(index, 9)
        screen = Mock()
        screen.getch.side_effect = [ord('j')] * index + [13, ord('q')]
        with patch('arcade_menu.ui.curses.curs_set'), patch('arcade_menu.ui.Renderer'), \
                patch('arcade_menu.ui.draw'), patch('arcade_menu.ui.launch', return_value='') as launch:
            run(screen, games)
        launch.assert_called_once_with(games[index], False)

    def test_docs_describe_launch_classic_and_taller_minimum(self):
        for name in ('README.md', 'DESIGN.md'):
            text = (ROOT / name).read_text()
            for required in ('tink_pacman', '--classic', '80 x 40'):
                with self.subTest(file=name, required=required):
                    self.assertIn(required, text)


if __name__ == '__main__':
    unittest.main()
