# Reconciled evidence counts

Generated from hash-checked schema-3 evaluations and matching CSVs. These are inventory facts, not certification of scientific claims. Numerical `ok` is separate from execution, calibration, reference validity and publication qualification.

| Mode | Planned defaults | Evaluated | Numerical ok | Scale collapse | Invalid trajectory | Nonzero exits | Protocol-verified N=3 cells |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 330 | 323 | 317 | 6 | 0 | 7 | 64 |
| vo-lc | 210 | 206 | 203 | 2 | 1 | 0 | 31 |
| vio | 300 | 299 | 272 | 27 | 0 | 6 | 50 |
| vio-lc | 210 | 196 | 180 | 16 | 0 | 14 | 23 |
| gnss-vio | 60 | 20 | 19 | 0 | 1 | 0 | 0 |

Legacy GNSS variants: 6 separate rows; not included in default repetition counts.

Scientific statuses among existing headline attempts: accepted=117, accepted_with_limitation=386, blocked=553, rerun_required=5, valid_observed_failure=15.

## Retained adverse outcomes

| Run | Numerical status | Exit | Scientific status |
|---|---|---:|---|
| `results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run1` | eval_failed | unknown | blocked |
| `results/gnss-vio/rosariov2/sequence1/cifasis_gnss_si/run1` | ok | unknown | rerun_required |
| `results/vio/citrusfarm/seq04/airslam/run50001` | scale_collapse | 0 | blocked |
| `results/vio/citrusfarm/seq04/airslam/run50002` | scale_collapse | 0 | blocked |
| `results/vio/citrusfarm/seq04/airslam/run50003` | scale_collapse | 0 | blocked |
| `results/vio/citrusfarm/seq07/airslam/run50001` | scale_collapse | 0 | blocked |
| `results/vio/citrusfarm/seq07/airslam/run50002` | scale_collapse | 0 | blocked |
| `results/vio/citrusfarm/seq07/airslam/run50003` | scale_collapse | 0 | blocked |
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
| `results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run20002` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run20003` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run20004` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run20001` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run20002` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run20003` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run20001` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run20002` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run20003` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run20001` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run20002` | scale_collapse | 1 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run20003` | scale_collapse | 1 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run20001` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run20002` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run20003` | scale_collapse | 0 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/svo_pro/run20002` | failed_without_trajectory | 134 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run20002` | scale_collapse | 143 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run20003` | scale_collapse | 143 | blocked |
| `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run20004` | scale_collapse | 143 | blocked |
| `results/vio-lc/citrusfarm/seq04/airslam/run50002` | scale_collapse | 0 | blocked |
| `results/vio-lc/citrusfarm/seq04/airslam/run50201` | scale_collapse | 0 | blocked |
| `results/vio-lc/citrusfarm/seq04/airslam/run50203` | scale_collapse | 0 | blocked |
| `results/vio-lc/citrusfarm/seq07/airslam/run50201` | failed_without_trajectory | 139 | blocked |
| `results/vio-lc/citrusfarm/seq07/airslam/run50202` | failed_without_trajectory | 139 | blocked |
| `results/vio-lc/citrusfarm/seq07/airslam/run50203` | failed_without_trajectory | 139 | blocked |
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
| `results/vio-lc/rosariov2/sequence1/orbslam3/run10003` | failed_without_trajectory | 139 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/airslam/run40022` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/airslam/run40023` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run20001` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run20002` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run20003` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run20102` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run20103` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run20001` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run20002` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run20003` | scale_collapse | 0 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/svo_pro/run20001` | failed_without_trajectory | 134 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/svo_pro/run20002` | failed_without_trajectory | 134 | blocked |
| `results/vio-lc/zed2i/field1_110426_full_10fps_q90/svo_pro/run20003` | failed_without_trajectory | 134 | blocked |
| `results/vo/citrusfarm/seq04/dsol/run10002` | failed_without_trajectory | 134 | blocked |
| `results/vo/citrusfarm/seq04/dsol/run10003` | failed_without_trajectory | 134 | blocked |
| `results/vo/citrusfarm/seq04/dsol/run10004` | failed_without_trajectory | 134 | blocked |
| `results/vo/citrusfarm/seq04/svo_pro/run10002` | scale_collapse | 0 | blocked |
| `results/vo/citrusfarm/seq04/svo_pro/run10003` | scale_collapse | 0 | blocked |
| `results/vo/citrusfarm/seq04/svo_pro/run10004` | scale_collapse | 0 | blocked |
| `results/vo/citrusfarm/seq07/dsol/run10002` | failed_without_trajectory | 134 | blocked |
| `results/vo/citrusfarm/seq07/dsol/run10003` | failed_without_trajectory | 134 | blocked |
| `results/vo/citrusfarm/seq07/dsol/run10004` | failed_without_trajectory | 134 | blocked |
| `results/vo/citrusfarm/seq07/ov2slam/run10003` | scale_collapse | 0 | blocked |
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
| `results/vo/rosariov2/sequence5/macvo/run10002` | failed_without_trajectory | 139 | blocked |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | scale_collapse | 0 | valid_observed_failure |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/citrusfarm/seq07/dpvo/run10001` | eval_failed | 0 | blocked |
| `results/vo-lc/citrusfarm/seq07/ov2slam/run10001` | scale_collapse | 0 | blocked |
| `results/vo-lc/citrusfarm/seq07/ov2slam/run10002` | scale_collapse | 0 | blocked |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run1` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run2` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run3` | ok | 0 | accepted_with_limitation |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run10001` | incomplete | unknown | blocked |
| `` | failed_without_trajectory | unknown | blocked |
| `` | failed_without_trajectory | unknown | blocked |
| `` | failed_without_trajectory | unknown | blocked |
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
| `inventory.json` | `4cb61869d00b082d783a1c094560e376931713ce305ab8e55889a5d59670813e` |
| `benchmark-vo.csv` | `15f24cead099f3bbf6a2f7f0f03ad86d192b68a6ebaa7055318c910fa2e11442` |
| `benchmark-vo-lc.csv` | `6ee44492478ce698deda9cbf695b83b42b8732752f9617d70e9dc8bb7bb1afdf` |
| `benchmark-vio.csv` | `bcef2a8f90b79751c83b37e0c24476ed9e1223fea3066b94f882c0daef3ab749` |
| `benchmark-vio-lc.csv` | `16c3e58685a0f25ca057e42d909e99372581b5a420fc34bbdb3b7704730b2be8` |
| `benchmark-gnss-vio.csv` | `7eccab1f3b593feedcf877b31ca5618f33a3b6dffcd196c60dc45848acd88494` |
