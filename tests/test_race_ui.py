import curses
import io
import unittest
from unittest.mock import Mock, patch

from neon_tetris import __main__
from neon_tetris.race import Race
from neon_tetris.race_ui import RaceRenderer, _run_loop, handle_key
from test_race import ManualWorker


class Screen:
    def __init__(self, rows=30, columns=80):
        self.rows, self.columns = rows, columns
        self.erase()

    def erase(self):
        self.cells = [[' '] * self.columns for _ in range(self.rows)]

    def getmaxyx(self):
        return self.rows, self.columns

    def addnstr(self, y, x, text, width, attr):
        assert 0 <= y < self.rows and 0 <= x < self.columns
        for offset, char in enumerate(text[:width]):
            assert x + offset < self.columns
            self.cells[y][x + offset] = char

    def refresh(self):
        pass

    def content(self):
        return '\n'.join(''.join(row) for row in self.cells)


class RaceUITests(unittest.TestCase):
    def setUp(self):
        self.race = Race(ManualWorker(), 1)
        self.audio = Mock(status='Sound off')

    def test_80_by_30_has_full_boards_status_cost_and_controls(self):
        screen = Screen()
        renderer = RaceRenderer(screen, no_color=True)
        renderer.draw(self.race, False, 'Sound off')
        text = screen.content()
        for label in ['YOU', 'JEV', '0/20 lines', 'HOLD', 'NEXT', 'Est. $', 'P pause', 'Q quit']:
            self.assertIn(label, text)
        for y in range(4, 24):
            self.assertEqual(screen.cells[y][1], '|')
            self.assertEqual(screen.cells[y][41], '|')
            self.assertEqual(screen.cells[y][22], '|')
            self.assertEqual(screen.cells[y][62], '|')

    def test_error_winner_and_small_screen_messages(self):
        screen = Screen()
        renderer = RaceRenderer(screen, no_color=True)
        self.race.error = 'Jev timed out'
        renderer.draw(self.race, False)
        self.assertIn('Enter retry', screen.content())
        self.assertIn('Jev timed out', screen.content())
        self.race.error, self.race.winner = '', 'You win'
        renderer.draw(self.race, False)
        self.assertIn('You win', screen.content())
        small = Screen(10, 60)
        RaceRenderer(small, no_color=True).draw(self.race, True)
        self.assertIn('Both boards are frozen', small.content())

    def test_global_controls_and_no_input_during_pause_error_or_resize(self):
        for key in [ord('p'), ord('P')]:
            handle_key(self.race, key, self.audio)
        self.assertFalse(self.race.paused)
        for attr in ['paused', 'too_small', 'error']:
            setattr(self.race, attr, True)
            self.assertIsNone(handle_key(self.race, ord(' '), self.audio)[1])
            setattr(self.race, attr, False)
        self.race.error = 'timeout'
        handle_key(self.race, 10, self.audio)
        self.assertEqual(self.race.error, '')
        before = self.race.epoch
        handle_key(self.race, ord('R'), self.audio)
        self.assertEqual(self.race.epoch, before + 1)
        self.assertFalse(handle_key(self.race, ord('Q'), self.audio)[0])
        self.assertFalse(handle_key(self.race, 3, self.audio)[0])

    def test_loop_handles_input_while_provider_is_waiting_and_quits(self):
        screen = Mock()
        screen.getmaxyx.return_value = (30, 80)
        screen.getch.side_effect = [-1, ord('a'), -1, ord('p'), -1, ord('q')]
        renderer = Mock()
        initial_x = self.race.human.active.x
        with patch('neon_tetris.race_ui.time.sleep'):
            _run_loop(screen, renderer, self.race, self.audio)
        self.assertEqual(len(self.race.worker.calls), 1)
        self.assertTrue(self.race.paused)
        self.assertEqual(self.race.human.active.x, initial_x - 1)
        self.assertEqual(renderer.draw.call_count, 3)

    def test_resize_does_not_apply_catchup_time(self):
        screen = Mock()
        screen.getmaxyx.side_effect = [(30, 80), (20, 60), (30, 80), (30, 80)]
        screen.getch.side_effect = [-1, ord(' '), -1, -1, ord('q')]
        clock = [0, .01, .012, 10, 10.002, 20, 20.002, 20.02]
        with patch('neon_tetris.race_ui.time.monotonic', side_effect=clock), patch('neon_tetris.race_ui.time.sleep'):
            _run_loop(screen, Mock(), self.race, self.audio)
        self.assertEqual(self.race.human.score, 0)
        self.assertEqual(self.race.human.active.y, 0)

    def test_cli_routes_versus_and_prints_final_cost(self):
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
             patch.dict('os.environ', {'TYPESAFE_API_KEY': 'test'}), \
             patch('curses.wrapper', return_value=('', 'Est. $0.00000100')) as wrapper, \
             patch('sys.stdout', new_callable=io.StringIO) as output:
            output.isatty = lambda: True
            self.assertEqual(__main__.main(['--versus-jev', '--seed', '1', '--no-sound']), 0)
            self.assertIn('Est. $', output.getvalue())
        self.assertEqual(wrapper.call_args.args[0].__module__, 'neon_tetris.race_ui')

    def test_cli_missing_key_does_not_open_curses(self):
        with patch('sys.stdin.isatty', return_value=True), patch('sys.stdout.isatty', return_value=True), \
             patch.dict('os.environ', {}, clear=True), patch('curses.wrapper') as wrapper, \
             patch('sys.stderr', new_callable=io.StringIO) as error:
            self.assertEqual(__main__.main(['--versus-jev']), 1)
        self.assertIn('TYPESAFE_API_KEY', error.getvalue())
        wrapper.assert_not_called()
