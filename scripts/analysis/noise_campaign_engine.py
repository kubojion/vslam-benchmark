"""Attempt execution for the expanded, isolated noise-development campaign.

No campaign starts by importing this module. A coordinator must first configure
it with a frozen protocol and an exclusive machine lease. Final N=1 attempts use
separate identities from development repeats; they are still development-set
measurements when they use the same recordings.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import noise_adapters as adapters
import noise_delivery
import noise_voxel_delivery
import noise_cleanup
import noise_execution_policy as execution_policy
import noise_pilot as base

ROOT = Path(__file__).resolve().parents[2]
ART = None
CAMPAIGN = None
PROTOCOL = None
CONFIG_ENVIRONMENT = (
    'ORBSLAM3_CONFIG', 'OKVIS2_CONFIG', 'OKVIS2X_CONFIG', 'NOISE_PILOT_CONFIG',
    'BASALT_CALIBRATION', 'BASALT_CONFIG', 'OPENVINS_CONFIG_DIR',
    'CUVSLAM_SENSOR', 'CUVSLAM_CONFIG', 'SVO_PRO_CONFIG', 'MAST3R_FUSION_CONFIG',
    'EXPERIMENT_IMU_NOISE', 'ROSARIO_VIO_PROFILE', 'MAST3R_FUSION_SEED',
    'OPENVINS_EXPERIMENT_IMAGE', 'OPENVINS_RATE',
    'OPENVINS_IMU_RELIABILITY',
    'OPENVINS_END_OF_STREAM_DRAIN',
    'OPENVINS_FLOW_CONTROL',
    'OPENVINS_TRANSPORT_PROFILE',
    'OPENVINS_MEMORY_LIMIT', 'OPENVINS_MEMORY_SWAP_LIMIT',
    'BASALT_EXPERIMENT_BIN', 'BASALT_EXPERIMENT_LIBDIR',
    'SVO_PRO_IMU_FILE', 'SVO_PRO_IMAGE', 'SVO_PRO_TIME_LIMIT_S',
    'SVO_PRO_MEMORY_LIMIT', 'SVO_PRO_MEMORY_SWAP_LIMIT',
    'VSLAM_EXPECTED_INPUT_SHA256', 'VSLAM_EXPECTED_SOURCE_SHA256',
    'VSLAM_EXPECTED_RUNTIME_SHA256',
)


def configure(artifact_directory, protocol, slot):
    global ART, CAMPAIGN, PROTOCOL
    if ROOT.resolve() == base.MAIN.resolve() or ROOT.name != 'vslam-noise-reliable-20261009':
        raise RuntimeError('Expanded search is restricted to the isolated experimental worktree')
    ART = Path(artifact_directory).resolve()
    if ART == base.MAIN.resolve() or base.MAIN.resolve() in ART.parents:
        raise RuntimeError('Campaign artifacts must be outside the production worktree')
    PROTOCOL = protocol
    CAMPAIGN = protocol['campaign_id']
    base.ART = ART
    base.ROOT = ROOT
    base.machine_slot = slot


def identities(study, label, sequence, mode, repetition, phase):
    if not CAMPAIGN:
        raise RuntimeError('Campaign not configured')
    key = '__'.join((phase, study, label, sequence, mode, 'rep' + str(repetition)))
    revision = execution_policy.reviewed_attempt_revision(PROTOCOL or {}, key)
    physical_key = CAMPAIGN + ':' + key
    if revision is not None:
        physical_key += ':revision=' + revision['revision']
    run_id = 2_000_000_000 + int(hashlib.sha256(physical_key.encode()).hexdigest()[:10], 16)
    # Common random numbers across noise candidates where the native algorithm
    # exposes a seed. NumPy's legacy seed interface requires an unsigned 32-bit value.
    seed_key = ':'.join((CAMPAIGN, study, sequence, phase, str(repetition)))
    seed = int(hashlib.sha256(seed_key.encode()).hexdigest()[:8], 16)
    return key, run_id, seed


def verify_frozen():
    if ART is None or PROTOCOL is None:
        raise RuntimeError('Campaign not configured')
    manifest = json.loads((ART / 'execution-identity.json').read_text())
    if manifest.get('controller_environment') != execution_policy.controller_environment():
        raise RuntimeError('Python or optimizer environment differs from the frozen campaign')
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if manifest.get('boot_id') != boot:
        raise RuntimeError('Host restarted since activation; explicit incident review is required')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if head != manifest['worktree_head']:
        raise RuntimeError('Experimental worktree revision changed; stop and review before resuming')
    for item in manifest['files']:
        if base.sha(ROOT / item['path']) != item['sha256']:
            raise RuntimeError('Frozen execution asset changed: ' + item['path'])
    if base.sha(ART / 'protocol.json') != manifest['protocol_sha256']:
        raise RuntimeError('Frozen protocol changed')
    base.verify_main()


def score(evaluation, returncode, algorithm, mode, distance):
    sparse = algorithm == 'airslam' or (algorithm == 'mast3r_fusion' and mode == 'vio-lc')
    result = base.score(evaluation, returncode, 'airslam' if sparse else algorithm, distance)
    result['export_policy'] = 'keyframe_span' if sparse else 'pose_span_and_gaps'
    return result


def verify_transport(run, spec, sequence, returncode):
    """Check available native delivery evidence without using accuracy to infer it."""
    evidence = {}
    algorithm = spec['algorithm']
    if algorithm == 'voxel_svio':
        published, received = run / 'transport_stats.json', run / 'native/input_receipt.json'
        if returncode == 0 and not (published.is_file() and received.is_file()):
            raise RuntimeError('Successful Voxel attempt lacks input-delivery evidence: ' + str(run))
        if published.exists() and received.exists():
            evidence = noise_voxel_delivery.audit(run, ROOT / 'datasets' / spec['dataset'] / sequence)
            base.write(run / 'native_delivery_audit.json', evidence)
            if not evidence['passed']:
                raise RuntimeError('Voxel input delivery or native rate gate audit failed: ' + str(run))
    elif algorithm == 'openvins':
        # A player/EOF failure can give the wrapper a nonzero exit while the
        # estimator itself exits normally. Audit that case too, so transport
        # problems cannot become a supposedly bad noise observation. Preserve
        # independent estimator crashes and attempt timeouts as failures.
        node_path = run / 'processes/node.json'
        native_clean_exit = False
        if returncode not in (0, 124) and node_path.is_file():
            node = json.loads(node_path.read_text())
            native_clean_exit = node.get('status') == 'exited' and node.get('exit_code') == 0
        if returncode != 0 and not native_clean_exit:
            return evidence
        evidence = noise_delivery.audit_openvins(run, ROOT / 'datasets' / spec['dataset'] / sequence,
            allowed_pending_tail=PROTOCOL['delivery_policy']['openvins_pending_camera_tail'], require_exact=True,
            require_end_of_stream=PROTOCOL['delivery_policy'].get('openvins_end_of_stream_drain', False),
            require_flow_control=PROTOCOL['delivery_policy'].get('openvins_flow_control', False))
        base.write(run / 'native_delivery_audit.json', evidence)
        if not evidence['passed']:
            raise RuntimeError('OpenVINS delivery gate failed; stop before optimizing around input loss: ' + str(run))
    return evidence


def run_attempt(spec, label, parameters, sequence, mode, repetition, phase):
    key, run_id, seed = identities(spec['id'], label, sequence, mode, repetition, phase)
    record_path = ART / 'attempts' / (key + '.json')
    revision = execution_policy.reviewed_attempt_revision(PROTOCOL, key)
    if revision is not None:
        predecessor = json.loads(Path(revision['record']).read_text())
        if predecessor['params'] != parameters:
            raise RuntimeError('Replacement parameters differ from the reviewed attempt: ' + key)
    if record_path.exists():
        old = json.loads(record_path.read_text())
        if old.get('state') != 'finished':
            raise RuntimeError('Incomplete attempt requires explicit recovery: ' + key)
        if old['params'] != parameters or old.get('campaign_id') != CAMPAIGN:
            raise RuntimeError('Cached observation identity differs: ' + key)
        if old.get('physical_attempt_revision') != revision:
            raise RuntimeError('Cached physical attempt belongs to another revision: ' + key)
        return old
    if (ART / 'STOP_AFTER_CURRENT').exists():
        raise InterruptedError('Stop requested at an attempt boundary')
    parent = spec['sequence_parents'][sequence]
    destination = ROOT / 'configs/experiments/generated' / CAMPAIGN / spec['id'] / label / parent / mode
    candidate = adapters.prepare(ROOT, spec['algorithm'], spec['dataset'], parent, mode, parameters, destination)
    run = ROOT / 'results' / mode / spec['dataset'] / sequence / spec['algorithm'] / ('run' + str(run_id))
    if run.exists():
        raise RuntimeError('Physical attempt already exists without a reusable finished record: ' + str(run))
    env = dict(os.environ)
    for name in CONFIG_ENVIRONMENT:
        env.pop(name, None)
    env.update(PYTHONDONTWRITEBYTECODE='1', BENCHMARK_EVAL_PYTHON=sys.executable,
               AIRSLAM_STAGE_TIMEOUT_S='3600')
    env.update(PROTOCOL['runtime_environment'].get(spec['algorithm'], {}))
    env.update(PROTOCOL.get('runtime_environment_by_study', {}).get(spec['id'], {}))
    env.update(candidate['environment'])
    env.update(execution_policy.identity_environment(
        PROTOCOL, spec['algorithm'], spec['dataset'], sequence))
    if spec['algorithm'] == 'mast3r_fusion':
        env['MAST3R_FUSION_SEED'] = str(seed)
    env['LD_LIBRARY_PATH'] = str(ROOT / 'src/ORB_SLAM3/Thirdparty/DBoW2/lib') + ':' + env.get('LD_LIBRARY_PATH', '')
    command = ['bash', str(ROOT / f'scripts/run/run_{spec["algorithm"]}.sh'),
               spec['dataset'], sequence, str(run_id), mode]
    command = execution_policy.bounded_command(
        command, PROTOCOL, spec['algorithm'], run_id, env)
    timeout_key = 'short' if sequence in spec['clips'] else mode
    timeouts = PROTOCOL['attempt_timeouts_s'].get(spec['algorithm'], PROTOCOL['attempt_timeouts_s'])
    timeout = timeouts[timeout_key]
    budget_path = ART / 'budget.json'
    if not budget_path.is_file():
        raise RuntimeError('No fixed execution deadline has been provided')
    budget = json.loads(budget_path.read_text())
    if time.time() + timeout + 120 > budget['deadline_unix']:
        raise InterruptedError('Insufficient campaign time remains for this attempt plus cleanup')
    distance = base.reference_distance(spec['dataset'], sequence)
    with base.machine_slot():
        verify_frozen()
        if spec['algorithm'] in noise_cleanup.PERSISTENT:
            container, location = noise_cleanup.owned_container(run, ROOT)
            if location != 'persistent':
                raise RuntimeError('Missing private persistent container')
            execution_policy.verify_persistent_limits(PROTOCOL, spec['algorithm'], container)
        record = dict(key=key, campaign_id=CAMPAIGN, state='running', started=base.now(),
                      study=spec['id'], phase=phase, label=label, params=parameters,
                      sequence=sequence, mode=mode, repetition=repetition, run=str(run),
                      candidate=candidate, command=command, timeout_limit_s=timeout,
                      native_seed=seed if spec['algorithm'] == 'mast3r_fusion' else None)
        if revision is not None:
            record['physical_attempt_revision'] = revision
        base.write(record_path, record)
        base.event('attempt_started', key=key, run=str(run))
        log_name = key + ('__physical_' + revision['revision'] if revision is not None else '')
        log = ART / 'wrapper-logs' / (log_name + '.log')
        log.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        with log.open('xb') as stream:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            try:
                returncode = process.wait(timeout=timeout)
                timed_out = False
            except subprocess.TimeoutExpired:
                noise_cleanup.stop_owned_attempt(process, run, ROOT)
                returncode, timed_out = 124, True
            except BaseException:
                noise_cleanup.stop_owned_attempt(process, run, ROOT)
                raise
        elapsed = time.monotonic() - started
        evaluation, native_evidence = {}, None
        if (run / 'run_meta.json').is_file():
            native_evidence = adapters.verify_snapshot(run, spec['algorithm'], parameters)
        elif not timed_out:
            raise RuntimeError('Wrapper did not create metadata; review infrastructure: ' + str(log))
        if (run / 'trajectory.txt').is_file():
            sparse = spec['algorithm'] == 'airslam' or (spec['algorithm'] == 'mast3r_fusion' and mode == 'vio-lc')
            evaluation, _ = base.evaluate_saved_run(ROOT, run, sparse_export=sparse)
            evaluation['qualification'] = dict(status='exploratory_development_only',
                blockers=evaluation.get('qualification', {}).get('blockers', []) +
                ['noise_selected_on_development_ground_truth', 'not_independent_final_test'])
            base.write(run / 'run_eval.json', evaluation)
        if spec['algorithm'] in ('orbslam3', 'voxel_svio', 'airslam'):
            config_path = Path(next(iter(candidate['environment'].values())))
            base.verify_native_parameters(run, spec, parameters, config_path, returncode)
        transport = verify_transport(run, spec, sequence, returncode)
        if spec['algorithm'] == 'openvins' and transport:
            transport['native_noise_parameters'] = noise_delivery.verify_native_noise(run, parameters)
        log_text = log.read_text(errors='replace')
        record.update(state='finished', finished=base.now(), returncode=returncode,
                      timeout=timed_out, wall_s=elapsed, wrapper_log=str(log),
                      result=score(evaluation, returncode, spec['algorithm'], mode, distance),
                      effective_noise_evidence=native_evidence, transport=transport,
                      solver_warnings={'cholesky_failure': log_text.count('Cholesky failure')})
        base.write(record_path, record)
        base.event('attempt_finished', key=key, returncode=returncode, wall_s=round(elapsed, 2), result=record['result'])
        verify_frozen()
        return record
