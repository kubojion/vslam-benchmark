"""Tests for the Sielinko N=3 dispatcher. Nothing here launches an estimator or touches docker state."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sielinko_n3 import build_manifest, dispatch, guard, identity  # noqa: E402
from sielinko_n3.common import (GIB, logical_key, manifest_sidecar, native_seed, run_id, sha,  # noqa: E402
                                verify_manifest, write_json)

CPU = 'sielinko-cpu-search-20261022'
GPU = 'sielinko-gpu-search-20261026'
HAVE_CAMPAIGNS = build_manifest.CPU_ART.is_dir() and build_manifest.GPU_ART.is_dir()


# ------------------------------------------------------------------ run IDs

def test_run_id_reproduces_recorded_first_runs():
    key = logical_key('final_n1', 'orbslam3_zed2i', 'noise_02144057d1c4a31a', 'field1_sielinko_h2_20261022', 'vio', 1)
    assert run_id(CPU, key) == 845463665264
    key = logical_key('final_n1', 'airslam_zed2i', 'envelope', 'field1_sielinko_h2_20261022', 'vio', 1)
    assert run_id(GPU, key) == 245321943311
    assert native_seed(GPU, 'mast3r_fusion_zed2i', 'field1_sielinko_h2_20261022', 'final_n1', 1) == 24043215


def test_run_id_is_deterministic_and_phase_separated():
    a = logical_key('paper_n3', 'basalt_zed2i', 'rule_c', 'field1_sielinko_h2_20261022', 'vio', 2)
    b = logical_key('final_n1', 'basalt_zed2i', 'rule_c', 'field1_sielinko_h2_20261022', 'vio', 2)
    assert run_id(CPU, a) == run_id(CPU, a)
    assert run_id(CPU, a) != run_id(CPU, b)
    assert run_id(CPU, a) != run_id(CPU, a.replace('rep2', 'rep3'))
    assert run_id(CPU, a) > 2_000_000_000


# ------------------------------------------------------------------ manifest hash binding

def test_manifest_hash_binding(tmp_path):
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(dict(items=[])))
    digest = sha(path)
    manifest_sidecar(path).write_text(digest + '  manifest.json\n')
    assert verify_manifest(path, digest)[1] == digest
    with pytest.raises(RuntimeError, match='reviewed hash'):
        verify_manifest(path, '0' * 64)
    path.write_text(json.dumps(dict(items=[1])))
    with pytest.raises(RuntimeError, match='changed since it was frozen'):
        verify_manifest(path)
    manifest_sidecar(path).unlink()
    with pytest.raises(RuntimeError, match='sidecar missing'):
        verify_manifest(path)


# ------------------------------------------------------------------ identity gate with fake provenance

def fake_item(tmp_path, *, commit):
    repo = tmp_path / 'wt'
    (repo / 'configs').mkdir(parents=True)
    (repo / 'configs/base.yaml').write_text('a: 1\n')
    param = tmp_path / 'estimator.yaml'
    param.write_text('noise: 1\n')
    record = tmp_path / 'record.json'
    record.write_text('{}')
    impl = tmp_path / 'implementation.json'
    impl.write_text(json.dumps(dict(trees=[dict(role='workspace', commit=commit, entries=[])])))
    identity_record = dict(Id='abc', Image='sha256:img', Name='box', CpusetCpus='4-7', Memory=50 * GIB, MemorySwap=50 * GIB,
                           gpu=False, Runtime='runc', Mounts=[['/src', '/dst', False]], Env=['A=1'], Cmd=['tail'])
    return dict(
        worktree=dict(path=str(repo), commit=commit), algorithm='voxel_svio', evaluator=dict(python=sys.executable),
        reference=dict(provenance=dict(implementation=dict(path=str(impl)), runtime=dict(path='r'), inputs=dict(path='i'))),
        pinned_evidence=[dict(role='reference_record', path=str(record), sha256=sha(record))],
        config=dict(mode='reuse', sources=[dict(path='configs/base.yaml', sha256=sha(repo / 'configs/base.yaml'))],
                    files=[dict(path=str(param), sha256=sha(param))], environment={}),
        container=dict(name='box', identity=identity_record, identity_source='recorded.json'),
        frozen_identity=dict(implementation='i' * 64, runtime='r' * 64, inputs='n' * 64))


def inspect_as(identity_record, **changes):
    def inspect(name):
        value = dict(identity_record, **changes)
        return dict(Id=value['Id'], Image=value['Image'], Name='/' + value['Name'],
                    HostConfig=dict(CpusetCpus=value['CpusetCpus'], Memory=value['Memory'], MemorySwap=value['MemorySwap'],
                                    DeviceRequests=None, Runtime=value['Runtime']),
                    Mounts=[dict(Source=s, Destination=d, RW=rw) for s, d, rw in value['Mounts']],
                    Config=dict(Env=value['Env'], Cmd=value['Cmd']))
    return inspect


def test_identity_gate_passes_on_exact_identity(tmp_path):
    item = fake_item(tmp_path, commit='c' * 40)
    gate = identity.light_gate(item, head=lambda root: 'c' * 40, inspect=inspect_as(item['container']['identity']))
    assert gate.passed, gate.failures()


@pytest.mark.parametrize('mutation', ['head', 'reference_commit', 'config', 'source', 'evidence', 'image', 'cpuset', 'missing'])
def test_identity_gate_refuses_any_mismatch(tmp_path, mutation):
    item = fake_item(tmp_path, commit='c' * 40)
    head, inspect = (lambda root: 'c' * 40), inspect_as(item['container']['identity'])
    if mutation == 'head':
        head = lambda root: 'd' * 40  # noqa: E731
    elif mutation == 'reference_commit':
        Path(item['reference']['provenance']['implementation']['path']).write_text(
            json.dumps(dict(trees=[dict(role='workspace', commit='e' * 40, entries=[])])))
    elif mutation == 'config':
        Path(item['config']['files'][0]['path']).write_text('noise: 2\n')
    elif mutation == 'source':
        (Path(item['worktree']['path']) / 'configs/base.yaml').write_text('a: 2\n')
    elif mutation == 'evidence':
        Path(item['pinned_evidence'][0]['path']).write_text('{"changed": true}')
    elif mutation == 'image':
        inspect = inspect_as(item['container']['identity'], Image='sha256:other')
    elif mutation == 'cpuset':
        inspect = inspect_as(item['container']['identity'], CpusetCpus='0-7')
    elif mutation == 'missing':
        inspect = lambda name: None  # noqa: E731
    gate = identity.light_gate(item, head=head, inspect=inspect)
    assert not gate.passed


def test_full_gate_refuses_live_provenance_mismatch(tmp_path):
    item = fake_item(tmp_path, commit='c' * 40)
    item['evaluator']['controller_environment'] = dict(python='x', package_versions={})

    def verifier(root, kind, path, env, python):
        if kind == 'runtime':
            return False, 'runtime assets changed since capture'
        return True, dict(trees_sha256='i' * 64, sha256='n' * 64)
    gate = identity.full_gate(item, {}, sys.executable, head=lambda r: 'c' * 40,
                              inspect=inspect_as(item['container']['identity']), verifier=verifier)
    failed = {c['check'] for c in gate.failures()}
    assert 'live runtime equals reference provenance' in failed
    assert not gate.passed


def test_frozen_verifier_failure_is_a_refusal(tmp_path):
    fake = tmp_path / 'frozen'
    (fake / 'scripts/run').mkdir(parents=True)
    (fake / 'scripts/run/_capture_implementation.py').write_text(
        'def verify_capture(*a, **k):\n    raise ValueError("source bytes changed since capture")\n')
    ref = tmp_path / 'implementation.json'
    ref.write_text(json.dumps(dict(trees=[])))
    ok, detail = identity.run_verifier(tmp_path, 'implementation', ref, None, sys.executable, scripts_root=fake)
    assert not ok and 'source bytes changed' in detail


# ------------------------------------------------------------------ static refusals

def static_manifest(tmp_path):
    out = tmp_path / 'cpu'
    out.mkdir()
    return dict(boot_id='boot-a', budget=dict(hours=120, file=str(out / 'budget.json')),
                stops=dict(stop_files=[str(out / 'STOP')], fault_files=[str(out / 'FAULT')]))


def static_item(tmp_path):
    return dict(run_dir=str(tmp_path / 'results/run123'), record=str(tmp_path / 'cpu/attempts/x.json'), timeout_s=3600)


def test_refuses_when_run_dir_exists(tmp_path):
    manifest, item = static_manifest(tmp_path), static_item(tmp_path)
    assert dispatch.static_refusals(manifest, item, boot='boot-a') == []
    Path(item['run_dir']).mkdir(parents=True)
    assert any('run directory already exists' in r for r in dispatch.static_refusals(manifest, item, boot='boot-a'))


def test_refuses_stop_boot_and_budget(tmp_path):
    manifest, item = static_manifest(tmp_path), static_item(tmp_path)
    assert any('host restarted' in r for r in dispatch.static_refusals(manifest, item, boot='boot-b'))
    Path(manifest['stops']['fault_files'][0]).write_text('x')
    assert any('stop/fault' in r for r in dispatch.static_refusals(manifest, item, boot='boot-a'))
    Path(manifest['stops']['fault_files'][0]).unlink()
    write_json(manifest['budget']['file'], dict(started_unix=0, deadline_unix=120 * 3600))
    assert any('insufficient budget' in r for r in dispatch.static_refusals(manifest, item, boot='boot-a', clock=lambda: 119 * 3600))
    assert dispatch.static_refusals(manifest, item, boot='boot-a', clock=lambda: 100) == []


def test_item_environment_matches_engine_order():
    item = dict(environment=dict(removed=['OKVIS2X_CONFIG', 'VOXEL_SVIO_CONTAINER'], set=dict(OKVIS2X_CONFIG='/new', A='1'),
                                 prepend=dict(LD_LIBRARY_PATH='/dbow')))
    env = dispatch.item_env(item, dict(OKVIS2X_CONFIG='/stale', VOXEL_SVIO_CONTAINER='other', LD_LIBRARY_PATH='/x', PATH='/bin'))
    assert env == dict(OKVIS2X_CONFIG='/new', A='1', LD_LIBRARY_PATH='/dbow:/x', PATH='/bin')


# ------------------------------------------------------------------ swap guard and launch blockers

def run(algorithm, pid, cpus, group, mode='vio'):
    return dict(pid=pid, algorithm=algorithm, wrapper='scripts/run/run_' + algorithm + '.sh', cpus=cpus,
                cgroup='0::/' + group, mode=mode)


def test_swap_guard_ignores_idle_containers_and_units(tmp_path):
    def group(name, swap):
        path = tmp_path / name
        path.mkdir(parents=True)
        (path / 'memory.swap.current').write_text(str(swap))
        return path
    idle_voxel = group('system.slice/docker-voxel.scope', 4096)
    idle_air = group('system.slice/docker-air.scope', 8192)
    group('user.slice/app.slice/vslam-corrected-20261031.service', 1 << 20)   # idle controller unit
    group('user.slice/app.slice/noise-campaign-x-1.scope', 1 << 20)           # left-over scope
    group('user.slice/app.slice/noise-campaign-x-2.scope', 0)                 # an active run's scope
    containers = [('sielinko_search_voxel_20261022', idle_voxel), ('sielinko_gpu_airslam_20261026', idle_air)]
    orb = run('orbslam3', 10, [0, 1, 2, 3], 'user.slice/app.slice/noise-campaign-x-2.scope')
    assert guard.benchmark_swap_bytes([], containers, root=tmp_path) == 0
    assert guard.benchmark_swap_bytes([orb], containers, root=tmp_path) == 0
    voxel = run('voxel_svio', 11, [4, 5, 6, 7], 'user.slice/app.slice/noise-campaign-x-1.scope')
    # The Voxel container counts once a Voxel wrapper is active, and so does that wrapper's own scope.
    assert guard.benchmark_swap_bytes([orb, voxel], containers, root=tmp_path) == 4096 + (1 << 20)


def test_container_algorithm_mapping():
    assert guard.container_algorithm('sielinko_search_voxel_20261022') == 'voxel_svio'
    assert guard.container_algorithm('sielinko_gpu_airslam_20261026') == 'airslam'
    assert guard.container_algorithm('vslam_openvins_123') == 'openvins'
    assert guard.container_algorithm('overleaf') is None


POLICY = dict(min_available_gib=40, min_disk_free_gib=100)
HOST = dict(mem_available=100 * GIB, disk_free=500 * GIB, gpu_pids=[], swap_bytes=0)


def item_for(algorithm, cpus, **admission):
    base = dict(exclusive_host=False, requires_no_gpu_jobs=False, gpu=False, requires_cpu_idle=False, one_at_a_time=False)
    base.update(admission)
    return dict(algorithm=algorithm, lane=dict(cpus=cpus), admission=base)


def test_launch_blockers():
    orb = item_for('orbslam3', '0-3')
    assert guard.launch_blockers(orb, POLICY, runs=[], **HOST) == []
    assert guard.launch_blockers(orb, POLICY, runs=[], **dict(HOST, mem_available=39 * GIB))
    assert guard.launch_blockers(orb, POLICY, runs=[], **dict(HOST, disk_free=99 * GIB))
    assert guard.launch_blockers(orb, POLICY, runs=[], **dict(HOST, swap_bytes=1))
    assert guard.launch_blockers(orb, POLICY, runs=[run('okvis2', 1, [2, 3, 4], 'x')], **HOST)
    assert guard.launch_blockers(orb, POLICY, runs=[run('okvis2', 1, [4, 5, 6, 7], 'x')], **HOST) == []
    assert guard.launch_blockers(orb, POLICY, runs=[run('basalt', 1, list(range(8, 16)), 'x')], **HOST)
    assert guard.launch_blockers(orb, POLICY, runs=[run('airslam', 1, [20, 21, 22, 23], 'x')], **HOST)
    basalt = item_for('basalt', '0-7', exclusive_host=True, requires_no_gpu_jobs=True)
    assert guard.launch_blockers(basalt, POLICY, runs=[run('cuvslam', 1, [20, 21, 22, 23], 'x')], **HOST)
    assert guard.launch_blockers(basalt, POLICY, runs=[], **dict(HOST, gpu_pids=[5]))
    assert guard.launch_blockers(basalt, POLICY, runs=[], **dict(HOST, gpu_pids=None))
    assert guard.launch_blockers(basalt, POLICY, runs=[], **HOST) == []
    d = item_for('okvis2x', '0-3', requires_no_gpu_jobs=True, one_at_a_time=True)
    assert guard.launch_blockers(d, POLICY, runs=[run('okvis2x', 1, [8, 9], 'x', 'vio-lc')], **HOST)
    assert guard.launch_blockers(d, POLICY, runs=[], **dict(HOST, gpu_pids=[7]))
    cuv = item_for('cuvslam', '20,21,22,23', gpu=True, requires_no_gpu_jobs=True)
    assert guard.launch_blockers(cuv, POLICY, runs=[run('okvis2x', 1, [0, 1, 2, 3], 'x', 'vio-lc')], **HOST)
    assert guard.launch_blockers(cuv, POLICY, runs=[run('orbslam3', 1, [0, 1, 2, 3], 'x')], **HOST) == []
    air = item_for('airslam', '20,21,22,23', gpu=True, requires_no_gpu_jobs=True, requires_cpu_idle=True)
    assert guard.launch_blockers(air, POLICY, runs=[run('orbslam3', 1, [0, 1, 2, 3], 'x')], **HOST)


def test_benchmark_runs_parses_wrapper_and_mode():
    snapshot = [dict(pid=3, argv=['bash', '/w/scripts/run/run_okvis2x.sh', 'zed2i', 'seq', '99', 'vio-lc'], cgroup='0::/a', cpus=[0]),
                dict(pid=4, argv=['python3', 'x.py'], cgroup='0::/b', cpus=[1])]
    runs = guard.benchmark_runs(snapshot)
    assert [(r['pid'], r['algorithm'], r['mode']) for r in runs] == [(3, 'okvis2x', 'vio-lc')]


# ------------------------------------------------------------------ manifests and counts

FINISHED_RUNS = {json.loads(p.read_text())['run'] for p in build_manifest.OUT.glob('*/attempts/*.json')
                 if json.loads(p.read_text()).get('state') == 'finished'}


@pytest.fixture(scope='module')
def built(tmp_path_factory):
    if not HAVE_CAMPAIGNS:
        pytest.skip('campaign artifacts not on this host')
    out = tmp_path_factory.mktemp('n3')
    return {kind: build_manifest.build(kind, out, allow_runs=FINISHED_RUNS) for kind in ('cpu', 'gpu')}


def test_counts_60_13_3(built):
    totals = {}
    for path, _, counts in built.values():
        for group, n in counts.items():
            totals[group] = totals.get(group, 0) + n
    assert totals == {'B': 60, 'C': 13, 'D-search': 3}
    cpu = json.loads(built['cpu'][0].read_text())
    gpu = json.loads(built['gpu'][0].read_text())
    items = cpu['items'] + gpu['items']
    assert len({i['run_id'] for i in items}) == 76
    systems_b = {i['system'] for i in items if i['group'] == 'B'}
    assert len(systems_b) == 10
    c = {}
    for i in items:
        if i['group'] == 'C':
            c[i['system']] = c.get(i['system'], 0) + 1
    assert c == dict(orbslam3=2, okvis2=2, airslam=2, cuvslam=2, mast3r_fusion=2, svo_pro=3)
    d = [i for i in items if i['group'] == 'D-search']
    assert all(i['timeout_s'] == 28800 and i['memory']['max_gib'] == 64 and i['admission']['one_at_a_time'] for i in d)
    assert {i['label'] for i in d} == {'noise_af98eb489d0f5ce2'}
    assert {i['label'] for i in items if i['system'] == 'svo_pro' and i['group'] == 'C'} == {'noise_57735ccdd0c68689'}


def test_manifest_items_are_bound_and_fresh(built):
    for path, digest, _ in built.values():
        manifest, actual = verify_manifest(path, digest)
        for item in manifest['items']:
            assert item['run_id'] == run_id(manifest['campaign_id'], item['key'])
            assert item['key'].startswith('paper_n3__')
            # fresh unless it is a finished N=3 attempt (the pilot of 11 Nov 2026)
            assert not Path(item['run_dir']).exists() or item['run_dir'] in FINISHED_RUNS
            assert item['command'][4] == '--unit=' + item['unit']
            assert item['inner_command'] == item['command'][-6:]
            assert all(Path(e['path']).is_file() and sha(e['path']) == e['sha256'] for e in item['pinned_evidence'])
        with pytest.raises(RuntimeError, match='never rebuilt'):
            build_manifest.build(manifest['campaign'], Path(path).parents[1])


def test_dry_run_prints_without_executing(built, capsys, monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, 'Popen', lambda *a, **k: calls.append(a))
    dispatch.dry_run(built['cpu'][0], [], True, False)
    text = capsys.readouterr().out
    assert text.count('=== ') == 52 and 'systemd-run --user --scope' in text and not calls


def test_verifier_never_activates_gpu_instrumentation():
    env = dict(GPU6_AUDIT_DIR='/x', GPU6_MEMORY_BYTES='1', GPU6_MEMORY_HIGH_BYTES='1', PYTHONPATH='/i', VSLAM_EXPECTED_INPUT_SHA256='a')
    assert identity.verifier_env(env) == dict(VSLAM_EXPECTED_INPUT_SHA256='a')


def test_evaluator_is_the_unresolved_worktree_venv_and_matches_the_recorded_versions():
    """Pilot refusal of 11 Nov 2026: the evaluator must be the venv the first runs' engine used."""
    for kind, root in (('cpu', build_manifest.CPU_ROOT), ('gpu', build_manifest.GPU_ROOT)):
        manifest = json.loads((build_manifest.OUT / kind / 'manifest.json').read_text())
        venv = str(Path(root) / '.venv/bin/python')
        for item in manifest['items']:
            assert item['evaluator']['python'] == venv
            assert venv in json.dumps(item['environment'])
            assert 'macvo/bin/python3.10' not in json.dumps(item['environment'])
        want = manifest['items'][0]['evaluator']['controller_environment']
        live = json.loads(subprocess.run([venv, '-B', '-c', 'import sys,json,importlib.metadata as m;'
            'print(json.dumps(dict(python=sys.version,package_versions={n:m.version(n) for n in ("numpy","scipy","optuna","PyYAML")})))'],
            capture_output=True, text=True, check=True).stdout)
        assert live['python'] == want['python'] and live['package_versions'] == want['package_versions']


def test_only_basalt_and_mast3r_enforce_the_1pct_rule():
    """Engineer, 11 Nov 2026: cuVSLAM is not reproducible (Rule C spread 10.34-10.51 m), so record-only."""
    assert build_manifest.REPEATABLE == {'basalt', 'mast3r_fusion'}
    for kind in ('cpu', 'gpu'):
        manifest = json.loads((build_manifest.OUT / kind / 'manifest.json').read_text())
        for item in manifest['items']:
            if item['algorithm'] not in build_manifest.REPEATABLE:
                assert item['repeat_check'] == 'record_only', item['id']
