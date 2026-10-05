"""Curses rendering and timing. The terminal never changes board geometry."""
import curses
import json
import os
import time
from neon_tetris.audio import KeyboardAudio
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
        self.muted = self.rule = curses.A_DIM
        if not no_color and curses.has_colors():
            curses.start_color()
            if curses.COLORS >= 8 and curses.COLOR_PAIRS >= 5:
                # Indexed approximations of Socratink's paper, carbon and jade.
                if curses.COLORS >= 256:
                    paper, ink, jade, graphite, rule = 230, 233, 29, 240, 245
                else:
                    paper, ink, jade = curses.COLOR_WHITE, curses.COLOR_BLACK, curses.COLOR_CYAN
                    graphite = rule = ink
                for number, color in enumerate((ink, jade, graphite, rule), 1):
                    curses.init_pair(number, color, paper)
                self.ink = curses.color_pair(1)
                self.accent = curses.color_pair(2) | curses.A_BOLD
                self.muted = curses.color_pair(3)
                self.rule = curses.color_pair(4)
                self.screen.bkgd(' ', self.ink)

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

    def box(self, y, x, height, width, title=''):
        self.text(y, x, '+' + '-' * (width - 2) + '+', self.rule)
        for row in range(y + 1, y + height - 1):
            self.text(row, x, '|', self.rule)
            self.text(row, x + width - 1, '|', self.rule)
        self.text(y + height - 1, x, '+' + '-' * (width - 2) + '+', self.rule)
        if title:
            self.text(y, x + 2, ' ' + title + ' ', self.ink)

    def draw(self, controller, sound_status=''):
        self.screen.erase()
        rows, cols = self.screen.getmaxyx()
        if controller.small:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, 'Socratink / paper breakout', self.ink | curses.A_BOLD)
            self.text(y + 1, 2, 'Resize terminal to at least 80 x 30.', curses.A_BOLD)
            self.text(y + 2, 2, f'Current: {cols} x {rows} // simulation frozen')
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, 'M mute  Q quit  Ctrl-C exit', self.muted)
        else:
            g = controller.game
            ox, oy = (cols - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
            left, top = ox + 9, oy + 4
            self.text(oy + 1, ox + 25, '. socratink / paper breakout', self.ink | curses.A_BOLD)
            self.text(oy + 2, ox + 30, 'three boards, three lives.', self.muted)
            self.text(oy + 3, left, f'SCORE {g.score:03}   LIVES {g.lives}   BRICKS {len(g.bricks)}'
                                    f'   BOARD {g.board + 1}/3  {NAMES[g.board]}', self.ink)
            self.box(top, left, HEIGHT + 2, WIDTH + 2, 'PLAY / PAPER')
            for brick in g.bricks.values():
                self.text(top + 1 + int(brick.y), left + 1 + int(brick.x), '[==]', self.ink | curses.A_REVERSE)
            self.text(top + 19, left + 1 + int(g.paddle - PADDLE_WIDTH / 2), '=' * int(PADDLE_WIDTH),
                      self.accent | curses.A_REVERSE)
            self.text(top + 1 + min(HEIGHT - 1, int(g.y)), left + 1 + min(WIDTH - 1, int(g.x)), 'o',
                      self.accent)
            message = {'waiting': 'SPACE to launch', 'playing': 'Clear every brick to advance.',
                       'won': 'YOU WIN  R to restart', 'lost': 'GAME OVER  R to restart'}[g.state]
            self.text(oy + 26, left, 'PAUSED  P to resume' if controller.paused else message, self.accent)
            self.text(oy + 27, left, 'Arrows / A D move   Space launch   P pause   R restart', self.ink)
            self.text(oy + 28, left, 'M mute   Q quit   Ctrl-C exit', self.muted)
            self.text(oy + 28, left + WIDTH + 2 - len(sound_status), sound_status, self.muted)
        self.screen.refresh()


def cues_for(before, after, key):
    """Map one frame's observable change to a keyboard-sound cue, or None."""
    if after['small'] or before is None:
        return None
    if after['board'] > before['board'] or (after['state'] == 'won' and before['state'] != 'won'):
        return 'clear'
    if after['state'] == 'lost' and before['state'] != 'lost':
        return 'over'
    if after['lives'] < before['lives']:
        return 'over'
    if after['score'] > before['score']:
        return 'place'
    if (after['paused'] != before['paused'] or after['state'] != before['state']
            or after['score'] < before['score']):
        return 'switch'
    if key in (curses.KEY_LEFT, curses.KEY_RIGHT, ord('a'), ord('A'), ord('d'), ord('D')):
        return 'move'
    return None


def run(screen, no_color=False, no_sound=False):
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
        with KeyboardAudio(enabled=not no_sound) as audio:
            previous = None
            while not controller.quit:
                key = screen.getch()
                rows, cols = screen.getmaxyx()
                if key in (ord('m'), ord('M')):
                    audio.toggle()
                state = controller.frame(time.monotonic(), rows, cols, key)
                if state['small']:
                    audio.stop()
                cue = cues_for(previous, state, key)
                if cue:
                    audio.play(cue)
                previous = state
                audio.tick()
                renderer.draw(controller, audio.status)
                if trace:
                    trace.write(json.dumps(dict(state, sound=audio.status, cue=cue)) + '\n')
                    trace.flush()
            return audio.warning
    finally:
        if trace:
            trace.close()
