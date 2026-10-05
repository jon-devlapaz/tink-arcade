
$ ["python3", "-B", "-c", "import unittest; s=unittest.defaultTestLoader.discover('tests', pattern='test*.py'); assert s.countTestCases() > 0, 'No tests discovered'; r=unittest.TextTestRunner(verbosity=2).run(s); raise SystemExit(not r.wasSuccessful())"]
test_context_cleanup_preserves_unexpected_errors (test_audio.PlaybackTests) ... ok
test_expired_cues_do_not_play_late (test_audio.PlaybackTests) ... ok
test_input_batch_retains_only_the_highest_priority_cue (test_audio.PlaybackTests) ... ok
test_mute_cancels_active_and_pending_cues_and_can_resume (test_audio.PlaybackTests) ... ok
test_player_failure_disables_audio_without_retry_spam (test_audio.PlaybackTests) ... ok
test_preloads_unique_samples_once_and_uses_all_three_choices (test_audio.PlaybackTests) ... ok
test_ready_backend_plays_consecutive_frames_without_waiting_for_a_tail (test_audio.PlaybackTests) ... ok
test_tick_failure_is_reported_and_releases_resources (test_audio.PlaybackTests) ... ok
test_unknown_cue_is_an_explicit_error_even_when_disabled (test_audio.PlaybackTests) ... ok
test_cancelled_child_is_not_reported_as_failure (test_audio.ProcessFallbackTests) ... ok
test_hung_child_and_cleanup_are_bounded (test_audio.ProcessFallbackTests) ... ok
test_missing_player_and_aplay_selection (test_audio.ProcessFallbackTests) ... ok
test_mute_escalates_to_kill_without_blocking (test_audio.ProcessFallbackTests) ... ok
test_nonzero_exit_and_spawn_errors_are_explicit (test_audio.ProcessFallbackTests) ... ok
test_polling_never_waits_during_normal_playback (test_audio.ProcessFallbackTests) ... ok
test_disabled_audio_does_not_probe_assets_or_initialize_backend (test_audio.SetupTests) ... ok
test_mac_uses_preloaded_backend_not_external_player (test_audio.SetupTests) ... ok
test_missing_asset_is_reported (test_audio.SetupTests) ... ok
test_non_mac_retains_portable_fallback (test_audio.SetupTests) ... ok
test_unavailable_backend_is_reported (test_audio.SetupTests) ... ok
test_blocked_controls_and_paused_gameplay_are_silent (test_audio.SoundEventTests) ... ok
test_gravity_lock_gets_a_placement_sound (test_audio.SoundEventTests) ... ok
test_line_clear_supersedes_drop_and_does_not_repeat_during_flash (test_audio.SoundEventTests) ... ok
test_pause_resume_and_mute_controls (test_audio.SoundEventTests) ... ok
test_successful_controls_use_the_selected_keyboard_cues (test_audio.SoundEventTests) ... ok
test_top_out_uses_the_enter_clack (test_audio.SoundEventTests) ... ok
test_bounded_elapsed_and_restart (test_breakout_engine.BreakoutEngineTests) ... ok
test_each_brick_face_and_ceiling (test_breakout_engine.BreakoutEngineTests) ... ok
test_fast_brick_crossing_scores_once (test_breakout_engine.BreakoutEngineTests) ... ok
test_loss_keeps_progress_and_stops_at_zero (test_breakout_engine.BreakoutEngineTests) ... ok
test_only_last_brick_advances_and_final_wins (test_breakout_engine.BreakoutEngineTests) ... ok
test_paddle_bounds_and_terminal_states (test_breakout_engine.BreakoutEngineTests) ... ok
test_start_launch_and_invalid_time (test_breakout_engine.BreakoutEngineTests) ... ok
test_tied_bricks_and_corner_reflect_once (test_breakout_engine.BreakoutEngineTests) ... ok
test_wall_and_paddle_center_edges (test_breakout_engine.BreakoutEngineTests) ... ok
test_legal_full_clear_and_determinism (test_breakout_layouts.BreakoutLayoutTests) ... ok
test_patterns_and_bounds (test_breakout_layouts.BreakoutLayoutTests) ... ok
test_controls_and_case_variants (test_breakout_ui.BreakoutUITests) ... ok
test_help_nonterminal_and_interrupt_cleanup (test_breakout_ui.BreakoutUITests) ... ok
test_monochrome_and_safe_clipping (test_breakout_ui.BreakoutUITests) ... ok
test_resize_ignores_game_input_and_preserves_pause (test_breakout_ui.BreakoutUITests) ... ok
test_bays (test_crossing_engine.LayoutTests) ... ok
test_board_rows_and_lanes (test_crossing_engine.LayoutTests) ... ok
test_periods_scale_with_level (test_crossing_engine.LayoutTests) ... ok
test_bays_fill_and_wall_and_repeat (test_crossing_engine.RuleTests) ... ok
test_carried_off_edge (test_crossing_engine.RuleTests) ... ok
test_elapsed_cap_and_validation (test_crossing_engine.RuleTests) ... ok
test_game_over_freezes (test_crossing_engine.RuleTests) ... ok
test_hop_clamps_and_scores_new_rows_once (test_crossing_engine.RuleTests) ... ok
test_lanes_move_one_cell_per_period (test_crossing_engine.RuleTests) ... ok
test_levels_and_win (test_crossing_engine.RuleTests) ... ok
test_new_game (test_crossing_engine.RuleTests) ... ok
test_pause_freezes_and_blocks_hops (test_crossing_engine.RuleTests) ... ok
test_road_hit_on_hop_and_by_shift (test_crossing_engine.RuleTests) ... ok
test_water_and_logs_carry (test_crossing_engine.RuleTests) ... ok
test_actions_and_cues (test_crossing_ui.CrossingUITests) ... ok
test_cells (test_crossing_ui.CrossingUITests) ... ok
test_cli (test_crossing_ui.CrossingUITests) ... ok
test_hop_bindings_both_cases (test_crossing_ui.CrossingUITests) ... ok
test_layout_states_sizes_bounds (test_crossing_ui.CrossingUITests) ... ok
test_loop_caps_delay_and_discards_transition_and_resize_time (test_crossing_ui.CrossingUITests) ... ok
test_menu_entry (test_crossing_ui.CrossingUITests) ... ok
test_small_terminal (test_crossing_ui.CrossingUITests) ... ok
test_above_board_lock_out_is_atomic (test_engine.EngineTests) ... ok
test_collision_and_invalid_access_guard (test_engine.EngineTests) ... ok
test_exhausted_deadline_locks_on_rotation_and_move_contact (test_engine.EngineTests) ... ok
test_exhausted_lock_timer_survives_lift_off_and_soft_drop_contact (test_engine.EngineTests) ... ok
test_failed_moves_do_not_reset_lock (test_engine.EngineTests) ... ok
test_floor_kick_cycles_cannot_bypass_lock_budget (test_engine.EngineTests) ... ok
test_ghost_matches_hard_drop_and_drop_points (test_engine.EngineTests) ... ok
test_gravity_pause_and_bounded_time (test_engine.EngineTests) ... ok
test_hold_gating_swap_orientation_and_timer_reset (test_engine.EngineTests) ... ok
test_hold_spawn_collision_tops_out (test_engine.EngineTests) ... ok
test_lock_delay_and_bounded_resets (test_engine.EngineTests) ... ok
test_restart_resets_play_state_and_preserves_session_best (test_engine.EngineTests) ... ok
test_rotation_round_trip_and_obstruction (test_engine.EngineTests) ... ok
test_scoring_and_level_progression (test_engine.EngineTests) ... ok
test_simultaneous_nonadjacent_line_clearing (test_engine.EngineTests) ... ok
test_soft_drop_only_scores_successful_steps (test_engine.EngineTests) ... ok
test_spawn_and_all_piece_rotations_have_four_cells (test_engine.EngineTests) ... ok
test_spawn_top_out_and_game_over_actions (test_engine.EngineTests) ... ok
test_wall_and_floor_kicks (test_engine.EngineTests) ... ok
test_fairness_and_preview (test_engine.SevenBagTests) ... ok
test_seed_determinism (test_engine.SevenBagTests) ... ok
test_clock_frame_partition (test_galaga.GalagaTests) ... ok
test_damage_and_protection (test_galaga.GalagaTests) ... ok
test_dive_returns_to_formation (test_galaga.GalagaTests) ... ok
test_enemy_contact_hits_player (test_galaga.GalagaTests) ... ok
test_enemy_dives_and_fires (test_galaga.GalagaTests) ... ok
test_fire_cooldown (test_galaga.GalagaTests) ... ok
test_game_over_stops_and_restart_resets_seed (test_galaga.GalagaTests) ... ok
test_help_and_non_terminal (test_galaga.GalagaTests) ... ok
test_higher_wave_has_faster_attacks (test_galaga.GalagaTests) ... ok
test_key_controls (test_galaga.GalagaTests) ... ok
test_missed_shot_does_not_score (test_galaga.GalagaTests) ... ok
test_movement_bounds (test_galaga.GalagaTests) ... ok
test_pause_blocks_time_and_input (test_galaga.GalagaTests) ... ok
test_seed_repeats_inputs_and_enemy_choices (test_galaga.GalagaTests) ... ok
test_shot_kills_only_first_enemy_in_path (test_galaga.GalagaTests) ... ok
test_stall_and_resize_do_not_catch_up (test_galaga.GalagaTests) ... ok
test_wave_advances_and_clears_danger (test_galaga.GalagaTests) ... ok
test_clear_each_wave_requires_all_enemies (test_invaders_engine.EngineTests) ... ok
test_enemy_reaching_ship_row_costs_one_life (test_invaders_engine.EngineTests) ... ok
test_formations_and_partial_clear (test_invaders_engine.EngineTests) ... ok
test_full_legal_replay (test_invaders_engine.EngineTests) ... ok
test_input_and_enemy_fire_limits (test_invaders_engine.EngineTests) ... ok
test_invalid_negative_and_delayed_time (test_invaders_engine.EngineTests) ... ok
test_multiple_hits_lose_one_life_and_preserve_survivors (test_invaders_engine.EngineTests) ... ok
test_only_surviving_bottom_enemies_fire (test_invaders_engine.EngineTests) ... ok
test_opposing_shots_pass_through (test_invaders_engine.EngineTests) ... ok
test_restart_and_seed_repeatability (test_invaders_engine.EngineTests) ... ok
test_reversal_descends_and_keeps_bounds (test_invaders_engine.EngineTests) ... ok
test_shot_collision_sweeps_marching_and_descending_enemy (test_invaders_engine.EngineTests) ... ok
test_simultaneous_last_enemy_and_ship_hit (test_invaders_engine.EngineTests) ... ok
test_swept_player_collision_hits_only_first_target (test_invaders_engine.EngineTests) ... ok
test_capture_adapter_does_not_mutate_observed_state (test_invaders_helpers.HelperTests) ... ok
test_explicit_destination_failure_retains_partial_evidence_and_cleans_up (test_invaders_helpers.HelperTests) ... ok
test_require_survives_optimized_python (test_invaders_helpers.HelperTests) ... ok
test_suite_rejects_missing_skipped_failed_and_unexecuted_required_groups (test_invaders_helpers.HelperTests) ... ok
test_terminal_cli_requires_output_and_failure_returns_nonzero (test_invaders_helpers.HelperTests) ... ok
test_bindings_and_start_does_not_fire (test_invaders_ui.UITests) ... ok
test_bounded_input_loop_draws_and_updates (test_invaders_ui.UITests) ... ok
test_cli_help_nonterminal_options_and_warning (test_invaders_ui.UITests) ... ok
test_cue_mapping_and_blocked_actions (test_invaders_ui.UITests) ... ok
test_end_states_ignore_gameplay (test_invaders_ui.UITests) ... ok
test_frozen_idle_frames_do_not_discard_fresh_resume_keys (test_invaders_ui.UITests) ... ok
test_layout_contains_states_stats_and_distinct_marks (test_invaders_ui.UITests) ... ok
test_palette_and_safe_clipping (test_invaders_ui.UITests) ... ok
test_pause_freezes_every_clock_and_suppresses_queued_input (test_invaders_ui.UITests) ... ok
test_repeated_space_cannot_freeze_clocks (test_invaders_ui.UITests) ... ok
test_resize_freezes_and_preserves_pause (test_invaders_ui.UITests) ... ok
test_restart_from_every_state_keeps_mute (test_invaders_ui.UITests) ... ok
test_run_cleanup_normal_and_error_disabled_and_unavailable_audio (test_invaders_ui.UITests) ... ok
test_empty_key_fails_before_network (test_jev_cost.ClientTests) ... ok
test_http_error_does_not_follow_redirects_or_retry (test_jev_cost.ClientTests) ... ok
test_invalid_reply_preserves_reported_usage (test_jev_cost.ClientTests) ... ok
test_malformed_shapes_are_errors (test_jev_cost.ClientTests) ... ok
test_request_contract_and_usage (test_jev_cost.ClientTests) ... ok
test_slow_response_obeys_total_deadline (test_jev_cost.ClientTests) ... ok
test_timeout_and_network_failures_do_not_retry_or_leak (test_jev_cost.ClientTests) ... ok
test_missing_invalid_and_unknown_usage_never_looks_free (test_jev_cost.CostTests) ... ok
test_tiny_costs_accumulate_across_calls_without_rounding (test_jev_cost.CostTests) ... ok
test_zero_reported_usage_and_inflight_cost (test_jev_cost.CostTests) ... ok
test_single_request_and_exactly_once_delivery (test_jev_cost.WorkerTests) ... ok
test_worker_exception_becomes_visible_reply (test_jev_cost.WorkerTests) ... ok
test_asset_read_failure_releases_previously_created_players (test_mac_audio.NativePlaybackTests) ... ok
test_close_releases_every_voice_once (test_mac_audio.NativePlaybackTests) ... ok
test_completed_voice_is_reprepared_before_the_next_key (test_mac_audio.NativePlaybackTests) ... ok
test_data_allocation_failure_is_explicit (test_mac_audio.NativePlaybackTests) ... ok
test_finished_sample_remains_audible_on_every_replay (test_mac_audio.NativePlaybackTests) ... ok
test_independent_sample_voices_can_overlap (test_mac_audio.NativePlaybackTests) ... ok
test_mute_pauses_all_voices_without_releasing_or_reallocating (test_mac_audio.NativePlaybackTests) ... ok
test_partial_load_failure_releases_previously_created_players (test_mac_audio.NativePlaybackTests) ... ok
test_play_and_reprepare_failures_are_explicit (test_mac_audio.NativePlaybackTests) ... ok
test_preloads_bounded_voices_once_and_reuses_them_under_repeat (test_mac_audio.NativePlaybackTests) ... ok
test_preparation_failure_releases_the_failed_player_too (test_mac_audio.NativePlaybackTests) ... ok
test_poll_services_default_mode_without_waiting (test_mac_audio.RunLoopTests) ... ok
test_each_sample_renders_on_repeated_spaced_plays (test_native_audio.NativeAudioIntegrationTests) ... skipped 'set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples'
test_replay_after_mute_and_resume (test_native_audio.NativeAudioIntegrationTests) ... skipped 'set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples'
test_computer_follows_current_height_only_at_bounded_speed (test_pong_engine.PongEngineTests) ... ok
test_delayed_frames_bounded_and_invalid_elapsed (test_pong_engine.PongEngineTests) ... ok
test_new_match_serve_alternation_and_restart (test_pong_engine.PongEngineTests) ... ok
test_ordinary_legal_player_win_and_idle_loss_replays (test_pong_engine.PongEngineTests) ... ok
test_paddle_returns_speed_and_contact_angle (test_pong_engine.PongEngineTests) ... ok
test_player_bounds_and_pause_freeze (test_pong_engine.PongEngineTests) ... ok
test_seven_ends_match_and_all_motion_stops (test_pong_engine.PongEngineTests) ... ok
test_swept_contacts_walls_misses_and_corner (test_pong_engine.PongEngineTests) ... ok
test_audio_mute_restart_disabled_unavailable_cleanup (test_pong_ui.PongUITests) ... ok
test_bindings_and_action_cues (test_pong_ui.PongUITests) ... ok
test_cli_flags_help_and_nonterminal (test_pong_ui.PongUITests) ... ok
test_layout_all_states_sizes_and_bounds (test_pong_ui.PongUITests) ... ok
test_loop_routes_contact_point_loss_and_silent_wall (test_pong_ui.PongUITests) ... ok
test_palette_and_monochrome (test_pong_ui.PongUITests) ... ok
test_repeated_noop_input_does_not_discard_rally_time (test_pong_ui.PongUITests) ... ok
test_resize_and_transition_frames_discard_elapsed (test_pong_ui.PongUITests) ... ok
test_small_and_clipping_errors (test_pong_ui.PongUITests) ... ok
test_error_freezes_both_until_explicit_retry (test_race.RaceTests) ... ok
test_every_option_is_legal_and_enumeration_does_not_mutate (test_race.RaceTests) ... ok
test_finished_match_accounts_inflight_reply_without_applying (test_race.RaceTests) ... ok
test_human_finish_stops_new_calls_and_actions (test_race.RaceTests) ... ok
test_invalid_provider_choice_is_visible_error (test_race.RaceTests) ... ok
test_pause_freezes_both_and_defers_reply_but_counts_cost (test_race.RaceTests) ... ok
test_resize_freezes_and_accounts_reply (test_race.RaceTests) ... ok
test_responsive_while_waiting_and_only_one_inflight (test_race.RaceTests) ... ok
test_restart_ignores_old_reply_but_keeps_cost_and_worker (test_race.RaceTests) ... ok
test_same_kind_next_piece_still_rejects_stale_response (test_race.RaceTests) ... ok
test_same_sequence_including_without_seed (test_race.RaceTests) ... ok
test_simultaneous_finish_is_draw (test_race.RaceTests) ... ok
test_topout_and_simultaneous_topout (test_race.RaceTests) ... ok
test_80_by_30_has_full_boards_status_cost_and_controls (test_race_ui.RaceUITests) ... ok
test_cli_missing_key_does_not_open_curses (test_race_ui.RaceUITests) ... ok
test_cli_routes_versus_and_prints_final_cost (test_race_ui.RaceUITests) ... ok
test_error_winner_and_small_screen_messages (test_race_ui.RaceUITests) ... ok
test_global_controls_and_no_input_during_pause_error_or_resize (test_race_ui.RaceUITests) ... ok
test_loop_handles_input_while_provider_is_waiting_and_quits (test_race_ui.RaceUITests) ... ok
test_resize_does_not_apply_catchup_time (test_race_ui.RaceUITests) ... ok
test_bundled_clicks_are_short_pcm_with_headroom_and_soft_edges (test_samples.SampleTests) ... ok
test_selected_samples_have_provenance_and_matching_hashes (test_samples.SampleTests) ... ok
test_each_wall_collision (test_snake_engine.SnakeRulesTests) ... ok
test_food_uniform_selection_uses_all_free_cells (test_snake_engine.SnakeRulesTests) ... ok
test_full_board_has_no_food_and_freezes (test_snake_engine.SnakeRulesTests) ... ok
test_initial_movement_growth_and_food_exclusion (test_snake_engine.SnakeRulesTests) ... ok
test_pause_remaining_timer_and_delayed_frame_cap (test_snake_engine.SnakeRulesTests) ... ok
test_queue_order_reverse_duplicates_and_overflow (test_snake_engine.SnakeRulesTests) ... ok
test_restart_resets_state_and_repeats_seed_preserving_best (test_snake_engine.SnakeRulesTests) ... ok
test_speed_boundaries_and_new_interval_after_food (test_snake_engine.SnakeRulesTests) ... ok
test_tail_departure_is_legal_but_body_collision_ends_game (test_snake_engine.SnakeRulesTests) ... ok
test_all_bindings (test_snake_ui.SnakeUITests) ... ok
test_ascii_layout_bounds_marks_overlays_and_centering (test_snake_ui.SnakeUITests) ... ok
test_cli_help_flags_nonterminal_and_error_after_wrapper (test_snake_ui.SnakeUITests) ... ok
test_clipping_and_resize_errors (test_snake_ui.SnakeUITests) ... ok
test_loop_successful_turn_food_collision_and_straight_cues (test_snake_ui.SnakeUITests) ... ok
test_palette_matches_tetris_in_256_and_eight_colors (test_snake_ui.SnakeUITests) ... ok
test_pause_restart_overlay_and_rejected_input_audio (test_snake_ui.SnakeUITests) ... ok
test_real_audio_coalescing_mute_disabled_failure_and_cleanup (test_snake_ui.SnakeUITests) ... ok
test_resize_freezes_time_clears_turns_polls_audio_and_keeps_pause (test_snake_ui.SnakeUITests) ... ok
test_run_closes_audio_on_quit_interrupt_and_exception (test_snake_ui.SnakeUITests) ... ok
test_default_and_relative_destinations (test_terminal_checker_compatibility.CheckerCompatibilityTests) ... ok
test_failure_writes_selected_transcript_and_exits_nonzero (test_terminal_checker_compatibility.CheckerCompatibilityTests) ... ok
test_help_and_argument_errors (test_terminal_checker_compatibility.CheckerCompatibilityTests) ... ok
test_both_turns_in_wrong_order_are_rejected (test_terminal_checker_compatibility.OrderedMovementTests) ... ok
test_directions_without_movement_are_rejected (test_terminal_checker_compatibility.OrderedMovementTests) ... ok
test_consumed_first_turn_is_accepted (test_terminal_checkers.SnakeQueueCheckerTests) ... ok
test_early_input_is_accepted (test_terminal_checkers.SnakeQueueCheckerTests) ... ok
test_missing_or_wrong_order_turns_are_rejected (test_terminal_checkers.SnakeQueueCheckerTests) ... ok
test_explicit_external_destination_preserves_existing_evidence (test_terminal_checkers.TranscriptDestinationTests) ... ok
test_audio_failure_is_reported_after_curses_returns (test_ui.CLITests) ... ok
test_help_without_tty (test_ui.CLITests) ... ok
test_invalid_seed (test_ui.CLITests) ... ok
test_no_sound_and_color_flags_reach_the_game (test_ui.CLITests) ... ok
test_non_tty_fails_cleanly (test_ui.CLITests) ... ok
test_terminal_error_and_ctrl_c_are_clean (test_ui.CLITests) ... ok
test_keyboard_mapping (test_ui.InputTests) ... ok
test_pause_and_restart_controls (test_ui.InputTests) ... ok
test_renderer_clips_and_tolerates_resize_errors (test_ui.InputTests) ... ok
test_renderer_does_not_swallow_programming_errors (test_ui.InputTests) ... ok
test_resize_freezes_simulation_and_discards_catchup (test_ui.InputTests) ... ok
test_active_ink_and_pencil_ghost_are_distinct (test_ui.ThemeTests) ... ok
test_no_color_does_not_initialize_colors (test_ui.ThemeTests) ... ok
test_paper_palette_and_basic_terminal_fallback (test_ui.ThemeTests) ... ok
test_socratink_copy_on_board_and_overlays (test_ui.ThemeTests) ... ok

----------------------------------------------------------------------
Ran 241 tests in 25.219s

OK (skipped=2)
Legal full-clear replay: seed=20261004, steps=31475, boards=[(0, 16548, 360, 3), (1, 19078, 480, 3), (2, 31474, 760, 3)]
Legal replay: seed=7, steps=1528/36000, score=340, lives=3

$ ["python3", "-B", "-c", "import unittest; s=unittest.defaultTestLoader.discover('tests'); assert s.countTestCases()>0, 'No tests discovered'; r=unittest.TextTestRunner(verbosity=2).run(s); raise SystemExit(not r.wasSuccessful())"]
test_context_cleanup_preserves_unexpected_errors (test_audio.PlaybackTests) ... ok
test_expired_cues_do_not_play_late (test_audio.PlaybackTests) ... ok
test_input_batch_retains_only_the_highest_priority_cue (test_audio.PlaybackTests) ... ok
test_mute_cancels_active_and_pending_cues_and_can_resume (test_audio.PlaybackTests) ... ok
test_player_failure_disables_audio_without_retry_spam (test_audio.PlaybackTests) ... ok
test_preloads_unique_samples_once_and_uses_all_three_choices (test_audio.PlaybackTests) ... ok
test_ready_backend_plays_consecutive_frames_without_waiting_for_a_tail (test_audio.PlaybackTests) ... ok
test_tick_failure_is_reported_and_releases_resources (test_audio.PlaybackTests) ... ok
test_unknown_cue_is_an_explicit_error_even_when_disabled (test_audio.PlaybackTests) ... ok
test_cancelled_child_is_not_reported_as_failure (test_audio.ProcessFallbackTests) ... ok
test_hung_child_and_cleanup_are_bounded (test_audio.ProcessFallbackTests) ... ok
test_missing_player_and_aplay_selection (test_audio.ProcessFallbackTests) ... ok
test_mute_escalates_to_kill_without_blocking (test_audio.ProcessFallbackTests) ... ok
test_nonzero_exit_and_spawn_errors_are_explicit (test_audio.ProcessFallbackTests) ... ok
test_polling_never_waits_during_normal_playback (test_audio.ProcessFallbackTests) ... ok
test_disabled_audio_does_not_probe_assets_or_initialize_backend (test_audio.SetupTests) ... ok
test_mac_uses_preloaded_backend_not_external_player (test_audio.SetupTests) ... ok
test_missing_asset_is_reported (test_audio.SetupTests) ... ok
test_non_mac_retains_portable_fallback (test_audio.SetupTests) ... ok
test_unavailable_backend_is_reported (test_audio.SetupTests) ... ok
test_blocked_controls_and_paused_gameplay_are_silent (test_audio.SoundEventTests) ... ok
test_gravity_lock_gets_a_placement_sound (test_audio.SoundEventTests) ... ok
test_line_clear_supersedes_drop_and_does_not_repeat_during_flash (test_audio.SoundEventTests) ... ok
test_pause_resume_and_mute_controls (test_audio.SoundEventTests) ... ok
test_successful_controls_use_the_selected_keyboard_cues (test_audio.SoundEventTests) ... ok
test_top_out_uses_the_enter_clack (test_audio.SoundEventTests) ... ok
test_bounded_elapsed_and_restart (test_breakout_engine.BreakoutEngineTests) ... ok
test_each_brick_face_and_ceiling (test_breakout_engine.BreakoutEngineTests) ... ok
test_fast_brick_crossing_scores_once (test_breakout_engine.BreakoutEngineTests) ... ok
test_loss_keeps_progress_and_stops_at_zero (test_breakout_engine.BreakoutEngineTests) ... ok
test_only_last_brick_advances_and_final_wins (test_breakout_engine.BreakoutEngineTests) ... ok
test_paddle_bounds_and_terminal_states (test_breakout_engine.BreakoutEngineTests) ... ok
test_start_launch_and_invalid_time (test_breakout_engine.BreakoutEngineTests) ... ok
test_tied_bricks_and_corner_reflect_once (test_breakout_engine.BreakoutEngineTests) ... ok
test_wall_and_paddle_center_edges (test_breakout_engine.BreakoutEngineTests) ... ok
test_legal_full_clear_and_determinism (test_breakout_layouts.BreakoutLayoutTests) ... ok
test_patterns_and_bounds (test_breakout_layouts.BreakoutLayoutTests) ... ok
test_controls_and_case_variants (test_breakout_ui.BreakoutUITests) ... ok
test_help_nonterminal_and_interrupt_cleanup (test_breakout_ui.BreakoutUITests) ... ok
test_monochrome_and_safe_clipping (test_breakout_ui.BreakoutUITests) ... ok
test_resize_ignores_game_input_and_preserves_pause (test_breakout_ui.BreakoutUITests) ... ok
test_bays (test_crossing_engine.LayoutTests) ... ok
test_board_rows_and_lanes (test_crossing_engine.LayoutTests) ... ok
test_periods_scale_with_level (test_crossing_engine.LayoutTests) ... ok
test_bays_fill_and_wall_and_repeat (test_crossing_engine.RuleTests) ... ok
test_carried_off_edge (test_crossing_engine.RuleTests) ... ok
test_elapsed_cap_and_validation (test_crossing_engine.RuleTests) ... ok
test_game_over_freezes (test_crossing_engine.RuleTests) ... ok
test_hop_clamps_and_scores_new_rows_once (test_crossing_engine.RuleTests) ... ok
test_lanes_move_one_cell_per_period (test_crossing_engine.RuleTests) ... ok
test_levels_and_win (test_crossing_engine.RuleTests) ... ok
test_new_game (test_crossing_engine.RuleTests) ... ok
test_pause_freezes_and_blocks_hops (test_crossing_engine.RuleTests) ... ok
test_road_hit_on_hop_and_by_shift (test_crossing_engine.RuleTests) ... ok
test_water_and_logs_carry (test_crossing_engine.RuleTests) ... ok
test_actions_and_cues (test_crossing_ui.CrossingUITests) ... ok
test_cells (test_crossing_ui.CrossingUITests) ... ok
test_cli (test_crossing_ui.CrossingUITests) ... ok
test_hop_bindings_both_cases (test_crossing_ui.CrossingUITests) ... ok
test_layout_states_sizes_bounds (test_crossing_ui.CrossingUITests) ... ok
test_loop_caps_delay_and_discards_transition_and_resize_time (test_crossing_ui.CrossingUITests) ... ok
test_menu_entry (test_crossing_ui.CrossingUITests) ... ok
test_small_terminal (test_crossing_ui.CrossingUITests) ... ok
test_above_board_lock_out_is_atomic (test_engine.EngineTests) ... ok
test_collision_and_invalid_access_guard (test_engine.EngineTests) ... ok
test_exhausted_deadline_locks_on_rotation_and_move_contact (test_engine.EngineTests) ... ok
test_exhausted_lock_timer_survives_lift_off_and_soft_drop_contact (test_engine.EngineTests) ... ok
test_failed_moves_do_not_reset_lock (test_engine.EngineTests) ... ok
test_floor_kick_cycles_cannot_bypass_lock_budget (test_engine.EngineTests) ... ok
test_ghost_matches_hard_drop_and_drop_points (test_engine.EngineTests) ... ok
test_gravity_pause_and_bounded_time (test_engine.EngineTests) ... ok
test_hold_gating_swap_orientation_and_timer_reset (test_engine.EngineTests) ... ok
test_hold_spawn_collision_tops_out (test_engine.EngineTests) ... ok
test_lock_delay_and_bounded_resets (test_engine.EngineTests) ... ok
test_restart_resets_play_state_and_preserves_session_best (test_engine.EngineTests) ... ok
test_rotation_round_trip_and_obstruction (test_engine.EngineTests) ... ok
test_scoring_and_level_progression (test_engine.EngineTests) ... ok
test_simultaneous_nonadjacent_line_clearing (test_engine.EngineTests) ... ok
test_soft_drop_only_scores_successful_steps (test_engine.EngineTests) ... ok
test_spawn_and_all_piece_rotations_have_four_cells (test_engine.EngineTests) ... ok
test_spawn_top_out_and_game_over_actions (test_engine.EngineTests) ... ok
test_wall_and_floor_kicks (test_engine.EngineTests) ... ok
test_fairness_and_preview (test_engine.SevenBagTests) ... ok
test_seed_determinism (test_engine.SevenBagTests) ... ok
test_clock_frame_partition (test_galaga.GalagaTests) ... ok
test_damage_and_protection (test_galaga.GalagaTests) ... ok
test_dive_returns_to_formation (test_galaga.GalagaTests) ... ok
test_enemy_contact_hits_player (test_galaga.GalagaTests) ... ok
test_enemy_dives_and_fires (test_galaga.GalagaTests) ... ok
test_fire_cooldown (test_galaga.GalagaTests) ... ok
test_game_over_stops_and_restart_resets_seed (test_galaga.GalagaTests) ... ok
test_help_and_non_terminal (test_galaga.GalagaTests) ... ok
test_higher_wave_has_faster_attacks (test_galaga.GalagaTests) ... ok
test_key_controls (test_galaga.GalagaTests) ... ok
test_missed_shot_does_not_score (test_galaga.GalagaTests) ... ok
test_movement_bounds (test_galaga.GalagaTests) ... ok
test_pause_blocks_time_and_input (test_galaga.GalagaTests) ... ok
test_seed_repeats_inputs_and_enemy_choices (test_galaga.GalagaTests) ... ok
test_shot_kills_only_first_enemy_in_path (test_galaga.GalagaTests) ... ok
test_stall_and_resize_do_not_catch_up (test_galaga.GalagaTests) ... ok
test_wave_advances_and_clears_danger (test_galaga.GalagaTests) ... ok
test_clear_each_wave_requires_all_enemies (test_invaders_engine.EngineTests) ... ok
test_enemy_reaching_ship_row_costs_one_life (test_invaders_engine.EngineTests) ... ok
test_formations_and_partial_clear (test_invaders_engine.EngineTests) ... ok
test_full_legal_replay (test_invaders_engine.EngineTests) ... ok
test_input_and_enemy_fire_limits (test_invaders_engine.EngineTests) ... ok
test_invalid_negative_and_delayed_time (test_invaders_engine.EngineTests) ... ok
test_multiple_hits_lose_one_life_and_preserve_survivors (test_invaders_engine.EngineTests) ... ok
test_only_surviving_bottom_enemies_fire (test_invaders_engine.EngineTests) ... ok
test_opposing_shots_pass_through (test_invaders_engine.EngineTests) ... ok
test_restart_and_seed_repeatability (test_invaders_engine.EngineTests) ... ok
test_reversal_descends_and_keeps_bounds (test_invaders_engine.EngineTests) ... ok
test_shot_collision_sweeps_marching_and_descending_enemy (test_invaders_engine.EngineTests) ... ok
test_simultaneous_last_enemy_and_ship_hit (test_invaders_engine.EngineTests) ... ok
test_swept_player_collision_hits_only_first_target (test_invaders_engine.EngineTests) ... ok
test_capture_adapter_does_not_mutate_observed_state (test_invaders_helpers.HelperTests) ... ok
test_explicit_destination_failure_retains_partial_evidence_and_cleans_up (test_invaders_helpers.HelperTests) ... ok
test_require_survives_optimized_python (test_invaders_helpers.HelperTests) ... ok
test_suite_rejects_missing_skipped_failed_and_unexecuted_required_groups (test_invaders_helpers.HelperTests) ... ok
test_terminal_cli_requires_output_and_failure_returns_nonzero (test_invaders_helpers.HelperTests) ... ok
test_bindings_and_start_does_not_fire (test_invaders_ui.UITests) ... ok
test_bounded_input_loop_draws_and_updates (test_invaders_ui.UITests) ... ok
test_cli_help_nonterminal_options_and_warning (test_invaders_ui.UITests) ... ok
test_cue_mapping_and_blocked_actions (test_invaders_ui.UITests) ... ok
test_end_states_ignore_gameplay (test_invaders_ui.UITests) ... ok
test_frozen_idle_frames_do_not_discard_fresh_resume_keys (test_invaders_ui.UITests) ... ok
test_layout_contains_states_stats_and_distinct_marks (test_invaders_ui.UITests) ... ok
test_palette_and_safe_clipping (test_invaders_ui.UITests) ... ok
test_pause_freezes_every_clock_and_suppresses_queued_input (test_invaders_ui.UITests) ... ok
test_repeated_space_cannot_freeze_clocks (test_invaders_ui.UITests) ... ok
test_resize_freezes_and_preserves_pause (test_invaders_ui.UITests) ... ok
test_restart_from_every_state_keeps_mute (test_invaders_ui.UITests) ... ok
test_run_cleanup_normal_and_error_disabled_and_unavailable_audio (test_invaders_ui.UITests) ... ok
test_empty_key_fails_before_network (test_jev_cost.ClientTests) ... ok
test_http_error_does_not_follow_redirects_or_retry (test_jev_cost.ClientTests) ... ok
test_invalid_reply_preserves_reported_usage (test_jev_cost.ClientTests) ... ok
test_malformed_shapes_are_errors (test_jev_cost.ClientTests) ... ok
test_request_contract_and_usage (test_jev_cost.ClientTests) ... ok
test_slow_response_obeys_total_deadline (test_jev_cost.ClientTests) ... ok
test_timeout_and_network_failures_do_not_retry_or_leak (test_jev_cost.ClientTests) ... ok
test_missing_invalid_and_unknown_usage_never_looks_free (test_jev_cost.CostTests) ... ok
test_tiny_costs_accumulate_across_calls_without_rounding (test_jev_cost.CostTests) ... ok
test_zero_reported_usage_and_inflight_cost (test_jev_cost.CostTests) ... ok
test_single_request_and_exactly_once_delivery (test_jev_cost.WorkerTests) ... ok
test_worker_exception_becomes_visible_reply (test_jev_cost.WorkerTests) ... ok
test_asset_read_failure_releases_previously_created_players (test_mac_audio.NativePlaybackTests) ... ok
test_close_releases_every_voice_once (test_mac_audio.NativePlaybackTests) ... ok
test_completed_voice_is_reprepared_before_the_next_key (test_mac_audio.NativePlaybackTests) ... ok
test_data_allocation_failure_is_explicit (test_mac_audio.NativePlaybackTests) ... ok
test_finished_sample_remains_audible_on_every_replay (test_mac_audio.NativePlaybackTests) ... ok
test_independent_sample_voices_can_overlap (test_mac_audio.NativePlaybackTests) ... ok
test_mute_pauses_all_voices_without_releasing_or_reallocating (test_mac_audio.NativePlaybackTests) ... ok
test_partial_load_failure_releases_previously_created_players (test_mac_audio.NativePlaybackTests) ... ok
test_play_and_reprepare_failures_are_explicit (test_mac_audio.NativePlaybackTests) ... ok
test_preloads_bounded_voices_once_and_reuses_them_under_repeat (test_mac_audio.NativePlaybackTests) ... ok
test_preparation_failure_releases_the_failed_player_too (test_mac_audio.NativePlaybackTests) ... ok
test_poll_services_default_mode_without_waiting (test_mac_audio.RunLoopTests) ... ok
test_each_sample_renders_on_repeated_spaced_plays (test_native_audio.NativeAudioIntegrationTests) ... skipped 'set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples'
test_replay_after_mute_and_resume (test_native_audio.NativeAudioIntegrationTests) ... skipped 'set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples'
test_computer_follows_current_height_only_at_bounded_speed (test_pong_engine.PongEngineTests) ... ok
test_delayed_frames_bounded_and_invalid_elapsed (test_pong_engine.PongEngineTests) ... ok
test_new_match_serve_alternation_and_restart (test_pong_engine.PongEngineTests) ... ok
test_ordinary_legal_player_win_and_idle_loss_replays (test_pong_engine.PongEngineTests) ... ok
test_paddle_returns_speed_and_contact_angle (test_pong_engine.PongEngineTests) ... ok
test_player_bounds_and_pause_freeze (test_pong_engine.PongEngineTests) ... ok
test_seven_ends_match_and_all_motion_stops (test_pong_engine.PongEngineTests) ... ok
test_swept_contacts_walls_misses_and_corner (test_pong_engine.PongEngineTests) ... ok
test_audio_mute_restart_disabled_unavailable_cleanup (test_pong_ui.PongUITests) ... ok
test_bindings_and_action_cues (test_pong_ui.PongUITests) ... ok
test_cli_flags_help_and_nonterminal (test_pong_ui.PongUITests) ... ok
test_layout_all_states_sizes_and_bounds (test_pong_ui.PongUITests) ... ok
test_loop_routes_contact_point_loss_and_silent_wall (test_pong_ui.PongUITests) ... ok
test_palette_and_monochrome (test_pong_ui.PongUITests) ... ok
test_repeated_noop_input_does_not_discard_rally_time (test_pong_ui.PongUITests) ... ok
test_resize_and_transition_frames_discard_elapsed (test_pong_ui.PongUITests) ... ok
test_small_and_clipping_errors (test_pong_ui.PongUITests) ... ok
test_error_freezes_both_until_explicit_retry (test_race.RaceTests) ... ok
test_every_option_is_legal_and_enumeration_does_not_mutate (test_race.RaceTests) ... ok
test_finished_match_accounts_inflight_reply_without_applying (test_race.RaceTests) ... ok
test_human_finish_stops_new_calls_and_actions (test_race.RaceTests) ... ok
test_invalid_provider_choice_is_visible_error (test_race.RaceTests) ... ok
test_pause_freezes_both_and_defers_reply_but_counts_cost (test_race.RaceTests) ... ok
test_resize_freezes_and_accounts_reply (test_race.RaceTests) ... ok
test_responsive_while_waiting_and_only_one_inflight (test_race.RaceTests) ... ok
test_restart_ignores_old_reply_but_keeps_cost_and_worker (test_race.RaceTests) ... ok
test_same_kind_next_piece_still_rejects_stale_response (test_race.RaceTests) ... ok
test_same_sequence_including_without_seed (test_race.RaceTests) ... ok
test_simultaneous_finish_is_draw (test_race.RaceTests) ... ok
test_topout_and_simultaneous_topout (test_race.RaceTests) ... ok
test_80_by_30_has_full_boards_status_cost_and_controls (test_race_ui.RaceUITests) ... ok
test_cli_missing_key_does_not_open_curses (test_race_ui.RaceUITests) ... ok
test_cli_routes_versus_and_prints_final_cost (test_race_ui.RaceUITests) ... ok
test_error_winner_and_small_screen_messages (test_race_ui.RaceUITests) ... ok
test_global_controls_and_no_input_during_pause_error_or_resize (test_race_ui.RaceUITests) ... ok
test_loop_handles_input_while_provider_is_waiting_and_quits (test_race_ui.RaceUITests) ... ok
test_resize_does_not_apply_catchup_time (test_race_ui.RaceUITests) ... ok
test_bundled_clicks_are_short_pcm_with_headroom_and_soft_edges (test_samples.SampleTests) ... ok
test_selected_samples_have_provenance_and_matching_hashes (test_samples.SampleTests) ... ok
test_each_wall_collision (test_snake_engine.SnakeRulesTests) ... ok
test_food_uniform_selection_uses_all_free_cells (test_snake_engine.SnakeRulesTests) ... ok
test_full_board_has_no_food_and_freezes (test_snake_engine.SnakeRulesTests) ... ok
test_initial_movement_growth_and_food_exclusion (test_snake_engine.SnakeRulesTests) ... ok
test_pause_remaining_timer_and_delayed_frame_cap (test_snake_engine.SnakeRulesTests) ... ok
test_queue_order_reverse_duplicates_and_overflow (test_snake_engine.SnakeRulesTests) ... ok
test_restart_resets_state_and_repeats_seed_preserving_best (test_snake_engine.SnakeRulesTests) ... ok
test_speed_boundaries_and_new_interval_after_food (test_snake_engine.SnakeRulesTests) ... ok
test_tail_departure_is_legal_but_body_collision_ends_game (test_snake_engine.SnakeRulesTests) ... ok
test_all_bindings (test_snake_ui.SnakeUITests) ... ok
test_ascii_layout_bounds_marks_overlays_and_centering (test_snake_ui.SnakeUITests) ... ok
test_cli_help_flags_nonterminal_and_error_after_wrapper (test_snake_ui.SnakeUITests) ... ok
test_clipping_and_resize_errors (test_snake_ui.SnakeUITests) ... ok
test_loop_successful_turn_food_collision_and_straight_cues (test_snake_ui.SnakeUITests) ... ok
test_palette_matches_tetris_in_256_and_eight_colors (test_snake_ui.SnakeUITests) ... ok
test_pause_restart_overlay_and_rejected_input_audio (test_snake_ui.SnakeUITests) ... ok
test_real_audio_coalescing_mute_disabled_failure_and_cleanup (test_snake_ui.SnakeUITests) ... ok
test_resize_freezes_time_clears_turns_polls_audio_and_keeps_pause (test_snake_ui.SnakeUITests) ... ok
test_run_closes_audio_on_quit_interrupt_and_exception (test_snake_ui.SnakeUITests) ... ok
test_default_and_relative_destinations (test_terminal_checker_compatibility.CheckerCompatibilityTests) ... ok
test_failure_writes_selected_transcript_and_exits_nonzero (test_terminal_checker_compatibility.CheckerCompatibilityTests) ... ok
test_help_and_argument_errors (test_terminal_checker_compatibility.CheckerCompatibilityTests) ... ok
test_both_turns_in_wrong_order_are_rejected (test_terminal_checker_compatibility.OrderedMovementTests) ... ok
test_directions_without_movement_are_rejected (test_terminal_checker_compatibility.OrderedMovementTests) ... ok
test_consumed_first_turn_is_accepted (test_terminal_checkers.SnakeQueueCheckerTests) ... ok
test_early_input_is_accepted (test_terminal_checkers.SnakeQueueCheckerTests) ... ok
test_missing_or_wrong_order_turns_are_rejected (test_terminal_checkers.SnakeQueueCheckerTests) ... ok
test_explicit_external_destination_preserves_existing_evidence (test_terminal_checkers.TranscriptDestinationTests) ... ok
test_audio_failure_is_reported_after_curses_returns (test_ui.CLITests) ... ok
test_help_without_tty (test_ui.CLITests) ... ok
test_invalid_seed (test_ui.CLITests) ... ok
test_no_sound_and_color_flags_reach_the_game (test_ui.CLITests) ... ok
test_non_tty_fails_cleanly (test_ui.CLITests) ... ok
test_terminal_error_and_ctrl_c_are_clean (test_ui.CLITests) ... ok
test_keyboard_mapping (test_ui.InputTests) ... ok
test_pause_and_restart_controls (test_ui.InputTests) ... ok
test_renderer_clips_and_tolerates_resize_errors (test_ui.InputTests) ... ok
test_renderer_does_not_swallow_programming_errors (test_ui.InputTests) ... ok
test_resize_freezes_simulation_and_discards_catchup (test_ui.InputTests) ... ok
test_active_ink_and_pencil_ghost_are_distinct (test_ui.ThemeTests) ... ok
test_no_color_does_not_initialize_colors (test_ui.ThemeTests) ... ok
test_paper_palette_and_basic_terminal_fallback (test_ui.ThemeTests) ... ok
test_socratink_copy_on_board_and_overlays (test_ui.ThemeTests) ... ok

----------------------------------------------------------------------
Ran 241 tests in 25.430s

OK (skipped=2)
Legal full-clear replay: seed=20261004, steps=31475, boards=[(0, 16548, 360, 3), (1, 19078, 480, 3), (2, 31474, 760, 3)]
Legal replay: seed=7, steps=1528/36000, score=340, lives=3

$ ["python3", "-B", "-m", "tink_breakout", "--help"]
usage: python3 -m tink_breakout [-h] [--no-color] [--no-sound]

Offline terminal Breakout: clear three boards with three lives.

options:
  -h, --help  show this help message and exit
  --no-color  use monochrome rendering
  --no-sound  disable keyboard sounds for this run

Requires an 80 x 30 terminal. Arrows or A/D move; Space launches; P pauses; R
restarts; M mutes keyboard sounds; Q or Ctrl-C quits.

# checklist item crossing-rules-regressions
$ ["python3", "-B", "scripts/check_crossing_tests.py"]
Crossing engine: 14 tests
Crossing ui: 8 tests
.............................................................................................................................................................ss..................................................................................
----------------------------------------------------------------------
Ran 241 tests in 25.012s

OK (skipped=2)
Legal full-clear replay: seed=20261004, steps=31475, boards=[(0, 16548, 360, 3), (1, 19078, 480, 3), (2, 31474, 760, 3)]
Legal replay: seed=7, steps=1528/36000, score=340, lives=3
Total: 241; skips: 2
SKIP test_native_audio.NativeAudioIntegrationTests.test_each_sample_renders_on_repeated_spaced_plays: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples
SKIP test_native_audio.NativeAudioIntegrationTests.test_replay_after_mute_and_resume: set NEON_TETRIS_AUDIO_TESTS=1 on macOS to play and meter real samples

# checklist item crossing-replays
$ ["python3", "-B", "scripts/crossing_replay.py"]
Legal win: level=3 score=2850 lives=3 steps=1664 (13.9s simulated)
Legal loss: score=70 deaths=3 steps=105

# checklist item crossing-terminal
$ ["python3", "-B", "scripts/check_crossing_terminal.py"]
PASS: Crossing real PTY arrows/WASD, hop, pause, restart, resize, mute, Q and SIGINT; modes restored; child groups gone.
Transcript: runs/crossing/04-test/output/terminal-transcript.txt

# checklist item crossing-cli
$ ["python3", "-B", "-m", "tink_crossing", "--help"]
usage: python3 -m tink_crossing [-h] [--no-color] [--no-sound]

Offline lane crossing. Fill five bays on each of three levels.

options:
  -h, --help  show this help message and exit
  --no-color  use monochrome rendering
  --no-sound  disable audio for the entire session

Requires 80 x 30. Arrows or WASD hop; P pauses; R restarts; M mutes; Q or
Ctrl-C quits.
