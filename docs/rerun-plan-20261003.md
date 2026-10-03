# What needs rerunning, and why (3 October 2026)

Written by Claude from the reviewed evidence in main (`7c3834e`) plus three corrections
made on 3 October. One place for the team to see which non-GNSS cells need new runs,
which only need a review decision, and which decisions are already made. GNSS-VIO is out
of scope here.

The matrices in `TODO.md` are generated from reviewed per-attempt findings. The
corrections below are recorded the same way (`docs/campaigns/rerun-findings-20261003.json`
plus `scripts/campaign/protocol_findings.py`), so they appear in the matrices the next
time evaluations, plans and `TODO.md` are regenerated in main. Until then, the current
matrices understate the AirSLAM, Voxel-SVIO and Basalt cells listed in section 2.

## 1. Decisions taken (3 October)

| Question | Decision |
|---|---|
| Rosario camera model | Accept the authors' ORB-SLAM3 evaluation profile already used by every Rosario row: recorded `image_rect_raw` pixels, fx = fy = 648.862 px, baseline 0.0497337 m. This closes the "camera model" review item **without reruns** (no row used anything else). |
| Rosario camera–IMU transform | The authors' published Kalibr result, **0.365° and 33.9 mm**, for every algorithm, OpenVINS included. |
| Rosario camera–IMU time offset | 0, as in every existing Rosario row and the authors' ORB-SLAM3 setup (ORB-SLAM3 has no offset parameter). Kalibr's 4.1 ms is disclosed, not applied. |
| AirSLAM saves keyframes only | How AirSLAM works; reported with a disclosure, not a defect. |
| OKVIS2-X VO-LC and VIO-LC: the final adjustment also optimises the camera extrinsics (`do_extrinsics_final_ba: true`; the authors' EuRoC config keeps it off) | **Kept as run; does not invalidate any run.** Disclosed as a configuration difference (main already attaches the claim limit `final_ba_enabled_with_extrinsic_optimization` to these cells). This also answers the planning item "freeze and label the final bundle adjustment and extrinsic optimisation policy". Earlier analysis found the stereo baseline shrinks by 1–9 % in the final adjustment and per-run scale error tracks it; worth stating next to the OKVIS2-X loop-closure numbers. Can be revisited later. |
| Results that fail because of the algorithm | Kept in the tables as measured outcomes. |

### Where 0.37° and 0.94° come from

| Value | Source |
|---|---|
| **0.365°, 33.9 mm** | The authors' Kalibr archive (`aprilgrid_calib_2-results-imucam.txt`, reprojection error 0.24 px), the IJRR paper ([Table 8](https://arxiv.org/html/2508.21635v1), infra1 → IMU), the authors' URDF, and their ORB-SLAM3 evaluation config. All four agree. |
| **0.94°, 34.7 mm** | Only the OpenVINS example config in the authors' GitHub repository (`data/evaluation/open-vins_imucam_rosariov2.yaml`, commit `82115db`). It is 0.74° and 7.5 mm from the Kalibr result; the paper does not explain it. Its time shift is 6.5 ms. |

There is no comparison of the two on the same algorithm, in the paper or here. The paper's
numbers (ORB-SLAM3 5.17 m and OpenVINS 2.30 m on sequence 1) come from different
algorithms and say nothing about which calibration is better. Choosing a calibration by
which one scores better would tune on the test data, so it is not done. Using 0.94° for
OpenVINS alone would give one algorithm a different sensor than all others.

A calibration of our own is not possible from the published material: the authors'
archives contain Kalibr results only, not the calibration recording. Estimating the
transform from the field sequences themselves (online calibration) is weakly observable
on a slow ground vehicle and would again fit the calibration to the test data.

## 2. Corrections recorded on 3 October (missing from the earlier reviews)

| Cells | Attempts | What is wrong | Why it was yellow |
|---|---|---|---|
| AirSLAM Rosario VIO and VIO-LC, seq1 and seq5 (4 cells) | 12 | The saved AirSLAM camera file sets the left camera to IMU transform to identity ("cam0 IS the body frame"). AirSLAM links IMU and camera poses through it (`src/airslam/src/frame.cc`). This is the same defect that makes the Basalt, OpenVINS and Voxel-SVIO Rosario VIO cells red; the review document rejects exactly this "IMU is the camera body" argument for those. AirSLAM's EuRoC file uses the real transform. | The 1 October list and the finding code covered only Basalt, OpenVINS and Voxel-SVIO; the 2 October candidate review grouped AirSLAM with the camera-model cases. No document gives a reason to exempt it. |
| Voxel-SVIO HortiMulti VIO, str02 and str03 (2 cells) | 6 | The attempts (11 September) ran Voxel-SVIO's original initializer, which the 2 October native review showed keeps the camera–IMU offset at zero although the config declares 9.16 ms. Propagation used the offset. Repaired in checkpoint `3be9197`. | The HortiMulti timing list was written on 1 October, when the declared offset was assumed to be applied; it was not updated after the 2 October discovery. |
| Basalt HortiMulti VIO, str02 and str03 (2 cells) | 6 | The saved calibration uses IMU noise 0.5 (accelerometer) and 0.006 (gyroscope) from a July tuning commit (`388767c`) with no recorded basis; the documented HortiMulti profile is 0.110 / 0.0035. The time offset question is open as well: upstream Basalt has its offset code commented out and the installed binary was never linked to that source. | The timing question was deliberately left open (reasoned). The noise values were missed: the August configuration clean-up removed Basalt's other HortiMulti tuning but not these. One rerun with the current runner settles both, because it applies the offset to the IMU input itself. |

## 3. All cells that need new runs (non-GNSS)

Counts are physical runs to execute; failures stay in the denominator as before.

| Group | Cells | Runs | Status |
|---|---|---|---|
| HortiMulti 9.16 ms offset not applied: ORB-SLAM3, AirSLAM, OKVIS2, OKVIS2-X, VIO and VIO-LC (ORB-SLAM3 VIO-LC also the rectified-IMU transform) | 16 | 48 | Confirmed, in main's plans |
| Rosario identity camera–IMU: Basalt, OpenVINS, Voxel-SVIO VIO | 6 | 18 (14 replacements, 4 missing) | Confirmed, in main's plans; **profiles must follow section 1** |
| Rosario identity camera–IMU: AirSLAM VIO and VIO-LC | 4 | 12 | Added 3 October |
| Voxel-SVIO HortiMulti VIO (initializer offset) | 2 | 6 | Added 3 October |
| Basalt HortiMulti VIO (noise, offset) | 2 | 6 | Added 3 October |
| ZED factory camera–IMU rotation: AirSLAM, Basalt, OpenVINS, Voxel-SVIO VIO | 4 | 12 | Running in the 3 October ZED batch |
| ZED VIO repetitions 2–3: ORB-SLAM3, OKVIS2, OKVIS2-X | 3 | 6 | Running in the 3 October ZED batch |
| ZED factory camera–IMU rotation: AirSLAM, OKVIS2, OKVIS2-X, ORB-SLAM3 VIO-LC | 4 | 12 | Confirmed, in main's ZED plan |
| ORB-SLAM3 ZED VO and VO-LC (camera rate 15 → 10 Hz) | 2 | 6 | Confirmed, in main's ZED plan |
| ORB-SLAM3 outside ZED: every historical run used the mismatched ORB-SLAM3/g2o libraries (EuRoC, Rosario, HortiMulti; VO, VO-LC, VIO, VIO-LC) | 24 more (28 incl. the 4 HortiMulti cells above) | 72 | Fix exists in the runner for all datasets; replacements **not yet in main's plans** |
| OpenVINS EuRoC VIO: three runs split over two implementation groups | 3 | 9 | Not yet in main's plans |

Missing repetitions that are not reruns (for example OpenVINS HortiMulti VIO r2–r3, ZED
VO-LC group completions) stay as listed in main's plans.

### Rosario rerun profiles must match the decisions

The four prepared candidate bundles in `configs/candidates/rosario-vio-20261002/`
(`basalt-kalibr`, `voxel-kalibr`, `openvins-kalibr`, `openvins-author`) use the Kalibr or the
author-OpenVINS **camera model** (fx 645.4 / fy 648.6 with distortion) and Kalibr's 4.1 ms
time shift. Every other Rosario row uses the authors' ORB-SLAM3 camera model and no shift.
Rerunning with those bundles would make the replacement rows differ from all other rows in
camera model and timing. The Rosario reruns need profiles with: the ORB-SLAM3 camera model
(fx = fy = 648.862 px, baseline 0.0497337 m, no distortion), the Kalibr camera–IMU transform
(0.365°, 33.9 mm), time offset 0, and the published IMU noise. This is exactly
`configs/sensors/rosariov2.json` on the `new-algorithms` branch.

## 4. Cells that need a review decision, not runs

| Item | Cells | What closes it |
|---|---|---|
| Rosario camera model | all Rosario cells | Closed by the decision in section 1; no reruns, no re-evaluation. |
| HortiMulti reference origin and clock (str02 `TagMap/base_link`, str03 `odom/odom_mapping`) | all HortiMulti cells | Answer from the HortiMulti authors, then re-evaluation of the saved trajectories (reference side; the estimates do not change). |
| Rosario reference is MINS fused from the same camera and IMU | all Rosario cells | Disclosure. |
| ZED reference (lever arm, heading, altitude, clock) | all ZED cells | Disclosure ("nominal position"). |
| AirSLAM keyframe-only export | AirSLAM cells | Disclosure (decided). |
| Per-attempt claim review in the acceptance ledger | every cell | Required for every ✅, as for all existing ticks. |

## 5. Rosario after the decisions

| Mode | Waiting only on the claim review (were yellow for "camera model") | Need reruns |
|---|---|---|
| VO | Basalt, MAC-VO, AirSLAM, DPVO, OKVIS2, OKVIS2-X, OV2SLAM (14 cells) | ORB-SLAM3 (libraries) |
| VO-LC | DPV-SLAM, OKVIS2, OKVIS2-X, AirSLAM, OV2SLAM (10 cells); OKVIS2-X seq1 also has its runs in two implementation groups | ORB-SLAM3 (libraries) |
| VIO | OKVIS2, OKVIS2-X (4 cells) | Basalt, OpenVINS, Voxel-SVIO, AirSLAM (identity transform); ORB-SLAM3 (libraries) |
| VIO-LC | OKVIS2, OKVIS2-X (4 cells) | AirSLAM (identity transform); ORB-SLAM3 (libraries) |

So, with the camera model and 0.365° accepted, 32 Rosario cells outside ORB-SLAM3 can
become ✅ after the claim review; the 10 inertial cells that used the identity transform
need their reruns first.
