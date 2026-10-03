"""Deterministic Tetris rules. Coordinates are (column, row); rows grow down."""

from collections import deque
from dataclasses import dataclass
import random

WIDTH = 10
HEIGHT = 20
KINDS = "IJLOSTZ"
BASES = {
    "I": ("....", "IIII", "....", "...."),
    "J": ("J..", "JJJ", "..."),
    "L": ("..L", "LLL", "..."),
    "O": ("OO", "OO"),
    "S": (".SS", "SS.", "..."),
    "T": (".T.", "TTT", "..."),
    "Z": ("ZZ.", ".ZZ", "..."),
}


def _rotations(base):
    result = []
    for _ in range(4):
        result.append(tuple((x, y) for y, row in enumerate(base)
                            for x, cell in enumerate(row) if cell != "."))
        base = tuple("".join(row) for row in zip(*base[::-1]))
    return tuple(result)


SHAPES = {kind: _rotations(base) for kind, base in BASES.items()}
# SRS kick offsets, expressed with positive rows DOWN (not SRS's positive up).
JLSTZ_KICKS = {
    (0, 1): ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
    (1, 0): ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
    (1, 2): ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
    (2, 1): ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
    (2, 3): ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
    (3, 2): ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)),
    (3, 0): ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)),
    (0, 3): ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
}
I_KICKS = {
    (0, 1): ((0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)),
    (1, 0): ((0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)),
    (1, 2): ((0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)),
    (2, 1): ((0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)),
    (2, 3): ((0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)),
    (3, 2): ((0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)),
    (3, 0): ((0, 0), (1, 0), (-2, 0), (1, 2), (-2, -1)),
    (0, 3): ((0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)),
}


@dataclass(frozen=True)
class Piece:
    kind: str
    x: int
    y: int
    rotation: int = 0

    def cells(self):
        return tuple((self.x + x, self.y + y)
                     for x, y in SHAPES[self.kind][self.rotation])


class SevenBag:
    def __init__(self, seed=None):
        self.random = random.Random(seed)
        self.queue = deque()
        self._fill()

    def _fill(self):
        while len(self.queue) < 7:
            bag = list(KINDS)
            self.random.shuffle(bag)
            self.queue.extend(bag)

    def pop(self):
        kind = self.queue.popleft()
        self._fill()
        return kind

    def preview(self, count=3):
        return tuple(self.queue)[:count]


class Game:
    LOCK_DELAY = 0.45
    MAX_LOCK_RESETS = 15
    MAX_DT = 0.25

    def __init__(self, seed=None):
        self.seed = seed
        self.best = 0
        self.restart()

    def restart(self):
        self.best = max(self.best, getattr(self, "score", 0))
        self.board = [[None] * WIDTH for _ in range(HEIGHT)]
        self.bag = SevenBag(self.seed)
        self.score = self.lines = 0
        self.held = None
        self.hold_used = False
        self.paused = self.game_over = False
        self.flash_rows = ()
        self.flash_time = 0.0
        self.message = "READY // GO"
        self.message_time = 1.5
        self.active = None
        self._spawn(self.bag.pop())

    @property
    def level(self):
        return 1 + self.lines // 10

    @property
    def gravity_interval(self):
        return max(0.055, 0.8 * (0.78 ** (self.level - 1)))

    @property
    def running(self):
        return not self.paused and not self.game_over and self.active is not None

    def fits(self, piece):
        # Above-board cells are legal during kicks, but never index the board.
        for x, y in piece.cells():
            if x < 0 or x >= WIDTH or y >= HEIGHT:
                return False
            if y >= 0 and self.board[y][x] is not None:
                return False
        return True

    def _spawn(self, kind):
        self.generation = getattr(self, "generation", 0) + 1
        self.gravity_time = self.lock_time = 0.0
        self.lock_resets = 0
        self.active = Piece(kind, (WIDTH - len(BASES[kind])) // 2, 0)
        if not self.fits(self.active):
            self._top_out()

    def _top_out(self):
        self.game_over = True
        self.active = None
        self.best = max(self.best, self.score)

    def grounded(self):
        p = self.active
        return p is not None and not self.fits(Piece(p.kind, p.x, p.y + 1, p.rotation))

    def _try_transform(self, candidate):
        if not self.fits(candidate):
            return False
        if self.grounded() and self.lock_resets < self.MAX_LOCK_RESETS:
            self.lock_time = 0.0
            self.lock_resets += 1
        self.active = candidate
        self._lock_if_due()
        return True

    def _lock_if_due(self):
        if self.grounded() and self.lock_time >= self.LOCK_DELAY:
            self._lock()

    def move(self, dx):
        if not self.running or dx not in (-1, 1):
            return False
        p = self.active
        return self._try_transform(Piece(p.kind, p.x + dx, p.y, p.rotation))

    def rotate(self, direction=1):
        if not self.running or direction not in (-1, 1):
            return False
        p = self.active
        if p.kind == "O":
            return False
        rotation = (p.rotation + direction) % 4
        kicks = I_KICKS if p.kind == "I" else JLSTZ_KICKS
        for dx, dy in kicks[p.rotation, rotation]:
            if self._try_transform(Piece(p.kind, p.x + dx, p.y + dy, rotation)):
                return True
        return False

    def _down(self):
        p = self.active
        candidate = Piece(p.kind, p.x, p.y + 1, p.rotation)
        if not self.fits(candidate):
            return False
        self.active = candidate
        return True

    def soft_drop(self):
        if not self.running or not self._down():
            return False
        self._award(1)
        self.gravity_time = 0.0
        self._lock_if_due()
        return True

    def ghost(self):
        if self.active is None:
            return None
        p = self.active
        while self.fits(Piece(p.kind, p.x, p.y + 1, p.rotation)):
            p = Piece(p.kind, p.x, p.y + 1, p.rotation)
        return p

    def hard_drop(self):
        if not self.running:
            return False
        landing = self.ghost()
        self._award(2 * (landing.y - self.active.y))
        self.active = landing
        self._lock()
        return True

    def hold(self):
        if not self.running or self.hold_used:
            return False
        kind = self.active.kind
        replacement = self.held if self.held is not None else self.bag.pop()
        self.held = kind
        self.hold_used = True
        self._spawn(replacement)
        return True

    def _award(self, points):
        self.score += points
        self.best = max(self.best, self.score)

    def _lock(self):
        cells = self.active.cells()
        # Lock-out is atomic: no partial write, including no Python negative indices.
        if not self.fits(self.active) or any(y < 0 for _, y in cells):
            self._top_out()
            return
        for x, y in cells:
            self.board[y][x] = self.active.kind
        full = tuple(y for y, row in enumerate(self.board) if all(row))
        if full:
            self._award((0, 100, 300, 500, 800)[len(full)] * self.level)
            self.lines += len(full)
            self.board = ([[None] * WIDTH for _ in full]
                          + [row for y, row in enumerate(self.board) if y not in full])
            self.flash_rows = full
            self.flash_time = 0.18
            self.message = ("", "SINGLE", "DOUBLE", "TRIPLE", "TETRIS!")[len(full)]
            self.message_time = 1.2
        self.hold_used = False
        self._spawn(self.bag.pop())

    def toggle_pause(self):
        if not self.game_over:
            self.paused = not self.paused

    def update(self, dt):
        """Advance active time only. Long stalls are capped; callers freeze on resize."""
        if not self.running:
            return
        dt = max(0.0, min(dt, self.MAX_DT))
        self.flash_time = max(0.0, self.flash_time - dt)
        self.message_time = max(0.0, self.message_time - dt)
        was_grounded = self.grounded()
        self.gravity_time += dt
        while self.gravity_time >= self.gravity_interval:
            self.gravity_time -= self.gravity_interval
            if not self._down():
                self.gravity_time = 0.0
                break
        # Once resets run out, kicks cannot stop the deadline while airborne.
        if was_grounded or self.lock_resets >= self.MAX_LOCK_RESETS:
            self.lock_time += dt
        self._lock_if_due()
