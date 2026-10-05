"""Run Paper Pong with python3 -m tink_pong."""
import argparse
import curses
import sys
from .ui import run


def main(argv=None):
    parser = argparse.ArgumentParser(prog='python3 -m tink_pong', description='Offline solo Pong. First to seven wins.',
        epilog='Requires 80 x 30. Up/down or W/S move; Space serves; P pauses; R restarts; M mutes; Q or Ctrl-C quits.')
    parser.add_argument('--no-color', action='store_true', help='use monochrome rendering')
    parser.add_argument('--no-sound', action='store_true', help='disable audio for the entire session')
    args = parser.parse_args(argv)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('Pong needs an interactive terminal. Try python3 -m tink_pong --help.', file=sys.stderr)
        return 1
    try:
        warning = curses.wrapper(run, args.no_color, args.no_sound)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f'Pong could not use this terminal: {error}', file=sys.stderr)
        return 1
    if warning:
        print(f'Pong audio: {warning}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
