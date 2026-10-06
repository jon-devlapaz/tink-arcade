#!/usr/bin/env python3
"""Drive the actual curses process through a POSIX PTY; keep readable evidence."""
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
OUTPUT = ROOT / 'runs/tron/04-test/output/terminal-transcript.txt'
GAME_KEYS = ('heads', 'dirs', 'scores', 'round', 'paused', 'over', 'winner', 'match', 'elapsed')


def physics(state):
    return {key: state[key] for key in GAME_KEYS}


class Terminal:
    def __init__(self, directory, cols=80, rows=30, args=('--level', 'easy'), command=None, env_extra=None):
        self.master, self.slave = pty.openpty()
        os.set_blocking(self.master, False)
        self.before = termios.tcgetattr(self.slave)
        self.trace = Path(directory) / 'trace.jsonl'
        self.raw = bytearray()
        self.notes = []
        self.proc = None
        self.resize(cols, rows)
        env = dict(os.environ, TERM='xterm-256color', TINK_TRON_TRACE=str(self.trace), **(env_extra or {}))
        self.proc = subprocess.Popen(command or [sys.executable, '-B', '-m', 'tink_tron', '--seed', '1', '--no-color', *args],
                                     cwd=ROOT, env=env, stdin=self.slave, stdout=self.slave,
                                     stderr=self.slave, start_new_session=True, close_fds=True)

    def resize(self, cols, rows):
        fcntl.ioctl(self.slave, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
        if self.proc:
            os.kill(self.proc.pid, signal.SIGWINCH)

    def states(self):
        if not self.trace.exists():
            return []
        lines = self.trace.read_text().split('\n')[:-1]
        return [json.loads(line) for line in lines if line]

    def pump(self):
        if select.select([self.master], [], [], .02)[0]:
            try:
                self.raw.extend(os.read(self.master, 65536))
            except OSError:
                pass

    def expect(self, value):
        deadline = time.monotonic() + 4
        while value not in self.raw and time.monotonic() < deadline:
            self.pump()
        assert value in self.raw, f"Missing terminal text: {value!r}"

    def wait(self, predicate, label, start=0):
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            self.pump()
            states = self.states()
            for state in states[start:]:
                if predicate(state):
                    self.notes.append(f'{label}: {json.dumps(state, sort_keys=True)}')
                    return state
            if self.proc.poll() is not None:
                raise AssertionError(f'Process exited before {label}: {self.proc.returncode}')
        raise AssertionError(f'Timed out: {label}; last states={self.states()[-2:]}')

    def send(self, data, predicate, label):
        start = len(self.states())
        os.write(self.master, data)
        return self.wait(predicate, label, start)

    def frozen(self, state, label):
        start = len(self.states())
        self.wait(lambda s: len(self.states()) >= start + 20, label, start)
        observed = self.states()[start:]
        assert all(physics(s) == physics(state) for s in observed), label
        self.notes.append(f'{label}: {len(observed)} unchanged frames')

    def finish(self, key):
        if key == b'\x03':
            # Without a controlling terminal, send the same signal Ctrl-C produces.
            # Keeping the slave unowned lets macOS inspect modes after child exit.
            os.killpg(self.proc.pid, signal.SIGINT)
        else:
            os.write(self.master, key)
        deadline = time.monotonic() + 4
        while self.proc.poll() is None and time.monotonic() < deadline:
            self.pump()
        assert self.proc.poll() == 0, f'Exit failed: {self.proc.poll()}'
        self.proc.wait()
        self.pump()
        after = termios.tcgetattr(self.slave)
        before = self.before.copy()
        # macOS sets the transient PENDIN (retype pending input) bit on restoration.
        # Compare every persistent mode, speed, and control character.
        after[3] &= ~getattr(termios, 'PENDIN', 0)
        before[3] &= ~getattr(termios, 'PENDIN', 0)
        assert after == before, f'Terminal settings leaked: {before!r} -> {after!r}'
        try:
            os.killpg(self.proc.pid, 0)
        except ProcessLookupError:
            pass
        else:
            raise AssertionError('Process group remains after exit')
        assert b'Traceback' not in self.raw
        self.notes.append(f'Exit {key!r}: code 0, original terminal settings restored, process group gone')

    def close(self):
        if self.proc and self.proc.poll() is None:
            os.killpg(self.proc.pid, signal.SIGKILL)
        os.close(self.master)
        os.close(self.slave)
        if self.proc:
            self.proc.wait(timeout=3)

    def transcript(self):
        text = self.raw.decode('utf-8', errors='replace')
        text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07]*(?:\x07)|\x1b[()][A-Z0-9]|\x1b[=>]', '', text)
        text = ''.join(c for c in text if c in '\n\t' or ord(c) >= 32)
        return '\n'.join(self.notes) + '\n\nSanitized terminal output:\n' + text + '\n'


START = [[6, 10], [31, 10]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT,
                        help='transcript path (relative to the current directory; default: %(default)s)')
    output = parser.parse_args().output.resolve()
    transcripts = []
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='tron-pty-') as directory:
            terminal = Terminal(directory)
            try:
                t = terminal
                initial = t.wait(lambda s: not s['small'], '80x30 playing')
                assert initial['heads'] == START and initial['scores'] == [0, 0], initial
                t.expect(b'paper tron')
                t.expect(b'MACHINE (easy)')
                t.send(b'W', lambda s: s['dirs'][0] == [0, -1], 'Uppercase WASD turn')
                paused = t.send(b'P', lambda s: s['paused'], 'Pause')
                t.frozen(paused, 'Pause freezes both cycles and the clock')
                start = len(t.states()); t.resize(40, 12)
                small = t.wait(lambda s: s['small'], 'Shrink while paused', start)
                assert physics(small) == physics(paused)
                t.expect(b'Resize terminal')
                t.send(b'rwpa', lambda s: s['small'], 'Ignore small-window game controls')
                t.frozen(small, 'Undersize freezes both cycles and the clock')
                t.send(b'M', lambda s: 'muted' in s['sound'] or 'unavailable' in s['sound'], 'Mute while small')
                t.send(b'm', lambda s: 'on' in s['sound'] or 'unavailable' in s['sound'], 'Unmute while small')
                start = len(t.states()); t.resize(100, 35)
                restored = t.wait(lambda s: not s['small'], 'Restore at 100x35', start)
                assert physics(restored) == physics(paused)
                t.frozen(restored, 'Restored pause stays frozen')
                resumed = t.send(b'p', lambda s: not s['paused'], 'Resume')
                assert resumed['heads'] == paused['heads'] and resumed['elapsed'] == paused['elapsed']
                start = len(t.states()); t.resize(40, 12)
                small = t.wait(lambda s: s['small'], 'Shrink while playing', start)
                t.frozen(small, 'Playing resize freezes time')
                start = len(t.states()); t.resize(80, 30)
                restored = t.wait(lambda s: not s['small'], 'Playing resize recovery', start)
                assert physics(restored) == physics(small)
                t.wait(lambda s: s['heads'] != restored['heads'], 'Movement resumes', len(t.states()))
                restarted = t.send(b'R', lambda s: s['heads'] == START and s['elapsed'] == 0, 'Restart')
                assert restarted['scores'] == [0, 0] and restarted['round'] == 1
                # Climbing the wall loses a round to the machine; Space starts the next one.
                for lost in (1, 2):
                    t.send(b'w', lambda s: s['dirs'][0] == [0, -1], f'Lowercase WASD turn, round {lost}')
                    over = t.wait(lambda s: s['over'] and s['scores'][1] == lost, f'Wall loses round {lost}', len(t.states()))
                    assert over['winner'] == 1 and over['round'] == lost, over
                    t.expect(b'THE MACHINE TAKES THE ROUND'); t.frozen(over, f'Round {lost} result freezes the board')
                    started = t.send(b' ', lambda s: not s['over'], f'Space starts round {lost + 1}')
                    assert started['heads'] == START and started['round'] == lost + 1, started
                t.send(b'w', lambda s: s['dirs'][0] == [0, -1], 'Third losing turn')
                final = t.wait(lambda s: s['match'] == 1, 'Machine wins the match', len(t.states()))
                assert final['scores'] == [0, 3], final
                t.expect(b'THE MACHINE WINS THE MATCH')
                t.send(b' ', lambda s: s['over'] and s['match'] == 1, 'Space does not leave a finished match')
                t.send(b'R', lambda s: s['scores'] == [0, 0] and s['match'] is None and not s['over'], 'Restart a finished match')
                t.finish(b'q')
            finally:
                transcripts.append(terminal.transcript()); terminal.close()
        with tempfile.TemporaryDirectory(prefix='tron-pty-') as directory:
            terminal = Terminal(directory, 40, 12, ('--two-player', '--level', 'hard'))
            try:
                t = terminal
                initial = t.wait(lambda s: s['small'], 'Starts undersized')
                t.frozen(initial, 'Initial undersize freezes time')
                start = len(t.states()); t.resize(80, 30)
                restored = t.wait(lambda s: not s['small'], 'Initial resize recovery', start)
                assert physics(restored) == physics(initial)
                t.expect(b'PLAYER 2')
                t.send(b'w\x1bOB', lambda s: s['dirs'] == [[0, -1], [0, 1]], 'Two players: WASD steers player 1, arrows steer player 2')
                t.finish(b'\x03')
            finally:
                transcripts.append(terminal.transcript()); terminal.close()
    finally:
        output.write_text('\n\n'.join(transcripts).rstrip() + '\n', encoding='utf-8')
    print('PASS: Tron real PTY solo and two-player steering, pause, restart, resize, mute, round and match results, Q and SIGINT; modes restored; child groups gone.')
    print(f'Transcript: {output}')


if __name__ == '__main__':
    main()
