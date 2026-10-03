import copy
import unittest

from neon_tetris.engine import Game, HEIGHT, KINDS, Piece, SevenBag, WIDTH


class StrictList(list):
    """Fail if the engine tries Python's negative-index wraparound."""

    def __getitem__(self, index):
        if isinstance(index, int) and not 0 <= index < len(self):
            raise AssertionError(f"invalid read: {index}")
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        if isinstance(index, int) and not 0 <= index < len(self):
            raise AssertionError(f"invalid write: {index}")
        super().__setitem__(index, value)


class SevenBagTests(unittest.TestCase):
    def test_fairness_and_preview(self):
        bag = SevenBag(123)
        for _ in range(20):
            preview = bag.preview()
            drawn = [bag.pop() for _ in range(7)]
            self.assertEqual(tuple(drawn[:3]), preview)
            self.assertEqual(sorted(drawn), sorted(KINDS))
            self.assertGreaterEqual(len(bag.preview()), 3)

    def test_seed_determinism(self):
        a, b, c = SevenBag(42), SevenBag(42), SevenBag(43)
        first = [a.pop() for _ in range(70)]
        self.assertEqual(first, [b.pop() for _ in range(70)])
        self.assertNotEqual(first, [c.pop() for _ in range(70)])


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(7)

    def empty_board(self):
        self.game.board = [[None] * WIDTH for _ in range(HEIGHT)]

    def prepare_clear(self, count):
        self.empty_board()
        for y in range(HEIGHT - count, HEIGHT):
            self.game.board[y] = ["J"] * WIDTH
            self.game.board[y][4] = None
        self.game.active = Piece("I", 2, 16, 1)

    def test_spawn_and_all_piece_rotations_have_four_cells(self):
        for kind in KINDS:
            self.game._spawn(kind)
            self.assertTrue(self.game.fits(self.game.active))
            for rotation in range(4):
                self.assertEqual(len(set(Piece(kind, 3, 0, rotation).cells())), 4)

    def test_collision_and_invalid_access_guard(self):
        game = self.game
        game.board = StrictList(StrictList([None] * WIDTH) for _ in range(HEIGHT))
        self.assertFalse(game.fits(Piece("O", -1, 0)))
        self.assertFalse(game.fits(Piece("O", WIDTH - 1, 0)))
        self.assertFalse(game.fits(Piece("O", 0, HEIGHT - 1)))
        self.assertTrue(game.fits(Piece("O", 0, -1)))
        game.board[0][0] = "I"
        self.assertFalse(game.fits(Piece("O", 0, -1)))
        # Locking an invalid piece must never make an out-of-bounds write.
        for piece in (Piece("O", -1, 2), Piece("O", 9, 2), Piece("O", 0, 20)):
            game.active = piece
            game._lock()
            self.assertTrue(game.game_over)

    def test_wall_and_floor_kicks(self):
        cases = [
            (Piece("T", -1, 3, 1), -1, Piece("T", 0, 3, 0)),
            (Piece("T", 3, 18, 0), 1, Piece("T", 2, 17, 1)),
            (Piece("I", -2, 3, 1), -1, Piece("I", 0, 3, 0)),
            (Piece("I", 3, 18, 0), 1, Piece("I", 4, 16, 1)),
        ]
        for before, direction, after in cases:
            with self.subTest(before=before):
                self.game.active = before
                self.assertTrue(self.game.fits(before))
                self.assertTrue(self.game.rotate(direction))
                self.assertEqual(self.game.active, after)

    def test_rotation_round_trip_and_obstruction(self):
        self.game.active = Piece("T", 3, 5)
        before = self.game.active
        for _ in range(4):
            self.assertTrue(self.game.rotate())
        self.assertEqual(self.game.active, before)
        self.assertTrue(self.game.rotate(-1))
        self.assertTrue(self.game.rotate(1))
        self.assertEqual(self.game.active, before)
        self.game.board = [["Z"] * WIDTH for _ in range(HEIGHT)]
        for x, y in before.cells():
            self.game.board[y][x] = None
        self.assertFalse(self.game.rotate())
        self.assertEqual(self.game.active, before)

    def test_ghost_matches_hard_drop_and_drop_points(self):
        self.game.active = Piece("T", 3, 0)
        self.game.board[18][4] = "J"
        before = self.game.active
        landing = self.game.ghost()
        self.assertEqual(self.game.active, before)
        self.assertTrue(self.game.fits(landing))
        self.assertFalse(self.game.fits(Piece("T", landing.x, landing.y + 1)))
        self.assertTrue(self.game.hard_drop())
        for x, y in landing.cells():
            self.assertEqual(self.game.board[y][x], "T")
        self.assertEqual(self.game.score, (landing.y - before.y) * 2)
        self.assertEqual(self.game.best, self.game.score)

    def test_soft_drop_only_scores_successful_steps(self):
        self.game.active = Piece("O", 4, 17)
        self.assertTrue(self.game.soft_drop())
        self.assertEqual(self.game.score, 1)
        self.assertFalse(self.game.soft_drop())
        self.assertEqual(self.game.score, 1)

    def test_hold_gating_swap_orientation_and_timer_reset(self):
        first = self.game.active.kind
        second = self.game.bag.preview()[0]
        self.game.lock_time = 0.4
        self.game.lock_resets = 14
        self.game.gravity_time = 0.7
        self.assertTrue(self.game.hold())
        self.assertEqual(self.game.held, first)
        self.assertEqual(self.game.active.kind, second)
        self.assertEqual((self.game.lock_time, self.game.gravity_time, self.game.lock_resets),
                         (0, 0, 0))
        state = (self.game.active, self.game.bag.preview(), self.game.held)
        self.assertFalse(self.game.hold())
        self.assertEqual(state, (self.game.active, self.game.bag.preview(), self.game.held))
        self.game.hard_drop()
        self.assertFalse(self.game.hold_used)
        next_kind = self.game.active.kind
        queue = self.game.bag.preview()
        self.game.rotate()
        self.assertTrue(self.game.hold())
        self.assertEqual(self.game.active.kind, first)
        self.assertEqual(self.game.active.rotation, 0)
        self.assertEqual(self.game.active.y, 0)
        self.assertEqual(self.game.held, next_kind)
        self.assertEqual(self.game.bag.preview(), queue)
        self.assertTrue(self.game.soft_drop())  # A held spawn is not frozen.

    def test_hold_spawn_collision_tops_out(self):
        self.game.active = Piece("T", 3, 12)
        self.game.held = "O"
        self.game.board[0][4] = "Z"
        self.assertTrue(self.game.hold())
        self.assertTrue(self.game.game_over)
        self.assertIsNone(self.game.active)

    def test_simultaneous_nonadjacent_line_clearing(self):
        for y in (17, 19):
            self.game.board[y] = ["J"] * WIDTH
            self.game.board[y][4] = None
        self.game.board[15][0] = "Z"
        self.game.active = Piece("I", 2, 16, 1)
        self.game.hard_drop()
        self.assertEqual(self.game.lines, 2)
        self.assertEqual(self.game.score, 300)
        self.assertEqual(self.game.flash_rows, (17, 19))
        self.assertEqual(self.game.board[17][0], "Z")
        self.assertEqual(self.game.board[18][4], "I")
        self.assertEqual(self.game.board[19][4], "I")
        self.assertTrue(all(cell is None for row in self.game.board[:2] for cell in row))
        self.assertEqual(len(self.game.board), HEIGHT)

    def test_scoring_and_level_progression(self):
        for count, points in ((1, 100), (2, 300), (3, 500), (4, 800)):
            with self.subTest(count=count):
                self.game.restart()
                self.prepare_clear(count)
                self.game.hard_drop()
                self.assertEqual(self.game.score, points)
                self.assertEqual(self.game.lines, count)
        self.game.restart()
        self.game.lines = 9
        speed_before = self.game.gravity_interval
        self.prepare_clear(2)
        self.game.hard_drop()
        self.assertEqual((self.game.score, self.game.lines, self.game.level), (300, 11, 2))
        self.assertLess(self.game.gravity_interval, speed_before)
        self.prepare_clear(1)
        self.game.hard_drop()
        self.assertEqual(self.game.score, 500)
        self.game.lines = 10000
        self.assertGreaterEqual(self.game.gravity_interval, 0.055)

    def test_spawn_top_out_and_game_over_actions(self):
        self.game.board[0] = ["J"] * WIDTH
        self.game._spawn("T")
        self.assertTrue(self.game.game_over)
        self.assertFalse(self.game.move(1))
        self.assertFalse(self.game.rotate())
        self.assertFalse(self.game.soft_drop())
        self.assertFalse(self.game.hard_drop())
        self.assertFalse(self.game.hold())
        self.assertIsNone(self.game.ghost())
        self.game.toggle_pause()
        self.assertFalse(self.game.paused)

    def test_above_board_lock_out_is_atomic(self):
        self.game.board = StrictList(StrictList([None] * WIDTH) for _ in range(HEIGHT))
        self.game.board[1][4] = "J"
        self.game.active = Piece("O", 4, -1)
        before = copy.deepcopy(self.game.board)
        self.assertTrue(self.game.grounded())
        self.game.hard_drop()
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.board, before)
        self.assertTrue(all(cell is None for cell in self.game.board[HEIGHT - 1]))

    def test_gravity_pause_and_bounded_time(self):
        before = self.game.active
        for _ in range(4):
            self.game.update(0.2)
        self.assertEqual(self.game.active.y, before.y + 1)
        self.game.toggle_pause()
        state = copy.deepcopy(self.game.__dict__)
        self.game.update(100)
        self.assertFalse(self.game.move(1))
        self.assertFalse(self.game.rotate())
        self.assertFalse(self.game.hard_drop())
        self.assertFalse(self.game.soft_drop())
        self.assertFalse(self.game.hold())
        for key in ("board", "active", "score", "gravity_time", "lock_time", "message_time"):
            self.assertEqual(getattr(self.game, key), state[key])
        self.game.toggle_pause()
        self.game.update(0.01)
        self.assertEqual(self.game.active, state["active"])
        self.game.update(100)
        self.assertLessEqual(self.game.active.y, state["active"].y + 1)
        timer = self.game.gravity_time
        self.game.update(-5)
        self.assertEqual(self.game.gravity_time, timer)

    def test_lock_delay_and_bounded_resets(self):
        self.game.active = Piece("O", 4, 18)
        for index in range(self.game.MAX_LOCK_RESETS):
            self.game.update(0.2)
            self.assertTrue(self.game.move(-1 if index % 2 == 0 else 1))
            self.assertEqual(self.game.lock_time, 0)
        self.assertEqual(self.game.lock_resets, self.game.MAX_LOCK_RESETS)
        self.game.update(0.25)
        self.game.move(1)
        self.assertEqual(self.game.lock_time, 0.25)
        self.game.update(0.2)
        self.assertEqual(sum(bool(cell) for row in self.game.board for cell in row), 4)
        self.assertEqual(self.game.lock_time, 0)
        self.assertEqual(self.game.lock_resets, 0)

    def test_floor_kick_cycles_cannot_bypass_lock_budget(self):
        game = self.game
        game.active = Piece("T", 3, 17, 0)
        actions = (game.soft_drop, lambda: game.rotate(1),
                   lambda: game.rotate(-1), lambda: game.move(1))
        for _ in range(30):
            for action in actions:
                self.assertTrue(action())
                if any(cell for row in game.board for cell in row):
                    break
            if any(cell for row in game.board for cell in row):
                break
            game.update(0.1)
        self.assertEqual(sum(bool(cell) for row in game.board for cell in row), 4)
        self.assertLess(game.score, 30)
        self.assertEqual((game.lock_time, game.lock_resets), (0, 0))

    def test_exhausted_lock_timer_survives_lift_off_and_soft_drop_contact(self):
        game = self.game
        game.active = Piece("T", 3, 17, 0)
        game.lock_resets = game.MAX_LOCK_RESETS
        game.lock_time = 0.4
        self.assertFalse(game.grounded())
        game.update(0.1)
        self.assertGreaterEqual(game.lock_time, game.LOCK_DELAY)
        self.assertTrue(all(cell is None for row in game.board for cell in row))
        self.assertTrue(game.soft_drop())
        self.assertEqual(sum(bool(cell) for row in game.board for cell in row), 4)
        self.assertEqual(game.score, 1)
        self.assertEqual((game.lock_time, game.lock_resets), (0, 0))

    def test_exhausted_deadline_locks_on_rotation_and_move_contact(self):
        game = self.game
        for action in ("rotate", "move"):
            with self.subTest(action=action):
                game.restart()
                if action == "rotate":
                    game.active = Piece("T", 3, 17, 0)
                    landing = Piece("T", 3, 17, 1)
                else:
                    game.active = Piece("T", 3, 16, 0)
                    game.board[18][2] = "J"
                    landing = Piece("T", 2, 16, 0)
                self.assertFalse(game.grounded())
                game.lock_resets = game.MAX_LOCK_RESETS
                game.lock_time = game.LOCK_DELAY + 0.1
                self.assertTrue(game.rotate(1) if action == "rotate" else game.move(-1))
                for x, y in landing.cells():
                    self.assertEqual(game.board[y][x], "T")
                self.assertEqual((game.lock_time, game.lock_resets), (0, 0))

    def test_failed_moves_do_not_reset_lock(self):
        self.game.active = Piece("O", 0, 18)
        self.game.update(0.2)
        self.assertFalse(self.game.move(-1))
        self.assertEqual(self.game.lock_time, 0.2)
        self.assertEqual(self.game.lock_resets, 0)

    def test_restart_resets_play_state_and_preserves_session_best(self):
        original = (self.game.active, self.game.bag.preview())
        self.game.hard_drop()
        best = self.game.score
        self.game.hold()
        self.game.toggle_pause()
        self.game.restart()
        self.assertEqual((self.game.active, self.game.bag.preview()), original)
        self.assertEqual(self.game.best, best)
        self.assertEqual((self.game.score, self.game.lines, self.game.level), (0, 0, 1))
        self.assertIsNone(self.game.held)
        self.assertFalse(self.game.hold_used)
        self.assertFalse(self.game.paused)
        self.assertFalse(self.game.game_over)
        self.assertEqual(self.game.flash_time, 0)
        self.assertTrue(all(cell is None for row in self.game.board for cell in row))


if __name__ == "__main__":
    unittest.main()
