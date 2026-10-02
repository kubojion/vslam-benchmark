import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts/campaign'))
from build_repair_inventory import cohort_identity


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',', ':'),allow_nan=False).encode()).hexdigest()


def capture(tmp_path,name,stamp,*,blob='source-a',binary='native-a'):
    run=tmp_path/name;run.mkdir()
    implementation={'schema':1,'captured_at':stamp,'elapsed_s':stamp,'trees':[
        {'role':'workspace','entries':[{'path':'scripts/runner.py','sha256':blob}]},
        {'role':'algorithm','commit':'historic-source','entries':[]}]}
    p=run/'implementation.json';p.write_text(json.dumps(implementation));sha=hashlib.sha256(p.read_bytes()).hexdigest()
    runtime={'schema':1,'files':[{'path':'estimator.so','sha256':binary}]};runtime['sha256']=digest(runtime)
    q=run/'runtime.json';q.write_text(json.dumps(runtime))
    meta={'machine_id':'server','provenance':{
        'workspace':{'commit':'historic-runner','dirty':True,'diff_sha256':'diff',
            'snapshot':p.name,'snapshot_sha256':sha,'capture_role':'workspace'},
        'implementation_capture':{'snapshot':p.name,'snapshot_sha256':sha},
        'runtime_assets':{'snapshot':q.name,'snapshot_sha256':hashlib.sha256(q.read_bytes()).hexdigest(),
            'content_sha256':runtime['sha256']}}}
    return run,meta


def test_same_bytes_different_capture_receipts_are_same_cohort(tmp_path):
    a,am=capture(tmp_path,'run1',1);b,bm=capture(tmp_path,'run2',2)
    assert am['provenance']['workspace']['snapshot_sha256']!=bm['provenance']['workspace']['snapshot_sha256']
    assert cohort_identity(am,'airslam',run_dir=a)==cohort_identity(bm,'airslam',run_dir=b)


@pytest.mark.parametrize('change',[{'blob':'source-b'},{'binary':'native-b'}])
def test_changed_source_or_runtime_stays_separate(tmp_path,change):
    a,am=capture(tmp_path,'run1',1);b,bm=capture(tmp_path,'run2',2,**change)
    assert cohort_identity(am,'airslam',run_dir=a)[0]!=cohort_identity(bm,'airslam',run_dir=b)[0]


def test_missing_or_changed_captures_fail_closed(tmp_path):
    a,am=capture(tmp_path,'run1',1)
    with pytest.raises(ValueError,match='run directory'):cohort_identity(am,'airslam')
    (a/'implementation.json').write_text('{}')
    with pytest.raises(ValueError,match='changed or missing'):cohort_identity(am,'airslam',run_dir=a)


def test_unverified_runtime_content_digest_rejected(tmp_path):
    a,am=capture(tmp_path,'run1',1)
    am['provenance']['runtime_assets']['content_sha256']='wrong'
    with pytest.raises(ValueError,match='runtime cohort'):cohort_identity(am,'airslam',run_dir=a)


def test_historical_payload_and_signature_preserved():
    am={'machine_id':'server','provenance':{'workspace':{'commit':'original','dirty':True,'diff_sha256':'diff'},
        'sources':[{'role':'algorithm','commit':'old-author-hash'}],'parameters':{'seed':1001}}}
    assert cohort_identity(am,'airslam')[0]=='725330314e03fddff75225b286bf02fa471640aafe072d8df649ee28f3928c93'
    assert cohort_identity(am,'dpvo')[0]=='d4fb082899efd045086914d7a57a3b287bf4f8e177804ea33f0e98ae6fe624a2'

from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'scripts/eval'),str(ROOT/'scripts/campaign'),str(ROOT/'scripts/eval/tests')]
from build_benchmark_csv import build_rows,build_historical_rows
from _aggregate_runs import summarize_cell
from test_reconciled_exports import attempt,evaluation


def test_current_failures_and_original_scores_survive_predeclared_cohort_selection(tmp_path):
    current=[];old=[]
    for i in (1,2,3,4,5,6):
        relative=f'vio/euroc_mav/MH_01_easy/airslam/run{i}'
        run=tmp_path/'results'/relative;run.mkdir(parents=True)
        ev=evaluation(run_status='scale_collapse' if i==5 else 'ok',
                      ate_se3={'rmse':1000 if i==5 else .01*i})
        path=run/'run_eval.json';path.write_text(json.dumps(ev))
        record=attempt(i,algo='airslam',mode='vio',path='results/'+relative,
            evaluation_path=str(path.relative_to(tmp_path)))
        if i<=3:
            record['category']='superseded_calibration_cohort';old.append(record)
        else:current.append(record)
    inv={'cells':[{'attempts':current,'original_campaign_member':True,
        'comparison_membership':'corrected_euroc_20261001'}],'other_artifacts':old}
    rows=build_rows(inv,repo=tmp_path);historical=build_historical_rows(inv,repo=tmp_path)
    assert [int(r['run']) for r in rows]==[4,5,6]
    assert [int(r['run']) for r in historical]==[1,2,3]
    assert all(r['campaign_membership']=='corrected_euroc_20261001' for r in rows)
    assert all(r['campaign_membership']=='superseded_calibration_cohort' for r in historical)
    summary=summarize_cell(rows)
    assert summary['planned_slots']==3 and summary['outcomes']=={'ok':2,'scale_collapse':1}
    assert summary['cohorts'][0]['conditional_primary_ate']['n']==2
    assert not summary['clean_qualified_n3']


@pytest.mark.parametrize('category',['superseded_calibration_cohort','gnss_variant'])
def test_companion_and_variant_exports_reject_stale_qualification(tmp_path,category):
    path=tmp_path/'evaluation.json';path.write_text(json.dumps(evaluation()))
    a=attempt(category=category,evaluation_path='evaluation.json')
    inv={'cells':[],'other_artifacts':[a],'qualification_review':{'evidence':['new review']}}
    fn=build_historical_rows if category=='superseded_calibration_cohort' else build_rows
    with pytest.raises(ValueError,match='qualification'):
        fn(inv,repo=tmp_path)


def test_interrupted_diagnostic_without_metadata_is_still_an_attempt(tmp_path):
    from build_repair_inventory import attempt_directories,saved_attempt
    relative='vio/euroc_mav/diagnostic/openvins/run4'
    run=tmp_path/'results'/relative;run.mkdir(parents=True)
    (run/'run_log.txt').write_text('interrupted before trajectory export')
    assert attempt_directories(tmp_path)=={run}
    record=saved_attempt(tmp_path,relative,tmp_path/'stage')
    assert record['exists'] and not record['evaluated'] and not record['trajectory_saved']
    assert record['qualification']['status']=='blocked'
    assert record['files'][0]['path'].endswith('run_log.txt')
