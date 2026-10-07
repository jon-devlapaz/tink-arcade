import curses
import unittest
from unittest.mock import Mock

from tink_pacman.engine import DOWN, LEFT, RIGHT, UP, Game
from tink_pacman.maze import Maze
from tink_pacman.ui import MIN_COLUMNS, MIN_ROWS, Renderer, handle_key, wall_mark


def _fright(game, left):
    game.fright_left = left
    return game


def drawn(rows, columns, game=None, too_small=False):
    screen = Mock()
    screen.getmaxyx.return_value = rows, columns
    Renderer(screen, True).draw(game or Game(), too_small)
    return [call.args for call in screen.addnstr.call_args_list]


class LayoutTests(unittest.TestCase):
    def test_minimum_canvas_is_80_by_40(self):
        self.assertEqual((MIN_COLUMNS, MIN_ROWS), (80, 40))

    def test_everything_is_ascii_and_inside_the_screen(self):
        for rows, columns in ((40, 80), (45, 100)):
            for state in ('playing', 'paused'):
                game = Game()
                game.paused = state == 'paused'
                calls = drawn(rows, columns, game)
                for y, x, text, width, attr in calls:
                    self.assertTrue(text.isascii(), text)
                    self.assertTrue(0 <= y < rows, (y, text))
                    self.assertTrue(0 <= x and x + len(text) <= columns, (x, text))

    def test_title_box_and_maze_marks_are_drawn(self):
        texts = [call[2] for call in drawn(40, 80)]
        self.assertIn('. socratink  /  paper pac-man', texts)
        self.assertTrue(any('PLAY / PAPER' in t for t in texts))
        self.assertIn(' .', texts)
        self.assertIn('()', texts)
        self.assertTrue(any(t in ('O>', '<O', 'O^', 'Ov') for t in texts))

    def test_the_house_door_is_drawn_where_the_door_is(self):
        maze = Game().maze
        calls = drawn(40, 80)
        for x, y in maze.door:
            self.assertIn('--', [c[2] for c in calls if (c[0], c[1]) == (5 + y, 4 + x * 2)])

    def test_walls_are_line_art_not_filled_blocks(self):
        texts = [call[2] for call in drawn(40, 80)]
        self.assertFalse(any('#' in t for t in texts))
        self.assertTrue(any(set(t) <= set('+-| ') and t.strip() for t in texts))

    def test_the_outer_ring_is_left_to_the_box_border(self):
        maze = Game().maze
        calls = drawn(40, 80)
        for call in calls:
            y, x, text = call[0], call[1], call[2]
            if 4 < y < 5 + maze.height and 4 <= x < 4 + maze.width * 2:
                self.assertNotEqual(y, 5, 'top ring row drawn')
                self.assertNotEqual(y, 5 + maze.height - 1, 'bottom ring row drawn')
                self.assertNotIn(x, (4, 4 + (maze.width - 1) * 2), 'side ring column drawn')

    def test_the_legend_sits_in_the_side_panel(self):
        calls = [c for c in drawn(40, 80) if 'pac-man' in c[2] and 'socratink' not in c[2]]
        self.assertTrue(calls)
        for y, x, text, width, attr in calls:
            self.assertGreaterEqual(x, 62)
            self.assertLess(y, 36)
        for mark in ('O>', ' .'):
            legend = [c for c in drawn(40, 80) if c[2] == mark and c[1] >= 62]
            self.assertTrue(legend, f'legend mark {mark!r} missing from the panel')

    def test_the_tunnel_opens_the_box_border(self):
        maze = Game().maze
        calls = drawn(40, 80)
        row = 5 + maze.tunnel_row
        for column in (3, 3 + maze.width * 2 + 1):
            last = [c for c in calls if (c[0], c[1]) == (row, column)][-1]
            self.assertEqual(last[2], ' ', f'border still drawn at column {column}')

    def test_pacman_mark_follows_its_facing(self):
        for direction, mark in ((LEFT, '<O'), (RIGHT, 'O>'), (UP, 'O^'), (DOWN, 'Ov')):
            game = Game()
            game.direction = direction
            self.assertIn(mark, [call[2] for call in drawn(40, 80, game)])

    def test_ghosts_are_drawn_distinct_from_each_other_and_from_pacman(self):
        game = Game()
        calls = drawn(40, 80, game)
        marks = {'blinky': 'Bl', 'pinky': 'Pk', 'inky': 'In', 'clyde': 'Cl'}
        for name, mark in marks.items():
            x, y = game.ghost(name).tile
            at = [c for c in calls if (c[0], c[1]) == (5 + y, 4 + x * 2) and c[2] == mark]
            self.assertTrue(at, f'{name} not drawn at its tile')
            self.assertTrue(at[-1][4] & curses.A_REVERSE)
        pacman = next(c for c in calls if c[2] in ('O>', '<O', 'O^', 'Ov'))
        ghost = next(c for c in calls if c[2] == 'Bl')
        self.assertNotEqual(pacman[4], ghost[4])

    def test_frightened_ghosts_are_blue_marks_that_flash_back_to_their_initials(self):
        game = Game()
        blinky = game.ghost('blinky')
        blinky.frightened = True
        game.fright_flashes = 5
        at = lambda marks, left: [c for c in drawn(40, 80, _fright(game, left)) if c[2] in marks
                                  and (c[0], c[1]) == (5 + blinky.tile[1], 4 + blinky.tile[0] * 2)]
        self.assertTrue(at(('~~',), 3.0))
        self.assertFalse(at(('Bl',), 3.0))
        self.assertTrue(at(('Bl',), 1.2))
        self.assertFalse(at(('~~',), 1.2))

    def test_eyes_are_drawn_as_oo(self):
        game = Game()
        game.ghost('pinky').state = 'eyes'
        x, y = game.ghost('pinky').tile
        self.assertTrue([c for c in drawn(40, 80, game) if c[2] == 'oo' and (c[0], c[1]) == (5 + y, 4 + x * 2)])

    def test_game_over_overlay(self):
        game = Game()
        game.game_over = True
        texts = [call[2] for call in drawn(40, 80, game)]
        self.assertIn('GAME OVER', texts)
        self.assertIn('R restart', ' '.join(texts))

    def test_paused_overlay(self):
        game = Game()
        game.paused = True
        self.assertIn('PAUSED', [call[2] for call in drawn(40, 80, game)])

    def test_undersize_freezes_with_a_message_and_draws_no_maze(self):
        texts = [call[2] for call in drawn(39, 80, too_small=True)]
        self.assertIn('Resize terminal to at least 80 x 40.', texts)
        self.assertNotIn('()', texts)

    def test_pacman_is_distinct_from_dots_in_attributes(self):
        calls = drawn(40, 80)
        pacman = next(c for c in calls if c[2] in ('O>', '<O', 'O^', 'Ov'))
        dot = next(c for c in calls if c[2] == ' .')
        self.assertNotEqual(pacman[4], dot[4])


class KeyTests(unittest.TestCase):
    def test_steering_keys(self):
        for direction, keys in ((UP, (curses.KEY_UP, ord('w'), ord('W'))),
                                (DOWN, (curses.KEY_DOWN, ord('s'), ord('S'))),
                                (LEFT, (curses.KEY_LEFT, ord('a'), ord('A'))),
                                (RIGHT, (curses.KEY_RIGHT, ord('d'), ord('D')))):
            for key in keys:
                game = Mock()
                self.assertTrue(handle_key(game, key))
                game.turn.assert_called_once_with(direction)

    def test_quit_pause_restart(self):
        for key in (ord('q'), ord('Q'), 3):
            self.assertFalse(handle_key(Game(), key))
        game = Mock()
        handle_key(game, ord('p'))
        game.toggle_pause.assert_called_once()
        handle_key(game, ord('R'))
        game.restart.assert_called_once()



BLOCK = ('#######',
         '#.....#',
         '#.###.#',
         '#.###.#',
         '#.###.#',
         '#.....#',
         '#######')
BAR = ('#######',
       '#..#..#',
       '#..#..#',
       '#######')


class WallMarkTests(unittest.TestCase):
    def test_edges_corners_and_hidden_interior_of_a_block(self):
        maze = Maze(BLOCK)
        expected = {(2, 2): '+-', (3, 2): '--', (4, 2): '-+',
                    (2, 3): '| ', (3, 3): None, (4, 3): ' |',
                    (2, 4): '+-', (3, 4): '--', (4, 4): '-+'}
        for tile, mark in expected.items():
            self.assertEqual(wall_mark(maze, tile), mark, tile)

    def test_a_one_tile_wide_wall_is_drawn_on_both_sides(self):
        self.assertEqual(wall_mark(Maze(BAR), (3, 1)), '||')

    def test_ring_tiles_are_never_drawn(self):
        maze = Maze(BLOCK)
        for tile in ((0, 3), (6, 3), (3, 0), (3, 6)):
            self.assertIsNone(wall_mark(maze, tile))

    def test_open_tiles_have_no_wall_mark(self):
        self.assertIsNone(wall_mark(Maze(BLOCK), (1, 1)))


if __name__ == '__main__':
    unittest.main()
