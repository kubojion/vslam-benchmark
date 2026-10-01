# ZED2i Dataset Setup

> **Status note 2026-10-01:** camera-optical/IMU frame corrections and the corrected N=1 cohort are documented in [ZED IMU extrinsics](zed2i-imu-extrinsics.md). See [the server audit](campaigns/server-status-20261001.md) for missing N=3 repetitions; old identity-extrinsic results are historical.

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
- `gt_tum.txt`: RTK-derived ground truth using the **correct 2.86 m** GPS-to-camera lever arm
  (installed 2026-08-06; see "Ground-truth lever arm" below).
- `gt_tum.txt.wrong-1p86-lever`: the superseded 1.86 m file, archived. **Do not use.**
- `gt_measured_2p86_interp_tum.txt`: reference 2.86 m interpolated GT (kept for verification).
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

`gt_tum.txt` / `gt_interp_tum.txt` are already the correct 2.86 m GT — no copying is needed.
(Historically the 2.86 m file had to be copied over a wrong 1.86 m default; that is now fixed.)

```bash
# no GT substitution required; evaluate directly

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


## Ground-truth lever arm (2026-08-06)

The GPS position antenna (`moving_base`, the REAR antenna) sits 0.320 m ahead of the rear axle;
the ZED optical centre sits 3.180 m ahead of it. The antenna->camera lever arm is therefore
**3.180 - 0.320 = 2.860 m**. Both are measured from the same datum, so the CAR/4WS `base_link`
convention cancels — mixing those conventions is what produced the earlier, undocumented 1.86 m
extractor default. `scripts/data/_zed2i_ros2_extract.py` now defaults `--gps_to_camera_x` to 2.86.

Published ZED2i ATEs were always scored against the correct 2.86 m *interpolated* GT; only the raw
`gt_tum.txt` (which feeds `segments_auto.csv`, segment maps and trajectory overlays) carried the
1.86 m error. It was replaced on 2026-08-06 and all 18 zed2i runs re-evaluated: ATEs moved by
<= 0.51 % (median 0.068 %), consistent with the interpolation fix alone.

Note `--gps_to_camera_z` is 0.0, so GT altitude is the **antenna's**, not the camera's 1.31 m
height. This does not affect horizontal ATE.

**Two-machine clock offset:** the camera and robot are recorded by different computers into
different bags; `/gps/fix` appears in both, giving a measured **0.10 s** camera->robot offset
(residual +/-40 ms ~ +/-2.4 cm at 0.6 m/s). Anything fusing camera and RTK across the two bags
must apply it.
