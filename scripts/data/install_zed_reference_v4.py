#!/usr/bin/env python3
"""Install the frozen Sielinko GNSS reference v4 (gnss-epoch-v4-20261117, scenario nominal) as main's reference.

Pinned copies, add-only; v2 (gnss-position-v2-20261002) stays in place byte-identical:
  datasets/zed2i/field1_110426_full_10fps_q90/references/gnss-epoch-v4-20261117/
      reference-manifest.json       byte copy of the frozen manifest (sha256 pinned below)
      {primary,fixed_only}.tum, {primary,fixed_only}-support.json
                                    byte copies of the manifest's nominal files (size and sha256 checked)
      reference.json                main-schema document (the schema _reference_source.selected_reference reads,
                                    as gnss-position-v2-20261002/reference.json), repo-relative paths
  configs/references/zed2i_field1_110426_full_10fps_q90.json      selector -> v4, variant primary (as v2)
  configs/references/zed2i_sielinko_imupilot_full_a33.json        a33 view selector -> v4, parent = the full recording
No evaluator code changes. The diagnostic subset selectors (field1_diag60_20261002) stay on v2.
Create-once: refuses to replace a file that differs, except the two selectors, which it rewrites only from the
exact v2 bytes main had (91e45f3) or the a33 view selector from absent.

  python -B scripts/data/install_zed_reference_v4.py [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = Path('/data/imoroz/CAMERA-IMU-GNSS-TIMING-ISSUE/reference-v4/references/gnss-epoch-v4-20261117/reference-manifest.json')
MANIFEST_SHA256 = '12fb6627565988f43a40b43d63aa4e8f122147e854bc7b881a1d7de52a0b0f91'
SCENARIO = 'nominal'
SEQUENCE = 'field1_110426_full_10fps_q90'
A33_VIEW = 'sielinko_imupilot_full_a33'
TARGET = f'datasets/zed2i/{SEQUENCE}/references/gnss-epoch-v4-20261117'
SELECTOR = f'configs/references/zed2i_{SEQUENCE}.json'
A33_SELECTOR = f'configs/references/zed2i_{A33_VIEW}.json'
TIMES = f'datasets/zed2i/{SEQUENCE}/times.txt'
A33_TIMES = f'datasets/zed2i/{A33_VIEW}/times.txt'
# main 91e45f3: the v2 selector and the v2 document it pins (both stay recoverable; v2 files are never touched)
V2_SELECTOR_SHA256 = 'bce242a75c1d48e41b9e2eb71c4ae7e613f0b5c4d5044108f13346a73f1e8ced'
V2_DOCUMENT = f'datasets/zed2i/{SEQUENCE}/references/gnss-position-v2-20261002/reference.json'
V2_DOCUMENT_SHA256 = 'e965f3701dc9ba706c98cf26f481a4e374f6b7b5e54a63a1ca196b0b846f0301'
# The v2 policy statement for the primary variant, kept beside v4's own limitations.
FLOAT_LIMITATION = 'RTK float retained in primary; fixed-only sensitivity is mandatory'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(value):
    return json.dumps(value, indent=2) + '\n'


def frozen():
    """The frozen manifest and its nominal scenario, every file checked against the manifest (size and sha256)."""
    raw = MANIFEST.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise RuntimeError('v4 manifest differs from its pin')
    side = MANIFEST.with_name(MANIFEST.name + '.sha256')
    if side.is_file() and side.read_text().split()[0] != MANIFEST_SHA256:
        raise RuntimeError('v4 manifest sidecar disagrees')
    manifest = json.loads(raw)
    scenario = manifest['scenarios'][SCENARIO]
    for item in [scenario[p][k] for p in ('primary', 'fixed_only') for k in ('trajectory', 'support')] + [scenario['reference_json']]:
        path = Path(item['path'])
        if path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
            raise RuntimeError('v4 file differs from the manifest: ' + item['path'])
    nominal = json.loads(Path(scenario['reference_json']['path']).read_text())
    if (nominal['dataset'], nominal['sequence'], nominal['orientation_valid']) != ('zed2i', SEQUENCE, False):
        raise RuntimeError('v4 nominal document is not the position-only Sielinko reference')
    return raw, manifest, scenario, nominal


def planned():
    """{repo-relative path: bytes} of everything this installs, generated from the frozen files only."""
    raw, manifest, scenario, nominal = frozen()
    files = {f'{TARGET}/reference-manifest.json': raw}
    variants = {}
    for policy in ('primary', 'fixed_only'):
        entry = scenario[policy]
        variant = {}
        for part, name in (('trajectory', f'{policy}.tum'), ('support', f'{policy}-support.json')):
            data = Path(entry[part]['path']).read_bytes()
            files[f'{TARGET}/{name}'] = data
            variant[part] = dict(path=f'{TARGET}/{name}', sha256=entry[part]['sha256'])
        variants[policy] = dict(variant, retained_samples=entry['retained_samples'],
                                support_intervals=entry['support_intervals'], policy=manifest['policies'][policy])
    document = dict(
        schema=1, version=manifest['version'], scenario=SCENARIO, dataset='zed2i', sequence=SEQUENCE,
        orientation_valid=nominal['orientation_valid'], nominal_geometry=nominal['nominal_geometry'],
        origin_lat_lon_alt=nominal['origin_lat_lon_alt'],
        antenna_above_left_camera_m=nominal['antenna_above_left_camera_m'],
        lever_lens_from_rear_antenna_body_m=nominal['lever_lens_from_rear_antenna_body_m'],
        attitude=nominal['attitude'], timing=nominal['timing'], convention=manifest['convention'],
        time_origin_ns=manifest['time_origin_ns'], support_policy=manifest['support_policy'],
        approved_rejected_raw_samples=nominal['approved_rejected_raw_samples'],
        approved_excursions=nominal['approved_excursions'], screening_sha256=nominal['screening_sha256'],
        limitations=list(nominal['limitations']) + [FLOAT_LIMITATION],
        frozen_source=dict(manifest=dict(path=str(MANIFEST), sha256=MANIFEST_SHA256),
                           pinned_copy=f'{TARGET}/reference-manifest.json',
                           nominal_reference=dict(path=scenario['reference_json']['path'],
                                                  sha256=scenario['reference_json']['sha256']),
                           decision_record=manifest['decision_record'], status=manifest['status']),
        supersedes=dict(path=V2_DOCUMENT, sha256=V2_DOCUMENT_SHA256, note='kept in place, byte-identical'),
        variants=variants, generated_by='scripts/data/install_zed_reference_v4.py')
    doc = text(document).encode()
    files[f'{TARGET}/reference.json'] = doc
    doc_ref = dict(path=f'{TARGET}/reference.json', sha256=hashlib.sha256(doc).hexdigest())
    times_sha = sha(REPO / TIMES)
    files[SELECTOR] = text(dict(schema=1, dataset='zed2i', sequence=SEQUENCE, variant='primary', reference=doc_ref)).encode()
    files[A33_SELECTOR] = text(dict(
        schema=1, dataset='zed2i', sequence=A33_VIEW, variant='primary', reference=doc_ref,
        diagnostic_parent_sequence=SEQUENCE, diagnostic_only=True,
        purpose='sequence alias: the a33 camera-IMU timing-corrected view of the full Sielinko recording '
                '(same images and times, corrected IMU); configs/campaigns/sielinko-a33-attempts-20261118.json',
        subset_times=dict(path=A33_TIMES, sha256=times_sha), parent_times=dict(path=TIMES, sha256=times_sha))).encode()
    return files


def install(check=False, repo=REPO):
    actions = {}
    for rel, data in planned().items():
        path = repo / rel
        if path.exists() and path.read_bytes() == data:
            actions[rel] = 'same'
            continue
        if path.exists() and not (rel == SELECTOR and sha(path) == V2_SELECTOR_SHA256):
            raise RuntimeError('refusing to replace a file that differs: ' + rel)
        actions[rel] = 'would write' if check else 'written'
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return actions


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='read-only: exit 1 unless every file is already installed')
    args = ap.parse_args(argv)
    actions = install(check=args.check)
    for rel, action in actions.items():
        print(action, rel)
    return 1 if args.check and any(a != 'same' for a in actions.values()) else 0


if __name__ == '__main__':
    raise SystemExit(main())
