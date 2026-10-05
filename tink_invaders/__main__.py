"""Run classic Invaders with python3 -m tink_invaders."""
import argparse
import curses
import sys
from .ui import run


def main(argv=None):
    parser = argparse.ArgumentParser(prog='python3 -m tink_invaders', description='Clear three waves with three shared lives on a paper terminal canvas.',
        epilog='Requires 80 x 30. Arrows/A/D move; Space starts or fires; P pauses; R restarts; M mutes; Q or Ctrl-C quits.')
    parser.add_argument('--seed', type=int, help='repeat the same enemy attack sequence on restart')
    parser.add_argument('--no-color', action='store_true', help='use monochrome rendering')
    parser.add_argument('--no-sound', action='store_true', help='disable audio for the entire session')
    args = parser.parse_args(argv)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('Invaders needs an interactive terminal. Try python3 -m tink_invaders --help.', file=sys.stderr)
        return 1
    try:
        warning = curses.wrapper(run, args.seed, args.no_color, args.no_sound)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f'Invaders could not use this terminal: {error}', file=sys.stderr)
        return 1
    if warning:
        print(f'Invaders audio: {warning}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
