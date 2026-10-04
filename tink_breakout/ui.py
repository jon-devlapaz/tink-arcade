"""Curses rendering and timing. The terminal never changes board geometry."""
import curses
import json
import os
import time
from .engine import Game, HEIGHT, WIDTH, PADDLE_WIDTH
from .layouts import NAMES

MIN_COLUMNS, MIN_ROWS = 80, 30


class Controller:
    def __init__(self, now):
        self.game = Game()
        self.paused = False
        self.small = False
        self.last = now
        self.quit = False

    def frame(self, now, rows, columns, key=-1):
        elapsed = max(0, now - self.last)
        self.last = now
        was_frozen = self.paused or self.small
        self.small = rows < MIN_ROWS or columns < MIN_COLUMNS
        if key in (ord('q'), ord('Q'), 3):
            self.quit = True
        elif not self.small:
            if key in (ord('r'), ord('R')):
                self.game.restart()
                self.paused = False
                was_frozen = True
            elif key in (ord('p'), ord('P')):
                self.paused = not self.paused
            elif not self.paused:
                if key in (curses.KEY_LEFT, ord('a'), ord('A')):
                    self.game.move(-1)
                elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
                    self.game.move(1)
                elif key == ord(' '):
                    self.game.launch()
                    was_frozen = True
        frozen = self.paused or self.small
        advanced = 0
        if frozen or was_frozen:
            self.game.accumulator = 0
        elif not self.quit:
            self.game.advance(elapsed)
            advanced = min(elapsed, .1)
        return dict(self.game.snapshot(), paused=self.paused, small=self.small,
                    quit=self.quit, advanced=advanced)


class Renderer:
    def __init__(self, screen, no_color=False):
        self.screen = screen
        self.ink = 0
        self.accent = curses.A_BOLD
        if not no_color and curses.has_colors():
            curses.start_color()
            if curses.COLORS >= 8 and curses.COLOR_PAIRS >= 2:
                curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
                self.accent |= curses.color_pair(1)

    def text(self, y, x, value, attr=0):
        rows, cols = self.screen.getmaxyx()
        if y < 0 or y >= rows or x >= cols:
            return
        if x < 0:
            value, x = value[-x:], 0
        width = cols - x - (y == rows - 1)
        if width > 0:
            try:
                self.screen.addnstr(y, x, value, width, attr)
            except curses.error:
                pass  # A resize can occur between measuring and writing.

    def draw(self, controller):
        self.screen.erase()
        rows, cols = self.screen.getmaxyx()
        if controller.small:
            self.text(0, 0, 'Terminal too small. Need 80 x 30.')
            self.text(2, 0, 'Resize to continue. Q quits.')
        else:
            g = controller.game
            left, top = (cols - WIDTH - 2) // 2, (rows - HEIGHT - 8) // 2
            self.text(top, left, f'BREAKOUT  Board {g.board + 1}/3: {NAMES[g.board]}', self.accent)
            self.text(top + 1, left, f'Score {g.score}   Lives {g.lives}   Bricks {len(g.bricks)}')
            self.text(top + 2, left, '+' + '-' * WIDTH + '+')
            for y in range(HEIGHT):
                self.text(top + 3 + y, left, '|')
                self.text(top + 3 + y, left + WIDTH + 1, '|')
            for brick in g.bricks.values():
                self.text(top + 3 + int(brick.y), left + 1 + int(brick.x), '[==]', self.accent)
            self.text(top + 21, left + 1 + int(g.paddle - PADDLE_WIDTH / 2), '=' * int(PADDLE_WIDTH), self.accent)
            self.text(top + 3 + min(HEIGHT - 1, int(g.y)), left + 1 + min(WIDTH - 1, int(g.x)), 'o', self.accent)
            self.text(top + 23, left, '+' + '-' * WIDTH + '+')
            message = {'waiting': 'SPACE to launch', 'playing': 'Clear every brick to advance.',
                       'won': 'YOU WIN! R to restart', 'lost': 'GAME OVER. R to restart'}[g.state]
            self.text(top + 24, left, 'PAUSED. P to resume' if controller.paused else message, self.accent)
            self.text(top + 25, left, 'Arrows/A D: move  Space: launch  P: pause  R: restart  Q: quit')
        self.screen.refresh()


def run(screen, no_color=False):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.keypad(True)
    screen.timeout(16)
    controller = Controller(time.monotonic())
    renderer = Renderer(screen, no_color)
    # Optional read-only test observation. It never accepts game state or commands.
    trace_path = os.environ.get('TINK_BREAKOUT_TRACE')
    trace = open(trace_path, 'w', encoding='utf-8') if trace_path else None
    try:
        while not controller.quit:
            key = screen.getch()
            rows, cols = screen.getmaxyx()
            state = controller.frame(time.monotonic(), rows, cols, key)
            renderer.draw(controller)
            if trace:
                trace.write(json.dumps(state) + '\n')
                trace.flush()
    finally:
        if trace:
            trace.close()
