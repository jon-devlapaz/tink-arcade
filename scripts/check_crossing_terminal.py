#!/usr/bin/env python3
"""Drive the actual curses process through a POSIX PTY; keep readable evidence."""
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
OUTPUT = ROOT / 'runs/crossing/04-test/output/terminal-transcript.txt'
GAME_KEYS = ('state', 'paused', 'score', 'lives', 'level', 'row', 'col', 'bays', 'deaths', 'accumulator', 'counters')


def physics(state):
    return {key: state[key] for key in GAME_KEYS}


class Terminal:
    def __init__(self, directory, cols=80, rows=30):
        self.master, self.slave = pty.openpty()
        os.set_blocking(self.master, False)
        self.before = termios.tcgetattr(self.slave)
        self.trace = Path(directory) / 'trace.jsonl'
        self.raw = bytearray()
        self.notes = []
        self.proc = None
        self.resize(cols, rows)
        env = dict(os.environ, TERM='xterm-256color', TINK_CROSSING_TRACE=str(self.trace))
        self.proc = subprocess.Popen([sys.executable, '-B', '-m', 'tink_crossing', '--no-color'],
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


def main():
    transcripts = []
    skipped = []
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='crossing-pty-') as directory:
            terminal = Terminal(directory)
            try:
                t = terminal
                initial = t.wait(lambda s: not s['small'], '80x30 new game')
                t.expect(b'paper crossing')
                assert (initial['row'], initial['col'], initial['lives']) == (12, 20, 3)
                # Without an audio player the sound status is 'unavailable' and M cannot
                # change it. Say so instead of letting the mute steps pass vacuously.
                audio = 'unavailable' not in initial['sound']
                if not audio:
                    skipped.append('mute/unmute: no audio player; only checked that M keeps the game running')
                    t.notes.append('SKIP ' + skipped[-1])
                muted = (lambda s: 'muted' in s['sound']) if audio else (lambda s: 'unavailable' in s['sound'])
                unmuted = (lambda s: 'on' in s['sound']) if audio else (lambda s: 'unavailable' in s['sound'])
                t.wait(lambda s: s['counters'] != initial['counters'], 'Lanes move', len(t.states()))
                t.send(b'\x1bOD', lambda s: s['col'] == 19, 'Left arrow')
                t.send(b'D', lambda s: s['col'] == 20, 'Uppercase D')
                t.send(b'\x1bOC', lambda s: s['col'] == 21, 'Right arrow')
                t.send(b'a', lambda s: s['col'] == 20, 'Lowercase A')
                t.send(b'S', lambda s: s['row'] == 12, 'Down clamps on start row')
                # Hop up until something happens: a new row, or a life lost to traffic.
                hopped = t.send(b'w', lambda s: s['row'] == 11 or s['deaths'] == 1, 'Up hop')
                assert hopped['score'] == 10 or hopped['lives'] == 2, hopped
                paused = t.send(b'P', lambda s: s['paused'], 'Pause')
                t.frozen(paused, 'Pause freezes lanes and marker')
                t.send(b'wasd', lambda s: s['paused'], 'Paused hops ignored')
                t.frozen(paused, 'Paused inputs keep state')
                start = len(t.states()); t.resize(40, 12)
                small = t.wait(lambda s: s['small'], 'Shrink while paused', start)
                assert physics(small) == physics(paused)
                t.expect(b'Resize terminal')
                t.send(b'rwp s', lambda s: s['small'], 'Ignore small-window controls')
                t.frozen(small, 'Undersize freezes state')
                t.send(b'M', lambda s: muted(s) and s['small'], 'Mute while small')
                t.send(b'm', lambda s: unmuted(s) and s['small'], 'Unmute while small')
                start = len(t.states()); t.resize(100, 35)
                restored = t.wait(lambda s: not s['small'], 'Restore at 100x35', start)
                assert physics(restored) == physics(paused)
                t.frozen(restored, 'Restored pause stays frozen')
                resumed = t.send(b'p', lambda s: not s['paused'], 'Resume')
                assert physics(resumed)['counters'] == paused['counters']
                t.wait(lambda s: s['counters'] != paused['counters'], 'Lanes resume', len(t.states()))
                start = len(t.states()); t.resize(40, 12)
                small = t.wait(lambda s: s['small'], 'Shrink while playing', start)
                t.frozen(small, 'Playing resize freezes time')
                start = len(t.states()); t.resize(80, 30)
                restored = t.wait(lambda s: not s['small'], 'Playing resize recovery', start)
                assert physics(restored) == physics(small)
                t.wait(lambda s: s['counters'] != restored['counters'], 'Lanes resume after resize', len(t.states()))
                t.send(b'm', muted, 'Mute before restart')
                restarted = t.send(b'R', lambda s: s['score'] == 0 and s['lives'] == 3 and s['row'] == 12
                                   and s['deaths'] == 0, 'Restart')
                assert muted(restarted), 'Restart must keep mute'
                t.finish(b'q')
            finally:
                transcripts.append(terminal.transcript()); terminal.close()
        with tempfile.TemporaryDirectory(prefix='crossing-pty-') as directory:
            terminal = Terminal(directory, 40, 12)
            try:
                t = terminal
                initial = t.wait(lambda s: s['small'], 'Starts undersized')
                t.frozen(initial, 'Initial undersize freezes state')
                start = len(t.states()); t.resize(80, 30)
                restored = t.wait(lambda s: not s['small'], 'Initial resize recovery', start)
                assert physics(restored) == physics(initial)
                t.finish(b'\x03')
            finally:
                transcripts.append(terminal.transcript()); terminal.close()
    finally:
        OUTPUT.write_text('\n\n'.join(transcripts).rstrip() + '\n', encoding='utf-8')
    for item in skipped:
        print(f'SKIP {item}')
    mute = '' if skipped else 'mute, '
    print(f'PASS: Crossing real PTY arrows/WASD, hop, pause, restart, resize, {mute}Q and SIGINT; '
          'modes restored; child groups gone.')
    print(f'Transcript: {OUTPUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
