#!/usr/bin/env python3
"""Extract effective saved settings and check sensor/LC mode contracts.

Reads hash-verified snapshots, never today's configs in place of historical ones.
This bounded audit is not a complete scientific qualification or a tuning search.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import yaml

REPO=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'scripts/eval'))
from build_benchmark_csv import load_inventory, preserved_write


class SavedLoader(yaml.SafeLoader):
    def construct_mapping(self,node,deep=False):
        self.flatten_mapping(node)
        seen={}
        for key_node,value_node in node.value:
            key=self.construct_object(key_node,deep=deep)
            if key in seen:
                value=self.construct_object(value_node,deep=True)
                # This legacy alias is ignored by the inspected ORB source.
                # Preserve a warning for identical aliases; never choose between
                # conflicting duplicate settings or silently accept other keys.
                if key!='System.LoopClosing' or seen[key]!=value:
                    raise ValueError(f'duplicate YAML key: {key!r}')
                self.duplicate_warnings.append('identical_ignored_alias:'+key)
            else:seen[key]=self.construct_object(value_node,deep=True)
        return super().construct_mapping(node,deep=deep)

    def __init__(self,stream):
        super().__init__(stream)
        self.duplicate_warnings=[]


SavedLoader.add_constructor('tag:yaml.org,2002:opencv-matrix',
    lambda loader,node:loader.construct_mapping(node,deep=True))
SavedLoader.add_constructor('!include',
    lambda loader,node:{'source_include':loader.construct_scalar(node)})


def flatten(value,prefix=''):
    if not isinstance(value,dict):return {prefix:value}
    result={}
    for key,item in value.items():
        name=f'{prefix}.{key}' if prefix else str(key)
        result.update(flatten(item,name))
    return result


def parse_snapshot(path,warnings=None):
    text=Path(path).read_text()
    text='\n'.join(line for line in text.splitlines() if not line.startswith('%YAML'))
    loader=SavedLoader(text)
    try:
        value=loader.get_single_data()
        if warnings is not None:warnings.extend(loader.duplicate_warnings)
    finally:loader.dispose()
    if not isinstance(value,dict):raise ValueError('configuration root is not a mapping')
    return flatten(value)


def mode_checks(algorithm,mode,documents,parameters):
    imu=mode in ('vio','vio-lc','gnss-vio');lc=mode in ('vo-lc','vio-lc')
    estimator=documents.get('estimator_config',{})
    checks=[]
    def expect(name,observed,expected):
        checks.append(dict(name=name,observed=observed,expected=expected,
            status='unverified' if observed is None else 'pass' if observed==expected else 'mismatch'))
    if algorithm=='orbslam3':
        expect('effective_loopClosing',estimator.get('loopClosing'),int(lc))
        expect('recorded_use_imu',parameters.get('use_imu'),imu)
    elif algorithm in ('okvis2','okvis2x'):
        expect('imu_parameters.use',estimator.get('imu_parameters.use'),imu)
        if mode!='gnss-vio':
            expect('estimator_parameters.do_loop_closures',estimator.get('estimator_parameters.do_loop_closures'),lc)
        if not lc and mode!='gnss-vio':
            expect('odometry_final_ba_disabled',estimator.get('estimator_parameters.do_final_ba'),False)
    elif algorithm=='airslam':
        expect('camera.use_imu',documents.get('camera_config',{}).get('use_imu'),int(imu))
        if lc:expect('refinement_config_saved',bool(documents.get('map_refinement_config')),True)
    elif algorithm=='basalt':
        expect('recorded_use_imu',parameters.get('use_imu'),imu)
        expect('realtime_frame_drop_disabled',estimator.get('value0.config.vio_enforce_realtime'),False)
    elif algorithm=='ov2slam':
        expect('buse_loop_closer',estimator.get('buse_loop_closer'),int(lc))
        expect('force_realtime',estimator.get('force_realtime'),0)
        expect('stereo',estimator.get('stereo'),1)
    elif algorithm=='dpvo':
        expect('recorded_loop_closure',parameters.get('loop_closure'),lc)
        expect('stride',parameters.get('stride'),1)
        expect('skip',parameters.get('skip'),0)
    elif algorithm=='macvo':
        expect('mode',mode,'vo')
        expect('ground_truth_disabled',documents.get('effective_dataset_config',{}).get('args.gt_pose'),False)
    elif algorithm in ('openvins','voxel_svio'):
        expect('mode',mode,'vio')
    elif algorithm=='cuvslam':
        effective=documents.get('effective_config',{})
        expect('odometry.odometry_mode',effective.get('odometry.odometry_mode'),'Inertial' if imu else 'Multicamera')
        expect('slam_enabled','slam.sync_mode' in effective if effective else None,lc)
        expect('odometry.async_sba',effective.get('odometry.async_sba'),False)
    elif algorithm=='dsol':
        expect('mode',mode,'vo')
    elif algorithm=='svo_pro':
        effective=documents.get('effective_config',{})
        expect('use_imu',effective.get('use_imu'),imu)
        expect('use_ceres_backend',effective.get('use_ceres_backend'),imu)
        expect('runlc',effective.get('runlc'),lc)
        expect('ceres_max_iteration_time',effective.get('ceres_max_iteration_time'),-1.0)
    elif algorithm=='mast3r_fusion':
        expect('mode_uses_imu',imu,True)
        expect('recorded_loop_closure',parameters.get('loop_closure'),lc)
    return checks


def selected_parameters(algorithm,documents):
    result={}
    for role,fields in documents.items():
        if role=='estimator_config_source':continue
        for key,value in fields.items():
            include=False
            if algorithm=='orbslam3':
                include=key.startswith(('ORBextractor.','IMU.')) or key in ('loopClosing','System.LoopClosing','Camera.fps','Stereo.ThDepth','ThDepth')
            elif algorithm in ('okvis2','okvis2x'):
                include=key.startswith(('frontend_parameters.','estimator_parameters.','camera_parameters.online_calibration.'))
            elif algorithm=='airslam':
                include=key in ('use_imu','depth_lower_thr','depth_upper_thr','max_y_diff','distortion_type') or key.startswith(('plnet.','keyframe.','optimization.'))
            elif algorithm=='basalt':include=key.startswith('value0.config.')
            elif algorithm=='ov2slam':include=role=='estimator_config' and not key.startswith(('Camera.','body_T_'))
            elif algorithm=='openvins':
                include=role=='estimator_config' and not any(part in key for part in ('filepath','relative_config','verbosity'))
            elif algorithm=='voxel_svio':
                include=key.startswith(('state_parameter.','initializer_parameter.','odometry_parameter.','feature_parameter.','voxel_parameter.'))
            elif algorithm=='dpvo':include=role=='algorithm_config'
            elif algorithm=='macvo':include=role=='odometry_config' and not key.startswith(('Data.','Preprocess.'))
            elif algorithm=='cuvslam':include=role=='effective_config' and key.startswith(('odometry.','slam.'))
            elif algorithm in ('dsol','mast3r_fusion'):include=role=='effective_config'
            elif algorithm=='svo_pro':
                include=role=='effective_config' and key not in ('dataset_directory','calib_file','trace_dir')
            if include:result[f'{role}:{key}']=value
    return result


def audit(inventory,repo=REPO):
    records=[]
    attempts=[a for c in inventory['cells'] for a in c['attempts']]+inventory['other_artifacts']
    for attempt in attempts:
        _,mode,dataset,sequence,algorithm,name=Path(attempt['path']).parts
        documents={};evidence=[];errors=[];warnings=[]
        for entry in attempt['snapshots']:
            actual=entry.get('actual')
            if not entry.get('verified') or not actual:
                errors.append('snapshot_not_verified:'+entry['role']);continue
            path=repo/actual['path']
            if path.suffix.lower() not in ('.yaml','.yml','.json'):continue
            try:
                duplicates=[]
                documents[entry['role']]=parse_snapshot(path,duplicates);evidence.append(actual)
                warnings.extend(entry['role']+':'+item for item in duplicates)
            except (ValueError,yaml.YAMLError) as exc:
                errors.append(entry['role']+':'+str(exc))
        checks=mode_checks(algorithm,mode,documents,attempt['parameters']) if attempt['exists'] else []
        records.append(dict(path=attempt['path'],exists=attempt['exists'],mode=mode,dataset=dataset,
            sequence=sequence,algorithm=algorithm,run=name,evidence=evidence,parse_errors=errors,parse_warnings=warnings,
            selected_parameters=selected_parameters(algorithm,documents),recorded_parameters=attempt['parameters'],
            mode_checks=checks,scope='selected_parameter_and_mode_checks_only_not_scientific_qualification'))
    default_paths={a['path'] for c in inventory['cells'] for a in c['attempts']}
    groups={}
    for record in records:
        if record['path'] not in default_paths:continue
        for key,value in record['selected_parameters'].items():
            group=groups.setdefault((record['algorithm'],record['mode'],key),{})
            item=group.setdefault(json.dumps(value,sort_keys=True),dict(value=value,attempts=[],datasets=set()))
            item['attempts'].append(record['path']);item['datasets'].add(record['dataset'])
    variants=[]
    for (algorithm,mode,key),group in sorted(groups.items()):
        if len(group)<2:continue
        variants.append(dict(algorithm=algorithm,mode=mode,parameter=key,
            values=[dict(value=v['value'],attempts=v['attempts'],datasets=sorted(v['datasets'])) for v in group.values()],
            interpretation='saved_literal_difference_not_automatically_a_protocol_error'))
    return dict(schema=1,scope='all_default_slots_and_retained_other_artifacts',records=records,
        setting_variants=variants,
        summary=dict(records=len(records),with_saved_config=sum(bool(r['evidence']) for r in records),
            parsing_errors=sum(len(r['parse_errors']) for r in records),
            parsing_warnings=sum(len(r['parse_warnings']) for r in records),
            settings_with_multiple_recorded_values=len(variants),
            mode_checks=dict(Counter(c['status'] for r in records for c in r['mode_checks']))))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inventory',type=Path,default=REPO/'results/repair-20261001/inventory.json')
    ap.add_argument('--output',type=Path,default=REPO/'results/repair-20261001/saved-parameter-audit.json')
    args=ap.parse_args();result=audit(load_inventory(args.inventory))
    result['inventory_sha256']=hashlib.sha256(args.inventory.read_bytes()).hexdigest()
    preserved_write(args.output,json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result['summary'],indent=2))
    return 1 if result['summary']['parsing_errors'] or result['summary']['mode_checks'].get('mismatch') else 0


if __name__=='__main__':raise SystemExit(main())
