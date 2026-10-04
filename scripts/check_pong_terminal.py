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
OUTPUT = ROOT / 'runs/pong/04-test/output/terminal-transcript.txt'
GAME_KEYS = ('state', 'paused', 'player_score', 'computer_score', 'serves', 'player', 'computer', 'x', 'y', 'vx', 'vy', 'accumulator')


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
        env = dict(os.environ, TERM='xterm-256color', TINK_PONG_TRACE=str(self.trace))
        self.proc = subprocess.Popen([sys.executable, '-B', '-m', 'tink_pong', '--no-color'],
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
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='pong-pty-') as directory:
            terminal = Terminal(directory)
            try:
                t = terminal
                initial = t.wait(lambda s: not s['small'], '80x30 waiting')
                t.expect(b'paper pong')
                moved = t.send(b'\x1bOA', lambda s: s['player'] == 8.5, 'Up arrow')
                t.send(b'S', lambda s: s['player'] == 10, 'Uppercase S')
                t.send(b'\x1bOB', lambda s: s['player'] == 11.5, 'Down arrow')
                t.send(b'w', lambda s: s['player'] == 10, 'Lowercase W')
                served = t.send(b' ', lambda s: s['state'] == 'playing', 'Serve')
                assert served['x'] == 30 and served['y'] == 10
                t.wait(lambda s:s['x'] > 30, 'Ball moves', len(t.states()))
                # Space must not freeze a rally. Accept either direction after a
                # bounce, a scored point, or a new serve if the point ended play.
                for frame in range(20):
                    before = t.states()[-1]
                    after = t.send(b' ', lambda s: True, f'Rally Space {frame + 1}')
                    motion = ('x', 'y', 'state', 'player_score', 'computer_score')
                    assert any(after[k] != before[k] for k in motion), f'No-op Space froze rally: {before} -> {after}'
                    assert not after['paused']
                # Later control checks need an active rally even if this sample
                # included a point. Start a fresh match rather than assume its state.
                t.send(b'R', lambda s: s['state'] == 'waiting' and s['serves'] == 0, 'Reset after Space samples')
                t.send(b' ', lambda s: s['state'] == 'playing', 'Serve for pause checks')
                paused = t.send(b'P', lambda s: s['paused'], 'Pause')
                t.frozen(paused, 'Pause freezes both paddles and ball')
                t.send(b'wS ', lambda s:s['paused'], 'Paused movement and serve ignored')
                t.frozen(paused, 'Paused inputs keep state')
                start = len(t.states()); t.resize(40,12)
                small = t.wait(lambda s: s['small'], 'Shrink while paused', start)
                assert physics(small) == physics(paused)
                t.expect(b'Resize terminal')
                t.send(b'rwp s', lambda s: s['small'], 'Ignore small-window controls')
                t.frozen(small, 'Undersize freezes state')
                t.send(b'M', lambda s: 'muted' in s['sound'] or 'unavailable' in s['sound'], 'Mute while small')
                t.send(b'm', lambda s: 'on' in s['sound'] or 'unavailable' in s['sound'], 'Unmute while small')
                start = len(t.states()); t.resize(100,35)
                restored = t.wait(lambda s: not s['small'], 'Restore at 100x35', start)
                assert physics(restored) == physics(paused)
                t.frozen(restored, 'Restored pause stays frozen')
                resumed = t.send(b'p', lambda s: not s['paused'], 'Resume')
                assert resumed['x'] == paused['x'] and resumed['y'] == paused['y']
                start = len(t.states()); t.resize(40,12)
                small = t.wait(lambda s: s['small'], 'Shrink while playing', start)
                t.frozen(small, 'Playing resize freezes time')
                start = len(t.states()); t.resize(80,30)
                restored = t.wait(lambda s: not s['small'], 'Playing resize recovery', start)
                assert physics(restored) == physics(small)
                t.wait(lambda s: s['x'] != restored['x'], 'Movement resumes', len(t.states()))
                t.send(b'm',lambda s:'muted' in s['sound'] or 'unavailable' in s['sound'],'Mute before restart')
                restarted = t.send(b'R', lambda s: s['state']=='waiting' and s['serves']==0, 'Restart')
                assert physics(restarted) == physics(initial)
                assert 'muted' in restarted['sound'] or 'unavailable' in restarted['sound']
                t.frozen(restarted,'Waiting serve freezes physics')
                t.finish(b'q')
            finally:
                transcripts.append(terminal.transcript()); terminal.close()
        with tempfile.TemporaryDirectory(prefix='pong-pty-') as directory:
            terminal = Terminal(directory,40,12)
            try:
                t=terminal
                initial=t.wait(lambda s:s['small'], 'Starts undersized')
                t.frozen(initial, 'Initial undersize freezes state')
                start=len(t.states()); t.resize(80,30)
                restored=t.wait(lambda s:not s['small'], 'Initial resize recovery',start)
                assert physics(restored)==physics(initial)
                t.finish(b'\x03')
            finally:
                transcripts.append(terminal.transcript()); terminal.close()
    finally:
        OUTPUT.write_text('\n\n'.join(transcripts).rstrip()+'\n',encoding='utf-8')
    print('PASS: Pong real PTY arrows/W/S, serve, pause, restart, resize, mute, Q and SIGINT; modes restored; child groups gone.')
    print(f'Transcript: {OUTPUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
