import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'run'))
from _capture_implementation import capture,verify_capture
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'results'))
from validate_run import validate_implementation_capture


def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL)


def init(root):
    root.mkdir(parents=True,exist_ok=True)
    git(root,'init','-q');git(root,'config','user.name','fixture');git(root,'config','user.email','fixture@example.invalid')


def commit(root):
    git(root,'add','.');git(root,'commit','-qm','fixture')


def fixture(tmp_path):
    root=tmp_path/'repo';init(root)
    (root/'scripts').mkdir();(root/'configs').mkdir()
    (root/'scripts/runner.py').write_bytes(b'original\r\n')
    (root/'configs/calibration.yaml').write_text('fx: 10\n')
    commit(root)
    source=root/'src/okvis2';init(source)
    (source/'source.cpp').write_text('old\n')
    (source/'removed.cpp').write_text('remove\n')
    (source/'.gitignore').write_text('ignored-build.so\n')
    commit(source)
    nested=source/'dependency';init(nested)
    (nested/'math.cpp').write_bytes(b'nested original\n');commit(nested)
    git(source,'add','dependency');git(source,'commit','-qm','nested dependency')
    (source/'source.cpp').write_text('local change\n')
    (source/'removed.cpp').unlink()
    (nested/'math.cpp').write_bytes(b'nested modified\r\n')
    (nested/'new.h').write_bytes(b'untracked source\n')
    (source/'link').symlink_to('source.cpp')
    (source/'ignored-build.so').write_text('separate native build contract')
    (root/'scripts/runner.py').write_bytes(b'dirty runner\r\n')
    run=root/'results/vo/test/seq/okvis2/run10001';run.mkdir(parents=True)
    return root,run,source,nested


def test_exact_runner_nested_dirty_untracked_deleted_and_symlink_bytes_are_recoverable(tmp_path):
    root,run,source,nested=fixture(tmp_path)
    target,value=capture(root,run,'okvis2')
    report=verify_capture(root,target,check_live=True)
    assert report['archive_verified'] and report['live_checkout_verified']
    trees={t['role']:t for t in value['trees']}
    entries={r['path']:r for r in trees['algorithm']['entries']}
    assert entries['removed.cpp']['kind']=='absent_tracked_file'
    assert 'ignored-build.so' not in entries
    assert entries['link']['kind']=='symlink'
    dep={e['path']:e for e in entries['dependency']['checkout']['entries']}
    assert dep['new.h']['tracked'] is False
    store=root/value['blob_store']
    assert (store/dep['math.cpp']['sha256']).read_bytes()==b'nested modified\r\n'
    runner=next(e for e in trees['workspace']['entries'] if e['path']=='scripts/runner.py')
    assert (store/runner['sha256']).read_bytes()==b'dirty runner\r\n'
    assert (store/entries['link']['sha256']).read_bytes()==b'source.cpp'
    with pytest.raises(ValueError,match='already exists'):capture(root,run,'okvis2')
    # A second attempt reuses the same immutable content blobs.
    count=len(list(store.iterdir()));another=run.with_name('run10002');another.mkdir()
    capture(root,another,'okvis2')
    assert len(list(store.iterdir()))==count


def test_later_source_edits_do_not_destroy_archive_and_are_detected(tmp_path):
    root,run,source,nested=fixture(tmp_path)
    target,value=capture(root,run,'okvis2')
    (nested/'math.cpp').write_text('concurrent edit\n')
    assert verify_capture(root,target)['archive_verified']
    with pytest.raises(ValueError,match='source bytes changed'):verify_capture(root,target,check_live=True)
    digest=next(e['sha256'] for e in value['trees'][0]['entries'] if e['kind']=='file')
    (root/value['blob_store']/digest).write_text('corrupt archive')
    with pytest.raises(ValueError,match='source archive blob'):verify_capture(root,target)


def test_capture_verifier_rejects_paths_outside_archive(tmp_path):
    root,run,source,nested=fixture(tmp_path)
    target,value=capture(root,run,'okvis2')
    value['trees'][0]['entries'][0]['path']='../../outside'
    target.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='unsafe capture path'):verify_capture(root,target)


def test_new_completion_requires_capture_but_historical_validation_does_not(tmp_path):
    root,run,source,nested=fixture(tmp_path)
    meta=run/'run_meta.json';meta.write_text('{}')
    assert validate_implementation_capture(run,repo=root)==[]
    assert validate_implementation_capture(run,required=True,repo=root)
    target,value=capture(root,run,'okvis2')
    meta.write_text(json.dumps(dict(provenance=dict(implementation_capture=dict(
        snapshot='provenance/implementation.json',phase='before_estimation',
        snapshot_sha256=hashlib.sha256(target.read_bytes()).hexdigest())))))
    assert validate_implementation_capture(run,required=True,repo=root)==[]
    (source/'source.cpp').write_text('changed after the attempt\n')
    assert validate_implementation_capture(run,required=True,repo=root)==[]
    target.write_text(target.read_text()+' ')
    assert 'manifest hash mismatch' in validate_implementation_capture(run,required=True,repo=root)[0]


def test_reviewed_source_identity_rejects_substitution_before_estimation(tmp_path,monkeypatch):
    root,run,source,nested=fixture(tmp_path)
    monkeypatch.setenv('VSLAM_EXPECTED_SOURCE_SHA256','0'*64)
    with pytest.raises(ValueError,match='reviewed campaign'):capture(root,run,'okvis2')
    assert not (run/'provenance/implementation.json').exists()


def test_direct_runner_does_not_overwrite_orphan_log(tmp_path):
    root=tmp_path/'workspace';log=root/'logs/test_seq_okvis2_vo_run10001.log'
    log.parent.mkdir(parents=True);log.write_bytes(b'original failure evidence\n')
    script=Path(__file__).resolve().parents[2]/'_paths.sh'
    result=subprocess.run(['bash','-c',
        'set -e; WS="$1"; source "$2"; resolve_run_type vo; prepare_fresh_run_dir "$WS/results/vo/test/seq/okvis2/run10001"',
        'fixture',str(root),str(script)],capture_output=True,text=True)
    assert result.returncode==2 and 'attempt log is preserved' in result.stderr
    assert log.read_bytes()==b'original failure evidence\n'
    assert not (root/'results/vo/test/seq/okvis2/run10001').exists()
