"""A listed cell pools across workspace commits only when its estimate receipts are identical."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_repair_inventory import POOLING, pooled_cohort  # noqa: E402

KEY = 'vio/zed2i/field1_110426_full_10fps_q90/okvis2'


def run(tmp, run_id, commit, binary='aa', parameters=None, algorithm_tree='src-1'):
    d = tmp / 'results' / KEY / f'run{run_id}'
    (d / 'provenance').mkdir(parents=True)
    snapshot = d / 'provenance/implementation.json'
    snapshot.write_text(json.dumps(dict(schema=1, trees=[
        dict(role='workspace', path='.', commit=commit, entries=[commit]),
        dict(role='algorithm', path='src/okvis2', commit='abc', entries=[algorithm_tree])])))
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    (d / 'run_meta.json').write_text(json.dumps(dict(provenance=dict(
        implementation_capture=dict(snapshot='provenance/implementation.json', snapshot_sha256=digest)))))
    payload = dict(workspace=dict(commit=commit), implementation_content_sha256=commit,
                   binaries=[dict(role='estimator', path='okvis_app', sha256=binary)],
                   parameters=parameters if parameters is not None else dict(use_imu='true'), machine_id='m')
    return dict(path=f'results/{KEY}/run{run_id}', cohort_fingerprint=commit + binary, cohort_evidence=payload)


def record(tmp, **spec):
    path = tmp / POOLING
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(schema=1, cells={KEY: dict(runs=[10001, 10003, 10004], **spec)})))


def test_pools_when_only_the_workspace_differs(tmp_path):
    record(tmp_path)
    attempts = [run(tmp_path, 10001, 'old'), run(tmp_path, 10003, 'new'), run(tmp_path, 10004, 'new')]
    result = pooled_cohort(tmp_path, KEY, attempts)
    assert result['status'] == 'pooled' and result['workspace_commits'] == ['new', 'old']


def test_refuses_on_any_estimate_receipt_difference(tmp_path):
    record(tmp_path)
    attempts = [run(tmp_path, 10001, 'old', binary='bb'), run(tmp_path, 10003, 'new'), run(tmp_path, 10004, 'new')]
    assert pooled_cohort(tmp_path, KEY, attempts)['status'] == 'refused'


def test_refuses_on_algorithm_source_difference(tmp_path):
    record(tmp_path)
    attempts = [run(tmp_path, 10001, 'old', algorithm_tree='src-0'), run(tmp_path, 10003, 'new'),
                run(tmp_path, 10004, 'new')]
    assert pooled_cohort(tmp_path, KEY, attempts)['status'] == 'refused'


def test_listed_diagnostic_parameter_only_at_its_default(tmp_path):
    record(tmp_path, ignored_parameters=dict(trace=0))
    old = run(tmp_path, 10001, 'old', parameters=dict(use_imu='true'))
    on = run(tmp_path, 10003, 'new', parameters=dict(use_imu='true', trace=1))
    off = run(tmp_path, 10004, 'new', parameters=dict(use_imu='true', trace=0))
    assert pooled_cohort(tmp_path, KEY, [old, on, off])['status'] == 'refused'
    on['cohort_evidence']['parameters']['trace'] = 0
    assert pooled_cohort(tmp_path, KEY, [old, on, off])['status'] == 'pooled'


def test_unlisted_cells_and_other_runs_are_not_pooled(tmp_path):
    record(tmp_path)
    attempts = [run(tmp_path, 10001, 'old'), run(tmp_path, 10003, 'new'), run(tmp_path, 10004, 'new')]
    assert pooled_cohort(tmp_path, KEY.replace('okvis2', 'basalt'), attempts) is None
    assert pooled_cohort(tmp_path, KEY, attempts[:2])['status'] == 'refused'
