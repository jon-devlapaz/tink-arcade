#!/usr/bin/env python3
"""Check the actual game in a POSIX PTY. Output includes partial failures."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import pty
import re
import select
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import time

ROOT = Path(__file__).resolve().parents[1]
GAME_KEYS = ('wave', 'score', 'lives', 'state', 'ship', 'direction', 'enemies',
             'player_shot', 'enemy_shots', 'accumulator', 'move_cooldown',
             'fire_cooldown', 'march_timer', 'attack_timer')


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def physics(state):
    return {key: state[key] for key in GAME_KEYS}


class Terminal:
    def __init__(self, directory, cols=80, rows=30, color=False, capture=False):
        self.master, self.slave = pty.openpty()
        self.proc = None
        self.raw, self.notes = bytearray(), []
        self.trace = Path(directory) / 'trace.jsonl'
        self._states, self._offset, self._partial = [], 0, ''
        self.before = termios.tcgetattr(self.slave)
        try:
            os.set_blocking(self.master, False)
            self.resize(cols, rows)
            env = dict(os.environ, TERM='xterm-256color', TINK_INVADERS_TRACE=str(self.trace),
                       TINK_INVADERS_CAPTURE='1' if capture else '0')
            command = [sys.executable, '-B', '-m', 'tink_invaders', '--seed', '7']
            if not color: command.append('--no-color')
            self.proc = subprocess.Popen(command, cwd=ROOT, env=env, stdin=self.slave,
                stdout=self.slave, stderr=self.slave, start_new_session=True, close_fds=True)
        except BaseException:
            os.close(self.master); os.close(self.slave)
            raise

    def resize(self, cols, rows):
        fcntl.ioctl(self.slave, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
        if self.proc: os.kill(self.proc.pid, signal.SIGWINCH)

    def states(self):
        if self.trace.exists():
            with self.trace.open() as stream:
                stream.seek(self._offset)
                data = stream.read()
                self._offset = stream.tell()
            lines = (self._partial + data).split('\n')
            self._partial = lines.pop()
            self._states.extend(json.loads(line) for line in lines if line)
        return self._states

    def pump(self):
        if select.select([self.master], [], [], .01)[0]:
            try: self.raw.extend(os.read(self.master, 65536))
            except OSError: pass

    def wait(self, predicate, label, start=0):
        deadline = time.monotonic() + 4
        checked = start
        while time.monotonic() < deadline:
            self.pump()
            states = self.states()
            for state in states[checked:]:
                if predicate(state):
                    self.notes.append(f'{label}: {json.dumps({k:v for k,v in state.items() if not k.startswith("screen")}, sort_keys=True)}')
                    return state
            checked = len(states)
            if self.proc.poll() is not None:
                raise AssertionError(f'Process exited before {label}: {self.proc.returncode}')
        raise AssertionError(f'Timed out: {label}; last states={self.states()[-2:]}')

    def send(self, data, predicate, label):
        start = len(self.states())
        os.write(self.master, data)
        return self.wait(predicate, label, start)

    def frozen(self, state, label):
        start = len(self.states())
        self.wait(lambda s: len(self.states()) >= start + 12, label, start)
        observed = self.states()[start:]
        require(all(physics(s) == physics(state) and s['advanced'] == 0 for s in observed), label)
        self.notes.append(f'{label}: {len(observed)} unchanged frames, including every clock')

    def finish(self, key):
        if key == b'\x03':
            # An unowned slave lets macOS inspect restored modes. SIGINT stands in for Ctrl-C.
            os.killpg(self.proc.pid, signal.SIGINT)
        else:
            os.write(self.master, key)
        deadline = time.monotonic() + 4
        while self.proc.poll() is None and time.monotonic() < deadline: self.pump()
        require(self.proc.poll() == 0, f'Exit failed: {self.proc.poll()}')
        self.proc.wait(); self.pump()
        after, before = termios.tcgetattr(self.slave), self.before.copy()
        after[3] &= ~getattr(termios, 'PENDIN', 0)
        before[3] &= ~getattr(termios, 'PENDIN', 0)
        require(after == before, f'Terminal settings leaked: {before!r} -> {after!r}')
        try: os.killpg(self.proc.pid, 0)
        except ProcessLookupError: pass
        else: raise AssertionError('Process group remains after exit')
        require(b'Traceback' not in self.raw, 'Game printed a traceback')
        self.notes.append(f'Exit {key!r}: code 0, original terminal settings restored, process group gone')

    def close(self):
        try:
            if self.proc and self.proc.poll() is None: os.killpg(self.proc.pid, signal.SIGKILL)
            if self.proc: self.proc.wait(timeout=3)
        finally:
            os.close(self.master); os.close(self.slave)

    def transcript(self):
        text = self.raw.decode('utf-8', errors='replace')
        text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07]*(?:\x07)|\x1b[()][A-Z0-9]|\x1b[=>]', '', text)
        text = ''.join(c for c in text if c in '\n\t' or ord(c) >= 32)
        return '\n'.join(self.notes) + '\n\nSanitized terminal output:\n' + text + '\n'


def exercise(t, color):
    initial = t.wait(lambda s: s['state'] == 'ready' and not s['small'], '80x30 ready')
    require(b'paper invaders' in t.raw, 'Missing game title')
    t.send(b' ', lambda s: s['state'] == 'playing', 'Space starts')
    shot = t.send(b' ', lambda s: s['player_shot'] is not None, 'Space fires')
    t.send(b'D', lambda s: s['ship'] > initial['ship'], 'Move right')
    t.wait(lambda s: s['move_cooldown'] == 0, 'Movement cooldown expires', len(t.states()))
    t.send(b'\x1bOD', lambda s: s['ship'] == initial['ship'], 'Left arrow')
    started = len(t.states())
    os.write(t.master, b' ' * 100)
    t.wait(lambda s: s['attack_timer'] > .7 and s['enemies'][0]['x'] > initial['enemies'][0]['x'],
           'Repeated Space keeps clocks and enemies moving', started)
    require(any(s['player_shot'] and s['player_shot']['y'] < shot['player_shot']['y'] for s in t.states()), 'Shot never moved')
    paused = t.send(b'P', lambda s: s['paused'], 'Pause')
    t.frozen(paused, 'Pause freezes game')
    sound = t.send(b'M', lambda s: s['paused'] and s['sound'] != paused['sound'], 'Mute') if paused['sound'] == 'key sound on [M]' else None
    if sound:
        t.send(b'm', lambda s: s['sound'] == paused['sound'], 'Unmute')
    else:
        # No backend on Linux is a supported fallback; the unit suite covers toggle behavior.
        t.send(b'M', lambda s: s['paused'], 'Mute accepted with unavailable audio')
    start = len(t.states()); t.resize(40, 12)
    small = t.wait(lambda s: s['small'], 'Shrink while paused', start)
    require(physics(small) == physics(paused), 'Resize changed paused game')
    t.send(b'rp ad ' * 20, lambda s: s['small'], 'Ignore frozen input')
    t.frozen(small, 'Undersized pause freezes game')
    start = len(t.states()); t.resize(100, 35)
    restored = t.wait(lambda s: not s['small'], '100x35 recovery preserves pause', start)
    require(restored['paused'] and physics(restored) == physics(paused), 'Recovery changed pause')
    resumed = t.send(b'p', lambda s: not s['paused'], 'Resume without catch-up')
    require(physics(resumed) == physics(paused) and resumed['advanced'] == 0, 'Resume caught up')
    start = len(t.states()); t.resize(40, 12)
    small = t.wait(lambda s: s['small'], 'Shrink while playing', start)
    t.frozen(small, 'Undersized play freezes game')
    start = len(t.states()); t.resize(80, 30)
    restored = t.wait(lambda s: not s['small'], '80x30 recovery without catch-up', start)
    require(not restored['paused'] and physics(restored) == physics(small) and restored['advanced'] == 0, 'Resize caught up')
    t.wait(lambda s: physics(s) != physics(restored), 'Simulation resumes', len(t.states()))
    restarted = t.send(b'R', lambda s: s['state'] == 'ready', 'Restart')
    require(physics(restarted) == physics(initial), 'Restart did not reset rules and clocks')
    require((b'38;5;' in t.raw) == color, 'Color mode did not match request')
    t.finish(b'Q')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='explicit transcript destination')
    output = parser.parse_args(argv).output.resolve()
    transcripts = []
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        for color in (False, True):
            with tempfile.TemporaryDirectory(prefix='invaders-pty-') as directory:
                terminal = Terminal(directory, color=color)
                try:
                    exercise(terminal, color)
                except BaseException as error:
                    terminal.notes.append(f'FAIL: {type(error).__name__}: {error}')
                    raise
                finally:
                    transcripts.append(terminal.transcript()); terminal.close()
        with tempfile.TemporaryDirectory(prefix='invaders-pty-') as directory:
            terminal = Terminal(directory, 40, 12)
            try:
                initial = terminal.wait(lambda s: s['small'], 'Starts undersized')
                terminal.send(b' drp ', lambda s: s['small'], 'Ignore initial frozen inputs')
                terminal.frozen(initial, 'Initial undersize freezes clocks')
                start = len(terminal.states()); terminal.resize(80, 30)
                restored = terminal.wait(lambda s: not s['small'], 'Initial recovery', start)
                require(physics(initial) == physics(restored), 'Initial recovery changed game')
                terminal.send(b' ', lambda s: s['state'] == 'playing', 'Start before SIGINT')
                terminal.finish(b'\x03')
            except BaseException as error:
                terminal.notes.append(f'FAIL: {type(error).__name__}: {error}')
                raise
            finally:
                transcripts.append(terminal.transcript()); terminal.close()
    finally:
        output.write_text('\n\n'.join(transcripts).rstrip() + '\n', encoding='utf-8')
    print('PASS: actual PTY controls, shots, clocks, freezes, recovery, color/mono, Q/SIGINT and cleanup.')
    print(f'Transcript: {output}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
