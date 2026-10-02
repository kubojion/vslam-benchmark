"""Presentation must preserve experimental validity, recorded failures and evidence gates."""
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from update_todo_matrices import (SEQUENCES, load_campaigns,
    ready_actions, render_cell, render_details, render_excluded, update, update_legend)


def attempt(run=1, verified='verified', exit_code=0, cohort='same'):
    return dict(path=f'results/vo/euroc_mav/MH_01_easy/okvis2/run{run}',
        exists=True, evaluated=True, trajectory_saved=True, numerical_status='ok',
        process={'exit_code': exit_code}, cohort_fingerprint=cohort,
        qualification={'protocol': {'status': verified}, 'blockers': [], 'claim_limits': [],
                       'status': 'accepted' if exit_code == 0 else 'valid_observed_failure'})


def cell(attempts=None):
    return dict(run_type='vo', algorithm='okvis2', dataset='euroc_mav', sequence='MH_01_easy',
                attempts=attempts if attempts is not None else [attempt(i) for i in (1, 2, 3)])


def test_three_verified_failures_keep_tick_and_all_overlapping_counts():
    c = cell([attempt(i, exit_code=139) for i in (1, 2, 3)])
    before = copy.deepcopy(c)
    result = render_cell(c)
    assert '✅ N=3' in result and 'A3/E3/S0/F3' in result
    assert 'protocol' not in result.lower() and c == before
    details = render_details({'cells': [c]}, 'snapshot', [])
    assert details.count('failure_with_saved_trajectory') == 3
    assert details.count('| 139 | yes |') == 3


def test_three_evaluations_without_review_never_become_verified():
    c = cell([attempt(i, verified='blocked') for i in (1, 2, 3)])
    for a in c['attempts']:
        a['qualification']['blockers'] = ['horti_exact_reference_origin_timing_unresolved']
    rendered = render_cell(c)
    assert '🟡 N=0' in rendered and 'A3/E3/S3/F0' in rendered
    assert 'review: reference/clock' in rendered and 'rerun:' not in rendered


def test_setup_rerun_and_reference_review_are_both_visible():
    c = cell()
    for a in c['attempts']:
        a['qualification']['protocol']['status'] = 'invalid_setup'
        a['confirmed_protocol_findings'] = [{'code': 'horti_camera_imu_time_offset_uncompensated'}]
        a['qualification']['blockers'] = ['horti_exact_reference_origin_timing_unresolved']
    rendered = render_cell(c)
    assert 'rerun: IMU timing' in rendered and 'review: reference/clock' in rendered
    assert '✅' not in rendered


def test_separate_groups_keep_failure_and_unknown_is_not_success():
    c = cell([attempt(1, exit_code=134, cohort='old'), attempt(2), attempt(3)])
    rendered = render_cell(c)
    assert '🟠 N=1+2' in rendered and 'A3/E3/S2/F1' in rendered and '✅' not in rendered
    c = cell([attempt(1, verified='blocked', exit_code=None)])
    assert 'A1/E1/S0/F0/U1' in render_cell(c)
    assert '✅' not in render_cell(c)


def test_selected_physical_failure_is_never_relabelled_or_hidden():
    c = cell([attempt(4, exit_code=139), attempt(5), attempt(6)])
    c['attempts'][0].update(evaluated=False, trajectory_saved=False, numerical_status=None)
    c['attempts'][0]['qualification']['claim_limits'] = ['no_final_vio_lc_trajectory_no_accuracy_claim']
    result = render_cell(c)
    assert '✅ N=3' in result and 'A3/E2/S2/F1' in result
    assert 'selected r4,r5,r6' in result and 'no final export' in result
    details = render_details({'cells': [c]}, 'snapshot', [])
    assert '| 1 | [run4]' in details and 'failure_without_final_trajectory | 139 | no' in details
    assert '[run1]' not in details


def test_unknown_legacy_counts_and_historical_exclusion_are_not_invented():
    result = render_excluded({}, 'vo', 'euroc_mav', 'MH_01_easy', 'mast3r_slam', 'old OOM')
    assert 'A?/E?/S?/F?' in result and 'reported OOM (12 GB)' in result
    a = attempt(1, exit_code=None)
    a.update(category='historical_excluded', path=a['path'].replace('okvis2', 'droidslam'))
    result = render_excluded({'other_artifacts': [a]}, 'vo', 'euroc_mav', 'MH_01_easy', 'droidslam', 'N=1 historical')
    assert 'A1/E1/S0/F0/U1' in result and 'excluded' in result and '✅' not in result


def test_five_matrices_row_order_counts_notes_and_idempotency():
    lines, cells = ['## Run combinations matrix', 'old legend'], []
    for mode in ('vo', 'vio', 'vo-lc', 'vio-lc', 'gnss-vio'):
        sequences = SEQUENCES[:4] if mode == 'gnss-vio' else SEQUENCES
        lines += [f'### Test - `results/{mode}/`', '| Algorithm | ' + ' | '.join(s for _, s in sequences) + ' |']
        for name in ('OKVIS2', 'MASt3R-SLAM'):
            lines.append('| ' + name + ' | ' + ' | '.join(['old OOM'] * len(sequences)) + ' |')
        for ds, seq in sequences:
            c = cell(); c.update(run_type=mode, dataset=ds, sequence=seq); cells.append(c)
        lines.append('> Historical note unchanged.')
    original = '\n'.join(lines) + '\n'
    rendered = update(original, {'cells': cells})
    assert [s.count('|') for s in original.splitlines()] == [s.count('|') for s in rendered.splitlines()]
    for before, after in zip(original.splitlines(), rendered.splitlines()):
        if before.startswith(('| OKVIS2', '| MASt3R-SLAM')):
            assert before.split('|')[1] == after.split('|')[1]
            assert all('A' in s and '/E' in s and '/S' in s and '/F' in s for s in after.split('|')[2:-1])
        else:
            assert before == after
    result = update_legend(rendered, [])
    assert result.count('### Test') == 5 and result.count('Historical note unchanged') == 5
    assert 'A3/E3/S0/F3' in result and 'not necessarily three successful runs' in result
    assert result == update_legend(update(result, {'cells': cells}), [])


def reviewed_manifest(root):
    def write(path, value):
        file = root / path; file.write_text(json.dumps(value))
        return {'path': path, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()}
    key = 'vo/euroc_mav/MH_01_easy/okvis2'
    inventory = write('inventory.json', {'cells': [{'key': key}]})
    proof = write('native-review.json', {'native_exit': 0, 'effective_config_reviewed': True})
    actions = []
    for n in (1, 2, 3):
        actions.append(dict(id=f'{key}/default/r{n}', cell=key, repetition=n, category='missing',
            cohort='reviewed', planned_output=f'results/{key}/run{10000+n}', prerequisites=[],
            command=['python3', 'scripts/campaign/run_repetitions.py', 'euroc_mav', 'MH_01_easy',
                     'okvis2', '3', 'vo', '--run-id', str(10000+n), '--repetition', str(n), '--cohort', 'reviewed'],
            prior_evidence=[], review_evidence=[proof],
            readiness={'verified_ready_to_run': True, 'static_checks': 'verified', 'execution_validation': 'verified'}))
    manifest = dict(schema_version=2, campaign_id='reviewed', inventory=inventory,
        target={'repetitions': 3, 'logical_repetitions': 3, 'default_cells': 1}, actions=actions)
    write('manifest.json', manifest)
    return manifest


def test_readiness_requires_matching_evidence_not_flags_or_config_files(tmp_path):
    manifest = reviewed_manifest(tmp_path)
    campaign = load_campaigns(tmp_path, ['manifest.json'])[0]
    assert not campaign['errors'] and len(ready_actions(campaign)) == 3
    (tmp_path / 'native-review.json').write_text('{"native_exit":139}')
    stale = load_campaigns(tmp_path, ['manifest.json'])[0]
    assert stale['errors'] and ready_actions(stale) == []
    for a in manifest['actions']:
        a['review_evidence'] = []
    (tmp_path / 'config.yaml').write_text('exists: true')
    (tmp_path / 'manifest.json').write_text(json.dumps(manifest))
    flags_only = load_campaigns(tmp_path, ['manifest.json'])[0]
    assert flags_only['errors'] and not ready_actions(flags_only)
    missing = load_campaigns(tmp_path, ['absent.json'])[0]
    assert missing['errors'] and not ready_actions(missing)


def test_future_corrected_orb_cell_is_not_forced_back_into_fps_rerun():
    c = cell(); c.update(algorithm='orbslam3', dataset='zed2i')
    result = render_cell(c)
    assert '✅ N=3' in result and 'rerun:' not in result
