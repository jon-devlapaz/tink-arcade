"""Run with python3 -m tink_breakout."""
import argparse
import curses
import sys
from .ui import run


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='python3 -m tink_breakout', description='Offline terminal Breakout: clear three boards with three lives.',
        epilog='Requires an 80 x 30 terminal. Arrows or A/D move; Space launches; P pauses; R restarts; M mutes keyboard sounds; Q or Ctrl-C quits.')
    parser.add_argument('--no-color', action='store_true', help='use monochrome rendering')
    parser.add_argument('--no-sound', action='store_true', help='disable keyboard sounds for this run')
    args = parser.parse_args(argv)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('Breakout needs an interactive terminal. Try python3 -m tink_breakout --help.', file=sys.stderr)
        return 1
    try:
        warning = curses.wrapper(run, args.no_color, args.no_sound)
        if warning:
            print(f'Keyboard sound unavailable: {warning}', file=sys.stderr)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f'Breakout could not use this terminal: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
