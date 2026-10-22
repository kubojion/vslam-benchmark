#!/usr/bin/env python3
"""Prepare independent metadata and read-only image links for the noise pilot."""
import hashlib
import json
from pathlib import Path
import re
import shutil

MAIN = Path('/data/imoroz/vslam-benchmark')
ROOT = Path(__file__).resolve().parents[2]
PAIRS = {'rosariov2': ['sequence1', 'sequence5'],
         'citrusfarm': ['seq04', 'seq07'],
         'hortimulti': ['strawberry02', 'strawberry03']}
KEYS = ['gyroscope_noise_density', 'accelerometer_noise_density',
        'gyroscope_random_walk', 'accelerometer_random_walk']
ORB_KEYS = ['IMU.NoiseGyro', 'IMU.NoiseAcc', 'IMU.GyroWalk', 'IMU.AccWalk']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def values(path, algo):
    text = Path(path).read_text()
    out = {}
    for k, actual in zip(KEYS, ORB_KEYS if algo == 'orbslam3' else KEYS):
        found = re.findall(r'^\s*' + re.escape(actual) + r':\s*([-+0-9.eE]+)', text, re.M)
        if len(found) != 1:
            raise ValueError((path, actual, found))
        out[k] = float(found[0])
    return out


def copy_sequence(source, target):
    """Copy small files; link image bytes to resolved originals, never hard-link."""
    def walk(src, dst, parts=()):
        dst.mkdir(parents=True, exist_ok=True)
        for p in src.iterdir():
            rel = parts + (p.name,)
            if not parts and p.name in ('cam0', 'cam1', 'left', 'right'):
                continue
            q = dst / p.name
            if p.is_dir():
                walk(p, q, rel)
            elif len(rel) >= 4 and rel[:3] in [('mav0', 'cam0', 'data'), ('mav0', 'cam1', 'data')]:
                q.symlink_to(p.resolve(strict=True))
            elif p.is_file():
                shutil.copy2(p, q)
    walk(source, target)
    for alias, camera in [('cam0', 'cam0'), ('left', 'cam0'), ('cam1', 'cam1'), ('right', 'cam1')]:
        (target / alias).symlink_to(f'mav0/{camera}/data')


def prefix(parent, target, seconds):
    # Independent files and independent symlinks; unlinking excess links cannot
    # touch the source files. Preserve original integer nanosecond stamps.
    shutil.copytree(parent, target, symlinks=True)
    times = (parent / 'times.txt').read_text().splitlines()
    start = int(times[0])
    selected = [s for s in times if int(s) <= start + seconds * 10**9]
    stamps = set(map(int, selected))
    (target / 'times.txt').write_text('\n'.join(selected) + '\n')
    for cam in ['cam0', 'cam1']:
        csv = target / 'mav0' / cam / 'data.csv'
        rows = csv.read_text().splitlines()
        keep = [s for s in rows if s.startswith('#') or int(s.split(',')[0]) in stamps]
        csv.write_text('\n'.join(keep) + '\n')
        files = {s.split(',')[1].strip() for s in keep if not s.startswith('#')}
        for p in (target / 'mav0' / cam / 'data').iterdir():
            if p.name not in files:
                p.unlink()
        if len(files) != len(selected):
            raise ValueError('stereo CSV and camera clock disagree')
    imu = target / 'mav0/imu0/data.csv'
    rows = imu.read_text().splitlines()
    # Keep the original warm-up head and IMU samples through 20 ms after the
    # last image, to preserve interpolation support without feeding more images.
    keep = [s for s in rows if s.startswith('#') or int(s.split(',')[0]) <= int(selected[-1]) + 20_000_000]
    imu.write_text('\n'.join(keep) + '\n')
    manifest = json.loads((target / 'manifest.json').read_text())
    manifest['experiment_subset'] = {'parent_sequence': parent.name, 'duration_s': seconds,
                                     'input_frames': len(selected), 'kind': 'exact_prefix',
                                     'parent_fields_describe_full_recording': True}
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    descriptor = {'schema': 1, 'diagnostic_only': True, 'parent_sequence': parent.name,
                  'parent_times_sha256': sha(parent / 'times.txt'),
                  'subset_times_sha256': sha(target / 'times.txt')}
    (target / 'experiment-prefix.json').write_text(json.dumps(descriptor, indent=2) + '\n')
    return descriptor


def main():
    if ROOT == MAIN or not (ROOT / '.git').is_file():
        raise RuntimeError('run only from the isolated worktree')
    records = []
    for dataset, sequences in PAIRS.items():
        for seq in sequences:
            parent = ROOT / 'datasets' / dataset / seq
            if (parent/'mav0/cam0/data').exists():
                raise FileExistsError(parent)
            copy_sequence(MAIN / 'datasets' / dataset / seq, parent)
            clip = parent.with_name(seq + '_noise180')
            info = prefix(parent, clip, 180)
            if dataset == 'citrusfarm':
                selector = json.loads((ROOT / f'configs/references/{dataset}_{seq}.json').read_text())
                selector.update(sequence=clip.name, diagnostic_only=True, diagnostic_parent_sequence=seq,
                    parent_times={'path': str((parent / 'times.txt').relative_to(ROOT)), 'sha256': info['parent_times_sha256']},
                    subset_times={'path': str((clip / 'times.txt').relative_to(ROOT)), 'sha256': info['subset_times_sha256']})
                (ROOT / f'configs/references/{dataset}_{clip.name}.json').write_text(json.dumps(selector, indent=2) + '\n')
            records.append({'dataset': dataset, 'sequence': seq, 'clip': clip.name, **info})
            print('Prepared', dataset, seq, flush=True)
    targets = [
        ('orbslam3', 'rosariov2', 'sequence1', 'configs/orbslam3/rosariov2_stereo_inertial.yaml', 'run1'),
        ('airslam', 'citrusfarm', 'seq04', 'configs/airslam/citrusfarm_camera_vio.yaml', 'run10001'),
        ('voxel_svio', 'citrusfarm', 'seq04', 'configs/voxel_svio/citrusfarm.yaml', 'run10001'),
        ('airslam', 'hortimulti', 'strawberry03', 'configs/airslam/hortimulti_camera.yaml', 'run90001'),
    ]
    studies = []
    for algo, ds, seq, cfg, old_run in targets:
        run = MAIN / 'results/vio' / ds / seq / algo / old_run
        meta = json.loads((run / 'run_meta.json').read_text())
        artifact = next(a for a in meta['provenance']['artifacts'] if a['role'] in ('camera_config', 'estimator_config'))
        old = run / artifact['snapshot']
        c, legacy = values(ROOT / cfg, algo), values(old, algo)
        # Same bound rule for every dimension/case. Include both controls and
        # allow below and above them, without searching unbounded inflation.
        bounds = {k: [min(c[k], legacy[k]) / 10, max(c[k] * 100, legacy[k] * 3)] for k in KEYS}
        studies.append(dict(id=f'{algo}_{ds}', algorithm=algo, dataset=ds, target_sequence=seq,
            clips=[s + '_noise180' for s in PAIRS[ds]], config=cfg, rule_c=c, legacy=legacy,
            legacy_label='previous_rounded_calibration' if ds == 'rosariov2' else 'historical_envelope_noise',
            legacy_source=str(old), legacy_sha256=sha(old), bounds=bounds, supports_lc=algo != 'voxel_svio'))
    config = ROOT / 'configs/experiments/noise-search-20261009.json'
    config.parent.mkdir(parents=True, exist_ok=True)
    protocol = dict(schema=1, pilot_only=True, seed=20261009, candidates_per_study=16,
        random_startup_trials=8, sampler='Optuna TPESampler multivariate=True', clips=records,
        repeat_top=2, extra_short_repetitions=2, full_vio='rule_c, legacy, top_two_after_short_repeats',
        full_vio_lc='rule_c and short_selected_winner, where supported', studies=studies,
        selection='Failed clip count first, then mean bounded path-normalized SE3 position error and unsupported export fraction.',
        validation='Full target sequences overlap development prefixes and were previously inspected; exploratory fidelity check, not independent final testing.',
        no_feedback='Full-run results do not feed search or change the short-selected winner.',
        main_root=str(MAIN), worktree=str(ROOT))
    config.write_text(json.dumps(protocol, indent=2) + '\n')
    print(config)


if __name__ == '__main__':
    main()
