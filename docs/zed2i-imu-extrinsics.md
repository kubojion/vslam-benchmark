# ZED2i camera–IMU extrinsics

## Current calibration — 2026-10-02

The per-serial SDK matrix for camera **30291010** has been recovered. Its original
[IMAGE-coordinate export](campaigns/zed-sdk-calibration-20261002.json), metres,
firmware and SDK version are preserved. Use the full matrix; the axis-only
September profile is superseded for future inertial estimation.

`T_A_B` maps B coordinates into A. Stereolabs defines its SDK matrix as IMU to
left camera. With `Q = [[0,0,1],[-1,0,0],[0,-1,0]]`, mapping IMAGE axes to the
ROS forward/left/up IMU convention, the benchmark uses
`T_imu_left = diag(Q,1) * inverse(T_left_imu_SDK_IMAGE)`:

```text
-0.00724344284   0.00881396234   0.99993492118   0.002168823615
-0.99996934119   0.00291087936  -0.00726935023   0.023046387610
-0.00297476170  -0.99995691950   0.00879260732  -0.000130804474
 0               0               0               1
```

The right-camera transform is `T_imu_left * Tx(0.11984625036568344)`.
The [derivation record](campaigns/zed-physical-calibration-20261002.json) contains
full precision and each algorithm's convention. The factory residual rotation is
0.675069 degrees. Projection of the supplied float32 matrix onto SO(3) removes only
rounding error. The later SDK image intrinsics/raw stereo rotation do not replace
the July recording's rectified CameraInfo.

`scripts/data/prepare_zed_calibration.py` verifies the eight applicable configuration
files for ORB-SLAM3, Basalt, OKVIS2, OKVIS2-X, AirSLAM, OpenVINS and Voxel-SVIO.
`--apply` changes only reviewed extrinsics. Noise, time offset, initialization and
feature/solver settings remain unchanged. Basalt shares its calibration with VO;
old VO exports must still use their preserved virtual-frame calibration snapshots.

## Historical cohorts and time

Before September's correction, some configurations confused optical camera axes
with ROS IMU axes. The September profile corrected that permutation but used an
identity **residual** rotation. Eleven current historical inertial run-1 attempts
used that incomplete calibration. Preserve their trajectories, scores and failures;
a corrected output transform cannot repair the preceding fusion. Those attempts
need a separate corrected estimation cohort, alongside the missing repetitions.
See the [evidence-pinned findings](campaigns/zed-calibration-findings-20261002.json).

Camera and IMU share the ZED timestamp domain; the configured camera–IMU offset
remains zero. No offset is fitted to this field trajectory. The previously quoted
+0.10 s camera-laptop/robot offset belongs to a **different hangar recording** and
must not be applied to the field reference. The field clock offset remains unknown,
with the reproduced sensitivity disclosed in the preparation report.

## Reference and validation

The approved nominal 1 m height, documented horizontal geometry and exact GNSS
spike mask now define a versioned position reference. RTK float remains in the
primary reference; excluded intervals are not interpolated. Identity quaternions
are placeholders and cannot support rotational accuracy claims.

See [ZED preparation](zed-preparation-20261002.md) for reference hashes, sensitivity,
saved-result qualification, short execution checks and remaining runs. Native
execution readiness is separate from a correctly parsed calibration. The newly
reproduced ORB g2o ABI incompatibility and Voxel shutdown-lifetime defect are tracked
there; historical outcomes have not been silently relabelled as repaired runs.

Sources: [Stereolabs SDK transform definition](https://www.stereolabs.com/docs/api/structsl_1_1SensorsConfiguration.html),
[pinned ROS wrapper](https://github.com/stereolabs/zed-ros2-wrapper/blob/cce25d32f88362b50f3aec08876519487be724c3/zed_components/src/zed_camera/src/zed_camera_component_main.cpp),
[read-only recording source index](campaigns/zed-source-records-20261001.json).
