#!/usr/bin/env python3
"""Attach privacy-safe, reproducible provenance schema v2 to run_meta.json.

Runners pass every effective input explicitly. Repeatable arguments use
``role=path`` or ``key=value`` syntax::

    _enrich_run_meta.py run_meta.json \
        --artifact estimator_config=configs/algo/config.yaml \
        --artifact model=weights.pth \
        --source algorithm=src/algo \
        --binary estimator=build/algo \
        --param playback_rate=1.0 --conda-env algo

Small text inputs are snapshotted under ``run<N>/provenance/``. Large models,
vocabularies, engines, and binaries are identified by SHA-256 without copying.
Paths stored in metadata are repository-relative or reduced to a basename, so
hostnames, usernames, and private absolute paths are never exported.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "results"
ROLE_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")
TEXT_SUFFIXES = {".json", ".yaml", ".yml", ".txt", ".cfg", ".ini", ".toml", ".csv"}
SNAPSHOT_LIMIT = 2 * 1024 * 1024
TRACKED_ENV = (
    "CUDA_VISIBLE_DEVICES",
    "TORCH_CUDA_ARCH_LIST",
    "ORBSLAM3_CONFIG",
    "OKVIS2_CONFIG",
    "OKVIS2X_CONFIG",
    "OV2SLAM_CONFIG",
    "OPENVINS_RATE",
    "OV2SLAM_PLAYBACK_RATE",
    "DPVO_STRIDE",
    "DPVO_SKIP",
    "DPVO_SEED",
    "GT_OVERRIDE",
    "AIRSLAM_LAUNCH",
    "GNSS_VARIANT",
)
MEASUREMENT_MODES = ("max_throughput", "paced", "transport")


def privacy_safe_string(value: str) -> str:
    """Remove repository/home prefixes from user-supplied metadata strings."""
    normalized = value.replace(str(REPO), "<repo>").replace(str(Path.home()), "<home>")
    hostname = socket.gethostname()
    if hostname:
        normalized = normalized.replace(hostname, "<host>")
    return re.sub(r"/(?:home|data)/[^/\s\"']+", "/<private>", normalized)


def command(args: list[str], *, cwd: Path | None = None, timeout: int = 30) -> str | None:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def split_assignment(value: str, option: str) -> tuple[str, str]:
    if "=" not in value:
        raise ValueError(f"{option} expects role=path or key=value, got {value!r}")
    key, raw = value.split("=", 1)
    if not ROLE_RE.fullmatch(key) or not raw:
        raise ValueError(f"invalid {option} assignment: {value!r}")
    return key, raw


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO).as_posix()
    except ValueError:
        return resolved.name


def cache_path() -> Path:
    return RESULTS / ".cache" / "provenance-hashes.json"


def sha256_file(path: Path) -> str:
    stat = path.stat()
    cache_key = hashlib.sha256(str(path.resolve()).encode()).hexdigest()
    signature = [stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns]
    target = cache_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    lock_path = target.with_suffix(".lock")
    with lock_path.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            cache = json.loads(target.read_text()) if target.is_file() else {}
        except (OSError, json.JSONDecodeError):
            cache = {}
        hit = cache.get(cache_key)
        if isinstance(hit, dict) and hit.get("signature") == signature:
            return str(hit["sha256"])

        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        value = digest.hexdigest()
        cache[cache_key] = {"signature": signature, "sha256": value}
        tmp = target.with_suffix(".tmp")
        tmp.write_text(json.dumps(cache, sort_keys=True) + "\n")
        os.replace(tmp, target)
        return value


def snapshot_text(path: Path, role: str, run_dir: Path) -> tuple[str, bool, str] | None:
    if path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > SNAPSHOT_LIMIT:
        return None
    try:
        raw = path.read_text(errors="strict")
    except (OSError, UnicodeError):
        return None
    normalized = privacy_safe_string(raw)
    out_dir = run_dir / "provenance"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", path.name)
    output = out_dir / f"{role}--{safe_name}"
    output.write_text(normalized)
    return (
        output.relative_to(run_dir).as_posix(),
        normalized != raw,
        hashlib.sha256(normalized.encode()).hexdigest(),
    )


def artifact_entry(role: str, raw_path: str, run_dir: Path, *, snapshot: bool) -> dict[str, Any]:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO / path
    if not path.is_file():
        raise ValueError(f"{role}: required file does not exist: {raw_path}")
    entry: dict[str, Any] = {
        "role": role,
        "path": display_path(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if snapshot and (saved := snapshot_text(path, role, run_dir)):
        entry["snapshot"], entry["snapshot_normalized"], entry["snapshot_sha256"] = saved
    return entry


def source_entry(role: str, raw_path: str) -> dict[str, Any]:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO / path
    if not path.is_dir():
        raise ValueError(f"{role}: source directory does not exist: {raw_path}")
    commit = command(["git", "-C", str(path), "rev-parse", "HEAD"])
    if not commit:
        raise ValueError(f"{role}: source is not a readable Git checkout: {raw_path}")
    status = command(["git", "-C", str(path), "status", "--porcelain", "--untracked-files=no"])
    diff = command(["git", "-C", str(path), "diff", "--binary", "HEAD"], timeout=60) or ""
    return {
        "role": role,
        "path": display_path(path),
        "commit": commit,
        "dirty": bool(status),
        "diff_sha256": hashlib.sha256(diff.encode()).hexdigest() if diff else None,
    }


def parse_scalar(raw: str) -> Any:
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"none", "null"}:
        return None
    try:
        return int(raw)
    except ValueError:
        try:
            return float(raw)
        except ValueError:
            return raw


def _timestamps(path: Path) -> list[float]:
    values: list[float] = []
    try:
        with path.open() as stream:
            for line in stream:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                token = line.split(",", 1)[0].split()[0]
                if token.lower() in {"timestamp", "timestamp_ns", "time"}:
                    continue
                values.append(float(token))
    except (OSError, ValueError):
        return []
    if values and max(abs(value) for value in values) > 1e11:
        values = [value / 1e9 for value in values]
    return values


def sequence_measurements(dataset: str, sequence: str) -> tuple[int | None, float | None]:
    seq_dir = REPO / "datasets" / dataset / sequence
    candidates = (
        seq_dir / "times.txt",
        seq_dir / "mav0" / "cam0" / "data.csv",
    )
    for candidate in candidates:
        values = _timestamps(candidate)
        if values:
            duration = values[-1] - values[0] if len(values) > 1 else None
            return len(values), duration if duration is not None and duration > 0 else None
    return None, None


def trajectory_measurements(path: Path) -> tuple[int | None, float | None]:
    values = _timestamps(path)
    if not values:
        return None, None
    duration = values[-1] - values[0] if len(values) > 1 else None
    return len(values), duration if duration is not None and duration > 0 else None


def read_transport_stats(raw_path: str | None) -> dict[str, Any] | None:
    if not raw_path:
        return None
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = REPO / path
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read transport statistics {raw_path!r}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("transport statistics must be a JSON object")
    allowed: dict[str, Any] = {}
    for key in (
        "camera_frames_expected", "camera_frames_published", "imu_messages_published",
        "gnss_messages_published", "camera_read_failures",
        "estimator_output_messages",
    ):
        item = value.get(key)
        if item is not None:
            if not isinstance(item, int) or item < 0:
                raise ValueError(f"transport statistic {key!r} must be a non-negative integer")
            allowed[key] = item
    return allowed


def resource_scope(run_dir: Path) -> str | None:
    path = run_dir / "resources.csv"
    import csv
    for _ in range(50):
        try:
            with path.open(newline="") as stream:
                row = next(csv.DictReader(stream), None)
            scope = row.get("scope") if row else None
            if scope in {"process_tree", "container", "process_tree+container"}:
                return scope
        except (OSError, csv.Error):
            pass
        time.sleep(0.1)
    return None


def build_measurements(
    meta: dict[str, Any], run_dir: Path, mode: str, transport_path: str | None,
) -> dict[str, Any]:
    dataset = str(meta.get("dataset", ""))
    sequence = str(meta.get("seq") or meta.get("sequence") or "")
    input_frames, input_duration = sequence_measurements(dataset, sequence)
    output_poses, trajectory_duration = trajectory_measurements(run_dir / "trajectory.txt")
    try:
        end_to_end = float(meta.get("duration_s"))
        if end_to_end <= 0:
            end_to_end = None
    except (TypeError, ValueError):
        end_to_end = None

    transport = read_transport_stats(transport_path)
    processed_frames: int | None = input_frames if mode in {"max_throughput", "paced"} else None
    processing_time = end_to_end if mode == "max_throughput" else None
    processing_fps = (
        processed_frames / processing_time
        if processed_frames is not None and processing_time else None
    )
    published_frames = transport.get("camera_frames_published") if transport else None
    publisher_dropped = None
    if transport and transport.get("camera_frames_expected") is not None and published_frames is not None:
        publisher_dropped = max(0, transport["camera_frames_expected"] - published_frames)

    measurements: dict[str, Any] = {
        "mode": mode,
        "input_frames": input_frames,
        "processed_frames": processed_frames,
        "published_frames": published_frames,
        # End-estimator drop counts require estimator instrumentation.  Source
        # publisher misses are reported separately and never substituted.
        "dropped_frames": None,
        "publisher_dropped_frames": publisher_dropped,
        "output_poses": output_poses,
        "input_duration_s": input_duration,
        "trajectory_duration_s": trajectory_duration,
        "processing_time_s": processing_time,
        "end_to_end_time_s": end_to_end,
        "initialization_time_s": None,
        "steady_state_time_s": None,
        "final_optimization_time_s": None,
        "shutdown_time_s": None,
        "processing_fps": processing_fps,
        "end_to_end_fps": input_frames / end_to_end if input_frames is not None and end_to_end else None,
        "trajectory_pose_rate": output_poses / trajectory_duration if output_poses and trajectory_duration else None,
        "realtime_factor": input_duration / end_to_end if input_duration and end_to_end else None,
        "processing_time_scope": (
            "estimator_command_including_initialization_and_finalization"
            if mode == "max_throughput" else "unavailable"
        ),
        "resource_scope": resource_scope(run_dir),
        "deadline_misses": None,
        "max_queue_depth": None,
        "transport": transport,
    }
    return measurements


def execution_stages(run_dir: Path) -> list[dict[str, Any]]:
    """Summarize retained supervisor evidence, separate from config identity.

    A roslaunch/composite command status is not a native node exit status.
    Keep both the raw state and signal log available for execution review.
    """
    result = []
    for path in sorted((run_dir / "processes").glob("*.json")):
        record = json.loads(path.read_text())
        item = {key: record.get(key) for key in (
            "status", "exit_code", "signal_requests", "error",
            "started_unix", "finished_unix", "descendants_remaining_at_parent_exit",
        )}
        item.update(stage=path.stem, state=path.relative_to(run_dir).as_posix(),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    scope="supervised_command_not_individual_native_nodes")
        stops = path.with_suffix(".stops.jsonl")
        item["forced_kill_recorded"] = False
        if stops.exists():
            events = [json.loads(line) for line in stops.read_text().splitlines() if line.strip()]
            item.update(stop_log=stops.relative_to(run_dir).as_posix(),
                        stop_log_sha256=hashlib.sha256(stops.read_bytes()).hexdigest(),
                        forced_kill_recorded=any(event.get("signal") == 9
                            for stop in events for event in stop.get("signals", [])))
        result.append(item)
    return result


def conda_snapshot(name: str, run_dir: Path) -> dict[str, Any]:
    raw = command(["conda", "list", "-n", name, "--json"], timeout=60)
    if raw is None:
        raise ValueError(f"cannot inspect conda environment {name!r}")
    packages = json.loads(raw)
    normalized = sorted(
        [{
            "name": str(pkg.get("name", "")),
            "version": str(pkg.get("version", "")),
            "build": str(pkg.get("build_string") or pkg.get("build", "")),
            # A channel URL can contain credentials. The final path component is
            # enough to distinguish defaults/conda-forge/pytorch/nvidia here.
            "channel": str(pkg.get("channel", "")).rstrip("/").rsplit("/", 1)[-1],
        }
        for pkg in packages
        ],
        key=lambda item: (item["name"], item["version"], item["build"]),
    )
    payload = json.dumps(normalized, indent=2, sort_keys=True) + "\n"
    out_dir = run_dir / "provenance"
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"conda-{name}.json"
    output.write_text(payload)
    return {
        "kind": "conda",
        "name": name,
        "snapshot": output.relative_to(run_dir).as_posix(),
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
        "package_count": len(normalized),
    }


def workspace_entry() -> dict[str, Any]:
    commit = command(["git", "-C", str(REPO), "rev-parse", "HEAD"])
    status = command(["git", "-C", str(REPO), "status", "--porcelain", "--untracked-files=no"])
    diff = command(["git", "-C", str(REPO), "diff", "--binary", "HEAD"], timeout=60) or ""
    return {
        "commit": commit,
        "dirty": bool(status),
        "diff_sha256": hashlib.sha256(diff.encode()).hexdigest() if diff else None,
    }


def container_entry(*, container: str | None = None, image_name: str | None = None) -> dict[str, Any]:
    if container:
        image_id = command(["docker", "inspect", "--format", "{{.Image}}", container])
        configured_image = command(["docker", "inspect", "--format", "{{.Config.Image}}", container])
        if not image_id:
            raise ValueError(f"cannot inspect container {container!r}")
    else:
        assert image_name
        image_id = command(["docker", "image", "inspect", "--format", "{{.Id}}", image_name])
        configured_image = image_name
        if not image_id:
            raise ValueError(f"cannot inspect image {image_name!r}")

    digests_raw = command(["docker", "image", "inspect", "--format", "{{json .RepoDigests}}", image_id])
    labels_raw = command(["docker", "image", "inspect", "--format", "{{json .Config.Labels}}", image_id])
    try:
        digests = json.loads(digests_raw) if digests_raw else []
    except json.JSONDecodeError:
        digests = []
    try:
        labels = json.loads(labels_raw) if labels_raw and labels_raw != "null" else {}
    except json.JSONDecodeError:
        labels = {}
    entry: dict[str, Any] = {
        "image": configured_image,
        "image_id": image_id,
        "repo_digests": sorted(str(value) for value in (digests or [])),
    }
    if container:
        entry["name"] = container
    source_labels = {
        key: privacy_safe_string(str(value))
        for key, value in (labels or {}).items()
        if key.startswith("org.opencontainers.image.")
    }
    if source_labels:
        entry["oci_labels"] = source_labels
    return entry


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("meta_path", type=Path)
    p.add_argument("--create", action="store_true", help="create minimal metadata for a failed run")
    p.add_argument("--algo")
    p.add_argument("--dataset")
    p.add_argument("--sequence")
    p.add_argument("--run-id")
    p.add_argument("--run-type")
    p.add_argument("--artifact", action="append", default=[])
    p.add_argument("--source", action="append", default=[])
    p.add_argument("--binary", action="append", default=[])
    p.add_argument("--param", action="append", default=[])
    p.add_argument("--container")
    p.add_argument("--container-image")
    p.add_argument("--conda-env")
    p.add_argument("--seed")
    p.add_argument("--process-exit-code", type=int, default=0)
    p.add_argument("--accepted-nonzero-exit", action="store_true")
    p.add_argument("--failure-reason")
    p.add_argument("--measurement-mode", choices=MEASUREMENT_MODES)
    p.add_argument("--transport-stats")
    # Backward-compatible aliases while out-of-tree runners migrate.
    p.add_argument("--config")
    p.add_argument("--playback-rate")
    p.add_argument("--extra", action="append", default=[])
    return p


def main() -> int:
    args = parser().parse_args()
    meta_path = args.meta_path.resolve()
    try:
        if meta_path.is_file():
            meta = json.loads(meta_path.read_text())
            if not isinstance(meta, dict):
                raise ValueError("top-level value is not an object")
        elif args.create:
            required = (args.algo, args.dataset, args.sequence, args.run_id, args.run_type)
            if any(value is None for value in required):
                raise ValueError("--create requires --algo, --dataset, --sequence, --run-id, and --run-type")
            meta_path.parent.mkdir(parents=True, exist_ok=True)
            meta = {
                "algo": args.algo,
                "dataset": args.dataset,
                "seq": args.sequence,
                "run_id": parse_scalar(str(args.run_id)),
                "run_type": args.run_type,
                "run_status": "failed",
            }
        else:
            raise FileNotFoundError(meta_path)
    except Exception as exc:
        print(f"[enrich] cannot read {meta_path}: {exc}", file=sys.stderr)
        return 1

    run_dir = meta_path.parent
    try:
        artifacts = list(args.artifact)
        if args.config:
            artifacts.append(f"estimator_config={args.config}")
        artifact_items = [split_assignment(v, "--artifact") for v in artifacts]
        source_items = [split_assignment(v, "--source") for v in args.source]
        binary_items = [split_assignment(v, "--binary") for v in args.binary]
        param_items = [split_assignment(v, "--param") for v in (*args.param, *args.extra)]
        if args.playback_rate:
            param_items.append(("playback_rate", args.playback_rate))

        for category, items in (
            ("artifact", artifact_items), ("source", source_items),
            ("binary", binary_items), ("parameter", param_items),
        ):
            roles = [key for key, _ in items]
            if len(roles) != len(set(roles)):
                raise ValueError(f"duplicate {category} role/key")

        provenance: dict[str, Any] = {
            "artifacts": [artifact_entry(role, path, run_dir, snapshot=True)
                          for role, path in artifact_items],
            "sources": [source_entry(role, path) for role, path in source_items],
            "binaries": [artifact_entry(role, path, run_dir, snapshot=False)
                         for role, path in binary_items],
            "parameters": {
                key: (privacy_safe_string(parsed) if isinstance(parsed := parse_scalar(value), str) else parsed)
                for key, value in param_items
            },
            "workspace": workspace_entry(),
            "runtime": {"python": sys.version.split()[0]},
        }
        if args.seed is not None:
            provenance["parameters"]["seed"] = parse_scalar(args.seed)
        env = {
            key: privacy_safe_string(value)
            for key in TRACKED_ENV
            if (value := os.environ.get(key)) is not None
        }
        if env:
            provenance["environment_overrides"] = env
        if args.conda_env:
            provenance["environment"] = conda_snapshot(args.conda_env, run_dir)
        if args.container and args.container_image:
            raise ValueError("use only one of --container and --container-image")
        if args.container:
            provenance["container"] = container_entry(container=args.container)
        elif args.container_image:
            provenance["container"] = container_entry(image_name=args.container_image)

        exit_code = args.process_exit_code
        meta["process"] = {
            "exit_code": exit_code,
            "accepted_nonzero_exit": bool(args.accepted_nonzero_exit),
            "failure_reason": args.failure_reason,
        }
        meta["execution_stages"] = execution_stages(run_dir)
        meta["provenance_schema"] = 2
        meta["provenance"] = provenance
        if args.measurement_mode:
            meta["measurement_schema"] = 1
            meta["measurements"] = build_measurements(
                meta, run_dir, args.measurement_mode, args.transport_stats,
            )
            # Retain old fields for historical readers, but make their meaning
            # explicit.  New consumers use the measurements object above.
            if "fps" in meta:
                meta["legacy_fps_semantics"] = "output_poses_per_end_to_end_second"
        elif meta.get("run_status") != "failed":
            raise ValueError("successful runs require --measurement-mode")

        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "results"))
        from machine_id import get_machine_id
        meta["machine_id"] = get_machine_id()

        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))
        from _system_info import collect as collect_system
        machine = collect_system()
        machine["collected_at"] = "run"
        meta["machine"] = machine

        tmp = meta_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
        os.replace(tmp, meta_path)
    except Exception as exc:
        print(f"[enrich] failed: {exc}", file=sys.stderr)
        return 1

    print(f"[enrich] provenance schema 2 -> {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
