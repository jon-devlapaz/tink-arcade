import contextlib
import importlib.util
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('stacker_checks', Path('scripts/check_stacker_tests.py'))
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


class StackerCheckRunnerTests(unittest.TestCase):
    def case(self, name, skipped=False, fails=False):
        class Case(unittest.TestCase):
            def id(self): return name
            def runTest(self):
                if skipped: self.skipTest('missing prerequisite')
                if fails: self.fail('regression')
        return Case()

    def check(self, suite, required):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return checks.check_suite(suite, set(required))

    def test_empty_missing_duplicate_and_skipped_required_tests_fail(self):
        name = 'test_stacker_engine.StackerRuleTests.test_first_row_locks_without_support'
        self.assertEqual(self.check(unittest.TestSuite(), [name]), 1)
        for suite in (unittest.TestSuite([self.case(name, skipped=True)]), unittest.TestSuite([self.case(name), self.case(name)])):
            self.assertEqual(self.check(suite, [name]), 1)
        self.assertEqual(self.check(unittest.TestSuite([self.case(name)]), [name]), 0)

    def test_any_failure_is_fatal_and_optional_skips_are_reported(self):
        name = 'required'
        self.assertEqual(self.check(unittest.TestSuite([self.case(name), self.case('optional', fails=True)]), [name]), 1)
        self.assertEqual(self.check(unittest.TestSuite([self.case(name), self.case('optional', skipped=True)]), [name]), 0)

    def test_native_mode_requires_platform_and_explicit_opt_in(self):
        for platform, env in (('linux', {'NEON_TETRIS_AUDIO_TESTS': '1'}), ('darwin', {})):
            with patch.object(checks.sys, 'platform', platform), patch.dict(os.environ, env, clear=True), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(checks.main(['--sounds', '--require-native']), 1)

    def test_approved_test_names_are_required(self):
        required = checks.required_ids('all', native=True)
        self.assertEqual(len(required), 26)
        self.assertEqual(len(checks.required_ids('rules')), 15)
        self.assertEqual(len(checks.required_ids('sounds', native=True)), 11)
        self.assertIn('test_stacker_native_audio.NativeStackerAudioTests.test_stacker_action_cues_advance_and_meter_on_spaced_repeats', required)
