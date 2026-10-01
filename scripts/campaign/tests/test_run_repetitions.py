"""Transactional behavior with fake executors only; no SLAM execution."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_repetitions import execute_attempt, lock
from prepare_cell import validate_cell


def arguments():
    return dict(runner=['estimate'], evaluator=['evaluate'],cache_check=['current'],validator=['validate'])


def fake_executor(run, events, *, exit_code=0, numeric='ok', eval_code=0, interrupt=False):
    def execute(command,check=False):
        action=command[0];events.append(action)
        if action=='estimate':
            run.mkdir(parents=True)
            (run/'run_meta.json').write_text(json.dumps({'process':{'exit_code':exit_code}}))
            (run/'trajectory.txt').write_text('immutable native trajectory\n')
            if interrupt:
                raise KeyboardInterrupt()
            return subprocess.CompletedProcess(command,exit_code)
        if action=='current':
            return subprocess.CompletedProcess(command,0 if (run/'run_eval.json').exists() else 1)
        if action=='evaluate':
            (run/'run_eval.json').write_text(json.dumps({'run_status':numeric,'qualification':{'status':'pending_review'}}))
            return subprocess.CompletedProcess(command,eval_code)
        return subprocess.CompletedProcess(command,0)
    return execute


def test_each_attempt_evaluated_before_next_and_resume_skips_estimation(tmp_path):
    events=[]
    for i in (1,2):
        run=tmp_path/f'run{i}';state=tmp_path/f'state{i}.json'
        args=arguments();args['execute']=fake_executor(run,events)
        result=execute_attempt(run,state,**args)
        assert result['status']=='evaluated'
        assert (run/'COMPLETE').is_file()
        assert result['qualification']=='pending_review'
    assert events==['estimate','current','evaluate','validate']*2
    events.clear()
    execute_attempt(tmp_path/'run1',tmp_path/'state1.json',**arguments(),execute=fake_executor(tmp_path/'run1',events))
    assert events==['current','validate']


def test_failed_process_saved_trajectory_is_evaluated_and_not_retried(tmp_path):
    run=tmp_path/'run1';state=tmp_path/'state.json';events=[]
    fake=fake_executor(run,events,exit_code=134,numeric='scale_collapse')
    result=execute_attempt(run,state,**arguments(),execute=fake)
    assert result['status']=='evaluated_failure_or_review'
    assert result['numerical_status']=='scale_collapse'
    assert not (run/'COMPLETE').exists()
    before=(run/'trajectory.txt').read_bytes()
    execute_attempt(run,state,**arguments(),execute=fake)
    assert events.count('estimate')==1
    assert (run/'trajectory.txt').read_bytes()==before


def test_partial_or_empty_attempt_is_preserved_without_running(tmp_path):
    for name in ['partial','empty']:
        run=tmp_path/name;run.mkdir()
        if name=='partial': (run/'stderr.txt').write_text('native crash')
        events=[]
        result=execute_attempt(run,tmp_path/(name+'.json'),**arguments(),execute=fake_executor(run,events))
        assert result['status']=='preserved_without_trajectory'
        assert not events
    assert (tmp_path/'partial/stderr.txt').read_text()=='native crash'


def test_evaluator_failure_retries_only_evaluation(tmp_path):
    run=tmp_path/'run1';state=tmp_path/'state.json';events=[]
    fake=fake_executor(run,events,eval_code=1)
    assert execute_attempt(run,state,**arguments(),execute=fake)['status']=='evaluation_failed'
    # Simulate an evaluator crash that left no valid JSON to cache.
    (run/'run_eval.json').unlink()
    good=fake_executor(run,events)
    assert execute_attempt(run,state,**arguments(),execute=good)['status']=='evaluated'
    assert events.count('estimate')==1
    assert events.count('evaluate')==2


def test_interruption_records_state_and_resumes_saved_output(tmp_path):
    run=tmp_path/'run1';state=tmp_path/'state.json';events=[]
    with pytest.raises(KeyboardInterrupt):
        execute_attempt(run,state,**arguments(),execute=fake_executor(run,events,interrupt=True))
    assert json.loads(state.read_text())['status']=='interrupted'
    execute_attempt(run,state,**arguments(),execute=fake_executor(run,events))
    assert events.count('estimate')==1
    assert 'evaluate' in events


def test_changed_repetition_identity_requires_new_attempt(tmp_path):
    run=tmp_path/'run1';state=tmp_path/'state.json';events=[]
    execute_attempt(run,state,**arguments(),execute=fake_executor(run,events),identity={'repetition':1})
    with pytest.raises(RuntimeError,match='identity changed'):
        execute_attempt(run,state,**arguments(),execute=fake_executor(run,events),identity={'repetition':2})


def test_recovery_only_never_starts_missing_run(tmp_path):
    events=[];run=tmp_path/'run1'
    result=execute_attempt(run,tmp_path/'state.json',**arguments(),execute=fake_executor(run,events),recover_only=True)
    assert result['status']=='no_saved_attempt'
    assert not events and not run.exists()
    assert not (tmp_path/'state.json').exists()


def test_lock_and_path_reject_conflicts(tmp_path):
    with lock(tmp_path/'test.lock'):
        with pytest.raises(RuntimeError,match='another process'):
            with lock(tmp_path/'test.lock'): pass
    (tmp_path/'results').mkdir()
    (tmp_path/'results/vo').symlink_to(tmp_path/'elsewhere')
    with pytest.raises(ValueError,match='symlink'):
        validate_cell(tmp_path,'vo','test','seq','algo')
