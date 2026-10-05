import math
import unittest
from tink_pong.engine import Game, SPEED, STEP, HEIGHT, PADDLE_HEIGHT
from scripts.pong_replay import play


class PongEngineTests(unittest.TestCase):
    def test_new_match_serve_alternation_and_restart(self):
        g = Game()
        self.assertEqual((g.state, g.player, g.computer, g.x, g.y), ('waiting',10,10,30,10))
        before = g.snapshot(); self.assertEqual(g.advance(5), []); self.assertEqual(g.snapshot(), before)
        self.assertTrue(g.launch()); self.assertFalse(g.launch()); self.assertGreater(g.vx,0); self.assertGreater(g.vy,0)
        g.x,g.y,g.vx,g.vy=59.9,1,24,0
        self.assertEqual(g.advance(STEP),['clear'])
        self.assertEqual((g.player_score,g.computer_score,g.state,g.player,g.computer),(1,0,'waiting',10,10))
        self.assertLess(g.vx,0); self.assertLess(g.vy,0)
        g.launch(); g.x,g.y,g.vx,g.vy=.1,1,-24,0; g.advance(STEP)
        self.assertGreater(g.vx,0); self.assertGreater(g.vy,0)
        g.restart(); self.assertEqual(g.snapshot(),Game().snapshot())

    def test_player_bounds_and_pause_freeze(self):
        g=Game()
        g.move(-1); self.assertEqual(g.player,8.5)
        for _ in range(100): g.move(-1)
        self.assertEqual(g.player,2.5)
        for _ in range(100): g.move(1)
        self.assertEqual(g.player,17.5)
        g.launch(); g.toggle_pause(); before=g.snapshot()
        g.move(-1); g.advance(.1); self.assertFalse(g.launch()); self.assertEqual(g.snapshot(),before)
        g.toggle_pause(); g.advance(STEP); self.assertNotEqual(g.snapshot(),before)

    def test_computer_follows_current_height_only_at_bounded_speed(self):
        g=Game(); g.y=2; g.launch(); g.advance(STEP)
        self.assertAlmostEqual(g.computer,10-6*STEP)
        g.y=19; before=g.computer; g.advance(STEP)
        self.assertAlmostEqual(g.computer-before,6*STEP)
        for _ in range(1000):
            g.y=0; g.x=30; g.vx=0; g.vy=0; g.advance(STEP)
        self.assertEqual(g.computer,2.5)

    def test_delayed_frames_bounded_and_invalid_elapsed(self):
        a,b=Game(),Game(); a.launch(); b.launch(); a.advance(60); b.advance(.1)
        self.assertEqual(a.snapshot(),b.snapshot())
        for value in (-1,math.nan,math.inf):
            with self.assertRaises(ValueError): a.advance(value)
        c=Game(); c.launch(); c.advance(STEP/2); self.assertEqual(c.x,30)
        c.advance(STEP/2); self.assertGreater(c.x,30)

    def test_paddle_returns_speed_and_contact_angle(self):
        for left in (True,False):
            for offset in (-2.5,-1,0,1,2.5):
                g=Game();g.launch(); g.x=1.1 if left else 58.9
                g.player=g.computer=10;g.y=10+offset;g.vx=-24 if left else 24;g.vy=0
                # Direct collision step holds paddles fixed to test exact contact geometry.
                cues=g._step(STEP)
                self.assertEqual(cues,['move']);self.assertEqual(g.vx>0,left)
                self.assertAlmostEqual(math.hypot(g.vx,g.vy),SPEED)
                self.assertLessEqual(abs(math.atan2(g.vy,abs(g.vx))),math.pi/3+1e-9)
                self.assertNotEqual(g.vy,0)

    def test_swept_contacts_walls_misses_and_corner(self):
        g=Game();g.launch();g.x=2;g.y=10;g.vx=-2400;g.vy=0
        self.assertIn('move',g._step(STEP));self.assertGreater(g.vx,0)
        for y,vy in ((.01,-24),(19.99,24)):
            g=Game();g.launch();g.y=y;g.vx=0;g.vy=vy
            self.assertEqual(g._step(STEP),[]);self.assertLess(g.vy*vy,0)
            self.assertTrue(0<=g.y<=20)
        g=Game();g.launch();g.player=2.5;g.x=1.1;g.y=.1;g.vx=-24;g.vy=-24
        self.assertEqual(g._step(STEP),['move']);self.assertGreater(g.vx,0);self.assertGreater(g.vy,0)
        g=Game();g.launch();g.x=.1;g.y=1;g.vx=-24;g.vy=0
        self.assertEqual(g.advance(.1),['clear']); self.assertEqual(g.computer_score,1)
        before=g.snapshot();g.advance(10);self.assertEqual(g.snapshot(),before)

    def test_seven_ends_match_and_all_motion_stops(self):
        for player in (True,False):
            g=Game()
            for point in range(7):
                g.launch();g.x=59.9 if player else .1;g.y=1;g.vx=24 if player else -24;g.vy=0
                cues=g.advance(.1)
                self.assertEqual(cues,['over'] if not player and point==6 else ['clear'])
            self.assertEqual(g.state,'won' if player else 'lost')
            before=g.snapshot();g.move(1);g.advance(.1)
            self.assertFalse(g.launch());self.assertFalse(g.toggle_pause());self.assertEqual(g.snapshot(),before)

    def test_ordinary_legal_player_win_and_idle_loss_replays(self):
        for player,expected in ((True,'won'),(False,'lost')):
            g,frames=play(player)
            self.assertEqual(g.state,expected);self.assertLess(frames,120000)
            self.assertEqual(max(g.player_score,g.computer_score),7)
