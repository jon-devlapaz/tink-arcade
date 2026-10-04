
$ ["python3", "-B", "-c", "import unittest; s=unittest.defaultTestLoader.discover('tests'); assert s.countTestCases()>0, 'No tests discovered'; r=unittest.TextTestRunner(verbosity=2).run(s); raise SystemExit(not r.wasSuccessful())"]
test_context_cleanup_preserves_unexpected_errors (test_audio.PlaybackTests.test_context_cleanup_preserves_unexpected_errors) ... ok
test_expired_cues_do_not_play_late (test_audio.PlaybackTests.test_expired_cues_do_not_play_late) ... ok
test_input_batch_retains_only_the_highest_priority_cue (test_audio.PlaybackTests.test_input_batch_retains_only_the_highest_priority_cue) ... ok
test_mute_cancels_active_and_pending_cues_and_can_resume (test_audio.PlaybackTests.test_mute_cancels_active_and_pending_cues_and_can_resume) ... ok
test_player_failure_disables_audio_without_retry_spam (test_audio.PlaybackTests.test_player_failure_disables_audio_without_retry_spam) ... ok
test_preloads_unique_samples_once_and_uses_all_three_choices (test_audio.PlaybackTests.test_preloads_unique_samples_once_and_uses_all_three_choices) ... ok
test_ready_backend_plays_consecutive_frames_without_waiting_for_a_tail (test_audio.PlaybackTests.test_ready_backend_plays_consecutive_frames_without_waiting_for_a_tail) ... ok
test_tick_failure_is_reported_and_releases_resources (test_audio.PlaybackTests.test_tick_failure_is_reported_and_releases_resources) ... ok
test_unknown_cue_is_an_explicit_error_even_when_disabled (test_audio.PlaybackTests.test_unknown_cue_is_an_explicit_error_even_when_disabled) ... ok
test_cancelled_child_is_not_reported_as_failure (test_audio.ProcessFallbackTests.test_cancelled_child_is_not_reported_as_failure) ... ok
test_hung_child_and_cleanup_are_bounded (test_audio.ProcessFallbackTests.test_hung_child_and_cleanup_are_bounded) ... ok
test_missing_player_and_aplay_selection (test_audio.ProcessFallbackTests.test_missing_player_and_aplay_selection) ... ok
test_mute_escalates_to_kill_without_blocking (test_audio.ProcessFallbackTests.test_mute_escalates_to_kill_without_blocking) ... ok
test_nonzero_exit_and_spawn_errors_are_explicit (test_audio.ProcessFallbackTests.test_nonzero_exit_and_spawn_errors_are_explicit) ... ok
test_polling_never_waits_during_normal_playback (test_audio.ProcessFallbackTests.test_polling_never_waits_during_normal_playback) ... ok
test_disabled_audio_does_not_probe_assets_or_initialize_backend (test_audio.SetupTests.test_disabled_audio_does_not_probe_assets_or_initialize_backend) ... ok
test_mac_uses_preloaded_backend_not_external_player (test_audio.SetupTests.test_mac_uses_preloaded_backend_not_external_player) ... ok
test_missing_asset_is_reported (test_audio.SetupTests.test_missing_asset_is_reported) ... ok
test_non_mac_retains_portable_fallback (test_audio.SetupTests.test_non_mac_retains_portable_fallback) ... ok
test_unavailable_backend_is_reported (test_audio.SetupTests.test_unavailable_backend_is_reported) ... ok
test_blocked_controls_and_paused_gameplay_are_silent (test_audio.SoundEventTests.test_blocked_controls_and_paused_gameplay_are_silent) ... ok
test_gravity_lock_gets_a_placement_sound (test_audio.SoundEventTests.test_gravity_lock_gets_a_placement_sound) ... ok
test_line_clear_supersedes_drop_and_does_not_repeat_during_flash (test_audio.SoundEventTests.test_line_clear_supersedes_drop_and_does_not_repeat_during_flash) ... ok
test_pause_resume_and_mute_controls (test_audio.SoundEventTests.test_pause_resume_and_mute_controls) ... ok
test_successful_controls_use_the_selected_keyboard_cues (test_audio.SoundEventTests.test_successful_controls_use_the_selected_keyboard_cues) ... ok
test_top_out_uses_the_enter_clack (test_audio.SoundEventTests.test_top_out_uses_the_enter_clack) ... ok
test_above_board_lock_out_is_atomic (test_engine.EngineTests.test_above_board_lock_out_is_atomic) ... ok
test_collision_and_invalid_access_guard (test_engine.EngineTests.test_collision_and_invalid_access_guard) ... ok
test_exhausted_deadline_locks_on_rotation_and_move_contact (test_engine.EngineTests.test_exhausted_deadline_locks_on_rotation_and_move_contact) ... ok
test_exhausted_lock_timer_survives_lift_off_and_soft_drop_contact (test_engine.EngineTests.test_exhausted_lock_timer_survives_lift_off_and_soft_drop_contact) ... ok
test_failed_moves_do_not_reset_lock (test_engine.EngineTests.test_failed_moves_do_not_reset_lock) ... ok
test_floor_kick_cycles_cannot_bypass_lock_budget (test_engine.EngineTests.test_floor_kick_cycles_cannot_bypass_lock_budget) ... ok
test_ghost_matches_hard_drop_and_drop_points (test_engine.EngineTests.test_ghost_matches_hard_drop_and_drop_points) ... ok
test_gravity_pause_and_bounded_time (test_engine.EngineTests.test_gravity_pause_and_bounded_time) ... ok
test_hold_gating_swap_orientation_and_timer_reset (test_engine.EngineTests.test_hold_gating_swap_orientation_and_timer_reset) ... ok
test_hold_spawn_collision_tops_out (test_engine.EngineTests.test_hold_spawn_collision_tops_out) ... ok
test_lock_delay_and_bounded_resets (test_engine.EngineTests.test_lock_delay_and_bounded_resets) ... ok
test_restart_resets_play_state_and_preserves_session_best (test_engine.EngineTests.test_restart_resets_play_state_and_preserves_session_best) ... ok
test_rotation_round_trip_and_obstruction (test_engine.EngineTests.test_rotation_round_trip_and_obstruction) ... ok
test_scoring_and_level_progression (test_engine.EngineTests.test_scoring_and_level_progression) ... ok
test_simultaneous_nonadjacent_line_clearing (test_engine.EngineTests.test_simultaneous_nonadjacent_line_clearing) ... ok
test_soft_drop_only_scores_successful_steps (test_engine.EngineTests.test_soft_drop_only_scores_successful_steps) ... ok
test_spawn_and_all_piece_rotations_have_four_cells (test_engine.EngineTests.test_spawn_and_all_piece_rotations_have_four_cells) ... ok
test_spawn_top_out_and_game_over_actions (test_engine.EngineTests.test_spawn_top_out_and_game_over_actions) ... ok
test_wall_and_floor_kicks (test_engine.EngineTests.test_wall_and_floor_kicks) ... ok
test_fairness_and_preview (test_engine.SevenBagTests.test_fairness_and_preview) ... ok
test_seed_determinism (test_engine.SevenBagTests.test_seed_determinism) ... ok
test_clock_frame_partition (test_galaga.GalagaTests.test_clock_frame_partition) ... ok
test_damage_and_protection (test_galaga.GalagaTests.test_damage_and_protection) ... ok
test_dive_returns_to_formation (test_galaga.GalagaTests.test_dive_returns_to_formation) ... ok
test_enemy_contact_hits_player (test_galaga.GalagaTests.test_enemy_contact_hits_player) ... ok
test_enemy_dives_and_fires (test_galaga.GalagaTests.test_enemy_dives_and_fires) ... ok
test_fire_cooldown (test_galaga.GalagaTests.test_fire_cooldown) ... ok
test_game_over_stops_and_restart_resets_seed (test_galaga.GalagaTests.test_game_over_stops_and_restart_resets_seed) ... ok
test_help_and_non_terminal (test_galaga.GalagaTests.test_help_and_non_terminal) ... ok
test_higher_wave_has_faster_attacks (test_galaga.GalagaTests.test_higher_wave_has_faster_attacks) ... ok
test_key_controls (test_galaga.GalagaTests.test_key_controls) ... ok
test_missed_shot_does_not_score (test_galaga.GalagaTests.test_missed_shot_does_not_score) ... ok
test_movement_bounds (test_galaga.GalagaTests.test_movement_bounds) ... ok
test_pause_blocks_time_and_input (test_galaga.GalagaTests.test_pause_blocks_time_and_input) ... ok
test_seed_repeats_inputs_and_enemy_choices (test_galaga.GalagaTests.test_seed_repeats_inputs_and_enemy_choices) ... ok
test_shot_kills_only_first_enemy_in_path (test_galaga.GalagaTests.test_shot_kills_only_first_enemy_in_path) ... ok
test_stall_and_resize_do_not_catch_up (test_galaga.GalagaTests.test_stall_and_resize_do_not_catch_up) ... ok
test_wave_advances_and_clears_danger (test_galaga.GalagaTests.test_wave_advances_and_clears_danger) ... ok
test_asset_read_failure_releases_previously_created_players (test_mac_audio.NativePlaybackTests.test_asset_read_failure_releases_previously_created_players) ... ok
test_close_releases_every_voice_once (test_mac_audio.NativePlaybackTests.test_close_releases_every_voice_once) ... ok
test_completed_voice_is_reprepared_before_the_next_key (test_mac_audio.NativePlaybackTests.test_completed_voice_is_reprepared_before_the_next_key) ... ok
test_data_allocation_failure_is_explicit (test_mac_audio.NativePlaybackTests.test_data_allocation_failure_is_explicit) ... ok
test_finished_sample_remains_audible_on_every_replay (test_mac_audio.NativePlaybackTests.test_finished_sample_remains_audible_on_every_replay) ... ok
test_independent_sample_voices_can_overlap (test_mac_audio.NativePlaybackTests.test_independent_sample_voices_can_overlap) ... ok
test_mute_pauses_all_voices_without_releasing_or_reallocating (test_mac_audio.NativePlaybackTests.test_mute_pauses_all_voices_without_releasing_or_reallocating) ... ok
test_partial_load_failure_releases_previously_created_players (test_mac_audio.NativePlaybackTests.test_partial_load_failure_releases_previously_created_players) ... ok
test_play_and_reprepare_failures_are_explicit (test_mac_audio.NativePlaybackTests.test_play_and_reprepare_failures_are_explicit) ... ok
test_preloads_bounded_voices_once_and_reuses_them_under_repeat (test_mac_audio.NativePlaybackTests.test_preloads_bounded_voices_once_and_reuses_them_under_repeat) ... ok
test_preparation_failure_releases_the_failed_player_too (test_mac_audio.NativePlaybackTests.test_preparation_failure_releases_the_failed_player_too) ... ok
test_poll_services_default_mode_without_waiting (test_mac_audio.RunLoopTests.test_poll_services_default_mode_without_waiting) ... ok
test_each_sample_renders_on_repeated_spaced_plays (test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays) ... skipped 'set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples'
test_replay_after_mute_and_resume (test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume) ... skipped 'set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples'
test_bundled_clicks_are_short_pcm_with_headroom_and_soft_edges (test_samples.SampleTests.test_bundled_clicks_are_short_pcm_with_headroom_and_soft_edges) ... ok
test_selected_samples_have_provenance_and_matching_hashes (test_samples.SampleTests.test_selected_samples_have_provenance_and_matching_hashes) ... ok
test_audio_failure_is_reported_after_curses_returns (test_ui.CLITests.test_audio_failure_is_reported_after_curses_returns) ... ok
test_help_without_tty (test_ui.CLITests.test_help_without_tty) ... ok
test_invalid_seed (test_ui.CLITests.test_invalid_seed) ... ok
test_no_sound_and_color_flags_reach_the_game (test_ui.CLITests.test_no_sound_and_color_flags_reach_the_game) ... ok
test_non_tty_fails_cleanly (test_ui.CLITests.test_non_tty_fails_cleanly) ... ok
test_terminal_error_and_ctrl_c_are_clean (test_ui.CLITests.test_terminal_error_and_ctrl_c_are_clean) ... ok
test_keyboard_mapping (test_ui.InputTests.test_keyboard_mapping) ... ok
test_pause_and_restart_controls (test_ui.InputTests.test_pause_and_restart_controls) ... ok
test_renderer_clips_and_tolerates_resize_errors (test_ui.InputTests.test_renderer_clips_and_tolerates_resize_errors) ... ok
test_renderer_does_not_swallow_programming_errors (test_ui.InputTests.test_renderer_does_not_swallow_programming_errors) ... ok
test_resize_freezes_simulation_and_discards_catchup (test_ui.InputTests.test_resize_freezes_simulation_and_discards_catchup) ... ok
test_active_ink_and_pencil_ghost_are_distinct (test_ui.ThemeTests.test_active_ink_and_pencil_ghost_are_distinct) ... ok
test_no_color_does_not_initialize_colors (test_ui.ThemeTests.test_no_color_does_not_initialize_colors) ... ok
test_paper_palette_and_basic_terminal_fallback (test_ui.ThemeTests.test_paper_palette_and_basic_terminal_fallback) ... ok
test_socratink_copy_on_board_and_overlays (test_ui.ThemeTests.test_socratink_copy_on_board_and_overlays) ... ok

----------------------------------------------------------------------
Ran 95 tests in 0.199s

OK (skipped=2)

# checklist item gameplay
$ ["python3", "-B", "-c", "import unittest; s=unittest.defaultTestLoader.discover('tests'); assert s.countTestCases()>0, 'No tests discovered'; r=unittest.TextTestRunner(verbosity=2).run(s); raise SystemExit(not r.wasSuccessful())"]
test_context_cleanup_preserves_unexpected_errors (test_audio.PlaybackTests.test_context_cleanup_preserves_unexpected_errors) ... ok
test_expired_cues_do_not_play_late (test_audio.PlaybackTests.test_expired_cues_do_not_play_late) ... ok
test_input_batch_retains_only_the_highest_priority_cue (test_audio.PlaybackTests.test_input_batch_retains_only_the_highest_priority_cue) ... ok
test_mute_cancels_active_and_pending_cues_and_can_resume (test_audio.PlaybackTests.test_mute_cancels_active_and_pending_cues_and_can_resume) ... ok
test_player_failure_disables_audio_without_retry_spam (test_audio.PlaybackTests.test_player_failure_disables_audio_without_retry_spam) ... ok
test_preloads_unique_samples_once_and_uses_all_three_choices (test_audio.PlaybackTests.test_preloads_unique_samples_once_and_uses_all_three_choices) ... ok
test_ready_backend_plays_consecutive_frames_without_waiting_for_a_tail (test_audio.PlaybackTests.test_ready_backend_plays_consecutive_frames_without_waiting_for_a_tail) ... ok
test_tick_failure_is_reported_and_releases_resources (test_audio.PlaybackTests.test_tick_failure_is_reported_and_releases_resources) ... ok
test_unknown_cue_is_an_explicit_error_even_when_disabled (test_audio.PlaybackTests.test_unknown_cue_is_an_explicit_error_even_when_disabled) ... ok
test_cancelled_child_is_not_reported_as_failure (test_audio.ProcessFallbackTests.test_cancelled_child_is_not_reported_as_failure) ... ok
test_hung_child_and_cleanup_are_bounded (test_audio.ProcessFallbackTests.test_hung_child_and_cleanup_are_bounded) ... ok
test_missing_player_and_aplay_selection (test_audio.ProcessFallbackTests.test_missing_player_and_aplay_selection) ... ok
test_mute_escalates_to_kill_without_blocking (test_audio.ProcessFallbackTests.test_mute_escalates_to_kill_without_blocking) ... ok
test_nonzero_exit_and_spawn_errors_are_explicit (test_audio.ProcessFallbackTests.test_nonzero_exit_and_spawn_errors_are_explicit) ... ok
test_polling_never_waits_during_normal_playback (test_audio.ProcessFallbackTests.test_polling_never_waits_during_normal_playback) ... ok
test_disabled_audio_does_not_probe_assets_or_initialize_backend (test_audio.SetupTests.test_disabled_audio_does_not_probe_assets_or_initialize_backend) ... ok
test_mac_uses_preloaded_backend_not_external_player (test_audio.SetupTests.test_mac_uses_preloaded_backend_not_external_player) ... ok
test_missing_asset_is_reported (test_audio.SetupTests.test_missing_asset_is_reported) ... ok
test_non_mac_retains_portable_fallback (test_audio.SetupTests.test_non_mac_retains_portable_fallback) ... ok
test_unavailable_backend_is_reported (test_audio.SetupTests.test_unavailable_backend_is_reported) ... ok
test_blocked_controls_and_paused_gameplay_are_silent (test_audio.SoundEventTests.test_blocked_controls_and_paused_gameplay_are_silent) ... ok
test_gravity_lock_gets_a_placement_sound (test_audio.SoundEventTests.test_gravity_lock_gets_a_placement_sound) ... ok
test_line_clear_supersedes_drop_and_does_not_repeat_during_flash (test_audio.SoundEventTests.test_line_clear_supersedes_drop_and_does_not_repeat_during_flash) ... ok
test_pause_resume_and_mute_controls (test_audio.SoundEventTests.test_pause_resume_and_mute_controls) ... ok
test_successful_controls_use_the_selected_keyboard_cues (test_audio.SoundEventTests.test_successful_controls_use_the_selected_keyboard_cues) ... ok
test_top_out_uses_the_enter_clack (test_audio.SoundEventTests.test_top_out_uses_the_enter_clack) ... ok
test_above_board_lock_out_is_atomic (test_engine.EngineTests.test_above_board_lock_out_is_atomic) ... ok
test_collision_and_invalid_access_guard (test_engine.EngineTests.test_collision_and_invalid_access_guard) ... ok
test_exhausted_deadline_locks_on_rotation_and_move_contact (test_engine.EngineTests.test_exhausted_deadline_locks_on_rotation_and_move_contact) ... ok
test_exhausted_lock_timer_survives_lift_off_and_soft_drop_contact (test_engine.EngineTests.test_exhausted_lock_timer_survives_lift_off_and_soft_drop_contact) ... ok
test_failed_moves_do_not_reset_lock (test_engine.EngineTests.test_failed_moves_do_not_reset_lock) ... ok
test_floor_kick_cycles_cannot_bypass_lock_budget (test_engine.EngineTests.test_floor_kick_cycles_cannot_bypass_lock_budget) ... ok
test_ghost_matches_hard_drop_and_drop_points (test_engine.EngineTests.test_ghost_matches_hard_drop_and_drop_points) ... ok
test_gravity_pause_and_bounded_time (test_engine.EngineTests.test_gravity_pause_and_bounded_time) ... ok
test_hold_gating_swap_orientation_and_timer_reset (test_engine.EngineTests.test_hold_gating_swap_orientation_and_timer_reset) ... ok
test_hold_spawn_collision_tops_out (test_engine.EngineTests.test_hold_spawn_collision_tops_out) ... ok
test_lock_delay_and_bounded_resets (test_engine.EngineTests.test_lock_delay_and_bounded_resets) ... ok
test_restart_resets_play_state_and_preserves_session_best (test_engine.EngineTests.test_restart_resets_play_state_and_preserves_session_best) ... ok
test_rotation_round_trip_and_obstruction (test_engine.EngineTests.test_rotation_round_trip_and_obstruction) ... ok
test_scoring_and_level_progression (test_engine.EngineTests.test_scoring_and_level_progression) ... ok
test_simultaneous_nonadjacent_line_clearing (test_engine.EngineTests.test_simultaneous_nonadjacent_line_clearing) ... ok
test_soft_drop_only_scores_successful_steps (test_engine.EngineTests.test_soft_drop_only_scores_successful_steps) ... ok
test_spawn_and_all_piece_rotations_have_four_cells (test_engine.EngineTests.test_spawn_and_all_piece_rotations_have_four_cells) ... ok
test_spawn_top_out_and_game_over_actions (test_engine.EngineTests.test_spawn_top_out_and_game_over_actions) ... ok
test_wall_and_floor_kicks (test_engine.EngineTests.test_wall_and_floor_kicks) ... ok
test_fairness_and_preview (test_engine.SevenBagTests.test_fairness_and_preview) ... ok
test_seed_determinism (test_engine.SevenBagTests.test_seed_determinism) ... ok
test_clock_frame_partition (test_galaga.GalagaTests.test_clock_frame_partition) ... ok
test_damage_and_protection (test_galaga.GalagaTests.test_damage_and_protection) ... ok
test_dive_returns_to_formation (test_galaga.GalagaTests.test_dive_returns_to_formation) ... ok
test_enemy_contact_hits_player (test_galaga.GalagaTests.test_enemy_contact_hits_player) ... ok
test_enemy_dives_and_fires (test_galaga.GalagaTests.test_enemy_dives_and_fires) ... ok
test_fire_cooldown (test_galaga.GalagaTests.test_fire_cooldown) ... ok
test_game_over_stops_and_restart_resets_seed (test_galaga.GalagaTests.test_game_over_stops_and_restart_resets_seed) ... ok
test_help_and_non_terminal (test_galaga.GalagaTests.test_help_and_non_terminal) ... ok
test_higher_wave_has_faster_attacks (test_galaga.GalagaTests.test_higher_wave_has_faster_attacks) ... ok
test_key_controls (test_galaga.GalagaTests.test_key_controls) ... ok
test_missed_shot_does_not_score (test_galaga.GalagaTests.test_missed_shot_does_not_score) ... ok
test_movement_bounds (test_galaga.GalagaTests.test_movement_bounds) ... ok
test_pause_blocks_time_and_input (test_galaga.GalagaTests.test_pause_blocks_time_and_input) ... ok
test_seed_repeats_inputs_and_enemy_choices (test_galaga.GalagaTests.test_seed_repeats_inputs_and_enemy_choices) ... ok
test_shot_kills_only_first_enemy_in_path (test_galaga.GalagaTests.test_shot_kills_only_first_enemy_in_path) ... ok
test_stall_and_resize_do_not_catch_up (test_galaga.GalagaTests.test_stall_and_resize_do_not_catch_up) ... ok
test_wave_advances_and_clears_danger (test_galaga.GalagaTests.test_wave_advances_and_clears_danger) ... ok
test_asset_read_failure_releases_previously_created_players (test_mac_audio.NativePlaybackTests.test_asset_read_failure_releases_previously_created_players) ... ok
test_close_releases_every_voice_once (test_mac_audio.NativePlaybackTests.test_close_releases_every_voice_once) ... ok
test_completed_voice_is_reprepared_before_the_next_key (test_mac_audio.NativePlaybackTests.test_completed_voice_is_reprepared_before_the_next_key) ... ok
test_data_allocation_failure_is_explicit (test_mac_audio.NativePlaybackTests.test_data_allocation_failure_is_explicit) ... ok
test_finished_sample_remains_audible_on_every_replay (test_mac_audio.NativePlaybackTests.test_finished_sample_remains_audible_on_every_replay) ... ok
test_independent_sample_voices_can_overlap (test_mac_audio.NativePlaybackTests.test_independent_sample_voices_can_overlap) ... ok
test_mute_pauses_all_voices_without_releasing_or_reallocating (test_mac_audio.NativePlaybackTests.test_mute_pauses_all_voices_without_releasing_or_reallocating) ... ok
test_partial_load_failure_releases_previously_created_players (test_mac_audio.NativePlaybackTests.test_partial_load_failure_releases_previously_created_players) ... ok
test_play_and_reprepare_failures_are_explicit (test_mac_audio.NativePlaybackTests.test_play_and_reprepare_failures_are_explicit) ... ok
test_preloads_bounded_voices_once_and_reuses_them_under_repeat (test_mac_audio.NativePlaybackTests.test_preloads_bounded_voices_once_and_reuses_them_under_repeat) ... ok
test_preparation_failure_releases_the_failed_player_too (test_mac_audio.NativePlaybackTests.test_preparation_failure_releases_the_failed_player_too) ... ok
test_poll_services_default_mode_without_waiting (test_mac_audio.RunLoopTests.test_poll_services_default_mode_without_waiting) ... ok
test_each_sample_renders_on_repeated_spaced_plays (test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays) ... skipped 'set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples'
test_replay_after_mute_and_resume (test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume) ... skipped 'set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples'
test_bundled_clicks_are_short_pcm_with_headroom_and_soft_edges (test_samples.SampleTests.test_bundled_clicks_are_short_pcm_with_headroom_and_soft_edges) ... ok
test_selected_samples_have_provenance_and_matching_hashes (test_samples.SampleTests.test_selected_samples_have_provenance_and_matching_hashes) ... ok
test_audio_failure_is_reported_after_curses_returns (test_ui.CLITests.test_audio_failure_is_reported_after_curses_returns) ... ok
test_help_without_tty (test_ui.CLITests.test_help_without_tty) ... ok
test_invalid_seed (test_ui.CLITests.test_invalid_seed) ... ok
test_no_sound_and_color_flags_reach_the_game (test_ui.CLITests.test_no_sound_and_color_flags_reach_the_game) ... ok
test_non_tty_fails_cleanly (test_ui.CLITests.test_non_tty_fails_cleanly) ... ok
test_terminal_error_and_ctrl_c_are_clean (test_ui.CLITests.test_terminal_error_and_ctrl_c_are_clean) ... ok
test_keyboard_mapping (test_ui.InputTests.test_keyboard_mapping) ... ok
test_pause_and_restart_controls (test_ui.InputTests.test_pause_and_restart_controls) ... ok
test_renderer_clips_and_tolerates_resize_errors (test_ui.InputTests.test_renderer_clips_and_tolerates_resize_errors) ... ok
test_renderer_does_not_swallow_programming_errors (test_ui.InputTests.test_renderer_does_not_swallow_programming_errors) ... ok
test_resize_freezes_simulation_and_discards_catchup (test_ui.InputTests.test_resize_freezes_simulation_and_discards_catchup) ... ok
test_active_ink_and_pencil_ghost_are_distinct (test_ui.ThemeTests.test_active_ink_and_pencil_ghost_are_distinct) ... ok
test_no_color_does_not_initialize_colors (test_ui.ThemeTests.test_no_color_does_not_initialize_colors) ... ok
test_paper_palette_and_basic_terminal_fallback (test_ui.ThemeTests.test_paper_palette_and_basic_terminal_fallback) ... ok
test_socratink_copy_on_board_and_overlays (test_ui.ThemeTests.test_socratink_copy_on_board_and_overlays) ... ok

----------------------------------------------------------------------
Ran 95 tests in 0.200s

OK (skipped=2)

# checklist item terminal
$ ["python3", "-B", "scripts/check_galaga_terminal.py"]
PASS: real terminal launch, movement/fire input, pause, resize, resume, restart, Q and Ctrl-C exits.
Engine tests check state changes. This check does not establish human enjoyment or visual taste.
