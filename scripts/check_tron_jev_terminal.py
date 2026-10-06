#!/usr/bin/env python3
"""Drive the real Tron vs Jev program through a POSIX PTY with a fixture client: no network, no key, no cost.

The fixture is installed by this script, never by a user-facing flag. A live run against real Jev is a separate,
billed step (see runs/tron-vs-jev/handoff.md) and is never part of this check.
"""
import argparse
from pathlib import Path
import sys
import tempfile

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import check_tron_terminal as base  # noqa: E402

ROOT = base.ROOT
OUTPUT = ROOT / 'runs/tron-vs-jev/04-test/output/terminal-transcript.txt'
FAKE_KEY = 'fixture-key-not-a-real-credential'
START = [[6, 10], [31, 10]]
LAUNCHER = (
    'import sys; sys.path.insert(0, {root!r}); '
    'from tests.tron_jev_fixture import FixtureClient; import tink_tron.__main__ as m; '
    'm.make_client = lambda key: FixtureClient(fail=({fail},)); '
    "sys.exit(m.main(['--versus-jev', '--seed', '1', '--no-color', '--no-sound']))")


def launch(directory, fail=(2,), cols=80, rows=30):
    command = [sys.executable, '-B', '-c', LAUNCHER.format(root=str(ROOT), fail=','.join(map(str, fail)))]
    return base.Terminal(directory, cols, rows, command=command, env_extra={'TYPESAFE_API_KEY': FAKE_KEY})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT,
                        help='transcript path (relative to the current directory; default: %(default)s)')
    output = parser.parse_args().output.resolve()
    transcripts = []
    output.parent.mkdir(parents=True, exist_ok=True)
    physics = base.physics
    try:
        with tempfile.TemporaryDirectory(prefix='tron-jev-pty-') as directory:
            terminal = launch(directory)
            try:
                t = terminal
                first = t.wait(lambda s: not s['small'], '80x30 first frame')
                assert first['elapsed'] == 0 and first['heads'] == START, first
                assert first['hold'] == 'WAITING FOR JEV', 'play must not start before the opening route'
                t.expect(b'paper tron'); t.expect(b'JEV')
                started = t.wait(lambda s: s['plan'] > 0 and not s['hold'], 'Opening route arrived, play released')
                t.wait(lambda s: s['elapsed'] > 0.2, 'Both cycles move along the route', len(t.states()))
                held = t.wait(lambda s: s['hold'] == 'JEV ERROR', 'Request 2 fails mid-round: play is held')
                t.expect(b'JEV ERROR'); t.expect(b'Enter retry')
                t.frozen(held, 'An error freezes both cycles and the clock')
                assert 'Jev' in held['error'] and held['calls'] == 2, held
                retried = t.send(b'\r', lambda s: not s['hold'], 'Enter retries explicitly')
                after = t.wait(lambda s: s['calls'] >= 3 and s['elapsed'] > held['elapsed'], 'Third request succeeds, play resumes', len(t.states()))
                assert after['error'] == '', after
                paused = t.send(b'p', lambda s: s['paused'], 'Pause')
                t.frozen(paused, 'Pause freezes both cycles')
                start = len(t.states()); t.resize(40, 12)
                small = t.wait(lambda s: s['small'], 'Shrink while paused', start)
                assert physics(small) == physics(paused)
                t.expect(b'Resize terminal')
                t.frozen(small, 'Undersize freezes both cycles')
                start = len(t.states()); t.resize(80, 30)
                restored = t.wait(lambda s: not s['small'], 'Restore', start)
                assert physics(restored) == physics(paused)
                t.send(b'p', lambda s: not s['paused'], 'Resume')
                restarted = t.send(b'R', lambda s: s['heads'] == START and s['elapsed'] == 0, 'Restart a match')
                assert restarted['scores'] == [0, 0]
                t.wait(lambda s: s['plan'] > 0 and not s['hold'], 'New match waits for a fresh opening route, then plays', len(t.states()))
                t.send(b'w', lambda s: s['dirs'][0] == [0, -1], 'Steer up')
                over = t.wait(lambda s: s['over'], 'Wall loses the round', len(t.states()))
                assert over['winner'] == 1, over
                t.expect(b'JEV TAKES THE ROUND'); t.frozen(over, 'Round result freezes the board')
                calls = over['calls']
                nxt = t.send(b' ', lambda s: not s['over'], 'Space starts the next round')
                assert nxt['hold'] == '' and nxt['plan'] > 0, ('the next opening route was fetched during the result', nxt)
                t.finish(b'q')
                t.expect(b'Tron vs Jev:')
                assert FAKE_KEY.encode() not in t.raw, 'the key must never be printed'
            finally:
                transcripts.append(terminal.transcript()); terminal.close()
        with tempfile.TemporaryDirectory(prefix='tron-jev-pty-') as directory:
            terminal = launch(directory, fail=(1,), cols=40, rows=12)
            try:
                t = terminal
                t.wait(lambda s: s['small'], 'Starts undersized')
                start = len(t.states()); t.resize(80, 30)
                err = t.wait(lambda s: s['hold'] == 'JEV ERROR', 'Opening request fails: the round never starts', start)
                assert err['elapsed'] == 0 and err['heads'] == START, err
                t.frozen(err, 'A failed opening leaves the board untouched')
                t.send(b'\r', lambda s: not s['hold'] or s['hold'] == 'WAITING FOR JEV', 'Enter retries the opening')
                t.wait(lambda s: s['plan'] > 0 and not s['hold'], 'Retry succeeds and play starts', len(t.states()))
                t.finish(b'\x03')
                assert FAKE_KEY.encode() not in t.raw
            finally:
                transcripts.append(terminal.transcript()); terminal.close()
    finally:
        output.write_text('\n\n'.join(transcripts).rstrip() + '\n', encoding='utf-8')
    print('PASS: Tron vs Jev real PTY with a fixture client: opening wait, mid-round error and retry, pause, resize, restart, '
          'round result with prefetched opening, failed opening and retry, Q and SIGINT; modes restored; no key in output.')
    print(f'Transcript: {output}')


if __name__ == '__main__':
    main()
