"""Clock normalization must preserve measurements and apply the declared sign once."""
import csv
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'run'))
from _basalt_input_clock import prepare


@pytest.mark.parametrize('offset',[4098308,0,-3000000])
def test_offset_applied_once_to_imu_only(tmp_path,offset):
    seq=tmp_path/'sequence'
    for camera in ['cam0','cam1']:
        p=seq/'mav0'/camera;p.mkdir(parents=True)
        (p/'data.csv').write_text('#timestamp,filename\n1000000000,a.png\n1100000000,b.png\n')
    imu=seq/'mav0/imu0';imu.mkdir()
    original='#timestamp,wx,wy,wz,ax,ay,az\n1009000000,1,2,3,4,5,6\n1110000000,7,8,9,10,11,12\n'
    (imu/'data.csv').write_text(original)
    calibration=tmp_path/'calib.json';value={'value0':{'cam_time_offset_ns':offset,'T_imu_cam':['unchanged'],'gyro_noise_std':[1,2,3]}}
    calibration.write_text(json.dumps(value));raw=calibration.read_bytes()
    out=tmp_path/'native';result=prepare(seq,calibration,out)
    rows=list(csv.reader((out/'dataset/mav0/imu0/data.csv').open()))
    assert [int(r[0])for r in rows[1:]]==[1009000000-offset,1110000000-offset]
    assert [r[1:]for r in rows[1:]]==[['1','2','3','4','5','6'],['7','8','9','10','11','12']]
    effective=json.loads((out/'effective-calibration.json').read_text())
    value['value0']['cam_time_offset_ns']=0
    assert effective==value and calibration.read_bytes()==raw
    assert (imu/'data.csv').read_text()==original
    assert (out/'dataset/mav0/cam0/data.csv').read_bytes()==(seq/'mav0/cam0/data.csv').read_bytes()
    assert not result['first_frame_has_prior_imu']
    assert result['last_frame_has_following_imu'] and result['input_rows_removed']==0
    with pytest.raises(FileExistsError):prepare(seq,calibration,out)


@pytest.mark.parametrize('invalid',[0.5,True,'4098308'])
def test_noninteger_offset_is_rejected_before_materialization(tmp_path,invalid):
    calibration=tmp_path/'calib.json';calibration.write_text(json.dumps({'value0':{'cam_time_offset_ns':invalid}}))
    with pytest.raises(ValueError,match='integer number'):
        prepare(tmp_path/'sequence',calibration,tmp_path/'native')
    assert not(tmp_path/'native').exists()
