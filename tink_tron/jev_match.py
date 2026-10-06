"""Jev as player 2: it picks routes, the cycle follows them, and a late reply is never covered for.

All state changes happen on the game thread. The worker thread only calls the client, so a reply is applied
only when it still matches the match, the round and the cell where the route is meant to start.
"""
from collections import deque

from neon_tetris.jev import Cost
from .ai import HEIGHT, WIDTH
from .engine import FACING, STARTS, WINS
from .jev_routes import NAMES, REQUEST_AT, enumerate_routes, plan_cells, projected_end

INSTRUCTIONS = ('You steer a Tron light cycle and are racing to win rounds. A cycle that touches a wall, any trail or '
                'the other cycle loses the round. Choose the route for your cycle to follow next. x=0 is left, y=0 is '
                'the top. Your rival keeps moving while you think, about every 90 milliseconds, and your cycle keeps '
                'following its plan, then goes straight. You decide the route; options are not ranked.')


class TronClient:
    """Adds Tron's question to any client with the shared `choose(state, criteria, instructions)` shape."""

    def __init__(self, client):
        self.client = client

    def choose(self, state, criteria):
        return self.client.choose(state, criteria, instructions=INSTRUCTIONS)


def board_rows(trails, heads):
    rows = [['.'] * WIDTH for _ in range(HEIGHT)]
    for (x, y), owner in trails.items():
        rows[y][x] = 'JP'[owner == 0] if owner in (0, 1) else '.'
    for owner, (x, y) in enumerate(heads):
        rows[y][x] = 'pj'[owner]
    return [''.join(row) for row in rows]


class JevPilot:
    """The opponent callback for `Game`, plus the request bookkeeping around it."""

    def __init__(self, worker):
        self.worker = worker
        self.cost = Cost()
        self.epoch = 0
        self.reset()

    def reset(self):
        """A new match: earlier replies still count toward cost but never steer."""
        self.epoch += 1
        self.plan = deque()
        self.openings = {}
        self.request = None
        self.error = ''
        self.round_id = None
        self.opened = False
        self.no_route = False

    def retry(self):
        self.error = ''

    def __call__(self, game):
        return self.plan.popleft() if self.plan else game.dirs[1]

    def holds(self, game):
        """True when play must not advance: an error is showing, or the round is waiting for Jev's opening route."""
        self.sync(game)
        return bool(self.error) or not self.opened

    def sync(self, game):
        if game.round_id != self.round_id:
            self.round_id = game.round_id
            self.plan = deque(self.openings.pop(game.round_id, ()))
            self.opened = bool(self.plan)
            self.no_route = False
        if not self.opened and game.round_id in self.openings:
            self.plan = deque(self.openings.pop(game.round_id))
            self.opened = True
        if not self.opened and len(game.trails) > 2:
            self.opened = True  # the round is already under way; Jev just goes straight until a route arrives

    def collect(self, game):
        """Apply the worker's reply if it still fits; always record its cost."""
        item = self.worker.poll()
        if item is None:
            return
        identity, reply = item
        self.cost.record(reply)
        epoch, round_id, mode, anchor = identity
        request, self.request = self.request, None
        if epoch != self.epoch:
            return
        if reply.error:
            self.error = reply.error
            return
        directions = (request or {}).get('routes', {}).get(reply.choice)
        if directions is None:
            self.error = 'Jev returned an invalid move.'
            return
        if mode == 'opening':
            if round_id >= game.round_id:
                self.openings[round_id] = directions
        elif round_id == game.round_id and not game.round_over:
            end, _ = projected_end(game.heads[1], game.dirs[1], self.plan)
            if end == anchor:
                self.plan.extend(directions)
        self.sync(game)

    def maybe_request(self, game):
        """Ask for an opening route (before a round) or the next route (while the plan runs short)."""
        self.sync(game)
        if self.worker.busy or self.error:
            return
        start = dict(zip(STARTS, (0, 1)))
        if game.round_over:
            if game.match_winner is None and game.round_id + 1 not in self.openings:
                self._submit(game, 'opening', game.round_id + 1, STARTS[1], FACING[1], set(STARTS), start, STARTS)
        elif not self.opened:
            if game.round_id not in self.openings:
                self._submit(game, 'opening', game.round_id, STARTS[1], FACING[1], set(STARTS), start, STARTS)
        elif len(self.plan) <= REQUEST_AT:
            end, heading = projected_end(game.heads[1], game.dirs[1], self.plan)
            blocked = set(game.trails) | set(plan_cells(game.heads[1], self.plan))
            self._submit(game, 'extend', game.round_id, end, heading, blocked, game.trails, game.heads)

    def _submit(self, game, mode, round_id, anchor, heading, blocked, trails, heads):
        routes = enumerate_routes(blocked, anchor, heading, heads[0])
        self.no_route = not routes
        if not routes:
            return
        state = {
            'board_rows_top_to_bottom': board_rows(trails, heads),
            'legend': 'J/j are your trail and head, P/p are your rival\'s trail and head, . is empty',
            'route_starts_at': list(anchor), 'your_heading_there': NAMES[heading], 'rival_head': list(heads[0]),
            'round_wins': {'you': game.scores[1], 'rival': game.scores[0], 'needed_to_win_match': WINS},
            'route_length': len(next(iter(routes.values()))[0]),
        }
        identity = (self.epoch, round_id, mode, anchor)
        self.request = {'routes': {name: directions for name, (directions, _) in routes.items()}}
        if not self.worker.submit(identity, state, {name: text for name, (_, text) in routes.items()}):
            self.request = None

    def status(self, game):
        if self.error:
            return f'Jev error: {self.error}'
        if not self.opened:
            return 'Waiting for Jev to choose an opening route'
        if self.worker.busy:
            return f'Jev thinking ({len(self.plan)} planned steps left)'
        if self.no_route:
            return 'Jev sees no clear route: going straight'
        return f'Jev following a route ({len(self.plan)} steps left)'
