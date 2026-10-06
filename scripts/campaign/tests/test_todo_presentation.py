"""Presentation must preserve experimental validity, recorded failures and evidence gates."""
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from update_todo_matrices import (LEGEND, SEQUENCES, cell_key, selected_campaign, load_campaigns,
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


def test_reviewed_algorithm_failure_marks_the_tick_only_when_present():
    failed = render_cell(cell([attempt(1, exit_code=139), attempt(2), attempt(3)]))
    clean = render_cell(cell())
    assert '✅ N=3 ❗' in failed and 'A3/E3/S2/F1' in failed
    assert '✅ N=3' in clean and '❗' not in clean
    assert '❗' in LEGEND


def test_three_evaluations_without_review_never_become_verified():
    c = cell([attempt(i, verified='blocked') for i in (1, 2, 3)])
    for a in c['attempts']:
        a['qualification']['blockers'] = ['horti_exact_reference_origin_timing_unresolved']
    rendered = render_cell(c)
    assert '🟨 3 recorded' in rendered and 'A3/E3/S3/F0' in rendered
    assert 'review: reference/clock' in rendered and 'rerun:' not in rendered


def test_setup_rerun_and_reference_review_are_both_visible():
    c = cell()
    for a in c['attempts']:
        a['qualification']['protocol']['status'] = 'invalid_setup'
        a['confirmed_protocol_findings'] = [{'code': 'horti_camera_imu_time_offset_uncompensated'}]
        a['qualification']['blockers'] = ['horti_exact_reference_origin_timing_unresolved']
    rendered = render_cell(c)
    assert rendered.startswith('[🟥 3 recorded]')
    assert '🔴 rerun not ready: IMU timing' in rendered and 'review: reference/clock' in rendered
    assert '✅' not in rendered


def test_separate_groups_keep_failure_and_unknown_is_not_success():
    c = cell([attempt(1, exit_code=134, cohort='old'), attempt(2), attempt(3)])
    rendered = render_cell(c)
    assert rendered.startswith('[🟨 🟢 N=1 + 🟢 N=2]')
    assert '🟢 N=1 + 🟢 N=2' in rendered and 'A3/E3/S2/F1' in rendered and '✅' not in rendered
    c = cell([attempt(1, verified='blocked', exit_code=None)])
    assert render_cell(c).startswith('[🟨 1 recorded]')
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


def plan(c, categories, ready=True, name='reviewed.json', replaces=None):
    actions = [dict(id=f'{cell_key(c)}/r{i}', cell=cell_key(c), repetition=i,
        category=category, prerequisites=[] if ready else ['pending native check'],
        review_evidence=[{'path': 'native-review.json', 'sha256': 'checked by loader'}],
        readiness={'verified_ready_to_run': ready, 'static_checks': 'verified',
                   'execution_validation': 'verified'}) for i, category in enumerate(categories, 1)]
    return dict(path=name, campaign_id=name, replaces_selection_in=replaces, actions=actions, errors=[])


def invalid_cell():
    c = cell([attempt(i, verified='invalid_setup') for i in (1, 2, 3)])
    for a in c['attempts']:
        a['confirmed_protocol_findings'] = [{'code': 'camera_fps_changed_15_to_10'}]
    return c


def absent(run):
    a = attempt(run, verified='not_attempted', exit_code=None)
    a.update(exists=False, evaluated=False, trajectory_saved=False, numerical_status=None)
    return a


def test_complete_requested_symbol_legend_and_verified_partial_counts():
    assert all(symbol in LEGEND for symbol in ['🟥', '🟨', '✅', '🟢', '🔄', '🔴', '🟡', '❌', '🔜', '➖'])
    for n in (1, 2):
        c = cell([attempt(i, exit_code=139 if i == 1 else 0) if i <= n else absent(i) for i in (1, 2, 3)])
        campaign = plan(c, ['reusable'] * n + ['missing'] * (3 - n))
        rendered = render_cell(c, [campaign])
        assert f'🟢 N={n}' in rendered and f'A{n}/E{n}/S{n-1}/F1' in rendered
        assert f'next: missing {3-n} ready' in rendered and '✅' not in rendered
        assert rendered.count('missing') == 1 and 'N=0' not in rendered


def test_confirmed_rerun_uses_ready_not_ready_and_stale_evidence_symbols():
    c = invalid_cell()
    campaign = plan(c, ['required_rerun'] * 3)
    result = render_cell(c, [campaign])
    assert '🟥 3 recorded' in result and '🔄 rerun ready: FPS' in result and 'A3/E3/S3/F0' in result
    campaign['errors'] = ['stale native review']
    result = render_cell(c, [campaign])
    assert '🟥 3 recorded' in result and '🔴 rerun not ready: FPS' in result and '🔄' not in result
    campaign = plan(c, ['required_rerun'] * 3)
    campaign['actions'][1]['prerequisites'] = ['blocked']
    campaign['actions'][2]['readiness']['verified_ready_to_run'] = False
    result = render_cell(c, [campaign])
    assert '🔴 rerun not ready (1/3 ready)' in result and '🔄' not in result


def test_zero_attempts_ready_and_unready_differ_without_inventing_failure():
    c = cell([absent(i) for i in (1, 2, 3)])
    ready = plan(c, ['missing'] * 3)
    result = render_cell(c, [ready])
    assert '🔜 no attempts' in result and 'A0/E0/S0/F0' in result
    assert 'next: missing 3 ready' in result and 'rerun' not in result
    result = render_cell(c, [plan(c, ['missing'] * 3, ready=False)])
    assert '❌ no attempts' in result and 'A0/E0/S0/F0' in result and 'next: missing 3 not ready' in result
    assert '❌ no attempts' in render_cell(c)  # No reviewed evidence is not readiness.


def test_verified_saved_observation_and_unresolved_review_coexist_with_ready_new_group():
    c = cell([attempt(1), attempt(2, verified='blocked', exit_code=139), absent(3)])
    c['attempts'][1]['qualification']['blockers'] = ['native_execution_cause_and_usable_export_missing']
    campaign = plan(c, ['cohort_completion', 'cohort_completion', 'missing'])
    result = render_cell(c, [campaign])
    assert result.startswith('[🟨 🟢 N=1]')
    assert '🟢 N=1' in result and 'A2/E2/S1/F1' in result
    assert '🟡 review: execution' in result and 'next: new group 3 ready' in result
    assert 'rerun' not in result and '🔄' not in result


def test_replacement_plan_wins_by_evidence_identity_not_order_or_ready_flags():
    c = invalid_cell()
    old = plan(c, ['required_rerun'] * 3, name='all.json')
    replacement = plan(c, ['required_rerun'] * 3, ready=False, name='zed.json', replaces='all.json')
    for campaigns in ([old, replacement], [replacement, old]):
        assert selected_campaign(cell_key(c), campaigns) is replacement
        assert '🔴 rerun not ready' in render_cell(c, campaigns)
    replacement['errors'] = ['stale replacement evidence']
    assert '🔄' not in render_cell(c, [old, replacement])
    replacement['replaces_selection_in'] = None
    assert selected_campaign(cell_key(c), [old, replacement]) is None
    assert '🔄' not in render_cell(c, [old, replacement])


def test_verified_partial_and_confirmed_rerun_are_both_shown():
    c = invalid_cell()
    c['attempts'][0] = attempt(1, exit_code=139)
    campaign = plan(c, ['reusable', 'required_rerun', 'required_rerun'])
    result = render_cell(c, [campaign])
    assert result.startswith('[🟥 🟢 N=1]')
    assert '🟢 N=1' in result and '🔄 rerun ready: FPS' in result
    assert 'A3/E3/S2/F1' in result and '✅' not in result


def test_missing_text_is_not_duplicated_without_a_reviewed_plan():
    c = cell([attempt(1, verified='blocked', exit_code=139), absent(2), absent(3)])
    rendered = render_cell(c)
    assert rendered.startswith('[🟨 1 recorded]')
    assert rendered.count('missing') == 1 and 'next: missing 2 not ready' in rendered
    assert 'A1/E1/S0/F1' in rendered and 'N=0' not in rendered


def test_new_group_keeps_distinct_actual_absence_without_duplicate_missing_text():
    c = cell([attempt(1), attempt(2, verified='blocked', exit_code=139), absent(3)])
    campaign = plan(c, ['cohort_completion', 'cohort_completion', 'missing'])
    rendered = render_cell(c, [campaign])
    assert 'next: new group 3 ready' in rendered and 'missing 1' in rendered
    assert rendered.count('missing') == 1


def test_rosario_candidate_preparation_does_not_promote_history_or_readiness():
    c = cell([attempt(i, verified='invalid_setup', exit_code=134) for i in (1, 2, 3)])
    c.update(dataset='rosariov2', sequence='sequence1', run_type='vio', algorithm='basalt')
    for i, a in enumerate(c['attempts'], 1):
        a['path'] = f'results/vio/rosariov2/sequence1/basalt/run{i}'
        a['confirmed_protocol_findings'] = [{'code': 'rosario_identity_camera_imu_extrinsic'}]
    before = copy.deepcopy(c)
    rendered = render_cell(c)
    details = render_details({'cells': [c]}, 'snapshot', [])
    assert 'rosario-vio-candidates-20261002.md' in details
    assert 'Execution remains unverified; historical validity is unchanged.' in details
    assert 'A3/E3/S0/F3' in rendered and '🟥' in rendered and '🔴 rerun not ready' in rendered
    assert '✅' not in rendered and c == before


def test_verified_partial_group_with_only_missing_repetitions_has_no_review_flag():
    c = cell([attempt(1), absent(2), absent(3)])
    result = render_cell(c, [plan(c, ['reusable', 'missing', 'missing'])])
    assert '🟢 N=1' in result and '🟡' not in result and '🟨' not in result
    assert 'next: missing 2 ready' in result
