"""Paper presentation and single-owner input, timing and audio lifecycle."""
import curses
import json
import os
import time

from arcade_common.audio import KeyboardAudio
from arcade_common.theme import PaperRenderer
from .engine import Game, WIDTH, HEIGHT

MIN_COLUMNS, MIN_ROWS = 80, 30
FRAME_TIME, MAX_KEYS = 1 / 60, 32


class Controller:
    def __init__(self, now):
        self.game = Game()
        self.last = now
        self.paused = self.small = self.quit = False
        self.discard_input = False

    def frame(self, now, rows, columns, keys=(), audio=None):
        elapsed = max(0.0, now - self.last)
        self.last = now
        was_small, was_paused = self.small, self.paused
        self.small = rows < MIN_ROWS or columns < MIN_COLUMNS
        transition = False
        cues = []
        if self.small and not was_small and audio:
            audio.stop()
        for key in keys[:MAX_KEYS]:
            if key in (ord('q'), ord('Q'), 3):
                self.quit = True
                break
            if key in (ord('m'), ord('M')):
                if audio:
                    audio.toggle()
                continue
            if self.small or was_small or transition:
                continue
            if key in (ord('r'), ord('R')):
                self.game.restart()
                self.paused = False
                transition = True
                if audio:
                    audio.stop()
                cues.append('switch')
            elif key in (ord('p'), ord('P')) and self.game.state == 'playing':
                self.paused = not self.paused
                transition = True
                if audio:
                    audio.stop()
                cues.append('switch')
            elif key in (ord(' '), 10, 13, curses.KEY_ENTER) and not self.paused:
                cue = self.game.lock_row()
                if cue:
                    cues.append(cue)
                    transition = True
        advanced = 0.0
        if not (self.quit or self.small or was_small or self.paused or was_paused or transition):
            self.game.advance(elapsed)
            if elapsed <= .250 and self.game.state == 'playing':
                advanced = elapsed
        if audio:
            for cue in cues:
                audio.play(cue)
            audio.tick()
        self.discard_input = self.small != was_small or transition
        return dict(self.game.snapshot(), paused=self.paused, small=self.small, quit=self.quit,
                    advanced=advanced, sound=audio.status if audio else 'key sound off')


class Renderer(PaperRenderer):
    def draw(self, controller, sound_status='key sound off'):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if controller.small:
            self.text(1, 2, 'Paper Stacker', self.accent)
            self.text(3, 2, 'Resize terminal to at least 80 x 30.', self.ink)
            self.text(4, 2, f'Current: {columns} x {rows}. Game frozen.', self.muted)
            self.text(6, 2, sound_status, self.muted)
            self.text(7, 2, 'M mute  Q quit  Ctrl-C exit', self.ink)
            self._refresh()
            return
        ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
        left, top = ox + 32, oy + 5
        game = controller.game
        self.text(oy + 1, ox + 25, '. socratink / paper stacker', self.ink | curses.A_BOLD)
        self.text(oy + 2, ox + 29, 'one row, then the next.', self.muted)
        self.box(top, left, HEIGHT + 2, WIDTH * 2 + 2, 'PLAY / PAPER')
        self.text(oy + 7, ox + 10, f'HEIGHT {len(game.rows):02}/{HEIGHT}', self.ink)
        self.text(oy + 9, ox + 10, f'BLOCKS {game.width}', self.ink)
        self.text(oy + 7, ox + 52, '[] moving / jade', self.accent)
        self.text(oy + 9, ox + 52, '[] settled / ink', self.ink)
        self.text(oy + 11, ox + 52, sound_status, self.muted)
        for level in range(HEIGHT):
            y = top + HEIGHT - level
            for x in range(WIDTH):
                self.text(y, left + 1 + 2 * x, ' .', self.muted)
            if level < len(game.rows):
                for x in game.rows[level]:
                    self.text(y, left + 1 + 2 * x, '[]', self.ink | curses.A_REVERSE)
        if game.state == 'playing':
            y = top + HEIGHT - len(game.rows)
            for x in range(game.x, game.x + game.width):
                self.text(y, left + 1 + 2 * x, '[]', self.accent | curses.A_REVERSE)
        label = 'PAUSED' if controller.paused else {'playing': '', 'won': 'YOU WIN', 'lost': 'GAME OVER'}[game.state]
        if label:
            self.text(top + 8, left + 2, label.center(12), self.ink | curses.A_REVERSE)
        message = ('PAUSED  P to resume' if controller.paused else
                   {'playing': 'Aim for the top. Only overlap survives.',
                    'won': 'YOU WIN  Top reached. R to restart.',
                    'lost': 'GAME OVER  No overlap. R to restart.'}[game.state])
        self.text(oy + 24, ox + 15, message, self.accent)
        self.text(oy + 27, ox + 13, 'Space / Enter lock   P pause   R restart', self.ink)
        self.text(oy + 28, ox + 13, 'M mute   Q quit   Ctrl-C exit', self.muted)
        self._refresh()


def run(screen, no_color=False, no_sound=False):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer = Renderer(screen, no_color)
    controller = Controller(time.monotonic())
    trace_path = os.environ.get('TINK_STACKER_TRACE')
    trace = open(trace_path, 'w', encoding='utf-8') if trace_path else None
    try:
        with KeyboardAudio(enabled=not no_sound) as audio:
            _run_loop(screen, renderer, controller, audio, trace)
            return audio.warning
    finally:
        if trace:
            trace.close()


def _run_loop(screen, renderer, controller, audio, trace=None):
    while not controller.quit:
        started = time.monotonic()
        rows, columns = screen.getmaxyx()
        keys = []
        for _ in range(MAX_KEYS):
            key = screen.getch()
            if key == -1:
                break
            keys.append(key)
        state = controller.frame(started, rows, columns, keys, audio)
        if controller.discard_input:
            curses.flushinp()
        renderer.draw(controller, audio.status)
        if trace:
            trace.write(json.dumps(state) + '\n')
            trace.flush()
        time.sleep(max(0, FRAME_TIME - (time.monotonic() - started)))
