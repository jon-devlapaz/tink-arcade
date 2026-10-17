"""Run Paper Wordle with python3 -m tink_wordle."""
import argparse
import curses
import sys
from .ui import run


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='python3 -m tink_wordle',
        description='Offline Wordle: find the five-letter word in six tries.',
        epilog='Type letters; Backspace deletes; Enter guesses; F2 restarts; F3 mutes; Esc quits.',
    )
    parser.add_argument('--seed', type=int, help='repeat the answer selection')
    parser.add_argument('--no-color', action='store_true', help='use monochrome rendering')
    parser.add_argument('--no-sound', action='store_true', help='disable audio for the session')
    args = parser.parse_args(argv)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('Wordle needs an interactive terminal. Try python3 -m tink_wordle --help.', file=sys.stderr)
        return 1
    try:
        warning = curses.wrapper(run, args.seed, args.no_color, args.no_sound)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f'Wordle could not use this terminal: {error}', file=sys.stderr)
        return 1
    if warning:
        print(f'Wordle audio: {warning}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
