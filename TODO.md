# vSLAM Benchmark - TODO

> **Reporting review:** completed campaign results and numerical scores are preserved.
> Green ticks now certify three correctly conducted attempts in one implementation cohort,
> including recorded failures. They do not promise three successful or full-coverage trajectories.
> The four-mode comparison retains **552/600 evaluations**; new short checks are separate diagnostics.
> See [ZED reference/claim limits](docs/zed-preparation-20261002.md),
> [protocol definitions](docs/protocol-review-20261002.md),
> [campaign evidence](docs/euroc-focused-campaign-20261001.md) and
> [current handoff](docs/acceptance-handoff-20261001.md).

Rosario VIO: [candidate configurations and remaining prerequisites](docs/rosario-vio-candidates-20261002.md)
are integrated and opt-in native checks have completed. Recording-specific
profile selection remains pending; the 14 confirmed replacements and four missing
OpenVINS repetitions are distinct. Historical attempts and scores are preserved.

Final destination: this `main` checkout. [Integration and validation](docs/rosario-main-integration-20261002.md)
preserve the completed ZED first attempts without automatically verifying them.
Rosario production profile selection remains unresolved. The current
[native review](docs/execution-readiness-20261002.md) holds 12 previously green
EuRoC ORB cells for unknown historical library/ABI identities: **69 cells retain
verified N=3**. No blanket rerun is implied. Future plan identities are being refreshed.

---

## Status legend

`[x]` done  `[ ]` not started  `[~]` in-progress / partially done  `[!]` blocked

---

## Run combinations matrix

<!-- todo-matrix-legend:start -->
**A = recorded attempts; E = trajectories evaluated; S = clean final exports;
F = observed failures; U = unknown outcomes, when present.**

Example: **A3/E3/S0/F3** means three attempts, three evaluated trajectories,
no clean final exports and three observed failures. A failed attempt can still
produce an evaluable trajectory, so these counts overlap. Verified completed
exports with shutdown errors remain in F, never S, and are labelled
`completed export; shutdown error`; other tracking/export failures stay distinct.
S does not certify
accuracy or full coverage. `?` means a legacy count is not documented.

**✅ N=3 means three verified attempts under consistent settings, including valid
observed failures—not necessarily three successful runs.** N counts verified,
completed attempts; A also includes attempts awaiting review or using invalid
settings. Unverified or invalid history is labelled `3 recorded` or `1 recorded`;
recorded attempts are not presented as verified repetitions.
`✔ N=1 + ✔ N=2` denotes separate implementation groups; it cannot be pooled into N=3.

| Mark | Meaning |
|---|---|
| 🟥 | Leading marker: a confirmed rerun is required; takes precedence over review |
| 🟨 | Leading marker: unresolved review, with no confirmed rerun assumed |
| ✅ N=3 | Three verified attempts in one implementation group, including valid observed failures |
| ✔ N=1 / ✔ N=2 | Verified partial group; separate groups remain separate |
| 🔴 | Beside a confirmed rerun requirement: not ready, including unverified readiness |
| 🔄 | Beside a confirmed rerun requirement: reviewed execution checks passed (ready) |
| 🟡 | Beside an unresolved evidence/reference/evaluation/execution review item |
| ❌ | No recorded attempts and not ready, with no separate review/rerun marker taking precedence |
| 🔜 | No recorded attempts and ready, with no separate review/rerun marker taking precedence |
| ➖ | Excluded; historical counts and reported failures remain visible |

Cells show saved-run verification and **next** action readiness separately when
needed. For example, `🟨 ✔ N=1; A2/E1/S1/F1; 🟡 review; next: new group ready`
retains the verified observation and failed attempt while reporting the reviewed
future plan. `rerun` is reserved for a confirmed setup defect; a planned new
implementation group is labelled `new group`. Mixed readiness is stated as a
fraction; it never makes the entire action group ready.

Cell links give selected physical run IDs, exits, failure evidence, implementation
groups, review blockers and claim limits. `missing` counts absent attempts only.
Sparse keyframes, partial exports and low accuracy alone do not require reruns.
Historical acceptance decisions and raw evidence are preserved; later evidence
can put a previously green cell back under review. ZED ticks support qualified
nominal position claims, with RTK float,
mounting and clock limits; they do not certify surveyed 6-DoF reference accuracy.
Readiness comes from the selected reviewed campaign and its unchanged evidence,
never from N=3 or configuration-file existence. It does not authorize a launch or
claim full-sequence stability. The plan summary below is separate from live progress.
<!-- todo-matrix-legend:end -->

<!-- todo-execution-readiness:start -->
**Future execution readiness — reviewed snapshot**

These plans describe reviewed checks, not live campaign progress or permission to
launch. Short checks do not establish full-sequence stability. A live attempt
enters the matrices only after its evidence has been reviewed.

| Plan | Reviewed new-attempt readiness | Details |
|---|---|---|
| future-n3-five-modes | Unverified: missing/stale evidence | [Evidence and prerequisites](docs/todo-status-details.md#future-execution-readiness) |
| zed-coherent-n3-20261002-main-integration | Unverified: missing/stale evidence | [Evidence and prerequisites](docs/todo-status-details.md#future-execution-readiness) |

The coherent ZED plan replaces the ZED selection in the five-mode plan; do not
add their counts or execute both. Saved-result ticks remain independent of these
readiness checks. The TODO and linked details are documentation only. Generator
and test changes stay isolated until the active batch and capture finish; any later
implementation update needs reviewed campaign pins before another launch.
<!-- todo-execution-readiness:end -->

### VO (no IMU, no loop closure) - `results/vo/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | [🟨 1 recorded](docs/todo-status-details.md#vo-rosariov2-sequence1-orbslam3); A1/E0/S0/F1; next: missing 2 not ready; 🟡 review: camera model, evidence | [🟨 1 recorded](docs/todo-status-details.md#vo-rosariov2-sequence5-orbslam3); A1/E0/S0/F1; next: missing 2 not ready; 🟡 review: camera model, evidence | [🟨 1 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry02-orbslam3); A1/E0/S0/F1; next: missing 2 not ready; 🟡 review: evidence, reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry03-orbslam3); A3/E3/S2/F1; 🟡 review: evidence, reference/clock; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-euroc-mav-mh-01-easy-orbslam3); A3/E3/S3/F0; 🟡 next: review (not ready); 🟡 review: evidence | [🟨 3 recorded](docs/todo-status-details.md#vo-euroc-mav-mh-03-medium-orbslam3); A3/E3/S2/F1; 🟡 next: review (not ready); 🟡 review: evidence; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-euroc-mav-mh-05-difficult-orbslam3); A3/E3/S3/F0; 🟡 next: review (not ready); 🟡 review: evidence | [🟥 3 recorded](docs/todo-status-details.md#vo-zed2i-field1-110426-full-10fps-q90-orbslam3); A3/E3/S1/F2; 🔴 rerun not ready: FPS; completed export; shutdown error; nominal position |
| Basalt | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence1-basalt); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence5-basalt); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry02-basalt); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry03-basalt); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-01-easy-basalt); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-03-medium-basalt); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-05-difficult-basalt); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-zed2i-field1-110426-full-10fps-q90-basalt); A3/E3/S3/F0; nominal position |
| MAC-VO | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence1-macvo); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence5-macvo); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry02-macvo); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry03-macvo); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-01-easy-macvo); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-03-medium-macvo); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-05-difficult-macvo); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-zed2i-field1-110426-full-10fps-q90-macvo); A3/E3/S3/F0; nominal position |
| AirSLAM | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence1-airslam); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence5-airslam); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry02-airslam); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry03-airslam); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-01-easy-airslam); A3/E3/S3/F0; keyframes | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-03-medium-airslam); A3/E3/S3/F0; keyframes | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-05-difficult-airslam); A3/E3/S3/F0; keyframes | [✅ N=3](docs/todo-status-details.md#vo-zed2i-field1-110426-full-10fps-q90-airslam); A3/E3/S3/F0; keyframes; nominal position |
| DPVO | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence1-dpvo); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence5-dpvo); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry02-dpvo); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry03-dpvo); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-01-easy-dpvo); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-03-medium-dpvo); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-05-difficult-dpvo); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-zed2i-field1-110426-full-10fps-q90-dpvo); A3/E3/S3/F0; nominal position |
| OKVIS2 | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence1-okvis2); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence5-okvis2); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry02-okvis2); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry03-okvis2); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-01-easy-okvis2); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-03-medium-okvis2); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-05-difficult-okvis2); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-zed2i-field1-110426-full-10fps-q90-okvis2); A3/E3/S2/F1; collapse r2; nominal position |
| OKVIS2-X | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence1-okvis2x); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence5-okvis2x); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry02-okvis2x); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry03-okvis2x); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-01-easy-okvis2x); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-03-medium-okvis2x); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-05-difficult-okvis2x); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-zed2i-field1-110426-full-10fps-q90-okvis2x); A3/E3/S3/F0; nominal position |
| OV2SLAM | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence1-ov2slam); A3/E3/S0/F3; 🟡 review: camera model; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-rosariov2-sequence5-ov2slam); A3/E3/S0/F3; 🟡 review: camera model; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry02-ov2slam); A3/E3/S0/F3; 🟡 review: reference/clock; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-hortimulti-strawberry03-ov2slam); A3/E3/S0/F3; 🟡 review: reference/clock; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-01-easy-ov2slam); A3/E3/S0/F3; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-03-medium-ov2slam); A3/E3/S0/F3; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vo-euroc-mav-mh-05-difficult-ov2slam); A3/E3/S0/F3; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vo-zed2i-field1-110426-full-10fps-q90-ov2slam); A3/E3/S0/F3; completed export; shutdown error; nominal position |
| MASt3R-SLAM | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A0/E0/S0/F0; config missing |
| MegaSaM | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A0/E0/S0/F0; config missing |
| DROID-SLAM | [➖ excluded](docs/todo-status-details.md#excluded-history); A3/E3/S0/F0/U3; historical | [➖ excluded](docs/todo-status-details.md#excluded-history); A3/E3/S0/F0/U3; historical | [➖ excluded](docs/todo-status-details.md#excluded-history); A3/E3/S0/F0/U3; historical | [➖ excluded](docs/todo-status-details.md#excluded-history); A3/E3/S0/F0/U3; historical | [➖ excluded](docs/todo-status-details.md#excluded-history); A1/E1/S0/F0/U1; historical | [➖ excluded](docs/todo-status-details.md#excluded-history); A1/E1/S0/F0/U1; historical | [➖ excluded](docs/todo-status-details.md#excluded-history); A1/E1/S0/F0/U1; historical | [➖ excluded](docs/todo-status-details.md#excluded-history); A0/E0/S0/F0; no recorded run |
| cuVSLAM | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |
| SVO Pro | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |
| DSOL | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |

> **Remaining:** ORB-SLAM3 Rosario seq1/seq5 and Horti str02 retain observed startup failures
> (no saved trajectories to recover); r2/r3 remain missing. OKVIS2 ZED run2 is a retained collapse, not an unexecuted repetition.
> **Basalt:** the explicit Rosario compatibility profile uses 0.03; other datasets retain
> the upstream 0.05 setting, matching saved runs. ZED relative stereo geometry is verified
> equivalent for pure VO. Other reference/qualification gates still apply.
> **ORB ZED VO/VO-LC:** six saved runs used 15 FPS for 10 Hz input; plan a corrected
> cohort. Evaluation cannot repair the estimator-side setting.
> DROID-SLAM is historical and excluded from the target. MASt3R/MegaSaM OOM notes refer
> to the earlier 12 GB machine, not a verified OOM measurement on this 24 GB server.
> DPVO is monocular; DPV-SLAM is its VO-LC variant. Current headline labels use Sim(3) for both monocular modes.

### VIO (stereo + IMU, no loop closure) - `results/vio/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | [🟨 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence1-orbslam3); A3/E3/S3/F0; 🟡 review: camera model, evidence | [🟨 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence5-orbslam3); A3/E3/S3/F0; 🟡 review: camera model, evidence | [🟥 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry02-orbslam3); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: evidence, reference/clock | [🟥 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry03-orbslam3); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: evidence, reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vio-euroc-mav-mh-01-easy-orbslam3); A3/E3/S3/F0; 🟡 next: review (not ready); 🟡 review: evidence | [🟨 3 recorded](docs/todo-status-details.md#vio-euroc-mav-mh-03-medium-orbslam3); A3/E3/S3/F0; 🟡 next: review (not ready); 🟡 review: evidence; partial | [🟨 3 recorded](docs/todo-status-details.md#vio-euroc-mav-mh-05-difficult-orbslam3); A3/E3/S3/F0; 🟡 next: review (not ready); 🟡 review: evidence | [✔ N=1](docs/todo-status-details.md#vio-zed2i-field1-110426-full-10fps-q90-orbslam3); A1/E1/S1/F0; next: missing 2 not ready; nominal position; selected r10001,r2,r3 |
| Basalt | [🟥 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence1-basalt); A3/E3/S3/F0; 🔴 rerun not ready: IMU extrinsic; 🟡 review: camera model | [🟥 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence5-basalt); A3/E3/S3/F0; 🔴 rerun not ready: IMU extrinsic; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry02-basalt); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry03-basalt); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-01-easy-basalt); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-03-medium-basalt); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-05-difficult-basalt); A3/E3/S3/F0 | [🟥 1 recorded](docs/todo-status-details.md#vio-zed2i-field1-110426-full-10fps-q90-basalt); A1/E1/S1/F0; 🔴 rerun not ready: camera–IMU; next: missing 2 not ready; nominal position |
| OKVIS2 | [🟨 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence1-okvis2); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence5-okvis2); A3/E3/S3/F0; 🟡 review: camera model | [🟥 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry02-okvis2); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [🟥 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry03-okvis2); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-01-easy-okvis2); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-03-medium-okvis2); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-05-difficult-okvis2); A3/E3/S3/F0 | [✔ N=1](docs/todo-status-details.md#vio-zed2i-field1-110426-full-10fps-q90-okvis2); A1/E1/S1/F0; next: missing 2 not ready; nominal position; selected r10001,r2,r3 |
| OKVIS2-X | [🟨 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence1-okvis2x); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence5-okvis2x); A3/E3/S3/F0; 🟡 review: camera model | [🟥 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry02-okvis2x); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [🟥 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry03-okvis2x); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-01-easy-okvis2x); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-03-medium-okvis2x); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-05-difficult-okvis2x); A3/E3/S3/F0 | [✔ N=1](docs/todo-status-details.md#vio-zed2i-field1-110426-full-10fps-q90-okvis2x); A1/E1/S1/F0; next: missing 2 not ready; nominal position; selected r10001,r2,r3 |
| OpenVINS | [🟥 1 recorded](docs/todo-status-details.md#vio-rosariov2-sequence1-openvins); A1/E1/S0/F1; 🔴 rerun not ready: IMU extrinsic; next: missing 2 not ready; 🟡 review: camera model; collapse r1 | [🟥 1 recorded](docs/todo-status-details.md#vio-rosariov2-sequence5-openvins); A1/E1/S0/F1; 🔴 rerun not ready: IMU extrinsic; next: missing 2 not ready; 🟡 review: camera model; collapse r1 | [🟨 1 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry02-openvins); A1/E1/S0/F1; next: missing 2 not ready; 🟡 review: reference/clock | [🟨 1 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry03-openvins); A1/E1/S0/F1; next: missing 2 not ready; 🟡 review: reference/clock | [🟨 ✔ N=1 + ✔ N=2](docs/todo-status-details.md#vio-euroc-mav-mh-01-easy-openvins); A3/E3/S2/F1; 🟡 next: group review (not ready); limits; separate groups | [🟨 ✔ N=1 + ✔ N=2](docs/todo-status-details.md#vio-euroc-mav-mh-03-medium-openvins); A3/E3/S2/F1; 🟡 next: group review (not ready); limits; separate groups | [🟨 ✔ N=1 + ✔ N=2](docs/todo-status-details.md#vio-euroc-mav-mh-05-difficult-openvins); A3/E3/S3/F0; 🟡 next: group review (not ready); partial; separate groups | [🟥 1 recorded](docs/todo-status-details.md#vio-zed2i-field1-110426-full-10fps-q90-openvins); A1/E1/S0/F1; 🔴 rerun not ready: camera–IMU; next: missing 2 not ready; collapse r1; nominal position |
| AirSLAM | [🟨 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence1-airslam); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence5-airslam); A3/E3/S3/F0; 🟡 review: camera model | [🟥 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry02-airslam); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [🟥 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry03-airslam); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-01-easy-airslam); A3/E3/S3/F0; keyframes; selected r4,r5,r6 | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-03-medium-airslam); A3/E3/S3/F0; keyframes; selected r4,r5,r6 | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-05-difficult-airslam); A3/E3/S3/F0; keyframes; selected r4,r5,r6 | [🟥 1 recorded](docs/todo-status-details.md#vio-zed2i-field1-110426-full-10fps-q90-airslam); A1/E1/S1/F0; 🔴 rerun not ready: camera–IMU; next: missing 2 not ready; nominal position |
| Voxel-SVIO | [🟥 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence1-voxel-svio); A3/E3/S0/F3; 🔴 rerun not ready: IMU extrinsic; 🟡 review: camera model; completed export; shutdown error | [🟥 3 recorded](docs/todo-status-details.md#vio-rosariov2-sequence5-voxel-svio); A3/E3/S0/F3; 🔴 rerun not ready: IMU extrinsic; 🟡 review: camera model; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry02-voxel-svio); A3/E3/S0/F3; 🟡 review: reference/clock; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vio-hortimulti-strawberry03-voxel-svio); A3/E3/S0/F3; 🟡 review: reference/clock; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-01-easy-voxel-svio); A3/E3/S0/F3; completed export; shutdown error; partial | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-03-medium-voxel-svio); A3/E3/S0/F3; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vio-euroc-mav-mh-05-difficult-voxel-svio); A3/E3/S0/F3; completed export; shutdown error | [🟥 1 recorded](docs/todo-status-details.md#vio-zed2i-field1-110426-full-10fps-q90-voxel-svio); A1/E1/S0/F1; 🔴 rerun not ready: camera–IMU; next: missing 2 not ready; completed export; shutdown error; nominal position |
| cuVSLAM | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |
| SVO Pro | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |
| MASt3R-Fusion | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |

> Horti IMU extraction/rectification corrections exist, but 48 saved inertial attempts
> still require camera–IMU timing correction (six overlap earlier rectification defects). All seven non-ZED
> sequences have A3 for six algorithms; **OpenVINS has three EuRoC attempts split into verified N=1 and N=2 groups, and A1 elsewhere**. Six
> previously unscored run1 trajectories have repaired evaluations, retaining exit 134.
> Rosario seq1/seq5 retain catastrophic scale failures; the saved fixed identity
> IMU/camera calibration is now a confirmed defect, not a valid physical convention. EuRoC recovered trajectories are accepted with exit/coverage limitations; agricultural accuracy remains blocked.
> **ZED:** all seven historical VIO run-1 configurations omitted the recovered factory
> camera–IMU rotation; their saved outcomes remain visible but require new calibrated
> estimation. Basalt, OKVIS2, OKVIS2-X, AirSLAM, OpenVINS and ORB passed bounded checks;
> Voxel shutdown is repaired, but initialization/export remains unverified.
> See [ZED calibration](docs/zed2i-imu-extrinsics.md) and the
> [prepared campaign](docs/zed-campaign-20261002.md).

### VO-LC (visual only + loop closure) - `results/vo-lc/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| DPV-SLAM | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence1-dpvo); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence5-dpvo); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry02-dpvo); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry03-dpvo); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-01-easy-dpvo); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-03-medium-dpvo); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-05-difficult-dpvo); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-lc-zed2i-field1-110426-full-10fps-q90-dpvo); A3/E3/S3/F0; nominal position |
| OKVIS2 | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence1-okvis2); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence5-okvis2); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry02-okvis2); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry03-okvis2); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-01-easy-okvis2); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-03-medium-okvis2); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-05-difficult-okvis2); A3/E3/S3/F0 | [🟨 ✔ N=1](docs/todo-status-details.md#vo-lc-zed2i-field1-110426-full-10fps-q90-okvis2); A2/E1/S1/F1; next: new group 3 not ready; 🟡 review: execution; nominal position; missing 1; separate groups |
| OKVIS2-X | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence1-okvis2x); A3/E3/S3/F0; 🟡 next: group review (not ready); 🟡 review: camera model; separate groups | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence5-okvis2x); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry02-okvis2x); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry03-okvis2x); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-01-easy-okvis2x); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-03-medium-okvis2x); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-05-difficult-okvis2x); A3/E3/S3/F0 | [🟨 1 recorded](docs/todo-status-details.md#vo-lc-zed2i-field1-110426-full-10fps-q90-okvis2x); A1/E1/S0/F1; next: new group 3 not ready; 🟡 review: execution; nominal position; missing 2 |
| ORB-SLAM3 | [🟨 1 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence1-orbslam3); A1/E0/S0/F1; next: missing 2 not ready; 🟡 review: camera model, evidence | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence5-orbslam3); A3/E3/S3/F0; 🟡 review: camera model, evidence | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry02-orbslam3); A3/E3/S1/F2; 🟡 review: evidence, reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry03-orbslam3); A3/E3/S2/F1; 🟡 review: evidence, reference/clock; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-euroc-mav-mh-01-easy-orbslam3); A3/E3/S2/F1; 🟡 next: review (not ready); 🟡 review: evidence; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-euroc-mav-mh-03-medium-orbslam3); A3/E3/S2/F1; 🟡 next: review (not ready); 🟡 review: evidence; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-euroc-mav-mh-05-difficult-orbslam3); A3/E3/S2/F1; 🟡 next: review (not ready); 🟡 review: evidence; completed export; shutdown error | [🟥 3 recorded](docs/todo-status-details.md#vo-lc-zed2i-field1-110426-full-10fps-q90-orbslam3); A3/E3/S2/F1; 🔴 rerun not ready: FPS; completed export; shutdown error; nominal position; separate groups |
| AirSLAM | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence1-airslam); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence5-airslam); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry02-airslam); A3/E3/S3/F0; 🟡 review: reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry03-airslam); A3/E3/S3/F0; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-01-easy-airslam); A3/E3/S3/F0; keyframes | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-03-medium-airslam); A3/E3/S3/F0; keyframes | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-05-difficult-airslam); A3/E3/S3/F0; keyframes | [✔ N=1 + ✔ N=2](docs/todo-status-details.md#vo-lc-zed2i-field1-110426-full-10fps-q90-airslam); A3/E3/S3/F0; next: new group 3 not ready; keyframes; nominal position; separate groups |
| OV2SLAM | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence1-ov2slam); A3/E3/S0/F3; 🟡 review: camera model; collapse r2; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-rosariov2-sequence5-ov2slam); A3/E3/S0/F3; 🟡 review: camera model; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry02-ov2slam); A3/E3/S0/F3; 🟡 review: reference/clock; completed export; shutdown error | [🟨 3 recorded](docs/todo-status-details.md#vo-lc-hortimulti-strawberry03-ov2slam); A3/E3/S0/F3; 🟡 review: reference/clock; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-01-easy-ov2slam); A3/E3/S0/F3; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-03-medium-ov2slam); A3/E3/S0/F3; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vo-lc-euroc-mav-mh-05-difficult-ov2slam); A3/E3/S0/F3; completed export; shutdown error | [✅ N=3](docs/todo-status-details.md#vo-lc-zed2i-field1-110426-full-10fps-q90-ov2slam); A3/E3/S0/F3; completed export; shutdown error; nominal position |
| MASt3R-SLAM | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A?/E?/S?/F?; reported OOM (12 GB) | [➖ excluded](docs/todo-status-details.md#excluded-history); A0/E0/S0/F0; config missing |
| cuVSLAM | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |

> **OKVIS2:** all seven non-ZED cells have A3 after the September 23 recovery (verification varies),
> using the later final-full-BA-disabled configuration. On ZED, run1 finished (exit 0,
> 46,282 output poses) and has a repaired evaluation against the versioned nominal 3D reference.
> Its historical COMPLETE marker is still absent. Run2 was killed and run3 is absent.
> The repaired wrapper preserves attempts and evaluates each repetition immediately.
> **OKVIS2-X ZED:** exit 141 remains unresolved. Its 354-pose / 35.3 s causal prefix is now evaluated; final BA was not completed and this is not a qualified completed trial.
> **ORB-SLAM3 Rosario seq1:** native crash; no complete evaluated run.
> **OV2SLAM Rosario seq1:** A3 includes run2 collapse; retain it in failure-rate reporting.
> AirSLAM and OV2SLAM VO-LC have three attempts on all eight sequences; AirSLAM ZED remains separate N=1 and N=2 implementation cohorts.
> Loop-event counts and final-BA settings require explicit interpretation; prior N=1
> conclusions are not automatically conclusions about this server cohort.

### VIO-LC (stereo + IMU + loop closure) - `results/vio-lc/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-rosariov2-sequence1-orbslam3); A3/E3/S3/F0; 🟡 review: camera model, evidence | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-rosariov2-sequence5-orbslam3); A3/E3/S3/F0; 🟡 review: camera model, evidence | [🟥 3 recorded](docs/todo-status-details.md#vio-lc-hortimulti-strawberry02-orbslam3); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing, rectified IMU; 🟡 review: evidence, reference/clock | [🟥 3 recorded](docs/todo-status-details.md#vio-lc-hortimulti-strawberry03-orbslam3); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing, rectified IMU; 🟡 review: evidence, reference/clock | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-euroc-mav-mh-01-easy-orbslam3); A3/E3/S3/F0; 🟡 next: review (not ready); 🟡 review: evidence | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-euroc-mav-mh-03-medium-orbslam3); A3/E3/S3/F0; 🟡 next: review (not ready); 🟡 review: evidence; partial | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-euroc-mav-mh-05-difficult-orbslam3); A3/E3/S3/F0; 🟡 next: review (not ready); 🟡 review: evidence | [🟥 1 recorded](docs/todo-status-details.md#vio-lc-zed2i-field1-110426-full-10fps-q90-orbslam3); A1/E0/S0/F1; 🔴 rerun not ready: camera–IMU; next: missing 2 not ready |
| OKVIS2 | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-rosariov2-sequence1-okvis2); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-rosariov2-sequence5-okvis2); A3/E3/S3/F0; 🟡 review: camera model | [🟥 3 recorded](docs/todo-status-details.md#vio-lc-hortimulti-strawberry02-okvis2); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [🟥 3 recorded](docs/todo-status-details.md#vio-lc-hortimulti-strawberry03-okvis2); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vio-lc-euroc-mav-mh-01-easy-okvis2); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-lc-euroc-mav-mh-03-medium-okvis2); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-lc-euroc-mav-mh-05-difficult-okvis2); A3/E3/S3/F0 | [🟥 1 recorded](docs/todo-status-details.md#vio-lc-zed2i-field1-110426-full-10fps-q90-okvis2); A1/E1/S1/F0; 🔴 rerun not ready: camera–IMU; next: missing 2 not ready; nominal position |
| OKVIS2-X | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-rosariov2-sequence1-okvis2x); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-rosariov2-sequence5-okvis2x); A3/E3/S3/F0; 🟡 review: camera model | [🟥 3 recorded](docs/todo-status-details.md#vio-lc-hortimulti-strawberry02-okvis2x); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [🟥 3 recorded](docs/todo-status-details.md#vio-lc-hortimulti-strawberry03-okvis2x); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vio-lc-euroc-mav-mh-01-easy-okvis2x); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-lc-euroc-mav-mh-03-medium-okvis2x); A3/E3/S3/F0 | [✅ N=3](docs/todo-status-details.md#vio-lc-euroc-mav-mh-05-difficult-okvis2x); A3/E3/S3/F0 | [🟥 1 recorded](docs/todo-status-details.md#vio-lc-zed2i-field1-110426-full-10fps-q90-okvis2x); A1/E1/S1/F0; 🔴 rerun not ready: camera–IMU; next: missing 2 not ready; nominal position |
| AirSLAM | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-rosariov2-sequence1-airslam); A3/E3/S3/F0; 🟡 review: camera model | [🟨 3 recorded](docs/todo-status-details.md#vio-lc-rosariov2-sequence5-airslam); A3/E3/S3/F0; 🟡 review: camera model | [🟥 3 recorded](docs/todo-status-details.md#vio-lc-hortimulti-strawberry02-airslam); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [🟥 3 recorded](docs/todo-status-details.md#vio-lc-hortimulti-strawberry03-airslam); A3/E3/S3/F0; 🔴 rerun not ready: IMU timing; 🟡 review: reference/clock | [✅ N=3](docs/todo-status-details.md#vio-lc-euroc-mav-mh-01-easy-airslam); A3/E3/S3/F0; keyframes; offline refinement; selected r4,r5,r6 | [✅ N=3](docs/todo-status-details.md#vio-lc-euroc-mav-mh-03-medium-airslam); A3/E3/S3/F0; keyframes; offline refinement; selected r4,r5,r6 | [✅ N=3](docs/todo-status-details.md#vio-lc-euroc-mav-mh-05-difficult-airslam); A3/E2/S2/F1; keyframes; offline refinement; no final export; selected r4,r5,r6 | [🟥 1 recorded](docs/todo-status-details.md#vio-lc-zed2i-field1-110426-full-10fps-q90-airslam); A1/E1/S1/F0; 🔴 rerun not ready: camera–IMU; next: missing 2 not ready; nominal position |
| cuVSLAM | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |
| SVO Pro | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |
| MASt3R-Fusion | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet | ❌ not run yet |

> All four methods have A3 on the seven non-ZED sequences (verification varies).
> **ZED:** all four historical run-1 configurations omitted the recovered factory rotation;
> prepare three fresh calibrated attempts per cell. All four bounded native checks passed.
> AirSLAM's map refinement is an offline step;
> final corrected trajectories do not by themselves establish live navigation latency.

### GNSS-VIO (stereo + IMU + GNSS) - `results/gnss-vio/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 |
|---|---|---|---|---|
| CIFASIS GNSS-SI | [🟥 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence1-cifasis-gnss-si); A1/E1/S0/F1; 🔴 rerun not ready: antenna lever; next: missing 2 not ready; 🟡 review: GNSS, camera model | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence5-cifasis-gnss-si); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, camera model | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry02-cifasis-gnss-si); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, reference/clock | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry03-cifasis-gnss-si); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, reference/clock |
| RTAB-Map | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence1-rtabmap-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, camera model, reference/frame | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence5-rtabmap-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, camera model, reference/frame | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry02-rtabmap-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, reference/clock, reference/frame | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry03-rtabmap-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, reference/clock, reference/frame |
| VINS-Fusion | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence1-vins-fusion-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, camera model, reference/frame | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence5-vins-fusion-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, camera model, reference/frame | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry02-vins-fusion-gps); A1/E1/S0/F1; next: missing 2 not ready; 🟡 review: GNSS, reference/clock, reference/frame; invalid export | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry03-vins-fusion-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, reference/clock, reference/frame |
| OpenVINS+GPS | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence1-openvins-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, camera model, reference/frame | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence5-openvins-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, camera model, reference/frame | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry02-openvins-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, reference/clock, reference/frame | [🟨 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry03-openvins-gps); A1/E1/S0/F0/U1; next: missing 2 not ready; 🟡 review: GNSS, reference/clock, reference/frame |
| OKVIS2-X (tight) | [🟥 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence1-okvis2x); A1/E1/S0/F0/U1; 🔴 rerun not ready: antenna lever; next: missing 2 not ready; 🟡 review: GNSS, camera model, reference/frame | [🟥 1 recorded](docs/todo-status-details.md#gnss-vio-rosariov2-sequence5-okvis2x); A1/E1/S0/F0/U1; 🔴 rerun not ready: antenna lever; next: missing 2 not ready; 🟡 review: GNSS, camera model, reference/frame | [🟥 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry02-okvis2x); A1/E1/S0/F0/U1; 🔴 rerun not ready: antenna lever; next: missing 2 not ready; 🟡 review: GNSS, reference/clock, reference/frame | [🟥 1 recorded](docs/todo-status-details.md#gnss-vio-hortimulti-strawberry03-okvis2x); A1/E1/S0/F0/U1; 🔴 rerun not ready: antenna lever; next: missing 2 not ready; 🟡 review: GNSS, reference/clock, reference/frame |

> **Excluded from the executed server N=3 campaign.** These are historical A1 results
> from earlier machines, not repeated server measurements. Sixteen default cells have
> COMPLETE; all four VINS-Fusion default cells have evaluation JSON but lack that marker.
> Three conventional-GPS variants are separately complete; three additional variants lack
> COMPLETE. Validate artifacts rather than adding markers manually.
> OpenVINS+GPS HortiMulti still needs corrected-extrinsic reruns/review. Current OKVIS2-X
> profiles now contain composed IMU-frame antenna levers. Four saved native OKVIS2-X
> logs loaded zero; CIFASIS Rosario seq1 loaded the v1 lever. These five require reruns. The future target is N=3; the old N=5 proposal remains
> a separate historical scope. VINS-Fusion Horti str02 has 153 invalid quaternion norms;
> its accuracy evaluation is blocked pending export recovery.
> Seq5 PPK and seq1 conventional GPS remain distinct inputs; seq1 PPK requires its recording.
> HortiMulti has consumer GNSS. EuRoC has no GNSS and is not part of this track.

---

## High-priority open tasks (Phase 2)

| # | Task | Status |
|---|---|---|
| 1 | Extract HortiMulti IMU (`/ms/imu/data` -> `mav0/imu0/data.csv`) | `[x]` |
| 2 | Run core VIO matrix | `[~]` OpenVINS now has three evaluated repetitions per EuRoC cell; original exit/coverage limits and separate cohorts remain. See the matrices for other cells and qualification. |
| 3 | Diagnose and fix hortimulti VIO scale collapse | `[~]` historical extrinsic defect corrected; this does not resolve the later confirmed time-offset or reference-origin findings. Corrected estimation and physical reference evidence remain necessary. |
| 3b | Build OKVIS2 standalone (was never built) | `[x]` (`build_okvis2.sh`; -DHAVE_LIBREALSENSE=OFF -DUSE_CUDA=OFF) |
| 3c | Re-run 2 stale bad VIO runs (Voxel EuRoC, OpenVINS seq5) | `[x]` (were bad runs, not algorithm limits) |
| 3d | Add EuRoC MH_03/MH_05 VIO coverage + fix EuRoC times.txt (s->ns) | `[x]` |
| 4 | Run ORB-SLAM3 VIO on rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| 5 | Run Basalt VIO on rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| 6 | Run OpenVINS VIO on rosariov2/seq5 N=3 | `[!]` run1 recovered and evaluated as collapse; confirmed IMU-extrinsic rerun, missing r2/r3, and agricultural prerequisites remain |
| 7 | MASt3R-SLAM / MegaSaM revisit on the 24 GB server (optional — both OOM'd at 12 GB) | `[ ]` |
| 8 | ORB-SLAM3 VO-clean LC-off re-runs | `[~]` LC-off configuration implemented; Rosario seq1/seq5 and Horti str02 missing after crashes |
| 9 | Finish executed N=3 server campaign (no GNSS) | `[~]` 551/600 selected evaluations; 178/200 cells contain three evaluations. Protocol counts are in the current handoff; the original 45 clean-qualified cells are preserved. Original N=5/GNSS target remains separate. |
| 10 | Complete/validate GNSS-VIO N=1 sweep | `[~]` 16 default cells COMPLETE; four VINS-Fusion evaluations unvalidated; server repeats not run |
| 10b | Re-run OpenVINS+GPS HortiMulti with corrected extrinsics; validate all four rows | `[ ]` not completed by the no-GNSS server campaign |
| 11 | Normalize EuRoC dataset aliases and result/config paths to `euroc_mav` | `[x]` central shell/Python canonicalization; obsolete aliases removed |
| 12 | Commit local-only runtime prerequisites | `[x]` **DONE 2026-08-06**: AirSLAM launch files + OpenVINS Dockerfile live in the forks (`kubojion/AirSLAM`, `kubojion/open_vins` @ `vslam-benchmark-patches`, wired in `.gitmodules`); OKVIS2 external CMake patches remain vendored in `vendor/prerequisites/` (nested upstream submodules — patch dir is the clean carrier) |
| 13 | Finish remaining LC/VO cells | `[~]` MAC-VO ZED VO and OV2SLAM VO-LC protocol N=3 verified; AirSLAM VO-LC remains separate N=1 + N=2 cohorts; OKVIS2/OKVIS2-X VO-LC incomplete |
| 14 | OKVIS2-X "0 loop closures" | `[x]` **RESOLVED: log-parsing bug, not the algorithm.** See finding 12 |
| 15 | Add `loopClosing: 0` to hortimulti/euroc/zed2i `_stereo.yaml` | `[x]` clean LC-off baselines are the current VO table (2026-08-04) |
| 16 | Re-evaluate the 2 colleague-machine OKVIS2 VIO-LC runs with corrected LC metric | `[x]` closed by the machine-B re-evaluation campaign (2026-08-06, all EuRoC/HortiMulti runs re-parsed) |
| 17 | ~~Create GitHub forks~~ | `[x]` **DONE 2026-08-06** — forks created, branches pushed (airslam 1b70ff6, open_vins 289bca3), `.gitmodules` re-pointed |
| 18 | ~~Machine B: zed2i segment maps + GT tracking~~ | `[x]` **DONE 2026-08-06** (commits 9b0fc92 + 42c3492): vio/vo-lc maps regenerated on 2.86 m GT; euroc/hortimulti/zed2i GT + times + segments + alias symlinks tracked — verified byte-reproducible CSVs on any clone |
| 19 | ~~Fix zed2i turn detection~~ | `[x]` **DONE 2026-08-06** (5d71cbd): tangent-derived headings (2 m path smoothing) → zed2i now 10 row + 5 turn segments; zed2i runs re-evaluated. Known limitation (documented in-code): short absorbed segments can split one row into several — coalescing deferred to the server-campaign re-eval since it re-segments every dataset |
| 20 | Complete corrected ZED VIO/VIO-LC N=3 | `[~]` 11 original inertial attempts require recovered factory calibration; prepare 33 new attempts, including missing slots; Voxel export readiness remains blocked |
| 21 | Freeze Basalt VO configuration cohort | `[x]` saved threshold policy reviewed and retained; ZED future shared calibration updated, historical VO frames use saved configs; Rosario camera-model prerequisite remains |
| 22 | Preserve/evaluate interrupted outputs and reconcile stale state | `[x]` saved exports and stale state reconciled; OKVIS2-X ZED causal prefix recovered; unresolved historical exits retained |
| 24 | Corrections and rerun list of 3 October: AirSLAM Rosario identity extrinsic, Voxel-SVIO HortiMulti initializer offset, Basalt HortiMulti IMU noise; Rosario decisions (authors' camera model, 0.365° Kalibr transform, zero offset) | `[x]` recorded in [`docs/rerun-plan-20261003.md`](docs/rerun-plan-20261003.md); reruns `[ ]` |
| 23 | Repair metric/reporting issues and exclude five smoke runs from headline discovery | `[x]` schema-3 metrics, per-attempt qualification, CSVs/reports and smoke separation reconciled; see current validation |

---

> **Historical note; current matrix above takes precedence.**
> **ZED2i TURN DETECTION (task 19, 2026-08-06, machine B):** the "2 pseudo-row segments / 0 turns"
> symptom was **not** a turn-angle threshold problem. `_segment_trajectory.py` derived heading from
> the GT quaternion, but the ZED2i GT is built from GPS position only — every row carries an
> **identity quaternion**, so yaw was constant 0 deg and no turn could ever be detected. Fix: a
> `yaw_from_path()` fallback that derives heading from the path tangent (2 m smoothing window) when
> the GT orientations are all identity. Verified neutral for rosariov2/hortimulti/euroc (those have
> real orientations, so the fallback never fires). ZED2i also needs `--min_seg_path_m 5` (the 25 m
> default merges its short 6-row pattern). Result: **15 segments {10 row, 5 turn}** (was 2 row / 0
> turn), and all 18 zed2i runs now report both row and turn ATE — e.g. ORB-SLAM3 VO 0.292 m row /
> 0.283 m turn, Basalt 0.448 / 0.642, DPVO 12.24 / 20.02.
>
> Two related issues found and **deliberately not fixed** (brief rule 5 — no improvised pipeline
> changes):
> 1. **`merge_segments` coalescing bug** — adjacent same-type segments are not merged. Fixing it
>    changes segmentation repo-wide (rosariov2 seq1 107 -> 43 segments, hortimulti 25 -> 14,
>    euroc 0 -> 11) and would require re-evaluating every rosariov2 run, which rule 3 forbids on
>    this machine. A `NOTE` documenting this sits at the call site.
> 2. **`datasets/rosariov2/sequence1/segments_auto.csv` is stale** relative to that sequence's
>    repaired PGT ground truth. Not regenerated here (rule 3).

> **Historical note; counts and metrics below describe July, not current artifacts.**
> **ORB-SLAM3 VO NATIVE (2026-07-31, this machine):** the submodule builds and runs natively (no
> Docker) - `src/ORB_SLAM3/Examples/Stereo/stereo_euroc` linked against a local Pangolin, driven by
> `run_orbslam3.sh`. The agricultural/EuRoC VO cells were filled natively here. **The earlier
> "shim-vs-native divergence" was NOT a Docker artefact - it is ORB-SLAM3's inherent non-determinism
> on agricultural sequences.** Determinism check + 1200->2000 feature sweep (finding 11): EuRoC is
> deterministic (~0.05 m every run); str02 varies {1.85, 4.3, 21.1} m (scale collapses to 0.89,
> coverage 31-100%), seq1 {1.16, 3.0, 4.86} m, seq5 {4.0, 6.9, 14.8} m across N=3 - a config cannot
> fix it. str03 alone is stable (0.11 m x3). So agri cells are recorded as **N=3 median (range)**;
> the old 0.893 m / 1.18 m references were single lucky draws. EuRoC + ZED2i (0.256 m) stay N=1.
> `ORBSLAM3_CONFIG` env override added to the runner for config sweeps.
> OKVIS2/OKVIS2-X VO on agri sequences are best-effort (IMU off) and expectedly weaker than their VIO.

## Phase 2 per-algorithm tasks

### ORB-SLAM3

| Task | Status |
|---|---|
| VO-clean (LC-off) on rosariov2/seq1 N=3 | `[!]` 1 recorded; no evaluated trajectory; recovery crash retained |
| VO-clean on hortimulti str02+03 N=3 | `[~]` str02: 1 recorded (crash); str03: 3 recorded and evaluated; review remains |
| VO-clean on EuRoC MH_01/03/05 N=1 | `[x]` now N=3 on each |
| VIO rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| VIO-LC rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| VIO EuRoC MH_01/03/05 N=1 | `[x]` now N=3 on each |
| VIO-LC EuRoC N=1 | `[x]` now N=3 on each |
| ZED VIO / VIO-LC N=3 | `[!]` 1 recorded in each mode; no evaluated trajectories; crashes retained |

### Basalt

| Task | Status |
|---|---|
| VIO rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| VIO EuRoC MH_01/03/05 N=1 | `[x]` now N=3 on each |
| VIO hortimulti (after IMU extraction) | `[x]` N=3 on both |
| hortimulti VIO scale collapse | `[x]` **FIXED via extrinsic correction** (was misdiagnosed as vibration floor; the 5-run noise sweep searched the wrong parameter). With rectified T_imu_cam: str02 22.9->2.49 m, str03 2.85->0.19 m, scale 0.57->1.03. |
| ZED corrected VIO N=3 | `[~]` N=1; run2/run3 needed |
| VO configuration consistency | `[~]` all eight cells N=3, but six retain 0.05 versus current 0.03 triangulation distance |

### OpenVINS

| Task | Status |
|---|---|
| VIO rosariov2/seq5 N=3 | `[!]` N=1 recovered collapse; IMU-extrinsic rerun and missing r2/r3 remain |
| VIO EuRoC MH_01/03/05 N=3 | `[x]` six missing repetitions completed; all three cells evaluated N=3. Original run1 limitations, MH05 partial coverage and separate implementation cohorts remain. |
| VIO hortimulti (after IMU extraction) | `[!]` N=1 recovered evaluation per cell; exit 134, reference/clock blockers and missing r2/r3 remain |
| ZED corrected VIO N=3 | `[~]` N=1 collapse; preserve outcome, run2/run3 missing |

### AirSLAM

| Task | Status |
|---|---|
| VIO rosariov2/seq1+seq5 N=3 | `[x]` N=3 on both |
| VI-SLAM (VIO-LC) rosariov2 N=3 | `[x]` N=3 on both |
| VIO/VI-SLAM hortimulti (after IMU extraction) | `[x]` N=3 on both sequences/modes |
| Corrected EuRoC VIO / VIO-LC cohort | `[x]` all 18 fixed attempts consumed once: VIO N=3 per sequence; VIO-LC MH01/MH03 N=3, MH05 N=2 plus run4 native refinement failure. Sparse-keyframe limits remain. |
| hortimulti str02/str03 scale collapse | `[x]` **FIXED**: extrinsic was inverted AND missing rectification. str02 46.3->5.30 m, str03 16.3->1.24 m, scale ~1.0. (Also recovered lost `vio_euroc.launch`; TensorRT needed a host reboot after a driver update.) |
| ZED corrected VIO / VIO-LC N=3 | `[~]` each N=1; run2/run3 missing |

### OKVIS2

| Task | Status |
|---|---|
| Scale seq1+seq5 to N=3 | `[x]` N=3 for VO, VO-LC, VIO and VIO-LC |
| Add hortimulti + EuRoC configs | `[x]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]` now N=3 on each |
| hortimulti failure | `[x]` **FIXED via extrinsic correction** (the tracking failures were largely self-inflicted by the wrong extrinsic, not greenhouse texture). str02 49.9->2.14 m, str03 15.5->0.40 m, scale 0->1.03. Independent check: freshly-built binary + config patched hours earlier. |
| ZED VO-LC N=3 | `[~]` 2 recorded, 1 evaluated; run2 killed, run3 absent; review remains |
| ZED corrected VIO / VIO-LC N=3 | `[~]` each N=1; two repetitions missing |

### OKVIS2-X

Source and result integration exists independently of OKVIS2. The top-level build, run and
GPS-conversion automation is committed; repeated VO/VIO results now exist through the
server runners. Remaining gaps are shown in the matrices above.

| Task | Status |
|---|---|
| Source submodule/gitlink pinned (`src/okvis2x`) | `[x]` |
| Reproducible top-level build script (`build_okvis2x.sh`) | `[x]` |
| Top-level multi-mode runner (`run_okvis2x.sh`) | `[x]` (all five run types; `OKVIS2X_CONFIG` override for sweeps) |
| Configs for rosariov2 / EuRoC / HortiMulti / ZED2i | `[x]` (40 files, including experimental `vo_lc`) |
| gnss-vio configs (rosariov2 seq1+seq5) | `[x]` |
| `gps.csv` -> `mav0/gps0/data_raw.csv` converter | `[x]` |
| Register in eval pipeline (LOG_PATTERNS, plot dicts) | `[x]` |
| Measure `r_SA` (GNSS antenna lever arm) on the robot | `[~]` nonzero lever arms configured; verify provenance and rerun historical GNSS cohort |
| First gnss-vio runs (rosariov2 seq1+seq5) | `[x]` historical N=1 results exist; no server GNSS repeats |
| Reproduce VO/VIO results through `run_okvis2x.sh` | `[x]` VO N=3 all eight; VIO N=3 seven core + corrected ZED N=1 |
| Manual N=1 VIO results | `[x]` superseded by server N=3 core and corrected ZED N=1 |
| Recover HortiMulti IMU + GPS from hortimulti.zip | `[x]` (str02 190493/7620, str03 48448/1939 - counts match bag) |
| HortiMulti gnss_vio configs | `[x]` configs and historical N=1 results exist |
| Head-to-head OKVIS2 vs OKVIS2-X on rosariov2 vio | `[x]` seq1: OKVIS2 18.89 / OKVIS2-X 18.89; seq5: 20.29 / 20.40 - near-identical (shared estimator core) |
| ZED VO-LC N=3 | `[!]` 1 recorded; recovered causal prefix evaluated; exit 141 and execution review retained |
| ZED corrected VIO / VIO-LC N=3 | `[~]` each N=1; run2/run3 missing |

### MASt3R-SLAM

| Task | Status |
|---|---|
| Download checkpoints | `[x]` 2.9 GB, Naver Labs direct URLs (see setup.md §10) |
| Build env (CUDA 12.1 nvcc, vendored dust3r/in3d, numpy/opencv pins) | `[x]` |
| Port runner to upstream API (`--save-as`, `--calib`, retrieval.k) | `[x]` |
| Smoke test | `[!]` historical 12 GB OOM; reported server slowness needs retained trial evidence |
| VO / VIO-LC runs on agri sequences | `[ ]` deferred/excluded from current campaign; supported visual tracks are VO / VO-LC (no VIO) |

> Historical setup observations on the earlier machine (not current server measurements): MASt3R-SLAM
> keeps every keyframe on-GPU with no supported bound (`local_opt.window_size` is read
> but never applied upstream; `dataset.img_downsample` breaks the fixed-512 checkpoint;
> `dataset.subsample: 2` still OOM'd on rosariov2). Checkpoints are CC-BY-NC-SA-4.0.

### MegaSaM

| Task | Status |
|---|---|
| Checkpoints (megasam_final, DepthAnything, RAFT) | `[x]` automated in `setup_megasam_env.sh` |
| Build vendored CUDA extensions (`lietorch`, `droid_backends`) | `[x]` needs cuda-nvcc 11.8 + `setuptools<81`; `python setup.py install` (not `pip -e`) |
| Runtime deps (torch_scatter, xformers, huggingface_hub, `numpy<2`) | `[x]` |
| Port runner to the real 3-stage pipeline | `[x]` was calling a non-existent `megasam.demo` module |
| Grayscale workaround for UniDepth stage | `[x]` PIL mis-slices mode-`L` images; runner feeds it an RGB copy |
| First end-to-end run (hortimulti str03) | `[~]` historical partial pipeline check; not currently running; excluded from campaign |
| Runs on remaining sequences | `[ ]` |
| zed2i config | `[ ]` |

> Upstream has no single entrypoint: Depth-Anything -> UniDepth -> camera tracking, each a
> separate script with hard-coded demo paths. Stage 3 (`cvd_opt`) refines depth only and is
> skipped. Cost is three ViT-scale passes per frame, so budget hours per sequence.
> Monocular: comparable under Sim(3) only.

### DPVO / DPV-SLAM (replaces DROID-SLAM)

| Task | Status |
|---|---|
| Setup script, configs and runner | `[x]` |
| DPVO VO N=1 on all 8 sequences | `[x]` now N=3 on all eight |
| DPV-SLAM VO-LC N=1 on all 8 sequences | `[x]` now N=3 on all eight |
| Keep DPV-SLAM out of true VIO-LC bucket | `[x]` moved out of `results-vio-lc/` |

### cuVSLAM, SVO Pro, DSOL, MASt3R-Fusion (added October 2026)

Setup, pilots and parameter sources: `docs/claude-new-algorithms-setup-20261003.md`.
All four take their calibration from `configs/sensors/<dataset>.json`.

| Task | Status |
|---|---|
| cuVSLAM 17.0.0: runner, settings, provenance, evaluator frame (VO, VO-LC, VIO, VIO-LC) | `[x]` one pilot run per mode on EuRoC, HortiMulti, Rosario and ZED |
| SVO Pro: image, runner, settings, provenance, evaluator frame (VO, VIO, VIO-LC) | `[x]` one pilot run per mode on EuRoC, HortiMulti, Rosario and ZED |
| DSOL: image, runner, settings, provenance, evaluator frame (VO) | `[x]` pilots on EuRoC, HortiMulti, Rosario and ZED |
| MASt3R-Fusion: environment, runner, settings, provenance, evaluator frame (VIO, VIO-LC) | `[x]` pilots on EuRoC, HortiMulti and Rosario; ZED not piloted |
| N=3 production runs for the 80 new cells | `[ ]` |
| Claim reviews in the acceptance ledger for the new cells | `[ ]` after the N=3 runs |
| GNSS-VIO for SVO Pro (`rpg_svo_pro_gps`) and MASt3R-Fusion | `[ ]` not set up |

### VO-LC Candidates

| Task | Status |
|---|---|
| OKVIS2 VO-LC full N=1 (all 8 sequences) | `[~]` seven non-ZED N=3; ZED run1 recovered/evaluated, r2 interrupted, r3 missing |
| OKVIS2-X VO-LC full N=1 (all 8 sequences) | `[~]` seven non-ZED cells: 3 recorded each; ZED: 1 recorded, prefix evaluation only |
| ORB-SLAM3 runner + configs for rosariov2/hortimulti/EuRoC/zed2i | `[~]` seven cells N=3; Rosario seq1 retains observed r1 startup failure |
| MASt3R-SLAM runner + configs for rosariov2/hortimulti/EuRoC | `[x]` scaffolded; excluded from current campaign |
| AirSLAM VO-LC | `[x]` visual-only LC now implemented; N=3 all eight |
| OV2SLAM VO full N=1 (str02/MH_01/MH_03 filled) | `[x]` now N=3 all eight, including ZED |
| OV2SLAM VO-LC full-sequence runs | `[x]` N=3 all eight; Rosario seq1 run2 collapse retained |

### OV2SLAM

| Task | Status |
|---|---|
| Accuracy-first configs (`force_realtime: 0`; server metadata records 1.0 replay) | `[x]` |
| VO N=1 on Rosario seq1+seq5, EuRoC MH_05 and HortiMulti str03 | `[x]` 7.236 m / 8.045 m / 0.099 m / 0.351 m Sim3 ATE |
| Complete VO N=1 sweep on the remaining four standard sequences | `[x]` N=3 all eight; see matrix for coverage caveats |

### Voxel-SVIO

| Task | Status |
|---|---|
| Docker image + container build (`scripts/setup/setup_voxel_svio_docker.sh`) | `[x]` (NOTE: setup guard skips clone if `src/voxel_svio/` exists even when empty - source must actually be present) |
| Configs: euroc_mav (per-seq), rosariov2, hortimulti | `[x]` |
| Run script (`scripts/run/run_voxel_svio.sh`) + ROS1 data player | `[x]` |
| Smoke test EuRoC MH_01_easy N=1 | `[x]` (0.083 m; earlier 3.03 m row was a stale bad run) |
| VIO rosariov2/seq1+seq5 N=3 | `[x]` N=3 both |
| VIO hortimulti str02+str03 N=3 | `[x]` N=3 both |
| VIO EuRoC MH_01/03/05 N=1 -> N=3 | `[x]` N=3 each |
| ZED corrected VIO N=3 | `[~]` N=1; run2/run3 missing |

---

## Aggregation and reporting

| Task | Status |
|---|---|
| Rebuild `benchmark-vo.csv` after ORB-SLAM3 VO-clean results land | `[x]` current 192 planned rows; unresolved ORB attempts remain visible |
| Rebuild `benchmark-vio.csv` after N=3 runs (Basalt/ORB-SLAM3/OpenVINS) | `[x]` current 168 planned rows; missing repetitions are explicit |
| Add MASt3R-SLAM to applicable CSVs | `[ ]` deferred scope extension, not a missing N=3 obligation |
| Generate segment maps for all new Phase 2 sequences | `[ ]` |
| Final cross-algo ATE plots (VO vs VIO per sequence) | `[~]` report reconciliation in progress: 69 verified protocol N=3 cells after the ORB history hold; retain A/E/S/F, claim limits and agricultural/GNSS blockers |
| Explicit claim acceptance and stable regeneration | `[~]` evidence-pinned ledger now verifies 69 protocol N=3 cells; previous decisions and all scores preserved; native review and future manifest refresh in progress |
| Capture actual native exits and validate repaired execution | `[!]` OV2/Voxel shutdown errors found despite wrapper zero; native diagnostic execution remains unauthorized |
| Thesis-ready LaTeX table | `[ ]` |
| Exclude five COMPLETE smoke artifacts from headline discovery | `[x]` explicit campaign membership; all smoke/historical evidence retained |
| DPVO metric labeling and mixed-status / failure counts | `[x]` monocular Sim(3), metric SE(3); failures and planned denominators retained |
| RPE, GNSS origin alignment, ZED orientation and sparse-output coverage semantics | `[x]` corrected definitions, unsupported metrics withheld; 593 evaluations reconciled |
| GT/segmentation cache freshness and deferred segment coalescing | `[x]` hash-bound inputs and corrected geometric segment generation |
| Refresh all CSVs, tables/claims, figures and browser together | `[x]` 666 CSV rows, 226 cell/variant summaries, 690 browser entries; failures remain explicit |
| Freeze source/config/binary provenance and declare final N / GNSS scope | `[!]` future N=3 scope frozen; exact historical rebuild gaps disclosed, future native readiness unverified |

---

## Dropped / out of scope

| Algorithm | Reason |
|---|---|
| DROID-SLAM | Historical exclusion retained. Original attribution is documented in the audit; saved results are under `results/vo/`, outside campaign comparisons. |
| Stella-VSLAM | "Mostly reimplementation of ORB-SLAM3, adds nothing" (supervisor). |
| VINS-Fusion | Overlaps Basalt + OpenVINS; ROS1 only. |
| DSO / Stereo-DSO | Misaligned with stereo-IMU direction. |
| Kimera-VIO | Overlaps OpenVINS. |
| MegaSaM | Excluded from the current and future campaign manifest; old memory failures do not establish a 4090 limit. |

---

## Adding a new algorithm

Complete the current matrix gaps and reporting repairs before expanding scope.

1. Build / containerize under `src/<algo>/`.
2. Write `scripts/run/run_<algo>.sh` with signature `<dataset> <seq> [run_id=1] [run_type=vo]`.
3. Write config(s) under `configs/<algo>/`.
4. Add a row to each table above.
5. Smoke-test on EuRoC MH_01_easy first.

## Adding a new dataset

1. Write extraction script in `scripts/data/`.
2. Create `docs/private/dataset-specific/dataset_<name>.md`.
3. Extract to `datasets/<name>/<seq>/mav0/` with standard layout.
4. Add a column to each table above.

---

## DONE (Phase 1 - VO benchmark)

> Historical Phase 1 record. The unchecked items below are retained history, not
> current campaign obligations. IMU extraction and later runs have occurred; exclusions
> persist. The current run status and exact required actions are in the matrices above.

All Phase 1 VO runs are complete (N=3) and evaluated. See PROGRESS.md Phase 1 for the full
results table. Summary:

- ORB-SLAM3 (LC-on): rosariov2 seq1+seq5, hortimulti str02+str03 - results in `obsolete/` (LC-on confound)
- Basalt VO: all agri + EuRoC - done-N3 / done-N1
- MAC-VO: all agri + EuRoC - done-N3 / done-N1
- AirSLAM VO: all agri + EuRoC - done-N3 / done-N1
- DROID-SLAM: all agri + EuRoC - done-N3 / done-N1
- OKVIS2 VO: rosariov2/seq1+seq5 - done-N1

Kept as Phase 2 restructure (Phase 4.5):
- [ ] Rebuild ORB-SLAM3 with loop closure disabled (or wire up the
      stereo-inertial example) so it slots back into `vo` / `vio` / `vio-lc`.
- [ ] Re-run AirSLAM with `run_type=vio` and `vio-lc` on Rosario v2 and
      HortiMulti once `mav0/imu0/data.csv` is available for both datasets.
- [ ] Re-run Basalt with `run_type=vio` on Rosario v2 and HortiMulti.
- [ ] Extract IMU streams: HortiMulti needs `mav0/imu0/data.csv` from the
      `/ms/imu/data` topic (`scripts/data/_hortimulti_extract.py`).
      Rosario v2 needs the same generated from its `imu.csv`.
- [ ] Download MegaSaM checkpoints, run on EuRoC sanity sequence, then on
      Rosario / HortiMulti (`run_type=vo`).
- [ ] Download MASt3R-SLAM checkpoints, run on EuRoC sanity sequence, then
      on the agricultural sequences (`run_type=vo` and `vo-lc`).
- [ ] Add a `vio_slam` ORB-SLAM3 binary path and configs once the build
      lands.

## How to read this file

- `[x]` = done   `[ ]` = pending   `[~]` = partially done / blocked
- Sections are organised by **dataset → algorithm**; add new blocks using the
  same template when extending to more algorithms or datasets.
- The **cross-algorithm comparison** section at the bottom is filled after
  every algorithm on a dataset is complete.

---

## Standard vSLAM benchmarking pipeline (reference)

See [evaluation](docs/evaluation.md) for current implementation limitations: translation
uses point-distance residuals, and rotational accuracy needs valid orientation GT.

The community-standard evaluation workflow (Sturm 2012, TUM RGB-D; Geiger 2012,
KITTI; Grupp 2017, evo) has the following stages:

1. **Data prep** — extract bag → EuRoC layout (`cam0/`, `cam1/`, `times.txt`),
   create `gt_tum.txt` in TUM format (timestamp tx ty tz qx qy qz qw, seconds).
2. **Algorithm config** — write a correctly-named YAML config file for each
   (algorithm, dataset) pair; verify all required parameters are present.
3. **Run** — execute the algorithm, capture trajectory + runtime metadata
   (FPS, peak GPU MB); save to `results/<type>/<dataset>/<seq>/<algo>/`.
4. **Timestamp normalisation** — ensure all estimated trajectories use
   second-epoch timestamps matching the GT file's epoch.
5. **ATE / APE** (`evo_ape`) — absolute trajectory error after rigid SE(3)
   alignment; primary global accuracy metric.  Report RMSE and mean.
6. **RPE** (`evo_rpe`) — relative pose error over a fixed window (~1 s);
   measures local drift.  Report RMSE of translational and rotational error.
7. **Coverage** — inspect time support and tracking outages. Output-pose count divided
   by input-frame count measures output rate, not reliable trajectory coverage.
8. **Runtime metrics** — wall-clock FPS, peak GPU memory, CPU usage.
9. **Multi-run benchmark** — run algorithm N times (N=3); `run_orbslam3.sh <dataset> <seq> <run_id>`.
10. **Per-run evaluation** — `scripts/eval/_evaluate_run.py <dataset> <seq> <algo> <run_id>` → `run_eval.json`.
11. **Aggregate runs** — `scripts/eval/_aggregate_runs.py <dataset> <seq> <algo>` → `metrics.csv`, `report.md`.
12. **Segment visualisation** — `scripts/eval/_plot_segments.py <dataset> <seq>` → `segment_map.png`.

---

## Phase 0 – Infrastructure

> Historical implementation checklist. Current evaluation limitations are tracked above.

| Task | Status |
|---|---|
| Clone + build ORB-SLAM3 (UZH upstream) | `[x]` |
| Patch ORB-SLAM3 for C++14 (sigslot) | `[x]` |
| Fix ORB-SLAM3 `Rectified` null-ptr bug (`Settings.cc`) | `[x]` |
| Build Pangolin v0.9.5 | `[x]` |
| Install `evo` evaluation toolkit | `[x]` |
| Script layout: `build/`, `data/`, `run/`, `eval/` | `[x]` |
| `run_orbslam3.sh` — multi-run with resource monitoring | `[x]` |
| `_resource_monitor.py` — GPU+CPU+RAM every 1s | `[x]` |
| `_interpolate_gt.py` — sparse GT → camera timestamps (Slerp) | `[x]` |
| `_segment_trajectory.py` — **v2: 2 m sliding-window path-length, 10° heading / 20 cm chord deviation** | `[x]` |
| `_evaluate_run.py` — full per-run evaluation (ATE Sim3 + **SE3**) → `run_eval.json` | `[x]` |
| `_aggregate_runs.py` — N runs → `metrics.csv` + `report.md` (Sim3 + SE3 columns) | `[x]` |
| `_plot_segments.py` — **8 K segment map, 3 hierarchies (per-run, per-algo, cross-algo)** | `[x]` |
| `run_benchmark.sh` — one-shot pipeline: run N times + interpolate GT + segment + evaluate + aggregate | `[x]` |
| RPE metric: use `point_distance` not `trans_part` (frame mismatch fix) | `[x]` |
| **Sim(3) vs SE(3) reporting**: both alignments computed every run | `[x]` |
| **Body↔camera mount mismatch documented** (Strawberry-03 RPE rot artefact) | `[x]` |
| `run_droidslam.sh` / `run_macvo.sh` upgraded to **multi-run framework** (`<run_id>` arg, `_resource_monitor.py`) | `[x]` |
| DROID-SLAM conda env (`droidenv`) | `[x]`; lietorch, torch_scatter, droid_backends all built |
| MAC-VO conda env | `[x]`; `macvo` env created; models downloaded |
| **Basalt binary install** (`~/.local/bin/basalt_vio`, v0.1.7) | `[x]`; Binary installer for Ubuntu 22.04; sources `~/.basalt/env` |
| `run_basalt.sh` | `[x]`; EuRoC format, auto-generates `mav0/cam*/data.csv`, `--use-imu false` |
| `configs/basalt/hortimulti_calib.json` + `rosariov2_calib.json` + `vo_config.json` | `[x]`; Pinhole + `vio_min_triangulation_dist: 0.03` |
| **AirSLAM Docker** (`air_slam` container, `xukuanhit/air_slam:v4`) | `[x]`; Docker Engine + nvidia-container-toolkit; catkin_make inside container |
| `scripts/setup/setup_airslam_docker.sh` | `[x]`; One-shot pull + create + build |
| `run_airslam.sh` | `[x]`; Polls `trajectory_v0.txt`, `pkill roslaunch`, `mv -f`, FPS from input frames |
| `configs/airslam/{hortimulti,rosariov2}_{camera,vo}.yaml` | `[x]`; Per-dataset intrinsics + TRT engine name |

---

## Phase 1 – Dataset: Rosario v2

> Historical experiments and values; superseded as current status by the matrices above.

> Agricultural field rows, stereo + GPS GT, 15 fps, 1280×720.
> Full sequence 1 = 13 821 frames, ~18 min.
> Official evaluation: https://github.com/CIFASIS/rosariov2

### 1-A  Data preparation

| Task | Status |
|---|---|
| `scripts/data/convert_rosario_to_tum.sh` — OOM-safe streaming extractor | `[x]` |
| Extract sequence 1 (13 821 frames) | `[x]` |
| `gt_tum.txt` present (GPS PGT, second-epoch timestamps) | `[x]` |
| Extract sequence 5 (11 640 frames) | `[x]` |
| Extract sequences 2–4 (if needed) | `[ ]` |

### 1-B  ORB-SLAM3

| Task | Status | Notes |
|---|---|---|
| Config `configs/orbslam3/rosariov2_stereo.yaml` | `[x]` | Rectified, fx=648.86 |
| Run full sequence 1 (single, old format) | `[x]` | 13 821 frames, 12.55 fps, 1101 s |
| ATE on sequence 1 (old single run) | `[x]` | **RMSE 1.361 m**, mean 1.311 m |
| RPE (15-frame window) on sequence 1 | `[x]` | trans RMSE **0.115 m**, rot RMSE **3.56 °** |
| Interpolate GT for seq1 (`gt_interp_tum.txt`) | `[x]` | 13821 poses at camera timestamps |
| Auto-segment seq1 (`segments_auto.csv`) | `[x]` | 145 segs: 125 row (863 s), 20 turn (60 s) |
| **Run seq1 × 3 (multi-run benchmark)** | `[x]` | ATE 1.176 ± 0.317 m, 100%, 5-6 loops |
| **Evaluate + aggregate seq1 × 3** | `[x]` | `metrics.csv` + `report.md` + `segment_map.png` done |
| Run sequence 5 (single, old format) | `[x]` | 11 640 frames, 11.55 fps, 1008 s, 100% completion |
| Evaluate sequence 5 (old single run) | `[x]` | **ATE RMSE 8.274 m** (Sim3 alignment) |
| Interpolate GT for seq5 (`gt_interp_tum.txt`) | `[x]` | 11640 poses at camera timestamps |
| Auto-segment seq5 (`segments_auto.csv`) | `[x]` | 101 segs: 95 row (756 s), 6 turn (19 s) |
| **Run seq5 × 3 (multi-run benchmark)** | `[x]` | ATE 20.207 ± 4.204 m, 91% avg, 0 loops |
| **Evaluate + aggregate seq5 × 3** | `[x]` | `metrics.csv` + `report.md` + `segment_map.png` done |
| Segment map visualisation seq1 | `[x]` | `results/rosariov2/sequence1/segment_map.png` |
| Segment map visualisation seq5 | `[x]` | `results/rosariov2/sequence5/segment_map.png` |
| Run remaining sequences | `[ ]` |  |
| Evaluate remaining sequences | `[ ]` |  |

### 1-C  DROID-SLAM

| Task | Status | Notes |
|---|---|---|
| Set up conda env + install dependencies | `[x]` | torch 2.7+cu126, lietorch 0.2, torch_scatter 2.1.2 |
| `scripts/run/run_droidslam.sh` + `_droid_demo_wrapper.py` | `[x]` | stereo, TUM trajectory output |
| `configs/droidslam/rosariov2.txt` intrinsics file | `[x]` | fx=fy=648.86, cx=645.01, cy=348.24 |
| `droid.pth` pretrained weights | `[x]` | downloaded to `src/DROID-SLAM/` |
| Run sequence 1 | `[x]` | full sequence (6911 frames, stride=2), skip_backend |
| Evaluate sequence 1 | `[x]` | **ATE RMSE 45.05 m** (Sim3 alignment) |
| Sequence 5 trajectory | `[x]` | 3 runs provided by collaborator; timestamps converted ns→s |
| Evaluate sequence 5 | `[x]` | **ATE RMSE 50.02 m** (Sim3, mean of 3 runs) |

### 1-D  MAC-VO

| Task | Status | Notes |
|---|---|---|
| Set up conda env + install dependencies | `[x]` | `macvo` env created; models downloaded |
| `scripts/run/run_macvo.sh` | `[x]` | fixed: conda set-u, upstream odom config, `--useRR`, correct Results path |
| `configs/macvo/rosario_v2_sequence.yaml` | `[x]` | GeneralStereo format; intrinsics=648.86, bl=0.04973; `left/right` symlinks created |
| Run sequence 1 | `[x]` | 13821 frames, 100% completion |
| Evaluate sequence 1 | `[x]` | **ATE RMSE 13.277 m** (Sim3 alignment) |
| `configs/macvo/rosariov2_sequence5.yaml` | `[x]` | same intrinsics/bl; root→sequence5; `left/right` symlinks created |
| Run sequence 5 | `[x]` | 11 640 frames, 100% completion (3 runs done) |
| Evaluate sequence 5 | `[x]` | **ATE RMSE 19.384 ± 0.006 m** (Sim3, 3 runs) |

### 1-E  Cross-algorithm comparison (Rosario v2)

| Task | Status |
|---|---|
| All four algorithms run on sequence 1 (single run) | `[x]` |
| ORB-SLAM3 + DROID-SLAM run on sequence 5 | `[x]` |
| MAC-VO on sequence 5 × 3 | `[x]`; ATE Sim3 **19.384 ± 0.006 m** (3 runs; scale=0.933, 100% tracking) |
| ORB-SLAM3 × 3 multi-run benchmark seq1 | `[x]`; ATE 1.176 ± 0.317 m, `report.md` + `segment_map.png` |
| ORB-SLAM3 × 3 multi-run benchmark seq5 | `[x]`; ATE 20.207 ± 4.204 m, `report.md` + `segment_map.png` |
| Segment maps for seq1 and seq5 | `[x]`; seq1 ✓, seq5 ✓ |
| `metrics.csv` + `report.md` for seq1 | `[x]`; done |
| `metrics.csv` + `report.md` for seq5 | `[x]`; done |
| Comparison table for thesis chapter | `[ ]`; Final LaTeX/PDF table for thesis |

### 1-F  Basalt (stereo VO)

| Task | Status | Notes |
|---|---|---|
| `configs/basalt/rosariov2_calib.json` | `[x]` | EuRoC format, pinhole, `vio_min_triangulation_dist: 0.03` |
| Run seq1 × 3 + evaluate | `[x]` | ATE Sim3 **14.279 ± 0.302 m**, SE3 **18.693 ± 0.586 m**, 100% |
| Run seq5 × 3 + evaluate | `[x]` | ATE Sim3 **15.035 ± 0.062 m**, SE3 **15.425 ± 0.068 m**, 100% |
| Segment maps with Basalt | `[x]` | seq1 + seq5 regenerated |

### 1-G  AirSLAM (deep-feature stereo VO)

| Task | Status | Notes |
|---|---|---|
| `configs/airslam/rosariov2_camera.yaml` + `rosariov2_vo.yaml` | `[x]` | 1280×720, baseline 0.04973m |
| TensorRT engine compiled for rosariov2 (1280×720) | `[x]` | Compiled on seq1 run1 startup |
| Run seq1 × 3 + evaluate | `[x]` | **DONE** (9.888 ± 0.059 m Sim3, 9.891 ± 0.058 m SE3, 100% × 3) |
| Run seq5 × 3 + evaluate | `[x]` | **DONE** (12.722 ± 0.991 m Sim3, 12.777 ± 1.014 m SE3, 100% × 3) |



---

## GNSS-VIO (stereo + IMU + GNSS) - `results-gnss-vio/`

> Historical infrastructure/experiment record. Use the GNSS matrix above for current
> artifact validation status; server GNSS repeats were excluded.

Phase F: GPS-aware algorithms with full Sim(3)+SE(3) eval pipeline.

Infrastructure status:
- [x] `run_type=gnss-vio` registered in `_paths.sh` and `_run_type.py`
- [x] `results-gnss-vio/` + `benchmark-gnss-vio.csv` wired into the eval pipeline
- [x] Shared GPS data players (`gnss_data_player.py` ROS 1, `gnss_data_player_ros2.py` ROS 2)
- [x] HortiMulti GPS extraction added to `_hortimulti_extract.py` (`--gps-only`,
      `--no-gps`, `--gps`); topic default `/antobot_gps`. Handles the upstream
      quirk where `header.stamp` is constant in `/antobot_gps` (falls back to
      bag-arrival time) and altitude is published in millimetres (auto-rescales
      when `max(alt) > 1000 m`).
- [x] CIFASIS GNSS-SI: clone + Dockerfile + setup script + configs for rosariov2
      seq1/seq5 + hortimulti str02/str03 + runner.
- [x] RTAB-Map: configs (rosariov2, hortimulti) + ROS 2 launch runner.
      `gnss_data_player_ros2.py` publishes `/cam{0,1}/camera_info` from per-dataset
      rectified intrinsics passed via `run_rtabmap_gps.sh`.
- [x] VINS-Fusion: clone + Dockerfile + setup script + configs for rosariov2
      seq1/seq5 + hortimulti str02/str03 (incl. per-cam YAMLs) + runner.
      Ceres pinned to `1.14.0` (2.1+ uses `std::integer_sequence`, incompatible
      with VINS-Fusion's hard-coded `-std=c++11`). All `CV_*` legacy macros are
      sed-rewritten to `cv::*` after `COPY src/VINS-Fusion` in the Dockerfile.
      HortiMulti `body_T_cam0` is `T_imu_cam0_raw @ blkdiag(R1.T, 1)` where
      `R1` comes from `cv2.fisheye.stereoRectify` in `_hortimulti_extract.py`.
- [x] OpenVINS+GPS: OpenVINS odometry + `robot_localization` EKF runner and four N=1 artifacts.
- [x] HortiMulti GPS extraction completed for str02/str03 (7620/1939 fixes;
      consumer-grade fixes with large vertical covariance).
- [x] CIFASIS GNSS-SI N=1 on rosariov2 seq1/seq5 + HortiMulti str02/str03; N=3 pending.
- [x] RTAB-Map N=1 on all four sequences; seq5 PPK is partial/nondeterministic; N=3 pending.
- [x] VINS-Fusion N=1 on all four sequences; N=3 pending.
- [~] OpenVINS+GPS N=1 on all four sequences; validate all rows and rerun HortiMulti with the
      corrected extrinsic before N=3.
- [x] Rosario sequence5 PPK-versus-conventional four-algorithm study completed.
