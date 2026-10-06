"""A stand-in for the Jev client: no network, no key, and replies the test controls."""
import threading

from neon_tetris.jev import MODEL, Reply


class FixtureClient:
    """Records every call. `gate` holds replies until the test sets it; `fail` lists 1-based call numbers to fail."""

    def __init__(self, pick=None, gate=None, fail=(), tokens=100, error='Jev request failed or timed out.'):
        self.pick = pick or (lambda criteria: next(iter(criteria)))
        self.gate, self.fail, self.tokens, self.error = gate, set(fail), tokens, error
        self.calls = []
        self.lock = threading.Lock()

    def choose(self, state, criteria, instructions=None):
        with self.lock:
            self.calls.append((state, dict(criteria), instructions))
            number = len(self.calls)
        if self.gate is not None:
            self.gate.wait(5)
        if number in self.fail:
            return Reply(error=self.error)
        return Reply(self.pick(criteria), MODEL, self.tokens)
