import math
import unittest

from tink_crossing import engine
from tink_crossing.engine import (BAYS, Game, LANES, MAX_BASE_SPEED, MEDIAN, RIVER,
                                  ROAD, START, START_COL, STEP, WIDTH, bay_at, period)


def find(game, row, want):
    return next(c for c in range(WIDTH) if game.occupied(row, c) == want)


def steps(game, n):
    cues = []
    for _ in range(n):
        cues += game.advance(STEP)
    return cues


class LayoutTests(unittest.TestCase):
    def test_board_rows_and_lanes(self):
        self.assertEqual((engine.WIDTH, engine.ROWS), (40, 13))
        self.assertEqual(sorted(LANES), list(RIVER) + list(ROAD))
        self.assertNotIn(MEDIAN, LANES)
        self.assertLessEqual(MAX_BASE_SPEED, 8)
        directions = [LANES[r][2] for r in sorted(LANES)]
        for lanes in (list(RIVER), list(ROAD)):
            dirs = [LANES[r][2] for r in lanes]
            self.assertTrue(all(a == -b for a, b in zip(dirs, dirs[1:])), dirs)
        self.assertTrue(all(len(LANES[r][0]) == WIDTH for r in LANES), directions)

    def test_bays(self):
        self.assertEqual(len(BAYS), 5)
        self.assertEqual([bay_at(c) for c in (2, 3, 5, 6, 11, 37, 38)], [None, 0, 0, None, 1, 4, None])

    def test_periods_scale_with_level(self):
        for row in LANES:
            self.assertGreater(period(row, 1), period(row, 3))
            self.assertAlmostEqual(1 / (period(row, 1) * STEP), LANES[row][1], delta=0.5)


class RuleTests(unittest.TestCase):
    def test_new_game(self):
        g = Game()
        self.assertEqual((g.row, g.col, g.lives, g.level, g.score, g.state), (START, START_COL, 3, 1, 0, 'playing'))

    def test_hop_clamps_and_scores_new_rows_once(self):
        g = Game()
        self.assertEqual(g.hop(1, 0), [])  # already on the start row
        g.col = 0
        self.assertEqual(g.hop(0, -1), [])  # left wall
        g.col = find(g, 11, False)
        self.assertEqual(g.hop(-1, 0), ['move'])
        self.assertEqual((g.row, g.score), (11, 10))
        self.assertEqual(g.hop(1, 0), ['move'])
        self.assertEqual(g.hop(-1, 0), ['move'])
        self.assertEqual(g.score, 10)  # row 11 already reached this attempt
        self.assertEqual(g.hop(2, 0), [])
        self.assertEqual(g.hop(1, 1), [])

    def test_road_hit_on_hop_and_by_shift(self):
        g = Game()
        g.col = find(g, 11, True)
        self.assertEqual(g.hop(-1, 0), ['move', 'over'])
        self.assertEqual((g.lives, g.row, g.col, g.deaths), (2, START, START_COL, 1))
        g = Game()
        # Stand on row 11 just ahead of a car moving left and wait for it.
        car = find(g, 11, True)
        col = (car - 1) % WIDTH
        while g.occupied(11, col):
            col = (col - 1) % WIDTH
        g.row, g.col, g.best = 11, col, 11
        cues = steps(g, period(11, 1) * WIDTH)
        self.assertIn('over', cues)
        self.assertEqual(g.lives, 2)

    def test_water_and_logs_carry(self):
        g = Game()
        g.row, g.col = MEDIAN, find(g, 5, False)
        self.assertEqual(g.hop(-1, 0)[-1], 'over')
        g = Game()
        log = next(c for c in range(5, 30) if g.occupied(5, c) and g.occupied(5, c + 1))
        g.row, g.col = MEDIAN, log
        self.assertEqual(g.hop(-1, 0), ['move'])
        steps(g, period(5, 1))
        self.assertEqual(g.col, log + LANES[5][2])
        self.assertTrue(g.occupied(5, g.col))

    def test_carried_off_edge(self):
        g = Game()
        g.row, g.col, g.best = 5, WIDTH - 1, 5
        g.lanes[5] = [True] * WIDTH
        cues = steps(g, period(5, 1))
        self.assertEqual(cues, ['over'])
        self.assertEqual((g.lives, g.row), (2, START))

    def test_bays_fill_and_wall_and_repeat(self):
        g = Game()
        g.row, g.col = 1, BAYS[0][0]
        self.assertEqual(g.hop(-1, 0), ['move', 'clear'])
        self.assertEqual((g.bays[0], g.row, g.score), (True, START, 10 + 50))
        g.row, g.col = 1, BAYS[0][0]
        self.assertEqual(g.hop(-1, 0)[-1], 'over')
        g.row, g.col = 1, 0
        self.assertEqual(g.hop(-1, 0)[-1], 'over')
        self.assertEqual(g.lives, 1)

    def test_levels_and_win(self):
        g = Game()
        for level in (1, 2, 3):
            self.assertEqual(g.level, level)
            for left, _ in BAYS:
                g.row, g.col = 1, left
                g.hop(-1, 0)
            if level < 3:
                self.assertEqual((g.bays, g.state), ([False] * 5, 'playing'))
                self.assertEqual(g.counters, {r: 0 for r in LANES})
        self.assertEqual(g.state, 'won')
        self.assertEqual(g.score, 3 * (5 * (10 + 50) + 100))
        self.assertEqual(g.hop(1, 0), [])
        self.assertEqual(g.advance(1), [])

    def test_game_over_freezes(self):
        g = Game()
        for _ in range(3):
            g.row, g.col = 1, 0
            g.hop(-1, 0)
        self.assertEqual((g.state, g.lives), ('over', 0))
        before = g.snapshot()
        self.assertEqual(g.advance(.1), [])
        self.assertEqual(g.hop(-1, 0), [])
        self.assertEqual(g.snapshot(), before)
        g.restart()
        self.assertEqual(g.snapshot(), Game().snapshot())

    def test_pause_freezes_and_blocks_hops(self):
        g = Game()
        self.assertTrue(g.toggle_pause())
        before = g.snapshot()
        self.assertEqual(g.advance(.1), [])
        self.assertEqual(g.hop(-1, 0), [])
        self.assertEqual(g.snapshot(), before)
        self.assertTrue(g.toggle_pause())
        g.state = 'won'
        self.assertFalse(g.toggle_pause())

    def test_elapsed_cap_and_validation(self):
        g = Game()
        g.advance(5)
        self.assertEqual(g.counters[3], round(.1 / STEP) % period(3, 1))
        for bad in (-1, math.inf, math.nan):
            with self.assertRaises(ValueError):
                g.advance(bad)

    def test_lanes_move_one_cell_per_period(self):
        g = Game()
        for row in LANES:
            before = list(g.lanes[row])
            g2 = Game()
            steps(g2, period(row, 1))
            d = LANES[row][2]
            self.assertEqual(g2.lanes[row], [before[(c - d) % WIDTH] for c in range(WIDTH)])


if __name__ == '__main__':
    unittest.main()
