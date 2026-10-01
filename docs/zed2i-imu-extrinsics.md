# ZED2i camera–IMU extrinsics

## Original-record verification, 2026-10-01

The [matched-session review](reference-review-20261001.md) independently verifies
the supplied July 3 robot bag and camera-laptop GPS/TF extract. It establishes the
physical 2.86 m longitudinal lever and quantifies the approximately 16.4 mm residual
from the antenna-heading/left-camera offsets. Clock alignment is a disclosed limitation after the requested sensitivity check;
reference 3D/quality policy and per-serial camera/IMU rotation remain unresolved. The latter is absent
from all supplied recordings and requires camera S/N 30291010 on the SDK. The
axis-convention correction below remains a nominal profile, not a per-serial
calibration certificate. Read-only original paths/hashes are in
[the source index](campaigns/zed-source-records-20261001.json).

## Applied calibration

The benchmark ZED2i (S/N 30291010) exports rectified images in
`zed_left_camera_frame_optical` / `zed_right_camera_frame_optical`, but
`imu.csv` is copied from `/zed/zed_node/imu/data_raw`, whose frame is
`zed_imu_link`. These are not the same coordinate convention:

- `zed_imu_link` / non-optical camera: x forward, y left, z up;
- optical camera: x right, y down, z forward.

Ignoring that difference made every previous ZED VIO configuration wrong by a
90-degree axis permutation. The common camera-to-IMU rotation now used by all
ZED VIO configurations is

```text
R_imu_cam = [ 0  0  1
             -1  0  0
              0 -1  0 ]
```

The ZED SDK translation for a ZED2i is the IMU origin in the left non-optical
camera frame:

```text
p_imu_in_left = [-0.002, -0.023061, 0.000217] m
```

After inversion and conversion to the optical camera convention, the two
camera-to-IMU transforms used by the estimators are:

```text
T_imu_cam0 = [ 0  0  1   0.002
              -1  0  0   0.023061
               0 -1  0  -0.000217
               0  0  0   1 ]

T_imu_cam1 = [ 0  0  1   0.002
              -1  0  0  -0.0967852504
               0 -1  0  -0.000217
               0  0  0   1 ]
```

The right-camera translation is composed using the measured rectified baseline
of 0.1198462504 m; it is not inserted along an IMU axis directly.

This calibration is applied to ORB-SLAM3, Basalt, OKVIS2, OKVIS2-X, AirSLAM,
OpenVINS, and Voxel-SVIO. Their field names differ, but all represent the same
camera-optical-to-IMU transform. VO-only configurations are intentionally left
camera-centred because they do not consume IMU samples.

## Remaining serial-specific term

Stereolabs factory-calibrates a small camera-to-IMU rotation per serial number.
The earlier SDK query for S/N 30291010 recorded its magnitude (about 0.675
degrees) but not the matrix. Neither available ROS bag contains the SDK
`left_cam_imu_transform` topic, and the light bag contains no images. The
truncated image bag has a malformed SQLite database. The server also has no
connected ZED or ZED SDK from which to query the value again.

Consequently, the configuration uses identity only for this residual
non-optical-camera-to-IMU rotation. It does **not** use identity between the
optical camera and IMU. Recovering the final sub-degree term requires either:

1. reconnecting S/N 30291010 and saving `camera_imu_transform` from the ZED SDK;
2. locating an original ZED wrapper startup log or recording containing
   `/zed/zed_node/left_cam_imu_transform`; or
3. making a new, well-excited stereo+IMU calibration recording and running a
   camera–IMU calibrator.

The long field sequence cannot reliably identify this residual because its
rotation is overwhelmingly planar. Gyro-versus-stereo-VO fits were rank-poor
and varied by several degrees across otherwise equivalent ORB-SLAM3 runs, so
using their fitted matrices would be less defensible than keeping the residual
at identity.

## Time offset

Camera and IMU timestamps originate from the same ZED hardware clock. No
defensible non-zero offset can be identified from the under-excited field
trajectory, so the camera–IMU time offset remains 0 seconds. This is unrelated
to the documented 0.10-second camera-computer/robot-computer offset used when
combining the ZED recording with the separate RTK bag.

## Validation and result status

All seven estimator configurations parse with their declared transforms. The
rotations are orthonormal with determinant +1, and composing the two camera
transforms recovers the measured 0.1198462504 m rectified baseline. Basalt also
accepted the calibration and initialized its filter on the full sequence;
OKVIS2 loaded both transforms and initialized.

ORB-SLAM3 now passes the earlier first-frame failure and creates its initial
359-point map, but it still crashes in `g2o::VertexSE3Expmap::oplusImpl`
immediately afterward. That is a remaining ORB-SLAM3 runtime defect, not a
configuration-parser or coordinate-frame error.

**Status checked 2026-10-01:** the September 16 `zed2i-imu-recalibration-n1`
campaign has replaced the old IMU artifacts in nine cells with corrected N=1
results: VIO for Basalt, OKVIS2, OKVIS2-X, AirSLAM, OpenVINS and Voxel-SVIO;
VIO-LC for OKVIS2, OKVIS2-X and AirSLAM. Eight are `ok`; OpenVINS VIO is a
recorded scale collapse. ORB-SLAM3 VIO and VIO-LC have no complete evaluated
result. All nine completed cells still need their remaining N=3 repetitions.
See [the current audit](campaigns/server-status-20261001.md).

Any retained pre-correction IMU results are a separate historical cohort.
VO/VO-LC do not use IMU measurements, but shared calibration edits can still
change pose-frame handling: Basalt ZED VO retains the earlier calibration
snapshot and needs an equivalence/configuration review. Do not infer that
all VO artifacts match the present shared calibration file.

## Sources

- [Stereolabs ROS wrapper discussion: the transform is relative to the left camera and unique per serial](https://github.com/stereolabs/zed-ros-wrapper/issues/611)
- [Stereolabs ZED2i wrapper output showing the model translation and a per-unit rotation](https://github.com/stereolabs/zed-ros2-wrapper/issues/83)
- [ZED wrapper output showing the translation at full logged precision](https://github.com/stereolabs/zed-ros2-wrapper/issues/282)
- The bag's `/zed/zed_description` URDF, generated from the official
  `zed_description` package, defines the optical-frame rotation as
  `rpy="-pi/2 0 -pi/2"`.
- `datasets/zed2i/field1_110426_full_10fps_q90/manifest.json` records the image
  frame IDs and the 0.1198462504 m rectified baseline.
