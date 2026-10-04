"""Curses display and keyboard controls."""
import curses
import time
from .engine import Game, Clock, WIDTH, HEIGHT, PLAYER_Y

MIN_COLS, MIN_ROWS = 80, 30


def handle_key(game, key):
    if key in (ord('q'), ord('Q'), 3):
        return False
    if key in (ord('p'), ord('P')) and not game.game_over:
        game.paused = not game.paused
    elif key in (ord('r'), ord('R')):
        game.restart()
    elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
        game.move(-1)
    elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
        game.move(1)
    elif key == ord(' '):
        game.fire()
    return True


def write(screen, row, col, text, attr=0):
    rows, cols = screen.getmaxyx()
    if 0 <= row < rows and 0 <= col < cols - 1:
        try:
            screen.addnstr(row, col, text, cols - col - 1, attr)
        except curses.error:
            pass  # A terminal may resize between bounds checking and drawing.


def draw(screen, game, color):
    screen.erase()
    rows, cols = screen.getmaxyx()
    if rows < MIN_ROWS or cols < MIN_COLS:
        write(screen, 0, 0, 'Terminal too small. Resize to 80 x 30.')
        write(screen, 1, 0, 'Game frozen. Q quits.')
        screen.refresh()
        return
    x, y = (cols - WIDTH - 2) // 2, 4
    write(screen, 0, x, 'TINK ARCADE  /  FORMATION', curses.A_BOLD)
    write(screen, 2, x, f'Score {game.score:06d}    Lives {game.lives}    Wave {game.wave}')
    write(screen, y, x, '+' + '-' * WIDTH + '+')
    for row in range(HEIGHT):
        write(screen, y + row + 1, x, '|')
        write(screen, y + row + 1, x + WIDTH + 1, '|')
    write(screen, y + HEIGHT + 1, x, '+' + '-' * WIDTH + '+')
    for enemy in game.enemies:
        sprite = 'vVv' if enemy.dive is not None else '<o>'
        write(screen, y + 1 + round(enemy.y), x + round(enemy.x), sprite, color(2))
    for bullet in game.bullets:
        write(screen, y + 1 + min(HEIGHT - 1, max(0, round(bullet.y))), x + 1 + round(bullet.x),
              '!' if bullet.hostile else '|', color(3 if bullet.hostile else 1))
    if not game.game_over and (game.protection <= 0 or game.tick % 12 < 8):
        write(screen, y + 1 + PLAYER_Y, x + round(game.player_x), '/^\\', color(1) | curses.A_BOLD)
    if game.game_over:
        write(screen, y + 12, x + 20, 'GAME OVER  /  R to restart', curses.A_REVERSE)
    elif game.paused:
        write(screen, y + 12, x + 24, 'PAUSED  /  P to resume', curses.A_REVERSE)
    write(screen, rows - 2, x, 'A/D or arrows move  SPACE fires  P pause  R restart  Q quit')
    screen.refresh()


def run(screen, seed=None, no_color=False):
    curses.curs_set(0)
    screen.nodelay(True)
    screen.keypad(True)
    curses.set_escdelay(25)
    colored = not no_color and curses.has_colors()
    if colored:
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    color = lambda n: curses.color_pair(n) if colored else 0
    game, clock = Game(seed), Clock()
    last = time.monotonic()
    was_small = False
    while True:
        now = time.monotonic()
        elapsed, last = now - last, now
        rows, cols = screen.getmaxyx()
        small = rows < MIN_ROWS or cols < MIN_COLS
        transition = False
        # Limit each batch so a stream of input cannot starve rendering or quitting.
        for _ in range(64):
            key = screen.getch()
            if key == -1:
                break
            if key in (ord('q'), ord('Q'), 3):
                return
            if small and key != curses.KEY_RESIZE:
                continue
            transition |= key in (ord('p'), ord('P'), ord('r'), ord('R'), curses.KEY_RESIZE)
            if not handle_key(game, key):
                return
        clock.advance(game, elapsed, blocked=small or was_small or transition)
        was_small = small
        draw(screen, game, color)
        time.sleep(1 / 60)
