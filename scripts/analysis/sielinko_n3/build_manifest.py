#!/usr/bin/env python3
"""Build the frozen N=3 manifests (Update 10 B, C, D search) for the two Sielinko campaigns.

Reads only finished campaign records; writes only under /data/imoroz/sielinko-n3-20261110/<campaign>/.
Never launches anything and never writes to a frozen worktree.

  python -B build_manifest.py [--out DIR] [--campaign cpu|gpu ...]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = 'sielinko_n3'

from .common import (DATASET, FULL, GIB, H2, OUT, LIVE_REPO, PHASE, boot_id, config_environment_names, dumps,
                     load, load_frozen_module, logical_key, manifest_sidecar, native_seed, now, run_dir, run_id, sha,
                     unit_name)
from .identity import container_projection

I = Path('/data/imoroz')
CPU_ROOT = I / 'vslam-sielinko-search-20261022'
GPU_ROOT = I / 'vslam-sielinko-gpu-search-20261026'
CPU_ART = I / 'sielinko-cpu-search-20261024'
GPU_ART = I / 'sielinko-gpu-search-20261026'
SUPP = I / 'sielinko-supplemental-validation-20261028'
AIR_LC = I / 'airslam-lc-completion-20261029/extended-selected/phase120'
AIR_LC_WORKER = AIR_LC / 'workers/air-selected-zed2i-field1_110426_full_10fps_q90-full-vio-lc-n1'

CAMPAIGNS = {
    'cpu': dict(campaign_id='sielinko-cpu-search-20261022', root=CPU_ROOT, commit='2b70664e3cafa65b7e901a475fd3955a53f3425b',
                art=CPU_ART),
    'gpu': dict(campaign_id='sielinko-gpu-search-20261026', root=GPU_ROOT, commit='26a9d3086e4fd2339ee3e05e66ae4deb961ec830',
                art=GPU_ART),
}
# System -> lane as its first test runs used it, and its VIO-LC treatment.
SYSTEMS = {
    'cpu': {
        'orbslam3': dict(lane='lane1', lc=('C', [2, 3], SUPP / 'workers/orbslam3-full-vio-lc-n1')),
        'okvis2': dict(lane='lane2', lc=('C', [2, 3], SUPP / 'workers/okvis2-full-vio-lc-n1')),
        'okvis2x': dict(lane='lane1', lc=('D-search', [1, 2, 3], None)),
        'openvins': dict(lane='lane2', lc=None),
        'voxel_svio': dict(lane='lane2', lc=None),
        'svo_pro': dict(lane='lane1', lc=('C', [1, 2, 3], None)),
        'basalt': dict(lane='exclusive', lc=None),
    },
    'gpu': {
        'airslam': dict(lane='gpu', lc=('C', [2, 3], AIR_LC_WORKER)),
        'cuvslam': dict(lane='gpu', lc=('C', [2, 3], SUPP / 'workers/cuvslam-full-vio-lc-n1')),
        'mast3r_fusion': dict(lane='gpu', lc=('C', [2, 3], SUPP / 'workers/mast3r_fusion-full-vio-lc-n1')),
    },
}
GPU_TASKSET = '20,21,22,23'          # gpu6.bounded()
GPU_HERE = {'final': GPU_ART, 'supp': SUPP / 'gpu', 'air_lc': AIR_LC / 'adapter-sielinko-validation'}
GPU_LOCK = LIVE_REPO / 'results/.locks/gpu-execution.lock'   # gpu6.LOCK; opened read-only, never created
CONTAINERS = {
    'voxel_svio': dict(name='sielinko_search_voxel_20261022',
                       record=SUPP / 'container-recovery/sielinko_search_voxel_20261022-after.json', cross=None),
    'airslam': dict(name='sielinko_gpu_airslam_20261026',
                    record=SUPP / 'container-recovery/sielinko_gpu_airslam_20261026-after.json',
                    cross=GPU_ART / 'air-private-container-identity.json'),
}
REPEATABLE = {'basalt', 'mast3r_fusion', 'cuvslam'}   # 1 % reproduction check (engineer, 10 Nov)
D_TIMEOUT_S, D_MEMORY_GIB = 28800, 64
BUDGET_HOURS = 120
DISCLOSURE = (
    'Update 10 B/C/D-search repetitions run under a new, manifest-driven dispatcher '
    '(branch eng/sielinko-n3-20261110), not the original campaign engines/controllers. They call the same '
    'scripts/run/run_<alg>.sh and the same frozen evaluator in the unchanged Sielinko worktrees '
    '(CPU 2b70664, GPU 26a9d30) with the first runs\' environment, parameter files, inputs, containers and limits. '
    'The GPU campaign\'s main-head pin (57332d5) is dropped for this dispatcher; the GPU worktree is unchanged at '
    '26a9d30 and main\'s move to 0dbc8b1 does not touch it. Fresh 120 h budget per campaign (user-approved). '
    'The user approved pooling these repetitions with their first runs as one cohort on 10 Nov 2026 '
    '(agents/mailbox/runner.md, 2026-11-10 23:00 UTC).')


def worker_record(worker, key):
    path = Path(worker) / 'attempts' / (key + '.json')
    if not path.is_file():
        raise RuntimeError('Reference record missing: ' + str(path))
    return path


def only_record(worker):
    found = sorted((Path(worker) / 'attempts').glob('*.json'))
    if len(found) != 1:
        raise RuntimeError('Expected one reference attempt in ' + str(worker))
    return found[0]


def pin(role, path):
    return dict(role=role, path=str(path), sha256=sha(path))


def frozen_call(root, code, *args):
    """Evaluate pure helper code inside the frozen worktree's modules (python -B, no writes)."""
    result = subprocess.run([sys.executable, '-B', '-c', code, str(root), *args], capture_output=True, text=True,
                            timeout=120, check=True)
    return json.loads(result.stdout)


MATERIALIZE = r'''
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); sys.path[:0] = [str(root / 'scripts/analysis'), str(root / 'scripts/run')]
import noise_adapters as a
algorithm, dataset, parent, mode, destination = sys.argv[2:7]
parameters = a.validate_parameters(json.loads(sys.argv[7]))
destination = Path(destination)
sources, files, env = [], {}, {}
def source(relative):
    sources.append(dict(path=relative, sha256=a.sha(root / relative))); return root / relative
if algorithm == 'svo_pro':
    files['noise.json'] = a.json_text(a.document(algorithm, dataset, parameters))
    env['SVO_PRO_IMU_NOISE'] = str(destination / 'noise.json')
    env['SVO_PRO_IMU_FILE'] = str(source(f'configs/okvis2/{dataset}_{parent}_vio.yaml'))
elif algorithm == 'okvis2x':
    relative = f'configs/{algorithm}/{dataset}_{parent}_{mode.replace("-", "_")}.yaml'
    files['estimator.yaml'] = a.replace_scalars(source(relative).read_text(), a.OKVIS_KEYS, parameters)
    env['OKVIS2X_CONFIG'] = str(destination / 'estimator.yaml')
else:
    raise SystemExit('unsupported materialization')
print(json.dumps(dict(parameters=parameters, sources=sources, texts=files, environment=env)))
'''


def materialized_config(root, campaign_id, study, algorithm, label, parameters, mode, out_dir):
    """Expected candidate of adapters.prepare() for a mode that never ran (bytes only, nothing written there)."""
    destination = Path(root) / 'configs/experiments/generated' / campaign_id / study / label / FULL / mode
    value = frozen_call(root, MATERIALIZE, algorithm, DATASET, FULL, mode, str(destination), json.dumps(parameters))
    files = []
    review = Path(out_dir) / 'candidates' / study / label / mode
    review.mkdir(parents=True, exist_ok=True)
    for name, text in value['texts'].items():
        (review / name).write_text(text)
        files.append(dict(path=str(destination / name), sha256=sha(review / name), review_copy=str(review / name)))
    receipt = dict(schema=1, algorithm=algorithm, dataset=DATASET, parent_sequence=FULL, mode=mode,
                   parameters=value['parameters'],
                   sources=[dict(path=s['path'], sha256=s['sha256']) for s in value['sources']],
                   files=[dict(path=f['path'], sha256=f['sha256']) for f in files],
                   environment=value['environment'], mode_materialization=[])
    return dict(mode='materialize', destination=str(destination), sources=value['sources'], files=files,
                environment=value['environment'], expected_receipt=receipt,
                note='Generated at execution by the frozen noise_adapters.prepare() into the campaign\'s '
                     'gitignored generated-config tree; bytes must equal files[].sha256.')


def reused_config(candidate):
    return dict(mode='reuse', sources=candidate['sources'],
                files=[dict(path=f['path'], sha256=f['sha256']) for f in candidate['files']],
                environment=candidate['environment'])


def provenance(run):
    base = Path(run) / 'provenance'
    return {kind: dict(path=str(base / name), sha256=sha(base / name)) for kind, name in
            (('implementation', 'implementation.json'), ('inputs', 'inputs.json'), ('runtime', 'runtime-assets.json'))}


def trees_digest(path):
    return frozen_digest(load(path)['trees'])


def frozen_digest(value):
    import hashlib
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def build_items(kind, out_dir):
    meta = CAMPAIGNS[kind]
    root, campaign_id = meta['root'], meta['campaign_id']
    items = []
    policy_mod = load_frozen_module(root / 'scripts/analysis/noise_execution_policy.py', 'frozen_policy_' + kind)
    removed = config_environment_names(root / 'scripts/analysis/noise_campaign_engine.py')
    for algorithm, system in SYSTEMS[kind].items():
        study = algorithm + '_zed2i'
        worker = meta['art'] / 'workers' / study
        protocol_path = worker / 'protocol.json'
        protocol = load(protocol_path)
        selection_path = worker / 'studies' / study / 'selection.json'
        winner = load(selection_path)['winner']
        tests = [('B', 'h2_sel', winner['label'], H2, 'vio', [2, 3], worker_record(worker, logical_key('final_n1', study, winner['label'], H2, 'vio', 1))),
                 ('B', 'h2_aop', 'rule_c', H2, 'vio', [2, 3], worker_record(worker, logical_key('final_n1', study, 'rule_c', H2, 'vio', 1))),
                 ('B', 'full_sel', winner['label'], FULL, 'vio', [2, 3], worker_record(worker, logical_key('final_n1', study, winner['label'], FULL, 'vio', 1)))]
        if system['lc']:
            group, reps, lc_worker = system['lc']
            ref = only_record(lc_worker) if lc_worker else tests[2][6]
            tests.append((group, 'full_sel_lc', winner['label'], FULL, 'vio-lc', reps, ref))
        for group, test, label, sequence, mode, reps, ref_path in tests:
            ref = load(ref_path)
            ref_dir = ref_path.parent.parent
            ref_protocol_path = ref_dir / 'protocol.json'
            ref_protocol = load(ref_protocol_path)
            if ref['mode'] == mode:
                # The reference ran this exact test: its own protocol defines environment and limits.
                env_protocol, env_protocol_path = ref_protocol, ref_protocol_path
                parameters, ref_kind = ref['params'], 'first_run_of_this_test'
            else:
                # SVO Pro / OKVIS2-X VIO-LC never ran: the VIO winner's full VIO run anchors identity.
                env_protocol, env_protocol_path = protocol, protocol_path
                parameters, ref_kind = winner['params'], 'vio_winner_full_vio_run_no_lc_first_run'
            if ref['params'] != parameters or ref['label'] != label or ref['sequence'] != sequence:
                raise RuntimeError('Reference record does not match the frozen test: ' + str(ref_path))
            if parameters != (winner['params'] if label == winner['label'] else
                              next(c['params'] for c in next(s for s in protocol['studies'] if s['id'] == study)['controls'] if c['label'] == label)):
                raise RuntimeError('Parameters differ from the frozen winner/control: ' + study + ' ' + label)
            spec = next(s for s in env_protocol['studies'] if s['id'] == study)
            role = spec['sequence_roles'][sequence]
            timeout = env_protocol['attempt_timeouts_s'][algorithm][role]
            limits = dict(env_protocol['attempt_resource_limits'][algorithm])
            if group == 'D-search':
                timeout, limits['memory_gib'] = D_TIMEOUT_S, D_MEMORY_GIB
            elif ref['mode'] == mode and timeout != ref['timeout_limit_s']:
                raise RuntimeError('Timeout differs from the reference attempt: ' + str(ref_path))
            if ref['mode'] == mode:
                config = reused_config(ref['candidate'])
            else:
                config = materialized_config(root, campaign_id, study, algorithm, label, parameters, mode, out_dir)
            ident = load(ref_dir / 'execution-identity.json')
            eval_python = ident['controller_environment']['executable']
            here = None
            if kind == 'gpu':
                here = GPU_HERE['final'] if ref['phase'] == 'final_n1' else (GPU_HERE['air_lc'] if algorithm == 'airslam' else GPU_HERE['supp'])
            for rep in reps:
                key = logical_key(PHASE, study, label, sequence, mode, rep)
                rid = run_id(campaign_id, key)
                seed = native_seed(campaign_id, study, sequence, PHASE, rep) if algorithm == 'mast3r_fusion' else None
                item_id = f'{group}-{algorithm}-{test}-r{rep}'
                audit_dir = out_dir / 'attempt-audits' / str(rid)
                # Environment, in the engine's order (noise_campaign_engine.run_attempt).
                env = dict(PYTHONDONTWRITEBYTECODE='1', BENCHMARK_EVAL_PYTHON=eval_python, AIRSLAM_STAGE_TIMEOUT_S='3600')
                runtime = dict(env_protocol['runtime_environment'].get(algorithm, {}))
                if kind == 'gpu':   # gpu6.guarded_run() adds these to runtime_environment[algorithm]
                    runtime.update(GPU6_AUDIT_DIR=str(audit_dir), GPU6_MEMORY_BYTES=str(limits['memory_gib'] * GIB),
                                   GPU6_MEMORY_HIGH_BYTES=str(limits['memory_high_gib'] * GIB),
                                   PYTHONPATH=str(here / 'instrumentation'), PYTHONDONTWRITEBYTECODE='1')
                env.update(runtime)
                env.update(env_protocol.get('runtime_environment_by_study', {}).get(study, {}))
                lane = system['lane']
                if kind == 'cpu':
                    env.update(policy_mod.lane_environment(env_protocol, algorithm, lane))
                env.update(config['environment'])
                env.update(policy_mod.identity_environment(env_protocol, algorithm, DATASET, sequence))
                if seed is not None:
                    env['MAST3R_FUSION_SEED'] = str(seed)
                prepend = dict(LD_LIBRARY_PATH=str(root / 'src/ORB_SLAM3/Thirdparty/DBoW2/lib'))
                inner = ['bash', str(root / f'scripts/run/run_{algorithm}.sh'), DATASET, sequence, str(rid), mode]
                bound = dict(env_protocol, campaign_id=campaign_id,
                             attempt_resource_limits={algorithm: dict(limits, swap_gib=0)})
                if kind == 'cpu':
                    command = policy_mod.bounded_command(inner, bound, algorithm, rid, env, lane=lane)
                    cpus = env_protocol['lanes'][lane]['cpus']
                else:
                    command = policy_mod.bounded_command(['taskset', '--cpu-list', GPU_TASKSET, *inner], bound, algorithm, rid, env)
                    index = command.index('taskset')
                    command[index:index] = ['-p', 'MemoryHigh=' + str(limits['memory_high_gib']) + 'G']
                    cpus = GPU_TASKSET
                if command[4] != '--unit=' + unit_name(campaign_id, rid):
                    raise RuntimeError('Unexpected scope unit')
                out_run = run_dir(root, mode, DATASET, sequence, algorithm, rid)
                container = None
                if algorithm in CONTAINERS:
                    c = CONTAINERS[algorithm]
                    identity = container_projection(load(c['record']))
                    if c['cross']:
                        cross = load(c['cross'])
                        if (cross['container_id'], cross['image_id'], cross['cpuset_cpus'], cross['memory_bytes']) != (
                                identity['Id'], identity['Image'], identity['CpusetCpus'], identity['Memory']):
                            raise RuntimeError('Recorded container identities disagree: ' + c['name'])
                    container = dict(name=c['name'], identity=identity, identity_source=str(c['record']),
                                     identity_source_sha256=sha(c['record']), start='docker start (never docker run/create)',
                                     effective_cgroup=dict(memory_max=str(identity['Memory']), memory_swap_max='0',
                                                           cpuset=identity['CpusetCpus']))
                    if container['identity']['CpusetCpus'] != (cpus if kind == 'cpu' else '20-23'):
                        raise RuntimeError('Container cpuset differs from the lane')
                prov = provenance(ref['run'])
                frozen_identity = dict(implementation=env_protocol['frozen_source_sha256'][algorithm],
                                       runtime=env_protocol['frozen_runtime_sha256'][algorithm],
                                       inputs=env_protocol['frozen_input_sha256'][DATASET + '/' + sequence])
                if trees_digest(prov['implementation']['path']) != frozen_identity['implementation'] or \
                        load(prov['runtime']['path'])['sha256'] != frozen_identity['runtime'] or \
                        load(prov['inputs']['path'])['sha256'] != frozen_identity['inputs']:
                    raise RuntimeError('Reference provenance differs from the frozen campaign identity: ' + ref['run'])
                result = ref.get('result', {})
                evidence = [pin('reference_record', ref_path), pin('reference_protocol', ref_protocol_path),
                            pin('env_protocol', env_protocol_path), pin('selection', selection_path)]
                evidence += [pin('provenance_' + k, v['path']) for k, v in prov.items()]
                if container:
                    evidence.append(pin('container_identity', container['identity_source']))
                auditor = None
                if kind == 'gpu':
                    auditor = dict(here=str(here), module=str(here / 'gpu6.py'))
                    for name in ('gpu6.py', 'guard_replacement.py', 'pressure_windows.py', 'parent_alerts.py',
                                 'admission.py', 'instrumentation/sitecustomize.py', 'instrumentation/gpu6_observe.py'):
                        if (here / name).is_file():
                            evidence.append(pin('gpu_auditor:' + name, here / name))
                admission = dict(exclusive_host=lane == 'exclusive', requires_no_gpu_jobs=lane == 'exclusive' or kind == 'gpu' or group == 'D-search',
                                 gpu=kind == 'gpu', requires_cpu_idle=algorithm == 'airslam', one_at_a_time=group == 'D-search',
                                 gpu_lock=str(GPU_LOCK) if kind == 'gpu' else None)
                items.append(dict(
                    id=item_id, group=group, system=algorithm, algorithm=algorithm, study=study, dataset=DATASET,
                    test=test, view='h2' if sequence == H2 else 'full', sequence=sequence, mode=mode, repetition=rep,
                    label=label, parameters=parameters, campaign_id=campaign_id, phase=PHASE, key=key, run_id=rid,
                    native_seed=seed, unit=unit_name(campaign_id, rid), run_dir=str(out_run),
                    worktree=dict(path=str(root), commit=meta['commit']),
                    lane=dict(name=lane, cpus=cpus), container=container, timeout_s=timeout,
                    memory=dict(max_gib=limits['memory_gib'], high_gib=limits.get('memory_high_gib'), swap_max=0),
                    config=config,
                    environment=dict(base='dispatcher environment with the engine CONFIG_ENVIRONMENT names removed',
                                     removed=removed, set=env, prepend=prepend),
                    command=command, inner_command=inner, cwd=str(root),
                    evaluator=dict(python=eval_python, controller_environment=ident['controller_environment'],
                                   post_run='frozen noise_campaign_engine post-run (evaluate_saved_run, score, native/transport audits)'
                                            + (' + gpu6 native/resource audit' if kind == 'gpu' else ''),
                                   gpu_auditor=auditor, audit_dir=str(audit_dir) if kind == 'gpu' else None),
                    admission=admission,
                    reference=dict(kind=ref_kind, record=str(ref_path), record_sha256=sha(ref_path), key=ref['key'],
                                   campaign_id=ref['campaign_id'], run=ref['run'], returncode=ref.get('returncode'),
                                   failed=result.get('failed'), numerical_status=result.get('numerical_status'),
                                   ate_se3_rmse_m=result.get('ate_se3_rmse_m'), wall_s=ref.get('wall_s'),
                                   timeout_limit_s=ref.get('timeout_limit_s'), native_seed=ref.get('native_seed'),
                                   command=ref['command'], protocol=str(ref_protocol_path),
                                   protocol_sha256=sha(ref_protocol_path), provenance=prov),
                    repeat_check=('match_within_1pct' if algorithm in REPEATABLE and ref_kind == 'first_run_of_this_test'
                                  and result.get('failed') is False and result.get('numerical_status') == 'ok' else 'record_only'),
                    frozen_identity=frozen_identity,
                    pinned_evidence=evidence,
                    record=str(out_dir / 'attempts' / (item_id + '.json')),
                    wrapper_log=str(out_dir / 'wrapper-logs' / (item_id + '.log'))))
    return items


def build(kind, out=OUT):
    out_dir = Path(out) / kind
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / 'manifest.json'
    if manifest_path.exists():
        raise RuntimeError('Manifest already frozen; never rebuilt in place: ' + str(manifest_path))
    items = build_items(kind, out_dir)
    ids = [i['id'] for i in items]
    rids = [i['run_id'] for i in items]
    if len(set(ids)) != len(ids) or len(set(rids)) != len(rids):
        raise RuntimeError('Duplicate item or run IDs')
    for item in items:
        if Path(item['run_dir']).exists() or list(Path(item['worktree']['path']).glob('results/*/*/*/*/run' + str(item['run_id']))):
            raise RuntimeError('Run ID already used: ' + item['run_dir'])
    eng = Path(__file__).resolve().parents[3]
    head = subprocess.run(['git', '-C', str(eng), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(['git', '-C', str(eng), 'status', '--porcelain', '--', 'scripts/analysis/sielinko_n3'],
                           capture_output=True, text=True, check=True).stdout.strip()
    counts = {}
    for item in items:
        counts[item['group']] = counts.get(item['group'], 0) + 1
    meta = CAMPAIGNS[kind]
    manifest = dict(
        schema=1, kind='sielinko-n3-repetitions', campaign=kind, campaign_id=meta['campaign_id'], amendment='paper-n3-20261110',
        created_at=now(), boot_id=boot_id(), phase=PHASE,
        worktree=dict(path=str(meta['root']), commit=meta['commit']),
        dispatcher=dict(worktree=str(eng), branch='eng/sielinko-n3-20261110', commit=head, uncommitted_changes=bool(dirty)),
        budget=dict(hours=BUDGET_HOURS, file=str(out_dir / 'budget.json'),
                    rule='Fresh 120 h budget (user-approved 10 Nov 2026); starts at the first launch and is written once to file.'),
        launch_policy=dict(min_available_gib=40, min_disk_free_gib=100, poll_s=30, sample_s=5, max_affinity_corrections=3,
                           consecutive_infrastructure_failures_stop=3),
        stops=dict(stop_files=[str(out_dir / 'STOP'), str(Path(out) / 'STOP')], fault_files=[str(out_dir / 'FAULT'), str(Path(out) / 'FAULT')],
                   boot='boot id must equal manifest boot_id (host reset stops everything)'),
        disclosure=DISCLOSURE, gpu_main_head_pin=dict(previous='57332d5', dropped=True, worktree_commit='26a9d30', main_now='0dbc8b1'),
        pooling=dict(approved_by='user', at='2026-11-10T23:00Z', source='/data/imoroz/agents/mailbox/runner.md'),
        counts=counts, items=items)
    text = dumps(manifest)
    with manifest_path.open('x') as stream:
        stream.write(text)
    digest = sha(manifest_path)
    manifest_sidecar(manifest_path).write_text(digest + '  manifest.json\n')
    return manifest_path, digest, counts


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default=str(OUT))
    parser.add_argument('--campaign', action='append', choices=sorted(CAMPAIGNS))
    args = parser.parse_args(argv)
    for kind in args.campaign or sorted(CAMPAIGNS):
        path, digest, counts = build(kind, Path(args.out))
        print(path, digest, json.dumps(counts))


if __name__ == '__main__':
    main()
