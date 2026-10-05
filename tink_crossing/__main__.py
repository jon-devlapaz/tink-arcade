"""Run Paper Crossing with python3 -m tink_crossing."""
import argparse
import curses
import sys
from .ui import run


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='python3 -m tink_crossing',
        description='Offline lane crossing. Fill five bays on each of three levels.',
        epilog='Requires 80 x 30. Arrows or WASD hop; P pauses; R restarts; M mutes; '
               'Q or Ctrl-C quits.')
    parser.add_argument('--no-color', action='store_true', help='use monochrome rendering')
    parser.add_argument('--no-sound', action='store_true', help='disable audio for the entire session')
    args = parser.parse_args(argv)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('Crossing needs an interactive terminal. Try python3 -m tink_crossing --help.',
              file=sys.stderr)
        return 1
    try:
        warning = curses.wrapper(run, args.no_color, args.no_sound)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f'Crossing could not use this terminal: {error}', file=sys.stderr)
        return 1
    if warning:
        print(f'Crossing audio: {warning}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
