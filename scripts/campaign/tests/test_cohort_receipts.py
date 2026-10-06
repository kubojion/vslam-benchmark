import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_repair_inventory import cohort_artifacts, cohort_identity


def receipt(run, role, value):
    path = run/'provenance'/role
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))
    return dict(role=role, snapshot=str(path.relative_to(run)),
                snapshot_sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def test_receipt_paths_and_observed_counts_do_not_split_new_cohorts(tmp_path):
    payloads = []
    for n in (1, 2):
        run = tmp_path/'results/vio/test/seq/basalt'/f'run{n}'
        artifacts = [receipt(run, 'input_clock_policy', {
            'path': str(run/'native-inputs/imu.csv'), 'offset': 4098308}),
            receipt(run, 'native_input_receipt.json', {'received': 100-n})]
        p = dict(parameters={'cohort_artifact_semantics': 2}, artifacts=artifacts)
        payloads.append((p, run))
    assert cohort_artifacts(*payloads[0]) == cohort_artifacts(*payloads[1])
    first, second = [dict(p, parameters={}) for p, run in payloads]
    assert cohort_artifacts(first) != cohort_artifacts(second)
    p, run = payloads[1]
    p['artifacts'][0] = receipt(run, 'input_clock_policy', {'path': str(run/'native-inputs/imu.csv'), 'offset': 0})
    assert cohort_artifacts(*payloads[0]) != cohort_artifacts(p, run)
    (run/'provenance/native_input_receipt.json').write_text('{}')
    with pytest.raises(ValueError, match='changed cohort receipt'):
        cohort_artifacts(p, run)


def svo_config(run, trace_dir=None, max_fts=180):
    path = run/'provenance/effective_config--svo_effective_config.yaml'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'max_fts: {max_fts}\ntrace_dir: {trace_dir or "/ws/" + str(run.relative_to(run.parents[5])) + "/native"}\n')
    return dict(role='effective_config', snapshot=str(path.relative_to(run)),
                snapshot_sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def test_svo_pro_attempt_trace_directory_does_not_split_cohorts(tmp_path):
    runs = [tmp_path/'results/vo/euroc_mav/MH_01_easy/svo_pro'/f'run1000{n}' for n in (1, 2)]
    provenance = [dict(parameters={}, artifacts=[svo_config(run)]) for run in runs]
    assert cohort_artifacts(provenance[0], runs[0], 'svo_pro') == cohort_artifacts(provenance[1], runs[1], 'svo_pro')
    # Other estimators keep byte-based historical signatures.
    assert cohort_artifacts(provenance[0], runs[0], 'orbslam3') != cohort_artifacts(provenance[1], runs[1], 'orbslam3')
    changed = dict(parameters={}, artifacts=[svo_config(runs[1], max_fts=120)])
    assert cohort_artifacts(provenance[0], runs[0], 'svo_pro') != cohort_artifacts(changed, runs[1], 'svo_pro')


def test_mast3r_fusion_repetition_seed_is_not_a_setting():
    def meta(seed):
        return dict(provenance=dict(parameters=dict(seed=seed, stride=1), artifacts=[]), machine_id='m')
    assert cohort_identity(meta(11001), 'mast3r_fusion')[0] == cohort_identity(meta(11002), 'mast3r_fusion')[0]
    assert cohort_identity(meta(11001), 'orbslam3')[0] != cohort_identity(meta(11002), 'orbslam3')[0]


def test_orb_canonicalization_marker_absent_after_a_crash_does_not_split_cohorts():
    def meta(**extra):
        return dict(provenance=dict(parameters=dict(dict(stride=1), **extra), artifacts=[]), machine_id='m')
    exported = meta(trajectory_canonicalization='drop_exact_duplicate_timestamp_pose_rows')
    assert cohort_identity(exported, 'orbslam3')[0] == cohort_identity(meta(), 'orbslam3')[0]
    assert cohort_identity(meta(stride=2), 'orbslam3')[0] != cohort_identity(meta(), 'orbslam3')[0]
