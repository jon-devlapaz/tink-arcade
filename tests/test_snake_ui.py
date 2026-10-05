import curses
import io
import unittest
from unittest.mock import Mock, patch
from contextlib import redirect_stdout, redirect_stderr
from tink_snake.engine import Game, UP, DOWN, LEFT, RIGHT
from tink_snake.ui import Renderer, handle_key, run, _run_loop
from tink_snake.__main__ import main
from arcade_common.audio import KeyboardAudio, SOUND_DIR


class SnakeUITests(unittest.TestCase):
    def test_all_bindings(self):
        for direction, keys in ((UP, (curses.KEY_UP, ord('w'), ord('W'))), (DOWN, (curses.KEY_DOWN, ord('s'), ord('S'))),
                                (LEFT, (curses.KEY_LEFT, ord('a'), ord('A'))), (RIGHT, (curses.KEY_RIGHT, ord('d'), ord('D')))):
            for key in keys:
                g = Mock(); a = Mock(); self.assertTrue(handle_key(g, key, a)); g.turn.assert_called_once_with(direction)
                a.play.assert_not_called()
        for key in (ord('q'), ord('Q'), 3):
            self.assertFalse(handle_key(Game(), key, Mock()))
        for key in 'mM':
            a = Mock(); handle_key(Game(), ord(key), a); a.toggle.assert_called_once()

    def test_pause_restart_overlay_and_rejected_input_audio(self):
        g = Game(1); a = Mock()
        for key in 'ad': handle_key(g, ord(key), a)
        a.play.assert_not_called()
        for key in 'pP':
            handle_key(g, ord(key), a); a.play.assert_called_with('switch')
        for key in 'rR':
            g.game_over = True; handle_key(g, ord(key), a)
            self.assertFalse(g.game_over); a.play.assert_called_with('switch')
        g.complete = True; a.reset_mock(); handle_key(g, ord('p'), a); a.play.assert_not_called()

    def test_palette_matches_tetris_in_256_and_eight_colors(self):
        for colors, expected in ((256, [(233,230),(29,230),(240,230),(245,230)]), (8,[(0,7),(6,7),(0,7),(0,7)])):
            with patch('curses.has_colors', return_value=True), patch('curses.start_color'), \
                 patch('curses.COLORS', colors, create=True), patch('curses.COLOR_PAIRS', 8, create=True), \
                 patch('curses.init_pair') as pairs, patch('curses.color_pair', side_effect=lambda n:n):
                Renderer(Mock())
                self.assertEqual([c.args[1:] for c in pairs.call_args_list], expected)
        with patch('curses.has_colors') as colors:
            Renderer(Mock(), True); colors.assert_not_called()

    def test_ascii_layout_bounds_marks_overlays_and_centering(self):
        for rows, cols in ((30,80),(35,100)):
            for state in ('playing','paused','game_over','complete'):
                screen = Mock(); screen.getmaxyx.return_value = rows, cols
                g = Game(1)
                if state != 'playing': setattr(g, state, True)
                Renderer(screen, True).draw(g, False, 'key sound muted [M]')
                calls = [c.args for c in screen.addnstr.call_args_list]
                for y,x,text,width,attr in calls:
                    self.assertTrue(text.isascii()); self.assertTrue(0 <= y < rows); self.assertTrue(0 <= x and x + len(text) <= cols)
                texts = [c[2] for c in calls]
                for text in ('>>','[]','()','key sound muted [M]','M mute   Q quit   Ctrl-C exit'):
                    self.assertIn(text, texts)
                if state != 'playing': self.assertIn({'paused':'PAUSED','game_over':'GAME OVER','complete':'BOARD COMPLETE'}[state], texts)
                head = next(c for c in calls if c[2] == '>>'); body = next(c for c in calls if c[2] == '[]'); food = next(c for c in calls if c[2] == '()')
                self.assertNotEqual(head[4], body[4]); self.assertFalse(food[4] & curses.A_REVERSE)
                self.assertEqual(head[:2], (15+(rows-30)//2,24+(cols-80)//2))

    def test_clipping_and_resize_errors(self):
        s=Mock(); s.getmaxyx.return_value=(5,8); r=Renderer(s,True)
        r.text(4,7,'x'); r.text(-1,0,'x'); s.addnstr.assert_not_called()
        r.text(2,-2,'abcdef'); s.addnstr.assert_called_with(2,0,'cdef',8,0)
        s.addnstr.side_effect=curses.error(); r.text(1,0,'x')
        s.refresh.side_effect=curses.error(); r._refresh()
        s.addnstr.side_effect=ValueError('bug')
        with self.assertRaises(ValueError): r.text(1,0,'x')

    def test_resize_freezes_time_clears_turns_polls_audio_and_keeps_pause(self):
        for paused in (False, True):
            g=Game(1); g.paused=paused; g.elapsed=.05; g.turns.append(UP)
            s=Mock(); s.getmaxyx.side_effect=[(12,40),(12,40),(30,80),(30,80)]
            s.getch.side_effect=[ord('r'),ord('p'),ord('w'),-1,ord('m'),-1,-1,ord('q')]
            a=Mock(); r=Mock()
            with patch('tink_snake.ui.time.monotonic', side_effect=[0,1,1,20,20,40,40,41]), patch('tink_snake.ui.time.sleep'):
                _run_loop(s,r,g,a)
            self.assertEqual(g.snake[0],(10,10)); self.assertAlmostEqual(g.elapsed,.05)
            self.assertEqual(g.paused,paused); self.assertFalse(g.turns)
            a.stop.assert_called_once(); a.toggle.assert_called_once(); self.assertEqual(a.tick.call_count,3)

    def test_real_audio_coalescing_mute_disabled_failure_and_cleanup(self):
        backend=Mock(ready=True)
        with patch('arcade_common.audio._make_backend', return_value=backend):
            with KeyboardAudio() as a:
                g=Game(1); handle_key(g,ord('w'),a); handle_key(g,ord('a'),a)
                self.assertIsNone(a._pending)
                a.play(g.update(.18)); g.food=(9,9); a.play(g.update(.18)); a.tick()
                backend.play.assert_called_once_with(SOUND_DIR/'clear.wav')
                handle_key(g,ord('m'),a); self.assertIn('muted',a.status)
                handle_key(g,ord('r'),a); a.tick(); self.assertEqual(backend.play.call_count,1)
                handle_key(g,ord('m'),a); a.tick(); backend.play.assert_called_with(SOUND_DIR/'mx-blue.wav')
                backend.tick.side_effect=OSError('broken'); a.tick(); self.assertIn('unavailable',a.status)
            backend.close.assert_called_once()
        with patch('arcade_common.audio._make_backend') as factory:
            with KeyboardAudio(False) as a:
                handle_key(Game(),ord('m'),a); self.assertEqual(a.status,'key sound off')
            factory.assert_not_called()

    def test_loop_successful_turn_food_collision_and_straight_cues(self):
        for scenario, expected in (('turn','move'),('food','clear'),('wall','over'),('straight',None)):
            g=Game(1)
            if scenario=='turn': g.turn(UP)
            if scenario=='food': g.turn(UP); g.food=(10,9)
            if scenario=='wall': g.snake=[(19,10)]
            s=Mock(); s.getmaxyx.return_value=(30,80); s.getch.side_effect=[-1,ord('q')]
            a=Mock()
            with patch('tink_snake.ui.time.monotonic', side_effect=[0,.18,.18,.2]), patch('tink_snake.ui.time.sleep'):
                _run_loop(s,Mock(),g,a)
            if expected: a.play.assert_called_once_with(expected)
            else: a.play.assert_not_called()

    def test_run_closes_audio_on_quit_interrupt_and_exception(self):
        for error in (None, KeyboardInterrupt(), ValueError('render')):
            backend=Mock(ready=True); s=Mock()
            with patch('curses.curs_set'),patch('curses.set_escdelay'),patch('tink_snake.ui.Renderer'), \
                 patch('tink_snake.ui._run_loop', side_effect=error),patch('arcade_common.audio._make_backend',return_value=backend):
                if error:
                    with self.assertRaises(type(error)): run(s)
                else: run(s)
            backend.close.assert_called_once()

    def test_cli_help_flags_nonterminal_and_error_after_wrapper(self):
        with redirect_stdout(io.StringIO()) as out, self.assertRaises(SystemExit) as result:
            main(['--help'])
        self.assertEqual(result.exception.code,0)
        for flag in ('--seed','--no-color','--no-sound'): self.assertIn(flag,out.getvalue())
        with patch('sys.stdin.isatty',return_value=False),redirect_stderr(io.StringIO()) as out:
            self.assertEqual(main([]),1)
        self.assertIn('interactive terminal',out.getvalue())
        with patch('sys.stdin.isatty',return_value=True),patch('sys.stdout.isatty',return_value=True), \
             patch('curses.wrapper',return_value='broken') as wrapper,redirect_stderr(io.StringIO()) as out:
            self.assertEqual(main(['--seed','42','--no-color','--no-sound']),0)
            wrapper.assert_called_once_with(run,42,True,True)
        self.assertIn('Snake audio: broken',out.getvalue())
