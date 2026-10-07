"""Curses presentation and input; the engine never depends on terminal state."""

import curses
import json
import os
import time

from arcade_common.audio import KeyboardAudio
from arcade_common.theme import PaperRenderer
from .engine import DOWN, Game, LEFT, RIGHT, UP

MIN_COLUMNS = 80
MIN_ROWS = 40
FRAME_TIME = 1 / 60
FACING = {RIGHT: 'O>', LEFT: '<O', UP: 'O^', DOWN: 'Ov'}
GHOST_MARKS = {'blinky': 'Bl', 'pinky': 'Pk', 'inky': 'In', 'clyde': 'Cl'}


def wall_mark(maze, tile):
    """Two characters of line art for a wall tile, or None. Only edges facing a non-wall tile are drawn,
    and the outer ring is left to the box border."""
    x, y = tile
    if tile not in maze.walls or x in (0, maze.width - 1) or y in (0, maze.height - 1):
        return None

    def facing(dx, dy):
        return (x + dx, y + dy) not in maze.walls

    flat = facing(0, -1) or facing(0, 1)
    left, right = facing(-1, 0), facing(1, 0)
    marks = ('+' if flat and left else '|' if left else '-' if flat else ' ',
             '+' if flat and right else '|' if right else '-' if flat else ' ')
    return ''.join(marks) if any(m != ' ' for m in marks) else None


class Renderer(PaperRenderer):
    def draw(self, game, too_small, sound_status=''):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if too_small:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, 'Socratink / paper pac-man', self.ink | curses.A_BOLD)
            self.text(y + 1, 2, f'Resize terminal to at least {MIN_COLUMNS} x {MIN_ROWS}.', curses.A_BOLD)
            self.text(y + 2, 2, f'Current: {columns} x {rows} // simulation frozen')
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, 'M mute  Q quit  Ctrl-C exit', self.muted)
            self._refresh()
            return
        ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
        for row, text, attr in ((1, '. socratink  /  paper pac-man', self.ink | curses.A_BOLD),
                                (2, 'clear the page, dot by dot.', self.muted)):
            self.text(oy + row, ox + (MIN_COLUMNS - len(text)) // 2, text, attr)
        maze = game.maze
        self.box(oy + 4, ox + 3, maze.height + 2, maze.width * 2 + 2, 'PLAY / PAPER')
        self._draw_maze(game, ox + 4, oy + 5)
        for column in (ox + 3, ox + 4 + maze.width * 2):  # the tunnel is an opening in the border
            self.text(oy + 5 + maze.tunnel_row, column, ' ')
        self._draw_panel(game, ox + 62, oy + 4)
        for row, mark, name, attr in ((21, 'O>', 'pac-man', self.accent), (22, '()', 'energizer', self.accent),
                                      (23, ' .', 'dot', self.ink), (24, 'Bl', 'ghost', self.ink | curses.A_REVERSE)):
            self.text(oy + row, ox + 63, mark, attr)
            self.text(oy + row, ox + 66, name, self.muted)
        if game.paused or game.game_over:
            x, y = ox + 18, oy + 17
            self.box(y, x, 7, 28)
            for row in range(1, 6):
                self.text(y + row, x + 1, ' ' * 26, self.ink)
            title = 'GAME OVER' if game.game_over else 'PAUSED'
            self.text(y + 1, x + (28 - len(title)) // 2, title, self.ink | curses.A_BOLD)
            self.text(y + 2, x + 7, 'Turn a fresh page.' if game.game_over else 'Take a breath.', self.muted)
            self.text(y + 3, x + 4, 'R restart' if game.game_over else 'P resume  R restart')
            self.text(y + 5, x + 4, 'Q quit')
        self.text(oy + 37, ox + 3, sound_status, self.muted)
        self.text(oy + 38, ox + 3, 'Arrows / WASD steer   P pause   R restart   M mute')
        controls = 'Q quit   Ctrl-C exit' if game.classic else 'Space bookmark   E erase   Q quit   Ctrl-C exit'
        self.text(oy + 39, ox + 3, controls, self.accent)
        self._refresh()

    def _draw_maze(self, game, left, top):
        maze = game.maze
        for y in range(maze.height):
            for x in range(maze.width):
                tile = (x, y)
                at = (top + y, left + x * 2)
                if tile in maze.walls:
                    mark = wall_mark(maze, tile)
                    if mark:
                        self.text(*at, mark, self.rule)
                elif tile in maze.door:
                    self.text(*at, '--', self.rule)
                elif tile == game.pacman:
                    self.text(*at, FACING[game.direction], self.accent | curses.A_REVERSE)
                elif tile == game.bookmark:
                    self.text(*at, '[]', self.accent)
                elif tile in game.dots:
                    if tile in maze.energizers:
                        self.text(*at, '()', self.accent)
                    else:
                        self.text(*at, ' .', self.ink)
        for ghost in game.ghosts:
            x, y = ghost.tile
            self.text(top + y, left + x * 2, *self._ghost_mark(game, ghost))

    def _ghost_mark(self, game, ghost):
        if ghost.state in ('eyes', 'entering'):
            return 'oo', self.ink | curses.A_BOLD
        if ghost.frightened and not game.flashing:
            return '~~', self.muted | curses.A_REVERSE
        return GHOST_MARKS[ghost.name], self.ink | curses.A_REVERSE

    def _draw_panel(self, game, left, top):
        self.box(top, left, 15, 16, 'SESSION')
        for row, label, value in ((2, 'SCORE', f'{game.score:,}'), (5, 'LEVEL', game.level),
                                  (8, 'LIVES', game.lives), (11, 'BEST', f'{game.best:,}')):
            self.text(top + row, left + 2, label, self.muted)
            self.text(top + row + 1, left + 2, str(value), self.ink | curses.A_BOLD)
        if not game.classic:
            for row, label, available in ((27, 'Bookmark', game.bookmark_available),
                                           (28, 'Eraser', game.eraser_available)):
                self.text(top + row, left + 1, f'{label} {int(available)}', self.accent)
            if game.bookmark is not None:
                self.text(top + 29, left + 1, 'Bookmark active', self.accent)


KEYS = {curses.KEY_LEFT: LEFT, curses.KEY_RIGHT: RIGHT, curses.KEY_UP: UP, curses.KEY_DOWN: DOWN}
for _letters, _direction in (('aA', LEFT), ('dD', RIGHT), ('wW', UP), ('sS', DOWN)):
    KEYS.update({ord(letter): _direction for letter in _letters})


def handle_key(game, key, audio=None):
    if key in (ord('q'), ord('Q'), 3):
        return False
    cue = None
    if key in (ord('m'), ord('M')):
        if audio is not None:
            audio.toggle()
    elif key in (ord('r'), ord('R')):
        game.restart()
    elif key in (ord('p'), ord('P')):
        game.toggle_pause()
    elif key == ord(' '):
        cue = game.drop_bookmark()
    elif key in (ord('e'), ord('E')):
        cue = game.erase()
    elif key in KEYS:
        game.turn(KEYS[key])
    if audio is not None:
        if key in map(ord, 'pPrR'):
            audio.stop()
        if cue:
            audio.play(cue)
    return True


def run(screen, seed=None, no_color=False, classic=False, no_sound=False):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer, game = Renderer(screen, no_color), Game(seed, classic=classic)
    trace_path = os.environ.get('TINK_PACMAN_TRACE')
    trace = open(trace_path, 'w', encoding='utf-8') if trace_path else None
    try:
        with KeyboardAudio(enabled=not no_sound) as audio:
            _run_loop(screen, renderer, game, audio, trace)
    finally:
        if trace:
            trace.close()


def _trace_state(game, too_small, sound):
    return dict(pacman=game.pacman, direction=game.direction, turn_buffer=game.turn_buffer,
                progress=game.progress, dots=sorted(game.dots), walls=sorted(game.maze.walls),
                ghosts=[vars(ghost).copy() for ghost in game.ghosts],
                score=game.score, best=game.best, level=game.level, lives=game.lives,
                paused=game.paused, over=game.game_over, fright_left=game.fright_left,
                waves=vars(game.waves).copy(), pen=vars(game.pen).copy(),
                bookmark=game.bookmark, bookmark_left=game.bookmark_left,
                bookmark_available=game.bookmark_available, eraser_available=game.eraser_available,
                small=too_small, sound=sound)


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
            game.turn_buffer = None
            audio.stop()
        transition = False  # time before pause/resume or restart belongs to the preceding state
        for _ in range(32):
            try:
                key = screen.getch()
            except curses.error:
                key = -1
            if key == -1:
                break
            if key in (ord('q'), ord('Q'), 3):
                return
            if key in map(ord, 'mM') or (not too_small and key != curses.KEY_RESIZE):
                transition = transition or key in map(ord, 'pPrR')
                handle_key(game, key, audio)
        if not too_small and not was_small and not transition:
            cue = game.update(dt)
            if cue:
                audio.play(cue)
        audio.tick()
        renderer.draw(game, too_small, audio.status)
        if trace:
            trace.write(json.dumps(_trace_state(game, too_small, audio.status)) + '\n')
            trace.flush()
        was_small = too_small
        time.sleep(max(0.0, FRAME_TIME - (time.monotonic() - frame_start)))
