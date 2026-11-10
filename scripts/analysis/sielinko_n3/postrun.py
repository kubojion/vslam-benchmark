#!/usr/bin/env python3
"""Post-run evaluation of one N=3 attempt with the frozen campaign's own code.

Run as a separate process with the item's evaluator interpreter and -B:
  python -B postrun.py evaluate ITEM_JSON RETURNCODE TIMED_OUT WRAPPER_LOG
  python -B postrun.py air-baseline ITEM_JSON
It imports the frozen worktree's noise_campaign_engine (and, for GPU items, the first run's
gpu6.py adapter) and repeats the post-native steps of engine.run_attempt / gpu6.guarded_run:
snapshot check, evaluate_saved_run, native parameter and transport audits, score, and the
GPU native/resource audits. Prints one JSON object. Any raised error is an infrastructure fault.
"""
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True


def env_protocol_path(item):
    return next(e['path'] for e in item['pinned_evidence'] if e['role'] == 'env_protocol')


def setup(item):
    root = Path(item['worktree']['path'])
    sys.path[:0] = [str(root / 'scripts/analysis'), str(root / 'scripts/run')]
    import noise_campaign_engine as engine
    protocol = json.loads(Path(env_protocol_path(item)).read_text())
    engine.PROTOCOL, engine.CAMPAIGN = protocol, item['campaign_id']
    gpu = None
    auditor = item['evaluator'].get('gpu_auditor')
    if auditor:
        sys.path.insert(0, auditor['here'])
        spec = importlib.util.spec_from_file_location('n3_gpu6', auditor['module'])
        gpu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gpu)
    study = next(s for s in protocol['studies'] if s['id'] == item['study'])
    return root, engine, protocol, study, gpu


def air_baseline(item):
    _, _, _, _, gpu = setup(item)
    directory = Path(item['evaluator']['audit_dir'])
    value = gpu.air_values()
    events = dict(line.split() for line in value['memory.events'].splitlines())
    (directory / 'air-resource-baseline.json').write_text(json.dumps(events, indent=2) + '\n')
    return dict(baseline=events)


def evaluate(item, returncode, timed_out, wrapper_log):
    root, engine, protocol, spec, gpu = setup(item)
    base, adapters = engine.base, engine.adapters
    algorithm, mode, sequence, parameters = item['algorithm'], item['mode'], item['sequence'], item['parameters']
    run = Path(item['run_dir'])
    evaluation, native_evidence = {}, None
    if (run / 'run_meta.json').is_file():
        native_evidence = adapters.verify_snapshot(run, algorithm, parameters)
    elif not timed_out:
        raise RuntimeError('Wrapper did not create metadata; review infrastructure: ' + wrapper_log)
    if (run / 'trajectory.txt').is_file():
        sparse = algorithm == 'airslam' or (algorithm == 'mast3r_fusion' and mode == 'vio-lc')
        evaluation, _ = base.evaluate_saved_run(engine.ROOT, run, sparse_export=sparse)
        evaluation['qualification'] = dict(status='exploratory_development_only',
            blockers=evaluation.get('qualification', {}).get('blockers', []) +
            ['noise_selected_on_development_ground_truth', 'not_independent_final_test'])
        base.write(run / 'run_eval.json', evaluation)
    if algorithm in ('orbslam3', 'voxel_svio', 'airslam'):
        config_path = Path(next(iter(item['config']['environment'].values())))
        base.verify_native_parameters(run, spec, parameters, config_path, returncode)
    transport = engine.verify_transport(run, spec, sequence, returncode)
    if algorithm == 'openvins' and transport.get('passed') is True:
        transport['native_noise_parameters'] = engine.noise_delivery.verify_native_noise(run, parameters)
    log_text = Path(wrapper_log).read_text(errors='replace')
    out = dict(result=engine.score(evaluation, returncode, algorithm, mode, base.reference_distance(item['dataset'], sequence)),
               effective_noise_evidence=native_evidence, transport=transport,
               solver_warnings={'cholesky_failure': log_text.count('Cholesky failure')})
    if gpu is not None:
        out['gpu_audit'] = gpu_audit(item, gpu, run, spec, returncode)
    return out


def gpu_audit(item, gpu, run, spec, returncode):
    """gpu6.guarded_run's post-native checks, against this attempt's audit directory."""
    directory = Path(item['evaluator']['audit_dir'])
    cap, high = item['memory']['max_gib'] * 1024 ** 3, item['memory']['high_gib'] * 1024 ** 3
    starts = [json.loads(p.read_text()) for p in directory.glob('native-start-*.json')]
    ends = [json.loads(p.read_text()) for p in directory.glob('native-end-*.json')]
    if item['algorithm'] != 'airslam' and (not starts or not ends):
        raise RuntimeError('Native start/end resource receipts absent')
    evidence = {}
    if item['algorithm'] == 'airslam':
        live = gpu.air_values()
        baseline = json.loads((directory / 'air-resource-baseline.json').read_text())
        errors = gpu.air_errors(live, baseline)
        if errors:
            raise RuntimeError('AirSLAM terminal resource mismatch: ' + str(errors))
        (directory / 'air-resource-terminal.json').write_text(json.dumps(live, indent=2) + '\n')
    for receipt in starts + ends:
        errors = gpu.resource_errors(receipt['live'], cap, high)
        if errors:
            raise RuntimeError('Native resource receipt fault: ' + str(errors))
        if not receipt['live']['path'].endswith('/' + item['unit'] + '.scope'):
            raise RuntimeError('Native process outside owned scope')
    candidate = dict(item['config'].get('expected_receipt') or {}, environment=item['config']['environment'])
    (directory / 'candidate.json').write_text(json.dumps(candidate, indent=2) + '\n')
    evidence['native'] = gpu.audit_native(run, spec, item['sequence'], item['mode'], item['parameters'], directory, returncode)
    evidence['receipts'] = dict(starts=len(starts), ends=len(ends))
    return evidence


def main(argv):
    action, item = argv[0], json.loads(Path(argv[1]).read_text())
    if action == 'air-baseline':
        out = air_baseline(item)
    elif action == 'evaluate':
        out = evaluate(item, int(argv[2]), argv[3] == '1', argv[4])
    else:
        raise SystemExit('unknown action')
    print(json.dumps(out, allow_nan=False, default=str))


if __name__ == '__main__':
    main(sys.argv[1:])
