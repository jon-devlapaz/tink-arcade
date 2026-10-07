import unittest

from tink_pacman.maze import HEIGHT, LAYOUT, MIN_ERASABLE, WIDTH, Maze, problems


def mutate(layout, tile, char):
    x, y = tile
    rows = list(layout)
    rows[y] = rows[y][:x] + char + rows[y][x + 1:]
    return tuple(rows)


def tiles(layout, chars):
    return [(x, y) for y, row in enumerate(layout) for x, c in enumerate(row) if c in chars]


class ShippedMazeTests(unittest.TestCase):
    def test_size_and_no_problems(self):
        self.assertEqual((WIDTH, HEIGHT), (28, 31))
        self.assertEqual(len(LAYOUT), HEIGHT)
        self.assertTrue(all(len(row) == WIDTH for row in LAYOUT))
        self.assertEqual(problems(LAYOUT), [])

    def test_the_bottom_corridor_runs_the_full_width(self):
        self.assertEqual(LAYOUT[28][1:-1], '.' * (WIDTH - 2))

    def test_ascii_only_known_characters(self):
        self.assertTrue(set(''.join(LAYOUT)) <= set('#.o PH-'))

    def test_four_energizers_one_start_house_and_tunnel(self):
        maze = Maze(LAYOUT)
        self.assertEqual(len(maze.energizers), 4)
        self.assertEqual(len(tiles(LAYOUT, 'P')), 1)
        self.assertTrue(maze.house and maze.door)
        self.assertIsNotNone(maze.tunnel_row)
        self.assertEqual(maze.dots, set(tiles(LAYOUT, '.o')))

    def test_at_least_the_required_erasable_walls(self):
        maze = Maze(LAYOUT)
        erasable = [t for t in maze.walls if maze.can_erase(t)]
        self.assertGreaterEqual(len(erasable), MIN_ERASABLE)


class ValidatorRejectsEachDefectTests(unittest.TestCase):
    def test_wrong_size(self):
        self.assertIn('size', problems(LAYOUT[:-1]))
        self.assertIn('size', problems(tuple(row[:-1] for row in LAYOUT)))

    def test_asymmetry(self):
        dot = tiles(LAYOUT, '.')[0]
        self.assertIn('asymmetric', problems(mutate(LAYOUT, dot, '#')))

    def test_unreachable_dot(self):
        dot = next(t for t in tiles(LAYOUT, '.') if t[0] < 13 and 3 < t[1] < 28)
        walled = LAYOUT
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = dot[0] + dx, dot[1] + dy
            if walled[ny][nx] != '#':
                walled = mutate(walled, (nx, ny), '#')
        self.assertIn('unreachable', problems(walled))

    def test_dead_end(self):
        maze = Maze(LAYOUT)
        corridor = next(t for t in sorted(maze.dots) if sum(maze.is_open(maze.step(t, d) or (-9, -9))
                                                            for d in ((1, 0), (-1, 0), (0, 1), (0, -1))) == 2)
        neighbour = next(maze.step(corridor, d) for d in ((1, 0), (-1, 0), (0, 1), (0, -1))
                         if maze.step(corridor, d) and maze.is_open(maze.step(corridor, d)))
        self.assertIn('dead-end', problems(mutate(LAYOUT, neighbour, '#')))

    def test_missing_tunnel(self):
        row = Maze(LAYOUT).tunnel_row
        layout = mutate(mutate(LAYOUT, (0, row), '#'), (WIDTH - 1, row), '#')
        self.assertIn('no-tunnel', problems(layout))

    def test_missing_house(self):
        layout = tuple(row.replace('H', '#').replace('-', '#') for row in LAYOUT)
        self.assertIn('no-house', problems(layout))

    def test_energizer_count(self):
        energizer = tiles(LAYOUT, 'o')[0]
        self.assertIn('energizers', problems(mutate(LAYOUT, energizer, '.')))

    def test_start_must_be_exactly_one(self):
        start = tiles(LAYOUT, 'P')[0]
        self.assertIn('start', problems(mutate(LAYOUT, start, ' ')))
        self.assertIn('start', problems(mutate(LAYOUT, (start[0] - 1, start[1]), 'P')))

    def test_too_few_erasable_walls(self):
        self.assertIn('few-erasable', problems(LAYOUT, min_erasable=10 ** 6))


THIN = ('#######',
        '#.....#',
        '#.###.#',
        '#.....#',
        '#######')
THICK = ('#######',
         '#.....#',
         '#.###.#',
         '#.###.#',
         '#.....#',
         '#######')
BY_THE_HOUSE = ('#########',
                '#.......#',
                '#..#-#..#',
                '#...H...#',
                '#########')
ON_THE_TUNNEL_ROW = ('#######',
                     ' ..#.. ',
                     '#######')


PEN = ('###########',
       '#.........#',
       '#.###-###.#',
       '#.#HHHHH#.#',
       '#.#######.#',
       ' ....P.... ',
       '###########')


class PenGeometryTests(unittest.TestCase):
    def test_the_exit_is_the_tile_above_the_door(self):
        self.assertEqual(Maze(PEN).door_exit, (5, 1))
        self.assertEqual(Maze(LAYOUT).door_exit, (13, 11))

    def test_ghost_start_tiles(self):
        self.assertEqual(Maze(PEN).ghost_starts(),
                         {'blinky': (5, 1), 'pinky': (5, 3), 'inky': (3, 3), 'clyde': (7, 3)})
        self.assertEqual(Maze(LAYOUT).ghost_starts(),
                         {'blinky': (13, 11), 'pinky': (13, 14), 'inky': (11, 14), 'clyde': (16, 14)})

    def test_a_maze_with_no_house_has_no_exit_or_starts(self):
        maze = Maze(('#####', '#.P.#', '#####'))
        self.assertIsNone(maze.door_exit)
        self.assertEqual(maze.ghost_starts(), {})

    def test_the_tunnel_is_the_walled_in_part_of_the_tunnel_row(self):
        maze = Maze(LAYOUT)
        for x in range(0, 6):
            self.assertTrue(maze.in_tunnel((x, 14)), x)
        for x in range(22, 28):
            self.assertTrue(maze.in_tunnel((x, 14)), x)
        self.assertFalse(maze.in_tunnel((6, 14)))
        self.assertFalse(maze.in_tunnel((13, 14)))
        self.assertFalse(maze.in_tunnel((3, 5)))
        self.assertFalse(Maze(('#####', '#.P.#', '#####')).in_tunnel((2, 1)))


class MazeRulesTests(unittest.TestCase):
    def test_open_means_not_wall_house_or_door(self):
        maze = Maze(('#####', '#P.H#', '##-##', '#####'))
        self.assertTrue(maze.is_open((1, 1)) and maze.is_open((2, 1)))
        self.assertFalse(maze.is_open((0, 0)))
        self.assertFalse(maze.is_open((3, 1)))
        self.assertFalse(maze.is_open((2, 2)))
        self.assertFalse(maze.is_open((9, 9)))

    def test_step_returns_the_open_neighbour_and_wraps_only_on_the_tunnel_row(self):
        maze = Maze(('#####', ' P.  ', '#####'))
        self.assertEqual(maze.tunnel_row, 1)
        self.assertEqual(maze.step((1, 1), (1, 0)), (2, 1))
        self.assertEqual(maze.step((0, 1), (-1, 0)), (4, 1))
        self.assertEqual(maze.step((4, 1), (1, 0)), (0, 1))
        self.assertIsNone(maze.step((1, 1), (0, -1)))
        self.assertIsNone(Maze(('###', '#P#', '###')).step((1, 1), (1, 0)))

    def test_only_the_tunnel_row_wraps(self):
        maze = Maze((' .. ', '####', ' .. '))
        self.assertEqual(maze.tunnel_row, 0)
        self.assertEqual(maze.step((0, 0), (-1, 0)), (3, 0))
        self.assertIsNone(maze.step((0, 2), (-1, 0)))
        self.assertIsNone(maze.step((3, 2), (1, 0)))

    def test_can_erase_thin_interior_walls_between_corridors(self):
        maze = Maze(THIN)
        self.assertTrue(maze.can_erase((2, 2)))
        self.assertTrue(maze.can_erase((3, 2)))

    def test_cannot_erase_a_corner_so_it_only_joins_corridors(self):
        maze = Maze(THICK)
        self.assertTrue(Maze(THICK).is_open((1, 1)))
        self.assertFalse(maze.can_erase((2, 2)))

    def test_cannot_erase_open_tiles_the_border_or_a_wall_that_would_leave_a_dead_end(self):
        maze = Maze(THIN)
        self.assertFalse(maze.can_erase((1, 1)))
        self.assertFalse(maze.can_erase((0, 2)))
        self.assertFalse(maze.can_erase((3, 0)))
        self.assertFalse(Maze(THICK).can_erase((3, 2)))

    def test_cannot_erase_on_the_tunnel_row(self):
        maze = Maze(ON_THE_TUNNEL_ROW)
        self.assertEqual(maze.tunnel_row, 1)
        self.assertTrue(maze.is_open((2, 1)) and maze.is_open((4, 1)))
        self.assertFalse(maze.can_erase((3, 1)))

    def test_cannot_erase_beside_the_house_or_its_door(self):
        maze = Maze(BY_THE_HOUSE)
        self.assertTrue(maze.is_open((3, 1)) and maze.is_open((3, 3)))
        self.assertFalse(maze.can_erase((3, 2)))


if __name__ == '__main__':
    unittest.main()
