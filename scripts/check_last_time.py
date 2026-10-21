#!/usr/bin/env python3
"""Require nonempty, unskipped Last Time acceptance tests."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REQUIRED = (
    'test_last_time_engine.LastTimeRules.test_collectible_sparks',
    'test_last_time_engine.LastTimeRules.test_fifteen_second_round',
    'test_last_time_engine.LastTimeRules.test_exact_replay',
    'test_last_time_engine.LastTimeRules.test_any_ghost_contact_is_fatal',
    'test_last_time_engine.LastTimeRules.test_stacking_keeps_all_paths_through_round_five',
    'test_last_time_ui.LastTimeUI.test_arrows_and_one_life',
    'test_last_time_engine.LastTimeRules.test_score_only_counts_sparks',
    'test_last_time_ui.LastTimeUI.test_registry_and_cli',
)


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_last_time_*.py')
    tests = list(flatten(suite))
    ids = {test.id() for test in tests}
    missing = set(REQUIRED) - ids
    if missing or not tests:
        raise SystemExit(f'Missing required tests: {sorted(missing)}')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(tests))
    return int(not result.wasSuccessful() or bool(result.skipped))


if __name__ == '__main__':
    sys.exit(main())
