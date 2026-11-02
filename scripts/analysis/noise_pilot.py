#!/usr/bin/env python3
"""Shared helpers of the noise search: artifacts, score, native-parameter checks.

Search copy of the original pilot module, reduced to what the search uses. The pilot's own
controller and its machine lock are gone: this search never opens a results/.locks file.
The coordinator supplies base.machine_slot (a lane check) and base.ART.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
MAIN = Path('/data/imoroz/vslam-benchmark')
ART = None
sys.path[:0] = [str(ROOT/'scripts/eval'), str(ROOT/'scripts/run')]
from _imu_noise_override import KEYS
from _saved_run import evaluate_saved_run
from _reference_source import selected_reference
from _metrics import interpolate_reference, reference_interval_ids


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    tmp.replace(path)


def event(kind, **data):
    record = dict(time=now(), event=kind, **data)
    with (ART/'events.jsonl').open('a') as f:
        f.write(json.dumps(record, allow_nan=False)+'\n')
    print(json.dumps(record, allow_nan=False), flush=True)
    write(ART/'status.json', record)


def verify_main():
    before = json.loads((ART/'main-before.json').read_text())
    changed = [p for p, h in before['sha256'].items() if not (MAIN/p).is_file() or sha(MAIN/p) != h]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=MAIN, text=True).strip()
    report = dict(checked=now(), files=len(before['sha256']), changed=changed,
                  main_head_unchanged=head == before['main_head'])
    # A campaign may pin only the main files it reads (enforce_main_head false):
    # then a reviewed commit elsewhere in main does not invalidate its inputs.
    report['main_head_enforced'] = before.get('enforce_main_head', True) is not False
    write(ART/'main-integrity.json', report)
    if changed or (report['main_head_enforced'] and not report['main_head_unchanged']):
        raise RuntimeError('main changed during experiment; pause to review provenance: '+str(changed))


machine_slot = None  # set by noise_campaign_engine.configure


def reference_distance(dataset, sequence):
    directory = ROOT/'datasets'/dataset/sequence
    selected = selected_reference(ROOT, dataset, sequence)
    gt = np.loadtxt(selected['path'] if selected else directory/'gt_tum.txt', ndmin=2)
    times = np.loadtxt(directory/'times.txt', ndmin=1)/1e9
    intervals = selected['valid_intervals'] if selected else None
    grid, support = interpolate_reference(gt, times, valid_intervals=intervals)
    idx = np.flatnonzero(support)
    usable = np.diff(idx) == 1
    if intervals is not None:
        usable &= np.diff(reference_interval_ids(grid[:, 0], intervals)) == 0
    distance = float(np.linalg.norm(np.diff(grid[:, 1:4], axis=0), axis=1)[usable].sum())
    if not math.isfinite(distance) or distance < 1:
        raise RuntimeError('development clip has insufficient reference motion')
    return distance


def verify_native_parameters(run, spec, params, cfg, returncode):
    """Check native diagnostics where exposed, plus AirSLAM's launched path."""
    algorithm = spec['algorithm']
    if algorithm == 'voxel_svio':
        path = run/'native/parameter_list.txt'
        names = ['sigma_w', 'sigma_a', 'sigma_wb', 'sigma_ab']
        text = path.read_text() if path.exists() else ''
        patterns = [r'^'+n+r':\s*([-+0-9.eE]+)' for n in names]
    elif algorithm == 'orbslam3':
        path = run/'run_log.txt'
        text = path.read_text() if path.exists() else ''
        names = ['Gyro noise', 'Accelerometer noise', 'Gyro walk', 'Accelerometer walk']
        patterns = [re.escape(n)+r':\s*([-+0-9.eE]+)' for n in names]
    else:
        path = run/'processes/odometry.json'
        if path.exists():
            command = json.loads(path.read_text())['command']
            expected = '/benchmark_configs/'+str(cfg.relative_to(ROOT/'configs'))
            if expected not in '\n'.join(command):
                raise RuntimeError('AirSLAM did not launch with the candidate camera config')
        elif returncode == 0:
            raise RuntimeError('AirSLAM native command evidence missing')
        return
    for key, pattern in zip(KEYS, patterns):
        found = re.findall(pattern, text, re.M)
        if not found and returncode == 0:
            raise RuntimeError('native noise diagnostic missing: '+key)
        if found and not math.isclose(float(found[0]), params[key], rel_tol=2e-6):
            raise RuntimeError('native noise disagrees with candidate: '+key)


def score(evaluation, returncode, algo, path_m):
    coverage = evaluation.get('coverage', {})
    span = float(coverage.get('export_span_pct') or 0)/100
    gap = coverage.get('coverage_gap_pct')
    support = span if algo == 'airslam' else min(span, float(gap or 0)/100)
    support = max(0., min(1., support))
    rmse = evaluation.get('ate_se3', {}).get('rmse')
    valid_error = rmse is not None and math.isfinite(rmse) and rmse >= 0
    failed = returncode != 0 or evaluation.get('run_status') != 'ok' or support < .90 or not valid_error
    bounded_error = rmse/(path_m+rmse) if valid_error else 1.
    return dict(failed=bool(failed), loss=10*int(failed)+bounded_error+(1-support),
                ate_se3_rmse_m=rmse if valid_error else None, reference_path_m=path_m,
                export_support_fraction=support, export_span_fraction=span,
                camera_pose_coverage_pct=coverage.get('camera_pose_coverage_pct'),
                scale_factor=evaluation.get('scale_factor'), numerical_status=evaluation.get('run_status'),
                sparse_export=algo == 'airslam', qualification=evaluation.get('qualification'))
