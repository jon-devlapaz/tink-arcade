"""Curses menu in the paper / carbon ink / jade language of DESIGN.md."""

import curses
import subprocess
import sys
import textwrap

MIN_COLUMNS = 80
MIN_ROWS = 30
LIST_WIDTH = 30


class Renderer:
    def __init__(self, screen, no_color=False):
        self.screen = screen
        self.ink = 0
        self.accent = curses.A_BOLD
        self.muted = self.rule = curses.A_DIM
        if not no_color and curses.has_colors():
            curses.start_color()
            if curses.COLORS >= 8 and curses.COLOR_PAIRS >= 5:
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
        if y < 0 or y >= rows or x < 0 or x >= columns:
            return
        width = columns - x - (1 if y == rows - 1 else 0)
        if width <= 0:
            return
        try:
            self.screen.addnstr(y, x, text, width, attr)
        except curses.error:
            pass

    def box(self, y, x, height, width, title=""):
        edge = "+" + "-" * (width - 2) + "+"
        self.text(y, x, edge, self.rule)
        self.text(y + height - 1, x, edge, self.rule)
        for row in range(y + 1, y + height - 1):
            self.text(row, x, "|", self.rule)
            self.text(row, x + width - 1, "|", self.rule)
        if title:
            self.text(y, x + 2, f" {title} ", self.ink | curses.A_BOLD)


def draw(r, games, index, notice=""):
    rows, columns = r.screen.getmaxyx()
    r.screen.erase()
    if rows < MIN_ROWS or columns < MIN_COLUMNS:
        r.text(rows // 2, max(0, (columns - 28) // 2), "Enlarge terminal to 80 x 30", r.ink)
        r.text(rows // 2 + 1, max(0, (columns - 6) // 2), "Q quits", r.muted)
        r.screen.refresh()
        return
    ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2

    r.text(oy + 1, ox + 4, ". tink / arcade", r.accent)
    r.text(oy + 2, ox + 4, "pick a cabinet. make room for the next idea.", r.muted)

    # Left: the cabinet list.
    top, height = oy + 5, 20
    r.box(top, ox + 3, height, LIST_WIDTH, "CABINETS")
    visible = height - 4
    first = min(max(0, index - visible + 1), max(0, len(games) - visible))
    for slot, number in enumerate(range(first, min(len(games), first + visible))):
        game = games[number]
        y = top + 2 + slot
        label = f" {number + 1:02d}  {game.title.upper():<{LIST_WIDTH - 10}} "
        if number == index:
            attr = (r.accent | curses.A_REVERSE) if game.available else (r.muted | curses.A_REVERSE)
            r.text(y, ox + 4, label.ljust(LIST_WIDTH - 2), attr)
        else:
            r.text(y, ox + 4, label, r.ink if game.available else r.muted)
    if first > 0:
        r.text(top, ox + LIST_WIDTH - 2, "^", r.muted)
    if first + visible < len(games):
        r.text(top + height - 1, ox + LIST_WIDTH - 2, "v", r.muted)

    # Right: details for the selected cabinet.
    game = games[index]
    left, width = ox + 3 + LIST_WIDTH + 2, MIN_COLUMNS - (3 + LIST_WIDTH + 2) - 3
    r.box(top, left, height, width, f"{index + 1:02d} / {game.title.upper()}")
    y = top + 2
    r.text(y, left + 3, game.tagline, r.accent)
    y += 2
    for line in textwrap.wrap(game.about, width - 6):
        r.text(y, left + 3, line, r.ink)
        y += 1
    y += 1
    r.text(y, left + 3, "CONTROLS", r.muted)
    y += 1
    for line in game.controls:
        r.text(y, left + 3, line, r.ink)
        y += 1
    if game.note:
        r.text(top + height - 4, left + 3, game.note, r.muted)
    r.text(top + height - 2, left + 3, game.status, r.accent if game.available else r.muted)

    # Footer.
    foot = oy + 26
    r.text(foot, ox + 4, "UP / DOWN choose    ENTER play    1-9 jump    Q quit", r.ink)
    r.text(foot + 1, ox + 4, notice or "scores are not saved. no network is needed.", r.muted)
    r.screen.refresh()


def launch(game, no_color):
    """Hand the terminal to a game, then take it back."""
    curses.def_prog_mode()
    curses.endwin()
    try:
        result = subprocess.run(game.command(sys.executable, no_color), cwd=game.cwd)
        code = result.returncode
    except OSError as error:
        code, detail = 1, str(error)
    else:
        detail = f"exit {code}"
    curses.reset_prog_mode()
    curses.flushinp()
    return "" if code == 0 else f"{game.title} stopped ({detail})."


def run(screen, games, no_color=False):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.keypad(True)
    r = Renderer(screen, no_color)
    index, notice = 0, ""
    while True:
        draw(r, games, index, notice)
        key = screen.getch()
        if key == curses.KEY_RESIZE:
            continue
        notice = ""
        if key in (ord("q"), ord("Q"), 27):
            return
        if key in (curses.KEY_UP, ord("w"), ord("W"), ord("k")):
            index = (index - 1) % len(games)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S"), ord("j")):
            index = (index + 1) % len(games)
        elif ord("1") <= key <= ord("9") and key - ord("1") < len(games):
            index = key - ord("1")
        elif key in (10, 13, curses.KEY_ENTER, ord(" ")):
            if games[index].available:
                notice = launch(games[index], no_color)
                screen.clear()
            else:
                notice = f"{games[index].title}: {games[index].status.lower()}."
