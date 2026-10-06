import unittest

from tink_tron.ai import HEIGHT, WIDTH
from tink_tron.jev_routes import (MAX_ROUTES, ROUTE_LENGTH, enumerate_routes, plan_cells, projected_end)

RIGHT, LEFT, UP, DOWN = (1, 0), (-1, 0), (0, -1), (0, 1)


def follow(start, directions):
    cells = plan_cells(start, directions)
    return cells


class RouteTests(unittest.TestCase):
    def routes(self, blocked=(), start=(31, 10), heading=LEFT, rival=(6, 10), **kwargs):
        return enumerate_routes(set(blocked) | {start}, start, heading, rival, **kwargs)

    def test_straight_route_comes_first_and_has_the_full_length(self):
        routes = self.routes()
        name, (directions, text) = next(iter(routes.items()))
        self.assertEqual(name, 'route_0')
        self.assertEqual(directions, [LEFT] * ROUTE_LENGTH)
        self.assertIn('16 steps left', text)

    def test_every_route_is_clear_of_walls_trails_and_itself(self):
        blocked = {(20, y) for y in range(HEIGHT) if y != 10} | {(25, 9)}
        for start, heading in (((31, 10), LEFT), ((2, 2), UP), ((36, 18), DOWN), ((5, 5), RIGHT)):
            routes = self.routes(blocked, start, heading)
            for name, (directions, _) in routes.items():
                cells = follow(start, directions)
                self.assertEqual(len(cells), ROUTE_LENGTH, name)
                self.assertEqual(len(set(cells)), len(cells), name)
                for x, y in cells:
                    self.assertTrue(0 <= x < WIDTH and 0 <= y < HEIGHT, (name, x, y))
                    self.assertNotIn((x, y), blocked, name)

    def test_the_first_step_never_reverses(self):
        for start, heading in (((31, 10), LEFT), ((10, 10), UP)):
            for directions, _ in self.routes(start=start, heading=heading).values():
                self.assertEqual(directions[0], heading)

    def test_stable_and_deterministic(self):
        first, second = self.routes(), self.routes()
        self.assertEqual(first, second)
        self.assertEqual(list(first), [f'route_{i}' for i in range(len(first))])

    def test_cap_and_no_duplicate_paths(self):
        routes = self.routes()
        self.assertLessEqual(len(routes), MAX_ROUTES)
        paths = {tuple(follow((31, 10), d)) for d, _ in routes.values()}
        self.assertEqual(len(paths), len(routes))
        small = self.routes()
        capped = enumerate_routes({(31, 10)}, (31, 10), LEFT, (6, 10))
        self.assertEqual(small, capped)

    def test_a_walled_in_cycle_has_no_routes(self):
        self.assertEqual(self.routes({(30, 10), (31, 9), (31, 11)}), {})
        self.assertEqual(self.routes(start=(0, 0), heading=UP), {})

    def test_a_cycle_at_a_wall_cannot_run_straight_but_can_turn_along_it(self):
        routes = self.routes(start=(2, 10), heading=LEFT)
        self.assertTrue(routes)
        for directions, _ in routes.values():
            self.assertNotEqual(directions, [LEFT] * ROUTE_LENGTH)
            self.assertTrue(all(0 <= x < WIDTH and 0 <= y < HEIGHT for x, y in follow((2, 10), directions)))

    def test_facts_are_computed_by_the_app_on_a_constructed_board(self):
        # An open board: straight left from (31,10) ends at (15,10).
        routes = enumerate_routes({(31, 10)}, (31, 10), LEFT, (6, 10))
        text = routes['route_0'][1]
        self.assertIn('Ends at (15, 10)', text)
        self.assertIn('0 turns', text)
        self.assertIn('to your rival\'s head: 9', text)
        self.assertIn('to the nearest wall: 9', text)
        self.assertIn('not counting it): 743', text)  # 760 cells minus the head and the 16 route cells

    def test_reachable_room_counts_the_pocket_not_the_whole_board(self):
        wall = {(24, y) for y in range(HEIGHT)}  # leaves columns 25..37 on Jev's side: 13 x 20 = 260 cells
        routes = enumerate_routes(wall | {(31, 10)}, (31, 10), LEFT, (6, 10))
        self.assertTrue(routes)
        import re
        for _, text in routes.values():
            room = int(re.search(r'not counting it\): (\d+)', text).group(1))
            self.assertLess(room, 260)
            self.assertGreater(room, 0)

    def test_projected_end_follows_the_plan(self):
        self.assertEqual(projected_end((5, 5), LEFT, []), ((5, 5), LEFT))
        self.assertEqual(projected_end((5, 5), LEFT, [LEFT, UP, UP]), ((4, 3), UP))
        self.assertEqual(plan_cells((5, 5), [LEFT, UP]), [(4, 5), (4, 4)])

    def test_descriptions_are_not_ranked_or_recommending(self):
        for _, text in self.routes().values():
            for word in ('best', 'recommend', 'safest', 'should'):
                self.assertNotIn(word, text.lower())


if __name__ == '__main__':
    unittest.main()
