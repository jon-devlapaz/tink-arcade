import curses
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import Mock, patch

from arcade_common.audio import KeyboardAudio, SOUND_DIR
from tink_tron.__main__ import main
from tink_tron.engine import DOWN, Game, LEFT, RIGHT, STEP, UP
from tink_tron.ui import Renderer, _run_loop, handle_key, key_turns, run


def screen_of(rows, cols):
    screen = Mock()
    screen.getmaxyx.return_value = rows, cols
    return screen


def drawn(game, rows=30, cols=80, small=False, sound='key sound muted [M]', no_color=True):
    screen = screen_of(rows, cols)
    Renderer(screen, no_color).draw(game, small, sound)
    return [c.args for c in screen.addnstr.call_args_list]


class TronUITests(unittest.TestCase):
    def test_solo_arrows_and_wasd_both_steer_player_one(self):
        for direction, keys in ((UP, (curses.KEY_UP, ord('w'), ord('W'))), (DOWN, (curses.KEY_DOWN, ord('s'), ord('S'))),
                                (LEFT, (curses.KEY_LEFT, ord('a'), ord('A'))), (RIGHT, (curses.KEY_RIGHT, ord('d'), ord('D')))):
            for key in keys:
                self.assertEqual(key_turns(Game(1), key), [(0, direction)])
        self.assertEqual(key_turns(Game(1), ord('x')), [])

    def test_two_player_splits_wasd_and_arrows(self):
        g = Game(1, two_player=True)
        self.assertEqual(key_turns(g, ord('w')), [(0, UP)])
        self.assertEqual(key_turns(g, curses.KEY_UP), [(1, UP)])
        self.assertEqual(key_turns(g, ord('D')), [(0, RIGHT)])
        self.assertEqual(key_turns(g, curses.KEY_LEFT), [(1, LEFT)])

    def test_keys_reach_the_game_and_stay_silent_unless_a_step_makes_a_cue(self):
        g, a = Game(1, two_player=True), Mock()
        handle_key(g, ord('w'), a)
        handle_key(g, curses.KEY_DOWN, a)
        self.assertEqual(g.pending, [UP, DOWN])
        a.play.assert_not_called()

    def test_quit_pause_restart_space_and_mute(self):
        for key in (ord('q'), ord('Q'), 3):
            self.assertFalse(handle_key(Game(1), key, Mock()))
        for key in 'mM':
            a = Mock()
            handle_key(Game(1), ord(key), a)
            a.toggle.assert_called_once()
        g, a = Game(1), Mock()
        for key in 'pP':
            handle_key(g, ord(key), a)
            a.play.assert_called_with('switch')
        g.paused = False
        g.scores = [1, 2]
        for key in 'rR':
            handle_key(g, ord(key), a)
            self.assertEqual(g.scores, [0, 0])
            a.play.assert_called_with('switch')
        a.reset_mock()
        handle_key(g, ord(' '), a)  # no round has ended, so Space does nothing
        a.play.assert_not_called()
        g.turn(0, UP)
        for _ in range(12):
            g.update(STEP)
        handle_key(g, ord(' '), a)
        self.assertFalse(g.round_over)
        a.play.assert_called_with('switch')

    def test_palette_matches_the_other_cabinets_in_256_and_eight_colors(self):
        for colors, expected in ((256, [(233, 230), (29, 230), (240, 230), (245, 230)]), (8, [(0, 7), (6, 7), (0, 7), (0, 7)])):
            with patch('curses.has_colors', return_value=True), patch('curses.start_color'), \
                 patch('curses.COLORS', colors, create=True), patch('curses.COLOR_PAIRS', 8, create=True), \
                 patch('curses.init_pair') as pairs, patch('curses.color_pair', side_effect=lambda n: n):
                Renderer(Mock())
                self.assertEqual([c.args[1:] for c in pairs.call_args_list], expected)
        with patch('curses.has_colors') as colors:
            Renderer(Mock(), True)
            colors.assert_not_called()

    def test_layout_stays_inside_the_screen_and_marks_are_distinct_without_color(self):
        for rows, cols in ((30, 80), (35, 100)):
            for state in ('playing', 'paused', 'round', 'match'):
                g = Game(1, two_player=True)
                for _ in range(3):
                    g.update(STEP)
                if state == 'paused':
                    g.paused = True
                if state == 'round':
                    g.round_over, g.winner = True, 0
                if state == 'match':
                    g.round_over, g.winner, g.match_winner = True, 1, 1
                calls = drawn(g, rows, cols)
                for y, x, text, width, attr in calls:
                    self.assertTrue(text.isascii())
                    self.assertTrue(0 <= y < rows and 0 <= x and x + len(text) <= cols, (y, x, text))
                texts = [c[2] for c in calls]
                for mark in ('##', '==', '@@', '::', 'key sound muted [M]', 'M mute   Q quit   Ctrl-C exit'):
                    self.assertIn(mark, texts)
                expected = {'paused': 'PAUSED', 'round': 'PLAYER 1 TAKES THE ROUND',
                            'match': 'PLAYER 2 WINS THE MATCH'}.get(state)
                if expected:
                    self.assertIn(expected, texts)
                head1 = next(c for c in calls if c[2] == '##')
                trail1 = next(c for c in calls if c[2] == '==')
                head2 = next(c for c in calls if c[2] == '@@')
                self.assertNotEqual(head1[4], trail1[4])
                self.assertTrue(head1[4] & curses.A_REVERSE and head2[4] & curses.A_REVERSE)
                self.assertFalse(trail1[4] & curses.A_REVERSE)
                self.assertEqual(head1[:2], ((rows - 30) // 2 + 5 + 10, (cols - 80) // 2 + 2 + 9 * 2))  # head after 3 steps from x=6

    def test_solo_shows_you_and_the_machine_level(self):
        texts = [c[2] for c in drawn(Game(1, level='hard'))]
        self.assertTrue(any('MACHINE (hard)' in t for t in texts))
        self.assertTrue(any(t.startswith('YOU') for t in texts))
        texts = [c[2] for c in drawn(Game(1, two_player=True))]
        self.assertTrue(any('PLAYER 2' in t for t in texts))

    def test_undersized_screen_shows_the_resize_message(self):
        texts = [c[2] for c in drawn(Game(1), 12, 40, small=True)]
        self.assertTrue(any('Resize terminal' in t for t in texts))
        self.assertNotIn('##', texts)

    def test_clipping_and_resize_errors(self):
        s = screen_of(5, 8)
        r = Renderer(s, True)
        r.text(4, 7, 'x'); r.text(-1, 0, 'x')
        s.addnstr.assert_not_called()
        r.text(2, -2, 'abcdef')
        s.addnstr.assert_called_with(2, 0, 'cdef', 8, 0)
        s.addnstr.side_effect = curses.error()
        r.text(1, 0, 'x')
        s.refresh.side_effect = curses.error()
        r._refresh()
        s.addnstr.side_effect = ValueError('bug')
        with self.assertRaises(ValueError):
            r.text(1, 0, 'x')

    def test_resize_freezes_time_clears_turns_polls_audio_and_keeps_pause(self):
        for paused in (False, True):
            g = Game(1)
            g.paused = paused
            g.elapsed = .05
            g.pending = [UP, None]
            s = Mock()
            s.getmaxyx.side_effect = [(12, 40), (12, 40), (30, 80), (30, 80)]
            s.getch.side_effect = [ord('r'), ord('p'), ord('w'), -1, ord('m'), -1, -1, ord('q')]
            a, r = Mock(), Mock()
            with patch('tink_tron.ui.time.monotonic', side_effect=[0, 1, 1, 20, 20, 40, 40, 41]), patch('tink_tron.ui.time.sleep'):
                _run_loop(s, r, g, a)
            self.assertEqual(g.heads[0], (6, 10))
            self.assertAlmostEqual(g.elapsed, .05)
            self.assertEqual(g.paused, paused)
            self.assertEqual(g.pending, [None, None])
            a.stop.assert_called_once(); a.toggle.assert_called_once()
            self.assertEqual(a.tick.call_count, 3)

    def test_real_audio_coalescing_mute_disabled_failure_and_cleanup(self):
        backend = Mock(ready=True)
        with patch('arcade_common.audio._make_backend', return_value=backend):
            with KeyboardAudio() as a:
                g = Game(1, two_player=True)
                handle_key(g, ord('w'), a)
                self.assertIsNone(a._pending)
                a.play(g.update(STEP)); a.tick()
                backend.play.assert_called_once_with(SOUND_DIR / 'tactile.wav')
                handle_key(g, ord('m'), a)
                self.assertIn('muted', a.status)
                handle_key(g, ord('r'), a); a.tick()
                self.assertEqual(backend.play.call_count, 1)
                handle_key(g, ord('m'), a); a.tick()
                backend.play.assert_called_with(SOUND_DIR / 'mx-blue.wav')
                backend.tick.side_effect = OSError('broken'); a.tick()
                self.assertIn('unavailable', a.status)
            backend.close.assert_called_once()
        with patch('arcade_common.audio._make_backend') as factory:
            with KeyboardAudio(False) as a:
                handle_key(Game(1), ord('m'), a)
                self.assertEqual(a.status, 'key sound off')
            factory.assert_not_called()

    def test_loop_turn_win_loss_and_straight_cues(self):
        def boxed_in(g):
            g.heads, g.dirs = [(10, 10), (0, 0)], [RIGHT, UP]
            g.trails = {(10, 10): 0, (0, 0): 1, (1, 0): 1, (0, 1): 1}
        def doomed(g):
            g.heads, g.dirs = [(0, 0), (10, 10)], [UP, RIGHT]
            g.trails = {(0, 0): 0, (10, 10): 1}
        for scenario, expected in (('turn', 'move'), ('win', 'clear'), ('loss', 'over'), ('straight', None)):
            g = Game(1)
            if scenario == 'turn':
                g.turn(0, UP)
            if scenario == 'win':
                boxed_in(g)
            if scenario == 'loss':
                doomed(g)
            s = Mock(); s.getmaxyx.return_value = (30, 80); s.getch.side_effect = [-1, ord('q')]
            a = Mock()
            with patch('tink_tron.ui.time.monotonic', side_effect=[0, STEP, STEP, STEP + .01]), patch('tink_tron.ui.time.sleep'):
                _run_loop(s, Mock(), g, a)
            if expected:
                a.play.assert_called_once_with(expected)
            else:
                a.play.assert_not_called()

    def test_run_closes_audio_on_quit_interrupt_and_exception(self):
        for error in (None, KeyboardInterrupt(), ValueError('render')):
            backend, s = Mock(ready=True), Mock()
            with patch('curses.curs_set'), patch('curses.set_escdelay'), patch('tink_tron.ui.Renderer'), \
                 patch('tink_tron.ui._run_loop', side_effect=error), patch('arcade_common.audio._make_backend', return_value=backend):
                if error:
                    with self.assertRaises(type(error)):
                        run(s)
                else:
                    run(s)
            backend.close.assert_called_once()

    def test_trace_is_written_only_when_asked_and_closed(self):
        import json, os, tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'trace.jsonl')
            s = Mock(); s.getmaxyx.return_value = (30, 80); s.getch.side_effect = [-1, ord('q')]
            with patch.dict(os.environ, {'TINK_TRON_TRACE': path}), patch('curses.curs_set'), patch('curses.set_escdelay'), \
                 patch('tink_tron.ui.Renderer'), patch('arcade_common.audio._make_backend', return_value=Mock(ready=True)), \
                 patch('tink_tron.ui.time.sleep'):
                run(s, 1, False, 'easy', True, False)
            with open(path) as trace:
                line = json.loads(trace.readline())
            self.assertEqual((line['heads'], line['scores'], line['small']), ([[6, 10], [31, 10]], [0, 0], False))

    def test_cli_help_flags_nonterminal_and_error_after_wrapper(self):
        with redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit) as result:
            main(['--help'])
        self.assertEqual(result.exception.code, 0)
        for flag in ('--two-player', '--level', '--seed', '--no-color', '--no-sound'):
            self.assertIn(flag, out.getvalue())
        with patch('sys.stdin.isatty', return_value=False), redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main([]), 1)
        self.assertIn('interactive terminal', err.getvalue())
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(['--level', 'nightmare'])
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
             patch('curses.wrapper', return_value='broken') as wrapper, redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main(['--seed', '42', '--two-player', '--level', 'hard', '--no-color', '--no-sound']), 0)
            wrapper.assert_called_once_with(run, 42, True, 'hard', True, True)
        self.assertIn('Tron audio: broken', err.getvalue())
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
             patch('curses.wrapper', side_effect=curses.error('no terminfo')), redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main([]), 1)
        self.assertIn('could not use this terminal', err.getvalue())
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
             patch('curses.wrapper', side_effect=KeyboardInterrupt):
            self.assertEqual(main([]), 0)


if __name__ == '__main__':
    unittest.main()
