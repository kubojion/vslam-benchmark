# OpenVINS input handling for the experimental noise comparison

This is an experimental replay correction, separate from the production Rule C
campaign. Core estimator equations, camera/IMU calibration, noise values, sensor
timestamps, and the trajectory export policy are unchanged. Comparisons must
rerun Rule C and historical-noise controls with the same input handling as tuned
candidates; historical runs with unknown delivery loss are not matched controls.

The serial 180-second Citrus checks showed that slower BEST_EFFORT playback still
lost IMU samples. Reliable transport delivered every sample, but one V4 attempt
left two eligible final images queued. The native worker runs from IMU callbacks,
so a queue can remain at end of playback even when suitable IMU data has arrived.
The detached callback worker also captured its local IMU message by reference.
Both patterns are present in the
[upstream ROS2 visualizer](https://github.com/rpng/open_vins/blob/master/ov_msckf/src/ros/ROS2Visualizer.cpp).
The reference can outlive its callback; V5 captures that message by value.

V5 optionally enables an end-of-recording control topic, independently of sensor
topics. The player sends schema version and published IMU/stereo counts. The
native callback acknowledges only after those counts have arrived, all stereo
frames have been queued, and the update worker is idle. It then feeds eligible
queued images using the already-received last IMU timestamp and current native
camera–IMU offset. No IMU sample or image is fabricated, duplicated, or shifted.
Duplicate control requests repeat only the acknowledgement. The recorder remains
alive for final outputs and fails if no valid acknowledgement arrives in 30 s.

The native callbacks use the node's default mutually exclusive callback group;
this keeps the end callback serialized with sensor callbacks. The independent
worker is checked separately and its queue mutex is acquired before draining.
See the [ROS 2 Humble callback-group documentation](https://github.com/ros2/ros2_documentation/blob/humble/source/How-To-Guides/Using-callback-groups.rst).

The new audit requires exact ordered IMU receipt, stereo counts and timestamp
fingerprints, no camera rate drops, queue accounting, native noise agreement,
matching native/player completion receipts, and zero eligible cameras pending.
Any pending images must be the real recording suffix and lack later real IMU
support at the native estimated offset. This policy uses sensor availability,
not ground-truth trajectory error or a progressively enlarged frame allowance.

The coordinator also audits a failed player when the native estimator exited
normally. Such a failure cannot silently become a failed noise observation.
Independent native crashes and explicit attempt timeouts remain estimator
failures. Repeated integration and concurrency validation are still required
before broad campaign activation.

## Build and switches

- Image: `sha256:e02ea6f53c6fb380eb671c2791be4bd0de3db3b2782c08da4f32f0ab37338197`.
- Base: `sha256:97cee7ddbd38f8c1c2f3678bf3c8823f5bedb8037f0b19e291f1903ddd29839d`.
- `OPENVINS_END_OF_STREAM_DRAIN=1` explicitly enables native/player completion.
- Use `OPENVINS_IMU_RELIABILITY=reliable` for both endpoints.
- The campaign audit uses `require_end_of_stream=True`, `require_exact=True`,
  and `allowed_pending_tail=None` for native IMU eligibility.
- Build recipe, exact source hashes, logs and test receipts are preserved under
  `/data/imoroz/IMU-NOISE-ISSUE2/noise-all-n1-20261010/openvins-input-audit/`.
- [Source patch](openvins-delivery-v5.patch) includes the earlier receipt and
  reliable-transport instrumentation relative to the private source checkout.

Compilation passed. At integration, the relevant suite passed 73 tests and 108
subtests; two subsequent failure-classification tests also passed in the 18-test
delivery suite. Player contract checks passed bad-ack rejection, retry, valid
receipt and timeout cases. Native V5 execution qualification is pending; these
checks alone do not establish search readiness.
