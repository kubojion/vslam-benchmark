from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from audit_saved_parameters import mode_checks, parse_snapshot, selected_parameters
from protocol_findings import historical_findings


def test_effective_orb_switch_is_checked_not_ignored_legacy_alias():
    result=mode_checks('orbslam3','vo-lc',
        {'estimator_config':{'System.LoopClosing':1,'loopClosing':0}}, {'use_imu':False})
    assert result[0]['status']=='mismatch'


def test_inertial_data_flag_is_required_and_lc_does_not_imply_final_ba():
    document={'imu_parameters.use':False,'estimator_parameters.do_loop_closures':True,
              'estimator_parameters.do_final_ba':False}
    result=mode_checks('okvis2','vio-lc',{'estimator_config':document},{})
    assert result[0]['status']=='mismatch' and result[1]['status']=='pass'
    assert not any('final_ba' in c['name'] for c in result)
    result=mode_checks('okvis2','vio',{}, {})
    assert all(c['status']=='unverified' for c in result)


def test_opencv_yaml_is_parsed_without_resolving_include_or_accepting_duplicate(tmp_path):
    p=tmp_path/'config.yaml'
    p.write_text('%YAML:1.0\nT: !!opencv-matrix\n  rows: 1\n  cols: 1\n  data: [1]\nData: !include absent.yaml\n')
    result=parse_snapshot(p)
    assert result['T.data']==[1] and result['Data.source_include']=='absent.yaml'
    p.write_text('loopClosing: 0\nloopClosing: 1\n')
    with pytest.raises(ValueError,match='duplicate YAML key'):parse_snapshot(p)
    p.write_text('System.LoopClosing: 0\nSystem.LoopClosing: 0\nloopClosing: 0\n')
    warnings=[]
    assert parse_snapshot(p,warnings)['loopClosing']==0
    assert warnings==['identical_ignored_alias:System.LoopClosing']


def test_online_calibration_is_reported_as_algorithm_setting():
    data={'estimator_config':{'calib_cam_intrinsics':False,'num_pts':200}}
    assert selected_parameters('openvins',data)['estimator_config:calib_cam_intrinsics'] is False


def test_horti_orb_vio_and_lc_use_the_same_sensor_geometry():
    root=Path(__file__).resolve().parents[3]/'configs/orbslam3'
    vio=parse_snapshot(root/'hortimulti_stereo_inertial.yaml')
    lc=parse_snapshot(root/'hortimulti_stereo_inertial_lc.yaml')
    assert vio['IMU.T_b_c1.data']==lc['IMU.T_b_c1.data']
    for key in vio.keys()|lc.keys():
        if key!='loopClosing':assert vio.get(key)==lc.get(key),key
    assert vio['loopClosing']==0 and lc['loopClosing']==1


def test_historical_horti_raw_extrinsic_is_flagged_only_with_matching_snapshot(tmp_path):
    import hashlib
    rel='vio-lc/hortimulti/strawberry02/orbslam3/run1'
    run=tmp_path/'results'/rel;run.mkdir(parents=True)
    path=run/'config.yaml'
    path.write_text('IMU.T_b_c1: !!opencv-matrix\n  rows: 4\n  cols: 4\n  dt: f\n'
        '  data: [.0521232345,-.0073054379,.9986139389,.1219040939,\n'
        '         -.9986040017,-.0089493528,.0520572461,.0366053924,\n'
        '         .0085566474,-.9999332676,-.0077617087,-.0562970105,0,0,0,1]\n')
    artifact={'role':'estimator_config','snapshot':'config.yaml','snapshot_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    meta={'provenance':{'artifacts':[artifact]}}
    assert historical_findings(tmp_path,rel,meta)[0]['code']=='orb_horti_rectified_camera_imu_extrinsic'
    path.write_text(path.read_text().replace('.0521232345','.0309292864'))
    assert historical_findings(tmp_path,rel,meta)==[]
