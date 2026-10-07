#!/usr/bin/env python3
"""Exercise Pac-Man controls and cleanup through its actual curses process."""
import argparse
from pathlib import Path
import sys
import tempfile

from check_tron_terminal import Terminal as BaseTerminal

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'runs/pacman/04-test/output/terminal-transcript.txt'


def physics(state):
    return {key: value for key, value in state.items() if key not in ('small', 'sound', 'turn_buffer')}


class Terminal(BaseTerminal):
    def __init__(self, directory, cols=80, rows=40, args=()):
        trace = str(Path(directory) / 'trace.jsonl')
        super().__init__(directory, cols, rows,
                         command=[sys.executable, '-B', '-m', 'tink_pacman', '--seed', '1', '--no-color', *args],
                         env_extra={'TINK_PACMAN_TRACE': trace})

    def frozen(self, state, label):
        start = len(self.states())
        self.wait(lambda s: len(self.states()) >= start + 20, label, start)
        observed = self.states()[start:]
        assert all(physics(s) == physics(state) for s in observed), label
        self.notes.append(f'{label}: {len(observed)} unchanged frames')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    output = parser.parse_args().output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    transcripts = []
    try:
        with tempfile.TemporaryDirectory(prefix='pacman-pty-') as directory:
            terminal = Terminal(directory)
            try:
                t = terminal
                initial = t.wait(lambda s: not s['small'], '80x40 playing')
                assert initial['pacman'] == [13, 23] and initial['lives'] == 3, initial
                t.expect(b'paper pac-man')
                t.expect(b'PLAY / PAPER')
                t.send(b'\x1bOC', lambda s: s['direction'] == [1, 0] and s['pacman'] == [14, 23],
                       'Right arrow reverses and moves Pac-Man')
                t.send(b'R', lambda s: s['pacman'] == initial['pacman'] and s['score'] == 0,
                       'Restart resets the board')
                # The real maze has an erasable horizontal wall at (9, 27).
                # Pac-Man reaches it by going left to column 9, then down three tiles.
                t.wait(lambda s: s['pacman'] == [9, 23], 'Move left along the starting corridor', len(t.states()))
                at_wall = t.send(b'S', lambda s: s['pacman'] == [9, 26] and s['direction'] == [0, 1],
                                 'Uppercase WASD turns down and reaches a thin wall')
                assert [9, 27] in at_wall['walls']
                t.send(b' ', lambda s: s['bookmark'] == [9, 26] and not s['bookmark_available'],
                       'Space places Bookmark')
                erased = t.send(b'E', lambda s: not s['eraser_available'] and [9, 27] not in s['walls'],
                                'E erases the wall ahead')
                assert len(erased['walls']) == len(at_wall['walls']) - 1
                t.send(b' e', lambda s: not s['eraser_available'] and not s['bookmark_available'],
                       'Spent twist charges remain spent')
                paused = t.send(b'P', lambda s: s['paused'], 'Pause')
                t.frozen(paused, 'Pause freezes actors, ghost clocks and Bookmark')
                start = len(t.states())
                t.resize(40, 12)
                small = t.wait(lambda s: s['small'], 'Shrink while paused', start)
                assert physics(small) == physics(paused)
                assert small['turn_buffer'] is None
                t.expect(b'Resize terminal')
                t.send(b'rwpe ', lambda s: s['small'], 'Ignore undersize gameplay controls')
                t.frozen(small, 'Undersize freezes the board and charges')
                t.send(b'M', lambda s: s['sound'] in ('key sound muted [M]', 'key sound unavailable'),
                       'Mute while undersized, or explicit unavailable status')
                t.send(b'm', lambda s: s['sound'] in ('key sound on [M]', 'key sound unavailable'),
                       'Unmute while undersized, or explicit unavailable status')
                start = len(t.states())
                t.resize(100, 45)
                restored = t.wait(lambda s: not s['small'], 'Recovery at 100x45', start)
                assert physics(restored) == physics(paused)
                t.frozen(restored, 'Recovered pause stays frozen')
                resumed = t.send(b'p', lambda s: not s['paused'], 'Resume')
                expected = physics(restored)
                expected['paused'] = False
                assert physics(resumed) == expected, 'Recovery applied stale elapsed time'
                t.send(b'r', lambda s: s['pacman'] == initial['pacman'] and s['score'] == 0,
                       'Lowercase restart')
                start = len(t.states())
                t.resize(40, 12)
                small = t.wait(lambda s: s['small'], 'Shrink while playing', start)
                t.frozen(small, 'Playing resize freezes actors and clocks')
                start = len(t.states())
                t.resize(80, 40)
                restored = t.wait(lambda s: not s['small'], 'Playing recovery at 80x40', start)
                assert physics(restored) == physics(small)
                t.wait(lambda s: s['pacman'] != restored['pacman'], 'Movement resumes', len(t.states()))
                restarted = t.send(b'R', lambda s: s['pacman'] == initial['pacman'] and s['score'] == 0,
                                   'Restart refills charges and restores the wall')
                assert restarted['walls'] == initial['walls']
                assert restarted['dots'] == initial['dots']
                assert restarted['bookmark_available'] and restarted['eraser_available']
                t.finish(b'q')
            finally:
                transcripts.append(terminal.transcript())
                terminal.close()
        with tempfile.TemporaryDirectory(prefix='pacman-pty-') as directory:
            terminal = Terminal(directory, 40, 12, ('--no-sound', '--classic'))
            try:
                t = terminal
                initial = t.wait(lambda s: s['small'], 'Starts undersized, classic and no sound')
                assert initial['sound'] == 'key sound off'
                t.frozen(initial, 'Initial undersize freezes the simulation')
                start = len(t.states())
                t.resize(80, 40)
                restored = t.wait(lambda s: not s['small'], 'Initial resize recovery', start)
                assert physics(restored) == physics(initial)
                t.send(b' eM', lambda s: s['bookmark_available'] and s['eraser_available']
                       and s['sound'] == 'key sound off', 'Classic twist keys and disabled mute are inert')
                t.finish(b'\x03')
            finally:
                transcripts.append(terminal.transcript())
                terminal.close()
    finally:
        output.write_text('\n\n'.join(transcripts).rstrip() + '\n', encoding='utf-8')
    print('PASS: Pac-Man real PTY arrows/WASD, Bookmark, Eraser, pause, restart, resize, mute status, classic, no sound, Q and SIGINT; modes restored; child groups gone.')
    print(f'Transcript: {output}')


if __name__ == '__main__':
    main()
