import hashlib
import json
import os
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'run'))
from _capture_inputs import identity,verify_identity,capture
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'results'))
from validate_run import validate_input_capture


def fixture(root):
    seq=root/'datasets/test/seq'
    for camera in ('cam0','cam1'):
        path=seq/'mav0'/camera; (path/'data').mkdir(parents=True)
        (path/'data/0.png').write_bytes(b'camera fixture bytes')
        (path/'data.csv').write_text('#timestamp [ns],filename\n0,0.png\n')
    (seq/'mav0/imu0').mkdir();(seq/'mav0/imu0/data.csv').write_text('0,1,2,3,4,5,6\n')
    (seq/'times.txt').write_text('0\n')
    (seq/'left').symlink_to('mav0/cam0/data');(seq/'right').symlink_to('mav0/cam1/data')
    return seq


def test_input_bytes_membership_and_alias_changes_invalidate_identity(tmp_path):
    seq=fixture(tmp_path);value=identity(tmp_path,'test','seq')
    verify_identity(tmp_path,value)
    image=seq/'left/0.png';before=image.stat();image.write_bytes(b'changed fixture bytes')
    os.utime(image,ns=(before.st_atime_ns,before.st_mtime_ns))
    with pytest.raises(ValueError,match='input bytes'):verify_identity(tmp_path,value)
    value=identity(tmp_path,'test','seq');(seq/'left/new.png').write_bytes(b'new')
    with pytest.raises(ValueError,match='membership'):verify_identity(tmp_path,value)
    (seq/'right').unlink();(seq/'right').symlink_to('mav0/cam0/data')
    with pytest.raises(ValueError,match='alias disagrees'):identity(tmp_path,'test','seq')


def test_snapshot_is_immutable_and_campaign_identity_is_enforced(tmp_path,monkeypatch):
    fixture(tmp_path);run=tmp_path/'results/vo/test/seq/okvis2/run10001';run.mkdir(parents=True)
    value=identity(tmp_path,'test','seq')
    monkeypatch.setenv('VSLAM_EXPECTED_INPUT_SHA256','wrong')
    with pytest.raises(ValueError,match='reviewed campaign'):capture(tmp_path,run)
    monkeypatch.setenv('VSLAM_EXPECTED_INPUT_SHA256',value['sha256'])
    assert capture(tmp_path,run)==value
    with pytest.raises(FileExistsError):capture(tmp_path,run)
    path=run/'provenance/inputs.json'
    meta={'provenance':{'prepared_inputs':{'snapshot':'provenance/inputs.json',
        'snapshot_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'content_sha256':value['sha256'],
        'verified_unchanged_after_execution':True}}}
    (run/'run_meta.json').write_text(json.dumps(meta))
    assert validate_input_capture(run,required=True)==[]
    path.write_text('{}')
    assert validate_input_capture(run,required=True)


def test_missing_camera_manifest_is_a_preparation_error_not_generated_in_runner(tmp_path):
    seq=fixture(tmp_path);path=seq/'mav0/cam0/data.csv';path.unlink()
    with pytest.raises(ValueError,match='missing prepared input'):identity(tmp_path,'test','seq')
    assert not path.exists()
