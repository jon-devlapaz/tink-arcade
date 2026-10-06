import unittest
from unittest.mock import patch

from tink_tron.engine import Game, STEP, WINS, STARTS
from tink_tron.ai import RIGHT, LEFT, UP, DOWN, WIDTH, HEIGHT


def duel(**kwargs):
    return Game(1, two_player=True, **kwargs)


def tick(game, steps=1):
    cue = None
    for _ in range(steps):
        cue = game.update(STEP) or cue
    return cue


class TronEngineTests(unittest.TestCase):
    def test_start_positions_and_trails(self):
        g = duel()
        self.assertEqual(g.heads, [(6, 10), (31, 10)])
        self.assertEqual(g.dirs, [RIGHT, LEFT])
        self.assertEqual(g.trails, {(6, 10): 0, (31, 10): 1})
        self.assertEqual((g.scores, g.round, g.round_over, g.paused), ([0, 0], 1, False, False))

    def test_both_cycles_move_together_and_leave_trails(self):
        g = duel()
        tick(g)
        self.assertEqual(g.heads, [(7, 10), (30, 10)])
        self.assertEqual(g.trails[(6, 10)], 0)
        self.assertEqual(g.trails[(31, 10)], 1)
        self.assertEqual(len(g.trails), 4)

    def test_no_step_until_a_full_interval_has_elapsed(self):
        g = duel()
        self.assertIsNone(g.update(STEP / 2))
        self.assertEqual(g.heads[0], (6, 10))
        g.update(STEP / 2)
        self.assertEqual(g.heads[0], (7, 10))

    def test_a_delayed_frame_counts_for_at_most_one_step(self):
        g = duel()
        g.update(5.0)
        self.assertEqual(g.heads[0], (7, 10))
        self.assertAlmostEqual(g.elapsed, STEP)

    def test_wall_collision_loses_the_round(self):
        g = duel()
        g.turn(0, UP)
        tick(g)
        tick(g, 10)
        self.assertTrue(g.round_over)
        self.assertEqual(g.winner, 1)
        self.assertEqual(g.scores, [0, 1])
        self.assertTrue(g.crashed[0] and not g.crashed[1])

    def test_trail_collision_loses_the_round(self):
        g = duel()
        for player, direction in ((0, UP), (1, UP)):
            g.turn(player, direction)
        tick(g, 2)
        g.turn(0, RIGHT); g.turn(1, LEFT)
        tick(g)
        g.turn(0, DOWN)
        tick(g)
        g.turn(0, LEFT)
        tick(g)  # steps back through its own trail
        self.assertTrue(g.round_over)
        self.assertEqual(g.winner, 1)

    def test_head_on_is_a_draw_that_scores_nobody(self):
        g = Game(1, two_player=True)
        g.heads, g.dirs = [(10, 10), (12, 10)], [RIGHT, LEFT]
        g.trails = {(10, 10): 0, (12, 10): 1}
        cue = tick(g)
        self.assertTrue(g.round_over)
        self.assertIsNone(g.winner)
        self.assertEqual(g.scores, [0, 0])
        self.assertEqual(cue, 'over')
        self.assertTrue(all(g.crashed))

    def test_swapping_cells_is_a_draw(self):
        g = Game(1, two_player=True)
        g.heads, g.dirs = [(10, 10), (11, 10)], [RIGHT, LEFT]
        g.trails = {(10, 10): 0, (11, 10): 1}
        tick(g)
        self.assertTrue(g.round_over)
        self.assertIsNone(g.winner)

    def test_a_draw_replays_the_same_round_number(self):
        g = Game(1, two_player=True)
        g.heads, g.dirs = [(10, 10), (12, 10)], [RIGHT, LEFT]
        g.trails = {(10, 10): 0, (12, 10): 1}
        tick(g)
        self.assertEqual(g.round, 1)
        self.assertTrue(g.next_round())
        self.assertEqual((g.round, g.heads, g.round_over), (1, list(STARTS), False))

    def test_first_to_three_wins_the_match(self):
        g = duel()
        for expected in range(1, WINS + 1):
            g.turn(0, UP)
            tick(g, 12)
            self.assertEqual(g.scores[1], expected)
            if expected < WINS:
                self.assertIsNone(g.match_winner)
                self.assertTrue(g.next_round())
        self.assertEqual(g.match_winner, 1)
        self.assertFalse(g.next_round())

    def test_round_number_stays_on_the_round_whose_result_is_showing(self):
        g = duel()
        g.turn(0, UP)
        tick(g, 12)
        self.assertEqual((g.round_over, g.round), (True, 1))
        g.next_round()
        self.assertEqual(g.round, 2)

    def test_next_round_only_after_a_round_ends(self):
        g = duel()
        self.assertFalse(g.next_round())

    def test_reversal_and_repeat_are_ignored(self):
        g = duel()
        self.assertFalse(g.turn(0, LEFT))
        self.assertFalse(g.turn(0, RIGHT))
        self.assertFalse(g.turn(0, (2, 0)))
        self.assertTrue(g.turn(0, UP))

    def test_only_one_buffered_turn_so_two_quick_presses_cannot_reverse(self):
        g = duel()
        self.assertTrue(g.turn(0, UP))
        self.assertFalse(g.turn(0, LEFT))
        tick(g)
        self.assertEqual(g.dirs[0], UP)
        self.assertTrue(g.turn(0, LEFT))

    def test_turn_changes_direction_on_the_next_step_and_cues_move(self):
        g = duel()
        g.turn(0, DOWN)
        self.assertEqual(g.dirs[0], RIGHT)
        self.assertEqual(tick(g), 'move')
        self.assertEqual((g.dirs[0], g.heads[0]), (DOWN, (6, 11)))

    def test_straight_movement_is_silent(self):
        self.assertIsNone(tick(duel()))

    def test_solo_game_gives_the_machine_no_keyboard(self):
        g = Game(1)
        self.assertFalse(g.turn(1, UP))
        self.assertTrue(g.turn(0, UP))

    def test_solo_machine_steers_away_from_a_wall(self):
        g = Game(1, level='normal')
        g.heads, g.dirs = [(6, 10), (0, 10)], [RIGHT, LEFT]
        g.trails = {(6, 10): 0, (0, 10): 1}
        tick(g)
        self.assertFalse(g.round_over)
        self.assertNotEqual(g.dirs[1], LEFT)
        self.assertTrue(g.heads[1] != (0, 10))

    def test_two_player_has_no_machine(self):
        g = duel()
        g.heads, g.dirs = [(6, 10), (0, 10)], [RIGHT, LEFT]
        g.trails = {(6, 10): 0, (0, 10): 1}
        tick(g)
        self.assertTrue(g.round_over)
        self.assertEqual(g.winner, 0)

    def test_machine_reads_the_board_not_the_pending_key(self):
        g = Game(1)
        g.turn(0, UP)
        with patch('tink_tron.engine.choose', return_value=LEFT) as chosen:
            tick(g)
        trails, me, opponent, direction = chosen.call_args.args[:4]
        self.assertEqual((me, opponent, direction), ((31, 10), (6, 10), LEFT))  # the player's head has not yet moved up
        self.assertEqual(trails, {(6, 10), (31, 10)})
        self.assertEqual(g.dirs[0], UP)

    def test_two_player_gives_both_players_a_keyboard(self):
        g = duel()
        self.assertTrue(g.turn(0, UP) and g.turn(1, DOWN))

    def test_pause_freezes_time_and_blocks_turns(self):
        g = duel()
        self.assertTrue(g.toggle_pause())
        before = (list(g.heads), g.elapsed, g.acc)
        self.assertIsNone(g.update(1))
        self.assertFalse(g.turn(0, UP))
        self.assertEqual((g.heads, g.elapsed, g.acc), before)
        g.toggle_pause()
        self.assertFalse(g.paused)

    def test_cannot_pause_between_rounds(self):
        g = duel()
        g.turn(0, UP)
        tick(g, 12)
        self.assertFalse(g.toggle_pause())

    def test_restart_clears_the_match_and_repeats_the_machine(self):
        def play(g):
            tick(g, 400)
            return list(g.heads), dict(g.trails), list(g.scores)
        g = Game(7)
        first = play(g)
        g.restart()
        self.assertEqual((g.scores, g.round, g.match_winner, g.paused), ([0, 0], 1, None, False))
        self.assertEqual(play(g), first)

    def test_unknown_level_is_refused(self):
        with self.assertRaises(ValueError):
            Game(1, level='nightmare')

    def test_solo_cues(self):
        win = Game(1)
        win.heads, win.dirs = [(10, 10), (0, 0)], [RIGHT, UP]
        win.trails = {(10, 10): 0, (0, 0): 1, (1, 0): 1, (0, 1): 1}  # boxed in: no safe move
        self.assertEqual(tick(win), 'clear')
        lose = Game(1)
        lose.heads, lose.dirs = [(0, 0), (10, 10)], [UP, RIGHT]
        lose.trails = {(0, 0): 0, (10, 10): 1}
        self.assertEqual(tick(lose), 'over')
        self.assertEqual(lose.winner, 1)

    def test_a_round_never_leaves_the_grid(self):
        g = Game(3, level='easy')
        tick(g, 2000)
        self.assertTrue(all(0 <= x < WIDTH and 0 <= y < HEIGHT for x, y in g.trails))


if __name__ == '__main__':
    unittest.main()
