"""Rule examples with explicit collision setups; full legal play is tested separately."""
import math
import unittest
from tink_breakout.engine import Game, STEP, SPEED, WIDTH, HEIGHT, PADDLE_Y


class BreakoutEngineTests(unittest.TestCase):
    def test_start_launch_and_invalid_time(self):
        g = Game()
        self.assertEqual((g.score, g.lives, g.board, g.state), (0, 3, 0, 'waiting'))
        before = g.snapshot()
        g.advance(1)
        self.assertEqual(before, g.snapshot())
        for dt in (-1, float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                g.advance(dt)
        g.launch()
        g.advance(STEP)
        self.assertLess(g.y, PADDLE_Y)

    def test_fast_brick_crossing_scores_once(self):
        g = Game()
        brick = list(g.bricks.values())[-1]
        g.x, g.y = brick.x + 2, brick.y + 2
        g.vx, g.vy, g.state = 0, -1000, 'playing'
        count = len(g.bricks)
        g.advance(STEP)
        self.assertEqual((len(g.bricks), g.score, g.lives, g.board), (count - 1, 10, 3, 0))
        self.assertGreater(g.vy, 0)
        g.advance(STEP)
        self.assertEqual(g.score, 10)

    def test_tied_bricks_and_corner_reflect_once(self):
        g = Game()
        bricks = list(g.bricks.values())[:2]
        g.bricks = {b.id: b for b in bricks}
        # Shared face at x=10 touches both adjacent bricks.
        g.x, g.y, g.vx, g.vy, g.state = 10, 3.5, 0, -SPEED, 'playing'
        g.advance(.05)
        self.assertEqual((g.score, g.board, g.state), (20, 1, 'waiting'))
        g = Game()
        b = next(iter(g.bricks.values()))
        g.x, g.y, g.vx, g.vy, g.state = b.x - .1, b.y + b.height + .1, 12, -12, 'playing'
        g.advance(.02)
        self.assertLess(g.vx, 0)
        self.assertGreater(g.vy, 0)
        self.assertEqual(g.score, 10)

    def test_wall_and_paddle_center_edges(self):
        for x, vx in ((.01, -SPEED), (WIDTH - .01, SPEED)):
            g = Game(); g.x, g.y, g.vx, g.vy, g.state = x, 12, vx, 0, 'playing'
            g.advance(STEP)
            self.assertEqual(math.copysign(1, g.vx), -math.copysign(1, vx))
            self.assertTrue(0 <= g.x <= WIDTH)
        for offset in (-4.5, 0, 4.5):
            g = Game(); g.x, g.y = g.paddle + offset, PADDLE_Y - .01
            g.vx, g.vy, g.state = 0, SPEED, 'playing'
            g.advance(STEP)
            self.assertLess(g.vy, 0)
            self.assertAlmostEqual(math.hypot(g.vx, g.vy), SPEED)
            self.assertGreaterEqual(abs(g.vy), SPEED * .49)
            if offset:
                self.assertEqual(math.copysign(1, g.vx), math.copysign(1, offset))
            else:
                self.assertAlmostEqual(g.vx, 0)

    def test_loss_keeps_progress_and_stops_at_zero(self):
        g = Game(); g.score = 10; g.bricks.pop(next(iter(g.bricks)))
        count = len(g.bricks)
        for lives in (2, 1, 0):
            g.x, g.y, g.vx, g.vy, g.state = 1, HEIGHT - .01, 0, SPEED, 'playing'
            g.advance(.2)
            self.assertEqual((g.lives, g.score, len(g.bricks), g.board), (lives, 10, count, 0))
            self.assertEqual(g.state, 'waiting' if lives else 'lost')
            before = g.snapshot(); g.advance(1)
            self.assertEqual(before, g.snapshot())

    def test_only_last_brick_advances_and_final_wins(self):
        for board in range(3):
            g = Game(); g.board = board
            b = next(iter(g.bricks.values()))
            g.bricks = {b.id: b}
            g.x, g.y, g.vx, g.vy, g.state = b.x + 2, b.y + 1, 0, -SPEED, 'playing'
            g.advance(.03)
            self.assertEqual((g.score, g.lives), (10, 3))
            self.assertEqual((g.board, g.state), (board + 1, 'waiting') if board < 2 else (2, 'won'))
        g = Game(); g.launch(); g.advance(STEP)
        self.assertEqual(g.board, 0)

    def test_each_brick_face_and_ceiling(self):
        for x, y, vx, vy, expected in (
                (8, 1.9, 0, SPEED, (0, -1)),
                (8, 2.85, 0, -SPEED, (0, 1)),
                (5.9, 2.4, SPEED, 0, (-1, 0)),
                (10.1, 2.4, -SPEED, 0, (1, 0))):
            g = Game()
            bricks = list(g.bricks.values())
            g.bricks = {b.id: b for b in (bricks[0], bricks[-1])}
            g.x, g.y, g.vx, g.vy, g.state = x, y, vx, vy, 'playing'
            g.advance(.02)
            self.assertEqual((g.score, len(g.bricks), g.board, g.lives), (10, 1, 0, 3))
            self.assertAlmostEqual(g.vx, expected[0] * SPEED)
            self.assertAlmostEqual(g.vy, expected[1] * SPEED)
            g.advance(.02)
            self.assertEqual(g.score, 10)
        g = Game()
        g.x, g.y, g.vx, g.vy, g.state = 1, .01, 0, -SPEED, 'playing'
        g.advance(STEP)
        self.assertGreater(g.vy, 0)
        self.assertGreaterEqual(g.y, 0)

    def test_paddle_bounds_and_terminal_states(self):
        g = Game()
        for direction, expected in ((-1, 4.5), (1, WIDTH - 4.5)):
            for _ in range(100):
                old = g.paddle
                g.move(direction)
                self.assertLessEqual(abs(g.paddle - old), 2)
            self.assertEqual(g.paddle, expected)
            self.assertEqual(g.x, expected)
        for state in ('won', 'lost'):
            g.state = state
            before = g.snapshot()
            g.move(1); g.launch(); g.advance(100)
            self.assertEqual(g.snapshot(), before)

    def test_bounded_elapsed_and_restart(self):
        g, h = Game(), Game(); g.launch(); h.launch()
        g.advance(1000); h.advance(.1)
        self.assertEqual(g.snapshot(), h.snapshot())
        for state in ('playing', 'paused', 'won', 'lost'):
            g.state, g.score, g.lives, g.board = state, 400, 1, 2
            g.restart()
            self.assertEqual(g.snapshot(), Game().snapshot())
