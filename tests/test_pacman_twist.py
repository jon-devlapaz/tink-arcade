import contextlib
import io
import unittest
from unittest.mock import patch

from tink_pacman.__main__ import main
from tink_pacman.engine import CHASE, SCATTER, DOWN, LEFT, RIGHT, Game
from tink_pacman.maze import Maze
from tink_pacman.ui import handle_key
from tests.test_pacman_ui import drawn

THIN = ('#######', '#..P..#', '#.###.#', '#.....#', '#######')
THICK = ('#######', '#..P..#', '#.###.#', '#.###.#', '#.....#', '#######')
HOUSE = ('#########', '#..P....#', '#..#-#..#', '#...H...#', '#########')
TUNNEL = ('#######', ' .P#.. ', '#######')


class BookmarkTests(unittest.TestCase):
    def test_drop_uses_current_tile_and_one_charge(self):
        game = Game()
        self.assertEqual(game.drop_bookmark(), 'rotate')
        self.assertEqual(game.bookmark, game.pacman)
        self.assertEqual(game.bookmark_left, 4.0)
        game.pacman = (1, 1)
        self.assertIsNone(game.drop_bookmark())
        self.assertNotEqual(game.bookmark, game.pacman)

    def test_overrides_every_roaming_ghost_in_chase_and_scatter(self):
        game = Game()
        game.drop_bookmark()
        game.pacman = (1, 1)
        for mode in (CHASE, SCATTER):
            game.waves = type(game.waves)(((mode, float('inf')),))
            for ghost in game.ghosts:
                ghost.state = 'out'
                self.assertEqual(game._target(ghost), game.bookmark)

    def test_frightened_and_eyes_ignore_bookmark(self):
        game = Game()
        ghost = game.ghost('blinky')
        original = game._target(ghost)
        game.drop_bookmark()
        ghost.frightened = True
        self.assertEqual(game._target(ghost), original)
        ghost.state = 'eyes'
        self.assertEqual(game._target(ghost), game.maze.door_exit)

    def test_plans_are_refreshed_on_drop_and_expiry(self):
        game = Game()
        with patch.object(game, '_replan', wraps=game._replan) as replan:
            game.drop_bookmark()
            replan.assert_any_call(game.ghost('blinky'))
            replan.reset_mock()
            game.bookmark_left = .05
            game.update(.1)
            replan.assert_any_call(game.ghost('blinky'))
        self.assertIsNone(game.bookmark)

    def test_expires_after_four_simulation_seconds_and_pause_freezes_it(self):
        game = Game(layout=THIN)
        game.pacman, game.direction = (1, 1), LEFT
        game.drop_bookmark()
        game.toggle_pause()
        game.update(10)
        self.assertEqual(game.bookmark_left, 4.0)
        game.toggle_pause()
        for _ in range(39):
            game.update(.1)
        self.assertIsNotNone(game.bookmark)
        game.update(.1)
        self.assertIsNone(game.bookmark)
        self.assertIsNone(game.drop_bookmark())

    def test_ghost_reaching_bookmark_consumes_it(self):
        game = Game()
        ghost = game.ghost('blinky')
        game.pacman = game.maze.step(ghost.tile, LEFT)
        game.drop_bookmark()
        game.pacman = (1, 1)
        game._roam(ghost)
        self.assertIsNone(game.bookmark)
        self.assertIsNone(game.drop_bookmark())

    def test_frightened_ghost_reaching_bookmark_also_consumes_it(self):
        game = Game()
        ghost = game.ghost('blinky')
        ghost.frightened = True
        game.pacman = game.maze.step(ghost.tile, LEFT)
        game.drop_bookmark()
        game.pacman = (1, 1)
        game._roam(ghost)
        self.assertIsNone(game.bookmark)


class EraserTests(unittest.TestCase):
    def test_erases_only_the_wall_ahead_and_opens_it_to_all_actors(self):
        game = Game(layout=THIN)
        game.direction = DOWN
        self.assertEqual(game.erase(), 'place')
        self.assertTrue(game.maze.is_open((3, 2)))
        self.assertEqual(game.maze.step(game.pacman, DOWN), (3, 2))
        self.assertEqual(game.maze.step((3, 3), (0, -1)), (3, 2))
        self.assertNotIn((3, 2), game.dots)
        game.pacman = (2, 1)
        self.assertIsNone(game.erase())
        self.assertIn((2, 2), game.maze.walls)

    def test_invalid_erase_does_not_spend_charge(self):
        game = Game(layout=THIN)
        self.assertIsNone(game.erase())
        game.direction = DOWN
        self.assertEqual(game.erase(), 'place')

    def test_protected_walls_are_rejected(self):
        cases = ((THIN, (0, 2)), (THIN, (3, 0)), (THICK, (3, 2)),
                 (HOUSE, (3, 2)), (HOUSE, (4, 2)), (HOUSE, (4, 3)), (TUNNEL, (3, 1)))
        for layout, tile in cases:
            with self.subTest(tile=tile, layout=layout):
                self.assertFalse(Maze(layout).can_erase(tile))

    def test_refills_on_life_loss_but_erased_wall_stays_until_level_clear(self):
        game = Game()
        wall = next(tile for tile in sorted(game.maze.walls) if game.maze.can_erase(tile))
        for direction in (DOWN, RIGHT):
            before = (wall[0] - direction[0], wall[1] - direction[1])
            if game.maze.is_open(before):
                break
        game.pacman, game.direction = before, direction
        self.assertEqual(game.erase(), 'place')
        game.drop_bookmark()
        ghost = game.ghost('blinky')
        ghost.tile = game.pacman
        self.assertEqual(game._touch(), 'over')
        self.assertEqual(game.lives, 2)
        self.assertTrue(game.bookmark_available and game.eraser_available)
        self.assertTrue(game.maze.is_open(wall))
        game.new_level()
        self.assertIn(wall, game.maze.walls)

    def test_level_clear_keeps_spent_charges_and_restart_refills_them(self):
        game = Game(layout=THIN)
        game.direction = DOWN
        game.erase()
        game.drop_bookmark()
        game.dots = {game.pacman}
        self.assertEqual(game._eat(), 'clear')
        self.assertFalse(game.bookmark_available or game.eraser_available)
        self.assertIsNone(game.bookmark)
        self.assertIn((3, 2), game.maze.walls)
        game.restart()
        self.assertTrue(game.bookmark_available and game.eraser_available)


class InputTests(unittest.TestCase):
    def test_space_and_e_keys_use_the_mechanics(self):
        game = Game(layout=THIN)
        game.direction = DOWN
        self.assertTrue(handle_key(game, ord(' ')))
        self.assertIsNotNone(game.bookmark)
        self.assertTrue(handle_key(game, ord('E')))
        self.assertNotIn((3, 2), game.maze.walls)

    def test_classic_keys_are_inert(self):
        game = Game(layout=THIN, classic=True)
        game.direction = DOWN
        for key in (' ', 'e', 'E'):
            handle_key(game, ord(key))
        self.assertIsNone(game.bookmark)
        self.assertIn((3, 2), game.maze.walls)
        self.assertTrue(game.bookmark_available and game.eraser_available)

    def test_pause_and_game_over_reject_mechanics_without_spending(self):
        for state in ('paused', 'game_over'):
            game = Game(layout=THIN)
            game.direction = DOWN
            setattr(game, state, True)
            self.assertIsNone(game.drop_bookmark())
            self.assertIsNone(game.erase())
            self.assertTrue(game.bookmark_available and game.eraser_available)

    def test_classic_cli_option_reaches_the_game(self):
        with patch('tink_pacman.__main__.sys.stdin.isatty', return_value=True), \
                patch('tink_pacman.__main__.sys.stdout.isatty', return_value=True), \
                patch('tink_pacman.__main__.curses.wrapper') as wrapper:
            self.assertEqual(main(['--classic', '--seed', '7']), 0)
            self.assertTrue(wrapper.call_args.args[3])

    def test_bookmark_is_drawn_and_classic_hides_charges(self):
        game = Game()
        game.drop_bookmark()
        game.pacman = (12, 23)
        calls = drawn(40, 80, game)
        x, y = game.bookmark
        self.assertTrue(any((c[0], c[1], c[2]) == (5 + y, 4 + 2 * x, '[]') for c in calls))
        self.assertIn('Bookmark 0', [c[2] for c in calls])
        self.assertIn('Eraser 1', [c[2] for c in calls])
        texts = [c[2] for c in drawn(40, 80, Game(classic=True))]
        self.assertFalse(any('Bookmark' in text or 'Eraser' in text for text in texts))

    def test_classic_help_works_without_a_terminal(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as exit:
            main(['--help'])
        self.assertEqual(exit.exception.code, 0)
        self.assertIn('--classic', output.getvalue())


if __name__ == '__main__':
    unittest.main()
