"""Confirmed historical protocol issues, derived from preserved attempt evidence.

This is not the complete qualification review. In particular, an empty issue
list does not certify a result. Never infer historical settings from current files.
"""
from pathlib import Path
import hashlib
import re

AIRSLAM_UNCORRECTED_SOURCE = '1b70ff63ea5f7c5654a4ec986abc59c838793208'


def scalar(text,key):
    found=re.findall(r'^'+re.escape(key)+r':\s*([0-9.eE+-]+)',text,re.M)
    return float(found[0]) if len(found)==1 else None


def historical_findings(repo,relative,meta):
    mode,ds,seq,algo,_=Path(relative).parts
    records=meta.get('provenance',{}).get('artifacts',[])
    role='camera_config' if algo=='airslam' else 'estimator_config'
    snapshots=[a for a in records if a.get('role')==role and a.get('snapshot')]
    if len(snapshots)!=1:return []
    path=Path(repo)/'results'/relative/snapshots[0]['snapshot']
    if not path.is_file():return []
    if hashlib.sha256(path.read_bytes()).hexdigest()!=snapshots[0].get('snapshot_sha256'):
        return []
    text=path.read_text()
    issues=[]
    if algo=='orbslam3' and ds=='zed2i' and mode in ('vo','vo-lc') and scalar(text,'Camera.fps')==15:
        issues.append(dict(code='camera_fps_changed_15_to_10',disposition='required_rerun',
            prerequisite='retain_fps15_attempts_and_validate_sequence_specific_10hz_config',
            evidence=['docs/repair-audit-20261001.md']))
    if algo=='orbslam3' and ds=='hortimulti' and mode=='vio-lc':
        matrix=re.search(r'^IMU\.T_b_c1:[\s\S]*?data:\s*\[([^\]]+)\]',text,re.M)
        values=[float(x) for x in matrix[1].replace(',',' ').split()] if matrix else []
        raw=[.0521232345,-.0073054379,.9986139389,.1219040939,
             -.9986040017,-.0089493528,.0520572461,.0366053924,
             .0085566474,-.9999332676,-.0077617087,-.0562970105,0.,0.,0.,1.]
        if len(values)==16 and all(abs(a-b)<1e-9 for a,b in zip(values,raw)):
            issues.append(dict(code='orb_horti_rectified_camera_imu_extrinsic',disposition='required_rerun',
                prerequisite='validate_rectified_horti_imu_extrinsic_and_run_new_vio_lc_cohort_preserving_raw_frame_attempts',
                evidence=['docs/saved-parameter-review-20261001.md','results/repair-20261001/orb-horti-rectification-validation.json']))
    source=next((s for s in meta.get('provenance',{}).get('sources',[]) if s.get('role')=='algorithm'),{})
    if (algo=='airslam' and mode in ('vio','vio-lc') and scalar(text,'use_imu')==1
            and scalar(text,'distortion_type') in (1,2) and source.get('commit')==AIRSLAM_UNCORRECTED_SOURCE
            and source.get('dirty') is False):
        issues.append(dict(code='airslam_rectified_camera_imu_extrinsic',disposition='required_rerun',
            prerequisite='apply_reviewed_rectification_patch_build_record_binary_hashes_and_validate_fusion_before_corrected_cohort',
            evidence=['docs/airslam-rectification-audit.md','scripts/patches/airslam-rectified-imu-extrinsic.patch']))
    return issues
