#!/usr/bin/env python3
"""Run the full suite and require successful Invaders groups and legal replay."""
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def cases(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from cases(test)
        else:
            yield test


class RequiredResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_ids = set()

    def addSuccess(self, test):
        self.passed_ids.add(test.id())
        super().addSuccess(test)


def check_suite(suite):
    required = {t.id() for t in cases(suite) if t.id().startswith(('test_invaders_engine.', 'test_invaders_ui.'))}
    for group in ('engine', 'ui'):
        count = sum(name.startswith(f'test_invaders_{group}.') for name in required)
        print(f'Invaders {group}: {count} tests', flush=True)
        if not count:
            return 1
    if not any(name.endswith('.test_full_legal_replay') for name in required):
        print('Missing full legal replay', file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=1, resultclass=RequiredResult).run(suite)
    for case, reason in result.skipped:
        print(f'SKIP {case.id()}: {reason}')
    missing = required - result.passed_ids
    if missing:
        print(f'Required tests did not pass: {sorted(missing)}', file=sys.stderr)
    print(f'Total: {result.testsRun}; skips: {len(result.skipped)}')
    return 0 if result.wasSuccessful() and not missing else 1


def main():
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / 'tests'))
    if loader.errors:
        print('\n'.join(loader.errors), file=sys.stderr)
        return 1
    return check_suite(suite)


if __name__ == '__main__':
    sys.exit(main())
