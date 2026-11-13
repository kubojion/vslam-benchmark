"""Author-reported attempts (13 Nov 2026) become label-only failed rows; any other pathless row still errors."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'scripts/eval')); sys.path.insert(0, str(ROOT/'scripts/campaign'))
import build_benchmark_csv as csvb  # noqa: E402
import build_repair_inventory as inventory  # noqa: E402
from protocol_status import observed_outcome, summarize_protocol  # noqa: E402

KEY = 'vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x'
IDS = [f'author-report-20261113-okvis2x-sielinko-volc-r{r}' for r in (1, 2, 3)]
NUMBERS = ('ate_se3_rmse_m', 'ate_sim3_rmse_m', 'primary_ate_rmse_m', 'coverage_gap_pct', 'end_to_end_time_s', 'duration_s',
           'process_exit_code', 'cpu_mean_pct', 'ram_peak_mib', 'scale_factor', 'n_pairs_ate', 'sequence_duration_s',
           'input_fps', 'image_width', 'trajectory_time_coverage_pct', 'machine_cpu', 'machine_id')


def repo_with(tmp, key=KEY):
    (tmp/'configs/campaigns').mkdir(parents=True)
    record = dict(schema=1, source=dict(kind='author_report', path='/paper/x.json', sha256='abc'),
                  cells={key: dict(attempts=[dict(repetition=r, id=i, outcome='dnf', provenance='author_report')
                                             for r, i in zip((1, 2, 3), IDS)])})
    (tmp/inventory.AUTHOR_OUTCOMES).write_text(json.dumps(record))
    return tmp


def attempt(repo, rep):
    return inventory.author_attempt(repo, KEY, dict(repetition=rep, id=IDS[rep-1], outcome='dnf', provenance='author_report'))


def cell(key=KEY):
    return dict(key=key, comparison_membership=inventory.AUTHOR_LABEL, acceptance=dict(status='blocked'))


def test_author_attempt_carries_no_machine_field(tmp_path):
    a = attempt(repo_with(tmp_path), 1)
    assert a['path'] is None and a['files'] == [] and a['process'] == {} and a['runtime'] == {} and a['machine_id'] is None
    assert a['evaluation_path'] is None and a['cohort_fingerprint'] is None and a['author_report']['id'] == IDS[0]


def test_listed_author_attempt_is_a_label_only_failed_row(tmp_path):
    repo = repo_with(tmp_path)
    row = csvb.row_from_attempt(attempt(repo, 2), {}, cell(), repo=repo)
    assert row['run'] == IDS[1] and row['run_path'] == '' and row['run_status'] == 'failed_without_trajectory'
    assert row['observed_outcome'] == 'failure_without_final_trajectory' and row['observed_failure'] and not row['successful_run']
    assert row['campaign_membership'] == 'author_report_20261113' and row['attempt_exists'] is True
    assert json.loads(row['claim_limits']) == json.loads(row['scientific_blockers']) == [
        'author_reported_did_not_finish', 'no_machine_receipt', 'runtime_not_comparable']
    assert all(row[name] is None for name in NUMBERS)
    assert set(row) == set(csvb.COLUMNS)


def test_three_author_rows_count_as_three_failed_repetitions(tmp_path):
    repo = repo_with(tmp_path)
    rows = [csvb.row_from_attempt(attempt(repo, r), {}, cell(), repo=repo) for r in (1, 2, 3)]
    summary = summarize_protocol([dict(r, evaluated=False) for r in rows])
    assert summary['attempt_count'] == 3 and summary['observed_failure_count'] == 3
    assert summary['successful_run_count'] == 0 and summary['missing_attempt_count'] == 0


def test_a_pathless_attempt_not_in_the_record_is_an_error(tmp_path):
    repo = repo_with(tmp_path)
    other = attempt(repo, 1); other['author_report'] = dict(other['author_report'], id='invented')
    with pytest.raises(ValueError, match='not an author-reported attempt'):
        csvb.row_from_attempt(other, {}, cell(), repo=repo)
    plain = dict(attempt(repo, 1)); plain.pop('author_report')
    with pytest.raises(ValueError, match='not an author-reported attempt'):
        csvb.row_from_attempt(plain, {}, cell(), repo=repo)
    with pytest.raises(ValueError, match='not an author-reported attempt'):
        csvb.row_from_attempt(attempt(repo, 1), {}, cell('vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2'), repo=repo)
    with pytest.raises(ValueError, match='not an author-reported attempt'):
        csvb.listed_author_attempt(attempt(repo, 1), None, repo)


def test_without_the_record_no_pathless_row_is_accepted(tmp_path):
    repo = repo_with(tmp_path); a = attempt(repo, 1)
    (repo/inventory.AUTHOR_OUTCOMES).unlink()
    with pytest.raises(ValueError, match='not an author-reported attempt'):
        csvb.row_from_attempt(a, {}, cell(), repo=repo)


def test_machine_recorded_outcomes_are_unchanged():
    assert observed_outcome(True, False, 'failed_without_trajectory', 134, None) == 'failure_without_final_trajectory'
    assert observed_outcome(True, False, None, None, None) == 'unknown'
    assert observed_outcome(False, False, 'failed_without_trajectory', None, None) == 'not_attempted'
    assert observed_outcome(True, True, 'ok', 0, None) == 'success'


def test_rows_sort_numbered_runs_before_author_ids():
    rows = [dict(run_type='vo-lc', dataset='zed2i', seq='s', algo='a', gnss_variant='default', run=r) for r in (IDS[1], '10', '9', IDS[0])]
    key = lambda r: (r['run_type'], r['dataset'], r['seq'], r['algo'], r['gnss_variant'],
                     (0, int(r['run']), '') if str(r['run']).isdigit() else (1, 0, str(r['run'])))
    assert [r['run'] for r in sorted(rows, key=key)] == ['9', '10', IDS[0], IDS[1]]
