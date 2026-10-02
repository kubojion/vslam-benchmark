# Draft PR: express the camera-to-body transform in rectified image axes

AirSLAM rectifies distorted stereo images but retains the raw left-camera-to-body
rotation. Visual geometry then uses rectified axes while the camera/body conversion
and inertial constraints use raw axes. Compose the raw extrinsic with the inverse
left rectification rotation and recompute its inverse. Translation and the
already-rectified (`distortion_type: 0`) path remain unchanged.

Current upstream was fetched on 2026-10-02:
[sair-lab/AirSLAM d126577](https://github.com/sair-lab/AirSLAM/tree/d1265771026091db97ee8f7a6d80692f0edd5fef).
The defect remains in that revision. The local review branch is
`/data/imoroz/vslam-upstream-review-20261002/AirSLAM`,
`fix/rectified-camera-imu-extrinsic`. It contains the nine-line geometry correction
and a geometry-only native regression with a Catkin test target.

The regression checks that three physical points map to identical body coordinates
from raw and rectified representations, using both radtan and fisheye rectification,
IMU enabled/disabled, and the unrectified control path. It also checks inverse
composition and an unchanged translation. Against current upstream, the four
rectifying cases fail with a maximum point discrepancy of 0.0634944 m; both controls
pass. With the patch, all six pass, maximum point error below 2e-16 m. This is a
geometry test, not an estimator performance result. Native logs and exact commands:
`results/protocol-review-20261002/airslam-upstream-regression/`.

Build the normal upstream dependencies, then enable Catkin testing and build
`test_camera_rectification`; CTest registers `camera_rectification` with the bundled
EuRoC calibration. The review here compiled the test, current-upstream/patched camera
sources and utilities directly in the existing Noetic environment; no GPU inference
or estimator sequence was required. The CTest integration itself was not used for
that direct-compilation verification.

Benchmark results retain the exact implementation
`1e0ad79c28d4d58d6a40d160df9b05c8361c7774` and the frozen native build. The source
correction in the review branch is byte-identical to that benchmark correction;
the new regression does not modify stored results. The independent map-publisher
crash is documented separately and is not claimed fixed by this change.

No push or PR submission has been made. This description and local branch are
prepared for review, not a claim of upstream acceptance.
