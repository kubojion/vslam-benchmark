import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_future_manifest import action_category, qualification_prerequisites
from build_repair_inventory import runtime_estimate
from run_future_manifest import validate,execute,check_execution_environment,UNREVIEWED_OVERRIDES
from update_todo_matrices import update


def test_true_failure_is_retained_but_invalid_config_is_replaced():
    cell=dict(algorithm='okvis2',dataset='zed2i',run_type='vo')
    attempt=dict(exists=True,trajectory_saved=True,evaluated=True,numerical_status='scale_collapse',
                 qualification={'reuse_qualified':True})
    assert action_category(cell,attempt,{'reuse_qualified':True})[0]=='reusable'
    attempt['qualification']['reuse_qualified']=False
    assert action_category(cell,attempt,{'reuse_qualified':True})[0]=='blocked'
    attempt['qualification']['reuse_qualified']=True
    cell['algorithm']='orbslam3'
    assert action_category(cell,attempt,{'reuse_qualified':True})[0]=='required_rerun'
    attempt['numerical_status']='eval_failed';cell['algorithm']='okvis2'
    assert action_category(cell,attempt,{'reuse_qualified':True})[0]=='blocked'


def test_unknown_reference_and_recorded_exit_are_concrete_prerequisites():
    cell=dict(algorithm='okvis2',dataset='hortimulti',run_type='vo-lc')
    attempt=dict(process={'exit_code':134},qualification={'blockers':['reference_frame_unknown']})
    items=qualification_prerequisites(cell,attempt,{})
    assert 'link_february_reference_generation_origin_and_clock_to_each_saved_session' in items
    assert 'resolve_or_document_claim_limit:reference_frame_unknown' in items
    assert 'retain_nonzero_exit_and_review_saved_native_failure_evidence' in items
    assert any('bundle_adjustment' in item for item in items)


def test_inherited_override_cannot_silently_change_future_recipe():
    check_execution_environment({'PATH':'/usr/bin','DPVO_SEED':''})
    for key in ('BASALT_CONFIG','DPVO_STRIDE','GNSS_CSV','GT_OVERRIDE','CUDA_VISIBLE_DEVICES'):
        with pytest.raises(ValueError,match=key):check_execution_environment({key:'changed'})


def test_runtime_excludes_other_hardware_and_partial_or_failed_runs():
    base=dict(machine_id='machine-3c9dca59a50f',process={'exit_code':0},numerical_status='ok',
              runtime={'end_to_end_time_s':100,'mode':'paced'},coverage={'coverage_gap_pct':99},path='run1')
    other=copy.deepcopy(base);other['machine_id']='laptop';other['runtime']['end_to_end_time_s']=1
    partial=copy.deepcopy(base);partial['coverage']['coverage_gap_pct']=20
    failed=copy.deepcopy(base);failed['process']['exit_code']=134
    native=copy.deepcopy(base);native['qualification']={'native_error_observations':[{'text':'terminate called'}]}
    invalid=copy.deepcopy(base);invalid['confirmed_protocol_findings']=[{'code':'wrong_camera_imu_offset'}]
    result=runtime_estimate([base,other,partial,failed,native,invalid])
    assert result['estimate_s']==100 and result['sources']==['run1']
    assert runtime_estimate([other,partial,failed,invalid])['estimate_s'] is None


def manifest():
    actions=[]
    for r in (1,2,3):
        actions.append(dict(id=f'vo/test/seq/okvis2/default/r{r}',cell='vo/test/seq/okvis2',repetition=r,
            category='missing',cohort='test',planned_output=f'results/vo/test/seq/okvis2/run{10000+r}',
            command=['python3','scripts/campaign/run_repetitions.py','test','seq','okvis2','3','vo','--run-id',str(10000+r),'--repetition',str(r),'--cohort','test'],
            prerequisites=['review'],prior_evidence=[],review_evidence=[],
            readiness={'verified_ready_to_run':False,'static_checks':'pending','execution_validation':'not_verified'}))
    return dict(schema_version=2,campaign_id='test',target=dict(repetitions=3,default_cells=1,logical_repetitions=3),actions=actions)


def test_manifest_requires_unique_complete_logical_repetitions_and_matching_commands(tmp_path):
    m=manifest();assert validate(tmp_path,m,check_files=False)==[]
    m['actions'][0]['command'][-1]='wrong-cohort'
    assert 'command disagrees with action identity' in validate(tmp_path,m,check_files=False)
    m=manifest();m['actions'][1]['repetition']=1
    assert any('exactly three' in s for s in validate(tmp_path,m,check_files=False))


def test_no_partial_launch_before_detecting_blocked_action(tmp_path,monkeypatch):
    for name in UNREVIEWED_OVERRIDES:monkeypatch.delenv(name,raising=False)
    m=manifest();events=[]
    def fake(command,check=False):events.append(command);return subprocess.CompletedProcess(command,0)
    with pytest.raises(ValueError,match='blocked'):
        execute(tmp_path,m,'hash',m['actions'],executor=fake)
    assert events==[] and not (tmp_path/'logs').exists()


def test_manifest_cannot_claim_readiness_from_flags_alone(tmp_path):
    m=manifest();m['actions'][0]['readiness']['verified_ready_to_run']=True
    assert any('readiness claim' in s for s in validate(tmp_path,m,check_files=False))


def test_todo_layout_preserved_and_failure_is_not_green():
    sections=[];cells=[]
    sequences=[('rosariov2','sequence1'),('rosariov2','sequence5'),('hortimulti','strawberry02'),('hortimulti','strawberry03'),('euroc_mav','MH_01_easy'),('euroc_mav','MH_03_medium'),('euroc_mav','MH_05_difficult'),('zed2i','field1_110426_full_10fps_q90')]
    for mode in ('vo','vo-lc','vio','vio-lc','gnss-vio'):
        seqs=sequences[:4] if mode=='gnss-vio' else sequences
        sections+=['### Test - `results/'+mode+'/`','| Algorithm | '+' | '.join(s for _,s in seqs)+' |','| OKVIS2 | '+' | '.join(['✅ N=3']*len(seqs))+' |']
        for ds,seq in seqs:
            cells.append(dict(run_type=mode,algorithm='okvis2',dataset=ds,sequence=seq,evaluated=3,
                attempts=[dict(evaluated=True,numerical_status='scale_collapse' if i==1 else 'ok',process={'exit_code':0}) for i in range(3)]))
    before='\n'.join(sections)+'\n';after=update(before,{'cells':cells})
    assert [s.count('|') for s in before.splitlines()]==[s.count('|') for s in after.splitlines()]
    assert [s for s in before.splitlines() if not s.startswith('| OKVIS2')]==[s for s in after.splitlines() if not s.startswith('| OKVIS2')]
    assert '✅' not in after and 'collapse r2' in after


def test_airslam_rectified_imu_finding_requires_preserved_clean_source_and_saved_config(tmp_path):
    import hashlib
    from protocol_findings import historical_findings,AIRSLAM_UNCORRECTED_SOURCE
    rel='vio/euroc_mav/MH_01_easy/airslam/run1';run=tmp_path/'results'/rel;run.mkdir(parents=True)
    (run/'camera.yaml').write_text('use_imu: 1\ndistortion_type: 1\n')
    meta={'provenance':{'artifacts':[{'role':'camera_config','snapshot':'camera.yaml'}],
                       'sources':[{'role':'algorithm','commit':AIRSLAM_UNCORRECTED_SOURCE,'dirty':False}]}}
    meta['provenance']['artifacts'][0]['snapshot_sha256']=hashlib.sha256((run/'camera.yaml').read_bytes()).hexdigest()
    findings=historical_findings(tmp_path,rel,meta)
    assert findings[0]['code']=='airslam_rectified_camera_imu_extrinsic'
    cell={'algorithm':'airslam','dataset':'euroc_mav','run_type':'vio'}
    assert action_category(cell,{'confirmed_protocol_findings':findings},{'reuse_qualified':True})[0]=='required_rerun'
    meta['provenance']['sources'][0]['dirty']=True
    assert historical_findings(tmp_path,rel,meta)==[]  # unknown patch history, not proof of no issue
    meta['provenance']['sources'][0]['dirty']=False
    (run/'camera.yaml').write_text('use_imu: 1\ndistortion_type: 0\n')
    assert historical_findings(tmp_path,rel,meta)==[]
    meta['provenance']['artifacts'][0]['snapshot_sha256']=hashlib.sha256((run/'camera.yaml').read_bytes()).hexdigest()
    assert historical_findings(tmp_path,rel,meta)==[]


def test_airslam_rejects_refinement_retries_before_any_container_or_attempt(tmp_path):
    import os
    repo=Path(__file__).resolve().parents[3]
    fake=tmp_path/'docker';marker=tmp_path/'called'
    fake.write_text('#!/bin/sh\ntouch "'+str(marker)+'"\nexit 99\n');fake.chmod(0o755)
    env=dict(os.environ,PATH=str(tmp_path)+os.pathsep+os.environ['PATH'],AIRSLAM_REFINEMENT_MAX_ATTEMPTS='2')
    run=subprocess.run(['bash',str(repo/'scripts/run/run_airslam.sh'),'unit_no_estimator','sequence','987654','vo-lc'],
                       env=env,capture_output=True,text=True)
    assert run.returncode==2 and 'retries are disabled' in run.stderr
    assert not marker.exists()
    assert not (repo/'results/vo-lc/unit_no_estimator').exists()
