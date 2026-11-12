#!/usr/bin/env python3
"""Write the user's decision of 12 Nov 2026 (option b): six receipt differences that cannot act on the estimate.

Writes configs/campaigns/rule-c-nonacting-differences-20261112.json. The cells, fields and reasons are the user's
decision (PROGRESS/IMU-TIMING-TUNE/PROMOTION-RULEC.md section 6); every per-run value, commit and setting is read from
the saved run receipts, never typed. A decision with reasons, not a paper disclosure.
Run with the repository's results/ visible (read-only is enough).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_repair_inventory as inventory  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
Z = 'zed2i/field1_110426_full_10fps_q90'
IMU_FIELDS = ('gyroscope_noise_density', 'accelerometer_noise_density', 'gyroscope_random_walk', 'accelerometer_random_walk')
CUVSLAM = dict(kind='artifact', role='camera_calibration', path='configs/sensors/zed2i.json', changed_by_commit='cc897ec',
               reason='Only the four IMU noise values of the shared Sielinko sensor file changed (commit cc897ec, 21 Oct 2026, '
                      'Rule C for Sielinko). These runs are VO / VO-LC with use_imu=false; the recorded effective cuVSLAM '
                      'configuration is byte-identical across the three runs, so the values never reach the estimator.')
OPENVINS = [dict(kind='artifact', role=role, reason=(
                'A receipt written after the run by the delivery check (scripts/run/run_openvins.sh: '
                'openvins_delivery_audit.json, or openvins_native_outcome.json after a native exit). It records observed '
                'delivery counts, the estimated final camera-IMU offset, output message counts and the log hash: '
                'outcomes, not settings. Estimator configuration, calibrations, transport profile, image mounts and the '
                'commit are identical across the runs.')) for role in ('delivery_audit', 'native_outcome')]
DPVO = dict(kind='parameter', name='buffer_size', changed_by_commit='50ee4ed',
            reason='DPVO keyframe buffer capacity, raised from 8192 to 16384 for CitrusFarm (scripts/run/run_dpvo.sh, commit '
                   '50ee4ed, 5 Oct 2026). It only sizes the keyframe arrays and raises an exception on overflow '
                   '(src/DPVO/dpvo/dpvo.py: "The buffer size is too small"); the 8192 run finished with 100 % span, so the '
                   'limit was never reached.')
DECIDED = {
    f'vo/{Z}/cuvslam': [CUVSLAM],
    f'vo-lc/{Z}/cuvslam': [CUVSLAM],
    'vio/rosariov2/sequence1/openvins': OPENVINS,
    'vio/rosariov2/sequence5/openvins': OPENVINS,
    f'vio/{Z}/openvins': OPENVINS,
    'vo/citrusfarm/seq04/dpvo': [DPVO],
}


def receipts(key, run_id):
    run = REPO/'results'/key/f'run{run_id}'; meta = inventory.read(run/'run_meta.json')
    payload = inventory.cohort_identity(meta, key.split('/')[3], run_dir=run)[1]
    return run, meta, payload


def imu_values(path):
    found = {}
    def walk(value):
        if isinstance(value, dict):
            for k, v in value.items():
                if k in IMU_FIELDS: found[k] = v
                else: walk(v)
    walk(json.loads(path.read_text()))
    return found


def main():
    selection = json.loads((REPO/inventory.PAPER_COMPLETION_SELECTION).read_text())['cells']
    cells = {}
    for key, differences in DECIDED.items():
        runs = selection[key]; entries = []
        evidence = {}
        for run_id in runs:
            run, meta, payload = receipts(key, run_id)
            evidence[str(run_id)] = dict(
                workspace_commit=((meta.get('provenance') or {}).get('workspace') or {}).get('commit'),
                other_artifacts={a['role']: a['sha256'] for a in payload['artifacts']
                                 if a['role'] not in {d.get('role') for d in differences}})
        for d in differences:
            entry = dict(d, per_run={})
            for run_id in runs:
                run, meta, payload = receipts(key, run_id)
                if d['kind'] == 'artifact':
                    found = [a['sha256'] for a in payload['artifacts'] if a['role'] == d['role']]
                    entry['per_run'][str(run_id)] = found[0] if found else None
                    if d['role'] == 'camera_calibration':
                        art = next(a for a in meta['provenance']['artifacts'] if a['role'] == 'camera_calibration')
                        entry.setdefault('values', {})[str(run_id)] = imu_values(run/art['snapshot'])
                else:
                    entry['per_run'][str(run_id)] = payload['parameters'].get(d['name'])
            values = set(json.dumps(v) for v in entry['per_run'].values())
            if values == {'null'}:
                continue  # this receipt does not exist in this cell
            if len(values) < 2:
                raise SystemExit(f'{key}: {d.get("role") or d.get("name")} does not differ; not a difference to declare')
            entries.append(entry)
        # Only the declared fields may differ; anything else would still refuse pooling.
        others = {json.dumps(e['other_artifacts'], sort_keys=True) for e in evidence.values()}
        if len(others) != 1:
            raise SystemExit(f'{key}: other artifacts differ too: {evidence}')
        cells[key] = dict(runs=runs, differences=entries, run_evidence=evidence)
    record = dict(schema=1,
                  decided='User, 12 Nov 2026 (option b): these receipt differences cannot act on the estimate; each '
                          'cell is one setup. Relayed by the engineer session.',
                  note='Decision with reasons, not a paper disclosure. Applies only to the listed cells with exactly '
                       'these runs and per-run values (build_repair_inventory.pooled_cohort).',
                  generated_by='scripts/campaign/make_nonacting_record.py',
                  source='PROGRESS/IMU-TIMING-TUNE/PROMOTION-RULEC.md section 6',
                  cells=cells)
    (REPO/inventory.NONACTING).write_text(json.dumps(record, indent=1) + '\n')
    print(json.dumps({k: [d.get('role') or d.get('name') for d in v['differences']] for k, v in cells.items()}, indent=1))


if __name__ == '__main__':
    main()
