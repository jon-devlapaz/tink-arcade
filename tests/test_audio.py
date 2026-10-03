import subprocess
import unittest
from unittest.mock import Mock, patch

from neon_tetris.audio import MAX_CUE_AGE, SOUND_DIR, KeyboardAudio, _ProcessPlayer, _make_backend
from neon_tetris.engine import Game, Piece
from neon_tetris.ui import _perform, handle_key


class PlaybackTests(unittest.TestCase):
    def setUp(self):
        self.backend = Mock(ready=True)
        patcher = patch("neon_tetris.audio._make_backend", return_value=self.backend)
        self.factory = patcher.start()
        self.addCleanup(patcher.stop)
        self.audio = KeyboardAudio()
        self.addCleanup(self.audio.close)

    def test_preloads_unique_samples_once_and_uses_all_three_choices(self):
        self.factory.assert_called_once()
        self.assertEqual(set(self.factory.call_args.args[0]),
                         {SOUND_DIR / name for name in ("tactile.wav", "mx-blue.wav", "enter.wav", "clear.wav")})
        for cue, filename in (("move", "tactile.wav"), ("rotate", "mx-blue.wav"),
                              ("place", "enter.wav")):
            self.audio.play(cue)
            self.audio.tick()
            self.backend.play.assert_called_with(SOUND_DIR / filename)
        self.assertEqual(self.factory.call_count, 1)

    def test_input_batch_retains_only_the_highest_priority_cue(self):
        self.audio.play("clear")
        for _ in range(100):
            self.audio.play("move")
        self.backend.play.assert_not_called()
        self.audio.tick()
        self.backend.play.assert_called_once_with(SOUND_DIR / "clear.wav")
        self.assertIsNone(self.audio._pending)

    def test_expired_cues_do_not_play_late(self):
        with patch("neon_tetris.audio.time.monotonic", return_value=0.0) as clock:
            self.backend.ready = False
            self.audio.play("move")
            self.audio.tick()
            self.backend.play.assert_not_called()
            clock.return_value = MAX_CUE_AGE + 0.001
            self.backend.ready = True
            self.audio.tick()
            self.backend.play.assert_not_called()
            self.assertIsNone(self.audio._pending)

    def test_ready_backend_plays_consecutive_frames_without_waiting_for_a_tail(self):
        for cue in ("move", "rotate", "place"):
            self.audio.play(cue)
            self.audio.tick()
        self.assertEqual(self.backend.play.call_count, 3)

    def test_mute_cancels_active_and_pending_cues_and_can_resume(self):
        self.audio.play("place")
        self.audio.tick()
        self.audio.play("clear")
        self.audio.toggle()
        self.backend.stop.assert_called_once()
        self.assertEqual(self.audio.status, "key sound muted [M]")
        self.assertIsNone(self.audio._pending)
        self.audio.play("rotate")
        self.audio.tick()
        self.assertEqual(self.backend.play.call_count, 1)
        self.audio.toggle()
        self.audio.tick()
        self.assertEqual(self.audio.status, "key sound on [M]")
        self.backend.play.assert_called_with(SOUND_DIR / "mx-blue.wav")

    def test_player_failure_disables_audio_without_retry_spam(self):
        self.backend.play.side_effect = OSError("no output device")
        self.audio.play("place")
        self.audio.tick()
        self.assertIn("no output device", self.audio.warning)
        self.assertFalse(self.audio.audible)
        self.backend.close.assert_called_once()
        self.audio.play("move")
        self.audio.tick()
        self.assertEqual(self.backend.play.call_count, 1)

    def test_tick_failure_is_reported_and_releases_resources(self):
        self.backend.tick.side_effect = OSError("audio device stopped")
        self.audio.tick()
        self.assertIn("audio device stopped", self.audio.warning)
        self.backend.close.assert_called_once()

    def test_context_cleanup_preserves_unexpected_errors(self):
        with self.assertRaisesRegex(RuntimeError, "render bug"):
            with self.audio:
                self.audio.play("place")
                self.audio.tick()
                raise RuntimeError("render bug")
        self.backend.close.assert_called_once()
        self.assertFalse(self.audio.audible)
        self.audio.close()
        self.backend.close.assert_called_once()

    def test_unknown_cue_is_an_explicit_error_even_when_disabled(self):
        with self.assertRaises(ValueError):
            self.audio.play("typo")
        with KeyboardAudio(enabled=False) as audio, self.assertRaises(ValueError):
            audio.play("typo")


class SetupTests(unittest.TestCase):
    def test_disabled_audio_does_not_probe_assets_or_initialize_backend(self):
        with (patch("neon_tetris.audio._make_backend") as factory,
              patch("neon_tetris.audio.Path.is_file") as files):
            with KeyboardAudio(enabled=False) as audio:
                audio.toggle()
                audio.play("move")
                audio.tick()
                self.assertEqual(audio.status, "key sound off")
            factory.assert_not_called()
            files.assert_not_called()

    def test_missing_asset_is_reported(self):
        with (patch("neon_tetris.audio.Path.is_file", return_value=False),
              patch("neon_tetris.audio._make_backend") as factory):
            with KeyboardAudio() as audio:
                self.assertIn("Missing keyboard sound", audio.warning)
                self.assertFalse(audio.audible)
            factory.assert_not_called()

    def test_unavailable_backend_is_reported(self):
        with patch("neon_tetris.audio._make_backend", side_effect=OSError("No audio player found.")):
            with KeyboardAudio() as audio:
                self.assertIn("No audio player", audio.warning)
                self.assertEqual(audio.status, "key sound unavailable")
                audio.play("switch")
                audio.tick()

    def test_mac_uses_preloaded_backend_not_external_player(self):
        paths = (SOUND_DIR / "tactile.wav",)
        with (patch("neon_tetris.audio.sys.platform", "darwin"),
              patch("neon_tetris._mac_audio.MacPlayer") as native,
              patch("neon_tetris.audio._ProcessPlayer") as process):
            self.assertIs(_make_backend(paths), native.return_value)
            native.assert_called_once_with(paths)
            process.assert_not_called()

    def test_non_mac_retains_portable_fallback(self):
        with (patch("neon_tetris.audio.sys.platform", "linux"),
              patch("neon_tetris.audio._ProcessPlayer") as process):
            self.assertIs(_make_backend(()), process.return_value)


class ProcessFallbackTests(unittest.TestCase):
    def setUp(self):
        patcher = patch("neon_tetris.audio.shutil.which", return_value="/player")
        patcher.start()
        self.addCleanup(patcher.stop)
        self.process = Mock()
        self.process.poll.return_value = None
        self.process.wait.return_value = 0
        patcher = patch("neon_tetris.audio.subprocess.Popen", return_value=self.process)
        self.popen = patcher.start()
        self.addCleanup(patcher.stop)
        self.player = _ProcessPlayer()
        self.addCleanup(self.player.close)

    def test_polling_never_waits_during_normal_playback(self):
        path = SOUND_DIR / "tactile.wav"
        self.player.play(path)
        self.player.tick()
        self.assertFalse(self.player.ready)
        self.popen.assert_called_once_with(["/player", str(path)], stdin=subprocess.DEVNULL,
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                          start_new_session=True)
        self.process.wait.assert_not_called()
        with self.assertRaises(RuntimeError):
            self.player.play(path)
        self.assertEqual(self.popen.call_count, 1)
        self.process.poll.return_value = 0
        self.player.tick()
        self.assertTrue(self.player.ready)

    def test_cancelled_child_is_not_reported_as_failure(self):
        self.player.play(SOUND_DIR / "enter.wav")
        self.player.stop()
        self.process.terminate.assert_called_once()
        self.process.poll.return_value = -15
        self.player.tick()
        self.assertTrue(self.player.ready)

    def test_nonzero_exit_and_spawn_errors_are_explicit(self):
        self.player.play(SOUND_DIR / "enter.wav")
        self.process.poll.return_value = 1
        with self.assertRaisesRegex(OSError, "status 1"):
            self.player.tick()
        self.popen.side_effect = OSError("device unavailable")
        with self.assertRaisesRegex(OSError, "device unavailable"):
            self.player.play(SOUND_DIR / "enter.wav")

    def test_hung_child_and_cleanup_are_bounded(self):
        with patch("neon_tetris.audio.time.monotonic", return_value=0.0) as clock:
            self.player.play(SOUND_DIR / "enter.wav")
            clock.return_value = 2.1
            with self.assertRaisesRegex(OSError, "timed out"):
                self.player.tick()
        self.process.wait.side_effect = [subprocess.TimeoutExpired("/player", .25), 0]
        self.player.close()
        self.process.terminate.assert_called_once()
        self.process.kill.assert_called_once()
        self.assertEqual(self.process.wait.call_count, 2)

    def test_mute_escalates_to_kill_without_blocking(self):
        with patch("neon_tetris.audio.time.monotonic", return_value=0.0) as clock:
            self.player.play(SOUND_DIR / "enter.wav")
            self.player.stop()
            clock.return_value = .3
            self.player.tick()
            self.process.kill.assert_called_once()
            self.process.wait.assert_not_called()

    def test_missing_player_and_aplay_selection(self):
        with patch("neon_tetris.audio.shutil.which", return_value=None):
            with self.assertRaisesRegex(OSError, "No audio player"):
                _ProcessPlayer()
        with patch("neon_tetris.audio.shutil.which", side_effect=[None, "/bin/aplay"]):
            player = _ProcessPlayer()
            self.assertEqual(player.command, ("/bin/aplay", "-q"))
            player.close()


class SoundEventTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(17)
        self.audio = Mock(audible=True)

    def test_successful_controls_use_the_selected_keyboard_cues(self):
        for key, cue in (("a", "move"), ("x", "rotate"), ("s", "move"),
                         ("c", "switch"), (" ", "place"), ("r", "switch")):
            with self.subTest(key=key):
                self.audio.play.reset_mock()
                handle_key(self.game, ord(key), self.audio)
                self.audio.play.assert_called_once_with(cue)

    def test_blocked_controls_and_paused_gameplay_are_silent(self):
        while self.game.move(-1):
            pass
        handle_key(self.game, ord("a"), self.audio)
        self.audio.play.assert_not_called()
        self.game.paused = True
        for key in "adsxzc ":
            handle_key(self.game, ord(key), self.audio)
        self.audio.play.assert_not_called()

    def test_pause_resume_and_mute_controls(self):
        handle_key(self.game, ord("p"), self.audio)
        self.audio.stop.assert_called_once()
        self.audio.play.assert_called_once_with("switch")
        self.audio.play.reset_mock()
        handle_key(self.game, ord("p"), self.audio)
        self.audio.play.assert_called_once_with("switch")
        before = self.game.active
        handle_key(self.game, ord("M"), self.audio)
        self.audio.toggle.assert_called_once()
        self.assertEqual(self.game.active, before)

    def test_gravity_lock_gets_a_placement_sound(self):
        self.game.active = Piece("T", 3, 18)
        self.game.lock_time = 0.4
        _perform(self.game, lambda: self.game.update(0.1), self.audio)
        self.audio.play.assert_called_once_with("place")

    def test_line_clear_supersedes_drop_and_does_not_repeat_during_flash(self):
        self.game.board[19] = ["J"] * 10
        self.game.board[19][5] = None
        self.game.active = Piece("I", 3, 0, 1)
        handle_key(self.game, ord(" "), self.audio)
        self.assertEqual(self.game.lines, 1)
        self.audio.play.assert_called_once_with("clear")
        _perform(self.game, lambda: self.game.update(0.01), self.audio)
        self.audio.play.assert_called_once_with("clear")

    def test_top_out_uses_the_enter_clack(self):
        self.game.board[1][6] = "J"
        handle_key(self.game, ord("c"), self.audio)
        self.assertTrue(self.game.game_over)
        self.audio.play.assert_called_once_with("over")


if __name__ == "__main__":
    unittest.main()
