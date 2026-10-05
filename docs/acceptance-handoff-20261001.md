# Acceptance handoff — 2026-10-01

Generated from the checked inventory. The [claim review](paper-acceptance-20261001.md) defines eligibility, limitations and evidence. This includes the [matched-session calibration review](reference-review-20261001.md): Rosario frame-dependent metrics were corrected; accepted EuRoC values and original attempts are preserved. **Acceptance review complete; focused EuRoC OpenVINS/AirSLAM execution validated. ZED short-check readiness is recorded separately below.**

| Mode | Protocol-verified N=3 cells | Accepted accuracy claims | Limited accuracy claims | Failure-only claim observations | Required reruns | Missing | Blocked |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 61 | 45 | 158 | 5 | 3 | 71 | 48 |
| vo-lc | 26 | 27 | 51 | 1 | 3 | 71 | 57 |
| vio | 56 | 27 | 156 | 4 | 24 | 68 | 21 |
| vio-lc | 13 | 18 | 20 | 1 | 34 | 122 | 15 |
| gnss-vio | 0 | 0 | 0 | 0 | 5 | 40 | 15 |

Protocol counts are separate from claim-status counts above. Success means a clean final export; native errors after saving remain failures with potentially usable accuracy.

| Mode | Verified attempts | Verified failures | Attempts | Evaluated | Clean exports | Observed failures | Unknown |
|---|---:|---:|---:|---:|---:|---:|---:|
| vo | 208 | 23 | 259 | 256 | 226 | 33 | 0 |
| vo-lc | 79 | 18 | 139 | 137 | 105 | 34 | 0 |
| vio | 187 | 13 | 232 | 232 | 213 | 19 | 0 |
| vio-lc | 39 | 1 | 88 | 86 | 86 | 2 | 0 |
| gnss-vio | 0 | 0 | 20 | 20 | 0 | 2 | 18 |

**OpenVINS cohort completeness:** each EuRoC sequence has historical N=1 plus patched N=2. The selected logical slots are consumed. One additional patched repetition per sequence would complete that implementation cohort, only if separately authorized. These three potential additions are separate from the 81 absent planned slots and are not scheduled here. Old cohorts are not resampled for success.


Future default actions: 513 reusable observations, 145 required reruns, 372 missing repetitions, 80 blocked. The separately authorized focused EuRoC campaign is complete; its 24 attempts yielded 23 final evaluations and one retained native refinement failure. The later ZED preparation used bounded diagnostics only; no ZED production repetitions or push occurred.

## Protocol-verified N=3 cells

| Cell | Accepted claim |
|---|---|
| `vo/rosariov2/sequence1/orbslam3` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence1/okvis2` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence1/okvis2x` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence1/airslam` | recorded_profile_rosario_sparse_keyframe_se3_metric_accuracy |
| `vo/rosariov2/sequence1/basalt` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence1/ov2slam` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence1/dpvo` | recorded_profile_rosario_final_trajectory_sim3_monocular_shape |
| `vo/rosariov2/sequence1/macvo` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence1/cuvslam` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence1/svo_pro` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence1/dsol` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence5/okvis2` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence5/okvis2x` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence5/airslam` | recorded_profile_rosario_sparse_keyframe_se3_metric_accuracy |
| `vo/rosariov2/sequence5/basalt` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence5/ov2slam` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence5/dpvo` | recorded_profile_rosario_final_trajectory_sim3_monocular_shape |
| `vo/rosariov2/sequence5/macvo` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence5/cuvslam` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence5/svo_pro` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo/rosariov2/sequence5/dsol` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
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
| `vo-lc/rosariov2/sequence1/okvis2` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo-lc/rosariov2/sequence1/airslam` | recorded_profile_rosario_sparse_keyframe_se3_metric_accuracy |
| `vo-lc/rosariov2/sequence1/ov2slam` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo-lc/rosariov2/sequence1/dpvo` | recorded_profile_rosario_final_trajectory_sim3_monocular_shape |
| `vo-lc/rosariov2/sequence5/okvis2` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo-lc/rosariov2/sequence5/okvis2x` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo-lc/rosariov2/sequence5/airslam` | recorded_profile_rosario_sparse_keyframe_se3_metric_accuracy |
| `vo-lc/rosariov2/sequence5/ov2slam` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vo-lc/rosariov2/sequence5/dpvo` | recorded_profile_rosario_final_trajectory_sim3_monocular_shape |
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
| `vio/rosariov2/sequence1/orbslam3` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence1/okvis2` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence1/okvis2x` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence1/airslam` | recorded_profile_rosario_sparse_keyframe_se3_metric_accuracy |
| `vio/rosariov2/sequence1/basalt` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence1/openvins` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence1/voxel_svio` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence1/cuvslam` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence1/svo_pro` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence1/mast3r_fusion` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence5/orbslam3` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence5/okvis2` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence5/okvis2x` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence5/airslam` | recorded_profile_rosario_sparse_keyframe_se3_metric_accuracy |
| `vio/rosariov2/sequence5/basalt` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence5/openvins` | None |
| `vio/rosariov2/sequence5/voxel_svio` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence5/cuvslam` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence5/svo_pro` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio/rosariov2/sequence5/mast3r_fusion` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
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
| `vio-lc/rosariov2/sequence1/okvis2` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio-lc/rosariov2/sequence1/okvis2x` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio-lc/rosariov2/sequence5/okvis2` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
| `vio-lc/rosariov2/sequence5/okvis2x` | recorded_profile_rosario_final_trajectory_se3_metric_accuracy |
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
| `results/vo/rosariov2/sequence1/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/okvis2/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/okvis2/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/okvis2/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/okvis2x/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/okvis2x/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/okvis2x/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/airslam/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/airslam/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/airslam/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/basalt/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/basalt/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/basalt/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/ov2slam/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/ov2slam/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/ov2slam/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/dpvo/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/dpvo/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/dpvo/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/macvo/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/macvo/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/macvo/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/dsol/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/dsol/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence1/dsol/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/orbslam3/run10004` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; export_coverage_below_95_percent_no_clean_success_tick; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/okvis2/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/okvis2/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/okvis2/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/okvis2x/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/okvis2x/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/okvis2x/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/airslam/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/airslam/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/airslam/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/basalt/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/basalt/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/basalt/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/ov2slam/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/ov2slam/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/ov2slam/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/dpvo/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/dpvo/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/dpvo/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/macvo/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/macvo/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/macvo/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/dsol/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/dsol/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo/rosariov2/sequence5/dsol/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; constant_velocity_motion_prior_without_gyroscope; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
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
| `results/vo-lc/rosariov2/sequence1/okvis2/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/okvis2/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/okvis2/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/airslam/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/airslam/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/airslam/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run2` | valid_observed_failure | collapse_under_recorded_reference_diagnostic_not_verified_physical_scale; fused_stereo_imu_ppk_reference_not_independent_ground_truth; no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim; retain_failure_in_attempt_denominator; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/ov2slam/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/dpvo/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/dpvo/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence1/dpvo/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/okvis2/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/okvis2/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/okvis2/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/okvis2x/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/okvis2x/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/okvis2x/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/airslam/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/airslam/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/airslam/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/ov2slam/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/ov2slam/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/ov2slam/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/dpvo/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/dpvo/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vo-lc/rosariov2/sequence5/dpvo/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
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
| `results/vio/rosariov2/sequence1/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/okvis2/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/okvis2/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/okvis2/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/okvis2x/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/okvis2x/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/okvis2x/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/airslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; sparse_keyframe_accuracy_only |
| `results/vio/rosariov2/sequence1/airslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; sparse_keyframe_accuracy_only |
| `results/vio/rosariov2/sequence1/airslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; sparse_keyframe_accuracy_only |
| `results/vio/rosariov2/sequence1/basalt/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/basalt/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/basalt/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/openvins/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/openvins/run10002` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/openvins/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/voxel_svio/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/voxel_svio/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/voxel_svio/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence1/mast3r_fusion/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/rosariov2/sequence1/mast3r_fusion/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/rosariov2/sequence1/mast3r_fusion/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/rosariov2/sequence5/orbslam3/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/orbslam3/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/orbslam3/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/okvis2/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/okvis2/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/okvis2/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/okvis2x/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/okvis2x/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/okvis2x/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/airslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; sparse_keyframe_accuracy_only |
| `results/vio/rosariov2/sequence5/airslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; sparse_keyframe_accuracy_only |
| `results/vio/rosariov2/sequence5/airslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; sparse_keyframe_accuracy_only |
| `results/vio/rosariov2/sequence5/basalt/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/basalt/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/basalt/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/openvins/run10001` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/openvins/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/openvins/run10003` | valid_observed_failure | configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/voxel_svio/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/voxel_svio/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/voxel_svio/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/cuvslam/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/cuvslam/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/cuvslam/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/svo_pro/run10002` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/svo_pro/run10003` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio/rosariov2/sequence5/mast3r_fusion/run10001` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/rosariov2/sequence5/mast3r_fusion/run10002` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/rosariov2/sequence5/mast3r_fusion/run10003` | accepted_with_limitation | configuration_choices_are_not_evidence_of_algorithm_optimality; fused_stereo_imu_ppk_reference_not_independent_ground_truth; recorded_native_assets_not_complete_transitive_build_reconstruction; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr; single_camera_with_imu_scale_from_imu_and_learned_depth |
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
| `results/vio/citrusfarm/seq04/okvis2/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq04/okvis2x/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq04/airslam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio/citrusfarm/seq04/basalt/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq04/voxel_svio/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq04/cuvslam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq04/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq04/mast3r_fusion/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio/citrusfarm/seq07/okvis2/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq07/okvis2x/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq07/airslam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; disclose_rig_specific_algorithm_parameters_in_saved_parameter_review; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; sparse_keyframe_accuracy_only |
| `results/vio/citrusfarm/seq07/basalt/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq07/voxel_svio/run10001` | valid_observed_failure | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; retain_failure_in_attempt_denominator; retain_observed_scale_collapse_in_attempt_denominator |
| `results/vio/citrusfarm/seq07/cuvslam/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq07/svo_pro/run10001` | accepted_with_limitation | authors_export_starts_after_keyframe_window_fills; citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction |
| `results/vio/citrusfarm/seq07/mast3r_fusion/run10001` | accepted_with_limitation | citrusfarm_position_only_reference_level_platform_lever_and_path_heading; citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured; configuration_choices_are_not_evidence_of_algorithm_optimality; no_rotation_or_full_relative_pose_accuracy_claim; recorded_native_assets_not_complete_transitive_build_reconstruction; single_camera_with_imu_scale_from_imu_and_learned_depth |
| `results/vio-lc/rosariov2/sequence1/okvis2/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence1/okvis2/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence1/okvis2/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence1/okvis2x/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence1/okvis2x/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence1/okvis2x/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence5/okvis2/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence5/okvis2/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence5/okvis2/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence5/okvis2x/run1` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence5/okvis2x/run2` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
| `results/vio-lc/rosariov2/sequence5/okvis2x/run3` | accepted_with_limitation | fused_stereo_imu_ppk_reference_not_independent_ground_truth; rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr |
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

There are 145 remaining distinct confirmed cases after the current cohort selection. Superseded affected AirSLAM attempts remain in their original directories and the historical-cohort CSV. Preserve every original attempt and use a new physical ID/cohort.

| Cell | Logical repetitions | Concrete defect |
|---|---|---|
| `vo/hortimulti/strawberry02/orbslam3` | r1 | historical_orb_library_identity_unverified |
| `vo/hortimulti/strawberry02/ov2slam` | r1, r2, r3 | ov2slam_horti_dataset_specific_parameters |
| `vo/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo/hortimulti/strawberry03/ov2slam` | r1, r2, r3 | ov2slam_horti_dataset_specific_parameters |
| `vo/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vo/citrusfarm/seq04/orbslam3` | r1 | orb_source_identity_changed_partial_cell |
| `vo/citrusfarm/seq07/orbslam3` | r1 | orb_source_identity_changed_partial_cell |
| `vo-lc/rosariov2/sequence1/orbslam3` | r1 | historical_orb_library_identity_unverified |
| `vo-lc/rosariov2/sequence5/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/hortimulti/strawberry02/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/hortimulti/strawberry02/ov2slam` | r1, r2, r3 | ov2slam_horti_dataset_specific_parameters |
| `vo-lc/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/hortimulti/strawberry03/ov2slam` | r1, r2, r3 | ov2slam_horti_dataset_specific_parameters |
| `vo-lc/euroc_mav/MH_01_easy/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/euroc_mav/MH_03_medium/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/euroc_mav/MH_05_difficult/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3` | r1, r2, r3 | camera_fps_changed_15_to_10 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/airslam` | r1, r2, r3 | airslam_zed_vo_lc_split_workspace_groups |
| `vio/hortimulti/strawberry02/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/okvis2` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/okvis2x` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/airslam` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry02/basalt` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;basalt_horti_undocumented_imu_noise |
| `vio/hortimulti/strawberry02/openvins` | r1 | horti_imu_profile_and_clock_inconsistent;openvins_track_frequency_dropped_frames |
| `vio/hortimulti/strawberry02/voxel_svio` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_voxel_initializer_camera_imu_offset_omitted |
| `vio/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/okvis2` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/okvis2x` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/airslam` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio/hortimulti/strawberry03/basalt` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;basalt_horti_undocumented_imu_noise |
| `vio/hortimulti/strawberry03/openvins` | r1 | horti_imu_profile_and_clock_inconsistent;openvins_track_frequency_dropped_frames |
| `vio/hortimulti/strawberry03/voxel_svio` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_voxel_initializer_camera_imu_offset_omitted |
| `vio/zed2i/field1_110426_full_10fps_q90/openvins` | r1, r2, r3 | openvins_track_frequency_dropped_frames |
| `vio/citrusfarm/seq04/orbslam3` | r1 | orb_source_identity_changed_partial_cell |
| `vio/citrusfarm/seq04/openvins` | r1 | openvins_track_frequency_dropped_frames |
| `vio/citrusfarm/seq07/orbslam3` | r1 | orb_source_identity_changed_partial_cell |
| `vio/citrusfarm/seq07/openvins` | r1 | openvins_track_frequency_dropped_frames |
| `vio-lc/rosariov2/sequence1/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/rosariov2/sequence1/airslam` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio-lc/rosariov2/sequence5/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified |
| `vio-lc/rosariov2/sequence5/airslam` | r1, r2, r3 | rosario_identity_camera_imu_extrinsic |
| `vio-lc/hortimulti/strawberry02/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;horti_imu_profile_and_clock_inconsistent;orb_horti_rectified_camera_imu_extrinsic;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/okvis2` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/okvis2x` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry02/airslam` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/orbslam3` | r1, r2, r3 | historical_orb_library_identity_unverified;horti_imu_profile_and_clock_inconsistent;orb_horti_rectified_camera_imu_extrinsic;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/okvis2` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/okvis2x` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
| `vio-lc/hortimulti/strawberry03/airslam` | r1, r2, r3 | horti_imu_profile_and_clock_inconsistent;horti_camera_imu_time_offset_uncompensated |
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
| `vo/hortimulti/strawberry02/orbslam3` | r2, r3 |
| `vo/hortimulti/strawberry02/cuvslam` | r1, r2, r3 |
| `vo/hortimulti/strawberry02/svo_pro` | r1, r2, r3 |
| `vo/hortimulti/strawberry02/dsol` | r1, r2, r3 |
| `vo/hortimulti/strawberry03/cuvslam` | r1, r2, r3 |
| `vo/hortimulti/strawberry03/svo_pro` | r1, r2, r3 |
| `vo/hortimulti/strawberry03/dsol` | r1, r2, r3 |
| `vo/zed2i/field1_110426_full_10fps_q90/cuvslam` | r2, r3 |
| `vo/zed2i/field1_110426_full_10fps_q90/svo_pro` | r2, r3 |
| `vo/zed2i/field1_110426_full_10fps_q90/dsol` | r1, r2, r3 |
| `vo/citrusfarm/seq04/orbslam3` | r2, r3 |
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
| `vo/citrusfarm/seq07/orbslam3` | r2, r3 |
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
| `vo-lc/hortimulti/strawberry02/cuvslam` | r1, r2, r3 |
| `vo-lc/hortimulti/strawberry03/cuvslam` | r1, r2, r3 |
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
| `vio/hortimulti/strawberry02/openvins` | r2, r3 |
| `vio/hortimulti/strawberry02/cuvslam` | r1, r2, r3 |
| `vio/hortimulti/strawberry02/svo_pro` | r1, r2, r3 |
| `vio/hortimulti/strawberry02/mast3r_fusion` | r1, r2, r3 |
| `vio/hortimulti/strawberry03/openvins` | r2, r3 |
| `vio/hortimulti/strawberry03/cuvslam` | r1, r2, r3 |
| `vio/hortimulti/strawberry03/svo_pro` | r1, r2, r3 |
| `vio/hortimulti/strawberry03/mast3r_fusion` | r1, r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/cuvslam` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/svo_pro` | r2, r3 |
| `vio/zed2i/field1_110426_full_10fps_q90/mast3r_fusion` | r2, r3 |
| `vio/citrusfarm/seq04/orbslam3` | r2, r3 |
| `vio/citrusfarm/seq04/okvis2` | r2, r3 |
| `vio/citrusfarm/seq04/okvis2x` | r2, r3 |
| `vio/citrusfarm/seq04/airslam` | r2, r3 |
| `vio/citrusfarm/seq04/basalt` | r2, r3 |
| `vio/citrusfarm/seq04/openvins` | r2, r3 |
| `vio/citrusfarm/seq04/voxel_svio` | r2, r3 |
| `vio/citrusfarm/seq04/cuvslam` | r2, r3 |
| `vio/citrusfarm/seq04/svo_pro` | r2, r3 |
| `vio/citrusfarm/seq04/mast3r_fusion` | r2, r3 |
| `vio/citrusfarm/seq07/orbslam3` | r2, r3 |
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
| `vio-lc/hortimulti/strawberry02/cuvslam` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry02/svo_pro` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry02/mast3r_fusion` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry03/cuvslam` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry03/svo_pro` | r1, r2, r3 |
| `vio-lc/hortimulti/strawberry03/mast3r_fusion` | r1, r2, r3 |
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
| historical_workspace_digest_differs_keep_cohorts_separate | 3 |
| horti_february_reference_generation_origin_and_timestamp_linkage_unresolved | 68 |
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
| `vio-lc/hortimulti/strawberry02/orbslam3` | deferred | unknown |
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

The timing subtotal is 19.2 serialized hours for 67 of the 517 required/missing actions; 450 have no comparable complete same-cell timing. It excludes native-error samples, diagnostics, unresolved blocked cases and evaluation/capture overhead. No total-campaign runtime is justified.

## Reproduction and preservation

Regenerate inventory, reconcile qualification, promote checked evaluations, then regenerate CSVs, TODO, reports and this handoff. Rosario evaluation uses the matched physical IMU-to-camera transform. The later ZED review uses the versioned nominal 3D position reference and recovered factory extrinsics; non-ZED numerical scores remain unchanged. Review decisions fail closed if pinned evidence changes. Run `build_future_manifest.py` after source/input/asset refresh; ordinary validation is read-only and is not readiness approval. The historical authorship mapping and all original provenance hashes remain intact. The obsolete temporary pause remains explicitly revoked.
