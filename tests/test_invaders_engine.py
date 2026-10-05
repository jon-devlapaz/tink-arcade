import math
import unittest
from tink_invaders.engine import (Game, Enemy, Shot, STEP, MAX_ELAPSED, WIDTH,
    SHIP_Y, MARCH_INTERVAL, ATTACK_INTERVAL, MAX_ENEMY_SHOTS, MOVE_INTERVAL)
from scripts.replay_invaders import replay, SEED, STEP_LIMIT


class EngineTests(unittest.TestCase):
    def playing(self):
        game = Game(7)
        self.assertEqual(game.start_or_fire(), 'start')
        self.assertIsNone(game.player_shot)
        return game

    def test_formations_and_partial_clear(self):
        g = self.playing()
        self.assertEqual(len(g.enemies), 18)
        g.player_shot = Shot(10, 6.1)
        g.advance(STEP)
        self.assertEqual((len(g.enemies), g.score, g.wave), (17, 10, 0))
        g.advance(STEP)
        self.assertEqual(g.score, 10)

    def test_reversal_descends_and_keeps_bounds(self):
        g = self.playing()
        g.enemies = [Enemy(0, 0, WIDTH - 2, 2), Enemy(1, 1, 10, 4)]
        g.march_timer = MARCH_INTERVAL - STEP
        g.advance(STEP)
        self.assertEqual([(e.x, e.y) for e in g.enemies], [(58, 3), (10, 5)])
        self.assertEqual(g.direction, -1)
        g.enemies = [Enemy(0, 0, 1, 2)]
        g.march_timer = MARCH_INTERVAL - STEP
        g.advance(STEP)
        self.assertEqual((g.enemies[0].x, g.enemies[0].y, g.direction), (1, 3, 1))

    def test_only_surviving_bottom_enemies_fire(self):
        g = self.playing()
        bottom = g.bottom_shooters()
        self.assertEqual({e.row for e in bottom}, {2})
        g.enemies.remove(next(e for e in bottom if e.column == 0))
        self.assertEqual(next(e for e in g.bottom_shooters() if e.column == 0).row, 1)
        allowed = {(e.x, e.y + 1) for e in g.bottom_shooters()}
        g.attack_timer = ATTACK_INTERVAL - STEP
        g.advance(STEP)
        self.assertIn((g.enemy_shots[0].x, g.enemy_shots[0].y), allowed)

    def test_input_and_enemy_fire_limits(self):
        g = self.playing()
        self.assertTrue(g.move(1))
        for _ in range(100):
            self.assertFalse(g.move(1))
        self.assertEqual(g.ship, 31)
        self.assertEqual(g.start_or_fire(), 'fire')
        for _ in range(100):
            self.assertIsNone(g.start_or_fire())
        g.player_shot = None
        self.assertIsNone(g.start_or_fire())
        g.enemy_shots = [Shot(1, 1) for _ in range(MAX_ENEMY_SHOTS)]
        g.attack_timer = ATTACK_INTERVAL - STEP
        g.advance(STEP)
        self.assertEqual(len(g.enemy_shots), MAX_ENEMY_SHOTS)
        g.ship, g.move_cooldown = 58, 0
        self.assertFalse(g.move(1))
        g.ship = 1
        self.assertFalse(g.move(-1))

    def test_swept_player_collision_hits_only_first_target(self):
        g = self.playing()
        g.enemies = [Enemy(0, 0, 10, 6), Enemy(1, 0, 10, 6)]
        g.player_shot = Shot(10, 6.2)
        g.advance(STEP)
        self.assertEqual((len(g.enemies), g.score), (1, 10))
        self.assertIsNone(g.player_shot)

    def test_shot_collision_sweeps_marching_and_descending_enemy(self):
        g = self.playing()
        g.enemies = [Enemy(0, 0, 10, 6), Enemy(1, 1, 20, 4)]
        g.player_shot = Shot(9, 6)
        g.march_timer = MARCH_INTERVAL - STEP
        g.advance(STEP)
        self.assertEqual(g.score, 10)
        self.assertEqual(len(g.enemies), 1)
        g = self.playing()
        g.enemies = [Enemy(0, 0, 58, 6), Enemy(1, 1, 20, 4)]
        g.player_shot = Shot(58, 6.2)
        g.march_timer = MARCH_INTERVAL - STEP
        g.advance(STEP)
        self.assertEqual(g.score, 10)
        self.assertEqual(len(g.enemies), 1)

    def test_opposing_shots_pass_through(self):
        g = self.playing()
        g.player_shot, g.enemy_shots = Shot(30, 10), [Shot(30, 9.9)]
        g.advance(STEP)
        self.assertIsNotNone(g.player_shot)
        self.assertEqual(len(g.enemy_shots), 1)

    def test_multiple_hits_lose_one_life_and_preserve_survivors(self):
        g = self.playing()
        g.enemies.pop(); g.score = 10
        g.enemy_shots = [Shot(g.ship, SHIP_Y - .05), Shot(g.ship, SHIP_Y - .1)]
        g.advance(STEP)
        self.assertEqual((g.lives, g.state, g.score, len(g.enemies)), (2, 'ready', 10, 17))
        self.assertEqual(g.enemy_shots, [])
        self.assertIsNone(g.player_shot)
        self.assertEqual(g.ship, 30)
        self.assertTrue(all(e.x == 10 + 7 * e.column and e.y == 2 + 2 * e.row for e in g.enemies))
        self.assertEqual((g.accumulator, g.march_timer, g.attack_timer, g.move_cooldown, g.fire_cooldown), (0, 0, 0, 0, 0))

    def test_enemy_reaching_ship_row_costs_one_life(self):
        g = self.playing()
        g.enemies[0].y = SHIP_Y
        g.enemy_shots = [Shot(g.ship, SHIP_Y)]
        g.advance(STEP)
        self.assertEqual((g.lives, g.state), (2, 'ready'))

    def test_simultaneous_last_enemy_and_ship_hit(self):
        for wave in range(3):
            for lives in (1, 2):
                with self.subTest(wave=wave, lives=lives):
                    g = self.playing(); g.wave, g.lives = wave, lives
                    g.enemies = [Enemy(0, 0, 10, 5)]
                    g.player_shot = Shot(10, 5.1)
                    g.enemy_shots = [Shot(g.ship, SHIP_Y - .01)]
                    g.advance(STEP)
                    self.assertEqual((g.lives, g.score), (lives - 1, 10))
                    self.assertEqual(g.state, 'lost' if lives == 1 else ('won' if wave == 2 else 'ready'))
                    self.assertEqual(g.wave, wave if lives == 1 or wave == 2 else wave + 1)

    def test_clear_each_wave_requires_all_enemies(self):
        g = self.playing()
        for wave, next_count in ((0, 6), (1, 10), (2, 0)):
            self.assertEqual(g.wave, wave)
            g.enemies = [Enemy(0, 0, 10, 5)]
            g.player_shot = Shot(10, 5.1)
            g.advance(STEP)
            self.assertEqual(len(g.enemies), next_count)
            self.assertEqual(g.lives, 3)
            if wave < 2:
                self.assertEqual(g.state, 'ready'); g.start_or_fire()
        self.assertEqual(g.state, 'won')
        frozen = g.snapshot()
        g.move(1); g.start_or_fire(); g.advance(1)
        self.assertEqual(g.snapshot(), frozen)

    def test_restart_and_seed_repeatability(self):
        baseline = Game(7).snapshot()
        for state in ('ready', 'playing', 'won', 'lost'):
            g = self.playing(); g.state = state; g.score = 100; g.lives = 1
            g.restart(); self.assertEqual(g.snapshot(), baseline)
        a, b = self.playing(), self.playing()
        for _ in range(500):
            for g in (a, b):
                g.start_or_fire(); g.move(1); g.advance(STEP)
            self.assertEqual(a.snapshot(), b.snapshot())

    def test_invalid_negative_and_delayed_time(self):
        g = self.playing()
        before = g.snapshot(); g.advance(-100)
        self.assertEqual(g.snapshot(), before)
        for value in (math.inf, -math.inf, math.nan):
            with self.assertRaises(ValueError): g.advance(value)
        a = self.playing(); a.advance(1000)
        b = self.playing(); b.advance(MAX_ELAPSED)
        self.assertEqual(a.snapshot(), b.snapshot())

    def test_full_legal_replay(self):
        game, steps = replay()
        self.assertLess(steps, STEP_LIMIT)
        self.assertEqual((game.state, game.wave, game.score, len(game.enemies)), ('won', 2, 340, 0))
        self.assertGreater(game.lives, 0)
        self.assertEqual(SEED, 7)
        print(f'Legal replay: seed={SEED}, steps={steps}/{STEP_LIMIT}, score={game.score}, lives={game.lives}')
