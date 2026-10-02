# Protocol validity and observed outcomes — 2026-10-02

This continuation preserves the completed audits and fixed EuRoC campaign. It
changes reporting semantics, not numerical scores, estimator settings or trial
selection. The evidence-pinned acceptance ledger now records a separate per-attempt
`protocol` decision. Existing claim decisions retain their meaning and evidence.

## Definitions

**Verified protocol** requires supported input/calibration, the intended recorded
profile, reviewed execution/output handling and appropriate evaluation of any saved
output. Verification is for the stated experiment and claim scope; historical build
reconstruction gaps remain disclosed. Low accuracy, partial coverage, tracking loss
and native keyframe exports do not themselves invalidate an experiment.

**✅ Protocol N=3** requires three completed verified attempts in one recorded
implementation/configuration/hardware cohort. Failures count. It does not guarantee
successful tracking, complete coverage, dense output, real-time operation or every
accuracy claim. Different implementations are never pooled into N=3.

The matrix retains its cells and ordering. `A` counts existing attempts, `E` evaluated
trajectories, `S` clean final exports and `F` observed failures; `U` marks unknown
outcomes when present. A clean final export can have low accuracy or partial
coverage. Native errors after saving count in F, while their validated saved
trajectories can still count in E and support conditional accuracy. A matrix
protocol tick describes completed attempts, not three successful trajectories.

The shared classifier preserves numerical scale-collapse/invalid-export outcomes,
nonzero exits and native errors hidden by wrapper zeros. It does not infer tracking
failure from sparse keyframes. Unsupported/incomplete execution remains unknown.
Counts must not be interpreted as an unqualified tracking success rate.

Invalid setup requires corrected execution only when the completed audit established
an estimator-side defect. Missing evidence remains blocked rather than becoming a
rerun request. Missing repetition slots remain separate from all existing failures.
Agricultural failures with unresolved calibration/reference support remain valid
observations of those configured attempts, without a verified-protocol tick or
an intrinsic-algorithm-failure claim.

## Claim scope and implementation

EuRoC supports the recorded profiles' conditional final-export accuracy: SE(3) for
metric stereo/VIO and separate Sim(3) shape accuracy for monocular DPVO. AirSLAM's
native sparse-keyframe accuracy is explicitly supported. Dense tracking coverage
cannot be inferred from its keyframe gaps. Partial trajectories support accuracy
only over the reported exported/reference-supported samples. No outcome is replaced
to obtain three successes.

Corrected AirSLAM inertial results retain physical attempts 4–6 under benchmark
revision `1e0ad79c28d4d58d6a40d160df9b05c8361c7774`. Original attempts 1–3 remain
in the historical-cohort CSV and reports. MH05 VIO-LC attempt4 remains failed
without a final trajectory; its odometry intermediate is diagnostic only.

OpenVINS has one original attempt and two patched attempts on each EuRoC sequence.
The corrected revision is `7a496c53d9eed17adbb0f76f1333168ac4b999d0`. Its six new
attempts exited cleanly. Exit134 belongs to historical MH01/MH03 run1 only;
historical MH05 run1 exited0. These are separate N=1 and N=2 implementation cohorts,
not a pooled N=3. A third patched repetition per sequence would complete that
cohort if separately authorized; none is launched or silently inserted here.

Rosario image/projection/baseline discrepancies, Horti exact reference origin/timing,
ZED physical 3D/fix-quality/serial-IMU issues and GNSS evidence gaps retain the
completed reference review's disposition. ZED's unknown field clock remains a
disclosed limitation after the requested evaluator sensitivity check, with no
fitted/applied offset. The hangar +0.10 s does not apply to the field recording.

## Preservation and execution limits

Checkpoint `cb014d5` preserves the user's TODO row ordering. The incremental backup
is `/data/imoroz/vslam-repair-backups/20261002T074823Z-protocol-before-repair`, backed
by the complete focused-campaign snapshot. Numerical content of saved evaluations
and the original 45 clean-qualified cells must remain unchanged.

Only bounded AirSLAM debugger diagnostics using copied saved maps are authorized.
No new production repetitions, algorithm additions, pushes or PR submissions.
Protocol validity of existing observations does not certify every future runner.
The old temporary maintenance pause is revoked; historical provenance hashes remain
unchanged through the documented author-rewrite mapping.

## Reconciled counts and remaining work

There are **72 protocol-verified N=3 cells**: VO24, VO-LC18, VIO18, VIO-LC12,
GNSS-VIO0. All 225 verified EuRoC attempts are retained: 191 clean final exports
and **34 native failures**, including 33 with evaluated saved trajectories and
one AirSLAM VIO-LC failure without final output. Thus **224 evaluated trajectories**
support their stated EuRoC accuracy scope. The 34 failures comprise four ORB,
18 OV2SLAM, nine Voxel-SVIO, two historical OpenVINS and one AirSLAM attempt;
this is an execution-outcome count, not a claim that all 34 lost tracking.

All 81 absent planned slots and **73 confirmed setup reruns** remain separate.
Nine additional agricultural configured-attempt failure observations are retained
for limited reporting, without verifying their calibration/reference protocol.
Accordingly the future manifest retains 234 reusable observations, 73 reruns,
81 missing slots and 272 blocked actions. At the stricter per-attempt protocol
level those nine reusable failure-only observations also remain blocked, giving
281 blocked protocol slots. These two counts answer different questions and do
not authorize new execution. Exact lists are in the generated handoff and manifest.

OpenVINS has three historical N=1 cohorts and three patched N=2 cohorts. Completing
the patched cohorts would require three additional attempts if authorized; these
are separate from the 81 absent logical slots. No old attempt is replaced and no
new slot is silently appended to the consumed fixed campaign.

Remaining concrete blockers: Rosario image/projection/baseline consistency;
Horti session-specific reference origin/timing; ZED 3D antenna/camera geometry,
fix-quality policy and per-serial IMU rotation; historical GNSS input/covariance/
antenna/fusion-output support; and the native failure/readiness paths listed in
the handoff. The bounded [AirSLAM diagnosis](airslam-refinement-diagnostic-20261002.md)
localizes the reproduced fault to the map publisher but does not establish or fix
its exact cause. None of these evidence gaps can be closed by collecting successes.

Prepared contributions: [AirSLAM minimal rectification PR](upstream/airslam-rectification-pr.md)
with positive/negative native geometry regression, and [OpenVINS shutdown report](upstream/openvins-shutdown-report.md)
with the benchmark-tested candidate and explicit lifecycle limitations. Exact local
branches/commits and patch hashes are in `upstream/prepared-contributions-20261002.json`.
The benchmark source revisions and historical provenance remain unchanged.
