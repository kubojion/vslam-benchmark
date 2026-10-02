"""Read factory camera/IMU geometry from ZED 30291010; no robot required.

Run on a computer with the ZED SDK and its Python API installed:
    python3 export_zed_imu.py
Writes a new zed_30291010_imu.json in the current directory, refusing overwrite.
"""
import json
from pathlib import Path
import pyzed.sl as sl

target = Path('zed_30291010_imu.json')
if target.exists():
    raise SystemExit(f'Refusing to overwrite {target}; preserve or rename it first.')
zed = sl.Camera()
init = sl.InitParameters()
init.set_from_serial_number(30291010)
init.camera_resolution = sl.RESOLUTION.HD1080
init.camera_fps = 15
init.depth_mode = sl.DEPTH_MODE.NONE
init.coordinate_units = sl.UNIT.METER
init.coordinate_system = sl.COORDINATE_SYSTEM.IMAGE
status = zed.open(init)
if status != sl.ERROR_CODE.SUCCESS:
    raise SystemExit(f'Could not open ZED: {status}')
try:
    info = zed.get_camera_information()
    if info.serial_number != 30291010:
        raise RuntimeError(f'Unexpected serial: {info.serial_number}')
    data = {
        'serial_number': int(info.serial_number),
        'sdk_version': str(sl.Camera.get_sdk_version()),
        'coordinate_system': 'IMAGE',
        'translation_units': 'metres',
        'source': 'get_camera_information().sensors_configuration.camera_imu_transform',
        'camera_imu_transform_4x4': info.sensors_configuration.camera_imu_transform.m.tolist(),
        'stereo_transform_rectified_4x4': info.camera_configuration.calibration_parameters.stereo_transform.m.tolist(),
        'stereo_transform_raw_4x4': info.camera_configuration.calibration_parameters_raw.stereo_transform.m.tolist(),
        'camera_firmware': int(info.camera_configuration.firmware_version),
        'sensor_firmware': int(info.sensors_configuration.firmware_version),
    }
    with target.open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
    print(json.dumps(data, indent=2))
    print(f'Saved {target.resolve()}')
finally:
    zed.close()
