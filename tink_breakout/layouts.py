"""Three fixed 12 by 6 patterns, in a 60 by 20 playfield."""
from dataclasses import dataclass

NAMES = ('Gate', 'Chevron', 'Islands')
PATTERNS = (
    ('############', '###......###', '###......###', '###......###', '###......###', '............'),
    ('#..........#', '.#........#.', '..#......#..', '...#....#...', '....#..#....', '.....##.....'),
    ('###..##..###', '###..##..###', '............', '..###..###..', '..###..###..', '............'),
)


@dataclass(frozen=True)
class Brick:
    id: int
    x: float
    y: float
    width: float = 4
    height: float = .75


def bricks_for(board):
    return {row * 12 + col: Brick(row * 12 + col, 6 + col * 4, 2 + row)
            for row, line in enumerate(PATTERNS[board])
            for col, char in enumerate(line) if char == '#'}
