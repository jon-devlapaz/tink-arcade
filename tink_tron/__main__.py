"""Run Tron light cycles with python3 -m tink_tron."""
import argparse
import curses
import os
import sys
from .ai import LEVELS
from .ui import run


def make_client(key):
    """The Jev client; the terminal check replaces this with a fixture, so no user-facing flag selects one."""
    from neon_tetris.jev import JevClient
    return JevClient(key)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='python3 -m tink_tron', description='Offline Tron light cycles on a paper terminal canvas.',
        epilog='Requires 80 x 30. --versus-jev makes billed API calls and shows an estimated cost. Arrows/WASD steer (two-player: WASD left, arrows right); Space next round; '
               'P pauses; R restarts the match; M mutes; Q or Ctrl-C quits.')
    parser.add_argument('--two-player', action='store_true', help='second human on the arrow keys instead of the machine')
    parser.add_argument('--level', choices=LEVELS, help='machine opponent (default: normal)')
    parser.add_argument('--versus-jev', action='store_true',
                        help='Jev steers player 2; needs TYPESAFE_API_KEY and makes billed API calls')
    parser.add_argument('--seed', type=int, help='repeat the same machine choices on restart')
    parser.add_argument('--no-color', action='store_true', help='use monochrome rendering')
    parser.add_argument('--no-sound', action='store_true', help='disable audio for the entire session')
    args = parser.parse_args(argv)
    if args.versus_jev and (args.two_player or args.level):
        parser.error('--versus-jev cannot be combined with --two-player or --level')
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print('Tron needs an interactive terminal. Try python3 -m tink_tron --help.', file=sys.stderr)
        return 1
    client = None
    if args.versus_jev:
        try:
            client = make_client(os.environ.get('TYPESAFE_API_KEY'))
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
    try:
        if client:
            from .jev_ui import run_jev
            warning, summary = curses.wrapper(run_jev, args.seed, args.no_color, args.no_sound, client)
            print(summary)
        else:
            warning = curses.wrapper(run, args.seed, args.two_player, args.level or 'normal', args.no_color, args.no_sound)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f'Tron could not use this terminal: {error}', file=sys.stderr)
        return 1
    if warning:
        print(f'Tron audio: {warning}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
