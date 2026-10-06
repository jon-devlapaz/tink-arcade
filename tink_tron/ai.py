"""Machine opponents: pure, seedable functions of the board; no terminal, no network."""
from collections import deque

WIDTH, HEIGHT = 38, 20
RIGHT, DOWN, LEFT, UP = (1, 0), (0, 1), (-1, 0), (0, -1)
DIRECTIONS = (RIGHT, DOWN, LEFT, UP)
LEVELS = ('easy', 'normal', 'hard')


def _open(cell, blocked, width, height):
    x, y = cell
    return 0 <= x < width and 0 <= y < height and cell not in blocked


def distances(blocked, start, width=WIDTH, height=HEIGHT):
    """Breadth-first step counts from start over open cells (start itself is 0)."""
    seen = {start: 0}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in DIRECTIONS:
            cell = (x + dx, y + dy)
            if cell not in seen and _open(cell, blocked, width, height):
                seen[cell] = seen[(x, y)] + 1
                queue.append(cell)
    return seen


def safe_moves(blocked, head, width=WIDTH, height=HEIGHT):
    """Directions whose next cell is on the grid and free; a reversal is never free."""
    return [d for d in DIRECTIONS if _open((head[0] + d[0], head[1] + d[1]), blocked, width, height)]


def territory(blocked, mine, theirs, width=WIDTH, height=HEIGHT):
    """Cells reachable strictly sooner from mine than from theirs (theirs moves next, so it wins ties)."""
    near = distances(blocked, mine, width, height)
    far = distances(blocked, theirs, width, height)
    return sum(1 for cell, steps in near.items() if cell != mine and steps < far.get(cell, steps + 1))


def choose(blocked, me, opponent, direction, level, rng, width=WIDTH, height=HEIGHT):
    """The direction for the cycle at `me`. `blocked` holds every trail cell, both heads included."""
    moves = safe_moves(blocked, me, width, height)
    if not moves:
        return direction
    if level == 'easy':
        return rng.choice(moves)
    scored = []
    for move in moves:
        cell = (me[0] + move[0], me[1] + move[1])
        walled = blocked | {cell}
        room = len(distances(walled, cell, width, height))
        claimed = territory(walled, cell, opponent, width, height) if level == 'hard' else 0
        scored.append(((claimed, room, move == direction), move))
    best = max(score for score, _ in scored)
    return rng.choice([move for score, move in scored if score == best])
