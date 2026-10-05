#!/usr/bin/env python3
"""A deterministic legal-input controller. Never assigns to game state."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tink_invaders.engine import Game, STEP, SHIP_Y

SEED, STEP_LIMIT = 7, 36000


def choose_input(game):
    if game.state == 'ready':
        return 'space'
    if game.state != 'playing':
        return None
    threats = [s for s in game.enemy_shots if s.y > SHIP_Y - 5 and abs(s.x - game.ship) <= 2]
    if threats:
        nearest = max(threats, key=lambda s: s.y)
        direction = -1 if nearest.x >= game.ship else 1
        if game.ship <= 2:
            direction = 1
        elif game.ship >= 57:
            direction = -1
        return 'right' if direction > 0 else 'left'
    if not game.enemies:
        return None
    target = min(game.bottom_shooters(), key=lambda e: abs(e.x - game.ship))
    # Shots fly while the formation marches; aim slightly ahead of its current lane.
    aim = max(1, min(58, target.x + game.direction))
    if abs(aim - game.ship) <= 1 and game.player_shot is None:
        return 'space'
    if game.ship != aim:
        return 'right' if game.ship < aim else 'left'
    return 'space'


def apply_input(game, command):
    if command == 'space':
        game.start_or_fire()
    elif command in ('left', 'right'):
        game.move(-1 if command == 'left' else 1)


def replay(seed=SEED, limit=STEP_LIMIT, observe=None):
    game = Game(seed)
    for step in range(limit):
        command = choose_input(game)
        apply_input(game, command)
        game.advance(STEP)
        if observe:
            observe(step, command, game)
        game.take_events()
        if game.state in ('won', 'lost'):
            return game, step + 1
    raise RuntimeError(f'Replay exceeded {limit} steps: {game.snapshot()}')


if __name__ == '__main__':
    game, steps = replay()
    print(f'seed={SEED} controller=choose_input limit={STEP_LIMIT} steps={steps} state={game.state} wave={game.wave + 1} score={game.score} lives={game.lives}')
    sys.exit(0 if game.state == 'won' and game.score == 340 and game.lives > 0 else 1)
