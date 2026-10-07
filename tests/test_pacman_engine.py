import unittest

from tink_pacman.engine import DOWN, LEFT, RIGHT, UP, Game, pacman_speed

CORRIDOR = ('#######',
            '#..P..#',
            '#######')
TEE = ('#######',
       '#.P...#',
       '###.###',
       '###.###',
       '#######')
WRAP = ('#####',
        ' .P. ',
        '#####')
TWO_DOTS = ('#####',
            '#.P.#',
            '#####')
THREE_PLUS_ENERGIZER = ('#######',
                        '#o.P.##',
                        '#######')


def run(game, until, limit=400):
    """Update in small steps until `until(game)` is true; return the cues seen. Fail if it never happens."""
    cues = []
    for _ in range(limit):
        cue = game.update(0.02)
        if cue:
            cues.append(cue)
        if until(game):
            return cues
    raise AssertionError('condition never reached')


def advance(game, tiles=1):
    """Update until Pac-Man has changed tile `tiles` times."""
    for _ in range(tiles):
        before = game.pacman
        run(game, lambda g: g.pacman != before)


class SpeedTests(unittest.TestCase):
    def test_table(self):
        for level, expected in ((1, .8), (2, .9), (4, .9), (5, 1.0), (20, 1.0), (21, .9), (99, .9)):
            self.assertAlmostEqual(pacman_speed(level), expected, msg=f'level {level}')

    def test_level_one_takes_longer_per_tile_than_level_five(self):
        def updates_for_one_tile(level):
            g = Game(layout=CORRIDOR)
            g.level = level
            count = 0
            while g.pacman == (3, 1):
                g.update(0.01)
                count += 1
            return count
        self.assertGreater(updates_for_one_tile(1), updates_for_one_tile(5))


class MovementTests(unittest.TestCase):
    def test_starts_on_p_facing_left_with_three_lives(self):
        g = Game(layout=CORRIDOR)
        self.assertEqual((g.pacman, g.direction, g.lives, g.level, g.score), ((3, 1), LEFT, 3, 1, 0))

    def test_moves_by_itself_and_stops_at_a_wall(self):
        g = Game(layout=CORRIDOR)
        advance(g, 2)
        self.assertEqual(g.pacman, (1, 1))
        g.update(5)
        self.assertEqual((g.pacman, g.direction), ((1, 1), LEFT))

    def test_blocked_pacman_is_ready_to_move_at_once_but_never_bursts(self):
        g = Game(layout=CORRIDOR)
        advance(g, 2)
        for _ in range(50):
            g.update(0.05)
        self.assertTrue(g.turn(RIGHT))
        g.update(0.001)
        self.assertEqual(g.pacman, (2, 1))
        g.update(0.001)
        self.assertEqual(g.pacman, (2, 1))

    def test_one_slow_frame_moves_at_most_one_tile(self):
        g = Game(layout=CORRIDOR)
        g.update(50)
        self.assertIn(g.pacman, ((3, 1), (2, 1)))
        self.assertLess(g.progress, 1)

    def test_reverse_is_immediate(self):
        g = Game(layout=CORRIDOR)
        advance(g, 1)
        self.assertEqual(g.pacman, (2, 1))
        self.assertTrue(g.turn(RIGHT))
        advance(g, 1)
        self.assertEqual((g.pacman, g.direction), ((3, 1), RIGHT))

    def test_buffered_turn_waits_for_a_junction(self):
        g = Game(layout=TEE)
        g.turn(RIGHT)
        advance(g, 1)
        self.assertEqual(g.pacman, (3, 1))
        self.assertTrue(g.turn(DOWN))
        self.assertEqual(g.turn_buffer, DOWN)
        advance(g, 1)
        self.assertEqual((g.pacman, g.direction, g.turn_buffer), ((3, 2), DOWN, None))

    def test_blocked_turn_is_held_not_dropped(self):
        g = Game(layout=TEE)
        g.turn(UP)
        advance(g, 1)
        self.assertEqual(g.pacman, (1, 1))
        self.assertEqual(g.turn_buffer, UP)
        self.assertEqual(g.direction, LEFT)

    def test_turn_rejects_the_current_direction_and_unknown_values(self):
        g = Game(layout=CORRIDOR)
        self.assertFalse(g.turn(LEFT))
        self.assertFalse(g.turn((2, 2)))
        self.assertTrue(g.turn(UP))

    def test_tunnel_wraps_both_ways(self):
        g = Game(layout=WRAP)
        advance(g, 2)
        self.assertEqual(g.pacman, (0, 1))
        advance(g, 1)
        self.assertEqual(g.pacman, (4, 1))
        g.turn(RIGHT)
        advance(g, 1)
        self.assertEqual(g.pacman, (0, 1))


class ScoringTests(unittest.TestCase):
    def test_dot_scores_ten_and_is_removed(self):
        g = Game(layout=TWO_DOTS)
        advance(g, 1)
        self.assertEqual((g.pacman, g.score, g.dots), ((1, 1), 10, {(3, 1)}))

    def test_energizer_scores_fifty(self):
        g = Game(layout=THREE_PLUS_ENERGIZER)
        advance(g, 2)
        self.assertEqual((g.score, g.level), (60, 1))
        self.assertNotIn((1, 1), g.dots)

    def test_clearing_the_last_dot_starts_the_next_level_and_restores_the_maze(self):
        g = Game(layout=TWO_DOTS)
        advance(g, 1)
        g.turn(RIGHT)
        cues = run(g, lambda game: game.level == 2)
        self.assertEqual(cues, ['clear'])
        self.assertEqual((g.pacman, g.direction, g.score), ((2, 1), LEFT, 20))
        self.assertEqual(g.dots, {(1, 1), (3, 1)})
        self.assertIsNone(g.turn_buffer)

    def test_best_survives_restart(self):
        g = Game(layout=THREE_PLUS_ENERGIZER)
        advance(g, 2)
        g.restart()
        self.assertEqual((g.score, g.best, g.level, g.lives, g.pacman), (0, 60, 1, 3, (3, 1)))
        self.assertEqual(g.dots, {(1, 1), (2, 1), (4, 1)})


class PauseTests(unittest.TestCase):
    def test_pause_freezes_time_and_input(self):
        g = Game(layout=CORRIDOR)
        g.update(0.05)
        progress = g.progress
        self.assertTrue(g.toggle_pause())
        g.update(10)
        self.assertEqual((g.pacman, g.progress), ((3, 1), progress))
        self.assertFalse(g.turn(UP))
        self.assertTrue(g.toggle_pause())
        self.assertTrue(g.turn(UP))


if __name__ == '__main__':
    unittest.main()
