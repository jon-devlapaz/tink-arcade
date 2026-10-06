"""One TypeSafe request at a time, with explicit failures and usage accounting."""

from dataclasses import dataclass
from decimal import Decimal
import json
import http.client
import socket
import queue
import threading

MODEL = 'jev-1.13.0'
PRICE_SOURCE = 'https://docs.typesafe.ai/models.md (checked 2026-10-03)'
INPUT_USD_PER_MILLION = {MODEL: Decimal('0.042')}


TETRIS_INSTRUCTIONS = ('Choose the best legal Tetris move to race to 20 cleared lines. '
                       'Clear lines, avoid covered empty cells and topping out, and keep the stack low. '
                       'x=0 is left, y=0 is top. Each placement rotates, moves and hard-drops '
                       'the current piece. You decide the move; options are not ranked.')


@dataclass(frozen=True)
class Reply:
    choice: str = ''
    model: str = ''
    input_tokens: int | None = None
    error: str = ''


class Cost:
    def __init__(self):
        self.usd = Decimal(0)
        self.incomplete = False
        self.responses = 0
        self.model = MODEL

    def record(self, reply):
        self.responses += 1
        if reply.model:
            self.model = reply.model
        price = INPUT_USD_PER_MILLION.get(reply.model)
        tokens = reply.input_tokens
        if price is None or type(tokens) is not int or tokens < 0:
            self.incomplete = True
        else:
            self.usd += price * tokens / Decimal(1_000_000)

    def display(self, pending=False):
        suffix = ' + unknown' if self.incomplete else ''
        if pending:
            suffix += ' + pending'
        return f'Est. ${self.usd:.8f}{suffix}'


class JevClient:
    def __init__(self, key, model=MODEL, timeout=10):
        if not key:
            raise ValueError('Set TYPESAFE_API_KEY to play against Jev.')
        self.key = key
        self.model = model
        self.timeout = timeout

    def choose(self, state, criteria, instructions=TETRIS_INSTRUCTIONS):
        body = json.dumps({
            'model': self.model, 'state': state,
            'questions': {'move': {
                'type': 'choice',
                'instructions': instructions,
                'criteria': criteria,
            }},
        }).encode()
        connection = http.client.HTTPSConnection('api.typesafe.ai', timeout=self.timeout)
        expired = threading.Event()
        connected_socket = []

        def abort():
            expired.set()
            if connected_socket:
                try:
                    connected_socket[0].shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
            connection.close()

        deadline = threading.Timer(self.timeout, abort)
        deadline.daemon = True
        deadline.start()
        try:
            connection.connect()
            connected_socket.append(connection.sock)
            if expired.is_set():
                raise TimeoutError
            connection.request('POST', '/v1/systemone', body=body,
                               headers={'Authorization': f'Bearer {self.key}',
                                        'Content-Type': 'application/json'})
            response = connection.getresponse()
            raw = response.read(1_000_001)
            if expired.is_set():
                raise TimeoutError
            if response.status != 200:
                return Reply(error=f'Jev HTTP {response.status}. Check access or retry.')
            if len(raw) > 1_000_000:
                return Reply(error='Jev response was too large.')
            result = json.loads(raw)
        except (TimeoutError, OSError, http.client.HTTPException):
            return Reply(error='Jev request failed or timed out.')
        except (ValueError, UnicodeError):
            return Reply(error='Jev returned invalid JSON.')
        finally:
            deadline.cancel()
            connection.close()
        if not isinstance(result, dict):
            return Reply(error='Jev returned an invalid response.')
        model = result.get('model')
        model = model if isinstance(model, str) else ''
        usage = result.get('usage')
        tokens = usage.get('input_tokens') if isinstance(usage, dict) else None
        answers = result.get('answers')
        answer = answers.get('move') if isinstance(answers, dict) else None
        choice = answer.get('choice') if isinstance(answer, dict) else None
        if not isinstance(choice, str) or choice not in criteria:
            return Reply(model=model, input_tokens=tokens, error='Jev returned an invalid move.')
        return Reply(choice, model, tokens)


class Worker:
    """The game thread submits copied data; only it reads and applies results."""

    def __init__(self, client):
        self.client = client
        self.results = queue.Queue(maxsize=1)
        self.busy = False

    def submit(self, identity, state, criteria):
        if self.busy:
            return False
        self.busy = True

        def run():
            try:
                reply = self.client.choose(state, criteria)
            except Exception:
                # Provider exceptions must not silently leave a match waiting forever.
                reply = Reply(error='Jev worker failed. Retry or quit.')
            self.results.put((identity, reply))

        threading.Thread(target=run, daemon=True, name='jev-request').start()
        return True

    def poll(self):
        try:
            item = self.results.get_nowait()
        except queue.Empty:
            return None
        self.busy = False
        return item
