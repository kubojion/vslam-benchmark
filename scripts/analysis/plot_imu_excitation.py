#!/usr/bin/env python3
"""Compare useful IMU motion excitation with high-frequency vibration.

The analysis is deliberately independent of estimator output and ground truth.
It reads only the EuRoC-format raw IMU CSV files, interpolates each stream onto
its median-rate time grid, and uses vector norms so the results do not depend
on the sensor-axis convention.

Frequency bands:
  * 0.01--2 Hz: vehicle-scale (operational) motion excitation
  * 10--45 Hz: common high-frequency vibration band

The upper vibration limit is 45 Hz because the slowest stream is approximately
100 Hz. One-second windows are labelled low-excitation when operational gyro
RMS is below 0.02 rad/s and operational acceleration RMS is below 0.10 m/s^2.
These are declared diagnostic thresholds, not an estimator requirement.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, sosfiltfilt, welch


OPERATIONAL_BAND_HZ = (0.01, 2.0)
VIBRATION_BAND_HZ = (10.0, 45.0)
GYRO_EXCITATION_THRESHOLD_RAD_S = 0.02
ACCEL_EXCITATION_THRESHOLD_M_S2 = 0.10


@dataclass(frozen=True)
class Sequence:
    key: str
    label: str
    relative_path: str
    color: str


SEQUENCES = (
    Sequence(
        "rosario_sequence1",
        "Rosario seq1",
        "datasets/rosariov2/sequence1/mav0/imu0/data.csv",
        "#4C78A8",
    ),
    Sequence(
        "rosario_sequence5",
        "Rosario seq5",
        "datasets/rosariov2/sequence5/mav0/imu0/data.csv",
        "#72B7B2",
    ),
    Sequence(
        "horti_strawberry02",
        "Horti str02",
        "datasets/hortimulti/strawberry02/mav0/imu0/data.csv",
        "#59A14F",
    ),
    Sequence(
        "horti_strawberry03",
        "Horti str03",
        "datasets/hortimulti/strawberry03/mav0/imu0/data.csv",
        "#8CD17D",
    ),
    Sequence(
        "zed2i_field1",
        "ZED2i field1",
        "datasets/zed2i/field1_110426_full_10fps_q90/mav0/imu0/data.csv",
        "#E45756",
    ),
)


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "docs" / "generated" / "figures",
    )
    parser.add_argument("--dpi", type=int, default=220)
    return parser.parse_args()


def load_uniform(path: Path) -> tuple[float, float, np.ndarray, np.ndarray]:
    raw = np.loadtxt(path, delimiter=",", comments="#")
    timestamps = raw[:, 0] * 1e-9
    increasing = np.r_[True, np.diff(timestamps) > 0]
    timestamps = timestamps[increasing]
    values = raw[increasing, 1:7]
    if len(values) < 100:
        raise ValueError(f"too few samples in {path}")

    sample_rate = round(1.0 / np.median(np.diff(timestamps)))
    uniform_time = np.arange(timestamps[0], timestamps[-1], 1.0 / sample_rate)
    uniform_values = np.column_stack(
        [np.interp(uniform_time, timestamps, values[:, axis]) for axis in range(6)]
    )
    # Remove constant gyro bias and the fixed gravity vector. Changes in the
    # gravity direction remain and therefore count as motion excitation.
    uniform_values -= np.median(uniform_values, axis=0)
    elapsed = uniform_time - uniform_time[0]
    return float(sample_rate), float(elapsed[-1]), elapsed, uniform_values


def bandpass(values: np.ndarray, sample_rate: float, low: float, high: float) -> np.ndarray:
    nyquist = sample_rate / 2.0
    if not 0 < low < high < nyquist:
        raise ValueError(f"invalid band {low}--{high} Hz at {sample_rate} Hz")
    sections = butter(
        4,
        (low / nyquist, high / nyquist),
        btype="bandpass",
        output="sos",
    )
    return sosfiltfilt(sections, values, axis=0)


def vector_rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.sum(values * values, axis=1))))


def window_rms(values: np.ndarray, sample_rate: float) -> np.ndarray:
    samples_per_window = int(round(sample_rate))
    complete_windows = len(values) // samples_per_window
    windows = values[: complete_windows * samples_per_window].reshape(
        complete_windows, samples_per_window, 3
    )
    return np.sqrt(np.mean(np.sum(windows * windows, axis=2), axis=1))


def analyse(sequence: Sequence, repo_root: Path) -> dict:
    path = repo_root / sequence.relative_path
    sample_rate, duration, _, values = load_uniform(path)
    gyro = values[:, :3]
    accel = values[:, 3:]
    gyro_operational = bandpass(gyro, sample_rate, *OPERATIONAL_BAND_HZ)
    accel_operational = bandpass(accel, sample_rate, *OPERATIONAL_BAND_HZ)
    gyro_vibration = bandpass(gyro, sample_rate, *VIBRATION_BAND_HZ)
    accel_vibration = bandpass(accel, sample_rate, *VIBRATION_BAND_HZ)

    gyro_windows = window_rms(gyro_operational, sample_rate)
    accel_windows = window_rms(accel_operational, sample_rate)
    excited = np.logical_or(
        gyro_windows >= GYRO_EXCITATION_THRESHOLD_RAD_S,
        accel_windows >= ACCEL_EXCITATION_THRESHOLD_M_S2,
    )

    # 16,384 samples gives 0.0122 Hz bins for the 200 Hz streams and
    # 0.0061 Hz bins for ZED2i, while retaining enough Welch segments to avoid
    # the very jagged estimate produced by a 32,768-sample window on str03.
    nperseg = min(len(values), 16384)
    frequencies, gyro_psd_axes = welch(
        gyro,
        fs=sample_rate,
        axis=0,
        nperseg=nperseg,
        detrend="constant",
        scaling="density",
    )
    _, accel_psd_axes = welch(
        accel,
        fs=sample_rate,
        axis=0,
        nperseg=nperseg,
        detrend="constant",
        scaling="density",
    )

    gyro_operational_rms = vector_rms(gyro_operational)
    accel_operational_rms = vector_rms(accel_operational)
    gyro_vibration_rms = vector_rms(gyro_vibration)
    accel_vibration_rms = vector_rms(accel_vibration)
    return {
        "sequence": sequence,
        "path": path,
        "sample_rate_hz": sample_rate,
        "duration_s": duration,
        "gyro_operational_rms_rad_s": gyro_operational_rms,
        "gyro_operational_rms_deg_s": np.degrees(gyro_operational_rms),
        "accel_operational_rms_m_s2": accel_operational_rms,
        "gyro_vibration_rms_rad_s": gyro_vibration_rms,
        "gyro_vibration_rms_deg_s": np.degrees(gyro_vibration_rms),
        "accel_vibration_rms_m_s2": accel_vibration_rms,
        "gyro_vibration_to_operational": gyro_vibration_rms / gyro_operational_rms,
        "accel_vibration_to_operational": accel_vibration_rms / accel_operational_rms,
        "low_excitation_fraction": float(1.0 - np.mean(excited)),
        "gyro_windows_deg_s": np.degrees(gyro_windows),
        "accel_windows_m_s2": accel_windows,
        "frequencies_hz": frequencies,
        "gyro_asd_deg_s_sqrt_hz": np.degrees(
            np.sqrt(np.sum(gyro_psd_axes, axis=1))
        ),
        "accel_asd_m_s2_sqrt_hz": np.sqrt(np.sum(accel_psd_axes, axis=1)),
    }


def style_axis(axis: plt.Axes) -> None:
    axis.grid(True, axis="y", alpha=0.25, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)


def save_summary(results: list[dict], output: Path, dpi: int) -> None:
    labels = [result["sequence"].label for result in results]
    colors = [result["sequence"].color for result in results]
    x = np.arange(len(results))
    panels = (
        (
            "gyro_operational_rms_deg_s",
            "Operational angular excitation",
            "0.01–2 Hz RMS (°/s)",
            "{:.2f}",
        ),
        (
            "accel_operational_rms_m_s2",
            "Operational acceleration excitation",
            "0.01–2 Hz RMS (m/s²)",
            "{:.3f}",
        ),
        (
            "low_excitation_fraction",
            "Low-excitation duration",
            "One-second windows (%)",
            "{:.1f}%",
        ),
    )
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    for axis, (key, title, ylabel, value_format) in zip(axes, panels):
        scale = 100.0 if key == "low_excitation_fraction" else 1.0
        values = [result[key] * scale for result in results]
        bars = axis.bar(x, values, color=colors, edgecolor="white", linewidth=0.8)
        axis.set_title(title, fontweight="bold")
        axis.set_ylabel(ylabel)
        axis.set_xticks(x, labels, rotation=28, ha="right")
        axis.set_ylim(0, max(values) * 1.20)
        style_axis(axis)
        for bar, value in zip(bars, values):
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(values) * 0.025,
                value_format.format(value),
                ha="center",
                va="bottom",
                fontsize=9,
            )
    fig.suptitle(
        "Vehicle-scale IMU excitation: ZED2i is a sustained weak-motion sequence",
        fontsize=14,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(output, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def save_band_comparison(results: list[dict], output: Path, dpi: int) -> None:
    labels = [result["sequence"].label for result in results]
    y = np.arange(len(results))
    width = 0.34
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2), sharey=True)
    specifications = (
        (
            "gyro_operational_rms_deg_s",
            "gyro_vibration_rms_deg_s",
            "Angular-rate RMS (°/s, log scale)",
            "Gyroscope",
        ),
        (
            "accel_operational_rms_m_s2",
            "accel_vibration_rms_m_s2",
            "Acceleration RMS (m/s², log scale)",
            "Accelerometer",
        ),
    )
    for axis, (operational_key, vibration_key, xlabel, title) in zip(axes, specifications):
        operational = [result[operational_key] for result in results]
        vibration = [result[vibration_key] for result in results]
        axis.barh(y - width / 2, operational, width, label="Operational 0.01–2 Hz", color="#4C78A8")
        axis.barh(y + width / 2, vibration, width, label="Vibration 10–45 Hz", color="#F28E2B")
        axis.set_xscale("log")
        axis.set_xlabel(xlabel)
        axis.set_title(title, fontweight="bold")
        axis.grid(True, axis="x", which="both", alpha=0.25)
        axis.set_axisbelow(True)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.legend(fontsize=9)
    axes[0].set_yticks(y, labels)
    axes[0].invert_yaxis()
    fig.suptitle(
        "Useful vehicle motion versus high-frequency platform vibration",
        fontsize=14,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(output, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def empirical_cdf(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ordered = np.sort(values)
    probability = np.arange(1, len(ordered) + 1) / len(ordered)
    return ordered, probability


def save_window_cdf(results: list[dict], output: Path, dpi: int) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.0))
    for result in results:
        sequence = result["sequence"]
        gx, gy = empirical_cdf(result["gyro_windows_deg_s"])
        ax, ay = empirical_cdf(result["accel_windows_m_s2"])
        axes[0].plot(gx, gy * 100, label=sequence.label, color=sequence.color, linewidth=2)
        axes[1].plot(ax, ay * 100, label=sequence.label, color=sequence.color, linewidth=2)

    axes[0].axvline(
        np.degrees(GYRO_EXCITATION_THRESHOLD_RAD_S),
        color="black",
        linestyle="--",
        linewidth=1.2,
        label="Diagnostic threshold",
    )
    axes[1].axvline(
        ACCEL_EXCITATION_THRESHOLD_M_S2,
        color="black",
        linestyle="--",
        linewidth=1.2,
        label="Diagnostic threshold",
    )
    for axis, title, xlabel in (
        (axes[0], "Gyroscope", "One-second operational RMS (°/s)"),
        (axes[1], "Accelerometer", "One-second operational RMS (m/s²)"),
    ):
        axis.set_xscale("log")
        axis.set_ylim(0, 100)
        axis.set_title(title, fontweight="bold")
        axis.set_xlabel(xlabel)
        axis.set_ylabel("Cumulative duration (%)")
        axis.grid(True, which="both", alpha=0.25)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.legend(fontsize=8.5, loc="lower right")
    fig.suptitle(
        "Distribution of vehicle-scale IMU excitation in one-second windows",
        fontsize=14,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(output, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def save_spectra(results: list[dict], output: Path, dpi: int) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.0))
    for result in results:
        sequence = result["sequence"]
        frequencies = result["frequencies_hz"]
        valid = (frequencies >= 0.01) & (frequencies <= 45.0)
        axes[0].loglog(
            frequencies[valid],
            result["gyro_asd_deg_s_sqrt_hz"][valid],
            color=sequence.color,
            linewidth=1.45,
            label=sequence.label,
        )
        axes[1].loglog(
            frequencies[valid],
            result["accel_asd_m_s2_sqrt_hz"][valid],
            color=sequence.color,
            linewidth=1.45,
            label=sequence.label,
        )
    for axis, title, ylabel in (
        (axes[0], "Gyroscope", "Vector ASD (°/s/√Hz)"),
        (axes[1], "Accelerometer", "Vector ASD (m/s²/√Hz)"),
    ):
        axis.axvspan(*OPERATIONAL_BAND_HZ, color="#4C78A8", alpha=0.08)
        axis.axvspan(*VIBRATION_BAND_HZ, color="#F28E2B", alpha=0.08)
        axis.set_xlim(0.01, 45)
        # Log axes normally label powers of ten only, which made the right edge
        # look like 10 Hz even though the data continued to 45 Hz. Show both
        # analysis-band boundaries and the true upper limit explicitly.
        axis.set_xticks((0.01, 0.1, 1, 2, 10, 45))
        axis.set_xticklabels(("0.01", "0.1", "1", "2", "10", "45"))
        axis.set_title(title, fontweight="bold")
        axis.set_xlabel("Frequency (Hz; plotted through 45 Hz)")
        axis.set_ylabel(ylabel)
        axis.grid(True, which="both", alpha=0.22)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.legend(fontsize=8.5)
    fig.suptitle(
        "IMU amplitude spectra (blue band: operational motion; orange band: vibration)",
        fontsize=14,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(output, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def save_metrics(results: list[dict], output: Path) -> None:
    columns = (
        "sequence",
        "source",
        "sample_rate_hz",
        "duration_s",
        "gyro_operational_rms_deg_s",
        "accel_operational_rms_m_s2",
        "gyro_vibration_rms_deg_s",
        "accel_vibration_rms_m_s2",
        "gyro_vibration_to_operational",
        "accel_vibration_to_operational",
        "low_excitation_pct",
    )
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "sequence": result["sequence"].label,
                    "source": result["sequence"].relative_path,
                    "sample_rate_hz": f'{result["sample_rate_hz"]:.3f}',
                    "duration_s": f'{result["duration_s"]:.3f}',
                    "gyro_operational_rms_deg_s": f'{result["gyro_operational_rms_deg_s"]:.6f}',
                    "accel_operational_rms_m_s2": f'{result["accel_operational_rms_m_s2"]:.6f}',
                    "gyro_vibration_rms_deg_s": f'{result["gyro_vibration_rms_deg_s"]:.6f}',
                    "accel_vibration_rms_m_s2": f'{result["accel_vibration_rms_m_s2"]:.6f}',
                    "gyro_vibration_to_operational": f'{result["gyro_vibration_to_operational"]:.6f}',
                    "accel_vibration_to_operational": f'{result["accel_vibration_to_operational"]:.6f}',
                    "low_excitation_pct": f'{100 * result["low_excitation_fraction"]:.6f}',
                }
            )


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    results = [analyse(sequence, repo_root) for sequence in SEQUENCES]
    outputs = {
        "summary": output_dir / "fig_imu_signal_excitation_summary.png",
        "bands": output_dir / "fig_imu_signal_excitation_bands.png",
        "cdf": output_dir / "fig_imu_signal_excitation_cdf.png",
        "spectra": output_dir / "fig_imu_signal_excitation_spectra.png",
        "metrics": output_dir / "imu_signal_excitation_metrics.csv",
    }
    save_summary(results, outputs["summary"], args.dpi)
    save_band_comparison(results, outputs["bands"], args.dpi)
    save_window_cdf(results, outputs["cdf"], args.dpi)
    save_spectra(results, outputs["spectra"], args.dpi)
    save_metrics(results, outputs["metrics"])
    for output in outputs.values():
        print(output)


if __name__ == "__main__":
    main()
