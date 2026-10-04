"""Deterministic Snake rules, independent of the terminal and audio."""
import random
from collections import deque

WIDTH = HEIGHT = 20
RIGHT, DOWN, LEFT, UP = (1, 0), (0, 1), (-1, 0), (0, -1)
DIRECTIONS = (RIGHT, DOWN, LEFT, UP)


class Game:
    def __init__(self, seed=None):
        self.seed = seed
        self.best = 0
        self.restart()

    def restart(self):
        self.rng = random.Random(self.seed)
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = RIGHT
        self.turns = deque()
        self.foods = self.score = 0
        self.paused = self.game_over = self.complete = False
        self.elapsed = 0.0
        self.food = self._food()

    @property
    def interval(self):
        return max(75, 180 - 15 * (self.foods // 5)) / 1000

    def _food(self):
        occupied = set(self.snake)
        free = [(x, y) for y in range(HEIGHT) for x in range(WIDTH) if (x, y) not in occupied]
        return self.rng.choice(free) if free else None

    def turn(self, direction):
        if self.paused or self.game_over or self.complete or len(self.turns) == 2:
            return False
        previous = self.turns[-1] if self.turns else self.direction
        if direction not in DIRECTIONS or direction == previous or direction == (-previous[0], -previous[1]):
            return False
        self.turns.append(direction)
        return True

    def toggle_pause(self):
        if self.game_over or self.complete:
            return False
        self.paused = not self.paused
        self.turns.clear()
        return True

    def update(self, dt):
        """Advance at most once; return the most important audible event."""
        if self.paused or self.game_over or self.complete:
            return None
        self.elapsed += max(0.0, min(dt, self.interval))
        if self.elapsed + 1e-12 < self.interval:
            return None
        self.elapsed = max(0.0, self.elapsed - self.interval)
        turned = bool(self.turns)
        if turned:
            self.direction = self.turns.popleft()
        x, y = self.snake[0]
        dx, dy = self.direction
        head = (x + dx, y + dy)
        eating = head == self.food
        occupied = self.snake if eating else self.snake[:-1]
        if not (0 <= head[0] < WIDTH and 0 <= head[1] < HEIGHT) or head in occupied:
            self.game_over = True
            self.turns.clear()
            return 'over'
        self.snake.insert(0, head)
        if eating:
            self.foods += 1
            self.score += 10
            self.best = max(self.best, self.score)
            self.food = self._food()
            self.complete = self.food is None
            if self.complete:
                self.turns.clear()
            return 'clear'
        self.snake.pop()
        return 'move' if turned else None
