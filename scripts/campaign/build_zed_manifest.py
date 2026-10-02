#!/usr/bin/env python3
"""Prepare a coherent ZED N=3 plan, preserving every historical observation.

This is an alternative selection to the all-mode logical-slot manifest, not an
additional campaign to execute on top of it. No estimator is launched.
"""
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

from build_future_manifest import build, digest
from run_future_manifest import validate

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO/'scripts/eval'))


def render_report(result):
    lines=['# ZED remaining N=3 campaign — 2026-10-02', '',
        'Prepared only; no production execution is authorized. This replaces the overlapping ZED selection in the all-mode manifest. Do not execute both plans.', '',
        'Retain nine complete historical N=3 cells (27 observations). Prepare 48 new attempts: **17 setup replacements, 25 missing slots and six cohort-completion attempts**. Historical failures, partial exports and separately qualified observations remain preserved.', '',
        '**Readiness:** 45 new attempts have passed configuration review and bounded native-path checks. The three Voxel attempts remain blocked because successful initialization/export was not verified. First authorized full repetitions are production gates; a 60-second check does not certify full-sequence stability.', '',
        '| Mode | Algorithm | New physical IDs | Logical slot reasons (r1 / r2 / r3) | Bounded readiness | Cost proxy per attempt |',
        '|---|---|---|---|---|---:|']
    for key in dict.fromkeys(a['cell'] for a in result['actions']):
        rows=[a for a in result['actions'] if a['cell']==key]
        new=[a for a in rows if a['command']]
        if not new:continue
        mode,_,_,algo=key.split('/')
        ids=', '.join(Path(a['planned_output']).name for a in new)
        estimate=new[0]['planning_runtime_proxy']['estimate_s']
        cost=f'{estimate/3600:.2f} h' if estimate is not None else 'unknown'
        lines.append(f"| {mode} | {algo} | {ids} | {' / '.join(a['category'] for a in rows)} | {'passed short check' if all(a['readiness']['verified_ready_to_run'] for a in new) else 'blocked: initialization/export'} | {cost} |")
    summary=result['summary']
    lines+=['', f"The indicative serialized cost subtotal is **{summary['planning_proxy_subtotal_s']/3600:.1f} hours for 39 attempts**; nine have no defensible complete historical proxy (six ORB inertial attempts and three OKVIS2-X VO-LC attempts). This includes Voxel's three blocked attempts. It is not a full-campaign runtime estimate. Paced ORB/OpenVINS/Voxel inputs alone take approximately 77.2 minutes per complete attempt; optimization, startup, capture and evaluation add time.", '',
        'These are historical wrapper wall-cost proxies, including configurations/builds that now require replacement and the old Voxel shutdown failure. They do not qualify those results or establish processing throughput. New calibration, loop closures, final optimization and host contention may change costs; no confidence interval or linear extrapolation from short checks is claimed. Serialize runs on shared GPU/containers.', '',
        'The six cohort-completion attempts comprise two OKVIS2 VO-LC, one OKVIS2-X VO-LC and three AirSLAM VO-LC slots. They create consistent current cohorts; they are not six additional proven configuration defects or retries selected for success. OKVIS2 run2 remains interrupted; OKVIS2-X run1 remains exit 141 with only a recovered causal prefix; AirSLAM retains its individually qualified N=1 and N=2 historical cohorts.', '',
        '## Retained complete cohorts', '', '| Cell | Retained physical attempts |', '|---|---|']
    for key in dict.fromkeys(a['cell'] for a in result['actions']):
        rows=[a for a in result['actions'] if a['cell']==key]
        if all(a['category']=='reusable' for a in rows):
            lines.append(f"| `{key}` | {', '.join(Path(a['prior_attempt']).name for a in rows)} |")
    lines+=['', '## Executable manifest and verification', '',
        'The full paths, commands, prior evidence, runtime samples and prerequisites are in `results/zed-preparation-20261002/campaign/manifest.json`. Each new attempt uses `run_repetitions.py` with one explicit physical ID, logical repetition and cohort. It preserves prior attempts, evaluates saved output immediately and refuses unsafe overwrite/resumption.', '',
        'Read-only verification (no estimator execution):', '', '```bash',
        '/data/imoroz/conda/envs/macvo/bin/python scripts/campaign/run_future_manifest.py results/zed-preparation-20261002/campaign/manifest.json',
        '```', '',
        'After source/config/build changes, refresh reviewed execution assets and regenerate both manifests; do not hand-edit hashes or widen readiness flags. Use `--action` to select an exact action and `--require-ready --check-inputs --check-implementations` for its strict read-only preflight from a clean execution environment. Voxel must fail readiness preflight until its export prerequisite is independently resolved. No `--run` command is authorized by this preparation.', '',
        'The broader all-five-mode audit and existing algorithm exclusions remain intact. Rosario, HortiMulti and GNSS blockers are unchanged; the non-ZED ORB native build still needs separate ABI/shutdown validation. See [preparation and limitations](zed-preparation-20261002.md) and [validation/preservation](zed-validation-20261002.md).']
    return '\n'.join(lines)+'\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--audit-status', choices=('in_progress', 'repair_audit_complete'), default='in_progress')
    args = ap.parse_args()
    out = REPO/'results/zed-preparation-20261002/campaign'
    out.mkdir(parents=True, exist_ok=True)
    source = REPO/'results/repair-20261001/inventory.json'
    inv = json.loads(source.read_text())
    inv['parent_inventory'] = dict(path=str(source.relative_to(REPO)), sha256=digest(source))
    inv['cells'] = [c for c in inv['cells'] if c['dataset']=='zed2i']
    inv['other_artifacts'] = [a for a in inv['other_artifacts'] if '/zed2i/' in a['path']]
    inv['scope'] = 'ZED subset; parent aggregate counts are intentionally omitted'
    inv.pop('counts', None)
    path = out/'inventory.json'
    path.write_text(json.dumps(inv, indent=2)+'\n')
    review_path = REPO/'docs/campaigns/zed-readiness-review-20261002.json'
    review = json.loads(review_path.read_text())
    decisions = deepcopy(review)
    for c in inv['cells']:
        if c['run_type']=='vo-lc' and c['algorithm'] in ('okvis2','okvis2x','airslam'):
            decisions['cells'][c['key']]['fresh_cohort'] = True
    result = build(REPO, inv, path, decisions)
    result.update(campaign_id='zed-coherent-n3-20261002', audit_status=args.audit_status,
        selection_policy='Retain nine verified N=3 cells; predeclare three fresh attempts in each remaining cell. Preserve all old outcomes; no success-conditioned retries.',
        replaces_selection_in='results/repair-20261001/future-n3-manifest.json',
        do_not_execute_both_plans=True)
    result['target']['note'] = '25 ZED cells; nine complete historical cohorts and sixteen new N=3 cohorts'
    for a in result['actions']:
        a['cohort'] = 'zed-current-n3-'+a['cohort'].removeprefix('repair-n3-')
        if a['command']:
            a['command'][-1] = a['cohort']
            a['planning_runtime_proxy'] = review['cells'][a['cell']]['planning_runtime_proxy']
            # Historical-cost proxies are deliberately distinct from the strict
            # comparable, scientifically-qualified runtime_estimate field.
    cats = Counter(a['category'] for a in result['actions'])
    if cats != dict(reusable=27, required_rerun=17, missing=25, cohort_completion=6):
        raise ValueError('ZED selection changed; review the cohort policy before regenerating: '+str(cats))
    result['summary']['categories'] = dict(cats)
    estimates = [a['planning_runtime_proxy']['estimate_s'] for a in result['actions'] if a['command']]
    result['summary']['planning_proxy_subtotal_s'] = sum(v for v in estimates if v is not None)
    result['summary']['planning_proxy_unknown_actions'] = sum(v is None for v in estimates)
    result['summary']['planning_proxy_scope'] = 'Indicative historical wall costs only; changed setup/build may change cost; no full-campaign total or real-time claim.'
    errors = validate(REPO, result)
    if errors:
        raise ValueError('; '.join(errors[:10]))
    from build_benchmark_csv import preserved_write
    preserved_write(out/'manifest.json', json.dumps(result, indent=2)+'\n')
    preserved_write(REPO/'docs/zed-campaign-20261002.md', render_report(result))
    print(json.dumps(result['summary'], indent=2))


if __name__=='__main__':
    main()
