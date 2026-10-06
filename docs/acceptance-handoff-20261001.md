# Acceptance handoff — 2026-10-01

Generated from the checked inventory. The [claim review](paper-acceptance-20261001.md) defines eligibility, limitations and evidence. This includes the [matched-session calibration review](reference-review-20261001.md): Rosario frame-dependent metrics were corrected; accepted EuRoC values and original attempts are preserved. **Acceptance review complete; focused EuRoC OpenVINS/AirSLAM execution validated. ZED short-check readiness is recorded separately below.**

| Mode | Protocol-verified N=3 cells | Accepted accuracy claims | Limited accuracy claims | Failure-only claim observations | Required reruns | Missing | Blocked |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 64 | 45 | 164 | 5 | 3 | 47 | 66 |
| vo-lc | 31 | 27 | 67 | 0 | 3 | 65 | 48 |
| vio | 56 | 27 | 141 | 3 | 0 | 42 | 87 |
| vio-lc | 23 | 18 | 41 | 10 | 10 | 104 | 27 |
| gnss-vio | 0 | 0 | 0 | 0 | 5 | 40 | 15 |

Protocol counts are separate from claim-status counts above. Success means a clean final export; native errors after saving remain failures with potentially usable accuracy.

| Mode | Verified attempts | Verified failures | Attempts | Evaluated | Clean exports | Observed failures | Unknown |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 214 | 17 | 283 | 281 | 264 | 19 | 0 |
| vo-lc | 94 | 12 | 145 | 143 | 125 | 20 | 0 |
| vio | 171 | 12 | 258 | 258 | 238 | 20 | 0 |
| vio-lc | 69 | 10 | 106 | 98 | 95 | 11 | 0 |
| gnss-vio | 0 | 0 | 20 | 20 | 0 | 2 | 18 |

**OpenVINS cohort completeness:** each EuRoC sequence has historical N=1 plus patched N=2. The selected logical slots are consumed. One additional patched repetition per sequence would complete that implementation cohort, only if separately authorized. These three potential additions are separate from the 81 absent planned slots and are not scheduled here. Old cohorts are not resampled for success.


Future default actions: 548 reusable observations, 247 required reruns, 298 missing repetitions, 17 blocked. The separately authorized focused EuRoC campaign is complete; its 24 attempts yielded 23 final evaluations and one retained native refinement failure. The later ZED preparation used bounded diagnostics only; no ZED production repetitions or push occurred.

## Protocol-verified N=3 cells

| Cell | Accepted claim |
|---|---|
| `vo/hortimulti/strawberry02/orbslam3` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry02/okvis2` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry02/okvis2x` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry02/airslam` | recorded_profile_hortimulti_sparse_keyframe_se3_metric_accuracy |
| `vo/hortimulti/strawberry02/basalt` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry02/ov2slam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry02/dpvo` | recorded_profile_hortimulti_final_trajectory_sim3_monocular_shape |
| `vo/hortimulti/strawberry02/macvo` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry02/cuvslam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry02/svo_pro` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry02/dsol` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/orbslam3` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/okvis2` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/okvis2x` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/airslam` | recorded_profile_hortimulti_sparse_keyframe_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/basalt` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/ov2slam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/dpvo` | recorded_profile_hortimulti_final_trajectory_sim3_monocular_shape |
| `vo/hortimulti/strawberry03/macvo` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/cuvslam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/svo_pro` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/hortimulti/strawberry03/dsol` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/airslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/ov2slam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo/euroc_mav/MH_01_easy/macvo` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/cuvslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/svo_pro` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_01_easy/dsol` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/airslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/ov2slam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo/euroc_mav/MH_03_medium/macvo` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/cuvslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/svo_pro` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_03_medium/dsol` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/airslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/ov2slam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo/euroc_mav/MH_05_difficult/macvo` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/cuvslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/svo_pro` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/euroc_mav/MH_05_difficult/dsol` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo/zed2i/field1_110426_full_10fps_q90/okvis2` | nominal_zed_se3_final_position_accuracy |
| `vo/zed2i/field1_110426_full_10fps_q90/okvis2x` | nominal_zed_se3_final_position_accuracy |
| `vo/zed2i/field1_110426_full_10fps_q90/airslam` | nominal_zed_se3_final_position_accuracy |
| `vo/zed2i/field1_110426_full_10fps_q90/basalt` | nominal_zed_se3_final_position_accuracy |
| `vo/zed2i/field1_110426_full_10fps_q90/ov2slam` | nominal_zed_se3_final_position_accuracy |
| `vo/zed2i/field1_110426_full_10fps_q90/dpvo` | nominal_zed_sim3_monocular_position_shape |
| `vo/zed2i/field1_110426_full_10fps_q90/macvo` | nominal_zed_se3_final_position_accuracy |
| `vo/citrusfarm/seq04/orbslam3` | nominal_citrusfarm_se3_final_position_accuracy |
| `vo/citrusfarm/seq07/orbslam3` | nominal_citrusfarm_se3_final_position_accuracy |
| `vo-lc/hortimulti/strawberry02/orbslam3` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry02/okvis2` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry02/okvis2x` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry02/airslam` | recorded_profile_hortimulti_sparse_keyframe_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry02/ov2slam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry02/dpvo` | recorded_profile_hortimulti_final_trajectory_sim3_monocular_shape |
| `vo-lc/hortimulti/strawberry02/cuvslam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry03/orbslam3` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry03/okvis2` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry03/okvis2x` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry03/airslam` | recorded_profile_hortimulti_sparse_keyframe_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry03/ov2slam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/hortimulti/strawberry03/dpvo` | recorded_profile_hortimulti_final_trajectory_sim3_monocular_shape |
| `vo-lc/hortimulti/strawberry03/cuvslam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_01_easy/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_01_easy/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_01_easy/airslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_01_easy/ov2slam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_01_easy/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo-lc/euroc_mav/MH_03_medium/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_03_medium/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_03_medium/airslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_03_medium/ov2slam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_03_medium/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo-lc/euroc_mav/MH_05_difficult/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_05_difficult/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_05_difficult/airslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_05_difficult/ov2slam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vo-lc/euroc_mav/MH_05_difficult/dpvo` | recorded_profile_euroc_final_trajectory_sim3_monocular_shape |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam` | nominal_zed_se3_final_position_accuracy |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/dpvo` | nominal_zed_sim3_monocular_position_shape |
| `vio/hortimulti/strawberry02/orbslam3` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry02/okvis2` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry02/okvis2x` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry02/airslam` | recorded_profile_hortimulti_sparse_keyframe_se3_metric_accuracy |
| `vio/hortimulti/strawberry02/basalt` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry02/openvins` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry02/voxel_svio` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry02/cuvslam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry02/svo_pro` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry02/mast3r_fusion` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/orbslam3` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/okvis2` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/okvis2x` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/airslam` | recorded_profile_hortimulti_sparse_keyframe_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/basalt` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/openvins` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/voxel_svio` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/cuvslam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/svo_pro` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio/hortimulti/strawberry03/mast3r_fusion` | None |
| `vio/euroc_mav/MH_01_easy/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/airslam` | recorded_profile_euroc_sparse_keyframe_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/openvins` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/voxel_svio` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/cuvslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/svo_pro` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_01_easy/mast3r_fusion` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/airslam` | recorded_profile_euroc_sparse_keyframe_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/openvins` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/voxel_svio` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/cuvslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/svo_pro` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_03_medium/mast3r_fusion` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/orbslam3` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/airslam` | recorded_profile_euroc_sparse_keyframe_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/basalt` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/openvins` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/voxel_svio` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/cuvslam` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/svo_pro` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/euroc_mav/MH_05_difficult/mast3r_fusion` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio/zed2i/field1_110426_full_10fps_q90/orbslam3` | nominal_zed_se3_final_position_accuracy |
| `vio/zed2i/field1_110426_full_10fps_q90/okvis2` | nominal_zed_se3_final_position_accuracy |
| `vio/zed2i/field1_110426_full_10fps_q90/okvis2x` | nominal_zed_se3_final_position_accuracy |
| `vio/zed2i/field1_110426_full_10fps_q90/airslam` | nominal_zed_se3_final_position_accuracy |
| `vio/zed2i/field1_110426_full_10fps_q90/basalt` | nominal_zed_se3_final_position_accuracy |
| `vio/zed2i/field1_110426_full_10fps_q90/voxel_svio` | nominal_zed_se3_final_position_accuracy |
| `vio-lc/hortimulti/strawberry02/orbslam3` | None |
| `vio-lc/hortimulti/strawberry02/okvis2` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry02/okvis2x` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry02/airslam` | recorded_profile_hortimulti_sparse_keyframe_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry02/cuvslam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry02/svo_pro` | None |
| `vio-lc/hortimulti/strawberry02/mast3r_fusion` | recorded_profile_hortimulti_sparse_keyframe_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry03/orbslam3` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry03/okvis2` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry03/okvis2x` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry03/airslam` | recorded_profile_hortimulti_sparse_keyframe_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry03/cuvslam` | recorded_profile_hortimulti_final_trajectory_se3_metric_accuracy |
| `vio-lc/hortimulti/strawberry03/svo_pro` | None |
| `vio-lc/hortimulti/strawberry03/mast3r_fusion` | None |
| `vio-lc/euroc_mav/MH_01_easy/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_01_easy/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_01_easy/airslam` | recorded_profile_euroc_sparse_keyframe_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_03_medium/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_03_medium/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_03_medium/airslam` | recorded_profile_euroc_sparse_keyframe_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_05_difficult/okvis2` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_05_difficult/okvis2x` | recorded_profile_euroc_final_trajectory_se3_metric_accuracy |
| `vio-lc/euroc_mav/MH_05_difficult/airslam` | configured_attempt_native_refinement_failure_under_corrected_euroc_profile |

## Limited results and accepted failures

| Attempt | Acceptance | Specific limit |
|---|---|---|
| `results/vo/hortimulti/strawberry02/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/okvis2/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/okvis2/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/okvis2/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/okvis2x/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/okvis2x/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/okvis2x/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/airslam/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo/hortimulti/strawberry02/airslam/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo/hortimulti/strawberry02/airslam/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo/hortimulti/strawberry02/basalt/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/basalt/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/basalt/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/ov2slam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/ov2slam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/ov2slam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/dpvo/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/dpvo/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/dpvo/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/macvo/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/macvo/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/macvo/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry02/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/dsol/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/dsol/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry02/dsol/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/okvis2/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/okvis2/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/okvis2/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/okvis2x/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/okvis2x/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/okvis2x/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/airslam/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo/hortimulti/strawberry03/airslam/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo/hortimulti/strawberry03/airslam/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo/hortimulti/strawberry03/basalt/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/basalt/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/basalt/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/ov2slam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/ov2slam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/ov2slam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/dpvo/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/dpvo/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/dpvo/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/macvo/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/macvo/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/macvo/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo/hortimulti/strawberry03/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/dsol/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/dsol/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/hortimulti/strawberry03/dsol/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_01_easy/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_01_easy/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_01_easy/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_01_easy/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/dsol/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/dsol/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_01_easy/dsol/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_03_medium/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_03_medium/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_03_medium/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_03_medium/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/dsol/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_03_medium/dsol/run10002` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator |
| `results/vo/euroc_mav/MH_03_medium/dsol/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_05_difficult/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_05_difficult/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_05_difficult/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo/euroc_mav/MH_05_difficult/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/dsol/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/dsol/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/euroc_mav/MH_05_difficult/dsol/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2` | valid_observed_failure | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; retain_failure_in_attempt_denominator; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run3` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2x/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2x/run2` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/okvis2x/run3` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/airslam/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; native_sparse_keyframe_accuracy_not_dense_tracking; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/airslam/run2` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; native_sparse_keyframe_accuracy_not_dense_tracking; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/airslam/run3` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; native_sparse_keyframe_accuracy_not_dense_tracking; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/basalt/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/basalt/run2` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/basalt/run3` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; native_shutdown_error_despite_wrapper_exit_zero_retain_failure_count; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; native_shutdown_error_despite_wrapper_exit_zero_retain_failure_count; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; native_shutdown_error_despite_wrapper_exit_zero_retain_failure_count; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/dpvo/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/dpvo/run2` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/dpvo/run3` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/macvo/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; official_performant_profile_not_paper_reproduction_profile; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/macvo/run2` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; official_performant_profile_not_paper_reproduction_profile; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/macvo/run3` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; official_performant_profile_not_paper_reproduction_profile; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/cuvslam/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vo/zed2i/field1_110426_full_10fps_q90/svo_pro/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vo/citrusfarm/seq04/orbslam3/run10002` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/orbslam3/run10003` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/orbslam3/run10004` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/okvis2/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/okvis2x/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/airslam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vo/citrusfarm/seq04/basalt/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/ov2slam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/dpvo/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; monocular_sim3_shape_only_not_metric_stereo_ranking; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/macvo/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; official_performant_profile_not_paper_reproduction_profile; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/cuvslam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq04/svo_pro/run10001` | valid_observed_failure | authors_export_starts_after_keyframe_window_fills; citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator |
| `results/vo/citrusfarm/seq04/dsol/run10001` | valid_observed_failure | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator |
| `results/vo/citrusfarm/seq07/orbslam3/run10002` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/orbslam3/run10003` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/orbslam3/run10004` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/okvis2/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/okvis2x/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/airslam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vo/citrusfarm/seq07/basalt/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/ov2slam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/dpvo/run10002` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; monocular_sim3_shape_only_not_metric_stereo_ranking; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/macvo/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; official_performant_profile_not_paper_reproduction_profile; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/cuvslam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo/citrusfarm/seq07/dsol/run10001` | valid_observed_failure | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry02/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry02/okvis2/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry02/okvis2/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry02/okvis2/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry02/okvis2x/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry02/okvis2x/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry02/okvis2x/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry02/airslam/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo-lc/hortimulti/strawberry02/airslam/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo-lc/hortimulti/strawberry02/airslam/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo-lc/hortimulti/strawberry02/ov2slam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry02/ov2slam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry02/ov2slam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry02/dpvo/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry02/dpvo/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry02/dpvo/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry02/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry02/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry02/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry03/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry03/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry03/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry03/okvis2/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry03/okvis2/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry03/okvis2/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry03/okvis2x/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry03/okvis2x/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry03/okvis2x/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry03/airslam/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo-lc/hortimulti/strawberry03/airslam/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo-lc/hortimulti/strawberry03/airslam/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; sparse_keyframe_accuracy_only |
| `results/vo-lc/hortimulti/strawberry03/ov2slam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry03/ov2slam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry03/ov2slam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry03/dpvo/run1` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry03/dpvo/run2` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry03/dpvo/run3` | accepted_with_limitation | hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006 |
| `results/vo-lc/hortimulti/strawberry03/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry03/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/hortimulti/strawberry03/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vo-lc/euroc_mav/MH_01_easy/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_01_easy/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_01_easy/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_03_medium/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_03_medium/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_03_medium/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_05_difficult/airslam/run1` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_05_difficult/airslam/run2` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_05_difficult/airslam/run3` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; final_ba_disabled; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; native_shutdown_error_despite_wrapper_exit_zero_retain_failure_count; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run2` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; native_shutdown_error_despite_wrapper_exit_zero_retain_failure_count; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run3` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; native_shutdown_error_despite_wrapper_exit_zero_retain_failure_count; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/dpvo/run1` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/dpvo/run2` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vo-lc/zed2i/field1_110426_full_10fps_q90/dpvo/run3` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; historical_profile_accuracy_not_bitwise_build_reproduction; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; unmeasured_field_clock_zero_offset_with_frozen_sensitivity; zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity |
| `results/vio/hortimulti/strawberry02/orbslam3/run10004` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/orbslam3/run10005` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/orbslam3/run10006` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/okvis2/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/okvis2/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/okvis2/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/okvis2x/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/okvis2x/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/okvis2x/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/airslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio/hortimulti/strawberry02/airslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio/hortimulti/strawberry02/airslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio/hortimulti/strawberry02/basalt/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/basalt/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/basalt/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/openvins/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/openvins/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/openvins/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/voxel_svio/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/voxel_svio/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/voxel_svio/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry02/mast3r_fusion/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/hortimulti/strawberry02/mast3r_fusion/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/hortimulti/strawberry02/mast3r_fusion/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/hortimulti/strawberry03/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/okvis2/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/okvis2/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/okvis2/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/okvis2x/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/okvis2x/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/okvis2x/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/airslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio/hortimulti/strawberry03/airslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio/hortimulti/strawberry03/airslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio/hortimulti/strawberry03/basalt/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/basalt/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/basalt/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/openvins/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/openvins/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/openvins/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/voxel_svio/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/voxel_svio/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/voxel_svio/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/hortimulti/strawberry03/mast3r_fusion/run10001` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/hortimulti/strawberry03/mast3r_fusion/run10002` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/hortimulti/strawberry03/mast3r_fusion/run10003` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/euroc_mav/MH_01_easy/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_01_easy/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_01_easy/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_01_easy/openvins/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/openvins/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/openvins/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run1` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick; native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run2` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick; native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_01_easy/voxel_svio/run3` | accepted_with_limitation | export_coverage_below_95_percent_no_clean_success_tick; native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_01_easy/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_01_easy/mast3r_fusion/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/euroc_mav/MH_01_easy/mast3r_fusion/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/euroc_mav/MH_01_easy/mast3r_fusion/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/euroc_mav/MH_03_medium/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_03_medium/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_03_medium/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_03_medium/openvins/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/openvins/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/openvins/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_03_medium/voxel_svio/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_03_medium/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_03_medium/mast3r_fusion/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/euroc_mav/MH_03_medium/mast3r_fusion/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/euroc_mav/MH_03_medium/mast3r_fusion/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/euroc_mav/MH_05_difficult/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_05_difficult/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_05_difficult/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only |
| `results/vio/euroc_mav/MH_05_difficult/openvins/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/openvins/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/openvins/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run1` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run2` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_05_difficult/voxel_svio/run3` | accepted_with_limitation | native_shutdown_error_despite_wrapper_exit_zero |
| `results/vio/euroc_mav/MH_05_difficult/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/euroc_mav/MH_05_difficult/mast3r_fusion/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/euroc_mav/MH_05_difficult/mast3r_fusion/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/euroc_mav/MH_05_difficult/mast3r_fusion/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run10003` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run10004` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run10003` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run10004` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run10003` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run10004` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; native_sparse_keyframe_accuracy_not_dense_tracking; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run10002` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; native_sparse_keyframe_accuracy_not_dense_tracking; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run10003` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; native_sparse_keyframe_accuracy_not_dense_tracking; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/basalt/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/basalt/run10002` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/basalt/run10003` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run10002` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run10003` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/cuvslam/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/svo_pro/run10001` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio/zed2i/field1_110426_full_10fps_q90/mast3r_fusion/run10002` | accepted_with_limitation | approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth; unmeasured_field_clock_zero_offset_with_frozen_sensitivity |
| `results/vio-lc/hortimulti/strawberry02/orbslam3/run10001` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator |
| `results/vio-lc/hortimulti/strawberry02/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/okvis2/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_disabled; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/okvis2/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_disabled; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/okvis2/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_disabled; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/okvis2x/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_enabled_with_extrinsic_optimization; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/okvis2x/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_enabled_with_extrinsic_optimization; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/okvis2x/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_enabled_with_extrinsic_optimization; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/airslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry02/airslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry02/airslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry02/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry02/svo_pro/run10001` | valid_observed_failure | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; loop_corrections_applied_forward_not_retroactively; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator |
| `results/vio-lc/hortimulti/strawberry02/svo_pro/run10002` | valid_observed_failure | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; loop_corrections_applied_forward_not_retroactively; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator |
| `results/vio-lc/hortimulti/strawberry02/svo_pro/run10003` | valid_observed_failure | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; loop_corrections_applied_forward_not_retroactively; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator |
| `results/vio-lc/hortimulti/strawberry02/mast3r_fusion/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; keyframe_only_globally_optimised_trajectory; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry02/mast3r_fusion/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; keyframe_only_globally_optimised_trajectory; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry02/mast3r_fusion/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; keyframe_only_globally_optimised_trajectory; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry03/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/okvis2/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_disabled; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/okvis2/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_disabled; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/okvis2/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_disabled; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/okvis2x/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_enabled_with_extrinsic_optimization; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/okvis2x/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_enabled_with_extrinsic_optimization; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/okvis2x/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; final_ba_enabled_with_extrinsic_optimization; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/airslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry03/airslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry03/airslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry03/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/svo_pro/run10001` | valid_observed_failure | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; loop_corrections_applied_forward_not_retroactively; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator |
| `results/vio-lc/hortimulti/strawberry03/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; loop_corrections_applied_forward_not_retroactively; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio-lc/hortimulti/strawberry03/svo_pro/run10003` | valid_observed_failure | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; loop_corrections_applied_forward_not_retroactively; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator |
| `results/vio-lc/hortimulti/strawberry03/mast3r_fusion/run10001` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; keyframe_only_globally_optimised_trajectory; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator; single_camera_with_imu_scale_from_imu_and_learned_depth; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry03/mast3r_fusion/run10002` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; keyframe_only_globally_optimised_trajectory; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator; single_camera_with_imu_scale_from_imu_and_learned_depth; sparse_keyframe_accuracy_only |
| `results/vio-lc/hortimulti/strawberry03/mast3r_fusion/run10003` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; export_coverage_below_95_percent_no_clean_success_tick; hortimulti_reference_frame_and_clock_as_recorded_user_decision_20261006; keyframe_only_globally_optimised_trajectory; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator; single_camera_with_imu_scale_from_imu_and_learned_depth; sparse_keyframe_accuracy_only |
| `results/vio-lc/euroc_mav/MH_01_easy/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_01_easy/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_01_easy/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_03_medium/airslam/run4` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_03_medium/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_03_medium/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run4` | valid_observed_failure | retain_failure_in_attempt_denominator; no_final_vio_lc_trajectory_no_accuracy_claim; intermediate_odometry_is_diagnostic_only; native_junction_database_segfault_root_cause_unresolved |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run5` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |
| `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run6` | accepted_with_limitation | sparse_keyframe_accuracy_only; final_offline_map_refinement_accuracy_not_causal_online_trajectory |

## Exact required reruns

There are 247 remaining distinct confirmed cases after the current cohort selection. Superseded affected AirSLAM attempts remain in their original directories and the historical-cohort CSV. Preserve every original attempt and use a new physical ID/cohort.

| Cell | Logical repetitions | Concrete defect |
|---|---|---|
| `vo/rosariov2/sequence1/orbslam3` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/okvis2` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/okvis2x` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/airslam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/basalt` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/ov2slam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/dpvo` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/macvo` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/cuvslam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/svo_pro` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence1/dsol` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/orbslam3` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/okvis2` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/okvis2x` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/airslam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/basalt` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/ov2slam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/dpvo` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/macvo` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/cuvslam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/svo_pro` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/rosariov2/sequence5/dsol` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vo-lc/rosariov2/sequence1/orbslam3` | r1 | historical_orb_library_identity_unverified;rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence1/okvis2` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence1/okvis2x` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence1/airslam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence1/ov2slam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence1/dpvo` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence5/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence5/okvis2` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence5/okvis2x` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence5/airslam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence5/ov2slam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/rosariov2/sequence5/dpvo` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vo-lc/euroc_mav/MH_01_easy/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/euroc_mav/MH_03_medium/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/euroc_mav/MH_05_difficult/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/airslam` | r1, r2, r3 | airslam_zed_vo_lc_split_workspace_groups |
| `vio/rosariov2/sequence1/orbslam3` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vio/rosariov2/sequence1/okvis2` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence1/okvis2x` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence1/airslam` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence1/basalt` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence1/openvins` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence1/voxel_svio` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence1/cuvslam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vio/rosariov2/sequence1/svo_pro` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence1/mast3r_fusion` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence5/orbslam3` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vio/rosariov2/sequence5/okvis2` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence5/okvis2x` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence5/airslam` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence5/basalt` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence5/openvins` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence5/voxel_svio` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence5/cuvslam` | r1, r2, r3 | rosario_camera_clock_model_superseded |
| `vio/rosariov2/sequence5/svo_pro` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/rosariov2/sequence5/mast3r_fusion` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio/zed2i/field1_110426_full_10fps_q90/openvins` | r1, r2, r3 | openvins_track_frequency_dropped_frames |
| `vio/citrusfarm/seq04/orbslam3` | r1, r2, r3 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq04/okvis2` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq04/okvis2x` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq04/airslam` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq04/basalt` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq04/openvins` | r1 | openvins_track_frequency_dropped_frames;imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq04/voxel_svio` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq04/cuvslam` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq04/svo_pro` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq04/mast3r_fusion` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/orbslam3` | r1, r2, r3 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/okvis2` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/okvis2x` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/airslam` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/basalt` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/openvins` | r1 | openvins_track_frequency_dropped_frames;imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/voxel_svio` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/cuvslam` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/svo_pro` | r1 | imu_noise_not_at_authors_operating_point |
| `vio/citrusfarm/seq07/mast3r_fusion` | r1 | imu_noise_not_at_authors_operating_point |
| `vio-lc/rosariov2/sequence1/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;rosario_camera_clock_model_superseded |
| `vio-lc/rosariov2/sequence1/okvis2` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio-lc/rosariov2/sequence1/okvis2x` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio-lc/rosariov2/sequence1/airslam` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point;rosario_identity_camera_imu_extrinsic |
| `vio-lc/rosariov2/sequence5/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;rosario_camera_clock_model_superseded |
| `vio-lc/rosariov2/sequence5/okvis2` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio-lc/rosariov2/sequence5/okvis2x` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point |
| `vio-lc/rosariov2/sequence5/airslam` | r1, r2, r3 | rosario_camera_clock_model_superseded;imu_noise_not_at_authors_operating_point;rosario_identity_camera_imu_extrinsic |
| `vio-lc/euroc_mav/MH_01_easy/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/euroc_mav/MH_03_medium/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/euroc_mav/MH_05_difficult/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1 | zed_factory_camera_imu_rotation_omitted |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | r1 | zed_factory_camera_imu_rotation_omitted |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | r1 | zed_factory_camera_imu_rotation_omitted |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/airslam` | r1 | zed_factory_camera_imu_rotation_omitted |
| `gnss-vio/rosariov2/sequence1/cifasis_gnss_si` | r1 | rosario_v1_antenna_lever_arm_used_on_v2 |
| `gnss-vio/rosariov2/sequence1/okvis2x` | r1 | gnss_zero_antenna_lever_arm_in_native_log |
| `gnss-vio/rosariov2/sequence5/okvis2x` | r1 | gnss_zero_antenna_lever_arm_in_native_log |
| `gnss-vio/hortimulti/strawberry02/okvis2x` | r1 | gnss_zero_antenna_lever_arm_in_native_log |
| `gnss-vio/hortimulti/strawberry03/okvis2x` | r1 | gnss_zero_antenna_lever_arm_in_native_log |

## Exact missing repetitions

Missing means no original attempt directory; an existing failed attempt is not reclassified as missing.

| Cell | Missing logical repetitions |
|---|---|
| `vo/zed2i/field1_110426_full_10fps_q90/cuvslam` | r2, r3 |
| `vo/zed2i/field1_110426_full_10fps_q90/svo_pro` | r2, r3 |
| `vo/zed2i/field1_110426_full_10fps_q90/dsol` | r1, r2, r3 |
| `vo/citrusfarm/seq04/okvis2` | r2, r3 |
| `vo/citrusfarm/seq04/okvis2x` | r2, r3 |
| `vo/citrusfarm/seq04/airslam` | r2, r3 |
| `vo/citrusfarm/seq04/basalt` | r2, r3 |
| `vo/citrusfarm/seq04/ov2slam` | r2, r3 |
| `vo/citrusfarm/seq04/dpvo` | r2, r3 |
| `vo/citrusfarm/seq04/macvo` | r2, r3 |
| `vo/citrusfarm/seq04/cuvslam` | r2, r3 |
| `vo/citrusfarm/seq04/svo_pro` | r2, r3 |
| `vo/citrusfarm/seq04/dsol` | r2, r3 |
| `vo/citrusfarm/seq07/okvis2` | r2, r3 |
| `vo/citrusfarm/seq07/okvis2x` | r2, r3 |
| `vo/citrusfarm/seq07/airslam` | r2, r3 |
| `vo/citrusfarm/seq07/basalt` | r2, r3 |
| `vo/citrusfarm/seq07/ov2slam` | r2, r3 |
| `vo/citrusfarm/seq07/dpvo` | r2, r3 |
| `vo/citrusfarm/seq07/macvo` | r2, r3 |
| `vo/citrusfarm/seq07/cuvslam` | r2, r3 |
| `vo/citrusfarm/seq07/svo_pro` | r2, r3 |
| `vo/citrusfarm/seq07/dsol` | r2, r3 |
| `vo-lc/rosariov2/sequence1/orbslam3` | r2, r3 |
| `vo-lc/rosariov2/sequence1/cuvslam` | r1, r2, r3 |
| `vo-lc/rosariov2/sequence5/cuvslam` | r1, r2, r3 |
| `vo-lc/euroc_mav/MH_01_easy/cuvslam` | r1, r2, r3 |
| `vo-lc/euroc_mav/MH_03_medium/cuvslam` | r1, r2, r3 |
| `vo-lc/euroc_mav/MH_05_difficult/cuvslam` | r1, r2, r3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | r3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | r2, r3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/cuvslam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/orbslam3` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/okvis2` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/okvis2x` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/airslam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/ov2slam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/dpvo` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq04/cuvslam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/orbslam3` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/okvis2` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/okvis2x` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/airslam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/ov2slam` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/dpvo` | r1, r2, r3 |
| `vo-lc/citrusfarm/seq07/cuvslam` | r1, r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/cuvslam` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/svo_pro` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/mast3r_fusion` | r2, r3 |
| `vio/citrusfarm/seq04/okvis2` | r2, r3 |
| `vio/citrusfarm/seq04/okvis2x` | r2, r3 |
| `vio/citrusfarm/seq04/airslam` | r2, r3 |
| `vio/citrusfarm/seq04/basalt` | r2, r3 |
| `vio/citrusfarm/seq04/openvins` | r2, r3 |
| `vio/citrusfarm/seq04/voxel_svio` | r2, r3 |
| `vio/citrusfarm/seq04/cuvslam` | r2, r3 |
| `vio/citrusfarm/seq04/svo_pro` | r2, r3 |
| `vio/citrusfarm/seq04/mast3r_fusion` | r2, r3 |
| `vio/citrusfarm/seq07/okvis2` | r2, r3 |
| `vio/citrusfarm/seq07/okvis2x` | r2, r3 |
| `vio/citrusfarm/seq07/airslam` | r2, r3 |
| `vio/citrusfarm/seq07/basalt` | r2, r3 |
| `vio/citrusfarm/seq07/openvins` | r2, r3 |
| `vio/citrusfarm/seq07/voxel_svio` | r2, r3 |
| `vio/citrusfarm/seq07/cuvslam` | r2, r3 |
| `vio/citrusfarm/seq07/svo_pro` | r2, r3 |
| `vio/citrusfarm/seq07/mast3r_fusion` | r2, r3 |
| `vio-lc/rosariov2/sequence1/cuvslam` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence1/svo_pro` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence1/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence5/cuvslam` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence5/svo_pro` | r1, r2, r3 |
| `vio-lc/rosariov2/sequence5/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_01_easy/cuvslam` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_01_easy/svo_pro` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_01_easy/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_03_medium/cuvslam` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_03_medium/svo_pro` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_03_medium/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_05_difficult/cuvslam` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_05_difficult/svo_pro` | r1, r2, r3 |
| `vio-lc/euroc_mav/MH_05_difficult/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/airslam` | r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/cuvslam` | r1, r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/svo_pro` | r1, r2, r3 |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/orbslam3` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/okvis2` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/okvis2x` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/airslam` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/cuvslam` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/svo_pro` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq04/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/orbslam3` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/okvis2` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/okvis2x` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/airslam` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/cuvslam` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/svo_pro` | r1, r2, r3 |
| `vio-lc/citrusfarm/seq07/mast3r_fusion` | r1, r2, r3 |
| `gnss-vio/rosariov2/sequence1/cifasis_gnss_si` | r2, r3 |
| `gnss-vio/rosariov2/sequence1/okvis2x` | r2, r3 |
| `gnss-vio/rosariov2/sequence1/openvins_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence1/rtabmap_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence1/vins_fusion_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/cifasis_gnss_si` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/okvis2x` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/openvins_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/rtabmap_gps` | r2, r3 |
| `gnss-vio/rosariov2/sequence5/vins_fusion_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/cifasis_gnss_si` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/okvis2x` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/openvins_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/rtabmap_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry02/vins_fusion_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/cifasis_gnss_si` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/okvis2x` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/openvins_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/rtabmap_gps` | r2, r3 |
| `gnss-vio/hortimulti/strawberry03/vins_fusion_gps` | r2, r3 |

## Material blockers

Exact affected attempt IDs and evidence are in `results/acceptance-20261001/handoff.json` and the future manifest. Counts overlap across blockers.

| Evidence needed | Blocked attempts |
|---|---:|
| estimate_frame_unverified: output frame not established for cifasis_gnss_si | 3 |
| estimate_frame_unverified: output frame not established for openvins_gps | 4 |
| estimate_frame_unverified: output frame not established for rtabmap_gps | 4 |
| estimate_frame_unverified: output frame not established for vins_fusion_gps | 4 |
| gnss_reference_independence_and_global_frame_not_established | 15 |
| historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified | 15 |
| horti_february_reference_generation_origin_and_timestamp_linkage_unresolved | 8 |
| native_execution_cause_and_usable_export_missing | 1 |
| native_execution_cause_unresolved_recovered_causal_prefix_not_final_ba | 1 |

## Completed focused execution

The three EuRoC OpenVINS/AirSLAM integration targets and first full gates passed. All six missing OpenVINS repetitions and all 18 corrected AirSLAM slots were consumed once, with immediate evaluation where final output existed and no success-conditioned retries. MH05 VIO-LC run4 has a native refinement SIGSEGV without final output (later reproduced in the map publisher; exact cause unresolved); runs5–6 succeeded. See [the focused campaign](euroc-focused-campaign-20261001.md) for source, build, configuration, output and shutdown evidence. AirSLAM supports sparse-keyframe accuracy; OpenVINS original run1 limitations and its separate implementation cohort remain. Protocol ticks include verified failures and supported sparse/partial outputs; OpenVINS implementation cohorts remain N=1 and N=2.

## Remaining execution prerequisites

The [ZED preparation](zed-preparation-20261002.md) validates 15 repaired algorithm/mode paths on a fixed 60-second input, including all four ORB modes. Voxel shutdown/failure reporting is verified, but initialization and successful trajectory export remain unverified. The non-ZED ORB build and OV2SLAM shutdown issues remain prerequisites. Rosario/HortiMulti/GNSS calibration/reference blockers are unchanged. Historical OKVIS interruptions remain unresolved outcomes. No production execution is authorized by this handoff.

**ZED cohort plan:** retain nine complete N=3 cells (27 observations). The remaining sixteen cells need 48 new attempts: 17 setup replacements, 25 missing slots and six separately labelled cohort-completion attempts. The latter preserve historical outcomes and are not confirmed parameter defects. Use the alternative `results/zed-preparation-20261002/campaign/manifest.json`; do not execute it in addition to the overlapping all-mode plan. See the ZED report for bounded readiness and timing proxies.

The following representatives cover the other algorithm/mode branches; a validated EuRoC path does not certify another dataset.

| Diagnostic target | Execution status | Full-sequence historical seconds (not diagnostic estimate) |
|---|---|---:|
| `vio/euroc_mav/MH_01_easy/airslam` | focused campaign validated | unknown |
| `vio-lc/euroc_mav/MH_01_easy/airslam` | focused campaign validated | unknown |
| `vo/euroc_mav/MH_01_easy/airslam` | deferred | unknown |
| `vo-lc/euroc_mav/MH_01_easy/airslam` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/basalt` | deferred | 9.6 |
| `vo/euroc_mav/MH_01_easy/basalt` | deferred | 10.6 |
| `gnss-vio/rosariov2/sequence1/cifasis_gnss_si` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/cuvslam` | deferred | 9.9 |
| `vio-lc/euroc_mav/MH_01_easy/cuvslam` | deferred | unknown |
| `vo/euroc_mav/MH_01_easy/cuvslam` | deferred | 4.2 |
| `vo-lc/euroc_mav/MH_01_easy/cuvslam` | deferred | unknown |
| `vo/euroc_mav/MH_01_easy/dpvo` | deferred | 86.2 |
| `vo-lc/euroc_mav/MH_01_easy/dpvo` | deferred | 95.0 |
| `vo/euroc_mav/MH_01_easy/dsol` | deferred | 20.7 |
| `vo/euroc_mav/MH_01_easy/macvo` | deferred | 721.6 |
| `vio/euroc_mav/MH_01_easy/mast3r_fusion` | deferred | 140.3 |
| `vio-lc/euroc_mav/MH_01_easy/mast3r_fusion` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/okvis2` | deferred | 208.2 |
| `vio-lc/euroc_mav/MH_01_easy/okvis2` | deferred | 231.2 |
| `vo/euroc_mav/MH_01_easy/okvis2` | deferred | 229.8 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2` | ZED short check passed | 22199.5 |
| `gnss-vio/rosariov2/sequence1/okvis2x` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/okvis2x` | deferred | 203.5 |
| `vio-lc/euroc_mav/MH_01_easy/okvis2x` | deferred | 228.3 |
| `vo/euroc_mav/MH_01_easy/okvis2x` | deferred | 220.2 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x` | ZED short check passed | unknown |
| `vio/euroc_mav/MH_01_easy/openvins` | focused campaign validated | 191.4 |
| `gnss-vio/rosariov2/sequence1/openvins_gps` | deferred | unknown |
| `vio/zed2i/field1_110426_full_10fps_q90/orbslam3` | ZED short check passed | 5526.8 |
| `vio-lc/hortimulti/strawberry02/orbslam3` | deferred | 1031.5 |
| `vo/zed2i/field1_110426_full_10fps_q90/orbslam3` | ZED short check passed | unknown |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | ZED short check passed | unknown |
| `vo/euroc_mav/MH_01_easy/ov2slam` | deferred | unknown |
| `vo-lc/euroc_mav/MH_01_easy/ov2slam` | deferred | unknown |
| `gnss-vio/rosariov2/sequence1/rtabmap_gps` | deferred | unknown |
| `vio/euroc_mav/MH_01_easy/svo_pro` | deferred | unknown |
| `vio-lc/euroc_mav/MH_01_easy/svo_pro` | deferred | unknown |
| `vo/euroc_mav/MH_01_easy/svo_pro` | deferred | 24.4 |
| `gnss-vio/rosariov2/sequence1/vins_fusion_gps` | deferred | unknown |
| `vio/euroc_mav/MH_03_medium/voxel_svio` | deferred | unknown |
| `vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | ZED short check passed | unknown |

The timing subtotal is 15.0 serialized hours for 41 of the 545 required/missing actions; 504 have no comparable complete same-cell timing. It excludes native-error samples, diagnostics, unresolved blocked cases and evaluation/capture overhead. No total-campaign runtime is justified.

## Reproduction and preservation

Regenerate inventory, reconcile qualification, promote checked evaluations, then regenerate CSVs, TODO, reports and this handoff. Rosario evaluation uses the matched physical IMU-to-camera transform. The later ZED review uses the versioned nominal 3D position reference and recovered factory extrinsics; non-ZED numerical scores remain unchanged. Review decisions fail closed if pinned evidence changes. Run `build_future_manifest.py` after source/input/asset refresh; ordinary validation is read-only and is not readiness approval. The historical authorship mapping and all original provenance hashes remain intact. The obsolete temporary pause remains explicitly revoked.
