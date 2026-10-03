
$ ["python3", "-B", "-c", "import unittest; s=unittest.defaultTestLoader.discover('tests', pattern='test*.py'); assert s.countTestCases() > 0, 'No tests discovered'; r=unittest.TextTestRunner(verbosity=2).run(s); raise SystemExit(not r.wasSuccessful())"]
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
test_empty_key_fails_before_network (test_jev_cost.ClientTests.test_empty_key_fails_before_network) ... ok
test_http_error_does_not_follow_redirects_or_retry (test_jev_cost.ClientTests.test_http_error_does_not_follow_redirects_or_retry) ... ok
test_invalid_reply_preserves_reported_usage (test_jev_cost.ClientTests.test_invalid_reply_preserves_reported_usage) ... ok
test_malformed_shapes_are_errors (test_jev_cost.ClientTests.test_malformed_shapes_are_errors) ... ok
test_request_contract_and_usage (test_jev_cost.ClientTests.test_request_contract_and_usage) ... ok
test_slow_response_obeys_total_deadline (test_jev_cost.ClientTests.test_slow_response_obeys_total_deadline) ... ok
test_timeout_and_network_failures_do_not_retry_or_leak (test_jev_cost.ClientTests.test_timeout_and_network_failures_do_not_retry_or_leak) ... ok
test_missing_invalid_and_unknown_usage_never_looks_free (test_jev_cost.CostTests.test_missing_invalid_and_unknown_usage_never_looks_free) ... ok
test_tiny_costs_accumulate_across_calls_without_rounding (test_jev_cost.CostTests.test_tiny_costs_accumulate_across_calls_without_rounding) ... ok
test_zero_reported_usage_and_inflight_cost (test_jev_cost.CostTests.test_zero_reported_usage_and_inflight_cost) ... ok
test_single_request_and_exactly_once_delivery (test_jev_cost.WorkerTests.test_single_request_and_exactly_once_delivery) ... ok
test_worker_exception_becomes_visible_reply (test_jev_cost.WorkerTests.test_worker_exception_becomes_visible_reply) ... ok
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
test_error_freezes_both_until_explicit_retry (test_race.RaceTests.test_error_freezes_both_until_explicit_retry) ... ok
test_every_option_is_legal_and_enumeration_does_not_mutate (test_race.RaceTests.test_every_option_is_legal_and_enumeration_does_not_mutate) ... ok
test_finished_match_accounts_inflight_reply_without_applying (test_race.RaceTests.test_finished_match_accounts_inflight_reply_without_applying) ... ok
test_human_finish_stops_new_calls_and_actions (test_race.RaceTests.test_human_finish_stops_new_calls_and_actions) ... ok
test_invalid_provider_choice_is_visible_error (test_race.RaceTests.test_invalid_provider_choice_is_visible_error) ... ok
test_pause_freezes_both_and_defers_reply_but_counts_cost (test_race.RaceTests.test_pause_freezes_both_and_defers_reply_but_counts_cost) ... ok
test_resize_freezes_and_accounts_reply (test_race.RaceTests.test_resize_freezes_and_accounts_reply) ... ok
test_responsive_while_waiting_and_only_one_inflight (test_race.RaceTests.test_responsive_while_waiting_and_only_one_inflight) ... ok
test_restart_ignores_old_reply_but_keeps_cost_and_worker (test_race.RaceTests.test_restart_ignores_old_reply_but_keeps_cost_and_worker) ... ok
test_same_kind_next_piece_still_rejects_stale_response (test_race.RaceTests.test_same_kind_next_piece_still_rejects_stale_response) ... ok
test_same_sequence_including_without_seed (test_race.RaceTests.test_same_sequence_including_without_seed) ... ok
test_simultaneous_finish_is_draw (test_race.RaceTests.test_simultaneous_finish_is_draw) ... ok
test_topout_and_simultaneous_topout (test_race.RaceTests.test_topout_and_simultaneous_topout) ... ok
test_80_by_30_has_full_boards_status_cost_and_controls (test_race_ui.RaceUITests.test_80_by_30_has_full_boards_status_cost_and_controls) ... ok
test_cli_missing_key_does_not_open_curses (test_race_ui.RaceUITests.test_cli_missing_key_does_not_open_curses) ... ok
test_cli_routes_versus_and_prints_final_cost (test_race_ui.RaceUITests.test_cli_routes_versus_and_prints_final_cost) ... ok
test_error_winner_and_small_screen_messages (test_race_ui.RaceUITests.test_error_winner_and_small_screen_messages) ... ok
test_global_controls_and_no_input_during_pause_error_or_resize (test_race_ui.RaceUITests.test_global_controls_and_no_input_during_pause_error_or_resize) ... ok
test_loop_handles_input_while_provider_is_waiting_and_quits (test_race_ui.RaceUITests.test_loop_handles_input_while_provider_is_waiting_and_quits) ... ok
test_resize_does_not_apply_catchup_time (test_race_ui.RaceUITests.test_resize_does_not_apply_catchup_time) ... ok
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
Ran 110 tests in 0.898s

OK (skipped=2)

# checklist item race
$ ["python3", "-B", "-c", "import unittest; s=unittest.defaultTestLoader.discover('tests', pattern='test_race*.py'); assert s.countTestCases() > 0, 'No tests discovered'; r=unittest.TextTestRunner(verbosity=2).run(s); raise SystemExit(not r.wasSuccessful())"]
test_error_freezes_both_until_explicit_retry (test_race.RaceTests.test_error_freezes_both_until_explicit_retry) ... ok
test_every_option_is_legal_and_enumeration_does_not_mutate (test_race.RaceTests.test_every_option_is_legal_and_enumeration_does_not_mutate) ... ok
test_finished_match_accounts_inflight_reply_without_applying (test_race.RaceTests.test_finished_match_accounts_inflight_reply_without_applying) ... ok
test_human_finish_stops_new_calls_and_actions (test_race.RaceTests.test_human_finish_stops_new_calls_and_actions) ... ok
test_invalid_provider_choice_is_visible_error (test_race.RaceTests.test_invalid_provider_choice_is_visible_error) ... ok
test_pause_freezes_both_and_defers_reply_but_counts_cost (test_race.RaceTests.test_pause_freezes_both_and_defers_reply_but_counts_cost) ... ok
test_resize_freezes_and_accounts_reply (test_race.RaceTests.test_resize_freezes_and_accounts_reply) ... ok
test_responsive_while_waiting_and_only_one_inflight (test_race.RaceTests.test_responsive_while_waiting_and_only_one_inflight) ... ok
test_restart_ignores_old_reply_but_keeps_cost_and_worker (test_race.RaceTests.test_restart_ignores_old_reply_but_keeps_cost_and_worker) ... ok
test_same_kind_next_piece_still_rejects_stale_response (test_race.RaceTests.test_same_kind_next_piece_still_rejects_stale_response) ... ok
test_same_sequence_including_without_seed (test_race.RaceTests.test_same_sequence_including_without_seed) ... ok
test_simultaneous_finish_is_draw (test_race.RaceTests.test_simultaneous_finish_is_draw) ... ok
test_topout_and_simultaneous_topout (test_race.RaceTests.test_topout_and_simultaneous_topout) ... ok
test_80_by_30_has_full_boards_status_cost_and_controls (test_race_ui.RaceUITests.test_80_by_30_has_full_boards_status_cost_and_controls) ... ok
test_cli_missing_key_does_not_open_curses (test_race_ui.RaceUITests.test_cli_missing_key_does_not_open_curses) ... ok
test_cli_routes_versus_and_prints_final_cost (test_race_ui.RaceUITests.test_cli_routes_versus_and_prints_final_cost) ... ok
test_error_winner_and_small_screen_messages (test_race_ui.RaceUITests.test_error_winner_and_small_screen_messages) ... ok
test_global_controls_and_no_input_during_pause_error_or_resize (test_race_ui.RaceUITests.test_global_controls_and_no_input_during_pause_error_or_resize) ... ok
test_loop_handles_input_while_provider_is_waiting_and_quits (test_race_ui.RaceUITests.test_loop_handles_input_while_provider_is_waiting_and_quits) ... ok
test_resize_does_not_apply_catchup_time (test_race_ui.RaceUITests.test_resize_does_not_apply_catchup_time) ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.220s

OK

# checklist item cost
$ ["python3", "-B", "-c", "import unittest; s=unittest.defaultTestLoader.discover('tests', pattern='test_jev_cost*.py'); assert s.countTestCases() > 0, 'No tests discovered'; r=unittest.TextTestRunner(verbosity=2).run(s); raise SystemExit(not r.wasSuccessful())"]
test_empty_key_fails_before_network (test_jev_cost.ClientTests.test_empty_key_fails_before_network) ... ok
test_http_error_does_not_follow_redirects_or_retry (test_jev_cost.ClientTests.test_http_error_does_not_follow_redirects_or_retry) ... ok
test_invalid_reply_preserves_reported_usage (test_jev_cost.ClientTests.test_invalid_reply_preserves_reported_usage) ... ok
test_malformed_shapes_are_errors (test_jev_cost.ClientTests.test_malformed_shapes_are_errors) ... ok
test_request_contract_and_usage (test_jev_cost.ClientTests.test_request_contract_and_usage) ... ok
test_slow_response_obeys_total_deadline (test_jev_cost.ClientTests.test_slow_response_obeys_total_deadline) ... ok
test_timeout_and_network_failures_do_not_retry_or_leak (test_jev_cost.ClientTests.test_timeout_and_network_failures_do_not_retry_or_leak) ... ok
test_missing_invalid_and_unknown_usage_never_looks_free (test_jev_cost.CostTests.test_missing_invalid_and_unknown_usage_never_looks_free) ... ok
test_tiny_costs_accumulate_across_calls_without_rounding (test_jev_cost.CostTests.test_tiny_costs_accumulate_across_calls_without_rounding) ... ok
test_zero_reported_usage_and_inflight_cost (test_jev_cost.CostTests.test_zero_reported_usage_and_inflight_cost) ... ok
test_single_request_and_exactly_once_delivery (test_jev_cost.WorkerTests.test_single_request_and_exactly_once_delivery) ... ok
test_worker_exception_becomes_visible_reply (test_jev_cost.WorkerTests.test_worker_exception_becomes_visible_reply) ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.512s

OK

# checklist item terminal
$ ["python3", "-B", "-c", "import unittest; s=unittest.defaultTestLoader.discover('tests', pattern='test_race_ui*.py'); assert s.countTestCases() > 0, 'No tests discovered'; r=unittest.TextTestRunner(verbosity=2).run(s); raise SystemExit(not r.wasSuccessful())"]
test_80_by_30_has_full_boards_status_cost_and_controls (test_race_ui.RaceUITests.test_80_by_30_has_full_boards_status_cost_and_controls) ... ok
test_cli_missing_key_does_not_open_curses (test_race_ui.RaceUITests.test_cli_missing_key_does_not_open_curses) ... ok
test_cli_routes_versus_and_prints_final_cost (test_race_ui.RaceUITests.test_cli_routes_versus_and_prints_final_cost) ... ok
test_error_winner_and_small_screen_messages (test_race_ui.RaceUITests.test_error_winner_and_small_screen_messages) ... ok
test_global_controls_and_no_input_during_pause_error_or_resize (test_race_ui.RaceUITests.test_global_controls_and_no_input_during_pause_error_or_resize) ... ok
test_loop_handles_input_while_provider_is_waiting_and_quits (test_race_ui.RaceUITests.test_loop_handles_input_while_provider_is_waiting_and_quits) ... ok
test_resize_does_not_apply_catchup_time (test_race_ui.RaceUITests.test_resize_does_not_apply_catchup_time) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.016s

OK
