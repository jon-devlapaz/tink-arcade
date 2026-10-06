#!/usr/bin/env python3
"""Measure real Jev's latency and token use on realistic Tron requests. BILLED: needs --live and TYPESAFE_API_KEY.

Requests are captured from an offline game (a fixture opponent plays, a scripted human steers), then sent to real
Jev one at a time, as the game does. The key is read from the environment and never printed or written.
Not part of the routine suite. Writes runs/tron-vs-jev/04-test/output/live-latency.json.
"""
import argparse
import json
import os
from pathlib import Path
import random
import re
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from neon_tetris.jev import Cost, JevClient, MODEL, Worker  # noqa: E402
from tests.tron_jev_fixture import FixtureClient  # noqa: E402
from tink_tron.ai import choose  # noqa: E402
from tink_tron.engine import Game, STEP  # noqa: E402
from tink_tron.jev_match import INSTRUCTIONS, JevPilot, TronClient  # noqa: E402
from tink_tron.jev_routes import REQUEST_AT, ROUTE_LENGTH  # noqa: E402

OUTPUT = ROOT / 'runs/tron-vs-jev/04-test/output/live-latency.json'


def capture(count):
    """The first `count` requests the game would send, from an offline game with a scripted human."""
    room = lambda criteria: max(criteria, key=lambda name: int(re.search(r'not counting it\): (\d+)', criteria[name]).group(1)))
    fixture = FixtureClient(pick=room)
    pilot = JevPilot(Worker(TronClient(fixture)))
    game = Game(1, opponent=pilot)
    rng = random.Random(1)
    for _ in range(20000):
        if len(fixture.calls) >= count:
            break
        pilot.collect(game)
        pilot.maybe_request(game)
        deadline = time.monotonic() + 2
        while pilot.worker.busy and time.monotonic() < deadline:
            pilot.collect(game)
            time.sleep(0.001)
        if game.round_over:
            game.next_round()
        elif not pilot.holds(game):
            game.turn(0, choose(set(game.trails), game.heads[0], game.heads[1], game.dirs[0], 'normal', rng))
            game.update(STEP)
    return [(state, criteria) for state, criteria, _ in fixture.calls[:count]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='make real, billed calls to Jev')
    parser.add_argument('--calls', type=int, default=6)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    requests = capture(args.calls)
    sizes = [len(json.dumps({'state': s, 'criteria': c})) for s, c in requests]
    print(f'Captured {len(requests)} realistic requests (payload {min(sizes)}-{max(sizes)} bytes, '
          f'{min(len(c) for _, c in requests)}-{max(len(c) for _, c in requests)} routes each).')
    if not args.live:
        print('Dry run: pass --live to send them to real Jev (billed).')
        return 0
    key = os.environ.get('TYPESAFE_API_KEY')
    if not key:
        print('Set TYPESAFE_API_KEY to measure live.', file=sys.stderr)
        return 1
    client, cost, rows = TronClient(JevClient(key)), Cost(), []
    for number, (state, criteria) in enumerate(requests, 1):
        start = time.perf_counter()
        reply = client.choose(state, criteria)
        seconds = time.perf_counter() - start
        cost.record(reply)
        rows.append(dict(call=number, kind='opening' if number == 1 else 'mid-round', seconds=round(seconds, 3),
                         routes=len(criteria), input_tokens=reply.input_tokens, model=reply.model,
                         choice_valid=reply.choice in criteria, error=reply.error))
        print(f'  call {number}: {seconds:6.2f}s  tokens={reply.input_tokens}  valid={reply.choice in criteria}  {reply.error}')
    good = [r['seconds'] for r in rows if not r['error']]
    budget = REQUEST_AT * STEP
    summary = dict(model=MODEL, calls=len(rows), succeeded=len(good), route_length=ROUTE_LENGTH, request_at=REQUEST_AT,
                   step_seconds=STEP, budget_seconds=round(budget, 3), route_seconds=round(ROUTE_LENGTH * STEP, 3),
                   median_seconds=round(statistics.median(good), 3) if good else None,
                   max_seconds=max(good) if good else None,
                   within_budget=sum(s <= budget for s in good), estimated_cost=cost.display().replace('Est. ', ''),
                   when=time.strftime('%Y-%m-%d'), rows=rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + '\n')
    print(f"Median {summary['median_seconds']}s, max {summary['max_seconds']}s; the early-request budget is {budget:.2f}s "
          f"({summary['within_budget']} of {len(good)} replies fit). {cost.display()}. Wrote {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
