# Draft report: ROS 2 visualization lifetime during shutdown

On ROS 2 Humble with Fast DDS, a native OpenVINS process segfaulted while destroying
publishers during global teardown after middleware singleton destruction. ROS launch
returned zero for that run, so wrapper status hid the native error. The saved GDB
trace, direct-native supervision and before/after checks are recorded in
`results/euroc-focused-20261001/` and the focused validation document.

Current upstream was fetched on 2026-10-02:
[rpng/open_vins 6948812](https://github.com/rpng/open_vins/tree/69488123ed9362dd44b6f28e7f4680abbff1442b).
Its ROS2Visualizer still detaches the image-publishing thread and the subscriber
entry point leaves global visualization objects for static destruction. The local
candidate branch is `/data/imoroz/vslam-upstream-review-20261002/open_vins`,
`fix/ros2-visualizer-shutdown-lifetime`.

The candidate retains the benchmark-tested change: own/join the image-publishing
thread, stop/drain background work after executor spin ends, and release visualization
and estimator objects before explicit ROS shutdown. No filter settings or estimator
math change. Its three changed source files match benchmark revision
`7a496c53d9eed17adbb0f76f1333168ac4b999d0`. Existing short checks plus six fixed full
EuRoC repetitions all have clean native exits under that implementation. Historical
MH01/MH03 run1 exit134 remains historical; it is not the exit of any new attempt.

This is an applicable upstream report and a review candidate, not a blanket thread
safety certification. The patch assumes the executor has stopped dispatching. The
pre-existing detached update worker clears `thread_update_running` before local
destructors release its camera-queue lock, so flag polling alone is not a general
worker-join guarantee. Upstream review should consider owned update-worker lifetime,
shutdown with callbacks in flight and thread-sanitizer coverage. These cases were
not established by the recorded EuRoC tests; no new production run is requested to
conceal that limit. The benchmark implementation remains pinned and disclosed.

For upstream validation, reproduce native shutdown under Humble/Fast DDS with direct
exit capture, both publication/subscription threading settings and orderly/interrupted
shutdown. Check owned-worker completion and publisher destruction before context
teardown. The preserved benchmark diagnostics provide a concrete reproducer and
six clean repaired outcomes, not proof for every executor or middleware.

No push, issue posting or PR submission has been made.
