"""Confirmed historical protocol issues, derived from preserved attempt evidence.

This is not the complete qualification review. In particular, an empty issue
list does not certify a result. Never infer historical settings from current files.
"""
from pathlib import Path
import hashlib
import json
import re

AIRSLAM_UNCORRECTED_SOURCE = '1b70ff63ea5f7c5654a4ec986abc59c838793208'

# Individually reviewed saved profiles, not hashes of today's configuration.
# Both raw bag IMU samples and the published calibration contradict colocation.
ROSARIO_IDENTITY_PROFILES = {
    'basalt': ('camera_calibration', '6ce7c0d5197e604f07e3866fe1845ef46607f0e5b74baf974e587ecc0c2e6d2d'),
    'openvins': ('camera_imu_calibration', '408a887ef92567582dc9d8f189093bd816168127f57efed8d63c44481f1a2262'),
    'voxel_svio': ('estimator_config', '4f9a27d350b437bf3e3c5636b4278e39f736e387751c14d0d184b2b0e6d1df0c'),
}


def verified_snapshot(repo, relative, records, role):
    matches = [a for a in records if a.get('role') == role and a.get('snapshot')]
    if len(matches) != 1:
        return None
    item = matches[0]
    path = Path(repo) / 'results' / relative / item['snapshot']
    if not path.is_file():
        return None
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return (path, digest) if digest == item.get('snapshot_sha256') else None


def scalar(text,key):
    found=re.findall(r'^'+re.escape(key)+r':\s*([0-9.eE+-]+)',text,re.M)
    return float(found[0]) if len(found)==1 else None


def native_gnss_findings(repo, relative):
    """Actual loaded antenna values can establish a defect without a config copy."""
    review = Path(repo) / 'docs/campaigns/gnss-lever-findings-20261001.json'
    if not relative.startswith('gnss-vio/') or not review.is_file():
        return []
    record = json.loads(review.read_text()).get('attempts', {}).get(relative)
    if not record:
        return []
    log = Path(repo) / record['log']['path']
    if not log.is_file() or hashlib.sha256(log.read_bytes()).hexdigest() != record['log']['sha256']:
        return []
    return [{key: record[key] for key in ('code', 'disposition', 'prerequisite', 'evidence')}]


USER_RERUN_DECISIONS = ('docs/campaigns/user-rerun-decisions-20261003.json',
                        'docs/campaigns/user-rerun-decisions-20261005.json')


def user_rerun_decisions(repo, relative, meta):
    """Replacements the user decided: ORB-SLAM3 libraries outside ZED, OpenVINS EuRoC VIO
    (2026-10-03); one HortiMulti IMU profile and camera-clock input, OV2SLAM HortiMulti values,
    the OpenVINS frame throttle (2026-10-05).

    A record applies only to its own attempt path with the binaries saved at the time, so
    replacement attempts (new physical run IDs) never inherit it. Later decisions live in a
    separate file, so the bytes earlier reviews pin stay unchanged; an attempt may carry one
    'decision' or a list of 'decisions'.
    """
    findings = []
    for name in USER_RERUN_DECISIONS:
        review = Path(repo) / name
        if not review.is_file():
            continue
        record = json.loads(review.read_text())
        pinned = record.get('attempts', {}).get(relative)
        if not pinned or meta.get('provenance', {}).get('binaries') != pinned['binaries']:
            continue
        for key in pinned.get('decisions') or [pinned['decision']]:
            decision = record['decisions'][key]
            findings.append({k: decision[k] for k in ('code', 'disposition', 'prerequisite', 'evidence')})
    return findings


def historical_findings(repo,relative,meta):
    mode,ds,seq,algo,_=Path(relative).parts
    issues = native_gnss_findings(repo, relative)
    issues += user_rerun_decisions(repo, relative, meta)
    records=meta.get('provenance',{}).get('artifacts',[])
    zed_review=Path(repo)/'docs/campaigns/zed-calibration-findings-20261002.json'
    if ds=='zed2i' and mode in ('vio','vio-lc') and zed_review.is_file():
        reviewed=json.loads(zed_review.read_text()).get('attempts',{}).get(relative)
        if reviewed:
            calibration=verified_snapshot(repo,relative,records,reviewed['role'])
            source=next((s for s in meta.get('provenance',{}).get('sources',[]) if s.get('role')=='algorithm'),{})
            if calibration and calibration[1]==reviewed['config_sha256'] and source==reviewed['algorithm_source']:
                issues.append({key:reviewed[key] for key in ('code','disposition','prerequisite','evidence')})
    role='camera_config' if algo=='airslam' else 'estimator_config'
    snapshots=[a for a in records if a.get('role')==role and a.get('snapshot')]
    if len(snapshots)!=1:return issues
    path=Path(repo)/'results'/relative/snapshots[0]['snapshot']
    if not path.is_file():return issues
    if hashlib.sha256(path.read_bytes()).hexdigest()!=snapshots[0].get('snapshot_sha256'):
        return issues
    text=path.read_text()
    if ds == 'rosariov2' and mode == 'vio' and algo in ROSARIO_IDENTITY_PROFILES:
        calibration_role, reviewed_hash = ROSARIO_IDENTITY_PROFILES[algo]
        calibration = verified_snapshot(repo, relative, records, calibration_role)
        # OpenVINS can estimate spatial extrinsics, but these reviewed attempts
        # explicitly disabled it. Estimating time offset cannot repair geometry.
        fixed = algo != 'openvins' or re.search(r'^calib_cam_extrinsics:\s*false\b', text, re.M)
        if calibration and calibration[1] == reviewed_hash and fixed:
            issues.append(dict(code='rosario_identity_camera_imu_extrinsic', disposition='required_rerun',
                prerequisite='use_matched_rosario_camera_imu_calibration_and_consistent_image_projection_before_new_inertial_attempt',
                evidence=['docs/reference-review-20261001.md', 'docs/campaigns/reference-sources-20261001.json']))
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
    # Later reviewed records for attempts the lists above missed (AirSLAM Rosario
    # identity extrinsic, Voxel HortiMulti initializer offset, Basalt HortiMulti noise).
    later = Path(repo) / 'docs/campaigns/rerun-findings-20261003.json'
    if later.is_file():
        reviewed = json.loads(later.read_text()).get('attempts', {}).get(relative)
        if reviewed:
            calibration = verified_snapshot(repo, relative, records, reviewed['role'])
            if (calibration and calibration[1] == reviewed['config_sha256']
                    and source == reviewed['algorithm_source']):
                issues.append({key: reviewed[key] for key in
                               ('code', 'disposition', 'prerequisite', 'evidence')})
    time_review = Path(repo) / 'docs/campaigns/horti-time-offset-findings-20261001.json'
    if ds == 'hortimulti' and time_review.is_file():
        reviewed = json.loads(time_review.read_text()).get('attempts', {}).get(relative)
        if reviewed:
            calibration = verified_snapshot(repo, relative, records, reviewed['role'])
            if (calibration and calibration[1] == reviewed['config_sha256']
                    and source == reviewed['algorithm_source']):
                issues.append({key: reviewed[key] for key in
                               ('code', 'disposition', 'prerequisite', 'evidence')})
    return issues
