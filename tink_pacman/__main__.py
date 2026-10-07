"""Run Pac-Man with python3 -m tink_pacman."""
import argparse
import curses
import sys
from .ui import run


def main(argv=None):
    parser = argparse.ArgumentParser(prog='python3 -m tink_pacman', description='Offline Pac-Man on a paper terminal canvas.',
        epilog='Requires 80 x 40. Arrows/WASD steer; P pauses; R restarts; Q or Ctrl-C quits.')
    parser.add_argument('--seed', type=int, help='repeat the same run')
    parser.add_argument('--no-color', action='store_true', help='use monochrome rendering')
    parser.add_argument('--classic', action='store_true', help='disable Bookmark and Eraser')
    parser.add_argument('--no-sound', action='store_true', help='disable keyboard sounds')
    args = parser.parse_args(argv)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('Pac-Man needs an interactive terminal. Try python3 -m tink_pacman --help.', file=sys.stderr)
        return 1
    try:
        curses.wrapper(run, args.seed, args.no_color, args.classic, args.no_sound)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f'Pac-Man could not use this terminal: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
