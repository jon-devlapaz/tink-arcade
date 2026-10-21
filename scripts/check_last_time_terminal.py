#!/usr/bin/env python3
"""Exercise the real cabinet through a POSIX PTY, without injected time/state."""
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


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def physics(state):
    return {k: state[k] for k in ('player', 'direction', 'score', 'round', 'tick',
                                  'ghosts', 'sparks', 'state', 'accumulator')}


class Terminal:
    def __init__(self, directory, color=False, small=False):
        self.master, self.slave = pty.openpty()
        self.proc = None
        self.raw, self.notes = bytearray(), []
        self.trace = Path(directory) / 'trace.jsonl'
        self.before = termios.tcgetattr(self.slave)
        try:
            os.set_blocking(self.master, False)
            self.resize(40 if small else 80, 12 if small else 30)
            env = dict(os.environ, TERM='xterm-256color', TINK_LAST_TIME_TRACE=str(self.trace))
            env.pop('TYPESAFE_API_KEY', None)
            command = [sys.executable, '-B', '-m', 'tink_last_time', '--no-sound', '--seed', '7']
            if not color:
                command.append('--no-color')
            self.proc = subprocess.Popen(command, cwd=ROOT, env=env, stdin=self.slave,
                                         stdout=self.slave, stderr=self.slave,
                                         start_new_session=True, close_fds=True)
        except BaseException:
            os.close(self.master); os.close(self.slave)
            raise

    def resize(self, columns, rows):
        fcntl.ioctl(self.slave, termios.TIOCSWINSZ, struct.pack('HHHH', rows, columns, 0, 0))
        if self.proc:
            os.kill(self.proc.pid, signal.SIGWINCH)

    def states(self):
        if not self.trace.exists():
            return []
        return [json.loads(line) for line in self.trace.read_text().split('\n')[:-1] if line]

    def pump(self):
        if select.select([self.master], [], [], .01)[0]:
            try:
                self.raw.extend(os.read(self.master, 65536))
            except OSError:
                pass

    def wait(self, predicate, label, start=0, timeout=4):
        deadline = time.monotonic() + timeout
        checked = start
        while time.monotonic() < deadline:
            self.pump()
            states = self.states()
            for state in states[checked:]:
                if predicate(state):
                    self.notes.append(f'{label}: {json.dumps(state, sort_keys=True)}')
                    return state
            checked = len(states)
            if self.proc.poll() is not None:
                raise AssertionError(f'Exited before {label}: {self.proc.returncode}')
        raise AssertionError(f'Timed out: {label}; latest={self.states()[-2:]}')

    def send(self, keys, predicate, label):
        start = len(self.states())
        os.write(self.master, keys)
        return self.wait(predicate, label, start)

    def frozen(self, state, label):
        start = len(self.states())
        self.wait(lambda s: len(self.states()) >= start + 12, label, start)
        require(all(physics(s) == physics(state) for s in self.states()[start:]), label)

    def finish(self, interrupt=False):
        if interrupt:
            os.killpg(self.proc.pid, signal.SIGINT)
        else:
            os.write(self.master, b'q')
        deadline = time.monotonic() + 4
        while self.proc.poll() is None and time.monotonic() < deadline:
            self.pump()
        require(self.proc.poll() == 0, f'Exit failed: {self.proc.poll()}')
        self.proc.wait(); self.pump()
        before, after = self.before.copy(), termios.tcgetattr(self.slave)
        before[3] &= ~getattr(termios, 'PENDIN', 0)
        after[3] &= ~getattr(termios, 'PENDIN', 0)
        require(before == after, 'Terminal modes leaked')
        try:
            os.killpg(self.proc.pid, 0)
        except ProcessLookupError:
            pass
        else:
            raise AssertionError('Process group remains after exit')
        require(b'Traceback' not in self.raw, 'CLI traceback')
        self.notes.append(f'{"SIGINT" if interrupt else "Q"}: exit 0, modes restored, group gone')

    def close(self):
        try:
            if self.proc and self.proc.poll() is None:
                os.killpg(self.proc.pid, signal.SIGKILL)
            if self.proc:
                self.proc.wait(timeout=3)
        finally:
            os.close(self.master); os.close(self.slave)

    def transcript(self):
        raw = self.raw.decode('utf-8', errors='replace')
        text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]|\x1b[()][A-Z0-9]|\x1b[=>]', '', raw)
        text = ''.join(c for c in text if c in '\n\t' or ord(c) >= 32)
        return '\n'.join(self.notes) + '\n\nSanitized terminal output:\n' + text


def exercise(t, color):
    initial = t.wait(lambda s: s['state'] == 'playing' and not s['small'], 'Immediate play at 80x30')
    require(b'paper last time' in t.raw and b'PLAY / PAPER' in t.raw, 'Missing presentation')
    for keys, direction in ((b'\x1bOC', [1, 0]), (b'\x1bOB', [0, 1]),
                            (b'\x1bOD', [-1, 0]), (b'\x1bOA', [0, -1])):
        moved = t.send(keys, lambda s: s['direction'] == direction, f'Arrow {direction}')
        t.wait(lambda s: s['player'] != moved['player'], 'Arrow advances light', len(t.states()))
    paused = t.send(b'P', lambda s: s['paused'], 'Pause')
    t.frozen(paused, 'Pause freezes all game clocks')
    muted = t.send(b'M', lambda s: s['paused'] and s['sound'] == 'key sound off', 'No-sound stays disabled')
    require(physics(muted) == physics(paused), 'Mute changed rules')
    start = len(t.states()); t.resize(40, 12)
    small = t.wait(lambda s: s['small'], 'Shrink while paused', start)
    t.send(b'rp' * 10 + b'\x1bOC', lambda s: s['small'], 'Ignore undersized gameplay')
    t.frozen(small, 'Undersized pause freezes clocks')
    start = len(t.states()); t.resize(100, 35)
    restored = t.wait(lambda s: not s['small'], 'Recover paused at 100x35', start)
    require(restored['paused'] and physics(restored) == physics(paused), 'Recovery changed paused state')
    resumed = t.send(b'p', lambda s: not s['paused'], 'Resume without catch-up')
    require(physics(resumed) == physics(paused), 'Resume caught up')
    start = len(t.states()); t.resize(40, 12)
    small = t.wait(lambda s: s['small'], 'Shrink while playing', start)
    t.frozen(small, 'Undersized play freezes clocks')
    start = len(t.states()); t.resize(80, 30)
    recovered = t.wait(lambda s: not s['small'], 'Recover playing', start)
    require(physics(recovered) == physics(small), 'Recovery caught up')
    t.wait(lambda s: s['tick'] > recovered['tick'], 'Time resumes', len(t.states()))
    restarted = t.send(b'R', lambda s: s['tick'] == 0 and s['direction'] == [0, 0], 'Restart')
    for key in ('player', 'sparks', 'score', 'round', 'ghosts'):
        require(restarted[key] == initial[key], f'Restart failed: {key}')
    require((b'48;5;230' in t.raw) == color, 'Color mode mismatch')
    if not color:
        t.send(b'\x1bOC', lambda s: s['direction'] == [1, 0], 'Begin real timed path')
        boundary = t.wait(lambda s: s['round'] == 2, 'Real 15-second boundary adds first ghost',
                          len(t.states()), timeout=18)
        require(len(boundary['ghosts']) == 1 and boundary['state'] == 'playing', 'Unsafe boundary')
        lost = t.wait(lambda s: s['state'] == 'lost', 'Past path reaches stationary endpoint', len(t.states()))
        t.frozen(lost, 'Death freezes rules with no second life')
        t.send(b'r', lambda s: s['round'] == 1 and not s['ghosts'], 'Restart after real death')
    t.finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'runs/new-cabinet/04-test/output/terminal-transcript.txt')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    transcripts = []
    try:
        for color, small in ((False, False), (True, False), (False, True)):
            with tempfile.TemporaryDirectory(prefix='last-time-pty-') as directory:
                terminal = Terminal(directory, color, small)
                try:
                    if small:
                        initial = terminal.wait(lambda s: s['small'], 'Starts undersized')
                        terminal.send(b'rp\x1bOC', lambda s: s['small'], 'Ignore initially frozen keys')
                        terminal.frozen(initial, 'Initial undersize freezes time')
                        start = len(terminal.states()); terminal.resize(80, 30)
                        recovered = terminal.wait(lambda s: not s['small'], 'Initial recovery', start)
                        require(physics(initial) == physics(recovered), 'Initial recovery changed game')
                        terminal.finish(interrupt=True)
                    else:
                        exercise(terminal, color)
                except BaseException as error:
                    terminal.notes.append(f'FAIL: {type(error).__name__}: {error}')
                    raise
                finally:
                    transcripts.append(terminal.transcript())
                    terminal.close()
    finally:
        args.output.write_text('\n\n'.join(transcripts) + '\n', encoding='utf-8')
    print('PASS Last Time PTY: arrows, pause, resize/recovery, restart, no-sound, color/mono, Q/SIGINT and cleanup.')
    print(f'Transcript: {args.output}')


if __name__ == '__main__':
    main()
