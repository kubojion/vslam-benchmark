#!/usr/bin/env python3
"""Freeze the second development experiment from the completed pilot."""
import copy
import json
from pathlib import Path

from prepare_noise_pilot import PAIRS, sha, values

ROOT = Path(__file__).resolve().parents[2]
PREVIOUS = Path('/data/imoroz/IMU-NOISE-ISSUE2/noise-search-20261009')
ART = Path('/data/imoroz/IMU-NOISE-ISSUE2/noise-reliable-20261009')


def main():
    if ROOT.name != 'vslam-noise-reliable-20261009':
        raise RuntimeError('wrong worktree')
    if json.loads((PREVIOUS/'status.json').read_text()).get('event') != 'stage_finished':
        raise RuntimeError('first pilot must be complete')
    old = json.loads((PREVIOUS/'protocol.json').read_text())
    studies = copy.deepcopy(old['studies'])
    for spec in studies:
        prior = PREVIOUS/'studies'/spec['id']/'short-selection.json'
        selected = json.loads(prior.read_text())
        spec['pilot_candidates'] = [dict(label=x['label'], params=x['params']) for x in selected['top_two']]
        spec['pilot_selection_source'] = dict(path=str(prior), sha256=sha(prior))
        spec['full_sequences'] = PAIRS[spec['dataset']]
    config = 'configs/airslam/rosariov2_camera_vio.yaml'
    legacy_meta = Path('/data/imoroz/vslam-benchmark/results/vio/rosariov2/sequence1/airslam/run10001/run_meta.json')
    meta = json.loads(legacy_meta.read_text())
    artifact = next(a for a in meta['provenance']['artifacts'] if a['role'] == 'camera_config')
    historical = legacy_meta.parent/artifact['snapshot']
    c, legacy = values(ROOT/config, 'airslam'), values(historical, 'airslam')
    studies.append(dict(id='airslam_rosariov2', algorithm='airslam', dataset='rosariov2',
        target_sequence='sequence1', clips=['sequence1_noise180','sequence5_noise180'],
        full_sequences=PAIRS['rosariov2'], config=config, rule_c=c, legacy=legacy,
        legacy_label='historical_Rosario_noise_profile', legacy_source=str(historical),
        legacy_sha256=sha(historical), supports_lc=True, pilot_candidates=[],
        bounds={k:[min(c[k],legacy[k])/10,max(100*c[k],3*legacy[k])] for k in c}))
    for spec in studies:
        if values(ROOT/spec['config'],spec['algorithm']) != spec['rule_c']:
            raise RuntimeError('baseline changed: '+spec['id'])
    protocol = dict(schema=2, experiment='noise-reliable-20261009', development_only=True,
        previous_pilot=dict(path=str(PREVIOUS),protocol_sha256=sha(PREVIOUS/'protocol.json')),
        screen_seeds=[202610091,202610092], screen_candidates_per_seed=16,
        screen_startup_trials=8, full_seed=202610093, full_candidates=12, full_seed_candidates=6,
        finalists=2, repetitions=3, max_wall_hours=48,
        studies=studies, clips=old['clips'], worktree=str(ROOT), main_root=old['main_root'],
        sampler='Optuna 4.5.0 multivariate TPE; four positive standard deviations in log space',
        short_selection='Independent seeded explorations, sharing freshly measured identical control observations. Full seeds include controls, pilot finalists, and each screen seed winner; fill to six by short score.',
        full_search='Each proposal runs both full development recordings. Six seeded proposals then six TPE proposals informed by full-recording scores. Short and full objectives are never mixed in one Optuna study.',
        repeated_selection='Top two full candidates plus both controls, deduplicated by exact parameter vector, receive N=3 on both full sequences. The selected candidate minimizes the same declared score over these equal-sized repeat cohorts.',
        score='10 * failed_observation_count + 0.5 * mean(residual) + 0.5 * max(residual); residual = RMSE/(reference_path_length+RMSE) + unsupported_export_fraction. Existing numerical and 90% export-support gates retained. Lower is better.',
        lc='After full-VIO selection is frozen: N=1 VIO-LC for selected and Rule C on the original target sequence, deduplicated. LC does not feed VIO search. These are diagnostics, not N=3 LC benchmark results.',
        budget='Measured wall deadline fixed on first execute. Do not start an attempt without its declared maximum time plus 120s cleanup reserve remaining. Budget truncation is recorded; unrun candidates are not failures.',
        bounds='Same per-component rule as pilot: [min(C,historical)/10, max(100*C,3*historical)]. Report boundary proximity; do not change bounds after starting.',
        limitations=['All recordings have already been inspected and are development data.',
            'This is not independent final testing or a new physical IMU calibration.',
            'Two screen seeds probe proposal sensitivity, not two independent full optimization replications.',
            'Prior pilot candidate parameters inform full seeds; previous pilot scores are not reused.',
            'One configuration per algorithm and dataset; no per-sequence parameter selection.',
            'Selected candidate may still fail; selection is never proof of reliable deployment.',
            'Retain existing reference-frame and sparse-export qualifications.',
            'Equal proposal counts, not equal CPU time; algorithm costs differ.'])
    target = ROOT/'configs/experiments/noise-reliable-20261009.json'
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(protocol,indent=2)+'\n')
    ART.mkdir(exist_ok=True)
    (ART/'preparation.json').write_text(json.dumps(dict(protocol=str(target),sha256=sha(target),
        previous_finished=json.loads((PREVIOUS/'status.json').read_text())),indent=2)+'\n')
    print(target)


if __name__ == '__main__':
    main()
