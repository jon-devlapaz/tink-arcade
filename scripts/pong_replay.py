"""Repeatable matches using only Game.move, launch and elapsed time."""
from tink_pong.engine import Game, HEIGHT, LEFT_X, STEP


def play(player=True, limit=120000):
    game = Game()
    for frame in range(limit):
        if game.state in ('won', 'lost'):
            return game, frame
        if game.state == 'waiting':
            game.launch()
        if player and game.vx < 0:
            # The player can aim a return. The computer engine never predicts.
            landing = game.y + game.vy * max(0, (LEFT_X - game.x) / game.vx)
            landing %= 2 * HEIGHT
            if landing > HEIGHT:
                landing = 2 * HEIGHT - landing
            target = landing + (1.8 if landing > HEIGHT / 2 else -1.8)
            target = min(HEIGHT - 2.5, max(2.5, target))
            if abs(target - game.player) > .75:
                game.move(1 if target > game.player else -1)
        game.advance(STEP)
    raise AssertionError(f'Replay exceeded {limit} steps: {game.snapshot()}')


if __name__ == '__main__':
    for player in (True, False):
        game, frames = play(player)
        print(f'{"legal player" if player else "idle player"}: {game.state}, {game.player_score}-{game.computer_score}, {frames} steps')
