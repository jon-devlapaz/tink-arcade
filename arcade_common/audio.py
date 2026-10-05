"""Bundled mechanical keyboard clicks with bounded, responsive playback."""

from pathlib import Path
import shutil
import subprocess
import sys
import time

SOUND_DIR = Path(__file__).resolve().parent / "sounds"
# Sample filename and priority within one input/render batch.
CUES = {
    "move": ("tactile.wav", 1),
    "rotate": ("mx-blue.wav", 2),
    "place": ("enter.wav", 3),
    "switch": ("mx-blue.wav", 2),
    "clear": ("clear.wav", 5),
    "over": ("enter.wav", 4),
}
MAX_CUE_AGE = 0.15


class _ProcessPlayer:
    """Portable fallback: one child, polled rather than waited on during play."""

    def __init__(self):
        self.command = None
        for name, flags in (("paplay", ()), ("aplay", ("-q",))):
            executable = shutil.which(name)
            if executable:
                self.command = (executable, *flags)
                break
        if self.command is None:
            raise OSError("No audio player found (paplay or aplay).")
        self._process = None
        self._started = 0.0
        self._stopping = None
        self._killed = False

    @property
    def ready(self):
        return self._process is None

    def play(self, path):
        if not self.ready:
            raise RuntimeError("Audio fallback is still busy.")
        self._process = subprocess.Popen(
            [*self.command, str(path)], stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
        )
        self._started = time.monotonic()

    def tick(self):
        if self._process is None:
            return
        code = self._process.poll()
        if code is None:
            if self._stopping is not None:
                if not self._killed and time.monotonic() - self._stopping >= 0.25:
                    self._process.kill()
                    self._killed = True
            elif time.monotonic() - self._started > 2:
                raise OSError("Audio player timed out.")
            return
        self._process = None
        cancelled = self._stopping is not None
        self._stopping = None
        self._killed = False
        if code != 0 and not cancelled:
            raise OSError(f"Audio player exited with status {code}.")

    def stop(self):
        if self._process is not None and self._process.poll() is None and self._stopping is None:
            self._process.terminate()
            self._stopping = time.monotonic()

    def close(self):
        self.stop()
        if self._process is not None:
            try:
                self._process.wait(timeout=0.25)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=0.25)
            self._process = None


def _make_backend(paths):
    if sys.platform == "darwin":
        from ._mac_audio import MacPlayer
        return MacPlayer(paths)
    return _ProcessPlayer()


class KeyboardAudio:
    """Coalesce each input batch; never build a stale sound backlog."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.muted = False
        self.warning = ""
        self._closed = False
        self._backend = None
        self._pending = None
        if not enabled:
            return
        try:
            paths = tuple(dict.fromkeys(SOUND_DIR / name for name, _ in CUES.values()))
            for path in paths:
                if not path.is_file():
                    raise OSError(f"Missing keyboard sound: {path.name}")
            self._backend = _make_backend(paths)
        except OSError as error:
            self.warning = str(error)

    @property
    def audible(self):
        return self.enabled and not (self.muted or self.warning or self._closed)

    @property
    def status(self):
        if self.warning:
            return "key sound unavailable"
        if not self.enabled or self._closed:
            return "key sound off"
        return "key sound muted [M]" if self.muted else "key sound on [M]"

    def play(self, cue):
        if cue not in CUES:
            raise ValueError(f"Unknown keyboard sound: {cue}")
        if self.audible and (self._pending is None or CUES[cue][1] >= CUES[self._pending[0]][1]):
            self._pending = (cue, time.monotonic())

    def tick(self):
        if self._backend is None:
            return
        try:
            self._backend.tick()
            if self._pending and time.monotonic() - self._pending[1] > MAX_CUE_AGE:
                self._pending = None
            if self.audible and self._pending and self._backend.ready:
                cue, _ = self._pending
                self._pending = None
                self._backend.play(SOUND_DIR / CUES[cue][0])
        except OSError as error:
            self.warning = str(error)
            self._pending = None
            self._backend.close()
            self._backend = None

    def stop(self):
        self._pending = None
        if self._backend is not None:
            self._backend.stop()

    def toggle(self):
        if self.enabled and not self.warning and not self._closed:
            self.muted = not self.muted
            self.stop()
            if not self.muted:
                self.play("switch")

    def close(self):
        self._closed = True
        self._pending = None
        if self._backend is not None:
            self._backend.close()
            self._backend = None

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        self.close()
