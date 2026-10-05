"""Point-ball Pong physics in terminal cells; no terminal or audio dependencies."""
import math

WIDTH, HEIGHT, PADDLE_HEIGHT = 60, 20, 5
SPEED, COMPUTER_SPEED, STEP, MAX_ELAPSED = 24, 6, 1 / 120, .1
LEFT_X, RIGHT_X, EPS = 1, 59, 1e-9


class Game:
    def __init__(self):
        self.restart()

    def restart(self):
        self.player_score = self.computer_score = self.serves = 0
        self.paused = False
        self._waiting()

    def _waiting(self):
        self.state = 'waiting'
        self.player = self.computer = HEIGHT / 2
        self.x, self.y = WIDTH / 2, HEIGHT / 2
        sign = 1 if self.serves % 2 == 0 else -1
        self.vx = sign * SPEED * math.sqrt(.91)
        self.vy = sign * SPEED * .3
        self.accumulator = 0

    def launch(self):
        if self.state == 'waiting' and not self.paused:
            self.state = 'playing'
            self.serves += 1
            return True
        return False

    def move(self, direction):
        if self.state in ('waiting', 'playing') and not self.paused:
            self.player = self._clamp(self.player + max(-1, min(1, direction)) * 1.5)

    @staticmethod
    def _clamp(value):
        return min(HEIGHT - PADDLE_HEIGHT / 2, max(PADDLE_HEIGHT / 2, value))

    def toggle_pause(self):
        if self.state in ('waiting', 'playing'):
            self.paused = not self.paused
            return True
        return False

    def snapshot(self):
        return {key: getattr(self, key) for key in ('state', 'paused', 'player_score',
                'computer_score', 'serves', 'player', 'computer', 'x', 'y', 'vx', 'vy', 'accumulator')}

    def advance(self, elapsed):
        if not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError('elapsed time must be finite and nonnegative')
        cues = []
        if self.state != 'playing' or self.paused:
            return cues
        self.accumulator += min(elapsed, MAX_ELAPSED)
        while self.accumulator + EPS >= STEP and self.state == 'playing':
            self.accumulator = max(0, self.accumulator - STEP)
            distance = max(-COMPUTER_SPEED * STEP, min(COMPUTER_SPEED * STEP, self.y - self.computer))
            self.computer = self._clamp(self.computer + distance)
            cues.extend(self._step(STEP))
        return cues

    def _step(self, remaining):
        cues = []
        for _ in range(32):
            contacts = []
            def add(t, kind):
                if -EPS <= t <= remaining + EPS:
                    contacts.append((max(0, t), kind))
            if self.vy < -EPS:
                add(-self.y / self.vy, 'wall')
            elif self.vy > EPS:
                add((HEIGHT - self.y) / self.vy, 'wall')
            if abs(self.vx) > EPS:
                left = self.vx < 0
                plane = LEFT_X if left else RIGHT_X
                paddle = self.player if left else self.computer
                t = (plane - self.x) / self.vx
                if abs(self.y + self.vy * t - paddle) <= PADDLE_HEIGHT / 2 + EPS:
                    add(t, 'paddle')
                add(((0 if left else WIDTH) - self.x) / self.vx, 'point')
            if not contacts:
                self.x += self.vx * remaining
                self.y += self.vy * remaining
                return cues
            first = min(t for t, _ in contacts)
            hits = {kind for t, kind in contacts if abs(t - first) < EPS}
            self.x += self.vx * first
            self.y += self.vy * first
            remaining = max(0, remaining - first)
            if 'point' in hits:
                if self.vx < 0:
                    self.computer_score += 1
                else:
                    self.player_score += 1
                self._waiting()
                if self.player_score == 7:
                    self.state = 'won'
                elif self.computer_score == 7:
                    self.state = 'lost'
                return cues + (['over'] if self.state == 'lost' else ['clear'])
            if 'paddle' in hits:
                left = self.vx < 0
                paddle = self.player if left else self.computer
                offset = max(-1, min(1, (self.y - paddle) / (PADDLE_HEIGHT / 2)))
                angle = offset * math.pi / 3
                if abs(angle) < .08:
                    angle = .08 if self.vy >= 0 else -.08
                self.vx = (1 if left else -1) * SPEED * math.cos(angle)
                self.vy = SPEED * math.sin(angle)
                cues.append('move')
            if 'wall' in hits:
                # A paddle and wall can meet at the same instant. Aim into court.
                self.vy = abs(self.vy) if self.y < HEIGHT / 2 else -abs(self.vy)
            nudge = min(remaining, EPS)
            self.x += self.vx * nudge
            self.y += self.vy * nudge
            remaining -= nudge
            if remaining <= EPS:
                return cues
        return cues
