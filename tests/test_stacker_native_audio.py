"""Opt-in Stacker output-device playback metering, never microphone recording."""
import ctypes as C
import os
import sys
import time
import unittest

from arcade_common.audio import KeyboardAudio, CUES, SOUND_DIR
from tink_stacker.ui import Controller


@unittest.skipUnless(sys.platform == 'darwin' and os.environ.get('NEON_TETRIS_AUDIO_TESTS') == '1',
                     'requires macOS and NEON_TETRIS_AUDIO_TESTS=1 for real playback metering')
class NativeStackerAudioTests(unittest.TestCase):
    def setUp(self):
        self.audio = KeyboardAudio()
        self.addCleanup(self.audio.close)
        self.assertTrue(self.audio.audible, self.audio.warning)
        self.player = self.audio._backend
        self.objc = self.player._objc
        for voices in self.player._voices.values():
            for voice in voices:
                self.objc.send(voice.handle, 'setMeteringEnabled:', None, C.c_bool(True))

    def frame(self, c, keys=''):
        return c.frame(time.monotonic(), 30, 80, [ord(k) for k in keys], self.audio)

    def action(self, cue):
        c = Controller(time.monotonic())
        if cue == 'over':
            c.game.lock_row()  # Next row starts at the nonoverlapping opposite edge.
        elif cue == 'clear':
            for _ in range(14):
                c.game.x = 0; c.game.lock_row()
            c.game.x = 0
        before = self.player._order
        self.frame(c, 'p' if cue == 'switch' else ' ')
        self.assertEqual(self.player._order, before + 1, f'{cue}: Stacker did not dispatch and service its cue')
        self.assertFalse(self.audio.warning, self.audio.warning)
        voices = self.player._voices[SOUND_DIR / CUES[cue][0]]
        voice = max(voices, key=lambda v: v.order)
        self.assertEqual(voice.order, self.player._order, f'{cue}: wrong sample was played')
        return c, voice

    def meter(self, controller, voice):
        duration = self.objc.send(voice.handle, 'duration', C.c_double)
        self.assertTrue(0 < duration < .5)
        furthest, peak = 0.0, -160.0
        deadline = time.monotonic() + duration + .2
        while time.monotonic() < deadline:
            # Observe before completion servicing can rewind an idle voice, and after it.
            furthest = max(furthest, self.objc.send(voice.handle, 'currentTime', C.c_double))
            self.frame(controller)
            self.assertFalse(self.audio.warning, self.audio.warning)
            furthest = max(furthest, self.objc.send(voice.handle, 'currentTime', C.c_double))
            self.objc.send(voice.handle, 'updateMeters', None)
            peak = max(peak, self.objc.send(voice.handle, 'peakPowerForChannel:', C.c_float, C.c_size_t(0)))
            time.sleep(1 / 60)
        self.assertGreater(furthest, .01, f'Playback did not advance: time={furthest}, peak={peak}, duration={duration}')
        self.assertGreater(peak, -80.0, f'No rendered sample signal: {peak} dB')
        print(f'Stacker sample time={furthest:.4f}s; peak={peak:.2f} dB', flush=True)

    def test_stacker_action_cues_advance_and_meter_on_spaced_repeats(self):
        for cue in ('place', 'over', 'clear', 'switch'):
            for attempt in range(3):
                with self.subTest(cue=cue, attempt=attempt):
                    self.meter(*self.action(cue))

    def test_stacker_action_cues_advance_and_meter_on_rapid_repeats(self):
        for cue in ('place', 'over', 'clear', 'switch'):
            for burst in range(3):
                with self.subTest(cue=cue, burst=burst):
                    # Overlapping cues may replace a voice before device startup completes.
                    # Require every dispatch, then measure the surviving output of each burst.
                    for _ in range(6):
                        controller, voice = self.action(cue)
                        self.frame(controller)
                        time.sleep(1 / 60)
                    self.assertEqual(len(self.player._voices[SOUND_DIR / CUES[cue][0]]), 2)
                    self.meter(controller, voice)

    def test_stacker_playback_resumes_after_mute_and_closes_voices(self):
        c, voice = self.action('place')
        self.frame(c, 'm')
        self.assertTrue(self.audio.muted)
        self.assertFalse(any(self.objc.send(v.handle, 'isPlaying', C.c_bool)
                             for voices in self.player._voices.values() for v in voices))
        self.frame(c, 'm')
        self.meter(*self.action('place'))
        self.audio.close()
        self.assertEqual(self.player._voices, {})
