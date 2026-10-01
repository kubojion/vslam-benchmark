#!/usr/bin/env python3
"""Validate one evaluated run and write its COMPLETE marker last."""

from __future__ import annotations

import argparse
import csv
import json
import os
import math
import re
import socket
import sys
from pathlib import Path


REQUIRED = ("trajectory.txt", "run_meta.json", "run_eval.json")
VALID_EVALUATION_STATUSES = {"ok", "scale_collapse"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40,64}$")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from provenance_requirements import requirement_for  # noqa: E402


def validate_location(run_dir: Path) -> list[str]:
    repo = Path(__file__).resolve().parents[2]
    results = (repo / "results").resolve()
    try:
        relative = run_dir.resolve().relative_to(results)
    except ValueError:
        return [f"run directory is outside {results}"]
    if len(relative.parts) != 5 or relative.parts[0] not in {
        "vo", "vo-lc", "vio", "vio-lc", "gnss-vio"
    } or not relative.parts[-1].startswith("run"):
        return [f"unexpected run directory layout: {relative}"]
    return []


def validate(run_dir: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED:
        path = run_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty {name}")
    for name in ("run_meta.json", "run_eval.json"):
        path = run_dir / name
        if path.is_file():
            try:
                data = json.loads(path.read_text())
                if name == "run_eval.json" and data.get("run_status") not in VALID_EVALUATION_STATUSES:
                    errors.append(
                        f"run_eval.json status is {data.get('run_status')!r}; "
                        f"expected one of {sorted(VALID_EVALUATION_STATUSES)}"
                    )
            except Exception as exc:
                errors.append(f"invalid {name}: {exc}")
    trajectory = run_dir / "trajectory.txt"
    if trajectory.is_file():
        rows = 0
        previous_timestamp: float | None = None
        try:
            with trajectory.open() as stream:
                for line in stream:
                    if not line.strip() or line.lstrip().startswith("#"):
                        continue
                    fields = line.split()
                    if len(fields) < 8:
                        errors.append("trajectory contains a row with fewer than 8 columns")
                        break
                    try:
                        values = [float(value) for value in fields[:8]]
                    except ValueError:
                        errors.append("trajectory contains a non-numeric pose")
                        break
                    if not all(math.isfinite(value) for value in values):
                        errors.append("trajectory contains a non-finite pose")
                        break
                    timestamp = values[0]
                    if previous_timestamp is not None and timestamp <= previous_timestamp:
                        errors.append("trajectory timestamps are not strictly increasing")
                        break
                    if sum(value * value for value in values[4:8]) < 1e-12:
                        errors.append("trajectory contains a zero quaternion")
                        break
                    previous_timestamp = timestamp
                    rows += 1
            if rows < 2:
                errors.append("trajectory contains fewer than 2 poses")
        except OSError as exc:
            errors.append(f"cannot read trajectory: {exc}")
    return errors


def validate_provenance(run_dir: Path, *, required_schema: int | None) -> list[str]:
    errors: list[str] = []
    meta_path = run_dir / "run_meta.json"
    if not meta_path.is_file():
        return errors
    try:
        meta = json.loads(meta_path.read_text())
    except Exception:
        return errors
    schema = meta.get("provenance_schema")
    if schema is None and required_schema is None:
        return errors  # Migrated historical run.
    expected = required_schema or 2
    if schema != expected:
        return [f"provenance_schema is {schema!r}, expected {expected}"]
    provenance = meta.get("provenance")
    if not isinstance(provenance, dict):
        return ["missing provenance object"]

    private_markers = (str(Path(__file__).resolve().parents[2]), str(Path.home()))
    private_path_re = re.compile(r"/(?:home|data)/[^/\s\"']+")

    def walk_strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for nested in value.values():
                yield from walk_strings(nested)
        elif isinstance(value, list):
            for nested in value:
                yield from walk_strings(nested)

    for value in walk_strings(meta):
        if any(marker and marker in value for marker in private_markers) or private_path_re.search(value):
            errors.append("run metadata exposes a private absolute path")
            break
        if socket.gethostname() and socket.gethostname() in value:
            errors.append("run metadata exposes the host name")
            break

    def indexed(category: str, identity: str = "role") -> dict[str, dict]:
        values = provenance.get(category)
        if not isinstance(values, list):
            errors.append(f"provenance.{category} is not a list")
            return {}
        result = {}
        for item in values:
            if not isinstance(item, dict) or not isinstance(item.get(identity), str):
                errors.append(f"provenance.{category} contains an invalid entry")
                continue
            if item[identity] in result:
                errors.append(f"provenance.{category} contains duplicate role {item[identity]!r}")
            result[item[identity]] = item
        return result

    artifacts = indexed("artifacts")
    binaries = indexed("binaries")
    sources = indexed("sources")
    parameters = provenance.get("parameters")
    if not isinstance(parameters, dict):
        errors.append("provenance.parameters is not an object")
        parameters = {}

    for category, entries in (("artifact", artifacts), ("binary", binaries)):
        for role, entry in entries.items():
            if not SHA256_RE.fullmatch(str(entry.get("sha256", ""))):
                errors.append(f"{category} {role!r} has no valid SHA-256")
            if not isinstance(entry.get("size_bytes"), int) or entry["size_bytes"] < 0:
                errors.append(f"{category} {role!r} has no valid size")
            path = str(entry.get("path", ""))
            if not path or Path(path).is_absolute():
                errors.append(f"{category} {role!r} exposes an absolute or empty path")
            snapshot = entry.get("snapshot")
            if snapshot is not None and (Path(str(snapshot)).is_absolute() or ".." in Path(str(snapshot)).parts):
                errors.append(f"{category} {role!r} has an unsafe snapshot path")
            if snapshot is not None and not SHA256_RE.fullmatch(str(entry.get("snapshot_sha256", ""))):
                errors.append(f"{category} {role!r} has no valid snapshot SHA-256")
    for role, entry in sources.items():
        if not COMMIT_RE.fullmatch(str(entry.get("commit", ""))):
            errors.append(f"source {role!r} has no valid commit")
        source_path = str(entry.get("path", ""))
        if not source_path or Path(source_path).is_absolute():
            errors.append(f"source {role!r} exposes an absolute or empty path")
        if not isinstance(entry.get("dirty"), bool):
            errors.append(f"source {role!r} has no dirty-state flag")
        if entry.get("dirty") and not SHA256_RE.fullmatch(str(entry.get("diff_sha256", ""))):
            errors.append(f"source {role!r} is dirty but has no diff hash")

    workspace = provenance.get("workspace")
    if not isinstance(workspace, dict) or not COMMIT_RE.fullmatch(str(workspace.get("commit", ""))):
        errors.append("workspace has no valid commit")
    elif not isinstance(workspace.get("dirty"), bool):
        errors.append("workspace has no dirty-state flag")
    elif workspace.get("dirty") and not SHA256_RE.fullmatch(str(workspace.get("diff_sha256", ""))):
        errors.append("workspace is dirty but has no diff hash")

    process = meta.get("process")
    if not isinstance(process, dict) or not isinstance(process.get("exit_code"), int):
        errors.append("missing process exit status")
    elif process["exit_code"] != 0 and not process.get("accepted_nonzero_exit"):
        errors.append(f"unaccepted process exit code {process['exit_code']}")
    elif process["exit_code"] != 0 and not process.get("failure_reason"):
        errors.append("accepted nonzero exit has no documented reason")

    requirement = requirement_for(str(meta.get("algo", "")), str(meta.get("run_type", "vo")))
    if requirement is None:
        errors.append(f"no provenance contract for algorithm {meta.get('algo')!r}")
        return errors
    for role in sorted(requirement.artifacts - artifacts.keys()):
        errors.append(f"missing required artifact role {role!r}")
    for role in sorted(requirement.binaries - binaries.keys()):
        errors.append(f"missing required binary role {role!r}")
    for role in sorted(requirement.sources - sources.keys()):
        errors.append(f"missing required source role {role!r}")
    for key in sorted(requirement.parameters - parameters.keys()):
        errors.append(f"missing required parameter {key!r}")
    environment = provenance.get("environment")
    if requirement.environment and not isinstance(environment, dict):
        errors.append("missing required environment fingerprint")
    elif requirement.environment:
        if not SHA256_RE.fullmatch(str(environment.get("sha256", ""))):
            errors.append("environment fingerprint has no valid SHA-256")
        snapshot = Path(str(environment.get("snapshot", "")))
        if not str(snapshot) or snapshot.is_absolute() or ".." in snapshot.parts:
            errors.append("environment fingerprint has an unsafe snapshot path")
    if requirement.container and not isinstance(provenance.get("container"), dict):
        errors.append("missing required container image identity")
    elif requirement.container and not re.fullmatch(r"sha256:[0-9a-f]{64}", str(provenance["container"].get("image_id", ""))):
        errors.append("container fingerprint has no valid image ID")
    return errors


def validate_measurements(run_dir: Path, *, required_schema: int | None) -> list[str]:
    errors: list[str] = []
    meta_path = run_dir / "run_meta.json"
    if not meta_path.is_file():
        return errors
    try:
        meta = json.loads(meta_path.read_text())
    except Exception:
        return errors
    schema = meta.get("measurement_schema")
    if schema is None and required_schema is None:
        return errors
    if schema not in (1, 2) or (required_schema is not None and schema != required_schema):
        return [f"measurement_schema is {schema!r}, expected {required_schema or '1 or 2'}"]
    values = meta.get("measurements")
    if not isinstance(values, dict):
        return ["missing measurements object"]

    mode = values.get("mode")
    if mode not in {"max_throughput", "paced", "transport"}:
        errors.append(f"invalid measurement mode {mode!r}")

    for field in (
        "input_frames", "processed_frames", "published_frames", "dropped_frames",
        "publisher_dropped_frames", "output_poses", "deadline_misses", "max_queue_depth",
    ):
        value = values.get(field)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
            errors.append(f"measurement {field!r} is not a non-negative integer or null")
    for field in (
        "input_duration_s", "trajectory_duration_s", "processing_time_s",
        "end_to_end_time_s", "initialization_time_s", "steady_state_time_s",
        "final_optimization_time_s", "shutdown_time_s", "processing_fps", "end_to_end_fps",
        "trajectory_pose_rate", "realtime_factor",
        "command_time_s", "command_input_fps",
    ):
        value = values.get(field)
        if value is not None and (
            not isinstance(value, (int, float)) or isinstance(value, bool)
            or not math.isfinite(float(value)) or value < 0
        ):
            errors.append(f"measurement {field!r} is not a finite non-negative number or null")

    if not isinstance(values.get("input_frames"), int) or values["input_frames"] < 1:
        errors.append("input frame count is unavailable")
    if not isinstance(values.get("output_poses"), int) or values["output_poses"] < 2:
        errors.append("output pose count is unavailable")
    if not isinstance(values.get("end_to_end_time_s"), (int, float)) or values["end_to_end_time_s"] <= 0:
        errors.append("end-to-end time is unavailable")

    trajectory = run_dir / "trajectory.txt"
    if trajectory.is_file() and isinstance(values.get("output_poses"), int):
        with trajectory.open() as stream:
            actual_poses = sum(
                1 for line in stream if line.strip() and not line.lstrip().startswith("#")
            )
        if actual_poses != values["output_poses"]:
            errors.append(
                f"output pose count {values['output_poses']} does not match trajectory rows {actual_poses}"
            )

    if schema == 1 and mode in {"max_throughput", "paced"}:
        if values.get("processed_frames") != values.get("input_frames"):
            errors.append(f"{mode} run did not account for every input frame")
    if schema == 1 and mode == "max_throughput":
        if values.get("processing_time_s") != values.get("end_to_end_time_s"):
            errors.append("max-throughput processing time does not match estimator command time")
        frames = values.get("processed_frames")
        seconds = values.get("processing_time_s")
        expected_fps = frames / seconds if frames is not None and seconds else None
        observed_fps = values.get("processing_fps")
        if expected_fps is None or observed_fps is None or not math.isclose(
            expected_fps, observed_fps, rel_tol=1e-9, abs_tol=1e-9,
        ):
            errors.append("processing FPS is missing or inconsistent")
    elif values.get("processing_fps") is not None or values.get("processing_time_s") is not None:
        errors.append(f"{mode} run claims processing throughput without internal timing")

    if schema == 2:
        # No current counter/timer adapter provides the evidence needed for these
        # claims. Future instrumentation must extend this contract explicitly.
        if values.get("processed_frames") is not None or values.get("dropped_frames") is not None:
            errors.append("run invents estimator processed/drop counts without instrumentation")
        if values.get("processed_frames_evidence") != "unavailable":
            errors.append("unsupported processed-frame evidence in measurement schema 2")
        if values.get("processing_time_scope") != "unavailable":
            errors.append("processing time scope requires unavailable instrumentation")
        if mode == "max_throughput":
            seconds = values.get("command_time_s")
            nominal = values.get("command_input_fps")
            frames = values.get("input_frames")
            expected = frames / seconds if isinstance(frames, int) and isinstance(seconds, (int, float)) and seconds > 0 else None
            if seconds != values.get("end_to_end_time_s") or expected is None or not isinstance(nominal, (int, float)) or not math.isclose(expected, nominal, rel_tol=1e-9):
                errors.append("nominal command input throughput is missing or inconsistent")
        elif values.get("command_time_s") is not None or values.get("command_input_fps") is not None:
            errors.append("paced/transport run claims unmeasured command throughput")

    if mode == "transport":
        transport = values.get("transport")
        if not isinstance(transport, dict):
            errors.append("transport run has no publisher statistics")
        elif values.get("published_frames") != transport.get("camera_frames_published"):
            errors.append("published frame count disagrees with transport statistics")
        if values.get("processed_frames") is not None or values.get("dropped_frames") is not None:
            errors.append("transport run invents estimator receive/drop counts")

    scope = values.get("resource_scope")
    if scope not in {"process_tree", "container", "process_tree+container"}:
        errors.append("resource measurements are missing an explicit scoped target")
    resources = run_dir / "resources.csv"
    try:
        with resources.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, csv.Error) as exc:
        errors.append(f"cannot read scoped resources.csv: {exc}")
        rows = []
    if not rows:
        errors.append("scoped resources.csv has no samples")
    else:
        scopes = {row.get("scope") for row in rows}
        if scopes != {scope}:
            errors.append("resources.csv contains an absent or inconsistent scope")
        if not any(row.get("target_available") == "true" for row in rows):
            errors.append("resource target was unavailable for every sample")
        if not any(row.get("cpu_time_s") not in {None, ""} for row in rows):
            errors.append("resources.csv has no process CPU accounting")
        if not any(row.get("ram_mib") not in {None, ""} for row in rows):
            errors.append("resources.csv has no process memory accounting")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--require-provenance", type=int, choices=(2,))
    parser.add_argument("--require-measurements", type=int, choices=(1, 2))
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    location_errors = validate_location(run_dir)
    if location_errors:
        for error in location_errors:
            print(f"[validate] {run_dir}: {error}")
        return 1
    marker = run_dir / "COMPLETE"
    if marker.exists() and not args.check_only:
        marker.unlink()
    errors = validate(run_dir)
    errors.extend(validate_provenance(run_dir, required_schema=args.require_provenance))
    errors.extend(validate_measurements(run_dir, required_schema=args.require_measurements))
    if errors:
        for error in errors:
            print(f"[validate] {run_dir}: {error}")
        return 1
    if not args.check_only:
        tmp = run_dir / ".COMPLETE.tmp"
        tmp.write_bytes(b"")
        os.replace(tmp, marker)
        print(f"[validate] complete -> {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
