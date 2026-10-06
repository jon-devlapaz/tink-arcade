"""Curses presentation and input; the engine never depends on terminal state."""

import curses
import json
import os
import time

from arcade_common.audio import KeyboardAudio
from arcade_common.theme import PaperRenderer
from .engine import Game, HEIGHT, WIDTH, WINS, LEFT, RIGHT, UP, DOWN

MIN_COLUMNS = 80
MIN_ROWS = 30
FRAME_TIME = 1 / 60
MARKS = (('##', '=='), ('@@', '::'))  # head, trail: distinct shapes so players differ without color
ARROWS = {curses.KEY_LEFT: LEFT, curses.KEY_RIGHT: RIGHT, curses.KEY_UP: UP, curses.KEY_DOWN: DOWN}
LETTERS = {ord(letter): direction for letters, direction in (('aA', LEFT), ('dD', RIGHT), ('wW', UP), ('sS', DOWN))
           for letter in letters}


def key_turns(game, key):
    """(player, direction) pairs a key press asks for: solo, both schemes steer you; two-player, WASD and arrows split."""
    if game.two_player:
        return [(0, LETTERS[key])] if key in LETTERS else [(1, ARROWS[key])] if key in ARROWS else []
    direction = LETTERS.get(key) or ARROWS.get(key)
    return [(0, direction)] if direction else []


class Renderer(PaperRenderer):
    def _scoreboard(self, game, jev=None):
        names = ('YOU', 'JEV') if jev else ('PLAYER 1', 'PLAYER 2') if game.two_player else ('YOU', f'MACHINE ({game.level})')
        left = f'{names[0]} {MARKS[0][0]}  {game.scores[0]}'
        right = f'{game.scores[1]}  {MARKS[1][0]} {names[1]}'
        return left, f'ROUND {game.round}  first to {WINS}', right

    def draw(self, game, too_small, sound_status='', jev=None):
        """`jev` is an optional (status, cost, hold_title, hold_hint) tuple for Tron vs Jev; hold_title is '' when play runs."""
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if too_small:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, 'Socratink / paper tron', self.ink | curses.A_BOLD)
            self.text(y + 1, 2, 'Resize terminal to at least 80 x 30.', curses.A_BOLD)
            self.text(y + 2, 2, f'Current: {columns} x {rows} // simulation frozen')
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, 'M mute  Q quit  Ctrl-C exit', self.muted)
            self._refresh()
            return
        ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
        subtitle = f'{jev[0]}  |  {jev[1]}' if jev else 'leave a line, cut a line.'
        for row, text, attr in ((1, '. socratink  /  paper tron', self.ink | curses.A_BOLD),
                                (2, subtitle[:MIN_COLUMNS - 2], self.muted)):
            self.text(oy + row, ox + (MIN_COLUMNS - len(text)) // 2, text, attr)
        left, middle, right = self._scoreboard(game, jev)
        self.text(oy + 3, ox + 1, left, self.accent)
        self.text(oy + 3, ox + (MIN_COLUMNS - len(middle)) // 2, middle, self.muted)
        self.text(oy + 3, ox + MIN_COLUMNS - 1 - len(right), right, self.ink | curses.A_BOLD)
        self.box(oy + 4, ox + 1, HEIGHT + 2, WIDTH * 2 + 2, 'PLAY / PAPER')
        for y in range(HEIGHT):
            for x in range(WIDTH):
                cell = (x, y)
                owner = game.trails.get(cell)
                if owner is None:
                    text, attr = ' .', self.muted
                else:
                    head, trail = MARKS[owner]
                    base = self.accent if owner == 0 else self.ink
                    if game.heads[owner] == cell:
                        text, attr = head, base | curses.A_BOLD | curses.A_REVERSE
                    else:
                        text, attr = trail, base
                self.text(oy + 5 + y, ox + 2 + x * 2, text, attr)
        self.text(oy + 26, ox + 3, f'{MARKS[0][0]} P1 head  {MARKS[0][1]} trail    {MARKS[1][0]} P2 head  {MARKS[1][1]} trail', self.muted)
        self.text(oy + 26, ox + MIN_COLUMNS - 3 - len(sound_status), sound_status, self.muted)
        hold = jev[2] if jev else ''
        rival = 'JEV' if jev else 'THE MACHINE'
        if hold or game.paused or game.round_over:
            x, y = ox + 22, oy + 11
            self.box(y, x, 7, 36)
            for row in range(1, 6):
                self.text(y + row, x + 1, ' ' * 34, self.ink)
            if hold:
                title, hint, keys = hold, jev[3], 'Enter retry  R restart' if 'ERROR' in hold else 'R restart'
            elif game.match_winner is not None:
                title = ('PLAYER 2 WINS THE MATCH' if game.match_winner else 'PLAYER 1 WINS THE MATCH') if game.two_player \
                    else ('YOU WIN THE MATCH' if game.match_winner == 0 else f'{rival} WINS THE MATCH')
                hint, keys = 'Turn a fresh page.', 'R new match'
            elif game.round_over:
                if game.winner is None:
                    title = 'DRAW: REPLAY THE ROUND'
                elif game.two_player:
                    title = f'PLAYER {game.winner + 1} TAKES THE ROUND'
                else:
                    title = 'YOU TAKE THE ROUND' if game.winner == 0 else f'{rival} TAKES THE ROUND'
                hint, keys = 'Space for the next round.', 'Space next  R restart'
            else:
                title, hint, keys = 'PAUSED', 'Take a breath.', 'P resume  R restart'
            self.text(y + 1, x + (36 - len(title)) // 2, title, self.ink | curses.A_BOLD)
            self.text(y + 2, x + 6, hint, self.muted)
            self.text(y + 3, x + 6, keys)
            self.text(y + 5, x + 6, 'M mute    Q quit')
        controls = ('WASD player 1   Arrows player 2' if game.two_player else 'Arrows / WASD steer')
        self.text(oy + 27, ox + 3, f'{controls}   Space next round   P pause   R restart')
        self.text(oy + 28, ox + 3, 'Enter retry   R restart   Q quit' if hold and 'ERROR' in hold else 'M mute   Q quit   Ctrl-C exit', self.accent)
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
    elif key in (ord('p'), ord('P')):
        if game.toggle_pause():
            audio.stop()
            audio.play('switch')
    elif key == ord(' '):
        if game.next_round():
            audio.stop()
            audio.play('switch')
    else:
        for player, direction in key_turns(game, key):
            game.turn(player, direction)
    return True


def run(screen, seed=None, two_player=False, level='normal', no_color=False, no_sound=False):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer = Renderer(screen, no_color)
    game = Game(seed, two_player, level)
    # Trace is observation only; no game state is read from the environment.
    trace_path = os.environ.get('TINK_TRON_TRACE')
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
            game.pending = [None, None]
            audio.stop()
        # Time before pause/resume or restart belongs to the preceding state.
        transition = False
        for _ in range(32):
            try:
                key = screen.getch()
            except curses.error:
                key = -1
            if key == -1:
                break
            if key in (ord('q'), ord('Q'), 3):
                return
            if key in (ord('m'), ord('M')) or (not too_small and key != curses.KEY_RESIZE):
                if key in map(ord, 'pPrR '):
                    transition = True
                handle_key(game, key, audio)
        cue = None
        if not too_small and not was_small and not transition:
            cue = game.update(dt)
            if cue:
                audio.play(cue)
        audio.tick()
        renderer.draw(game, too_small, audio.status)
        if trace:
            trace.write(json.dumps(dict(heads=game.heads, dirs=game.dirs, pending=game.pending, scores=game.scores,
                                        round=game.round, trail=len(game.trails), paused=game.paused,
                                        over=game.round_over, winner=game.winner, match=game.match_winner,
                                        elapsed=game.elapsed, small=too_small, sound=audio.status, cue=cue)) + '\n')
            trace.flush()
        was_small = too_small
        time.sleep(max(0.0, FRAME_TIME - (time.monotonic() - frame_start)))
