import curses
from dataclasses import asdict
import subprocess
import sys
import unittest
from tink_galaga.engine import Bullet, Clock, Enemy, Game, HEIGHT, PLAYER_Y, STEP, WIDTH
from tink_galaga.ui import handle_key


class GalagaTests(unittest.TestCase):
    def test_seed_repeats_inputs_and_enemy_choices(self):
        a, b = Game(12), Game(12)
        for tick in range(700):
            for game in (a, b):
                if tick % 20 == 0:
                    game.move(-1 if tick % 40 else 1)
                    game.fire()
                game.step()
            self.assertEqual([asdict(e) for e in a.enemies], [asdict(e) for e in b.enemies])
            self.assertEqual(a.bullets, b.bullets)
        self.assertEqual((a.score, a.lives), (b.score, b.lives))

    def test_movement_bounds(self):
        game = Game(1)
        for _ in range(100):
            game.move(-1)
        self.assertEqual(game.player_x, 1)
        for _ in range(100):
            game.move(1)
        self.assertEqual(game.player_x, WIDTH - 2)

    def test_shot_kills_only_first_enemy_in_path(self):
        game = Game(1)
        game.enemies = [Enemy(20, 4, 20, 4), Enemy(20, 8, 20, 8)]
        game.bullets = [Bullet(20, 10, -600)]
        game.step()
        self.assertEqual(game.score, 100)
        self.assertEqual([e.home_y for e in game.enemies], [4])
        self.assertEqual(game.bullets, [])

    def test_missed_shot_does_not_score(self):
        game = Game(1)
        game.bullets = [Bullet(0, 0, -32)]
        game.step()
        self.assertEqual(game.score, 0)
        self.assertEqual(game.bullets, [])

    def test_fire_cooldown(self):
        game = Game(1)
        game.fire()
        game.fire()
        self.assertEqual(len(game.bullets), 1)
        for _ in range(12):
            game.step()
        game.fire()
        self.assertEqual(len(game.bullets), 2)

    def test_damage_and_protection(self):
        game = Game(1)
        game.protection = 0
        game.bullets = [Bullet(game.player_x, PLAYER_Y - 1, 120, True) for _ in range(4)]
        game.step()
        self.assertEqual(game.lives, 2)
        self.assertEqual(game.bullets, [])
        game.hit()
        self.assertEqual(game.lives, 2)
        game.protection = 0
        game.hit()
        self.assertEqual(game.lives, 1)

    def test_enemy_contact_hits_player(self):
        game = Game(1)
        game.protection = 0
        game.enemies = [Enemy(35, 3, 35, PLAYER_Y, .49, 35, 35, 3)]
        game.step()
        self.assertEqual(game.lives, 2)

    def test_dive_returns_to_formation(self):
        game = Game(1)
        enemy = game.enemies[0]
        enemy.dive, enemy.target = .99, 35
        game.step()
        game.step()
        self.assertIsNone(enemy.dive)
        self.assertEqual(enemy.y, enemy.home_y)

    def test_enemy_dives_and_fires(self):
        game = Game(1)
        for _ in range(100):
            game.step()
        self.assertTrue(any(e.dive is not None for e in game.enemies))
        self.assertTrue(any(b.hostile for b in game.bullets))

    def test_wave_advances_and_clears_danger(self):
        game = Game(1)
        game.enemies = [Enemy(20, 4, 20, 4)]
        game.bullets = [Bullet(20, 5, -60), Bullet(35, 8, 8, True)]
        game.step()
        self.assertEqual(game.wave, 2)
        self.assertEqual(game.score, 100)
        self.assertEqual(len(game.enemies), 32)
        self.assertEqual(game.bullets, [])
        self.assertGreater(game.protection, 0)

    def test_higher_wave_has_faster_attacks(self):
        first, later = Game(1), Game(1)
        for _ in range(6):
            later.next_wave()
        for game in (first, later):
            game.fire_timer = game.dive_timer = 0
            game.step()
        self.assertLess(later.fire_timer, first.fire_timer)
        self.assertLess(later.dive_timer, first.dive_timer)
        self.assertGreater(later.bullets[0].vy, first.bullets[0].vy)

    def test_game_over_stops_and_restart_resets_seed(self):
        game = Game(1)
        for _ in range(3):
            game.protection = 0
            game.hit()
        self.assertTrue(game.game_over)
        game.step()
        game.fire()
        self.assertEqual(game.tick, 0)
        self.assertEqual(game.bullets, [])
        handle_key(game, ord('r'))
        self.assertEqual(game.enemies, Game(1).enemies)
        self.assertEqual((game.lives, game.score, game.wave), (3, 0, 1))

    def test_pause_blocks_time_and_input(self):
        game = Game(1)
        handle_key(game, ord('p'))
        handle_key(game, ord('a'))
        handle_key(game, ord(' '))
        Clock().advance(game, .05)
        self.assertEqual((game.tick, game.player_x, game.bullets), (0, WIDTH / 2, []))
        handle_key(game, ord('p'))
        game.step()
        self.assertEqual(game.tick, 1)

    def test_clock_frame_partition(self):
        a, b = Game(1), Game(1)
        ca, cb = Clock(), Clock()
        for _ in range(100):
            ca.advance(a, .01)
        for _ in range(20):
            cb.advance(b, .05)
        self.assertEqual(a.tick, 60)
        self.assertEqual(a.enemies, b.enemies)
        self.assertEqual(a.bullets, b.bullets)

    def test_stall_and_resize_do_not_catch_up(self):
        game, clock = Game(1), Clock()
        clock.advance(game, .008)
        clock.advance(game, 5)
        self.assertEqual(game.tick, 0)
        clock.advance(game, STEP)
        self.assertEqual(game.tick, 1)
        clock.advance(game, .08, blocked=True)
        clock.advance(game, STEP)
        self.assertEqual(game.tick, 2)

    def test_key_controls(self):
        game = Game(1)
        handle_key(game, curses.KEY_LEFT)
        self.assertEqual(game.player_x, WIDTH / 2 - 2)
        handle_key(game, ord('D'))
        handle_key(game, ord(' '))
        self.assertEqual(game.bullets[0].x, WIDTH / 2)
        for key in (ord('q'), ord('Q'), 3):
            self.assertFalse(handle_key(game, key))

    def test_help_and_non_terminal(self):
        result = subprocess.run([sys.executable, '-B', '-m', 'tink_galaga', '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('80 x 30', result.stdout)
        result = subprocess.run([sys.executable, '-B', '-m', 'tink_galaga'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('interactive terminal', result.stderr)


if __name__ == '__main__':
    unittest.main()
