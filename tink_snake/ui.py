"""Curses presentation and input; the engine never depends on terminal state."""

import curses
import time
import json
import os

from arcade_common.audio import KeyboardAudio
from arcade_common.theme import PaperRenderer
from .engine import Game, HEIGHT, WIDTH, LEFT, RIGHT, UP, DOWN

MIN_COLUMNS = 80
MIN_ROWS = 30
FRAME_TIME = 1 / 60


class Renderer(PaperRenderer):
    def draw(self, game, too_small, sound_status=''):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if too_small:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, 'Socratink / paper snake', self.ink | curses.A_BOLD)
            self.text(y + 1, 2, 'Resize terminal to at least 80 x 30.', curses.A_BOLD)
            self.text(y + 2, 2, f'Current: {columns} x {rows} // simulation frozen')
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, 'M mute  Q quit  Ctrl-C exit', self.muted)
            self._refresh()
            return
        ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
        for row, text, attr in ((1, '. socratink  /  paper snake', self.ink | curses.A_BOLD),
                                (2, 'leave room to grow.', self.muted)):
            self.text(oy + row, ox + (MIN_COLUMNS - len(text)) // 2, text, attr)
        self.box(oy + 4, ox + 3, 22, 42, 'PLAY / PAPER')
        occupied = set(game.snake)
        heads = {RIGHT: '>>', LEFT: '<<', UP: '^^', DOWN: 'vv'}
        for y in range(HEIGHT):
            for x in range(WIDTH):
                cell = (x, y)
                if cell == game.snake[0]:
                    text, attr = heads[game.direction], self.accent | curses.A_REVERSE
                elif cell in occupied:
                    text, attr = '[]', self.ink | curses.A_REVERSE
                elif cell == game.food:
                    text, attr = '()', self.accent
                else:
                    text, attr = ' .', self.muted
                self.text(oy + 5 + y, ox + 4 + x * 2, text, attr)
        self.box(oy + 4, ox + 49, 15, 27, 'SESSION')
        for row, label, value in ((6, 'SCORE', f'{game.score:,}'),
                                  (9, 'SPEED / STEPS PER SEC', f'{1 / game.interval:.1f}'),
                                  (12, 'LENGTH', len(game.snake)), (15, 'SESSION BEST', f'{game.best:,}')):
            self.text(oy + row, ox + 52, label, self.muted)
            self.text(oy + row + 1, ox + 52, str(value), self.ink | curses.A_BOLD)
        self.text(oy + 20, ox + 51, 'A fresh page.' if game.score == 0 else 'Room to grow.', self.ink)
        self.text(oy + 21, ox + 51, sound_status, self.muted)
        self.text(oy + 23, ox + 51, '>> head   [] body', self.muted)
        self.text(oy + 24, ox + 51, '() food', self.accent)
        if game.paused or game.game_over or game.complete:
            x, y = ox + 10, oy + 11
            self.box(y, x, 7, 28)
            for row in range(1, 6):
                self.text(y + row, x + 1, ' ' * 26, self.ink)
            title = 'BOARD COMPLETE' if game.complete else 'GAME OVER' if game.game_over else 'PAUSED'
            self.text(y + 1, x + (28 - len(title)) // 2, title, self.ink | curses.A_BOLD)
            self.text(y + 2, x + 4, 'Take a breath.' if game.paused else 'Turn a fresh page.', self.muted)
            self.text(y + 3, x + 4, 'P resume  R restart' if game.paused else 'R restart')
            self.text(y + 5, x + 4, 'M mute    Q quit')
        self.text(oy + 27, ox + 3, 'Arrows / WASD steer   P pause   R restart')
        self.text(oy + 28, ox + 3, 'M mute   Q quit   Ctrl-C exit', self.accent)
        self._refresh()

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
        keys = {curses.KEY_LEFT: LEFT, curses.KEY_RIGHT: RIGHT,
                curses.KEY_UP: UP, curses.KEY_DOWN: DOWN}
        for letters, direction in (('aA', LEFT), ('dD', RIGHT), ('wW', UP), ('sS', DOWN)):
            keys.update({ord(letter): direction for letter in letters})
        if key in keys:
            game.turn(keys[key])
    return True


def run(screen, seed=None, no_color=False, no_sound=False):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer = Renderer(screen, no_color)
    game = Game(seed)
    # Trace is observation only; no game state is read from the environment.
    trace_path = os.environ.get('TINK_SNAKE_TRACE')
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
            game.turns.clear()
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
                if key in map(ord, 'pPrR'):
                    transition = True
                handle_key(game, key, audio)
        cue = None
        if not too_small and not was_small and not transition:
            cue = game.update(dt)
            if cue:
                audio.play(cue)
        audio.tick()
        renderer.draw(game, too_small, audio.status)
        if trace:
            trace.write(json.dumps(dict(snake=game.snake, direction=game.direction, turns=list(game.turns),
                                        food=game.food, score=game.score, best=game.best,
                                        paused=game.paused, over=game.game_over, complete=game.complete,
                                        elapsed=game.elapsed, small=too_small, sound=audio.status, cue=cue)) + '\n')
            trace.flush()
        was_small = too_small
        time.sleep(max(0.0, FRAME_TIME - (time.monotonic() - frame_start)))
