import curses
import io
import subprocess
import sys
import unittest
from unittest.mock import Mock, call, patch

from neon_tetris import __main__
from neon_tetris.engine import Game
from neon_tetris.ui import Renderer, handle_key, run


class InputTests(unittest.TestCase):
    def test_keyboard_mapping(self):
        bindings = {
            "move": [((curses.KEY_LEFT, ord("a"), ord("A")), (-1,)),
                     ((curses.KEY_RIGHT, ord("d"), ord("D")), (1,))],
            "soft_drop": [((curses.KEY_DOWN, ord("s"), ord("S")), ())],
            "rotate": [((curses.KEY_UP, ord("x"), ord("X")), (1,)),
                       ((ord("z"), ord("Z")), (-1,))],
            "hard_drop": [((ord(" "),), ())],
            "hold": [((ord("c"), ord("C")), ())],
            "toggle_pause": [((ord("p"), ord("P")), ())],
            "restart": [((ord("r"), ord("R")), ())],
        }
        for method, groups in bindings.items():
            for keys, args in groups:
                for key in keys:
                    with self.subTest(method=method, key=key):
                        game = Mock()
                        self.assertTrue(handle_key(game, key))
                        getattr(game, method).assert_called_once_with(*args)
        for key in (ord("q"), ord("Q"), 3):
            self.assertFalse(handle_key(Mock(), key))

    def test_pause_and_restart_controls(self):
        game = Game(1)
        handle_key(game, ord("p"))
        self.assertTrue(game.paused)
        before = game.active
        handle_key(game, ord(" "))
        self.assertEqual(game.active, before)
        handle_key(game, ord("r"))
        self.assertFalse(game.paused)
        self.assertTrue(game.running)

    def test_resize_freezes_simulation_and_discards_catchup(self):
        game = Game(1)
        screen = Mock()
        screen.getmaxyx.side_effect = [(30, 80), (20, 60), (30, 80), (30, 80), (30, 80)]
        # Ignore a hard drop while undersized; quit on frame five.
        screen.getch.side_effect = [-1, ord(" "), -1, -1, -1, ord("q")]
        clock = [0, 0.01, 0.012, 10, 10.002, 20, 20.002, 20.02, 20.022, 20.04]
        with (patch("neon_tetris.ui.curses.curs_set"),
              patch("neon_tetris.ui.curses.set_escdelay"),
              patch("neon_tetris.ui.Renderer") as renderer,
              patch("neon_tetris.ui.Game", return_value=game),
              patch("neon_tetris.ui.time.monotonic", side_effect=clock),
              patch("neon_tetris.ui.time.sleep") as sleep,
              patch.object(game, "update", wraps=game.update) as update):
            run(screen, seed=1, no_color=True, no_sound=True)
        self.assertEqual(update.call_count, 2)
        self.assertAlmostEqual(update.call_args_list[0].args[0], 0.01)
        self.assertAlmostEqual(update.call_args_list[1].args[0], 0.02)
        self.assertEqual([call.args[1] for call in renderer.return_value.draw.call_args_list],
                         [False, True, False, False])
        self.assertEqual(game.score, 0)
        self.assertTrue(all(cell is None for row in game.board for cell in row))
        self.assertEqual(sleep.call_count, 4)
        self.assertTrue(all(call.args[0] > 0 for call in sleep.call_args_list))

    def test_renderer_clips_and_tolerates_resize_errors(self):
        screen = Mock()
        screen.getmaxyx.return_value = (5, 8)
        renderer = Renderer(screen, no_color=True)
        renderer.text(4, 7, "not safe")
        screen.addnstr.assert_not_called()
        renderer.text(2, -2, "abcdef")
        screen.addnstr.assert_called_once_with(2, 0, "cdef", 8, 0)
        screen.addnstr.side_effect = curses.error("resize")
        renderer.text(1, 0, "safe failure")
        screen.refresh.side_effect = curses.error("resize")
        renderer._refresh()

    def test_renderer_does_not_swallow_programming_errors(self):
        screen = Mock()
        screen.getmaxyx.return_value = (30, 80)
        screen.addnstr.side_effect = ValueError("bug")
        with self.assertRaises(ValueError):
            Renderer(screen, no_color=True).text(1, 1, "test")


class ThemeTests(unittest.TestCase):
    def test_paper_palette_and_basic_terminal_fallback(self):
        for colors, expected in (
            (256, ((233, 230), (29, 230), (240, 230), (245, 230))),
            (8, ((0, 7), (6, 7), (0, 7), (0, 7))),
        ):
            with (
                self.subTest(colors=colors),
                patch("neon_tetris.ui.curses.has_colors", return_value=True),
                patch("neon_tetris.ui.curses.start_color"),
                patch("neon_tetris.ui.curses.COLORS", colors, create=True),
                patch("neon_tetris.ui.curses.COLOR_PAIRS", 64, create=True),
                patch("neon_tetris.ui.curses.init_pair") as init_pair,
                patch("neon_tetris.ui.curses.color_pair", side_effect=lambda n: n << 8),
            ):
                screen = Mock()
                Renderer(screen)
                self.assertEqual(init_pair.call_args_list,
                                 [call(i, *pair) for i, pair in enumerate(expected, 1)])
                screen.bkgd.assert_called_once_with(" ", 1 << 8)

    def test_no_color_does_not_initialize_colors(self):
        with patch("neon_tetris.ui.curses.start_color") as start:
            Renderer(Mock(), no_color=True)
        start.assert_not_called()

    def test_socratink_copy_on_board_and_overlays(self):
        screen = Mock()
        screen.getmaxyx.return_value = (30, 80)
        renderer = Renderer(screen, no_color=True)
        game = Game(17)
        for state, expected in (("play", "A fresh page."), ("pause", "Take a breath."),
                                ("over", "Turn a fresh page."), ("small", "Socratink")):
            with self.subTest(state=state):
                game.paused = state == "pause"
                game.game_over = state == "over"
                screen.addnstr.reset_mock()
                renderer.draw(game, state == "small")
                rendered = "\n".join(c.args[2] for c in screen.addnstr.call_args_list)
                self.assertIn(expected, rendered)
                self.assertIn("socratink", rendered.lower())
                self.assertNotIn("NEON", rendered)
                self.assertNotIn("AFTERGLOW", rendered)
                if state == "over":
                    self.assertNotIn("A fresh page.", rendered)
                for c in screen.addnstr.call_args_list:
                    y, x, text, width, _ = c.args
                    self.assertTrue(text.isascii())
                    self.assertTrue(0 <= y < 30 and 0 <= x < 80)
                    self.assertLessEqual(x + min(width, len(text)), 80)

    def test_active_ink_and_pencil_ghost_are_distinct(self):
        screen = Mock()
        screen.getmaxyx.return_value = (30, 80)
        renderer = Renderer(screen, no_color=True)
        renderer.block(5, 5, "T", active=True)
        active = screen.addnstr.call_args.args
        renderer.block(5, 5, "T")
        settled = screen.addnstr.call_args.args
        renderer.block(5, 5, "T", ghost=True)
        ghost = screen.addnstr.call_args.args
        self.assertTrue(active[4] & curses.A_BOLD)
        self.assertTrue(settled[4] & curses.A_REVERSE)
        self.assertFalse(ghost[4] & curses.A_REVERSE)
        self.assertEqual(ghost[2], "()")
        self.assertNotEqual(active[4], settled[4])


class CLITests(unittest.TestCase):
    def invoke(self, *arguments):
        return subprocess.run([sys.executable, "-m", "neon_tetris", *arguments],
                              stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              timeout=5)

    def test_help_without_tty(self):
        result = self.invoke("--help")
        self.assertEqual(result.returncode, 0)
        for text in ("Socratink", "--seed INT", "--no-color", "--no-sound", "M mute", "80", "30", "Ctrl-C"):
            self.assertIn(text, result.stdout)

    def test_non_tty_fails_cleanly(self):
        result = self.invoke("--seed", "42", "--no-color")
        self.assertEqual(result.returncode, 1)
        self.assertIn("interactive terminal", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_seed(self):
        result = self.invoke("--seed", "not-an-int")
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_no_sound_and_color_flags_reach_the_game(self):
        with (patch("sys.stdin.isatty", return_value=True),
              patch("sys.stdout.isatty", return_value=True),
              patch("neon_tetris.__main__.curses.wrapper", return_value="") as wrapper):
            self.assertEqual(__main__.main(["--seed", "42", "--no-color", "--no-sound"]), 0)
            wrapper.assert_called_once_with(run, 42, True, True)

    def test_audio_failure_is_reported_after_curses_returns(self):
        with (patch("sys.stdin.isatty", return_value=True),
              patch("sys.stdout.isatty", return_value=True),
              patch("neon_tetris.__main__.curses.wrapper", return_value="No audio player found."),
              patch("sys.stderr", new_callable=io.StringIO) as stderr):
            self.assertEqual(__main__.main([]), 0)
            self.assertIn("Keyboard sound unavailable: No audio player found.", stderr.getvalue())

    def test_terminal_error_and_ctrl_c_are_clean(self):
        for error, code in ((curses.error("unsupported terminal"), 1),
                            (KeyboardInterrupt(), 0)):
            with self.subTest(error=type(error).__name__):
                with (patch("sys.stdin.isatty", return_value=True),
                      patch("sys.stdout.isatty", return_value=True),
                      patch("neon_tetris.__main__.curses.wrapper", side_effect=error),
                      patch("sys.stderr", new_callable=io.StringIO)):
                    self.assertEqual(__main__.main([]), code)


if __name__ == "__main__":
    unittest.main()
