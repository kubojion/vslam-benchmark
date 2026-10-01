import json
import os
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'run'))
from _config_preflight import camera_rate, select_orb_config, validate_basalt
from _macvo_to_tum import convert, select_sandbox


def test_sequence_config_precedes_generic_and_rate_is_checked(tmp_path):
    configs = tmp_path/'configs/orbslam3'; configs.mkdir(parents=True)
    ds = tmp_path/'datasets/zed2i/field'; ds.mkdir(parents=True)
    (ds/'times.txt').write_text('0\n66666667\n200000000\n266666667\n400000000\n')
    (configs/'zed2i_stereo_lc.yaml').write_text('Camera.fps: 15\n')
    correct = configs/'zed2i_field.yaml'; correct.write_text('Camera.fps: 10\n')
    assert camera_rate(ds/'times.txt') == 10
    assert select_orb_config(tmp_path, 'zed2i', 'field', 'vo-lc') == correct
    with pytest.raises(ValueError, match='disagrees'):
        select_orb_config(tmp_path, 'zed2i', 'field', 'vo-lc', configs/'zed2i_stereo_lc.yaml')
    with pytest.raises(ValueError, match='no ORB config'):
        select_orb_config(tmp_path, 'zed2i', 'field', 'vo-lc', configs/'missing.yaml')


def test_basalt_gate_must_allow_initial_stereo_triangulation(tmp_path):
    cfg, calib = tmp_path/'vo.json', tmp_path/'calib.json'
    calib.write_text(json.dumps({'value0': {'T_imu_cam': [dict(px=0,py=0,pz=0),dict(px=.0497,py=0,pz=0)]}}))
    values = {'config.vio_min_triangulation_dist': .05, 'config.vio_enforce_realtime': False}
    cfg.write_text(json.dumps({'value0': values}))
    with pytest.raises(ValueError, match='below stereo baseline'):
        validate_basalt(cfg, calib, 'vo')
    # VIO can acquire temporal baseline through inertial propagation.
    validate_basalt(cfg, calib, 'vio')
    values['config.vio_min_triangulation_dist'] = .03
    cfg.write_text(json.dumps({'value0': values}))
    validate_basalt(cfg, calib, 'vo')


def fixture(tmp_path):
    times = np.array([1700000000000000000,1700000000067000000,1700000000200000000], dtype=np.int64)
    p = tmp_path/'times.txt'; np.savetxt(p,times,fmt='%d')
    poses = np.zeros((3,8)); poses[:,7]=1; poses[:,1]=np.arange(3)
    dirs=[]
    for side in ['left','right']:
        d=tmp_path/side;d.mkdir();dirs.append(d)
        for t in times: (d/f'{t}.png').touch()
    return p, poses, dirs


def test_macvo_general_stereo_uses_verified_order_with_irregular_times(tmp_path):
    times, poses, dirs = fixture(tmp_path)
    poses[:,0]=np.arange(3)*1000;np.save(tmp_path/'poses.npy',poses)
    out, evidence=convert(tmp_path,times,'GeneralStereo',left=dirs[0],right=dirs[1])
    np.testing.assert_allclose(out[:,0],np.loadtxt(times)/1e9,atol=0,rtol=0)
    assert evidence['timestamp_mapping']=='verified_input_image_order'
    next(dirs[1].glob('*.png')).unlink()
    with pytest.raises(ValueError,match='right image order/count'):
        convert(tmp_path,times,'GeneralStereo',left=dirs[0],right=dirs[1])


def test_macvo_rejects_partial_or_nonsequential_exports(tmp_path):
    times, poses, dirs=fixture(tmp_path)
    poses[:,0]=[0,1000,3000];np.save(tmp_path/'poses.npy',poses)
    with pytest.raises(ValueError,match='sequential'):
        convert(tmp_path,times,'GeneralStereo',left=dirs[0],right=dirs[1])
    np.save(tmp_path/'poses.npy',poses[:2])
    with pytest.raises(ValueError,match='exactly one'):
        convert(tmp_path,times,'GeneralStereo',left=dirs[0],right=dirs[1])


def test_macvo_preserves_native_euroc_time_and_rejects_shift(tmp_path):
    times, poses, _=fixture(tmp_path)
    poses[:,0]=np.loadtxt(times);np.save(tmp_path/'poses.npy',poses)
    out,_=convert(tmp_path,times,'EuRoC_NoIMU')
    np.testing.assert_allclose(out[:,0],poses[:,0]/1e9,atol=0,rtol=0)
    poses[:,0]+=1e8;np.save(tmp_path/'poses.npy',poses)
    with pytest.raises(ValueError,match='do not match'):
        convert(tmp_path,times,'EuRoC_NoIMU')


def test_macvo_sandbox_requires_unique_fresh_matching_project(tmp_path):
    data=tmp_path/'data.yaml';data.write_text('name: sample\n')
    odom=tmp_path/'odom.yaml';odom.write_text('Odometry:\n  name: model\n')
    os.utime(data,ns=(1,1))
    foreign=tmp_path/'model@other/run1';foreign.mkdir(parents=True);(foreign/'poses.npy').touch()
    with pytest.raises(ValueError,match='found 0'):
        select_sandbox(tmp_path,data,odom,data)
    own=tmp_path/'model@sample/run1';own.mkdir(parents=True);(own/'poses.npy').touch()
    assert select_sandbox(tmp_path,data,odom,data)==own
    own2=tmp_path/'model@sample/run2';own2.mkdir();(own2/'poses.npy').touch()
    with pytest.raises(ValueError,match='found 2'):
        select_sandbox(tmp_path,data,odom,data)
