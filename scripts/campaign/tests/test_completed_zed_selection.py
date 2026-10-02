"""Retain completed planned slots without success-conditioned retries or readiness promotion."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_repair_inventory import completed_zed_selections, ZED_SELECTION
from build_future_manifest import action_category
from run_future_manifest import validate


def write(root, name, value):
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value))
    return dict(path=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def fixture(root, status='evaluated', exit_code=0):
    value=dict(schema=1,cells={},completed=[])
    actions=[]
    for algo in ('orbslam3','okvis2','okvis2x'):
        key=f'vio/zed2i/field1_110426_full_10fps_q90/{algo}'
        action=dict(cell=key,repetition=1,planned_output=f'results/{key}/run10001',
                    cohort='reviewed-cohort-'+algo,id=key+'/default/r1')
        actions.append(action)
        state=write(root,f'states/{algo}.json',dict(status=status,estimator_exit_code=exit_code,
            identity=dict(cohort=action['cohort'],repetition=1,physical_run_id=10001)))
        value['cells'][key]=[10001,2,3]
        value['completed'].append(dict(cell=key,repetition=1,physical_run_id=10001,
            action_id=action['id'],path=action['planned_output'],attempt_state=state,evidence=[state]))
    value.update(source_manifest=write(root,'executed.json',dict(actions=actions)),
        batch_selection=write(root,'selection.json',actions),pause_record=write(root,'pause.json',dict(stopped=True)))
    write(root,ZED_SELECTION,value)
    return value


@pytest.mark.parametrize('status,exit_code', [('evaluated',0),('evaluated_failure_or_review',134),
                                           ('no_trajectory',139),('evaluation_failed',0)])
def test_success_failure_and_missing_export_are_all_retained(tmp_path,status,exit_code):
    value=fixture(tmp_path,status,exit_code)
    assert completed_zed_selections(tmp_path)==value['cells']
    for algo in ('orbslam3','okvis2','okvis2x'):
        cell=dict(algorithm=algo,dataset='zed2i',run_type='vio',
                  comparison_membership='corrected_zed_first_20261002_pending_claim_review')
        attempt=dict(exists=True,logical_repetition=1,numerical_status='ok' if exit_code==0 else 'scale_collapse')
        category,reason=action_category(cell,attempt,dict(reuse_qualified=True,fresh_cohort=True))
        assert category=='blocked' and 'no_automatic_rerun' in reason


def test_missing_failed_cell_cannot_be_omitted(tmp_path):
    value=fixture(tmp_path,'evaluated_failure_or_review',134)
    value['completed'].pop();write(tmp_path,ZED_SELECTION,value)
    with pytest.raises(ValueError,match='all three'):
        completed_zed_selections(tmp_path)


@pytest.mark.parametrize('status,evaluated', [('accepted_with_limitation',True),
                                             ('valid_observed_failure',False)])
def test_reviewed_completed_slot_is_reusable_without_resampling(status,evaluated):
    cell=dict(algorithm='orbslam3',dataset='zed2i',run_type='vio',
              comparison_membership='corrected_zed_first_20261002')
    attempt=dict(exists=True,logical_repetition=1,numerical_status='ok',evaluated=evaluated,
                 qualification=dict(review='explicit_claim_review',reuse_qualified=True,status=status))
    category,reason=action_category(cell,attempt,dict(fresh_cohort=True))
    assert category=='reusable' and 'predeclared_first' in reason
    attempt['qualification']['review']='explicit_claim_review_stale'
    assert action_category(cell,attempt,{})[0]=='blocked'


def test_changed_final_receipt_blocks_selection(tmp_path):
    fixture(tmp_path)
    (tmp_path/'states/orbslam3.json').write_text('{}')
    with pytest.raises(ValueError,match='stale'):
        completed_zed_selections(tmp_path)


def test_active_evaluation_cannot_be_selected_as_finished(tmp_path):
    fixture(tmp_path,'evaluating')
    with pytest.raises(ValueError,match='not terminal'):
        completed_zed_selections(tmp_path)


def test_later_success_cannot_replace_predeclared_first_attempt(tmp_path):
    value=fixture(tmp_path)
    value['completed'][0]['physical_run_id']=10002
    write(tmp_path,ZED_SELECTION,value)
    with pytest.raises(ValueError,match='predeclared first'):
        completed_zed_selections(tmp_path)


def test_absent_selection_keeps_existing_behavior(tmp_path):
    assert completed_zed_selections(tmp_path)=={}


def test_future_manifest_rechecks_completed_selection_dependencies(tmp_path):
    from test_repair_plan import manifest
    m=manifest()
    m['inventory']=write(tmp_path,'inventory.json',dict(cells=[dict(key='vo/test/seq/okvis2')]))
    receipt=write(tmp_path,'receipt.json',dict(status='evaluated_failure_or_review'))
    m['completed_attempt_selection_evidence']=[receipt]
    assert validate(tmp_path,m)==[]
    (tmp_path/'receipt.json').write_text('{}')
    assert 'stale or absent evidence: receipt.json' in validate(tmp_path,m)
