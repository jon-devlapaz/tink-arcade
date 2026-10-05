"""Fixed-step Invaders rules. Positions and speeds use terminal cells and seconds."""
from dataclasses import asdict, dataclass
import math
import random

WIDTH, HEIGHT, SHIP_Y = 60, 20, 18
STEP, MAX_ELAPSED, EPS = 1 / 60, .1, 1e-9
MOVE_INTERVAL, FIRE_INTERVAL = .055, .22
MARCH_INTERVAL, ATTACK_INTERVAL = .7, 1.1
PLAYER_SPEED, ENEMY_SPEED, MAX_ENEMY_SHOTS = 32, 8, 3
NAMES = ('Ranks', 'Wings', 'Islands')
PATTERNS = (('######', '######', '######'),
            ('#....#', '.#..#.', '..##..'),
            ('##..##', '..##..', '##..##'))


@dataclass
class Enemy:
    row: int
    column: int
    x: int
    y: int


@dataclass
class Shot:
    x: int
    y: float


class Game:
    def __init__(self, seed=None):
        self.seed = seed
        self.restart()

    def restart(self):
        self.random = random.Random(self.seed)
        self.wave, self.score, self.lives = 0, 0, 3
        self.events = []
        self._formation()
        self._ready()

    def _formation(self):
        self.enemies = [Enemy(row, col, 10 + col * 7, 2 + row * 2)
                        for row, pattern in enumerate(PATTERNS[self.wave])
                        for col, mark in enumerate(pattern) if mark == '#']

    def _ready(self):
        self.state, self.ship, self.direction = 'ready', WIDTH // 2, 1
        self.player_shot, self.enemy_shots = None, []
        self.accumulator = self.move_cooldown = self.fire_cooldown = 0.
        self.march_timer = self.attack_timer = 0.
        for enemy in self.enemies:
            enemy.x, enemy.y = 10 + enemy.column * 7, 2 + enemy.row * 2

    def start_or_fire(self):
        if self.state == 'ready':
            self.state = 'playing'
            return 'start'
        if self.state == 'playing' and self.player_shot is None and self.fire_cooldown <= EPS:
            self.player_shot = Shot(self.ship, SHIP_Y - 1)
            self.fire_cooldown = FIRE_INTERVAL
            self.events.append('rotate')
            return 'fire'
        return None

    def move(self, direction):
        if self.state != 'playing' or self.move_cooldown > EPS or direction == 0:
            return False
        destination = min(WIDTH - 2, max(1, self.ship + (1 if direction > 0 else -1)))
        if destination == self.ship:
            return False
        self.ship = destination
        self.move_cooldown = MOVE_INTERVAL
        self.events.append('move')
        return True

    def bottom_shooters(self):
        return [e for e in self.enemies
                if not any(other.column == e.column and other.y > e.y for other in self.enemies)]

    def take_events(self):
        events, self.events = self.events, []
        return events

    def snapshot(self):
        return dict(wave=self.wave, score=self.score, lives=self.lives, state=self.state,
                    ship=self.ship, direction=self.direction,
                    enemies=[asdict(e) for e in self.enemies],
                    player_shot=asdict(self.player_shot) if self.player_shot else None,
                    enemy_shots=[asdict(s) for s in self.enemy_shots],
                    accumulator=self.accumulator, move_cooldown=self.move_cooldown,
                    fire_cooldown=self.fire_cooldown, march_timer=self.march_timer,
                    attack_timer=self.attack_timer)

    def advance(self, elapsed):
        if not math.isfinite(elapsed):
            raise ValueError('elapsed time must be finite')
        if self.state != 'playing':
            return
        self.accumulator += min(max(0, elapsed), MAX_ELAPSED)
        while self.accumulator + EPS >= STEP and self.state == 'playing':
            self.accumulator = max(0, self.accumulator - STEP)
            self._step()

    def _step(self):
        self.move_cooldown = max(0, self.move_cooldown - STEP)
        self.fire_cooldown = max(0, self.fire_cooldown - STEP)
        self.march_timer += STEP
        self.attack_timer += STEP
        previous = {(e.row, e.column): (e.x, e.y) for e in self.enemies}
        # March, resolve both kinds of damage, then apply life loss before progression.
        if self.march_timer + EPS >= MARCH_INTERVAL:
            self.march_timer -= MARCH_INTERVAL
            if any(not 1 <= e.x + self.direction <= WIDTH - 2 for e in self.enemies):
                self.direction *= -1
                for enemy in self.enemies:
                    enemy.y += 1
            else:
                for enemy in self.enemies:
                    enemy.x += self.direction
        damage = any(e.y >= SHIP_Y for e in self.enemies)
        shot = self.player_shot
        if shot:
            destination = shot.y - PLAYER_SPEED * STEP
            hits = []
            for enemy in self.enemies:
                old_x, old_y = previous[enemy.row, enemy.column]
                relative_travel = destination - shot.y - (enemy.y - old_y)
                contact = (old_y - shot.y) / relative_travel
                x_at_contact = old_x + (enemy.x - old_x) * contact
                if -EPS <= contact <= 1 + EPS and abs(x_at_contact - shot.x) <= 1 + EPS:
                    hits.append((contact, enemy.row, enemy.column, enemy))
            if hits:
                target = min(hits, key=lambda hit: hit[:3])[3]
                self.enemies.remove(target)
                self.score += 10
                self.player_shot = None
            elif destination < 0:
                self.player_shot = None
            else:
                shot.y = destination
        survivors = []
        for shot in self.enemy_shots:
            destination = shot.y + ENEMY_SPEED * STEP
            if abs(shot.x - self.ship) <= 1 and shot.y - EPS <= SHIP_Y <= destination + EPS:
                damage = True
            elif destination < HEIGHT:
                shot.y = destination
                survivors.append(shot)
        self.enemy_shots = survivors
        if damage:
            self.lives -= 1
            self.events.append('over')
            self._ready()
            if not self.lives:
                self.state = 'lost'
                return
        if not self.enemies:
            self.events.append('clear')
            if self.wave == 2:
                self.state = 'won'
                self.player_shot, self.enemy_shots = None, []
            else:
                self.wave += 1
                self._formation()
                self._ready()
            return
        if damage:
            return
        if self.attack_timer + EPS >= ATTACK_INTERVAL:
            self.attack_timer -= ATTACK_INTERVAL
            if len(self.enemy_shots) < MAX_ENEMY_SHOTS:
                enemy = self.random.choice(self.bottom_shooters())
                self.enemy_shots.append(Shot(enemy.x, enemy.y + 1))
