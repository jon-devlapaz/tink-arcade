import curses
import io
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import Mock, patch
from tink_pong.engine import Game
from tink_pong.ui import Renderer, handle_key, run, _run_loop
from tink_pong.__main__ import main
from arcade_common.audio import KeyboardAudio, SOUND_DIR


class PongUITests(unittest.TestCase):
    def test_bindings_and_action_cues(self):
        for direction,keys in ((-1,(curses.KEY_UP,ord('w'),ord('W'))),(1,(curses.KEY_DOWN,ord('s'),ord('S')))):
            for key in keys:
                g=Game();a=Mock();self.assertTrue(handle_key(g,key,a))
                self.assertEqual(g.player,10+direction*1.5);a.play.assert_not_called()
        g=Game();a=Mock();handle_key(g,32,a);self.assertEqual(g.state,'playing');a.play.assert_called_with('switch')
        a.reset_mock();handle_key(g,32,a);a.play.assert_not_called()
        for key in 'pP':
            handle_key(g,ord(key),a);a.stop.assert_called();a.play.assert_called_with('switch')
        for key in 'rR':
            handle_key(g,ord(key),a);self.assertEqual(g.snapshot(),Game().snapshot())
        for key in 'mM': handle_key(g,ord(key),a)
        self.assertEqual(a.toggle.call_count,2)
        for key in (ord('q'),ord('Q'),3):self.assertFalse(handle_key(g,key,a))
        g.state='won';a.reset_mock();handle_key(g,ord('p'),a);a.play.assert_not_called()

    def test_palette_and_monochrome(self):
        for colors,expected in ((256,[(233,230),(29,230),(240,230),(245,230)]),(8,[(0,7),(6,7),(0,7),(0,7)])):
            with patch('curses.has_colors',return_value=True),patch('curses.start_color'),patch('curses.COLORS',colors,create=True),patch('curses.COLOR_PAIRS',8,create=True),patch('curses.init_pair') as pairs,patch('curses.color_pair',side_effect=lambda n:n):
                Renderer(Mock());self.assertEqual([c.args[1:] for c in pairs.call_args_list],expected)
        with patch('curses.has_colors') as colors:Renderer(Mock(),True);colors.assert_not_called()

    def test_layout_all_states_sizes_and_bounds(self):
        for rows,cols in ((30,80),(35,100)):
            for state in ('waiting','playing','paused','won','lost'):
                g=Game();g.state='playing' if state=='paused' else state;g.paused=state=='paused'
                s=Mock();s.getmaxyx.return_value=(rows,cols);Renderer(s,True).draw(g,False,'key sound on [M]')
                calls=[c.args for c in s.addnstr.call_args_list]
                for y,x,text,width,attr in calls:
                    self.assertTrue(text.isascii());self.assertTrue(0<=y<rows);self.assertTrue(0<=x and x+len(text)<=cols)
                texts=[c[2] for c in calls]
                self.assertIn('o',texts);self.assertIn('key sound on [M]',texts)
                self.assertIn({'waiting':'SPACE to serve','playing':'RALLY','paused':'PAUSED / P resume','won':'YOU WIN / R restart / Q quit','lost':'COMPUTER WINS / R restart / Q quit'}[state],texts)
                self.assertIn('YOU  0     FIRST TO 7     COMPUTER  0',texts)
                self.assertEqual(sum(t=='|' and bool(c[4]&curses.A_REVERSE) for t,c in zip(texts,calls)),10)

    def test_small_and_clipping_errors(self):
        s=Mock();s.getmaxyx.return_value=(12,40);r=Renderer(s,True);r.draw(Game(),True,'key sound off')
        self.assertIn('Resize terminal to at least 80 x 30.',[c.args[2] for c in s.addnstr.call_args_list])
        s.reset_mock();s.getmaxyx.return_value=(5,8);r.text(4,7,'x');r.text(-1,0,'x');s.addnstr.assert_not_called()
        r.text(2,-2,'abcdef');s.addnstr.assert_called_with(2,0,'cdef',8,0)
        s.addnstr.side_effect=curses.error();r.text(1,0,'x');s.refresh.side_effect=curses.error();r._refresh()
        s.addnstr.side_effect=ValueError('bug')
        with self.assertRaises(ValueError):r.text(1,0,'x')

    def test_resize_and_transition_frames_discard_elapsed(self):
        for paused in (False,True):
            g=Game();g.launch();g.paused=paused;before=g.snapshot()
            s=Mock();s.getmaxyx.side_effect=[(12,40),(12,40),(30,80),(30,80)]
            s.getch.side_effect=[ord('r'),ord('p'),ord('w'),32,-1,ord('m'),-1,-1,ord('q')]
            a=Mock()
            with patch('tink_pong.ui.time.monotonic',side_effect=[0,1,1,20,20,40,40,41]),patch('tink_pong.ui.time.sleep'):
                _run_loop(s,Mock(),g,a)
            self.assertEqual(g.snapshot(),before);a.stop.assert_called_once();a.toggle.assert_called_once();self.assertEqual(a.tick.call_count,3)
        for key in (' ','p','r'):
            g=Game()
            if key!=' ':g.launch()
            s=Mock();s.getmaxyx.return_value=(30,80);s.getch.side_effect=[ord(key),-1,ord('q')]
            with patch('tink_pong.ui.time.monotonic',side_effect=[0,30,30,31]),patch('tink_pong.ui.time.sleep'):
                _run_loop(s,Mock(),g,Mock())
            self.assertEqual((g.x,g.y,g.computer),(30,10,10))

    def test_repeated_noop_input_does_not_discard_rally_time(self):
        expected = Game()
        expected.launch()
        for _ in range(60):
            expected.advance(1 / 60)
        for key in (' ', 'x', 'm'):
            with self.subTest(key=key):
                game = Game()
                game.launch()
                screen = Mock()
                screen.getmaxyx.return_value = (30, 80)
                screen.getch.side_effect = [value for _ in range(60) for value in (ord(key), -1)] + [ord('q')]
                times = [0] + [value for frame in range(1, 61) for value in (frame / 60, frame / 60)] + [61 / 60]
                with patch('tink_pong.ui.time.monotonic', side_effect=times), patch('tink_pong.ui.time.sleep'):
                    _run_loop(screen, Mock(), game, Mock())
                for field in ('x', 'y', 'player', 'computer', 'accumulator'):
                    self.assertAlmostEqual(getattr(game, field), getattr(expected, field), msg=field)
                self.assertEqual(game.state, 'playing')
                self.assertFalse(game.paused)

    def test_loop_routes_contact_point_loss_and_silent_wall(self):
        for scenario,expected in (('paddle','move'),('point','clear'),('loss','over'),('wall',None)):
            g=Game();g.launch();g.x=.1;g.y=1;g.vx=-24;g.vy=0
            if scenario=='paddle':g.x=1.1;g.y=10
            if scenario=='loss':g.computer_score=6
            if scenario=='wall':g.x=30;g.y=.01;g.vx=0;g.vy=-24
            s=Mock();s.getmaxyx.return_value=(30,80);s.getch.side_effect=[-1,ord('q')];a=Mock()
            with patch('tink_pong.ui.time.monotonic',side_effect=[0,.02,.02,.03]),patch('tink_pong.ui.time.sleep'):
                _run_loop(s,Mock(),g,a)
            if expected:a.play.assert_called_once_with(expected)
            else:a.play.assert_not_called()

    def test_audio_mute_restart_disabled_unavailable_cleanup(self):
        backend=Mock(ready=True)
        with patch('arcade_common.audio._make_backend',return_value=backend):
            with KeyboardAudio() as a:
                g=Game();handle_key(g,32,a);a.tick();backend.play.assert_called_with(SOUND_DIR/'mx-blue.wav')
                handle_key(g,ord('m'),a);handle_key(g,ord('r'),a);a.tick();self.assertTrue(a.muted);self.assertEqual(backend.play.call_count,1)
                handle_key(g,ord('m'),a);a.tick();self.assertEqual(backend.play.call_count,2)
                backend.tick.side_effect=OSError('broken');a.tick();self.assertIn('unavailable',a.status)
                handle_key(g,32,a);self.assertEqual(g.state,'playing')
            backend.close.assert_called_once()
        with patch('arcade_common.audio._make_backend') as factory:
            with KeyboardAudio(False) as a:
                handle_key(Game(),ord('m'),a);self.assertEqual(a.status,'key sound off')
            factory.assert_not_called()
        for error in (None,KeyboardInterrupt(),ValueError('render')):
            backend=Mock(ready=True)
            with patch('curses.curs_set'),patch('curses.set_escdelay'),patch('tink_pong.ui.Renderer'),patch('tink_pong.ui._run_loop',side_effect=error),patch('arcade_common.audio._make_backend',return_value=backend):
                if error:
                    with self.assertRaises(type(error)):run(Mock())
                else:run(Mock())
            backend.close.assert_called_once()

    def test_cli_flags_help_and_nonterminal(self):
        with redirect_stdout(io.StringIO()) as out,self.assertRaises(SystemExit) as result:main(['--help'])
        self.assertEqual(result.exception.code,0)
        for flag in ('--no-color','--no-sound'):self.assertIn(flag,out.getvalue())
        with patch('sys.stdin.isatty',return_value=False),redirect_stderr(io.StringIO()) as out:self.assertEqual(main([]),1)
        self.assertIn('interactive terminal',out.getvalue())
        with patch('sys.stdin.isatty',return_value=True),patch('sys.stdout.isatty',return_value=True),patch('curses.wrapper',return_value='broken') as wrapper,redirect_stderr(io.StringIO()) as out:
            self.assertEqual(main(['--no-color','--no-sound']),0);wrapper.assert_called_once_with(run,True,True)
        self.assertIn('Pong audio: broken',out.getvalue())
