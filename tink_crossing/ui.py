"""Curses presentation and input; the engine never depends on terminal state."""

import curses
import json
import os
import time

from arcade_common.audio import KeyboardAudio
from arcade_common.theme import PaperRenderer
from .engine import BAYS, Game, HOME, LEVELS, RIVER, ROAD, ROWS, WIDTH, bay_at

MIN_COLUMNS = 80
MIN_ROWS = 30
FRAME_TIME = 1 / 60
HOPS = {
    curses.KEY_UP: (-1, 0), ord('w'): (-1, 0), ord('W'): (-1, 0),
    curses.KEY_DOWN: (1, 0), ord('s'): (1, 0), ord('S'): (1, 0),
    curses.KEY_LEFT: (0, -1), ord('a'): (0, -1), ord('A'): (0, -1),
    curses.KEY_RIGHT: (0, 1), ord('d'): (0, 1), ord('D'): (0, 1),
}
QUIT = (ord('q'), ord('Q'), 3)


def cell(game, row, col):
    """Glyph and style name for one board cell, player excluded."""
    if row == HOME:
        bay = bay_at(col)
        if bay is None:
            return '^', 'rule'
        return ('*', 'accent') if game.bays[bay] else (' ', 'ink')
    if row in RIVER:
        return ('=', 'ink') if game.occupied(row, col) else ('~', 'muted')
    if row in ROAD:
        return ('#', 'ink') if game.occupied(row, col) else ('.', 'rule')
    return ('_', 'rule')


class Renderer(PaperRenderer):
    def draw(self, game, too_small, sound_status=''):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if too_small:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, 'Socratink / paper crossing', self.ink | curses.A_BOLD)
            self.text(y + 1, 2, 'Resize terminal to at least 80 x 30.', curses.A_BOLD)
            self.text(y + 2, 2, f'Current: {columns} x {rows} // simulation frozen')
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, 'M mute  Q quit  Ctrl-C exit', self.muted)
            self._refresh()
            return
        ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
        self.text(oy + 1, ox + 26, '. socratink / paper crossing', self.ink | curses.A_BOLD)
        self.text(oy + 2, ox + 30, 'five bays, three lives.', self.muted)
        self.text(oy + 3, ox + 71 - len(sound_status), sound_status, self.muted)
        bx, by = ox + 6, oy + 5
        self.box(by - 1, bx - 1, ROWS + 2, WIDTH + 2, 'PLAY / PAPER')
        styles = {'ink': self.ink, 'accent': self.accent, 'muted': self.muted, 'rule': self.rule}
        for row in range(ROWS):
            line = [cell(game, row, col) for col in range(WIDTH)]
            for col, (glyph, style) in enumerate(line):
                self.text(by + row, bx + col, glyph, styles[style])
        if game.state != 'won':
            self.text(by + game.row, bx + game.col, '@', self.accent | curses.A_REVERSE)
        px = bx + WIDTH + 4
        self.text(by, px, f'SCORE  {game.score}', self.ink | curses.A_BOLD)
        self.text(by + 2, px, f'LIVES  {game.lives}', self.ink)
        self.text(by + 3, px, f'LEVEL  {game.level} / {LEVELS}', self.ink)
        self.text(by + 4, px, f'BAYS   {sum(game.bays)} / {len(BAYS)}', self.ink)
        self.text(by + 6, px, 'river: ride the =', self.muted)
        self.text(by + 7, px, 'road: dodge the #', self.muted)
        state = 'PAUSED / P resume' if game.paused else {
            'playing': 'HOP', 'won': 'YOU WIN / R restart / Q quit',
            'over': 'GAME OVER / R restart / Q quit'}[game.state]
        self.text(oy + 20, ox + 5, state, self.accent)
        self.text(oy + 22, ox + 5, 'Arrows or WASD hop  P pause  R restart  M mute', self.ink)
        self.text(oy + 23, ox + 5, 'Q quit  Ctrl-C exit', self.muted)
        self._refresh()


def handle_key(game, key, audio):
    """Apply one key. Returns False to quit."""
    if key in QUIT:
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
    elif key in HOPS:
        for cue in game.hop(*HOPS[key]):
            audio.play(cue)
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
    trace_path = os.environ.get('TINK_CROSSING_TRACE')
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
        transition = False
        for _ in range(32):
            try:
                key = screen.getch()
            except curses.error:
                key = -1
            if key == -1:
                break
            if key in QUIT:
                return
            if key in (ord('m'), ord('M')) or (not too_small and key != curses.KEY_RESIZE):
                before = game.state, game.paused
                handle_key(game, key, audio)
                if (game.state, game.paused) != before:
                    transition = True
        cues = []
        # Time spent paused, undersized, or before a transition is discarded.
        if not too_small and not was_small and not transition:
            cues = game.advance(dt)
            for cue in cues:
                audio.play(cue)
        audio.tick()
        renderer.draw(game, too_small, audio.status)
        if trace:
            trace.write(json.dumps(dict(game.snapshot(), small=too_small, sound=audio.status,
                                        cues=cues)) + '\n')
            trace.flush()
        was_small = too_small
        time.sleep(max(0.0, FRAME_TIME - (time.monotonic() - frame_start)))
