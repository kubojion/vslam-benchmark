#!/usr/bin/env python3
"""Convert reviewed MAC-VO Nx8 poses.npy with evidenced camera timestamps.

EuRoC_NoIMU stores nanoseconds. GeneralStereo stores index*1000 placeholders;
replace those only after verifying both image orders against the camera times.
Never invent a frame rate or attach timestamps to an unknown partial export.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from _metrics import validate_poses


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def convert(sandbox, times_file, loader, *, left=None, right=None, image_format='png'):
    source = Path(sandbox)/'poses.npy'
    poses = np.load(source, allow_pickle=False)
    times_ns = np.loadtxt(times_file, dtype=np.int64, ndmin=1)
    if poses.ndim != 2 or poses.shape != (len(times_ns), 8):
        raise ValueError('native poses.npy must have exactly one Nx8 pose per input camera frame')
    if len(times_ns) < 2 or np.any(np.diff(times_ns) <= 0) or not np.isfinite(poses).all():
        raise ValueError('invalid native pose or input camera timestamps')
    evidence = {'loader': loader, 'native_poses_sha256': digest(source),
                'camera_times_sha256': digest(times_file), 'poses': len(poses),
                'input_camera_frames': len(times_ns), 'orientation_convention_changed': False}
    out = poses.copy()
    if loader == 'EuRoC_NoIMU':
        native_seconds = poses[:, 0]/1e9
        if not np.allclose(native_seconds, times_ns/1e9, atol=1e-6, rtol=0):
            raise ValueError('EuRoC native timestamps do not match the complete camera sequence')
        out[:, 0] = native_seconds
        evidence['timestamp_mapping'] = 'native_nanoseconds_to_seconds'
    elif loader == 'GeneralStereo':
        if not np.array_equal(poses[:, 0], np.arange(len(poses))*1000):
            raise ValueError('GeneralStereo native frame indices are not the complete sequential export')
        image_order = {}
        for name, directory in [('left', left), ('right', right)]:
            if directory is None:
                raise ValueError('GeneralStereo conversion requires both image directories')
            images = sorted(Path(directory).glob(f'*.{image_format}'))
            if len(images) != len(times_ns) or not np.array_equal([int(p.stem) for p in images], times_ns):
                raise ValueError(f'{name} image order/count does not match camera times')
            image_order[name] = hashlib.sha256('\n'.join(p.name for p in images).encode()).hexdigest()
        out[:, 0] = times_ns/1e9
        evidence.update(timestamp_mapping='verified_input_image_order', image_order_sha256=image_order)
    else:
        raise ValueError(f'unreviewed MAC-VO loader {loader!r}')
    validate_poses(out)
    return out, evidence


def select_sandbox(results_root, dataset_config, odometry_config, newer_than):
    import yaml

    class Lenient(yaml.SafeLoader):
        """Only Odometry.name is read; MAC-VO's own !include tags are left unresolved."""
    Lenient.add_multi_constructor('!', lambda loader, suffix, node: None)
    data = yaml.safe_load(Path(dataset_config).read_text())
    odom = yaml.load(Path(odometry_config).read_text(), Loader=Lenient)
    project = odom['Odometry']['name']+'@'+data['name']
    # A freshly created directory alone may contain no poses after an error.
    candidates = [p.parent for p in (Path(results_root)/project).glob('*/poses.npy')
                  if p.stat().st_mtime_ns > Path(newer_than).stat().st_mtime_ns]
    if len(candidates) != 1:
        raise ValueError(f'expected one fresh {project} pose export, found {len(candidates)}')
    return candidates[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('sandbox', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--times-ns', required=True, type=Path)
    ap.add_argument('--loader', required=True, choices=('EuRoC_NoIMU', 'GeneralStereo'))
    ap.add_argument('--left', type=Path)
    ap.add_argument('--right', type=Path)
    ap.add_argument('--image-format', default='png')
    args = ap.parse_args()
    poses, evidence = convert(args.sandbox, args.times_ns, args.loader, left=args.left, right=args.right,
                              image_format=args.image_format)
    temporary = args.output.with_name('.'+args.output.name+'.tmp')
    np.savetxt(temporary, poses, fmt=['%.9f']+['%.9f']*7)
    temporary.replace(args.output)
    evidence['trajectory_sha256'] = digest(args.output)
    args.output.with_name('trajectory_conversion.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(f'wrote {args.output}: {len(poses)} verified camera timestamps')


if __name__ == '__main__':
    main()
