from decimal import Decimal
import json
import threading
import unittest
import http.client
import http.server
import time
from unittest.mock import Mock, patch

from neon_tetris.jev import Cost, JevClient, MODEL, Reply, Worker


class CostTests(unittest.TestCase):
    def test_tiny_costs_accumulate_across_calls_without_rounding(self):
        cost = Cost()
        for _ in range(10):
            cost.record(Reply(model=MODEL, input_tokens=1))
        self.assertEqual(cost.usd, Decimal('0.00000042'))
        self.assertIn('0.00000042', cost.display())
        self.assertFalse(cost.incomplete)

    def test_missing_invalid_and_unknown_usage_never_looks_free(self):
        for tokens, model in [(None, MODEL), (-1, MODEL), (True, MODEL), (1.2, MODEL), (100, 'new-model')]:
            with self.subTest(tokens=tokens, model=model):
                cost = Cost()
                cost.record(Reply(model=model, input_tokens=tokens))
                self.assertIn('unknown', cost.display())
                cost.record(Reply(model=MODEL, input_tokens=100))
                self.assertIn('unknown', cost.display())
                self.assertGreater(cost.usd, 0)

    def test_zero_reported_usage_and_inflight_cost(self):
        cost = Cost()
        cost.record(Reply(model=MODEL, input_tokens=0))
        self.assertFalse(cost.incomplete)
        self.assertIn('pending', cost.display(pending=True))


class ClientTests(unittest.TestCase):
    def response(self, result, status=200):
        connection = Mock()
        connection.getresponse.return_value = Mock(
            read=Mock(return_value=json.dumps(result).encode()), status=status)
        return connection

    def test_request_contract_and_usage(self):
        result = dict(model=MODEL, usage=dict(input_tokens=123), answers=dict(move=dict(type='choice', choice='left')))
        connection = self.response(result)
        with patch('http.client.HTTPSConnection', return_value=connection) as factory:
            reply = JevClient('test-key').choose({'board': ['....']}, {'left': 'drop left'})
        data = json.loads(connection.request.call_args.kwargs['body'])
        self.assertEqual(data['questions']['move']['criteria'], {'left': 'drop left'})
        self.assertEqual(data['model'], MODEL)
        self.assertEqual(reply.input_tokens, 123)
        self.assertEqual(reply.choice, 'left')
        self.assertEqual(factory.call_args.kwargs['timeout'], 10)
        connection.close.assert_called_once()

    def test_timeout_and_network_failures_do_not_retry_or_leak(self):
        for error in [TimeoutError('secret'), OSError('secret'), http.client.BadStatusLine('secret')]:
            connection = self.response({})
            connection.getresponse.side_effect = error
            with patch('http.client.HTTPSConnection', return_value=connection):
                reply = JevClient('test-key').choose({}, {'x': 'drop'})
            self.assertEqual(connection.request.call_count, 1)
            self.assertTrue(reply.error)
            self.assertNotIn('secret', reply.error)
            self.assertIsNone(reply.input_tokens)

    def test_http_error_does_not_follow_redirects_or_retry(self):
        for status in (301, 401, 429, 500):
            connection = self.response({}, status)
            with patch('http.client.HTTPSConnection', return_value=connection):
                reply = JevClient('test-key').choose({}, {'x': 'drop'})
            self.assertIn(str(status), reply.error)
            self.assertEqual(connection.request.call_count, 1)

    def test_slow_response_obeys_total_deadline(self):
        class Slow(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                self.send_response(200)
                self.end_headers()
                try:
                    for _ in range(30):
                        self.wfile.write(b' ')
                        self.wfile.flush()
                        time.sleep(.02)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, *_):
                pass

        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Slow)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=.15)
            with patch('http.client.HTTPSConnection', return_value=connection):
                start = time.monotonic()
                reply = JevClient('test-key', timeout=.15).choose({}, {'x': 'drop'})
                elapsed = time.monotonic() - start
            self.assertIn('timed out', reply.error)
            self.assertLess(elapsed, .5)
        finally:
            server.shutdown()
            server.server_close()

    def test_invalid_reply_preserves_reported_usage(self):
        result = dict(model=MODEL, usage=dict(input_tokens=123), answers=dict(move=dict(choice='bad')))
        with patch('http.client.HTTPSConnection', return_value=self.response(result)):
            reply = JevClient('test-key').choose({}, {'x': 'drop'})
        self.assertTrue(reply.error)
        self.assertEqual(reply.input_tokens, 123)

    def test_malformed_shapes_are_errors(self):
        for result in [[], {}, {'answers': []}, {'answers': {'move': None}}]:
            with patch('http.client.HTTPSConnection', return_value=self.response(result)):
                self.assertTrue(JevClient('test-key').choose({}, {'x': 'drop'}).error)

    def test_empty_key_fails_before_network(self):
        with self.assertRaises(ValueError):
            JevClient('')


class WorkerTests(unittest.TestCase):
    def test_single_request_and_exactly_once_delivery(self):
        release = threading.Event()
        client = Mock()
        client.choose.side_effect = lambda *_: (release.wait(2), Reply('x', MODEL, 1))[1]
        worker = Worker(client)
        try:
            self.assertTrue(worker.submit((1, 1), {}, {'x': 'drop'}))
            self.assertFalse(worker.submit((2, 1), {}, {'x': 'drop'}))
            self.assertIsNone(worker.poll())
        finally:
            release.set()
        item = worker.results.get(timeout=2)
        worker.results.put(item)
        self.assertIsNotNone(worker.poll())
        self.assertIsNone(worker.poll())
        self.assertFalse(worker.busy)

    def test_worker_exception_becomes_visible_reply(self):
        client = Mock()
        client.choose.side_effect = RuntimeError('private details')
        worker = Worker(client)
        worker.submit((1, 1), {}, {})
        identity, reply = worker.results.get(timeout=2)
        self.assertEqual(identity, (1, 1))
        self.assertTrue(reply.error)
        self.assertNotIn('private', reply.error)
