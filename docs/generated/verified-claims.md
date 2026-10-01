# Reconciled evidence counts

Generated from hash-checked schema-3 evaluations and matching CSVs. These are inventory facts, not certification of scientific claims. Numerical `ok` is separate from execution, calibration, reference validity and publication qualification.

| Mode | Planned defaults | Evaluated | Numerical ok | Scale collapse | Invalid trajectory | Nonzero exits | Qualified clean N=3 cells |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 192 | 183 | 182 | 1 | 0 | 7 | 17 |
| vo-lc | 144 | 136 | 135 | 1 | 0 | 9 | 9 |
| vio | 168 | 145 | 142 | 3 | 0 | 7 | 11 |
| vio-lc | 96 | 86 | 86 | 0 | 0 | 2 | 8 |
| gnss-vio | 60 | 20 | 19 | 0 | 1 | 0 | 0 |

Legacy GNSS variants: 6 separate rows; not included in default repetition counts.

Scientific statuses among existing headline attempts: accepted=151, accepted_with_limitation=73, blocked=278, rerun_required=73, valid_observed_failure=10.

## Retained adverse outcomes

| Run | Numerical status | Exit | Scientific status |
|---|---|---:|---|
| `results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run1` | eval_failed | unknown | blocked |
| `results/gnss-vio/rosariov2/sequence1/cifasis_gnss_si/run1` | ok | unknown | rerun_required |
| `results/vio/euroc_mav/MH_01_easy/openvins/run1` | ok | 134 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run1` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run2` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run3` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/openvins/run1` | ok | 134 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run1` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run2` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run3` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run1` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run2` | ok | 0 | accepted_with_limitation |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run3` | ok | 0 | accepted_with_limitation |
| `results/vio/hortimulti/strawberry02/openvins/run1` | ok | 134 | blocked |
| `results/vio/hortimulti/strawberry02/voxel_svio/run1` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry02/voxel_svio/run2` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry02/voxel_svio/run3` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry03/openvins/run1` | ok | 134 | blocked |
| `results/vio/hortimulti/strawberry03/voxel_svio/run1` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry03/voxel_svio/run2` | ok | 0 | blocked |
| `results/vio/hortimulti/strawberry03/voxel_svio/run3` | ok | 0 | blocked |
| `results/vio/rosariov2/sequence1/openvins/run1` | scale_collapse | 134 | rerun_required |
| `results/vio/rosariov2/sequence1/voxel_svio/run1` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence1/voxel_svio/run2` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence1/voxel_svio/run3` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence5/openvins/run1` | scale_collapse | 134 | rerun_required |
| `results/vio/rosariov2/sequence5/voxel_svio/run1` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence5/voxel_svio/run2` | ok | 0 | rerun_required |
| `results/vio/rosariov2/sequence5/voxel_svio/run3` | ok | 0 | rerun_required |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run1` | scale_collapse | 0 | valid_observed_failure |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run1` | ok | 0 | blocked |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run4` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/orbslam3/run2` | ok | 139 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo/hortimulti/strawberry02/orbslam3/run1` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vo/hortimulti/strawberry02/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry02/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry02/ov2slam/run3` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry03/orbslam3/run2` | ok | 139 | blocked |
| `results/vo/hortimulti/strawberry03/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry03/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/hortimulti/strawberry03/ov2slam/run3` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence1/orbslam3/run1` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vo/rosariov2/sequence1/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence1/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence1/ov2slam/run3` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence5/orbslam3/run1` | failed_without_trajectory | 139 | valid_observed_failure |
| `results/vo/rosariov2/sequence5/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence5/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/rosariov2/sequence5/ov2slam/run3` | ok | 0 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | scale_collapse | 0 | valid_observed_failure |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | rerun_required |
| `results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run2` | ok | 139 | rerun_required |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | ok | 0 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | ok | 0 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/euroc_mav/MH_01_easy/orbslam3/run3` | ok | 139 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/orbslam3/run3` | ok | 139 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/orbslam3/run1` | ok | 134 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run1` | ok | 134 | blocked |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run2` | ok | 139 | blocked |
| `results/vo-lc/hortimulti/strawberry02/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry02/ov2slam/run2` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry02/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry03/orbslam3/run1` | ok | 139 | blocked |
| `results/vo-lc/hortimulti/strawberry03/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry03/ov2slam/run2` | ok | 0 | blocked |
| `results/vo-lc/hortimulti/strawberry03/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence1/orbslam3/run1` | failed_without_trajectory | 134 | valid_observed_failure |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run2` | scale_collapse | 0 | valid_observed_failure |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence5/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence5/ov2slam/run2` | ok | 0 | blocked |
| `results/vo-lc/rosariov2/sequence5/ov2slam/run3` | ok | 0 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | incomplete | unknown | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run1` | failed_without_trajectory | 141 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1` | ok | 139 | rerun_required |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | ok | 0 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | ok | 0 | blocked |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | ok | 0 | blocked |

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
| `inventory.json` | `2b55697202e3e83031550c5f3fad07d313ecb0c9b1d06d09044bab3215beafed` |
| `benchmark-vo.csv` | `281a1d2e577339f57ad1ae173a7986d9a7822a76dd668818e53d1488e93849d1` |
| `benchmark-vo-lc.csv` | `74837ed0caa431b848e1348d4ad4992dfcf724659d066505889601db8a8a2817` |
| `benchmark-vio.csv` | `bdc937a097257244e886132948481c72e1b48eefde474dd3783a84643f200816` |
| `benchmark-vio-lc.csv` | `8298fd060ed996a89a2b87b4a466c220c9dabe3bbed841fef93686f7fcf649e0` |
| `benchmark-gnss-vio.csv` | `b43cee6493aa173d418fa9fc6a9ac3f241eca175a520e28192faa59ffe050bb6` |
