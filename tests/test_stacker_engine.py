import math
import unittest

from tink_stacker.engine import Game, WIDTH, HEIGHT


class StackerRuleTests(unittest.TestCase):
    def supported(self):
        game = Game()
        game.x = 1
        self.assertEqual(game.lock_row(), 'place')
        return game

    def test_first_row_locks_without_support(self):
        game = Game()
        self.assertEqual((WIDTH, HEIGHT, game.width), (7, 15, 3))
        game.x = 4
        self.assertEqual(game.lock_row(), 'place')
        self.assertEqual(game.rows, [(4, 5, 6)])

    def test_moving_row_reflects_at_both_edges(self):
        game = Game()
        for expected in (1, 2, 3, 4, 3, 2, 1, 0, 1):
            game.advance(.240)
            self.assertEqual(game.x, expected)

    def test_lock_retains_only_overlap_and_discards_overhang(self):
        game = self.supported()
        game.x = 3
        self.assertEqual(game.lock_row(), 'place')
        self.assertEqual(game.rows, [(1, 2, 3), (3,)])

    def test_next_row_width_equals_surviving_blocks(self):
        game = self.supported()
        game.x = 0
        game.lock_row()
        self.assertEqual(game.rows[-1], (1, 2))
        self.assertEqual(game.width, 2)
        self.assertEqual((game.x, game.direction), (0, 1))

    def test_zero_overlap_loses_without_advancing(self):
        game = Game()
        game.lock_row()
        game.x = 4
        self.assertEqual(game.lock_row(), 'over')
        self.assertEqual(game.state, 'lost')
        self.assertEqual(game.rows, [(0, 1, 2)])
        self.assertEqual(game.lock_row(), None)
        before = game.snapshot()
        game.advance(.24)
        self.assertEqual(game.snapshot(), before)

    def test_successful_lock_automatically_starts_next_row(self):
        game = Game()
        game.lock_row()
        self.assertEqual(game.state, 'playing')
        self.assertEqual(len(game.rows), 1)
        self.assertEqual((game.x, game.direction, game.accumulator), (4, -1, 0))
        game.advance(.228)
        self.assertEqual(game.x, 3)

    def test_top_row_wins_without_checkpoint_or_payout_choice(self):
        game = Game()
        for index in range(15):
            game.x = 0
            self.assertEqual(game.lock_row(), 'clear' if index == 14 else 'place')
            self.assertEqual(game.state, 'won' if index == 14 else 'playing')
        self.assertEqual(len(game.rows), 15)
        before = game.snapshot()
        game.lock_row(); game.advance(.24)
        self.assertEqual(game.snapshot(), before)

    def test_height_only_speed_curve_and_identical_elapsed_inputs_repeat(self):
        first, second = Game(), Game()
        for height in range(15):
            self.assertAlmostEqual(first.interval, max(.072, .240 - .012 * height))
            for elapsed in (.031, .051, .011):
                first.advance(elapsed); second.advance(elapsed)
                self.assertEqual(first.snapshot(), second.snapshot())
            first.x = second.x = 0
            first.lock_row(); second.lock_row()
            self.assertEqual(first.snapshot(), second.snapshot())

    def test_restart_restores_initial_state(self):
        game = self.supported(); game.advance(.1); game.restart()
        self.assertEqual(game.snapshot(), Game().snapshot())
        snapshot = game.snapshot()
        snapshot['rows'].append([6])
        self.assertEqual(game.rows, [])

    def test_legal_timed_input_replay_reaches_top(self):
        game = Game()
        for height in range(15):
            # Travel from the right edge back to the left on odd rows.
            for _ in range(4 if height % 2 else 0):
                game.advance(game.interval)
            self.assertEqual(game.x, 0)
            game.lock_row()
        self.assertEqual(game.state, 'won')
        self.assertEqual(game.rows, [(0, 1, 2)] * 15)

    def test_fractional_time_and_long_stall_discard(self):
        game = Game()
        game.advance(.12); self.assertEqual(game.x, 0)
        game.advance(.12); self.assertEqual(game.x, 1)
        before = game.snapshot()
        game.advance(10)
        self.assertEqual(game.snapshot(), before)
        for value in (-1, math.nan, math.inf):
            with self.assertRaises(ValueError): game.advance(value)

    def test_engine_does_not_import_io_or_randomness(self):
        import ast
        from pathlib import Path
        tree = ast.parse(Path('tink_stacker/engine.py').read_text())
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        names = [a.name for n in imports if isinstance(n, ast.Import) for a in n.names]
        names += [n.module for n in imports if isinstance(n, ast.ImportFrom)]
        self.assertFalse(set(names) - {'math'})
