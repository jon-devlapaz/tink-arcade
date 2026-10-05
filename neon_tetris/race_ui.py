"""Side-by-side paper Tetris, using the solo renderer's drawing primitives."""

import curses
import time

from .audio import KeyboardAudio
from .engine import HEIGHT, WIDTH
from .jev import Worker
from .race import Race
from .ui import FRAME_TIME, MIN_COLUMNS, MIN_ROWS, Renderer

ACTIONS = {
    curses.KEY_LEFT: ('move', (-1,)), ord('a'): ('move', (-1,)),
    curses.KEY_RIGHT: ('move', (1,)), ord('d'): ('move', (1,)),
    curses.KEY_DOWN: ('soft_drop', ()), ord('s'): ('soft_drop', ()),
    curses.KEY_UP: ('rotate', (1,)), ord('x'): ('rotate', (1,)),
    ord('z'): ('rotate', (-1,)), ord(' '): ('hard_drop', ()),
    ord('c'): ('hold', ()),
}


class RaceRenderer(Renderer):
    def draw(self, race, too_small, sound_status=''):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if too_small:
            self.text(1, 2, 'Tink arcade / Tetris vs Jev', self.ink | curses.A_BOLD)
            self.text(3, 2, 'Resize to at least 80 x 30. Both boards are frozen.')
            self.text(4, 2, f'Current: {columns} x {rows}. Q quit.')
            self._refresh()
            return
        ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
        self.text(oy, ox + 22, 'TINK ARCADE / a race to 20', self.ink | curses.A_BOLD)
        self.text(oy + 1, ox + 13, 'Same pieces. Your board on the left. Jev on the right.', self.muted)
        for offset, name, game in ((0, 'YOU', race.human), (40, 'JEV', race.jev)):
            x = ox + offset
            self.text(oy + 2, x + 2, f'{name}   {game.lines:2}/20 lines', self.accent)
            self.box(oy + 3, x + 1, HEIGHT + 2, WIDTH * 2 + 2)
            for y, row in enumerate(game.board):
                for col, kind in enumerate(row):
                    if kind:
                        self.block(oy + 4 + y, x + 2 + col * 2, kind)
                    else:
                        self.text(oy + 4 + y, x + 2 + col * 2, ' .', self.muted)
            ghost = game.ghost()
            if ghost:
                active = set(game.active.cells())
                for col, y in ghost.cells():
                    if 0 <= y < HEIGHT and (col, y) not in active:
                        self.block(oy + 4 + y, x + 2 + col * 2, ghost.kind, ghost=True)
            if game.active:
                for col, y in game.active.cells():
                    if 0 <= y < HEIGHT:
                        self.block(oy + 4 + y, x + 2 + col * 2, game.active.kind, active=True)
            if game.flash_time:
                for y in game.flash_rows:
                    self.text(oy + 4 + y, x + 2, '=' * 20, self.accent)
            self.text(oy + 4, x + 26, 'HOLD', self.muted)
            self.preview(game.held, oy + 5, x + 26)
            self.text(oy + 8, x + 26, 'NEXT', self.muted)
            for i, kind in enumerate(game.bag.preview(3)):
                self.preview(kind, oy + 9 + i * 4, x + 26)
            self.text(oy + 22, x + 26, f'Level {game.level}', self.muted)
            self.text(oy + 23, x + 26, f'{game.score} pts', self.muted)
        status = race.winner or ('Jev error: match paused' if race.error else
                                'PAUSED' if race.paused else 'Jev thinking...' if race.worker.busy else 'Racing')
        self.text(oy + 25, ox + 2, status, self.accent)
        self.text(oy + 26, ox + 2, race.error or f'{race.cost.model} | {sound_status}', self.muted)
        self.text(oy + 27, ox + 2, race.cost.display(race.worker.busy), self.ink)
        self.text(oy + 28, ox + 2, 'Arrows / WASD move | X/Z rotate | Space drop | C hold', self.muted)
        controls = 'Enter retry | R restart | Q quit' if race.error else 'P pause | R restart | M sound | Q quit'
        self.text(oy + 29, ox + 2, controls, self.muted)
        self._refresh()


def handle_key(race, key, audio):
    if 65 <= key <= 90:
        key += 32
    if key in (ord('q'), 3):
        return False, None
    if key == ord('m'):
        audio.toggle()
    elif not race.too_small:
        if key == ord('r'):
            race.restart()
            audio.stop()
        elif key == ord('p'):
            race.toggle_pause()
            audio.stop()
        elif key in (10, 13, curses.KEY_ENTER) and race.error:
            race.retry()
        elif race.running:
            return True, ACTIONS.get(key)
    return True, None


def run(screen, seed=None, no_color=False, no_sound=False, client=None):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer = RaceRenderer(screen, no_color)
    race = Race(Worker(client), seed)
    with KeyboardAudio(enabled=not no_sound) as audio:
        _run_loop(screen, renderer, race, audio)
        pending = race.worker.busy
        summary = f'{race.winner or "Match unfinished"}. {race.cost.display(pending)}'
        if pending:
            summary += '; final in-flight request may still be charged.'
        return audio.warning, summary


def _run_loop(screen, renderer, race, audio):
    previous = time.monotonic()
    was_small = False
    while True:
        start = time.monotonic()
        dt, previous = start - previous, start
        rows, columns = screen.getmaxyx()
        race.too_small = rows < MIN_ROWS or columns < MIN_COLUMNS
        race.collect()
        actions = []
        for _ in range(32):
            try:
                key = screen.getch()
            except curses.error:
                key = -1
            if key == -1:
                break
            epoch, paused = race.epoch, race.paused
            keep, action = handle_key(race, key, audio)
            if not keep:
                return
            if race.epoch != epoch or race.paused != paused or not race.running:
                actions.clear()
            if action:
                actions.append(action)
        before_lines = race.human.lines
        before_board = tuple(map(tuple, race.human.board))
        before_piece = race.human.active
        race.tick(0 if was_small else dt, actions)
        if race.human.lines > before_lines:
            audio.play('clear')
        elif tuple(map(tuple, race.human.board)) != before_board:
            audio.play('place')
        elif race.human.active != before_piece and actions:
            audio.play('move')
        if race.too_small and not was_small:
            audio.stop()
        audio.tick()
        renderer.draw(race, race.too_small, audio.status)
        was_small = race.too_small
        time.sleep(max(0.0, FRAME_TIME - (time.monotonic() - start)))
