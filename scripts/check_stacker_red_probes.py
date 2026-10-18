#!/usr/bin/env python3
"""Prove named protections in disposable copies, never edit the working implementation."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PROBES = (
    ('overhang', 'engine.py',
     'surviving = tuple(x for x in occupied if not self.rows or x in self.rows[-1])',
     'surviving = occupied',
     'test_stacker_engine.StackerRuleTests.test_lock_retains_only_overlap_and_discards_overhang'),
    ('auto-advance', 'engine.py', "        return 'place'",
     "        self.state = 'waiting'\n        return 'place'",
     'test_stacker_engine.StackerRuleTests.test_successful_lock_automatically_starts_next_row'),
    ('cue-dispatch', 'ui.py', '                audio.play(cue)', '                pass',
     'test_stacker_audio.StackerAudioTests.test_lock_loss_and_win_dispatch_shared_cues'),
    ('frame-servicing', 'ui.py', '            audio.tick()', '            pass',
     'test_stacker_audio.StackerAudioTests.test_audio_tick_runs_each_frame_including_pause_resize_and_end_states'),
)


def invoke(directory, names, output, label, expected_failure=False):
    env = dict(os.environ, PYTHONPATH=str(directory / 'tests'))
    env.pop('TYPESAFE_API_KEY', None)
    command = [sys.executable, '-B', '-m', 'unittest', '-v', *names]
    result = subprocess.run(command, cwd=directory, env=env, capture_output=True, text=True, timeout=90)
    text = result.stdout + result.stderr
    (output / f'{label}.log').write_text(f'$ {json.dumps(command)}\nexit: {result.returncode}\n{text}')
    if expected_failure:
        valid = (result.returncode != 0 and 'AssertionError' in text and 'ERROR:' not in text
                 and all(f'FAIL: {name.rsplit(".", 1)[-1]}' in text for name in names))
    else:
        valid = result.returncode == 0 and '\nOK' in text and 'skipped' not in text
    if not valid:
        raise RuntimeError(f'Unexpected {label} outcome; inspect {output / (label + ".log")}')
    print(f'PASS {label}: {"assertion-level red" if expected_failure else "green without skips"}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true', help='also challenge native Stacker cue dispatch and servicing')
    parser.add_argument('--output', type=Path, default=ROOT / 'runs/stacker/03-build/output/red-probes')
    args = parser.parse_args(argv)
    if args.native and (sys.platform != 'darwin' or os.environ.get('NEON_TETRIS_AUDIO_TESTS') != '1'):
        parser.error('--native requires macOS and NEON_TETRIS_AUDIO_TESTS=1')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for label, filename, old, new, test in PROBES:
        with tempfile.TemporaryDirectory(prefix='stacker-red-') as scratch:
            directory = Path(scratch)
            for package in ('tink_stacker', 'arcade_common'):
                shutil.copytree(ROOT / package, directory / package, ignore=shutil.ignore_patterns('__pycache__'))
            (directory / 'tests').mkdir()
            for path in (ROOT / 'tests').glob('test_stacker_*.py'):
                if path.name != 'test_stacker_checks.py':
                    shutil.copy2(path, directory / 'tests' / path.name)
            names = [test]
            if args.native and filename == 'ui.py':
                names.append('test_stacker_native_audio.NativeStackerAudioTests.test_stacker_action_cues_advance_and_meter_on_spaced_repeats')
            invoke(directory, names, output, label + '-baseline')
            target = directory / 'tink_stacker' / filename
            original = target.read_text()
            if original.count(old) != 1:
                raise RuntimeError(f'{label}: mutation target is not unique')
            target.write_text(original.replace(old, new))
            (output / f'{label}.diff').write_text(f'--- tink_stacker/{filename}\n+++ disposable mutation\n-{old}\n+{new}\n')
            invoke(directory, names, output, label + '-red', True)
            target.write_text(original)
            invoke(directory, names, output, label + '-restored')
    return 0


if __name__ == '__main__':
    sys.exit(main())
