"""Launch with python3 -m neon_tetris."""

import argparse
import curses
import sys

from .ui import run


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m neon_tetris",
        description="Socratink / paper tetris. Make room for the next idea. Starts playing immediately.",
        epilog=("Requires an interactive terminal of at least 80 columns x 30 rows. "
                "Controls: Left/Right or A/D move; Down/S soft drop; Up/X rotate; "
                "Z reverse rotate; Space hard drop; C hold; P pause; R restart; "
                "M mute keyboard sounds; Q or Ctrl-C quit. Clear 10 lines per level. "
                "No scores are saved. Sounds are bundled; no network is needed."),
    )
    parser.add_argument("--seed", type=int, metavar="INT",
                        help="reproducible seven-bag order (also used on restart)")
    parser.add_argument("--no-color", action="store_true", help="use monochrome rendering")
    parser.add_argument("--no-sound", action="store_true", help="disable keyboard sounds for this run")
    args = parser.parse_args(argv)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("Socratink Tetris needs an interactive terminal. Try python3 -m neon_tetris --help.",
              file=sys.stderr)
        return 1
    try:
        warning = curses.wrapper(run, args.seed, args.no_color, args.no_sound)
        if warning:
            print(f"Keyboard sound unavailable: {warning}", file=sys.stderr)
    except KeyboardInterrupt:
        return 0
    except curses.error as error:
        print(f"Socratink Tetris could not use this terminal: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
