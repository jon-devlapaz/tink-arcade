"""Deterministic Tron rules, independent of the terminal and audio."""
import random

from .ai import DIRECTIONS, DOWN, HEIGHT, LEFT, LEVELS, RIGHT, UP, WIDTH, choose

WINS = 3
STEP = 0.09
STARTS = ((6, HEIGHT // 2), (WIDTH - 7, HEIGHT // 2))
FACING = (RIGHT, LEFT)


class Game:
    def __init__(self, seed=None, two_player=False, level='normal'):
        if level not in LEVELS:
            raise ValueError(f'level must be one of {", ".join(LEVELS)}')
        self.seed, self.two_player, self.level = seed, two_player, level
        self.restart()

    def restart(self):
        self.rng = random.Random(self.seed)
        self.scores = [0, 0]
        self.match_winner = None
        self.paused = False
        self.new_round()

    def new_round(self):
        self.heads = list(STARTS)
        self.dirs = list(FACING)
        self.trails = {STARTS[0]: 0, STARTS[1]: 1}
        self.pending = [None, None]
        self.crashed = [False, False]
        self.round_over = False
        self.winner = None
        self.paused = False
        self.acc = self.elapsed = 0.0

    @property
    def round(self):
        """The round in play, or the one that just ended while its result is showing; a draw replays its number."""
        return sum(self.scores) + (0 if self.round_over and self.winner is not None else 1)

    def next_round(self):
        if not self.round_over or self.match_winner is not None:
            return False
        self.new_round()
        return True

    def is_human(self, player):
        return player == 0 or self.two_player

    def turn(self, player, direction):
        if self.paused or self.round_over or not self.is_human(player) or self.pending[player] is not None:
            return False
        current = self.dirs[player]
        if direction not in DIRECTIONS or direction == current or direction == (-current[0], -current[1]):
            return False
        self.pending[player] = direction
        return True

    def toggle_pause(self):
        if self.round_over:
            return False
        self.paused = not self.paused
        return True

    def update(self, dt):
        """Advance by elapsed time; one late frame counts for at most one step. Returns a cue or None."""
        if self.paused or self.round_over:
            return None
        dt = min(dt, STEP)
        self.elapsed += dt
        self.acc += dt
        if self.acc < STEP:
            return None
        self.acc -= STEP
        return self._step()

    def _step(self):
        before = list(self.dirs)
        if not self.two_player:
            # The machine reads the board only, never the pending key press.
            self.dirs[1] = choose(set(self.trails), self.heads[1], self.heads[0], self.dirs[1], self.level, self.rng)
        for player in (0, 1):
            if self.pending[player] is not None:
                self.dirs[player], self.pending[player] = self.pending[player], None
        targets = [(h[0] + d[0], h[1] + d[1]) for h, d in zip(self.heads, self.dirs)]
        dead = [not (0 <= x < WIDTH and 0 <= y < HEIGHT) or (x, y) in self.trails for x, y in targets]
        if targets[0] == targets[1]:
            dead = [True, True]
        for player in (0, 1):
            if dead[player]:
                self.crashed[player] = True
            else:
                self.heads[player] = targets[player]
                self.trails[targets[player]] = player
        if not any(dead):
            return 'move' if any(self.is_human(p) and self.dirs[p] != before[p] for p in (0, 1)) else None
        self.round_over = True
        if dead[0] != dead[1]:
            self.winner = 1 if dead[0] else 0
            self.scores[self.winner] += 1
            if self.scores[self.winner] == WINS:
                self.match_winner = self.winner
        decisive = self.winner is not None
        return 'clear' if decisive and (self.two_player or self.winner == 0) else 'over'
