# Attempt process and output isolation audit — 2026-10-01

Code repair and synthetic validation are complete for the changes below. Actual
ROS/container execution is **unverified**. No estimator was started; the relevant
benchmark containers were stopped during this audit and were not started for tests.
This does not resolve native crashes or establish campaign readiness.

## Confirmed defects and repairs

- AirSLAM, OV2SLAM, Voxel-SVIO, VINS-Fusion+GPS, CIFASIS, RTAB-Map+GPS and
  OpenVINS+GPS used process-name cleanup that could signal another job. OpenVINS
  VIO also lacked outer-container cleanup on interruption. All eight wrappers now
  bind shutdown to their own attempt stages or unique Docker container IDs.
- ROS 1 wrappers choose a private master port and refuse conflicting native jobs
  in their shared container without signalling them. They verify that `/results`
  mounts this workspace before sending a process supervisor into the container.
  ROS 2 wrappers reserve a workspace-locked domain, reject occupied DDS UDP ports,
  and propagate the domain to their host/container components.
- Voxel-SVIO previously removed shared `output/pose.txt` and parameter files.
  It now sets the upstream `output_path` to the attempt's `native/` directory.
  The original native export is retained before camera-clock conversion.
- CIFASIS previously deleted shared output files and tried a chain of GPS, keyframe
  and non-GPS trajectory fallbacks. It now runs in its own `native/` directory and
  requires `CameraTrajectoryGPSOpt.txt`. Source inspection establishes that this
  EuRoC-named exporter writes seconds and, for inertial mode, body poses. A selected
  source file is recorded; historical unknown selections remain unknown.
- CIFASIS reset `GPS_COV_XY` and `GPS_COV_Z` after input preservation. That reset is
  removed so supplied fallbacks agree with the saved input policy. Its Xvfb process
  chooses an unused display rather than deleting a global X99 lock/socket.
- RTAB-Map now retains its database and raw pose export inside the attempt. Export
  command errors propagate. OpenVINS rejects all modes except VIO; its GNSS
  composite has its own separate runner. OpenVINS+GPS writers are stopped before
  trajectory counts/hashes are taken.

## Ownership and evidence

`scripts/run/_owned_process.py` gives each stage a fresh inherited environment
token. Descendants retain ownership even when they start a new process session.
Before signalling, the helper opens a Linux pidfd and rechecks token/start time;
there is no fallback that signals an unverified numeric PID. Launch and cancellation
are serialized, so cancellation before startup cannot launch a late child. Stage
identities cannot be reused. SIGINT, SIGTERM and any eventual SIGKILL are recorded,
and remaining owned processes cause a shutdown error.

State and stop logs remain under `processes/`. Metadata links their hashes and
explicitly labels these as supervised-command statuses, not necessarily individual
native-node exit statuses. A successful ROS launcher/composite shell can still
conceal a failed child; output and native logs must also be assessed. A trajectory
alone does not prove clean shutdown. These logs are execution evidence, not config
signature inputs, so random tokens and times do not split repetition cohorts.

## Validation and outstanding prerequisites

Eleven synthetic process tests exercise detached descendants, unrelated-process
survival, exact Docker argument transport through a fake Docker shim, cancellation,
supervisor interruption, PID identity changes, forced-shutdown records, UDP domain
occupation and inter-attempt domain locking. Metadata tests verify retained forced
shutdown evidence. Shell syntax passes for every runner; the helper parses with
Python 3.8 syntax. No real Docker or ROS node is launched by these tests.

Before readiness can be certified, validate pidfd availability under each actual
container's Python/kernel/seccomp configuration, ROS master/domain discovery,
signal forwarding, native finalization and writer flushing. Composite ROS stacks
still need per-native-node outcome validation. Environment-scrubbing descendants
cannot be owned by the inherited token; such behavior must be checked in actual
stacks. Container mount/config/binary identity and native export behavior are also
prerequisites. Resource isolation against unrelated manual work is not guaranteed
by workspace locks. No claim of a fixed ORB, OpenVINS, AirSLAM or GNSS native failure
follows from these wrapper repairs.
