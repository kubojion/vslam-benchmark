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
         'OpenVINS+GPS': 'openvins_gps', 'OKVIS2-X (tight)': 'okvis2x'}
EXCLUDED = {'MASt3R-SLAM': 'mast3r_slam', 'MegaSaM': 'megasam', 'DROID-SLAM': 'droidslam'}
SEQUENCES = [('rosariov2', 'sequence1'), ('rosariov2', 'sequence5'),
             ('hortimulti', 'strawberry02'), ('hortimulti', 'strawberry03'),
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
}
LEGEND = """<!-- todo-matrix-legend:start -->
**A = recorded attempts; E = trajectories evaluated; S = clean final exports;
F = observed failures; U = unknown outcomes, when present.**

Example: **A3/E3/S0/F3** means three attempts, three evaluated trajectories,
no clean final exports and three observed failures. A failed attempt can still
produce an evaluable trajectory, so these counts overlap. S does not certify
accuracy or full coverage. `?` means a legacy count is not documented.

**✅ N=3 means three verified attempts under consistent settings, including valid
observed failures—not necessarily three successful runs.** N counts verified,
completed attempts; A also includes attempts awaiting review or using invalid
settings. `N=0; A3` therefore means three recorded attempts with none verified.
`N=1+2` denotes separate implementation groups; it cannot be pooled into N=3.

| Mark | Meaning for saved attempts |
|---|---|
| ✅ | Verified N=3 in one implementation group; retain listed claim limits and failures |
| 🟠 | Separate implementation groups; linked details identify each group |
| 🟡 review | Evidence, reference/evaluation or execution review remains; a rerun is not yet established |
| 🔁 rerun | Confirmed setup defect requires corrected execution; additional review may also remain |
| ⬜ | Recorded repetitions are missing; linked details distinguish missing from failed attempts |
| ➖ | Excluded from the target; historical counts and reported failures remain visible |

Cell links give selected physical run IDs, exits, failure evidence, implementation
groups, review blockers and claim limits. `missing` counts absent attempts only.
Sparse keyframes, partial exports and low accuracy alone do not require reruns.
The 45 legacy clean-qualified cells and all underlying acceptance decisions are
unchanged. ZED ticks support qualified nominal position claims, with RTK float,
mounting and clock limits; they do not certify surveyed 6-DoF reference accuracy.
Future execution readiness is reported separately below and is never implied by
N=3 or the existence of a configuration file.
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
        flags.append('review: ' + ', '.join(sorted(reviews)))
    elif review['protocol_state'] == 'blocked':
        flags.append('review: evidence')
    if review['protocol_state'] == 'invalid_setup' and not reruns:
        flags.append('rerun: setup')
    collapse = [run_label(a, i) for i, a in enumerate(attempts, 1) if a.get('numerical_status') == 'scale_collapse']
    if collapse:
        flags.append('collapse ' + ','.join(collapse))
    if any(a.get('numerical_status') == 'eval_failed' for a in attempts):
        flags.append('invalid export')
    if any('sparse_keyframe' in s for s in limits):
        flags.append('keyframes')
    if any('shutdown_error' in s for s in limits):
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
            s in flags for s in ('keyframes', 'partial', 'shutdown error', 'offline refinement', 'nominal position')):
        flags.append('limits')
    if review['missing_attempt_count']:
        flags.append(f"missing {review['missing_attempt_count']}")
    if len(review['protocol_cohorts']) > 1 or not cell.get('within_cell_cohort_consistent', True):
        flags.append('separate groups')
    selected = [run_label(a, i) for i, a in enumerate(attempts, 1)]
    if selected != [f'r{i}' for i in range(1, len(attempts) + 1)]:
        flags.append('selected ' + ','.join(selected))
    return flags


def render_cell(cell):
    review = acceptance(cell)
    state = review['protocol_state']
    icon = ('✅' if review['protocol_verified_n3'] else '🔁' if state == 'invalid_setup'
            else '🟡' if state == 'blocked' else '🟠' if state == 'separate_implementation_cohorts' else '⬜')
    groups = sorted(c['verified_completed'] for c in review['protocol_cohorts'] if c['verified_completed'])
    n = '+'.join(map(str, groups)) if groups else '0'
    label = f'{icon} N={n}'
    flags = short_flags(cell, review)
    target = DETAILS + '#' + anchor(cell_key(cell))
    # A single link per cell keeps raw Markdown readable as well as the rendered table.
    return f'[{label}]({target}); {counts(review)}' + (f"; {'; '.join(flags)}" if flags else '')


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


def update(text, inventory):
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
                    value = (render_cell(cells[(mode, NAMES[name], ds, seq)]) if name in NAMES else
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
              'readiness checks. Refresh pinned campaign evidence after presentation files change,',
              'before any later launch; this renderer never rewrites campaign pins.',
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
             'Common limits: accuracy is conditional on saved exports and reference support; no measured',
             'processing-rate or real-time deadline claim is established. ZED uses the qualified nominal',
             'position reference, retains RTK float, and discloses mounting and clock uncertainty.', '',
             '## Future execution readiness', '',
             'This is a snapshot of reviewed campaign evidence, not a live scheduler. Configuration',
             'existence alone cannot establish readiness. Validation checks the manifest structure and',
             'its pinned evidence. Later launch still requires current input/runtime checks and the',
             'applicable authorization. ZED readiness covers bounded checks only.', '']
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
              'Neither a failure in a selected run nor a failure in the preserved cohort is discarded.', '']
    for cell in inventory['cells']:
        key = cell_key(cell)
        review = acceptance(cell)
        lines += [f'<a id="{anchor(key)}"></a>', f'## {key}', '',
                  f"**{counts(review)}**; verified completed groups: " +
                  ('+'.join(str(c['verified_completed']) for c in review['protocol_cohorts']) or '0') +
                  f". Verified N=3: {'yes' if review['protocol_verified_n3'] else 'no'}.", '',
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
    result = update_legend(update(args.input.read_text(), inventory), campaigns)
    detail = render_details(inventory, hashlib.sha256(raw).hexdigest(), campaigns)
    args.details.write_text(detail)
    args.output.write_text(result)


if __name__ == '__main__':
    main()
