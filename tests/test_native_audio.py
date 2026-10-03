"""Opt-in hardware check: NEON_TETRIS_AUDIO_TESTS=1 python3 -m unittest discover -s tests."""

import ctypes as C
import os
import sys
import time
import unittest

from neon_tetris.audio import CUES, SOUND_DIR, KeyboardAudio


@unittest.skipUnless(sys.platform == "darwin" and os.environ.get("NEON_TETRIS_AUDIO_TESTS") == "1",
                     "set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples")
class NativeAudioIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.audio = KeyboardAudio()
        self.addCleanup(self.audio.close)
        self.assertTrue(self.audio.audible, self.audio.warning)
        self.player = self.audio._backend
        self.objc = self.player._objc
        for voices in self.player._voices.values():
            for voice in voices:
                self.objc.send(voice.handle, "setMeteringEnabled:", None, C.c_bool(True))

    def assert_sample_renders(self, cue):
        self.audio.play(cue)
        self.audio.tick()
        self.assertFalse(self.audio.warning, self.audio.warning)
        voices = self.player._voices[SOUND_DIR / CUES[cue][0]]
        voice = max(voices, key=lambda v: v.order)
        duration = self.objc.send(voice.handle, "duration", C.c_double)
        self.assertTrue(0 < duration < 0.5)
        deadline = time.monotonic() + duration + 0.2
        advanced = False
        peak = -160.0
        while time.monotonic() < deadline:
            self.audio.tick()
            self.assertFalse(self.audio.warning, self.audio.warning)
            advanced |= self.objc.send(voice.handle, "currentTime", C.c_double) > 0.01
            self.objc.send(voice.handle, "updateMeters", None)
            peak = max(peak, self.objc.send(voice.handle, "peakPowerForChannel:",
                                           C.c_float, C.c_size_t(0)))
            # Match the real curses loop; do not supply an extra Cocoa run loop in the test.
            time.sleep(1 / 60)
        self.assertTrue(advanced, f"{cue}: play succeeded but playback never advanced")
        self.assertGreater(peak, -80.0, f"{cue}: no rendered signal (peak {peak} dB)")

    def test_each_sample_renders_on_repeated_spaced_plays(self):
        for cue in ("move", "rotate", "place", "clear"):
            for attempt in range(3):
                with self.subTest(cue=cue, attempt=attempt):
                    self.assert_sample_renders(cue)

    def test_replay_after_mute_and_resume(self):
        self.assert_sample_renders("rotate")
        self.audio.toggle()
        self.assertFalse(self.audio.audible)
        self.audio.tick()
        self.assertFalse(any(self.objc.send(v.handle, "isPlaying", C.c_bool)
                             for voices in self.player._voices.values() for v in voices))
        self.audio.toggle()
        self.assert_sample_renders("switch")
        self.assert_sample_renders("rotate")


if __name__ == "__main__":
    unittest.main()
