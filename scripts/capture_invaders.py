#!/usr/bin/env python3
"""Retain actual curses cells for ready/play/pause/win/loss, reached by legal keys."""
import argparse
import html
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_invaders_terminal import Terminal, require
from scripts.replay_invaders import choose_input


class ObservedGame:
    """Read-only snapshot adapter for the same replay controller; never writes to the game."""
    def __init__(self, state):
        self.state, self.ship, self.direction = state['state'], state['ship'], state['direction']
        self.enemies = [SimpleNamespace(**e) for e in state['enemies']]
        self.enemy_shots = [SimpleNamespace(**s) for s in state['enemy_shots']]
        self.player_shot = state['player_shot']

    def bottom_shooters(self):
        return [e for e in self.enemies if not any(o.column == e.column and o.y > e.y for o in self.enemies)]


def loss_input(state):
    if state['state'] == 'ready':
        return 'space'
    if state['enemy_shots']:
        target = max(state['enemy_shots'], key=lambda s: s['y'])['x']
    else:
        return None
    return 'right' if state['ship'] < target else 'left' if state['ship'] > target else None


def drive(terminal, target):
    deadline = time.monotonic() + 100
    last_count = 0
    while time.monotonic() < deadline:
        terminal.pump()
        states = terminal.states()
        if len(states) == last_count:
            continue
        last_count = len(states)
        state = states[-1]
        if state['state'] == target:
            return state
        require(state['state'] not in ('won', 'lost'), f'Unexpected end while seeking {target}: {state["state"]}')
        command = choose_input(ObservedGame(state)) if target == 'won' else loss_input(state)
        key = {'left': b'a', 'right': b'd', 'space': b' '}.get(command)
        if key:
            os.write(terminal.master, key)
    raise RuntimeError(f'Timed out seeking {target}')


def screen_html(state, color):
    masks = state['screen_masks']
    lines = []
    for row in state['screen']:
        spans = []
        for cell in row:
            char = chr(cell & masks['char'])
            pair = (cell & masks['color']) >> 8
            classes = [f'p{pair}' if color else 'mono']
            if cell & masks['bold']: classes.append('bold')
            if cell & masks['dim']: classes.append('dim')
            spans.append(f'<span class="{" ".join(classes)}">{html.escape(char)}</span>')
        lines.append(''.join(spans))
    return ('<pre class="color">' if color else '<pre>') + '\n'.join(lines) + '</pre>'


def write_sheet(output, color):
    states = json.loads((output / 'cells.json').read_text())
    sections = []
    for state in states:
        label = 'pause' if state['paused'] else state['state']
        sections.append(f'<section><h2>{label}</h2>{screen_html(state, color)}</section>')
    (output / 'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Paper Invaders actual terminal cells</title>
<style>body{background:#ddd;color:#222;font:16px system-ui;margin:24px}section{margin-bottom:28px}pre{display:inline-block;font:14px/18px Menlo,monospace;padding:0;margin:0;background:#151719;color:#eee}pre.color{background:#ffffd7}.p1{color:#121212;background:#ffffd7}.p2{color:#00875f;background:#ffffd7}.p3{color:#585858;background:#ffffd7}.p4{color:#8a8a8a;background:#ffffd7}.bold{font-weight:bold}.dim{opacity:.7}h2{margin:12px 0}</style>
<h1>Observed curses screen cells</h1><p>Captured from the running terminal game after drawing. The HTML preserves observed characters and attributes. It uses the standard xterm paper palette; monochrome assumes a dark terminal. Font metrics and terminal-specific palette overrides are not captured.</p>''' + '\n'.join(sections), encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--columns', type=int, default=80)
    parser.add_argument('--rows', type=int, default=30)
    parser.add_argument('--color', action='store_true')
    args = parser.parse_args(argv)
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    retained = []
    with tempfile.TemporaryDirectory(prefix='invaders-capture-') as directory:
        terminal = Terminal(directory, args.columns, args.rows, args.color, capture=True)
        try:
            terminal.wait(lambda s: s['state'] == 'ready', 'Ready')
            terminal.send(b' ', lambda s: s['state'] == 'playing', 'Play')
            terminal.send(b'P', lambda s: s['paused'], 'Pause')
            terminal.send(b'p', lambda s: not s['paused'], 'Resume')
            won = drive(terminal, 'won')
            require(won['score'] == 340 and won['lives'] > 0 and not won['enemies'], 'Incomplete win')
            terminal.notes.append(f'Legal real-loop win: score={won["score"]}, lives={won["lives"]}')
            terminal.send(b'R', lambda s: s['state'] == 'ready', 'Restart to observe loss')
            lost = drive(terminal, 'lost')
            require(lost['lives'] == 0, 'Incomplete loss')
            terminal.notes.append('Legal real-loop loss: steered into normal enemy projectiles until zero lives')
            terminal.finish(b'q')
        except BaseException as error:
            terminal.notes.append(f'FAIL: {type(error).__name__}: {error}')
            raise
        finally:
            retained = [s for s in terminal.states() if 'screen' in s]
            (output / 'cells.json').write_text(json.dumps(retained) + '\n')
            (output / 'terminal.txt').write_text(terminal.transcript())
            (output / 'terminal.ansi').write_bytes(terminal.raw)
            terminal.close()
            write_sheet(output, args.color)
    labels = {'pause' if s['paused'] else s['state'] for s in retained}
    require({'ready', 'playing', 'pause', 'won', 'lost'} <= labels, f'Missing captures: {labels}')
    print(f'PASS: five actual states at {args.columns}x{args.rows}, color={args.color}: {output / "index.html"}')


if __name__ == '__main__':
    main()
