import unittest
from tink_snake.engine import Game, UP, DOWN, LEFT, RIGHT


class SnakeRulesTests(unittest.TestCase):
    def test_initial_movement_growth_and_food_exclusion(self):
        g = Game(7)
        self.assertEqual(g.snake, [(10, 10), (9, 10), (8, 10)])
        self.assertNotIn(g.food, g.snake)
        self.assertIsNone(g.update(.18))
        self.assertEqual(g.snake, [(11, 10), (10, 10), (9, 10)])
        g.food = (12, 10)
        self.assertEqual(g.update(.18), 'clear')
        self.assertEqual((g.score, g.best, len(g.snake)), (10, 10, 4))
        self.assertNotIn(g.food, g.snake)

    def test_food_uniform_selection_uses_all_free_cells(self):
        from unittest.mock import Mock
        g = Game(1); g.rng = Mock(); g.rng.choice.side_effect = lambda cells: cells[-1]
        self.assertEqual(g._food(), (19, 19))
        candidates = g.rng.choice.call_args.args[0]
        self.assertEqual(len(candidates), 397)
        self.assertEqual(set(candidates), {(x, y) for x in range(20) for y in range(20)} - set(g.snake))

    def test_queue_order_reverse_duplicates_and_overflow(self):
        g = Game(1)
        self.assertFalse(g.turn(LEFT)); self.assertFalse(g.turn(RIGHT))
        self.assertTrue(g.turn(UP)); self.assertFalse(g.turn(DOWN)); self.assertFalse(g.turn(UP))
        self.assertTrue(g.turn(LEFT)); self.assertFalse(g.turn(DOWN))
        self.assertEqual(g.update(.18), 'move'); self.assertEqual(g.snake[0], (10, 9))
        self.assertEqual(g.update(.18), 'move'); self.assertEqual(g.snake[0], (9, 9))
        self.assertEqual(g.direction, LEFT)

    def test_tail_departure_is_legal_but_body_collision_ends_game(self):
        g = Game(1); g.snake = [(1, 1), (1, 2), (0, 2), (0, 1)]; g.direction = LEFT; g.food = (5, 5)
        self.assertIsNone(g.update(.18)); self.assertFalse(g.game_over)
        g.snake = [(1, 1), (1, 2), (0, 2), (0, 1), (0, 0)]; g.direction = LEFT
        self.assertEqual(g.update(.18), 'over'); self.assertTrue(g.game_over)
        before = list(g.snake); self.assertIsNone(g.update(100)); self.assertEqual(before, g.snake)
        self.assertFalse(g.turn(UP)); self.assertFalse(g.toggle_pause())

    def test_each_wall_collision(self):
        for head, direction in (((0, 5), LEFT), ((19, 5), RIGHT), ((5, 0), UP), ((5, 19), DOWN)):
            g = Game(1); g.snake = [head]; g.direction = direction
            self.assertEqual(g.update(.18), 'over')
            self.assertTrue(g.game_over)

    def test_full_board_has_no_food_and_freezes(self):
        g = Game(1)
        g.snake = [(18, 19)] + [(x, y) for y in range(20) for x in range(20) if (x, y) not in ((18, 19), (19, 19))]
        g.food = (19, 19)
        self.assertEqual(g.update(.18), 'clear')
        self.assertTrue(g.complete); self.assertIsNone(g.food); self.assertEqual(len(g.snake), 400)
        before = list(g.snake); g.update(30); self.assertEqual(before, g.snake)
        self.assertFalse(g.toggle_pause()); self.assertFalse(g.turn(UP))

    def test_speed_boundaries_and_new_interval_after_food(self):
        g = Game(1)
        for foods, interval in ((0, .18), (4, .18), (5, .165), (34, .09), (35, .075), (200, .075)):
            g.foods = foods; self.assertAlmostEqual(g.interval, interval)
        g.foods = 4; g.food = (11, 10)
        g.update(.179); self.assertEqual(g.foods, 4)
        g.update(.001); self.assertEqual(g.foods, 5); self.assertAlmostEqual(g.interval, .165)

    def test_pause_remaining_timer_and_delayed_frame_cap(self):
        g = Game(1); g.update(.1); g.turn(UP); g.toggle_pause()
        self.assertFalse(g.turn(DOWN)); self.assertFalse(g.turns)
        g.update(20); self.assertAlmostEqual(g.elapsed, .1)
        g.toggle_pause(); g.update(.079); self.assertEqual(g.snake[0], (10, 10))
        g.update(.001); self.assertEqual(g.snake[0], (11, 10))
        g.update(50); self.assertEqual(g.snake[0], (12, 10))
        self.assertLess(g.elapsed, g.interval)

    def test_restart_resets_state_and_repeats_seed_preserving_best(self):
        g = Game(5); first = g.food; g.food = (11, 10); g.update(.18); second = g.food
        g.turn(UP); g.toggle_pause(); g.game_over = True; g.complete = True; g.restart()
        self.assertEqual(g.food, first); self.assertEqual(g.best, 10)
        self.assertEqual((g.score, g.foods, g.elapsed), (0, 0, 0))
        self.assertFalse(g.turns or g.paused or g.game_over or g.complete)
        g.food = (11, 10); g.update(.18); self.assertEqual(g.food, second)
