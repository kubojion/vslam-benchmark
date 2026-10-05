#!/usr/bin/env python3
"""Render the five TODO matrices from reviewed evidence, without reclassifying runs.

An alternate evidence root permits a presentation preview outside a running
checkout. This command never executes estimators or writes evidence/manifests.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from acceptance_ledger import cell_acceptance
from protocol_status import attempt_protocol, summarize_attempts
from run_future_manifest import validate

REPO = Path(__file__).resolve().parents[2]
NAMES = {'ORB-SLAM3': 'orbslam3', 'Basalt': 'basalt', 'MAC-VO': 'macvo',
         'AirSLAM': 'airslam', 'DPVO': 'dpvo', 'DPV-SLAM': 'dpvo', 'OKVIS2': 'okvis2',
         'OKVIS2-X': 'okvis2x', 'OV2SLAM': 'ov2slam', 'OpenVINS': 'openvins',
         'Voxel-SVIO': 'voxel_svio', 'CIFASIS GNSS-SI': 'cifasis_gnss_si',
         'RTAB-Map': 'rtabmap_gps', 'VINS-Fusion': 'vins_fusion_gps',
         'OpenVINS+GPS': 'openvins_gps', 'OKVIS2-X (tight)': 'okvis2x',
         'cuVSLAM': 'cuvslam', 'SVO Pro': 'svo_pro', 'DSOL': 'dsol', 'MASt3R-Fusion': 'mast3r_fusion'}
EXCLUDED = {'MASt3R-SLAM': 'mast3r_slam', 'MegaSaM': 'megasam', 'DROID-SLAM': 'droidslam'}
# Column order of the TODO.md matrices: agricultural datasets first, CitrusFarm beside HortiMulti
# (layout of 2026-10-04). GNSS-VIO uses the first four (Rosario, HortiMulti).
SEQUENCES = [('rosariov2', 'sequence1'), ('rosariov2', 'sequence5'),
             ('hortimulti', 'strawberry02'), ('hortimulti', 'strawberry03'),
             ('citrusfarm', 'seq04'), ('citrusfarm', 'seq07'),
             ('euroc_mav', 'MH_01_easy'), ('euroc_mav', 'MH_03_medium'),
             ('euroc_mav', 'MH_05_difficult'), ('zed2i', 'field1_110426_full_10fps_q90')]
MODES = {'vo', 'vio', 'vo-lc', 'vio-lc', 'gnss-vio'}
DETAILS = 'docs/todo-status-details.md'
MANIFESTS = ('results/repair-20261001/future-n3-manifest.json',
             'results/zed-preparation-20261002/campaign/manifest.json')
RERUN_LABELS = {
    'airslam_rectified_camera_imu_extrinsic': 'rectified IMU',
    'orb_horti_rectified_camera_imu_extrinsic': 'rectified IMU',
    'rosario_identity_camera_imu_extrinsic': 'IMU extrinsic',
    'zed_factory_camera_imu_rotation_omitted': 'camera–IMU',
    'horti_camera_imu_time_offset_uncompensated': 'IMU timing',
    'gnss_zero_antenna_lever_arm_in_native_log': 'antenna lever',
    'rosario_v1_antenna_lever_arm_used_on_v2': 'antenna lever',
    'camera_fps_changed_15_to_10': 'FPS',
    'horti_voxel_initializer_camera_imu_offset_omitted': 'IMU timing',
    'basalt_horti_undocumented_imu_noise': 'IMU noise',
    'horti_imu_profile_and_clock_inconsistent': 'IMU noise/timing',
    'ov2slam_horti_dataset_specific_parameters': 'tuning',
    'openvins_track_frequency_dropped_frames': 'frame drop',
    'orb_source_identity_changed_partial_cell': 'one group',
}
LEGEND = """<!-- todo-matrix-legend:start -->
**A = recorded attempts; E = trajectories evaluated; S = clean final exports;
F = observed failures; U = unknown outcomes, when present.**

Example: **A3/E3/S0/F3** means three attempts, three evaluated trajectories,
no clean final exports and three observed failures. A failed attempt can still
produce an evaluable trajectory, so these counts overlap. Verified completed
exports with shutdown errors remain in F, never S, and are labelled
`completed export; shutdown error`; other tracking/export failures stay distinct.
S does not certify
accuracy or full coverage. `?` means a legacy count is not documented.

**✅ N=3 means three verified attempts under consistent settings, including valid
observed failures—not necessarily three successful runs.** N counts verified,
completed attempts; A also includes attempts awaiting review or using invalid
settings. Unverified or invalid history is labelled `3 recorded` or `1 recorded`;
recorded attempts are not presented as verified repetitions.
`🟢 N=1 + 🟢 N=2` denotes separate implementation groups; it cannot be pooled into N=3.

| Mark | Meaning |
|---|---|
| 🟥 | Leading marker: a confirmed rerun is required; takes precedence over review |
| 🟨 | Leading marker: unresolved review, with no confirmed rerun assumed |
| ✅ N=3 | Three verified attempts in one implementation group, including valid observed failures |
| 🟢 N=1 / 🟢 N=2 | Verified partial group (fewer than three verified attempts); separate groups remain separate |
| 🔴 | Beside a confirmed rerun requirement: not ready, including unverified readiness |
| 🔄 | Beside a confirmed rerun requirement: reviewed execution checks passed (ready) |
| 🟡 | Beside an unresolved evidence/reference/evaluation/execution review item |
| ❌ | No recorded attempts and not ready, with no separate review/rerun marker taking precedence |
| 🔜 | No recorded attempts and ready, with no separate review/rerun marker taking precedence |
| ➖ | Excluded; historical counts and reported failures remain visible |

Cells show saved-run verification and **next** action readiness separately when
needed. For example, `🟨 🟢 N=1; A2/E1/S1/F1; 🟡 review; next: new group ready`
retains the verified observation and failed attempt while reporting the reviewed
future plan. `rerun` is reserved for a confirmed setup defect; a planned new
implementation group is labelled `new group`. Mixed readiness is stated as a
fraction; it never makes the entire action group ready.

Cell links give selected physical run IDs, exits, failure evidence, implementation
groups, review blockers and claim limits. `missing` counts absent attempts only.
Sparse keyframes, partial exports and low accuracy alone do not require reruns.
Historical acceptance decisions and raw evidence are preserved; later evidence
can put a previously green cell back under review. ZED ticks support qualified
nominal position claims, with RTK float,
mounting and clock limits; they do not certify surveyed 6-DoF reference accuracy.
Readiness comes from the selected reviewed campaign and its unchanged evidence,
never from N=3 or configuration-file existence. It does not authorize a launch or
claim full-sequence stability. The plan summary below is separate from live progress.
<!-- todo-matrix-legend:end -->"""


def cell_key(cell):
    return cell.get('key') or '/'.join(cell.get(k, 'unknown') for k in
                                     ('run_type', 'dataset', 'sequence', 'algorithm'))


def anchor(key):
    return re.sub(r'[^a-z0-9]+', '-', key.lower()).strip('-')


def acceptance(cell):
    return cell.get('acceptance') or cell_acceptance(
        cell['attempts'], cell.get('within_cell_cohort_consistent', True))


def counts(review):
    result = '/'.join(f'{label}{review[field]}' for label, field in (
        ('A', 'attempt_count'), ('E', 'evaluated_trajectory_count'),
        ('S', 'successful_run_count'), ('F', 'observed_failure_count')))
    if review['unknown_outcome_count']:
        result += f"/U{review['unknown_outcome_count']}"
    return result


def run_label(attempt, index):
    name = Path(attempt.get('path') or f'run{index}').name
    return 'r' + name.removeprefix('run')


def review_codes(cell):
    return sorted({code for a in cell['attempts'] for code in
                   a.get('qualification', {}).get('blockers', []) +
                   a.get('qualification', {}).get('protocol', {}).get('blockers', [])})


def short_flags(cell, review):
    attempts = cell['attempts']
    limits = {s for a in attempts for s in a.get('qualification', {}).get('claim_limits', [])}
    findings = {f['code'] for a in attempts for f in a.get('confirmed_protocol_findings', [])}
    reruns = sorted({RERUN_LABELS.get(code, 'setup') for code in findings})
    flags = ['rerun: ' + ', '.join(reruns)] if reruns else []
    reviews = set()
    for code in review_codes(cell):
        if code in findings or code in {'missing_repetition', 'historical_workspace_digest_differs_keep_cohorts_separate'}:
            continue
        if code.startswith(('horti_february_reference', 'horti_exact_reference')):
            reviews.add('reference/clock')
        elif code.startswith(('rosario_unchanged_images', 'rosario_image_projection')):
            reviews.add('camera model')
        elif code.startswith('native_execution'):
            reviews.add('execution')
        elif 'gnss' in code:
            reviews.add('GNSS')
        elif 'frame' in code or 'reference' in code:
            reviews.add('reference/frame')
        else:
            reviews.add('evidence')
    if reviews:
        flags.append('🟡 review: ' + ', '.join(sorted(reviews)))
    elif (review['protocol_state'] == 'blocked' and review['attempt_count']
          and review.get('protocol_verified_attempts', 0) < review['attempt_count']):
        # Missing repetitions alone are a planning gap, not an open review of recorded evidence.
        flags.append('🟡 review: evidence')
    if review['protocol_state'] == 'invalid_setup' and not reruns:
        flags.append('rerun: setup')
    collapse = [run_label(a, i) for i, a in enumerate(attempts, 1) if a.get('numerical_status') == 'scale_collapse']
    if collapse:
        flags.append('collapse ' + ','.join(collapse))
    if any(a.get('numerical_status') == 'eval_failed' for a in attempts):
        flags.append('invalid export')
    if any('sparse_keyframe' in s for s in limits):
        flags.append('keyframes')
    if review.get('completed_export_shutdown_error_count'):
        flags.append('completed export; shutdown error')
    elif any('shutdown_error' in s for s in limits):
        flags.append('shutdown error')
    if any('coverage_below' in s for s in limits):
        flags.append('partial')
    if any('offline_map_refinement' in s for s in limits):
        flags.append('offline refinement')
    if any('no_final_vio_lc_trajectory' in s for s in limits):
        flags.append('no final export')
    if cell['dataset'] == 'zed2i' and review['evaluated_trajectory_count']:
        flags.append('nominal position')
    if review.get('attempts', {}).get('accepted_with_limitation') and not any(
            s in flags for s in ('keyframes', 'partial', 'shutdown error', 'completed export; shutdown error', 'offline refinement', 'nominal position')):
        flags.append('limits')
    if review['missing_attempt_count']:
        flags.append(f"missing {review['missing_attempt_count']}")
    if len(review['protocol_cohorts']) > 1 or not cell.get('within_cell_cohort_consistent', True):
        flags.append('separate groups')
    pooling = cell.get('cohort_pooling') or {}
    if pooling.get('status') == 'pooled':
        flags.append(f"spans {len(pooling['workspace_commits'])} commits (receipts identical)")
    elif pooling.get('status') == 'refused':
        flags.append('pooling refused')
    selected = [run_label(a, i) for i, a in enumerate(attempts, 1)]
    if selected != [f'r{i}' for i in range(1, len(attempts) + 1)]:
        flags.append('selected ' + ','.join(selected))
    return flags


def selected_campaign(key, campaigns):
    """Honor an explicit replacement plan; never pool plans or prefer a ready flag."""
    candidates = [c for c in campaigns if any(a['cell'] == key for a in c['actions'])]
    if len(candidates) == 1:
        return candidates[0]
    winners = [c for c in candidates if all(
        other is c or c.get('replaces_selection_in') == other['path'] for other in candidates)]
    return winners[0] if len(winners) == 1 else None


def cell_next_action(cell, campaigns):
    campaign = selected_campaign(cell_key(cell), campaigns)
    actions = [a for a in campaign['actions'] if a['cell'] == cell_key(cell)] if campaign else []
    ready_ids = {a['id'] for a in ready_actions(campaign)} if campaign else set()
    planned = [a for a in actions if a['category'] in ('required_rerun', 'missing', 'cohort_completion')]
    reruns = [a for a in planned if a['category'] == 'required_rerun']
    return dict(campaign=campaign, actions=actions, planned=planned, reruns=reruns,
                ready_count=sum(a['id'] in ready_ids for a in planned),
                all_ready=bool(planned) and all(a['id'] in ready_ids for a in planned),
                reruns_ready=bool(reruns) and all(a['id'] in ready_ids for a in reruns),
                ready_reruns=sum(a['id'] in ready_ids for a in reruns))


def next_action_labels(cell, review, next_action):
    confirmed = (review['protocol_state'] == 'invalid_setup' or any(
        a.get('confirmed_protocol_findings') for a in cell['attempts']))
    labels = []
    planned = next_action['planned']
    if confirmed:
        ready = next_action['reruns_ready']
        detail = 'ready' if ready else 'not ready'
        if next_action['ready_reruns'] and not ready:
            detail += f" ({next_action['ready_reruns']}/{len(next_action['reruns'])} ready)"
        labels.append(('🔄' if ready else '🔴') + ' rerun ' + detail)
        remaining = [a for a in planned if a['category'] != 'required_rerun']
    else:
        remaining = planned
    if remaining:
        ready_ids = {a['id'] for a in ready_actions(next_action['campaign'])}
        n_ready = sum(a['id'] in ready_ids for a in remaining)
        name = 'new group' if any(a['category'] == 'cohort_completion' for a in remaining) else 'missing'
        state = 'ready' if n_ready == len(remaining) else 'not ready'
        suffix = f'; {n_ready}/{len(remaining)} ready' if 0 < n_ready < len(remaining) else ''
        labels.append(f'next: {name} {len(remaining)} {state}' + suffix)
    elif not confirmed and not review['protocol_verified_n3']:
        if len(review['protocol_cohorts']) > 1:
            labels.append('🟡 next: group review (not ready)')
        elif review['missing_attempt_count'] or not review['attempt_count']:
            labels.append(f"next: missing {review['missing_attempt_count']} not ready" if review['missing_attempt_count'] else 'next: attempts not ready')
        elif not any(a['category'] == 'blocked' for a in next_action['actions']):
            labels.append('🟡 next: review (not ready)')
    return labels


def render_cell(cell, campaigns=()):
    review = acceptance(cell)
    next_action = cell_next_action(cell, campaigns)
    labels = next_action_labels(cell, review, next_action)
    flags = short_flags(cell, review)
    rerun_reason = next((f.removeprefix('rerun: ') for f in flags if f.startswith('rerun: ')), None)
    flags = [f for f in flags if not f.startswith('rerun: ')]
    if rerun_reason:
        labels[0] += ': ' + rerun_reason
    missing = review['missing_attempt_count']
    if missing and any(s.startswith(f'next: missing {missing} ') for s in labels):
        flags = [s for s in flags if s != f'missing {missing}']
    groups = sorted(c['verified_completed'] for c in review['protocol_cohorts'] if c['verified_completed'])
    if review['protocol_verified_n3']:
        label = '✅ N=3'
    elif groups and all(n in (1, 2) for n in groups):
        label = ' + '.join(f'🟢 N={n}' for n in groups)
    else:
        label = f"{review['attempt_count']} recorded" if review['attempt_count'] else 'no attempts'
    # Rerun/review severity leads the cell; verification and readiness are separate.
    if any(s.startswith(('🔄 rerun', '🔴 rerun')) for s in labels):
        label = '🟥 ' + label
    elif any(s.startswith('🟡') for s in labels + flags):
        label = '🟨 ' + label
    elif not review['attempt_count']:
        label = ('🔜' if next_action['all_ready'] else '❌') + ' ' + label
    target = DETAILS + '#' + anchor(cell_key(cell))
    suffix = '; '.join(labels + flags)
    return f'[{label}]({target}); {counts(review)}' + ('; ' + suffix if suffix else '')


def excluded_attempts(inventory, mode, ds, seq, algorithm):
    prefix = f'results/{mode}/{ds}/{seq}/{algorithm}/'
    return [a for a in inventory.get('other_artifacts', [])
            if a.get('category') == 'historical_excluded' and a['path'].startswith(prefix)]


def render_excluded(inventory, mode, ds, seq, algorithm, previous):
    attempts = excluded_attempts(inventory, mode, ds, seq, algorithm)
    suffix = ''
    if attempts:
        tally = counts(summarize_attempts(attempts))
        suffix = '; historical'
    elif 'old OOM' in previous or 'reported OOM' in previous:
        tally = 'A?/E?/S?/F?'
        suffix = '; reported OOM (12 GB)'
    else:
        tally = 'A0/E0/S0/F0'
        suffix = '; config missing' if 'config missing' in previous else '; no recorded run'
    return f'[➖ excluded]({DETAILS}#excluded-history); {tally}{suffix}'


def update(text, inventory, campaigns=()):
    """Only replace cells; keep every matrix, row, column and surrounding note."""
    cells = {(c['run_type'], c['algorithm'], c['dataset'], c['sequence']): c for c in inventory['cells']}
    mode = None
    out, seen = [], set()
    for line in text.splitlines():
        if line.startswith('## '):
            mode = None
        match = re.match(r'### .*`results/([^/]+)/`', line)
        if match:
            mode = match[1]
            seen.add(mode)
        if mode and line.startswith('| '):
            parts = line.split('|')
            name = parts[1].strip()
            if name in NAMES or name in EXCLUDED:
                sequences = SEQUENCES[:4] if mode == 'gnss-vio' else SEQUENCES
                if len(parts) != len(sequences) + 3:
                    raise ValueError('unexpected TODO matrix column layout')
                for i, (ds, seq) in enumerate(sequences, 2):
                    value = (render_cell(cells[(mode, NAMES[name], ds, seq)], campaigns) if name in NAMES else
                             render_excluded(inventory, mode, ds, seq, EXCLUDED[name], parts[i]))
                    parts[i] = ' ' + value + ' '
                line = '|'.join(parts)
        out.append(line)
    if seen != MODES:
        raise ValueError('missing one or more existing mode matrices')
    return '\n'.join(out) + '\n'


def load_campaigns(evidence_root, paths):
    """Readiness is a reviewed snapshot, never inferred from config existence.

Use the existing read-only validator to check schema, prerequisites and pinned
files. Do not call execute, runtime capture, or production result generators.
"""
    campaigns = []
    for path in paths:
        path = Path(path)
        source = path if path.is_absolute() else evidence_root / path
        record = {'path': str(path), 'actions': [], 'errors': []}
        try:
            raw = source.read_bytes()
            manifest = json.loads(raw)
            record.update(sha256=hashlib.sha256(raw).hexdigest(),
                          campaign_id=manifest['campaign_id'], actions=manifest['actions'],
                          replaces_selection_in=manifest.get('replaces_selection_in'),
                          errors=validate(evidence_root, manifest))
        except (OSError, ValueError, KeyError, TypeError) as error:
            record['errors'] = [str(error)]
        campaigns.append(record)
    return campaigns


def ready_actions(campaign):
    if campaign['errors']:
        return []
    return [a for a in campaign['actions'] if a['category'] in ('missing', 'required_rerun', 'cohort_completion')
            and not a.get('prerequisites') and a.get('review_evidence')
            and a.get('readiness', {}).get('verified_ready_to_run')
            and a['readiness'].get('static_checks') == 'verified'
            and a['readiness'].get('execution_validation') == 'verified']


def readiness_text(campaigns):
    lines = ['<!-- todo-execution-readiness:start -->', '**Future execution readiness — reviewed snapshot**', '',
             'These plans describe reviewed checks, not live campaign progress or permission to',
             'launch. Short checks do not establish full-sequence stability. A live attempt',
             'enters the matrices only after its evidence has been reviewed.', '',
             '| Plan | Reviewed new-attempt readiness | Details |', '|---|---|---|']
    for campaign in campaigns:
        label = campaign.get('campaign_id', campaign['path'])
        actions = [a for a in campaign['actions'] if a['category'] in ('missing', 'required_rerun', 'cohort_completion')]
        status = ('Unverified: missing/stale evidence' if campaign['errors'] else
                  f'{len(ready_actions(campaign))}/{len(actions)} planned new attempts passed reviewed checks')
        lines.append(f'| {label} | {status} | [Evidence and prerequisites]({DETAILS}#future-execution-readiness) |')
    if not campaigns:
        lines.append(f'| No reviewed manifest supplied | Unverified | [Details]({DETAILS}#future-execution-readiness) |')
    lines += ['', 'The coherent ZED plan replaces the ZED selection in the five-mode plan; do not',
              'add their counts or execute both. Saved-result ticks remain independent of these',
              'readiness checks. The TODO and linked details are documentation only. Generator',
              'and test changes stay isolated until the active batch and capture finish; any later',
              'implementation update needs reviewed campaign pins before another launch.',
              '<!-- todo-execution-readiness:end -->']
    return '\n'.join(lines)


def update_legend(text, campaigns):
    heading = '## Run combinations matrix\n'
    if heading not in text:
        raise ValueError('missing matrix introduction')
    start = text.index(heading) + len(heading)
    stop = text.index('### ', start)
    return text[:start] + '\n' + LEGEND + '\n\n' + readiness_text(campaigns) + '\n\n' + text[stop:]


def code_list(values):
    return ', '.join('`' + str(value).replace('|', '&#124;').replace('\n', ' ') + '`'
                     for value in sorted(set(values))) or 'none'


def render_details(inventory, inventory_sha, campaigns):
    lines = ['# TODO status details', '',
             'Generated presentation of the reviewed inventory; no acceptance decisions or scores are changed.',
             f'Inventory SHA-256: `{inventory_sha}`. [Matrix legend](../TODO.md#run-combinations-matrix).',
             '[Source inventory](../results/repair-20261001/inventory.json); '
             '[acceptance ledger](campaigns/paper-acceptance-20261001.json); '
             '[review definitions](protocol-review-20261002.md).', '',
             'N counts completed verified attempts. Counts describe the selected physical runs, including',
             'failures. Clean exports can still have limited coverage or accuracy. Reference/evaluation',
             'review alone is not a confirmed rerun requirement. Exact blocker/limit identifiers below',
             'are copied from the inventory and its acceptance ledger.', '',
             'Cell-leading 🟥 marks a confirmed rerun; otherwise 🟨 marks unresolved review.',
             'Rosario candidates are integrated into main; native readiness remains unverified.',
             'See [integration and remaining prerequisites](rosario-main-integration-20261002.md).',
             'Rerun items use 🔴 for not ready and 🔄 for verified ready; review items use 🟡.',
             '✅ N=3 and 🟢 N=1/N=2 describe verified groups. Unverified or invalid history',
             'uses recorded-attempt counts; it never receives a verified repetition label.', '',
             'Common limits: accuracy is conditional on saved exports and reference support; no measured',
             'processing-rate or real-time deadline claim is established. ZED uses the qualified nominal',
             'position reference, retains RTK float, and discloses mounting and clock uncertainty.', '',
             '## Future execution readiness', '',
             'This is a snapshot of reviewed campaign evidence, not a live scheduler. Configuration',
             'existence alone cannot establish readiness. Validation checks the manifest structure and',
             'its pinned evidence. Later launch still requires current input/runtime checks and the',
             'applicable authorization. ZED readiness covers bounded checks only. Cell symbols use',
             'the coherent ZED replacement where present, otherwise the five-mode plan. Conflicting',
             'or stale plans cannot establish readiness. Missing group-completion plans remain review',
             'items; separately verified N=1 and N=2 never become one N=3.', '']
    for campaign in campaigns:
        lines += [f"### {campaign.get('campaign_id', campaign['path'])}", '',
                  f"Manifest: [{campaign['path']}](../{campaign['path']}); SHA-256: `{campaign.get('sha256', 'unavailable')}`.",
                  f"Categories: {code_list(f'{k}={v}' for k, v in Counter(a['category'] for a in campaign['actions']).items())}.",
                  f"Verified new-attempt readiness: **{len(ready_actions(campaign))}**.", '']
        if campaign['errors']:
            lines += ['Evidence validation errors (readiness is unverified):', '',
                      *['- ' + str(error) for error in campaign['errors']], '']
    if not campaigns:
        lines += ['No reviewed campaign supplied; future execution readiness is unverified.', '']
    lines += ['The coherent ZED selection replaces its part of the five-mode plan. Counts must not be added.', '',
              '## Excluded history', '',
              'MASt3R-SLAM, MegaSaM and DROID-SLAM remain excluded. The reported MASt3R/MegaSaM OOM',
              'events concern the earlier 12 GB machine, not a measured OOM on the 24 GB server.',
              'Their attempt/export/failure totals are not documented in this inventory: `A?/E?/S?/F?`.',
              'Zero counts in the ZED exclusions mean no recorded attempt in this inventory.',
              'DROID-SLAM counts below are historical observations; unrecorded exits stay unknown (U),',
              'and historical N=3 does not become a verified tick.', '']
    for a in inventory.get('other_artifacts', []):
        if a.get('category') in ('historical_excluded', 'superseded_calibration_cohort'):
            p = attempt_protocol(a)
            lines.append(f"- `{a['path']}`: {a['category']}; {counts(summarize_attempts([a]))}; "
                         f"{p['observed_outcome']}; exit {a.get('process', {}).get('exit_code', 'unknown')}; "
                         f"numerical status {a.get('numerical_status') or 'not evaluated'}.")
    lines += ['', 'Superseded AirSLAM runs1–3 remain above; selected corrected runs4–6 are detailed below.',
              'Displaced ZED run1 histories remain above; the three predeclared completed run10001 attempts',
              'are selected into their original first logical slots below, with claim review still pending.',
              'Neither a failure in a selected run nor a failure in the preserved cohort is discarded.', '']
    for cell in inventory['cells']:
        key = cell_key(cell)
        review = acceptance(cell)
        next_action = cell_next_action(cell, campaigns)
        next_labels = next_action_labels(cell, review, next_action)
        plan_name = (next_action['campaign'].get('campaign_id') if next_action['campaign'] else None)
        lines += [f'<a id="{anchor(key)}"></a>', f'## {key}', '',
                  f"**{counts(review)}**; verified completed groups: " +
                  ('+'.join(str(c['verified_completed']) for c in review['protocol_cohorts']) or '0') +
                  f". Verified N=3: {'yes' if review['protocol_verified_n3'] else 'no'}.", '',
                  'Cell next-action display: ' + ('; '.join(next_labels) or 'no new action required by this plan') + '.',
                  f"Selected plan: `{plan_name or 'none / ambiguous; readiness unverified'}`.", '',
                  '| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |',
                  '|---|---|---|---|---|---|']
        for i, a in enumerate(cell['attempts'], 1):
            p = attempt_protocol(a)
            path = a.get('path')
            link = f'[{Path(path).name}](../{path})' if path else 'absent'
            exit_code = a.get('process', {}).get('exit_code')
            lines.append(f"| {a.get('logical_repetition', i)} | {link} | {p['protocol_status']} | "
                         f"{p['observed_outcome']} | {exit_code if exit_code is not None else 'unknown'} | "
                         f"{'yes' if a.get('evaluated') else 'no'} |")
        lines += ['']
        for group in review['protocol_cohorts']:
            lines.append(f"Group `{group['cohort']}`: {group['verified_completed']} verified / "
                         f"{group['attempts']} recorded; {code_list(Path(p).name for p in group['run_paths'] if p)}.")
        findings = [f['code'] for a in cell['attempts'] for f in a.get('confirmed_protocol_findings', [])]
        limits = [s for a in cell['attempts'] for s in a.get('qualification', {}).get('claim_limits', [])]
        lines += ['', 'Confirmed setup findings: ' + code_list(findings) + '.',
                  'Review blockers: ' + code_list(review_codes(cell)) + '.',
                  'Claim limits: ' + code_list(limits) + '.']
        if (cell.get('dataset') == 'rosariov2' and cell.get('run_type') == 'vio'
                and 'rosario_identity_camera_imu_extrinsic' in findings):
            lines += ['', 'Candidate preparation (2026-10-02): [published-profile candidates and remaining prerequisites]'
                      '(rosario-vio-candidates-20261002.md) are integrated into this main checkout. '
                      '**Execution remains unverified; historical validity is unchanged.** '
                      'The 14 confirmed replacements across these six cells remain red; '
                      'four absent OpenVINS repetitions remain missing, not failed.']
        for i, a in enumerate(cell['attempts'], 1):
            errors = a.get('qualification', {}).get('native_error_observations', [])
            if errors:
                lines.append(f"Native failure evidence {run_label(a, i)}: " +
                             code_list(json.dumps(e, sort_keys=True, ensure_ascii=False) for e in errors) + '.')
        for campaign in campaigns:
            actions = [a for a in campaign['actions'] if a['cell'] == key]
            if not actions:
                continue
            ready_ids = {a['id'] for a in ready_actions(campaign)}
            labels = [f"r{a['repetition']} {a['category']}" +
                      ('; checks verified' if a['id'] in ready_ids else '; readiness unverified'
                       if a['category'] != 'reusable' else '; retained observation') for a in actions]
            lines += ['', f"Future plan `{campaign.get('campaign_id', campaign['path'])}`: " + '; '.join(labels) + '.',
                      'Prerequisites: ' + code_list(p for a in actions for p in a.get('prerequisites', [])) + '.']
        lines += ['']
    return '\n'.join(lines).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-root', type=Path, default=REPO)
    parser.add_argument('--inventory', type=Path)
    parser.add_argument('--manifest', type=Path, action='append')
    parser.add_argument('--input', type=Path, default=REPO / 'TODO.md')
    parser.add_argument('--output', type=Path, default=REPO / 'TODO.md')
    parser.add_argument('--details', type=Path, default=REPO / DETAILS)
    args = parser.parse_args()
    path = args.inventory or args.evidence_root / 'results/repair-20261001/inventory.json'
    raw = path.read_bytes()
    inventory = json.loads(raw)
    campaigns = load_campaigns(args.evidence_root, args.manifest or MANIFESTS)
    result = update_legend(update(args.input.read_text(), inventory, campaigns), campaigns)
    detail = render_details(inventory, hashlib.sha256(raw).hexdigest(), campaigns)
    args.details.write_text(detail)
    args.output.write_text(result)


if __name__ == '__main__':
    main()
