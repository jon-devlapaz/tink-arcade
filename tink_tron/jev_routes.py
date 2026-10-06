"""Candidate routes for Jev: pure, deterministic and unranked. Facts are computed by the app, never by the model."""
from .ai import DIRECTIONS, HEIGHT, WIDTH, distances

ROUTE_LENGTH = 16
REQUEST_AT = 10          # ask for the next route when this many planned steps remain
TURN_STEPS = (2, 4, 6, 8, 10)
MAX_ROUTES = 60
LEFT_OF = {(1, 0): (0, -1), (0, -1): (-1, 0), (-1, 0): (0, 1), (0, 1): (1, 0)}   # screen y points down
RIGHT_OF = {value: key for key, value in LEFT_OF.items()}
TURN = {'L': LEFT_OF, 'R': RIGHT_OF}
NAMES = {(1, 0): 'right', (-1, 0): 'left', (0, -1): 'up', (0, 1): 'down'}


def _patterns():
    """Turn plans as ((step, 'L'|'R'), ...): none, one turn, then two turns, in a fixed order."""
    yield ()
    for step in TURN_STEPS:
        for side in 'LR':
            yield ((step, side),)
    for i, first in enumerate(TURN_STEPS):
        for second in TURN_STEPS[i + 1:]:
            for a in 'LR':
                for b in 'LR':
                    yield ((first, a), (second, b))


def _walk(start, heading, pattern, length):
    """The direction of each step: steps up to a turn go the old way, then the heading rotates."""
    turns = dict(pattern)
    directions, cell, cells = [], start, []
    for step in range(1, length + 1):
        if step - 1 in turns:
            heading = TURN[turns[step - 1]][heading]
        directions.append(heading)
        cell = (cell[0] + heading[0], cell[1] + heading[1])
        cells.append(cell)
    return directions, cells


def _describe(pattern, heading):
    legs, previous, side_words = [], 0, {'L': 'left', 'R': 'right'}
    for step, side in pattern:
        legs.append(f'{step - previous} steps {NAMES[heading]}, then turn {side_words[side]}')
        heading, previous = TURN[side][heading], step
    return ', '.join(legs + [f'{ROUTE_LENGTH - previous} steps {NAMES[heading]}'])


def enumerate_routes(blocked, start, heading, player_head, length=ROUTE_LENGTH, width=WIDTH, height=HEIGHT):
    """{name: (directions, description)} for each clear route, with neutral facts and no ranking."""
    routes, seen = {}, set()
    for pattern in _patterns():
        directions, cells = _walk(start, heading, pattern, length)
        if len(set(cells)) != len(cells) or seen & {tuple(cells)}:
            continue
        if any(not (0 <= x < width and 0 <= y < height) or (x, y) in blocked for x, y in cells):
            continue
        seen.add(tuple(cells))
        end = cells[-1]
        room = len(distances(blocked | set(cells), end, width, height)) - 1  # not counting the cell the cycle is on
        wall = min(end[0], width - 1 - end[0], end[1], height - 1 - end[1])
        gap = abs(end[0] - player_head[0]) + abs(end[1] - player_head[1])
        description = (f'{_describe(pattern, heading)}. Ends at {end}. {len(pattern)} turns. '
                       f'Open cells reachable from the end (not counting it): {room}. Cells from the end to your rival\'s head: {gap}. '
                       f'Cells from the end to the nearest wall: {wall}.')
        routes[f'route_{len(routes)}'] = (directions, description)
        if len(routes) == MAX_ROUTES:
            break
    return routes


def projected_end(start, heading, plan):
    """Where a cycle ends up, and heading, after following planned directions."""
    cell = start
    for heading in plan:
        cell = (cell[0] + heading[0], cell[1] + heading[1])
    return cell, heading


def plan_cells(start, plan):
    cells, cell = [], start
    for step in plan:
        cell = (cell[0] + step[0], cell[1] + step[1])
        cells.append(cell)
    return cells
