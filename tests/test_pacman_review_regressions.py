import unittest
from unittest.mock import patch

from tink_pacman.engine import CHASE, SCATTER, DOWN, LEFT, RIGHT, Game
from tink_pacman.ghosts import EYES_SPEED, Waves, fright_speed, ghost_speed
from tink_pacman.maze import DIRECTIONS
from tests.test_pacman_ghosts import PEN_E, make
from tests.test_pacman_ui import drawn


class CueSimulationTests(unittest.TestCase):
    def test_energizer_cue_does_not_skip_ghost_progress_or_fright_timer(self):
        game = make(layout=PEN_E)
        game.pacman, game.direction, game.progress = (2, 5), LEFT, 1.0
        self.assertEqual(game.update(.02), 'switch')
        self.assertAlmostEqual(game.ghost('blinky').progress, .1)
        self.assertAlmostEqual(game.ghost('pinky').progress, .1)
        self.assertAlmostEqual(game.fright_left, 5.98)
        self.assertAlmostEqual(game.pen.idle, .02)
        self.assertEqual(game.waves.left, float('inf'))

    def test_ghost_eaten_cue_does_not_skip_other_ghosts_or_timer(self):
        game = make()
        game._frighten()
        game.pacman, game.direction, game.progress = (4, 1), RIGHT, 1.0
        self.assertEqual(game.update(.02), 'clear')
        self.assertEqual(game.ghost('blinky').state, 'eyes')
        self.assertAlmostEqual(game.ghost('pinky').progress, .1)
        self.assertAlmostEqual(game.fright_left, 5.98)

    def test_ghost_cue_takes_precedence_over_energizer_cue(self):
        game = make(layout=PEN_E)
        game.pacman, game.direction, game.progress = (2, 5), LEFT, 1.0
        blinky = game.ghost('blinky')
        blinky.tile, blinky.direction, blinky.plan, blinky.progress = (0, 5), RIGHT, RIGHT, 1.0
        self.assertEqual(game.update(.02), 'clear')
        self.assertEqual(blinky.state, 'eyes')
        self.assertEqual(game.score, 250)

    def test_new_level_does_not_advance_its_ghosts_in_the_old_frame(self):
        game = make()
        game.pacman, game.direction, game.progress = (4, 5), LEFT, 1.0
        game.dots = {(3, 5)}
        with patch.object(game, '_move_ghosts', wraps=game._move_ghosts) as move:
            self.assertEqual(game.update(.1), 'clear')
            move.assert_not_called()
        self.assertEqual(game.level, 2)
        self.assertEqual(game.ghost('blinky').progress, 0)
        self.assertEqual(game.pen.idle, 0)

    def test_life_loss_does_not_advance_reset_ghosts(self):
        game = make()
        game.pacman, game.direction, game.progress = (4, 1), RIGHT, 1.0
        with patch.object(game, '_move_ghosts', wraps=game._move_ghosts) as move:
            self.assertEqual(game.update(.1), 'over')
            move.assert_not_called()
        self.assertEqual(game.lives, 2)
        self.assertEqual(game.ghost('blinky').progress, 0)
        self.assertEqual(game.pen.idle, 0)

    def test_final_life_loss_does_not_advance_ghosts(self):
        game = make()
        game.lives = 1
        game.pacman, game.direction, game.progress = (4, 1), RIGHT, 1.0
        with patch.object(game, '_move_ghosts', wraps=game._move_ghosts) as move:
            self.assertEqual(game.update(.1), 'over')
            move.assert_not_called()
        self.assertTrue(game.game_over)


class FrightenedPlanTests(unittest.TestCase):
    def test_twist_refreshes_preserve_frightened_plans_and_random_state(self):
        for action in ('drop', 'expire', 'consume', 'erase'):
            with self.subTest(action=action):
                game = Game(seed=1)
                game._frighten()
                game._refresh_plans()
                if action in ('expire', 'consume'):
                    game.drop_bookmark()
                before = game.rng.getstate()
                plans = [ghost.plan for ghost in game.ghosts]
                if action == 'drop':
                    self.assertEqual(game.drop_bookmark(), 'rotate')
                elif action == 'expire':
                    game.bookmark_left = 0
                    game.update(0)
                    self.assertIsNone(game.bookmark)
                elif action == 'consume':
                    game.ghost('blinky').tile = game.bookmark
                    game._consume_bookmark()
                    self.assertIsNone(game.bookmark)
                else:
                    game.pacman, game.direction = (9, 26), DOWN
                    self.assertEqual(game.erase(), 'place')
                self.assertEqual(game.rng.getstate(), before)
                self.assertEqual([ghost.plan for ghost in game.ghosts], plans)

    def test_target_refresh_still_updates_normal_ghosts_and_eyes(self):
        game = Game(seed=1)
        blinky, pinky = game.ghost('blinky'), game.ghost('pinky')
        pinky.state, pinky.frightened = 'eyes', False
        game.ghost('inky').state, game.ghost('inky').frightened = 'out', True
        with patch.object(game, '_replan', wraps=game._replan) as replan:
            game._refresh_plans()
            self.assertEqual([call.args[0] for call in replan.call_args_list], [blinky, pinky])


class BookmarkVisibilityTests(unittest.TestCase):
    def test_bookmark_does_not_cover_pacman_or_facing_at_either_size(self):
        for rows, columns in ((40, 80), (45, 100)):
            game = Game()
            game.drop_bookmark()
            calls = drawn(rows, columns, game)
            x, y = game.pacman
            ox, oy = (columns - 80) // 2, (rows - 40) // 2
            at = [c for c in calls if (c[0], c[1]) == (oy + 5 + y, ox + 4 + 2 * x)]
            self.assertEqual(at[-1][2], '<O')
            self.assertIn('Bookmark active', [c[2] for c in calls])
            game.pacman = (12, 23)
            calls = drawn(rows, columns, game)
            at = [c for c in calls if (c[0], c[1]) == (oy + 5 + y, ox + 4 + 2 * x)]
            self.assertEqual(at[-1][2], '[]')


class BookmarkMovementTests(unittest.TestCase):
    def game_at_bookmark(self, mode=SCATTER):
        game = Game(seed=1)
        game.waves = Waves(((mode, float('inf')),))
        ghost = game.ghost('blinky')
        game.pacman, game.direction = (9, 26), DOWN
        ghost.tile, ghost.direction = (3, 1), LEFT
        game.bookmark, game.bookmark_left = (2, 1), 4.0
        game._refresh_plans()
        return game, ghost

    def test_consumption_preserves_the_current_turn_without_voluntary_reversal(self):
        for mode in (SCATTER, CHASE):
            with self.subTest(mode=mode):
                game, ghost = self.game_at_bookmark(mode)
                history = [ghost.tile]
                for _ in range(2):
                    ghost.progress = 1.0
                    self.assertIsNone(game.update(0))
                    history.append(ghost.tile)
                    self.assertIsNotNone(game.maze.step(ghost.tile, ghost.direction))
                self.assertEqual(history, [(3, 1), (2, 1), (1, 1)])
                self.assertIsNone(game.bookmark)

    def test_consumption_keeps_headings_legal_across_the_shipped_maze(self):
        game = Game(seed=1)
        for tile in game.maze.open_tiles():
            for heading in DIRECTIONS:
                ahead = game.maze.step(tile, heading)
                behind = game.maze.step(tile, (-heading[0], -heading[1]))
                if ahead is None or behind is None:
                    continue
                ghost = game.ghost('blinky')
                ghost.tile, ghost.direction, ghost.reverse = tile, heading, False
                game.bookmark, game.bookmark_left = ahead, 4.0
                game._refresh_plans()
                game._roam(ghost)
                self.assertIsNone(game.bookmark)
                self.assertIsNotNone(game.maze.step(ghost.tile, ghost.direction), (tile, heading))
                self.assertNotEqual(ghost.direction, (-heading[0], -heading[1]), (tile, heading))

    def test_pending_forced_reversal_is_still_applied_on_consumption(self):
        game, ghost = self.game_at_bookmark()
        ghost.reverse = True
        game._roam(ghost)
        self.assertEqual((ghost.tile, ghost.direction, ghost.reverse), ((2, 1), RIGHT, False))
        self.assertIsNone(game.bookmark)

    def test_leaving_ghost_consumes_bookmark_without_changing_its_exit_direction(self):
        for frightened in (False, True):
            for flipped in (False, True):
                with self.subTest(frightened=frightened, flipped=flipped):
                    game = Game(seed=1)
                    game._roam(game.ghost('blinky'))
                    game.pacman = game.maze.door_exit
                    self.assertEqual(game.drop_bookmark(), 'rotate')
                    game.pacman = (9, 26)
                    ghost = game.ghost('pinky')
                    ghost.tile, ghost.progress = (13, 12), 1.0
                    ghost.frightened, ghost.flipped = frightened, flipped
                    if frightened:
                        game.fright_left = 6.0
                    self.assertIsNone(game.update(0))
                    expected_direction = RIGHT if flipped else LEFT
                    self.assertEqual((ghost.tile, ghost.state, ghost.direction),
                                     ((13, 11), 'out', expected_direction))
                    self.assertIsNone(game.bookmark)
                    self.assertEqual(game.bookmark_left, 0)
                    self.assertFalse(game.bookmark_available)
                    self.assertIsNotNone(game.maze.step(ghost.tile, ghost.direction))
                    ghost.progress = 1.0
                    game.update(0)
                    self.assertEqual(ghost.tile, (14, 11) if flipped else (12, 11))

    def test_bookmark_waits_until_the_leaving_ghost_reaches_the_exit(self):
        game = Game(seed=1)
        game._roam(game.ghost('blinky'))
        game.pacman = game.maze.door_exit
        game.drop_bookmark()
        game.pacman = (9, 26)
        ghost = game.ghost('pinky')
        ghost.tile, ghost.progress = (13, 13), 1.0
        game.update(0)
        self.assertEqual(ghost.tile, (13, 12))
        self.assertEqual(game.bookmark, (13, 11))
        ghost.progress = 1.0
        game.update(0)
        self.assertEqual(ghost.tile, (13, 11))
        self.assertIsNone(game.bookmark)

    def test_eyes_consume_bookmark_when_entering_the_house(self):
        game = Game(seed=1)
        ghost = game.ghost('blinky')
        ghost.state, ghost.tile, ghost.direction = 'eyes', (12, 11), RIGHT
        game.bookmark, game.bookmark_left = game.maze.door_exit, 4.0
        game._refresh_plans()
        game._roam(ghost)
        self.assertEqual((ghost.tile, ghost.state), (game.maze.door_exit, 'entering'))
        self.assertIsNone(game.bookmark)


class TunnelSpeedTests(unittest.TestCase):
    def test_tunnel_speed_applies_in_normal_and_frightened_modes_at_every_speed_tier(self):
        for level in (1, 2, 4, 5, 21):
            for frightened in (False, True):
                game = Game(seed=1)
                game.level = level
                ghost = game.ghost('blinky')
                ghost.tile, ghost.frightened = (0, 14), frightened
                self.assertTrue(game.maze.in_tunnel(ghost.tile))
                self.assertEqual(game._speed(ghost), ghost_speed(level, True), (level, frightened))
                ghost.tile = (6, 14)
                self.assertFalse(game.maze.in_tunnel(ghost.tile))
                expected = fright_speed(level) if frightened else ghost_speed(level, False)
                self.assertEqual(game._speed(ghost), expected, (level, frightened))

    def test_eyes_keep_their_separate_speed_even_in_the_tunnel(self):
        game = Game(seed=1)
        ghost = game.ghost('blinky')
        ghost.tile, ghost.state = (0, 14), 'eyes'
        self.assertEqual(game._speed(ghost), EYES_SPEED)

    def test_real_update_accumulates_tunnel_progress_while_frightened(self):
        game = Game(seed=1)
        game.pacman, game.direction = (1, 1), LEFT
        game._frighten()
        ghost = game.ghost('blinky')
        ghost.tile, ghost.direction, ghost.progress = (0, 14), RIGHT, 0
        game._replan(ghost)
        game.update(.1)
        self.assertAlmostEqual(ghost.progress, .4)
        self.assertEqual(ghost.tile, (0, 14))
        self.assertAlmostEqual(game.fright_left, 5.9)


if __name__ == '__main__':
    unittest.main()
