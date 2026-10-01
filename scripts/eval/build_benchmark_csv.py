#!/usr/bin/env python3
"""Build schema-3 CSVs from the authoritative attempt inventory.

All planned default repetitions remain visible, including failures and missing
attempts. GNSS variants remain separate. Historical/smoke artifacts are excluded
from headline CSVs and remain in the inventory. COMPLETE is not a selection gate.
No legacy coverage fallback, fabricated tracking count, or origin-alignment claim.
"""
from __future__ import annotations
import argparse
import csv
from functools import lru_cache
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile

REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'scripts/campaign'))
from run_future_manifest import verify_files
from _run_type import RUN_TYPES

COLUMNS = ['dataset', 'seq', 'environment_type', 'algo', 'run_type', 'use_imu', 'use_lc', 'run',
 'gnss_variant', 'run_status', 'eval_schema', 'input_fps', 'image_width', 'image_height',
 'sequence_duration_s', 'sequence_frames_total', 'coverage_gap_pct', 'frames_tracked', 'track_pct',
 'trajectory_duration_s', 'trajectory_time_coverage_pct', 'n_pairs_ate', 'ate_se3_rmse_m',
 'ate_se3_max_m', 'ate_sim3_rmse_m', 'ate_sim3_max_m', 'ate_origin_rmse_m', 'ate_origin_max_m',
 'scale_factor', 'scale_error_pct', 'rpe_trans_1m_rmse_m', 'rpe_trans_1m_se3_rmse_m',
 'rpe_rot_1m_rmse_deg', 'drift_10m_pct', 'drift_50m_pct', 'drift_100m_pct', 'path_length_gt_m',
 'path_length_est_m', 'ate_se3_rmse_pct_path', 'ate_sim3_rmse_pct_path', 'loop_closures',
 'tracking_losses', 'map_resets', 'init_success', 'measurement_mode', 'input_frames',
 'processed_frames', 'published_frames', 'output_poses', 'dropped_frames',
 'publisher_dropped_frames', 'processing_time_s', 'end_to_end_time_s', 'initialization_time_s',
 'steady_state_time_s', 'final_optimization_time_s', 'shutdown_time_s', 'processing_fps',
 'end_to_end_fps', 'trajectory_pose_rate', 'real_time_factor', 'deadline_misses', 'max_queue_depth',
 'duration_s', 'fps', 'processing_ms_per_frame', 'resource_scope', 'cpu_time_s', 'cpu_mean_pct',
 'cpu_peak_pct', 'ram_mean_mib', 'ram_peak_mib', 'vram_mean_mib', 'vram_peak_mib', 'gpu_mean_pct',
 'gpu_peak_pct', 'ate_row_rmse_m', 'ate_turn_rmse_m', 'n_segments_row', 'n_segments_turn',
 'segment_alignment', 'machine_cpu', 'machine_gpu', 'final_drift_m', 'gt_source', 'run_path',
 'evaluation_path', 'cohort', 'campaign_membership', 'attempt_exists', 'trajectory_saved',
 'execution_status', 'process_exit_code', 'scientific_status', 'scientific_blockers', 'paper_ready',
 'primary_alignment', 'primary_ate_rmse_m', 'position_metric_validity',
 'orientation_metrics_available', 'export_kind', 'camera_pose_coverage_pct',
 'reference_pairs_pct_of_input', 'reference_supported_pose_pct',
 'position_only_diagnostic_ate_se3_rmse_m', 'position_only_diagnostic_qualified',
 'displacement_magnitude_error_1m_se3_rmse_m', 'displacement_magnitude_error_1m_sim3_rmse_m',
 'window_protocol', 'evaluator_sha256', 'machine_id']


def get(document,*keys):
    value=document
    for key in keys:
        if not isinstance(value,dict):return None
        value=value.get(key)
    return value


def preserved_write(path,content,repo=REPO):
    """Preserve previous derived bytes independently, then replace atomically."""
    raw=content.encode() if isinstance(content,str) else content
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        old=path.read_bytes()
        if old==raw:return
        digest=hashlib.sha256(old).hexdigest()
        archive=repo/'results/.derived-history'/f'{path.name}.{digest}'
        archive.parent.mkdir(parents=True,exist_ok=True)
        try:
            with archive.open('xb') as stream:stream.write(old)
        except FileExistsError:pass
        if archive.read_bytes()!=old:raise RuntimeError('derived-output backup mismatch')
    fd,name=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)


@lru_cache(maxsize=32)
def sequence_meta(repo,dataset,sequence):
    base=Path(repo)/'datasets'/dataset/sequence;result={}
    times=base/'times.txt'
    if times.is_file():
        stamps=[int(s) for s in times.read_text().splitlines() if s.strip() and not s.startswith('#')]
        if len(stamps)>1:
            duration=(stamps[-1]-stamps[0])/1e9
            result.update(sequence_frames_total=len(stamps),sequence_duration_s=duration,input_fps=(len(stamps)-1)/duration)
    # The dimensions are observed from an input file, not inferred from an old cache.
    image_dir=base/'mav0/cam0/data'
    first=next(image_dir.glob('*.png'),None) or next(image_dir.glob('*.jpg'),None)
    if first:
        from PIL import Image
        with Image.open(first) as image:result.update(image_width=image.width,image_height=image.height)
    return result


def row_from_attempt(attempt,evaluation,cell,*,repo=REPO,membership='original_n3_campaign'):
    path=Path(attempt['path']);name=path.name.removeprefix('run');run,_,variant=name.partition('_')
    variant=variant or 'default';ev=evaluation;cov=ev.get('coverage',{});runtime=ev.get('runtime',{})
    if ev and ev.get('eval_schema')!=3:raise ValueError('only schema-3 evaluations may enter repaired CSVs')
    mode,ds,seq,algo=path.parts[1:5]
    mono=algo=='dpvo';alignment=ev.get('primary_alignment') or ('sim3' if mono else 'se3')
    status=ev.get('run_status') or ('missing' if not attempt['exists'] else
        'saved_not_evaluated' if attempt['trajectory_saved'] else
        'failed_without_trajectory' if attempt.get('process',{}).get('exit_code') not in (0,None) else 'incomplete')
    qualification=attempt.get('qualification',{})
    blockers=qualification.get('blockers',[])
    if cell and not cell.get('within_cell_config_consistent',True):blockers=blockers+['within_cell_configuration_mismatch']
    if cell and not cell.get('within_cell_cohort_consistent',True):
        blockers=blockers+['within_cell_source_binary_parameter_or_hardware_mismatch']
    machine=ev.get('machine',{});process=attempt.get('process',{})
    row=dict.fromkeys(COLUMNS)
    row.update(dataset=ds,seq=seq,algo=algo,run_type=mode,run=run,gnss_variant=variant,
        environment_type='indoor_reference' if ds=='euroc_mav' else 'agricultural',
        use_imu=mode in ('vio','vio-lc','gnss-vio'),use_lc=ev.get('use_lc'),
        run_status=status,eval_schema=ev.get('eval_schema'),run_path=attempt['path'],evaluation_path=attempt.get('evaluation_path'),
        cohort=attempt.get('cohort_fingerprint') or ('unverified:' + attempt['path'] if attempt['exists'] else 'not_executed'),campaign_membership=membership,
        attempt_exists=attempt['exists'],trajectory_saved=attempt['trajectory_saved'],
        execution_status=get(ev,'execution','status') or 'unknown',process_exit_code=process.get('exit_code'),
        scientific_status=qualification.get('status','not_evaluated'),scientific_blockers=json.dumps(blockers,separators=(',',':')),
        paper_ready=qualification.get('status')=='qualified',
        primary_alignment=alignment,primary_ate_rmse_m=get(ev,'ate' if alignment=='sim3' else 'ate_se3','rmse'),
        position_metric_validity=get(ev,'metric_validity','position'),
        orientation_metrics_available=bool(get(ev,'pose_frames','orientation_valid') and get(ev,'pose_frames','common_origin_verified')) if ev else None,
        export_kind=cov.get('export_kind'),coverage_gap_pct=cov.get('coverage_gap_pct'),
        camera_pose_coverage_pct=cov.get('camera_pose_coverage_pct'),reference_pairs_pct_of_input=cov.get('reference_pairs_pct_of_input'),
        reference_supported_pose_pct=cov.get('reference_supported_pose_pct'),
        trajectory_duration_s=cov.get('export_span_s'),trajectory_time_coverage_pct=cov.get('export_span_pct'),
        n_pairs_ate=ev.get('n_pairs_ate'),ate_se3_rmse_m=get(ev,'ate_se3','rmse'),ate_se3_max_m=get(ev,'ate_se3','max'),
        ate_sim3_rmse_m=get(ev,'ate','rmse'),ate_sim3_max_m=get(ev,'ate','max'),
        ate_origin_rmse_m=get(ev,'ate_origin','rmse'),ate_origin_max_m=get(ev,'ate_origin','max'),
        scale_factor=ev.get('scale_factor'),
        rpe_trans_1m_rmse_m=get(ev,'rpe_trans_1m','rmse'),rpe_trans_1m_se3_rmse_m=get(ev,'rpe_trans_1m_se3','rmse'),
        rpe_rot_1m_rmse_deg=get(ev,'rpe_rot_1m_deg','rmse'),
        displacement_magnitude_error_1m_se3_rmse_m=get(ev,'displacement_magnitude_error_1m','se3','rmse'),
        displacement_magnitude_error_1m_sim3_rmse_m=get(ev,'displacement_magnitude_error_1m','sim3','rmse'),
        window_protocol='custom overlapping reference-distance windows; not KITTI' if ev else None,
        position_only_diagnostic_ate_se3_rmse_m=get(ev,'position_only_diagnostic','ate_se3','rmse'),
        position_only_diagnostic_qualified=False if ev.get('position_only_diagnostic') else None,
        evaluator_sha256=get(ev,'evaluation_provenance','evaluator','sha256'),machine_id=attempt.get('machine_id'),
        gt_source=ev.get('gt_source'),final_drift_m=ev.get('final_drift_m'))
    row.update(sequence_meta(str(repo),ds,seq))
    if not mono and ev.get('scale_factor') is not None:row['scale_error_pct']=abs(ev['scale_factor']-1)*100
    for distance in (10,50,100):
        row[f'drift_{distance}m_pct']=get(ev,'window_drift',f'{distance}m','translation_se3_pct','rmse')
    for key in ('loop_closures','tracking_losses','map_resets','init_success'):row[key]=get(ev,'robustness',key)
    # Copy only explicitly recorded runtime fields. Output density never becomes
    # processed-image count, and legacy FPS never becomes processing throughput.
    for key in COLUMNS:
        if key in runtime:row[key]=runtime[key]
    row['measurement_mode']=runtime.get('measurement_mode') or runtime.get('mode')
    row['duration_s']=runtime.get('end_to_end_time_s',runtime.get('wall_s'))
    row['end_to_end_time_s']=row['duration_s']
    row['fps']=runtime.get('processing_fps')
    row['real_time_factor']=runtime.get('realtime_factor')
    if runtime.get('processing_time_s') is not None and runtime.get('processed_frames'):
        row['processing_ms_per_frame']=1000*runtime['processing_time_s']/runtime['processed_frames']
    for kind in ('row','turn'):
        row[f'ate_{kind}_rmse_m']=get(ev,'agri_segments',kind,'ate_rmse_mean')
        row[f'n_segments_{kind}']=get(ev,'agri_segments',kind,'n_segments')
        row['segment_alignment']=row['segment_alignment'] or get(ev,'agri_segments',kind,'alignment')
    if machine.get('collected_at')!='evaluation':
        row['machine_cpu']=machine.get('cpu')
        gpus=machine.get('gpus')
        row['machine_gpu']=gpus[0].get('name') if isinstance(gpus,list) and gpus else None
    return row


def load_inventory(path,repo=REPO):
    inventory=json.loads(Path(path).read_text());files={}
    for attempt in [a for c in inventory['cells'] for a in c['attempts']]+inventory['other_artifacts']:
        for item in attempt['files']:
            if item['path'] in files and files[item['path']]['sha256']!=item['sha256']:
                raise ValueError('conflicting inventory evidence: '+item['path'])
            files[item['path']]=item
    errors=verify_files(repo,list(files.values()))
    if errors:raise ValueError('inventory must be regenerated: '+'; '.join(errors[:5]))
    return inventory


def build_rows(inventory,repo=REPO):
    rows=[]
    for cell in inventory['cells']:
        for attempt in cell['attempts']:
            ev=json.loads((repo/attempt['evaluation_path']).read_text()) if attempt['evaluation_path'] else {}
            rows.append(row_from_attempt(attempt,ev,cell,repo=repo,
                membership='original_n3_campaign' if cell['original_campaign_member'] else 'gnss_default_future_n3'))
    for attempt in inventory['other_artifacts']:
        if attempt['category']!='gnss_variant':continue
        ev=json.loads((repo/attempt['evaluation_path']).read_text()) if attempt['evaluation_path'] else {}
        rows.append(row_from_attempt(attempt,ev,None,repo=repo,membership='legacy_gnss_variant'))
    return sorted(rows,key=lambda r:(r['run_type'],r['dataset'],r['seq'],r['algo'],r['gnss_variant'],int(r['run'])))


def csv_text(rows):
    stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=COLUMNS,lineterminator='\n')
    writer.writeheader();writer.writerows(rows);return stream.getvalue()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',nargs='?',choices=(*RUN_TYPES,'all'),default='all')
    ap.add_argument('--inventory',type=Path,default=REPO/'results/repair-20261001/inventory.json')
    ap.add_argument('--output-dir',type=Path,default=REPO)
    args=ap.parse_args();inventory=load_inventory(args.inventory);rows=build_rows(inventory)
    for mode in RUN_TYPES if args.mode=='all' else [args.mode]:
        selected=[r for r in rows if r['run_type']==mode]
        path=args.output_dir/f'benchmark-{mode}.csv';preserved_write(path,csv_text(selected))
        print(f'[csv] {mode}: {len(selected)} rows including missing/failed repetitions -> {path}')
    return 0


if __name__=='__main__':raise SystemExit(main())
