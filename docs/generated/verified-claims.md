# Reconciled evidence counts

Generated from hash-checked schema-3 evaluations and matching CSVs. These are inventory facts, not certification of scientific claims. Numerical `ok` is separate from execution, calibration, reference validity and publication qualification.

| Mode | Planned defaults | Evaluated | Numerical ok | Scale collapse | Invalid trajectory | Nonzero exits | Protocol-verified N=3 cells |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 330 | 183 | 182 | 1 | 0 | 7 | 0 |
| vo-lc | 210 | 137 | 136 | 1 | 0 | 9 | 0 |
| vio | 300 | 160 | 156 | 4 | 0 | 9 | 0 |
| vio-lc | 210 | 86 | 86 | 0 | 0 | 2 | 0 |
| gnss-vio | 60 | 20 | 19 | 0 | 1 | 0 | 0 |

Legacy GNSS variants: 6 separate rows; not included in default repetition counts.

Scientific statuses among existing headline attempts: blocked=599.

## Retained adverse outcomes

| Run | Numerical status | Exit | Scientific status |
|---|---|---:|---|
| `results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run1` | eval_failed | unknown | blocked |
| `results/vio/euroc_mav/MH_01_easy/openvins/run1` | ok | 134 | blocked |
| `results/vio/euroc_mav/MH_03_medium/openvins/run1` | ok | 134 | blocked |
| `results/vio/hortimulti/strawberry02/openvins/run1` | ok | 134 | blocked |
| `results/vio/hortimulti/strawberry03/openvins/run1` | ok | 134 | blocked |
| `results/vio/rosariov2/sequence1/openvins/run1` | scale_collapse | 134 | blocked |
| `results/vio/rosariov2/sequence5/openvins/run1` | scale_collapse | 134 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run10001` | scale_collapse | 139 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run10002` | scale_collapse | 139 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run10003` | ok | 139 | blocked |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run4` | failed_without_trajectory | 139 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 139 | blocked |
| `results/vo/euroc_mav/MH_03_medium/orbslam3/run2` | ok | 139 | blocked |
| `results/vo/hortimulti/strawberry02/orbslam3/run1` | failed_without_trajectory | 139 | blocked |
| `results/vo/hortimulti/strawberry03/orbslam3/run2` | ok | 139 | blocked |
| `results/vo/rosariov2/sequence1/orbslam3/run1` | failed_without_trajectory | 134 | blocked |
| `results/vo/rosariov2/sequence5/orbslam3/run1` | failed_without_trajectory | 139 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | scale_collapse | 0 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run2` | ok | 139 | blocked |
| `results/vo-lc/euroc_mav/MH_01_easy/orbslam3/run3` | ok | 139 | blocked |
| `results/vo-lc/euroc_mav/MH_03_medium/orbslam3/run3` | ok | 139 | blocked |
| `results/vo-lc/euroc_mav/MH_05_difficult/orbslam3/run1` | ok | 134 | blocked |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run1` | ok | 134 | blocked |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run2` | ok | 139 | blocked |
| `results/vo-lc/hortimulti/strawberry03/orbslam3/run1` | ok | 139 | blocked |
| `results/vo-lc/rosariov2/sequence1/orbslam3/run1` | failed_without_trajectory | 134 | blocked |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run2` | scale_collapse | 0 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | incomplete | unknown | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run1` | ok | 141 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | blocked |

## Claim boundaries

- Primary ATE is SE(3) for metric stereo/inertial methods and Sim(3) for monocular DPVO. No cross-scale winner is inferred.
- Conditional accuracy in the tables excludes numerical failures from the score calculation only; all failures and missing repetitions remain in the denominator. Distinct cohorts and GNSS variants are separate.
- AirSLAM keyframe density does not measure tracking loss or processed-image throughput. Exported-pose coverage and reference-supported score coverage have separate fields.
- Nominal input divided by elapsed time is not measured estimator processing speed or real-time latency.
- Mode comparisons alone do not establish that excitation or a particular loop mechanism caused an error. Reference, config and final-optimization differences must be resolved before drawing those conclusions.
- Aligned GNSS shape error is not absolute global positioning accuracy. Historical input/reference independence remains unqualified.

## Source identities

| Source | SHA-256 |
|---|---|
| `inventory.json` | `b745194028fe5e66d7bfafd940ece4b4d5c07c311cbf217f341d19ea1ec91da0` |
| `benchmark-vo.csv` | `81fe96456f09731e61599bd46c80a1658d2aede2caa68d1dfb3183b9aa78edb0` |
| `benchmark-vo-lc.csv` | `3e2a20853ab676c0b18746562d012b250470cfa447bbf586e4205277ce78497a` |
| `benchmark-vio.csv` | `17a4b300817614569e67ddee22b1ca6537a9f39c1aa53bc8bdb245641a365882` |
| `benchmark-vio-lc.csv` | `d412a7c5551d4329651bbf95909e6df16599bd99ec81e227648df0c9af48832d` |
| `benchmark-gnss-vio.csv` | `2423e820b0f71e859a123b1291bb0c7ebfcdb3c2acf6028def8e2a5e56268f39` |
