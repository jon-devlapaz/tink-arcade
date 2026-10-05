"""Launch the terminal shooter."""
import argparse
import curses
import sys
from .ui import run


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Offline solo formation shooter with original text graphics.',
        epilog='Requires an 80 x 30 terminal. Arrows or A/D move, Space fires, P pauses, R restarts, M mutes keyboard sounds, Q or Ctrl-C quits.')
    parser.add_argument('--seed', type=int, help='repeatable enemy choices, also used on restart')
    parser.add_argument('--no-color', action='store_true', help='use monochrome graphics')
    parser.add_argument('--no-sound', action='store_true', help='disable keyboard sounds for this run')
    args = parser.parse_args(argv)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('This game needs an interactive terminal. Use --help for controls.', file=sys.stderr)
        return 1
    try:
        warning = curses.wrapper(run, args.seed, args.no_color, args.no_sound)
        if warning:
            print(f'Keyboard sound unavailable: {warning}', file=sys.stderr)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f'Cannot use this terminal: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
