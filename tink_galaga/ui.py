"""Curses display and keyboard controls."""
import curses
import time
from neon_tetris.audio import KeyboardAudio
from .engine import Game, Clock, WIDTH, HEIGHT, PLAYER_Y

MIN_COLS, MIN_ROWS = 80, 30


def handle_key(game, key):
    if key in (ord('q'), ord('Q'), 3):
        return False
    if key in (ord('p'), ord('P')) and not game.game_over:
        game.paused = not game.paused
    elif key in (ord('r'), ord('R')):
        game.restart()
    elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
        game.move(-1)
    elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
        game.move(1)
    elif key == ord(' '):
        game.fire()
    return True


class Renderer:
    def __init__(self, screen, no_color=False):
        self.screen = screen
        self.ink = 0
        self.accent = curses.A_BOLD
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
                for number, color in enumerate((ink, jade, graphite, rule), 1):
                    curses.init_pair(number, color, paper)
                self.ink = curses.color_pair(1)
                self.accent = curses.color_pair(2) | curses.A_BOLD
                self.muted = curses.color_pair(3)
                self.rule = curses.color_pair(4)
                self.screen.bkgd(' ', self.ink)

    def text(self, row, col, text, attr=0):
        rows, cols = self.screen.getmaxyx()
        if 0 <= row < rows and 0 <= col < cols - 1:
            try:
                self.screen.addnstr(row, col, text, cols - col - 1, attr)
            except curses.error:
                pass  # A terminal may resize between bounds checking and drawing.

    def box(self, y, x, height, width, title=''):
        self.text(y, x, '+' + '-' * (width - 2) + '+', self.rule)
        for row in range(y + 1, y + height - 1):
            self.text(row, x, '|', self.rule)
            self.text(row, x + width - 1, '|', self.rule)
        self.text(y + height - 1, x, '+' + '-' * (width - 2) + '+', self.rule)
        if title:
            self.text(y, x + 2, ' ' + title + ' ', self.ink)

    def draw(self, game, sound_status=''):
        self.screen.erase()
        rows, cols = self.screen.getmaxyx()
        if rows < MIN_ROWS or cols < MIN_COLS:
            y = max(0, rows // 2 - 2)
            self.text(y, 2, 'Socratink / paper galaga', self.ink | curses.A_BOLD)
            self.text(y + 1, 2, 'Resize terminal to at least 80 x 30.', curses.A_BOLD)
            self.text(y + 2, 2, f'Current: {cols} x {rows} // game frozen')
            self.text(y + 3, 2, sound_status, self.muted)
            self.text(y + 4, 2, 'M mute  Q quit  Ctrl-C exit', self.muted)
            self.screen.refresh()
            return
        ox, oy = (cols - MIN_COLS) // 2, (rows - MIN_ROWS) // 2
        x, y = ox + (MIN_COLS - WIDTH - 2) // 2, oy + 4
        self.text(oy + 1, ox + 26, '. socratink / paper galaga', self.ink | curses.A_BOLD)
        self.text(oy + 2, ox + 31, 'hold the formation.', self.muted)
        self.text(oy + 3, x + WIDTH + 2 - len(sound_status), sound_status, self.muted)
        self.text(oy + 3, x, f'SCORE {game.score:06d}   LIVES {game.lives}   WAVE {game.wave}', self.ink)
        self.box(y, x, HEIGHT + 2, WIDTH + 2, 'PLAY / PAPER')
        for enemy in game.enemies:
            sprite = 'vVv' if enemy.dive is not None else '<o>'
            self.text(y + 1 + round(enemy.y), x + round(enemy.x), sprite, self.ink | curses.A_BOLD)
        for bullet in game.bullets:
            self.text(y + 1 + min(HEIGHT - 1, max(0, round(bullet.y))), x + 1 + round(bullet.x),
                      '!' if bullet.hostile else '|', self.ink | curses.A_BOLD if bullet.hostile else self.accent)
        if not game.game_over and (game.protection <= 0 or game.tick % 12 < 8):
            self.text(y + 1 + PLAYER_Y, x + round(game.player_x), '/^\\', self.accent)
        if game.game_over:
            self.text(y + 12, x + 25, 'GAME OVER  R to restart', self.accent | curses.A_REVERSE)
        elif game.paused:
            self.text(y + 12, x + 27, 'PAUSED  P to resume', self.accent | curses.A_REVERSE)
        self.text(oy + 28, x, 'A/D or arrows move   SPACE fires   P pause   R restart', self.ink)
        self.text(oy + 29, x, 'M mute   Q quit   Ctrl-C exit', self.muted)
        self.screen.refresh()


def observe(game):
    return dict(score=game.score, lives=game.lives, wave=game.wave, over=game.game_over,
                paused=game.paused, shots=sum(1 for b in game.bullets if not b.hostile))


def cue_for(before, after, key):
    """Map one frame's observable change to a keyboard-sound cue, or None."""
    if after['over'] and not before['over']:
        return 'over'
    if after['wave'] > before['wave']:
        return 'clear'
    if after['lives'] < before['lives']:
        return 'over'
    if after['score'] > before['score']:
        return 'place'
    if after['shots'] > before['shots']:
        return 'rotate'
    if after['paused'] != before['paused'] or after['score'] < before['score']:
        return 'switch'
    if key in (curses.KEY_LEFT, curses.KEY_RIGHT, ord('a'), ord('A'), ord('d'), ord('D')):
        return 'move'
    return None


def run(screen, seed=None, no_color=False, no_sound=False):
    curses.curs_set(0)
    screen.nodelay(True)
    screen.keypad(True)
    curses.set_escdelay(25)
    renderer = Renderer(screen, no_color)
    game, clock = Game(seed), Clock()
    last = time.monotonic()
    was_small = False
    with KeyboardAudio(enabled=not no_sound) as audio:
        while True:
            now = time.monotonic()
            elapsed, last = now - last, now
            rows, cols = screen.getmaxyx()
            small = rows < MIN_ROWS or cols < MIN_COLS
            if small and not was_small:
                audio.stop()
            transition = False
            before, last_key = observe(game), -1
            # Limit each batch so a stream of input cannot starve rendering or quitting.
            for _ in range(64):
                key = screen.getch()
                if key == -1:
                    break
                if key in (ord('q'), ord('Q'), 3):
                    return audio.warning
                if key in (ord('m'), ord('M')):
                    audio.toggle()
                    continue
                if small and key != curses.KEY_RESIZE:
                    continue
                transition |= key in (ord('p'), ord('P'), ord('r'), ord('R'), curses.KEY_RESIZE)
                last_key = key
                if not handle_key(game, key):
                    return audio.warning
            clock.advance(game, elapsed, blocked=small or was_small or transition)
            was_small = small
            if not small:
                cue = cue_for(before, observe(game), last_key)
                if cue:
                    audio.play(cue)
            audio.tick()
            renderer.draw(game, audio.status)
            time.sleep(1 / 60)
