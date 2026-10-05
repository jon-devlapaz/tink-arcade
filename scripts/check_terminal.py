#!/usr/bin/env python3
"""Exercise the actual curses CLI in a PTY. --live spends on Jev requests."""

import argparse
import errno
import fcntl
import json
import os
from pathlib import Path
import pty
import select
import signal
import struct
import sys
import termios
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='call real Jev using TYPESAFE_API_KEY')
    args = parser.parse_args()
    if args.live and not os.environ.get('TYPESAFE_API_KEY'):
        parser.error('TYPESAFE_API_KEY is required for the live check')
    root = Path(__file__).resolve().parents[1]
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(root)
        os.environ['TERM'] = 'xterm-256color'
        argv = [sys.executable, '-B', '-m', 'neon_tetris', '--no-sound', '--seed', '1']
        if args.live:
            argv += ['--versus-jev']
        os.execv(sys.executable, argv)
    data = bytearray()
    exited = False

    def resize(rows, columns):
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, columns, 0, 0))
        os.kill(pid, signal.SIGWINCH)

    def collect(seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if select.select([fd], [], [], max(0, deadline - time.monotonic()))[0]:
                try:
                    chunk = os.read(fd, 65536)
                except OSError as error:
                    if error.errno == errno.EIO:
                        return
                    raise
                if not chunk:
                    return
                data.extend(chunk)

    try:
        resize(30, 80)
        collect(.5)
        os.write(fd, b'adx ')
        collect(.5)
        os.write(fd, b'p')
        collect(.3)
        resize(20, 60)
        collect(.3)
        resize(30, 80)
        collect(.3)
        os.write(fd, b'p')
        collect(.3)
        os.write(fd, b'r')
        collect(2)
        if args.live:
            os.write(fd, b' ' * 30)
            collect(.4)
        os.write(fd, b'q')
        collect(1)
        deadline = time.monotonic() + 1
        child, status = os.waitpid(pid, os.WNOHANG)
        while child == 0 and time.monotonic() < deadline:
            time.sleep(.01)
            child, status = os.waitpid(pid, os.WNOHANG)
        assert child == pid, 'CLI did not exit within one second of Q'
        exited = True
        assert os.waitstatus_to_exitcode(status) == 0, f'CLI exit: {status}'
        text = data.decode('utf-8', 'replace')
        assert 'Traceback' not in text, 'CLI crashed'
        assert 'Resize' in text, 'Resize warning missing'
        if args.live:
            assert 'TINK ARCADE' in text and 'JEV' in text, 'Race view missing'
            assert 'PAUSED' in text, 'Pause did not render'
            assert 'Est. $' in text, 'Cost display missing'
            assert 'Jev wins' in text or 'You win' in text or 'Draw' in text, 'Match result missing'
            assert 'Jev error:' not in text, 'Live provider failed; inspect sanitized terminal output'
        print(json.dumps({'mode': 'live Jev' if args.live else 'solo', 'exit': 0,
                          'match_result': ('Jev wins' if 'Jev wins' in text else 'You win' if 'You win' in text else 'Draw') if args.live else None,
                          'exercised': ['launch', 'movement', 'drop', 'pause', 'resize', 'resume', 'restart', 'match end' if args.live else 'solo play', 'quit'],
                          'captured_bytes': len(data),
                          'limits': 'Scripted input with forced human top-out in live mode; not a competitive playtest or enjoyment assessment.'}, indent=2))
        # Only the final plain-text cost line, outside the alternate screen.
        if args.live:
            tail = text.rsplit('Est. $', 1)[-1].strip()
            print('Final session estimate: Est. $' + tail)
    finally:
        if not exited:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            os.waitpid(pid, 0)
        os.close(fd)


if __name__ == '__main__':
    main()
