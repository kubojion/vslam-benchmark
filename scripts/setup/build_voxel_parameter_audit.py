#!/usr/bin/env python3
"""Build an isolated Voxel executable with parameter/input reporting only.

Run inside the existing voxel_svio container. Reuse unchanged objects from the
destructor-repaired build, preserving its executable, source and build directory.
"""
import hashlib
import argparse
import json
from pathlib import Path
import shlex
import subprocess

OLD = Path('/root/catkin_ws_shutdown_20261002')
NEW = Path('/root/vslam_voxel_audit_20261002_v2')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('unexpected native source: ' + old[:80])
    return text.replace(old, new)


def build():
    NEW.mkdir(exist_ok=False)
    build_dir = OLD / 'build/voxel_svio'
    target = build_dir / 'CMakeFiles/vio_node.dir'
    flags_path = target / 'flags.make'
    flags = dict(line.split(' = ', 1) for line in flags_path.read_text().splitlines() if ' = ' in line)
    common = sum((shlex.split(flags[name]) for name in ('CXX_DEFINES', 'CXX_INCLUDES', 'CXX_FLAGS')), [])
    # GCC 9's Boost macro diagnostic tracking crashed in the preserved first
    # build attempt. Disable only macro-expansion diagnostic bookkeeping.
    common.append('-ftrack-macro-expansion=0')
    original = OLD / 'src/voxel_svio/src'
    stereo = (original / 'stereoVio.cpp').read_text()
    stereo = replace_once(stereo, '#include "stereoVio.h"', '''#include "stereoVio.h"
#include <iomanip>
static unsigned long audit_imu = 0, audit_stereo = 0, audit_queued = 0;
static double audit_first_imu = 0, audit_last_imu = 0;
static double audit_first_camera = 0, audit_last_camera = 0;
static int audit_width = 0, audit_height = 0, audit_type = -1;
''')
    stereo = replace_once(stereo, '    // odometry_options.recordParameters();', '    odometry_options.recordParameters();')
    stereo = replace_once(stereo, '    processImu(imu_data);', '''    if (audit_imu++ == 0) audit_first_imu = imu_data.timestamp;
    audit_last_imu = imu_data.timestamp;
    processImu(imu_data);''')
    stereo = replace_once(stereo, '    double timestamp = msg_0->header.stamp.toSec();', '''    double timestamp = msg_0->header.stamp.toSec();
    if (audit_stereo++ == 0) audit_first_camera = timestamp;
    audit_last_camera = timestamp;''')
    stereo = replace_once(stereo, '    camera_buffer.push(camera_data);', '''    ++audit_queued;
    audit_width = cv_ptr_0->image.cols;
    audit_height = cv_ptr_0->image.rows;
    audit_type = cv_ptr_0->image.type();
    camera_buffer.push(camera_data);''')
    stereo = replace_once(stereo, '    Eigen::Matrix4d T_imu_cam_right = mat44FromArray(v_T_imu_cam_right);', '''    Eigen::Matrix4d T_imu_cam_right = mat44FromArray(v_T_imu_cam_right);
    {
        std::ofstream audit(output_path + "/camera_load.txt");
        audit << std::scientific << std::setprecision(17);
        audit << "left_time_offset " << calib_camimu_dt_left << "\\n";
        audit << "right_time_offset " << calib_camimu_dt_right << "\\n";
        audit << "common_stereo_uses_left_time_offset 1\\n";
        audit << "T_imu_cam_left\\n" << T_imu_cam_left << "\\n";
        audit << "T_imu_cam_right\\n" << T_imu_cam_right << "\\n";
    }''')
    ending = '''    return 0;
}'''
    pos = stereo.rfind(ending)
    if pos < stereo.index('int main('):
        raise ValueError('cannot locate native shutdown')
    dump = r'''    {
        std::ofstream audit(output_path + "/input_receipt.json");
        audit << std::setprecision(17)
              << "{\"imu_received\":" << audit_imu
              << ",\"stereo_received\":" << audit_stereo
              << ",\"stereo_queued_after_rate_gate\":" << audit_queued
              << ",\"first_imu_s\":" << audit_first_imu
              << ",\"last_imu_s\":" << audit_last_imu
              << ",\"first_camera_s\":" << audit_first_camera
              << ",\"last_camera_s\":" << audit_last_camera
              << ",\"image_width\":" << audit_width
              << ",\"image_height\":" << audit_height
              << ",\"opencv_type\":" << audit_type << "}\n";
    }
'''
    stereo = stereo[:pos] + dump + stereo[pos:]
    parameters = '#include <iomanip>\n' + (original / 'parameters.cpp').read_text()
    parameters = parameters.replace('std::fixed', 'std::scientific << std::setprecision(17)')
    commands = []
    for name, content in [('stereoVio.cpp', stereo), ('parameters.cpp', parameters)]:
        path = NEW / name
        path.write_text(content)
        command = ['/usr/bin/c++', *common, '-c', str(path), '-o', str(NEW / (name + '.o'))]
        commands.append(command)
        subprocess.run(command, cwd=build_dir, check=True)
    link = shlex.split((target / 'link.txt').read_text())
    inputs = []
    for index, arg in enumerate(link):
        if arg.endswith('.o'):
            old = build_dir / arg
            inputs.append({'path': str(old), 'sha256': digest(old)})
            if old.name in ('stereoVio.cpp.o', 'parameters.cpp.o'):
                link[index] = str(NEW / old.name)
    link[link.index('-o') + 1] = str(NEW / 'vio_node')
    commands.append(link)
    subprocess.run(link, cwd=build_dir, check=True)
    record = dict(schema=1, scope='parameter and input reporting only; no estimator policy change',
                  old_prefix=str(OLD), new_executable=str(NEW / 'vio_node'), commands=commands,
                  original_objects=inputs, flags_sha256=digest(flags_path),
                  source=[{'path': str(p), 'sha256': digest(p)} for p in [original / 'stereoVio.cpp',
                          original / 'parameters.cpp', OLD / 'src/voxel_svio/include/stereoVio.h']],
                  outputs=[{'path': str(p), 'sha256': digest(p)} for p in [NEW / 'stereoVio.cpp',
                           NEW / 'parameters.cpp', NEW / 'vio_node']])
    (NEW / 'build-recipe.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record['outputs'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=NEW)
    args = parser.parse_args()
    if args.output.parent != Path('/root') or not args.output.name.startswith('vslam_voxel_audit_'):
        parser.error('expected a fresh /root/vslam_voxel_audit_* directory')
    NEW = args.output
    build()
