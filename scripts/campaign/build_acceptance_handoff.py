#!/usr/bin/env python3
"""Render current claim decisions and exact remaining actions from checked evidence."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'scripts/eval'))
from build_benchmark_csv import load_inventory, preserved_write
from build_future_manifest import action_category


def main():
    inv=load_inventory(REPO/'results/repair-20261001/inventory.json')
    proof_path=REPO/'docs/campaigns/euroc-focused-validation-20261001.json'
    proof=json.loads(proof_path.read_text()) if proof_path.is_file() else {}
    focused=proof.get('complete',False)
    zed_path=REPO/'docs/campaigns/zed-readiness-review-20261002.json'
    zed=json.loads(zed_path.read_text()).get('cells',{}) if zed_path.is_file() else {}
    validated_cells={'/'.join(a['output'].split('/')[1:5]) for a in proof.get('records',[]) if a.get('execution_verified')}
    actions=[]
    for cell in inv['cells']:
        for i,attempt in enumerate(cell['attempts'],1):
            category,reason=action_category(cell,attempt,{})
            actions.append(dict(cell=cell['key'],repetition=i,path=attempt['path'],category=category,
                reason=reason,qualification=attempt['qualification']))
    counts=Counter(a['category'] for a in actions)
    estimates=[c['runtime_estimate']['estimate_s'] for c in inv['cells'] for a in c['attempts']
               if action_category(c,a,{})[0] in ('required_rerun','missing')]
    known=[x for x in estimates if x is not None]
    # One representative per repaired algorithm/mode path, plus the distinct
    # ORB ZED VIO-LC failure. These are diagnostic targets, NOT launch commands
    # or permission to run a full sequence/campaign.
    groups=defaultdict(list)
    for c in inv['cells']:groups[c['algorithm'],c['run_type']].append(c)
    diagnostics=[]
    for (algo,mode),cells in sorted(groups.items()):
        ds,seq=('rosariov2','sequence1') if mode=='gnss-vio' else ('euroc_mav','MH_01_easy')
        if algo=='orbslam3':
            ds,seq=('hortimulti','strawberry02') if mode=='vio-lc' else ('zed2i','field1_110426_full_10fps_q90')
        if algo in ('okvis2','okvis2x') and mode=='vo-lc':ds,seq='zed2i','field1_110426_full_10fps_q90'
        if algo=='voxel_svio':seq='MH_03_medium'
        cell=next(c for c in cells if (c['dataset'],c['sequence'])==(ds,seq))
        diagnostics.append(dict(cell=cell['key'],first_batch=(algo=='openvins' or algo=='airslam' and mode.startswith('vio')),
            verified_ready_to_run=False,estimated_full_sequence_s=cell['runtime_estimate']['estimate_s'],
            purpose='native config/input loading, output isolation, actual native exit, saved export, immediate evaluation and resume',
            prerequisite='resolve cell-specific build/calibration/input prerequisites; separately authorize bounded diagnostic recipe'))
    diagnostics.append(dict(cell='vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3',first_batch=False,
        verified_ready_to_run=False,estimated_full_sequence_s=None,
        purpose='distinct ZED inertial+LC startup/optimizer crash',prerequisite='serial-specific calibration and native crash diagnosis'))
    for d in diagnostics:
        d['focused_execution_validated']=focused and d['cell'] in validated_cells
        d['zed_short_execution_validated']=zed.get(d['cell'],{}).get('execution_verified',False)
        if d['zed_short_execution_validated']:
            d['prerequisite']='First authorized full repetition is the production gate; short checks do not certify full-sequence stability.'
    protocol_totals={key:sum(c['acceptance'][key] for c in inv['cells']) for key in
        ('protocol_verified_n3','protocol_verified_attempts','verified_failure_count',
         'attempt_count','completed_attempt_count','evaluated_trajectory_count',
         'successful_run_count','observed_failure_count','unknown_outcome_count','missing_attempt_count')}
    output=dict(schema=2,protocol_totals=protocol_totals,claim_review='docs/paper-acceptance-20261001.md',protocol_review='docs/protocol-review-20261002.md',categories=dict(counts),
        actions=actions,diagnostic_targets=diagnostics,diagnostics_are_not_campaign_repetitions=True,
        execution_authorized=False, completed_focused_campaign=str(proof_path.relative_to(REPO)) if focused else None)
    preserved_write(REPO/'results/acceptance-20261001/handoff.json',json.dumps(output,indent=2)+'\n')
    lines=['# Acceptance handoff — 2026-10-01','',
        'Generated from the checked inventory. The [claim review](paper-acceptance-20261001.md) defines eligibility, limitations and evidence. '
        'This includes the [matched-session calibration review](reference-review-20261001.md): Rosario frame-dependent metrics were corrected; accepted EuRoC values and original attempts are preserved. '+
        ('**Acceptance review complete; focused EuRoC OpenVINS/AirSLAM execution validated. ZED short-check readiness is recorded separately below.**' if focused else '**Acceptance review complete; see the separate native execution evidence.**'),'',
        '| Mode | Protocol-verified N=3 cells | Accepted accuracy claims | Limited accuracy claims | Failure-only claim observations | Required reruns | Missing | Blocked |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for mode in ('vo','vo-lc','vio','vio-lc','gnss-vio'):
        group=[c for c in inv['cells'] if c['run_type']==mode]
        states=Counter(a['qualification']['status'] for c in group for a in c['attempts'])
        lines.append(f"| {mode} | {sum(c['acceptance']['protocol_verified_n3'] for c in group)} | "+' | '.join(str(states[s]) for s in ('accepted','accepted_with_limitation','valid_observed_failure','rerun_required','not_executed','blocked'))+' |')
    lines+=['','Protocol counts are separate from claim-status counts above. Success means a clean final export; native errors after saving remain failures with potentially usable accuracy.', '',
        '| Mode | Verified attempts | Verified failures | Attempts | Evaluated | Clean exports | Observed failures | Unknown |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for mode in ('vo','vo-lc','vio','vio-lc','gnss-vio'):
        group=[c for c in inv['cells'] if c['run_type']==mode]
        lines.append('| '+mode+' | '+' | '.join(str(sum(c['acceptance'][k] for c in group)) for k in
            ('protocol_verified_attempts','verified_failure_count','attempt_count','evaluated_trajectory_count',
             'successful_run_count','observed_failure_count','unknown_outcome_count'))+' |')
    lines+=['', '**OpenVINS cohort completeness:** each EuRoC sequence has historical N=1 plus patched N=2. '+
        'The selected logical slots are consumed. One additional patched repetition per sequence would complete that implementation cohort, only if separately authorized. '+
        'These three potential additions are separate from the 81 absent planned slots and are not scheduled here. Old cohorts are not resampled for success.', '']
    lines+=['',f"Future default actions: {counts['reusable']} reusable observations, {counts['required_rerun']} required reruns, {counts['missing']} missing repetitions, {counts['blocked']} blocked. "+
        ('The separately authorized focused EuRoC campaign is complete; its 24 attempts yielded 23 final evaluations and one retained native refinement failure. The later ZED preparation used bounded diagnostics only; no ZED production repetitions or push occurred.' if focused else 'Retaining an observation does not certify a repaired runner.'), '',
        '## Protocol-verified N=3 cells', '', '| Cell | Accepted claim |','|---|---|']
    for c in inv['cells']:
        if c['acceptance']['protocol_verified_n3']:
            lines.append(f"| `{c['key']}` | {c['attempts'][0]['qualification']['claim']} |")
    lines+=['','## Limited results and accepted failures','','| Attempt | Acceptance | Specific limit |','|---|---|---|']
    for a in actions:
        q=a['qualification']
        if q['status'] in ('accepted_with_limitation','valid_observed_failure'):
            limits=[s for s in q['claim_limits'] if s not in ('accuracy_conditional_on_observed_exports_and_reference_support','no_measured_processing_rate_or_realtime_deadline_claim')]
            lines.append(f"| `{a['path']}` | {q['status']} | {'; '.join(limits)} |")
    lines+=['','## Exact required reruns','',f"There are {counts['required_rerun']} remaining distinct confirmed cases after the current cohort selection. Superseded affected AirSLAM attempts remain in their original directories and the historical-cohort CSV. Preserve every original attempt and use a new physical ID/cohort.",'',
        '| Cell | Logical repetitions | Concrete defect |','|---|---|---|']
    for c in inv['cells']:
        rows=[a for a in actions if a['cell']==c['key'] and a['category']=='required_rerun']
        if rows:lines.append(f"| `{c['key']}` | {', '.join('r'+str(a['repetition']) for a in rows)} | {rows[0]['reason']} |")
    lines+=['','## Exact missing repetitions','','Missing means no original attempt directory; an existing failed attempt is not reclassified as missing.','',
        '| Cell | Missing logical repetitions |','|---|---|']
    for c in inv['cells']:
        rows=[a for a in actions if a['cell']==c['key'] and a['category']=='missing']
        if rows:lines.append(f"| `{c['key']}` | {', '.join('r'+str(a['repetition']) for a in rows)} |")
    blockers=Counter(b for a in actions if a['category']=='blocked' for b in a['qualification']['blockers'])
    lines+=['','## Material blockers','','Exact affected attempt IDs and evidence are in `results/acceptance-20261001/handoff.json` and the future manifest. Counts overlap across blockers.','',
        '| Evidence needed | Blocked attempts |','|---|---:|']
    lines += [f'| {b} | {n} |' for b,n in sorted(blockers.items())]
    if focused:
        lines+=['','## Completed focused execution','',
            'The three EuRoC OpenVINS/AirSLAM integration targets and first full gates passed. All six missing OpenVINS repetitions and all 18 corrected AirSLAM slots were consumed once, with immediate evaluation where final output existed and no success-conditioned retries. MH05 VIO-LC run4 has a native refinement SIGSEGV without final output (later reproduced in the map publisher; exact cause unresolved); runs5–6 succeeded. '
            'See [the focused campaign](euroc-focused-campaign-20261001.md) for source, build, configuration, output and shutdown evidence. '
            'AirSLAM supports sparse-keyframe accuracy; OpenVINS original run1 limitations and its separate implementation cohort remain. Protocol ticks include verified failures and supported sparse/partial outputs; OpenVINS implementation cohorts remain N=1 and N=2.', '',
            '## Remaining execution prerequisites','',
            'The [ZED preparation](zed-preparation-20261002.md) validates 15 repaired algorithm/mode paths on a fixed 60-second input, including all four ORB modes. Voxel shutdown/failure reporting is verified, but initialization and successful trajectory export remain unverified. The non-ZED ORB build and OV2SLAM shutdown issues remain prerequisites. Rosario/HortiMulti/GNSS calibration/reference blockers are unchanged. Historical OKVIS interruptions remain unresolved outcomes. No production execution is authorized by this handoff.', '',
            '**ZED cohort plan:** retain nine complete N=3 cells (27 observations). The remaining sixteen cells need 48 new attempts: 17 setup replacements, 25 missing slots and six separately labelled cohort-completion attempts. The latter preserve historical outcomes and are not confirmed parameter defects. Use the alternative `results/zed-preparation-20261002/campaign/manifest.json`; do not execute it in addition to the overlapping all-mode plan. See the ZED report for bounded readiness and timing proxies.']
    else:
        lines+=['','## Next execution, after authorization','','First resolve static prerequisites: apply/build the reviewed AirSLAM rectification patch; verify the corrected ORB FPS/IMU profiles load; capture actual native exits separately from wrapper/player exits; diagnose OV2SLAM/Voxel shutdown and the remaining ORB/OKVIS ZED execution failures. '
        'Retain the existing final-optimization/profile choices; do not tune them on these test scores. Resolve the specific remaining image/projection, reference-origin/time and GNSS-input issues in the matched-session review before qualified production comparisons.','',
        '**Smallest useful first batch: three diagnostic targets** — OpenVINS EuRoC MH01 VIO, AirSLAM EuRoC MH01 VIO, and AirSLAM EuRoC MH01 VIO-LC. '
        'These cover the shutdown/capture path and both patched Air inertial stages needed for the immediately actionable EuRoC missing/rerun cases. '
        'Freeze a separately labelled bounded-input diagnostic recipe, preserve its input subset and all output, and exercise normal completion plus safe interruption/resume without overwriting. '
        'A truncated diagnostic cannot certify full-sequence stability, LC occurrence or runtime. After it passes, the first production repetition is the full-sequence gate and must be evaluated before continuing.','',
        '**Whole-scope readiness remains conditional:** the following 31 representative targets cover each of the 30 repaired algorithm/mode paths once, plus ORB ZED inertial+LC. '
        'This is the minimum branch-coverage target set used here, not proof that all dataset-specific paths behave identically. Defer blocked agricultural/GNSS targets until their prerequisites are resolved; do not launch this as a campaign. '
        'Passing the first three does not certify the other paths. Tests of failure/interruption can be combined with each integration target; no arbitrary extra N=3 diagnostic campaign is proposed.','',
        '| Diagnostic target | Execution status | Full-sequence historical seconds (not diagnostic estimate) |','|---|---|---:|']
    if focused:
        lines+=['','The following representatives cover the other algorithm/mode branches; a validated EuRoC path does not certify another dataset.','','| Diagnostic target | Execution status | Full-sequence historical seconds (not diagnostic estimate) |','|---|---|---:|']
    lines += [f"| `{d['cell']}` | {'ZED short check passed' if d['zed_short_execution_validated'] else 'focused campaign validated' if d['focused_execution_validated'] else 'pending first batch' if d['first_batch'] else 'deferred'} | {round(d['estimated_full_sequence_s'],1) if d['estimated_full_sequence_s'] else 'unknown'} |" for d in diagnostics]
    lines+=['',f'The timing subtotal is {sum(known)/3600:.1f} serialized hours for {len(known)} of the {len(estimates)} required/missing actions; {len(estimates)-len(known)} have no comparable complete same-cell timing. '
        'It excludes native-error samples, diagnostics, unresolved blocked cases and evaluation/capture overhead. No total-campaign runtime is justified.','',
        '## Reproduction and preservation','','Regenerate inventory, reconcile qualification, promote checked evaluations, then regenerate CSVs, TODO, reports and this handoff. '
        'Rosario evaluation uses the matched physical IMU-to-camera transform. The later ZED review uses the versioned nominal 3D position reference and recovered factory extrinsics; non-ZED numerical scores remain unchanged. Review decisions fail closed if pinned evidence changes. '
        'Run `build_future_manifest.py` after source/input/asset refresh; ordinary validation is read-only and is not readiness approval. '
        'The historical authorship mapping and all original provenance hashes remain intact. The obsolete temporary pause remains explicitly revoked.']
    preserved_write(REPO/'docs/acceptance-handoff-20261001.md','\n'.join(lines)+'\n')
    print(json.dumps(dict(categories=dict(counts),diagnostic_targets=len(diagnostics),first_batch=sum(d['first_batch'] for d in diagnostics))))


if __name__=='__main__':main()
