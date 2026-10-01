import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from acceptance_ledger import LEDGER, numerical_digest, reviewed_decision, cell_acceptance
from build_future_manifest import action_category
from update_todo_matrices import render_cell


def fixture(repo, status='accepted'):
    relative='vo/euroc_mav/MH_01_easy/okvis2/run1'
    original=repo/'original.txt';original.write_text('saved config and output')
    ev={'run_status':'ok','ate_se3':{'rmse':0.1}}
    record=dict(status=status,exists=True,evaluation_sha256=numerical_digest(ev),claim='recorded_profile',
        blockers=[],claim_limits=[],disclosures=['historical_build_linkage'],
        evidence=[{'path':'original.txt','sha256':hashlib.sha256(original.read_bytes()).hexdigest()}])
    path=repo/LEDGER;path.parent.mkdir(parents=True);path.write_text(json.dumps(
        {'attempts':{relative:record},'supporting_evidence':[]}))
    return relative,ev


def test_explicit_review_replays_without_numerical_or_qualification_hash_cycle(tmp_path):
    relative,ev=fixture(tmp_path)
    first=reviewed_decision(tmp_path,relative,{},ev,[],[{'verified':True}],True)
    assert first['status']=='accepted' and first['reuse_qualified'] and first['accuracy_eligible']
    ev['qualification']=first;ev['qualification_provenance']={'updated':'review-only'}
    assert reviewed_decision(tmp_path,relative,{},ev,[],[{'verified':True}],True)==first


def test_changed_log_config_or_numerical_evidence_and_new_defects_block_acceptance(tmp_path):
    relative,ev=fixture(tmp_path)
    def check(value, findings=()):
        return reviewed_decision(tmp_path,relative,{},value,findings,[{'verified':True}],True)
    changed=copy.deepcopy(ev);changed['ate_se3']['rmse']=0.0001
    assert check(changed)['status']=='blocked'
    assert check(ev,[{'code':'new_calibration_defect'}])['status']=='blocked'
    (tmp_path/'original.txt').write_text('different effective config')
    assert check(ev)['status']=='blocked'


def attempt(status='accepted', outcome='ok', coverage=100):
    return dict(exists=True,evaluated=True,numerical_status=outcome,coverage={'coverage_gap_pct':coverage},
        process={'exit_code':0},qualification={'status':status,'claim_limits':[]})


def test_green_requires_three_accepted_clean_compatible_dense_repetitions():
    attempts=[attempt() for _ in range(3)]
    cell=dict(run_type='vo',algorithm='okvis2',dataset='euroc_mav',evaluated=3,attempts=attempts)
    assert render_cell(cell)=='✅ N=3'
    for status,outcome,coverage in [('accepted_with_limitation','ok',100),
        ('valid_observed_failure','scale_collapse',100),('accepted','ok',94.9)]:
        changed=copy.deepcopy(cell);changed['attempts'][1]=attempt(status,outcome,coverage)
        assert '✅' not in render_cell(changed)
    assert not cell_acceptance(attempts,False)['clean_qualified_n3']
    attempts[0]['qualification']['native_error_observations']=[{'line':125,'text':'terminate called'}]
    assert not cell_acceptance(attempts)['clean_qualified_n3']


def test_accepted_native_failure_without_trajectory_is_reused_not_sampled_again():
    cell={'algorithm':'orbslam3','dataset':'hortimulti','run_type':'vo'}
    a=attempt('valid_observed_failure',None);a.update(trajectory_saved=False,evaluated=False)
    a['qualification'].update(review='explicit_claim_review',reuse_qualified=True)
    assert action_category(cell,a,{})[0]=='reusable'
    a['confirmed_protocol_findings']=[{'code':'bad_config'}]
    assert action_category(cell,a,{})[0]=='required_rerun'
