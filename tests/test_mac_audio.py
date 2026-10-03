from contextlib import nullcontext
from pathlib import Path
import unittest
from unittest.mock import Mock, patch, sentinel

from neon_tetris._mac_audio import MacPlayer, _ObjC


class FakeObjC:
    """Model player ownership and state without loading Apple frameworks in tests."""

    def __init__(self):
        self.next_id = 100
        self.allocated = set()
        self.playing = set()
        self.pending_completions = set()
        self.released = []
        self.prepared = []
        self.positions = {}
        self.initialized = 0
        self.fail_init = None
        self.fail_data = False
        self.fail_prepare = None
        self.fail_play = False

    def cls(self, name):
        return {"NSData": 1, "AVAudioPlayer": 3}[name]

    def pool(self):
        return nullcontext()

    def finish(self, handle):
        self.playing.discard(handle)
        self.pending_completions.add(handle)

    def poll(self):
        self.pending_completions.clear()

    def send(self, receiver, selector, result=None, *arguments):
        if selector == "dataWithBytes:length:":
            return None if self.fail_data else 10
        if selector == "alloc":
            self.next_id += 1
            self.allocated.add(self.next_id)
            return self.next_id
        if selector == "initWithData:error:":
            self.initialized += 1
            if self.initialized == self.fail_init:
                self.allocated.remove(receiver)
                return None
            return receiver
        if selector == "localizedDescription":
            return None
        if selector == "UTF8String":
            return b"invalid audio"
        if selector == "prepareToPlay":
            self.prepared.append(receiver)
            return len(self.prepared) != self.fail_prepare
        if selector == "setCurrentTime:":
            self.positions[receiver] = arguments[0].value
        elif selector == "play":
            if self.fail_play:
                return False
            # AVAudioPlayer can report success yet stay silent until completion events run.
            if receiver not in self.pending_completions:
                self.playing.add(receiver)
            return True
        elif selector == "isPlaying":
            return receiver in self.playing
        elif selector in ("pause", "stop"):
            self.playing.discard(receiver)
        elif selector == "release":
            self.released.append(receiver)
            self.allocated.remove(receiver)
        return None


class RunLoopTests(unittest.TestCase):
    def test_poll_services_default_mode_without_waiting(self):
        objc = _ObjC.__new__(_ObjC)
        objc.core = Mock()
        objc._run_mode = sentinel.default_mode
        objc.poll()
        objc.core.CFRunLoopRunInMode.assert_called_once_with(sentinel.default_mode, 0.0, False)


class NativePlaybackTests(unittest.TestCase):
    def setUp(self):
        self.objc = FakeObjC()
        patcher = patch("neon_tetris._mac_audio._ObjC", return_value=self.objc)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch.object(Path, "read_bytes", return_value=b"test-wave")
        self.reads = patcher.start()
        self.addCleanup(patcher.stop)
        self.paths = tuple(Path(name) for name in ("tactile.wav", "mx-blue.wav", "enter.wav", "clear.wav"))

    def player(self):
        player = MacPlayer(self.paths)
        self.addCleanup(player.close)
        return player

    def test_preloads_bounded_voices_once_and_reuses_them_under_repeat(self):
        player = self.player()
        self.assertEqual(len(self.objc.allocated), 8)
        self.assertEqual(len(self.objc.prepared), 8)
        handles = set(self.objc.allocated)
        for _ in range(100):
            player.play(self.paths[0])
        self.assertEqual(self.objc.allocated, handles)
        self.assertEqual(self.reads.call_count, 4)
        self.assertEqual(len(self.objc.playing), 2)
        self.assertTrue(player.ready)
        self.assertTrue(all(value == 0.0 for value in self.objc.positions.values()))

    def test_independent_sample_voices_can_overlap(self):
        player = self.player()
        for path in self.paths:
            player.play(path)
        self.assertEqual(len(self.objc.playing), 4)

    def test_completed_voice_is_reprepared_before_the_next_key(self):
        player = self.player()
        player.play(self.paths[0])
        handle = next(iter(self.objc.playing))
        self.objc.finish(handle)
        player.tick()
        self.assertEqual(self.objc.prepared[-1], handle)
        self.assertEqual(len(self.objc.prepared), 9)
        self.assertEqual(self.objc.positions[handle], 0.0)
        self.assertTrue(player._voices[self.paths[0]][0].ready)

    def test_finished_sample_remains_audible_on_every_replay(self):
        player = self.player()
        path = self.paths[0]
        for attempt in range(6):
            with self.subTest(attempt=attempt):
                player.play(path)
                voice = max(player._voices[path], key=lambda v: v.order)
                self.assertIn(voice.handle, self.objc.playing)
                self.objc.finish(voice.handle)
                player.tick()

    def test_mute_pauses_all_voices_without_releasing_or_reallocating(self):
        player = self.player()
        for path in self.paths:
            player.play(path)
        player.stop()
        self.assertFalse(self.objc.playing)
        self.assertEqual(len(self.objc.allocated), 8)
        player.tick()
        player.play(self.paths[0])
        self.assertEqual(len(self.objc.playing), 1)
        self.assertEqual(len(self.objc.allocated), 8)

    def test_close_releases_every_voice_once(self):
        player = self.player()
        player.play(self.paths[0])
        player.close()
        self.assertFalse(player.ready)
        self.assertFalse(self.objc.allocated)
        self.assertFalse(self.objc.playing)
        self.assertEqual(len(self.objc.released), 8)
        player.close()
        self.assertEqual(len(self.objc.released), 8)

    def test_data_allocation_failure_is_explicit(self):
        self.objc.fail_data = True
        with self.assertRaisesRegex(OSError, "Cannot allocate"):
            MacPlayer(self.paths)
        self.assertFalse(self.objc.allocated)

    def test_asset_read_failure_releases_previously_created_players(self):
        self.reads.side_effect = [b"test-wave", OSError("cannot read asset")]
        with self.assertRaisesRegex(OSError, "cannot read asset"):
            MacPlayer(self.paths)
        self.assertFalse(self.objc.allocated)
        self.assertEqual(len(self.objc.released), 2)

    def test_partial_load_failure_releases_previously_created_players(self):
        self.objc.fail_init = 3
        with self.assertRaisesRegex(OSError, "Cannot load"):
            MacPlayer(self.paths)
        self.assertFalse(self.objc.allocated)
        self.assertEqual(len(self.objc.released), 2)

    def test_preparation_failure_releases_the_failed_player_too(self):
        self.objc.fail_prepare = 3
        with self.assertRaisesRegex(OSError, "Cannot prepare"):
            MacPlayer(self.paths)
        self.assertFalse(self.objc.allocated)
        self.assertEqual(len(self.objc.released), 3)

    def test_play_and_reprepare_failures_are_explicit(self):
        player = self.player()
        self.objc.fail_play = True
        with self.assertRaisesRegex(OSError, "Cannot play"):
            player.play(self.paths[0])
        self.objc.fail_play = False
        player.play(self.paths[0])
        self.objc.playing.clear()
        self.objc.fail_prepare = len(self.objc.prepared) + 1
        with self.assertRaisesRegex(OSError, "Cannot reprepare"):
            player.tick()


if __name__ == "__main__":
    unittest.main()
