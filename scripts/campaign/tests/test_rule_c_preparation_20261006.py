"""Source-traced noise and geometry checks; never execute an estimator."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import cv2
import numpy as np
import pytest
import yaml

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'scripts/run'),str(ROOT/'scripts/setup'),str(ROOT/'scripts/data')]
import _imu_noise_rule as rule
from _rosario_rectified import geometry, maps
from prepare_rosario_option_a import shifted
from test_imu_noise_rule_20261005 import orb, okvis, basalt, kalibr_style, cv_yaml


@pytest.mark.parametrize('dataset', ['rosariov2','citrusfarm'])
@pytest.mark.parametrize('algorithm', sorted(rule.load()['authors_euroc']))
def test_each_noise_quantity_traces_to_published_source_and_author_ratio(dataset,algorithm):
    policy=rule.load();entry=policy['dataset_allan'][dataset]
    raw=(ROOT/entry['source']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==entry['sha256']
    source=yaml.safe_load(raw);source=source.get('imu0',source)
    author=policy['authors_euroc'][algorithm]
    for k in policy['keys']:
        factor=1 if author.get('copies_reference') else author[k]/policy['euroc_reference'][k]
        assert rule.noise(algorithm,dataset)[k]==source[k]*factor


@pytest.mark.parametrize('dataset', ['rosariov2','citrusfarm'])
def test_all_static_adapters_and_modes(dataset):
    def check(a,actual):
        assert actual==pytest.approx(rule.noise(a,dataset),rel=1e-12)
    for p in (ROOT/'configs/orbslam3').glob(dataset+'_stereo_inertial*.yaml'):check('orbslam3',orb(p))
    for a in ('okvis2','okvis2x'):
        for p in (ROOT/'configs'/a).glob(dataset+'_*_vio*.yaml'):
            if 'gnss' not in p.name:check(a,okvis(p))
    check('basalt',basalt(ROOT/f'configs/basalt/{dataset}_calib.json'))
    check('openvins',kalibr_style(ROOT/f'configs/openvins/{dataset}/kalibr_imu_chain.yaml'))
    check('airslam',kalibr_style(ROOT/f'configs/airslam/{dataset}_camera_vio.yaml'))
    v=cv_yaml(ROOT/f'configs/voxel_svio/{dataset}.yaml')['imu_parameter']
    check('voxel_svio',{k:v[k] for k in rule.load()['keys']})
    v=json.loads((ROOT/f'configs/sensors/{dataset}.json').read_text())['imu']
    check('cuvslam',{k:v[k] for k in rule.load()['keys']})


def test_horti_policy_identity_is_unchanged_new_sources_are_captured():
    assert rule.record(dataset='hortimulti')==rule.record()
    assert rule.noise('svo_pro','hortimulti')==rule.noise('svo_pro','hortimulti',rule.load(rule.RULE))
    for ds in ('rosariov2','citrusfarm'):
        record=rule.record(dataset=ds)
        assert len(record['files'])==3 and record['sha256']!=rule.record()['sha256']


def test_stereo_geometry_closure_and_pinned_targets():
    g=geometry(ROOT);k=np.array(g['K']);poses=np.array(g['T_imu_cam'])
    assert g == json.loads((ROOT/'configs/sensors/rosario-rectification-20261006.json').read_text())
    assert g['baseline_m']==pytest.approx(0.05024089082502646,abs=1e-14)
    assert g['bf']==pytest.approx(32.599425851220396,abs=1e-11)
    relative=np.linalg.inv(poses[0])@poses[1]
    expected=np.eye(4);expected[0,3]=g['baseline_m']
    np.testing.assert_allclose(relative,expected,atol=2e-13)
    source=yaml.safe_load((ROOT/g['source']).read_text())
    for i in range(2):
        r=np.array(g['R'][i]);np.testing.assert_allclose(r@r.T,np.eye(3),atol=1e-14)
        rotation=np.eye(4);rotation[:3,:3]=r.T
        np.testing.assert_allclose(poses[i],np.linalg.inv(source[f'cam{i}']['T_cam_imu'])@rotation,atol=1e-14)
    assert g['imu_shift_ns']==-4098308
    assert g['right_minus_left_offset_s']==pytest.approx(0.000012583031196191)
    # Independent epipolar check on projected synthetic 3-D points.
    t=np.array(source['cam1']['T_cn_cnm1'])
    for point in ([0.2,0.1,2.],[-0.3,0.25,5.]):
        left=np.array(g['R'][0])@point
        right=np.array(g['R'][1])@(t[:3,:3]@point+t[:3,3])
        uv0=k@left;uv1=k@right
        assert uv0[1]/uv0[2]==pytest.approx(uv1[1]/uv1[2],abs=1e-10)
        assert uv0[0]/uv0[2]-uv1[0]/uv1[2]==pytest.approx(g['bf']/left[2],abs=1e-10)


def test_shift_preserves_values_headers_and_mixed_line_endings():
    raw=b'#timestamp,wx,wy,wz,ax,ay,az\n1703261657043841280,1,2,3,4,5,6\r\n1703261657048833792,7,8,9,0,1,2\r\n'
    got=shifted(raw,-4098308)
    before=raw.splitlines(keepends=True);after=got.splitlines(keepends=True)
    assert before[0]==after[0]
    for a,b in zip(before[1:],after[1:]):
        assert int(b.split(b',')[0])-int(a.split(b',')[0])==-4098308
        assert a.split(b',',1)[1]==b.split(b',',1)[1]
    with pytest.raises(ValueError):shifted(b'2,a\n1,b\n',-1)


def test_orb_matrices_parse_and_do_not_rectify_again():
    g=geometry(ROOT)
    for p in (ROOT/'configs/orbslam3').glob('rosariov2_stereo*.yaml'):
        f=cv2.FileStorage(str(p),cv2.FILE_STORAGE_READ)
        assert f.isOpened() and f.getNode('Camera.type').string()=='Rectified'
        assert f.getNode('Stereo.b').real()==g['baseline_m']
        for i,side in enumerate(('LEFT','RIGHT')):
            np.testing.assert_allclose(f.getNode(side+'.R').mat(),np.eye(3))
            np.testing.assert_allclose(f.getNode(side+'.P').mat(),g['P'][i])
            assert not f.getNode(side+'.D').mat().any()
        f.release()


def test_delivery_log_lag_conversion_and_counts():
    sys.path.insert(0,str(ROOT/'scripts/analysis'))
    from openvins_delivery_audit import audit
    got=audit('[TIME]: 0.0120 seconds total (83.3 hz, 2.50 ms behind)\n',dict(published_left=10,published_right=10))
    assert got['processed_camera_callbacks']==1
    assert got['processed_over_published']==0.1
    assert got['max_native_lag_ms']==25
    assert got['estimator_received_imu'] is None
