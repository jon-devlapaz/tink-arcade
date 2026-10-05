"""Curses presentation and input; the engine never depends on terminal state."""

import curses
import time
import json
import os

from neon_tetris.audio import KeyboardAudio
from .engine import Game, HEIGHT, WIDTH, PADDLE_HEIGHT, LEFT_X, RIGHT_X

MIN_COLUMNS = 80
MIN_ROWS = 30
FRAME_TIME = 1 / 60


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
                self.screen.bkgd(" ", self.ink)

    def text(self, y, x, text, attr=0):
        rows, columns = self.screen.getmaxyx()
        if y < 0 or y >= rows or x >= columns:
            return
        if x < 0:
            text, x = text[-x:], 0
        # Avoid the lower-right cell, whose write may signal ERR after succeeding.
        width = columns - x - (1 if y == rows - 1 else 0)
        if width <= 0:
            return
        try:
            self.screen.addnstr(y, x, text, width, attr)
        except curses.error:
            # A resize can invalidate dimensions between getmaxyx and addnstr.
            pass

    def box(self, y, x, height, width, title=""):
        self.text(y, x, "+" + "-" * (width - 2) + "+", self.rule)
        for row in range(y + 1, y + height - 1):
            self.text(row, x, "|", self.rule)
            self.text(row, x + width - 1, "|", self.rule)
        self.text(y + height - 1, x, "+" + "-" * (width - 2) + "+", self.rule)
        if title:
            self.text(y, x + 2, " " + title + " ", self.ink)

    def draw(self, game, too_small, sound_status=''):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if too_small:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, 'Socratink / paper pong', self.ink | curses.A_BOLD)
            self.text(y + 1, 2, 'Resize terminal to at least 80 x 30.', curses.A_BOLD)
            self.text(y + 2, 2, f'Current: {columns} x {rows} // simulation frozen')
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, 'M mute  Q quit  Ctrl-C exit', self.muted)
            self._refresh()
            return
        ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
        self.text(oy + 1, ox + 26, '. socratink / paper pong', self.ink | curses.A_BOLD)
        self.text(oy + 2, ox + 34, 'first to seven.', self.muted)
        self.text(oy + 3, ox + 9, f'YOU  {game.player_score}     FIRST TO 7     COMPUTER  {game.computer_score}', self.ink)
        self.box(oy + 4, ox + 9, 22, 62, 'PLAY / PAPER')
        for y in range(HEIGHT):
            self.text(oy + 5 + y, ox + 40, ':', self.rule)
        for center, x in ((game.player, LEFT_X), (game.computer, RIGHT_X)):
            top = min(HEIGHT - PADDLE_HEIGHT, max(0, int(center - PADDLE_HEIGHT / 2)))
            for y in range(top, top + PADDLE_HEIGHT):
                self.text(oy + 5 + y, ox + 10 + x, '|', self.accent | curses.A_REVERSE)
        self.text(oy + 5 + min(HEIGHT - 1, max(0, int(game.y))),
                  ox + 10 + min(WIDTH - 1, max(0, int(game.x))), 'o', self.accent | curses.A_BOLD)
        state = 'PAUSED / P resume' if game.paused else {
            'waiting': 'SPACE to serve', 'playing': 'RALLY',
            'won': 'YOU WIN / R restart / Q quit', 'lost': 'COMPUTER WINS / R restart / Q quit'}[game.state]
        self.text(oy + 26, ox + 9, state, self.accent)
        self.text(oy + 3, ox + 71 - len(sound_status), sound_status, self.muted)
        self.text(oy + 27, ox + 9, 'Up/Down or W/S move  Space serve  P pause  R restart', self.ink)
        self.text(oy + 28, ox + 9, 'M mute  Q quit  Ctrl-C exit', self.muted)
        self._refresh()

    def _refresh(self):
        try:
            self.screen.refresh()
        except curses.error:
            pass


def handle_key(game, key, audio):
    if key in (ord('q'), ord('Q'), 3):
        return False
    if key in (ord('m'), ord('M')):
        audio.toggle()
    elif key in (ord('r'), ord('R')):
        game.restart()
        audio.stop()
        audio.play('switch')
    elif key in (ord('p'), ord('P')):
        if game.toggle_pause():
            audio.stop()
            audio.play('switch')
    else:
        if key == ord(' '):
            if game.launch():
                audio.play('switch')
        elif key in (curses.KEY_UP, ord('w'), ord('W')):
            game.move(-1)
        elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
            game.move(1)
    return True


def run(screen, no_color=False, no_sound=False):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer = Renderer(screen, no_color)
    game = Game()
    # Trace is observation only; no game state is read from the environment.
    trace_path = os.environ.get('TINK_PONG_TRACE')
    trace = open(trace_path, 'w', encoding='utf-8') if trace_path else None
    try:
        with KeyboardAudio(enabled=not no_sound) as audio:
            _run_loop(screen, renderer, game, audio, trace)
            return audio.warning
    finally:
        if trace:
            trace.close()


def _run_loop(screen, renderer, game, audio, trace=None):
    previous = time.monotonic()
    was_small = False
    while True:
        frame_start = time.monotonic()
        dt = frame_start - previous
        previous = frame_start
        rows, columns = screen.getmaxyx()
        too_small = rows < MIN_ROWS or columns < MIN_COLUMNS
        if too_small and not was_small:
            audio.stop()
        # Time before pause/resume or restart belongs to the preceding state.
        transition = False
        for _ in range(32):
            try:
                key = screen.getch()
            except curses.error:
                key = -1
            if key == -1:
                break
            if key in (ord('q'), ord('Q'), 3):
                return
            if key in (ord('m'), ord('M')) or (not too_small and key != curses.KEY_RESIZE):
                before = game.state, game.paused
                handle_key(game, key, audio)
                # Ignored inputs, including Space during a rally, do not reset time.
                if (game.state, game.paused) != before:
                    transition = True
        cues = []
        if not too_small and not was_small and not transition:
            cues = game.advance(dt)
            for cue in cues:
                audio.play(cue)
        audio.tick()
        renderer.draw(game, too_small, audio.status)
        if trace:
            trace.write(json.dumps(dict(game.snapshot(), small=too_small, sound=audio.status, cues=cues)) + '\n')
            trace.flush()
        was_small = too_small
        time.sleep(max(0.0, FRAME_TIME - (time.monotonic() - frame_start)))
