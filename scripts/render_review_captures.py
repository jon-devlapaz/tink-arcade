#!/usr/bin/env python3
"""Render retained terminal-cell JSON captures without checking generated SVGs into Git."""
import argparse
from pathlib import Path
import shutil

from capture_pong import svg


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('captures', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    paths = sorted(args.captures.glob('*.json'))
    if not paths:
        parser.error('No JSON captures found')
    args.output.mkdir(parents=True, exist_ok=True)
    for path in paths:
        destination = args.output / path.name
        shutil.copyfile(path, destination)
        svg(destination)
    print(f'Rendered {len(paths)} captures to {args.output}')
