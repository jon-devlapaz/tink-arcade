import random
import time
import unittest

from tink_tron.ai import (DIRECTIONS, DOWN, HEIGHT, LEFT, LEVELS, RIGHT, UP, WIDTH, choose, distances,
                          safe_moves, territory)
from tink_tron.engine import Game, STEP


def wall(cells):
    return set(cells)


class TronAITests(unittest.TestCase):
    def test_flood_fill_counts_reachable_cells(self):
        blocked = {(1, 0), (1, 1), (1, 2)}
        reach = distances(blocked, (0, 0), 3, 3)
        self.assertEqual(set(reach), {(0, 0), (0, 1), (0, 2)})
        self.assertEqual(reach[(0, 2)], 2)

    def test_safe_moves_exclude_walls_and_trails(self):
        self.assertEqual(sorted(safe_moves(set(), (0, 0), 5, 5)), sorted([RIGHT, DOWN]))
        self.assertEqual(safe_moves({(1, 0)}, (0, 0), 5, 5), [DOWN])
        self.assertEqual(safe_moves({(1, 0), (0, 1)}, (0, 0), 5, 5), [])

    def test_no_level_steps_into_immediate_death_when_a_safe_move_exists(self):
        rng = random.Random(1)
        for level in LEVELS:
            for seed in range(200):
                r = random.Random(seed)
                cells = {(r.randrange(WIDTH), r.randrange(HEIGHT)) for _ in range(300)}
                me = (r.randrange(WIDTH), r.randrange(HEIGHT))
                opp = (r.randrange(WIDTH), r.randrange(HEIGHT))
                blocked = cells | {me, opp}
                move = choose(blocked, me, opp, RIGHT, level, rng)
                if safe_moves(blocked, me):
                    cell = (me[0] + move[0], me[1] + move[1])
                    self.assertTrue(0 <= cell[0] < WIDTH and 0 <= cell[1] < HEIGHT and cell not in blocked,
                                    f'{level} seed {seed}')

    def test_with_no_safe_move_the_machine_keeps_going(self):
        blocked = {(0, 0), (1, 0), (0, 1)}
        self.assertEqual(choose(blocked, (0, 0), (4, 4), UP, 'hard', random.Random(1), 5, 5), UP)

    def test_normal_prefers_the_larger_pocket(self):
        # The cycle sits in a gap of a full wall. Up is a 14-cell room; down is a sealed 1-cell nook.
        width, height = 7, 5
        blocked = {(x, 2) for x in range(width) if x != 3} | {(3, 2)}
        blocked |= {(2, 3), (4, 3), (3, 4)}
        me = (3, 2)
        self.assertEqual(sorted(safe_moves(blocked, me, width, height)), sorted([UP, DOWN]))
        for level in ('normal', 'hard'):
            self.assertEqual(choose(blocked, me, (6, 0), RIGHT, level, random.Random(1), width, height), UP)

    def test_hard_prefers_the_move_that_claims_more_territory(self):
        # Both moves keep the same flood-fill room; one cuts toward the opponent and claims more.
        width, height = 9, 5
        me, opp = (4, 2), (8, 2)
        blocked = {me, opp}
        rng = random.Random(1)
        pick = choose(blocked, me, opp, UP, 'hard', rng, width, height)
        mine = {m: territory(blocked | {(me[0] + m[0], me[1] + m[1])}, (me[0] + m[0], me[1] + m[1]), opp, width, height)
                for m in safe_moves(blocked, me, width, height)}
        self.assertEqual(mine[pick], max(mine.values()))
        self.assertEqual(pick, RIGHT)
        self.assertGreater(mine[RIGHT], mine[LEFT])

    def test_territory_is_zero_when_the_opponent_is_nearer_everywhere(self):
        self.assertEqual(territory({(0, 0), (1, 0)}, (0, 0), (1, 1), 2, 2), 0)

    def test_machine_decisions_are_seed_deterministic(self):
        def run(level, seed):
            game = Game(seed, level=level)
            for _ in range(600):
                game.update(STEP)
            return dict(game.trails), list(game.scores)
        for level in LEVELS:
            self.assertEqual(run(level, 5), run(level, 5))

    def test_ai_versus_ai_match_terminates_and_replays(self):
        def match(seed):
            # Two identical machines from mirrored starts can draw forever, so pit different levels.
            a = Game(seed, two_player=True)
            rng = random.Random(seed)
            levels = ('hard', 'easy')
            moves = 0
            while a.match_winner is None and moves < 20000:
                if a.round_over:
                    a.next_round()
                for p in (0, 1):
                    direction = choose(set(a.trails), a.heads[p], a.heads[1 - p], a.dirs[p], levels[p], rng)
                    a.turn(p, direction)
                a.update(STEP)
                moves += 1
            return a.scores, a.match_winner, moves
        first = match(3)
        self.assertIsNotNone(first[1])
        self.assertLess(first[2], 20000)
        self.assertEqual(match(3), first)

    def test_decisions_are_fast_on_a_crowded_board(self):
        r = random.Random(2)
        blocked = {(r.randrange(WIDTH), r.randrange(HEIGHT)) for _ in range(250)}
        me, opp = (1, 1), (WIDTH - 2, HEIGHT - 2)
        blocked -= {me, opp, (2, 1), (1, 2)}
        blocked |= {me, opp}
        start = time.perf_counter()
        for _ in range(20):
            choose(blocked, me, opp, RIGHT, 'hard', r)
        self.assertLess((time.perf_counter() - start) / 20, 0.05)


if __name__ == '__main__':
    unittest.main()
