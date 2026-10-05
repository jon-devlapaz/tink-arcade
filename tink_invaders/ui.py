"""Curses presentation, bounded input and wall-clock ownership."""
import curses
import json
import os
import time
from arcade_common.audio import KeyboardAudio
from arcade_common.theme import PaperRenderer
from .engine import Game, WIDTH, HEIGHT, SHIP_Y, NAMES, MAX_ELAPSED

MIN_COLUMNS, MIN_ROWS, FRAME_TIME, MAX_KEYS = 80, 30, 1 / 60, 32


class Controller:
    def __init__(self, now, seed=None):
        self.game = Game(seed)
        self.last = now
        self.paused = self.small = self.quit = False
        self.discard_input = False

    def frame(self, now, rows, columns, keys=(), audio=None):
        elapsed = max(0, now - self.last)
        self.last = now
        was_frozen = self.paused or self.small
        was_small = self.small
        self.small = rows < MIN_ROWS or columns < MIN_COLUMNS
        transition = False
        if self.small and not was_small and audio:
            audio.stop()
        for key in keys[:MAX_KEYS]:
            if key in (ord('q'), ord('Q'), 3):
                self.quit = True
                break
            if key in (ord('m'), ord('M')):
                if audio: audio.toggle()
                continue
            if self.small or was_small or transition:
                continue
            if key in (ord('r'), ord('R')):
                self.game.restart()
                self.paused = False
                transition = True
                if audio:
                    audio.stop(); audio.play('switch')
            elif key in (ord('p'), ord('P')) and self.game.state in ('ready', 'playing'):
                self.paused = not self.paused
                transition = True
                if audio:
                    audio.stop(); audio.play('switch')
            elif not self.paused:
                if key in (curses.KEY_LEFT, ord('a'), ord('A')):
                    self.game.move(-1)
                elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
                    self.game.move(1)
                elif key == ord(' '):
                    transition = self.game.start_or_fire() == 'start'
        advanced = 0
        if not (self.quit or self.small or self.paused or was_frozen or transition):
            if self.game.state == 'playing':
                self.game.advance(elapsed)
                advanced = min(elapsed, MAX_ELAPSED)
        events = self.game.take_events()
        if audio:
            for cue in events:
                audio.play(cue)
            audio.tick()
        self.discard_input = self.small != was_small or transition
        return dict(self.game.snapshot(), paused=self.paused, small=self.small,
                    quit=self.quit, advanced=advanced, events=events,
                    sound=audio.status if audio else 'key sound off')


class Renderer(PaperRenderer):
    def draw(self, controller, sound_status='key sound off'):
        self.screen.erase()
        rows, columns = self.screen.getmaxyx()
        if controller.small:
            self.text(1, 2, 'Paper Invaders', self.accent)
            self.text(3, 2, 'Resize terminal to at least 80 x 30.', self.ink)
            self.text(4, 2, f'Current: {columns} x {rows}. Game frozen.', self.muted)
            self.text(6, 2, sound_status, self.muted)
            self.text(7, 2, 'M mute  Q quit  Ctrl-C exit', self.ink)
        else:
            ox, oy = (columns - MIN_COLUMNS) // 2, (rows - MIN_ROWS) // 2
            left, top = ox + 9, oy + 4
            game = controller.game
            self.text(oy + 1, ox + 24, '. socratink / paper invaders', self.ink | curses.A_BOLD)
            self.text(oy + 2, ox + 32, 'hold the line.', self.muted)
            self.text(oy + 3, left, f'SCORE {game.score:03}   LIVES {game.lives}   WAVE {game.wave + 1}/3  {NAMES[game.wave]}', self.ink)
            self.text(oy + 3, left + WIDTH + 2 - len(sound_status), sound_status, self.muted)
            self.box(top, left, HEIGHT + 2, WIDTH + 2, 'PLAY / PAPER')
            for enemy in game.enemies:
                self.text(top + 1 + enemy.y, left + enemy.x, '[W]', self.ink | curses.A_BOLD)
            self.text(top + 1 + SHIP_Y, left + game.ship, '/^\\', self.accent)
            if game.player_shot:
                shot = game.player_shot
                self.text(top + 1 + int(shot.y), left + 1 + shot.x, '^', self.accent)
            for shot in game.enemy_shots:
                self.text(top + 1 + int(shot.y), left + 1 + shot.x, 'v', self.ink | curses.A_BOLD)
            message = {'ready': 'READY  Space to begin', 'playing': 'Clear every enemy to advance.',
                       'won': 'YOU WIN  All three waves cleared. R restarts.',
                       'lost': 'GAME OVER  R to restart'}[game.state]
            if controller.paused:
                message = 'PAUSED  P to resume'
            self.text(oy + 26, left, message, self.accent)
            self.text(oy + 27, left, 'Arrows / A D move   Space start / fire   P pause', self.ink)
            self.text(oy + 28, left, 'R restart   M mute   Q quit   Ctrl-C exit', self.muted)
        try:
            self.screen.refresh()
        except curses.error:
            pass


def run(screen, seed=None, no_color=False, no_sound=False):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer = Renderer(screen, no_color)
    controller = Controller(time.monotonic(), seed)
    # Observation only. No state, commands or clock overrides are read here.
    trace_path = os.environ.get('TINK_INVADERS_TRACE')
    trace = open(trace_path, 'w', encoding='utf-8') if trace_path else None
    try:
        with KeyboardAudio(enabled=not no_sound) as audio:
            _run_loop(screen, renderer, controller, audio, trace, os.environ.get("TINK_INVADERS_CAPTURE") == "1")
            return audio.warning
    finally:
        if trace:
            trace.close()


def _run_loop(screen, renderer, controller, audio, trace=None, capture=False):
    captured = set()
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
            label = (rows, columns, controller.small, controller.paused, controller.game.state)
            if capture and label not in captured:
                # Read the real curses backing screen after draw, without changing it.
                state['screen'] = [[screen.inch(y, x) for x in range(columns)] for y in range(rows)]
                state['screen_masks'] = dict(char=curses.A_CHARTEXT, color=curses.A_COLOR,
                                             bold=curses.A_BOLD, dim=curses.A_DIM)
                captured.add(label)
            trace.write(json.dumps(state) + '\n')
            trace.flush()
        time.sleep(max(0, FRAME_TIME - (time.monotonic() - started)))
