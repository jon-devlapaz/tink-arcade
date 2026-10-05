#!/usr/bin/env python3
"""Run all tests and refuse empty or missing Crossing groups."""
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


def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    tests = list(cases(suite))
    for group in ('engine', 'ui'):
        count = sum(t.id().startswith(f'test_crossing_{group}.') for t in tests)
        print(f'Crossing {group}: {count} tests', flush=True)
        if count == 0:
            raise SystemExit(f'Missing Crossing {group} tests')
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    print(f'Total: {result.testsRun}; skips: {len(result.skipped)}', flush=True)
    for case, reason in result.skipped:
        print(f'SKIP {case.id()}: {reason}')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
