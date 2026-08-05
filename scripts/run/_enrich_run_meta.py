#!/usr/bin/env python3
"""Add provenance fields to an existing run_meta.json (2026-08-05, audit fix).

Usage (called by every runner right after it writes run_meta.json):
    python3 _enrich_run_meta.py <run_meta.json> [--config PATH] [--container NAME]
                                [--playback-rate R] [--extra key=value ...]

Adds:
  provenance:
    config_path / config_sha256      the effective config file (if given)
    playback_rate                    data-player rate (ROS-fed algorithms)
    container_image                  docker image ID (if --container given)
    env_overrides                    any VSLAM-relevant env vars that were set
    git_describe                     workspace state at run time
  machine:                           run-host hardware (authoritative — the
                                     evaluator preserves this over eval-host)

Why: run_meta.json previously recorded neither the config nor the playback
rate nor the container image, so e.g. the OV2SLAM half-speed accommodation and
config-file env overrides (ORBSLAM3_CONFIG, ...) were invisible in the
artifacts. Machine identity was collected at EVALUATION time, which
mis-attributes hardware when a run is re-evaluated on another laptop.
"""
from __future__ import annotations
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

TRACKED_ENV = [
    "ORBSLAM3_CONFIG", "OKVIS2_CONFIG", "OKVIS2X_CONFIG", "OV2SLAM_CONFIG",
    "OPENVINS_RATE", "OV2SLAM_PLAYBACK_RATE", "DPVO_STRIDE", "DPVO_SKIP",
    "GT_OVERRIDE", "AIRSLAM_LAUNCH",
]


def sha256_file(p: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1
    meta_path = Path(sys.argv[1])
    args = sys.argv[2:]

    def opt(name):
        return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else None

    try:
        meta = json.loads(meta_path.read_text())
    except Exception as e:
        print(f"[enrich] cannot read {meta_path}: {e}", file=sys.stderr)
        return 1

    prov: dict = {}
    cfg = opt("--config")
    if cfg:
        cfg_p = Path(cfg)
        prov["config_path"] = str(cfg_p)
        prov["config_sha256"] = sha256_file(cfg_p)
    rate = opt("--playback-rate")
    if rate:
        prov["playback_rate"] = float(rate)
    container = opt("--container")
    if container:
        try:
            img = subprocess.run(["docker", "inspect", "--format", "{{.Image}}",
                                  container], capture_output=True, text=True,
                                 timeout=10).stdout.strip()
            prov["container"] = container
            prov["container_image"] = img or None
        except Exception:
            prov["container"] = container
    for a in args:
        if "=" in a and not a.startswith("--"):
            k, v = a.split("=", 1)
            prov.setdefault("extra", {})[k] = v
    env = {k: v for k in TRACKED_ENV if (v := os.environ.get(k)) is not None}
    if env:
        prov["env_overrides"] = env
    try:
        prov["git_describe"] = subprocess.run(
            ["git", "-C", str(meta_path.resolve().parents[0]), "describe",
             "--always", "--dirty"], capture_output=True, text=True,
            timeout=10).stdout.strip() or None
    except Exception:
        pass

    meta["provenance"] = prov

    # Run-host machine identity, captured AT RUN TIME (authoritative).
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))
        from _system_info import collect as _collect
        m = _collect()
        m["collected_at"] = "run"
        meta["machine"] = m
    except Exception as e:
        meta.setdefault("machine", {})["error"] = str(e)

    meta_path.write_text(json.dumps(meta, indent=1))
    print(f"[enrich] provenance added -> {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
