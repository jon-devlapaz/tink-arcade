#!/usr/bin/env python3
"""Legal-input replays for Paper Crossing: one full win, one loss of every life.

A planner searches a time-expanded grid using a copy of the lane timeline. The
replay itself drives a fresh Game only through hop() and advance(STEP), so the
plan is checked by the real rules, not by the planner's model of them.
"""
from collections import deque
import copy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tink_crossing.engine import (  # noqa: E402
    Game, HOME, LANES, RIVER, ROAD, STEP, WIDTH, START, bay_at)

DECISION = 4  # steps between hop opportunities (1/30 s)
HOPS = ((-1, 0), (0, -1), (0, 1), (1, 0))
HORIZON = 120 * 60  # one minute of simulated time per bay


def timeline(game, steps):
    """Lanes and river shifts for each future step; independent of the player."""
    ghost = copy.deepcopy(game)
    ghost.row, ghost.col = START, 0  # parked on the safe start row
    frames = [{row: tuple(cells) for row, cells in ghost.lanes.items()}]
    shifts = []
    for _ in range(steps):
        ghost.step()
        frames.append({row: tuple(cells) for row, cells in ghost.lanes.items()})
        shifts.append({row for row in RIVER if ghost.counters[row] == 0})
    return frames, shifts


def safe(frame, row, col):
    if not 0 <= col < WIDTH:
        return False
    if row in RIVER:
        return frame[row][col]
    if row in ROAD:
        return not frame[row][col]
    return True


def plan_bay(game):
    """Shortest list of per-decision hops (or None) that fills an empty bay."""
    frames, shifts = timeline(game, HORIZON)
    start = (0, game.row, game.col)
    parent = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        k, row, col = node
        if k + DECISION > HORIZON:
            continue
        for move in (None,) + HOPS:
            r, c = row, col
            if move:
                r, c = min(START, max(HOME, row + move[0])), min(WIDTH - 1, max(0, col + move[1]))
                if (r, c) == (row, col):
                    continue
                if r == HOME:
                    bay = bay_at(c)
                    if bay is not None and not game.bays[bay]:
                        return _path(parent, node) + [move]
                    continue
                if not safe(frames[k], r, c):
                    continue
            alive = True
            for i in range(k, k + DECISION):
                if r in RIVER and r in shifts[i]:
                    c += LANES[r][2]
                if not safe(frames[i + 1], r, c):
                    alive = False
                    break
            nxt = (k + DECISION, r, c)
            if alive and nxt not in parent:
                parent[nxt] = (node, move)
                queue.append(nxt)
    raise SystemExit('Planner found no route to an empty bay')


def _path(parent, node):
    moves = []
    while parent[node]:
        node, move = parent[node]
        moves.append(move)
    return moves[::-1]



def replay_win():
    game = Game()
    steps = 0
    while game.state == 'playing':
        before = (game.level, sum(game.bays), game.deaths)
        moves = plan_bay(game)
        for move in moves[:-1]:
            if move:
                game.hop(*move)
            for _ in range(DECISION):
                game.advance(STEP)
                steps += 1
        game.hop(*moves[-1])
        assert game.deaths == before[2], f'life lost following plan at {game.snapshot()}'
        after = (game.level, sum(game.bays))
        assert after != before[:2], 'plan did not fill a bay'
    assert game.state == 'won', game.snapshot()
    assert game.lives == 3 and game.level == 3 and all(game.bays), game.snapshot()
    return game, steps


def replay_loss():
    game = Game()
    steps = 0
    while game.state == 'playing' and steps < 120 * 120:
        game.hop(-1, 0)  # keep hopping forward into traffic and water
        for _ in range(15):
            game.advance(STEP)
            steps += 1
    assert game.state == 'over' and game.lives == 0 and game.deaths == 3, game.snapshot()
    return game, steps


def main():
    won, steps = replay_win()
    print(f'Legal win: level={won.level} score={won.score} lives={won.lives} '
          f'steps={steps} ({steps * STEP:.1f}s simulated)')
    lost, steps = replay_loss()
    print(f'Legal loss: score={lost.score} deaths={lost.deaths} steps={steps}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
