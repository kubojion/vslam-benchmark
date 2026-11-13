"""The author-outcome record supersedes one closed cell, with three dnf attempts and no machine fields."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_repair_inventory as inventory  # noqa: E402

KEY = 'vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def repo_with(tmp, attempts=None, key=KEY, historical=None):
    (tmp/'configs/campaigns').mkdir(parents=True, exist_ok=True)
    selection = tmp/inventory.PAPER_COMPLETION_SELECTION
    selection.write_text(json.dumps(dict(closed_cells={KEY: dict(disposition='did_not_finish', open_attempts={f'{KEY}/run10001': {}})})))
    source = tmp/'author.json'; source.write_text('{"source": "x"}')
    attempts = attempts or [dict(repetition=r, id=f'author-r{r}', outcome='dnf', provenance='author_report') for r in (1, 2, 3)]
    record = dict(schema=1, source=dict(kind='author_report', path=str(source), sha256=sha(source)),
                  supersedes=dict(path=inventory.PAPER_COMPLETION_SELECTION, sha256=sha(selection)),
                  cells={key: dict(attempts=attempts, historical_not_selected=[dict(attempt=h) for h in
                                   (historical or [f'results/{KEY}/run10001'])])})
    (tmp/inventory.AUTHOR_OUTCOMES).write_text(json.dumps(record))
    return tmp, source


def test_valid_record(tmp_path):
    repo, _ = repo_with(tmp_path)
    assert list(inventory.author_outcome_record(repo)) == [KEY]


def test_absent_record_changes_nothing(tmp_path):
    assert inventory.author_outcome_record(tmp_path) == {}


@pytest.mark.parametrize('extra', [dict(run_dir='results/x/run1'), dict(exact_runtime_s=1.0), dict(machine_receipt='x'),
                                   dict(exit_code=0), dict(hardware='cpu')])
def test_no_machine_field_can_be_recorded(tmp_path, extra):
    attempts = [dict(repetition=r, id=f'author-r{r}', outcome='dnf', provenance='author_report') for r in (1, 2, 3)]
    attempts[1].update(extra)
    repo, _ = repo_with(tmp_path, attempts)
    with pytest.raises(ValueError, match='no machine fields'):
        inventory.author_outcome_record(repo)


def test_wrong_outcome_or_duplicate_ids_are_refused(tmp_path):
    attempts = [dict(repetition=r, id='same', outcome='dnf', provenance='author_report') for r in (1, 2, 3)]
    repo, _ = repo_with(tmp_path, attempts)
    with pytest.raises(ValueError, match='three distinct'):
        inventory.author_outcome_record(repo)


def test_changed_source_is_refused(tmp_path):
    repo, source = repo_with(tmp_path)
    source.write_text('{"source": "edited"}')
    with pytest.raises(ValueError, match='source changed'):
        inventory.author_outcome_record(repo)


def test_only_a_closed_cell_and_its_server_attempt_stays_historical(tmp_path):
    repo, _ = repo_with(tmp_path, key='vio/rosariov2/sequence1/airslam')
    with pytest.raises(ValueError, match='closed cell'):
        inventory.author_outcome_record(repo)
    repo, _ = repo_with(tmp_path/'b', historical=[f'results/{KEY}/run2'])
    with pytest.raises(ValueError, match='historical'):
        inventory.author_outcome_record(repo)


def test_changed_superseded_record_is_refused(tmp_path):
    repo, _ = repo_with(tmp_path)
    (repo/inventory.PAPER_COMPLETION_SELECTION).write_text('{"closed_cells": {}}')
    with pytest.raises(ValueError, match='supersedes changed'):
        inventory.author_outcome_record(repo)


def test_committed_record_matches_the_decision():
    repo = Path(__file__).resolve().parents[3]
    path = repo/inventory.AUTHOR_OUTCOMES
    if not path.is_file():
        pytest.skip('record not present')
    record = json.loads(path.read_text())
    assert list(record['cells']) == [KEY]
    cell = record['cells'][KEY]
    assert [a['id'] for a in cell['attempts']] == [f'author-report-20261113-okvis2x-sielinko-volc-r{r}' for r in (1, 2, 3)]
    assert all(set(a) == inventory.AUTHOR_ATTEMPT_KEYS for a in cell['attempts'])
    assert [h['attempt'] for h in cell['historical_not_selected']] == [f'results/{KEY}/run10001']
    assert record['source']['path'].endswith('PAPER/vslam-paper/data/metadata/author-outcomes-20261113.json')
