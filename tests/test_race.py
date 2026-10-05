import copy
import unittest
from unittest.mock import patch

from neon_tetris.engine import Game, Piece
from neon_tetris.jev import Reply
from neon_tetris.race import Race, options, place


class ManualWorker:
    def __init__(self):
        self.busy = False
        self.calls = []
        self.result = None

    def submit(self, identity, state, criteria):
        assert not self.busy
        self.busy = True
        self.calls.append((identity, state, criteria))

    def answer(self, choice=None, error='', tokens=100):
        identity, _, criteria = self.calls[-1]
        self.result = identity, Reply(choice or next(iter(criteria)), 'jev-1.13.0', tokens, error)

    def poll(self):
        result, self.result = self.result, None
        if result:
            self.busy = False
        return result


def almost_won(game):
    game.lines = 19
    game.board[-1] = ['J'] * 6 + [None] * 4
    game.active = Piece('I', 6, 0)


class RaceTests(unittest.TestCase):
    def setUp(self):
        self.worker = ManualWorker()
        self.race = Race(self.worker, 1)

    def test_same_sequence_including_without_seed(self):
        for seed in (None, 9):
            race = Race(ManualWorker(), seed)
            self.assertEqual(race.human.active, race.jev.active)
            self.assertEqual([race.human.bag.pop() for _ in range(30)],
                             [race.jev.bag.pop() for _ in range(30)])

    def test_every_option_is_legal_and_enumeration_does_not_mutate(self):
        for seed in range(14):
            game = Game(seed)
            before = copy.deepcopy(game.__dict__)
            moves, criteria = options(game)
            self.assertGreater(len(moves), 8)
            self.assertEqual(moves.keys(), criteria.keys())
            for move in moves.values():
                self.assertTrue(place(copy.deepcopy(game), move))
            self.assertEqual(game.board, before['board'])
            self.assertEqual(game.active, before['active'])
            self.assertEqual(game.bag.preview(7), before['bag'].preview(7))

    def test_responsive_while_waiting_and_only_one_inflight(self):
        self.race.tick(0)
        start = self.race.human.active.x
        for _ in range(5):
            self.race.tick(.2, [('move', (-1,))])
        self.assertLess(self.race.human.active.x, start)
        self.assertGreater(self.race.human.active.y, 0)
        self.assertEqual(len(self.worker.calls), 1)

    def test_pause_freezes_both_and_defers_reply_but_counts_cost(self):
        self.race.tick(0)
        self.race.toggle_pause()
        before = self.race.jev.active
        self.worker.answer()
        self.race.tick(10, [('hard_drop', ())])
        self.assertEqual(self.race.human.lines, 0)
        self.assertEqual(self.race.jev.active, before)
        self.assertEqual(self.race.cost.responses, 1)
        self.assertEqual(len(self.worker.calls), 1)
        self.race.toggle_pause()
        self.race.tick(0)
        self.assertGreater(self.race.jev.generation, 1)

    def test_error_freezes_both_until_explicit_retry(self):
        self.race.tick(0)
        before = self.race.human.active, self.race.jev.active
        self.worker.answer(error='timeout', tokens=None)
        self.race.tick(10, [('hard_drop', ())])
        self.assertEqual((self.race.human.active, self.race.jev.active), before)
        self.assertEqual(self.race.error, 'timeout')
        self.assertTrue(self.race.cost.incomplete)
        self.race.toggle_pause()
        self.race.tick(1)
        self.assertEqual(len(self.worker.calls), 1)
        self.race.retry()
        self.race.tick(0)
        self.assertEqual(len(self.worker.calls), 2)

    def test_restart_ignores_old_reply_but_keeps_cost_and_worker(self):
        self.race.tick(0)
        for _ in range(10):
            self.race.restart()
            self.race.tick(0)
        self.assertEqual(len(self.worker.calls), 1)
        before = self.race.jev.active
        self.worker.answer()
        self.race.tick(0)
        self.assertEqual(self.race.jev.active, before)
        self.assertEqual(self.race.cost.responses, 1)
        self.assertEqual(len(self.worker.calls), 2)

    def test_same_kind_next_piece_still_rejects_stale_response(self):
        self.race.tick(0)
        kind = self.race.jev.active.kind
        self.race.jev._spawn(kind)
        before = self.race.jev.active
        self.worker.answer()
        self.race.tick(0)
        self.assertEqual(self.race.jev.active, before)
        self.assertEqual(self.race.cost.responses, 1)

    def test_resize_freezes_and_accounts_reply(self):
        self.race.tick(0)
        self.race.too_small = True
        self.worker.answer()
        before = self.race.jev.active
        self.race.tick(100, [('hard_drop', ())])
        self.assertEqual(self.race.jev.active, before)
        self.assertEqual(self.race.cost.responses, 1)
        self.assertEqual(len(self.worker.calls), 1)

    def test_human_finish_stops_new_calls_and_actions(self):
        almost_won(self.race.human)
        self.race.tick(0, [('hard_drop', ()), ('hard_drop', ())])
        self.assertEqual(self.race.winner, 'You win')
        self.assertEqual(self.race.human.lines, 20)
        self.assertEqual(len(self.worker.calls), 0)
        before = self.race.human.active
        self.race.tick(5, [('hard_drop', ())])
        self.assertEqual(self.race.human.active, before)

    def test_simultaneous_finish_is_draw(self):
        almost_won(self.race.human)
        almost_won(self.race.jev)
        self.race.tick(0)
        moves, _ = options(self.race.jev)
        choice = next(key for key, move in moves.items() if not move.hold and move.dx == 0 and move.rotations == 0)
        self.worker.answer(choice)
        self.race.tick(0, [('hard_drop', ())])
        self.assertEqual(self.race.winner, 'Draw')

    def test_topout_and_simultaneous_topout(self):
        for h, j, expected in [(True, False, 'Jev wins'), (False, True, 'You win'), (True, True, 'Draw')]:
            self.race.restart()
            self.race.human.game_over, self.race.jev.game_over = h, j
            self.race.tick(0)
            self.assertEqual(self.race.winner, expected)

    def test_finished_match_accounts_inflight_reply_without_applying(self):
        self.race.tick(0)
        self.race.human.game_over = True
        self.race.tick(0)
        before = self.race.jev.active
        self.worker.answer()
        self.race.tick(1)
        self.assertEqual(self.race.jev.active, before)
        self.assertEqual(self.race.cost.responses, 1)
        self.assertEqual(len(self.worker.calls), 1)

    def test_invalid_provider_choice_is_visible_error(self):
        self.race.tick(0)
        self.worker.answer('not-an-option')
        self.race.tick(0)
        self.assertIn('invalid', self.race.error)
