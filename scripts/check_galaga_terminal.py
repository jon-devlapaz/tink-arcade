#!/usr/bin/env python3
"""Exercise the actual curses app in a PTY, without third-party terminal tools."""
import errno
import fcntl
import os
from pathlib import Path
import pty
import select
import signal
import struct
import sys
import termios
import time

ROOT = Path(__file__).resolve().parents[1]


def run_check(quit_key):
    pid, master = pty.fork()
    if pid == 0:
        os.chdir(ROOT)
        os.environ['TERM'] = 'xterm-256color'
        os.execv(sys.executable, [sys.executable, '-B', '-m', 'tink_galaga', '--seed', '17', '--no-color'])
    reaped = False
    output = bytearray()

    def resize(rows, cols):
        fcntl.ioctl(master, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
        os.kill(pid, signal.SIGWINCH)

    def collect(seconds=.25):
        deadline = time.monotonic() + seconds
        start = len(output)
        while time.monotonic() < deadline:
            if select.select([master], [], [], min(.05, max(0, deadline - time.monotonic())))[0]:
                try:
                    data = os.read(master, 65536)
                except OSError as error:
                    if error.errno == errno.EIO:
                        break
                    raise
                if not data:
                    break
                output.extend(data)
        return bytes(output[start:])

    def expect(fragment, seconds=3):
        deadline = time.monotonic() + seconds
        seen = bytearray()
        while time.monotonic() < deadline:
            seen.extend(collect(.1))
            if fragment in seen:
                return
        raise AssertionError(f'Missing terminal text {fragment!r}. Last output: {bytes(output[-1500:])!r}')

    try:
        resize(30, 80)
        expect(b'TINK ARCADE')
        # Move, fire, and wait for actual redraws. Model tests check the resulting rules.
        os.write(master, b'aa \x1bOD\x1bOC')
        assert collect(.35), 'Input produced no terminal output'
        os.write(master, b'p')
        expect(b'PAUSED')
        collect(.1)
        assert collect(.25) == b'', 'Paused screen continued changing'
        resize(12, 45)
        expect(b'Terminal too small')
        collect(.1)
        assert collect(.25) == b'', 'Small terminal continued changing'
        resize(30, 80)
        expect(b'PAUSED')
        os.write(master, b'p')
        assert collect(.3), 'Resume did not redraw'
        os.write(master, b'p')
        expect(b'PAUSED')
        os.write(master, b'r')
        assert collect(.4), 'Restart did not redraw'
        os.write(master, b'p')
        expect(b'PAUSED')  # Restart left the paused state and accepted a new pause.
        os.write(master, quit_key)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            collect(.05)
            child, status = os.waitpid(pid, os.WNOHANG)
            if child:
                reaped = True
                assert os.waitstatus_to_exitcode(status) == 0, f'Exit status: {status}'
                assert b'Traceback' not in output
                assert b'\x1b[?1049l' in output, 'Curses did not restore the terminal screen'
                return
        raise AssertionError('Game did not quit within three seconds')
    finally:
        if not reaped:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
        os.close(master)


if __name__ == '__main__':
    run_check(b'q')
    run_check(b'\x03')
    print('PASS: real terminal launch, movement/fire input, pause, resize, resume, restart, Q and Ctrl-C exits.')
    print('Engine tests check state changes. This check does not establish human enjoyment or visual taste.')
