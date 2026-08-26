#!/usr/bin/env python3
"""Rebuild results/manifest.json from the current filesystem result set."""

from __future__ import annotations

import hashlib
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
from machine_id import get_machine_id  # noqa: E402
from validate_run import (  # noqa: E402
    validate, validate_location, validate_measurements, validate_provenance,
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
        "ate_rmse": (evaluation.get("ate") or {}).get("rmse"),
        "ate_se3_rmse": (evaluation.get("ate_se3") or {}).get("rmse"),
        "rpe_trans_1m_rmse": (evaluation.get("rpe_trans_1m") or {}).get("rmse"),
        "rpe_rot_1m_deg_rmse": (evaluation.get("rpe_rot_1m_deg") or {}).get("rmse"),
        "scale_factor": evaluation.get("scale_factor"),
        "coverage_gap_pct": coverage.get("coverage_gap_pct"),
        "n_pairs_ate": evaluation.get("n_pairs_ate"),
        "processing_fps": runtime.get("processing_fps"),
        "end_to_end_fps": runtime.get("end_to_end_fps"),
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
        measurement_status = "complete"
    else:
        measurement_status = "invalid"
    errors.extend(measurement_errors)
    process = metadata.get("process")
    process_exit_code = process.get("exit_code") if isinstance(process, dict) else None
    if (run_dir / "COMPLETE").is_file():
        status = "complete" if not errors else "invalid"
    elif metadata.get("run_status") == "failed" or process_exit_code not in (None, 0):
        status = "failed"
    else:
        status = "incomplete"

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


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    runs = []
    for run_type in RUN_TYPES:
        root = RESULTS / run_type
        if not root.is_dir():
            continue
        for run_dir in sorted(root.glob("*/*/*/run*")):
            if run_dir.is_dir():
                runs.append(run_entry(run_type, run_dir))

    status = git_value("status", "--porcelain", "--untracked-files=no")
    manifest = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_dirty": bool(status),
        "machine_id": get_machine_id(),
        "runs": runs,
    }
    target = RESULTS / "manifest.json"
    tmp = RESULTS / ".manifest.json.tmp"
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    tmp.replace(target)
    counts: dict[str, int] = {}
    for run in runs:
        counts[run["status"]] = counts.get(run["status"], 0) + 1
    print(f"[manifest] {len(runs)} runs -> {target} ({counts})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
