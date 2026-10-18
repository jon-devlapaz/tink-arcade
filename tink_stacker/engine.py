"""Deterministic, skill-only row stacking. No terminal or audio dependencies."""
import math

WIDTH, HEIGHT = 7, 15
MAX_ELAPSED = .250


class Game:
    def __init__(self):
        self.restart()

    def restart(self):
        self.rows = []
        self.x, self.width, self.direction = 0, 3, 1
        self.accumulator = 0.0
        self.state = 'playing'

    @property
    def interval(self):
        return max(.072, .240 - .012 * len(self.rows))

    def lock_row(self):
        if self.state != 'playing':
            return None
        occupied = tuple(range(self.x, self.x + self.width))
        surviving = tuple(x for x in occupied if not self.rows or x in self.rows[-1])
        if not surviving:
            self.state = 'lost'
            return 'over'
        self.rows.append(surviving)
        self.width = len(surviving)
        self.accumulator = 0.0
        if len(self.rows) == HEIGHT:
            self.state = 'won'
            return 'clear'
        self.direction = -1 if len(self.rows) % 2 else 1
        self.x = WIDTH - self.width if self.direction == -1 else 0
        return 'place'

    def advance(self, elapsed_seconds):
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError('Elapsed time must be finite and nonnegative.')
        if self.state != 'playing' or elapsed_seconds > MAX_ELAPSED:
            return
        self.accumulator += elapsed_seconds
        while self.accumulator + 1e-12 >= self.interval:
            self.accumulator = max(0.0, self.accumulator - self.interval)
            next_x = self.x + self.direction
            if next_x < 0 or next_x + self.width > WIDTH:
                self.direction *= -1
            self.x += self.direction

    def snapshot(self):
        return dict(rows=[list(row) for row in self.rows], x=self.x, width=self.width,
                    direction=self.direction, accumulator=self.accumulator,
                    state=self.state, interval=self.interval)
