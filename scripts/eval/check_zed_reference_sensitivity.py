#!/usr/bin/env python3
"""Predeclared ZED reference sensitivities using the benchmark evaluator.

Only saved exports are read. No best-scoring reference or clock offset is chosen.
"""
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np
from scipy.spatial.transform import Rotation

from _saved_run import atomic_json, evaluate_saved_run, evaluator_identity
from _trajectory_evaluation import evaluate_arrays
from _pose_frames import file_evidence

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/data'))
from _zed_reference import camera_positions, horizontal_lever


def scenarios(ds):
    ref=ds/'references/gnss-position-v2-20261002';data=np.load(ref/'construction.npz')
    keep=data['primary_keep'];times=data['timestamp_ns'][keep].astype(float)/1e9
    antenna,baseline=data['antenna_enu'][keep],data['baseline_enu'][keep]
    primary=np.loadtxt(ref/'primary.tum')
    support=json.loads((ref/'primary-support.json').read_text())['valid_intervals']
    variants={'primary':(primary,support),
              'fixed_only':(np.loadtxt(ref/'fixed_only.tum'),json.loads((ref/'fixed_only-support.json').read_text())['valid_intervals']),
              'legacy_reference_same_estimator_frame':(np.loadtxt(ds/'gt_tum.txt'),None)}
    for height in (.5,1.5):
        a=primary.copy();a[:,1:4]=camera_positions(antenna,baseline,antenna_above_camera_m=height)
        variants[f'height_{height:g}m']=(a,support)
    for axis in ('roll','pitch'):
        for angle in (-10.,-5.,5.,10.):
            a=primary.copy();a[:,1:4]=camera_positions(antenna,baseline,**{axis+'_deg':angle})
            variants[f'{axis}_{angle:+g}deg']=(a,support)
    # Assumed roll=0; compensate the known lateral baseline while deriving pitch.
    direction=baseline/np.linalg.norm(baseline,axis=1)[:,None]
    pitch=np.arcsin(np.clip(-direction[:,2]*np.hypot(1.385,.037)/1.385,-1,1))
    yaw=np.arctan2(baseline[:,1],baseline[:,0])-np.arctan2(.037,1.385*np.cos(pitch))
    attitude=Rotation.from_euler('z',yaw)*Rotation.from_euler('y',pitch)
    a=primary.copy();a[:,1:4]=antenna+attitude.apply([*horizontal_lever(),-1.])
    variants['baseline_pitch_zero_roll_diagnostic']=(a,support)
    for dt in (-.5,-.1,.1,.5):
        a=primary.copy();a[:,0]-=dt
        variants[f'query_offset_{dt:+g}s']=(a,(np.array(support)-dt).tolist())
    details={}
    for key,(a,_) in variants.items():
        if len(a)==len(primary) and not key.startswith('query_offset'):
            delta=np.linalg.norm(a[:,1:4]-primary[:,1:4],axis=1)
            details[key]=dict(reference_displacement_max_m=float(delta.max()),reference_displacement_rms_m=float(np.sqrt(np.mean(delta**2))))
    details['baseline_pitch_zero_roll_diagnostic']['pitch_deg_quantiles']=np.quantile(np.rad2deg(pitch),[0,.01,.5,.99,1]).tolist()
    return variants,details


def main():
    started=time.monotonic();ds=ROOT/'datasets/zed2i/field1_110426_full_10fps_q90'
    out=ROOT/'results/zed-preparation-20261002'
    target=out/'sensitivity.json'
    if target.exists():raise FileExistsError('preserve previous sensitivity report before recomputation')
    times=np.loadtxt(ds/'times.txt')/1e9;refs,details=scenarios(ds)
    runs=sorted(p.parent for mode in ('vo','vo-lc','vio','vio-lc','gnss-vio')
                for p in (ROOT/'results'/mode/'zed2i'/ds.name).glob('*/run*/trajectory.txt'))
    records=[];identity=evaluator_identity()
    for index,run in enumerate(runs,1):
        record=dict(run=str(run.relative_to(ROOT/'results')),source=file_evidence(run/'trajectory.txt',ROOT),variants={})
        try:
            value,_=evaluate_saved_run(ROOT,run)
            atomic_json(out/'stage/evaluations'/run.relative_to(ROOT/'results')/'run_eval.json',value)
            estimate=np.loadtxt(run/'trajectory.txt',ndmin=2)
            for name,(ref,support) in refs.items():
                frames=dict(value['pose_frames']);frames.pop('reference_valid_intervals',None)
                if support is not None:frames['reference_valid_intervals']=support
                m,_=evaluate_arrays(ref,estimate,times,frames,monocular=value['algo'] in ('dpvo','droidslam'),
                                    sparse_export=value['algo']=='airslam',gnss=value['use_gnss'])
                record['variants'][name]=dict(ate_se3_m=m['ate_se3']['rmse'],ate_sim3_m=m['ate']['rmse'],
                    n_pairs=m['n_pairs_ate'],numerical_status=m['run_status'],scale_factor=m['scale_factor'])
            record['status']='evaluated'
        except (OSError,ValueError,KeyError,RuntimeError) as exc:
            record.update(status='error',error=f'{type(exc).__name__}: {exc}')
        if evaluator_identity()['sha256']!=identity['sha256']:raise RuntimeError('evaluator changed during sensitivity check')
        records.append(record)
        atomic_json(out/'sensitivity-progress.json',dict(expected=len(runs),processed=index,runs=records,
                    elapsed_s=time.monotonic()-started,evaluator=identity,reference_scenarios=details))
        print(f'{index}/{len(runs)} {record["run"]}: {record["status"]}',flush=True)
    atomic_json(target,dict(expected=len(runs),runs=records,elapsed_s=time.monotonic()-started,
        evaluator=identity,reference_scenarios=details,protocol=file_evidence(ROOT/'docs/zed-preparation-20261002.md',ROOT),
        selected_by_scores=False,clock_correction_applied_s=0.))
    return int(any(r['status']=='error' for r in records))


if __name__=='__main__':raise SystemExit(main())
