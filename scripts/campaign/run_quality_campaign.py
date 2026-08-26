#!/usr/bin/env python3
"""Validate and run the serial N=5 quality campaign.

The committed JSON file is the protocol.  Runtime state and logs stay under
logs/server-campaign/ and make an interrupted campaign safely resumable.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any


REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "configs/campaigns/quality-final.json"
RUN_TYPES = ("vo", "vo-lc", "vio", "vio-lc", "gnss-vio")
EXCLUDED = {"droidslam", "megasam", "mast3r_slam"}

NATIVE_BINARIES = {
    "orbslam3": (
        "src/ORB_SLAM3/Examples/Stereo/stereo_euroc",
        "src/ORB_SLAM3/Examples/Stereo-Inertial/stereo_inertial_euroc",
    ),
    "okvis2": ("src/okvis2/build/okvis_app_synchronous",),
    "okvis2x": ("src/okvis2x/build/okvis_app_synchronous",),
}
PATH_BINARIES = {"basalt": "basalt_vio"}
CONDA_ENVS = {"dpvo": "dpvo", "macvo": "macvo"}
CONTAINERS = {
    "airslam": "air_slam",
    "ov2slam": "ov2slam",
    "voxel_svio": "voxel_svio",
    "cifasis_gnss_si": "cifasis_gnss_si",
    "vins_fusion_gps": "vins_fusion",
}
HOST_ROS_PACKAGES = {
    "openvins_gps": "robot_localization",
    "rtabmap_gps": "rtabmap_ros",
}


def run_output(command: list[str], *, check: bool = False) -> str:
    result = subprocess.run(command, cwd=REPO, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if check and result.returncode:
        raise RuntimeError(f"{' '.join(command)} failed:\n{result.stdout.rstrip()}")
    # Preserve leading whitespace: Git porcelain uses the first two columns as
    # status fields. Trimming the first line would corrupt its path parsing.
    return result.stdout.rstrip()


def load_manifest(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    doc = json.loads(raw)
    return doc, hashlib.sha256(raw).hexdigest()


def expand_cells(doc: dict[str, Any]) -> list[dict[str, str]]:
    cells: list[dict[str, str]] = []
    for run_type in RUN_TYPES:
        sequences = doc["gnss_sequences"] if run_type == "gnss-vio" else doc["sequences"]
        for item in sequences:
            for algorithm in doc["tables"][run_type]:
                cells.append({
                    "run_type": run_type,
                    "dataset": item["dataset"],
                    "sequence": item["sequence"],
                    "algorithm": algorithm,
                })
    return cells


def cell_key(cell: dict[str, str]) -> str:
    return "/".join(cell[k] for k in ("run_type", "dataset", "sequence", "algorithm"))


def run_type_requires_imu(run_type: str) -> bool:
    return run_type in {"vio", "vio-lc", "gnss-vio"}


def source_fingerprint() -> str:
    """Fingerprint tracked benchmark sources, including dirty nested submodules."""
    h = hashlib.sha256()
    h.update(run_output(["git", "rev-parse", "HEAD"], check=True).encode())
    h.update(run_output(["git", "submodule", "status", "--recursive"], check=True).encode())
    h.update(subprocess.run(
        ["git", "diff", "--binary", "HEAD", "--", "scripts", "configs"],
        cwd=REPO, stdout=subprocess.PIPE, check=True).stdout)
    for path in ("src/okvis2", "src/okvis2x"):
        h.update(path.encode())
        h.update(run_output(["git", "-C", path, "rev-parse", "HEAD"], check=True).encode())
        h.update(subprocess.run(
            ["git", "-C", path, "diff", "--binary", "HEAD"],
            cwd=REPO, stdout=subprocess.PIPE, check=True).stdout)
        for nested in ("external/DBoW2", "external/opengv"):
            nested_path = f"{path}/{nested}"
            h.update(nested_path.encode())
            h.update(subprocess.run(
                ["git", "-C", nested_path, "diff", "--binary", "HEAD"],
                cwd=REPO, stdout=subprocess.PIPE, check=True).stdout)
    return h.hexdigest()


def validate_manifest(doc: dict[str, Any], cells: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if doc.get("schema_version") != 1:
        errors.append("manifest schema_version must be 1")
    if not isinstance(doc.get("repeats"), int) or doc["repeats"] < 1:
        errors.append("manifest repeats must be a positive integer")
    if set(doc.get("tables", {})) != set(RUN_TYPES):
        errors.append(f"manifest tables must be exactly: {', '.join(RUN_TYPES)}")
    algorithms = {a for algos in doc.get("tables", {}).values() for a in algos}
    prohibited = algorithms & EXCLUDED
    if prohibited:
        errors.append(f"excluded algorithms present: {', '.join(sorted(prohibited))}")
    keys = [cell_key(cell) for cell in cells]
    if len(keys) != len(set(keys)):
        errors.append("manifest expands to duplicate cells")
    if len(cells) != doc.get("expected_cells"):
        errors.append(f"expected_cells={doc.get('expected_cells')} but expansion has {len(cells)}")
    executions = len(cells) * doc.get("repeats", 0)
    if executions != doc.get("expected_executions"):
        errors.append(
            f"expected_executions={doc.get('expected_executions')} but expansion has {executions}")
    return errors


def airslam_engines(doc: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for item in doc["sequences"]:
        config = REPO / "configs/airslam" / f"{item['dataset']}_vo.yaml"
        if not config.is_file():
            continue
        for line in config.read_text().splitlines():
            if line.strip().startswith("engine_file:"):
                names.add(line.split(":", 1)[1].strip().strip('"\''))
                break
    return names


def config_groups(cell: dict[str, str]) -> list[tuple[str, tuple[Path, ...]]]:
    """Return required configuration groups; one existing path per group is enough."""
    dataset, sequence = cell["dataset"], cell["sequence"]
    algorithm, run_type = cell["algorithm"], cell["run_type"]
    groups: list[tuple[str, tuple[Path, ...]]] = []

    def require(label: str, *paths: str) -> None:
        groups.append((label, tuple(REPO / path for path in paths)))

    mode = run_type.replace("-", "_")
    if algorithm == "orbslam3":
        suffix = {
            "vo": "stereo", "vo-lc": "stereo_lc",
            "vio": "stereo_inertial", "vio-lc": "stereo_inertial_lc",
        }[run_type]
        paths = [f"configs/orbslam3/{dataset}_{suffix}.yaml"]
        if dataset == "zed2i" and run_type.startswith("vio"):
            paths.append(f"configs/orbslam3/{dataset}_{sequence}_stereo_inertial.yaml")
        require("ORB-SLAM3 sensor profile", *paths)
        require("ORB-SLAM3 vocabulary", "src/ORB_SLAM3/Vocabulary/ORBvoc.txt")
    elif algorithm == "okvis2":
        paths = [f"configs/okvis2/{dataset}_{sequence}_{mode}.yaml"]
        if run_type == "vio-lc":
            paths.append(f"configs/okvis2/{dataset}_{sequence}_vio.yaml")
        require("OKVIS2 profile", *paths)
    elif algorithm == "okvis2x":
        require("OKVIS2-X profile", f"configs/okvis2x/{dataset}_{sequence}_{mode}.yaml")
        require("OKVIS2-X vocabulary", "src/okvis2x/build/small_voc.yml.gz")
    elif algorithm == "airslam":
        tag = {"vo": "vo", "vo-lc": "vo_lc", "vio": "vio", "vio-lc": "vio_slam"}[run_type]
        paths = [f"configs/airslam/{dataset}_{tag}.yaml"]
        if run_type == "vio-lc":
            paths.append(f"configs/airslam/{dataset}_vio.yaml")
        require("AirSLAM odometry profile", *paths)
        if run_type.endswith("lc"):
            require("AirSLAM map-refinement profile", f"configs/airslam/{dataset}_mr.yaml")
        camera_mode = "vio" if run_type.startswith("vio") else "vo"
        require("AirSLAM camera profile",
                f"configs/airslam/{dataset}_camera_{camera_mode}.yaml",
                f"configs/airslam/{dataset}_camera.yaml")
    elif algorithm == "basalt":
        require("Basalt calibration", f"configs/basalt/{dataset}_calib.json")
        require("Basalt estimator profile", f"configs/basalt/{run_type}_config.json")
    elif algorithm == "ov2slam":
        require("OV2SLAM profile",
                f"configs/ov2slam/{dataset}_{sequence}_{mode}.yaml",
                f"configs/ov2slam/{dataset}_{mode}.yaml")
    elif algorithm == "dpvo":
        require("DPVO calibration", f"configs/dpvo/{dataset}.txt")
        require("DPVO estimator profile", "src/DPVO/config/default.yaml")
        require("DPVO model", "src/DPVO/dpvo.pth")
    elif algorithm == "macvo":
        require("MAC-VO dataset profile", f"configs/macvo/{dataset}_{sequence}.yaml")
        require("MAC-VO estimator profile", "src/MAC-VO/Config/Experiment/MACVO/MACVO_Performant.yaml")
        require("MAC-VO frontend model", "src/MAC-VO/Model/MACVO_FrontendCov.pth")
        require("MAC-VO pose model", "src/MAC-VO/Model/MACVO_posenet.pkl")
    elif algorithm in {"openvins", "openvins_gps"}:
        require("OpenVINS estimator profile", f"configs/openvins/{dataset}/estimator_config.yaml")
        require("OpenVINS camera/IMU chain", f"configs/openvins/{dataset}/kalibr_imucam_chain.yaml")
        require("OpenVINS IMU profile", f"configs/openvins/{dataset}/kalibr_imu_chain.yaml")
        if algorithm == "openvins_gps":
            require("OpenVINS GPS EKF profile", "configs/robot_loc_openvins/ekf_gps.yaml")
            require("OpenVINS navsat profile", "configs/robot_loc_openvins/navsat.yaml")
    elif algorithm == "voxel_svio":
        require("Voxel-SVIO profile",
                f"configs/voxel_svio/{dataset}_{sequence}.yaml",
                f"configs/voxel_svio/{dataset}.yaml")
    elif algorithm == "cifasis_gnss_si":
        require("CIFASIS GNSS-SI profile",
                f"configs/cifasis_gnss_si/{dataset}_{sequence}.yaml",
                f"configs/cifasis_gnss_si/{dataset}.yaml")
    elif algorithm == "rtabmap_gps":
        require("RTAB-Map GPS profile", "configs/rtabmap_gps/benchmark.ini")
    elif algorithm == "vins_fusion_gps":
        require("VINS-Fusion profile",
                f"configs/vins_fusion/{dataset}_{sequence}.yaml",
                f"configs/vins_fusion/{dataset}.yaml")
        require("VINS-Fusion cam0 calibration", f"configs/vins_fusion/{dataset}_cam0.yaml")
        require("VINS-Fusion cam1 calibration", f"configs/vins_fusion/{dataset}_cam1.yaml")
    return groups


def preflight(doc: dict[str, Any], cells: list[dict[str, str]], *, require_engines: bool) -> list[str]:
    errors = validate_manifest(doc, cells)
    warnings: list[str] = []
    algorithms = sorted({c["algorithm"] for c in cells})

    for cell in cells:
        runner = REPO / "scripts/run" / f"run_{cell['algorithm']}.sh"
        dataset = REPO / "datasets" / cell["dataset"] / cell["sequence"]
        if not runner.is_file():
            errors.append(f"missing runner: {runner.relative_to(REPO)}")
        if not dataset.is_dir():
            errors.append(f"missing dataset: {dataset.relative_to(REPO)}")
            continue
        for label, candidates in config_groups(cell):
            if not any(path.is_file() and path.stat().st_size > 0 for path in candidates):
                rendered = " or ".join(str(path.relative_to(REPO)) for path in candidates)
                errors.append(f"{cell_key(cell)}: missing {label}: {rendered}")
        for camera in ("cam0", "cam1"):
            image_dir = dataset / "mav0" / camera / "data"
            if not image_dir.is_dir():
                errors.append(f"{cell_key(cell)}: missing image directory {image_dir.relative_to(REPO)}")
        if not (dataset / "times.txt").is_file():
            errors.append(f"{cell_key(cell)}: missing {dataset.relative_to(REPO)}/times.txt")
        if run_type_requires_imu(cell["run_type"]) and not (dataset / "mav0/imu0/data.csv").is_file():
            errors.append(f"{cell_key(cell)}: missing IMU data")
        if cell["run_type"] == "gnss-vio" and not (dataset / "gps.csv").is_file():
            errors.append(f"{cell_key(cell)}: missing GPS data")

    for algorithm in algorithms:
        for relpath in NATIVE_BINARIES.get(algorithm, ()):
            path = REPO / relpath
            if not path.is_file() or not os.access(path, os.X_OK):
                errors.append(f"missing executable for {algorithm}: {relpath}")
        command = PATH_BINARIES.get(algorithm)
        if command and shutil.which(command) is None:
            errors.append(f"missing executable on PATH for {algorithm}: {command}")

    if any(a in CONDA_ENVS for a in algorithms):
        if shutil.which("conda") is None:
            errors.append("conda is not on PATH")
        else:
            env_doc = json.loads(run_output(["conda", "env", "list", "--json"], check=True))
            envs = {Path(path).name for path in env_doc["envs"]}
            for algorithm, env in CONDA_ENVS.items():
                if algorithm in algorithms and env not in envs:
                    errors.append(f"missing conda environment for {algorithm}: {env}")

    if any(a in CONTAINERS for a in algorithms):
        if shutil.which("docker") is None:
            errors.append("docker is not on PATH")
        else:
            running = set(run_output(["docker", "ps", "--format", "{{.Names}}"], check=True).splitlines())
            for algorithm, container in CONTAINERS.items():
                if algorithm in algorithms and container not in running:
                    errors.append(f"container is not running for {algorithm}: {container}")

    if any(a in {"openvins", "openvins_gps"} for a in algorithms):
        images = run_output(["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}"], check=True)
        if "openvins:humble" not in set(images.splitlines()):
            errors.append("Docker image is missing: openvins:humble")

    if any(a in HOST_ROS_PACKAGES for a in algorithms):
        if not (Path("/opt/ros/humble") / "setup.bash").is_file():
            errors.append("host ROS 2 Humble is missing")
        else:
            package_output = run_output([
                "bash", "-lc", "source /opt/ros/humble/setup.bash && ros2 pkg list"
            ])
            packages = set(package_output.splitlines())
            for algorithm, package in HOST_ROS_PACKAGES.items():
                if algorithm in algorithms and package not in packages:
                    errors.append(f"ROS package is missing for {algorithm}: {package}")

    if any(a in {"orbslam3", "okvis2", "okvis2x"} for a in algorithms):
        if shutil.which("xvfb-run") is None or shutil.which("xdpyinfo") is None:
            errors.append("xvfb-run and xdpyinfo are required for headless native estimators")
        else:
            display_test = subprocess.run(
                ["xvfb-run", "-a", "sh", "-c", "xdpyinfo >/dev/null"],
                cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            if display_test.returncode:
                errors.append(f"headless Xvfb test failed: {display_test.stdout.strip()}")

    if require_engines and "airslam" in algorithms:
        for name in sorted(airslam_engines(doc)):
            path = REPO / "src/airslam/output" / name
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f"missing AirSLAM TensorRT engine: {path.relative_to(REPO)}")

    usage = shutil.disk_usage(REPO)
    if usage.free < 500 * 1024**3:
        errors.append(f"less than 500 GiB free under {REPO}: {usage.free / 1024**3:.1f} GiB")

    if shutil.which("nvidia-smi") is None:
        errors.append("nvidia-smi is unavailable")
    else:
        query = run_output([
            "nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"
        ])
        if "RTX 4090" not in query:
            warnings.append(f"campaign was prepared for RTX 4090; detected: {query or 'no GPU'}")

    # These installer-produced CMake changes are required by the built OKVIS2
    # binaries. They are fingerprinted above, so a resumed campaign cannot
    # silently switch source even though the nested submodules are dirty.
    status = run_output(["git", "status", "--porcelain", "--untracked-files=no"])
    unexpected = []
    for line in status.splitlines():
        path = line[3:]
        if path not in {"src/okvis2", "src/okvis2x"}:
            unexpected.append(line)
    if unexpected:
        errors.append("unexpected tracked worktree changes:\n  " + "\n  ".join(unexpected))
    expected_okvis_paths = {"external/DBoW2", "external/opengv"}
    for submodule in ("src/okvis2", "src/okvis2x"):
        nested_paths = {
            line[3:]
            for line in run_output([
                "git", "-C", submodule, "status", "--porcelain", "--untracked-files=no"
            ]).splitlines()
        }
        if nested_paths != expected_okvis_paths:
            errors.append(
                f"unexpected tracked changes inside {submodule}: "
                f"{sorted(nested_paths) or ['clean; expected prerequisite patches']}")
        for dependency in ("external/DBoW2", "external/opengv"):
            dependency_status = run_output([
                "git", "-C", f"{submodule}/{dependency}",
                "status", "--porcelain", "--untracked-files=no",
            ]).splitlines()
            dependency_paths = [line[3:] for line in dependency_status]
            if dependency_paths != ["CMakeLists.txt"]:
                errors.append(
                    f"unexpected tracked changes inside {submodule}/{dependency}: "
                    f"{dependency_paths or ['clean; expected prerequisite patch']}")
    if status:
        warnings.append("OKVIS2 build-prerequisite patches make nested submodules dirty; source is fingerprinted")

    for warning in warnings:
        print(f"[preflight] WARNING: {warning}")
    return sorted(set(errors))


def idle_guard(max_load: float, min_free_vram_mib: int) -> None:
    while True:
        load = os.getloadavg()[0]
        gpu = run_output([
            "nvidia-smi", "--query-gpu=memory.free,utilization.gpu",
            "--format=csv,noheader,nounits",
        ])
        try:
            free_s, util_s = gpu.splitlines()[0].split(",")
            free_mib, util = int(free_s.strip()), int(util_s.strip())
        except (ValueError, IndexError):
            raise RuntimeError(f"cannot parse nvidia-smi idle state: {gpu}")
        if load <= max_load and free_mib >= min_free_vram_mib and util <= 10:
            return
        print(f"[guard] waiting: load={load:.2f}/{max_load:.2f}, "
              f"VRAM free={free_mib}/{min_free_vram_mib} MiB, GPU={util}%", flush=True)
        time.sleep(30)


def save_state(path: Path, state: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def execute(doc: dict[str, Any], manifest_hash: str, cells: list[dict[str, str]], args: argparse.Namespace) -> int:
    campaign_dir = REPO / "logs/server-campaign" / doc["campaign_id"]
    campaign_dir.mkdir(parents=True, exist_ok=True)
    lock_file = (campaign_dir / "campaign.lock").open("w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("ERROR: this campaign is already running", file=sys.stderr)
        return 2

    fingerprint = source_fingerprint()
    state_path = campaign_dir / "state.json"
    if state_path.is_file():
        state = json.loads(state_path.read_text())
        if state.get("manifest_sha256") != manifest_hash:
            print("ERROR: manifest changed since campaign state was created", file=sys.stderr)
            return 2
        if state.get("source_fingerprint") != fingerprint:
            print("ERROR: tracked campaign source changed; archive state before starting a new campaign", file=sys.stderr)
            return 2
    else:
        state = {
            "campaign_id": doc["campaign_id"],
            "manifest_sha256": manifest_hash,
            "source_fingerprint": fingerprint,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "cells": {},
        }
        save_state(state_path, state)

    repeats = doc["repeats"]
    for index, cell in enumerate(cells, 1):
        key = cell_key(cell)
        if state["cells"].get(key, {}).get("status") == "ok":
            print(f"[{index:03d}/{len(cells)}] skip completed {key}", flush=True)
            continue
        idle_guard(args.max_load, args.min_free_vram_mib)
        log_path = campaign_dir / f"{index:03d}_{key.replace('/', '__')}.log"
        command = [
            "bash", str(REPO / "scripts/run/run_benchmark.sh"),
            cell["dataset"], cell["sequence"], cell["algorithm"],
            str(repeats), cell["run_type"],
        ]
        entry = {**cell, "status": "running", "attempts": [],
                 "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        state["cells"][key] = entry
        save_state(state_path, state)

        rc = 1
        for attempt in range(1, args.retry + 2):
            print(f"[{index:03d}/{len(cells)}] {key} attempt {attempt}", flush=True)
            started = time.time()
            with log_path.open("a") as log:
                log.write(f"\n===== attempt {attempt} {' '.join(command)} =====\n")
                log.flush()
                process = subprocess.Popen(command, cwd=REPO, text=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           bufsize=1)
                assert process.stdout is not None
                for line in process.stdout:
                    sys.stdout.write(line)
                    log.write(line)
                rc = process.wait()
            entry["attempts"].append({
                "attempt": attempt,
                "exit_code": rc,
                "duration_s": round(time.time() - started, 3),
            })
            save_state(state_path, state)
            if rc == 0:
                break

        entry["status"] = "ok" if rc == 0 else "failed"
        entry["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        save_state(state_path, state)
        if rc != 0 and not args.continue_on_failure:
            print(f"ERROR: campaign stopped at {key}; resume after fixing it", file=sys.stderr)
            return rc

    if any(value.get("status") != "ok" for value in state["cells"].values()) or \
            len(state["cells"]) != len(cells):
        print("ERROR: campaign has incomplete or failed cells; finalization skipped", file=sys.stderr)
        return 1

    final_commands = [
        ["conda", "run", "-n", "macvo", "python3", "scripts/eval/build_benchmark_csv.py", "all"],
        ["conda", "run", "-n", "macvo", "python3", "scripts/eval/make_report_tables.py", "--check"],
        ["conda", "run", "-n", "macvo", "python3", "scripts/eval/verify_claims.py"],
    ]
    for command in final_commands:
        print(f"[finalize] {' '.join(command)}", flush=True)
        if subprocess.run(command, cwd=REPO).returncode:
            return 1
    state["status"] = "complete"
    state["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    save_state(state_path, state)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--list", action="store_true", help="print the expanded cells")
    parser.add_argument("--preflight", action="store_true", help="validate without running (default)")
    parser.add_argument("--run", action="store_true", help="execute/resume the campaign")
    parser.add_argument("--retry", type=int, default=1, help="retries after a failed cell (default: 1)")
    parser.add_argument("--continue-on-failure", action="store_true")
    parser.add_argument("--max-load", type=float, default=max(4.0, (os.cpu_count() or 1) / 4))
    parser.add_argument("--min-free-vram-mib", type=int, default=20000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.retry < 0:
        print("ERROR: --retry cannot be negative", file=sys.stderr)
        return 2
    if args.run and (args.list or args.preflight):
        print("ERROR: --run cannot be combined with --list or --preflight", file=sys.stderr)
        return 2
    doc, manifest_hash = load_manifest(args.manifest.resolve())
    cells = expand_cells(doc)
    if args.list:
        for index, cell in enumerate(cells, 1):
            print(f"{index:03d} {cell_key(cell)} N={doc['repeats']}")
        print(f"{len(cells)} cells, {len(cells) * doc['repeats']} executions")
        return 0

    errors = preflight(doc, cells, require_engines=True)
    if errors:
        for error in errors:
            print(f"[preflight] ERROR: {error}", file=sys.stderr)
        return 2
    print(f"[preflight] OK: {len(cells)} cells, {len(cells) * doc['repeats']} executions")
    if not args.run:
        return 0
    return execute(doc, manifest_hash, cells, args)


if __name__ == "__main__":
    raise SystemExit(main())
