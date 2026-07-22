# ZED2i Dataset Setup

This repo is a small visual-SLAM benchmark harness. It stores converted datasets,
algorithm configs, run scripts, and evaluation output in one predictable layout.

## Current ZED2i Sequence

The main exported sequence is:

```bash
datasets/zed2i/field1_110426_full_10fps_q90
```

It contains:

- `mav0/cam0/data/*.jpg` and `mav0/cam1/data/*.jpg`: rectified stereo images.
- `times.txt`: camera timestamps in nanoseconds.
- `imu.csv`: raw IMU export.
- `gt_tum.txt`: RTK-derived ground truth using the original 1.86 m lever arm.
- `gt_measured_2p86_interp_tum.txt`: RTK-derived ground truth with the measured 2.86 m GPS-to-camera lever arm.
- `manifest.json`: source bags, topics, camera intrinsics, FPS, and export notes.

The ORB-SLAM3 config for this sequence is:

```bash
configs/orbslam3/zed2i_field1_110426_full_10fps_q90.yaml
```

That file points to `zed2i_full_10fps_q90.yaml`.

## Run ORB-SLAM3

From the repo root:

```bash
cd /home/iman/slam_tests/vslam-benchmark
bash scripts/run/run_orbslam3.sh zed2i field1_110426_full_10fps_q90 2
```

Outputs go to:

```bash
results/zed2i/field1_110426_full_10fps_q90/orbslam3/run2
```

`run1` already contains earlier manual experiment outputs, so `run2` is the
clean first standardized run from this wrapper.

The runner uses the Docker-built ORB-SLAM3 checkout by default:

```bash
/home/iman/slam_tests/orb_slam_test/ORB-SLAM3-ROS2-Docker/ORB_SLAM3
```

Override it if needed:

```bash
ORB_SLAM3_DIR=/path/to/ORB_SLAM3 bash scripts/run/run_orbslam3.sh zed2i field1_110426_full_10fps_q90 1
```

## Evaluate Against RTK

For the current dataset, prefer the measured 2.86 m lever-arm GT:

```bash
cp datasets/zed2i/field1_110426_full_10fps_q90/gt_measured_2p86_interp_tum.txt \
   datasets/zed2i/field1_110426_full_10fps_q90/gt_interp_tum.txt

conda run -n droid_slam python3 scripts/eval/_evaluate_run.py \
  zed2i field1_110426_full_10fps_q90 orbslam3 2
```

## Run Full Benchmark Wrapper

This runs ORB-SLAM3 and then evaluates it:

```bash
cp datasets/zed2i/field1_110426_full_10fps_q90/gt_measured_2p86_interp_tum.txt \
   datasets/zed2i/field1_110426_full_10fps_q90/gt_interp_tum.txt

bash scripts/run/run_benchmark.sh zed2i field1_110426_full_10fps_q90 orbslam3 1
```

The benchmark wrapper starts from `run1`; use it only when you are comfortable
replacing the old manual `run1` output, or move that folder aside first.

## Map Export

The local ORB-SLAM3 stereo example has been patched to export sparse map points
as a PLY file when a run finishes:

```bash
results/zed2i/<sequence>/orbslam3/run<N>/map_points.ply
```

This is an ORB landmark map, not a dense colored reconstruction.

## Quick Preview Dataset

A small 1,000-frame preview sequence exists for fast tests:

```bash
datasets/zed2i/field1_110426_full_10fps_q90_map_preview_1k
```

Run it with the full sequence config:

```bash
ORB_CONFIG=configs/orbslam3/zed2i_full_10fps_q90.yaml \
  bash scripts/run/run_orbslam3.sh zed2i field1_110426_full_10fps_q90_map_preview_1k 1
```
