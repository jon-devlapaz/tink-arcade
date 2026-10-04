import contextlib
import curses
import io
import unittest
from unittest.mock import Mock, patch
from tink_breakout.ui import Controller, Renderer
from tink_breakout.__main__ import main


class BreakoutUITests(unittest.TestCase):
    def test_controls_and_case_variants(self):
        for key in (ord('a'), ord('A'), curses.KEY_LEFT):
            c = Controller(0); c.frame(.01, 30, 80, key)
            self.assertEqual(c.game.paddle, 28)
        for key in (ord('d'), ord('D'), curses.KEY_RIGHT):
            c = Controller(0); c.frame(.01, 30, 80, key)
            self.assertEqual(c.game.paddle, 32)
        for pause in ('p', 'P'):
            c = Controller(0); c.frame(.01, 30, 80, ord(' '))
            c.frame(.02, 30, 80, ord(pause)); before = c.game.snapshot()
            c.frame(50, 30, 80, ord('d'))
            self.assertEqual(before, c.game.snapshot())
            c.frame(100, 30, 80, ord(pause))
            self.assertEqual(before, c.game.snapshot())
            c.frame(100.02, 30, 80)
            self.assertNotEqual(before, c.game.snapshot())
        for restart in ('r', 'R'):
            for state in ('playing', 'won', 'lost'):
                c = Controller(0); c.game.state = state; c.paused = True
                c.frame(.01, 30, 80, ord(restart))
                self.assertEqual(c.game.state, 'waiting'); self.assertFalse(c.paused)
        for quit_key in (ord('q'), ord('Q'), 3):
            c = Controller(0); c.frame(.01, 1, 1, quit_key)
            self.assertTrue(c.quit)

    def test_resize_ignores_game_input_and_preserves_pause(self):
        for paused in (False, True):
            c = Controller(0); c.game.launch(); c.paused = paused
            before = c.game.snapshot()
            for key in (ord(' '), ord('r'), ord('p'), ord('d'), curses.KEY_LEFT):
                c.frame(20, 12, 40, key)
            self.assertEqual(before, c.game.snapshot()); self.assertEqual(c.paused, paused)
            state = c.frame(200, 30, 80)
            self.assertEqual(before, c.game.snapshot()); self.assertEqual(state['advanced'], 0)
            c.frame(200.02, 30, 80)
            self.assertEqual(c.game.snapshot() == before, paused)

    def test_monochrome_and_safe_clipping(self):
        screen = Mock(); screen.getmaxyx.return_value = (2, 4)
        with patch('curses.has_colors') as colors:
            r = Renderer(screen, True)
            colors.assert_not_called()
        r.text(-1, 0, 'hidden'); r.text(0, 4, 'hidden')
        screen.addnstr.assert_not_called()
        r.text(1, -2, 'abcdef')
        screen.addnstr.assert_called_with(1, 0, 'cdef', 3, 0)
        screen.addnstr.side_effect = curses.error()
        r.text(0, 0, 'resize')

    def test_help_nonterminal_and_interrupt_cleanup(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as result:
                main(['--help'])
        self.assertEqual(result.exception.code, 0); self.assertIn('80 x 30', out.getvalue())
        with patch('sys.stdin.isatty', return_value=False), contextlib.redirect_stderr(io.StringIO()) as out:
            self.assertEqual(main([]), 1)
        self.assertIn('interactive terminal', out.getvalue())
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
                patch('curses.wrapper', side_effect=KeyboardInterrupt) as wrapper:
            self.assertEqual(main([]), 0)
            wrapper.assert_called_once()
