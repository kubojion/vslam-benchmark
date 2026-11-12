"""The user's non-acting differences (12 Nov 2026) apply to exactly the listed cell, runs, fields and values."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_repair_inventory as inventory  # noqa: E402

KEY = 'vio/rosariov2/sequence1/openvins'
CITRUS = 'vio/citrusfarm/seq04/openvins'
RUNS = [10004, 10005, 10006]


def attempt(tmp, key, run_id, audit, config='cfg', parameters=None):
    d = tmp/'results'/key/f'run{run_id}'; (d/'provenance').mkdir(parents=True)
    snapshot = d/'provenance/implementation.json'
    snapshot.write_text(json.dumps(dict(schema=1, trees=[dict(role='algorithm', path='src/open_vins', commit='abc', entries=['x'])])))
    (d/'run_meta.json').write_text(json.dumps(dict(provenance=dict(implementation_capture=dict(
        snapshot='provenance/implementation.json', snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest())))))
    artifacts = [dict(role='estimator_config', sha256=config)] + ([dict(role='delivery_audit', sha256=audit)] if audit else [])
    payload = dict(workspace=dict(commit='ad1470c'), artifacts=artifacts, parameters=parameters or dict(use_imu='true'), machine_id='m')
    return dict(path=f'results/{key}/run{run_id}', cohort_fingerprint=str(run_id), cohort_evidence=payload, process=dict(exit_code=0))


def records(tmp, key=KEY, per_run=None, runs=RUNS):
    (tmp/'configs/campaigns').mkdir(parents=True, exist_ok=True)
    (tmp/inventory.RULEC_POOLING).write_text(json.dumps(dict(schema=1, cells={key: dict(runs=runs)})))
    per_run = per_run or {str(r): f'audit-{r}' for r in runs}
    (tmp/inventory.NONACTING).write_text(json.dumps(dict(schema=1, cells={key: dict(runs=runs, differences=[
        dict(kind='artifact', role='delivery_audit', per_run=per_run, reason='post-run receipt')])})))


def attempts(tmp, key=KEY, **change):
    return [attempt(tmp, key, r, f'audit-{r}', **(change if r == RUNS[-1] else {})) for r in RUNS]


def test_listed_receipt_with_recorded_values_pools(tmp_path):
    records(tmp_path)
    result = inventory.pooled_cohort(tmp_path, KEY, attempts(tmp_path), (inventory.RULEC_POOLING,))
    assert result['status'] == 'pooled' and result['nonacting_user_decision']['fields'] == ['delivery_audit']


def test_without_the_record_the_same_cell_is_refused(tmp_path):
    records(tmp_path); (tmp_path/inventory.NONACTING).unlink()
    result = inventory.pooled_cohort(tmp_path, KEY, attempts(tmp_path), (inventory.RULEC_POOLING,))
    assert result['status'] == 'refused' and 'nonacting_user_decision' not in result


def test_a_value_other_than_the_recorded_one_is_refused(tmp_path):
    records(tmp_path, per_run={'10004': 'audit-10004', '10005': 'audit-10005', '10006': 'other'})
    assert inventory.pooled_cohort(tmp_path, KEY, attempts(tmp_path), (inventory.RULEC_POOLING,))['status'] == 'refused'


def test_any_other_difference_still_refuses(tmp_path):
    records(tmp_path)
    assert inventory.pooled_cohort(tmp_path, KEY, attempts(tmp_path, config='changed'), (inventory.RULEC_POOLING,))['status'] == 'refused'
    other = attempts(tmp_path/'p', parameters=dict(use_imu='true', buffer_size=1))
    records(tmp_path/'p')
    assert inventory.pooled_cohort(tmp_path/'p', KEY, other, (inventory.RULEC_POOLING,))['status'] == 'refused'


def test_record_for_other_runs_is_refused(tmp_path):
    records(tmp_path)
    value = json.loads((tmp_path/inventory.NONACTING).read_text())
    value['cells'][KEY]['runs'] = [1, 2, 3]
    value['cells'][KEY]['differences'][0]['per_run'] = {'1': 'a', '2': 'b', '3': 'c'}
    (tmp_path/inventory.NONACTING).write_text(json.dumps(value))
    assert inventory.pooled_cohort(tmp_path, KEY, attempts(tmp_path), (inventory.RULEC_POOLING,))['status'] == 'refused'


def test_an_unlisted_cell_is_untouched(tmp_path):
    """Job A's corrected CitrusFarm OpenVINS cells differ only in delivery_audit too; the record must not reach them."""
    records(tmp_path)  # lists only the Rosario cell
    citrus = [attempt(tmp_path, CITRUS, r, f'audit-{r}') for r in (50001, 50002, 50003)]
    assert inventory.pooled_cohort(tmp_path, CITRUS, citrus, (inventory.RULEC_POOLING,)) is None
    assert inventory.pooled_cohort(tmp_path, CITRUS, citrus) is None


def test_scope_refuses_corrected_citrus_and_cells_outside_the_rule_c_pooling(tmp_path):
    records(tmp_path, key=CITRUS, runs=[50001, 50002, 50003])
    with pytest.raises(ValueError, match='corrected CitrusFarm'):
        inventory.check_nonacting_scope(tmp_path, {CITRUS: [50001, 50002, 50003]}, {CITRUS})
    records(tmp_path)
    with pytest.raises(ValueError, match='outside the Rule C pooling'):
        inventory.check_nonacting_scope(tmp_path, {KEY: [1, 2, 3]}, set())
    inventory.check_nonacting_scope(tmp_path, {KEY: RUNS}, set())


def test_a_difference_needs_a_reason_and_every_run(tmp_path):
    records(tmp_path)
    value = json.loads((tmp_path/inventory.NONACTING).read_text())
    del value['cells'][KEY]['differences'][0]['per_run']['10006']
    (tmp_path/inventory.NONACTING).write_text(json.dumps(value))
    with pytest.raises(ValueError, match='reason and a value for every listed run'):
        inventory.nonacting_record(tmp_path)


def test_committed_record_names_exactly_the_six_decided_cells():
    repo = Path(__file__).resolve().parents[3]
    path = repo/inventory.NONACTING
    if not path.is_file():
        pytest.skip('record not present')
    cells = json.loads(path.read_text())['cells']
    z = 'zed2i/field1_110426_full_10fps_q90'
    assert set(cells) == {f'vo/{z}/cuvslam', f'vo-lc/{z}/cuvslam', 'vio/rosariov2/sequence1/openvins',
                          'vio/rosariov2/sequence5/openvins', f'vio/{z}/openvins', 'vo/citrusfarm/seq04/dpvo'}
    assert not any(key.split('/')[1] == 'citrusfarm' and key.split('/')[0] in ('vio', 'vio-lc') for key in cells)
    fields = {key: sorted(d.get('role') or d.get('name') for d in c['differences']) for key, c in cells.items()}
    assert fields['vo/citrusfarm/seq04/dpvo'] == ['buffer_size']
    assert fields[f'vio/{z}/openvins'] == ['delivery_audit', 'native_outcome']
    assert fields[f'vo/{z}/cuvslam'] == fields[f'vo-lc/{z}/cuvslam'] == ['camera_calibration']


def test_configuration_consistency_follows_only_a_pooled_non_acting_decision():
    attempts = [dict(config_fingerprint=f'c{i}') for i in range(3)]
    assert inventory.config_consistent([dict(config_fingerprint='c')] * 3, None)
    assert not inventory.config_consistent(attempts, None)
    assert not inventory.config_consistent(attempts, dict(status='pooled', accepted_decisions=['harness_python']))
    assert not inventory.config_consistent(attempts, dict(status='refused', nonacting_user_decision=dict(fields=['x'])))
    assert inventory.config_consistent(attempts, dict(status='pooled', nonacting_user_decision=dict(fields=['x'])))
