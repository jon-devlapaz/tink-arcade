#!/usr/bin/env python3
"""Run every check locally: the games' test suite, then the menu end-to-end check."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = (
    ("games: unit and terminal tests",
     [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"], ROOT),
    ("menu: launch every game, check design and sound",
     [sys.executable, "-B", "scripts/check_arcade.py"], ROOT),
)


def main():
    failed = []
    for name, command, cwd in STEPS:
        print(f"\n== {name}", flush=True)
        if subprocess.run(command, cwd=cwd).returncode:
            failed.append(name)
    print("\nFAILED: " + "; ".join(failed) if failed else "\nAll checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
