import random
import unittest
from unittest.mock import patch

from tink_pacman.engine import DOWN, LEFT, RIGHT, UP, Game
from tink_pacman.ghosts import (CHASE, EYES_SPEED, SCATTER, Pen, Waves, chase_target, choose_direction, dot_limits,
                                fright_flashes, fright_speed, fright_time, frightened_direction, ghost_speed, idle_limit,
                                plan_direction, scatter_target, wave_schedule)
from tink_pacman.maze import LAYOUT, Maze

INF = float('inf')
ROOM = ('###########',) + ('#.........#',) * 9 + ('###########',)
PEN = ('###########',
       '#.........#',
       '#.###-###.#',
       '#.#HHHHH#.#',
       '#.#######.#',
       ' ....P.... ',
       '###########')


def make(layout=PEN, schedule=((CHASE, INF),), limits=None, idle=4.0):
    """A game whose wave schedule and release limits are fixed for the test."""
    with patch('tink_pacman.engine.wave_schedule', return_value=schedule), \
            patch('tink_pacman.engine.dot_limits', return_value=limits or {'pinky': 0, 'inky': 30, 'clyde': 60}), \
            patch('tink_pacman.engine.idle_limit', return_value=idle):
        return Game(layout=layout)


def park(game, tile=(9, 2), facing=RIGHT):
    """Leave Pac-Man standing still against a wall."""
    game.pacman, game.direction, game.turn_buffer = tile, facing, None


def ghost_steps(game, name, count, dt=0.02, limit=3000):
    """Run until the ghost has changed tile `count` times; return the tiles it entered."""
    ghost, tiles = game.ghost(name), []
    for _ in range(count):
        before = ghost.tile
        for _ in range(limit):
            game.update(dt)
            if ghost.tile != before:
                tiles.append(ghost.tile)
                break
        else:
            raise AssertionError(f'{name} never left {before}')
    return tiles


class TargetTests(unittest.TestCase):
    def test_scatter_corners_lie_off_the_maze(self):
        maze = Maze(LAYOUT)
        self.assertEqual([scatter_target(n, maze) for n in ('blinky', 'pinky', 'inky', 'clyde')],
                         [(25, -3), (2, -3), (27, 33), (0, 33)])

    def test_blinky_targets_pacman(self):
        self.assertEqual(chase_target('blinky', (5, 5), UP, None, None, None), (5, 5))

    def test_pinky_aims_four_tiles_ahead_and_has_no_up_bug(self):
        for heading, expected in ((RIGHT, (9, 5)), (LEFT, (1, 5)), (DOWN, (5, 9)), (UP, (5, 1))):
            self.assertEqual(chase_target('pinky', (5, 5), heading, None, None, None), expected, heading)

    def test_inky_doubles_the_vector_from_blinky_through_the_tile_two_ahead(self):
        for heading, expected in ((RIGHT, (4, 0)), (UP, (0, -4)), (LEFT, (-4, 0)), (DOWN, (0, 4))):
            self.assertEqual(chase_target('inky', (5, 5), heading, (10, 10), None, None), expected, heading)

    def test_clyde_chases_from_eight_tiles_and_retreats_inside_it(self):
        corner = (0, 33)
        self.assertEqual(chase_target('clyde', (8, 0), LEFT, None, (0, 0), corner), (8, 0))
        self.assertEqual(chase_target('clyde', (6, 6), LEFT, None, (0, 0), corner), (6, 6))
        self.assertEqual(chase_target('clyde', (7, 0), LEFT, None, (0, 0), corner), corner)
        self.assertEqual(chase_target('clyde', (5, 5), LEFT, None, (0, 0), corner), corner)


class JunctionTests(unittest.TestCase):
    def setUp(self):
        self.room = Maze(ROOM)

    def test_takes_the_exit_nearest_the_target(self):
        self.assertEqual(choose_direction(self.room, (5, 5), DOWN, (5, 9)), DOWN)
        self.assertEqual(choose_direction(self.room, (5, 5), DOWN, (9, 6)), RIGHT)

    def test_never_reverses_even_when_the_target_is_behind(self):
        self.assertNotEqual(choose_direction(self.room, (5, 5), RIGHT, (1, 5)), LEFT)

    def test_ties_go_up_then_left_then_down_then_right(self):
        cases = (((5, 5), RIGHT, (1, 5), UP),       # up and down tie
                 ((5, 5), RIGHT, (7, 7), DOWN),     # down and right tie
                 ((5, 5), LEFT, (3, 7), LEFT),      # left and down tie
                 ((5, 5), LEFT, (3, 3), UP))        # up and left tie
        for tile, heading, target, expected in cases:
            self.assertEqual(choose_direction(self.room, tile, heading, target), expected, (heading, target))

    def test_walls_are_never_chosen(self):
        maze = Maze(('#####', '#...#', '##.##', '#####'))
        self.assertEqual(choose_direction(maze, (2, 1), RIGHT, (0, 0)), DOWN)

    def test_a_dead_end_is_the_only_place_a_ghost_turns_back(self):
        maze = Maze(('#####', '#...#', '#####'))
        self.assertEqual(choose_direction(maze, (3, 1), RIGHT, (0, 1)), LEFT)

    def test_a_ghost_decides_one_tile_before_the_intersection(self):
        maze = Maze(('#######', '#.....#', '###.###', '###.###', '#######'))
        self.assertEqual(plan_direction(maze, (2, 1), RIGHT, (3, 3)), DOWN)
        self.assertEqual(plan_direction(maze, (2, 1), RIGHT, (6, 1)), RIGHT)


class WaveTests(unittest.TestCase):
    def test_modes_follow_the_schedule_and_report_changes(self):
        waves = Waves(((SCATTER, 1), (CHASE, 2), (SCATTER, 1), (CHASE, INF)))
        self.assertEqual(waves.mode, SCATTER)
        self.assertFalse(waves.tick(0.5))
        self.assertTrue(waves.tick(0.5))
        self.assertEqual(waves.mode, CHASE)
        self.assertFalse(waves.tick(1.9))
        self.assertTrue(waves.tick(0.2))
        self.assertEqual(waves.mode, SCATTER)
        self.assertFalse(waves.tick(0.85))  # 0.1 s of the last tick already counted toward this period
        self.assertTrue(waves.tick(0.1))
        self.assertEqual(waves.mode, CHASE)
        self.assertFalse(waves.tick(10 ** 6))
        self.assertEqual(waves.mode, CHASE)

    def test_reset_starts_over(self):
        waves = Waves(((SCATTER, 1), (CHASE, INF)))
        waves.tick(5)
        waves.reset()
        self.assertEqual(waves.mode, SCATTER)
        self.assertFalse(waves.tick(0.5))

    def test_level_one_schedule_is_used_on_every_level(self):
        expected = ((SCATTER, 7), (CHASE, 20), (SCATTER, 7), (CHASE, 20), (SCATTER, 5), (CHASE, 20), (SCATTER, 5), (CHASE, INF))
        for level in (1, 2, 5, 30):
            self.assertEqual(wave_schedule(level), expected)


class PenTests(unittest.TestCase):
    def test_limits_by_level(self):
        self.assertEqual(dot_limits(1), {'pinky': 0, 'inky': 30, 'clyde': 60})
        self.assertEqual(dot_limits(2), {'pinky': 0, 'inky': 0, 'clyde': 50})
        for level in (3, 4, 40):
            self.assertEqual(dot_limits(level), {'pinky': 0, 'inky': 0, 'clyde': 0})

    def test_idle_limit_drops_at_level_five(self):
        self.assertEqual([idle_limit(level) for level in (1, 4, 5, 9)], [4, 4, 3, 3])

    def test_level_one_release_order_and_counts(self):
        pen = Pen(dot_limits(1), 4)
        self.assertEqual(pen.start(), ['pinky'])
        for _ in range(29):
            self.assertEqual(pen.dot(), [])
        self.assertEqual(pen.dot(), ['inky'])
        for _ in range(59):
            self.assertEqual(pen.dot(), [])
        self.assertEqual(pen.dot(), ['clyde'])
        self.assertEqual(pen.dot(), [])

    def test_a_zero_limit_cascades(self):
        self.assertEqual(Pen(dot_limits(2), 4).start(), ['pinky', 'inky'])
        self.assertEqual(Pen(dot_limits(3), 4).start(), ['pinky', 'inky', 'clyde'])

    def test_only_the_preferred_ghost_counts_dots(self):
        pen = Pen({'pinky': 3, 'inky': 1, 'clyde': 1}, 4)
        self.assertEqual(pen.start(), [])
        self.assertEqual(pen.dot(), [])
        self.assertEqual(pen.dot(), [])
        self.assertEqual(pen.dot(), ['pinky'])
        self.assertEqual(pen.dot(), ['inky'])
        self.assertEqual(pen.dot(), ['clyde'])

    def test_idle_timer_forces_the_preferred_ghost_out_and_dots_reset_it(self):
        pen = Pen({'pinky': 99, 'inky': 99, 'clyde': 99}, 4)
        self.assertEqual(pen.tick(3.9), [])
        pen.dot()
        self.assertEqual(pen.tick(3.9), [])
        self.assertEqual(pen.tick(0.2), ['pinky'])
        self.assertEqual(pen.tick(3.9), [])
        self.assertEqual(pen.tick(0.2), ['inky'])
        self.assertEqual(pen.tick(4), ['clyde'])
        self.assertEqual(pen.tick(100), [])


class SpeedTests(unittest.TestCase):
    def test_table(self):
        for level, normal, tunnel in ((1, .75, .40), (2, .85, .45), (4, .85, .45), (5, .95, .50), (20, .95, .50), (21, .95, .50), (99, .95, .50)):
            self.assertAlmostEqual(ghost_speed(level, False), normal, msg=level)
            self.assertAlmostEqual(ghost_speed(level, True), tunnel, msg=level)


class GhostsInTheGameTests(unittest.TestCase):
    def test_a_maze_without_a_house_has_no_ghosts(self):
        self.assertEqual(Game(layout=('#####', '#.P.#', '#####')).ghosts, [])

    def test_start_positions_and_states(self):
        g = make()
        blinky, pinky, inky, clyde = (g.ghost(n) for n in ('blinky', 'pinky', 'inky', 'clyde'))
        self.assertEqual((blinky.tile, blinky.direction, blinky.state), ((5, 1), LEFT, 'out'))
        self.assertEqual((pinky.tile, pinky.state), ((5, 3), 'leaving'))
        self.assertEqual((inky.tile, inky.state), ((3, 3), 'house'))
        self.assertEqual((clyde.tile, clyde.state), ((7, 3), 'house'))
        self.assertEqual(g.mode, CHASE)

    def test_first_mode_is_scatter_on_the_real_schedule(self):
        self.assertEqual(Game(layout=PEN).mode, SCATTER)

    def test_pinky_leaves_by_the_door_and_exits_left(self):
        g = make()
        park(g)
        self.assertEqual(ghost_steps(g, 'pinky', 2), [(5, 2), (5, 1)])
        pinky = g.ghost('pinky')
        self.assertEqual((pinky.state, pinky.direction), ('out', LEFT))

    def test_a_dot_limit_releases_inky_and_counts_start_over_for_clyde(self):
        g = make(limits={'pinky': 0, 'inky': 2, 'clyde': 2})
        g.pacman = (4, 5)
        g._eat()
        self.assertEqual(g.ghost('inky').state, 'house')
        g.pacman = (3, 5)
        g._eat()
        self.assertEqual(g.ghost('inky').state, 'leaving')
        self.assertEqual(g.ghost('clyde').state, 'house')
        g.pacman = (2, 5)
        g._eat()
        g.pacman = (6, 5)
        g._eat()
        self.assertEqual(g.ghost('clyde').state, 'leaving')

    def test_the_idle_timer_releases_a_waiting_ghost(self):
        g = make(limits={'pinky': 99, 'inky': 99, 'clyde': 99}, idle=1.0)
        park(g)
        self.assertEqual(g.ghost('pinky').state, 'house')
        for _ in range(60):
            g.update(0.02)
        self.assertEqual(g.ghost('pinky').state, 'leaving')

    def test_blinky_cannot_turn_back_toward_pacman_and_takes_the_long_way_round(self):
        g = make()
        park(g, (9, 2))
        self.assertEqual(ghost_steps(g, 'blinky', 9),
                         [(4, 1), (3, 1), (2, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 5)])

    def test_scatter_sends_a_ghost_toward_its_corner_not_pacman(self):
        # At the junction (1, 5) the left tile leads to Pac-Man and the right tile toward Blinky's corner.
        g = make(schedule=((SCATTER, INF),))
        park(g, (0, 5), UP)
        blinky = g.ghost('blinky')
        blinky.tile, blinky.direction, blinky.plan = (1, 3), DOWN, DOWN
        self.assertEqual(ghost_steps(g, 'blinky', 3), [(1, 4), (1, 5), (2, 5)])

    def test_chase_sends_the_same_ghost_toward_pacman(self):
        g = make(schedule=((CHASE, INF),))
        park(g, (0, 5), UP)
        blinky = g.ghost('blinky')
        blinky.tile, blinky.direction, blinky.plan = (1, 3), DOWN, DOWN
        tiles = []
        for _ in range(600):
            g.update(0.02)
            if g.lives < 3:
                break
            if not tiles or blinky.tile != tiles[-1]:
                tiles.append(blinky.tile)
        self.assertEqual(g.lives, 2, 'Blinky should have reached Pac-Man by turning left at the junction')
        self.assertIn((1, 5), tiles)

    def test_a_mode_change_makes_a_ghost_turn_back_after_its_next_tile(self):
        g = make(schedule=((CHASE, 0.35), (SCATTER, INF)))
        park(g, (9, 2))
        blinky = g.ghost('blinky')
        while g.mode == CHASE:
            g.update(0.02)
        here = blinky.tile
        first, second = ghost_steps(g, 'blinky', 2)
        self.assertNotEqual(first, here)
        self.assertEqual(second, here)

    def test_a_ghost_inside_the_house_when_the_mode_changes_leaves_to_the_right(self):
        limits = {'pinky': 0, 'inky': 1, 'clyde': 99}
        for schedule, expected in ((((SCATTER, 0.2), (CHASE, INF)), RIGHT), (((SCATTER, 100), (CHASE, INF)), LEFT)):
            g = make(schedule=schedule, limits=limits)
            park(g)
            for _ in range(15):
                g.update(0.02)
            g.pacman = (4, 5)
            g._eat()
            park(g)
            for _ in range(400):
                g.update(0.02)
                if g.ghost('inky').state == 'out':
                    break
            self.assertEqual(g.ghost('inky').state, 'out')
            self.assertEqual(g.ghost('inky').direction, expected)

    def test_ghosts_gather_progress_at_their_own_speed(self):
        g = make()
        park(g)
        g.update(0.1)
        self.assertAlmostEqual(g.ghost('blinky').progress, 0.75)
        self.assertAlmostEqual(g.progress, 0.8)
        g = make()
        g.level = 5
        park(g)
        g.update(0.1)
        self.assertAlmostEqual(g.ghost('blinky').progress, 0.95)

    def test_a_ghost_in_the_tunnel_is_slower(self):
        g = make()
        park(g)
        g.ghost('blinky').tile = (3, 5)
        g.update(0.1)
        self.assertAlmostEqual(g.ghost('blinky').progress, 0.40)

    def test_waiting_ghosts_do_not_bank_progress(self):
        g = make()
        park(g)
        for _ in range(10):
            g.update(0.1)
        self.assertEqual(g.ghost('inky').progress, 0)


class TouchTests(unittest.TestCase):
    def test_touching_a_live_ghost_costs_a_life_and_resets_the_round(self):
        g = make(schedule=((SCATTER, 0.1), (CHASE, INF)))
        g.dots.discard((2, 5))
        for _ in range(8):
            g.update(0.02)
        score = g.score
        self.assertGreater(score, 0)
        g.ghost('blinky').tile = g.pacman
        self.assertEqual(g.update(0.0), 'over')
        self.assertEqual((g.lives, g.pacman, g.direction, g.score), (2, (5, 5), LEFT, score))
        self.assertEqual((g.ghost('blinky').tile, g.ghost('blinky').state), ((5, 1), 'out'))
        self.assertEqual((g.ghost('pinky').state, g.ghost('inky').state), ('leaving', 'house'))
        self.assertEqual(g.mode, SCATTER)
        self.assertNotIn((2, 5), g.dots)
        self.assertFalse(g.game_over)

    def test_pacman_walking_into_a_ghost_counts(self):
        g = make()
        g.pacman, g.direction = (4, 5), RIGHT
        g.ghost('blinky').tile, g.ghost('blinky').direction = (5, 5), LEFT
        g.progress = 1.0
        self.assertEqual(g.update(0.0), 'over')
        self.assertEqual(g.lives, 2)

    def test_a_ghost_walking_into_pacman_counts(self):
        g = make()
        park(g, (1, 1), LEFT)
        blinky = g.ghost('blinky')
        blinky.tile, blinky.direction, blinky.plan, blinky.progress = (2, 1), LEFT, LEFT, 1.0
        self.assertEqual(g.update(0.0), 'over')
        self.assertEqual(g.lives, 2)

    def test_a_ghost_still_in_the_house_is_harmless(self):
        g = make()
        park(g)
        g.ghost('inky').tile = g.pacman
        self.assertIsNone(g.update(0.0))
        self.assertEqual(g.lives, 3)

    def test_the_last_life_ends_the_game_and_freezes_everything(self):
        g = make()
        for lives in (2, 1, 0):
            g.ghost('blinky').tile = g.pacman
            self.assertEqual(g.update(0.0), 'over')
            self.assertEqual(g.lives, lives)
        self.assertTrue(g.game_over)
        before = (g.pacman, g.ghost('blinky').tile, g.progress)
        self.assertIsNone(g.update(5))
        self.assertEqual((g.pacman, g.ghost('blinky').tile, g.progress), before)
        self.assertFalse(g.turn(UP))
        self.assertFalse(g.toggle_pause())
        g.restart()
        self.assertEqual((g.game_over, g.lives, g.level, g.score), (False, 3, 1, 0))

    def test_clearing_the_maze_returns_the_ghosts_to_the_house(self):
        layout = ('###########', '#         #', '# ###-### #', '# #HHHHH# #', '# ####### #', '   . P .   ', '###########')
        g = make(layout=layout)
        g.ghost('blinky').tile = (8, 1)
        g.ghost('pinky').state = 'out'
        g.pacman = (3, 5)
        self.assertIsNone(g._eat())
        g.pacman = (7, 5)
        self.assertEqual(g._eat(), 'clear')
        self.assertEqual(g.level, 2)
        self.assertEqual([g.ghost(n).state for n in ('blinky', 'pinky', 'inky', 'clyde')], ['out', 'leaving', 'leaving', 'house'])
        self.assertEqual(g.ghost('blinky').tile, (5, 1))


def play(seed, seconds, schedule=None):
    """A scripted game on the shipped maze: Pac-Man takes random turns from a seeded generator."""
    bot = random.Random(seed)
    game = Game(seed=seed)
    if schedule:
        game.waves = Waves(schedule)
    trace = []
    for _ in range(int(seconds * 60)):
        if bot.random() < 0.05:
            game.turn(bot.choice((UP, DOWN, LEFT, RIGHT)))
        cue = game.update(1 / 60)
        trace.append((game.pacman, game.lives, cue, tuple((g.tile, g.state) for g in game.ghosts)))
        if game.game_over:
            game.restart()
    return game, trace


class RealMazeTests(unittest.TestCase):
    def test_the_same_inputs_give_the_same_game(self):
        self.assertEqual(play(3, 40)[1], play(3, 40)[1])
        self.assertNotEqual(play(3, 40)[1], play(4, 40)[1])

    def test_ghosts_stay_on_legal_tiles_and_never_reverse_in_a_long_chase(self):
        for seed in (1, 2, 3):
            with patch('tink_pacman.engine.wave_schedule', return_value=((CHASE, INF),)), \
                    patch.object(Game, '_frighten', lambda self: None):  # an energizer legitimately turns ghosts around
                self._watch(seed)

    def test_the_same_holds_for_all_four_ghosts_when_pacman_cannot_be_caught(self):
        for seed in (1, 2):
            with patch('tink_pacman.engine.wave_schedule', return_value=((CHASE, INF),)), \
                    patch.object(Game, '_frighten', lambda self: None), \
                    patch.object(Game, '_touch', lambda self: None):
                roaming = self._watch(seed)
            self.assertEqual(roaming, {'blinky', 'pinky', 'inky', 'clyde'})

    def _watch(self, seed):
        bot, game = random.Random(seed), Game(seed=seed)
        roaming = set()
        maze = game.maze
        history = {g.name: [g.tile] for g in game.ghosts}
        lives, moves = game.lives, 0
        for _ in range(60 * 120):
            if bot.random() < 0.05:
                game.turn(bot.choice((UP, DOWN, LEFT, RIGHT)))
            game.update(1 / 60)
            if game.game_over:
                game.restart()
            if game.lives != lives:
                lives = game.lives
                history = {g.name: [g.tile] for g in game.ghosts}
                continue
            for ghost in game.ghosts:
                trail = history[ghost.name]
                if ghost.tile == trail[-1]:
                    continue
                (px, py), (x, y) = trail[-1], ghost.tile
                wrapped = abs(px - x) == maze.width - 1 and py == y
                self.assertTrue(abs(px - x) + abs(py - y) == 1 or wrapped, (ghost.name, trail[-1], ghost.tile))
                if ghost.state == 'out':
                    self.assertTrue(maze.is_open(ghost.tile), (ghost.name, ghost.tile))
                    if len(trail) >= 2:
                        self.assertNotEqual(ghost.tile, trail[-2], f'{ghost.name} reversed at {trail[-1]} (seed {seed})')
                moves += 1
                roaming |= {g.name for g in game.ghosts if g.state == 'out'}
                trail.append(ghost.tile)
                del trail[:-3]
        self.assertGreater(moves, 500, 'the simulation barely moved the ghosts')
        return roaming

    def test_every_ghost_eventually_leaves_the_house_on_the_real_maze(self):
        game = Game()
        for _ in range(60 * 30):
            game.update(1 / 60)
            if game.lives != 3 or all(g.state == 'out' for g in game.ghosts):
                break
        self.assertTrue(game.lives != 3 or all(g.state == 'out' for g in game.ghosts))


PEN_E = PEN[:5] + (' o...P.... ',) + PEN[6:]


class Pick:
    """A stand-in for the random generator that always picks index `n`."""
    def __init__(self, n):
        self.n = n

    def randrange(self, count):
        return self.n


class FrightTableTests(unittest.TestCase):
    def test_seconds_and_flashes_by_level_follow_table_a1(self):
        table = {1: (6, 5), 2: (5, 5), 3: (4, 5), 4: (3, 5), 5: (2, 5), 6: (5, 5), 7: (2, 5), 8: (2, 5), 9: (1, 3),
                 10: (5, 5), 11: (2, 5), 12: (1, 3), 13: (1, 3), 14: (3, 5), 15: (1, 3), 16: (1, 3), 17: (0, 0),
                 18: (1, 3), 19: (0, 0), 20: (0, 0), 21: (0, 0), 99: (0, 0)}
        for level, expected in table.items():
            self.assertEqual((fright_time(level), fright_flashes(level)), expected, level)

    def test_frightened_speed_and_eyes_speed(self):
        self.assertEqual([fright_speed(level) for level in (1, 2, 4, 5, 30)], [.50, .55, .55, .60, .60])
        self.assertEqual(EYES_SPEED, 1.0)

    def test_a_frightened_ghost_tries_a_random_direction_then_turns_clockwise(self):
        room = Maze(ROOM)
        self.assertEqual(frightened_direction(room, (5, 5), RIGHT, Pick(2)), DOWN)
        self.assertEqual(frightened_direction(room, (5, 5), RIGHT, Pick(1)), RIGHT)
        self.assertEqual(frightened_direction(room, (5, 5), RIGHT, Pick(3)), UP)  # left is a reverse; next clockwise is up
        corridor = Maze(('#####', '#...#', '##.##', '#####'))
        self.assertEqual(frightened_direction(corridor, (2, 1), RIGHT, Pick(0)), RIGHT)  # up is a wall; next clockwise is right
        self.assertEqual(frightened_direction(Maze(('#####', '#...#', '#####')), (3, 1), RIGHT, Pick(1)), LEFT)  # dead end


class FrightenedGameTests(unittest.TestCase):
    def test_an_energizer_scores_cues_and_frightens_every_ghost(self):
        g = make(layout=PEN_E)
        g.pacman = (1, 5)
        self.assertEqual(g._eat(), 'switch')
        self.assertEqual(g.score, 50)
        self.assertEqual(g.fright_left, 6)
        self.assertEqual(g.chain, 0)
        self.assertTrue(all(ghost.frightened for ghost in g.ghosts))
        self.assertTrue(g.ghost('blinky').reverse)
        self.assertTrue(g.ghost('inky').flipped)

    def test_from_the_high_levels_an_energizer_only_turns_the_ghosts_around(self):
        g = make(layout=PEN_E)
        g.level = 17
        g._frighten()
        self.assertEqual(g.fright_left, 0)
        self.assertFalse(any(ghost.frightened for ghost in g.ghosts))
        self.assertTrue(g.ghost('blinky').reverse)

    def test_eaten_ghosts_score_200_400_800_1600_and_the_chain_restarts_with_each_energizer(self):
        g = make()
        park(g)
        g._frighten()
        points = []
        for name in ('blinky', 'pinky', 'inky', 'clyde'):
            ghost = g.ghost(name)
            ghost.state, ghost.frightened, ghost.tile = 'out', True, g.pacman
            before = g.score
            self.assertEqual(g._touch(), 'clear')
            points.append(g.score - before)
            self.assertEqual((ghost.state, ghost.frightened), ('eyes', False))
        self.assertEqual(points, [200, 400, 800, 1600])
        g._frighten()
        self.assertEqual(g.chain, 0)

    def test_a_frightened_ghost_is_eaten_even_when_the_energizer_is_eaten_on_its_tile(self):
        g = make(layout=PEN_E)
        g.pacman = (1, 5)
        g.ghost('blinky').tile = (1, 5)
        g.progress = 1.0
        g.direction = LEFT
        g.pacman = (2, 5)
        self.assertEqual(g.update(0.0), 'clear')
        self.assertEqual(g.ghost('blinky').state, 'eyes')
        self.assertEqual(g.score, 50 + 200)

    def test_eyes_are_harmless_and_a_live_ghost_still_is_not(self):
        g = make()
        park(g)
        g.ghost('blinky').state, g.ghost('blinky').tile = 'eyes', g.pacman
        self.assertIsNone(g._touch())
        self.assertEqual(g.lives, 3)
        g.ghost('pinky').state, g.ghost('pinky').tile = 'out', g.pacman
        self.assertEqual(g._touch(), 'over')

    def test_eyes_go_home_are_revived_and_leave_again(self):
        g = make()
        park(g)
        blinky = g.ghost('blinky')
        blinky.state, blinky.frightened, blinky.tile, blinky.direction, blinky.plan = 'eyes', False, (4, 1), RIGHT, RIGHT
        self.assertEqual(ghost_steps(g, 'blinky', 5), [(5, 1), (5, 2), (5, 3), (5, 2), (5, 1)])
        self.assertEqual((blinky.state, blinky.direction, blinky.frightened), ('out', LEFT, False))

    def test_eyes_choose_their_turns_by_the_way_home_not_by_pacman(self):
        # At the junction (1, 5) home is to the right and Pac-Man is to the left.
        g = make(schedule=((CHASE, INF),))
        park(g, (0, 5), UP)
        blinky = g.ghost('blinky')
        blinky.state, blinky.frightened, blinky.tile, blinky.direction, blinky.plan = 'eyes', False, (1, 3), DOWN, DOWN
        self.assertEqual(ghost_steps(g, 'blinky', 3), [(1, 4), (1, 5), (2, 5)])

    def test_eyes_and_frightened_ghosts_move_at_their_own_speeds(self):
        g = make()
        park(g)
        g._frighten()
        g.ghost('blinky').state, g.ghost('blinky').frightened = 'eyes', False
        g.update(0.1)
        self.assertAlmostEqual(g.ghost('pinky').progress, 0.5)  # frightened, level 1
        self.assertAlmostEqual(g.ghost('blinky').progress, 0.0)  # eyes covered a whole tile at full speed
        self.assertEqual(g.ghost('blinky').tile, (4, 1))

    def test_the_wave_timer_waits_for_the_fright_and_nobody_turns_back_when_it_ends(self):
        g = make(schedule=((CHASE, 0.3), (SCATTER, INF)))
        park(g)
        g._frighten()
        for _ in range(50):
            g.update(0.02)
        self.assertEqual(g.mode, CHASE)
        self.assertAlmostEqual(g.fright_left, 5.0, places=1)
        g.fright_left = 0.05
        for _ in range(5):
            g.update(0.02)
        self.assertEqual(g.fright_left, 0)
        self.assertFalse(any(ghost.frightened or ghost.reverse for ghost in g.ghosts))
        self.assertEqual(g.mode, CHASE)
        for _ in range(20):
            g.update(0.02)
        self.assertEqual(g.mode, SCATTER)

    def test_a_frightened_ghost_turns_back_once_and_then_never_reverses(self):
        with patch.object(Game, '_touch', lambda self: None):
            g = make()
            park(g)
            blinky = g.ghost('blinky')
            start = blinky.tile
            g._frighten()
            tiles = [start] + ghost_steps(g, 'blinky', 12)
        self.assertNotEqual(tiles[1], start)
        self.assertEqual(tiles[2], start)  # the forced turn, one tile after the signal
        for i in range(3, len(tiles)):
            self.assertNotEqual(tiles[i], tiles[i - 2], f'reversed at step {i}: {tiles}')

    def test_ghosts_waiting_in_the_house_come_out_frightened(self):
        g = make(limits={'pinky': 0, 'inky': 1, 'clyde': 99})
        park(g)
        g._frighten()
        g.pacman = (4, 5)
        g._eat()
        park(g)
        for _ in range(100):
            g.update(0.02)
            if g.ghost('inky').state == 'out':
                break
        self.assertEqual((g.ghost('inky').state, g.ghost('inky').frightened), ('out', True))

    def test_clearing_the_maze_ends_the_fright(self):
        layout = ('###########', '#         #', '# ###-### #', '# #HHHHH# #', '# ####### #', '   . P .   ', '###########')
        g = make(layout=layout)
        g._frighten()
        g.pacman = (3, 5)
        g._eat()
        g.pacman = (7, 5)
        self.assertEqual(g._eat(), 'clear')
        self.assertEqual(g.fright_left, 0)
        self.assertFalse(any(ghost.frightened for ghost in g.ghosts))

    def test_the_generator_restarts_on_every_new_round(self):
        g = Game(seed=5)
        g.rng.random()
        g.rng.random()
        g.new_round()
        self.assertEqual(g.rng.random(), random.Random(5).random())

    def test_flashing_happens_only_in_the_last_moments(self):
        g = make()
        g.fright_flashes = 5
        cases = ((0.0, False), (3.0, False), (5.9, False), (1.3, False), (1.2, True), (1.1, False), (0.2, True), (0.1, False))
        for left, expected in cases:
            g.fright_left = left
            self.assertEqual(g.flashing, expected, left)


class FrightOnTheRealMazeTests(unittest.TestCase):
    def _wander(self, seed):
        bot = random.Random(100 + seed)
        with patch.object(Game, '_touch', lambda self: None):
            g = Game(seed=seed)
            for _ in range(60 * 3):
                g.update(1 / 60)
            g._frighten()
            tiles = []
            for _ in range(60 * 8):
                if bot.random() < 0.05:
                    g.turn(bot.choice((UP, DOWN, LEFT, RIGHT)))
                g.update(1 / 60)
                tiles.append(tuple(x.tile for x in g.ghosts))
        return tiles

    def test_frightened_ghosts_turn_back_once_then_never_reverse_on_the_real_maze(self):
        for seed in (1, 2, 3):
            with patch.object(Game, '_touch', lambda self: None):
                g = Game(seed=seed)
                for _ in range(60 * 15):  # long enough for all four to be out
                    g.update(1 / 60)
                roaming = [x for x in g.ghosts if x.state == 'out']
                self.assertGreaterEqual(len(roaming), 3)
                g._frighten()
                trails = {x.name: [x.tile] for x in roaming}
                for _ in range(60 * 5):
                    g.update(1 / 60)
                    for x in roaming:
                        if x.tile != trails[x.name][-1]:
                            trails[x.name].append(x.tile)
            for name, trail in trails.items():
                self.assertGreater(len(trail), 8, name)
                self.assertEqual(trail[2], trail[0], f'{name} did not turn back (seed {seed})')
                for i in range(3, len(trail)):
                    self.assertNotEqual(trail[i], trail[i - 2], f'{name} reversed at step {i} (seed {seed})')

    def test_frightened_wandering_repeats_for_a_seed_and_differs_between_seeds(self):
        self.assertEqual(self._wander(1), self._wander(1))
        self.assertNotEqual(self._wander(1), self._wander(2))


if __name__ == '__main__':
    unittest.main()
