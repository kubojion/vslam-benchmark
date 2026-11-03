#!/usr/bin/env python3
"""Prepare the cross-fit IMU noise search, PLAN Update 6 Job C: M, clips, reference selectors, protocol.

    plan      print the clip windows, without writing (default)
    motion    compute M from the private IMU files into configs/experiments/ (reads IMU tables only)
    protocol  write the draft protocol (configs/experiments/) and the clips' reference selectors
    views     build the 180-s clips inside this checkout
    freeze    after the gates' go: freeze the protocol and identities into --art

No estimator runs. Clips hold small copied tables and read-only symlinks to the original image files, built by
the Sielinko search's window method. Nothing outside this checkout changes.

Protocol: 30 studies (10 systems x CitrusFarm, HortiMulti, Rosario). Each study has two folds, tuning on one
sequence and testing on the other. Per term the range is [min(A,C)/10, max(100C,3M)], with A the dataset's static
calibration, C Rule C and M the unrounded in-motion level with released random walks (imu_motion_noise.py).
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
import imu_motion_noise as motion  # noqa: E402
import _imu_noise_rule  # noqa: E402

KEYS = adapters.KEYS
CAMPAIGN = 'imu-timing-search-20261031'
PROTOCOL = ROOT / 'configs/experiments' / (CAMPAIGN + '.json')
MOTION = ROOT / 'configs/experiments' / (CAMPAIGN + '-motion.json')
PAPER_ENVELOPE = Path('/data/imoroz/PAPER/vslam-paper/data/snapshot-20261102/imu-envelope.json')
CORRECTED_IMU_SHA256 = {'seq04': '9ec219ee1fa598ede605cb5c55b5dc98f57a47512c64b63dc8c09598d7625336',
                        'seq07': '1629baf2b4af799cd9ab652c60bc97edb1f385f96690fe50e24b1ce8d7247f65'}
DATASETS = {'citrusfarm': ('seq04', 'seq07'), 'hortimulti': ('strawberry02', 'strawberry03'),
            'rosariov2': ('sequence1', 'sequence5')}
RUN_ORDER = ['citrusfarm', 'hortimulti', 'rosariov2']
SYSTEMS = ('okvis2', 'okvis2x', 'orbslam3', 'openvins', 'voxel_svio', 'svo_pro',
           'basalt', 'cuvslam', 'airslam', 'mast3r_fusion')
SYSTEM_LANES = {'orbslam3': ['cpu_a', 'cpu_b'], 'okvis2': ['cpu_a', 'cpu_b'], 'okvis2x': ['cpu_a', 'cpu_b'],
                'openvins': ['cpu_a', 'cpu_b'], 'voxel_svio': ['cpu_a', 'cpu_b'], 'svo_pro': ['cpu_a', 'cpu_b'],
                'cuvslam': ['gpu'], 'airslam': ['gpu'], 'mast3r_fusion': ['gpu'], 'basalt': ['exclusive']}
GPU_SYSTEMS = ('cuvslam', 'airslam', 'mast3r_fusion')
CLIP_S = 180
# IMU kept beyond a window's first and last image (a prefix keeps the parent's head).
IMU_MARGIN_NS = 20_000_000
RUN_ID_FIRST, RUN_ID_LAST, FOLD_BLOCK = 70000, 76999, 100
CHECK_BLOCK_FIRST, GATE_BLOCK_FIRST, SMALL_BLOCK = 76000, 76500, 10
# Gate and check attempts of the earlier freezes (protocols 47f45ddb and a7f801bd, E-core lanes) and the lane gate
# under real load of 3 Nov 2026. They stay on disk as evidence; this freeze never reuses their IDs.
SUPERSEDED_FREEZE_IDS = (76000, 76499)
TOP_FILES = ('gt_tum.txt', 'gt_interp_tum.txt', 'gps.csv', 'segments_auto.csv')
CPU_LIMITS = dict(memory_gib=64, swap_gib=0)
GPU_LIMITS = dict(memory_gib=50, memory_high_gib=40, swap_gib=0)
# Limits of the earlier searches: Sielinko for short clips, cpu15 for full CPU runs, gpu6 and air3 for GPU runs.
TIMEOUTS_S = {'orbslam3': dict(short=1020, vio=5400, **{'vio-lc': 7200}),
              'okvis2': dict(short=1020, vio=5400, **{'vio-lc': 7200}),
              'okvis2x': dict(short=1020, vio=5400, **{'vio-lc': 7200}),
              'svo_pro': dict(short=1020, vio=5400, **{'vio-lc': 7200}),
              'openvins': dict(short=1200, vio=5400),
              'voxel_svio': dict(short=1200, vio=5400),
              'basalt': dict(short=1020, vio=5400),
              'cuvslam': dict(short=300, vio=900, **{'vio-lc': 1200}),
              'mast3r_fusion': dict(short=1200, vio=5400, **{'vio-lc': 7200}),
              'airslam': dict(short=1800, vio=10800, **{'vio-lc': 10800})}
# Median wall seconds of the first search's attempts (clip, full VIO, full VIO-LC): cpu15, cpu6, gpu6 and air3
# campaigns. Only the dry plan's hours use them.
WALL_ESTIMATES_S = {
    'citrusfarm': {'orbslam3': (239, 1142, 1143), 'okvis2': (154, 767, 3213), 'okvis2x': (157, 754, 3616),
                   'openvins': (195, 909), 'voxel_svio': (194, 919), 'svo_pro': (83, 392, 390),
                   'basalt': (34, 159), 'cuvslam': (31, 141, 158), 'airslam': (72, 337, 674),
                   'mast3r_fusion': (228, 1035, 1238)},
    'hortimulti': {'orbslam3': (201, 653, 653), 'okvis2': (104, 376, 658), 'okvis2x': (105, 355, 668),
                   'openvins': (194, 613), 'voxel_svio': (194, 613), 'svo_pro': (38, 54, 36),
                   'basalt': (8, 22), 'cuvslam': (20, 49, 154), 'airslam': (66, 187, 374),
                   'mast3r_fusion': (208, 649, 670)},
    'rosariov2': {'orbslam3': (225, 1063, 1049), 'okvis2': (225, 1208, 1986), 'okvis2x': (221, 1142, 1863),
                  'openvins': (194, 888), 'voxel_svio': (195, 889), 'svo_pro': (83, 394, 401),
                  'basalt': (31, 146), 'cuvslam': (26, 123, 392), 'airslam': (73, 404, 808),
                  'mast3r_fusion': (251, 1140, 1245)}}
REPRO_TARGETS = {'openvins': 0.8008678157909523, 'voxel_svio': 0.888741295416627}  # median of runs 50001-50003
SCREEN = dict(seeds=[202610091, 202610092], candidates_per_seed=12, startup=8)
FULL = dict(seed=202610093, candidates=10, seed_candidates=6, finalists=2, repetitions=3)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_text(value):
    return json.dumps(value, indent=2, allow_nan=False) + '\n'


def clip_name(sequence, number):
    return f'{sequence}_tsearch_c{number}'


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


def clip_windows(times):
    """{clip number: (first index, count)}: the recording's start, and the window starting at its time midpoint.

    A recording too short for a full window after its midpoint (strawberry03, 242 s) keeps a 180-s window by
    ending it at the last image, so the two clips overlap. That overlap is disclosed in the protocol.
    """
    start, end = times[0], times[-1]
    clip = CLIP_S * 10**9
    if end - start < clip:
        raise ValueError('recording is shorter than one clip')
    midpoint = start + (end - start) // 2
    if midpoint + clip <= end:
        first2 = next(i for i, t in enumerate(times) if t >= midpoint)
    else:
        first2 = next(i for i, t in enumerate(times) if t > end - clip)
    result = {1: (0, sum(t < start + clip for t in times)),
              2: (first2, sum(times[first2] <= t < times[first2] + clip for t in times))}
    for number, (first, count) in result.items():
        if first + count > len(times) or times[first + count - 1] - times[first] < clip - 10**9:
            raise ValueError(f'clip {number} is shorter than {CLIP_S} s')
    return result


def overlap_seconds(times, windows):
    first1, count1 = windows[1]
    first2, _ = windows[2]
    return max(0., (times[first1 + count1 - 1] - times[first2]) / 1e9)


def times_text(selected):
    return '\n'.join(map(str, selected)) + '\n'


def read_times(path):
    return [int(x) for x in Path(path).read_text().split()]


def view_records(times):
    """Window and camera-clock identity of both clips, computed without writing."""
    windows = clip_windows(times)
    records = {number: dict(first=first, count=count, start_s=(times[first] - times[0]) / 1e9,
                            duration_s=(times[first + count - 1] - times[first]) / 1e9,
                            times_sha256=hashlib.sha256(times_text(times[first:first + count]).encode()).hexdigest())
               for number, (first, count) in windows.items()}
    return records, overlap_seconds(times, windows)


def build_view(source, target, first, count, parent_name):
    """Exact parent window: copied tables, read-only symlinks to the original images."""
    source, target = Path(source), Path(target)
    if target.exists():
        raise FileExistsError('view exists; compare it with `plan` before rebuilding: ' + str(target))
    times = read_times(source / 'times.txt')
    selected = times[first:first + count]
    stamps = set(selected)
    target.mkdir(parents=True)
    (target / 'times.txt').write_text(times_text(selected))
    for name in TOP_FILES:
        if (source / name).is_file():
            (target / name).write_bytes((source / name).read_bytes())
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
        if (source / 'mav0' / camera / 'sensor.yaml').is_file():
            (folder.parent / 'sensor.yaml').write_bytes((source / 'mav0' / camera / 'sensor.yaml').read_bytes())
    header, data = rows(source / 'mav0/imu0/data.csv')
    low = -math.inf if first == 0 else selected[0] - IMU_MARGIN_NS
    high = selected[-1] + IMU_MARGIN_NS
    imu = [line for stamp, line in data if low <= stamp <= high]
    (target / 'mav0/imu0').mkdir(parents=True)
    (target / 'mav0/imu0/data.csv').write_text('\n'.join(header + imu) + '\n')
    if (source / 'mav0/imu0/sensor.yaml').is_file():
        (target / 'mav0/imu0/sensor.yaml').write_bytes((source / 'mav0/imu0/sensor.yaml').read_bytes())
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
    # _saved_run.py reads this: the clip keeps its parent's reviewed pose frame.
    (target / 'experiment-prefix.json').write_text(json_text(dict(
        schema=1, diagnostic_only=True, parent_sequence=parent_name, parent_offset=first,
        parent_times_sha256=sha(source / 'times.txt'), subset_times_sha256=sha(target / 'times.txt'))))
    return dict(first=first, count=count, times_sha256=sha(target / 'times.txt'), imu_samples=len(imu))


def make_views(root):
    records = {}
    for dataset, sequences in DATASETS.items():
        for sequence in sequences:
            source = Path(root) / 'datasets' / dataset / sequence
            for number, (first, count) in clip_windows(read_times(source / 'times.txt')).items():
                name, target = clip_name(sequence, number), source.with_name(clip_name(sequence, number))
                if target.exists():  # a repeated setup keeps an identical view
                    times = times_text(read_times(source / 'times.txt')[first:first + count])
                    if (target / 'times.txt').read_text() != times:
                        raise RuntimeError('existing view differs: ' + str(target))
                    continue
                records[f'{dataset}/{name}'] = build_view(source, target, first, count, sequence)
    return records


def selector(root, dataset, parent, name, record):
    """CitrusFarm's reference is a reviewed version bound by hash; a clip selects it through its parent."""
    base = json.loads((Path(root) / f'configs/references/{dataset}_{parent}.json').read_text())
    parent_times = f'datasets/{dataset}/{parent}/times.txt'
    value = dict(base, sequence=name, diagnostic_only=True, diagnostic_parent_sequence=parent,
                 purpose=f'{CAMPAIGN}: tuning clip',
                 subset_times=dict(path=f'datasets/{dataset}/{name}/times.txt', sha256=record['times_sha256']),
                 parent_times=dict(path=parent_times, sha256=sha(Path(root) / parent_times)))
    if record['first']:
        value['parent_offset'] = record['first']
    return value


def write_selectors(root, views):
    """Only CitrusFarm has selectors: HortiMulti and Rosario clips use their copied gt_tum.txt."""
    written = []
    for sequence in DATASETS['citrusfarm']:
        for number in (1, 2):
            name = clip_name(sequence, number)
            path = Path(root) / 'configs/references' / f'citrusfarm_{name}.json'
            value = json_text(selector(root, 'citrusfarm', sequence, name, views['citrusfarm'][sequence]['clips'][str(number)]))
            if path.exists() and path.read_text() != value:
                raise RuntimeError('reference selector differs: ' + str(path))
            path.write_text(value)
            written.append(str(path.relative_to(root)))
    return written


def effective_rule_c(root, algorithm, dataset, sequence):
    """The value a Rule C run applies, and where it comes from. Configs must agree with the rule."""
    rule = _imu_noise_rule.noise(algorithm, dataset)
    source = adapters.noise_source(root, algorithm, dataset, sequence, 'vio')
    if source is None:
        return rule, 'scripts/run/_imu_noise_rule.py (' + dataset + ')'
    configured = adapters.read_effective(Path(root) / source, algorithm)
    if any(not math.isclose(configured[k], rule[k], rel_tol=1e-5) for k in KEYS):
        raise RuntimeError(f'production config disagrees with Rule C: {algorithm} {dataset} {sequence}')
    return configured, source


def noise_bounds(static, rule_c, level):
    """PLAN Update 6, per term: [min(A,C)/10, max(100C,3M)]."""
    return {k: [min(static[k], rule_c[k]) / 10, max(100 * rule_c[k], 3 * level[k])] for k in KEYS}


def run_id_plan(fold_ids, check_ids, gate_ids):
    """Fixed, disjoint inclusive blocks. Attempts take the next free ID of their block."""
    fold_blocks = {fold: [RUN_ID_FIRST + i * FOLD_BLOCK, RUN_ID_FIRST + (i + 1) * FOLD_BLOCK - 1]
                   for i, fold in enumerate(fold_ids)}
    return dict(range=[RUN_ID_FIRST, RUN_ID_LAST], fold_blocks=fold_blocks,
                check_blocks={fold: [CHECK_BLOCK_FIRST + i * SMALL_BLOCK, CHECK_BLOCK_FIRST + (i + 1) * SMALL_BLOCK - 1]
                              for i, fold in enumerate(check_ids)},
                gate_blocks={fold: [GATE_BLOCK_FIRST + i * SMALL_BLOCK, GATE_BLOCK_FIRST + (i + 1) * SMALL_BLOCK - 1]
                             for i, fold in enumerate(gate_ids)})


def motion_document(root=ROOT):
    """M per dataset, from the IMU files of this checkout's private datasets."""
    rule = _imu_noise_rule.load()
    paper = json.loads(PAPER_ENVELOPE.read_text())['sequences'] if PAPER_ENVELOPE.is_file() else {}
    datasets = {}
    for dataset, sequences in DATASETS.items():
        levels = {}
        for sequence in sequences:
            path = Path(root) / 'datasets' / dataset / sequence / 'mav0/imu0/data.csv'
            levels[sequence] = motion.sequence_levels(path)
            old = paper.get(f'{dataset}/{sequence}')
            if old:
                levels[sequence]['paper_snapshot'] = dict(gyro_q95=old['gyro_q95'], accel_q95=old['accel_q95'])
        static = rule['dataset_allan'][dataset]
        datasets[dataset] = dict(sequences=levels, M=motion.dataset_level(levels, static),
                                 random_walks_source=static['source'])
    if any(datasets['citrusfarm']['sequences'][s]['sha256'] != CORRECTED_IMU_SHA256[s] for s in DATASETS['citrusfarm']):
        raise RuntimeError('CitrusFarm M must be computed on the corrected IMU files')
    return dict(schema=1, definition=motion.DEFINITION, datasets=datasets,
                sources=dict(code='scripts/analysis/imu_motion_noise.py, the estimator of PAPER/vslam-paper/scripts/imu_envelope.py',
                             method='docs/okvis-imu-noise-derivation.md',
                             dataset_level='PAPER/vslam-paper/scripts/paperdata/noise.py _motion: largest per-sequence value',
                             check='paper_snapshot values: data/snapshot-20261102/imu-envelope.json, read from live IMU files'))


def static_source(dataset):
    """Where A comes from: the rule file that records it, then the authors' calibration."""
    rule_file = _imu_noise_rule.extension_for(dataset) or _imu_noise_rule.RULE
    source = _imu_noise_rule.load()['dataset_allan'][dataset]['source']
    return f'{Path(rule_file).relative_to(_imu_noise_rule.RULE.parents[2])}: {source}'


def study_record(root, algorithm, dataset, level, static):
    sequences = DATASETS[dataset]
    values = [effective_rule_c(root, algorithm, dataset, sequence) for sequence in sequences]
    if values[0][0] != values[1][0]:
        raise RuntimeError(f'Rule C differs between sequences: {algorithm} {dataset}')
    rule_c, source = values[0]
    return dict(id=f'{algorithm}_{dataset}', algorithm=algorithm, dataset=dataset,
                A=static, C=rule_c, M=level, bounds=noise_bounds(static, rule_c, level),
                sources=dict(A=static_source(dataset),
                             C=[v[1] for v in values], M='configs/experiments/' + MOTION.name))


def fold_record(study, tune, test):
    dataset, algorithm = study['dataset'], study['algorithm']
    clips = [clip_name(tune, 1), clip_name(tune, 2)]
    parents = {tune: tune, test: test, clips[0]: tune, clips[1]: tune}
    return dict(id=f"{study['id']}__tune_{tune}", study=study['id'], algorithm=algorithm, dataset=dataset,
                tune_sequence=tune, test_sequence=test, clips=clips, full_sequences=[tune], test_sequences=[test],
                sequence_parents=parents, supports_lc=algorithm not in adapters.VIO_ONLY,
                final_modes=['vio'] if algorithm in adapters.VIO_ONLY else ['vio', 'vio-lc'],
                controls=[dict(label='rule_c', params=study['C'], source=study['sources']['C'][0]),
                          dict(label='motion', params=study['M'], source=study['sources']['M'])],
                bounds=study['bounds'], lanes=SYSTEM_LANES[algorithm])


def protocol(root, views, level_document):
    rule = _imu_noise_rule.load()
    studies, folds = [], []
    for dataset, sequences in DATASETS.items():
        static = {k: float(rule['dataset_allan'][dataset][k]) for k in KEYS}
        for algorithm in SYSTEMS:
            study = study_record(root, algorithm, dataset, level_document['datasets'][dataset]['M'], static)
            studies.append(study)
            folds += [fold_record(study, sequences[0], sequences[1]), fold_record(study, sequences[1], sequences[0])]
    by_dataset = {d: [f for f in folds if f['dataset'] == d] for d in DATASETS}
    check = {d: [next(f['id'] for f in items if f['algorithm'] == a) for a in SYSTEMS] for d, items in by_dataset.items()}
    repro = [dict(algorithm=a, fold=f'{a}_citrusfarm__tune_seq04', sequence='seq04', expected_m=REPRO_TARGETS[a])
             for a in REPRO_TARGETS]
    overlaps = {f'{d}/{s}': v['overlap_s'] for d, seqs in views.items() for s, v in seqs.items() if v['overlap_s'] > 0}
    return dict(
        schema=1, status='DRAFT_NOT_FROZEN', campaign_id=CAMPAIGN, development_only=True, source_plan=
        'PROGRESS/IMU-TIMING-TUNE/PLAN.md, Update 6, Job C', worktree=str(ROOT), main_root=str(MAIN),
        run_order=RUN_ORDER, max_wall_hours=120,
        screen=SCREEN, full=FULL, test_later=dict(repetitions=[2, 3], mode='vio'),
        studies=studies, folds=folds, views=views,
        input_variants=dict(
            citrusfarm={s: dict(variant='corrected', imu_sha256=CORRECTED_IMU_SHA256[s],
                                path=f'datasets/.timing-imu/citrusfarm__{s}/corrected/data.csv') for s in DATASETS['citrusfarm']},
            hortimulti={s: dict(variant='authors_unchanged') for s in DATASETS['hortimulti']},
            rosariov2={s: dict(variant='authors_unchanged') for s in DATASETS['rosariov2']}),
        range_rule='[min(A,C)/10, max(100C,3M)] per term, frozen for a study, the same in both of its folds.',
        starting_candidates='C and M, enqueued first in both seeds and in the full stage.',
        cross_fit='Each study runs twice: tune on one sequence and test on the other, then the reverse.',
        repeated_selection=('Top two full candidates plus C and M, deduplicated by exact parameter vector, receive N=3 '
                            'on the tuning sequence. The selected candidate minimizes the same declared score.'),
        test=('The frozen winner runs N=1 in VIO and N=1 in VIO-LC where supported on the other sequence. Later, two '
              'more VIO repetitions reach N=3 on the same commit and worktree. Test runs never feed selection.'),
        score=('10 * failed_observation_count + 0.5 * mean(residual) + 0.5 * max(residual); residual = '
               'RMSE/(reference_path_length+RMSE) + unsupported_export_fraction. Existing numerical and 90% '
               'export-support gates retained. Lower is better.'),
        run_ids=run_id_plan([f['id'] for f in folds], [i for d in RUN_ORDER for i in check[d]],
                            [r['fold'] for r in repro]),
        gates=dict(check_folds=check, repro=dict(targets=repro, relative_tolerance=.10,
                   source='PROGRESS/IMU-TIMING-TUNE/results.csv, cohort timing-corrected-20261031, median of 3')),
        runtime_environment=dict(cuvslam={'CUVSLAM_CONDA_ENV': '/data/imoroz/conda/envs/cuvslam'},
                                 mast3r_fusion={'MAST3R_FUSION_CONDA_ENV': '/data/imoroz/conda/envs/mast3r_fusion'}),
        runtime_environment_by_study={},
        delivery_policy=dict(openvins_pending_camera_tail=None, openvins_end_of_stream_drain=True,
                             openvins_flow_control=True, openvins_transport_profile='large_shm',
                             voxel_camera_rate_gate=('Audit the expected native timestamp gate from its recorded '
                                                     'frequency; do not change sampling or accept unexplained missing input.'),
                             basis='exact native receipts; never chosen using ATE'),
        attempt_timeouts_s=TIMEOUTS_S,
        attempt_resource_limits={a: dict(GPU_LIMITS if a in GPU_SYSTEMS else CPU_LIMITS) for a in SYSTEMS},
        wall_estimates_s={d: {a: dict(zip(('clip', 'vio', 'vio-lc'), v)) for a, v in table.items()}
                          for d, table in WALL_ESTIMATES_S.items()},
        lanes=dict(cpu_a=dict(cpus='0-3', memory_gib=64, core_type='P'), cpu_b=dict(cpus='4-7', memory_gib=64, core_type='P'),
                   gpu=dict(cpus='16-23', memory_gib=50, gpu=True, core_type='E'),
                   exclusive=dict(cpus='0-7', memory_gib=64, idle_host=True, core_type='P')),
        launch_policy=dict(min_available_gib=40, no_host_swap_use=True, min_disk_free_gib=100,
                           poll_s=30, sample_s=5, max_affinity_corrections=3),
        scheduling=dict(resource_class={a: 'gpu' if a in GPU_SYSTEMS else 'cpu' for a in SYSTEMS},
                        same_algorithm_concurrent=['orbslam3'],
                        develop=('One fold per lane at a time, one attempt per lane; a fold keeps to its declared lanes. '
                                 'An exclusive fold starts only after every other fold, with the host idle.'),
                        test='Same lanes, after every selection of the dataset is frozen.'),
        disclosures=['Range constants were checked against the first search: the plan compared old selected values '
                     'with candidate ranges before freezing this one. Under [min(A,C)/10, max(100C,3M)] one old winner '
                     'falls outside (AirSLAM Rosario, selection score 0.0142 to 0.0156).',
                     'strawberry03 is 242 s, so its two 180-s clips overlap: ' + json.dumps(overlaps) + ' seconds.'],
        limitations=['Each recording was inspected before, in Rule C and in the first search.',
                     'M reads the IMU of both sequences of a dataset, so a fold\'s range knows its test sequence\'s IMU '
                     'level. It reads no trajectory and no reference.',
                     'Two clips probe short-horizon behaviour; equal proposal counts, not equal CPU time.',
                     'Runtimes from concurrent lanes are labelled overlapped.'],
        decisions=_decisions(),
        exclusions=['Sielinko (zed2i): no study of this campaign may use it', 'EuRoC'],
        frozen_input_sha256={}, frozen_runtime_sha256={}, frozen_source_sha256={},
        shared_budget_file='imu-timing-search-budget.json',
        main_pins=[f'datasets/{d}/{s}/{name}' for d, sequences in DATASETS.items() for s in sequences
                   for name in ('times.txt', 'mav0/cam0/data.csv', 'mav0/cam1/data.csv', 'mav0/imu0/data.csv')],
        enforce_main_head=False,
        pending=['frozen identities', 'gates', 'readiness', "user's go"])


def _decisions():
    """Choices the plan does not settle: the most conservative reading, recorded."""
    return [
        dict(topic='Scope of M', choice='One M per dataset, the largest of both sequences, the same in both folds.',
             why='The range table in the plan was checked this way, and one range per study keeps both folds comparable.'),
        dict(topic='M random-walk terms', choice='Released random walks, equal to A for those terms.',
             why='Update 6: in-motion densities with released random walks. The plan table left them out of 3M, so '
                 'upper bounds can differ from it where 100C < 3A: MASt3R-Fusion only.'),
        dict(topic='Second clip of strawberry03', choice='180 s ending at the last image.',
             why='A window starting at its 121-s midpoint would hold 121 s. Update 6 fixes 180 s and discloses overlap.'),
        dict(topic='Tuning stage sizes', choice='Screen startup 8 and full seed candidates 6, unchanged from the earlier '
             'searches; C and M count inside the 12 and the 10.', why='Update 6 sets only the totals.'),
        dict(topic='Preliminary stage', choice='Dropped.', why='Update 6 lists no such stage; section 4 Speed drops it.'),
        dict(topic='Same algorithm in two lanes', choice='Forbidden except ORB-SLAM3, as in the Rule C controller.',
             why='Native outputs share names by sequence and container.'),
        dict(topic='Basalt lane', choice='Cores 0-7 with the host idle, last in each dataset.', why='As Rule C and Sielinko.'),
        dict(topic='GPU lane memory', choice='50 GiB with MemoryHigh 40 GiB for all three GPU systems.', why='As the Rule C controller.'),
        dict(topic='VIO-LC of a clip', choice='Clips run VIO only.', why='Selection is VIO; LC appears only in the test.'),
        dict(topic='Rule C baselines on test sequences', choice='None in this campaign.', why='Update 6 lists none; corrected '
             'Rule C results exist.'),
        dict(topic='Budget', choice='120 h per dataset, as Sielinko, so the review between datasets spends none.',
             why='Update 6 sets no limit.'),
        dict(topic='AirSLAM VIO-LC hours', choice='Twice its VIO time in the dry plan.', why='The first search has no measured value.'),
        dict(topic='Lane handover', choice='Removed: no lane owner exists after Rule C closed. Lane checks stay.',
             why='Sielinko needed a written handover from the Rule C runner, which is gone.'),
        dict(topic='Gate tolerance', choice='10 % against the Rule C median.', why='Update 3 regression limit.'),
        dict(topic='P-core lanes only (amendment, 3 Nov 2026)',
             choice=('2 CPU + 1 GPU: lanes 0-3 and 4-7 run every CPU system, including OpenVINS, Voxel-SVIO and SVO Pro. '
                     'GPU lane 16-23. Basalt alone on 0-7. Voxel-SVIO keeps one private container, whose CPU set is moved to '
                     'the lane before each of its attempts; it never runs twice at once.'),
             why=('User decision of 3 Nov 2026. Under real load the E-core lanes mostly reproduced Rule C, but one Voxel-SVIO run on '
                  '8-11 moved 10.8 %, and E-cores would mix core types in the held-out comparison with Rule C. These are the lanes '
                  'Rule C and Job B used, so no new lane gate. It replaces the freezes 47f45ddb (lane 8-11) and a7f801bd (8-11 and '
                  '12-15); their gate and check runs, IDs 76000-76413, stay on disk. During the search a single run that differs '
                  'from earlier values is a result to report, not a reason to stop.')),
        dict(topic='Activation per dataset', choice='Readiness covers the folds of the dataset being started only.',
             why='Clips ran only on CitrusFarm; HortiMulti and Rosario are not validated and must not be claimed ready.'),
    ]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True)


def view_data(root=ROOT):
    views = {}
    for dataset, sequences in DATASETS.items():
        views[dataset] = {}
        for sequence in sequences:
            records, overlap = view_records(read_times(Path(root) / 'datasets' / dataset / sequence / 'times.txt'))
            views[dataset][sequence] = dict(clips={str(k): v for k, v in records.items()}, overlap_s=overlap,
                                            names=[clip_name(sequence, n) for n in records])
    return views


def source_identity(algorithm):
    """The digest _capture_implementation.capture compares with VSLAM_EXPECTED_SOURCE_SHA256."""
    import _capture_implementation as implementation
    store = ROOT / 'results/.implementation-blobs/sha256'
    trees = [dict(role='workspace', **implementation.capture_tree(ROOT, ROOT, store, scope=('scripts', 'configs', '.gitmodules')))]
    name = implementation.SOURCES[algorithm]
    if name:
        tree = ROOT / 'src' / name
        if not (tree / '.git').exists():
            raise RuntimeError('private source link missing (run timing-search/setup_private.sh): ' + str(tree))
        trees.append(dict(role='algorithm', **implementation.capture_tree(ROOT, tree, store)))
    return hashlib.sha256(json.dumps(trees, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def verify_input_selection(root=ROOT):
    """CitrusFarm reads the corrected IMU files; HortiMulti and Rosario read the live, unchanged ones."""
    for sequence, expected in CORRECTED_IMU_SHA256.items():
        link = Path(root) / 'datasets/citrusfarm' / sequence / 'mav0/imu0'
        if os.readlink(link) != f'../../../.timing-imu/citrusfarm__{sequence}/corrected' or motion.sha(link / 'data.csv') != expected:
            raise RuntimeError('CitrusFarm is not on the corrected IMU file: ' + sequence)
    for dataset in ('hortimulti', 'rosariov2'):
        for sequence in DATASETS[dataset]:
            path = f'datasets/{dataset}/{sequence}/mav0/imu0/data.csv'
            if motion.sha(Path(root) / path) != motion.sha(MAIN / path):
                raise RuntimeError('IMU differs from the authors\' values in the live dataset: ' + path)


def used_run_ids(root):
    return [p for p in Path(root).glob('results/*/*/*/*/run7[0-9][0-9][0-9][0-9]')]


def freeze(art):
    """Freeze into the artifact directory; refuses a dirty checkout or a changed earlier freeze."""
    import _capture_inputs
    import _capture_runtime
    import noise_execution_policy
    art = Path(art).resolve()
    if MAIN.resolve() in art.parents or art == MAIN.resolve():
        raise RuntimeError('campaign artifacts must be outside the main checkout')
    if git('status', '--porcelain', '--', 'scripts', 'configs').strip():
        raise RuntimeError('commit every script and config change before freezing')
    verify_input_selection()
    taken = [p for p in used_run_ids(MAIN) + used_run_ids(ROOT)
             if not SUPERSEDED_FREEZE_IDS[0] <= int(p.name[3:]) <= SUPERSEDED_FREEZE_IDS[1]]
    if taken:
        raise RuntimeError('run IDs in the reserved range already exist: ' + str(taken[:5]))
    value = json.loads(PROTOCOL.read_text())
    sequences = sorted({(f['dataset'], s) for f in value['folds'] for s in f['sequence_parents']})
    for dataset, parents in value['views'].items():
        for parent, view in parents.items():
            for number, record in view['clips'].items():
                name = clip_name(parent, number)
                if sha(ROOT / 'datasets' / dataset / name / 'times.txt') != record['times_sha256']:
                    raise RuntimeError('view differs from the draft protocol: ' + name)
    os.environ.update({k: v for env in value['runtime_environment'].values() for k, v in env.items()})
    _capture_runtime.ALGORITHM_ENVS.update({a: '/data/imoroz/conda/envs/' + a for a in ('cuvslam', 'mast3r_fusion')})
    value.update(status='FROZEN', frozen_at=datetime.now(timezone.utc).isoformat(), pending=['gates', 'readiness', "user's go"],
                 frozen_input_sha256={f'{d}/{s}': _capture_inputs.identity(ROOT, d, s)['sha256'] for d, s in sequences},
                 frozen_source_sha256={a: source_identity(a) for a in SYSTEMS})
    runtime = {}
    for algorithm in SYSTEMS:
        identity = _capture_runtime.identity(ROOT, algorithm)
        if identity['missing']:
            raise RuntimeError(algorithm + ' runtime incomplete: ' + '; '.join(identity['missing']))
        runtime[algorithm] = identity['sha256']
    value['frozen_runtime_sha256'] = runtime
    pins = {path: sha(MAIN / path) for path in value['main_pins']}
    main_before = dict(main_head=subprocess.check_output(['git', '-C', str(MAIN), 'rev-parse', 'HEAD'], text=True).strip(),
                       sha256=pins, enforce_main_head=value['enforce_main_head'],
                       note='Only the main files this search reads are pinned; images are hashed per attempt.')
    art.mkdir(parents=True, exist_ok=True)
    targets = {'protocol.json': json_text(value), 'main-before.json': json_text(main_before)}
    for name in targets:
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


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', nargs='?', choices=('plan', 'motion', 'protocol', 'views', 'freeze'), default='plan')
    parser.add_argument('--art', type=Path, help='campaign artifact directory (freeze)')
    args = parser.parse_args()
    if ROOT.resolve() == MAIN.resolve():
        raise RuntimeError('run only from the isolated search checkout')
    if args.action == 'plan':
        print(json_text(view_data()))
    elif args.action == 'motion':
        MOTION.parent.mkdir(parents=True, exist_ok=True)
        MOTION.write_text(json_text(motion_document()))
        print(MOTION)
    elif args.action == 'views':
        print(json_text(make_views(ROOT)))
    elif args.action == 'freeze':
        if not args.art:
            parser.error('freeze needs --art')
        print(json_text(freeze(args.art)))
    else:
        views = view_data()
        write_selectors(ROOT, views)
        value = json_text(protocol(ROOT, views, json.loads(MOTION.read_text())))
        if PROTOCOL.exists() and PROTOCOL.read_text() != value:
            print('draft protocol changed:', PROTOCOL, file=sys.stderr)
        PROTOCOL.parent.mkdir(parents=True, exist_ok=True)
        PROTOCOL.write_text(value)
        print(PROTOCOL)


if __name__ == '__main__':
    main()
