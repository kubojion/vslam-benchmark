# Paper acceptance review — 2026-10-01

This review supersedes the blanket historical-provenance hold in the earlier
[repair handoff](repair-handoff-20261001.md). It accepts specific claims supported
by saved evidence. It does not certify exact historical rebuilds, optimal tuning,
real-time operation, agricultural reference accuracy, or repaired runner readiness.
No estimator was run. The subsequent [matched-session reference review](reference-review-20261001.md)
corrects Rosario evaluation and future timing/GNSS calibration settings; saved run
parameters and the accepted EuRoC numerical values remain unchanged.

## Comparison and acceptance criteria

The accepted comparison is **final saved trajectory accuracy of the recorded
algorithm profiles on the three EuRoC control sequences**, accompanied by export
coverage, process exits and all attempted outcomes. It is not a reproduction of
each algorithm's paper or an identical-compute/identical-feature-budget contest.
Metric stereo/VIO uses SE(3); monocular DPVO/DPV-SLAM uses a separate Sim(3) shape
comparison. LC tables include the recorded final optimization policy. These
control results alone do not establish agricultural performance.

Each explicit decision in [the ledger](campaigns/paper-acceptance-20261001.json)
pins original logs/configs/trajectories, evaluation inputs and the numerical
evaluation content. Qualification fields are excluded from the numerical digest,
so regeneration can replay the decision without a circular hash. Changed evidence
blocks acceptance; it never silently requalifies a new run. The ledger covers all
660 default slots and records cell decisions and per-repetition exceptions.
Historical excluded/smoke outputs and GNSS variants retain their separate scopes.

A green **✅ N=3** requires three explicitly accepted, same-cohort repetitions,
valid evaluated trajectories, zero recorded exits and at least 95% dense camera
export coverage in each repetition. It does not mean zero tracking loss or full
processing instrumentation. Sparse exports, crashes after saving and lower coverage
remain paper-usable only with their specific limitation and receive no clean tick.
The 95% gate is a reporting criterion; scores and exact coverage remain visible.
Genuine failed attempts stay in the denominator and are never replaced merely to
obtain three successes. An accepted failure supports the observed configured-attempt
outcome, not a claim that a calibrated algorithm inherently cannot solve that scene.

Historical dirty runner bytes and some source-to-binary linkage are unrecoverable
from recorded digests alone. They remain disclosed reproducibility limitations.
They are not, by themselves, proof of an invalid trajectory. Supporting evidence
includes saved effective configs, mode metadata, source/image or executable
identities, native startup/output observations, timestamp/coverage checks and
independently checked frame conversion. Agricultural physical-frame and GNSS
input/reference uncertainties are materially different and remain blockers.

## Shared profile review

`scripts/campaign/audit_acceptance_evidence.py` records semantic differences from
bundled examples, today's resolvable config files, startup/completion observations
and native-export correspondence for every existing default repetition. The
artifact is `results/acceptance-20261001/evidence.json`. It reuses the selected-mode
audit of 690 default/retained slots: 1,220 passing checks, 21 explicitly unverified
checks, no parse errors or mismatches. Author examples are supported starting
points, not evidence of optimality. Full saved configs remain the protocol source.

| Profile | Reviewed choice and interpretation |
|---|---|
| ORB-SLAM3 | EuRoC's 1,200 features, depth threshold 60, 20 Hz camera and IMU/noise/calibration values match the bundled stereo/inertial examples. `Camera.RGB=0` is immaterial on grayscale EuRoC. Explicit `IMU.InsertKFsWhenLost=1` matches the default in `Settings.cc`. LC is selected by `loopClosing`; duplicate identical `System.LoopClosing` aliases are ignored, not conflicting active settings. Rig depth adaptations elsewhere remain disclosed. |
| OKVIS2 | EuRoC VIO differs from the bundled config by disabling LC; VIO-LC matches its numerical settings, including final BA disabled. VO is the supported IMU-disabled visual ablation, not the author's principal VIO result. VO-LC increases the LC-frame window from 3 to 5; VIO-LC retains 3. The author's conservative noise and solver choices are not erroneous copies of raw sensor noise. |
| OKVIS2-X | Preserves EuRoC calibration, front-end/solver values; disables dense/submap display/mapping for this trajectory benchmark. VO disables IMU. Odometry disables LC/final BA. LC uses final BA and locally enables extrinsic optimization; its LC-frame window is 5 versus the example's 3 (ZED VIO-LC retains 3). These are benchmark profile choices. Do not present OKVIS2 versus OKVIS2-X as a controlled ablation of implementation alone. Final-BA output/frame correspondence is checked against saved native files and final extrinsics. |
| Basalt | Separate VO/VIO profiles, realtime dropping disabled. Rosario's 0.03 m triangulation compatibility exception avoids the baseline gate; other rigs retain 0.05 m. EuRoC's calibrated native stereo/IMU geometry and exported body origin were already independently reviewed. The installed binary hash is known; exact package/source linkage remains a disclosure. |
| OV2SLAM | Bundled accurate EuRoC profile with `force_realtime=0`; VO disables LC, VO-LC enables it. `nmaxdist=35` comes from that example. Optimized indexed LC exports are matched to saved raw timestamps; they are not expected to equal the unoptimized trajectory. Horti's initialization/coverage thresholds are separate benchmark adaptations. |
| AirSLAM | EuRoC camera/odometry/refinement values match bundled examples except IMU disabled in VO and per-rig TensorRT cache names; unused IMU noise fields are absent in historical VO configs. VO/VO-LC support sparse keyframe accuracy only. All 18 EuRoC inertial attempts have the already-confirmed rectified-axis fusion defect and require corrected estimation. |
| OpenVINS | EuRoC enables `init_dyn_use=true`, whereas the bundled example uses false. This is an author-supported dynamic initializer selected by the benchmark, not an unchanged default. Other EuRoC feature/calibration/initialization settings match the example. Agricultural online-calibration and acceleration-threshold adaptations remain separately disclosed. Its immutable image identifies installed bytes, not verified historical library resolution. |
| Voxel-SVIO | 500 features and the bundled estimator settings; gravity 9.81007 rather than 9.81. MH01 uses the author's expressly recommended 10 s initialization window; MH03/MH05 use 2 s. MH01's approximately 75% coverage remains a limited outcome, not grounds for tuning or replacing the runs. |
| DPVO / DPV-SLAM | Saved 96-patch config matches the bundled default; benchmark stride 1 versus demo CLI default 2 processes every input image. Seeds 1001/1002/1003 are intentional independent repetitions. Directory input is not half-resolution video input; it is undistorted and cropped to multiples of 16. LC uses proximity retrieval, not classic DBoW. Sim(3) claims stay separate from metric stereo. |
| MAC-VO | Saved official Performant config matches its bundled example, which explicitly is not the paper-reproduction profile. EuRoC uses native 752×480 input, disabled GT poses, and the loader's approximately 0.110 m baseline. GeneralStereo uses the local 640×480 resize adaptation. All 24 saved exports were checked against native poses/timestamps; absent GeneralStereo `gt_pose` fields do not imply GT leakage. |
| GNSS modes | Current recipes and repaired selectors cannot establish historical covariance, antenna/input selection, output frame or reference independence. Five default observations now require reruns from native-log antenna evidence; the other 15 defaults and six variants retain unresolved accuracy blockers; the invalid full-pose VINS-Fusion Horti02 export remains an observed artifact failure. |

Different feature budgets, solver iterations, initialization and internal resizing
are legitimate algorithm/profile differences when disclosed. They do not support
claims of equal compute or exhaustive tuning. No retrospectively chosen threshold
or parameter is justified by obtaining a better final-test ATE here.

## Exceptions and failures

The ledger records every exception individually. EuRoC ORB VO MH03 r2 and VO-LC
MH01 r3, MH03 r3, MH05 r1 saved full-coverage trajectories but exited nonzero.
Their accuracy is usable with the exit disclosed, not as clean successes.
The native logs reveal another execution-reporting inconsistency: all 18 EuRoC
OV2SLAM runs report `terminate called without an active exception` after playback,
with a joinable `std::thread` destructor in the stack trace. All nine EuRoC
Voxel-SVIO runs report a Boost mutex error after the wrapper stops the node.
Their metadata nevertheless records exit 0. They are accepted only with a native
shutdown-error limitation; a wrapper zero is not evidence of clean native exit.
Future runners must capture the node's actual exit/signal separately from the
player/wrapper and diagnose shutdown before production. No such crash is claimed
fixed by the earlier process-isolation changes.
ORB MH03 VIO r2 and VIO-LC r1 cover about 85.6% and 86.3%; Voxel MH01 covers
about 75% in all repetitions. OpenVINS has only r1 per sequence: MH01/MH03 exited
134 after saving; MH05 has 94.1% coverage. These observations remain intact.

EuRoC OKVIS2-X VO-LC variability (MH03 ATE about 0.041–0.216 m; MH05 about
0.205–0.423 m) is not alone evidence of a bad experiment. Native selected exports,
saved final-BA policy and repetition settings are checked; the range must be
reported, not replaced by the best run. Repeated similar Basalt/Air scores do not
establish duplicated runs: each attempt retains its own logs, runtime and output
hashes. No published-paper numerical ranking is asserted without matching its
input, alignment, coverage and optimization protocol.

Six ORB startup attempts with saved configs/logs and nonzero exits are accepted
as observed configured-attempt failures only. `bad_alloc`, segmentation faults
and optimizer assertions do not establish OOM, insufficient GPU power or a
sensor-excitation root cause. Five retained collapse outcomes remain visible. The two OpenVINS Rosario collapses
now have confirmed identity-extrinsic defects and require corrected estimation;
three other collapses remain accepted diagnostic failure observations. Physical
agricultural accuracy is withheld; no failure has been erased.
OKVIS2 ZED VO-LC r2 ended with `Killed` and lacks metadata/output; OKVIS2-X ZED
VO-LC r1 has exit 141 and no usable final trajectory. Their execution causes remain
blocked, not certified algorithm failures or invented missing executions.

Three agricultural cells have differing historical workspace digests although
their recorded config/algorithm/binary/model settings agree. Keep those cohorts
separate: OKVIS2-X Rosario seq1 VO-LC, ORB ZED VO-LC, AirSLAM ZED VO-LC.

## Remaining material evidence and execution

The [matched-session review](reference-review-20261001.md) resolves Rosario's
physical IMU-to-camera reference chain and repairs evaluation, but finds a shared
image/projection/baseline inconsistency. Horti's February calibration and reference
rows match; the exact generation-origin and timestamp linkage remains unresolved.
ZED original bags and the physical longitudinal lever are verified; 3D/quality
policy and serial calibration remain unresolved. Its unmeasured camera/RTK clock
is a disclosed limitation after the requested sensitivity check, not a blocker. GNSS still requires historical inputs, covariance, selected
antenna and fusion-output evidence. More repetitions cannot establish these facts.

There are now 91 distinct required reruns: the previous 30, fourteen Rosario
identity-extrinsic cases, forty-two additional Horti timing cases (48 timing
findings overlap six previous ORB rectification reruns), and five GNSS lever cases.
Missing slots remain separate from existing
failed/interrupted attempts. The generated acceptance handoff and future manifest
list every action. Retaining accepted saved results requires no estimator execution;
it does not verify the repaired runner. Production execution stays blocked until
the documented small diagnostic batch and its prerequisites are authorized and pass.
