"""Two independent games; all match mutations happen on the caller's thread."""

import copy
from dataclasses import dataclass
import random

from .engine import Game
from .jev import Cost


@dataclass(frozen=True)
class Move:
    rotations: int = 0
    dx: int = 0
    hold: bool = False


def place(game, move):
    if move.hold:
        return game.hold()
    generation = game.generation
    for _ in range(move.rotations):
        if not game.rotate() or game.generation != generation:
            return False
    for _ in range(abs(move.dx)):
        if not game.move(1 if move.dx > 0 else -1) or game.generation != generation:
            return False
    return game.hard_drop()


def options(game):
    """Enumerate reachable placements, with no heuristic ranking or selection."""
    moves, descriptions, seen = {}, {}, set()
    for rotations in range(4):
        for dx in range(-9, 10):
            trial = copy.deepcopy(game)
            generation = trial.generation
            valid = True
            for _ in range(rotations):
                if not trial.rotate() or trial.generation != generation:
                    valid = False
                    break
            if not valid:
                continue
            for _ in range(abs(dx)):
                if not trial.move(1 if dx > 0 else -1) or trial.generation != generation:
                    valid = False
                    break
            if not valid or trial.active is None:
                continue
            cells = tuple(sorted(trial.ghost().cells()))
            if cells in seen:
                continue
            seen.add(cells)
            before = trial.lines
            trial.hard_drop()
            name = f'place_{len(moves)}'
            moves[name] = Move(rotations, dx)
            heights = []
            holes = 0
            for x in range(len(trial.board[0])):
                occupied = [y for y, row in enumerate(trial.board) if row[x]]
                top = occupied[0] if occupied else len(trial.board)
                heights.append(len(trial.board) - top)
                holes += sum(not trial.board[y][x] for y in range(top, len(trial.board)))
            descriptions[name] = (
                f'Land on cells {cells}; clears {trial.lines - before} lines. '
                f'After clearing: column heights {heights}, covered empty cells {holes}, '
                f'top out {trial.game_over}.'
            )
    if not game.hold_used:
        moves['hold'] = Move(hold=True)
        descriptions['hold'] = 'Hold this piece and play the held piece, or the next piece if hold is empty.'
    return moves, descriptions


class Race:
    TARGET = 20

    def __init__(self, worker, seed=None):
        self.worker = worker
        self.seed = random.SystemRandom().randrange(2**63) if seed is None else seed
        self.cost = Cost()
        self.epoch = 0
        self.restart()

    def restart(self):
        self.epoch += 1
        self.human = Game(self.seed)
        self.jev = Game(self.seed)
        self.paused = False
        self.too_small = False
        self.error = ''
        self.winner = None
        self.ready = None
        self.request_moves = {}
        self.request_id = None
        self.last_choice = ''

    @property
    def running(self):
        return not (self.paused or self.too_small or self.error or self.winner)

    def toggle_pause(self):
        if not self.winner and not self.error:
            self.paused = not self.paused

    def retry(self):
        self.error = ''
        self.ready = None

    def collect(self):
        item = self.worker.poll()
        if item is None:
            return
        identity, reply = item
        self.cost.record(reply)
        # Accounting survives restart; gameplay never crosses match/piece boundaries.
        if identity[0] != self.epoch or self.winner:
            return
        if reply.error:
            self.error = reply.error
        elif identity == self.request_id and identity[1] == self.jev.generation:
            self.ready = (identity, reply)

    def tick(self, dt, actions=()):
        self.collect()
        if not self.running:
            return
        for action, args in actions:
            getattr(self.human, action)(*args)
            if self.human.game_over or self.human.lines >= self.TARGET:
                break
        if self.ready:
            identity, reply = self.ready
            self.ready = None
            if identity == (self.epoch, self.jev.generation):
                move = self.request_moves.get(reply.choice)
                if move is None:
                    self.error = 'Jev returned an invalid move.'
                    return
                # Gravity may have changed reachability since the snapshot.
                trial = copy.deepcopy(self.jev)
                if place(trial, move):
                    place(self.jev, move)
                    self.last_choice = reply.choice
        # A terminal action is settled this frame; neither board takes an extra turn.
        if not self.human.game_over and self.human.lines < self.TARGET:
            self.human.update(dt)
        if not self.jev.game_over and self.jev.lines < self.TARGET:
            self.jev.update(dt)
        self._finish()
        if self.running and not self.worker.busy and not self.ready:
            self.request_moves, criteria = options(self.jev)
            self.request_id = (self.epoch, self.jev.generation)
            state = {
                'board_rows_top_to_bottom': [''.join(c or '.' for c in row) for row in self.jev.board],
                'active': vars(self.jev.active), 'held': self.jev.held,
                'next': self.jev.bag.preview(3), 'lines': self.jev.lines, 'target': self.TARGET,
            }
            self.worker.submit(self.request_id, state, criteria)

    def _finish(self):
        human = self.human.lines >= self.TARGET or self.jev.game_over
        jev = self.jev.lines >= self.TARGET or self.human.game_over
        if human or jev:
            self.winner = 'Draw' if human and jev else 'You win' if human else 'Jev wins'
