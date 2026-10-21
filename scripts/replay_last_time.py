#!/usr/bin/env python3
"""Legal-input survival and loss replays, without game-state or clock injection."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tink_last_time.engine import DIRECTIONS, Game, HEIGHT, TICK_SECONDS, WIDTH


def survive():
    game = Game(7)
    for step in range(600):
        old = game.player
        candidates = []
        for order, direction in enumerate(DIRECTIONS):
            dx, dy = direction
            new = (max(0, min(WIDTH - 1, old[0] + dx)),
                   max(0, min(HEIGHT - 1, old[1] + dy)))
            if any(new == p[game.tick + 1] or (old == p[game.tick + 1] and new == p[game.tick])
                   for p in game.paths):
                continue
            distance = min(abs(new[0] - s[0]) + abs(new[1] - s[1]) for s in game.sparks)
            candidates.append((distance, order, direction))
        assert candidates, f'No safe move at step {step}'
        game.steer(min(candidates)[2])
        game.advance(TICK_SECONDS)
        assert game.state == 'playing', f'Lost at step {step}'
    assert game.round == 5 and len(game.ghosts) == 4
    assert game.score > 0
    print(f'Legal survival: seed=7 ticks=600 round={game.round} ghosts={len(game.ghosts)} sparks={game.score}')
    return game


def lose():
    game = Game(7)
    game.steer((1, 0))
    for _ in range(150):
        game.advance(TICK_SECONDS)
    assert game.round == 2
    for ticks in range(1, 151):
        game.advance(TICK_SECONDS)
        if game.state == 'lost':
            break
    assert game.state == 'lost', 'Sitting at the first path endpoint must lose to its replay'
    print(f'Legal loss: seed=7 round=2 tick={ticks}, no steering after the first arrow')
    return game


if __name__ == '__main__':
    survive()
    lose()
