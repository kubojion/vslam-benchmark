# Field-IMU noise derivation

## Purpose

The Rosario and HortiMulti OKVIS configurations, together with the ZED2i
IMU-consuming estimator configurations, previously mixed unrelated RealSense
defaults, raw Allan values, and undocumented multipliers. This procedure
replaces those exceptions with one reproducible sensor profile per dataset.
The ZED2i profile is shared by every benchmark estimator that consumes its IMU.
It never reads ground truth, an estimated trajectory, or ATE, so the result is
not tuned to favour an algorithm.

## Method

Run:

```bash
source /opt/ros/humble/setup.bash
/usr/bin/python3 scripts/analysis/derive_okvis_imu_noise.py \
  --zed-stationary-bag ../steering-test1-light \
  > /tmp/okvis-imu-noise.json
```

For each IMU recording at its native recorded rate, the script:

1. estimates gyro bias from a fixed known-stationary or lowest-motion interval;
2. estimates white-noise density from adjacent differences using
   `1.4826 * MAD(delta) / sqrt(2 * sample_rate)`;
3. repeats that estimate in non-overlapping one-second windows over the full
   recording;
4. takes the largest per-axis/per-sequence 95th percentile and rounds it up to
   a declared resolution.

The stationary estimate is a useful sensor sanity check. The operational q95
is used for `sigma_g_c` and `sigma_a_c`, because it also represents the
high-frequency vibration delivered to the IMU on the agricultural platform.
It must be described as an *effective recording noise envelope*, not as a
laboratory Allan-deviation measurement.

The stationary/low-motion intervals are too short to estimate bias random walk reliably.
Accordingly, `sigma_gw_c` and `sigma_aw_c` retain the published calibration
values rather than inventing a fit from insufficient data.

The ZED SDK publishes gyroscope noise and random walk in degrees-based units.
OKVIS requires radians, so the factory gyroscope random walk is converted from
`0.0424 deg/s^2/sqrt(Hz)` to `0.0007400196 rad/s^2/sqrt(Hz)`. The effective
measurement densities come from the recording, not from those factory values.
See the [official ZED sensor API example](https://github.com/stereolabs/zed-sdk/blob/master/tutorials/tutorial%207%20-%20sensor%20data/cpp/main.cpp),
which reports each sensor's unit alongside noise density and random walk.

## Frozen values

| Dataset | `sigma_g_c` | `sigma_a_c` | `sigma_gw_c` | `sigma_aw_c` |
|---|---:|---:|---:|---:|
| Rosario v2 | 0.0015 | 0.070 | 1.823e-6 | 4.750e-5 |
| HortiMulti | 0.0035 | 0.110 | 3.22094e-5 | 4.584471e-5 |
| ZED2i | 0.0195 | 0.180 | 7.400196e-4 | 2.020e-2 |

The ZED2i row is used unchanged by Basalt, ORB-SLAM3, AirSLAM, OpenVINS,
Voxel-SVIO, OKVIS2, and OKVIS2-X. Parameter names differ, but each schema
represents the same continuous-time noise density and bias random walk.

Initial `g0` is sequence-specific and is copied verbatim from the script's
stationary mean. Sensor noise is dataset-specific but never sequence-specific.
Camera/front-end settings remain the same across datasets.

| Sequence | Stationary head | `g0` [rad/s] |
|---|---:|---|
| Rosario `sequence1` | 5.00 s | `[-0.0044351044, -0.0008770673, -0.0017121638]` |
| Rosario `sequence5` | 10.00 s | `[-0.0042909713, -0.0005803788, -0.0016624973]` |
| HortiMulti `strawberry02` | 2.00 s | `[-0.0004084356, 0.0006965301, -0.0011057867]` |
| HortiMulti `strawberry03` | 0.75 s | `[-0.0005410027, 0.0006781232, -0.0012222300]` |
| ZED2i S/N 30291010 (`steering-test1-light`) | first 30.00 s | `[0.0018397597, -0.0023903539, -0.0055601826]` |

The benchmark ZED sequence begins with the vehicle already moving and with
strong platform vibration, so its first samples cannot be treated as a
stationary head. The separate `steering-test1-light` ROS 2 bag is from the same
camera (diagnostics identify S/N 30291010), and GPS confirms that its first 30
seconds are stationary. GPS is used only to establish this fixed interval; the
script reads raw IMU from the bag and does not read GPS, ground truth, estimated
trajectories, or trajectory error. The operational q95 still comes from the
actual benchmark field recording.

For source-integrity checking, the calibration bag's SQLite file has SHA-256
`eed14567ef1d322c2d25c6b2510d41f5c53b47229244bdf47045ba42ecf70f75`.

## Limits

This is a defensible in-recording estimate, not a replacement for a multi-hour
stationary Allan-deviation experiment. If such raw calibration logs become
available, replace the effective envelope in one declared revision before the
final campaign; do not select noise values by benchmark error.

The stationary/low-motion intervals above are fixed inputs to the derivation,
not values optimized against trajectory quality. They should be rechecked only
if the underlying recordings are replaced or re-trimmed.
