# Bounded AirSLAM refinement diagnostics — 2026-10-02

The historical MH05 VIO-LC run4 remains a failed production attempt: native SIGSEGV,
wrapper139, no final LC trajectory. Its last log line was `Build junction database...`;
that line alone did not identify the crashing thread. No production repetition was
retried or replaced.

Two bounded diagnostic executions used independent copies of the saved map and
effective refinement configuration, private ROS masters and 180-second limits.
The original map SHA-256 is
`053f2a9c003577767a1e651610346a2461d43850b87b9c379b879a99dad285e2`.
All eight executable/library/config artifacts in the frozen corrected native tree
matched their campaign hashes before diagnosis. Neither wrapper pacing nor input
image replay is involved in direct saved-map refinement.

1. **Exact production binary/library:** GDB reproduced SIGSEGV in thread10,
   `RosPublisher`'s `MapMessage` callback, called by `ThreadPublisher<MapMessage>::Process`.
   The main thread was in vocabulary clustering under `BuildJunctionDatabase`.
   The map deserialized, reported 188 keyframes/28,694 points, found 42 loop pairs and
   reached global optimization. Loaded mappings identify the frozen corrected library.
2. **Diagnostic symbols in publisher translation unit:** only `ros_publisher.cc`
   was recompiled with the original release flags plus `-g` and relinked into a
   separate library using unchanged production objects. The same copied map completed
   and saved diagnostic-only output. GDB's script then returned1 because no live
   stack remained; the inferior itself exited normally. This is not a production
   success, replacement trajectory or new score.

Source inspection identifies a credible race: `MapRefiner::PubMap` calls
`Map::Publish(..., true)`; this calls `RosPublisher::Clear()` while the asynchronous
publisher can read/update the same point/index containers. The map mutex does not
protect the publisher callback. These source paths match current upstream. The
exact faulting memory operation and causal chain are **not established** by the
release-symbol backtrace, and the diagnostic rebuild's success does not prove a fix.
Treat the race as a supported hypothesis for further upstream diagnosis, not a
confirmed historical root cause or a junction-descriptor/serialization defect.

There is no observed configuration mismatch, input-copy corruption, wrong-library
load or wrapper signal in the reproduced case. Successful deserialization and the
second completion argue against a deterministic malformed-map failure, but do not
prove every serialized field valid. No upstream blame is inferred from a log line.

Evidence, exact commands, loaded mappings, copied inputs, hashes and both outcomes
are in `results/protocol-review-20261002/`. Diagnostic outputs remain outside all
benchmark repetition trees and exports. Production map/log/config/source bytes are
preserved. No change to the experimental validity decision or failure count follows
from diagnostic success. A publisher synchronization repair requires separate review
and validation; it is not claimed fixed here.
