import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _evaluate_run import evaluation_current, preserve_evaluation
from _saved_run import evaluator_identity


def test_existing_metrics_are_preserved_as_independent_bytes(tmp_path):
    old=tmp_path/'run_eval.json';old.write_text('{"eval_schema":2,"ate":5}\n')
    raw=old.read_bytes();preserve_evaluation(old)
    backup=tmp_path/'.evaluation_history'/(hashlib.sha256(raw).hexdigest()+'.json')
    assert backup.read_bytes()==raw
    old.write_text('replacement')
    assert backup.read_bytes()==raw


def test_resume_revalidates_trajectory_metadata_reference_and_calibration(tmp_path):
    run=tmp_path/'run1';run.mkdir()
    inputs=[]
    for path in [run/'trajectory.txt',run/'run_meta.json',tmp_path/'gt.txt',tmp_path/'times.txt']:
        path.write_text('saved evidence')
        inputs.append({'path':str(path.relative_to(tmp_path)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    calib=run/'calibration.yaml';calib.write_text('camera')
    evidence=[{'path':str(calib.relative_to(tmp_path)),'sha256':hashlib.sha256(calib.read_bytes()).hexdigest()}]
    doc={'eval_schema':3,'evaluation_provenance':{'evaluator':evaluator_identity(),'inputs':inputs},'pose_frames':{'evidence':evidence}}
    assert evaluation_current(tmp_path,run,doc)
    calib.write_text('changed')
    assert not evaluation_current(tmp_path,run,doc)
    calib.write_text('camera')
    (tmp_path/'gt.txt').write_text('new reference')
    assert not evaluation_current(tmp_path,run,doc)
