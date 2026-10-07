"""Deterministic point-ball physics. Y grows down; all distances are terminal cells."""
import math
from .layouts import bricks_for

WIDTH, HEIGHT = 60, 20
PADDLE_Y, PADDLE_WIDTH = 18, 9
SPEED, STEP, MAX_ELAPSED = 18, 1 / 120, .1
EPS = 1e-9


def rectangle_hit(x, y, vx, vy, brick, duration):
    """Slab intersection with the entire traveled segment, including tied corners."""
    entries, exits = [], []
    for pos, velocity, low, high in ((x, vx, brick.x, brick.x + brick.width),
                                      (y, vy, brick.y, brick.y + brick.height)):
        if abs(velocity) < EPS:
            if pos < low - EPS or pos > high + EPS:
                return None
            entries.append(-math.inf); exits.append(math.inf)
        else:
            a, b = (low - pos) / velocity, (high - pos) / velocity
            entries.append(min(a, b)); exits.append(max(a, b))
    entry, leave = max(entries), min(exits)
    if entry < -EPS or entry > leave + EPS or entry > duration + EPS:
        return None
    return max(0, entry), abs(entries[0] - entry) < EPS, abs(entries[1] - entry) < EPS


class Game:
    def __init__(self):
        self.best = 0
        self.restart()

    def restart(self):
        self.board, self.score, self.lives = 0, 0, 3
        self.bricks = bricks_for(0)
        self._serve()

    def _serve(self):
        self.state, self.paddle = 'waiting', WIDTH / 2
        self.x, self.y = self.paddle, PADDLE_Y - .5
        self.vx, self.vy = SPEED * .4, -SPEED * math.sqrt(.84)
        self.accumulator = 0

    def move(self, direction):
        if self.state not in ('waiting', 'playing'):
            return
        self.paddle = min(WIDTH - PADDLE_WIDTH / 2,
                          max(PADDLE_WIDTH / 2, self.paddle + max(-1, min(1, direction)) * 2))
        if self.state == 'waiting':
            self.x = self.paddle

    def launch(self):
        if self.state == 'waiting':
            self.state = 'playing'

    def snapshot(self):
        return dict(board=self.board, score=self.score, lives=self.lives, best=self.best, state=self.state,
                    paddle=self.paddle, x=self.x, y=self.y, vx=self.vx, vy=self.vy,
                    bricks=sorted(self.bricks))

    def advance(self, elapsed):
        if not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError('elapsed time must be finite and nonnegative')
        if self.state != 'playing':
            return
        self.accumulator += min(elapsed, MAX_ELAPSED)
        while self.accumulator + EPS >= STEP and self.state == 'playing':
            self.accumulator = max(0, self.accumulator - STEP)
            self._step(STEP)

    def _step(self, remaining):
        # At extreme injected speeds, discard excess time after 32 contacts.
        # Ordinary play at SPEED encounters at most a few contacts in one step.
        for _ in range(32):
            contacts = []
            def add(t, nx=False, ny=False, kind='wall', key=None):
                if -EPS <= t <= remaining + EPS:
                    contacts.append((max(0, t), nx, ny, kind, key))
            if self.vx < -EPS:
                add(-self.x / self.vx, nx=True)
            elif self.vx > EPS:
                add((WIDTH - self.x) / self.vx, nx=True)
            if self.vy < -EPS:
                add(-self.y / self.vy, ny=True)
            elif self.vy > EPS:
                add((HEIGHT - self.y) / self.vy, kind='bottom')
                t = (PADDLE_Y - self.y) / self.vy
                landing = self.x + self.vx * t
                if abs(landing - self.paddle) <= PADDLE_WIDTH / 2 + EPS:
                    add(t, ny=True, kind='paddle')
            for key, brick in self.bricks.items():
                hit = rectangle_hit(self.x, self.y, self.vx, self.vy, brick, remaining)
                if hit:
                    add(*hit, kind='brick', key=key)
            if not contacts:
                self.x += self.vx * remaining; self.y += self.vy * remaining
                return
            first = min(c[0] for c in contacts)
            hits = [c for c in contacts if abs(c[0] - first) < EPS]
            self.x += self.vx * first; self.y += self.vy * first
            remaining = max(0, remaining - first)
            if any(c[3] == 'bottom' for c in hits):
                self.lives -= 1
                if self.lives:
                    self._serve()
                else:
                    self.state = 'lost'
                return
            for key in {c[4] for c in hits if c[3] == 'brick'}:
                del self.bricks[key]
                self.score += 10
                self.best = max(self.best, self.score)
            if not self.bricks:
                if self.board == 2:
                    self.state = 'won'
                else:
                    self.board += 1
                    self.bricks = bricks_for(self.board)
                    self._serve()
                return
            if any(c[3] == 'paddle' for c in hits):
                angle = max(-1, min(1, (self.x - self.paddle) / (PADDLE_WIDTH / 2))) * math.pi / 3
                self.vx, self.vy = SPEED * math.sin(angle), -SPEED * math.cos(angle)
            else:
                if any(c[1] for c in hits):
                    self.vx = -self.vx
                if any(c[2] for c in hits):
                    self.vy = -self.vy
            # Move a negligible distance off the contact plane to avoid rounding recontacts.
            nudge = min(remaining, EPS)
            self.x += self.vx * nudge; self.y += self.vy * nudge
            remaining -= nudge
            if remaining <= EPS:
                return
