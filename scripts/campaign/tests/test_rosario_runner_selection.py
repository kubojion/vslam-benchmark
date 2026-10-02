"""Candidate selection is explicit, complete, reproducible and never a readiness grant."""
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts/run'))
sys.path.insert(0, str(ROOT / 'scripts/campaign'))
from _rosario_profile import BUNDLE, FILES, select_profile, snapshot_profile
from _config_preflight import select_basalt_config
from run_future_manifest import check_execution_environment


@pytest.fixture
def repo(tmp_path):
    shutil.copytree(ROOT / BUNDLE, tmp_path / BUNDLE)
    shutil.copytree(ROOT / 'configs/basalt', tmp_path / 'configs/basalt')
    return tmp_path


@pytest.mark.parametrize('profile', FILES)
def test_complete_profile_captured_and_native_loads_immutable_copies(repo, profile):
    algorithm = FILES[profile][0]
    record = select_profile(repo, algorithm, 'rosariov2', 'sequence1', profile)
    snapshot = snapshot_profile(record, repo / 'attempt-configs')
    assert len(snapshot['files']) == len(FILES[profile][1])
    assert not snapshot['production_ready'] and not snapshot['production_profile_confirmed']
    with pytest.raises(FileExistsError):
        snapshot_profile(record, repo / 'attempt-configs')
    for item in snapshot['files']:
        assert Path(item['loaded_path']).read_bytes() == Path(item['source']).read_bytes()
        Path(item['source']).write_text('changed after snapshot')
        assert Path(item['loaded_path']).read_text() != 'changed after snapshot'


@pytest.mark.parametrize('algorithm,dataset,sequence,profile', [
    ('basalt', 'zed2i', 'sequence1', 'basalt-kalibr'),
    ('basalt', 'rosariov2', 'sequence1', 'voxel-kalibr'),
    ('openvins', 'rosariov2', 'sequence2', 'openvins-author'),
    ('voxel_svio', 'rosariov2', 'sequence1', '../unreviewed'),
])
def test_inconsistent_selection_rejected(repo, algorithm, dataset, sequence, profile):
    with pytest.raises((ValueError, OSError)):
        select_profile(repo, algorithm, dataset, sequence, profile)


@pytest.mark.parametrize('name', ['calibration.json', 'vio_config.json'])
def test_missing_or_changed_selected_file_rejected(repo, name):
    path = repo / BUNDLE / 'basalt-kalibr' / name
    path.write_text(path.read_text() + ' ')
    with pytest.raises(ValueError, match='hash mismatch'):
        select_profile(repo, 'basalt', 'rosariov2', 'sequence1', 'basalt-kalibr')
    path.unlink()
    with pytest.raises(OSError):
        select_profile(repo, 'basalt', 'rosariov2', 'sequence1', 'basalt-kalibr')


def test_basalt_calibration_override_is_independent_and_validated(repo):
    settings = repo / BUNDLE / 'basalt-kalibr/vio_config.json'
    calibration = repo / BUNDLE / 'basalt-kalibr/calibration.json'
    assert select_basalt_config(repo, 'rosariov2', 'vio', settings, calibration) == settings
    with pytest.raises(OSError):
        select_basalt_config(repo, 'rosariov2', 'vio', settings, repo / 'missing-calibration')


def test_snapshot_rejects_change_between_selection_and_materialization(repo):
    record = select_profile(repo, 'openvins', 'rosariov2', 'sequence1', 'openvins-author')
    Path(record['files'][1]['source']).write_text('tampered')
    with pytest.raises(ValueError, match='changed between'):
        snapshot_profile(record, repo / 'not-created')
    assert not (repo / 'not-created').exists()


def test_candidate_override_cannot_leak_into_a_default_production_manifest():
    for name in ('ROSARIO_VIO_PROFILE', 'BASALT_CALIBRATION'):
        with pytest.raises(ValueError, match='unreviewed inherited'):
            check_execution_environment({name: 'unreviewed'})
