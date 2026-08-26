#!/usr/bin/env python3
"""Algorithm-specific provenance requirements for newly produced runs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Requirement:
    artifacts: frozenset[str] = field(default_factory=frozenset)
    sources: frozenset[str] = field(default_factory=lambda: frozenset({"algorithm"}))
    binaries: frozenset[str] = field(default_factory=frozenset)
    parameters: frozenset[str] = field(default_factory=frozenset)
    environment: bool = False
    container: bool = False


REQUIREMENTS: dict[str, Requirement] = {
    "airslam": Requirement(
        artifacts=frozenset({"camera_config", "odometry_config", "tensorrt_engine"}),
        parameters=frozenset({"use_imu", "use_lc", "playback_rate"}), container=True,
    ),
    "basalt": Requirement(
        artifacts=frozenset({"camera_calibration", "estimator_config"}),
        sources=frozenset(), binaries=frozenset({"estimator"}),
        parameters=frozenset({"use_imu", "num_threads", "playback_rate"}),
    ),
    "cifasis_gnss_si": Requirement(
        artifacts=frozenset({"estimator_config", "vocabulary"}),
        parameters=frozenset({"gps_cov_xy", "gps_cov_z", "playback_rate", "gnss_variant"}), container=True,
    ),
    "dpvo": Requirement(
        artifacts=frozenset({"camera_calibration", "algorithm_config", "model"}),
        parameters=frozenset({"stride", "skip", "loop_closure", "seed"}), environment=True,
    ),
    "droidslam": Requirement(
        artifacts=frozenset({"camera_calibration", "model"}),
        parameters=frozenset({"stereo", "stride", "buffer", "filter_threshold", "frontend_window", "skip_backend", "extra_args"}),
        environment=True,
    ),
    "macvo": Requirement(
        artifacts=frozenset({"odometry_config", "dataset_config", "effective_dataset_config", "model"}),
        parameters=frozenset({"use_rerun_viewer", "matmul_precision"}), environment=True,
    ),
    "mast3r_slam": Requirement(
        artifacts=frozenset({"algorithm_config", "camera_calibration", "base_config"}),
        parameters=frozenset({"loop_closure", "visualization"}), environment=True,
    ),
    "megasam": Requirement(
        artifacts=frozenset({"megasam_model", "depth_anything_model"}),
        parameters=frozenset({"unidepth_model", "visualization"}), environment=True,
    ),
    "okvis2": Requirement(
        artifacts=frozenset({"estimator_config"}), binaries=frozenset({"estimator"}),
        parameters=frozenset({"use_imu", "use_lc", "matching_threads"}),
    ),
    "okvis2x": Requirement(
        artifacts=frozenset({"estimator_config", "vocabulary"}), binaries=frozenset({"estimator"}),
        parameters=frozenset({"use_imu", "use_lc", "use_gnss"}),
    ),
    "openvins": Requirement(
        artifacts=frozenset({"estimator_config", "imu_calibration", "camera_imu_calibration"}),
        parameters=frozenset({"playback_rate"}), container=True,
    ),
    "openvins_gps": Requirement(
        artifacts=frozenset({"estimator_config", "imu_calibration", "camera_imu_calibration", "ekf_config", "navsat_config"}),
        parameters=frozenset({"playback_rate", "gnss_variant"}), container=True,
    ),
    "orbslam3": Requirement(
        artifacts=frozenset({"estimator_config", "vocabulary"}), binaries=frozenset({"estimator"}),
        parameters=frozenset({"use_imu", "use_lc", "pacing_policy"}),
    ),
    "ov2slam": Requirement(
        artifacts=frozenset({"estimator_config"}),
        parameters=frozenset({"use_lc", "playback_rate", "finish_timeout"}), container=True,
    ),
    "rtabmap_gps": Requirement(
        artifacts=frozenset({"estimator_config"}), sources=frozenset(),
        parameters=frozenset({"playback_rate", "gnss_variant", "ros_package"}),
    ),
    "vins_fusion_gps": Requirement(
        artifacts=frozenset({"estimator_config", "camera0_config", "camera1_config"}),
        parameters=frozenset({"playback_rate", "gnss_variant"}), container=True,
    ),
    "voxel_svio": Requirement(
        artifacts=frozenset({"estimator_config"}),
        parameters=frozenset({"playback_rate"}), container=True,
    ),
}


def requirement_for(algorithm: str, run_type: str) -> Requirement | None:
    base = REQUIREMENTS.get(algorithm)
    if base is None:
        return None
    if algorithm == "airslam" and run_type in {"vo-lc", "vio-lc"}:
        return Requirement(
            artifacts=base.artifacts | {"map_refinement_config"},
            sources=base.sources, binaries=base.binaries, parameters=base.parameters,
            environment=base.environment, container=base.container,
        )
    return base
