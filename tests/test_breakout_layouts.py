"""Reproducible full-run controller. It uses only move, launch and elapsed time."""
import random
import unittest
from tink_breakout.engine import Game, STEP, WIDTH, PADDLE_Y
from tink_breakout.layouts import PATTERNS, bricks_for


def legal_replay(seed=20261004, limit=180000):
    g = Game()
    rng = random.Random(seed)
    offset = 0
    was_down = False
    boards = []
    for tick in range(limit):
        if g.state == 'waiting':
            g.launch()
        down = g.vy > 0
        if was_down and not down:
            offset = rng.uniform(-3.8, 3.8)
        was_down = down
        landing = g.x
        if down:
            landing += g.vx * max(0, PADDLE_Y - g.y) / g.vy
            landing %= WIDTH * 2
            if landing > WIDTH:
                landing = WIDTH * 2 - landing
        target = landing - offset
        if abs(target - g.paddle) > 1:
            g.move(1 if target > g.paddle else -1)
        previous = g.board
        g.advance(STEP)
        if g.board != previous or g.state == 'won':
            boards.append((previous, tick, g.score, g.lives))
        if g.state in ('won', 'lost'):
            return g, boards, tick
    raise AssertionError(f'Legal replay exceeded {limit} steps: {g.snapshot()}')


class BreakoutLayoutTests(unittest.TestCase):
    def test_patterns_and_bounds(self):
        self.assertEqual(len(PATTERNS), 3)
        self.assertEqual(len(set(PATTERNS)), 3)
        for index, pattern in enumerate(PATTERNS):
            self.assertEqual(len(pattern), 6)
            self.assertTrue(all(len(row) == 12 and set(row) <= {'#', '.'} for row in pattern))
            bricks = list(bricks_for(index).values())
            for b in bricks:
                self.assertTrue(0 < b.x < b.x + b.width < WIDTH)
                self.assertTrue(0 < b.y < b.y + b.height < PADDLE_Y)
                for other in bricks:
                    if b != other:
                        self.assertFalse(b.x < other.x + other.width and other.x < b.x + b.width
                                         and b.y < other.y + other.height and other.y < b.y + b.height)

    def test_legal_full_clear_and_determinism(self):
        g, boards, ticks = legal_replay()
        h, again, repeated_ticks = legal_replay()
        self.assertEqual((boards, ticks, g.snapshot()), (again, repeated_ticks, h.snapshot()))
        self.assertEqual(g.state, 'won')
        self.assertEqual([b[0] for b in boards], [0, 1, 2])
        expected = 0
        for board, tick, score, lives in boards:
            expected += len(bricks_for(board)) * 10
            self.assertEqual(score, expected)
            self.assertGreater(lives, 0)
        self.assertEqual(g.bricks, {})
        print(f'Legal full-clear replay: seed=20261004, steps={ticks + 1}, boards={boards}')
