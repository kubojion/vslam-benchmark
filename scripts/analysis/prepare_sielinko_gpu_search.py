#!/usr/bin/env python3
"""Prepare the Sielinko CPU noise search: recording views, reference selectors, protocol.

    plan      print the views and protocol path, without writing (default)
    protocol  write the draft protocol and the views' reference selectors (configs/)
    views     build the halves and clips of the recording inside this checkout
    freeze    after the go: freeze the protocol, identities and handover into --art

No estimator runs. Views hold small copied tables and read-only symlinks to the
original image files in the main checkout; nothing in the main checkout changes.
The split is fixed before any search run: selection sees only the first half.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
MAIN = Path('/data/imoroz/vslam-benchmark')
sys.path[:0] = [str(ROOT / 'scripts/analysis'), str(ROOT / 'scripts/run')]
import noise_adapters as adapters  # noqa: E402
import _imu_noise_rule  # noqa: E402

CAMPAIGN = 'sielinko-gpu-search-20261026'
DATASET = 'zed2i'
PARENT = 'field1_110426_full_10fps_q90'
PROTOCOL = ROOT / 'configs/experiments' / (CAMPAIGN + '.json')
CLIP_S = 180
# IMU kept beyond a window's first and last image (a prefix keeps the parent's head).
IMU_MARGIN_NS = 20_000_000
VIEWS = {
    'full': PARENT,
    'half1': 'field1_sielinko_h1_20261022',
    'half2': 'field1_sielinko_h2_20261022',
    'clip1': 'field1_sielinko_h1c1_20261022',
    'clip2': 'field1_sielinko_h1c2_20261022',
}
ROLES = {'full': 'full', 'half1': 'half', 'half2': 'half', 'clip1': 'short', 'clip2': 'short'}
ENVELOPE = {'gyroscope_noise_density': 0.0195, 'accelerometer_noise_density': 0.18,
            'gyroscope_random_walk': 7.400196e-4, 'accelerometer_random_walk': 0.0202}
ENGINE_ON = 'configs/sensitivity/zed2i-engine-on-20261021/profile.json'
RULE_C_FILES = {'cuvslam': None, 'mast3r_fusion': None, 'airslam': 'configs/airslam/zed2i_camera_vio.yaml'}
ENVELOPE_RUNS = {a: f'results/vio/{DATASET}/{PARENT}/{a}/run10001' for a in RULE_C_FILES}
ORDER = ['cuvslam', 'mast3r_fusion', 'airslam']
TIMEOUTS_S = {'cuvslam': dict(short=600,half=1800,full=1800),
              'mast3r_fusion': dict(short=1800,half=7200,full=10800),
              'airslam': dict(short=1800,half=5400,full=10800)}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_text(value):
    return json.dumps(value, indent=2, allow_nan=False) + '\n'


def rows(path):
    """(header lines, data rows) of an EuRoC CSV; data rows keyed by integer stamp."""
    header, data = [], []
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        if line.startswith('#'):
            header.append(line)
        else:
            data.append((int(line.split(',')[0]), line))
    if any(b[0] <= a[0] for a, b in zip(data, data[1:])):
        raise ValueError('timestamps must be strictly increasing: ' + str(path))
    return header, data


def windows(times):
    """Fixed split rule; returns {view: (first index, count)} into the parent frames."""
    start, end = times[0], times[-1]
    cutoff = start + (end - start) // 2
    half1 = sum(t < cutoff for t in times)
    if not 0 < half1 < len(times):
        raise ValueError('cannot split the recording at its time midpoint')
    clip = CLIP_S * 10**9
    first2 = next(i for i, t in enumerate(times) if t >= start + (times[half1 - 1] - start) // 2)
    result = dict(full=(0, len(times)), half1=(0, half1), half2=(half1, len(times) - half1),
                  clip1=(0, sum(t < start + clip for t in times[:half1])),
                  clip2=(first2, sum(times[first2] <= t < times[first2] + clip for t in times[:half1])))
    for name in ('clip1', 'clip2'):
        first, count = result[name]
        if first + count > half1 or times[first + count - 1] - times[first] < clip - 10**9:
            raise ValueError('clip does not lie inside the first half: ' + name)
    return result


def times_text(selected):
    return '\n'.join(map(str, selected)) + '\n'


def view_records(source):
    """Window and camera-clock identity of every view, computed without writing."""
    times = [int(x) for x in (Path(source) / 'times.txt').read_text().split()]
    return {view: dict(first=first, count=count,
                       times_sha256=hashlib.sha256(times_text(times[first:first + count]).encode()).hexdigest())
            for view, (first, count) in windows(times).items()}


def build_view(source, target, first, count, parent_name):
    """Exact parent window: copied tables, read-only symlinks to the original images."""
    source, target = Path(source), Path(target)
    if target.exists():
        raise FileExistsError('view exists; compare it with `plan` before rebuilding: ' + str(target))
    times = [int(x) for x in (source / 'times.txt').read_text().split()]
    selected = times[first:first + count]
    stamps = set(selected)
    target.mkdir(parents=True)
    (target / 'times.txt').write_text(times_text(selected))
    for camera in ('cam0', 'cam1'):
        header, data = rows(source / 'mav0' / camera / 'data.csv')
        keep = [line for stamp, line in data if stamp in stamps]
        if len(keep) != len(selected):
            raise ValueError('stereo CSV and camera clock disagree: ' + camera)
        folder = target / 'mav0' / camera / 'data'
        folder.mkdir(parents=True)
        (folder.parent / 'data.csv').write_text('\n'.join(header + keep) + '\n')
        for line in keep:
            name = line.split(',')[1].strip()
            if Path(name).name != name:
                raise ValueError('unsafe image name: ' + name)
            (folder / name).symlink_to((source / 'mav0' / camera / 'data' / name).resolve(strict=True))
    header, data = rows(source / 'mav0/imu0/data.csv')
    low = -math.inf if first == 0 else selected[0] - IMU_MARGIN_NS
    high = selected[-1] + IMU_MARGIN_NS
    imu = [line for stamp, line in data if low <= stamp <= high]
    (target / 'mav0/imu0').mkdir(parents=True)
    (target / 'mav0/imu0/data.csv').write_text('\n'.join(header + imu) + '\n')
    for alias, camera in [('cam0', 'cam0'), ('left', 'cam0'), ('cam1', 'cam1'), ('right', 'cam1')]:
        (target / alias).symlink_to(f'mav0/{camera}/data')
    manifest = json.loads((source / 'manifest.json').read_text())
    manifest['experiment_subset'] = dict(
        campaign=CAMPAIGN, parent_sequence=parent_name,
        kind='exact_prefix' if first == 0 else 'exact_window', parent_offset=first,
        input_frames=len(selected), first_camera_ns=selected[0], last_camera_ns=selected[-1],
        imu_samples=len(imu), imu_policy=('parent head, then through 20 ms after the last image' if first == 0
                                          else 'from 20 ms before the first to 20 ms after the last image'),
        parent_fields_describe_full_recording=True)
    (target / 'manifest.json').write_text(json_text(manifest))
    return dict(first=first, count=count, times_sha256=sha(target / 'times.txt'), imu_samples=len(imu))


def selector(name, view, parent_times, subset_times, offset, purpose):
    reference = json.loads((ROOT / f'configs/references/{DATASET}_{PARENT}.json').read_text())
    value = dict(schema=1, dataset=DATASET, sequence=name, variant=reference['variant'],
                 reference=reference['reference'], diagnostic_parent_sequence=PARENT,
                 diagnostic_only=True, purpose=f'{CAMPAIGN}: {purpose}',
                 subset_times=dict(path=f'datasets/{DATASET}/{name}/times.txt', sha256=subset_times),
                 parent_times=dict(path=f'datasets/{DATASET}/{PARENT}/times.txt', sha256=parent_times))
    if offset:
        value['parent_offset'] = offset
    return value


def control_values():
    profile = json.loads((ROOT / ENGINE_ON).read_text())
    values = {}
    for algorithm in ORDER:
        path = RULE_C_FILES[algorithm]
        rule = _imu_noise_rule.noise(algorithm, DATASET)
        if path is not None:
            configured = adapters.read_effective(ROOT / path, algorithm)
            if any(not math.isclose(configured[k], rule[k], rel_tol=1e-12) for k in adapters.KEYS):
                raise RuntimeError('production config disagrees with Rule C: ' + algorithm)
            rule = configured
        values[algorithm] = [
            dict(label='rule_c', params=rule, source=path or 'scripts/run/_imu_noise_rule.py (zed2i)'),
            dict(label='engine_on', params=profile['estimators'][algorithm]['noise'], source=ENGINE_ON),
            dict(label='envelope', params=dict(ENVELOPE), source='docs/imu-noise-rule-20261005.md (ZED2i envelope)',
                 historical_run=ENVELOPE_RUNS[algorithm]),
        ]
    return values


def bounds(controls):
    """Earlier rule [min(C, historical)/10, max(100 C, 3 historical)], engine-on as historical."""
    by = {c['label']: c['params'] for c in controls}
    return {k: [min(c['params'][k] for c in controls) / 10,
                max(100 * by['rule_c'][k], 3 * by['engine_on'][k], 3 * by['envelope'][k])]
            for k in adapters.KEYS}


def protocol(view_records):
    names = {view: VIEWS[view] for view in VIEWS}
    controls = control_values()
    studies = []
    for algorithm in ORDER:
        studies.append(dict(
            id=f'{algorithm}_{DATASET}', algorithm=algorithm, dataset=DATASET,
            supports_lc=algorithm not in ('basalt', 'openvins', 'voxel_svio'), final_modes=['vio'],
            clips=[names['clip1'], names['clip2']], full_sequences=[names['half1']],
            # User 22 Oct: Rule C also once on the second half, as its held-out baseline.
            test_sequences=[names['half2'], names['full']], final_controls=['rule_c'],
            final_control_sequences=[names['half2']],
            sequence_parents={names[v]: PARENT for v in VIEWS},
            sequence_roles={names[v]: ROLES[v] for v in VIEWS},
            controls=controls[algorithm], bounds=bounds(controls[algorithm]),
            lane='exclusive' if algorithm == 'basalt' else 'lane2' if algorithm == 'voxel_svio' else None))
    # Revision 13 of the Rule C coordinator uses no lane lock files: the written handover
    # releases the lanes, and every launch checks the lane's cores for other runs.
    locks = []
    return dict(
        schema=1, status='DRAFT_NOT_FROZEN', campaign_id=CAMPAIGN, development_only=True,
        worktree=str(ROOT), main_root=str(MAIN), max_wall_hours=120,
        preliminary=dict(seed=20261009, candidates=16, startup=8, finalists=2, repetitions=3),
        screen=dict(seeds=[202610091, 202610092], candidates_per_seed=16, startup=8),
        full=dict(seed=202610093, candidates=12, seed_candidates=6, finalists=2, repetitions=3),
        studies=studies, views={names[v]: dict(role=ROLES[v], **view_records.get(v, {})) for v in VIEWS},
        split=('Time midpoint of the recording. Development (all selection) uses only the first half and two '
               f'{CLIP_S} s clips from it: its start, and the window starting at its own time midpoint. '
               'The fresh final N=1 runs the selected setting on the second half and on the full recording.'),
        runtime_environment={'voxel_svio': {'VOXEL_SVIO_CONTAINER': 'sielinko_search_voxel_20261022'}},
        runtime_environment_by_study={},
        delivery_policy=dict(openvins_pending_camera_tail=None, openvins_end_of_stream_drain=True,
                             openvins_flow_control=True, openvins_transport_profile='large_shm',
                             voxel_camera_rate_gate=('Audit the expected native timestamp gate from its recorded '
                                                     'frequency; do not change sampling or accept unexplained missing input.'),
                             basis='exact native receipts; never chosen using ATE'),
        attempt_timeouts_s=TIMEOUTS_S,
        attempt_resource_limits={a: dict(memory_gib=50, swap_gib=0) for a in ORDER},
        lanes=dict(lane1=dict(cpus='0-3', memory_gib=50, locks=locks),
                   lane2=dict(cpus='4-7', memory_gib=50, locks=locks),
                   exclusive=dict(cpus='0-7', memory_gib=50, locks=locks, idle_host=True)),
        launch_policy=dict(min_available_gib=40, no_host_swap_use=True, min_disk_free_gib=100,
                           poll_s=30, sample_s=5, max_affinity_corrections=3),
        lane_handover=None,
        scheduling=dict(resource_class={a: 'cpu' for a in ORDER}, develop=('Two lanes, one study per lane at a time; a study keeps its declared lane. '
                                 'An exclusive study starts only after every other study, with the host idle.'),
                        final='serial, one attempt at a time, after every selection is frozen'),
        score=('10 * failed_observation_count + 0.5 * mean(residual) + 0.5 * max(residual); residual = '
               'RMSE/(reference_path_length+RMSE) + unsupported_export_fraction. Existing numerical and 90% '
               'export-support gates retained. Lower is better.'),
        repeated_selection=('Top two full candidates plus the three controls, deduplicated by exact parameter vector, '
                            'receive N=3 on the first half. The selected candidate minimizes the same declared score.'),
        controls='Rule C engine-off, engine-on sensitivity and the historical envelope, enqueued first in every stage.',
        bounds_rule='[min(controls)/10, max(100*Rule C, 3*engine-on, 3*envelope)] per component; never changed after start.',
        exclusions=['every dataset except zed2i', 'GPU estimators', 'AirSLAM'],
        limitations=['One recording; its halves share platform, field and day.',
                     'The recording was inspected before (Rule C and envelope runs on the full run).',
                     'The full-run test includes the development half; only the second half is unseen by selection.',
                     'Position-only GNSS reference; SE3 position alignment.',
                     'Two clips probe short-horizon behaviour; equal proposal counts, not equal CPU time.',
                     'Runtimes from concurrent lanes are labelled overlapped.'],
        frozen_input_sha256={}, frozen_runtime_sha256={}, frozen_source_sha256={},
        shared_budget_file='sielinko-cpu-search-budget.json',
        main_pins=[f'datasets/{DATASET}/{PARENT}/{name}' for name in
                   ('times.txt', 'mav0/cam0/data.csv', 'mav0/cam1/data.csv', 'mav0/imu0/data.csv')],
        enforce_main_head=False,
        decisions=dict(at='2026-10-22', clips='2 x 180 s', second_half_rule_c=True, vio_lc_final=False,
                       approved='protocol approved; starts only after the written lane handover and the user\'s go'),
        pending=['lane_handover', 'frozen identities', 'check clips', "user's go"])


def plan(source):
    times = [int(x) for x in (source / 'times.txt').read_text().split()]
    result = {}
    for view, (first, count) in windows(times).items():
        selected = times[first:first + count]
        result[view] = dict(sequence=VIEWS[view], first=first, count=count,
                            start_s=(selected[0] - times[0]) / 1e9, duration_s=(selected[-1] - selected[0]) / 1e9)
    return result


def make_views(source, root):
    source, root = Path(source), Path(root)
    times = [int(x) for x in (source / 'times.txt').read_text().split()]
    records, parent_times = {}, sha(source / 'times.txt')
    for view, (first, count) in windows(times).items():
        target = root / 'datasets' / DATASET / VIEWS[view]
        if view == 'full':
            # Tracked tables of the parent are already in this checkout; add its sensor tree.
            if (target / 'times.txt').read_bytes() != (source / 'times.txt').read_bytes():
                raise RuntimeError('checkout and main disagree on the parent camera clock')
            staging = root / 'datasets' / DATASET / '.full-staging'
            record = build_view(source, staging, first, count, PARENT)
            for name in ('mav0', 'cam0', 'cam1', 'left', 'right'):
                if (target / name).exists() or (target / name).is_symlink():
                    raise FileExistsError(target / name)
                (staging / name).rename(target / name)
            for name in ('times.txt', 'manifest.json'):
                (staging / name).unlink()
            staging.rmdir()
        else:
            record = build_view(source, target, first, count, PARENT)
        records[view] = record
    return records


def write_selectors(source, root):
    parent_times = sha(Path(source) / 'times.txt')
    written = []
    for view, record in view_records(source).items():
        if view == 'full':
            continue
        purpose = 'test (not used by selection)' if view == 'half2' else 'development'
        path = Path(root) / 'configs/references' / f'{DATASET}_{VIEWS[view]}.json'
        value = json_text(selector(VIEWS[view], view, parent_times, record['times_sha256'], record['first'], purpose))
        if path.exists() and path.read_text() != value:
            raise RuntimeError('reference selector differs: ' + str(path))
        path.write_text(value)
        written.append(str(path))
    return written


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True)


def source_identity(algorithm):
    """The digest _capture_implementation.capture compares with VSLAM_EXPECTED_SOURCE_SHA256."""
    import _capture_implementation as implementation
    store = ROOT / 'results/.implementation-blobs/sha256'
    trees = [dict(role='workspace', **implementation.capture_tree(ROOT, ROOT, store, scope=('scripts', 'configs', '.gitmodules')))]
    name = implementation.SOURCES[algorithm]
    if name:
        tree = ROOT / 'src' / name
        if not (tree / '.git').exists():
            raise RuntimeError('private source tree missing (prepare it first): ' + str(tree))
        trees.append(dict(role='algorithm', **implementation.capture_tree(ROOT, tree, store)))
    return hashlib.sha256(json.dumps(trees, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def freeze(art, handover):
    """Freeze into the artifact directory; refuses a dirty checkout or a changed earlier freeze."""
    import _capture_inputs
    import _capture_runtime
    import noise_execution_policy
    art, handover = Path(art).resolve(), Path(handover).resolve()
    if MAIN.resolve() in art.parents or art == MAIN.resolve():
        raise RuntimeError('campaign artifacts must be outside the main checkout')
    if git('status', '--porcelain', '--', 'scripts', 'configs').strip():
        raise RuntimeError('commit every script and config change before freezing')
    value = json.loads(PROTOCOL.read_text())
    records = view_records(MAIN / 'datasets' / DATASET / PARENT)
    for view, sequence in VIEWS.items():
        actual = sha(ROOT / 'datasets' / DATASET / sequence / 'times.txt')
        if actual != records[view]['times_sha256'] or actual != value['views'][sequence]['times_sha256']:
            raise RuntimeError('view differs from the draft protocol: ' + sequence)
    os.environ.update({k:v for env in value['runtime_environment'].values() for k,v in env.items()})
    _capture_runtime.ALGORITHM_ENVS.update({a: '/data/imoroz/conda/envs/'+a for a in ('cuvslam','mast3r_fusion')})
    value.update(
        status='FROZEN', frozen_at=datetime.now(timezone.utc).isoformat(),
        frozen_input_sha256={f'{DATASET}/{s}': _capture_inputs.identity(ROOT, DATASET, s)['sha256'] for s in VIEWS.values()},
        frozen_source_sha256={s['algorithm']: source_identity(s['algorithm']) for s in value['studies']},
        lane_handover=dict(path=str(handover), sha256=sha(handover)), pending=[])
    runtime = {}
    for spec in value['studies']:
        identity = _capture_runtime.identity(ROOT, spec['algorithm'])
        if identity['missing']:
            raise RuntimeError(spec['algorithm'] + ' runtime incomplete: ' + '; '.join(identity['missing']))
        runtime[spec['algorithm']] = identity['sha256']
    value['frozen_runtime_sha256'] = runtime
    pins = {path: sha(MAIN / path) for path in value['main_pins']}
    main_before = dict(main_head=subprocess.check_output(['git', '-C', str(MAIN), 'rev-parse', 'HEAD'], text=True).strip(),
                       sha256=pins, enforce_main_head=value['enforce_main_head'],
                       note='Only the main files this search reads are pinned; images are hashed per attempt.')
    art.mkdir(parents=True, exist_ok=True)
    targets = {'protocol.json': json_text(value), 'main-before.json': json_text(main_before)}
    for name, text in targets.items():
        if (art / name).exists():
            raise FileExistsError('already frozen; review instead of refreezing: ' + str(art / name))
    for name, text in targets.items():
        (art / name).write_text(text)
    files = [dict(path=p, sha256=sha(ROOT / p)) for p in git('ls-files', '--', 'scripts', 'configs').split('\n')
             if p and (ROOT / p).is_file()]
    identity = dict(schema=1, worktree_head=git('rev-parse', 'HEAD').strip(),
                    boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                    protocol_sha256=sha(art / 'protocol.json'),
                    controller_environment=noise_execution_policy.controller_environment(), files=files)
    (art / 'execution-identity.json').write_text(json_text(identity))
    return dict(art=str(art), protocol_sha256=identity['protocol_sha256'], files=len(files))


_cpu_protocol = protocol

def protocol(view_records):
    value = _cpu_protocol(view_records)
    for study in value['studies']:
        study['lane'] = 'gpu'
    value.update(runtime_environment={a: {a.upper()+'_CONDA_ENV':'/data/imoroz/conda/envs/'+a}
                                      for a in ('cuvslam','mast3r_fusion')},
        attempt_resource_limits={a:dict(memory_gib=50 if a=='airslam' else 32,
                                         memory_high_gib=40 if a=='airslam' else 24,swap_gib=0) for a in ORDER},
        lanes={'gpu':dict(cpus='20-23',memory_gib=32)},
        scheduling=dict(resource_class={a:'gpu' for a in ORDER},
                        develop='One GPU study at a time beside external CPU lanes. AirSLAM only after CPU campaign complete.',
                        final='Serial VIO only after all three selections frozen; selected second-half/full and Rule C second-half, exact-setting deduplicated.'),
        exclusions=['other datasets','VIO-LC','CPU estimators'],
        shared_budget_file='sielinko-gpu-search-budget.json',
        enforce_main_head=True,
        decisions=dict(at='2026-10-26',approved='User: yes please do it then, Sielinko GPU extended search alongside CPU',
                       inherited_method='Same Sielinko CPU split/stages/control bounds/scoring and VIO final modes',
                       phase_budget_hours=120,air_starts='Only after CPU campaign complete including Basalt'),
        source_protocol='Sielinko CPU 20261022 method; new independent campaign, run IDs and deadline',
        outcome_policy={'numerical_failures':'retain unchanged score; never retry for accuracy',
                        'native_nonzero':'stop for infrastructure/native classification; preserve failed attempt',
                        'resource_guard_abort':'preserve as resource-censored; reviewed new-ID replacement only under standing rules',
                        'air_cap_contact':'qualified result at50GiB; never censor for cap contact alone; OOM remains fault'})
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', nargs='?', choices=('plan', 'views', 'protocol', 'freeze'), default='plan')
    parser.add_argument('--art', type=Path, help='campaign artifact directory (freeze)')
    parser.add_argument('--handover', type=Path, help="lane owner's written handover (freeze)")
    args = parser.parse_args()
    if ROOT.resolve() == MAIN.resolve():
        raise RuntimeError('run only from the isolated search checkout')
    source = MAIN / 'datasets' / DATASET / PARENT
    if args.action == 'plan':
        print(json.dumps(dict(views=plan(source), protocol=str(PROTOCOL)), indent=2))
    elif args.action == 'views':
        print(json.dumps(make_views(source, ROOT), indent=2))
    elif args.action == 'freeze':
        if not args.art or not args.handover:
            parser.error('freeze needs --art and --handover')
        print(json.dumps(freeze(args.art, args.handover), indent=2))
    else:
        # Reuse the byte-identical reviewed Sielinko window reference selectors.
        for sequence in VIEWS.values():
            assert (ROOT/'configs/references'/f'{DATASET}_{sequence}.json').is_file()
        value = json_text(protocol(view_records(source)))
        if PROTOCOL.exists() and PROTOCOL.read_text() != value:
            raise RuntimeError('draft protocol differs; review the change: ' + str(PROTOCOL))
        PROTOCOL.parent.mkdir(parents=True, exist_ok=True)
        PROTOCOL.write_text(value)
        print(PROTOCOL)


if __name__ == '__main__':
    main()
