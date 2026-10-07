"""Ghost rules as pure functions and small timers: targets, junction choice, waves, house release.
No terminal, audio or clock; the engine feeds them elapsed time."""
from .maze import DOWN, LEFT, RIGHT, UP

NAMES = ('blinky', 'pinky', 'inky', 'clyde')
SCATTER, CHASE = 'scatter', 'chase'
TIE_ORDER = (UP, LEFT, DOWN, RIGHT)
CLOCKWISE = (UP, RIGHT, DOWN, LEFT)
EYES_SPEED = 1.0  # not in the source text; see runs/pacman/dossier-notes.md
INF = float('inf')
LEVEL_ONE_WAVES = ((SCATTER, 7), (CHASE, 20), (SCATTER, 7), (CHASE, 20), (SCATTER, 5), (CHASE, 20), (SCATTER, 5), (CHASE, INF))


def _ahead(tile, direction, count):
    return (tile[0] + direction[0] * count, tile[1] + direction[1] * count)


def scatter_target(name, maze):
    """Each ghost's home corner is a tile off the maze it can never reach, so it circles that corner."""
    return {'blinky': (maze.width - 3, -3), 'pinky': (2, -3),
            'inky': (maze.width - 1, maze.height + 2), 'clyde': (0, maze.height + 2)}[name]


def chase_target(name, pacman, heading, blinky, own, corner):
    """The tile a ghost aims for while chasing. The arcade's overflow bug for upward travel is not copied."""
    if name == 'blinky':
        return pacman
    if name == 'pinky':
        return _ahead(pacman, heading, 4)
    if name == 'inky':
        pivot = _ahead(pacman, heading, 2)
        return (2 * pivot[0] - blinky[0], 2 * pivot[1] - blinky[1])
    dx, dy = own[0] - pacman[0], own[1] - pacman[1]
    return pacman if dx * dx + dy * dy >= 64 else corner


def choose_direction(maze, tile, heading, target):
    """The exit to take from `tile`: the open one whose next tile is nearest the target. Never a reverse
    unless nothing else is open. Ties go up, left, down, right."""
    back = (-heading[0], -heading[1])
    best = None
    for direction in TIE_ORDER:
        if direction == back or maze.step(tile, direction) is None:
            continue
        nx, ny = tile[0] + direction[0], tile[1] + direction[1]
        distance = (nx - target[0]) ** 2 + (ny - target[1]) ** 2
        if best is None or distance < best[0]:
            best = (distance, direction)
    return best[1] if best else back


def plan_direction(maze, tile, heading, target):
    """A ghost decides one tile early: on reaching `tile` it picks the exit for the tile it is about to enter."""
    ahead = maze.step(tile, heading)
    return choose_direction(maze, ahead or tile, heading, target)


def wave_schedule(level):
    """Scatter and chase periods in seconds. v1 uses the level-1 table on every level (see runs/pacman/dossier-notes.md)."""
    return LEVEL_ONE_WAVES


class Waves:
    """The scatter/chase timer. `tick` returns True when the mode changed."""

    def __init__(self, schedule):
        self.schedule = schedule
        self.reset()

    def reset(self):
        self.index, self.left = 0, self.schedule[0][1]

    @property
    def mode(self):
        return self.schedule[self.index][0]

    def tick(self, dt):
        changed = False
        self.left -= dt
        while self.left <= 0 and self.index < len(self.schedule) - 1:
            overshoot = -self.left
            self.index += 1
            self.left = self.schedule[self.index][1] - overshoot
            changed = True
        return changed


def dot_limits(level):
    """Dots Pac-Man must eat, counted for one waiting ghost at a time, before that ghost leaves the house."""
    if level == 1:
        return {'pinky': 0, 'inky': 30, 'clyde': 60}
    return {'pinky': 0, 'inky': 0, 'clyde': 50} if level == 2 else {'pinky': 0, 'inky': 0, 'clyde': 0}


def idle_limit(level):
    """Seconds without eating a dot before the next waiting ghost is forced out."""
    return 4 if level < 5 else 3


class Pen:
    """Who leaves the ghost house and when. Each method returns the names released by that event."""
    ORDER = ('pinky', 'inky', 'clyde')

    def __init__(self, limits, idle_limit):
        self.limits, self.idle_limit = dict(limits), idle_limit
        self.waiting = list(self.ORDER)
        self.counts = dict.fromkeys(self.ORDER, 0)
        self.idle = 0.0

    def _due(self):
        released = []
        while self.waiting and self.counts[self.waiting[0]] >= self.limits[self.waiting[0]]:
            released.append(self.waiting.pop(0))
        return released

    def start(self):
        return self._due()

    def dot(self):
        self.idle = 0.0
        if self.waiting:
            self.counts[self.waiting[0]] += 1
        return self._due()

    def tick(self, dt):
        if not self.waiting:
            return []
        self.idle += dt
        if self.idle < self.idle_limit:
            return []
        self.idle = 0.0
        return [self.waiting.pop(0)]


# Table A.1 of the Pac-Man Dossier: (seconds, flashes) by level. Levels 17, 19 and up have no blue time.
FRIGHT_TABLE = {1: (6, 5), 2: (5, 5), 3: (4, 5), 4: (3, 5), 5: (2, 5), 6: (5, 5), 7: (2, 5), 8: (2, 5), 9: (1, 3),
                10: (5, 5), 11: (2, 5), 12: (1, 3), 13: (1, 3), 14: (3, 5), 15: (1, 3), 16: (1, 3), 18: (1, 3)}


def fright_time(level):
    return FRIGHT_TABLE.get(level, (0, 0))[0]


def fright_flashes(level):
    return FRIGHT_TABLE.get(level, (0, 0))[1]


def fright_speed(level):
    return .50 if level == 1 else .55 if level <= 4 else .60


def frightened_direction(maze, tile, heading, rng):
    """A frightened ghost tries a random direction, then the next clockwise one, skipping walls and a reverse."""
    back = (-heading[0], -heading[1])
    start = rng.randrange(4)
    for offset in range(4):
        direction = CLOCKWISE[(start + offset) % 4]
        if direction != back and maze.step(tile, direction):
            return direction
    return back


def ghost_speed(level, in_tunnel):
    """A ghost's share of top speed."""
    normal, tunnel = (.75, .40) if level == 1 else (.85, .45) if level <= 4 else (.95, .50)
    return tunnel if in_tunnel else normal


class Ghost:
    def __init__(self, name, tile, out):
        self.name, self.tile = name, tile
        self.direction = self.plan = LEFT
        # 'house' waits, 'leaving' walks to the exit, 'out' roams, 'eyes' head home, 'entering' goes back in
        self.state = 'out' if out else 'house'
        self.progress = 0.0
        self.frightened = False
        self.flipped = False   # a mode change came while it was inside, so it leaves to the right
        self.reverse = False   # ordered to turn back once it enters its next tile
