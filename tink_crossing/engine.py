"""Lane-crossing rules on an integer grid; no terminal or audio dependencies.

Lanes shift one whole cell at a time on a fixed 1/120 s step, so a moving car or
log can never skip a cell, and collisions are checked after every shift and hop.
"""
import math

WIDTH, ROWS = 40, 13
HOME, MEDIAN, START = 0, 6, 12
RIVER = range(1, 6)
ROAD = range(7, 12)
STEP, MAX_ELAPSED = 1 / 120, .1
LIVES, LEVELS = 3, 3
LEVEL_SPEED = (1.0, 1.25, 1.5)
BAYS = ((3, 6), (11, 14), (19, 22), (27, 30), (35, 38))  # half-open column ranges
ROW_POINTS, BAY_POINTS, LEVEL_POINTS = 10, 50, 100
START_COL = WIDTH // 2


def _pattern(segments):
    cells = [False] * WIDTH
    for start, length in segments:
        for col in range(start, start + length):
            cells[col % WIDTH] = True
    return tuple(cells)


# row: (occupied cells, cells per second, direction). True means car or log.
LANES = {
    1: (_pattern(((0, 7), (14, 6), (27, 8))), 2, 1),
    2: (_pattern(((3, 8), (18, 7), (31, 6))), 3, -1),
    3: (_pattern(((0, 10), (20, 9))), 4, 1),
    4: (_pattern(((6, 6), (16, 7), (29, 6))), 2, -1),
    5: (_pattern(((2, 9), (17, 8), (31, 7))), 3, 1),
    7: (_pattern(((0, 3), (14, 3), (27, 3))), 4, -1),
    8: (_pattern(((5, 2), (19, 2), (30, 2))), 3, 1),
    9: (_pattern(((2, 4), (24, 4))), 5, -1),
    10: (_pattern(((8, 2), (20, 2), (33, 2))), 2, 1),
    11: (_pattern(((0, 3), (13, 3), (26, 3))), 3, -1),
}
MAX_BASE_SPEED = max(speed for _, speed, _ in LANES.values())


def period(row, level):
    """Simulation steps between one-cell shifts of a lane at a level (1-based)."""
    return max(1, round(1 / (STEP * LANES[row][1] * LEVEL_SPEED[level - 1])))


def bay_at(col):
    for index, (left, right) in enumerate(BAYS):
        if left <= col < right:
            return index
    return None


class Game:
    def __init__(self):
        self.restart()

    def restart(self):
        self.score = 0
        self.lives = LIVES
        self.level = 1
        self.state = 'playing'
        self.paused = False
        self.deaths = 0
        self._new_level()

    def _new_level(self):
        self.bays = [False] * len(BAYS)
        self.lanes = {row: list(cells) for row, (cells, _, _) in LANES.items()}
        self.counters = {row: 0 for row in LANES}
        self.accumulator = 0
        self._to_start()

    def _to_start(self):
        self.row, self.col = START, START_COL
        self.best = START

    # Queries -----------------------------------------------------------------
    def occupied(self, row, col):
        return row in self.lanes and self.lanes[row][col]

    def safe(self, row, col):
        if not 0 <= col < WIDTH:
            return False
        if row in RIVER:
            return self.occupied(row, col)
        if row in ROAD:
            return not self.occupied(row, col)
        return True

    def snapshot(self):
        return {'state': self.state, 'paused': self.paused, 'score': self.score,
                'lives': self.lives, 'level': self.level, 'row': self.row, 'col': self.col,
                'bays': list(self.bays), 'deaths': self.deaths, 'accumulator': self.accumulator,
                'counters': [self.counters[row] for row in sorted(LANES)]}

    # Input -------------------------------------------------------------------
    def hop(self, drow, dcol):
        """Hop one cell. Returns audio cues. Ignored unless actively playing."""
        if self.state != 'playing' or self.paused or abs(drow) + abs(dcol) != 1:
            return []
        row = min(START, max(HOME, self.row + drow))
        col = min(WIDTH - 1, max(0, self.col + dcol))
        if (row, col) == (self.row, self.col):
            return []
        self.row, self.col = row, col
        cues = ['move']
        if row < self.best:
            self.best = row
            self.score += ROW_POINTS
        if row == HOME:
            return cues + self._arrive()
        if not self.safe(row, col):
            return cues + self._die()
        return cues

    def _arrive(self):
        bay = bay_at(self.col)
        if bay is None or self.bays[bay]:
            return self._die()
        self.bays[bay] = True
        self.score += BAY_POINTS
        if all(self.bays):
            self.score += LEVEL_POINTS
            if self.level == LEVELS:
                self.state = 'won'
                return ['clear']
            self.level += 1
            self._new_level()
            return ['clear']
        self._to_start()
        return ['clear']

    def _die(self):
        self.lives -= 1
        self.deaths += 1
        if self.lives == 0:
            self.state = 'over'
        else:
            self._to_start()
        return ['over']

    def toggle_pause(self):
        if self.state == 'playing':
            self.paused = not self.paused
            return True
        return False

    # Time --------------------------------------------------------------------
    def advance(self, elapsed):
        if not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError('elapsed time must be finite and nonnegative')
        if self.state != 'playing' or self.paused:
            return []
        cues = []
        self.accumulator += min(elapsed, MAX_ELAPSED)
        while self.accumulator + 1e-9 >= STEP and self.state == 'playing':
            self.accumulator = max(0, self.accumulator - STEP)
            cues.extend(self.step())
        return cues

    def step(self):
        """One fixed simulation step: shift due lanes, carry the rider, check."""
        for row in sorted(LANES):
            self.counters[row] += 1
            if self.counters[row] < period(row, self.level):
                continue
            self.counters[row] = 0
            direction = LANES[row][2]
            cells = self.lanes[row]
            self.lanes[row] = cells[-direction:] + cells[:-direction]
            if row == self.row and row in RIVER:
                self.col += direction
        if self.row in RIVER or self.row in ROAD:
            if not self.safe(self.row, self.col):
                return self._die()
        return []
