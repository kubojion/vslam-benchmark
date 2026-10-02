#!/usr/bin/env python3
"""Rebuild the browser manifest from the authoritative, hash-checked inventory."""

from __future__ import annotations

import hashlib
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS = REPO / "results"
RUN_TYPES = ("vo", "vo-lc", "vio", "vio-lc", "gnss-vio")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / 'scripts/eval'))
from build_benchmark_csv import build_rows, load_inventory, preserved_write, row_from_attempt
from validate_run import (  # noqa: E402
    validate, validate_location, validate_measurements, validate_provenance,
    validate_implementation_capture, validate_input_capture, validate_runtime_capture,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO), *args], capture_output=True, text=True,
            timeout=10, check=False,
        )
        return result.stdout.strip() or None
    except Exception:
        return None


def metric_summary(evaluation: dict) -> dict:
    coverage = evaluation.get("coverage") or {}
    runtime = evaluation.get("runtime") or {}
    return {
        "primary_alignment": evaluation.get("primary_alignment"),
        "primary_ate_rmse_m": (evaluation.get("ate" if evaluation.get("primary_alignment")=="sim3" else "ate_se3") or {}).get("rmse"),
        "ate_rmse": (evaluation.get("ate") or {}).get("rmse"),
        "ate_se3_rmse": (evaluation.get("ate_se3") or {}).get("rmse"),
        "rpe_trans_1m_rmse": (evaluation.get("rpe_trans_1m") or {}).get("rmse"),
        "rpe_rot_1m_deg_rmse": (evaluation.get("rpe_rot_1m_deg") or {}).get("rmse"),
        "scale_factor": evaluation.get("scale_factor"),
        "coverage_gap_pct": coverage.get("coverage_gap_pct"),
        "export_kind": coverage.get("export_kind"),
        "camera_pose_coverage_pct": coverage.get("camera_pose_coverage_pct"),
        "reference_pairs_pct_of_input": coverage.get("reference_pairs_pct_of_input"),
        "position_metric_validity": (evaluation.get('metric_validity') or {}).get('position'),
        "n_pairs_ate": evaluation.get("n_pairs_ate"),
        "processing_fps": runtime.get("processing_fps"),
        "end_to_end_fps": runtime.get("end_to_end_fps"),
        "command_input_fps": runtime.get("command_input_fps"),
        "measurement_warning": runtime.get("measurement_warning"),
        "trajectory_pose_rate": runtime.get("trajectory_pose_rate"),
        "realtime_factor": runtime.get("realtime_factor"),
        "end_to_end_time_s": runtime.get("end_to_end_time_s", runtime.get("wall_s")),
        "resource_scope": runtime.get("resource_scope"),
    }


def artifact_inventory(run_dir: Path) -> list[dict]:
    artifacts = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file() or path.name in {"COMPLETE", ".COMPLETE.tmp"}:
            continue
        resolved = path.resolve()
        if run_dir.resolve() not in resolved.parents:
            continue
        artifacts.append({
            "path": path.relative_to(run_dir).as_posix(),
            "size_bytes": path.stat().st_size,
        })
    return artifacts


def run_entry(run_type: str, run_dir: Path) -> dict:
    relative = run_dir.relative_to(RESULTS)
    dataset, sequence, algorithm, run_name = relative.parts[1:5]
    metadata = read_json(run_dir / "run_meta.json")
    evaluation = read_json(run_dir / "run_eval.json")
    errors = validate_location(run_dir) + validate(run_dir)
    provenance_errors = validate_provenance(run_dir, required_schema=None)
    provenance_errors += validate_implementation_capture(run_dir)
    provenance_errors += validate_input_capture(run_dir)
    provenance_errors += validate_runtime_capture(run_dir)
    measurement_errors = validate_measurements(run_dir, required_schema=None)
    if metadata.get("run_status") == "failed":
        provenance_errors = [
            error for error in provenance_errors
            if not error.startswith("unaccepted process exit code ")
        ]
    schema = metadata.get("provenance_schema")
    if schema is None:
        provenance_status = "legacy"
    elif schema == 2 and not provenance_errors:
        provenance_status = "complete"
    else:
        provenance_status = "invalid"
    errors.extend(provenance_errors)
    measurement_schema = metadata.get("measurement_schema")
    if measurement_schema is None:
        measurement_status = "legacy"
    elif measurement_schema == 1 and not measurement_errors:
        measurement_status = "legacy_assumed_processing"
    elif measurement_schema == 2 and not measurement_errors:
        measurement_status = "complete"
    else:
        measurement_status = "invalid"
    errors.extend(measurement_errors)
    process = metadata.get("process")
    process_exit_code = process.get("exit_code") if isinstance(process, dict) else None
    # A metadata probe alone does not reconcile campaign membership or science.
    status = "invalid" if errors else "unreconciled"

    repeat = metadata.get("run_id")
    if repeat is None and run_name.startswith("run"):
        digits = "".join(ch for ch in run_name[3:] if ch.isdigit())
        repeat = int(digits) if digits else run_name

    entry = {
        "path": relative.as_posix(),
        "run_type": run_type,
        "dataset": dataset,
        "sequence": sequence,
        "algorithm": algorithm,
        "repeat": repeat,
        "status": status,
        "machine_id": metadata.get("machine_id", "unknown"),
        "provenance_status": provenance_status,
        "provenance_schema": schema,
        "measurement_status": measurement_status,
        "measurement_schema": measurement_schema,
        "metrics": metric_summary(evaluation),
        "artifacts": artifact_inventory(run_dir),
    }
    if errors:
        entry["validation_errors"] = errors
    for filename, key in (
        ("trajectory.txt", "trajectory_sha256"),
        ("run_meta.json", "run_meta_sha256"),
        ("run_eval.json", "run_eval_sha256"),
    ):
        path = run_dir / filename
        if path.is_file():
            entry[key] = sha256(path)
    return entry


def reconciled_entry(attempt, row):
    run_dir = REPO / attempt['path']
    mode = row['run_type']
    entry = run_entry(mode, run_dir)
    evaluation = read_json(REPO / attempt['evaluation_path']) if attempt.get('evaluation_path') else {}
    entry.update(status=row['run_status'], repeat=int(row['run']), execution_status=row['execution_status'],
                 process_exit_code=row['process_exit_code'], scientific_status=row['scientific_status'],
                 protocol_status=row.get('protocol_status', 'unreviewed'),
                 protocol_state=row.get('protocol_state', 'unreviewed'),
                 protocol_verified_n3=row.get('protocol_verified_n3', False),
                 protocol_blockers=json.loads(row.get('protocol_blockers') or '[]'),
                 attempt_completed=row.get('attempt_completed', False),
                 observed_outcome=row.get('observed_outcome', 'unknown'),
                 implementation_label=row.get('implementation_label', 'historical'),
                 scientific_blockers=json.loads(row['scientific_blockers']), paper_ready=row['paper_ready'],
                 paper_usable=row.get('paper_usable',False), accepted_claim=row.get('accepted_claim'),
                 native_error_observation_count=row.get('native_error_observation_count',0),
                 claim_limits=json.loads(row.get('claim_limits') or '[]'),
                 reproducibility_disclosures=json.loads(row.get('reproducibility_disclosures') or '[]'),
                 campaign_membership=row['campaign_membership'], cohort=row['cohort'],
                 input_variant=row['gnss_variant'], attempt_exists=row['attempt_exists'],
                 trajectory_saved=row['trajectory_saved'], metrics=metric_summary(evaluation),
                 evaluation_path=attempt.get('evaluation_path'),
                 evaluation_sha256=sha256(REPO / attempt['evaluation_path']) if attempt.get('evaluation_path') else None,
                 historical_complete_marker=attempt.get('historical_complete',False))
    # Never preview old plots as if they were generated by the repaired evaluator.
    for artifact in entry['artifacts']:
        suffix=Path(artifact['path']).suffix.lower()
        artifact['interpretation']='historical_derived' if suffix in ('.png','.jpg','.jpeg','.webp','.pdf','.zip') else 'saved_evidence'
        if artifact['path']=='run_eval.json':
            artifact['interpretation']='current_evaluation' if entry.get('run_eval_sha256')==entry['evaluation_sha256'] else 'historical_evaluation'
    if attempt.get('evaluation_path'):
        entry['artifacts'].append(dict(path='repaired_run_eval.json',source_path=attempt['evaluation_path'],
            size_bytes=(REPO/attempt['evaluation_path']).stat().st_size,interpretation='current_numerical_evaluation'))
    return entry


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory',type=Path,default=RESULTS/'repair-20261001/inventory.json')
    parser.add_argument('--output',type=Path,default=RESULTS/'manifest.json')
    args=parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    inventory=load_inventory(args.inventory)
    rows={r['run_path']:r for r in build_rows(inventory)}
    attempts=[a for c in inventory['cells'] for a in c['attempts']]+inventory['other_artifacts']
    runs=[]
    for attempt in attempts:
        row=rows.get(attempt['path'])
        if row is None:
            evaluation=read_json(REPO/attempt['evaluation_path']) if attempt.get('evaluation_path') else {}
            row=row_from_attempt(attempt,evaluation,None,membership=attempt['category'])
        runs.append(reconciled_entry(attempt,row))

    status = git_value("status", "--porcelain", "--untracked-files=no")
    manifest = {
        "schema_version": 2,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_dirty": bool(status),
        "inventory_sha256": sha256(args.inventory),
        "inventory_path": str(args.inventory.resolve().relative_to(REPO)),
        "audit_status": inventory['audit_status'],
        "counts": inventory['counts'],
        "exclusions": inventory['excluded'],
        "runs": runs,
    }
    target = args.output
    preserved_write(target,json.dumps(manifest, indent=2, sort_keys=True,allow_nan=False) + "\n")
    counts: dict[str, int] = {}
    for run in runs:
        counts[run["status"]] = counts.get(run["status"], 0) + 1
    print(f"[manifest] {len(runs)} runs -> {target} ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
