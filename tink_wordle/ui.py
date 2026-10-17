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
    def __init__(self, screen, no_color=False):
        super().__init__(screen, no_color)
        # Pair 5 is reserved here so the shared palette stays unchanged for other games.
        if not no_color and curses.has_colors() and curses.COLORS >= 256 and curses.COLOR_PAIRS >= 5:
            curses.init_pair(5, 226, 230)
            self.warning = curses.color_pair(5) | curses.A_BOLD

    def _sound_status(self, sound_status):
        """Wordle uses F3; the shared audio service keeps its M hint for other games."""
        return sound_status.replace('[M]', '[F3]')

    def _state_attrs(self):
        strikeout = getattr(curses, 'A_STRIKEOUT', curses.A_DIM)
        return {
            'correct': self.accent | curses.A_REVERSE,
            'present': self.warning,
            'absent': self.muted | strikeout | curses.A_REVERSE,
        }

    def draw(self, game, too_small, sound_status=''):
        self.screen.erase()
        sound_status = self._sound_status(sound_status)
        rows, columns = self.screen.getmaxyx()
        if too_small:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, 'Socratink / paper wordle', self.ink | curses.A_BOLD)
            self.text(y + 1, 2, 'Resize terminal to at least 80 x 30.', curses.A_BOLD)
            self.text(y + 2, 2, f'Current: {columns} x {rows} // game frozen')
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, 'F3 mute  Esc quit  Ctrl-C exit', self.muted)
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
                mark = f'[{letter}]'
                if col < len(result):
                    state = result[col]
                    attr = self._state_attrs()[state]
                    mark = {'correct': f'[{letter}]',
                            'present': f'{{{letter}}}',
                            'absent': f'-{letter}-'}[state]
                self.text(oy + 6 + row * 2, ox + 12 + col * 5, mark, attr | curses.A_BOLD)
        self.box(oy + 4, ox + 47, 20, 25, 'SESSION')
        self.text(oy + 7, ox + 50, f'TRIES  {len(game.guesses)} / {MAX_GUESSES}', self.ink | curses.A_BOLD)
        self.text(oy + 10, ox + 50, game.message or 'Make a guess.', self.muted)
        keyboard = ('QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM')
        states = game.letter_states
        state_attrs = self._state_attrs()
        # Keep the physical keyboard with the guess grid, like Wordle, and
        # leave SESSION for status and the four-state legend.
        for row, keys in enumerate(keyboard):
            x = ox + (15, 16, 18)[row]
            for letter in keys:
                state = states.get(letter.lower())
                self.text(oy + 18 + row, x, letter,
                          state_attrs.get(state, self.ink))
                x += 2
        self.text(oy + 13, ox + 50, 'GREEN  right place', state_attrs['correct'])
        self.text(oy + 14, ox + 50, 'YELLOW wrong place', state_attrs['present'])
        self.text(oy + 15, ox + 50, 'DIM    not in word', state_attrs['absent'])
        self.text(oy + 16, ox + 50, 'INK    unused letter', self.ink)
        self.text(oy + 20, ox + 50, sound_status, self.muted)
        if game.status != 'playing':
            self.box(oy + 11, ox + 14, 7, 29)
            title = 'YOU WIN' if game.status == 'won' else 'WORD REVEALED'
            self.text(oy + 12, ox + 15 + (27 - len(title)) // 2, title, self.ink | curses.A_BOLD)
            self.text(oy + 14, ox + 17, game.message, self.muted)
            self.text(oy + 16, ox + 18, 'F2 restart   Esc quit', self.ink)
        self.text(oy + 26, ox + 8, 'Type letters   Backspace delete   Enter guess   F2 restart', self.ink)
        self.text(oy + 27, ox + 8, 'F3 mute   Esc quit   Ctrl-C exit', self.accent)
        self._refresh()


def handle_key(game, key, audio):
    if key == 3:
        return False
    if key in (curses.KEY_F3, 27):
        if key == curses.KEY_F3:
            audio.toggle()
        return key != 27
    if key == curses.KEY_F2:
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
                    if not too_small or key in (curses.KEY_F2, curses.KEY_F3, 27, 3):
                        if not handle_key(game, key, audio):
                            return audio.warning
                audio.tick()
                renderer.draw(game, too_small, audio.status)
                time.sleep(FRAME_TIME)
    except KeyboardInterrupt:
        return ''
