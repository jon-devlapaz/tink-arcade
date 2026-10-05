"""Curses presentation and input; the engine never depends on terminal state."""

import curses
import time

from arcade_common.audio import KeyboardAudio
from arcade_common.theme import PaperRenderer
from .engine import Game, HEIGHT, SHAPES, WIDTH

MIN_COLUMNS = 80
MIN_ROWS = 30
FRAME_TIME = 1 / 60


class Renderer(PaperRenderer):
    def block(self, y, x, kind, ghost=False, active=False):
        if ghost:
            self.text(y, x, "()", self.muted | curses.A_DIM)
        else:
            self.text(y, x, "[]", (self.accent if active else self.ink) | curses.A_REVERSE)

    def preview(self, kind, y, x):
        if kind is None:
            self.text(y, x, "-- empty --", self.muted)
            return
        cells = SHAPES[kind][0]
        min_x = min(cx for cx, _ in cells)
        min_y = min(cy for _, cy in cells)
        for cx, cy in cells:
            self.block(y + cy - min_y, x + 2 * (cx - min_x), kind)

    def draw(self, game, too_small, sound_status=""):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if too_small:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, "Socratink / paper tetris", self.ink | curses.A_BOLD)
            self.text(y + 1, 2, "Resize terminal to at least 80 x 30.", curses.A_BOLD)
            self.text(y + 2, 2, f"Current: {columns} x {rows} // simulation frozen")
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, "Q quit  |  Ctrl-C exit", self.muted)
            self._refresh()
            return

        # Center a fixed ASCII canvas; its dimensions never depend on Unicode width.
        ox = (columns - MIN_COLUMNS) // 2
        oy = (rows - MIN_ROWS) // 2
        title = ". socratink  /  paper tetris"
        subtitle = "make room for the next idea."
        self.text(oy + 1, ox + (MIN_COLUMNS - len(title)) // 2, title, self.ink | curses.A_BOLD)
        self.text(oy + 2, ox + (MIN_COLUMNS - len(subtitle)) // 2, subtitle, self.muted)
        bx, by = ox + 29, oy + 5
        self.box(by - 1, bx - 1, HEIGHT + 2, WIDTH * 2 + 2, "PLAY / PAPER")
        for y, row in enumerate(game.board):
            for x, kind in enumerate(row):
                if kind:
                    self.block(by + y, bx + x * 2, kind)
                else:
                    self.text(by + y, bx + x * 2, " .", self.muted)
        ghost = game.ghost()
        if ghost:
            active_cells = set(game.active.cells())
            for x, y in ghost.cells():
                if y >= 0 and (x, y) not in active_cells:
                    self.block(by + y, bx + x * 2, ghost.kind, ghost=True)
        if game.active:
            for x, y in game.active.cells():
                if 0 <= y < HEIGHT:
                    self.block(by + y, bx + x * 2, game.active.kind, active=True)
        if game.flash_time > 0:
            for y in game.flash_rows:
                self.text(by + y, bx, "=" * (WIDTH * 2), self.accent | curses.A_REVERSE)

        self.box(oy + 4, ox + 3, 7, 22, "HOLD / MARGIN")
        self.preview(game.held, oy + 6, ox + 9)
        self.text(oy + 9, ox + 6, "LOCKED" if game.hold_used else "C  swap / store",
                  self.muted if game.hold_used else self.accent)
        self.box(oy + 12, ox + 3, 14, 22, "SESSION")
        for y, label, value in ((14, "SCORE", game.score), (17, "LEVEL", game.level),
                                (20, "LINES", game.lines), (23, "SESSION BEST", game.best)):
            self.text(oy + y, ox + 6, label, self.muted)
            self.text(oy + y + 1, ox + 6, f"{value:,}", curses.A_BOLD)
        self.box(oy + 4, ox + 53, 17, 23, "NEXT / 7-BAG")
        for index, kind in enumerate(game.bag.preview(3)):
            self.text(oy + 6 + index * 5, ox + 56, f"0{index + 1}", self.muted)
            self.preview(kind, oy + 6 + index * 5, ox + 61)
        if game.message_time > 0 and not game.game_over:
            messages = {"READY // GO": "A fresh page.", "SINGLE": "One line, distilled.",
                        "DOUBLE": "Two lines, distilled.", "TRIPLE": "Three lines, distilled.",
                        "TETRIS!": "A clean slate. +4"}
            self.text(oy + 22, ox + 55, messages.get(game.message, game.message), self.ink)
        self.text(oy + 23, ox + 55, sound_status, self.muted)
        self.text(oy + 24, ox + 55, "() pencil / ghost", self.muted)

        if game.paused or game.game_over:
            self.box(oy + 11, bx, 7, 20)
            for y in range(oy + 12, oy + 17):
                self.text(y, bx + 1, " " * 18)
            self.text(oy + 12, bx + 3, "GAME OVER" if game.game_over else "PAUSED",
                      curses.A_BOLD | self.ink)
            self.text(oy + 13, bx + 1, "Turn a fresh page." if game.game_over else "Take a breath.",
                      self.muted)
            self.text(oy + 14, bx + 2, "R  restart" if game.game_over else "P  resume")
            self.text(oy + 16, bx + 2, "Q  quit")

        self.text(oy + 27, ox + 3, "<- -> / A D move   Down/S soft drop   Up/X rotate   Z reverse")
        self.text(oy + 28, ox + 3, "Space DROP  C hold  P pause  R restart  M mute  Q quit  Ctrl-C exit",
                  self.accent)
        self._refresh()

    def _refresh(self):
        try:
            self.screen.refresh()
        except curses.error:
            pass  # Terminal dimensions may change while flushing a frame.


def _perform(game, action, audio, cue=None):
    if audio is None or not audio.audible:
        return action()
    before = (game.game_over, game.lines, tuple(map(tuple, game.board)))
    result = action()
    if game.game_over and not before[0]:
        audio.play("over")
    elif game.lines > before[1]:
        audio.play("clear")
    elif tuple(map(tuple, game.board)) != before[2]:
        audio.play("place")
    elif result and cue:
        audio.play(cue)
    return result


def handle_key(game, key, audio=None):
    """Return False to quit. Restart, pause and mute work on overlays."""
    if key in (ord("q"), ord("Q"), 3):
        return False
    if key in (ord("m"), ord("M")):
        if audio is not None:
            audio.toggle()
    elif key in (ord("r"), ord("R")):
        game.restart()
        if audio is not None:
            audio.stop()
            audio.play("switch")
    elif key in (ord("p"), ord("P")):
        paused = game.paused
        game.toggle_pause()
        if audio is not None and game.paused != paused:
            audio.stop()
            audio.play("switch")
    elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
        _perform(game, lambda: game.move(-1), audio, "move")
    elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
        _perform(game, lambda: game.move(1), audio, "move")
    elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
        _perform(game, game.soft_drop, audio, "move")
    elif key in (curses.KEY_UP, ord("x"), ord("X")):
        _perform(game, lambda: game.rotate(1), audio, "rotate")
    elif key in (ord("z"), ord("Z")):
        _perform(game, lambda: game.rotate(-1), audio, "rotate")
    elif key == ord(" "):
        _perform(game, game.hard_drop, audio, "place")
    elif key in (ord("c"), ord("C")):
        _perform(game, game.hold, audio, "switch")
    return True


def run(screen, seed=None, no_color=False, no_sound=False):
    try:
        curses.curs_set(0)
    except curses.error:
        pass  # Some terminals cannot change cursor visibility.
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer = Renderer(screen, no_color)
    game = Game(seed)
    with KeyboardAudio(enabled=not no_sound) as audio:
        _run_loop(screen, renderer, game, audio)
        return audio.warning


def _run_loop(screen, renderer, game, audio):
    previous = time.monotonic()
    was_small = False
    while True:
        frame_start = time.monotonic()
        dt = frame_start - previous
        previous = frame_start
        rows, columns = screen.getmaxyx()
        too_small = rows < MIN_ROWS or columns < MIN_COLUMNS
        # Drain bounded input batches so key repeat cannot starve rendering.
        for _ in range(32):
            try:
                key = screen.getch()
            except curses.error:
                key = -1
            if key == -1:
                break
            if key in (ord("q"), ord("Q"), 3):
                return
            if key in (ord("m"), ord("M")) or (not too_small and key != curses.KEY_RESIZE):
                if not handle_key(game, key, audio):
                    return
        if too_small and not was_small:
            audio.stop()
        if not too_small and not was_small:
            _perform(game, lambda: game.update(dt), audio)
        audio.tick()
        renderer.draw(game, too_small, audio.status)
        was_small = too_small
        time.sleep(max(0.0, FRAME_TIME - (time.monotonic() - frame_start)))
