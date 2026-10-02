import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _run_observations import parse_log
from _segment_trajectory import merge_segments, window_indices


def test_missing_initialization_message_is_unknown(tmp_path):
    p = tmp_path/'run.log'; p.write_text('1.200 finishing\n')
    assert parse_log(str(p), 'orbslam3')['init_success'] is None
    p.write_text('1.200 New Map created with 50 points\n')
    assert parse_log(str(p), 'orbslam3')['init_success'] is True


def test_readiness_is_not_initialization_and_missing_log_is_not_zero(tmp_path):
    p = tmp_path/'run.log'
    absent = parse_log(str(p), 'orbslam3')
    assert absent['tracking_losses'] is None
    assert absent['output_valid'] is None
    p.write_text('1.200 dataset done\n')
    assert parse_log(str(p), 'airslam')['init_success'] is None


def test_orb_resets_and_recoverable_loss_are_separate_messages(tmp_path):
    p = tmp_path/'run.log'
    p.write_text('''0.100 Creation of new map with id: 0
1.000 Not enough motion for initializing. Reseting...
1.001 LM: Reseting current map in Local Mapping...
1.002 LM: Reset free the mutex
2.000 Fail to track local map!
2.100 Track Lost...
3.000 Active map Reseting
3.001 Reseting Local Mapper...
3.002 LM: Reseting current map in Local Mapping...
4.000 System Reseting
4.001 LM: Reseting Atlas in Local Mapping...
5.000 Creation of new map with id: 1
5.001 Creation of new map with last KF id: 17
6.000 Map id: 0
6.001 Map id: 1
7.000 Summary: LOST = 0; Active map Reseting = 1
8.000 No LOST state observed
''')
    result = parse_log(str(p), 'orbslam3')
    assert result['tracking_losses'] == 2
    assert result['first_failure_s'] == 2.0
    assert result['local_tracking_failure_messages'] == 1
    assert result['map_resets'] == 2
    assert result['map_creation_messages'] == 2
    assert result['local_mapping_reset_messages'] == 3
    assert result['imu_initialization_reset_requests'] == 1
    assert 'not unique lost episodes' in result['event_semantics']
    assert parse_log(str(tmp_path/'missing'), 'orbslam3')['local_mapping_reset_messages'] is None
    assert parse_log(str(p), 'okvis2')['local_mapping_reset_messages'] is None


def test_absorbed_segment_coalesces_and_retains_joining_path():
    times = np.arange(9, dtype=float)
    distance = np.array([0, 1, 2, 2.1, 2.2, 2.3, 3.3, 4.3, 5.3])
    turn = np.array([False]*3 + [True]*3 + [False]*3)
    result = merge_segments(times, turn, distance, 1.0)
    assert len(result) == 1
    assert result[0]['n'] == 9
    assert result[0]['path'] == 5.3


def test_search_window_matches_original_strict_distance_semantics():
    distance = np.array([0, 0, .1, .5, 1, 1, 1.4, 2, 3])
    for i in range(len(distance)):
        lo = hi = i
        while lo > 0 and distance[i]-distance[lo-1] < .5:
            lo -= 1
        while hi < len(distance)-1 and distance[hi+1]-distance[i] < .5:
            hi += 1
        assert window_indices(distance, i, .5) == (lo, hi)
