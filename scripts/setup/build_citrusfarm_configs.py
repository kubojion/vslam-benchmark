#!/usr/bin/env python3
"""Write the CitrusFarm estimator configs from the authors' calibration and the ZED2i templates.

CitrusFarm (Teng et al., ISVC 2023) records the same camera model as our own field data
(ZED2i, factory-rectified 1280x720 colour at 10 Hz), so every estimator setting is taken
from that estimator's ZED2i config and only sensor values are replaced:

  camera     seq04 rectified CameraInfo (seq07 differs by 0.13 px in fx, 0.025 %)
  stereo     baseline from the right projection matrix (0.119885 m; Kalibr on the same
             images: 0.11982 m)
  imu        MicroStrain 3DM-GX5, 200 Hz. T_imu_cam0 = inverse of the authors' Kalibr chain
             MicroStrain -> Blackfly -> ZED left (checked against the ZED IMU's gyro: 0.3 deg)
  clock      the extracted IMU stamps are already on the camera clock (measured offset
             removed at preparation), so every time offset here is 0
  imu noise  one profile for every estimator, as for ZED2i (user decision 2026-10-04): the
             recording-derived densities (scripts/analysis/derive_okvis_imu_noise.py --datasets
             citrusfarm; gyro 0.003, accel 0.05) with the authors' Allan random walks
             (configs/sensors/sources/citrusfarm/microstrain_gx5.yaml). The authors' Allan
             densities (gyro 1.04e-4, accel 2.28e-4) describe the IMU at rest; on this vibrating
             platform the first pilots of OpenVINS, Voxel-SVIO and AirSLAM diverged with them.
             The sensor profile (cuVSLAM, MASt3R-Fusion) is derived from the ORB-SLAM3 file.
  gravity    9.796 m/s^2 (Riverside, CA, 34 deg N, ~300 m)

Outputs are written next to the ZED2i files with `citrusfarm` in place of `zed2i` (and
the ZED2i sequence name replaced by seq04/seq07 where a file is per sequence).
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'configs/sensors/sources/citrusfarm'
ZED_SEQ = 'field1_110426_full_10fps_q90'
SEQUENCES = ('seq04', 'seq07')
GRAVITY = 9.796


def values(envelope):
    info = json.loads((ROOT / 'datasets/citrusfarm/seq04/manifest.json').read_text())['camera_info']
    k, p = info['left']['k'], info['right']['p']
    t_blackfly_imu = np.array(yaml.safe_load((SOURCES / '02-imu-cam-result.yaml').read_text())['cam0']['T_cam_imu'])
    multi = yaml.safe_load((SOURCES / '01-multi-cam-result.yaml').read_text())
    assert multi['cam1']['rostopic'] == '/zed2i/zed_node/left/image_rect_color'
    t_imu_cam0 = np.linalg.inv(np.array(multi['cam1']['T_cn_cnm1']) @ t_blackfly_imu)
    u, _, vt = np.linalg.svd(t_imu_cam0[:3, :3])
    t_imu_cam0[:3, :3] = u @ vt
    baseline = -p[3] / p[0]
    t_cam0_cam1 = np.eye(4)
    t_cam0_cam1[0, 3] = baseline
    allan = yaml.safe_load((SOURCES / 'microstrain_gx5.yaml').read_text())
    # The envelope keeps the authors' random walks; only the densities come from the recording.
    assert (envelope['sigma_gw_c'], envelope['sigma_aw_c']) == (allan['gyroscope_random_walk'], allan['accelerometer_random_walk'])
    return dict(fx=k[0], fy=k[4], cx=k[2], cy=k[5], width=info['left']['width'], height=info['left']['height'],
                baseline=baseline, t_imu_cam0=t_imu_cam0, t_imu_cam1=t_imu_cam0 @ t_cam0_cam1,
                imu=dict(gyro_nd=envelope['sigma_g_c'], acc_nd=envelope['sigma_a_c'],
                         gyro_rw=envelope['sigma_gw_c'], acc_rw=envelope['sigma_aw_c']),
                envelope=envelope, rate=200.0)


def num(x):
    return repr(round(float(x), 12))


def matrix_rows(t, indent):
    return ',\n'.join(indent + ', '.join(num(v) for v in row) for row in t)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print('wrote', path.relative_to(ROOT))


HEADER = ('# CitrusFarm (UCR citrus orchard, Teng et al. ISVC 2023): ZED2i factory-rectified 1280x720\n'
          '# colour at 10 Hz, MicroStrain 3DM-GX5 IMU at 200 Hz on the camera clock. Written by\n'
          '# scripts/setup/build_citrusfarm_configs.py from {template}; only sensor values differ.\n')


def orbslam3(v):
    for suffix, lc, inertial in (('stereo', 0, False), ('stereo_lc', 1, False),
                                 ('stereo_inertial', 0, True), ('stereo_inertial_lc', 1, True)):
        # The current ZED2i files are the sequence-specific ones (zed2i_stereo.yaml is the
        # historical 15 Hz VO profile that is being replaced).
        template = ROOT / 'configs/orbslam3' / (f'zed2i_{ZED_SEQ}_stereo_inertial.yaml' if inertial else f'zed2i_{ZED_SEQ}.yaml')
        text = template.read_text()
        head, sep, body = text.partition('File.version')
        text = '%YAML:1.0\n' + HEADER.format(template=template.relative_to(ROOT)) + '\n' + sep + body
        for key, value in (('Camera1.fx', v['fx']), ('Camera1.fy', v['fy']), ('Camera1.cx', v['cx']), ('Camera1.cy', v['cy']),
                           ('Camera2.fx', v['fx']), ('Camera2.fy', v['fy']), ('Camera2.cx', v['cx']), ('Camera2.cy', v['cy']),
                           ('Camera.width', v['width']), ('Camera.height', v['height']), ('Stereo.b', v['baseline']),
                           ('LEFT.height', v['height']), ('LEFT.width', v['width']),
                           ('RIGHT.height', v['height']), ('RIGHT.width', v['width'])):
            text, n = re.subn(rf'(?m)^({re.escape(key)}:\s*).*$', lambda m: m.group(1) + (str(value) if isinstance(value, int) else num(value)), text)
            assert n == 1 or key.startswith(('LEFT', 'RIGHT')) and n <= 1, (key, n, template)
        k = f"[{num(v['fx'])}, 0.0, {num(v['cx'])},\n         0.0, {num(v['fy'])}, {num(v['cy'])},\n         0.0, 0.0, 1.0]"
        for side, tx in (('LEFT', 0.0), ('RIGHT', -v['fx'] * v['baseline'])):
            p = (f"[{num(v['fx'])}, 0.0, {num(v['cx'])}, {num(tx)},\n         0.0, {num(v['fy'])}, {num(v['cy'])}, 0.0,\n"
                 f"         0.0, 0.0, 1.0, 0.0]")
            text = re.sub(rf'({side}\.K: !!opencv-matrix\n(?:  [^\n]*\n){{3}}  data: )\[[^\]]*\]', lambda m: m.group(1) + k, text)
            text = re.sub(rf'({side}\.P: !!opencv-matrix\n(?:  [^\n]*\n){{3}}  data: )\[[^\]]*\]', lambda m: m.group(1) + p, text)
        # The recipe drops both LC keys and appends one canonical loopClosing; set them anyway
        # so a file read on its own says what its name says.
        text = re.sub(r'(?m)^((?:System\.)?[lL]oopClosing:\s*)\d+', lambda m: m.group(1) + str(lc), text)
        if inertial:
            t = v['t_imu_cam0']
            text = re.sub(r'(IMU\.T_b_c1: !!opencv-matrix\n(?:  [^\n]*\n){3}  data: )\[[^\]]*\]',
                          lambda m: m.group(1) + '[' + matrix_rows(t, '          ').lstrip() + ']', text)
            text = re.sub(r'# IMU\.T_b_c1 = body\(IMU\) <- cam0 optical\.[^\n]*\n(#[^\n]*\n)*',
                          '# IMU.T_b_c1 = MicroStrain <- ZED left optical: inverse of the authors Kalibr chain\n'
                          '# (MicroStrain -> Blackfly 02-imu-cam-result, Blackfly -> ZED left 01-multi-cam-result).\n', text)
            text = re.sub(r'# Common ZED field IMU profile[^\n]*\n', '# CitrusFarm IMU profile (all estimators): recording-derived densities, authors Allan random walks.\n', text)
            a = v['imu']
            for key, value in (('IMU.NoiseGyro', a['gyro_nd']), ('IMU.NoiseAcc', a['acc_nd']),
                               ('IMU.GyroWalk', a['gyro_rw']), ('IMU.AccWalk', a['acc_rw']), ('IMU.Frequency', v['rate'])):
                text, n = re.subn(rf'(?m)^({re.escape(key)}:\s*).*$', lambda m: m.group(1) + num(value), text)
                assert n == 1, key
        if 'System.LoopClosing' not in text:
            text = text.replace('\n#------', f'\nSystem.LoopClosing: {lc}\n\n#------', 1) if inertial else text + f'\nSystem.LoopClosing: {lc}\n'
        write(ROOT / 'configs/orbslam3' / f'citrusfarm_{suffix}.yaml', text)


def basalt(v):
    from scipy.spatial.transform import Rotation
    template = ROOT / 'configs/basalt/zed2i_calib.json'
    calib = json.loads(template.read_text())
    c = calib['value0']
    for i, t in enumerate((v['t_imu_cam0'], v['t_imu_cam1'])):
        q = Rotation.from_matrix(t[:3, :3]).as_quat()
        c['T_imu_cam'][i] = dict(px=float(t[0, 3]), py=float(t[1, 3]), pz=float(t[2, 3]),
                                 qx=float(q[0]), qy=float(q[1]), qz=float(q[2]), qw=float(q[3]))
        c['intrinsics'][i]['intrinsics'] = dict(fx=v['fx'], fy=v['fy'], cx=v['cx'], cy=v['cy'])
        c['resolution'][i] = [v['width'], v['height']]
    e = v['envelope']
    c.update(imu_update_rate=v['rate'], accel_noise_std=[e['sigma_a_c']] * 3, gyro_noise_std=[e['sigma_g_c']] * 3,
             accel_bias_std=[e['sigma_aw_c']] * 3, gyro_bias_std=[e['sigma_gw_c']] * 3, cam_time_offset_ns=0)
    c['_comment'] = ('CitrusFarm ZED2i factory-rectified 1280x720 (seq04 CameraInfo; seq07 within 0.13 px). '
                     'Written by scripts/setup/build_citrusfarm_configs.py from configs/basalt/zed2i_calib.json.')
    c['_comment_extrinsic'] = ('MicroStrain <- ZED left: inverse of the authors Kalibr chain (02-imu-cam-result, '
                               '01-multi-cam-result in configs/sensors/sources/citrusfarm). IMU stamps are on the camera clock.')
    c['_comment_noise'] = ('Recording-derived envelope (derive_okvis_imu_noise.py --datasets citrusfarm) with the authors '
                           'Allan random walks, as for HortiMulti (same MicroStrain 3DM-GX5 model).')
    write(ROOT / 'configs/basalt/citrusfarm_calib.json', json.dumps(calib, indent=4) + '\n')


def okvis(v, algorithm, modes):
    e = v['envelope']
    for seq in SEQUENCES:
        bias = v['sequences'][seq]['gyro_bias_rad_s']
        for mode in modes:
            template = ROOT / f'configs/{algorithm}' / f'zed2i_{ZED_SEQ}_{mode}.yaml'
            text = template.read_text()
            body = text[text.index('\ncameras:'):]
            note = ('# OKVIS2 ' if algorithm == 'okvis2' else '# OKVIS2-X ') + f'{mode.upper().replace("_", "-")} configuration for CitrusFarm {seq}.\n'
            text = '%YAML:1.0\n' + note + HEADER.format(template=template.relative_to(ROOT)) + \
                   '# T_SC maps the rectified optical cameras into the MicroStrain frame (inverse Kalibr chain).\n' + body
            blocks = [',\n'.join(('        [' if i == 0 else '          ') + ', '.join(num(x) for x in r)
                                 for i, r in enumerate(t)) + ']' for t in (v['t_imu_cam0'], v['t_imu_cam1'])]
            text, n = re.subn(r'\{T_SC:\n        \[[^\]]*\]', lambda m: '{T_SC:\n' + blocks.pop(0), text)
            assert n == 2 and not blocks, (template, 'T_SC')
            for key, value in (('image_dimension', f"[{v['width']}, {v['height']}]"),
                               ('focal_length', f"[{num(v['fx'])}, {num(v['fy'])}]"),
                               ('principal_point', f"[{num(v['cx'])}, {num(v['cy'])}]")):
                text, n = re.subn(rf'({key}: )\[[^\]]*\]', lambda m: m.group(1) + value, text)
                assert n == 2, (template, key)
            for key, value, comment in (('sigma_g_c', e['sigma_g_c'], 'recording-derived gyro envelope'),
                                        ('sigma_a_c', e['sigma_a_c'], 'recording-derived accel envelope'),
                                        ('sigma_gw_c', e['sigma_gw_c'], 'authors Allan gyro bias random walk'),
                                        ('sigma_aw_c', e['sigma_aw_c'], 'authors Allan accel bias random walk'),
                                        ('g', GRAVITY, 'Riverside, CA (~34 deg N)')):
                text, n = re.subn(rf'(?m)^(\s*{key}:\s*)[^\n#]*(#[^\n]*)?$',
                                  lambda m: f'{m.group(1)}{num(value)}  # {comment}', text, count=1)
                assert n == 1, (template, key)
            text, n = re.subn(r'(?m)^(\s*g0:\s*)\[[^\]]*\]', lambda m: m.group(1) + '[' + ', '.join(num(b) for b in bias) + ']'
                              + f'  # stationary gyro bias at the start of {seq}', text, count=1)
            assert n == 1, (template, 'g0')
            text, n = re.subn(r'(?m)^(\s*image_delay:\s*)[^\n]*$', lambda m: m.group(1) + '0.0  # IMU stamps on the camera clock', text)
            assert n == 1, (template, 'image_delay')
            text = re.sub(r'# IMU noise model:[^\n]*\n(#[^\n]*\n)*',
                          '# IMU: MicroStrain 3DM-GX5. Recording-derived densities, Allan random walks (HortiMulti policy).\n', text)
            write(ROOT / f'configs/{algorithm}' / f'citrusfarm_{seq}_{mode}.yaml', text)


def replace_keys(text, pairs, template, count=1):
    for key, value in pairs:
        # The whole rest of the line is replaced: a template comment describes the template's value.
        text, n = re.subn(rf'(?m)^(\s*{re.escape(key)}:\s*)[^\n]*', lambda m: m.group(1) + str(value), text)
        assert n == count, (template, key, n)
    return text


def opencv_rows(t, indent='  '):
    return '\n'.join(f'{indent}- [' + ', '.join(num(x) for x in r) + ']' for r in t)


def airslam(v):
    a = v['imu']
    for mode in ('vio', 'vo', 'vo_lc', 'mr'):
        template = ROOT / 'configs/airslam' / f'zed2i_{mode}.yaml'
        text = template.read_text()
        text = re.sub(r'(?s)\A(#[^\n]*\n)+', '# AirSLAM ' + mode.upper().replace('_', '-') + ' config for CitrusFarm.\n'
                      + HEADER.format(template=template.relative_to(ROOT))
                      + '# Image size 1280x720 and a dataset-named TensorRT engine; all other settings unchanged.\n', text)
        text = replace_keys(text, (('image_width', v['width']), ('image_height', v['height']),
                                   ('engine_file', '"superpoint_lightglue_citrusfarm.engine"')), template)
        write(ROOT / 'configs/airslam' / f'citrusfarm_{mode}.yaml', text)
    for mode, inertial in (('vio', True), ('vo', False)):
        template = ROOT / 'configs/airslam' / f'zed2i_camera_{mode}.yaml'
        text = template.read_text()
        intro = ('# T_type 0 (src/airslam/src/camera.cc): T is T_bc, the camera pose in the IMU body frame;\n'
                 '# here the inverse of the authors Kalibr chain MicroStrain -> Blackfly -> ZED left.\n'
                 '# IMU noise: CitrusFarm profile (recording-derived densities, authors Allan random walks).\n') if inertial else \
                ('# VO mode (use_imu: 0): body = cam0; cam1 is the right camera at +baseline. AirSLAM uses only\n'
                 '# |x| of the cam0-cam1 offset as the stereo baseline.\n')
        text = re.sub(r'(?s)\A%YAML:1.0\n(#[^\n]*\n|\s*\n)+', '%YAML:1.0\n# AirSLAM camera file (' + mode.upper()
                      + ') for CitrusFarm.\n' + HEADER.format(template=template.relative_to(ROOT)) + intro + '\n', text)
        text = replace_keys(text, (('image_height', v['height']), ('image_width', v['width'])), template)
        intr = f"[{num(v['fx'])}, {num(v['fy'])}, {num(v['cx'])}, {num(v['cy'])}]  # fx fy cx cy"
        text, n = re.subn(r'(?m)^(  intrinsics: )\[[^\]]*\][^\n]*', lambda m: m.group(1) + intr, text)
        assert n == 2, (template, 'intrinsics')
        if inertial:
            poses = [v['t_imu_cam0'], v['t_imu_cam1']]
        else:
            right = np.eye(4)
            right[0, 3] = v['baseline']
            poses = [np.eye(4), right]
        text, n = re.subn(r'(?m)^(  T:\n)((?:  - \[[^\n]*\]\n){4})', lambda m: m.group(1) + opencv_rows(poses.pop(0)) + '\n', text)
        assert n == 2 and not poses, (template, 'T')
        if inertial:
            text = re.sub(r'#\s*Common ZED field IMU profile[^\n]*\n', '', text)
            text = replace_keys(text, (('rate_hz', int(v['rate'])), ('gyroscope_noise_density', num(a['gyro_nd'])),
                                       ('gyroscope_random_walk', num(a['gyro_rw'])),
                                       ('accelerometer_noise_density', num(a['acc_nd'])),
                                       ('accelerometer_random_walk', num(a['acc_rw'])),
                                       ('g_value', f'{GRAVITY}  # Riverside, CA (~34 deg N)')), template)
        write(ROOT / 'configs/airslam' / f'citrusfarm_camera_{mode}.yaml', text)


def ov2slam(v):
    for mode in ('vo', 'vo_lc'):
        template = ROOT / 'configs/ov2slam' / f'zed2i_{mode}.yaml'
        text = template.read_text()
        text = re.sub(r'(?m)^# OV2SLAM stereo [^\n]*$', f'# OV2SLAM stereo {mode.upper().replace("_", "-")} on pre-rectified '
                      'CitrusFarm ZED2i 1280x720 images.\n' + HEADER.format(template=template.relative_to(ROOT)).rstrip('\n'), text)
        pairs = [(f'Camera.{k}', v[w]) for k, w in (('left_nwidth', 'width'), ('left_nheight', 'height'),
                                                     ('right_nwidth', 'width'), ('right_nheight', 'height'))]
        pairs += [(f'Camera.{k}{side}', num(v[k])) for side in 'lr' for k in ('fx', 'fy', 'cx', 'cy')]
        text = replace_keys(text, pairs, template)
        text, n = re.subn(r'(body_T_cam1: !!opencv-matrix\n(?:  [^\n]*\n){3}  data: \[1\.0, 0\.0, 0\.0, )[0-9.e+-]+',
                          lambda m: m.group(1) + num(v['baseline']), text)
        assert n == 1, (template, 'body_T_cam1')
        write(ROOT / 'configs/ov2slam' / f'citrusfarm_{mode}.yaml', text)


def voxel_svio(v):
    template = ROOT / 'configs/voxel_svio/zed2i.yaml'
    text = template.read_text()
    a = v['imu']
    text = replace_keys(text, (('gravity_mag', f'{GRAVITY}           # Riverside, CA (~34 deg N)'),
                               ('accelerometer_noise_density', num(a['acc_nd'])),
                               ('accelerometer_random_walk', num(a['acc_rw'])),
                               ('gyroscope_noise_density', num(a['gyro_nd'])),
                               ('gyroscope_random_walk', num(a['gyro_rw'])),
                               ('intrinsics_left', f"[{num(v['fx'])}, {num(v['fy'])}, {num(v['cx'])}, {num(v['cy'])}]"),
                               ('intrinsics_right', f"[{num(v['fx'])}, {num(v['fy'])}, {num(v['cx'])}, {num(v['cy'])}]"),
                               ('resolution_left', f"[{v['width']}, {v['height']}]"),
                               ('resolution_right', f"[{v['width']}, {v['height']}]"),
                               ('timeshift_cam_imu_left', '0.0'), ('timeshift_cam_imu_right', '0.0')), template)
    for side, t in (('left', v['t_imu_cam0']), ('right', v['t_imu_cam1'])):
        pad = ' ' * len(f'    T_imu_cam_{side}: [') + (' ' if side == 'left' else '')
        flat = (',\n' + pad).join(', '.join(num(x) for x in r) for r in t)
        text, n = re.subn(rf'(    T_imu_cam_{side}: +\[)[^\]]*\]', lambda m: m.group(1) + flat + ']', text)
        assert n == 1, (template, side)
    text, n = re.subn(r'(?m)^# ZED2i field1 IMU\.[^\n]*\n(#[^\n]*\n)*',
                      '# MicroStrain 3DM-GX5 (CitrusFarm profile): recording-derived densities, authors Allan random walks.\n', text)
    assert n == 1, (template, 'imu comment')
    text, n = re.subn(r'(?m)^# ZED2i rectified optical cameras\.[^\n]*\n(#[^\n]*\n)*',
                      '# ZED2i factory-rectified cameras; T_imu_cam = inverse of the authors Kalibr chain\n'
                      '# MicroStrain -> Blackfly -> ZED left. IMU stamps are on the camera clock.\n', text)
    assert n == 1, (template, 'camera comment')
    text = HEADER.format(template=template.relative_to(ROOT)) + text
    write(ROOT / 'configs/voxel_svio/citrusfarm.yaml', text)


def openvins(v):
    a = v['imu']
    src = ROOT / 'configs/openvins/zed2i'
    text = (src / 'estimator_config.yaml').read_text()
    text = replace_keys(text, (('gravity_mag', GRAVITY),), src / 'estimator_config.yaml')
    text = text.replace('gravity_mag: 9.812           Poznan, Poland (~52.29N) - ZED2i field dataset.',
                        f'gravity_mag: {GRAVITY}           Riverside, CA (~34N) - CitrusFarm.')
    write(ROOT / 'configs/openvins/citrusfarm/estimator_config.yaml',
          text.replace('%YAML:1.0\n', '%YAML:1.0\n' + HEADER.format(template='configs/openvins/zed2i/estimator_config.yaml'), 1))
    imu = (src / 'kalibr_imu_chain.yaml').read_text()
    imu = replace_keys(imu, (('accelerometer_noise_density', num(a['acc_nd'])), ('accelerometer_random_walk', num(a['acc_rw'])),
                             ('gyroscope_noise_density', num(a['gyro_nd'])), ('gyroscope_random_walk', num(a['gyro_rw'])),
                             ('update_rate', v['rate']), ('time_offset', '0.0')), src / 'kalibr_imu_chain.yaml')
    imu = re.sub(r'(?s)\A%YAML:1.0\n(#[^\n]*\n)*', '%YAML:1.0\n' + HEADER.format(template='configs/openvins/zed2i/kalibr_imu_chain.yaml')
                 + '# MicroStrain 3DM-GX5, CitrusFarm profile (recording-derived densities, authors Allan random walks);\n'
                 + '# stamps on the camera clock.\n', imu)
    write(ROOT / 'configs/openvins/citrusfarm/kalibr_imu_chain.yaml', imu)
    cam = (src / 'kalibr_imucam_chain.yaml').read_text()
    poses = [v['t_imu_cam0'], v['t_imu_cam1']]
    cam, n = re.subn(r'(  T_imu_cam:\n)((?:    - \[[^\n]*\]\n){4})', lambda m: m.group(1) + opencv_rows(poses.pop(0), '    ') + '\n', cam)
    assert n == 2 and not poses, 'openvins T_imu_cam'
    cam = replace_keys(cam, (('intrinsics', f"[{num(v['fx'])}, {num(v['fy'])}, {num(v['cx'])}, {num(v['cy'])}]"),
                             ('resolution', f"[{v['width']}, {v['height']}]")), src / 'kalibr_imucam_chain.yaml', count=2)
    cam = re.sub(r'(?s)\A%YAML:1.0\n(#[^\n]*\n)*', '%YAML:1.0\n' + HEADER.format(template='configs/openvins/zed2i/kalibr_imucam_chain.yaml')
                 + '# T_imu_cam = (R_CtoI | p_CinI): inverse of the authors Kalibr chain MicroStrain -> Blackfly -> ZED left.\n', cam)
    write(ROOT / 'configs/openvins/citrusfarm/kalibr_imucam_chain.yaml', cam)


def dpvo(v):
    write(ROOT / 'configs/dpvo/citrusfarm.txt', '# DPVO calib for CitrusFarm (rectified ZED2i cam0, monocular; no distortion).\n'
          f"{num(v['fx'])} {num(v['fy'])} {num(v['cx'])} {num(v['cy'])}\n")


def macvo(v):
    for seq in SEQUENCES:
        write(ROOT / 'configs/macvo' / f'citrusfarm_{seq}.yaml',
              f'# MAC-VO sequence config for CitrusFarm {seq} (ZED2i factory-rectified 1280x720 colour PNG).\n'
              '# Written by scripts/setup/build_citrusfarm_configs.py.\n'
              f'type: GeneralStereo\nname: citrusfarm_{seq}\nargs:\n  root: __WS__/datasets/citrusfarm/{seq}\n'
              f"  bl: {num(v['baseline'])}\n  format: png\n  camera:\n    fx: {num(v['fx'])}\n    fy: {num(v['fy'])}\n"
              f"    cx: {num(v['cx'])}\n    cy: {num(v['cy'])}\n")


def physical_record(v):
    """Reviewed physical calibration the evaluator uses for inertial outputs (_pose_frames.py)."""
    import hashlib
    def evidence(path):
        return dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    checks = {}
    for seq in SEQUENCES:
        manifest = json.loads((ROOT / 'datasets/citrusfarm' / seq / 'manifest.json').read_text())['imu']
        checks[seq] = dict(camera_clock_shift_s=manifest['camera_clock_shift_s'],
                           measurement='MicroStrain vs ZED IMU gyro cross-correlation and rotation fit '
                                       '(scripts/data/citrusfarm_imu_alignment.py)')
    for seq, values in v.get('alignment', {}).get('sequences', {}).items():
        checks[seq].update(values)
    record = dict(
        schema=1, dataset='citrusfarm', sequences=list(SEQUENCES),
        T_imu_left=v['t_imu_cam0'].round(12).tolist(),
        frames='T_imu_left maps ZED left rectified optical coordinates into the MicroStrain 3DM-GX5 frame',
        source="inverse of the authors' Kalibr chain: 02-imu-cam-result (MicroStrain -> Blackfly) and "
               '01-multi-cam-result cam1 (Blackfly -> rectified ZED left)',
        independent_checks=checks,
        evidence=[evidence(SOURCES / name) for name in ('01-multi-cam-result.yaml', '02-imu-cam-result.yaml', 'index.json')])
    write(ROOT / 'docs/campaigns/citrusfarm-physical-calibration-20261003.json', json.dumps(record, indent=1) + '\n')


WRITERS = dict(orbslam3=orbslam3, basalt=basalt, airslam=airslam, ov2slam=ov2slam, voxel_svio=voxel_svio,
               openvins=openvins, dpvo=dpvo, macvo=macvo, physical_record=physical_record,
               okvis2=lambda v: okvis(v, 'okvis2', ('vio', 'vo', 'vo_lc')),
               okvis2x=lambda v: okvis(v, 'okvis2x', ('vio', 'vio_lc', 'vo', 'vo_lc')))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--envelope', type=Path, required=True,
                    help='JSON from derive_okvis_imu_noise.py --datasets citrusfarm')
    ap.add_argument('--alignment', type=Path,
                    help='JSON with the per-sequence alignment results to quote in the physical calibration record')
    ap.add_argument('--only', nargs='+', choices=sorted(WRITERS), default=sorted(WRITERS))
    args = ap.parse_args()
    report = json.loads(args.envelope.read_text())
    envelope = report['datasets']['citrusfarm']['recommended']
    v = values(envelope)
    v['sequences'] = report['datasets']['citrusfarm']['sequences']
    if args.alignment:
        v['alignment'] = json.loads(args.alignment.read_text())
    for name in args.only:
        WRITERS[name](v)


if __name__ == '__main__':
    main()
