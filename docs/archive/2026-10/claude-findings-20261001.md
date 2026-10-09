# Independent findings (Claude) — 2026-10-01

Read-only review of the server campaign, made in parallel with the reference review in
`docs/reference-review-20261001.md`. This file is the only thing written to the workspace.
No estimator was run, nothing was re-evaluated in place, no result or config was changed.

Everything below is derived from (a) the per-run `provenance/` snapshots and logs saved inside
`results/<mode>/<dataset>/<seq>/<algo>/runN/`, (b) the five root `benchmark-*.csv` files at commit
`e0ee49b`, and (c) author material: `CIFASIS/rosariov2` at `82115db` (2026-09-13), `shuoyuanxu/HortiMulti`
at `6df2c26` (2026-08-05), and the HortiMulti S3 files for `Feb2026/Strawberry` (last modified 2026-08-01).

Numbers I computed myself are stated as such. Where I rely on the other review, I say so.

---

## 1. Answer in one table

200 non-GNSS cells (600 planned repetitions, 545 evaluated) plus 20 GNSS cells.

| Category | Cells | Existing evaluations | Runs to execute | Serial hours (historical durations) |
|---|---:|---:|---:|---:|
| **Keep as is** — no rerun, no re-evaluation | 103 | 309 | 0 | 0 |
| **Re-evaluate only** — saved trajectories are fine, reference handling changes | 39 | 117 | 0 | minutes |
| **Rerun** — estimator-side setting or calibration was wrong | 38 | 105 | 114 | ~44 |
| **New runs** — repetitions missing or crashed at startup | 20 | 14 | 46 | ~46 |
| **GNSS-VIO** — no server run exists | 20 | 19 (old machines) | 60 | ~13 (rough) |

Yellow and orange in `TODO.md` therefore mostly do **not** mean rerun: 142 of 200 non-GNSS cells
need no estimation at all. The matrices in the `TODO.md` layout are in section 1b, with a short explanation of every code; the full evidence is in sections 2 to 4.

Hours are `mean historical duration × runs` per cell; cells with no completed run use the same algorithm
on the same sequence in another mode. They exclude diagnostics and evaluation.

---

## 1b. Findings matrix (same layout as `TODO.md`)

Built from the root CSVs at commit `e0ee49b`. `N` is the number of evaluated repetitions that exist today.

Legend per cell: ✅ keep, nothing to do | 🟠 keep, with the named limitation stated in the paper |
🔄 re-evaluate the saved runs only, no estimation | 🔁 rerun all three, estimator-side defect |
⬜ new runs needed, repetitions missing or crashed | ❓ keep for now, open question | ➖ excluded, unchanged from `TODO.md`.

Counts over the 200 non-GNSS cells: ✅ 68, 🟠 31, ❓ 4 (103 keep) · 🔄 39 · 🔁 38 · ⬜ 20.
The codes (`R1`–`R6`, `N1`–`N3`, `E1`–`E2`, `Q1`) are explained directly below the matrices.
"then E1/E2" means the new runs must be evaluated with the corrected HortiMulti reference.

### VO (no IMU, no loop closure) - `results/vo/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | ⬜ N=0; crash at start; run 3: N1 | ⬜ N=0; crash at start; run 3: N1 | ⬜ N=0; crash at start; run 3: N1; then E1 | 🔄 N=3; re-evaluate: E2; exit 139 after save | ✅ N=3; keep | 🟠 N=3; keep; exit 139 after save | ✅ N=3; keep | 🔁 N=3; rerun: R1 |
| Basalt | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep |
| MAC-VO | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep |
| AirSLAM | ❓ N=3; keep, check Q1; keyframes only | ❓ N=3; keep, check Q1; keyframes only | 🔄 N=3; re-evaluate: E1; keyframes only | 🔄 N=3; re-evaluate: E2; keyframes only | 🟠 N=3; keep; keyframes only | 🟠 N=3; keep; keyframes only | 🟠 N=3; keep; keyframes only | 🟠 N=3; keep; keyframes only |
| DROID-SLAM | ➖ historical | ➖ historical | ➖ historical | ➖ historical | ➖ historical | ➖ historical | ➖ historical | ➖ excluded |
| DPVO | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep |
| OKVIS2 | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | 🟠 N=3; keep; collapse r2 retained |
| OKVIS2-X | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep |
| OV2SLAM | 🟠 N=3; keep; shutdown error | 🟠 N=3; keep; shutdown error | 🔄 N=3; re-evaluate: E1; shutdown error | 🔄 N=3; re-evaluate: E2; shutdown error | 🟠 N=3; keep; shutdown error | 🟠 N=3; keep; shutdown error | 🟠 N=3; keep; shutdown error | 🟠 N=3; keep; shutdown error |
| MASt3R-SLAM | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded |
| MegaSaM | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded |

### VIO (stereo + IMU, no loop closure) - `results/vio/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | 🟠 N=3; keep; coverage 86% | ✅ N=3; keep | ⬜ N=0; crash at start; run 3: N1 |
| Basalt | 🔁 N=3; rerun: R5 | 🔁 N=3; rerun: R5 | 🔁 N=3; rerun: R6; then E1 | 🔁 N=3; rerun: R6; then E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ⬜ N=1; run 2 more: N2 |
| OKVIS2 | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ⬜ N=1; run 2 more: N2 |
| OKVIS2-X | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ⬜ N=1; run 2 more: N2 |
| OpenVINS | 🔁 N=1; run 3: R5 | 🔁 N=1; run 3: R5 | ⬜ N=1; run 2 more: N2; r1: E1 | ⬜ N=1; run 2 more: N2; r1: E2 | ⬜ N=1; run 2 more: N2 | ⬜ N=1; run 2 more: N2 | ⬜ N=1; run 2 more: N2 | ⬜ N=1; run 2 more: N2 |
| AirSLAM | 🔁 N=3; rerun: R5 | 🔁 N=3; rerun: R5 | 🔄 N=3; re-evaluate: E1; keyframes only | 🔄 N=3; re-evaluate: E2; keyframes only | 🔁 N=3; rerun: R2 | 🔁 N=3; rerun: R2 | 🔁 N=3; rerun: R2 | ⬜ N=1; run 2 more: N2 |
| Voxel-SVIO | 🔁 N=3; rerun: R5 | 🔁 N=3; rerun: R5 | 🔄 N=3; re-evaluate: E1; shutdown error | 🔄 N=3; re-evaluate: E2; shutdown error | 🟠 N=3; keep; shutdown error; coverage 68% | 🟠 N=3; keep; shutdown error; coverage 78% | 🟠 N=3; keep; shutdown error; coverage 76% | ⬜ N=1; run 2 more: N2 |

### VO-LC (visual only + loop closure) - `results/vo-lc/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| DPV-SLAM | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep |
| OKVIS2 | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ⬜ N=1; run 2 more: N2 |
| OKVIS2-X | 🔁 N=3; rerun: R4 | 🔁 N=3; rerun: R4 | 🔁 N=3; rerun: R4; then E1 | 🔁 N=3; rerun: R4; then E2 | 🔁 N=3; rerun: R4 | 🔁 N=3; rerun: R4 | 🔁 N=3; rerun: R4 | 🔁 N=0; run 3: R4 |
| ORB-SLAM3 | ⬜ N=0; crash at start; run 3: N1 | 🟠 N=3; keep; coverage 73% | 🔄 N=3; re-evaluate: E1; exit 134/139 after save; coverage 47% | 🔄 N=3; re-evaluate: E2; exit 139 after save | 🟠 N=3; keep; exit 139 after save | 🟠 N=3; keep; exit 139 after save | 🟠 N=3; keep; exit 134 after save | 🔁 N=3; rerun: R1 |
| AirSLAM | ❓ N=3; keep, check Q1; keyframes only | ❓ N=3; keep, check Q1; keyframes only | 🔄 N=3; re-evaluate: E1; keyframes only | 🔄 N=3; re-evaluate: E2; keyframes only | 🟠 N=3; keep; keyframes only | 🟠 N=3; keep; keyframes only | 🟠 N=3; keep; keyframes only | 🟠 N=3; keep; keyframes only |
| OV2SLAM | 🟠 N=3; keep; shutdown error; collapse r2 retained | 🟠 N=3; keep; shutdown error | 🔄 N=3; re-evaluate: E1; shutdown error | 🔄 N=3; re-evaluate: E2; shutdown error | 🟠 N=3; keep; shutdown error | 🟠 N=3; keep; shutdown error | 🟠 N=3; keep; shutdown error | 🟠 N=3; keep; shutdown error |
| MASt3R-SLAM | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded | ➖ excluded |

### VIO-LC (stereo + IMU + loop closure) - `results/vio-lc/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | ✅ N=3; keep | ✅ N=3; keep | 🔁 N=3; rerun: R3; then E1 | 🔁 N=3; rerun: R3; then E2 | ✅ N=3; keep | 🟠 N=3; keep; coverage 86% | ✅ N=3; keep | ⬜ N=0; crash at start; run 3: N1 |
| OKVIS2 | ✅ N=3; keep | ✅ N=3; keep | 🔄 N=3; re-evaluate: E1 | 🔄 N=3; re-evaluate: E2 | ✅ N=3; keep | ✅ N=3; keep | ✅ N=3; keep | ⬜ N=1; run 2 more: N2 |
| OKVIS2-X | 🔁 N=3; rerun: R4 | 🔁 N=3; rerun: R4 | 🔁 N=3; rerun: R4; then E1 | 🔁 N=3; rerun: R4; then E2 | 🔁 N=3; rerun: R4 | 🔁 N=3; rerun: R4 | 🔁 N=3; rerun: R4 | 🔁 N=1; run 3: R4 |
| AirSLAM | 🔁 N=3; rerun: R5 | 🔁 N=3; rerun: R5 | 🔄 N=3; re-evaluate: E1; keyframes only | 🔄 N=3; re-evaluate: E2; keyframes only | 🔁 N=3; rerun: R2 | 🔁 N=3; rerun: R2 | 🔁 N=3; rerun: R2 | ⬜ N=1; run 2 more: N2 |

### GNSS-VIO (stereo + IMU + GNSS) - `results/gnss-vio/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 |
|---|---|---|---|---|
| CIFASIS GNSS-SI | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 |
| RTAB-Map | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 |
| VINS-Fusion | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 |
| OpenVINS+GPS | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 |
| OKVIS2-X (tight) | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 | ⬜ old N=1 only; run 3 on server: N3 |

### What the codes mean

**Rerun — the estimator was given a wrong setting or calibration, so the saved trajectory cannot be repaired afterwards.**

| Code | Cells | What was wrong | How I know | What has to change |
|---|---|---|---|---|
| `R1` | ORB-SLAM3 ZED VO, VO-LC (6 runs) | The config says the camera runs at 15 fps; the ZED sequence is 10 fps. ORB-SLAM3 uses this number for keyframe timing. | Saved snapshots show `Camera.fps: 15`; the ZED inertial snapshots show 10. | Use the 10 fps profile. Already flagged by the acceptance review. |
| `R2` | AirSLAM EuRoC VIO, VIO-LC (18 runs) | AirSLAM rectifies EuRoC images internally but keeps the camera–IMU rotation of the unrectified camera. Vision and IMU are fused with axes 0.62° apart. | `src/airslam/src/camera.cc` sets `_Tbc` before rectification and never updates it. | Apply and build the prepared source patch. Already flagged. |
| `R3` | ORB-SLAM3 HortiMulti VIO-LC (6 runs) | Same kind of mismatch: rectified images with the raw-camera IMU rotation, 1.22° off. The VIO config was already corrected; the VIO-LC one was not. | The saved VIO-LC matrix equals the authors' raw `T_imu_link_forwardLeft_cam` exactly. | Use the rectified transform. Already flagged. |
| `R4` | OKVIS2-X VO-LC and VIO-LC, all 8 sequences (43 existing runs, 48 to execute) | The benchmark configs let the final bundle adjustment re-optimise the camera extrinsics (`do_extrinsics_final_ba: true`). The upstream OKVIS2-X config has this off. The optimiser then shrinks the stereo baseline, which changes the metric scale of the whole trajectory. | Saved final maps: baseline changes of −1 to −9 %, camera position shifts up to 98 mm; each run's scale error matches its own baseline change (section 2.2). | Set `do_extrinsics_final_ba: false`. The three EuRoC VO-LC cells are green in `TODO.md` today and should not be. |
| `R5` | Rosario inertial runs of Basalt, AirSLAM (VIO and VIO-LC), OpenVINS, Voxel-SVIO (26 existing runs, 30 to execute) | These four were told the IMU sits exactly at the left camera with no rotation. The dataset authors publish 0.37° and 34 mm. ORB-SLAM3 and OKVIS2/OKVIS2-X use the published value, so the comparison is also unequal. | Saved snapshots contain an identity transform; authors' URDF and ORB config agree on the real one; nothing in data preparation compensates (section 2.3). | Use the authors' transform in all four. Decide one IMU-noise policy at the same time. |
| `R6` | Basalt HortiMulti VIO (6 runs) | Accelerometer noise is set to 0.5 and gyroscope noise to 0.006, about 450× and 10× the sensor values. They come from a tuning sweep made while the extrinsic bug was still present. With these values Basalt almost ignores the IMU. | Saved `hortimulti_calib.json`; VIO and VO results are nearly identical (section 2.4). | Use a justified noise value, not one tuned on these sequences. |

**New runs — nothing valid to keep or repair yet.**

| Code | Cells | Why |
|---|---|---|
| `N1` | ORB-SLAM3: VO Rosario seq1, seq5, HortiMulti str02; VO-LC Rosario seq1; ZED VIO, VIO-LC (18 runs) | One attempt each. The process crashed (`bad_alloc` or segfault) 0.05–0.15 s after creating its first map, before any tracking. The same binary finishes the same images in other modes. This is a software crash to diagnose, not a result about the algorithm (section 3.1). |
| `N2` | OpenVINS VIO on EuRoC, HortiMulti, ZED; ZED inertial cells of Basalt, OKVIS2, OKVIS2-X, AirSLAM, Voxel-SVIO; OKVIS2 ZED VO-LC (28 runs) | Only one evaluated repetition exists. It stays as an observation; two more are needed. If the acceptance rule requires all three from one runner version, run three (section 3.2). |
| `N3` | All GNSS-VIO cells (60 runs) | The only results are single runs from older machines without saved configs. They were never run on the server (section 3.3). |

**Re-evaluate — the saved trajectories are fine; only the comparison with the reference changes. No estimator runs.**

| Code | Cells | What was wrong | What to do |
|---|---|---|---|
| `E1` | Every HortiMulti str02 cell | The reference trajectory is the pose of the robot's `base_link`. The estimates are poses of the left camera, which sits 0.37 m ahead, 0.08 m to the side and 0.86 m above it. The evaluation currently compares the two points directly. | Move the reference to the camera with the authors' published chain (`T_base_link_mount`, `T_mount_os_sensor`, `T_os_sensor_forwardLeft_cam` in the Feb 2026 `calibration.yaml`). For OKVIS2 VIO-LC run 1 this changes Sim(3) ATE from 0.76 to 0.46 m (section 4.2). |
| `E2` | Every HortiMulti str03 cell | The reference file for this sequence is labelled `odom → odom_mapping`, a LiDAR-odometry output, not `base_link`. Which sensor origin it describes is not documented, so the correct offset to the camera is not yet known. | Get the frame from the authors or their source, then re-evaluate with the matching offset. Until then the current numbers stay provisional. |

For both `E1` and `E2`: the HortiMulti reference appears about 3 % longer than both the stereo calibration and
raw GNSS indicate (strong on str02, inconclusive on str03). That inflates SE(3) error for every well-tracking
method by a similar amount. Report SE(3) and Sim(3) side by side; do not rescale the reference (section 4.2).

**Open question.**

| Code | Cells | Question |
|---|---|---|
| `Q1` | AirSLAM Rosario VO, VO-LC (12 runs) | Scale factors are 0.47–0.94, far from the other stereo methods. A likely cause is the benchmark's 50 m depth limit, which on this 5 cm baseline accepts stereo disparities down to 0.65 px. Not confirmed. Keep the runs; test one corrected profile in a diagnostic run before deciding (section 5). |

**Why the Rosario and ZED cells marked keep are yellow in `TODO.md`.**

- Rosario: the block was "reference chain unverified". The authors' site states the reference is the RealSense IMU
  pose, which is what the evaluator already assumes, so the numbers do not change. Two things to state in the paper:
  the calibration is the authors' ORB-SLAM3 evaluation profile (depth scale 0.5–1 % below their other sources),
  and the reference was itself computed from the same camera and IMU (section 4.1).
- ZED: the reference has positions only. Position accuracy is usable; orientation metrics are not (section 4.3).

---

## 2. Definite reruns (estimator-side)

### 2.1 Already flagged by the acceptance review — I agree (10 cells, 30 runs, ~11 h)

| Cells | Defect | Check I made |
|---|---|---|
| ORB-SLAM3 ZED VO, VO-LC | `Camera.fps: 15` on 10 Hz input | saved snapshots show 15; ZED VIO snapshots show 10 |
| AirSLAM EuRoC VIO, VIO-LC (MH01/03/05) | `_Tbc` not updated after internal rectification | `src/airslam/src/camera.cc`: `_Tbc = Tbc0` is set before `stereoRectify` and never recomposed |
| ORB-SLAM3 HortiMulti VIO-LC (str02, str03) | raw-camera `IMU.T_b_c1` with rectified images | saved VIO-LC matrix equals the authors' raw `T_imu_link_forwardLeft_cam` exactly |

### 2.2 OKVIS2-X VO-LC and VIO-LC, all eight sequences (16 cells, 43 existing evaluations, 48 runs, ~26 h)

**Defect.** Saved LC configs have `do_final_ba: true` **and** `do_extrinsics_final_ba: true`
(`sigma_r_final_ba: 0.03`, `sigma_alpha_final_ba: 0.3`). The upstream file
`src/okvis2x/config/euroc/okvis2.yaml` has `do_final_ba: true` with `do_extrinsics_final_ba: false`.
So the benchmark, not upstream, lets the final bundle adjustment move the camera extrinsics.
OKVIS2 LC configs have `do_final_ba: false`, so its identical `do_extrinsics_final_ba: true` is inactive.

**Measured consequence.** I read the first camera-0 and camera-1 `FRAME` records from every saved
`okvis2-slam-final_map.g2o` and compared them with the configured `T_SC`:

| Mode / dataset | Baseline configured | Baseline after final BA | Change | Camera-0 position shift |
|---|---:|---:|---:|---:|
| VO-LC EuRoC (9 runs) | 0.11007 | 0.1027–0.1085 | −1.5 to −6.7 % | 1–4 mm |
| VO-LC HortiMulti (6) | 0.13950 | 0.1329–0.1346 | −3.5 to −4.8 % | 2–3 mm |
| VO-LC Rosario (6) | 0.04973 | 0.0490–0.0492 | −1.1 to −1.5 % | 1–2 mm |
| VIO-LC EuRoC (9) | 0.11007 | 0.1084–0.1106 | +0.5 to −1.6 % | 10–25 mm |
| VIO-LC HortiMulti (6) | 0.13950 | 0.1271–0.1340 | −3.9 to −8.9 % | 13–44 mm |
| VIO-LC Rosario (6) | 0.04973 | 0.0474–0.0488 | −1.9 to −4.7 % | 70–98 mm |
| VIO-LC ZED (1) | 0.11985 | 0.11973 | −0.1 % | 6 mm |

The scale error of each run tracks its own baseline change. On EuRoC VO-LC the predicted scale
`b_configured / b_final` and the evaluated `scale_factor` are, run by run:
1.024/1.025, 1.019/1.013, 1.018/1.015, 1.041/1.034, 1.065/1.062, 1.015/1.009, 1.042/1.029, 1.072/1.059, 1.066/1.064.
Correlation over all runs: 0.82 (VO-LC, n=21), 0.96 (VIO-LC, n=22).

Effect on reported accuracy (cell medians, SE(3) ATE in metres, OKVIS2 → OKVIS2-X on the same cell):

| Cell | OKVIS2 (final BA off) | OKVIS2-X | OKVIS2-X Sim(3) |
|---|---:|---:|---:|
| VO-LC MH01 | 0.023 | 0.065 | 0.019 |
| VO-LC MH03 | 0.038 | 0.125 | 0.037 |
| VO-LC MH05 | 0.093 | 0.393 | 0.076 |
| VO-LC str03 | 0.686 | 1.696 | 1.264 |
| VIO-LC str02 | 1.742 | 3.387 | 1.529 |
| VIO-LC Rosario seq1 | 0.837 | 5.360 | 5.122 |

In visual-only mode nothing but the 3 cm prior fixes the stereo scale, so the drift is a gauge artefact,
not a loop-closure result. With the IMU on, scale is only weakly observable for a slow ground robot and
the extrinsics drift the same way.

**Disposition.**
- VO-LC, all sequences: rerun. The three EuRoC VO-LC cells are currently green and should not be.
- VIO-LC on Rosario, HortiMulti, ZED: rerun.
- VIO-LC on EuRoC: same deviating setting, small measured effect (accuracy is not visibly harmed). Rerun for a
  single consistent cohort; it costs about 25 minutes of machine time.
- Correction: `do_extrinsics_final_ba: false` (the upstream value). Whether final BA itself stays on for
  OKVIS2-X while it is off for OKVIS2 is a separate disclosed profile difference.

### 2.3 Rosario inertial runs with an identity camera–IMU transform (10 cells, 26 existing evaluations, 30 runs, ~7 h)

Saved snapshots for Basalt VIO, AirSLAM VIO and VIO-LC, OpenVINS VIO and Voxel-SVIO VIO on seq1/seq5 contain
`T_imu_cam0 = identity`. ORB-SLAM3, OKVIS2, OKVIS2-X (and today's VINS-Fusion and CIFASIS GNSS-SI configs)
use the authors' transform. Author material:

| Source | Rotation from identity | Lever arm |
|---|---:|---:|
| `data/config/rosario_v2.urdf.xacro`, joint `infra1_to_imu` | 0.365° | 33.9 mm |
| `orb-slam3_rosariov2.yaml`, `Tbc` | 0.371° | 33.9 mm |
| `open-vins_imucam_rosariov2.yaml`, Kalibr `T_cam_imu` (inverted) | 0.939° | 34.7 mm |
| Benchmark: Basalt, AirSLAM, OpenVINS, Voxel-SVIO | 0° | 0 mm |

The URDF and the ORB config agree; the OpenVINS example is a different calibration (0.74° from the other two).
Whichever is preferred, identity matches none of them. The data preparation and players pass IMU samples
through unchanged (`_rosario_extract.py`, `imu_to_euroc.py`, the three data players), so nothing compensates it.
None of the four estimators calibrates extrinsics online in the saved configs. The config comments that justify
identity ("convention used by the Rosario v2 paper, basalt config, and OKVIS2 config", "ZED IMU") are wrong:
the sensor is a RealSense D435i and the OKVIS2 config is not identity.

This is the same class of defect as 2.1 (0.62° for AirSLAM EuRoC), with a 34 mm lever arm on top.
`configs/openvins/rosariov2/kalibr_imucam_chain.yaml` still has identity today.

Related, same cells: these four also use IMU noise `1.6e-2 / 2.82e-4`, bias walks `1e-3 / 1e-4`, which are
Basalt's EuRoC default values, not the D435i values the authors publish (`9.94e-4 / 2.32e-4`, `4.75e-5 / 1.82e-6`).
Decide one noise policy before the rerun.

### 2.4 Basalt HortiMulti VIO (2 cells, 6 runs, a few minutes)

Saved `hortimulti_calib.json`: `accel_noise_std 0.5`, `gyro_noise_std 0.006`, `accel_bias_std 0.1`.
The authors' session calibration gives `1.09e-3 / 6.04e-4`, which every other algorithm uses, and Basalt's own
values on the other datasets are `0.016 / 0.000282`. `TODO.md` records that the "5-run noise sweep searched the
wrong parameter" while the extrinsic was still wrong; the swept values stayed in the config. The IMU is
effectively switched off: VIO str02 3.11 m vs VO 2.72 m, str03 0.677 vs 0.723. This is a parameter chosen on
test data under a since-fixed bug. Rerun with a justified value.

---

## 3. New runs needed (not re-runs of valid results)

### 3.1 ORB-SLAM3 startup crashes (6 cells, 18 runs, ~13 h)

VO Rosario seq1, seq5, HortiMulti str02; VO-LC Rosario seq1; ZED VIO and VIO-LC. Each has exactly one attempt.
All six logs end 0.05–0.15 s after `New Map created with N points` with `std::bad_alloc`, `Segmentation fault`,
or g2o `0 vertices to optimize` followed by a segfault. The same binary and images complete in other modes
(VO-LC seq5, VIO seq1/seq5, VO str03). The July notes in `TODO.md` record completed ORB-SLAM3 VO runs on these
sequences on another machine.

"Observed failure" is an accurate label for the attempt. It should not appear in a paper table as the algorithm's
outcome on these sequences: it is a process crash before tracking starts, sampled once. It needs diagnosis and
three attempts under a stated retry policy. I agree with the reviewer that retries need a documented rule that
keeps every attempt; "one attempt, no retry" on a crash at frame 2 is not a neutral rule either.

### 3.2 Missing repetitions (14 cells, 28 runs, ~33 h, dominated by ZED)

- OpenVINS VIO: MH01, MH03, MH05, str02, str03, ZED (r2, r3). Rosario is in 2.3.
- ZED VIO: Basalt, OKVIS2, OKVIS2-X, AirSLAM, Voxel-SVIO (r2, r3).
- ZED VIO-LC: OKVIS2, AirSLAM (r2, r3). OKVIS2-X is in 2.2.
- ZED VO-LC: OKVIS2 (r2 was killed, r3 absent).

Two notes. The OpenVINS exit code 134 is `openvins_data_player.py` aborting ("terminate called without an
active exception") **after** it writes the trajectory; it is a harness shutdown problem, not an estimator crash.
And adding r2/r3 from a repaired runner to an r1 from September makes a mixed cohort under the current
acceptance rule; for the short EuRoC cells it is simpler to run all three.

### 3.3 GNSS-VIO (20 cells, 60 runs)

All existing results are N=1 from older machines and lack saved configs. Resolving their historical provenance
is not worth the effort: they must be run on the server anyway. Before that, the authors' URDF gives the Rosario
antenna positions (`sensor_box_to_gps1/2/3`; `gps3` differs between recording day 1 and day 2, and seq1 and seq5
are on different days), and the HortiMulti calibration gives `T_base_link_gps_frame = (0.62, −0.11, 0.42)`.
The Rosario reference is itself fused from the same three PPK antennas (see 4.1), so GNSS-VIO accuracy against
it is not an independent test; that has to be stated in the paper.

---

## 4. Re-evaluate only, or keep

### 4.1 Rosario — keep (33 cells, 99 evaluations); the reference blocker can be closed

- **Reference frame.** The authors' site (`www/index.html` in their repo) states that the PGT is produced by
  MINS from the RealSense stereo-IR camera, the three PPK GNSS modules and the RealSense IMU, and is "a trajectory
  estimate of the IMU sensor in an ENU frame". `_pose_frames.py` already treats the reference as that IMU and moves
  it to the camera with the authors' `Tbc`. `docs/postprocessed_ground_truth.md` in the repo is still empty, so the
  website is the only statement. No re-evaluation is needed for the frame.
- **Images and intrinsics.** The benchmark uses `image_rect_raw` without re-rectification and the values
  `fx=fy=648.862, cx=645.011, cy=348.243, b=0.0497337`. This reproduces the authors' ORB-SLAM3 and ORB-SLAM3+GNSS
  evaluation profiles exactly: both launch files set `do_rectify` to `false` and both YAML files carry the same
  numbers and `Camera.bf: 32.27032495`.
- **What those numbers are.** I reproduced `LEFT.R` exactly and `cx, cy` exactly with `cv2.stereoRectify` on the
  authors' Kalibr values, and `648.862` is the mean of the two Kalibr `fy`. So they are post-rectification values
  for images that were never re-rectified. Other author sources for the same images:

  | Source | fx | cx | cy | baseline | fx·b |
  |---|---:|---:|---:|---:|---:|
  | Benchmark = authors' ORB profile | 648.86 | 645.01 | 348.24 | 0.049734 | 32.270 |
  | Authors' ORB profile, `RIGHT.P` | 648.86 | 645.01 | 348.24 | 0.050241 | 32.599 |
  | Authors' Kalibr (`open-vins_imucam`) | 645.41 | 648.73 | 349.04 | 0.050241 | 32.426 |
  | Authors' URDF `infra1_to_infra2` | – | – | – | 0.050240 | – |
  | Bag `camera_info` (from the other review, not checked by me) | 647.01 | 648.23 | 350.13 | 0.050211 | 32.487 |

  The benchmark's depth scale `fx·b` is 0.5–1.0 % low against every other source, and its principal point is
  about 3.5 px (0.3°) off. The Rosario scale factors of the inertial methods (0.99–1.05, mostly 1.01–1.03) are
  consistent with that but do not prove it.
- **Correction of my earlier statement.** I wrote "about 4 % at 10 m" and "affects all algorithms equally". The
  4 % figure needs the Kalibr left/right principal-point and rotation differences to be accurate to a fraction
  of a pixel, which is not established; the supported figure is 0.5–1 %. And the effect is not equal across
  methods. The reviewer is right on both. I also withdraw "I would redo it": this is the authors' own evaluation
  profile, so it is a disclosure ("authors' ORB-SLAM3 evaluation calibration; fx·b 0.5–1 % below the Kalibr/URDF
  values"), not a defect. 137 of the 150 planned Rosario slots have evaluations, not 150.
- **Reference independence.** The PGT uses the same camera and IMU as the estimators. State it as a limitation.

### 4.2 HortiMulti — re-evaluate (39 cells, 117 evaluations); 8 more cells are in section 2 and 3 in section 3

**Dataset version.** The server data is `Feb2026/Strawberry/Strawberry_2` and `Strawberry_3`. I downloaded the
current `GT_trajectory.csv` for both: same row counts and same values as the server files; only the column order
changed (`qw` is now first, the old files have it last). The old converter would fail on the new header rather
than misread it. The current `Feb2026/Strawberry/calibration.yaml` matches the extractor constants (K, D,
`T_forwardRight_cam_forwardLeft_cam`, 2048×1536), the raw `T_imu_link_forwardLeft_cam`, the 9.160379 ms time
shift and the IMU noise. `May2026` and `Jun2026` are different sessions with their own calibration and RTK GPS;
they are not what was run. The other review reached the same conclusion.

**Reference to camera.** The session calibration contains the chain that was listed as missing:
`T_base_link_mount`, `T_mount_os_sensor`, `T_os_sensor_forwardLeft_cam`. Composed, the left camera origin is at
`(0.368, 0.076, 0.860)` m in `base_link`; the Ouster is at `(0.268, 0, 0.940)`.

- str02: the original CSV header says `TagMap → base_link`. Applying the chain is an evaluation-only change.
  For OKVIS2 VIO-LC run1 I get SE(3) ATE 1.77 → 1.67 m and Sim(3) ATE 0.76 → 0.46 m. That is a large change for
  the well-tracked methods and none of it needs estimation.
- str03: the original CSV header says `odom → odom_mapping`, a LiDAR-odometry output, not `base_link`. Which
  sensor origin that is must come from the authors or from the Poly-TagSLAM/LIO source. For the record, the same
  run gives Sim(3) ATE 0.092 m as-is, 0.308 m under the `base_link` hypothesis and 0.060 m under the Ouster
  hypothesis. I am not proposing to pick the hypothesis by the lower error; this stays an open question (7.1).

**Reference scale.** My earlier wording ("the reference is 3–4 % too large", "every algorithm 0.65–0.85 m") was
too strong. Corrected statement and the checks the reviewer asked for:

| Check (my computation) | str02 | str03 |
|---|---:|---:|
| GT → raw GNSS, 2D similarity scale, block bootstrap | 0.9733 ± 0.0034 | 0.961 ± 0.016 |
| Same, after applying the authors' antenna lever arm | 0.9734 | 0.960 |
| Same, at the best time offset (searched ±3 s) | 0.9737 (−1.0 s) | 0.963 (−1.3 s) |
| First half / second half of the sequence | 0.972 / 0.975 | 0.996 / 0.930 |
| Authors' local GT → authors' `GT_trajectory_global.csv` | 1.000000 (rigid) | 1.000000 (rigid) |
| Estimate → GT scale, six algorithms (run1) | 1.008–1.039 | 1.030–1.037 |
| Estimate → raw GNSS scale, same six | 0.987–1.012 | 0.991–0.997 (±0.018) |

What this supports: on str02 two physically independent metric sources, the stereo calibration and GNSS, agree
with each other to about 1 % and both differ from the reference by about 3 %; antenna offset and timing do not
explain it; the authors' georeferenced reference carries the same scale. What it does not support: a correction
factor. The GNSS here is the raw, non-RTK `/antobot_gps` stream (status 0 throughout, σ_h ≈ 1.9 m) inside
polytunnels, and str03 on its own is inconclusive (its two halves disagree). A common stereo calibration error
would need the raw GNSS to be wrong by the same amount in the same direction, which is unlikely but not excluded.

Consequence for reporting, no reruns either way: among methods that track well (Sim(3) ATE below about 0.5 m)
SE(3) ATE on str03 is 0.57–0.83 m in all 16 such cells (OKVIS2-X VIO-LC excluded, see 2.2), so SE(3) cannot
rank them there. Poorly tracking methods
(AirSLAM VO 4.2–4.4 m, DPV-SLAM 9 m) are far above that floor; the reviewer's correction is right. Report SE(3)
and Sim(3) side by side with this explanation, do not rescale the reference, and ask the authors (7.2). A decisive
test exists in their data: `May2026` sequences have RTK GPS and the same tag map.

**Time offset.** Basalt and Voxel-SVIO use the published 9.16 ms; OKVIS2/OKVIS2-X have `image_delay: 0.0`;
OpenVINS starts at 0 and estimates it; ORB-SLAM3 and AirSLAM have no such input. This is an inconsistency worth
a line in the paper. At walking speed it is about 5 mm, so I do not count it as a rerun reason on its own.

### 4.3 ZED — keep (10 cells, 30 evaluations), plus the new runs in section 3

All inertial snapshots use one transform (axis permutation, `t = (0.002, 0.023, −0.0002)`) and one noise set;
intrinsics and baseline agree across algorithms. The reference is position-only, so positional metrics are usable
with that limitation and orientation metrics are not. I found no estimator-side defect beyond the flagged
ORB-SLAM3 frame rate. I did not re-derive the 2.86 m lever arm today.

### 4.4 EuRoC — keep (60 cells, 180 evaluations)

Camera–IMU transforms agree across algorithms; loop-closure switches are correct in all four modes; intrinsics
agree. Exceptions are the AirSLAM inertial cells (2.1) and OKVIS2-X LC cells (2.2).

---

## 5. Items that are not reruns but need a decision or a label

- **AirSLAM on Rosario (VO, VO-LC: 4 cells; its VIO cells are in 2.3).** Scale factors are 0.47–0.94 across the
  four modes (I previously wrote 0.58–0.73, which was wrong), against 0.90–1.05 for the other metric-scale methods.
  What I checked: baseline sign is harmless (`_bf = fx * abs(Tc1c0(0,3))`); depth is `BF / (x_left − x_right)`
  from raw keypoint coordinates (`frame.cc:144–170`) with a gate `bf / depth_upper_thr`. With the benchmark's
  `depth_upper_thr` that gate is 4.8 px on EuRoC, 2.4 px on HortiMulti, 2.7 px on ZED and **0.65 px on Rosario**.
  Accepting sub-pixel disparities on a 5 cm baseline is a plausible cause. The logs also show g2o "Cholesky
  failure" messages on Rosario and HortiMulti and none on EuRoC. I did not check input resizing or trajectory
  selection. This is a suspect benchmark adaptation, not a confirmed defect; a rule fixed in advance (for example
  the same minimum disparity as the upstream EuRoC profile) could be tested in a diagnostic run. Do not tune it
  on ATE.
- **Voxel-SVIO on EuRoC.** Two separate effects, both from the author-recommended profile. Late initialisation:
  the first pose is 46.0 s after sequence start on MH01 (4.2 s on MH03, 5.5 s on MH05), which is the whole
  duration gap; MH01 has a long pre-take-off phase. Single-frame skips after initialisation: about 10 % of frames on MH01 and
  20 % on MH03 and MH05 (output intervals of 100 ms instead of 50 ms), with no gap above 0.3 s, consistent with
  `track_frequency: 20.0` on 20 Hz input. Keep, label as limited.
- **OpenVINS on Rosario.** The authors publish their own OpenVINS profile. Besides the transform (2.3) ours
  differs in: intrinsics (theirs are the Kalibr values with distortion), online extrinsic and intrinsic calibration
  (theirs on, ours off), `num_pts` 1200 vs 200, `init_dyn_use` false vs true, IMU noise, and a 6.5 ms time shift.
  Both have `try_zupt: false`, so I withdraw my earlier remark about zero-velocity updates. The saved run tracks
  for more than 200 s and then diverges to 280 km; with this many deviations from the authors' profile it is not
  evidence about OpenVINS on this dataset.
- **Tick semantics.** I agree with the reviewer: separate "usable in the paper" from "clean execution" instead of
  one tick. Under that split, complete trajectories followed by a shutdown error (OV2SLAM, Voxel-SVIO, ORB-SLAM3
  exit 139 after save, OpenVINS player exit 134) and AirSLAM keyframe-only exports are usable with a footnote.

---

## 6. Per-mode map

Moved to section 1b, in the `TODO.md` layout with one row per algorithm.

---

## 7. Open questions that only the authors or more evidence can settle

1. HortiMulti Strawberry_3: which sensor origin is the `odom_mapping` reference, and is it the Poly-TagSLAM
   output or plain LiDAR-inertial odometry?
2. HortiMulti: is the tag-map scale constrained by the total-station survey in the tunnels used for
   Strawberry_2/_3? Raw GPS and the stereo calibration both suggest the reference is about 3 % long.
3. Rosario: which camera–IMU calibration is current, the URDF/ORB one (0.37°) or the Kalibr one in the OpenVINS
   example (0.94°)? And which baseline, 0.04973 (`Camera.bf`) or 0.05024 (URDF, Kalibr, `RIGHT.P`)?
4. ZED: serial-specific IMU rotation and time offset. Not addressed here.

---

## 8. Checked and found consistent

- Intrinsics and baseline are identical across algorithms within each dataset, in VO and VO-LC snapshots.
- Loop closure is off in every VO/VIO snapshot and on in every VO-LC/VIO-LC snapshot.
- Camera–IMU transforms agree across all inertial algorithms on EuRoC, HortiMulti (rectified, except 2.1) and ZED.
- Configured camera rate matches the input everywhere except ORB-SLAM3 ZED VO/VO-LC.
- Config snapshots are identical across repetitions in all 176 cells that have at least two runs.

## 9. Not checked

- ZED reference construction and IMU calibration; GNSS input files; DROID-SLAM, MASt3R-SLAM, MegaSaM.
- Source-level review of each estimator's output frame; I relied on `_pose_frames.py` and its tests.
- Whether the repaired runners execute; nothing was run.
- Bag-level facts (camera_info, pixel identity of extracted images); those come from the other review.
