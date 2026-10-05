"""Launch with python3 -m arcade_menu."""

import argparse
import curses
import sys

from .registry import load_games
from .ui import run


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m arcade_menu",
        description="Tink arcade. Pick a cabinet and play.",
        epilog=("Requires an interactive terminal of at least 80 columns x 30 rows. "
                "Up/Down or W/S choose; Enter or Space plays; 1-9 jump; Q quits. "
                "Games are listed in arcade_menu/games.json."),
    )
    parser.add_argument("--no-color", action="store_true",
                        help="use monochrome rendering (also passed to each game)")
    args = parser.parse_args(argv)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("The arcade needs an interactive terminal. Try python3 -m arcade_menu --help.",
              file=sys.stderr)
        return 1
    games = load_games()
    if not games:
        print("No games listed in arcade_menu/games.json.", file=sys.stderr)
        return 1
    try:
        curses.wrapper(run, games, args.no_color)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f"The arcade could not use this terminal: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
