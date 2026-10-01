import copy
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'campaign'))
from build_benchmark_csv import build_rows, csv_text, load_inventory, preserved_write, row_from_attempt
from build_repair_inventory import cohort_identity
from _aggregate_runs import summarize_cell, write_cells
from make_report_tables import cell_text, render_tables, main as tables_main
from _saved_run import interpreted_measurements


def attempt(run=1,algo='okvis2',mode='vo',**changes):
    return dict(path=f'results/{mode}/test/seq/{algo}/run{run}',exists=True,trajectory_saved=True,
                process={'exit_code':0},qualification={'status':'pending_review','blockers':['review']},
                cohort_fingerprint='cohort-a',files=[],evaluation_path=None) | changes


def evaluation(**changes):
    return dict(eval_schema=3,run_status='ok',primary_alignment='se3',ate_se3={'rmse':1.0},ate={'rmse':0.1},
                scale_factor=0.8,n_pairs_ate=20,coverage={'coverage_gap_pct':100,'export_kind':'poses'},
                robustness={},runtime={},pose_frames={},execution={'status':'exited_zero'}) | changes


def rows(tmp_path,n=3):
    return [row_from_attempt(attempt(i),evaluation(),None,repo=tmp_path) for i in range(1,n+1)]


def test_legacy_processing_assumptions_are_withheld_without_mutating_evidence(tmp_path):
    raw={'measurement_schema':1,'measurements':{'mode':'max_throughput','input_frames':100,
         'processed_frames':100,'processing_time_s':5.,'processing_fps':20.,'end_to_end_time_s':5.}}
    before=copy.deepcopy(raw)
    interpreted=interpreted_measurements(raw)
    assert raw==before and interpreted['processed_frames'] is None
    assert interpreted['command_input_fps']==20. and interpreted['processing_fps'] is None
    row=row_from_attempt(attempt(),evaluation(runtime=interpreted),None,repo=tmp_path)
    assert row['processed_frames'] is None and row['fps'] is None and row['processing_ms_per_frame'] is None
    assert row['command_input_fps']==20. and 'withheld' in row['measurement_warning']


def test_monocular_primary_sparse_unknowns_and_failed_position_diagnostic(tmp_path):
    mono=row_from_attempt(attempt(algo='dpvo'),evaluation(primary_alignment='sim3'),None,repo=tmp_path)
    assert mono['primary_ate_rmse_m']==.1 and mono['scale_error_pct'] is None
    sparse=row_from_attempt(attempt(algo='airslam'),evaluation(
        coverage={'export_kind':'keyframes','coverage_gap_pct':None,'export_span_pct':100},
        runtime={'legacy_fps':42,'output_poses':20}),None,repo=tmp_path)
    assert sparse['coverage_gap_pct'] is None and sparse['frames_tracked'] is None
    assert sparse['processed_frames'] is None and sparse['fps'] is None
    assert sparse['init_success'] is None and sparse['tracking_losses'] is None
    assert 'keyframes' in cell_text([sparse])
    failed=row_from_attempt(attempt(mode='gnss-vio'),evaluation(run_status='eval_failed',ate_se3={},ate={},
        position_only_diagnostic={'ate_se3':{'rmse':5.26}}),None,repo=tmp_path)
    assert failed['primary_ate_rmse_m'] is None and failed['ate_origin_rmse_m'] is None
    assert failed['position_only_diagnostic_ate_se3_rmse_m']==5.26
    assert failed['position_only_diagnostic_qualified'] is False and failed['paper_ready'] is False
    with pytest.raises(ValueError,match='schema-3'):
        row_from_attempt(attempt(),evaluation(eval_schema=2),None,repo=tmp_path)


def test_failure_missing_exit_and_cohort_denominators(tmp_path):
    data=rows(tmp_path)
    data[1].update(run_status='scale_collapse',primary_ate_rmse_m=10000.)
    data[2].update(run_status='missing',eval_schema=None,attempt_exists=False,primary_ate_rmse_m=None)
    result=summarize_cell(data)
    assert result['planned_slots']==3 and result['evaluated']==2 and result['attempted']==2
    assert result['outcomes']=={'ok':1,'scale_collapse':1,'missing':1}
    assert result['cohorts'][0]['conditional_primary_ate']['median']==1
    assert result['cohorts'][0]['conditional_primary_ate']['sample_std'] is None
    assert result['clean_qualified_n3'] is False
    text=cell_text(data)
    assert '1 scale_collapse' in text and '1 missing' in text and 'eval 2/3' in text and '✅' not in text
    data=rows(tmp_path)
    for r in data:r['paper_ready']=True
    assert summarize_cell(data)['clean_qualified_n3']
    data[1]['process_exit_code']=139
    assert not summarize_cell(data)['clean_qualified_n3']
    data[1]['process_exit_code']=0;data[1]['coverage_gap_pct']=None
    assert not summarize_cell(data)['clean_qualified_n3']
    data[1]['coverage_gap_pct']=100;data[2]['cohort']='other'
    result=summarize_cell(data)
    assert len(result['cohorts'])==2 and not result['clean_qualified_n3']
    assert 'cohort other' in cell_text(data)
    data[0]['scientific_status']='rerun_required'
    assert 'rerun required' in cell_text(data)


def test_variant_separation_preservation_and_reproducible_check(tmp_path):
    data=rows(tmp_path,1);var=copy.deepcopy(data[0]);var['gnss_variant']='ppk';var['primary_ate_rmse_m']=2
    with pytest.raises(ValueError,match='variants'):
        summarize_cell(data+[var])
    out=tmp_path/'reports';n,errors=write_cells(data+[var],out,repo=tmp_path)
    assert n==2 and not errors
    assert (out/'vo/test/seq/okvis2/variants/ppk/summary.json').exists()
    assert write_cells(data+[var],out,repo=tmp_path,check=True)[1]==[]
    target=out/'vo/test/seq/okvis2/report.md';original=target.read_bytes();target.write_text('stale')
    assert str(target) in write_cells(data+[var],out,repo=tmp_path,check=True)[1]
    assert target.read_text()=='stale'
    write_cells(data+[var],out,repo=tmp_path)
    assert target.read_bytes()==original
    assert (tmp_path/'results/.derived-history'/('report.md.'+hashlib.sha256(b'stale').hexdigest())).read_bytes()==b'stale'


def test_inventory_excludes_smoke_but_keeps_missing_and_variants_and_rejects_stale_hash(tmp_path):
    a=attempt(exists=False,trajectory_saved=False)
    variant=attempt();variant['path']='results/gnss-vio/test/seq/okvis2x/run1_ppk';variant['category']='gnss_variant'
    smoke=attempt(algo='droidslam');smoke['category']='historical_excluded'
    inv={'cells':[{'original_campaign_member':True,'attempts':[a]}], 'other_artifacts':[variant,smoke]}
    data=build_rows(inv,repo=tmp_path)
    assert len(data)==2 and {r['gnss_variant'] for r in data}=={'default','ppk'}
    assert next(r for r in data if r['gnss_variant']=='default')['run_status']=='missing'
    evidence=tmp_path/'evidence';evidence.write_text('before')
    a['files']=[{'path':'evidence','sha256':hashlib.sha256(b'before').hexdigest()}]
    path=tmp_path/'inventory.json';path.write_text(json.dumps(inv))
    assert load_inventory(path,repo=tmp_path)==inv
    evidence.write_text('after')
    with pytest.raises(ValueError,match='regenerated'):load_inventory(path,repo=tmp_path)


def test_cohort_covers_binary_source_settings_hardware_and_only_excludes_dpvo_seed():
    meta={'machine_id':'server','provenance':{'parameters':{'seed':1001,'stride':1},
            'sources':[{'role':'algorithm','commit':'historical','dirty':True,'diff_sha256':'a'}],
            'artifacts':[{'role':'config','snapshot_sha256':'x','path':'tmp-name'}],
            'binaries':[{'role':'estimator','sha256':'b'}]}}
    baseline=cohort_identity(meta,'dpvo')[0]
    seed=copy.deepcopy(meta);seed['provenance']['parameters']['seed']=1002
    assert cohort_identity(seed,'dpvo')[0]==baseline
    assert cohort_identity(seed,'other')[0]!=cohort_identity(meta,'other')[0]
    for field in ('source','binary','stride','machine'):
        changed=copy.deepcopy(meta)
        if field=='source':changed['provenance']['sources'][0]['diff_sha256']='different'
        if field=='binary':changed['provenance']['binaries'][0]['sha256']='different'
        if field=='stride':changed['provenance']['parameters']['stride']=2
        if field=='machine':changed['machine_id']='laptop'
        assert cohort_identity(changed,'dpvo')[0]!=baseline
    assert cohort_identity({},'dpvo')==(None,None)
    assert cohort_identity(meta,'dpvo')[1]['sources'][0]['commit']=='historical'


def test_tables_check_is_read_only_and_detects_changed_bytes(tmp_path,monkeypatch):
    import make_report_tables as module
    data=rows(tmp_path,1);data[0].update(dataset='euroc_mav',seq='MH_01_easy',algo='dpvo',primary_alignment='sim3',primary_ate_rmse_m=.1)
    monkeypatch.setattr(module,'load_inventory',lambda path:{})
    monkeypatch.setattr(module,'build_rows',lambda inv:data)
    csv_dir=tmp_path/'csv';out=tmp_path/'tables';csv_dir.mkdir();out.mkdir()
    for mode in module.RUN_TYPES:
        (csv_dir/f'benchmark-{mode}.csv').write_text(csv_text([r for r in data if r['run_type']==mode]))
    monkeypatch.setattr(sys,'argv',['tables','--csv-dir',str(csv_dir),'--output-dir',str(out)])
    assert tables_main()==0
    content=(out/'tables-vo.md').read_text()
    assert 'DPVO (mono) — Sim(3)' in content and '0.1 [score N=1]' in content
    monkeypatch.setattr(sys,'argv',sys.argv+['--check'])
    assert tables_main()==0
    target=out/'tables-vo.md';target.write_text('stale')
    assert tables_main()==1 and target.read_text()=='stale'
    source=csv_dir/'benchmark-vo.csv';source.write_text('stale CSV')
    assert tables_main()==1 and source.read_text()=='stale CSV'
