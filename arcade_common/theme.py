"""Paper / carbon ink / jade terminal theme shared by every cabinet (see DESIGN.md)."""

import curses


class PaperRenderer:
    """Palette setup and the text/box primitives; games subclass and add draw()."""

    def __init__(self, screen, no_color=False):
        self.screen = screen
        self.ink = 0
        self.accent = curses.A_BOLD
        self.warning = curses.A_BOLD | curses.A_UNDERLINE
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
                colors = (ink, jade, graphite, rule)
                for number, color in enumerate(colors, 1):
                    curses.init_pair(number, color, paper)
                self.ink = curses.color_pair(1)
                self.accent = curses.color_pair(2) | curses.A_BOLD
                self.muted = curses.color_pair(3)
                self.rule = curses.color_pair(4)
                self.warning = curses.A_BOLD | curses.A_UNDERLINE
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

    def _refresh(self):
        try:
            self.screen.refresh()
        except curses.error:
            pass
