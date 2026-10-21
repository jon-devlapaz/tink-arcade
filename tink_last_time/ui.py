"""Paper canvas, dark arena and single-owner terminal loop."""
import curses
import json
import os
import time

from arcade_common.audio import KeyboardAudio
from arcade_common.theme import PaperRenderer
from .engine import DIRECTIONS, Game, HEIGHT, ROUND_TICKS, TICK_SECONDS, WIDTH

MIN_COLUMNS, MIN_ROWS = 80, 30
FRAME_TIME, MAX_KEYS = 1 / 60, 32
ARROWS = dict(zip((curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT), DIRECTIONS))


class Controller:
    def __init__(self, now, seed=None):
        self.game = Game(seed)
        self.last = now
        self.best = 0
        self.paused = self.small = self.quit = self.discard_input = False

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
            elif key in ARROWS and not self.paused:
                self.game.steer(ARROWS[key])
        before_score, before_state = self.game.score, self.game.state
        if not (self.quit or self.small or was_small or self.paused or was_paused or transition):
            self.game.advance(elapsed)
        self.best = max(self.best, self.game.score)
        if before_state == 'playing' and self.game.state == 'lost':
            cues.append('over')
        elif self.game.score > before_score:
            cues.append('clear')
        if audio:
            for cue in cues:
                audio.play(cue)
            audio.tick()
        self.discard_input = self.small != was_small or transition
        return dict(self.game.snapshot(), paused=self.paused, small=self.small,
                    quit=self.quit, best=self.best,
                    sound=audio.status if audio else 'key sound off')


class Renderer(PaperRenderer):
    def draw(self, controller, sound_status='key sound off'):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if controller.small:
            self.text(1, 2, 'Last Time', self.accent)
            self.text(3, 2, 'Resize terminal to at least 80 x 30.', self.ink)
            self.text(4, 2, f'Current: {columns} x {rows}. Game frozen.', self.muted)
            self.text(6, 2, sound_status, self.muted)
            self.text(7, 2, 'M mute  Q quit  Ctrl-C exit', self.ink)
            self._refresh()
            return
        ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
        left, top = ox + 9, oy + 5
        game = controller.game
        self.text(oy + 1, ox + 24, '. socratink / paper last time', self.ink | curses.A_BOLD)
        self.text(oy + 2, ox + 24, 'your only enemy is you.', self.muted)
        remaining = (ROUND_TICKS - game.tick) * TICK_SECONDS - game.accumulator
        self.text(oy + 3, ox + 9,
                  f'SCORE {game.score:04}   BEST {controller.best:04}   ROUND {game.round}   GHOSTS {len(game.paths)}', self.ink)
        self.text(oy + 4, ox + 9, f'NEXT ROUND {remaining:04.1f}s   {sound_status}', self.muted)
        self.box(top, left, HEIGHT + 2, WIDTH * 2 + 2, 'PLAY / PAPER')
        dark = self.ink | curses.A_REVERSE
        for y in range(HEIGHT):
            self.text(top + 1 + y, left + 1, ' ' * (WIDTH * 2), dark)
        for x, y in game.sparks:
            self.text(top + 1 + y, left + 1 + 2 * x, '* ', dark | curses.A_BOLD)
        for x, y in game.ghosts:
            self.text(top + 1 + y, left + 1 + 2 * x, 'xx', dark | curses.A_DIM)
        x, y = game.player
        self.text(top + 1 + y, left + 1 + 2 * x, '<>', self.accent | curses.A_REVERSE | curses.A_BOLD)
        label = 'PAUSED  P to resume' if controller.paused else (
            'GAME OVER  R to restart' if game.state == 'lost' else '<> you   * spark   xx past you')
        self.text(oy + 25, ox + 9, label, self.accent)
        self.text(oy + 26, ox + 9, 'Every 15s ghosts loop. Overlapping starts shift you to safety.', self.muted)
        self.text(oy + 27, ox + 9, 'Arrows steer   P pause   R restart   M mute   Q / Ctrl-C quit', self.ink)
        self.text(oy + 28, ox + 9, 'One life. Touch a ghost and it ends. Walls only stop you.', self.muted)
        self._refresh()


def run(screen, no_color=False, no_sound=False, seed=None):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer = Renderer(screen, no_color)
    controller = Controller(time.monotonic(), seed)
    trace_path = os.environ.get('TINK_LAST_TIME_TRACE')
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
