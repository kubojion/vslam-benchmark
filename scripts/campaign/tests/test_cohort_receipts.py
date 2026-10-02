import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_repair_inventory import cohort_artifacts


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
