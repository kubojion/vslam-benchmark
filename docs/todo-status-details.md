# TODO status details

Generated presentation of the reviewed inventory; no acceptance decisions or scores are changed.
Inventory SHA-256: `1ebf1d964147ecfc2125b3aa2e1b5f60c5a6f32f2a4676ed7a592cbf5a493c19`. [Matrix legend](../TODO.md#run-combinations-matrix).
[Source inventory](../results/repair-20261001/inventory.json); [acceptance ledger](campaigns/paper-acceptance-20261001.json); [review definitions](protocol-review-20261002.md).

N counts completed verified attempts. Counts describe the selected physical runs, including
failures. Clean exports can still have limited coverage or accuracy. Reference/evaluation
review alone is not a confirmed rerun requirement. Exact blocker/limit identifiers below
are copied from the inventory and its acceptance ledger.

Cell-leading 🟥 marks a confirmed rerun; otherwise 🟨 marks unresolved review.
Rosario candidates are integrated into main; native readiness remains unverified.
See [integration and remaining prerequisites](rosario-main-integration-20261002.md).
Rerun items use 🔴 for not ready and 🔄 for verified ready; review items use 🟡.
✅ N=3 and 🟢 N=1/N=2 describe verified groups. Unverified or invalid history
uses recorded-attempt counts; it never receives a verified repetition label.

Common limits: accuracy is conditional on saved exports and reference support; no measured
processing-rate or real-time deadline claim is established. ZED uses the qualified nominal
position reference, retains RTK float, and discloses mounting and clock uncertainty.

## Future execution readiness

This is a snapshot of reviewed campaign evidence, not a live scheduler. Configuration
existence alone cannot establish readiness. Validation checks the manifest structure and
its pinned evidence. Later launch still requires current input/runtime checks and the
applicable authorization. ZED readiness covers bounded checks only. Cell symbols use
the coherent ZED replacement where present, otherwise the five-mode plan. Conflicting
or stale plans cannot establish readiness. Missing group-completion plans remain review
items; separately verified N=1 and N=2 never become one N=3.

### future-n3-five-modes

Manifest: [results/repair-20261001/future-n3-manifest.json](../results/repair-20261001/future-n3-manifest.json); SHA-256: `e3728647506ff3a70f8ef2f0264416c1084b7fbb85f1a22b3d774ff2f15a1b4a`.
Categories: `blocked=94`, `missing=372`, `required_rerun=122`, `reusable=522`.
Verified new-attempt readiness: **0**.

Evidence validation errors (readiness is unverified):

- stale or absent evidence: results/repair-20261001/inventory.json
- stale or absent evidence: configs/airslam/hortimulti_camera.yaml
- stale or absent evidence: configs/basalt/hortimulti_calib.json
- stale or absent evidence: configs/okvis2/hortimulti_strawberry02_vio.yaml
- stale or absent evidence: configs/okvis2/hortimulti_strawberry02_vio_lc.yaml
- stale or absent evidence: configs/okvis2/hortimulti_strawberry03_vio.yaml
- stale or absent evidence: configs/okvis2/hortimulti_strawberry03_vio_lc.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry02_gnss_vio.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry02_vio.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry02_vio_lc.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry03_gnss_vio.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry03_vio.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry03_vio_lc.yaml
- stale or absent evidence: configs/openvins/citrusfarm/estimator_config.yaml
- stale or absent evidence: configs/openvins/hortimulti/estimator_config.yaml
- stale or absent evidence: configs/openvins/hortimulti/kalibr_imu_chain.yaml
- stale or absent evidence: configs/openvins/zed2i/estimator_config.yaml
- stale or absent evidence: configs/orbslam3/hortimulti_stereo_inertial.yaml
- stale or absent evidence: configs/orbslam3/hortimulti_stereo_inertial_lc.yaml
- stale or absent evidence: configs/ov2slam/hortimulti_vo.yaml
- stale or absent evidence: configs/ov2slam/hortimulti_vo_lc.yaml
- stale or absent evidence: configs/sensors/hortimulti.json
- stale or absent evidence: configs/vins_fusion/hortimulti_strawberry02.yaml
- stale or absent evidence: configs/vins_fusion/hortimulti_strawberry03.yaml
- stale or absent evidence: configs/voxel_svio/hortimulti.yaml
- stale or absent evidence: scripts/campaign/build_repair_inventory.py
- stale or absent evidence: scripts/campaign/protocol_findings.py
- stale or absent evidence: scripts/campaign/tests/test_cohort_receipts.py
- stale or absent evidence: scripts/campaign/tests/test_new_algorithm_calibration.py
- stale or absent evidence: scripts/campaign/update_todo_matrices.py
- stale or absent evidence: scripts/run/openvins_data_player.py
- stale or absent evidence: scripts/run/run_openvins.sh
- stale or absent evidence: scripts/run/run_voxel_svio.sh
- stale or absent evidence: docs/campaigns/paper-acceptance-20261001.json

### zed-coherent-n3-20261002-main-integration

Manifest: [results/zed-preparation-20261002/campaign/manifest.json](../results/zed-preparation-20261002/campaign/manifest.json); SHA-256: `fc3d1bf27788162afb4fe7a10b53d308cfff48ef46c967b5d352381e0ead1be8`.
Categories: `cohort_completion=3`, `missing=36`, `required_rerun=13`, `reusable=53`.
Verified new-attempt readiness: **0**.

Evidence validation errors (readiness is unverified):

- stale or absent evidence: configs/airslam/hortimulti_camera.yaml
- stale or absent evidence: configs/basalt/hortimulti_calib.json
- stale or absent evidence: configs/okvis2/hortimulti_strawberry02_vio.yaml
- stale or absent evidence: configs/okvis2/hortimulti_strawberry02_vio_lc.yaml
- stale or absent evidence: configs/okvis2/hortimulti_strawberry03_vio.yaml
- stale or absent evidence: configs/okvis2/hortimulti_strawberry03_vio_lc.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry02_gnss_vio.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry02_vio.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry02_vio_lc.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry03_gnss_vio.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry03_vio.yaml
- stale or absent evidence: configs/okvis2x/hortimulti_strawberry03_vio_lc.yaml
- stale or absent evidence: configs/openvins/citrusfarm/estimator_config.yaml
- stale or absent evidence: configs/openvins/hortimulti/estimator_config.yaml
- stale or absent evidence: configs/openvins/hortimulti/kalibr_imu_chain.yaml
- stale or absent evidence: configs/openvins/zed2i/estimator_config.yaml
- stale or absent evidence: configs/orbslam3/hortimulti_stereo_inertial.yaml
- stale or absent evidence: configs/orbslam3/hortimulti_stereo_inertial_lc.yaml
- stale or absent evidence: configs/ov2slam/hortimulti_vo.yaml
- stale or absent evidence: configs/ov2slam/hortimulti_vo_lc.yaml
- stale or absent evidence: configs/sensors/hortimulti.json
- stale or absent evidence: configs/vins_fusion/hortimulti_strawberry02.yaml
- stale or absent evidence: configs/vins_fusion/hortimulti_strawberry03.yaml
- stale or absent evidence: configs/voxel_svio/hortimulti.yaml
- stale or absent evidence: scripts/campaign/build_repair_inventory.py
- stale or absent evidence: scripts/campaign/protocol_findings.py
- stale or absent evidence: scripts/campaign/tests/test_cohort_receipts.py
- stale or absent evidence: scripts/campaign/tests/test_new_algorithm_calibration.py
- stale or absent evidence: scripts/campaign/update_todo_matrices.py
- stale or absent evidence: scripts/run/openvins_data_player.py
- stale or absent evidence: scripts/run/run_openvins.sh
- stale or absent evidence: scripts/run/run_voxel_svio.sh
- stale or absent evidence: docs/campaigns/paper-acceptance-20261001.json

The coherent ZED selection replaces its part of the five-mode plan. Counts must not be added.

## Excluded history

MASt3R-SLAM, MegaSaM and DROID-SLAM remain excluded. The reported MASt3R/MegaSaM OOM
events concern the earlier 12 GB machine, not a measured OOM on the 24 GB server.
Their attempt/export/failure totals are not documented in this inventory: `A?/E?/S?/F?`.
Zero counts in the ZED exclusions mean no recorded attempt in this inventory.
DROID-SLAM counts below are historical observations; unrecorded exits stay unknown (U),
and historical N=3 does not become a verified tick.

- `results/vio/euroc_mav/MH_01_easy/airslam/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_01_easy/airslam/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_01_easy/airslam/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_01_easy/openvins/run1`: superseded_calibration_cohort; A1/E1/S0/F1; failure_with_saved_trajectory; exit 134; numerical status ok.
- `results/vio/euroc_mav/MH_01_easy/openvins/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_01_easy/openvins/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_01_easy/orbslam3/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_01_easy/orbslam3/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_01_easy/orbslam3/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_03_medium/airslam/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_03_medium/airslam/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_03_medium/airslam/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_03_medium/openvins/run1`: superseded_calibration_cohort; A1/E1/S0/F1; failure_with_saved_trajectory; exit 134; numerical status ok.
- `results/vio/euroc_mav/MH_03_medium/openvins/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_03_medium/openvins/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_03_medium/orbslam3/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_03_medium/orbslam3/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_03_medium/orbslam3/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_05_difficult/airslam/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_05_difficult/airslam/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_05_difficult/airslam/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_05_difficult/openvins/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_05_difficult/openvins/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_05_difficult/openvins/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_05_difficult/orbslam3/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_05_difficult/orbslam3/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/euroc_mav/MH_05_difficult/orbslam3/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/airslam/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/airslam/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/airslam/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/basalt/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/basalt/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/basalt/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/openvins/run1`: superseded_calibration_cohort; A1/E1/S0/F1; failure_scale_collapse; exit 134; numerical status scale_collapse.
- `results/vio/rosariov2/sequence1/orbslam3/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/orbslam3/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/orbslam3/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/voxel_svio/run1`: superseded_calibration_cohort; A1/E1/S0/F1; completed_export_shutdown_error; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/voxel_svio/run2`: superseded_calibration_cohort; A1/E1/S0/F1; completed_export_shutdown_error; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence1/voxel_svio/run3`: superseded_calibration_cohort; A1/E1/S0/F1; completed_export_shutdown_error; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/airslam/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/airslam/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/airslam/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/basalt/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/basalt/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/basalt/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/openvins/run1`: superseded_calibration_cohort; A1/E1/S0/F1; failure_scale_collapse; exit 134; numerical status scale_collapse.
- `results/vio/rosariov2/sequence5/orbslam3/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/orbslam3/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/orbslam3/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/voxel_svio/run1`: superseded_calibration_cohort; A1/E1/S0/F1; completed_export_shutdown_error; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/voxel_svio/run2`: superseded_calibration_cohort; A1/E1/S0/F1; completed_export_shutdown_error; exit 0; numerical status ok.
- `results/vio/rosariov2/sequence5/voxel_svio/run3`: superseded_calibration_cohort; A1/E1/S0/F1; completed_export_shutdown_error; exit 0; numerical status ok.
- `results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/zed2i/field1_110426_full_10fps_q90/basalt/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run1`: superseded_calibration_cohort; A1/E1/S0/F1; failure_scale_collapse; exit 0; numerical status scale_collapse.
- `results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run1`: superseded_calibration_cohort; A1/E0/S0/F1; failure_without_final_trajectory; exit 134; numerical status not evaluated.
- `results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run1`: superseded_calibration_cohort; A1/E1/S0/F1; completed_export_shutdown_error; exit 0; numerical status ok.
- `results/vio-lc/euroc_mav/MH_01_easy/airslam/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio-lc/euroc_mav/MH_01_easy/airslam/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio-lc/euroc_mav/MH_01_easy/airslam/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio-lc/euroc_mav/MH_03_medium/airslam/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio-lc/euroc_mav/MH_03_medium/airslam/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio-lc/euroc_mav/MH_03_medium/airslam/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vio-lc/euroc_mav/MH_05_difficult/airslam/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vo/euroc_mav/MH_01_easy/droidslam/run1`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/euroc_mav/MH_01_easy/orbslam3/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vo/euroc_mav/MH_01_easy/orbslam3/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vo/euroc_mav/MH_01_easy/orbslam3/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vo/euroc_mav/MH_03_medium/droidslam/run1`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/euroc_mav/MH_03_medium/orbslam3/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vo/euroc_mav/MH_03_medium/orbslam3/run2`: superseded_calibration_cohort; A1/E1/S0/F1; completed_export_shutdown_error; exit 139; numerical status ok.
- `results/vo/euroc_mav/MH_03_medium/orbslam3/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vo/euroc_mav/MH_05_difficult/droidslam/run1`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/euroc_mav/MH_05_difficult/orbslam3/run1`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vo/euroc_mav/MH_05_difficult/orbslam3/run2`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vo/euroc_mav/MH_05_difficult/orbslam3/run3`: superseded_calibration_cohort; A1/E1/S1/F0; success; exit 0; numerical status ok.
- `results/vo/hortimulti/strawberry02/droidslam/run1`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/hortimulti/strawberry02/droidslam/run2`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/hortimulti/strawberry02/droidslam/run3`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/hortimulti/strawberry03/droidslam/run1`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/hortimulti/strawberry03/droidslam/run2`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/hortimulti/strawberry03/droidslam/run3`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/rosariov2/sequence1/droidslam/run1`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/rosariov2/sequence1/droidslam/run2`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/rosariov2/sequence1/droidslam/run3`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/rosariov2/sequence1/orbslam3/run1`: superseded_calibration_cohort; A1/E0/S0/F1; failure_without_final_trajectory; exit 134; numerical status not evaluated.
- `results/vo/rosariov2/sequence5/droidslam/run1`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/rosariov2/sequence5/droidslam/run2`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/rosariov2/sequence5/droidslam/run3`: historical_excluded; A1/E1/S0/F0/U1; unknown; exit unknown; numerical status ok.
- `results/vo/rosariov2/sequence5/orbslam3/run1`: superseded_calibration_cohort; A1/E0/S0/F1; failure_without_final_trajectory; exit 139; numerical status not evaluated.

Superseded AirSLAM runs1–3 remain above; selected corrected runs4–6 are detailed below.
Displaced ZED run1 histories remain above; the three predeclared completed run10001 attempts
are selected into their original first logical slots below, with claim review still pending.
Neither a failure in a selected run nor a failure in the preserved cohort is discarded.

<a id="vo-rosariov2-sequence1-orbslam3"></a>
## vo/rosariov2/sequence1/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/rosariov2/sequence1/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/rosariov2/sequence1/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/rosariov2/sequence1/orbslam3/run10003) | verified | success | 0 | yes |

Group `b369efff51ed8168bcf238806772fa8557a27a499e0d7667eee76222086505c8`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `export_coverage_below_95_percent_no_clean_success_tick`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-okvis2"></a>
## vo/rosariov2/sequence1/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence1/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence1/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence1/okvis2/run3) | verified | success | 0 | yes |

Group `999ce37da98315e6088688c002f075151dce09e41d7daa922707993981c6a8c8`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-okvis2x"></a>
## vo/rosariov2/sequence1/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence1/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence1/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence1/okvis2x/run3) | verified | success | 0 | yes |

Group `6697bf269cb67bc7d6d23cbc0b8389ae5944a21dd1a6c11ac38bbca7e3c88d3c`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-airslam"></a>
## vo/rosariov2/sequence1/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence1/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence1/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence1/airslam/run3) | verified | success | 0 | yes |

Group `939eb2e99c47183475a257fd340f477b140ccc85c305632b3d0d673312572175`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-basalt"></a>
## vo/rosariov2/sequence1/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence1/basalt/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence1/basalt/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence1/basalt/run3) | verified | success | 0 | yes |

Group `9cc18a10ee8c86a12fce7db96dae830cbc611ed92b079e4bebc12777de107f18`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-ov2slam"></a>
## vo/rosariov2/sequence1/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence1/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence1/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence1/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `828b3abbc8235882c6f463448820d2002cc34e50358a4f28d30a7b39750571e8`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.
Native failure evidence r1: `{"line": 176, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 176, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 176, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-dpvo"></a>
## vo/rosariov2/sequence1/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence1/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence1/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence1/dpvo/run3) | verified | success | 0 | yes |

Group `c536a38361306e570d5d76f1359d77a81dfe4c660a1ee4d99aa619132063cac2`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-macvo"></a>
## vo/rosariov2/sequence1/macvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence1/macvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence1/macvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence1/macvo/run3) | verified | success | 0 | yes |

Group `b86aa8357eb1f3f4ffe0a7e26f1e1c6d3f0bff4c2ce0d50ef70c0939fc9f27f3`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-cuvslam"></a>
## vo/rosariov2/sequence1/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/rosariov2/sequence1/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/rosariov2/sequence1/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/rosariov2/sequence1/cuvslam/run10003) | verified | success | 0 | yes |

Group `68c21590e8b78a08855de030964151863ef0646237bc5da47caf2a43240ffda8`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-svo-pro"></a>
## vo/rosariov2/sequence1/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/rosariov2/sequence1/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/rosariov2/sequence1/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/rosariov2/sequence1/svo_pro/run10003) | verified | success | 0 | yes |

Group `d4439e0e2a6e506942c8b4cc9121ba3a1f90c82914425df87f2a6ca9c2ad5cad`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence1-dsol"></a>
## vo/rosariov2/sequence1/dsol

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/rosariov2/sequence1/dsol/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/rosariov2/sequence1/dsol/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/rosariov2/sequence1/dsol/run10003) | verified | success | 0 | yes |

Group `fa64feea676629d8d7a55a75c77015c8b6dac7bfd8abfebee17fd4b3ab488a76`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `constant_velocity_motion_prior_without_gyroscope`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-orbslam3"></a>
## vo/rosariov2/sequence5/orbslam3

**A3/E3/S3/F0**; verified completed groups: 1+2. Verified N=3: no.

Cell next-action display: 🟡 next: group review (not ready).
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10004](../results/vo/rosariov2/sequence5/orbslam3/run10004) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/rosariov2/sequence5/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/rosariov2/sequence5/orbslam3/run10003) | verified | success | 0 | yes |

Group `1052de2fef72f052ea66df14ad10363cc40640031b17006999f9a9ece329f0b0`: 1 verified / 1 recorded; `run10004`.
Group `b369efff51ed8168bcf238806772fa8557a27a499e0d7667eee76222086505c8`: 2 verified / 2 recorded; `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `export_coverage_below_95_percent_no_clean_success_tick`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-okvis2"></a>
## vo/rosariov2/sequence5/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence5/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence5/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence5/okvis2/run3) | verified | success | 0 | yes |

Group `2fbb25649ae8dc8342348ef014596e8fc8abd784057324b1b88e65cc95cdf092`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-okvis2x"></a>
## vo/rosariov2/sequence5/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence5/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence5/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence5/okvis2x/run3) | verified | success | 0 | yes |

Group `ff23099061b551b9aa99be52fe45e430558123f769b78de6fb20ecadbd770db8`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-airslam"></a>
## vo/rosariov2/sequence5/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence5/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence5/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence5/airslam/run3) | verified | success | 0 | yes |

Group `939eb2e99c47183475a257fd340f477b140ccc85c305632b3d0d673312572175`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-basalt"></a>
## vo/rosariov2/sequence5/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence5/basalt/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence5/basalt/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence5/basalt/run3) | verified | success | 0 | yes |

Group `9cc18a10ee8c86a12fce7db96dae830cbc611ed92b079e4bebc12777de107f18`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-ov2slam"></a>
## vo/rosariov2/sequence5/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence5/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence5/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence5/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `828b3abbc8235882c6f463448820d2002cc34e50358a4f28d30a7b39750571e8`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.
Native failure evidence r1: `{"line": 165, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 165, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 165, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-dpvo"></a>
## vo/rosariov2/sequence5/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence5/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence5/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence5/dpvo/run3) | verified | success | 0 | yes |

Group `c536a38361306e570d5d76f1359d77a81dfe4c660a1ee4d99aa619132063cac2`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-macvo"></a>
## vo/rosariov2/sequence5/macvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/rosariov2/sequence5/macvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/rosariov2/sequence5/macvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/rosariov2/sequence5/macvo/run3) | verified | success | 0 | yes |

Group `8f96a379d77446ea0c8eb49571f35cae9cffb7fd735759f80863f6789513bcaf`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-cuvslam"></a>
## vo/rosariov2/sequence5/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/rosariov2/sequence5/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/rosariov2/sequence5/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/rosariov2/sequence5/cuvslam/run10003) | verified | success | 0 | yes |

Group `9f1d6d731a83cac1264a8747944a3a1e123944ebc62dea6505a452e34429cfbc`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-svo-pro"></a>
## vo/rosariov2/sequence5/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/rosariov2/sequence5/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/rosariov2/sequence5/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/rosariov2/sequence5/svo_pro/run10003) | verified | success | 0 | yes |

Group `b57ccbbf8f2ad0d49de2400c32ae16b577b08792723c6200260bb05ac8421fce`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-rosariov2-sequence5-dsol"></a>
## vo/rosariov2/sequence5/dsol

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/rosariov2/sequence5/dsol/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/rosariov2/sequence5/dsol/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/rosariov2/sequence5/dsol/run10003) | verified | success | 0 | yes |

Group `f75d9657779cede382d5fa875cdc08c159f039927071fb68f85118106372f990`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `constant_velocity_motion_prior_without_gyroscope`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-hortimulti-strawberry02-orbslam3"></a>
## vo/hortimulti/strawberry02/orbslam3

**A1/E0/S0/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/orbslam3/run1) | blocked | failure_without_final_trajectory | 139 | no |
| 2 | [run2](../results/vo/hortimulti/strawberry02/orbslam3/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/vo/hortimulti/strawberry02/orbslam3/run3) | not_executed | not_attempted | unknown | no |

Group `a97d3710859ffa8efb12f7fa1f02db8a44b5291d70a351cbb1548eb69ebd65f7`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`, `horti_exact_reference_origin_timing_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim`, `no_measured_processing_rate_or_realtime_deadline_claim`, `retain_failure_in_attempt_denominator`.
Native failure evidence r1: `{"line": 57, "text": "2.191 Segmentation fault (core dumped)"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_with_recorded_compatible_orb_g2o_build_keeping_historical_attempts_separate`, `resolve_or_document_claim_limit:historical_orb_loaded_library_abi_unknown`, `resolve_or_document_claim_limit:missing_repetition`, `retain_nonzero_exit_and_review_saved_native_failure_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_non_zed_orb_eigen_abi_and_shutdown_native_build`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry02-okvis2"></a>
## vo/hortimulti/strawberry02/okvis2

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/okvis2/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry02/okvis2/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry02/okvis2/run3) | blocked | success | 0 | yes |

Group `0bbfdaa1673f7e61b754a24c9da25102c8379d66f9b01ab4dc94cc7e4885fcdc`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry02-okvis2x"></a>
## vo/hortimulti/strawberry02/okvis2x

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/okvis2x/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry02/okvis2x/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry02/okvis2x/run3) | blocked | success | 0 | yes |

Group `c3dbfad80e34e0e4ed0ae7ee68c07b331a39e5319eb582185d7043fafbfa23aa`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry02-airslam"></a>
## vo/hortimulti/strawberry02/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/airslam/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry02/airslam/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry02/airslam/run3) | blocked | success | 0 | yes |

Group `afa2b7613f95daa3bcfc8aa7f2ff598dc82d8c39e6aa396f5e651c599911f0cc`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `declare_sparse_keyframe_claim_or_validate_dense_export_before_dense_comparison`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry02-basalt"></a>
## vo/hortimulti/strawberry02/basalt

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/basalt/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry02/basalt/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry02/basalt/run3) | blocked | success | 0 | yes |

Group `342c84fda25fec145be0832a499a8b4ad5b363184d32849ef83dcbaae3ff51b0`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry02-ov2slam"></a>
## vo/hortimulti/strawberry02/ov2slam

**A3/E3/S0/F3**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/ov2slam/run1) | blocked | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry02/ov2slam/run2) | blocked | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry02/ov2slam/run3) | blocked | completed_export_shutdown_error | 0 | yes |

Group `596214197599c7ea1b9187d7ac157514ae110ed3a98d2eaed3a970271c8cfdec`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `ov2slam_horti_dataset_specific_parameters`.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 154, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 154, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 154, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `capture_native_exit_separately_and_diagnose_logged_shutdown_errors`, `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry02-dpvo"></a>
## vo/hortimulti/strawberry02/dpvo

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/dpvo/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry02/dpvo/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry02/dpvo/run3) | blocked | success | 0 | yes |

Group `7013cdd95b08627391b9b7da737e14542bd30a2c2e75a64d89e24f39c864a6b0`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry02-macvo"></a>
## vo/hortimulti/strawberry02/macvo

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/macvo/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry02/macvo/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry02/macvo/run3) | blocked | success | 0 | yes |

Group `450367dcfd4a1faf6966b579a7217b98fe6febc775978ae08316419e18082459`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry02-cuvslam"></a>
## vo/hortimulti/strawberry02/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo/hortimulti/strawberry02/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/hortimulti/strawberry02/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vo-hortimulti-strawberry02-svo-pro"></a>
## vo/hortimulti/strawberry02/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo/hortimulti/strawberry02/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/hortimulti/strawberry02/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `declare_window_gated_export_start`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vo-hortimulti-strawberry02-dsol"></a>
## vo/hortimulti/strawberry02/dsol

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry02/dsol/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo/hortimulti/strawberry02/dsol/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/hortimulti/strawberry02/dsol/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vo-hortimulti-strawberry03-orbslam3"></a>
## vo/hortimulti/strawberry03/orbslam3

**A3/E3/S2/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/orbslam3/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry03/orbslam3/run2) | blocked | completed_export_shutdown_error | 139 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry03/orbslam3/run3) | blocked | success | 0 | yes |

Group `2fb6c3448bac07def910b05d7e7d8a84d45deda6dcb6ad7b6bd1ab368a8280dc`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r2: `{"line": 66, "text": "256.102 Segmentation fault (core dumped)"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_with_recorded_compatible_orb_g2o_build_keeping_historical_attempts_separate`, `resolve_or_document_claim_limit:historical_orb_loaded_library_abi_unknown`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `retain_nonzero_exit_and_review_saved_native_failure_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_non_zed_orb_eigen_abi_and_shutdown_native_build`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry03-okvis2"></a>
## vo/hortimulti/strawberry03/okvis2

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/okvis2/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry03/okvis2/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry03/okvis2/run3) | blocked | success | 0 | yes |

Group `1618e3557d8c87fbf9914d54c2a9507f036e30b93d07e4c059c8cee653d26af1`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry03-okvis2x"></a>
## vo/hortimulti/strawberry03/okvis2x

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/okvis2x/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry03/okvis2x/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry03/okvis2x/run3) | blocked | success | 0 | yes |

Group `eac959e52e37e448131d85a397bcac246c6dced83a0e959838c61dc80211b33c`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry03-airslam"></a>
## vo/hortimulti/strawberry03/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/airslam/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry03/airslam/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry03/airslam/run3) | blocked | success | 0 | yes |

Group `afa2b7613f95daa3bcfc8aa7f2ff598dc82d8c39e6aa396f5e651c599911f0cc`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `declare_sparse_keyframe_claim_or_validate_dense_export_before_dense_comparison`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry03-basalt"></a>
## vo/hortimulti/strawberry03/basalt

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/basalt/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry03/basalt/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry03/basalt/run3) | blocked | success | 0 | yes |

Group `342c84fda25fec145be0832a499a8b4ad5b363184d32849ef83dcbaae3ff51b0`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry03-ov2slam"></a>
## vo/hortimulti/strawberry03/ov2slam

**A3/E3/S0/F3**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/ov2slam/run1) | blocked | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry03/ov2slam/run2) | blocked | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry03/ov2slam/run3) | blocked | completed_export_shutdown_error | 0 | yes |

Group `596214197599c7ea1b9187d7ac157514ae110ed3a98d2eaed3a970271c8cfdec`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `ov2slam_horti_dataset_specific_parameters`.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 119, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 119, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 119, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `capture_native_exit_separately_and_diagnose_logged_shutdown_errors`, `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry03-dpvo"></a>
## vo/hortimulti/strawberry03/dpvo

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/dpvo/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry03/dpvo/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry03/dpvo/run3) | blocked | success | 0 | yes |

Group `7013cdd95b08627391b9b7da737e14542bd30a2c2e75a64d89e24f39c864a6b0`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry03-macvo"></a>
## vo/hortimulti/strawberry03/macvo

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/macvo/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo/hortimulti/strawberry03/macvo/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo/hortimulti/strawberry03/macvo/run3) | blocked | success | 0 | yes |

Group `03c3ceaf989ea4a3d33eca1a48da0052dbd5af4a06740b87a7ff57035f953592`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-hortimulti-strawberry03-cuvslam"></a>
## vo/hortimulti/strawberry03/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo/hortimulti/strawberry03/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/hortimulti/strawberry03/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vo-hortimulti-strawberry03-svo-pro"></a>
## vo/hortimulti/strawberry03/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo/hortimulti/strawberry03/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/hortimulti/strawberry03/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `declare_window_gated_export_start`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vo-hortimulti-strawberry03-dsol"></a>
## vo/hortimulti/strawberry03/dsol

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/hortimulti/strawberry03/dsol/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo/hortimulti/strawberry03/dsol/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/hortimulti/strawberry03/dsol/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vo-euroc-mav-mh-01-easy-orbslam3"></a>
## vo/euroc_mav/MH_01_easy/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_01_easy/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_01_easy/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_01_easy/orbslam3/run10003) | verified | success | 0 | yes |

Group `713570b5d4726c6b3c415debc4cac6b39f010e6399f89fb8fe90fd3caf2259bc`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-okvis2"></a>
## vo/euroc_mav/MH_01_easy/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_01_easy/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_01_easy/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_01_easy/okvis2/run3) | verified | success | 0 | yes |

Group `228b733e2f141097c7509c36c0a59e981cc3cb05ce64b59a6ffe921d5b683df6`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-okvis2x"></a>
## vo/euroc_mav/MH_01_easy/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_01_easy/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_01_easy/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_01_easy/okvis2x/run3) | verified | success | 0 | yes |

Group `523eb612ca04a2ea8cd5e60a6ef6ed4d43674aa124d30a5c4025256fb24ea0cf`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-airslam"></a>
## vo/euroc_mav/MH_01_easy/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_01_easy/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_01_easy/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_01_easy/airslam/run3) | verified | success | 0 | yes |

Group `806f46dd5de192d35f935467713dd1a72fd8e0f60f95179354683ebc95a0e3b1`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-basalt"></a>
## vo/euroc_mav/MH_01_easy/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_01_easy/basalt/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_01_easy/basalt/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_01_easy/basalt/run3) | verified | success | 0 | yes |

Group `c19927b5adbd3b07d4bb000342a08b3ded8f2815e60da014cc7f13db28a1e90d`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-ov2slam"></a>
## vo/euroc_mav/MH_01_easy/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_01_easy/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_01_easy/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_01_easy/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `c711a8a07339c763bb1bba9026b207c1c1aa2c3b760014b4cffa2045c9b28ae4`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `native_shutdown_error_despite_wrapper_exit_zero`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 125, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 125, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 125, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-dpvo"></a>
## vo/euroc_mav/MH_01_easy/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_01_easy/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_01_easy/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_01_easy/dpvo/run3) | verified | success | 0 | yes |

Group `900b544e995a2352ce44b26189d52f4b42a12c75bc6bb7c51ef3776f1278c6e2`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-macvo"></a>
## vo/euroc_mav/MH_01_easy/macvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_01_easy/macvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_01_easy/macvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_01_easy/macvo/run3) | verified | success | 0 | yes |

Group `9694faa4aac39f0b3b3662b614512c155c5466159a96b6e05b5e6a3f3839a10f`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-cuvslam"></a>
## vo/euroc_mav/MH_01_easy/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_01_easy/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_01_easy/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_01_easy/cuvslam/run10003) | verified | success | 0 | yes |

Group `e80191e75c66a4cc49b52c023d59b241947b1993be9492729d78111e2cc4fa2b`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-svo-pro"></a>
## vo/euroc_mav/MH_01_easy/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_01_easy/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_01_easy/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_01_easy/svo_pro/run10003) | verified | success | 0 | yes |

Group `8237f36895272f15db40202c47464f358d14dbea16c237b572a70bedbc6d2578`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-01-easy-dsol"></a>
## vo/euroc_mav/MH_01_easy/dsol

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_01_easy/dsol/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_01_easy/dsol/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_01_easy/dsol/run10003) | verified | success | 0 | yes |

Group `252434c8bc8aa39ee982649ce6c32a5d22ddca89e9989a0965f6a312bbcff48f`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `constant_velocity_motion_prior_without_gyroscope`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-orbslam3"></a>
## vo/euroc_mav/MH_03_medium/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_03_medium/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_03_medium/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_03_medium/orbslam3/run10003) | verified | success | 0 | yes |

Group `713570b5d4726c6b3c415debc4cac6b39f010e6399f89fb8fe90fd3caf2259bc`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-okvis2"></a>
## vo/euroc_mav/MH_03_medium/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_03_medium/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_03_medium/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_03_medium/okvis2/run3) | verified | success | 0 | yes |

Group `0e44f795ff7e32c38e97f99b4f5e233b5cae1863b7481fdf5562dc930496f2f9`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-okvis2x"></a>
## vo/euroc_mav/MH_03_medium/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_03_medium/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_03_medium/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_03_medium/okvis2x/run3) | verified | success | 0 | yes |

Group `d861a5fdd3ea0c3352622b1e29e44cc9b7c85a5e1d48700ced9ae0da420e8510`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-airslam"></a>
## vo/euroc_mav/MH_03_medium/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_03_medium/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_03_medium/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_03_medium/airslam/run3) | verified | success | 0 | yes |

Group `806f46dd5de192d35f935467713dd1a72fd8e0f60f95179354683ebc95a0e3b1`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-basalt"></a>
## vo/euroc_mav/MH_03_medium/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_03_medium/basalt/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_03_medium/basalt/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_03_medium/basalt/run3) | verified | success | 0 | yes |

Group `c19927b5adbd3b07d4bb000342a08b3ded8f2815e60da014cc7f13db28a1e90d`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-ov2slam"></a>
## vo/euroc_mav/MH_03_medium/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_03_medium/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_03_medium/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_03_medium/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `c711a8a07339c763bb1bba9026b207c1c1aa2c3b760014b4cffa2045c9b28ae4`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `native_shutdown_error_despite_wrapper_exit_zero`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 120, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 120, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 120, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-dpvo"></a>
## vo/euroc_mav/MH_03_medium/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_03_medium/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_03_medium/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_03_medium/dpvo/run3) | verified | success | 0 | yes |

Group `900b544e995a2352ce44b26189d52f4b42a12c75bc6bb7c51ef3776f1278c6e2`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-macvo"></a>
## vo/euroc_mav/MH_03_medium/macvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_03_medium/macvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_03_medium/macvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_03_medium/macvo/run3) | verified | success | 0 | yes |

Group `cb05abd52ba18c03af2d8a499858e120914e54173a21c0cf70c323c5fc5391f3`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-cuvslam"></a>
## vo/euroc_mav/MH_03_medium/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_03_medium/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_03_medium/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_03_medium/cuvslam/run10003) | verified | success | 0 | yes |

Group `9ec5f3f66e13faeefe7dd4769b0e0ae3497b155d31dac29760aaff6aa1edeed7`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-svo-pro"></a>
## vo/euroc_mav/MH_03_medium/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_03_medium/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_03_medium/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_03_medium/svo_pro/run10003) | verified | success | 0 | yes |

Group `f7781b2324df5cef36ea603543a26fb12ce9d5138426d33579f7925aa7a56a82`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-03-medium-dsol"></a>
## vo/euroc_mav/MH_03_medium/dsol

**A3/E3/S2/F1**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_03_medium/dsol/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_03_medium/dsol/run10002) | verified | failure_scale_collapse | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_03_medium/dsol/run10003) | verified | success | 0 | yes |

Group `a928d9eaa5233f5894c0b584b7c435097996bba453e781060d73cd58363df169`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `constant_velocity_motion_prior_without_gyroscope`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `retain_failure_in_attempt_denominator`, `retain_observed_scale_collapse_in_attempt_denominator`.
Native failure evidence r10002: `"native exit 0; evaluated outcome scale_collapse"`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-orbslam3"></a>
## vo/euroc_mav/MH_05_difficult/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_05_difficult/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_05_difficult/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_05_difficult/orbslam3/run10003) | verified | success | 0 | yes |

Group `713570b5d4726c6b3c415debc4cac6b39f010e6399f89fb8fe90fd3caf2259bc`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-okvis2"></a>
## vo/euroc_mav/MH_05_difficult/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_05_difficult/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_05_difficult/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_05_difficult/okvis2/run3) | verified | success | 0 | yes |

Group `e3225b91609ea6e5f09e495aa8f7e7b3d2e7b1a025b388243ad5cdd74fa93b1a`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-okvis2x"></a>
## vo/euroc_mav/MH_05_difficult/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_05_difficult/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_05_difficult/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_05_difficult/okvis2x/run3) | verified | success | 0 | yes |

Group `ff6c4e40826e565ec4b2dd51d74b83a8d58e4c6ab5d49bff7a57f8e20b310391`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-airslam"></a>
## vo/euroc_mav/MH_05_difficult/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_05_difficult/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_05_difficult/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_05_difficult/airslam/run3) | verified | success | 0 | yes |

Group `806f46dd5de192d35f935467713dd1a72fd8e0f60f95179354683ebc95a0e3b1`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-basalt"></a>
## vo/euroc_mav/MH_05_difficult/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_05_difficult/basalt/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_05_difficult/basalt/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_05_difficult/basalt/run3) | verified | success | 0 | yes |

Group `c19927b5adbd3b07d4bb000342a08b3ded8f2815e60da014cc7f13db28a1e90d`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-ov2slam"></a>
## vo/euroc_mav/MH_05_difficult/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_05_difficult/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_05_difficult/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_05_difficult/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `c711a8a07339c763bb1bba9026b207c1c1aa2c3b760014b4cffa2045c9b28ae4`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `native_shutdown_error_despite_wrapper_exit_zero`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 118, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 118, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 118, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-dpvo"></a>
## vo/euroc_mav/MH_05_difficult/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_05_difficult/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_05_difficult/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_05_difficult/dpvo/run3) | verified | success | 0 | yes |

Group `900b544e995a2352ce44b26189d52f4b42a12c75bc6bb7c51ef3776f1278c6e2`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-macvo"></a>
## vo/euroc_mav/MH_05_difficult/macvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/euroc_mav/MH_05_difficult/macvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/euroc_mav/MH_05_difficult/macvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/euroc_mav/MH_05_difficult/macvo/run3) | verified | success | 0 | yes |

Group `2085d4709aa64b9a18c2825c12cc5bad6e079c2467f2305d211357f7ecdb85be`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-cuvslam"></a>
## vo/euroc_mav/MH_05_difficult/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_05_difficult/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_05_difficult/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_05_difficult/cuvslam/run10003) | verified | success | 0 | yes |

Group `2dcd85c3b186eb43661fe0ff61b63d6451968d4bc8ed0350ef190c439194875c`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-svo-pro"></a>
## vo/euroc_mav/MH_05_difficult/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_05_difficult/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_05_difficult/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_05_difficult/svo_pro/run10003) | verified | success | 0 | yes |

Group `79f6e8302f654cce50463a2711b744c4370514036bd9cd5a5bb088c6487915da`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-euroc-mav-mh-05-difficult-dsol"></a>
## vo/euroc_mav/MH_05_difficult/dsol

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/euroc_mav/MH_05_difficult/dsol/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vo/euroc_mav/MH_05_difficult/dsol/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vo/euroc_mav/MH_05_difficult/dsol/run10003) | verified | success | 0 | yes |

Group `5e2d058ea0d213823e1e3cbbbe4899e1e3d8dc0f8f5fff272dec759debbdcc70`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `constant_velocity_motion_prior_without_gyroscope`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-orbslam3"></a>
## vo/zed2i/field1_110426_full_10fps_q90/orbslam3

**A3/E3/S1/F2**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run1) | invalid_setup | completed_export_shutdown_error | 139 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run2) | invalid_setup | completed_export_shutdown_error | 139 | yes |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/orbslam3/run3) | invalid_setup | success | 0 | yes |

Group `b5d255e908662a81d1800e4f74481dfdc2540b8b21f30141916e226cc5f6735a`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `camera_fps_changed_15_to_10`.
Review blockers: `camera_fps_changed_15_to_10`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.
Native failure evidence r1: `{"line": 66, "text": "5647.331 Segmentation fault (core dumped)"}`.
Native failure evidence r2: `{"line": 66, "text": "5752.268 Segmentation fault (core dumped)"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-okvis2"></a>
## vo/zed2i/field1_110426_full_10fps_q90/okvis2

**A3/E3/S2/F1**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run2) | verified | failure_scale_collapse | 0 | yes |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/okvis2/run3) | verified | success | 0 | yes |

Group `553085faf41e2027f0e1654c23e5229860b7a14c3b54f1ed2cbc1d93a4244d6e`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `retain_failure_in_attempt_denominator`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-okvis2x"></a>
## vo/zed2i/field1_110426_full_10fps_q90/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/zed2i/field1_110426_full_10fps_q90/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/okvis2x/run3) | verified | success | 0 | yes |

Group `e35849633f0deebaf9403f2f15443b61b15c881002b0d69c5d92dd1432c6c19b`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-airslam"></a>
## vo/zed2i/field1_110426_full_10fps_q90/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/zed2i/field1_110426_full_10fps_q90/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/airslam/run3) | verified | success | 0 | yes |

Group `0eb34700132fededea0c165fba13c8c8492fc027d4e15a129b254cded45b82af`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `native_sparse_keyframe_accuracy_not_dense_tracking`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-basalt"></a>
## vo/zed2i/field1_110426_full_10fps_q90/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/zed2i/field1_110426_full_10fps_q90/basalt/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/basalt/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/basalt/run3) | verified | success | 0 | yes |

Group `6ae59b2062ac01b855ea3713ca6d3b5b96c045993a2ccdcab63668c79f44ee6f`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-ov2slam"></a>
## vo/zed2i/field1_110426_full_10fps_q90/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `052d85309cf2df535687b2fc6b101901ffe72244d7de9529dc27ed0e8ebc5c5d`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `native_shutdown_error_despite_wrapper_exit_zero_retain_failure_count`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.
Native failure evidence r1: `{"line": 338, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 338, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 338, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-dpvo"></a>
## vo/zed2i/field1_110426_full_10fps_q90/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/zed2i/field1_110426_full_10fps_q90/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/dpvo/run3) | verified | success | 0 | yes |

Group `f970f0e10e115385c0fa47b5247cb2c7d2b50244a33e1730cec759c656456d39`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-macvo"></a>
## vo/zed2i/field1_110426_full_10fps_q90/macvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/zed2i/field1_110426_full_10fps_q90/macvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/macvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/macvo/run3) | verified | success | 0 | yes |

Group `d238443431c551c07629a6397b58ca51cf56992f17491f85f1c831c5b5db2b4c`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `official_performant_profile_not_paper_reproduction_profile`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-cuvslam"></a>
## vo/zed2i/field1_110426_full_10fps_q90/cuvslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/zed2i/field1_110426_full_10fps_q90/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/cuvslam/run3) | blocked | not_attempted | unknown | no |

Group `a1999cda6287779e0479d93b4e172ca4f40f896fe6dd8b71cb3543f339a6ceb5`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-svo-pro"></a>
## vo/zed2i/field1_110426_full_10fps_q90/svo_pro

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/zed2i/field1_110426_full_10fps_q90/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/svo_pro/run3) | blocked | not_attempted | unknown | no |

Group `a540702150c24554590e583e150bcce90e32091b52c2522fa53f73db27e53588`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-zed2i-field1-110426-full-10fps-q90-dsol"></a>
## vo/zed2i/field1_110426_full_10fps_q90/dsol

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo/zed2i/field1_110426_full_10fps_q90/dsol/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo/zed2i/field1_110426_full_10fps_q90/dsol/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/zed2i/field1_110426_full_10fps_q90/dsol/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-orbslam3"></a>
## vo/citrusfarm/seq04/orbslam3

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/orbslam3/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/orbslam3/run3) | blocked | not_attempted | unknown | no |

Group `c44e576345b90e9c1a9aafd3b6c47f8d100054c483cb6722be36e4fd8875bc85`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-okvis2"></a>
## vo/citrusfarm/seq04/okvis2

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/okvis2/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/okvis2/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/okvis2/run3) | blocked | not_attempted | unknown | no |

Group `8cc6891501ede6329968c989c52c415e7ff84c042af84c059cbcccdd40155645`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-okvis2x"></a>
## vo/citrusfarm/seq04/okvis2x

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/okvis2x/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/okvis2x/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/okvis2x/run3) | blocked | not_attempted | unknown | no |

Group `f912e30514c59cbb9568099f6cbb4f41eed6afdc2b4f5f6a69e40262bea212a4`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-airslam"></a>
## vo/citrusfarm/seq04/airslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/airslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/airslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/airslam/run3) | blocked | not_attempted | unknown | no |

Group `4500cdcb07151eeaa49afecab65ac159e3f0f50227cb0e18b07e63fa1e66e4cb`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-basalt"></a>
## vo/citrusfarm/seq04/basalt

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/basalt/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/basalt/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/basalt/run3) | blocked | not_attempted | unknown | no |

Group `03114bdbfecda1bd0c26ad62d9cbf02427235e3a5f7bf3135d13c473085596f0`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-ov2slam"></a>
## vo/citrusfarm/seq04/ov2slam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/ov2slam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/ov2slam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/ov2slam/run3) | blocked | not_attempted | unknown | no |

Group `ab6ce07992c716826c26ddbe7a12795a805f79ca439b272b6a8cbbfd9128ea36`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-dpvo"></a>
## vo/citrusfarm/seq04/dpvo

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/dpvo/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/dpvo/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/dpvo/run3) | blocked | not_attempted | unknown | no |

Group `cff54306824f5c0b6cec024cf23c0439f3b7beb12a96bf6c31d91f6c61bb43e3`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `monocular_sim3_shape_only_not_metric_stereo_ranking`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-macvo"></a>
## vo/citrusfarm/seq04/macvo

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/macvo/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/macvo/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/macvo/run3) | blocked | not_attempted | unknown | no |

Group `d5761135880a2dbed1657c33bd827d4ebea0bee23354635ca6f0b11e8c68d98f`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `official_performant_profile_not_paper_reproduction_profile`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-cuvslam"></a>
## vo/citrusfarm/seq04/cuvslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/cuvslam/run3) | blocked | not_attempted | unknown | no |

Group `a15d63d66a7cd4919ec60d79d5836ded4981132e2aa2ffe490d9ab0cb99a77bb`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-svo-pro"></a>
## vo/citrusfarm/seq04/svo_pro

**A1/E1/S0/F1**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/svo_pro/run10001) | verified | failure_scale_collapse | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq04/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/svo_pro/run3) | blocked | not_attempted | unknown | no |

Group `66b7b899b5293f3ce8021204e7c91e71e4f7b01acd16718f042bd68d10359173`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `retain_failure_in_attempt_denominator`, `retain_observed_scale_collapse_in_attempt_denominator`.
Native failure evidence r10001: `"native exit 0; evaluated outcome scale_collapse"`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq04-dsol"></a>
## vo/citrusfarm/seq04/dsol

**A1/E0/S0/F1**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq04/dsol/run10001) | verified | failure_without_final_trajectory | 134 | no |
| 2 | [run2](../results/vo/citrusfarm/seq04/dsol/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq04/dsol/run3) | blocked | not_attempted | unknown | no |

Group `e57fb2cf61a4957ed48200f5dfbb348163605a3eaa648241f1d9f00d2e08151e`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `constant_velocity_motion_prior_without_gyroscope`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `retain_failure_in_attempt_denominator`.
Native failure evidence r10001: `"native exit 134, no trajectory: DSOL aborts on its own assertion (align.cpp:307) after losing the scene at motion onset; docs/campaigns/readiness-review-20261004.json"`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-orbslam3"></a>
## vo/citrusfarm/seq07/orbslam3

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/orbslam3/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/orbslam3/run3) | blocked | not_attempted | unknown | no |

Group `c44e576345b90e9c1a9aafd3b6c47f8d100054c483cb6722be36e4fd8875bc85`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-okvis2"></a>
## vo/citrusfarm/seq07/okvis2

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/okvis2/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/okvis2/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/okvis2/run3) | blocked | not_attempted | unknown | no |

Group `eee4f240103c746e8e8911475254eb403543f3586d060716c18e9a4633566712`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-okvis2x"></a>
## vo/citrusfarm/seq07/okvis2x

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/okvis2x/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/okvis2x/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/okvis2x/run3) | blocked | not_attempted | unknown | no |

Group `06d78538f167666cb7efdf1a337f13a22bf721ec427702a5baf4e9f3a8a8d5c5`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-airslam"></a>
## vo/citrusfarm/seq07/airslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/airslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/airslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/airslam/run3) | blocked | not_attempted | unknown | no |

Group `4500cdcb07151eeaa49afecab65ac159e3f0f50227cb0e18b07e63fa1e66e4cb`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-basalt"></a>
## vo/citrusfarm/seq07/basalt

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/basalt/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/basalt/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/basalt/run3) | blocked | not_attempted | unknown | no |

Group `03114bdbfecda1bd0c26ad62d9cbf02427235e3a5f7bf3135d13c473085596f0`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-ov2slam"></a>
## vo/citrusfarm/seq07/ov2slam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/ov2slam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/ov2slam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/ov2slam/run3) | blocked | not_attempted | unknown | no |

Group `ab6ce07992c716826c26ddbe7a12795a805f79ca439b272b6a8cbbfd9128ea36`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-dpvo"></a>
## vo/citrusfarm/seq07/dpvo

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10002](../results/vo/citrusfarm/seq07/dpvo/run10002) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/dpvo/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/dpvo/run3) | blocked | not_attempted | unknown | no |

Group `5c5751e8758ff7bfaecd8e149ef3f92ec5b0be7e50df25dd341b43aee7e89246`: 1 verified / 1 recorded; `run10002`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `monocular_sim3_shape_only_not_metric_stereo_ranking`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-macvo"></a>
## vo/citrusfarm/seq07/macvo

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/macvo/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/macvo/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/macvo/run3) | blocked | not_attempted | unknown | no |

Group `0caf9471922f09f5f7480cf33349a7b968bb4043d7290d4141650dd6d6b08848`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `official_performant_profile_not_paper_reproduction_profile`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-cuvslam"></a>
## vo/citrusfarm/seq07/cuvslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/cuvslam/run3) | blocked | not_attempted | unknown | no |

Group `741e0f206d2ef905fcccc959c788b348c9e22be76172a319c6bef4ee2f1f579a`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-svo-pro"></a>
## vo/citrusfarm/seq07/svo_pro

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vo/citrusfarm/seq07/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/svo_pro/run3) | blocked | not_attempted | unknown | no |

Group `81774431e6e78770392db91f9506d3ffaa70f3dca48cc40d9f43068a754ed0c2`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-citrusfarm-seq07-dsol"></a>
## vo/citrusfarm/seq07/dsol

**A1/E0/S0/F1**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vo/citrusfarm/seq07/dsol/run10001) | verified | failure_without_final_trajectory | 134 | no |
| 2 | [run2](../results/vo/citrusfarm/seq07/dsol/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo/citrusfarm/seq07/dsol/run3) | blocked | not_attempted | unknown | no |

Group `06e6bd0839d8510fa3fe39e1e91c0ab521cf048e0a390c92892ac3139c84f058`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `constant_velocity_motion_prior_without_gyroscope`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `retain_failure_in_attempt_denominator`.
Native failure evidence r10001: `"native exit 134, no trajectory: DSOL aborts on its own assertion (align.cpp:307) after losing the scene at motion onset; docs/campaigns/readiness-review-20261004.json"`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence1-orbslam3"></a>
## vo-lc/rosariov2/sequence1/orbslam3

**A1/E0/S0/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence1/orbslam3/run1) | blocked | failure_without_final_trajectory | 134 | no |
| 2 | [run2](../results/vo-lc/rosariov2/sequence1/orbslam3/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/rosariov2/sequence1/orbslam3/run3) | not_executed | not_attempted | unknown | no |

Group `f2d011ccb14b9114f9015f1076ffb6b442dc4caf04f0d88dd3cef392acfb049f`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `historical_orb_loaded_library_abi_unknown`, `no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim`, `no_measured_processing_rate_or_realtime_deadline_claim`, `retain_failure_in_attempt_denominator`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.
Native failure evidence r1: `{"line": 56, "text": "2.145 terminate called after throwing an instance of 'std::bad_alloc'"}`, `{"line": 57, "text": "2.145   what():  std::bad_alloc"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence1-okvis2"></a>
## vo-lc/rosariov2/sequence1/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence1/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence1/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence1/okvis2/run3) | verified | success | 0 | yes |

Group `994e020624eea676eac47556679e8e537128e2201dc2ae341441509df8d4f2f9`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence1-okvis2x"></a>
## vo-lc/rosariov2/sequence1/okvis2x

**A3/E3/S3/F0**; verified completed groups: 0+0. Verified N=3: no.

Cell next-action display: 🟡 next: group review (not ready).
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence1/okvis2x/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence1/okvis2x/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence1/okvis2x/run3) | blocked | success | 0 | yes |

Group `14b263872f323f0bb6d0a64b0bdf3ca65669394b8c5b4e0484b045df5d5df3f7`: 0 verified / 2 recorded; `run1`, `run2`.
Group `a48281653d63a5be844549d31a19ad516c7fc502fecca34db8a36be0f97b4ffe`: 0 verified / 1 recorded; `run3`.

Confirmed setup findings: none.
Review blockers: `historical_workspace_digest_differs_keep_cohorts_separate`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `resolve_or_document_claim_limit:historical_workspace_digest_differs_keep_cohorts_separate`, `resolve_recorded_source_binary_parameter_or_hardware_cohort_difference`, `saved_result_has_unresolved_scientific_evidence`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-rosariov2-sequence1-airslam"></a>
## vo-lc/rosariov2/sequence1/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence1/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence1/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence1/airslam/run3) | verified | success | 0 | yes |

Group `8cbc15694c397198555006ecda4ea5489cb050bb451b6e7aebc4ae78952a7daf`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence1-ov2slam"></a>
## vo-lc/rosariov2/sequence1/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence1/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence1/ov2slam/run2) | verified | failure_scale_collapse | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence1/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `2110daa8b7da8fe88e07c76625f5b58b8017bdbc4e96b7c2051725ebfa8adccc`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `collapse_under_recorded_reference_diagnostic_not_verified_physical_scale`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_calibrated_agricultural_accuracy_or_intrinsic_algorithm_failure_claim`, `no_measured_processing_rate_or_realtime_deadline_claim`, `retain_failure_in_attempt_denominator`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.
Native failure evidence r1: `{"line": 270, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 222, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 269, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence1-dpvo"></a>
## vo-lc/rosariov2/sequence1/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence1/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence1/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence1/dpvo/run3) | verified | success | 0 | yes |

Group `fadfb913bb7703c4079c9ced67f393fd60fbfbc586dd77b10559d61fda69466a`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence1-cuvslam"></a>
## vo-lc/rosariov2/sequence1/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence1/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/rosariov2/sequence1/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/rosariov2/sequence1/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence5-orbslam3"></a>
## vo-lc/rosariov2/sequence5/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence5/orbslam3/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence5/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence5/orbslam3/run3) | blocked | success | 0 | yes |

Group `7b48dc57080e7b413b83255fbe1e87cc96e7be04cf9ed0703060daa7ecaa4e98`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence5-okvis2"></a>
## vo-lc/rosariov2/sequence5/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence5/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence5/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence5/okvis2/run3) | verified | success | 0 | yes |

Group `628296a62fcf8a793c27126c7198f4da99c1243cd1b18e1897bedf36e2b31bca`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence5-okvis2x"></a>
## vo-lc/rosariov2/sequence5/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence5/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence5/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence5/okvis2x/run3) | verified | success | 0 | yes |

Group `0781bb16e8c7f960f3e2aa159279e29b682e90de1e5a1d215f94b1bd16044a36`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence5-airslam"></a>
## vo-lc/rosariov2/sequence5/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence5/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence5/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence5/airslam/run3) | verified | success | 0 | yes |

Group `98528bef439a08e5f73346f91a7fcebec14a6f4ea67d6298e4761926c82c597d`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence5-ov2slam"></a>
## vo-lc/rosariov2/sequence5/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence5/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence5/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence5/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `4a1fed12c4f45e9f4b238a2b1d290fdb9ee857e538449dd86088f321aef150d3`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.
Native failure evidence r1: `{"line": 181, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 184, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 181, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence5-dpvo"></a>
## vo-lc/rosariov2/sequence5/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence5/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/rosariov2/sequence5/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/rosariov2/sequence5/dpvo/run3) | verified | success | 0 | yes |

Group `d2489bc0b7fa355f2929a7ab8b2614839cc7a21aa04b79f815c99c4b2da15413`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-rosariov2-sequence5-cuvslam"></a>
## vo-lc/rosariov2/sequence5/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/rosariov2/sequence5/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/rosariov2/sequence5/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/rosariov2/sequence5/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-hortimulti-strawberry02-orbslam3"></a>
## vo-lc/hortimulti/strawberry02/orbslam3

**A3/E3/S1/F2**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry02/orbslam3/run1) | blocked | failure_with_saved_trajectory | 134 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry02/orbslam3/run2) | blocked | failure_with_saved_trajectory | 139 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry02/orbslam3/run3) | blocked | success | 0 | yes |

Group `5d8b80a466bca1529910dd70011ba6705013ffc80cdb845e6b60dabd5793bf02`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r2: `{"line": 104, "text": "1031.979 Segmentation fault (core dumped)"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_with_recorded_compatible_orb_g2o_build_keeping_historical_attempts_separate`, `resolve_or_document_claim_limit:historical_orb_loaded_library_abi_unknown`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `retain_nonzero_exit_and_review_saved_native_failure_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_non_zed_orb_eigen_abi_and_shutdown_native_build`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry02-okvis2"></a>
## vo-lc/hortimulti/strawberry02/okvis2

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry02/okvis2/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry02/okvis2/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry02/okvis2/run3) | blocked | success | 0 | yes |

Group `0a64b3993335ee0e4b615b33cf1913fa7b99cbc0ef6aeabb0ac83563b6a4c16a`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry02-okvis2x"></a>
## vo-lc/hortimulti/strawberry02/okvis2x

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry02/okvis2x/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry02/okvis2x/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry02/okvis2x/run3) | blocked | success | 0 | yes |

Group `e2956f06790731aff966c78544486a36e5427d50223efe317affba7b86d0853d`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry02-airslam"></a>
## vo-lc/hortimulti/strawberry02/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry02/airslam/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry02/airslam/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry02/airslam/run3) | blocked | success | 0 | yes |

Group `67662cd8cc5aec617b7736a4883f56eaf24200675b14b22078a1a6a90e3ab487`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `declare_sparse_keyframe_claim_or_validate_dense_export_before_dense_comparison`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry02-ov2slam"></a>
## vo-lc/hortimulti/strawberry02/ov2slam

**A3/E3/S0/F3**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry02/ov2slam/run1) | blocked | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry02/ov2slam/run2) | blocked | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry02/ov2slam/run3) | blocked | completed_export_shutdown_error | 0 | yes |

Group `3d44ca34443fb94597e3c8a34ab10f186c2aa2eb9bdf8c66d9cb4f78d938387d`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `ov2slam_horti_dataset_specific_parameters`.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 158, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 158, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 158, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `capture_native_exit_separately_and_diagnose_logged_shutdown_errors`, `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry02-dpvo"></a>
## vo-lc/hortimulti/strawberry02/dpvo

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry02/dpvo/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry02/dpvo/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry02/dpvo/run3) | blocked | success | 0 | yes |

Group `4637225210a4ea381f49448ab590e0b2abd1bf0aeba05dfb620e4b6d58071903`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry02-cuvslam"></a>
## vo-lc/hortimulti/strawberry02/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry02/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry02/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry02/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vo-lc-hortimulti-strawberry03-orbslam3"></a>
## vo-lc/hortimulti/strawberry03/orbslam3

**A3/E3/S2/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry03/orbslam3/run1) | blocked | completed_export_shutdown_error | 139 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry03/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry03/orbslam3/run3) | blocked | success | 0 | yes |

Group `baaa5530dc964aabb6dd8c8ec731b1a58a2e5a62763558e734fbd2b53f012a74`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 71, "text": "272.755 Segmentation fault (core dumped)"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_with_recorded_compatible_orb_g2o_build_keeping_historical_attempts_separate`, `resolve_or_document_claim_limit:historical_orb_loaded_library_abi_unknown`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `retain_nonzero_exit_and_review_saved_native_failure_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_non_zed_orb_eigen_abi_and_shutdown_native_build`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry03-okvis2"></a>
## vo-lc/hortimulti/strawberry03/okvis2

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry03/okvis2/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry03/okvis2/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry03/okvis2/run3) | blocked | success | 0 | yes |

Group `b9511f099206d1a57a1abcccd9e37dd9f637dfdd3a1d4cf9a46c773e5bda3020`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry03-okvis2x"></a>
## vo-lc/hortimulti/strawberry03/okvis2x

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry03/okvis2x/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry03/okvis2x/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry03/okvis2x/run3) | blocked | success | 0 | yes |

Group `58b8bacb5f6445f6afb6b31b32e725057802f7819515486fc037deae8f1e5391`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry03-airslam"></a>
## vo-lc/hortimulti/strawberry03/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry03/airslam/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry03/airslam/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry03/airslam/run3) | blocked | success | 0 | yes |

Group `67662cd8cc5aec617b7736a4883f56eaf24200675b14b22078a1a6a90e3ab487`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `declare_sparse_keyframe_claim_or_validate_dense_export_before_dense_comparison`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry03-ov2slam"></a>
## vo-lc/hortimulti/strawberry03/ov2slam

**A3/E3/S0/F3**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry03/ov2slam/run1) | blocked | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry03/ov2slam/run2) | blocked | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry03/ov2slam/run3) | blocked | completed_export_shutdown_error | 0 | yes |

Group `3d44ca34443fb94597e3c8a34ab10f186c2aa2eb9bdf8c66d9cb4f78d938387d`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `ov2slam_horti_dataset_specific_parameters`.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 192, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 187, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 195, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `capture_native_exit_separately_and_diagnose_logged_shutdown_errors`, `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry03-dpvo"></a>
## vo-lc/hortimulti/strawberry03/dpvo

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry03/dpvo/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry03/dpvo/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry03/dpvo/run3) | blocked | success | 0 | yes |

Group `4637225210a4ea381f49448ab590e0b2abd1bf0aeba05dfb620e4b6d58071903`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 blocked; readiness unverified; r3 blocked; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vo-lc-hortimulti-strawberry03-cuvslam"></a>
## vo-lc/hortimulti/strawberry03/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/hortimulti/strawberry03/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/hortimulti/strawberry03/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/hortimulti/strawberry03/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vo-lc-euroc-mav-mh-01-easy-orbslam3"></a>
## vo-lc/euroc_mav/MH_01_easy/orbslam3

**A3/E3/S2/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_01_easy/orbslam3/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_01_easy/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_01_easy/orbslam3/run3) | blocked | completed_export_shutdown_error | 139 | yes |

Group `2fb7a8a1ab2b92230c69f9c42e7da5e311ac3f0079a814fb8405dc8a66d38cd1`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`, `saved_accuracy_with_recorded_nonzero_exit_no_clean_success`.
Native failure evidence r3: `{"line": 71, "text": "201.536 Segmentation fault (core dumped)"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-01-easy-okvis2"></a>
## vo-lc/euroc_mav/MH_01_easy/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_01_easy/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_01_easy/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_01_easy/okvis2/run3) | verified | success | 0 | yes |

Group `ad1df09e192d2bb622379ab8b7375a688e766e684fe4e2ab1ca5e8fdaa586389`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-01-easy-okvis2x"></a>
## vo-lc/euroc_mav/MH_01_easy/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_01_easy/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_01_easy/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_01_easy/okvis2x/run3) | verified | success | 0 | yes |

Group `a8b20f048d7a72ff6a2f85a664fd51e14897331a8f37388a9781371e47c51d24`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-01-easy-airslam"></a>
## vo-lc/euroc_mav/MH_01_easy/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_01_easy/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_01_easy/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_01_easy/airslam/run3) | verified | success | 0 | yes |

Group `90397eea56c4f73ae0c2c1bd22508b4e3c03864eb40c559805242ff176174dd9`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-01-easy-ov2slam"></a>
## vo-lc/euroc_mav/MH_01_easy/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_01_easy/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `993143e732f96366d92572be078ad906beb2329831ce54e2bc99c9155a385f80`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `native_shutdown_error_despite_wrapper_exit_zero`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 163, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 167, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 145, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-01-easy-dpvo"></a>
## vo-lc/euroc_mav/MH_01_easy/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_01_easy/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_01_easy/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_01_easy/dpvo/run3) | verified | success | 0 | yes |

Group `18add92b0bcca50388430099140734efaebe395b83a3e80cbd45086245fb8968`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-01-easy-cuvslam"></a>
## vo-lc/euroc_mav/MH_01_easy/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_01_easy/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_01_easy/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_01_easy/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-03-medium-orbslam3"></a>
## vo-lc/euroc_mav/MH_03_medium/orbslam3

**A3/E3/S2/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_03_medium/orbslam3/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_03_medium/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_03_medium/orbslam3/run3) | blocked | completed_export_shutdown_error | 139 | yes |

Group `2fb7a8a1ab2b92230c69f9c42e7da5e311ac3f0079a814fb8405dc8a66d38cd1`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`, `saved_accuracy_with_recorded_nonzero_exit_no_clean_success`.
Native failure evidence r3: `{"line": 71, "text": "148.380 Segmentation fault (core dumped)"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-03-medium-okvis2"></a>
## vo-lc/euroc_mav/MH_03_medium/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_03_medium/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_03_medium/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_03_medium/okvis2/run3) | verified | success | 0 | yes |

Group `cfc3fae48330a43045c12f9e3baee2a9d728e6349c9adf36f833603d4c5a8b2d`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-03-medium-okvis2x"></a>
## vo-lc/euroc_mav/MH_03_medium/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_03_medium/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_03_medium/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_03_medium/okvis2x/run3) | verified | success | 0 | yes |

Group `4dd82501d0c1cabff757d5e889430297db6a9970aa55ed1dbf37eb3858d51cb0`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-03-medium-airslam"></a>
## vo-lc/euroc_mav/MH_03_medium/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_03_medium/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_03_medium/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_03_medium/airslam/run3) | verified | success | 0 | yes |

Group `90397eea56c4f73ae0c2c1bd22508b4e3c03864eb40c559805242ff176174dd9`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-03-medium-ov2slam"></a>
## vo-lc/euroc_mav/MH_03_medium/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_03_medium/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `993143e732f96366d92572be078ad906beb2329831ce54e2bc99c9155a385f80`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `native_shutdown_error_despite_wrapper_exit_zero`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 170, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 156, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 164, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-03-medium-dpvo"></a>
## vo-lc/euroc_mav/MH_03_medium/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_03_medium/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_03_medium/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_03_medium/dpvo/run3) | verified | success | 0 | yes |

Group `18add92b0bcca50388430099140734efaebe395b83a3e80cbd45086245fb8968`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-03-medium-cuvslam"></a>
## vo-lc/euroc_mav/MH_03_medium/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_03_medium/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_03_medium/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_03_medium/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-05-difficult-orbslam3"></a>
## vo-lc/euroc_mav/MH_05_difficult/orbslam3

**A3/E3/S2/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_05_difficult/orbslam3/run1) | blocked | completed_export_shutdown_error | 134 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_05_difficult/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_05_difficult/orbslam3/run3) | blocked | success | 0 | yes |

Group `2fb7a8a1ab2b92230c69f9c42e7da5e311ac3f0079a814fb8405dc8a66d38cd1`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`, `saved_accuracy_with_recorded_nonzero_exit_no_clean_success`.
Native failure evidence r1: `{"line": 77, "text": "126.067 terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-05-difficult-okvis2"></a>
## vo-lc/euroc_mav/MH_05_difficult/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_05_difficult/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_05_difficult/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_05_difficult/okvis2/run3) | verified | success | 0 | yes |

Group `f008abc6ef8588bd1ce1e0e42d832468b3416242c7f0755e716dfd1f36b79531`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-05-difficult-okvis2x"></a>
## vo-lc/euroc_mav/MH_05_difficult/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_05_difficult/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_05_difficult/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_05_difficult/okvis2x/run3) | verified | success | 0 | yes |

Group `4420f691447af480fcee7012c6e3f8a5a149f005de7628ed234a6257f9ff0838`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-05-difficult-airslam"></a>
## vo-lc/euroc_mav/MH_05_difficult/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_05_difficult/airslam/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_05_difficult/airslam/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_05_difficult/airslam/run3) | verified | success | 0 | yes |

Group `90397eea56c4f73ae0c2c1bd22508b4e3c03864eb40c559805242ff176174dd9`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-05-difficult-ov2slam"></a>
## vo-lc/euroc_mav/MH_05_difficult/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_05_difficult/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `44b82c17735c86e09896facdffc8a2b0d0500c0c850d52636e531e77498fbdec`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `native_shutdown_error_despite_wrapper_exit_zero`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 137, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 134, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 136, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-05-difficult-dpvo"></a>
## vo-lc/euroc_mav/MH_05_difficult/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_05_difficult/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_05_difficult/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_05_difficult/dpvo/run3) | verified | success | 0 | yes |

Group `0c757988994201fa47dc431e462ed66173da93dfca50e2284b68eb22bdbb5784`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-euroc-mav-mh-05-difficult-cuvslam"></a>
## vo-lc/euroc_mav/MH_05_difficult/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/euroc_mav/MH_05_difficult/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/euroc_mav/MH_05_difficult/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/euroc_mav/MH_05_difficult/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-zed2i-field1-110426-full-10fps-q90-orbslam3"></a>
## vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3

**A3/E3/S2/F1**; verified completed groups: 0+0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1) | invalid_setup | completed_export_shutdown_error | 139 | yes |
| 2 | [run2](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run3) | invalid_setup | success | 0 | yes |

Group `3a94af0233858111304b2576385f8e0d1d4866b7afa71b4a8884a465975601fd`: 0 verified / 1 recorded; `run1`.
Group `bedd5c4ff1ae3185aea851301102e4ad0246107fa04b2558a52d52056d40e80e`: 0 verified / 2 recorded; `run2`, `run3`.

Confirmed setup findings: `camera_fps_changed_15_to_10`.
Review blockers: `camera_fps_changed_15_to_10`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.
Native failure evidence r1: `{"line": 66, "text": "5651.548 Segmentation fault (core dumped)"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vo-lc-zed2i-field1-110426-full-10fps-q90-okvis2"></a>
## vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2

**A2/E1/S1/F1**; verified completed groups: 1+0. Verified N=3: no.

Cell next-action display: next: new group 3 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run2) | blocked | failure_without_final_trajectory | unknown | no |
| 3 | [run3](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run3) | not_executed | not_attempted | unknown | no |

Group `0adc87005c0fa3dc15449c46d7974f45203e6fb6b12cb54a319a4c37d4ebf6fa`: 1 verified / 1 recorded; `run1`.
Group `unverified:results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run2`: 0 verified / 1 recorded; `run2`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`, `native_execution_cause_and_usable_export_missing`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `final_ba_disabled`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.
Native failure evidence r2: `{"line": 12602, "text": "9388.271 Killed"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 blocked; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `retain_failed_or_interrupted_attempt_and_resolve_execution_cause`.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 cohort_completion; readiness unverified; r2 cohort_completion; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-zed2i-field1-110426-full-10fps-q90-okvis2x"></a>
## vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x

**A1/E1/S0/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: new group 3 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run1) | blocked | failure_with_saved_trajectory | 141 | yes |
| 2 | [run2](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run3) | not_executed | not_attempted | unknown | no |

Group `d61d6b79e4d0101a848fe2059474da38ee040b5d05b514d99216f16bbc52b47f`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`, `native_execution_cause_unresolved_recovered_causal_prefix_not_final_ba`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recovered_35_second_causal_prefix_not_final_bundle_adjustment`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `saved_result_has_unresolved_scientific_evidence`.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 cohort_completion; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-zed2i-field1-110426-full-10fps-q90-airslam"></a>
## vo-lc/zed2i/field1_110426_full_10fps_q90/airslam

**A3/E3/S3/F0**; verified completed groups: 0+0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/airslam/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/airslam/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/airslam/run3) | blocked | success | 0 | yes |

Group `166d9d1eb78dde4fa87a7bc36baf72d87b7a59c6b1f25b8b603157ddfe832dd6`: 0 verified / 1 recorded; `run3`.
Group `231be16dffe85468b65935fc49213abbeb06d17c27e8891599dd09eaca00e04e`: 0 verified / 2 recorded; `run1`, `run2`.

Confirmed setup findings: `airslam_zed_vo_lc_split_workspace_groups`.
Review blockers: `confirmed_estimator_defect_prevents_acceptance`.
Claim limits: none.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vo-lc-zed2i-field1-110426-full-10fps-q90-ov2slam"></a>
## vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `1baa6d8782baba323818c35fb128c7c20158c6e6444ee1f456ac4646fc2d5a4f`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `native_shutdown_error_despite_wrapper_exit_zero_retain_failure_count`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.
Native failure evidence r1: `{"line": 409, "text": "terminate called without an active exception"}`.
Native failure evidence r2: `{"line": 391, "text": "terminate called without an active exception"}`.
Native failure evidence r3: `{"line": 394, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-zed2i-field1-110426-full-10fps-q90-dpvo"></a>
## vo-lc/zed2i/field1_110426_full_10fps_q90/dpvo

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/dpvo/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/dpvo/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/dpvo/run3) | verified | success | 0 | yes |

Group `436c8393382803d40f9d467f150ea76bd6583b3218aa32572ea90e7428e74c6f`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vo-lc-zed2i-field1-110426-full-10fps-q90-cuvslam"></a>
## vo-lc/zed2i/field1_110426_full_10fps_q90/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/zed2i/field1_110426_full_10fps_q90/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq04-orbslam3"></a>
## vo-lc/citrusfarm/seq04/orbslam3

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq04/orbslam3/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq04/orbslam3/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq04/orbslam3/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq04-okvis2"></a>
## vo-lc/citrusfarm/seq04/okvis2

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq04/okvis2/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq04/okvis2/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq04/okvis2/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq04-okvis2x"></a>
## vo-lc/citrusfarm/seq04/okvis2x

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq04/okvis2x/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq04/okvis2x/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq04/okvis2x/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq04-airslam"></a>
## vo-lc/citrusfarm/seq04/airslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq04/airslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq04/airslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq04/airslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq04-ov2slam"></a>
## vo-lc/citrusfarm/seq04/ov2slam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq04/ov2slam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq04/ov2slam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq04/ov2slam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq04-dpvo"></a>
## vo-lc/citrusfarm/seq04/dpvo

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq04/dpvo/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq04/dpvo/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq04/dpvo/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq04-cuvslam"></a>
## vo-lc/citrusfarm/seq04/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq04/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq04/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq04/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq07-orbslam3"></a>
## vo-lc/citrusfarm/seq07/orbslam3

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq07/orbslam3/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq07/orbslam3/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq07/orbslam3/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq07-okvis2"></a>
## vo-lc/citrusfarm/seq07/okvis2

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq07/okvis2/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq07/okvis2/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq07/okvis2/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq07-okvis2x"></a>
## vo-lc/citrusfarm/seq07/okvis2x

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq07/okvis2x/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq07/okvis2x/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq07/okvis2x/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq07-airslam"></a>
## vo-lc/citrusfarm/seq07/airslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq07/airslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq07/airslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq07/airslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq07-ov2slam"></a>
## vo-lc/citrusfarm/seq07/ov2slam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq07/ov2slam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq07/ov2slam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq07/ov2slam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq07-dpvo"></a>
## vo-lc/citrusfarm/seq07/dpvo

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq07/dpvo/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq07/dpvo/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq07/dpvo/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vo-lc-citrusfarm-seq07-cuvslam"></a>
## vo-lc/citrusfarm/seq07/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vo-lc/citrusfarm/seq07/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vo-lc/citrusfarm/seq07/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vo-lc/citrusfarm/seq07/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-orbslam3"></a>
## vio/rosariov2/sequence1/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence1/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence1/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence1/orbslam3/run10003) | verified | success | 0 | yes |

Group `37bd807bbd4d4b7ee95ae7c6af4ef94e958f0595ad456e389c60489b03415791`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-okvis2"></a>
## vio/rosariov2/sequence1/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/rosariov2/sequence1/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/rosariov2/sequence1/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/rosariov2/sequence1/okvis2/run3) | verified | success | 0 | yes |

Group `076796bbb3d5673402122248a6aab8a99c1b593fdfcd2e5d1e1ec26f817f5b51`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-okvis2x"></a>
## vio/rosariov2/sequence1/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/rosariov2/sequence1/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/rosariov2/sequence1/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/rosariov2/sequence1/okvis2x/run3) | verified | success | 0 | yes |

Group `cccd51d2383929e00a600a0968d6b30ff08a6ad84d3bd4a76197e99ad51a2f40`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-airslam"></a>
## vio/rosariov2/sequence1/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence1/airslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence1/airslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence1/airslam/run10003) | verified | success | 0 | yes |

Group `7785ee1cbe285f0edc3a0b2bf2666b2f168306717c439b9c422f98f84d875c74`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-basalt"></a>
## vio/rosariov2/sequence1/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence1/basalt/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence1/basalt/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence1/basalt/run10003) | verified | success | 0 | yes |

Group `503136b7f95b8f06d5e94cdf46babf25eff0999996fd84375fc227b3f5b3c4d3`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-openvins"></a>
## vio/rosariov2/sequence1/openvins

**A3/E3/S2/F1**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence1/openvins/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence1/openvins/run10002) | verified | failure_scale_collapse | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence1/openvins/run10003) | verified | success | 0 | yes |

Group `0760bc08efdefc28d032752205e01596f976c397cd628a232bcaac6d3eb868c8`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `retain_failure_in_attempt_denominator`, `retain_observed_scale_collapse_in_attempt_denominator`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.
Native failure evidence r10002: `"native exit 0; evaluated outcome scale_collapse"`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-voxel-svio"></a>
## vio/rosariov2/sequence1/voxel_svio

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence1/voxel_svio/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence1/voxel_svio/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence1/voxel_svio/run10003) | verified | success | 0 | yes |

Group `30be1151cbeaf20e0cf3b34b6be205cc3f1507b73da3e704daaec125e94f331b`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-cuvslam"></a>
## vio/rosariov2/sequence1/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence1/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence1/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence1/cuvslam/run10003) | verified | success | 0 | yes |

Group `0d279c44af02e4c5705e2222b1caa24938dda4ec6dcd55e1a62005ae519bde5b`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-svo-pro"></a>
## vio/rosariov2/sequence1/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence1/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence1/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence1/svo_pro/run10003) | verified | success | 0 | yes |

Group `2713104a07a545ac2b8c9e52063a00afd8d1bed043c5ec256482a8a4d5499782`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence1-mast3r-fusion"></a>
## vio/rosariov2/sequence1/mast3r_fusion

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence1/mast3r_fusion/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence1/mast3r_fusion/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence1/mast3r_fusion/run10003) | verified | success | 0 | yes |

Group `b33bbbe9f3199dce54bcd4bdfd6acb7bab150eb5dc65d7330b1c8fdace7416b2`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`, `single_camera_with_imu_scale_from_imu_and_learned_depth`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-orbslam3"></a>
## vio/rosariov2/sequence5/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence5/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence5/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence5/orbslam3/run10003) | verified | success | 0 | yes |

Group `37bd807bbd4d4b7ee95ae7c6af4ef94e958f0595ad456e389c60489b03415791`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-okvis2"></a>
## vio/rosariov2/sequence5/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/rosariov2/sequence5/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/rosariov2/sequence5/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/rosariov2/sequence5/okvis2/run3) | verified | success | 0 | yes |

Group `d41b478ac09ac6be10070245d13471911e21fc4b3a5c91684ec9b0682aba40b7`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-okvis2x"></a>
## vio/rosariov2/sequence5/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/rosariov2/sequence5/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/rosariov2/sequence5/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/rosariov2/sequence5/okvis2x/run3) | verified | success | 0 | yes |

Group `0203c30fa160d4d994c26f414c5bc9a51241a794e14aaa9b12cd88e558db1ee8`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-airslam"></a>
## vio/rosariov2/sequence5/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence5/airslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence5/airslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence5/airslam/run10003) | verified | success | 0 | yes |

Group `7785ee1cbe285f0edc3a0b2bf2666b2f168306717c439b9c422f98f84d875c74`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-basalt"></a>
## vio/rosariov2/sequence5/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence5/basalt/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence5/basalt/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence5/basalt/run10003) | verified | success | 0 | yes |

Group `6e694bb09e2298a493885136fc25456d2c59b09f6b2fd25576350c046e0341ae`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-openvins"></a>
## vio/rosariov2/sequence5/openvins

**A3/E3/S1/F2**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence5/openvins/run10001) | verified | failure_scale_collapse | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence5/openvins/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence5/openvins/run10003) | verified | failure_scale_collapse | 0 | yes |

Group `0760bc08efdefc28d032752205e01596f976c397cd628a232bcaac6d3eb868c8`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `retain_failure_in_attempt_denominator`, `retain_observed_scale_collapse_in_attempt_denominator`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.
Native failure evidence r10001: `"native exit 0; evaluated outcome scale_collapse"`.
Native failure evidence r10003: `"native exit 0; evaluated outcome scale_collapse"`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-voxel-svio"></a>
## vio/rosariov2/sequence5/voxel_svio

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence5/voxel_svio/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence5/voxel_svio/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence5/voxel_svio/run10003) | verified | success | 0 | yes |

Group `30be1151cbeaf20e0cf3b34b6be205cc3f1507b73da3e704daaec125e94f331b`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-cuvslam"></a>
## vio/rosariov2/sequence5/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence5/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence5/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence5/cuvslam/run10003) | verified | success | 0 | yes |

Group `0f34f0d6064bbb0a3c3fb86c0cc9328426e83ac86b0380c26dafe2f1beb0cd4a`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-svo-pro"></a>
## vio/rosariov2/sequence5/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence5/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence5/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence5/svo_pro/run10003) | verified | success | 0 | yes |

Group `7a5c98dcf97d68e9c9068b7d4e1a9d49490a18f2d708293585d99fda6dba6719`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-rosariov2-sequence5-mast3r-fusion"></a>
## vio/rosariov2/sequence5/mast3r_fusion

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/rosariov2/sequence5/mast3r_fusion/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/rosariov2/sequence5/mast3r_fusion/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/rosariov2/sequence5/mast3r_fusion/run10003) | verified | success | 0 | yes |

Group `b33bbbe9f3199dce54bcd4bdfd6acb7bab150eb5dc65d7330b1c8fdace7416b2`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`, `single_camera_with_imu_scale_from_imu_and_learned_depth`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-hortimulti-strawberry02-orbslam3"></a>
## vio/hortimulti/strawberry02/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/orbslam3/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry02/orbslam3/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry02/orbslam3/run3) | invalid_setup | success | 0 | yes |

Group `e4e246ca2f26ad675ca292e67f365ad9b438a524a3876f8ba92dc399c42b40e1`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`, `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `historical_orb_loaded_library_abi_unknown`, `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_with_recorded_compatible_orb_g2o_build_keeping_historical_attempts_separate`, `resolve_or_document_claim_limit:historical_orb_loaded_library_abi_unknown`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_non_zed_orb_eigen_abi_and_shutdown_native_build`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry02-okvis2"></a>
## vio/hortimulti/strawberry02/okvis2

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/okvis2/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry02/okvis2/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry02/okvis2/run3) | invalid_setup | success | 0 | yes |

Group `aec160653d6faafd3180478787a1f147e6b0af639a16e8e739a96b8b4d61cc63`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry02-okvis2x"></a>
## vio/hortimulti/strawberry02/okvis2x

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/okvis2x/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry02/okvis2x/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry02/okvis2x/run3) | invalid_setup | success | 0 | yes |

Group `52dd52eaec9c09feb5135895755234d5b52c24831e58acf3e14026673fb044e4`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry02-airslam"></a>
## vio/hortimulti/strawberry02/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/airslam/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry02/airslam/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry02/airslam/run3) | invalid_setup | success | 0 | yes |

Group `79e939d4973f106e227d84178ee498bd593e7e73326c2434de425e0d72cfa05b`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `declare_sparse_keyframe_claim_or_validate_dense_export_before_dense_comparison`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry02-basalt"></a>
## vio/hortimulti/strawberry02/basalt

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/basalt/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry02/basalt/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry02/basalt/run3) | blocked | success | 0 | yes |

Group `0ebf0138550eea069538aba59df2634dc3343d6acc728f370715e70b44fd5004`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `basalt_horti_undocumented_imu_noise`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_leftover_imu_noise_with_documented_horti_profile_and_rerun_with_explicit_input_clock`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry02-openvins"></a>
## vio/hortimulti/strawberry02/openvins

**A1/E1/S0/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/openvins/run1) | blocked | failure_with_saved_trajectory | 134 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry02/openvins/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/vio/hortimulti/strawberry02/openvins/run3) | not_executed | not_attempted | unknown | no |

Group `1c955198923325c661966c833fed4ac55045231b1023acc7dcefeaa98acfc779`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `horti_imu_profile_and_clock_inconsistent`, `openvins_track_frequency_dropped_frames`.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 48, "text": "959.571 terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `retain_nonzero_exit_and_review_saved_native_failure_evidence`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry02-voxel-svio"></a>
## vio/hortimulti/strawberry02/voxel_svio

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/voxel_svio/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry02/voxel_svio/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry02/voxel_svio/run3) | blocked | success | 0 | yes |

Group `615143d25e1c76579b8f4752b4e03c1f05567302e862c0b6d47b1ea8299bd5f3`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_imu_profile_and_clock_inconsistent`, `horti_voxel_initializer_camera_imu_offset_omitted`.
Review blockers: `reviewed_evidence_changed:datasets/hortimulti/strawberry02/mav0/imu0/data.csv`.
Claim limits: none.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `capture_native_exit_separately_and_diagnose_logged_shutdown_errors`, `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `rerun_with_repaired_voxel_initializer_that_loads_the_declared_9p160379ms_offset_preserve_original_attempts`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry02-cuvslam"></a>
## vio/hortimulti/strawberry02/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio/hortimulti/strawberry02/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/hortimulti/strawberry02/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-hortimulti-strawberry02-svo-pro"></a>
## vio/hortimulti/strawberry02/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio/hortimulti/strawberry02/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/hortimulti/strawberry02/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `declare_window_gated_export_start`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-hortimulti-strawberry02-mast3r-fusion"></a>
## vio/hortimulti/strawberry02/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry02/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio/hortimulti/strawberry02/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/hortimulti/strawberry02/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-hortimulti-strawberry03-orbslam3"></a>
## vio/hortimulti/strawberry03/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/orbslam3/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry03/orbslam3/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry03/orbslam3/run3) | invalid_setup | success | 0 | yes |

Group `e4e246ca2f26ad675ca292e67f365ad9b438a524a3876f8ba92dc399c42b40e1`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`, `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `historical_orb_loaded_library_abi_unknown`, `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_with_recorded_compatible_orb_g2o_build_keeping_historical_attempts_separate`, `resolve_or_document_claim_limit:historical_orb_loaded_library_abi_unknown`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_non_zed_orb_eigen_abi_and_shutdown_native_build`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry03-okvis2"></a>
## vio/hortimulti/strawberry03/okvis2

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/okvis2/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry03/okvis2/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry03/okvis2/run3) | invalid_setup | success | 0 | yes |

Group `3b6a186fe461e056f92e96e0c4eea9888eb3dd0739f4f137ba91b03ec4172ae9`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry03-okvis2x"></a>
## vio/hortimulti/strawberry03/okvis2x

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/okvis2x/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry03/okvis2x/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry03/okvis2x/run3) | invalid_setup | success | 0 | yes |

Group `b83ceab6919b0d6d14cc38ffe4113b670f2850f014d69ba485bb48abe789e9af`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry03-airslam"></a>
## vio/hortimulti/strawberry03/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/airslam/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry03/airslam/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry03/airslam/run3) | invalid_setup | success | 0 | yes |

Group `79e939d4973f106e227d84178ee498bd593e7e73326c2434de425e0d72cfa05b`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `declare_sparse_keyframe_claim_or_validate_dense_export_before_dense_comparison`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry03-basalt"></a>
## vio/hortimulti/strawberry03/basalt

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/basalt/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry03/basalt/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry03/basalt/run3) | blocked | success | 0 | yes |

Group `0ebf0138550eea069538aba59df2634dc3343d6acc728f370715e70b44fd5004`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `basalt_horti_undocumented_imu_noise`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_leftover_imu_noise_with_documented_horti_profile_and_rerun_with_explicit_input_clock`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry03-openvins"></a>
## vio/hortimulti/strawberry03/openvins

**A1/E1/S0/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/openvins/run1) | blocked | failure_with_saved_trajectory | 134 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry03/openvins/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/vio/hortimulti/strawberry03/openvins/run3) | not_executed | not_attempted | unknown | no |

Group `1c955198923325c661966c833fed4ac55045231b1023acc7dcefeaa98acfc779`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `horti_imu_profile_and_clock_inconsistent`, `openvins_track_frequency_dropped_frames`.
Review blockers: `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 17, "text": "249.021 terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `retain_nonzero_exit_and_review_saved_native_failure_evidence`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry03-voxel-svio"></a>
## vio/hortimulti/strawberry03/voxel_svio

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/voxel_svio/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio/hortimulti/strawberry03/voxel_svio/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vio/hortimulti/strawberry03/voxel_svio/run3) | blocked | success | 0 | yes |

Group `615143d25e1c76579b8f4752b4e03c1f05567302e862c0b6d47b1ea8299bd5f3`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_imu_profile_and_clock_inconsistent`, `horti_voxel_initializer_camera_imu_offset_omitted`.
Review blockers: `reviewed_evidence_changed:datasets/hortimulti/strawberry03/mav0/imu0/data.csv`.
Claim limits: none.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `capture_native_exit_separately_and_diagnose_logged_shutdown_errors`, `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `rerun_with_repaired_voxel_initializer_that_loads_the_declared_9p160379ms_offset_preserve_original_attempts`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-hortimulti-strawberry03-cuvslam"></a>
## vio/hortimulti/strawberry03/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio/hortimulti/strawberry03/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/hortimulti/strawberry03/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-hortimulti-strawberry03-svo-pro"></a>
## vio/hortimulti/strawberry03/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio/hortimulti/strawberry03/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/hortimulti/strawberry03/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `declare_window_gated_export_start`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-hortimulti-strawberry03-mast3r-fusion"></a>
## vio/hortimulti/strawberry03/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/hortimulti/strawberry03/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio/hortimulti/strawberry03/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/hortimulti/strawberry03/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-euroc-mav-mh-01-easy-orbslam3"></a>
## vio/euroc_mav/MH_01_easy/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_01_easy/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_01_easy/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_01_easy/orbslam3/run10003) | verified | success | 0 | yes |

Group `6c8d30af406e96b7915652cbfcc7b9f7384d10ebb19fbc443a786cbb27489759`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-01-easy-okvis2"></a>
## vio/euroc_mav/MH_01_easy/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_01_easy/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_01_easy/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_01_easy/okvis2/run3) | verified | success | 0 | yes |

Group `9cbd15fe1d40ba0b9e16b4d9897d1fe5bc864ce0a819f469f4b8a6d79b01f3dd`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-01-easy-okvis2x"></a>
## vio/euroc_mav/MH_01_easy/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_01_easy/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_01_easy/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_01_easy/okvis2x/run3) | verified | success | 0 | yes |

Group `7bcb58383a4e43828892980dff24fce7973e681d8843d59f17dbb39a2a30f0a8`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-01-easy-airslam"></a>
## vio/euroc_mav/MH_01_easy/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run4](../results/vio/euroc_mav/MH_01_easy/airslam/run4) | verified | success | 0 | yes |
| 2 | [run5](../results/vio/euroc_mav/MH_01_easy/airslam/run5) | verified | success | 0 | yes |
| 3 | [run6](../results/vio/euroc_mav/MH_01_easy/airslam/run6) | verified | success | 0 | yes |

Group `08ef5be209d4a2b495f6700c9c5e88db3a893871f981d102c996b6d84425e9c0`: 3 verified / 3 recorded; `run4`, `run5`, `run6`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-01-easy-basalt"></a>
## vio/euroc_mav/MH_01_easy/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_01_easy/basalt/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_01_easy/basalt/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_01_easy/basalt/run3) | verified | success | 0 | yes |

Group `7c6540f133d06960cbc2f0eaa8f4b77dcc78bb662b1dfa7b1cf1ab19c5c287d3`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-01-easy-openvins"></a>
## vio/euroc_mav/MH_01_easy/openvins

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_01_easy/openvins/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_01_easy/openvins/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_01_easy/openvins/run10003) | verified | success | 0 | yes |

Group `ea3258d485fad6593d1f4cdd3129ad0f113eccd13a4cbc7263d86f51068222ca`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-01-easy-voxel-svio"></a>
## vio/euroc_mav/MH_01_easy/voxel_svio

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_01_easy/voxel_svio/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_01_easy/voxel_svio/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_01_easy/voxel_svio/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `65cddd59117d4d326b33574821beba012584e232e67c2c37099d6b9149ee3b25`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `export_coverage_below_95_percent_no_clean_success_tick`, `native_shutdown_error_despite_wrapper_exit_zero`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 43351, "text": "terminate called after throwing an instance of 'boost::wrapexcept<boost::lock_error>'"}`.
Native failure evidence r2: `{"line": 43337, "text": "terminate called after throwing an instance of 'boost::wrapexcept<boost::lock_error>'"}`.
Native failure evidence r3: `{"line": 43346, "text": "terminate called after throwing an instance of 'boost::wrapexcept<boost::lock_error>'"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-01-easy-cuvslam"></a>
## vio/euroc_mav/MH_01_easy/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_01_easy/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_01_easy/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_01_easy/cuvslam/run10003) | verified | success | 0 | yes |

Group `16469a3f8aa464b903771b25ab1b7c41b0f491674782700b26d03a4c38e7ed89`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-01-easy-svo-pro"></a>
## vio/euroc_mav/MH_01_easy/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_01_easy/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_01_easy/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_01_easy/svo_pro/run10003) | verified | success | 0 | yes |

Group `38ad8c1b9966cb962de9748e733088c3ed89357b811854ec0618e5e85e218876`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-01-easy-mast3r-fusion"></a>
## vio/euroc_mav/MH_01_easy/mast3r_fusion

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_01_easy/mast3r_fusion/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_01_easy/mast3r_fusion/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_01_easy/mast3r_fusion/run10003) | verified | success | 0 | yes |

Group `71c974a4f0f9b2beb0d54c73a4aaf7a3793b41ac8e2d8f0a509d4e684accaa5e`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `single_camera_with_imu_scale_from_imu_and_learned_depth`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-orbslam3"></a>
## vio/euroc_mav/MH_03_medium/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_03_medium/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_03_medium/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_03_medium/orbslam3/run10003) | verified | success | 0 | yes |

Group `6c8d30af406e96b7915652cbfcc7b9f7384d10ebb19fbc443a786cbb27489759`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-okvis2"></a>
## vio/euroc_mav/MH_03_medium/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_03_medium/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_03_medium/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_03_medium/okvis2/run3) | verified | success | 0 | yes |

Group `69102c90f4c098fa605c7e54a225c7af66dcaeb170878dc2451e302a7dacec52`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-okvis2x"></a>
## vio/euroc_mav/MH_03_medium/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_03_medium/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_03_medium/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_03_medium/okvis2x/run3) | verified | success | 0 | yes |

Group `01be1235e667a3383f25ee263a78c8b2ee7aa6b022ded4d10bcdc87f618165a1`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-airslam"></a>
## vio/euroc_mav/MH_03_medium/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run4](../results/vio/euroc_mav/MH_03_medium/airslam/run4) | verified | success | 0 | yes |
| 2 | [run5](../results/vio/euroc_mav/MH_03_medium/airslam/run5) | verified | success | 0 | yes |
| 3 | [run6](../results/vio/euroc_mav/MH_03_medium/airslam/run6) | verified | success | 0 | yes |

Group `08ef5be209d4a2b495f6700c9c5e88db3a893871f981d102c996b6d84425e9c0`: 3 verified / 3 recorded; `run4`, `run5`, `run6`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-basalt"></a>
## vio/euroc_mav/MH_03_medium/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_03_medium/basalt/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_03_medium/basalt/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_03_medium/basalt/run3) | verified | success | 0 | yes |

Group `7c6540f133d06960cbc2f0eaa8f4b77dcc78bb662b1dfa7b1cf1ab19c5c287d3`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-openvins"></a>
## vio/euroc_mav/MH_03_medium/openvins

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_03_medium/openvins/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_03_medium/openvins/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_03_medium/openvins/run10003) | verified | success | 0 | yes |

Group `ea3258d485fad6593d1f4cdd3129ad0f113eccd13a4cbc7263d86f51068222ca`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-voxel-svio"></a>
## vio/euroc_mav/MH_03_medium/voxel_svio

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_03_medium/voxel_svio/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_03_medium/voxel_svio/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_03_medium/voxel_svio/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `72ad00dbe0457d282f0633e79d58a18802fc2211da7b1f3000dd8a6f2df40f94`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `native_shutdown_error_despite_wrapper_exit_zero`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 31896, "text": "terminate called after throwing an instance of 'boost::wrapexcept<boost::lock_error>'"}`.
Native failure evidence r2: `{"line": 31865, "text": "terminate called after throwing an instance of 'boost::wrapexcept<boost::lock_error>'"}`.
Native failure evidence r3: `{"line": 31868, "text": "terminate called after throwing an instance of 'boost::wrapexcept<boost::lock_error>'"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-cuvslam"></a>
## vio/euroc_mav/MH_03_medium/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_03_medium/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_03_medium/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_03_medium/cuvslam/run10003) | verified | success | 0 | yes |

Group `c5fbd7b22d2921831521c1386ee6b8ea95f73493eb4a60f73b6e01b7309ca689`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-svo-pro"></a>
## vio/euroc_mav/MH_03_medium/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_03_medium/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_03_medium/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_03_medium/svo_pro/run10003) | verified | success | 0 | yes |

Group `0a84d736d537a38bdf0e252691cd9049def3e1c422ecbebb9baf3f4653106fbc`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-03-medium-mast3r-fusion"></a>
## vio/euroc_mav/MH_03_medium/mast3r_fusion

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_03_medium/mast3r_fusion/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_03_medium/mast3r_fusion/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_03_medium/mast3r_fusion/run10003) | verified | success | 0 | yes |

Group `71c974a4f0f9b2beb0d54c73a4aaf7a3793b41ac8e2d8f0a509d4e684accaa5e`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `single_camera_with_imu_scale_from_imu_and_learned_depth`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-orbslam3"></a>
## vio/euroc_mav/MH_05_difficult/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_05_difficult/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_05_difficult/orbslam3/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_05_difficult/orbslam3/run10003) | verified | success | 0 | yes |

Group `6c8d30af406e96b7915652cbfcc7b9f7384d10ebb19fbc443a786cbb27489759`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-okvis2"></a>
## vio/euroc_mav/MH_05_difficult/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_05_difficult/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_05_difficult/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_05_difficult/okvis2/run3) | verified | success | 0 | yes |

Group `c7d388626001f1158e01d5238755405d1d8d40bc1b258a97d36c15f1c5e689d0`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-okvis2x"></a>
## vio/euroc_mav/MH_05_difficult/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_05_difficult/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_05_difficult/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_05_difficult/okvis2x/run3) | verified | success | 0 | yes |

Group `34110798627c53f4dad017588ec3b163985de88392d1a7e1dfb509740c2e9206`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-airslam"></a>
## vio/euroc_mav/MH_05_difficult/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run4](../results/vio/euroc_mav/MH_05_difficult/airslam/run4) | verified | success | 0 | yes |
| 2 | [run5](../results/vio/euroc_mav/MH_05_difficult/airslam/run5) | verified | success | 0 | yes |
| 3 | [run6](../results/vio/euroc_mav/MH_05_difficult/airslam/run6) | verified | success | 0 | yes |

Group `08ef5be209d4a2b495f6700c9c5e88db3a893871f981d102c996b6d84425e9c0`: 3 verified / 3 recorded; `run4`, `run5`, `run6`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-basalt"></a>
## vio/euroc_mav/MH_05_difficult/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_05_difficult/basalt/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_05_difficult/basalt/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_05_difficult/basalt/run3) | verified | success | 0 | yes |

Group `7c6540f133d06960cbc2f0eaa8f4b77dcc78bb662b1dfa7b1cf1ab19c5c287d3`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-openvins"></a>
## vio/euroc_mav/MH_05_difficult/openvins

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_05_difficult/openvins/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_05_difficult/openvins/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_05_difficult/openvins/run10003) | verified | success | 0 | yes |

Group `ea3258d485fad6593d1f4cdd3129ad0f113eccd13a4cbc7263d86f51068222ca`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-voxel-svio"></a>
## vio/euroc_mav/MH_05_difficult/voxel_svio

**A3/E3/S0/F3**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio/euroc_mav/MH_05_difficult/voxel_svio/run1) | verified | completed_export_shutdown_error | 0 | yes |
| 2 | [run2](../results/vio/euroc_mav/MH_05_difficult/voxel_svio/run2) | verified | completed_export_shutdown_error | 0 | yes |
| 3 | [run3](../results/vio/euroc_mav/MH_05_difficult/voxel_svio/run3) | verified | completed_export_shutdown_error | 0 | yes |

Group `d9f7cc63d1cd0b377f417dbc74ad1534079f57b9eb8f4cf90b3fc3b1a6929974`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `native_shutdown_error_despite_wrapper_exit_zero`, `no_measured_processing_rate_or_realtime_deadline_claim`.
Native failure evidence r1: `{"line": 26517, "text": "terminate called after throwing an instance of 'boost::wrapexcept<boost::lock_error>'"}`.
Native failure evidence r2: `{"line": 26539, "text": "terminate called after throwing an instance of 'boost::wrapexcept<boost::lock_error>'"}`.
Native failure evidence r3: `{"line": 26573, "text": "terminate called after throwing an instance of 'boost::wrapexcept<boost::lock_error>'"}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-cuvslam"></a>
## vio/euroc_mav/MH_05_difficult/cuvslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_05_difficult/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_05_difficult/cuvslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_05_difficult/cuvslam/run10003) | verified | success | 0 | yes |

Group `20f3668a92fdc423f7a4f2fe2fff976b26a0b30a11956fb49a07d6515552ee8c`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-svo-pro"></a>
## vio/euroc_mav/MH_05_difficult/svo_pro

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_05_difficult/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_05_difficult/svo_pro/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_05_difficult/svo_pro/run10003) | verified | success | 0 | yes |

Group `fbcd96ceb0e9f7de76dc1789097a64d6cab8b34c41d9ab04159c2bb510f4fdc1`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `export_coverage_below_95_percent_no_clean_success_tick`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-euroc-mav-mh-05-difficult-mast3r-fusion"></a>
## vio/euroc_mav/MH_05_difficult/mast3r_fusion

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/euroc_mav/MH_05_difficult/mast3r_fusion/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/euroc_mav/MH_05_difficult/mast3r_fusion/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/euroc_mav/MH_05_difficult/mast3r_fusion/run10003) | verified | success | 0 | yes |

Group `71c974a4f0f9b2beb0d54c73a4aaf7a3793b41ac8e2d8f0a509d4e684accaa5e`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `single_camera_with_imu_scale_from_imu_and_learned_depth`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-orbslam3"></a>
## vio/zed2i/field1_110426_full_10fps_q90/orbslam3

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run10003](../results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run10003) | verified | success | 0 | yes |
| 3 | [run10004](../results/vio/zed2i/field1_110426_full_10fps_q90/orbslam3/run10004) | verified | success | 0 | yes |

Group `pooled-ae62430aa8f2005648be420e3feab96284a8688d16fdc85cd6d64f15acabc493`: 3 verified / 3 recorded; `run10001`, `run10003`, `run10004`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-okvis2"></a>
## vio/zed2i/field1_110426_full_10fps_q90/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run10001) | verified | success | 0 | yes |
| 2 | [run10003](../results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run10003) | verified | success | 0 | yes |
| 3 | [run10004](../results/vio/zed2i/field1_110426_full_10fps_q90/okvis2/run10004) | verified | success | 0 | yes |

Group `pooled-89ccb0dd78075245b7803e0c9191da07f1556ca8cfca01d16fbfd5638b250c6a`: 3 verified / 3 recorded; `run10001`, `run10003`, `run10004`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-okvis2x"></a>
## vio/zed2i/field1_110426_full_10fps_q90/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run10001) | verified | success | 0 | yes |
| 2 | [run10003](../results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run10003) | verified | success | 0 | yes |
| 3 | [run10004](../results/vio/zed2i/field1_110426_full_10fps_q90/okvis2x/run10004) | verified | success | 0 | yes |

Group `pooled-00ad8efe75720f1821c5eb3782528d8db4fa958c2c121de3f77c5d01c1359934`: 3 verified / 3 recorded; `run10001`, `run10003`, `run10004`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-airslam"></a>
## vio/zed2i/field1_110426_full_10fps_q90/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/zed2i/field1_110426_full_10fps_q90/airslam/run10003) | verified | success | 0 | yes |

Group `493c511163fb62d020ef9de753403a162486b65accd890308f28bfc96c294b36`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `native_sparse_keyframe_accuracy_not_dense_tracking`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-basalt"></a>
## vio/zed2i/field1_110426_full_10fps_q90/basalt

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/zed2i/field1_110426_full_10fps_q90/basalt/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/zed2i/field1_110426_full_10fps_q90/basalt/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/zed2i/field1_110426_full_10fps_q90/basalt/run10003) | verified | success | 0 | yes |

Group `2016ca170cd641e56986df750ee744eb82dbf839e70115e2cc6342dc7460dafe`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-openvins"></a>
## vio/zed2i/field1_110426_full_10fps_q90/openvins

**A3/E3/S0/F3**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run10001) | blocked | failure_scale_collapse | 139 | yes |
| 2 | [run10002](../results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run10002) | blocked | failure_scale_collapse | 139 | yes |
| 3 | [run10003](../results/vio/zed2i/field1_110426_full_10fps_q90/openvins/run10003) | blocked | failure_with_saved_trajectory | 139 | yes |

Group `b847248537defbe77aa834709f8f723159f85c7ee5c350d6d3b9e5a1519b2bf2`: 0 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: `openvins_track_frequency_dropped_frames`.
Review blockers: `confirmed_estimator_defect_prevents_acceptance`.
Claim limits: none.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-voxel-svio"></a>
## vio/zed2i/field1_110426_full_10fps_q90/voxel_svio

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run10001) | verified | success | 0 | yes |
| 2 | [run10002](../results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run10002) | verified | success | 0 | yes |
| 3 | [run10003](../results/vio/zed2i/field1_110426_full_10fps_q90/voxel_svio/run10003) | verified | success | 0 | yes |

Group `94ace07f1b3e75e665d18c926f7c760883e791a9d795c729dad14b0cf8e36656`: 3 verified / 3 recorded; `run10001`, `run10002`, `run10003`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-cuvslam"></a>
## vio/zed2i/field1_110426_full_10fps_q90/cuvslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/zed2i/field1_110426_full_10fps_q90/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/zed2i/field1_110426_full_10fps_q90/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/zed2i/field1_110426_full_10fps_q90/cuvslam/run3) | blocked | not_attempted | unknown | no |

Group `45cb95fc37d5606e6c76190fb421da261b25223704ed8582e590fbbed766e8cd`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-svo-pro"></a>
## vio/zed2i/field1_110426_full_10fps_q90/svo_pro

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/zed2i/field1_110426_full_10fps_q90/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/zed2i/field1_110426_full_10fps_q90/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/zed2i/field1_110426_full_10fps_q90/svo_pro/run3) | blocked | not_attempted | unknown | no |

Group `cf3e3b12f3b8646980ac3b3dd97b0b6c6a52fcd8beb2b04150fa3d5c0838cdbb`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `authors_export_starts_after_keyframe_window_fills`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-zed2i-field1-110426-full-10fps-q90-mast3r-fusion"></a>
## vio/zed2i/field1_110426_full_10fps_q90/mast3r_fusion

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10002](../results/vio/zed2i/field1_110426_full_10fps_q90/mast3r_fusion/run10002) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/zed2i/field1_110426_full_10fps_q90/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/zed2i/field1_110426_full_10fps_q90/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |

Group `a070ea08ab63e0ff9eae85b1de4f9e5de3ba7afd03544685ee912b533eb15b93`: 1 verified / 1 recorded; `run10002`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `single_camera_with_imu_scale_from_imu_and_learned_depth`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-orbslam3"></a>
## vio/citrusfarm/seq04/orbslam3

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/orbslam3/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/orbslam3/run3) | blocked | not_attempted | unknown | no |

Group `a63f66df631d68a3470c4e995767967c4a973d85ad7bd7d3793f5c2f562a8315`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-okvis2"></a>
## vio/citrusfarm/seq04/okvis2

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/okvis2/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/okvis2/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/okvis2/run3) | blocked | not_attempted | unknown | no |

Group `d7f927a2462128981daea68e23c7a81be73228c72c2ae4784ef088c5257b4d15`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-okvis2x"></a>
## vio/citrusfarm/seq04/okvis2x

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/okvis2x/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/okvis2x/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/okvis2x/run3) | blocked | not_attempted | unknown | no |

Group `76a1321c798ab0178138781a0baa655bc9f8ef24aad6cfcc32158cae6f7f65e0`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-airslam"></a>
## vio/citrusfarm/seq04/airslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/airslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/airslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/airslam/run3) | blocked | not_attempted | unknown | no |

Group `7642d23c5342cea7229c17b4d299677a581d9b97acc6301e79d6751ee15e1981`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-basalt"></a>
## vio/citrusfarm/seq04/basalt

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/basalt/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/basalt/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/basalt/run3) | blocked | not_attempted | unknown | no |

Group `b97bfdad8f461c66aeefa35ef4ee9c7e4963c4f9506d96de1fbd099b603b1441`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-openvins"></a>
## vio/citrusfarm/seq04/openvins

**A1/E1/S1/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/openvins/run10001) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/openvins/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/openvins/run3) | blocked | not_attempted | unknown | no |

Group `559dc32bb9f38bede002fb5a2a127af079393c63271183d84c66fef318280f64`: 0 verified / 1 recorded; `run10001`.

Confirmed setup findings: `openvins_track_frequency_dropped_frames`.
Review blockers: `confirmed_estimator_defect_prevents_acceptance`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-voxel-svio"></a>
## vio/citrusfarm/seq04/voxel_svio

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/voxel_svio/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/voxel_svio/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/voxel_svio/run3) | blocked | not_attempted | unknown | no |

Group `d53e12c09f9d7d8c149d8ec4934db3e1918c03ce5524d47056a060f515024688`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-cuvslam"></a>
## vio/citrusfarm/seq04/cuvslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/cuvslam/run3) | blocked | not_attempted | unknown | no |

Group `b13f31ae01c7f00992dad0943052b429918e03774c3445e9cc10bb0e7f02bd56`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-svo-pro"></a>
## vio/citrusfarm/seq04/svo_pro

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/svo_pro/run3) | blocked | not_attempted | unknown | no |

Group `4718830fad1fb0e39b8f6a3df4f5bb65e1131cea4c5835509c462f1078b290f7`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq04-mast3r-fusion"></a>
## vio/citrusfarm/seq04/mast3r_fusion

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq04/mast3r_fusion/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq04/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq04/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |

Group `142ea1bb52b3c7afba89a45d8821eea07f9714de3cd86a590f066afd7e8dca2e`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `single_camera_with_imu_scale_from_imu_and_learned_depth`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-orbslam3"></a>
## vio/citrusfarm/seq07/orbslam3

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/orbslam3/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/orbslam3/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/orbslam3/run3) | blocked | not_attempted | unknown | no |

Group `a63f66df631d68a3470c4e995767967c4a973d85ad7bd7d3793f5c2f562a8315`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-okvis2"></a>
## vio/citrusfarm/seq07/okvis2

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/okvis2/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/okvis2/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/okvis2/run3) | blocked | not_attempted | unknown | no |

Group `0b7a1c03da4a61226178da67c2a16765840c27bf0b9fcaf40fc08d9f6c05f035`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-okvis2x"></a>
## vio/citrusfarm/seq07/okvis2x

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/okvis2x/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/okvis2x/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/okvis2x/run3) | blocked | not_attempted | unknown | no |

Group `c5eb9ea7077e67dd6f8cd4a5018d6d39fd9fa4ce43fb935b747ce2931648bef6`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-airslam"></a>
## vio/citrusfarm/seq07/airslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/airslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/airslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/airslam/run3) | blocked | not_attempted | unknown | no |

Group `7642d23c5342cea7229c17b4d299677a581d9b97acc6301e79d6751ee15e1981`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `disclose_rig_specific_algorithm_parameters_in_saved_parameter_review`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-basalt"></a>
## vio/citrusfarm/seq07/basalt

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/basalt/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/basalt/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/basalt/run3) | blocked | not_attempted | unknown | no |

Group `111f7551ce149281c7f3f19cffe19363fd5eb59be016795aa3866bdd47d60aa1`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-openvins"></a>
## vio/citrusfarm/seq07/openvins

**A1/E1/S0/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/openvins/run10001) | blocked | failure_scale_collapse | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/openvins/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/openvins/run3) | blocked | not_attempted | unknown | no |

Group `559dc32bb9f38bede002fb5a2a127af079393c63271183d84c66fef318280f64`: 0 verified / 1 recorded; `run10001`.

Confirmed setup findings: `openvins_track_frequency_dropped_frames`.
Review blockers: `confirmed_estimator_defect_prevents_acceptance`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-voxel-svio"></a>
## vio/citrusfarm/seq07/voxel_svio

**A1/E1/S0/F1**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/voxel_svio/run10001) | verified | failure_scale_collapse | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/voxel_svio/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/voxel_svio/run3) | blocked | not_attempted | unknown | no |

Group `d53e12c09f9d7d8c149d8ec4934db3e1918c03ce5524d47056a060f515024688`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `retain_failure_in_attempt_denominator`, `retain_observed_scale_collapse_in_attempt_denominator`.
Native failure evidence r10001: `"native exit 0; evaluated outcome scale_collapse"`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-cuvslam"></a>
## vio/citrusfarm/seq07/cuvslam

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/cuvslam/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/cuvslam/run3) | blocked | not_attempted | unknown | no |

Group `ed05a78ea376ea0769db90b9f9f297c67ac0dd07f605441dff273841433138fc`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-svo-pro"></a>
## vio/citrusfarm/seq07/svo_pro

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/svo_pro/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/svo_pro/run3) | blocked | not_attempted | unknown | no |

Group `2a230d7a906bbe8424028e24c33cfd21383299a6b2d6f99d15947740879a32cd`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `authors_export_starts_after_keyframe_window_fills`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-citrusfarm-seq07-mast3r-fusion"></a>
## vio/citrusfarm/seq07/mast3r_fusion

**A1/E1/S1/F0**; verified completed groups: 1. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run10001](../results/vio/citrusfarm/seq07/mast3r_fusion/run10001) | verified | success | 0 | yes |
| 2 | [run2](../results/vio/citrusfarm/seq07/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio/citrusfarm/seq07/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |

Group `142ea1bb52b3c7afba89a45d8821eea07f9714de3cd86a590f066afd7e8dca2e`: 1 verified / 1 recorded; `run10001`.

Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `citrusfarm_position_only_reference_level_platform_lever_and_path_heading`, `citrusfarm_reference_host_arrival_stamps_camera_gnss_clock_unmeasured`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `recorded_native_assets_not_complete_transitive_build_reconstruction`, `single_camera_with_imu_scale_from_imu_and_learned_depth`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence1-orbslam3"></a>
## vio-lc/rosariov2/sequence1/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence1/orbslam3/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio-lc/rosariov2/sequence1/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vio-lc/rosariov2/sequence1/orbslam3/run3) | blocked | success | 0 | yes |

Group `c5eaa79e03fdc75fd88c70c5e747edaca2b3d3308854092cb8033b8142c99125`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence1-okvis2"></a>
## vio-lc/rosariov2/sequence1/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence1/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/rosariov2/sequence1/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/rosariov2/sequence1/okvis2/run3) | verified | success | 0 | yes |

Group `19cf70f6c56204a165ac8e273f7f493895936793c74b2c1420252061ed102d21`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence1-okvis2x"></a>
## vio-lc/rosariov2/sequence1/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence1/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/rosariov2/sequence1/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/rosariov2/sequence1/okvis2x/run3) | verified | success | 0 | yes |

Group `738da94cf8f861e42e2e0920827cc4cf993f96a5723c9558dd3349aed0782708`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence1-airslam"></a>
## vio-lc/rosariov2/sequence1/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence1/airslam/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/rosariov2/sequence1/airslam/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/rosariov2/sequence1/airslam/run3) | invalid_setup | success | 0 | yes |

Group `f4d572cca81d2f7e538479040f16f4c851d3faaa7853f50fcf7deb9cd402c9f1`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `rosario_identity_camera_imu_extrinsic`.
Review blockers: `rosario_identity_camera_imu_extrinsic`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence1-cuvslam"></a>
## vio-lc/rosariov2/sequence1/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence1/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/rosariov2/sequence1/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/rosariov2/sequence1/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence1-svo-pro"></a>
## vio-lc/rosariov2/sequence1/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence1/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/rosariov2/sequence1/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/rosariov2/sequence1/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence1-mast3r-fusion"></a>
## vio-lc/rosariov2/sequence1/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence1/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/rosariov2/sequence1/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/rosariov2/sequence1/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence5-orbslam3"></a>
## vio-lc/rosariov2/sequence5/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence5/orbslam3/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio-lc/rosariov2/sequence5/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vio-lc/rosariov2/sequence5/orbslam3/run3) | blocked | success | 0 | yes |

Group `c5eaa79e03fdc75fd88c70c5e747edaca2b3d3308854092cb8033b8142c99125`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence5-okvis2"></a>
## vio-lc/rosariov2/sequence5/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence5/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/rosariov2/sequence5/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/rosariov2/sequence5/okvis2/run3) | verified | success | 0 | yes |

Group `bd0b8790e7b22727881f1d201cd64d77081ed5c7bea793a14e2d40f4952f238d`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence5-okvis2x"></a>
## vio-lc/rosariov2/sequence5/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence5/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/rosariov2/sequence5/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/rosariov2/sequence5/okvis2x/run3) | verified | success | 0 | yes |

Group `97307362bc482f4e94d5fd5b68c287989458a7069cbdd7c1996a7f3ba5bc3fe9`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence5-airslam"></a>
## vio-lc/rosariov2/sequence5/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence5/airslam/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/rosariov2/sequence5/airslam/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/rosariov2/sequence5/airslam/run3) | invalid_setup | success | 0 | yes |

Group `f4d572cca81d2f7e538479040f16f4c851d3faaa7853f50fcf7deb9cd402c9f1`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `rosario_identity_camera_imu_extrinsic`.
Review blockers: `rosario_identity_camera_imu_extrinsic`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence5-cuvslam"></a>
## vio-lc/rosariov2/sequence5/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence5/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/rosariov2/sequence5/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/rosariov2/sequence5/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence5-svo-pro"></a>
## vio-lc/rosariov2/sequence5/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence5/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/rosariov2/sequence5/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/rosariov2/sequence5/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-rosariov2-sequence5-mast3r-fusion"></a>
## vio-lc/rosariov2/sequence5/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/rosariov2/sequence5/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/rosariov2/sequence5/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/rosariov2/sequence5/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-hortimulti-strawberry02-orbslam3"></a>
## vio-lc/hortimulti/strawberry02/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry02/orbslam3/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry02/orbslam3/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry02/orbslam3/run3) | invalid_setup | success | 0 | yes |

Group `c8fb082f5e74e1529ad692cd01516ae7c253669990776919bb03905bd7527cbe`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`, `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`, `orb_horti_rectified_camera_imu_extrinsic`.
Review blockers: `historical_orb_loaded_library_abi_unknown`, `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `orb_horti_rectified_camera_imu_extrinsic`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_with_recorded_compatible_orb_g2o_build_keeping_historical_attempts_separate`, `resolve_or_document_claim_limit:historical_orb_loaded_library_abi_unknown`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:orb_horti_rectified_camera_imu_extrinsic`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_non_zed_orb_eigen_abi_and_shutdown_native_build`, `validate_rectified_horti_imu_extrinsic_and_run_new_vio_lc_cohort_preserving_raw_frame_attempts`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-lc-hortimulti-strawberry02-okvis2"></a>
## vio-lc/hortimulti/strawberry02/okvis2

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry02/okvis2/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry02/okvis2/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry02/okvis2/run3) | invalid_setup | success | 0 | yes |

Group `be86e9aa751b50b0aa4caa36ad02397841c03dcd23426d1f323cffc6af2434e8`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-lc-hortimulti-strawberry02-okvis2x"></a>
## vio-lc/hortimulti/strawberry02/okvis2x

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry02/okvis2x/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry02/okvis2x/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry02/okvis2x/run3) | invalid_setup | success | 0 | yes |

Group `40b444ef5ce4af78d4ae2b4a6067bbce7aa4ed88df41ae66fc7f8d30bb23904c`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-lc-hortimulti-strawberry02-airslam"></a>
## vio-lc/hortimulti/strawberry02/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry02/airslam/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry02/airslam/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry02/airslam/run3) | invalid_setup | success | 0 | yes |

Group `08b962a0b00ade1997e4bf6bb729d28939389c036bc8deb49422a8b51a4645da`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `declare_sparse_keyframe_claim_or_validate_dense_export_before_dense_comparison`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-lc-hortimulti-strawberry02-cuvslam"></a>
## vio-lc/hortimulti/strawberry02/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry02/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry02/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry02/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-lc-hortimulti-strawberry02-svo-pro"></a>
## vio-lc/hortimulti/strawberry02/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry02/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry02/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry02/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `declare_window_gated_export_start_and_forward_only_loop_correction`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-lc-hortimulti-strawberry02-mast3r-fusion"></a>
## vio-lc/hortimulti/strawberry02/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry02/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry02/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry02/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `declare_keyframe_only_global_trajectory_claim`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-lc-hortimulti-strawberry03-orbslam3"></a>
## vio-lc/hortimulti/strawberry03/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry03/orbslam3/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry03/orbslam3/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry03/orbslam3/run3) | invalid_setup | success | 0 | yes |

Group `c8fb082f5e74e1529ad692cd01516ae7c253669990776919bb03905bd7527cbe`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`, `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`, `orb_horti_rectified_camera_imu_extrinsic`.
Review blockers: `historical_orb_loaded_library_abi_unknown`, `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `orb_horti_rectified_camera_imu_extrinsic`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `replace_with_recorded_compatible_orb_g2o_build_keeping_historical_attempts_separate`, `resolve_or_document_claim_limit:historical_orb_loaded_library_abi_unknown`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:orb_horti_rectified_camera_imu_extrinsic`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_non_zed_orb_eigen_abi_and_shutdown_native_build`, `validate_rectified_horti_imu_extrinsic_and_run_new_vio_lc_cohort_preserving_raw_frame_attempts`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-lc-hortimulti-strawberry03-okvis2"></a>
## vio-lc/hortimulti/strawberry03/okvis2

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry03/okvis2/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry03/okvis2/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry03/okvis2/run3) | invalid_setup | success | 0 | yes |

Group `182b1097d4cdc561ff738fdd7229a670e480973b321d3617a9012cd02900d664`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-lc-hortimulti-strawberry03-okvis2x"></a>
## vio-lc/hortimulti/strawberry03/okvis2x

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry03/okvis2x/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry03/okvis2x/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry03/okvis2x/run3) | invalid_setup | success | 0 | yes |

Group `86f33a0ad698589886db3a46ae9697422dd1a4565aa93747d9c9a9e416c2e9d1`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `freeze_and_label_final_bundle_adjustment_and_extrinsic_optimization_policy`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-lc-hortimulti-strawberry03-airslam"></a>
## vio-lc/hortimulti/strawberry03/airslam

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry03/airslam/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry03/airslam/run2) | invalid_setup | success | 0 | yes |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry03/airslam/run3) | invalid_setup | success | 0 | yes |

Group `08b962a0b00ade1997e4bf6bb729d28939389c036bc8deb49422a8b51a4645da`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `horti_camera_imu_time_offset_uncompensated`, `horti_imu_profile_and_clock_inconsistent`.
Review blockers: `horti_camera_imu_time_offset_uncompensated`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: `apply_published_positive_9p160379ms_camera_to_imu_time_relation_in_estimator_inputs_preserve_original_attempts`, `complete_cell_configuration_input_and_claim_review`, `declare_sparse_keyframe_claim_or_validate_dense_export_before_dense_comparison`, `document_remaining_rig_specific_algorithm_settings_from_saved_parameter_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:horti_camera_imu_time_offset_uncompensated`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`.

<a id="vio-lc-hortimulti-strawberry03-cuvslam"></a>
## vio-lc/hortimulti/strawberry03/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry03/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry03/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry03/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-lc-hortimulti-strawberry03-svo-pro"></a>
## vio-lc/hortimulti/strawberry03/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry03/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry03/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry03/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `declare_window_gated_export_start_and_forward_only_loop_correction`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-lc-hortimulti-strawberry03-mast3r-fusion"></a>
## vio-lc/hortimulti/strawberry03/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/hortimulti/strawberry03/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/hortimulti/strawberry03/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/hortimulti/strawberry03/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `declare_keyframe_only_global_trajectory_claim`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:missing_repetition`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`.

<a id="vio-lc-euroc-mav-mh-01-easy-orbslam3"></a>
## vio-lc/euroc_mav/MH_01_easy/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_01_easy/orbslam3/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_01_easy/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_01_easy/orbslam3/run3) | blocked | success | 0 | yes |

Group `8d7d796cd40b271ccd5508b44ea2cd3398df046ade49c489747bc38f543e5902`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-01-easy-okvis2"></a>
## vio-lc/euroc_mav/MH_01_easy/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_01_easy/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_01_easy/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_01_easy/okvis2/run3) | verified | success | 0 | yes |

Group `eafbd5f7849f577c75340b82a26bcce13c7f7ee5f42533bc4da619a243b94558`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-01-easy-okvis2x"></a>
## vio-lc/euroc_mav/MH_01_easy/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_01_easy/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_01_easy/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_01_easy/okvis2x/run3) | verified | success | 0 | yes |

Group `f3a3e0f0da35a14d00caf1e5c70f5fd847da0d07de48013ac98639860f8423f5`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-01-easy-airslam"></a>
## vio-lc/euroc_mav/MH_01_easy/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run4](../results/vio-lc/euroc_mav/MH_01_easy/airslam/run4) | verified | success | 0 | yes |
| 2 | [run5](../results/vio-lc/euroc_mav/MH_01_easy/airslam/run5) | verified | success | 0 | yes |
| 3 | [run6](../results/vio-lc/euroc_mav/MH_01_easy/airslam/run6) | verified | success | 0 | yes |

Group `16f70d81329ca61df95c11200ad23e478e80e4a3c87c9b48e20656706720ccd8`: 3 verified / 3 recorded; `run4`, `run5`, `run6`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `final_offline_map_refinement_accuracy_not_causal_online_trajectory`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-01-easy-cuvslam"></a>
## vio-lc/euroc_mav/MH_01_easy/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_01_easy/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_01_easy/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_01_easy/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-01-easy-svo-pro"></a>
## vio-lc/euroc_mav/MH_01_easy/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_01_easy/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_01_easy/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_01_easy/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-01-easy-mast3r-fusion"></a>
## vio-lc/euroc_mav/MH_01_easy/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_01_easy/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_01_easy/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_01_easy/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-03-medium-orbslam3"></a>
## vio-lc/euroc_mav/MH_03_medium/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_03_medium/orbslam3/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_03_medium/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_03_medium/orbslam3/run3) | blocked | success | 0 | yes |

Group `8d7d796cd40b271ccd5508b44ea2cd3398df046ade49c489747bc38f543e5902`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `export_coverage_below_95_percent_no_clean_success_tick`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-03-medium-okvis2"></a>
## vio-lc/euroc_mav/MH_03_medium/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_03_medium/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_03_medium/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_03_medium/okvis2/run3) | verified | success | 0 | yes |

Group `7e5f117ad7f3ca70ed9bc886407adf93fbedc678c7f93f20ff46a3567facdcc2`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-03-medium-okvis2x"></a>
## vio-lc/euroc_mav/MH_03_medium/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_03_medium/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_03_medium/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_03_medium/okvis2x/run3) | verified | success | 0 | yes |

Group `e290a9daa25704c60b8a69dfd1fc1697fc8b5fc11c805694ca42ddef491e23d8`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-03-medium-airslam"></a>
## vio-lc/euroc_mav/MH_03_medium/airslam

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run4](../results/vio-lc/euroc_mav/MH_03_medium/airslam/run4) | verified | success | 0 | yes |
| 2 | [run5](../results/vio-lc/euroc_mav/MH_03_medium/airslam/run5) | verified | success | 0 | yes |
| 3 | [run6](../results/vio-lc/euroc_mav/MH_03_medium/airslam/run6) | verified | success | 0 | yes |

Group `16f70d81329ca61df95c11200ad23e478e80e4a3c87c9b48e20656706720ccd8`: 3 verified / 3 recorded; `run4`, `run5`, `run6`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `final_offline_map_refinement_accuracy_not_causal_online_trajectory`, `no_measured_processing_rate_or_realtime_deadline_claim`, `sparse_keyframe_accuracy_only`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-03-medium-cuvslam"></a>
## vio-lc/euroc_mav/MH_03_medium/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_03_medium/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_03_medium/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_03_medium/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-03-medium-svo-pro"></a>
## vio-lc/euroc_mav/MH_03_medium/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_03_medium/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_03_medium/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_03_medium/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-03-medium-mast3r-fusion"></a>
## vio-lc/euroc_mav/MH_03_medium/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_03_medium/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_03_medium/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_03_medium/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-05-difficult-orbslam3"></a>
## vio-lc/euroc_mav/MH_05_difficult/orbslam3

**A3/E3/S3/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_05_difficult/orbslam3/run1) | blocked | success | 0 | yes |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_05_difficult/orbslam3/run2) | blocked | success | 0 | yes |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_05_difficult/orbslam3/run3) | blocked | success | 0 | yes |

Group `8d7d796cd40b271ccd5508b44ea2cd3398df046ade49c489747bc38f543e5902`: 0 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: `historical_orb_library_identity_unverified`.
Review blockers: `historical_orb_loaded_library_abi_unknown`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `historical_orb_loaded_library_abi_unknown`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 required_rerun; readiness unverified; r3 required_rerun; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-05-difficult-okvis2"></a>
## vio-lc/euroc_mav/MH_05_difficult/okvis2

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_05_difficult/okvis2/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_05_difficult/okvis2/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_05_difficult/okvis2/run3) | verified | success | 0 | yes |

Group `b6a155a9dde43282e7322adfe80fd5b29d08ce9b0cf6a32cea3e55067ac1d253`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-05-difficult-okvis2x"></a>
## vio-lc/euroc_mav/MH_05_difficult/okvis2x

**A3/E3/S3/F0**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_05_difficult/okvis2x/run1) | verified | success | 0 | yes |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_05_difficult/okvis2x/run2) | verified | success | 0 | yes |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_05_difficult/okvis2x/run3) | verified | success | 0 | yes |

Group `b6d94e0ea3940f948fd4afbf0c332f166f908588a21352a7c069a774bc77b20f`: 3 verified / 3 recorded; `run1`, `run2`, `run3`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-05-difficult-airslam"></a>
## vio-lc/euroc_mav/MH_05_difficult/airslam

**A3/E2/S2/F1**; verified completed groups: 3. Verified N=3: yes.

Cell next-action display: no new action required by this plan.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run4](../results/vio-lc/euroc_mav/MH_05_difficult/airslam/run4) | verified | failure_without_final_trajectory | 139 | no |
| 2 | [run5](../results/vio-lc/euroc_mav/MH_05_difficult/airslam/run5) | verified | success | 0 | yes |
| 3 | [run6](../results/vio-lc/euroc_mav/MH_05_difficult/airslam/run6) | verified | success | 0 | yes |

Group `16f70d81329ca61df95c11200ad23e478e80e4a3c87c9b48e20656706720ccd8`: 3 verified / 3 recorded; `run4`, `run5`, `run6`.

Confirmed setup findings: none.
Review blockers: none.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `final_offline_map_refinement_accuracy_not_causal_online_trajectory`, `intermediate_odometry_is_diagnostic_only`, `native_junction_database_segfault_root_cause_unresolved`, `no_final_vio_lc_trajectory_no_accuracy_claim`, `no_measured_processing_rate_or_realtime_deadline_claim`, `retain_failure_in_attempt_denominator`, `sparse_keyframe_accuracy_only`.
Native failure evidence r4: `{"last_log_message": "Build junction database...", "native_exit": -11, "root_cause": "not established; no final trajectory saved; no forced signal requested", "stage": "refinement", "wrapper_exit": 139}`.

Future plan `future-n3-five-modes`: r1 reusable; retained observation; r2 reusable; retained observation; r3 reusable; retained observation.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-05-difficult-cuvslam"></a>
## vio-lc/euroc_mav/MH_05_difficult/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_05_difficult/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_05_difficult/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_05_difficult/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-05-difficult-svo-pro"></a>
## vio-lc/euroc_mav/MH_05_difficult/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_05_difficult/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_05_difficult/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_05_difficult/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-euroc-mav-mh-05-difficult-mast3r-fusion"></a>
## vio-lc/euroc_mav/MH_05_difficult/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/euroc_mav/MH_05_difficult/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/euroc_mav/MH_05_difficult/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/euroc_mav/MH_05_difficult/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-zed2i-field1-110426-full-10fps-q90-orbslam3"></a>
## vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3

**A1/E0/S0/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run1) | invalid_setup | failure_without_final_trajectory | 139 | no |
| 2 | [run2](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/orbslam3/run3) | not_executed | not_attempted | unknown | no |

Group `39cb58e90d66a78bfe3af9ea74a9ea22f6e61e3f631dfb5f9281ffc76d4bfc37`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `zed_factory_camera_imu_rotation_omitted`.
Review blockers: `missing_repetition`, `zed_factory_camera_imu_rotation_omitted`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `retain_failure_in_attempt_denominator`, `serial_specific_imu_rotation_and_timing_unverified`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.
Native failure evidence r1: `{"line": 65, "text": "2.695 Segmentation fault (core dumped)"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-zed2i-field1-110426-full-10fps-q90-okvis2"></a>
## vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2

**A1/E1/S1/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2/run3) | not_executed | not_attempted | unknown | no |

Group `57d6f2cbbf2343da790f5f8cdc639428406f2749d5ddef20e351729069d21296`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `zed_factory_camera_imu_rotation_omitted`.
Review blockers: `missing_repetition`, `zed_factory_camera_imu_rotation_omitted`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-zed2i-field1-110426-full-10fps-q90-okvis2x"></a>
## vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x

**A1/E1/S1/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/okvis2x/run3) | not_executed | not_attempted | unknown | no |

Group `cfa8b53ce21e2598efc7ace17dc4990b0d06bf4db259c250649564e94956c859`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `zed_factory_camera_imu_rotation_omitted`.
Review blockers: `missing_repetition`, `zed_factory_camera_imu_rotation_omitted`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-zed2i-field1-110426-full-10fps-q90-airslam"></a>
## vio-lc/zed2i/field1_110426_full_10fps_q90/airslam

**A1/E1/S1/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/airslam/run1) | invalid_setup | success | 0 | yes |
| 2 | [run2](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/airslam/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/airslam/run3) | not_executed | not_attempted | unknown | no |

Group `a90691b7ed10ce7c85f6ffed47b456dfbd8084f5dfeec93d84154943db08a336`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `zed_factory_camera_imu_rotation_omitted`.
Review blockers: `missing_repetition`, `zed_factory_camera_imu_rotation_omitted`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `approved_gnss_spike_mask_gaps_preserved_rtk_float_retained_fixed_only_sensitivity`, `historical_profile_accuracy_not_bitwise_build_reproduction`, `no_measured_processing_rate_or_realtime_deadline_claim`, `no_rotation_or_full_relative_pose_accuracy_claim`, `nominal_3d_position_reference_1m_height_level_platform_not_surveyed_6dof`, `unmeasured_field_clock_zero_offset_with_frozen_sensitivity`, `zed_camera_rtk_clock_unmeasured_zero_offset_with_disclosed_sampled_sensitivity`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-zed2i-field1-110426-full-10fps-q90-cuvslam"></a>
## vio-lc/zed2i/field1_110426_full_10fps_q90/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-zed2i-field1-110426-full-10fps-q90-svo-pro"></a>
## vio-lc/zed2i/field1_110426_full_10fps_q90/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-zed2i-field1-110426-full-10fps-q90-mast3r-fusion"></a>
## vio-lc/zed2i/field1_110426_full_10fps_q90/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `zed-coherent-n3-20261002-main-integration`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/zed2i/field1_110426_full_10fps_q90/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

Future plan `zed-coherent-n3-20261002-main-integration`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq04-orbslam3"></a>
## vio-lc/citrusfarm/seq04/orbslam3

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq04/orbslam3/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq04/orbslam3/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq04/orbslam3/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq04-okvis2"></a>
## vio-lc/citrusfarm/seq04/okvis2

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq04/okvis2/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq04/okvis2/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq04/okvis2/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq04-okvis2x"></a>
## vio-lc/citrusfarm/seq04/okvis2x

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq04/okvis2x/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq04/okvis2x/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq04/okvis2x/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq04-airslam"></a>
## vio-lc/citrusfarm/seq04/airslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq04/airslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq04/airslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq04/airslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq04-cuvslam"></a>
## vio-lc/citrusfarm/seq04/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq04/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq04/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq04/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq04-svo-pro"></a>
## vio-lc/citrusfarm/seq04/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq04/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq04/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq04/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq04-mast3r-fusion"></a>
## vio-lc/citrusfarm/seq04/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq04/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq04/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq04/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq07-orbslam3"></a>
## vio-lc/citrusfarm/seq07/orbslam3

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq07/orbslam3/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq07/orbslam3/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq07/orbslam3/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq07-okvis2"></a>
## vio-lc/citrusfarm/seq07/okvis2

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq07/okvis2/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq07/okvis2/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq07/okvis2/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq07-okvis2x"></a>
## vio-lc/citrusfarm/seq07/okvis2x

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq07/okvis2x/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq07/okvis2x/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq07/okvis2x/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq07-airslam"></a>
## vio-lc/citrusfarm/seq07/airslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq07/airslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq07/airslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq07/airslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq07-cuvslam"></a>
## vio-lc/citrusfarm/seq07/cuvslam

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq07/cuvslam/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq07/cuvslam/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq07/cuvslam/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq07-svo-pro"></a>
## vio-lc/citrusfarm/seq07/svo_pro

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq07/svo_pro/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq07/svo_pro/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq07/svo_pro/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="vio-lc-citrusfarm-seq07-mast3r-fusion"></a>
## vio-lc/citrusfarm/seq07/mast3r_fusion

**A0/E0/S0/F0**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 3 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/vio-lc/citrusfarm/seq07/mast3r_fusion/run1) | blocked | not_attempted | unknown | no |
| 2 | [run2](../results/vio-lc/citrusfarm/seq07/mast3r_fusion/run2) | blocked | not_attempted | unknown | no |
| 3 | [run3](../results/vio-lc/citrusfarm/seq07/mast3r_fusion/run3) | blocked | not_attempted | unknown | no |


Confirmed setup findings: none.
Review blockers: `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `configuration_choices_are_not_evidence_of_algorithm_optimality`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 missing; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: none.

<a id="gnss-vio-rosariov2-sequence1-cifasis-gnss-si"></a>
## gnss-vio/rosariov2/sequence1/cifasis_gnss_si

**A1/E1/S0/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence1/cifasis_gnss_si/run1) | invalid_setup | failure_with_saved_trajectory | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence1/cifasis_gnss_si/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence1/cifasis_gnss_si/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence1/cifasis_gnss_si/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `rosario_v1_antenna_lever_arm_used_on_v2`.
Review blockers: `estimate_frame_unverified: output frame not established for cifasis_gnss_si`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`, `rosario_v1_antenna_lever_arm_used_on_v2`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.
Native failure evidence r1: `{"line": 287, "text": "terminate called without an active exception"}`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for cifasis_gnss_si`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `resolve_or_document_claim_limit:rosario_v1_antenna_lever_arm_used_on_v2`, `use_dataset_session_specific_imu_to_selected_gnss_antenna_transform_and_verify_native_loaded_values`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-rosariov2-sequence1-okvis2x"></a>
## gnss-vio/rosariov2/sequence1/okvis2x

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence1/okvis2x/run1) | invalid_setup | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence1/okvis2x/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence1/okvis2x/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence1/okvis2x/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `gnss_zero_antenna_lever_arm_in_native_log`.
Review blockers: `estimate_frame_unverified: expected one saved estimator_config, found 0`, `gnss_reference_independence_and_global_frame_not_established`, `gnss_zero_antenna_lever_arm_in_native_log`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `resolve_or_document_claim_limit:estimate_frame_unverified: expected one saved estimator_config, found 0`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:gnss_zero_antenna_lever_arm_in_native_log`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `use_dataset_session_specific_imu_to_selected_gnss_antenna_transform_and_verify_native_loaded_values`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-rosariov2-sequence1-openvins-gps"></a>
## gnss-vio/rosariov2/sequence1/openvins_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence1/openvins_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence1/openvins_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence1/openvins_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence1/openvins_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for openvins_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `replace_identity_imu_camera_profile_with_consistent_matched_camera_model`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for openvins_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_enu_heading_initialization_and_imu_body_alias`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-rosariov2-sequence1-rtabmap-gps"></a>
## gnss-vio/rosariov2/sequence1/rtabmap_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence1/rtabmap_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence1/rtabmap_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence1/rtabmap_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence1/rtabmap_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for rtabmap_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for rtabmap_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-rosariov2-sequence1-vins-fusion-gps"></a>
## gnss-vio/rosariov2/sequence1/vins_fusion_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence1/vins_fusion_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence1/vins_fusion_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence1/vins_fusion_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence1/vins_fusion_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for vins_fusion_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `implement_and_validate_antenna_lever_in_global_position_factor`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for vins_fusion_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-rosariov2-sequence5-cifasis-gnss-si"></a>
## gnss-vio/rosariov2/sequence5/cifasis_gnss_si

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence5/cifasis_gnss_si/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence5/cifasis_gnss_si/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence5/cifasis_gnss_si/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence5/cifasis_gnss_si/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for cifasis_gnss_si`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for cifasis_gnss_si`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-rosariov2-sequence5-okvis2x"></a>
## gnss-vio/rosariov2/sequence5/okvis2x

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence5/okvis2x/run1) | invalid_setup | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence5/okvis2x/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence5/okvis2x/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence5/okvis2x/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `gnss_zero_antenna_lever_arm_in_native_log`.
Review blockers: `estimate_frame_unverified: expected one saved estimator_config, found 0`, `gnss_reference_independence_and_global_frame_not_established`, `gnss_zero_antenna_lever_arm_in_native_log`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `resolve_or_document_claim_limit:estimate_frame_unverified: expected one saved estimator_config, found 0`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:gnss_zero_antenna_lever_arm_in_native_log`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `use_dataset_session_specific_imu_to_selected_gnss_antenna_transform_and_verify_native_loaded_values`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-rosariov2-sequence5-openvins-gps"></a>
## gnss-vio/rosariov2/sequence5/openvins_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence5/openvins_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence5/openvins_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence5/openvins_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence5/openvins_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for openvins_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `replace_identity_imu_camera_profile_with_consistent_matched_camera_model`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for openvins_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_enu_heading_initialization_and_imu_body_alias`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-rosariov2-sequence5-rtabmap-gps"></a>
## gnss-vio/rosariov2/sequence5/rtabmap_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence5/rtabmap_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence5/rtabmap_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence5/rtabmap_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence5/rtabmap_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for rtabmap_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for rtabmap_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-rosariov2-sequence5-vins-fusion-gps"></a>
## gnss-vio/rosariov2/sequence5/vins_fusion_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/rosariov2/sequence5/vins_fusion_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/rosariov2/sequence5/vins_fusion_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/rosariov2/sequence5/vins_fusion_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/rosariov2/sequence5/vins_fusion_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for vins_fusion_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `fused_stereo_imu_ppk_reference_not_independent_ground_truth`, `no_measured_processing_rate_or_realtime_deadline_claim`, `rosario_authors_orb_camera_model_accepted_by_decision_20261003_fxb_0p5_to_1pct_below_kalibr`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `implement_and_validate_antenna_lever_in_global_position_factor`, `reconcile_unchanged_recorded_images_with_author_virtual_projection_and_baseline`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for vins_fusion_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry02-cifasis-gnss-si"></a>
## gnss-vio/hortimulti/strawberry02/cifasis_gnss_si

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry02/cifasis_gnss_si/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry02/cifasis_gnss_si/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry02/cifasis_gnss_si/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry02/cifasis_gnss_si/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for cifasis_gnss_si`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for cifasis_gnss_si`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry02-okvis2x"></a>
## gnss-vio/hortimulti/strawberry02/okvis2x

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry02/okvis2x/run1) | invalid_setup | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry02/okvis2x/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry02/okvis2x/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry02/okvis2x/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `gnss_zero_antenna_lever_arm_in_native_log`.
Review blockers: `estimate_frame_unverified: expected one saved estimator_config, found 0`, `gnss_reference_independence_and_global_frame_not_established`, `gnss_zero_antenna_lever_arm_in_native_log`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: expected one saved estimator_config, found 0`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:gnss_zero_antenna_lever_arm_in_native_log`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `use_dataset_session_specific_imu_to_selected_gnss_antenna_transform_and_verify_native_loaded_values`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry02-openvins-gps"></a>
## gnss-vio/hortimulti/strawberry02/openvins_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry02/openvins_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry02/openvins_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry02/openvins_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry02/openvins_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for openvins_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for openvins_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_enu_heading_initialization_and_imu_body_alias`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry02-rtabmap-gps"></a>
## gnss-vio/hortimulti/strawberry02/rtabmap_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry02/rtabmap_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry02/rtabmap_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry02/rtabmap_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry02/rtabmap_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for rtabmap_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for rtabmap_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry02-vins-fusion-gps"></a>
## gnss-vio/hortimulti/strawberry02/vins_fusion_gps

**A1/E1/S0/F1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run1) | blocked | failure_invalid_export | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry02/vins_fusion_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for vins_fusion_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `implement_and_validate_antenna_lever_in_global_position_factor`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for vins_fusion_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry03-cifasis-gnss-si"></a>
## gnss-vio/hortimulti/strawberry03/cifasis_gnss_si

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry03/cifasis_gnss_si/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry03/cifasis_gnss_si/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry03/cifasis_gnss_si/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry03/cifasis_gnss_si/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for cifasis_gnss_si`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for cifasis_gnss_si`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry03-okvis2x"></a>
## gnss-vio/hortimulti/strawberry03/okvis2x

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: 🔴 rerun not ready; next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry03/okvis2x/run1) | invalid_setup | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry03/okvis2x/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry03/okvis2x/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry03/okvis2x/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: `gnss_zero_antenna_lever_arm_in_native_log`.
Review blockers: `estimate_frame_unverified: expected one saved estimator_config, found 0`, `gnss_reference_independence_and_global_frame_not_established`, `gnss_zero_antenna_lever_arm_in_native_log`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 required_rerun; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `keep_original_invalid_configuration_cohort_separate`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: expected one saved estimator_config, found 0`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:gnss_zero_antenna_lever_arm_in_native_log`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `use_dataset_session_specific_imu_to_selected_gnss_antenna_transform_and_verify_native_loaded_values`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry03-openvins-gps"></a>
## gnss-vio/hortimulti/strawberry03/openvins_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry03/openvins_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry03/openvins_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry03/openvins_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry03/openvins_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for openvins_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for openvins_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `validate_enu_heading_initialization_and_imu_body_alias`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry03-rtabmap-gps"></a>
## gnss-vio/hortimulti/strawberry03/rtabmap_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry03/rtabmap_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry03/rtabmap_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry03/rtabmap_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry03/rtabmap_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for rtabmap_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for rtabmap_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.

<a id="gnss-vio-hortimulti-strawberry03-vins-fusion-gps"></a>
## gnss-vio/hortimulti/strawberry03/vins_fusion_gps

**A1/E1/S0/F0/U1**; verified completed groups: 0. Verified N=3: no.

Cell next-action display: next: missing 2 not ready.
Selected plan: `future-n3-five-modes`.

| Logical repetition | Physical run / evidence | Reviewed attempt | Observed outcome | Exit | Evaluated |
|---|---|---|---|---|---|
| 1 | [run1](../results/gnss-vio/hortimulti/strawberry03/vins_fusion_gps/run1) | blocked | unknown | unknown | yes |
| 2 | [run2](../results/gnss-vio/hortimulti/strawberry03/vins_fusion_gps/run2) | not_executed | not_attempted | unknown | no |
| 3 | [run3](../results/gnss-vio/hortimulti/strawberry03/vins_fusion_gps/run3) | not_executed | not_attempted | unknown | no |

Group `unverified:results/gnss-vio/hortimulti/strawberry03/vins_fusion_gps/run1`: 0 verified / 1 recorded; `run1`.

Confirmed setup findings: none.
Review blockers: `estimate_frame_unverified: output frame not established for vins_fusion_gps`, `gnss_reference_independence_and_global_frame_not_established`, `historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `horti_exact_reference_origin_timing_unresolved`, `horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `missing_repetition`.
Claim limits: `accuracy_conditional_on_observed_exports_and_reference_support`, `no_measured_processing_rate_or_realtime_deadline_claim`.

Future plan `future-n3-five-modes`: r1 blocked; readiness unverified; r2 missing; readiness unverified; r3 missing; readiness unverified.
Prerequisites: `complete_cell_configuration_input_and_claim_review`, `implement_and_validate_antenna_lever_in_global_position_factor`, `link_february_reference_generation_origin_and_clock_to_each_saved_session`, `resolve_or_document_claim_limit:estimate_frame_unverified: output frame not established for vins_fusion_gps`, `resolve_or_document_claim_limit:gnss_reference_independence_and_global_frame_not_established`, `resolve_or_document_claim_limit:historical_effective_gnss_input_covariance_antenna_and_fusion_output_unverified`, `resolve_or_document_claim_limit:horti_february_reference_generation_origin_and_timestamp_linkage_unresolved`, `resolve_or_document_claim_limit:missing_repetition`, `saved_result_has_unresolved_scientific_evidence`, `validate_camera_imu_time_compensation_and_output_clock_in_native_path`, `verify_effective_native_config_after_runtime_materialization`, `verify_gnss_input_variant_covariance_and_antenna_frame`, `verify_native_build_source_linkage_and_loaded_runtime_dependency_closure`, `verify_reference_independence_and_fusion_output`.
