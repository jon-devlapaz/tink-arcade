import ast
import math
from pathlib import Path
import unittest

from tink_last_time.engine import Game, WIDTH, HEIGHT, ROUND_TICKS, TICK_SECONDS, SPARK_COUNT


class LastTimeRules(unittest.TestCase):
    def advance_ticks(self, game, count):
        for _ in range(count):
            game.advance(TICK_SECONDS)

    def test_collectible_sparks(self):
        game = Game(7)
        target = min(game.sparks)
        for axis in (0, 1):
            while game.player[axis] != target[axis]:
                delta = 1 if game.player[axis] < target[axis] else -1
                game.steer((delta, 0) if axis == 0 else (0, delta))
                game.advance(TICK_SECONDS)
        self.assertEqual(game.player, target)
        self.assertGreaterEqual(game.score, 1)
        self.assertEqual(len(game.sparks), SPARK_COUNT)
        self.assertNotIn(game.player, game.sparks)
        self.assertEqual(game.state, 'playing')

    def test_fifteen_second_round(self):
        game = Game(7)
        self.assertEqual(ROUND_TICKS * TICK_SECONDS, 15)
        self.advance_ticks(game, 149)
        self.assertEqual((game.round, game.tick, len(game.paths)), (1, 149, 0))
        game.advance(.099)
        self.assertEqual(game.round, 1)
        game.advance(.001)
        self.assertEqual((game.round, game.tick, len(game.paths)), (2, 0, 1))
        self.assertEqual(len(game.paths[0]), 151)

    def test_exact_replay(self):
        game = Game(7)
        recorded = [game.player]
        for tick in range(150):
            game.steer((1, 0) if tick < 20 else (0, -1))
            game.advance(.1)
            if tick < 149:
                recorded.append(game.player)
        recorded.append((WIDTH - 1, 0))
        self.assertEqual(game.paths[0], tuple(recorded))
        for tick in range(50):
            self.assertEqual(game.ghosts, (recorded[tick],))
            game.steer((-1, 0) if tick < 20 else (0, 1))
            game.advance(.1)
            self.assertEqual(game.state, 'playing')

    def test_any_ghost_contact_is_fatal(self):
        for index in (0, 1, 2):
            game = Game(7)
            far = ((0, 0),) * 151
            hit = ((16, 9),) * 151
            game.paths = [far, far, far]
            game.paths[index] = hit
            game.steer((1, 0))
            game.advance(.1)
            self.assertEqual(game.state, 'lost')
            before = game.snapshot()
            game.steer((-1, 0))
            game.advance(.2)
            self.assertEqual(game.snapshot(), before)

    def test_swapping_cells_and_stationary_contacts_kill(self):
        game = Game(7)
        game.paths = [((16, 9), (15, 9)) + ((0, 0),) * 149]
        game.steer((1, 0))
        game.advance(.1)
        self.assertEqual(game.state, 'lost')
        game = Game(7)
        game.paths = [((0, 0), (15, 9)) + ((0, 0),) * 149]
        game.advance(.1)
        self.assertEqual(game.state, 'lost')

    def test_stacking_keeps_all_paths_through_round_five(self):
        game = Game(7)
        # Remaining still records a real path; boundary relocation avoids the
        # origins. With no input every new path differs from all earlier paths.
        for number in range(1, 5):
            self.advance_ticks(game, 150)
            self.assertEqual(game.state, 'playing')
            self.assertEqual(len(game.paths), number)
            self.assertEqual(game.round, number + 1)
            self.assertEqual(game.ghosts, tuple(p[0] for p in game.paths))
        first = game.paths[0]
        self.advance_ticks(game, 10)
        self.assertEqual(game.paths[0], first)
        self.assertEqual(len(game.ghosts), 4)

    def test_boundary_keeps_endpoint_unless_occupied(self):
        game = Game(7)
        game.steer((1, 0))
        self.advance_ticks(game, 150)
        self.assertEqual(game.player, (WIDTH - 1, HEIGHT // 2))
        self.assertEqual(game.path, [game.player])
        closed = Game(7)
        start = closed.player
        self.advance_ticks(closed, 150)
        self.assertNotEqual(closed.player, start)
        self.assertNotIn(closed.player, closed.ghosts)
        self.assertEqual(closed.paths[0], (start,) * 151)
        self.assertGreater(abs(closed.player[0] - start[0]) + abs(closed.player[1] - start[1]), 1)
        closed.advance(.1)
        self.assertEqual(closed.state, 'playing')

    def test_fully_occupied_origins_end_without_crashing(self):
        game = Game(7)
        game.paths = [((x, y),) * 151 for y in range(HEIGHT) for x in range(WIDTH)]
        game._safe_origin()
        self.assertEqual(game.state, 'lost')
        before = game.snapshot()
        game.advance(.1)
        self.assertEqual(game.snapshot(), before)

    def test_score_only_counts_sparks(self):
        game = Game(7)
        game.sparks = {(16, 9), (17, 9), (0, 0), (0, 1), (0, 2), (0, 3)}
        self.advance_ticks(game, 10)
        self.assertEqual(game.score, 0)
        game.steer((1, 0))
        game.advance(.1)
        self.assertEqual(game.score, 1)
        game.advance(.1)
        self.assertEqual(game.score, 2)
        game.steer((0, -1))
        game.advance(.1)
        self.assertEqual(game.score, 2)
        # Fatal contacts do not award an extra spark.
        game.paths = [((17, 7),) * 151]
        game.sparks.add((17, 7))
        game.advance(.1)
        self.assertEqual((game.score, game.state), (2, 'lost'))

    def test_walls_stop_without_losing_and_restart_repeats_seed(self):
        game = Game(7)
        self.assertEqual(game.direction, (0, 0))
        game.steer((-1, 0))
        self.advance_ticks(game, 40)
        self.assertEqual(game.player, (0, 9))
        self.assertEqual(game.state, 'playing')
        game.restart()
        self.assertEqual(game.snapshot(), Game(7).snapshot())
        self.assertEqual(game.paths, [])

    def test_time_partitioning_stalls_and_invalid_boundaries(self):
        first, second = Game(7), Game(7)
        first.steer((1, 0)); second.steer((1, 0))
        for _ in range(40):
            first.advance(.1)
            for dt in (.031, .051, .018):
                second.advance(dt)
        self.assertEqual(first.snapshot(), second.snapshot())
        before = first.snapshot()
        first.advance(10)
        self.assertEqual(first.snapshot(), before)
        for invalid in (-.01, math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                first.advance(invalid)
        for invalid in ((1, 1), (0, 0), 'right', None):
            with self.assertRaises(ValueError):
                first.steer(invalid)

    def test_snapshot_is_detached_and_engine_has_no_io(self):
        game = Game(7)
        snap = game.snapshot()
        snap['player'][0] = -1
        snap['sparks'].clear()
        self.assertNotEqual(game.player[0], -1)
        self.assertEqual(len(game.sparks), 6)
        tree = ast.parse(Path('tink_last_time/engine.py').read_text())
        names = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        names |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
        self.assertLessEqual(names, {'math', 'random'})
