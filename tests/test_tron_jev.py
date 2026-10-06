import json
import threading
import time
import unittest
from unittest.mock import Mock, patch

from neon_tetris.jev import MODEL, JevClient, Worker
from tests.tron_jev_fixture import FixtureClient
from tink_tron.engine import Game, STEP, STARTS
from tink_tron.jev_match import INSTRUCTIONS, JevPilot, TronClient
from tink_tron.jev_routes import REQUEST_AT, ROUTE_LENGTH, plan_cells, projected_end

LEFT, RIGHT, UP, DOWN = (-1, 0), (1, 0), (0, -1), (0, 1)
# The Tetris prompt exactly as `main` sends it; Tron must not change it.
TETRIS_PROMPT = ('Choose the best legal Tetris move to race to 20 cleared lines. Clear lines, avoid covered empty cells '
                 'and topping out, and keep the stack low. x=0 is left, y=0 is top. Each placement rotates, moves and '
                 'hard-drops the current piece. You decide the move; options are not ranked.')


class Rig:
    def __init__(self, **fixture):
        self.client = FixtureClient(**fixture)
        self.pilot = JevPilot(Worker(TronClient(self.client)))
        self.game = Game(1, opponent=self.pilot)
        # Park the human cycle on the bottom row so the two never meet while a test steps.
        self.game.trails.pop(STARTS[0])
        self.game.heads[0], self.game.dirs[0] = (0, 19), RIGHT
        self.game.trails[(0, 19)] = 0

    def request(self):
        self.pilot.maybe_request(self.game)

    def settle(self):
        deadline = time.monotonic() + 3
        while self.pilot.worker.busy and time.monotonic() < deadline:
            self.pilot.collect(self.game)
            time.sleep(0.002)
        self.pilot.collect(self.game)
        assert not self.pilot.worker.busy, 'reply never arrived'

    def open(self):
        self.request()
        self.settle()
        return self

    def steps(self, count):
        for _ in range(count):
            self.game.update(STEP)


class TronJevTests(unittest.TestCase):
    def test_tetris_prompt_is_byte_for_byte_unchanged_and_tron_overrides_it(self):
        result = dict(model=MODEL, usage=dict(input_tokens=1), answers=dict(move=dict(type='choice', choice='a')))
        for call, expected in ((lambda c: c.choose({}, {'a': 'x'}), TETRIS_PROMPT),
                               (lambda c: c.choose({}, {'a': 'x'}, instructions='other'), 'other'),
                               (lambda c: TronClient(c).choose({}, {'a': 'x'}), INSTRUCTIONS)):
            connection = Mock()
            connection.getresponse.return_value = Mock(read=Mock(return_value=json.dumps(result).encode()), status=200)
            with patch('http.client.HTTPSConnection', return_value=connection):
                call(JevClient('test-key'))
            body = json.loads(connection.request.call_args.kwargs['body'])
            self.assertEqual(body['questions']['move']['instructions'], expected)

    def test_the_round_waits_for_the_opening_route_then_follows_it(self):
        rig = Rig(gate=threading.Event())
        self.assertTrue(rig.pilot.holds(rig.game))
        self.assertIn('Waiting for Jev', rig.pilot.status(rig.game))
        rig.request(); rig.request()
        self.assertEqual(len(rig.client.calls), 1)  # one request in flight
        rig.client.gate.set()
        rig.settle()
        self.assertFalse(rig.pilot.holds(rig.game))
        self.assertEqual(len(rig.pilot.plan), ROUTE_LENGTH)
        route = list(rig.pilot.plan)
        expected = plan_cells(STARTS[1], route)
        rig.steps(5)
        self.assertEqual(rig.game.heads[1], expected[4])
        self.assertEqual(len(rig.pilot.plan), ROUTE_LENGTH - 5)

    def test_the_request_carries_neutral_facts_and_the_tron_question(self):
        rig = Rig().open()
        state, criteria, instructions = rig.client.calls[0]
        self.assertEqual(instructions, INSTRUCTIONS)
        self.assertEqual(state['route_starts_at'], list(STARTS[1]))
        self.assertEqual(state['rival_head'], list(STARTS[0]))
        self.assertEqual(len(state['board_rows_top_to_bottom']), 20)
        self.assertEqual(state['board_rows_top_to_bottom'][10][6], 'p')
        self.assertEqual(state['board_rows_top_to_bottom'][10][31], 'j')
        self.assertIn('route_0', criteria)

    def test_next_route_is_requested_early_and_anchored_where_the_plan_ends(self):
        rig = Rig().open()
        end, heading = projected_end(rig.game.heads[1], rig.game.dirs[1], rig.pilot.plan)
        rig.steps(ROUTE_LENGTH - REQUEST_AT - 1)
        rig.request()
        self.assertEqual(len(rig.client.calls), 1)  # more than REQUEST_AT steps still planned
        rig.steps(1)
        rig.request()
        self.assertEqual(len(rig.client.calls), 2)
        self.assertEqual(rig.client.calls[1][0]['route_starts_at'], list(end))
        rig.settle()
        self.assertEqual(len(rig.pilot.plan), REQUEST_AT + ROUTE_LENGTH)

    def test_a_late_reply_does_not_get_a_dodge_the_cycle_just_goes_straight_and_crashes(self):
        rig = Rig(gate=threading.Event())
        rig.pilot.opened = True  # a round already under way with no route in hand
        rig.pilot.round_id = rig.game.round_id
        rig.game.heads[1], rig.game.dirs[1] = (3, 10), LEFT
        rig.game.trails[(3, 10)] = 1
        rig.request()
        for _ in range(6):
            rig.game.update(STEP)
        self.assertTrue(rig.game.round_over)
        self.assertEqual(rig.game.winner, 0)
        self.assertTrue(rig.game.crashed[1])
        rig.client.gate.set()
        rig.settle()

    def test_a_reply_after_the_plan_ran_out_is_discarded_but_still_costs(self):
        rig = Rig().open()
        rig.steps(ROUTE_LENGTH - REQUEST_AT)
        rig.client.gate = threading.Event()
        rig.request()
        self.assertTrue(rig.pilot.worker.busy)
        for _ in range(ROUTE_LENGTH):
            if rig.pilot.plan:
                rig.game.update(STEP)
        self.assertFalse(rig.pilot.plan)
        rig.steps(3)  # past the anchor: the route would start from a cell the cycle has already left
        before = rig.pilot.cost.usd
        rig.client.gate.set()
        rig.settle()
        self.assertEqual(len(rig.pilot.plan), 0)
        self.assertGreater(rig.pilot.cost.usd, before)

    def test_a_reply_after_restart_never_steers_but_still_counts_cost(self):
        rig = Rig(gate=threading.Event())
        rig.request()
        rig.game.restart(); rig.pilot.reset()
        rig.client.gate.set()
        rig.settle()
        self.assertEqual(rig.pilot.cost.responses, 1)
        self.assertGreater(rig.pilot.cost.usd, 0)
        self.assertFalse(rig.pilot.plan)
        self.assertFalse(rig.pilot.openings)
        self.assertTrue(rig.pilot.holds(rig.game))
        rig.request()  # a fresh request for the new match
        self.assertEqual(len(rig.client.calls), 2)

    def test_an_opening_reply_for_a_round_that_has_passed_is_dropped(self):
        rig = Rig(gate=threading.Event())
        rig.request()
        rig.game.round_id += 3  # the match moved on while Jev was thinking
        rig.client.gate.set()
        rig.settle()
        self.assertEqual(rig.pilot.openings, {})
        self.assertEqual(rig.pilot.cost.responses, 1)

    def test_error_holds_play_shows_a_short_message_and_retry_is_explicit(self):
        rig = Rig(fail=(1,))
        rig.request(); rig.settle()
        self.assertEqual(rig.pilot.error, 'Jev request failed or timed out.')
        self.assertTrue(rig.pilot.holds(rig.game))
        self.assertIn('Jev error', rig.pilot.status(rig.game))
        rig.request()
        self.assertEqual(len(rig.client.calls), 1)  # no hidden retry
        rig.pilot.retry()
        rig.request(); rig.settle()
        self.assertEqual(len(rig.client.calls), 2)
        self.assertFalse(rig.pilot.holds(rig.game))

    def test_an_invalid_choice_is_an_error_not_a_guess(self):
        rig = Rig(pick=lambda criteria: 'route_999')
        rig.request(); rig.settle()
        self.assertEqual(rig.pilot.error, 'Jev returned an invalid move.')
        self.assertFalse(rig.pilot.plan)

    def test_the_next_rounds_opening_is_fetched_while_the_result_shows(self):
        rig = Rig().open()
        rig.game.round_over, rig.game.winner = True, 0  # the result is showing
        rig.request()
        self.assertEqual(len(rig.client.calls), 2)
        self.assertEqual(rig.client.calls[1][0]['route_starts_at'], list(STARTS[1]))
        rig.settle()
        self.assertIn(rig.game.round_id + 1, rig.pilot.openings)
        rig.game.next_round()
        self.assertFalse(rig.pilot.holds(rig.game))
        self.assertEqual(len(rig.pilot.plan), ROUTE_LENGTH)

    def test_no_opening_is_fetched_after_the_match_ends(self):
        rig = Rig().open()
        rig.game.round_over, rig.game.match_winner = True, 0
        rig.request()
        self.assertEqual(len(rig.client.calls), 1)

    def test_no_clear_route_goes_straight_without_asking(self):
        rig = Rig().open()
        rig.pilot.plan.clear()
        rig.game.heads[1], rig.game.dirs[1] = (0, 0), UP
        rig.game.trails.update({(0, 0): 1, (1, 0): 0, (0, 1): 0})
        rig.request()
        self.assertEqual(len(rig.client.calls), 1)
        self.assertIn('no clear route', rig.pilot.status(rig.game))

    def test_cost_is_shown_and_the_key_never_reaches_state_or_messages(self):
        client = Mock()
        client.choose.side_effect = RuntimeError('boom SECRET-KEY-123')
        pilot = JevPilot(Worker(client))
        game = Game(1, opponent=pilot)
        pilot.maybe_request(game)
        deadline = time.monotonic() + 3
        while pilot.worker.busy and time.monotonic() < deadline:
            pilot.collect(game); time.sleep(0.002)
        text = ' '.join([pilot.error, pilot.status(game), pilot.cost.display()])
        self.assertIn('Jev worker failed', text)
        self.assertNotIn('SECRET', text)
        self.assertIn('Est. $', pilot.cost.display())

    def test_every_planned_route_is_collision_free_when_it_is_chosen(self):
        rig = Rig().open()
        cells = plan_cells(STARTS[1], rig.pilot.plan)
        self.assertEqual(len(set(cells)), len(cells))
        self.assertTrue(all(0 <= x < 38 and 0 <= y < 20 for x, y in cells))
        self.assertTrue(set(cells).isdisjoint(rig.game.trails))


if __name__ == '__main__':
    unittest.main()
