# OpenVINS large-image transport diagnostic

V6's first full Rosario sequence1 was stopped after its playback became extremely slow. Its partial player receipt reports 1,300.7 seconds waiting for acknowledgements, maximum event publication cost 0.0234 seconds, 44,367 published IMU samples and 3,242 published stereo pairs. Native receipts contain all those IMU samples, 3,242 left images and 3,241 right images; interruption happened while the last pair was outstanding. This is a stopped diagnostic, not a completed input audit or a benchmark result. The one passed 180-second V6 check did not establish full-recording readiness.

The pinned image uses Fast DDS 2.6.12 and rmw_fastrtps_cpp 6.2.10. A raw Rosario mono image is 921,600 bytes. The default SHM descriptor reports size zero before initialization; the matching Fast DDS source resolves zero to 512 KiB. An actual disposable RMW participant created a 549,408-byte segment file, including overhead. The native CPU times and low system load do not explain the large acknowledgement delay. Undersized shared-memory transport is a hypothesis supported by these observations, not yet a proven complete explanation.

Optional `OPENVINS_TRANSPORT_PROFILE=large_shm` selects the checked-in XML with a 32 MiB shared-memory segment and UDP restricted to 127.0.0.1, with builtin transports disabled. Docker receives a private 128 MiB `/dev/shm` to accommodate the participants. No host/kernel configuration changes are required. Message size, queues, noise, images, timestamps, geometry and estimator binaries are unchanged from V6. Application receipt barriers and exact input/EOF checks remain enabled in the diagnostic.

Humble's `ROS_LOCALHOST_ONLY=1` appends another default-size SHM transport even after loading XML. Therefore this profile uses `ROS_LOCALHOST_ONLY=0` and specifies localhost confinement directly in its transport descriptors. A disposable native RMW preflight confirmed a 33,579,552-byte segment file and no additional default-size segment. The profile is snapshotted in run provenance; default wrapper behavior remains available unchanged.

This is an experiment in complete offline input delivery. Both fresh Rule C controls and tuned OpenVINS configurations must use whichever delivery policy passes all validation. It cannot be reported as an IMU tuning gain or real-time throughput improvement. Full native validation and concurrency validation remain prerequisites to noise-search activation.

Evidence: `openvins-input-audit/v6-full-rosario-slowdown.json` and `large-shm-preflight.json` in the external campaign artifact directory.

Primary sources:

- [Fast DDS SHM documentation](https://fast-dds.docs.eprosima.com/en/2.6.x/fastdds/transport/shared_memory/shared_memory.html)
- [Fast DDS 2.6.12 initialization](https://github.com/eProsima/Fast-DDS/blob/v2.6.12/src/cpp/rtps/transport/shared_mem/SharedMemTransport.cpp)
- [RMW 6.2.10 participant initialization](https://github.com/ros2/rmw_fastrtps/blob/6.2.10/rmw_fastrtps_shared_cpp/src/participant.cpp)
