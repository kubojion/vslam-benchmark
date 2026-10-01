# Saved parameter review — 2026-10-01

This review reads hash-verified historical config snapshots across all five modes.
It does not substitute today's files for run-time evidence. Reproduce the selected
parameter and mode checks with the scientific Python environment:

```bash
/data/imoroz/conda/envs/macvo/bin/python scripts/campaign/audit_saved_parameters.py
```

The artifact is `results/repair-20261001/saved-parameter-audit.json`: 690 planned or
retained artifact records, 561 with saved configuration evidence, 1,220 passing
selected mode checks and 21 unverified checks. There are 41 settings with multiple
recorded values within an algorithm/mode, including legitimate sensor differences.
These counts do not certify full provenance, correct calibration or publication
readiness. A syntactically matching switch does not prove a native binary used it.

## Confirmed ORB-SLAM3 HortiMulti VIO-LC calibration defect

All six saved VIO-LC repetitions on Strawberry02/03 contain the raw-camera IMU
rotation. Their images and camera model are rectified. The corresponding VIO
profile already composes the rotation with the extraction rectification.

Independent recomputation from the constants and OpenCV fisheye call in
`scripts/data/_hortimulti_extract.py` establishes:

`R_imu_rectified = R_imu_raw @ R_rectified_from_raw.T`.

The rotation difference is **1.2189490371 degrees**. The composed matrix agrees
with the existing VIO configuration to **4.55e-11** maximum absolute element error;
translation is unchanged. Every affected snapshot hash was verified. Evidence:
`results/repair-20261001/orb-horti-rectification-validation.json`.

The future VIO-LC config now uses that same rectified sensor transform. Historical
snapshots and trajectories are unchanged. These six results require a corrected
estimation cohort: post-hoc trajectory transformation cannot repair sensor fusion
performed with the wrong extrinsic. Native validation remains outstanding, as do
the independent Horti reference-to-camera transform/provenance questions. This
repair therefore establishes neither a complete Horti calibration certificate nor
execution readiness.

## Actual algorithm-profile differences

| Algorithm | Saved settings | Consequence for reporting |
|---|---|---|
| ORB-SLAM3 | 1,200 ORB features across recorded configs; `Stereo.ThDepth` is 40 for Horti, 60 for EuRoC, 80 for Rosario/ZED | Feature-budget normalization was applied, but the depth heuristic remains rig-specific. Do not claim every algorithm parameter is fixed across datasets. Historical ZED VO/VO-LC still require the separate 15-to-10 Hz correction. |
| OKVIS2 / OKVIS2-X | IMU and LC switches agree with the declared non-GNSS modes wherever saved config evidence exists. All recorded OKVIS2 LC configs disable final BA; OKVIS2-X LC configs enable it | Label final BA explicitly in both VO-LC and VIO-LC. The comparison includes an optimization-policy difference, not just an implementation difference. `do_extrinsics_final_ba=true` is inactive when final BA is disabled. |
| OKVIS2-X | VIO-LC uses five loop-closure frames on EuRoC/Horti/Rosario, three on ZED | Another declared configuration variant is needed; it is not a camera calibration field. |
| Basalt | Rosario VO triangulation gate 0.03 m, other recorded gates 0.05 m; realtime frame dropping disabled | Keep the documented 49.7 mm-baseline exception. Distinguish the separately selected VO/VIO profiles. |
| AirSLAM | Upper depth bound is 10 m for EuRoC, 15 m for Horti, 50 m for Rosario/ZED | A benchmark adaptation remains inside camera-named files. Sparse export and the 18 EuRoC inertial rectification reruns remain separate issues. |
| OV2SLAM | `nmaxdist=35` everywhere, but Horti uses initialization parallax 15 and coverage score 20 versus 20/25 elsewhere | The earlier normalization did not produce one identical algorithm profile. Report these remaining adaptations rather than calling all settings unchanged upstream defaults. |
| OpenVINS | 200 points everywhere; online camera intrinsics/extrinsics calibration enabled for EuRoC and disabled for agriculture; initialization acceleration threshold 1.5 versus 1.0 | The comments justify the calibration switch by pre-rectified input, but this is still an algorithm choice. Record the exception and its selection rationale; do not relabel it as a measured sensor constant. |
| Voxel-SVIO | 500 points; 10 s initialization window for MH01, 2 s elsewhere | The upstream EuRoC config explicitly recommends 10 s for MH01/02/04. Disclose the author-specified sequence exception and retain the observed incomplete MH01 trajectory coverage. |
| DPVO / DPV-SLAM | Recorded stride 1, skip 0, mode-specific LC and predetermined seeds | Selected input/mode contracts pass where metadata exists. Sim(3) remains the primary monocular shape metric; this does not validate all native/runtime dependencies. |
| MAC-VO | Official Performant configuration, with loader-specific data configs | Label Performant explicitly; its own config says it is not the paper-reproduction profile. Fifteen generic `gt_pose` checks are unverified because GeneralStereo configs lack that switch; this is not evidence of ground-truth leakage. Inspect loader semantics separately. |
| GNSS-VIO | Legacy source/config snapshots are generally absent | Today's configs cannot certify the historical inputs, fusion output or effective calibration. Keep the 20 defaults and six variants separate and unqualified until evidence supports each claim. |

These are findings, not permission to tune on final-test ATE. No numeric algorithm
settings above were silently harmonized during this review. Future cohort selection
must explicitly preserve justified adaptations or define a different frozen protocol.

## Identical obsolete ORB key duplicates

Seven historical ORB VO attempts contain two identical `System.LoopClosing: 0`
entries, yielding 14 warnings across effective/source snapshots. The inspected
`System.cc` reads `loopClosing`, whose value is 0. The audit reports these identical
ignored aliases and rejects conflicting duplicate keys; it does not treat the alias
duplication as evidence that LC was enabled or as a rerun reason by itself.

Future ORB config materialization drops both old LC keys and writes exactly one
effective `loopClosing` setting. Original configs/snapshots remain available. Native
failure diagnoses and scientific qualification are independent of this cleanup.
