"""a33_search_guard: identical snapshots pass; any change to what the a33 search reads writes the FAULT (create-only)."""
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import a33_search_guard as G  # noqa: E402


def fixture(tmp):
    live, state, checkout = tmp/'live', tmp/'state', tmp/'checkout'
    cam = live/'datasets/zed2i/full/mav0/cam0'; cam.mkdir(parents=True)
    (cam/'1.png').write_bytes(b'image'); (live/'datasets/zed2i/full/times.txt').write_text('1\n')
    view = checkout/'datasets/zed2i/view'; (view/'mav0/imu0').mkdir(parents=True)
    (view/'mav0/imu0/data.csv').write_text('imu\n')
    os.symlink(cam, view/'mav0/cam0'); os.symlink('mav0/cam0', view/'cam0'); os.symlink(live/'datasets/zed2i/full/times.txt', view/'times.txt')
    prov = live/'results/vio/zed2i/full/okvis2/run20001/provenance'; prov.mkdir(parents=True)
    (prov/'implementation.json').write_text('{}'); (checkout/'configs').mkdir()
    (checkout/'configs/okvis2.yaml').write_text('a: 1\n')
    (live/'results/.cache').mkdir(parents=True); (live/'results/.cache/input-content.sqlite').write_bytes(b'sqlite')
    pin = state/'protocol.json'; state.mkdir(exist_ok=True); pin.write_text('{}')
    manifest = dict(checkout=dict(path=str(checkout)), helper_python=sys.executable,
                    pinned_evidence=[dict(role='protocol', path=str(pin), sha256=G.sha(pin))],
                    views={'view': dict(dir=str(view))},
                    templates={'okvis2/vio': dict(native=dict(source_rel='src/okvis2'), environment_base={}, container=None,
                               reference=dict(provenance=dict(implementation=dict(path=str(prov/'implementation.json'),
                                                                                  sha256=G.sha(prov/'implementation.json')))),
                               config=dict(files=[dict(role='estimator_config_source', path='configs/okvis2.yaml',
                                                       sha256=G.sha(checkout/'configs/okvis2.yaml'))], environment={}))})
    (state/'manifests/A').mkdir(parents=True); (state/'manifests/A/manifest.json').write_text(json.dumps(manifest))
    return live, state, checkout, cam


def snap(live, state, tmp, tree_value='t1', runtime_value='r1', deep=False):
    return G.snapshot(state, live, scratch=tmp/'scratch', deep=deep,
                      tree=lambda root, rel, store, py: dict(path=rel, commit=tree_value, scope='algorithm', entries=[]),
                      runtime=lambda root, algorithm, py, env: dict(container=runtime_value, sha256='x'))


def test_identical_snapshots_pass_and_write_no_fault(tmp_path):
    live, state, _, _ = fixture(tmp_path)
    before, after = snap(live, state, tmp_path), snap(live, state, tmp_path)
    assert before['pin_mismatches'] == [] and set(before['native']) == {'okvis2'}
    assert G.compare(before, after, state/'FAULT') == [] and not (state/'FAULT').exists()


def test_camera_write_is_caught_without_deep_hashing(tmp_path):
    live, state, _, cam = fixture(tmp_path)
    before = snap(live, state, tmp_path)
    (cam/'1.png').write_bytes(b'image')                     # same bytes, rewritten: ctime/mtime move
    diff = G.compare(before, snap(live, state, tmp_path), state/'FAULT')
    assert diff and json.loads((state/'FAULT').read_text())['kind'] == 'main_apply_guard'


def test_native_tree_or_runtime_change_is_a_difference(tmp_path):
    live, state, _, _ = fixture(tmp_path)
    before = snap(live, state, tmp_path)
    assert G.compare(before, snap(live, state, tmp_path, tree_value='t2'), None)
    assert G.compare(before, snap(live, state, tmp_path, runtime_value='r2'), None)


def test_cache_and_pinned_provenance_changes_are_caught(tmp_path):
    live, state, checkout, _ = fixture(tmp_path)
    before = snap(live, state, tmp_path)
    (live/'results/.cache/input-content.sqlite').write_bytes(b'sqlite2')
    assert any('/cache/' in d['path'] for d in G.compare(before, snap(live, state, tmp_path), None))
    (checkout/'configs/okvis2.yaml').write_text('a: 2\n')
    after = snap(live, state, tmp_path)
    assert after['pin_mismatches'] == [str(checkout/'configs/okvis2.yaml')]


def test_fault_is_create_only_and_scratch_is_required(tmp_path):
    live, state, _, cam = fixture(tmp_path)
    (state/'FAULT').write_text('earlier fault\n')
    before = snap(live, state, tmp_path); (cam/'2.png').write_bytes(b'new')
    assert G.compare(before, snap(live, state, tmp_path), state/'FAULT')
    assert (state/'FAULT').read_text() == 'earlier fault\n'
    try:
        G.snapshot(state, live, scratch=None)
    except ValueError:
        pass
    else:
        raise AssertionError('scratch store must be required')


def test_superseded_manifests_are_not_inputs(tmp_path):
    live, state, _, _ = fixture(tmp_path)
    old = state/'manifests/A.superseded-20261117T000000Z'; old.mkdir()
    value = json.loads((state/'manifests/A/manifest.json').read_text())
    value['pinned_evidence'][0]['sha256'] = '0'*64
    (old/'manifest.json').write_text(json.dumps(value))
    assert snap(live, state, tmp_path)['pin_mismatches'] == []
