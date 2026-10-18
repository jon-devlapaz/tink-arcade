#!/usr/bin/env python3
"""Run repository regressions or required Stacker rules/native sound acceptance tests."""
import argparse
from collections import Counter
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REQUIRED = {
    'test_stacker_engine.StackerRuleTests': '''
        test_first_row_locks_without_support
        test_moving_row_reflects_at_both_edges
        test_lock_retains_only_overlap_and_discards_overhang
        test_next_row_width_equals_surviving_blocks
        test_zero_overlap_loses_without_advancing
        test_successful_lock_automatically_starts_next_row
        test_top_row_wins_without_checkpoint_or_payout_choice
        test_height_only_speed_curve_and_identical_elapsed_inputs_repeat
        test_restart_restores_initial_state
        test_legal_timed_input_replay_reaches_top'''.split(),
    'test_stacker_ui.StackerUITests': '''
        test_lock_uses_displayed_position_once_per_input_batch
        test_pause_and_small_terminal_freeze_without_catchup
        test_resize_recovery_preserves_prior_pause
        test_end_states_ignore_placement_and_restart_is_available
        test_bounded_input_does_not_starve_update_or_render'''.split(),
    'test_stacker_audio.StackerAudioTests': '''
        test_lock_loss_and_win_dispatch_shared_cues
        test_automatic_travel_and_frozen_gameplay_are_silent
        test_audio_tick_runs_each_frame_including_pause_resize_and_end_states
        test_mute_cancels_pending_and_active_cues_and_unmute_confirms
        test_no_sound_never_creates_backend_and_m_cannot_enable_it
        test_unavailable_audio_keeps_game_playable_and_reports_warning
        test_audio_closes_on_quit_sigint_and_exception
        test_restart_preserves_mute_without_reloading_samples'''.split(),
    'test_stacker_native_audio.NativeStackerAudioTests': '''
        test_stacker_action_cues_advance_and_meter_on_spaced_repeats
        test_stacker_action_cues_advance_and_meter_on_rapid_repeats
        test_stacker_playback_resumes_after_mute_and_closes_voices'''.split(),
}


def required_ids(mode, native=False):
    groups = {'rules': ('engine', 'ui'), 'sounds': ('audio', 'native_audio'),
              'all': ('engine', 'ui', 'audio', 'native_audio')}[mode]
    return {f'{group}.{name}' for group, names in REQUIRED.items() for name in names
            if any(group.startswith(f'test_stacker_{suffix}.') for suffix in groups)
            and (native or not group.startswith('test_stacker_native_audio.'))}


def cases(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from cases(case)
        else:
            yield case


class RequiredResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_ids = set()

    def addSuccess(self, test):
        self.passed_ids.add(test.id())
        super().addSuccess(test)


def check_suite(suite, required):
    counts = Counter(test.id() for test in cases(suite))
    if not counts or required - counts.keys() or any(n != 1 for n in counts.values()):
        print(f'Missing or duplicate tests: {sorted(required - counts.keys())}', file=sys.stderr)
        return 1
    result = unittest.TextTestRunner(verbosity=2, resultclass=RequiredResult).run(suite)
    for case, reason in result.skipped:
        print(f'SKIP {case.id()}: {reason}')
    missing = required - result.passed_ids
    if missing:
        print(f'Required tests did not pass: {sorted(missing)}', file=sys.stderr)
    print(f'Total: {result.testsRun}; skips: {len(result.skipped)}; required passed: {len(required - missing)}/{len(required)}')
    return 0 if result.wasSuccessful() and not missing else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--rules', action='store_true')
    group.add_argument('--sounds', action='store_true')
    parser.add_argument('--require-native', action='store_true')
    args = parser.parse_args(argv)
    if args.require_native != args.sounds:
        parser.error('--sounds and --require-native must be supplied together')
    if args.require_native and (sys.platform != 'darwin' or os.environ.get('NEON_TETRIS_AUDIO_TESTS') != '1'):
        print('Native Stacker sound checks require macOS and NEON_TETRIS_AUDIO_TESTS=1; refusing a skip-based pass.', file=sys.stderr)
        return 1
    mode = 'rules' if args.rules else 'sounds' if args.sounds else 'all'
    required = required_ids(mode, args.require_native)
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / 'tests'))
    if loader.errors:
        print('\n'.join(loader.errors), file=sys.stderr)
        return 1
    if mode != 'all':
        prefixes = ('test_stacker_engine.', 'test_stacker_ui.') if mode == 'rules' else ('test_stacker_audio.', 'test_stacker_native_audio.')
        suite = unittest.TestSuite(test for test in cases(suite) if test.id().startswith(prefixes))
    return check_suite(suite, required)


if __name__ == '__main__':
    sys.exit(main())
