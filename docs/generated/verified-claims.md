# Reconciled evidence counts

Generated from hash-checked schema-3 evaluations and matching CSVs. These are inventory facts, not certification of scientific claims. Numerical `ok` is separate from execution, calibration, reference validity and publication qualification.

| Mode | Planned defaults | Evaluated | Numerical ok | Scale collapse | Invalid trajectory | Nonzero exits | Protocol-verified N=3 cells |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 330 | 281 | 278 | 3 | 0 | 4 | 52 |
| vo-lc | 210 | 143 | 142 | 1 | 0 | 6 | 23 |
| vio | 300 | 258 | 248 | 10 | 0 | 3 | 56 |
| vio-lc | 210 | 98 | 95 | 3 | 0 | 8 | 23 |
| gnss-vio | 60 | 20 | 19 | 0 | 1 | 0 | 0 |

Legacy GNSS variants: 6 separate rows; not included in default repetition counts.

Scientific statuses among existing headline attempts: accepted=117, accepted_with_limitation=353, blocked=309, rerun_required=21, valid_observed_failure=18.

## Retained adverse outcomes

| Run | Numerical status | Exit | Scientific status |
|---|---|---:|---|
| `results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run1` | eval_failed | unknown | blocked |
| `results/gnss-vio/rosariov2/sequence1/cifasis_gnss_si/run1` | ok | unknown | rerun_required |
| `results/vio/citrusfarm/seq07/openvins/run10001` | scale_collapse | 0 | blocked |
| `results/vio/citrusfarm/seq07/voxel_svio/run10001` | scale_collapse | 0 | blocked |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run1` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run2` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run3` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run1` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run2` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run3` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run1` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run2` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run3` | ok | 0 | accepted_with_limitation |
| `results/vio/hortimulti/strawberry03/mast3r_fusion/run10001` | scale_collapse | 0 | valid_observed_failure |
| `results/vio/hortimulti/strawberry03/mast3r_fusion/run10002` | scale_collapse | 0 | valid_observed_failure |
| `results/vio/hortimulti/strawberry03/mast3r_fusion/run10003` | scale_collapse | 0 | valid_observed_failure |
| `results/vio/rosariov2/sequence1/openvins/run10002` | scale_collapse | 0 | blocked |
| `results/vio/rosariov2/sequence5/openvins/run10001` | scale_collapse | 0 | blocked |
| `results/vio/rosariov2/sequence5/openvins/run10003` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run10001` | scale_collapse | 139 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run10002` | scale_collapse | 139 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run10003` | ok | 139 | blocked |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run4` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vio-lc/hortimulti/strawberry02/orbslam3/run10001` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vio-lc/hortimulti/strawberry02/svo_pro/run10001` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vio-lc/hortimulti/strawberry02/svo_pro/run10002` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vio-lc/hortimulti/strawberry02/svo_pro/run10003` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vio-lc/hortimulti/strawberry03/mast3r_fusion/run10001` | scale_collapse | 0 | valid_observed_failure |
| `results/vio-lc/hortimulti/strawberry03/mast3r_fusion/run10002` | scale_collapse | 0 | valid_observed_failure |
| `results/vio-lc/hortimulti/strawberry03/mast3r_fusion/run10003` | scale_collapse | 0 | valid_observed_failure |
| `results/vio-lc/hortimulti/strawberry03/svo_pro/run10001` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vio-lc/hortimulti/strawberry03/svo_pro/run10003` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 139 | rerun_required |
| `results/vo/citrusfarm/seq04/dsol/run10001` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vo/citrusfarm/seq04/svo_pro/run10001` | scale_collapse | 0 | valid_observed_failure |
| `results/vo/citrusfarm/seq07/dsol/run10001` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/dsol/run10002` | scale_collapse | 0 | valid_observed_failure |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | scale_collapse | 0 | valid_observed_failure |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | rerun_required |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run2` | ok | 139 | rerun_required |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/orbslam3/run3` | ok | 139 | blocked |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/orbslam3/run3` | ok | 139 | blocked |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/orbslam3/run1` | ok | 134 | blocked |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/rosariov2/sequence1/orbslam3/run1` | failed_without_trajectory | 134 | blocked |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run2` | scale_collapse | 0 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | incomplete | unknown | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run1` | ok | 141 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | rerun_required |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | ok | 0 | accepted_with_limitation |

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
| `inventory.json` | `75cf643c7ed435b07edf12cef4898f0824723b5de5f31f76197a8f77ab04e4d4` |
| `benchmark-vo.csv` | `1857edadf2b72382f98c8fcd836c25917c3462c2f643a382b5a8a9afe894edea` |
| `benchmark-vo-lc.csv` | `034c8b804cbdcc51b178c30c4da34de0154b8a65e95580fe709d4caf1583f911` |
| `benchmark-vio.csv` | `7ee347b003f688dcfe4490272b1d9367c7fb07296328042d585e6e2669053c85` |
| `benchmark-vio-lc.csv` | `ea821383a7526e1d1b8d72b9b7c0426c04b0d048af9fe35205434d35d53310a8` |
| `benchmark-gnss-vio.csv` | `7eccab1f3b593feedcf877b31ca5618f33a3b6dffcd196c60dc45848acd88494` |
