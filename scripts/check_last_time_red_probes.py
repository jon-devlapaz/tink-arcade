#!/usr/bin/env python3
"""Mutate disposable source copies; each acceptance test must fail by assertion."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
PROBES = (
    ('timer', 'tink_last_time/engine.py', 'ROUND_TICKS = 150', 'ROUND_TICKS = 151',
     'test_last_time_engine.LastTimeRules.test_fifteen_second_round'),
    ('replay', 'tink_last_time/engine.py', 'tuple(path[self.tick] for path in self.paths)', 'tuple(path[0] for path in self.paths)',
     'test_last_time_engine.LastTimeRules.test_exact_replay'),
    ('collision', 'tink_last_time/engine.py', 'if hit:', 'if False:',
     'test_last_time_engine.LastTimeRules.test_any_ghost_contact_is_fatal'),
    ('stacking', 'tink_last_time/engine.py', 'self.paths.append(tuple(self.path))', 'self.paths[:] = [tuple(self.path)]',
     'test_last_time_engine.LastTimeRules.test_stacking_keeps_all_paths_through_round_five'),
    ('score', 'tink_last_time/engine.py', 'self.score += 1', 'self.score += 2',
     'test_last_time_engine.LastTimeRules.test_score_only_counts_sparks'),
    ('arrows', 'tink_last_time/ui.py', 'curses.KEY_LEFT, curses.KEY_RIGHT), DIRECTIONS', 'curses.KEY_RIGHT, curses.KEY_LEFT), DIRECTIONS',
     'test_last_time_ui.LastTimeUI.test_arrows_and_one_life'),
    ('registry', 'arcade_menu/games.json', '"module": "tink_last_time"', '"module": "tink_stacker"',
     'test_last_time_ui.LastTimeUI.test_registry_and_cli'),
    ('dark-field', 'tink_last_time/ui.py', 'dark = self.ink | curses.A_REVERSE', 'dark = self.ink',
     'test_last_time_ui.LastTimeUI.test_dark_arena_symbols_and_states_in_all_palette_modes'),
    ('transition', 'tink_last_time/engine.py', '            self._safe_origin()', '            pass',
     'test_last_time_engine.LastTimeRules.test_boundary_keeps_endpoint_unless_occupied'),
)


def run(command, root):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(root / 'tests') + os.pathsep + str(root))
    return subprocess.run([sys.executable, '-B', *command], cwd=root, env=env,
                          capture_output=True, text=True, timeout=15)


def main():
    with tempfile.TemporaryDirectory(prefix='last-time-red-') as directory:
        root = Path(directory)
        for name in ('tink_last_time', 'arcade_common', 'arcade_menu'):
            shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns('__pycache__'))
        (root / 'tests').mkdir()
        for file in (ROOT / 'tests').glob('test_last_time_*.py'):
            shutil.copy2(file, root / 'tests' / file.name)
        (root / 'scripts').mkdir()
        shutil.copy2(ROOT / 'scripts/check_last_time.py', root / 'scripts/check_last_time.py')
        green = run(['scripts/check_last_time.py'], root)
        assert green.returncode == 0, green.stdout + green.stderr
        for name, filename, old, new, test in PROBES:
            path = root / filename
            original = path.read_text()
            assert original.count(old) == 1, f'Nonunique mutation: {name}'
            path.write_text(original.replace(old, new))
            try:
                result = run(['-m', 'unittest', test], root)
                output = result.stdout + result.stderr
                assert result.returncode != 0 and 'AssertionError' in output and 'FAIL:' in output and 'ERROR:' not in output, f'{name} did not fail by assertion:\n{output}'
            finally:
                path.write_text(original)
            restored = run(['-m', 'unittest', test], root)
            assert restored.returncode == 0, restored.stdout + restored.stderr
            print(f'PASS red probe {name}: assertion failure, restored green')
        green = run(['scripts/check_last_time.py'], root)
        assert green.returncode == 0, green.stdout + green.stderr
        print('PASS full green rerun after all probes')


if __name__ == '__main__':
    main()
