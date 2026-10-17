"""Curses presentation and input for Paper Wordle."""
import curses
import time

from arcade_common.audio import KeyboardAudio
from arcade_common.theme import PaperRenderer
from .engine import Game, MAX_GUESSES, WORD_LENGTH

MIN_COLUMNS = 80
MIN_ROWS = 30
FRAME_TIME = 1 / 30


class Renderer(PaperRenderer):
    def draw(self, game, too_small, sound_status=''):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if too_small:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, 'Socratink / paper wordle', self.ink | curses.A_BOLD)
            self.text(y + 1, 2, 'Resize terminal to at least 80 x 30.', curses.A_BOLD)
            self.text(y + 2, 2, f'Current: {columns} x {rows} // game frozen')
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, 'M mute  Q quit  Ctrl-C exit', self.muted)
            self._refresh()
            return
        ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
        self.text(oy + 1, ox + 29, '. socratink / paper wordle', self.ink | curses.A_BOLD)
        self.text(oy + 2, ox + 33, 'six tries.', self.muted)
        self.box(oy + 4, ox + 8, 20, 34, 'PLAY / PAPER')
        for row in range(MAX_GUESSES):
            guess = game.guesses[row] if row < len(game.guesses) else game.current if row == len(game.guesses) else ''
            result = game.results[row] if row < len(game.results) else ()
            for col in range(WORD_LENGTH):
                letter = guess[col].upper() if col < len(guess) else ' '
                attr = self.muted
                if col < len(result):
                    attr = {'correct': self.accent | curses.A_REVERSE,
                            'present': self.accent, 'absent': self.muted}[result[col]]
                self.text(oy + 6 + row * 2, ox + 12 + col * 5, f'[{letter}]', attr | curses.A_BOLD)
        self.box(oy + 4, ox + 47, 20, 25, 'SESSION')
        self.text(oy + 7, ox + 50, f'TRIES  {len(game.guesses)} / {MAX_GUESSES}', self.ink | curses.A_BOLD)
        self.text(oy + 10, ox + 50, game.message or 'Make a guess.', self.muted)
        self.text(oy + 14, ox + 50, 'GREEN  right place', self.accent)
        self.text(oy + 15, ox + 50, 'JADE   wrong place', self.ink)
        self.text(oy + 16, ox + 50, 'DIM    not in word', self.muted)
        self.text(oy + 20, ox + 50, sound_status, self.muted)
        if game.status != 'playing':
            self.box(oy + 11, ox + 14, 7, 29)
            title = 'YOU WIN' if game.status == 'won' else 'WORD REVEALED'
            self.text(oy + 12, ox + 15 + (27 - len(title)) // 2, title, self.ink | curses.A_BOLD)
            self.text(oy + 14, ox + 17, game.message, self.muted)
            self.text(oy + 16, ox + 18, 'R restart   Q quit', self.ink)
        self.text(oy + 26, ox + 8, 'Type letters   Backspace delete   Enter guess   R restart', self.ink)
        self.text(oy + 27, ox + 8, 'M mute   Q quit   Ctrl-C exit', self.accent)
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
    elif key in (curses.KEY_BACKSPACE, 127, 8):
        if game.remove_letter():
            audio.play('move')
    elif key in (curses.KEY_ENTER, 10, 13):
        result = game.submit()
        if result is not None:
            audio.play('clear' if game.status == 'won' else 'place')
        elif game.status == 'playing' and game.message:
            audio.play('over')
    elif 0 <= key < 256 and chr(key).isalpha():
        if game.add_letter(chr(key)):
            audio.play('move')
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
    game = Game(seed=seed)
    try:
        with KeyboardAudio(enabled=not no_sound) as audio:
            while True:
                rows, columns = screen.getmaxyx()
                too_small = rows < MIN_ROWS or columns < MIN_COLUMNS
                for _ in range(32):
                    try:
                        key = screen.getch()
                    except curses.error:
                        key = -1
                    if key == -1:
                        break
                    if not too_small or key in (ord('q'), ord('Q'), ord('m'), ord('M'), 3):
                        if not handle_key(game, key, audio):
                            return audio.warning
                audio.tick()
                renderer.draw(game, too_small, audio.status)
                time.sleep(FRAME_TIME)
    except KeyboardInterrupt:
        return ''
