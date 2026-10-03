import hashlib
import json
from pathlib import Path
import struct
import unittest
import wave


SOUNDS = Path(__file__).resolve().parents[1] / "neon_tetris" / "sounds"


class SampleTests(unittest.TestCase):
    def test_selected_samples_have_provenance_and_matching_hashes(self):
        manifest = json.loads((SOUNDS / "credits.json").read_text())
        self.assertEqual(manifest["license"], "CC0-1.0")
        self.assertEqual({sample["creator"] for sample in manifest["samples"] if "creator" in sample},
                         {"StavSounds", "alpinemesh", "Professor-Syntax"})
        self.assertEqual({sample["file"] for sample in manifest["samples"]},
                         {"tactile.wav", "enter.wav", "mx-blue.wav", "clear.wav"})
        for sample in manifest["samples"]:
            with self.subTest(file=sample["file"]):
                path = SOUNDS / sample["file"]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), sample["sha256"])
                with wave.open(str(path), "rb") as wav:
                    self.assertEqual(wav.getnframes(), sample["frames"])

    def test_bundled_clicks_are_short_pcm_with_headroom_and_soft_edges(self):
        for path in SOUNDS.glob("*.wav"):
            with self.subTest(file=path.name), wave.open(str(path), "rb") as wav:
                self.assertEqual((wav.getnchannels(), wav.getsampwidth(), wav.getframerate()),
                                 (1, 2, 44100))
                self.assertTrue(0.05 < wav.getnframes() / 44100 < 0.30)
                values = struct.unpack(f"<{wav.getnframes()}h", wav.readframes(wav.getnframes()))
                self.assertEqual((values[0], values[-1]), (0, 0))
                self.assertTrue(1000 < max(abs(value) for value in values) < 25000)
                self.assertGreater(sum(abs(value) for value in values) / len(values), 50)


if __name__ == "__main__":
    unittest.main()
