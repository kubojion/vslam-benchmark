"""User decision D1 (18 Nov 2026): explicit Sielinko reviews carry over to the reference-v4 re-evaluation only when
nothing but the reference changed, and only for attempts the pinned record lists."""
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import acceptance_ledger as AL  # noqa: E402
import reference_carryover as RC  # noqa: E402

REL = 'vo/zed2i/field1_110426_full_10fps_q90/okvis2/run1'
V2 = {RC.SELECTOR: 'sel2', 'ref2/reference.json': 'r2', 'ref2/primary.tum': 't2', 'ref2/primary-support.json': 's2'}
V4 = {RC.SELECTOR: 'sel4', 'ref4/reference.json': 'r4', 'ref4/primary.tum': 't4', 'ref4/primary-support.json': 's4'}
RUN_INPUTS = {f'results/{REL}/trajectory.txt': 'traj', f'results/{REL}/run_meta.json': 'meta', 'times.txt': 'times'}


def evaluation(reference, ate=1.0, **changes):
    value = dict(dataset='zed2i', seq='field1_110426_full_10fps_q90', algo='okvis2', run='1', run_directory='run1',
                 run_type='vo', gnss_variant='default', run_status='ok', failure_reason=None,
                 ate_se3=dict(rmse=ate), coverage=dict(coverage_gap_pct=99.0, reference_pairs_pct_of_input=90.0 + ate),
                 pose_frames=dict(blockers=[], estimate_transform=[[1]], reference_version=str(sorted(reference)[1]),
                                  reference_valid_intervals=[[0, ate]], reference_limitations=[]),
                 evaluation_provenance=dict(inputs=[dict(path=p, sha256=s) for p, s in {**RUN_INPUTS, **reference}.items()],
                                            timestamp_utc=str(ate)))
    for key, val in changes.items():
        value[key] = val
    return value


RECORD = dict(schema=1, decision=dict(accept=True), reference=dict(v2=V2, v4=V4))


def test_only_reference_derived_fields_may_differ():
    v2, v4 = evaluation(V2, 1.0), evaluation(V4, 1.1)
    assert RC.only_reference_changed(v2, v4, RECORD) == []
    moved = copy.deepcopy(v4); moved['evaluation_provenance']['inputs'][0]['sha256'] = 'other trajectory'
    assert any('trajectory.txt' in r for r in RC.only_reference_changed(v2, moved, RECORD))
    assert 'run_status differs' in RC.only_reference_changed(v2, evaluation(V4, 1.1, run_status='scale_collapse'), RECORD)
    blocked = copy.deepcopy(v4); blocked['pose_frames']['blockers'] = ['estimate_frame_unverified']
    assert 'pose_frames differ beyond the reference-derived keys' in RC.only_reference_changed(v2, blocked, RECORD)
    assert 'current evaluation does not use exactly the v4 reference inputs' in RC.only_reference_changed(v2, evaluation(V2, 1.1), RECORD)
    other_run = evaluation(V4, 1.1, run='2')
    assert 'run identity differs: run' in RC.only_reference_changed(v2, other_run, RECORD)


def ledger_repo(tmp_path, *, list_it=True, preserved=True):
    repo = tmp_path
    run = repo/'results'/REL; run.mkdir(parents=True)
    v2, v4 = evaluation(V2, 1.0), evaluation(V4, 1.1)
    raw2 = (json.dumps(v2)+'\n').encode(); sha2 = hashlib.sha256(raw2).hexdigest()
    (run/'run_eval.json').write_text(json.dumps(v4)+'\n')
    if preserved:
        (run/'.evaluation_history').mkdir(); (run/'.evaluation_history'/f'{sha2}.json').write_bytes(raw2)
    (repo/'configs/references').mkdir(parents=True); (repo/RC.SELECTOR).write_text('v4 selector\n')
    record = dict(RECORD, reference=dict(v2=V2, v4=dict(V4, **{RC.SELECTOR: RC.sha(repo/RC.SELECTOR)})), reviews={}, selection_pins={})
    v4['evaluation_provenance']['inputs'] = [dict(path=p, sha256=s) for p, s in {**RUN_INPUTS, **record['reference']['v4']}.items()]
    (run/'run_eval.json').write_text(json.dumps(v4)+'\n')
    if list_it:
        record['reviews'][REL] = dict(ledger_status='accepted_with_limitation', ledger_evaluation_sha256=RC.numerical_digest(v2),
                                      v2_run_eval_sha256=sha2)
        record['selection_pins'][f'results/{REL}/run_eval.json'] = dict(record=RC.ZED_SELECTION, v2_run_eval_sha256=sha2)
    (repo/RC.RECORD).parent.mkdir(parents=True, exist_ok=True); (repo/RC.RECORD).write_text(json.dumps(record))
    ledger = dict(supporting_evidence=[], attempts={REL: dict(
        exists=True, evaluation_sha256=RC.numerical_digest(v2), status='accepted_with_limitation', blockers=[],
        claim_limits=['limit'], disclosures=[], claim='claim',
        evidence=[dict(path=RC.SELECTOR, sha256='v2-selector-sha'), dict(path=f'results/{REL}/run_eval.json', sha256=sha2)])})
    (repo/AL.LEDGER).parent.mkdir(parents=True, exist_ok=True); (repo/AL.LEDGER).write_text(json.dumps(ledger))
    return repo, v4, sha2


def test_listed_review_carries_over_and_keeps_its_acceptance(tmp_path, monkeypatch):
    monkeypatch.setattr(RC, 'V2_SELECTOR_SHA256', 'v2-selector-sha')
    repo, v4, _ = ledger_repo(tmp_path)
    decision = AL.reviewed_decision(repo, REL, {}, v4, [], [dict(verified=True)], True)
    assert decision['status'] == 'accepted_with_limitation' and decision['accuracy_eligible'] is True
    assert decision['reference_carryover']['record'] == RC.RECORD


def test_unlisted_or_unpreserved_review_goes_stale(tmp_path, monkeypatch):
    monkeypatch.setattr(RC, 'V2_SELECTOR_SHA256', 'v2-selector-sha')
    repo, v4, _ = ledger_repo(tmp_path/'a', list_it=False)
    assert AL.reviewed_decision(repo, REL, {}, v4, [], [dict(verified=True)], True)['status'] == 'blocked'
    repo, v4, _ = ledger_repo(tmp_path/'b', preserved=False)
    stale = AL.reviewed_decision(repo, REL, {}, v4, [], [dict(verified=True)], True)
    assert stale['status'] == 'blocked' and 'numerical_evidence_changed_since_claim_review' in stale['blockers']


def test_a_non_reference_change_is_never_carried(tmp_path, monkeypatch):
    monkeypatch.setattr(RC, 'V2_SELECTOR_SHA256', 'v2-selector-sha')
    repo, v4, _ = ledger_repo(tmp_path)
    v4['run_status'] = 'scale_collapse'
    assert AL.reviewed_decision(repo, REL, {}, v4, [], [dict(verified=True)], True)['status'] == 'blocked'


def test_selection_pin_accepts_only_the_listed_carried_file(tmp_path):
    repo, _, sha2 = ledger_repo(tmp_path)
    assert RC.carried_selection_pin(repo, dict(path=f'results/{REL}/run_eval.json', sha256=sha2))
    assert not RC.carried_selection_pin(repo, dict(path=f'results/{REL}/run_eval.json', sha256='0'*64))
    (repo/'results'/REL/'.evaluation_history'/f'{sha2}.json').unlink()
    assert not RC.carried_selection_pin(repo, dict(path=f'results/{REL}/run_eval.json', sha256=sha2))


def test_the_record_must_be_an_accepted_decision(tmp_path):
    repo, _, _ = ledger_repo(tmp_path)
    value = json.loads((repo/RC.RECORD).read_text()); value['decision']['accept'] = False
    (repo/RC.RECORD).write_text(json.dumps(value))
    try:
        RC.load_record(repo)
    except ValueError:
        return
    raise AssertionError('an unaccepted record must refuse')
