#!/usr/bin/env python3
"""Prepare, but do not execute, bounded ZED integration checks.

The fixed first 60 seconds are selected before looking at estimator outcomes.
Original data are unchanged; relative links remain visible inside Docker mounts.
"""
import csv
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SEQUENCE='field1_110426_full_10fps_q90'
DIAGNOSTIC='field1_diag60_20261002'


def prepare():
    source=ROOT/'datasets/zed2i'/SEQUENCE;target=source.parent/DIAGNOSTIC
    out=ROOT/'results/zed-preparation-20261002'
    if target.exists():raise FileExistsError('preserve prior diagnostic input: '+str(target))
    stamps=[int(s) for s in (source/'times.txt').read_text().splitlines() if s.strip()]
    cutoff=stamps[0]+60_000_000_000;selected=[t for t in stamps if t<=cutoff]
    target.mkdir();(target/'times.txt').write_text(''.join(f'{t}\n' for t in selected))
    for camera in ('cam0','cam1'):
        sensor=target/'mav0'/camera;(sensor/'data').mkdir(parents=True)
        with (source/'mav0'/camera/'data.csv').open() as f:rows=list(csv.reader(f))
        chosen=[row for row in rows if row and not row[0].startswith('#') and int(row[0]) in set(selected)]
        if len(chosen)!=len(selected):raise ValueError('camera manifest differs')
        with (sensor/'data.csv').open('w') as f:
            f.write('#timestamp [ns],filename\n');csv.writer(f).writerows(chosen)
        for _,name in chosen:
            p=sensor/'data'/name
            p.symlink_to(os.path.relpath(source/'mav0'/camera/'data'/name,p.parent))
        (target/camera).symlink_to(f'mav0/{camera}/data')
    imu=target/'mav0/imu0';imu.mkdir()
    with (source/'mav0/imu0/data.csv').open() as f:rows=list(csv.reader(f))
    # Preserve any leading IMU samples and one sample after the final camera.
    data=[row for row in rows if row and not row[0].startswith('#')]
    end=next(i for i,row in enumerate(data) if int(row[0])>selected[-1])+1
    with (imu/'data.csv').open('w') as f:f.write(','.join(rows[0])+'\n');csv.writer(f).writerows(data[:end])
    # Reference is diagnostic only; never included in production N=3 selection.
    with (source/'gt_tum.txt').open() as f:
        gt=[line for line in f if not line.startswith('#') and float(line.split()[0])<=cutoff/1e9]
    (target/'gt_tum.txt').write_text(''.join(gt))
    cfgdir=out/'diagnostic-configs';cfgdir.mkdir(exist_ok=True)
    modes={'vo':['orbslam3'],'vo-lc':['orbslam3'],
           'vio':['orbslam3','basalt','okvis2','okvis2x','airslam','openvins','voxel_svio'],
           'vio-lc':['orbslam3','okvis2','okvis2x','airslam']}
    actions=[]
    for mode,algorithms in modes.items():
        for algorithm in algorithms:
            env=dict(PATH='/data/imoroz/conda/envs/macvo/bin:'+os.environ['PATH'],DISPLAY='')
            if algorithm=='orbslam3':
                cfg=ROOT/'configs/orbslam3'/('zed2i_field1_110426_full_10fps_q90_stereo_inertial.yaml' if mode.startswith('vio') else 'zed2i_full_10fps_q90.yaml')
                env['ORBSLAM3_CONFIG']=str(cfg)
            elif algorithm in ('okvis2','okvis2x'):
                cfg=ROOT/f'configs/{algorithm}/zed2i_{SEQUENCE}_{mode.replace("-","_")}.yaml'
                if algorithm=='okvis2' and mode=='vio-lc':
                    parent=ROOT/f'configs/okvis2/zed2i_{SEQUENCE}_vio.yaml'
                    cfg=cfgdir/'okvis2_vio_lc.yaml';text=parent.read_text()
                    if text.count('do_loop_closures: false')!=1:raise ValueError('LC config key ambiguous')
                    cfg.write_text(text.replace('do_loop_closures: false','do_loop_closures: true'))
                env[algorithm.upper()+'_CONFIG']=str(cfg)
            if algorithm=='airslam':env.update(AIRSLAM_STAGE_TIMEOUT_S='240',AIRSLAM_STARTUP_TIMEOUT_S='90')
            actions.append(dict(algorithm=algorithm,mode=mode,physical_run_id=1,timeout_s=420,
                command=['bash',str(ROOT/f'scripts/run/run_{algorithm}.sh'),'zed2i',DIAGNOSTIC,'1',mode],env=env,
                result_directory=f'results/{mode}/zed2i/{DIAGNOSTIC}/{algorithm}/run1'))
    recipe=dict(schema=1,purpose='first 60 seconds; integration only; no production repetitions',
        source_sequence=SEQUENCE,diagnostic_sequence=DIAGNOSTIC,camera_frames=len(selected),
        first_camera_ns=selected[0],last_camera_ns=selected[-1],imu_samples=end,
        forbidden='No retries to obtain successful outcomes; preserve every failed check; no full sequence execution.',
        actions=actions)
    (out/'short-check-plan.json').write_text(json.dumps(recipe,indent=2)+'\n')
    print(json.dumps({k:v for k,v in recipe.items() if k!='actions'},indent=2));print('actions',len(actions))


if __name__=='__main__':prepare()
