"""Deterministic Pac-Man rules, independent of the terminal and audio."""
import random

from .ghosts import (CHASE, EYES_SPEED, NAMES, SCATTER, Ghost, Pen, Waves, chase_target, choose_direction,  # noqa: F401
                     dot_limits, fright_flashes, fright_speed, fright_time, frightened_direction, ghost_speed,
                     idle_limit, plan_direction, scatter_target, wave_schedule)
from .maze import DIRECTIONS, DOWN, LAYOUT, LEFT, RIGHT, UP, Maze  # noqa: F401  (directions re-exported)

TOP_SPEED = 10  # tiles per second at 100%
LIVES = 3
DOT_SCORE, ENERGIZER_SCORE, GHOST_SCORE = 10, 50, 100  # an eaten ghost scores GHOST_SCORE * 2 ** chain
FLASH_PERIOD = 0.25  # seconds per warning flash; the source gives counts, not times


def pacman_speed(level):
    """Pac-Man's share of top speed on a level; the table stops changing after level 21."""
    if level == 1:
        return .8
    if level <= 4:
        return .9
    return 1.0 if level <= 20 else .9


class Game:
    def __init__(self, seed=None, layout=LAYOUT, classic=False):
        self.seed, self.layout, self.classic = seed, layout, classic
        self.best = 0
        self.restart()

    def restart(self):
        self.score, self.level, self.lives = 0, 1, LIVES
        self.paused = self.game_over = False
        self.bookmark_available = self.eraser_available = True
        self.new_level()

    def new_level(self):
        self.maze = Maze(self.layout)
        self.dots = set(self.maze.dots)
        self.new_round(refill=False)

    def new_round(self, refill=True):
        """Everyone back to the start. Dots and erased walls stay; only a new life refills charges."""
        if refill:
            self.bookmark_available = self.eraser_available = True
        self.bookmark, self.bookmark_left = None, 0.0
        self.pacman = self.maze.start
        self.direction = LEFT
        self.turn_buffer = None
        self.progress = 0.0
        self.rng = random.Random(self.seed)
        self.fright_left, self.fright_flashes, self.chain = 0.0, 0, 0
        self.waves = Waves(wave_schedule(self.level))
        self.pen = Pen(dot_limits(self.level), idle_limit(self.level))
        starts = self.maze.ghost_starts()
        self.ghosts = [Ghost(name, starts[name], out=name == 'blinky') for name in NAMES] if starts else []
        for ghost in self.ghosts:
            if ghost.state == 'out':
                self._replan(ghost)
        self._release(self.pen.start())

    def ghost(self, name):
        return next(g for g in self.ghosts if g.name == name)

    @property
    def mode(self):
        return self.waves.mode

    @property
    def flashing(self):
        """True on the blink-on half of each warning flash in the last moments of a fright."""
        return (0 < self.fright_left <= self.fright_flashes * FLASH_PERIOD
                and int(self.fright_left / (FLASH_PERIOD / 2)) % 2 == 1)

    def turn(self, direction):
        """Remember a turn until it fits at a junction. A reverse fits at once."""
        if (self.paused or self.game_over or direction not in DIRECTIONS
                or direction in (self.direction, self.turn_buffer)):
            return False
        self.turn_buffer = direction
        return True

    def toggle_pause(self):
        if self.game_over:
            return False
        self.paused = not self.paused
        return True

    def drop_bookmark(self):
        if self.classic or self.paused or self.game_over or not self.bookmark_available:
            return None
        self.bookmark_available = False
        self.bookmark, self.bookmark_left = self.pacman, 4.0
        self._refresh_plans()
        self._consume_bookmark()
        return 'rotate'

    def erase(self):
        if self.classic or self.paused or self.game_over or not self.eraser_available:
            return None
        tile = (self.pacman[0] + self.direction[0], self.pacman[1] + self.direction[1])
        if not self.maze.can_erase(tile):
            return None
        self.maze.walls.remove(tile)
        self.eraser_available = False
        self._refresh_plans()
        return 'place'

    def _refresh_plans(self):
        for ghost in self.ghosts:
            if ghost.state in ('out', 'eyes') and not ghost.frightened:
                self._replan(ghost)

    def _clear_bookmark(self):
        self.bookmark, self.bookmark_left = None, 0.0
        self._refresh_plans()

    def _consume_bookmark(self):
        if self.bookmark is not None and any(g.tile == self.bookmark for g in self.ghosts):
            self._clear_bookmark()

    def update(self, dt):
        """Advance by elapsed time. One call moves each actor at most one tile. Returns a cue or None."""
        if self.paused or self.game_over:
            return None
        dt = max(0.0, min(dt, 1 / TOP_SPEED))
        if self.bookmark is not None:
            self.bookmark_left = max(0.0, self.bookmark_left - dt)
            if self.bookmark_left <= 1e-9:
                self._clear_bookmark()
        level, lives = self.level, self.lives
        cue = self._move_pacman(dt)
        if self.game_over or self.level != level or self.lives != lives:
            return cue
        ghost_cue = self._move_ghosts(dt)
        return ghost_cue or cue

    def _move_pacman(self, dt):
        self.progress += dt * TOP_SPEED * pacman_speed(self.level)
        if self.progress < 1:
            return None
        if self.turn_buffer and self.maze.step(self.pacman, self.turn_buffer):
            self.direction, self.turn_buffer = self.turn_buffer, None
        target = self.maze.step(self.pacman, self.direction)
        if target is None:
            self.progress = 1.0  # blocked: stay ready to move the moment a way opens
            return None
        self.progress -= 1
        self.pacman = target
        cue = self._eat()
        return cue if cue == 'clear' else self._touch() or cue

    def _eat(self):
        if self.pacman not in self.dots:
            return None
        self.dots.discard(self.pacman)
        energizer = self.pacman in self.maze.energizers
        self.score += ENERGIZER_SCORE if energizer else DOT_SCORE
        self.best = max(self.best, self.score)
        self._release(self.pen.dot())
        if energizer:
            self._frighten()
        if self.dots:
            return 'switch' if energizer else None
        self.level += 1
        self.new_level()
        return 'clear'

    def _frighten(self):
        """An energizer: every ghost outside turns back, and on most levels every ghost turns blue."""
        self.chain = 0
        seconds = fright_time(self.level)
        self.fright_left, self.fright_flashes = float(seconds), fright_flashes(self.level)
        for ghost in self.ghosts:
            if ghost.state == 'out':
                ghost.reverse = True
            elif ghost.state in ('house', 'leaving'):
                ghost.flipped = True
            if seconds and ghost.state in ('out', 'house', 'leaving'):
                ghost.frightened = True

    def _touch(self):
        """A live ghost on Pac-Man's tile costs a life; a frightened one is eaten and its eyes head home."""
        here = [g for g in self.ghosts if g.state == 'out' and g.tile == self.pacman]
        if any(not g.frightened for g in here):
            self.lives -= 1
            if self.lives:
                self.new_round()
            else:
                self.game_over = True
            return 'over'
        for ghost in here:
            self.chain += 1
            self.score += GHOST_SCORE * 2 ** self.chain
            self.best = max(self.best, self.score)
            ghost.state, ghost.frightened, ghost.reverse = 'eyes', False, False
            self._replan(ghost)
        return 'clear' if here else None

    def _release(self, names):
        for name in names if self.ghosts else ():
            self.ghost(name).state = 'leaving'

    def _move_ghosts(self, dt):
        if self.fright_left > 0:
            self.fright_left = max(0.0, self.fright_left - dt)
            if self.fright_left == 0:
                for ghost in self.ghosts:
                    ghost.frightened = False
        elif self.waves.tick(dt):
            for ghost in self.ghosts:
                if ghost.state == 'out':
                    ghost.reverse = True
                elif ghost.state in ('house', 'leaving'):
                    ghost.flipped = True
        self._release(self.pen.tick(dt))
        cue = None
        for ghost in self.ghosts:
            if ghost.state == 'house':
                continue
            ghost.progress += dt * TOP_SPEED * self._speed(ghost)
            if ghost.progress < 1:
                continue
            ghost.progress -= 1
            {'leaving': self._leave, 'entering': self._enter}.get(ghost.state, self._roam)(ghost)
            cue = self._touch() or cue
            if cue == 'over':
                return cue
        return self._touch() or cue

    def _speed(self, ghost):
        if ghost.state in ('eyes', 'entering'):
            return EYES_SPEED
        if self.maze.in_tunnel(ghost.tile):
            return ghost_speed(self.level, True)
        if ghost.frightened:
            return fright_speed(self.level)
        return ghost_speed(self.level, False)

    def _leave(self, ghost):
        """Walk to the tile above the door: sideways to the door's column, then up."""
        exit_x, exit_y = self.maze.door_exit
        x, y = ghost.tile
        if x != exit_x:
            x += 1 if exit_x > x else -1
        elif y > exit_y:
            y -= 1
        ghost.tile = (x, y)
        if ghost.tile == (exit_x, exit_y):
            ghost.state, ghost.direction, ghost.flipped = 'out', RIGHT if ghost.flipped else LEFT, False
            self._replan(ghost)
        self._consume_bookmark()

    def _enter(self, ghost):
        """Revived eyes drop through the door to the middle of the house, then leave like any other ghost."""
        x, y = ghost.tile
        ghost.tile = (x, y + 1)
        if y + 1 >= self.maze.ghost_starts()['pinky'][1]:
            ghost.state, ghost.direction = 'leaving', LEFT

    def _roam(self, ghost):
        moving = ghost.direction
        ahead = self.maze.step(ghost.tile, moving)
        if ahead is None:  # not expected on a valid maze; decide on the spot
            moving = ghost.direction = choose_direction(self.maze, ghost.tile, moving, self._target(ghost))
            ahead = self.maze.step(ghost.tile, moving)
            if ahead is None:
                return
        ghost.tile = ahead
        if ghost.state == 'eyes' and ghost.tile == self.maze.door_exit:
            ghost.state = 'entering'
        else:
            if ghost.reverse:
                ghost.direction, ghost.reverse = (-moving[0], -moving[1]), False
            else:
                ghost.direction = ghost.plan
            self._replan(ghost)
        self._consume_bookmark()

    def _replan(self, ghost):
        if ghost.frightened and ghost.state == 'out':
            ahead = self.maze.step(ghost.tile, ghost.direction)
            ghost.plan = frightened_direction(self.maze, ahead or ghost.tile, ghost.direction, self.rng)
        else:
            ghost.plan = plan_direction(self.maze, ghost.tile, ghost.direction, self._target(ghost))

    def _target(self, ghost):
        if ghost.state == 'eyes':
            return self.maze.door_exit
        if self.bookmark is not None and ghost.state == 'out' and not ghost.frightened:
            return self.bookmark
        corner = scatter_target(ghost.name, self.maze)
        if self.mode == SCATTER:
            return corner
        return chase_target(ghost.name, self.pacman, self.direction, self.ghost('blinky').tile, ghost.tile, corner)
