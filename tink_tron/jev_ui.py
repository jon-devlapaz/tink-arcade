"""Curses loop for Tron vs Jev: the shared renderer plus the pilot's requests, holds and errors."""

import curses
import json
import os
import time

from arcade_common.audio import KeyboardAudio
from neon_tetris.jev import Worker
from .engine import Game
from .jev_match import JevPilot, TronClient
from .ui import FRAME_TIME, MIN_COLUMNS, MIN_ROWS, Renderer, handle_key


def hold_banner(pilot, game):
    """(title, hint) while play is held, else ('', '')."""
    if pilot.error:
        return 'JEV ERROR', pilot.error[:34]
    if pilot.holds(game):
        return 'WAITING FOR JEV', 'Choosing an opening route.'
    return '', ''


def handle_jev_key(game, pilot, key, audio):
    if key in (ord('q'), ord('Q'), 3):
        return False
    if key in (10, 13, curses.KEY_ENTER):
        if pilot.error:
            pilot.retry()
    elif key in (ord('r'), ord('R')):
        game.restart()
        pilot.reset()
        audio.stop()
        audio.play('switch')
    elif key in (ord('m'), ord('M'), ord('p'), ord('P'), ord(' ')) or not pilot.holds(game):
        return handle_key(game, key, audio)
    return True


def run_jev(screen, seed, no_color, no_sound, client):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    curses.set_escdelay(25)
    screen.keypad(True)
    screen.nodelay(True)
    renderer = Renderer(screen, no_color)
    pilot = JevPilot(Worker(TronClient(client)))
    game = Game(seed, opponent=pilot)
    trace_path = os.environ.get('TINK_TRON_TRACE')
    trace = open(trace_path, 'w', encoding='utf-8') if trace_path else None
    try:
        with KeyboardAudio(enabled=not no_sound) as audio:
            _run_loop(screen, renderer, game, pilot, audio, trace)
            busy = pilot.worker.busy
            result = ('match won' if game.match_winner == 0 else 'match lost' if game.match_winner == 1
                      else f'unfinished, {game.scores[0]}-{game.scores[1]}')
            summary = f'Tron vs Jev: {result}. {pilot.cost.display(busy)}'
            if busy:
                summary += '; the final in-flight request may still be charged.'
            return audio.warning, summary
    finally:
        if trace:
            trace.close()


def _run_loop(screen, renderer, game, pilot, audio, trace=None):
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
        pilot.collect(game)
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
                if key in map(ord, 'pPrR \n\r'):
                    transition = True
                handle_jev_key(game, pilot, key, audio)
        pilot.collect(game)
        cue = None
        if not too_small and not was_small and not transition and not pilot.holds(game):
            cue = game.update(dt)
            if cue:
                audio.play(cue)
        if not too_small and not game.paused:
            pilot.maybe_request(game)
        audio.tick()
        title, hint = hold_banner(pilot, game)
        renderer.draw(game, too_small, audio.status,
                      (pilot.status(game), pilot.cost.display(pilot.worker.busy), title, hint))
        if trace:
            trace.write(json.dumps(dict(heads=game.heads, dirs=game.dirs, scores=game.scores, round=game.round,
                                        paused=game.paused, over=game.round_over, winner=game.winner,
                                        match=game.match_winner, elapsed=game.elapsed, small=too_small,
                                        sound=audio.status, cue=cue, busy=pilot.worker.busy, plan=len(pilot.plan),
                                        hold=title, error=pilot.error, calls=pilot.cost.responses,
                                        cost=pilot.cost.display(pilot.worker.busy))) + '\n')
            trace.flush()
        was_small = too_small
        time.sleep(max(0.0, FRAME_TIME - (time.monotonic() - frame_start)))
