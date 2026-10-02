"""Physical frame and exclusion tests independent of SLAM outcomes."""
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts/data'))
from prepare_zed_calibration import derive
from _zed_reference import camera_positions, horizontal_lever, retained_intervals, enu_positions


def test_factory_transform_direction_and_axis_conversion():
    sdk=json.loads((ROOT/'docs/campaigns/zed-sdk-calibration-20261002.json').read_text())
    recording=json.loads((ROOT/'datasets/zed2i/field1_110426_full_10fps_q90/manifest.json').read_text())
    d=derive(sdk,recording);t=np.array(d['T_imu_left']);raw=np.array(d['T_left_imu_SDK_IMAGE'])
    q=np.array(d['Q_IMAGE_to_ROS'])
    # Map an arbitrary optical point to ROS IMU, then SDK IMAGE IMU and back.
    point=np.array([.2,-.5,3.,1.])
    np.testing.assert_allclose(raw@np.linalg.inv(q)@t@point,point,atol=1e-14)
    np.testing.assert_allclose(np.linalg.inv(t)@np.array(d['T_imu_right']),
                              [[1,0,0,d['recorded_baseline_m']],[0,1,0,0],[0,0,1,0],[0,0,0,1]],atol=1e-14)
    assert .67<d['residual_rotation_deg']<.68
    # Optical z is forward; the ROS IMU x component must remain positive.
    assert t[0,2]>.999
    assert t[1,3]>.023 and t[0,3]>.002


def test_bad_serial_and_nonrigid_sdk_export_are_rejected():
    sdk=json.loads((ROOT/'docs/campaigns/zed-sdk-calibration-20261002.json').read_text())
    sdk['serial_number']=1
    with pytest.raises(ValueError,match='serial'):derive(sdk,{})
    sdk['serial_number']=30291010;sdk['camera_imu_transform_4x4'][0][0]=2.
    with pytest.raises(ValueError,match='orthonormal'):derive(sdk,{})


def test_geometry_heading_bias_and_height_not_double_counted():
    bias=np.arctan2(.037,1.385)
    b=np.array([[1.385,.037,0.]])
    # Robot physical forward points east. Raw antenna heading includes +bias.
    xyz=camera_positions(np.zeros((1,3)),b)
    np.testing.assert_allclose(xyz[0], [2.855648945,.059990261,-1.],atol=1e-9)
    b2=Rotation.from_euler('z',np.pi/2).apply(b)
    xyz2=camera_positions(np.zeros((1,3)),b2)
    np.testing.assert_allclose(xyz2[0], [-xyz[0,1],xyz[0,0],-1.],atol=1e-12)


def test_height_alone_is_global_translation_for_level_nominal_reference():
    b=np.array([[1.,0,0],[0,1.,0],[-1.,0,0]])
    a=camera_positions(np.zeros((3,3)),b,antenna_above_camera_m=.5)
    c=camera_positions(np.zeros((3,3)),b,antenna_above_camera_m=1.5)
    np.testing.assert_allclose(c-a,np.tile([0,0,-1.],(3,1)),atol=1e-15)


def test_mask_support_splits_even_one_excluded_epoch():
    assert retained_intervals([0,.2,.4,.6,.8],[True,True,False,True,True])==[[0.,.2],[.6,.8]]
    assert retained_intervals([0,.2,4,4.2],[True]*4)==[[0.,.2],[4.,4.2]]
    with pytest.raises(ValueError):retained_intervals([0,.2],[False,False])


def test_geodetic_altitude_and_origin_axes():
    xyz=enu_positions([[0,0,10],[0,0,11],[0,.00001,10]],[0,0,10])
    np.testing.assert_allclose(xyz[0],0)
    np.testing.assert_allclose(xyz[1],[0,0,1],atol=1e-9)
    assert xyz[2,0]>1 and abs(xyz[2,1])<1e-12


def test_diagnostic_parent_reference_requires_exact_pinned_prefix(tmp_path):
    import hashlib
    sys.path.insert(0,str(ROOT/'scripts/eval'))
    from _reference_source import selected_reference
    def put(name,text):
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        return dict(path=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    parent=put('datasets/zed2i/full/times.txt','100\n200\n300\n')
    subset=put('datasets/zed2i/diag/times.txt','100\n200\n')
    trajectory=put('ref.tum','1 0 0 0 0 0 0 1\n')
    support=put('support.json',json.dumps(dict(valid_intervals=[[1,2]])))
    reference=put('ref.json',json.dumps(dict(dataset='zed2i',sequence='full',version='test',
        variants={'primary':dict(trajectory=trajectory,support=support)},limitations=[],
        orientation_valid=False,nominal_geometry={})))
    cfg=dict(schema=1,dataset='zed2i',sequence='diag',diagnostic_parent_sequence='full',
        diagnostic_only=True,subset_times=subset,parent_times=parent,reference=reference,variant='primary')
    selector=tmp_path/'configs/references/zed2i_diag.json'
    put(str(selector.relative_to(tmp_path)),json.dumps(cfg))
    assert selected_reference(tmp_path,'zed2i','diag')['physical_sequence']=='full'
    cfg['subset_times']=put('datasets/zed2i/diag/times.txt','100\n300\n')
    selector.write_text(json.dumps(cfg))
    with pytest.raises(ValueError,match='exact parent prefix'):
        selected_reference(tmp_path,'zed2i','diag')
