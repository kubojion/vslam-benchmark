# OpenVINS configs

Per-dataset OpenVINS estimator configs. OpenVINS is a stereo + IMU MSCKF
filter (no loop closure in the open-source release), so only `vio` runs are
supported.

Each `<dataset>/` directory contains:

- `estimator_config.yaml`     - filter / front-end parameters
- `kalibr_imu_chain.yaml`     - IMU rate, noise densities, body extrinsics
- `kalibr_imucam_chain.yaml`  - per-camera intrinsics, distortion, T_imu_cam,
                                ROS topic names, resolution

`relative_config_imu` and `relative_config_imucam` in `estimator_config.yaml`
reference the other two files relative to the config dir.

The wrapper `scripts/run/run_openvins.sh <dataset> <seq>` mounts the workspace
into the `openvins:humble` container and points
`config_path:=/ws/configs/openvins/<dataset>/estimator_config.yaml`.

## Datasets

| Dir          | Sensor                          | Notes                                             |
|--------------|---------------------------------|---------------------------------------------------|
| `EuRoC-MAV/` | VI-Sensor (wide-FoV global shutter + ADIS16448) | Verbatim copy of upstream `config/euroc_mav/`. Used for sanity testing against the published numbers. |
| `rosariov2/` | ZED stereo IR + integrated IMU  | Pre-rectified 1280x720 mono8, 15 Hz cameras + 200 Hz IMU. T_imu_cam0 = identity (IMU is colocated with cam0). |

When adding a new dataset:

1. Create `configs/openvins/<dataset>/`.
2. Copy and edit the three YAMLs - keep the `%YAML:1.0` header so cv::FileStorage
   loads them.
3. Topics in `kalibr_imucam_chain.yaml` MUST match what `openvins_data_player.py`
   publishes (`/cam0/image_raw`, `/cam1/image_raw`, `/imu0`).
