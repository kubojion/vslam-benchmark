"""Production OpenVINS input-delivery policy in run_openvins.sh (21 October 2026), without runs."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[3]
RUNNER = REPO / 'scripts/run/run_openvins.sh'
sys.path.insert(0, str(REPO / 'scripts/run'))
import _capture_runtime  # noqa: E402

TEXT = RUNNER.read_text()


def test_validated_delivery_policy_is_the_default_without_environment():
    for line in ('OPENVINS_IMU_RELIABILITY=${OPENVINS_IMU_RELIABILITY:-reliable}',
                 'OPENVINS_END_OF_STREAM_DRAIN=${OPENVINS_END_OF_STREAM_DRAIN:-1}',
                 'OPENVINS_FLOW_CONTROL=${OPENVINS_FLOW_CONTROL:-1}',
                 'OPENVINS_TRANSPORT_PROFILE=${OPENVINS_TRANSPORT_PROFILE:-large_shm}'):
        assert line in TEXT.splitlines(), line
    # The policy reaches both the player and the patched native node.
    for name in ('OPENVINS_IMU_RELIABILITY', 'OPENVINS_END_OF_STREAM_DRAIN', 'OPENVINS_FLOW_CONTROL'):
        assert f'--env {name}="${name}"' in TEXT
    assert 'export OPENVINS_INPUT_RECEIPT=/ws/${OUT_REL}/openvins_input_receipt.json' in TEXT
    assert 'DELIVERY_GATE=exact_receipt_end_drain_flow_control' in TEXT


def test_runner_and_runtime_capture_pin_the_same_validated_image():
    tag = re.search(r'^OPENVINS_IMAGE=(\S+)$', TEXT, re.M).group(1)
    image_id = re.search(r'^OPENVINS_IMAGE_ID=(\S+)$', TEXT, re.M).group(1)
    assert tag == _capture_runtime.OPENVINS_DELIVERY_IMAGE == 'openvins:noise-delivery-audit-20261010-v6'
    assert image_id == _capture_runtime.OPENVINS_DELIVERY_IMAGE_ID
    assert len(re.findall(r'^OPENVINS_IMAGE=', TEXT, re.M)) == 1
    assert '"$(docker image inspect --format \'{{.Id}}\' "$OPENVINS_IMAGE")" == "$OPENVINS_IMAGE_ID"' in TEXT


def test_runtime_identity_records_and_checks_the_delivery_image(tmp_path):
    good = _capture_runtime.identity(tmp_path, 'openvins', inspector=lambda args: {
        'Id': _capture_runtime.OPENVINS_DELIVERY_IMAGE_ID if args[-1].startswith('openvins:noise') else 'sha256:old'})
    assert good['container']['delivery_image']['image_id'] == _capture_runtime.OPENVINS_DELIVERY_IMAGE_ID
    assert not any('delivery' in m for m in good['missing'])
    retagged = _capture_runtime.identity(tmp_path, 'openvins', inspector=lambda args: {'Id': 'sha256:other'})
    assert any(m.startswith('unvalidated_openvins_delivery_image:') for m in retagged['missing'])


def test_native_patch_and_build_record_match_the_validated_sources():
    patch = REPO / 'scripts/patches/openvins-ros2-input-delivery-v6.patch'
    record = json.loads((REPO / 'scripts/patches/openvins-ros2-input-delivery-v6.json').read_text())
    assert record['image_id'] == _capture_runtime.OPENVINS_DELIVERY_IMAGE_ID
    assert record['patch_sha256'] == hashlib.sha256(patch.read_bytes()).hexdigest()
    touched = sorted(re.findall(r'^\+\+\+ b/(\S+)$', patch.read_text(), re.M))
    assert touched == sorted(f['path'] for f in record['patched_sources'])


def test_large_image_transport_profile_is_loopback_only_with_32mib_shm():
    path = REPO / 'configs/ros/openvins-local-large-images.xml'
    assert '/ws/configs/ros/openvins-local-large-images.xml' in TEXT
    ns = {'d': 'http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles'}
    root = ET.parse(path).getroot()
    assert root.find('.//d:interfaceWhiteList/d:address', ns).text == '127.0.0.1'
    assert root.find('.//d:segment_size', ns).text == str(32 * 1024 * 1024)
    assert root.find('.//d:useBuiltinTransports', ns).text == 'false'


def run_with_config_dir(value, tmp_path):
    env = dict(os.environ, OPENVINS_CONFIG_DIR=value, HOME=str(tmp_path))
    env.pop('ROSARIO_VIO_PROFILE', None)
    # A nonexistent sequence stops the runner before any directory, container or
    # result is created, whatever the configuration check decides.
    return subprocess.run(['bash', str(RUNNER), 'zed2i', '__delivery_test_no_such_sequence__', '1', 'vio'],
                          cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60)


def test_config_dir_override_must_resolve_under_configs(tmp_path):
    for value in ('/tmp', 'configs/../scripts', str(tmp_path)):
        result = run_with_config_dir(value, tmp_path)
        assert result.returncode == 2, (value, result.stderr)
        assert 'OPENVINS_CONFIG_DIR must resolve under $WS/configs' in result.stderr, (value, result.stderr)
    missing = run_with_config_dir('configs/openvins/__no_such_profile__', tmp_path)
    assert missing.returncode == 2 and 'OPENVINS_CONFIG_DIR does not exist' in missing.stderr


def test_config_dir_override_inside_configs_is_accepted(tmp_path):
    result = run_with_config_dir('configs/openvins/zed2i', tmp_path)
    assert result.returncode == 2
    assert 'OPENVINS_CONFIG_DIR' not in result.stderr
    assert 'missing' in result.stderr and '__delivery_test_no_such_sequence__' in result.stderr


def test_rosario_camera_chain_uses_opencv_readable_indentation():
    text = (REPO / 'configs/openvins/rosariov2/kalibr_imucam_chain.yaml').read_text()
    assert not re.search(r'^  - \[', text, re.M)
    assert len(re.findall(r'^    - \[', text, re.M)) == 8
    sys.path.insert(0, str(REPO / 'scripts/setup'))
    import yaml
    from prepare_rule_c_20261006 import opencv_dump
    assert '\n  - - ' not in opencv_dump(dict(T=[[1, 0], [0, 1]]))
    assert yaml.safe_load(opencv_dump(dict(T=[[1, 0], [0, 1]]))) == dict(T=[[1, 0], [0, 1]])
