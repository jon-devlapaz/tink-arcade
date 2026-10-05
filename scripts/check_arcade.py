#!/usr/bin/env python3
"""E2E: drive the real menu in a pty, launch every game, check design parity, return, quit."""
import fcntl, os, pty, select, signal, struct, sys, termios, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from arcade_menu.registry import load_games  # noqa: E402

PAPER = b'48;5;230'  # indexed paper background shared by every game


def main():
    games = load_games()
    pid, fd = pty.fork()
    if pid == 0:
        os.environ['TERM'] = 'xterm-256color'
        os.chdir(ROOT)
        os.execvp(sys.executable, [sys.executable, '-m', 'arcade_menu'])
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', 32, 90, 0, 0))
    buf = b''

    def expect(*needles, timeout=8):
        nonlocal buf
        end = time.time() + timeout
        while time.time() < end:
            if all(n in buf for n in needles):
                return
            if select.select([fd], [], [], .1)[0]:
                try:
                    buf += os.read(fd, 65536)
                except OSError:
                    break
        raise AssertionError(f'missing {[n for n in needles if n not in buf]} in {buf[-300:]!r}')

    failures = []
    try:
        expect(b'tink / arcade', PAPER)
        for number, game in enumerate(games, 1):
            if game.requires_env:  # billed or credentialed; never launched by routine checks
                continue
            buf = b''
            os.write(fd, str(number).encode()); os.write(fd, b'\r')
            try:
                name = game.title.lower().encode()
                expect(b'socratink', b'paper ' + name, b'PLAY / PAPER', PAPER, b'key sound on')
                os.write(fd, b'm')
                expect(b'muted')  # curses redraws only the changed cells
                os.write(fd, b'q')
                buf = b''
                expect(b'tink / arcade')
                print(f'PASS {game.title}')
            except AssertionError as error:
                failures.append(f'{game.title}: {error}')
                print(f'FAIL {game.title}: {error}', flush=True)
                break  # a stuck game leaves the menu unreachable
        if failures:
            return report(failures)
        os.write(fd, b'q')
        end = time.time() + 5
        while time.time() < end:  # keep draining so the menu can exit
            if select.select([fd], [], [], .1)[0]:
                try:
                    os.read(fd, 65536)
                except OSError:
                    break
        _, status = os.waitpid(pid, 0)
        if os.WEXITSTATUS(status) != 0:
            failures.append(f'menu exit status {status}')
    finally:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    return report(failures)


def report(failures):
    for failure in failures:
        print(failure, file=sys.stderr)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
