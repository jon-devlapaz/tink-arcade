"""Pac-Man maze: layout text, tile rules and the validator. Pure; no terminal, audio or clock."""

RIGHT, DOWN, LEFT, UP = (1, 0), (0, 1), (-1, 0), (0, -1)
DIRECTIONS = (RIGHT, DOWN, LEFT, UP)
WIDTH, HEIGHT = 28, 31
MIN_ERASABLE = 8

# '#' wall, '.' dot, 'o' energizer, ' ' empty, 'P' Pac-Man start, 'H' ghost house, '-' house door.
LAYOUT = (
    '############################',
    '#............##............#',
    '#.####.#####.##.#####.####.#',
    '#o####.#####.##.#####.####o#',
    '#.####.#####.##.#####.####.#',
    '#..........................#',
    '#.####.##.########.##.####.#',
    '#.####.##.########.##.####.#',
    '#......##..........##......#',
    '######.##.########.##.######',
    '######.##.########.##.######',
    '######................######',
    '######.######--######.######',
    '######.####HHHHHH####.######',
    '      .####HHHHHH####.      ',
    '######.####HHHHHH####.######',
    '######.##############.######',
    '######................######',
    '######.##.########.##.######',
    '######.##.########.##.######',
    '#..........................#',
    '#.####.#####.##.#####.####.#',
    '#.####.#####.##.#####.####.#',
    '#o..##.......P .......##..o#',
    '###.##.##.##.##.##.##.##.###',
    '###.##.##.##.##.##.##.##.###',
    '#......##..........##......#',
    '#.##########.##.##########.#',
    '#..........................#',
    '############################',
    '############################',
)


class Maze:
    """One owner for "which tiles are open". Tiles are (x, y); the tunnel row wraps left to right."""

    def __init__(self, layout):
        self.height, self.width = len(layout), len(layout[0])
        self.walls, self.dots, self.energizers = set(), set(), set()
        self.house, self.door, self.starts = set(), set(), []
        for y, row in enumerate(layout):
            for x, char in enumerate(row):
                tile = (x, y)
                if char == '#':
                    self.walls.add(tile)
                elif char in '.o':
                    self.dots.add(tile)
                    if char == 'o':
                        self.energizers.add(tile)
                elif char == 'H':
                    self.house.add(tile)
                elif char == '-':
                    self.door.add(tile)
                elif char == 'P':
                    self.starts.append(tile)
        self.start = self.starts[0] if self.starts else None
        self.tunnel_row = next((y for y, row in enumerate(layout) if row[0] != '#' and row[-1] != '#'), None)

    def is_open(self, tile):
        x, y = tile
        return (0 <= x < self.width and 0 <= y < self.height
                and tile not in self.walls and tile not in self.house and tile not in self.door)

    def step(self, tile, direction):
        """The open tile one step away, or None. Only the tunnel row wraps."""
        x, y = tile[0] + direction[0], tile[1] + direction[1]
        if not 0 <= y < self.height:
            return None
        if not 0 <= x < self.width:
            if y != self.tunnel_row:
                return None
            x %= self.width
        return (x, y) if self.is_open((x, y)) else None

    def can_erase(self, tile):
        """A wall tile Eraser may remove: interior, clear of the house and tunnel row, and a thin wall with
        open tiles on opposite sides, so removing it joins two corridors and never leaves a dead end."""
        x, y = tile
        if tile not in self.walls:
            return False
        if x in (0, self.width - 1) or y in (0, self.height - 1) or y == self.tunnel_row:
            return False
        sealed = self.house | self.door
        if any((x + dx, y + dy) in sealed for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            return False
        open_at = lambda dx, dy: self.is_open((x + dx, y + dy))
        return (open_at(-1, 0) and open_at(1, 0)) or (open_at(0, -1) and open_at(0, 1))

    @property
    def door_exit(self):
        """The tile above the left half of the door: where ghosts leave and where eyes aim."""
        if not self.door:
            return None
        return (min(x for x, _ in self.door), min(y for _, y in self.door) - 1)

    def ghost_starts(self):
        """Blinky waits outside the door; the others wait inside, Pinky under the door, Inky left, Clyde right."""
        if not self.door or not self.house:
            return {}
        rows = sorted({y for _, y in self.house})
        middle = rows[len(rows) // 2]
        xs = [x for x, y in self.house if y == middle]
        exit_x, _ = self.door_exit
        return {'blinky': self.door_exit, 'pinky': (exit_x, middle), 'inky': (min(xs), middle), 'clyde': (max(xs), middle)}

    def in_tunnel(self, tile):
        """The walled-in stretch of the tunnel row, where ghosts slow down."""
        x, y = tile
        return self.is_open(tile) and y == self.tunnel_row and (x, y - 1) in self.walls and (x, y + 1) in self.walls

    def open_tiles(self):
        return [(x, y) for y in range(self.height) for x in range(self.width) if self.is_open((x, y))]


def problems(layout, min_erasable=MIN_ERASABLE):
    """Defects in a layout, as short codes. An empty list means the layout is fit to ship."""
    if len(layout) != HEIGHT or any(len(row) != WIDTH for row in layout):
        return ['size']
    found = []
    maze = Maze(layout)
    if any(row.replace('P', ' ') != row.replace('P', ' ')[::-1] for row in layout):
        found.append('asymmetric')
    if len(maze.starts) != 1:
        found.append('start')
    if len(maze.energizers) != 4:
        found.append('energizers')
    if not maze.house or not maze.door:
        found.append('no-house')
    if maze.tunnel_row is None:
        found.append('no-tunnel')
    if any(sum(maze.step(tile, d) is not None for d in DIRECTIONS) < 2 for tile in maze.open_tiles()):
        found.append('dead-end')
    if maze.start:
        seen, frontier = {maze.start}, [maze.start]
        while frontier:
            tile = frontier.pop()
            for direction in DIRECTIONS:
                nxt = maze.step(tile, direction)
                if nxt and nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        if not maze.dots <= seen:
            found.append('unreachable')
    if sum(maze.can_erase(tile) for tile in maze.walls) < min_erasable:
        found.append('few-erasable')
    return found
