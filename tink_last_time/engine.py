"""Fixed-tick rules and recorded positions, independent of terminal and audio."""
import math
import random

WIDTH, HEIGHT = 30, 18
TICK_SECONDS = .1
ROUND_TICKS = 150
SPARK_COUNT = 6
DIRECTIONS = ((0, -1), (0, 1), (-1, 0), (1, 0))


class Game:
    def __init__(self, seed=None):
        self.seed = seed
        self.restart()

    def restart(self):
        self.rng = random.Random(self.seed)
        self.player = (WIDTH // 2, HEIGHT // 2)
        self.direction = (0, 0)
        self.score = self.tick = 0
        self.accumulator = 0.0
        self.state = 'playing'
        self.paths = []
        self.path = [self.player]
        self.sparks = set()
        self._fill_sparks()

    @property
    def round(self):
        return len(self.paths) + 1

    @property
    def ghosts(self):
        return tuple(path[self.tick] for path in self.paths)

    def steer(self, direction):
        if direction not in DIRECTIONS:
            raise ValueError('Expected a cardinal direction')
        if self.state == 'playing':
            self.direction = direction

    def _fill_sparks(self):
        occupied = self.sparks | set(self.ghosts) | {self.player}
        free = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
                if (x, y) not in occupied]
        count = min(SPARK_COUNT - len(self.sparks), len(free))
        self.sparks.update(self.rng.sample(free, count))

    def _safe_origin(self):
        origins = set(self.ghosts)
        if self.player not in origins:
            return
        future = {path[1] for path in self.paths}
        cells = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
                 if (x, y) not in origins]
        # A completely occupied arena has no safe relocation: every cell is
        # genuine ghost contact. End normally rather than crashing.
        if not cells:
            self.state = 'lost'
            self.accumulator = 0.0
            return
        clear = [p for p in cells if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) > 1
                                       for q in origins | future)]
        self.player = min(clear or cells,
                          key=lambda p: (abs(p[0] - self.player[0]) + abs(p[1] - self.player[1]), p[1], p[0]))

    def _step(self):
        old = self.player
        dx, dy = self.direction
        new = (max(0, min(WIDTH - 1, old[0] + dx)),
               max(0, min(HEIGHT - 1, old[1] + dy)))
        # Both endpoints and swaps are contacts. Paths only move one cell/tick.
        hit = any(old == p[self.tick] or new == p[self.tick + 1]
                  or (old == p[self.tick + 1] and new == p[self.tick])
                  for p in self.paths)
        self.player = new
        self.tick += 1
        self.path.append(new)
        if hit:
            self.state = 'lost'
            self.accumulator = 0.0
            return
        if new in self.sparks:
            self.sparks.remove(new)
            self.score += 1
        if self.tick == ROUND_TICKS:
            self.paths.append(tuple(self.path))
            self.tick = 0
            self._safe_origin()
            self.path = [self.player]
        self._fill_sparks()

    def advance(self, seconds):
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError('Elapsed time must be finite and nonnegative')
        if self.state != 'playing' or seconds > .250:
            return
        self.accumulator += seconds
        while self.accumulator + 1e-12 >= TICK_SECONDS and self.state == 'playing':
            self.accumulator = max(0.0, self.accumulator - TICK_SECONDS)
            self._step()

    def snapshot(self):
        return dict(player=list(self.player), direction=list(self.direction),
                    score=self.score, round=self.round, tick=self.tick,
                    ghosts=[list(p) for p in self.ghosts],
                    sparks=[list(p) for p in sorted(self.sparks)],
                    state=self.state, accumulator=self.accumulator)
