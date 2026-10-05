"""Deterministic rules. Coordinates are terminal cells; time advances in fixed ticks."""
from dataclasses import dataclass
import math
import random

WIDTH, HEIGHT = 70, 22
STEP = 1 / 60
PLAYER_Y = HEIGHT - 2


@dataclass
class Enemy:
    home_x: float
    home_y: float
    x: float
    y: float
    dive: float | None = None
    target: float = 0
    origin_x: float = 0
    origin_y: float = 0


@dataclass
class Bullet:
    x: float
    y: float
    vy: float
    hostile: bool = False


class Game:
    def __init__(self, seed=None):
        self.seed = seed
        self.restart()

    def restart(self):
        self.rng = random.Random(self.seed)
        self.tick = 0
        self.player_x = WIDTH / 2
        self.lives = 3
        self.score = 0
        self.wave = 0
        self.paused = False
        self.game_over = False
        self.protection = 0.0
        self.cooldown = 0.0
        self.bullets = []
        self.next_wave()

    def next_wave(self):
        self.wave += 1
        self.wave_time = 0.0
        self.bullets.clear()
        self.protection = max(self.protection, 1.0)
        self.enemies = [Enemy(11 + col * 7, 2 + row * 2, 11 + col * 7, 2 + row * 2)
                        for row in range(min(5, 2 + self.wave)) for col in range(8)]
        self.dive_timer = 1.5
        self.fire_timer = 1.0

    def move(self, direction):
        if not self.paused and not self.game_over:
            self.player_x = min(WIDTH - 2, max(1, self.player_x + direction * 2))

    def fire(self):
        if not self.paused and not self.game_over and self.cooldown <= 0:
            self.bullets.append(Bullet(self.player_x, PLAYER_Y - 1, -32))
            self.cooldown = .18

    def hit(self):
        if self.protection > 0 or self.game_over:
            return
        self.lives -= 1
        self.protection = 2.0
        self.player_x = WIDTH / 2
        if self.lives == 0:
            self.game_over = True

    def step(self):
        if self.paused or self.game_over:
            return
        self.tick += 1
        self.wave_time += STEP
        self.protection = max(0, self.protection - STEP)
        self.cooldown = max(0, self.cooldown - STEP)
        speed = min(2.0, 1 + .12 * (self.wave - 1))
        sway = math.sin(self.wave_time * speed) * 4
        self.dive_timer -= STEP
        self.fire_timer -= STEP
        if self.dive_timer <= 0:
            candidates = [e for e in self.enemies if e.dive is None]
            if candidates:
                enemy = self.rng.choice(candidates)
                enemy.dive = 0.0
                enemy.target = self.player_x
                enemy.origin_x, enemy.origin_y = enemy.x, enemy.y
            self.dive_timer = max(.35, 1.8 - self.wave * .12)
        for enemy in self.enemies:
            if enemy.dive is None:
                enemy.x, enemy.y = enemy.home_x + sway, enemy.home_y
            else:
                enemy.dive += STEP * speed / 3
                t = enemy.dive
                if t >= 1:
                    enemy.dive = None
                    enemy.x, enemy.y = enemy.home_x + sway, enemy.home_y
                elif t <= .5:
                    k = t * 2
                    enemy.x = enemy.origin_x + (enemy.target - enemy.origin_x) * k
                    enemy.y = enemy.origin_y + (PLAYER_Y - enemy.origin_y) * k
                else:
                    k = (t - .5) * 2
                    enemy.x = enemy.target + (enemy.home_x + sway - enemy.target) * k
                    enemy.y = PLAYER_Y + (enemy.home_y - PLAYER_Y) * k
            if abs(enemy.x - self.player_x) <= 1.5 and abs(enemy.y - PLAYER_Y) <= .8:
                self.hit()
        if self.fire_timer <= 0 and self.enemies:
            enemy = self.rng.choice(self.enemies)
            self.bullets.append(Bullet(enemy.x, enemy.y + 1, 9 + min(self.wave, 10), True))
            self.fire_timer = max(.18, 1.0 - self.wave * .065)
        remaining = []
        for bullet in self.bullets:
            old_y = bullet.y
            bullet.y += bullet.vy * STEP
            low, high = sorted((old_y, bullet.y))
            if bullet.hostile:
                if abs(bullet.x - self.player_x) <= 1.3 and low - .5 <= PLAYER_Y <= high + .5:
                    self.hit()
                    continue
            else:
                # The first enemy along the shot's path receives the hit.
                targets = [e for e in self.enemies
                           if abs(e.x - bullet.x) <= 1.3 and low - .5 <= e.y <= high + .5]
                if targets:
                    target = max(targets, key=lambda e: e.y)
                    self.score += 150 if target.dive is not None else 100
                    self.enemies.remove(target)
                    continue
            if 0 <= bullet.y < HEIGHT:
                remaining.append(bullet)
        self.bullets = remaining
        if not self.enemies and not self.game_over:
            self.next_wave()


class Clock:
    """Drop long stalls instead of simulating unseen time. Retain fractional ticks."""
    def __init__(self):
        self.remainder = 0.0

    def advance(self, game, elapsed, blocked=False):
        if blocked or game.paused or game.game_over or elapsed > .1 or elapsed < 0:
            self.remainder = 0.0
            return
        self.remainder += elapsed
        while self.remainder + 1e-12 >= STEP:
            game.step()
            self.remainder -= STEP
