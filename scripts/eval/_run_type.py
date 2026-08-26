#!/usr/bin/env python3
"""Shared run-type definitions for the evaluation pipeline.

Five run types are supported:

    vo       visual-only / no IMU, no loop closure
             -> results folder:  <repo>/results/vo
             -> CSV file:        <repo>/benchmark-vo.csv

    vo-lc   visual-only + loop closure
             -> results folder:  <repo>/results/vo-lc
             -> CSV file:        <repo>/benchmark-vo-lc.csv

    vio      visual-inertial, no loop closure
             -> results folder:  <repo>/results/vio
             -> CSV file:        <repo>/benchmark-vio.csv

    vio-lc   visual-inertial + loop closure
             -> results folder:  <repo>/results/vio-lc
             -> CSV file:        <repo>/benchmark-vio-lc.csv

    gnss-vio visual-inertial + GNSS fusion (loose or tight)
             -> results folder:  <repo>/results/gnss-vio
             -> CSV file:        <repo>/benchmark-gnss-vio.csv

Usage::

    from _run_type import RunType, resolve

    rt = resolve("vio")
    rt.results_root          # PosixPath('.../results/vio')
    rt.csv_path              # PosixPath('.../benchmark-vio.csv')
    rt.use_imu, rt.use_lc    # True, False
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

RUN_TYPES = ("vo", "vo-lc", "vio", "vio-lc", "gnss-vio")

DATASET_ALIASES = {
    "EuRoC-MAV": "euroc_mav",
    "euroc": "euroc_mav",
    "euroc_mav": "euroc_mav",
}


def canonicalize_dataset(name: str) -> str:
    """Return the repository's canonical identifier for a dataset alias."""
    return DATASET_ALIASES.get(name, name)


@dataclass(frozen=True)
class RunType:
    name: str
    results_root: Path
    csv_path: Path
    use_imu: bool
    use_lc: bool
    use_gnss: bool = False


def resolve(name: str, repo: Path | None = None) -> RunType:
    """Return the RunType for a given short tag."""
    repo = repo or REPO_ROOT
    n = (name or "vo").strip().lower().replace("_", "-")
    if n in ("viol-c", "vio_lc"):
        n = "vio-lc"
    if n in ("vol-c", "vo_lc"):
        n = "vo-lc"
    if n in ("gnssvio", "gnss_vio"):
        n = "gnss-vio"
    if n == "vo":
        return RunType("vo", repo / "results" / "vo", repo / "benchmark-vo.csv",
                       use_imu=False, use_lc=False, use_gnss=False)
    if n == "vo-lc":
        return RunType("vo-lc", repo / "results" / "vo-lc", repo / "benchmark-vo-lc.csv",
                       use_imu=False, use_lc=True, use_gnss=False)
    if n == "vio":
        return RunType("vio", repo / "results" / "vio", repo / "benchmark-vio.csv",
                       use_imu=True, use_lc=False, use_gnss=False)
    if n == "vio-lc":
        return RunType("vio-lc", repo / "results" / "vio-lc", repo / "benchmark-vio-lc.csv",
                       use_imu=True, use_lc=True, use_gnss=False)
    if n == "gnss-vio":
        return RunType("gnss-vio", repo / "results" / "gnss-vio", repo / "benchmark-gnss-vio.csv",
                       use_imu=True, use_lc=False, use_gnss=True)
    raise SystemExit(f"unknown run-type {name!r}. Use one of: {', '.join(RUN_TYPES)}")


def all_types(repo: Path | None = None) -> list[RunType]:
    """Return all five RunType definitions."""
    return [resolve(t, repo) for t in RUN_TYPES]
