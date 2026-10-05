import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from scripts import check_invaders_terminal as terminal
from scripts import check_invaders_tests as suite_checker
from scripts.capture_invaders import ObservedGame, loss_input, screen_html


class HelperTests(unittest.TestCase):
    def test_explicit_destination_failure_retains_partial_evidence_and_cleans_up(self):
        fake = Mock()
        fake.transcript.return_value = 'partial real-output sentinel\n'
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'outside checkout' / 'partial.txt'
            with patch.object(terminal, 'Terminal', return_value=fake), \
                    patch.object(terminal, 'exercise', side_effect=RuntimeError('deliberate failure')):
                with self.assertRaisesRegex(RuntimeError, 'deliberate failure'):
                    terminal.main(['--output', str(target)])
            self.assertIn('partial real-output sentinel', target.read_text())
            fake.close.assert_called_once()
            self.assertIn('FAIL', fake.notes.append.call_args.args[0])

    def test_terminal_cli_requires_output_and_failure_returns_nonzero(self):
        result = subprocess.run([sys.executable, '-B', 'scripts/check_invaders_terminal.py'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('--output', result.stderr)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'failed.txt'
            # Failure is injected into the checker driver, never the running game.
            code = ('from scripts import check_invaders_terminal as m; '
                    'm.exercise=lambda t,c: (_ for _ in ()).throw(RuntimeError("forced failure")); '
                    f'm.main(["--output", {str(destination)!r}])')
            result = subprocess.run([sys.executable, '-B', '-c', code], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FAIL: RuntimeError: forced failure', destination.read_text())

    def test_require_survives_optimized_python(self):
        result = subprocess.run([sys.executable, '-O', '-B', '-c',
            'from scripts.check_invaders_terminal import require; require(False,"must fail")'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('must fail', result.stderr)

    def test_suite_rejects_missing_skipped_failed_and_unexecuted_required_groups(self):
        def case(name, behavior='pass'):
            class Example(unittest.TestCase):
                def runTest(self):
                    if behavior == 'skip': self.skipTest('required case skipped')
                    if behavior == 'fail': self.fail('required case failed')
                def id(self): return name
            return Example()
        engine = 'test_invaders_engine.Example.test_full_legal_replay'
        ui = 'test_invaders_ui.Example.test_input'
        for entries in ([], [(ui, 'pass')], [(engine, 'pass')],
                        [(engine, 'skip'), (ui, 'pass')], [(engine, 'pass'), (ui, 'fail')],
                        [('test_invaders_engine.Example.test_other', 'pass'), (ui, 'pass')]):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(suite_checker.check_suite(unittest.TestSuite(case(*e) for e in entries)), 1)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(suite_checker.check_suite(unittest.TestSuite([case(engine), case(ui)])), 0)

    def test_capture_adapter_does_not_mutate_observed_state(self):
        from tink_invaders.engine import Game
        from scripts.replay_invaders import choose_input
        state = Game(7).snapshot(); before = json.dumps(state)
        self.assertEqual(choose_input(ObservedGame(state)), 'space')
        self.assertEqual(loss_input(state), 'space')
        self.assertEqual(json.dumps(state), before)
        rendered = screen_html({'screen_masks': {'char':255, 'color':65280, 'bold':65536, 'dim':131072},
                                'screen': [[ord('<'), ord('&')]]}, False)
        self.assertIn('&lt;', rendered); self.assertIn('&amp;', rendered)
