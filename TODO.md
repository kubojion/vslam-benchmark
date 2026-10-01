# vSLAM Benchmark - TODO

> **Acceptance review 2026-10-01:** 45 clean N=3 EuRoC cells now qualify for the documented
> recorded-profile comparison. A further 54 repetitions have explicit limitations;
> Nine observed configured-attempt failures remain reusable; two OpenVINS Rosario collapses
> now also require calibration reruns. Agricultural accuracy and GNSS
> claims remain blocked by material calibration/reference/input evidence.
> The five matrix layouts are unchanged. **N counts evaluations, not accepted successes.**
> All 593 evaluations were refreshed: 159 Rosario metrics corrected, 434 numerically
> unchanged; previous derived results and original attempts are preserved. The four-mode
> campaign still has 545/600 evaluations. No estimator was run and no native execution
> path is newly certified ready. See [acceptance handoff](docs/acceptance-handoff-20261001.md),
> [claim criteria](docs/paper-acceptance-20261001.md) and [the repair record](docs/repair-handoff-20261001.md).

---

## Status legend

`[x]` done  `[ ]` not started  `[~]` in-progress / partially done  `[!]` blocked

---

## Run combinations matrix

Legend per cell: ✅ N=3 clean accepted for the stated claim | 🟠 accepted with limitations |
❌ observed failure retained | 🟡 blocked by specific evidence | ⬜ missing repetitions |
🔁 required corrected cohort | ➖ excluded / unsupported | 🔧 missing excluded config.

**N counts schema-3 evaluations, including retained numerical failures**, independently
of historical COMPLETE markers. `N=0` can contain an accepted observed startup failure.
`missing r2,r3` means those physical attempts are absent; existing failed/interrupted
attempts are not missing. Limited claims name sparse exports, partial coverage,
nonzero exits or native shutdown errors despite wrapper exit 0. A green tick requires
three accepted, same-cohort, zero-exit, valid trajectories each with ≥95% dense export
coverage and no observed native fatal error. It does not certify future runner readiness.
Monocular Sim(3), final-optimization profiles and historical build disclosures remain explicit.

The future manifest contains **210 reusable observations, 91 required reruns, 87 missing
repetitions and 272 blocked cases**. No new estimation is certified ready. The previous
30 reruns remain; matched-session evidence adds 14 Rosario IMU-extrinsic cases,
42 additional Horti timing cases and five GNSS antenna-lever cases. See the
[reference review](docs/reference-review-20261001.md) and handoff for exact evidence and prerequisites.

### VO (no IMU, no loop closure) - `results/vo/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | ❌ N=0; observed failure r1; missing r2,r3 | ❌ N=0; observed failure r1; missing r2,r3 | ❌ N=0; observed failure r1; missing r2,r3 | 🟡 N=3; blocked: reference/clock; exit 139 | ✅ N=3 | 🟠 N=3; limited; exit 139 | ✅ N=3 | 🔁 N=3; rerun: FPS; exit 139 |
| Basalt | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=3; blocked: reference |
| MAC-VO | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=3; blocked: reference |
| AirSLAM | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | 🟠 N=3; limited; sparse | 🟠 N=3; limited; sparse | 🟠 N=3; limited; sparse | 🟡 N=3; blocked: reference |
| DROID-SLAM | 🟡 N=3 historical | 🟡 N=3 historical | 🟡 N=3 historical | 🟡 N=3 historical | 🟡 N=1 historical | 🟡 N=1 historical | 🟡 N=1 historical | ➖ excluded; no run |
| DPVO | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=3; blocked: reference |
| OKVIS2 | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=3; collapse r2; blocked: reference; observed failure r2 |
| OKVIS2-X | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=3; blocked: reference |
| OV2SLAM | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | 🟠 N=3; limited; native shutdown error | 🟠 N=3; limited; native shutdown error | 🟠 N=3; limited; native shutdown error | 🟡 N=3; blocked: reference |
| MASt3R-SLAM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | 🔧 config missing; excluded |
| MegaSaM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | 🔧 config missing; excluded |

> **Remaining:** ORB-SLAM3 Rosario seq1/seq5 and Horti str02 retain observed startup failures
> (no saved trajectories to recover); r2/r3 remain missing. OKVIS2 ZED run2 is a retained collapse, not an unexecuted repetition.
> **Basalt:** the explicit Rosario compatibility profile uses 0.03; other datasets retain
> the upstream 0.05 setting, matching saved runs. ZED relative stereo geometry is verified
> equivalent for pure VO. Other reference/qualification gates still apply.
> **ORB ZED VO/VO-LC:** six saved runs used 15 FPS for 10 Hz input; plan a corrected
> cohort. Evaluation cannot repair the estimator-side setting.
> DROID-SLAM is historical and excluded from the target. MASt3R/MegaSaM OOM notes refer
> to the earlier 12 GB machine, not a verified OOM measurement on this 24 GB server.
> DPVO is monocular; DPV-SLAM is its VO-LC variant. Current headline labels use Sim(3) for both monocular modes.

### VIO (stereo + IMU, no loop closure) - `results/vio/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🔁 N=3; rerun: time offset | 🔁 N=3; rerun: time offset | ✅ N=3 | 🟠 N=3; limited; partial coverage | ✅ N=3 | ❌ N=0; observed failure r1; missing r2,r3 |
| Basalt | 🔁 N=3; rerun: IMU extrinsic | 🔁 N=3; rerun: IMU extrinsic | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=1; blocked: reference/IMU; missing r2,r3 |
| OKVIS2 | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🔁 N=3; rerun: time offset | 🔁 N=3; rerun: time offset | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=1; blocked: reference/IMU; missing r2,r3 |
| OKVIS2-X | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🔁 N=3; rerun: time offset | 🔁 N=3; rerun: time offset | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=1; blocked: reference/IMU; missing r2,r3 |
| OpenVINS | 🔁 N=1; collapse r1; rerun: IMU extrinsic; exit 134; missing r2,r3 | 🔁 N=1; collapse r1; rerun: IMU extrinsic; exit 134; missing r2,r3 | 🟡 N=1; blocked: reference/clock; exit 134; missing r2,r3 | 🟡 N=1; blocked: reference/clock; exit 134; missing r2,r3 | 🟠 N=1; limited; exit 134; missing r2,r3 | 🟠 N=1; limited; exit 134; missing r2,r3 | 🟠 N=1; limited; partial coverage; missing r2,r3 | ❌ N=1; collapse r1; observed failure r1; missing r2,r3 |
| AirSLAM | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🔁 N=3; rerun: time offset | 🔁 N=3; rerun: time offset | 🔁 N=3; rerun: rectified IMU | 🔁 N=3; rerun: rectified IMU | 🔁 N=3; rerun: rectified IMU | 🟡 N=1; blocked: reference/IMU; missing r2,r3 |
| Voxel-SVIO | 🔁 N=3; rerun: IMU extrinsic | 🔁 N=3; rerun: IMU extrinsic | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | 🟠 N=3; limited; native shutdown error; partial coverage | 🟠 N=3; limited; native shutdown error | 🟠 N=3; limited; native shutdown error | 🟡 N=1; blocked: reference/IMU; missing r2,r3 |

> Horti IMU extraction/rectification corrections exist, but 48 saved inertial attempts
> still require camera–IMU timing correction (six overlap earlier rectification defects). All seven non-ZED
> sequences have N=3 for six algorithms; **OpenVINS remains N=1 in every cell**. Six
> previously unscored run1 trajectories have repaired evaluations, retaining exit 134.
> Rosario seq1/seq5 retain catastrophic scale failures; the saved fixed identity
> IMU/camera calibration is now a confirmed defect, not a valid physical convention. EuRoC recovered trajectories are accepted with exit/coverage limitations; agricultural accuracy remains blocked.
> **ZED:** the six N=1 results use the corrected camera-optical/IMU transform. OpenVINS
> still collapses; ORB-SLAM3 still has no evaluated output. Each N=1 cell needs run2/run3.
> The old identity-transform results and excitation-only explanation are historical.
> See [ZED calibration](docs/zed2i-imu-extrinsics.md) for remaining residual/timing limitations.

### VO-LC (visual only + loop closure) - `results/vo-lc/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| DPV-SLAM | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=3; blocked: reference |
| OKVIS2 | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=1; blocked: reference; missing r3 |
| OKVIS2-X | 🟡 N=3; blocked: camera model; separate cohorts | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=0; blocked: execution/evidence; missing r2,r3 |
| ORB-SLAM3 | ❌ N=0; observed failure r1; missing r2,r3 | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock; exit 134,139 | 🟡 N=3; blocked: reference/clock; exit 139 | 🟠 N=3; limited; exit 139 | 🟠 N=3; limited; exit 139 | 🟠 N=3; limited; exit 134 | 🔁 N=3; rerun: FPS; exit 139; separate cohorts |
| AirSLAM | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | 🟠 N=3; limited; sparse | 🟠 N=3; limited; sparse | 🟠 N=3; limited; sparse | 🟡 N=3; blocked: reference; separate cohorts |
| OV2SLAM | 🟡 N=3; collapse r2; blocked: camera model; observed failure r2 | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: reference/clock | 🟡 N=3; blocked: reference/clock | 🟠 N=3; limited; native shutdown error | 🟠 N=3; limited; native shutdown error | 🟠 N=3; limited; native shutdown error | 🟡 N=3; blocked: reference |
| MASt3R-SLAM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | ➖ excluded; old OOM | 🔧 config missing; excluded |

> **OKVIS2:** all seven non-ZED cells now have N=3 after the September 23 recovery,
> using the later final-full-BA-disabled configuration. On ZED, run1 finished (exit 0,
> 46,282 output poses) and has a repaired evaluation (ATE 0.720 m, with reference limitations).
> Its historical COMPLETE marker is still absent. Run2 was killed and run3 is absent.
> The repaired wrapper preserves attempts and evaluates each repetition immediately.
> **OKVIS2-X ZED:** no complete evaluated run; latest recovery stopped near initialization.
> **ORB-SLAM3 Rosario seq1:** native crash; no complete evaluated run.
> **OV2SLAM Rosario seq1:** N=3 includes run2 collapse; retain it in failure-rate reporting.
> AirSLAM and OV2SLAM VO-LC are now implemented and N=3 on all eight sequences.
> Loop-event counts and final-BA settings require explicit interpretation; prior N=1
> conclusions are not automatically conclusions about this server cohort.

### VIO-LC (stereo + IMU + loop closure) - `results/vio-lc/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 | EuRoC MH_01 | EuRoC MH_03 | EuRoC MH_05 | zed2i field1 |
|---|---|---|---|---|---|---|---|---|
| ORB-SLAM3 | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🔁 N=3; rerun: rectified IMU; rerun: time offset | 🔁 N=3; rerun: rectified IMU; rerun: time offset | ✅ N=3 | 🟠 N=3; limited; partial coverage | ✅ N=3 | ❌ N=0; observed failure r1; missing r2,r3 |
| OKVIS2 | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🔁 N=3; rerun: time offset | 🔁 N=3; rerun: time offset | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=1; blocked: reference/IMU; missing r2,r3 |
| OKVIS2-X | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🔁 N=3; rerun: time offset | 🔁 N=3; rerun: time offset | ✅ N=3 | ✅ N=3 | ✅ N=3 | 🟡 N=1; blocked: reference/IMU; missing r2,r3 |
| AirSLAM | 🟡 N=3; blocked: camera model | 🟡 N=3; blocked: camera model | 🔁 N=3; rerun: time offset | 🔁 N=3; rerun: time offset | 🔁 N=3; rerun: rectified IMU | 🔁 N=3; rerun: rectified IMU | 🔁 N=3; rerun: rectified IMU | 🟡 N=1; blocked: reference/IMU; missing r2,r3 |

> All four methods have N=3 on the seven non-ZED sequences. **ZED configs now exist**:
> OKVIS2, OKVIS2-X and AirSLAM each have corrected N=1 and need two more repetitions;
> ORB-SLAM3's corrected attempt failed. AirSLAM's map refinement is an offline step;
> final corrected trajectories do not by themselves establish live navigation latency.

### GNSS-VIO (stereo + IMU + GNSS) - `results/gnss-vio/`

| Algorithm | rosariov2 seq1 | rosariov2 seq5 | hortimulti str02 | hortimulti str03 |
|---|---|---|---|---|
| CIFASIS GNSS-SI | 🔁 N=1; rerun: antenna lever; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 |
| RTAB-Map | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 |
| VINS-Fusion | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; invalid trajectory; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 |
| OpenVINS+GPS | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 | 🟡 N=1; blocked: GNSS evidence; missing r2,r3 |
| OKVIS2-X (tight) | 🔁 N=1; rerun: antenna lever; missing r2,r3 | 🔁 N=1; rerun: antenna lever; missing r2,r3 | 🔁 N=1; rerun: antenna lever; missing r2,r3 | 🔁 N=1; rerun: antenna lever; missing r2,r3 |

> **Excluded from the executed server N=3 campaign.** These are historical N=1 results
> from earlier machines, not repeated server measurements. Sixteen default cells have
> COMPLETE; all four VINS-Fusion default cells have evaluation JSON but lack that marker.
> Three conventional-GPS variants are separately complete; three additional variants lack
> COMPLETE. Validate artifacts rather than adding markers manually.
> OpenVINS+GPS HortiMulti still needs corrected-extrinsic reruns/review. Current OKVIS2-X
> profiles now contain composed IMU-frame antenna levers. Four saved native OKVIS2-X
> logs loaded zero; CIFASIS Rosario seq1 loaded the v1 lever. These five require reruns. The future target is N=3; the old N=5 proposal remains
> a separate historical scope. VINS-Fusion Horti str02 has 153 invalid quaternion norms;
> its accuracy evaluation is blocked pending export recovery.
> Seq5 PPK and seq1 conventional GPS remain distinct inputs; seq1 PPK requires its recording.
> HortiMulti has consumer GNSS. EuRoC has no GNSS and is not part of this track.

---

## High-priority open tasks (Phase 2)

| # | Task | Status |
|---|---|---|
| 1 | Extract HortiMulti IMU (`/ms/imu/data` -> `mav0/imu0/data.csv`) | `[x]` |
| 2 | Run core VIO matrix | `[~]` six algorithms N=3 on all seven core sequences; OpenVINS only MH05 N=1; see VIO cells |
| 3 | Diagnose and fix hortimulti VIO scale collapse | `[x]` **root cause was a camera-IMU EXTRINSIC bug, NOT vibration** (the earlier "vibration floor" conclusion was wrong). Fixed in config; all algos scale ~1.0. See PROGRESS.md "RESOLVED". |
| 3b | Build OKVIS2 standalone (was never built) | `[x]` (`build_okvis2.sh`; -DHAVE_LIBREALSENSE=OFF -DUSE_CUDA=OFF) |
| 3c | Re-run 2 stale bad VIO runs (Voxel EuRoC, OpenVINS seq5) | `[x]` (were bad runs, not algorithm limits) |
| 3d | Add EuRoC MH_03/MH_05 VIO coverage + fix EuRoC times.txt (s->ns) | `[x]` |
| 4 | Run ORB-SLAM3 VIO on rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| 5 | Run Basalt VIO on rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| 6 | Run OpenVINS VIO on rosariov2/seq5 N=3 | `[!]` no complete evaluated repetitions; shutdown failure/recovery pending |
| 7 | MASt3R-SLAM / MegaSaM revisit on the 24 GB server (optional — both OOM'd at 12 GB) | `[ ]` |
| 8 | ORB-SLAM3 VO-clean LC-off re-runs | `[~]` LC-off configuration implemented; Rosario seq1/seq5 and Horti str02 missing after crashes |
| 9 | Finish executed N=3 server campaign (no GNSS) | `[~]` 538/600 evaluated runs; 176/200 cells N=3. Original N=5/GNSS target is separate and unfinished |
| 10 | Complete/validate GNSS-VIO N=1 sweep | `[~]` 16 default cells COMPLETE; four VINS-Fusion evaluations unvalidated; server repeats not run |
| 10b | Re-run OpenVINS+GPS HortiMulti with corrected extrinsics; validate all four rows | `[ ]` not completed by the no-GNSS server campaign |
| 11 | Normalize EuRoC dataset aliases and result/config paths to `euroc_mav` | `[x]` central shell/Python canonicalization; obsolete aliases removed |
| 12 | Commit local-only runtime prerequisites | `[x]` **DONE 2026-08-06**: AirSLAM launch files + OpenVINS Dockerfile live in the forks (`kubojion/AirSLAM`, `kubojion/open_vins` @ `vslam-benchmark-patches`, wired in `.gitmodules`); OKVIS2 external CMake patches remain vendored in `vendor/prerequisites/` (nested upstream submodules — patch dir is the clean carrier) |
| 13 | Finish remaining LC/VO cells | `[~]` MAC-VO ZED VO and AirSLAM/OV2SLAM VO-LC N=3 done; ZED OKVIS2/OKVIS2-X VO-LC still incomplete |
| 14 | OKVIS2-X "0 loop closures" | `[x]` **RESOLVED: log-parsing bug, not the algorithm.** See finding 12 |
| 15 | Add `loopClosing: 0` to hortimulti/euroc/zed2i `_stereo.yaml` | `[x]` clean LC-off baselines are the current VO table (2026-08-04) |
| 16 | Re-evaluate the 2 colleague-machine OKVIS2 VIO-LC runs with corrected LC metric | `[x]` closed by the machine-B re-evaluation campaign (2026-08-06, all EuRoC/HortiMulti runs re-parsed) |
| 17 | ~~Create GitHub forks~~ | `[x]` **DONE 2026-08-06** — forks created, branches pushed (airslam 1b70ff6, open_vins 289bca3), `.gitmodules` re-pointed |
| 18 | ~~Machine B: zed2i segment maps + GT tracking~~ | `[x]` **DONE 2026-08-06** (commits 9b0fc92 + 42c3492): vio/vo-lc maps regenerated on 2.86 m GT; euroc/hortimulti/zed2i GT + times + segments + alias symlinks tracked — verified byte-reproducible CSVs on any clone |
| 19 | ~~Fix zed2i turn detection~~ | `[x]` **DONE 2026-08-06** (5d71cbd): tangent-derived headings (2 m path smoothing) → zed2i now 10 row + 5 turn segments; zed2i runs re-evaluated. Known limitation (documented in-code): short absorbed segments can split one row into several — coalescing deferred to the server-campaign re-eval since it re-segments every dataset |
| 20 | Complete corrected ZED VIO/VIO-LC N=3 | `[~]` nine cells at N=1 (including one collapse); two ORB cells failed |
| 21 | Freeze Basalt VO configuration cohort | `[ ]` Rosario 0.03 versus remaining six cells 0.05 triangulation distance; review ZED shared calibration |
| 22 | Preserve/evaluate interrupted outputs and reconcile stale state | `[ ]` ZED OKVIS2 VO-LC run1 exported; three state files have stale running entries |
| 23 | Repair metric/reporting issues and exclude five smoke runs from headline discovery | `[ ]` see aggregation/reporting below before regeneration |

---

> **Historical note; current matrix above takes precedence.**
> **ZED2i TURN DETECTION (task 19, 2026-08-06, machine B):** the "2 pseudo-row segments / 0 turns"
> symptom was **not** a turn-angle threshold problem. `_segment_trajectory.py` derived heading from
> the GT quaternion, but the ZED2i GT is built from GPS position only — every row carries an
> **identity quaternion**, so yaw was constant 0 deg and no turn could ever be detected. Fix: a
> `yaw_from_path()` fallback that derives heading from the path tangent (2 m smoothing window) when
> the GT orientations are all identity. Verified neutral for rosariov2/hortimulti/euroc (those have
> real orientations, so the fallback never fires). ZED2i also needs `--min_seg_path_m 5` (the 25 m
> default merges its short 6-row pattern). Result: **15 segments {10 row, 5 turn}** (was 2 row / 0
> turn), and all 18 zed2i runs now report both row and turn ATE — e.g. ORB-SLAM3 VO 0.292 m row /
> 0.283 m turn, Basalt 0.448 / 0.642, DPVO 12.24 / 20.02.
>
> Two related issues found and **deliberately not fixed** (brief rule 5 — no improvised pipeline
> changes):
> 1. **`merge_segments` coalescing bug** — adjacent same-type segments are not merged. Fixing it
>    changes segmentation repo-wide (rosariov2 seq1 107 -> 43 segments, hortimulti 25 -> 14,
>    euroc 0 -> 11) and would require re-evaluating every rosariov2 run, which rule 3 forbids on
>    this machine. A `NOTE` documenting this sits at the call site.
> 2. **`datasets/rosariov2/sequence1/segments_auto.csv` is stale** relative to that sequence's
>    repaired PGT ground truth. Not regenerated here (rule 3).

> **Historical note; counts and metrics below describe July, not current artifacts.**
> **ORB-SLAM3 VO NATIVE (2026-07-31, this machine):** the submodule builds and runs natively (no
> Docker) - `src/ORB_SLAM3/Examples/Stereo/stereo_euroc` linked against a local Pangolin, driven by
> `run_orbslam3.sh`. The agricultural/EuRoC VO cells were filled natively here. **The earlier
> "shim-vs-native divergence" was NOT a Docker artefact - it is ORB-SLAM3's inherent non-determinism
> on agricultural sequences.** Determinism check + 1200->2000 feature sweep (finding 11): EuRoC is
> deterministic (~0.05 m every run); str02 varies {1.85, 4.3, 21.1} m (scale collapses to 0.89,
> coverage 31-100%), seq1 {1.16, 3.0, 4.86} m, seq5 {4.0, 6.9, 14.8} m across N=3 - a config cannot
> fix it. str03 alone is stable (0.11 m x3). So agri cells are recorded as **N=3 median (range)**;
> the old 0.893 m / 1.18 m references were single lucky draws. EuRoC + ZED2i (0.256 m) stay N=1.
> `ORBSLAM3_CONFIG` env override added to the runner for config sweeps.
> OKVIS2/OKVIS2-X VO on agri sequences are best-effort (IMU off) and expectedly weaker than their VIO.

## Phase 2 per-algorithm tasks

### ORB-SLAM3

| Task | Status |
|---|---|
| VO-clean (LC-off) on rosariov2/seq1 N=3 | `[!]` N=0 complete evaluations; recovery crashes |
| VO-clean on hortimulti str02+03 N=3 | `[~]` str02 N=0 (crash); str03 N=3 evaluated |
| VO-clean on EuRoC MH_01/03/05 N=1 | `[x]` now N=3 on each |
| VIO rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| VIO-LC rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| VIO EuRoC MH_01/03/05 N=1 | `[x]` now N=3 on each |
| VIO-LC EuRoC N=1 | `[x]` now N=3 on each |
| ZED VIO / VIO-LC N=3 | `[!]` both N=0 complete evaluations; crashes |

### Basalt

| Task | Status |
|---|---|
| VIO rosariov2/seq1 N=3 | `[x]` N=3 evaluated |
| VIO EuRoC MH_01/03/05 N=1 | `[x]` now N=3 on each |
| VIO hortimulti (after IMU extraction) | `[x]` N=3 on both |
| hortimulti VIO scale collapse | `[x]` **FIXED via extrinsic correction** (was misdiagnosed as vibration floor; the 5-run noise sweep searched the wrong parameter). With rectified T_imu_cam: str02 22.9->2.49 m, str03 2.85->0.19 m, scale 0.57->1.03. |
| ZED corrected VIO N=3 | `[~]` N=1; run2/run3 needed |
| VO configuration consistency | `[~]` all eight cells N=3, but six retain 0.05 versus current 0.03 triangulation distance |

### OpenVINS

| Task | Status |
|---|---|
| VIO rosariov2/seq5 N=3 | `[!]` N=0 complete evaluations; recovery needed |
| VIO EuRoC MH_01/03/05 N=1 | `[~]` MH01/MH03 N=0; MH05 N=1 (two repeats needed) |
| VIO hortimulti (after IMU extraction) | `[!]` extraction/config fix done; neither current cell has a complete evaluation |
| ZED corrected VIO N=3 | `[~]` N=1 collapse; preserve outcome, run2/run3 missing |

### AirSLAM

| Task | Status |
|---|---|
| VIO rosariov2/seq1+seq5 N=3 | `[x]` N=3 on both |
| VI-SLAM (VIO-LC) rosariov2 N=3 | `[x]` N=3 on both |
| VIO/VI-SLAM hortimulti (after IMU extraction) | `[x]` N=3 on both sequences/modes |
| VIO EuRoC MH_01/03/05 N=1 | `[x]` now N=3 on each |
| hortimulti str02/str03 scale collapse | `[x]` **FIXED**: extrinsic was inverted AND missing rectification. str02 46.3->5.30 m, str03 16.3->1.24 m, scale ~1.0. (Also recovered lost `vio_euroc.launch`; TensorRT needed a host reboot after a driver update.) |
| ZED corrected VIO / VIO-LC N=3 | `[~]` each N=1; run2/run3 missing |

### OKVIS2

| Task | Status |
|---|---|
| Scale seq1+seq5 to N=3 | `[x]` N=3 for VO, VO-LC, VIO and VIO-LC |
| Add hortimulti + EuRoC configs | `[x]` |
| VIO EuRoC MH_01/03/05 N=1 | `[x]` now N=3 on each |
| hortimulti failure | `[x]` **FIXED via extrinsic correction** (the tracking failures were largely self-inflicted by the wrong extrinsic, not greenhouse texture). str02 49.9->2.14 m, str03 15.5->0.40 m, scale 0->1.03. Independent check: freshly-built binary + config patched hours earlier. |
| ZED VO-LC N=3 | `[~]` N=0 evaluated; run1 exported, run2 killed, run3 absent |
| ZED corrected VIO / VIO-LC N=3 | `[~]` each N=1; two repetitions missing |

### OKVIS2-X

Source and result integration exists independently of OKVIS2. The top-level build, run and
GPS-conversion automation is committed; repeated VO/VIO results now exist through the
server runners. Remaining gaps are shown in the matrices above.

| Task | Status |
|---|---|
| Source submodule/gitlink pinned (`src/okvis2x`) | `[x]` |
| Reproducible top-level build script (`build_okvis2x.sh`) | `[x]` |
| Top-level multi-mode runner (`run_okvis2x.sh`) | `[x]` (all five run types; `OKVIS2X_CONFIG` override for sweeps) |
| Configs for rosariov2 / EuRoC / HortiMulti / ZED2i | `[x]` (40 files, including experimental `vo_lc`) |
| gnss-vio configs (rosariov2 seq1+seq5) | `[x]` |
| `gps.csv` -> `mav0/gps0/data_raw.csv` converter | `[x]` |
| Register in eval pipeline (LOG_PATTERNS, plot dicts) | `[x]` |
| Measure `r_SA` (GNSS antenna lever arm) on the robot | `[~]` nonzero lever arms configured; verify provenance and rerun historical GNSS cohort |
| First gnss-vio runs (rosariov2 seq1+seq5) | `[x]` historical N=1 results exist; no server GNSS repeats |
| Reproduce VO/VIO results through `run_okvis2x.sh` | `[x]` VO N=3 all eight; VIO N=3 seven core + corrected ZED N=1 |
| Manual N=1 VIO results | `[x]` superseded by server N=3 core and corrected ZED N=1 |
| Recover HortiMulti IMU + GPS from hortimulti.zip | `[x]` (str02 190493/7620, str03 48448/1939 - counts match bag) |
| HortiMulti gnss_vio configs | `[x]` configs and historical N=1 results exist |
| Head-to-head OKVIS2 vs OKVIS2-X on rosariov2 vio | `[x]` seq1: OKVIS2 18.89 / OKVIS2-X 18.89; seq5: 20.29 / 20.40 - near-identical (shared estimator core) |
| ZED VO-LC N=3 | `[!]` N=0 complete evaluations; latest recovery stopped near initialization |
| ZED corrected VIO / VIO-LC N=3 | `[~]` each N=1; run2/run3 missing |

### MASt3R-SLAM

| Task | Status |
|---|---|
| Download checkpoints | `[x]` 2.9 GB, Naver Labs direct URLs (see setup.md §10) |
| Build env (CUDA 12.1 nvcc, vendored dust3r/in3d, numpy/opencv pins) | `[x]` |
| Port runner to upstream API (`--save-as`, `--calib`, retrieval.k) | `[x]` |
| Smoke test | `[!]` historical 12 GB OOM; reported server slowness needs retained trial evidence |
| VO / VIO-LC runs on agri sequences | `[ ]` deferred/excluded from current campaign; supported visual tracks are VO / VO-LC (no VIO) |

> Historical setup observations on the earlier machine (not current server measurements): MASt3R-SLAM
> keeps every keyframe on-GPU with no supported bound (`local_opt.window_size` is read
> but never applied upstream; `dataset.img_downsample` breaks the fixed-512 checkpoint;
> `dataset.subsample: 2` still OOM'd on rosariov2). Checkpoints are CC-BY-NC-SA-4.0.

### MegaSaM

| Task | Status |
|---|---|
| Checkpoints (megasam_final, DepthAnything, RAFT) | `[x]` automated in `setup_megasam_env.sh` |
| Build vendored CUDA extensions (`lietorch`, `droid_backends`) | `[x]` needs cuda-nvcc 11.8 + `setuptools<81`; `python setup.py install` (not `pip -e`) |
| Runtime deps (torch_scatter, xformers, huggingface_hub, `numpy<2`) | `[x]` |
| Port runner to the real 3-stage pipeline | `[x]` was calling a non-existent `megasam.demo` module |
| Grayscale workaround for UniDepth stage | `[x]` PIL mis-slices mode-`L` images; runner feeds it an RGB copy |
| First end-to-end run (hortimulti str03) | `[~]` historical partial pipeline check; not currently running; excluded from campaign |
| Runs on remaining sequences | `[ ]` |
| zed2i config | `[ ]` |

> Upstream has no single entrypoint: Depth-Anything -> UniDepth -> camera tracking, each a
> separate script with hard-coded demo paths. Stage 3 (`cvd_opt`) refines depth only and is
> skipped. Cost is three ViT-scale passes per frame, so budget hours per sequence.
> Monocular: comparable under Sim(3) only.

### DPVO / DPV-SLAM (replaces DROID-SLAM)

| Task | Status |
|---|---|
| Setup script, configs and runner | `[x]` |
| DPVO VO N=1 on all 8 sequences | `[x]` now N=3 on all eight |
| DPV-SLAM VO-LC N=1 on all 8 sequences | `[x]` now N=3 on all eight |
| Keep DPV-SLAM out of true VIO-LC bucket | `[x]` moved out of `results-vio-lc/` |

### VO-LC Candidates

| Task | Status |
|---|---|
| OKVIS2 VO-LC full N=1 (all 8 sequences) | `[~]` seven non-ZED N=3; ZED run1 recovered/evaluated, r2 interrupted, r3 missing |
| OKVIS2-X VO-LC full N=1 (all 8 sequences) | `[~]` seven non-ZED N=3; ZED N=0 complete evaluations |
| ORB-SLAM3 runner + configs for rosariov2/hortimulti/EuRoC/zed2i | `[~]` seven cells N=3; Rosario seq1 retains observed r1 startup failure |
| MASt3R-SLAM runner + configs for rosariov2/hortimulti/EuRoC | `[x]` scaffolded; excluded from current campaign |
| AirSLAM VO-LC | `[x]` visual-only LC now implemented; N=3 all eight |
| OV2SLAM VO full N=1 (str02/MH_01/MH_03 filled) | `[x]` now N=3 all eight, including ZED |
| OV2SLAM VO-LC full-sequence runs | `[x]` N=3 all eight; Rosario seq1 run2 collapse retained |

### OV2SLAM

| Task | Status |
|---|---|
| Accuracy-first configs (`force_realtime: 0`; server metadata records 1.0 replay) | `[x]` |
| VO N=1 on Rosario seq1+seq5, EuRoC MH_05 and HortiMulti str03 | `[x]` 7.236 m / 8.045 m / 0.099 m / 0.351 m Sim3 ATE |
| Complete VO N=1 sweep on the remaining four standard sequences | `[x]` N=3 all eight; see matrix for coverage caveats |

### Voxel-SVIO

| Task | Status |
|---|---|
| Docker image + container build (`scripts/setup/setup_voxel_svio_docker.sh`) | `[x]` (NOTE: setup guard skips clone if `src/voxel_svio/` exists even when empty - source must actually be present) |
| Configs: euroc_mav (per-seq), rosariov2, hortimulti | `[x]` |
| Run script (`scripts/run/run_voxel_svio.sh`) + ROS1 data player | `[x]` |
| Smoke test EuRoC MH_01_easy N=1 | `[x]` (0.083 m; earlier 3.03 m row was a stale bad run) |
| VIO rosariov2/seq1+seq5 N=3 | `[x]` N=3 both |
| VIO hortimulti str02+str03 N=3 | `[x]` N=3 both |
| VIO EuRoC MH_01/03/05 N=1 -> N=3 | `[x]` N=3 each |
| ZED corrected VIO N=3 | `[~]` N=1; run2/run3 missing |

---

## Aggregation and reporting

| Task | Status |
|---|---|
| Rebuild `benchmark-vo.csv` after ORB-SLAM3 VO-clean results land | `[x]` current 192 planned rows; unresolved ORB attempts remain visible |
| Rebuild `benchmark-vio.csv` after N=3 runs (Basalt/ORB-SLAM3/OpenVINS) | `[x]` current 168 planned rows; missing repetitions are explicit |
| Add MASt3R-SLAM to applicable CSVs | `[ ]` deferred scope extension, not a missing N=3 obligation |
| Generate segment maps for all new Phase 2 sequences | `[ ]` |
| Final cross-algo ATE plots (VO vs VIO per sequence) | `[~]` all-mode figures label 45 clean EuRoC N=3 cells, limited claims and material agricultural/GNSS blockers |
| Explicit claim acceptance and stable regeneration | `[x]` evidence-pinned ledger; 45 clean N=3 cells; EuRoC numbers retained, Rosario frame conversion corrected |
| Capture actual native exits and validate repaired execution | `[!]` OV2/Voxel shutdown errors found despite wrapper zero; native diagnostic execution remains unauthorized |
| Thesis-ready LaTeX table | `[ ]` |
| Exclude five COMPLETE smoke artifacts from headline discovery | `[x]` explicit campaign membership; all smoke/historical evidence retained |
| DPVO metric labeling and mixed-status / failure counts | `[x]` monocular Sim(3), metric SE(3); failures and planned denominators retained |
| RPE, GNSS origin alignment, ZED orientation and sparse-output coverage semantics | `[x]` corrected definitions, unsupported metrics withheld; 593 evaluations reconciled |
| GT/segmentation cache freshness and deferred segment coalescing | `[x]` hash-bound inputs and corrected geometric segment generation |
| Refresh all CSVs, tables/claims, figures and browser together | `[x]` 666 CSV rows, 226 cell/variant summaries, 690 browser entries; failures remain explicit |
| Freeze source/config/binary provenance and declare final N / GNSS scope | `[!]` future N=3 scope frozen; exact historical rebuild gaps disclosed, future native readiness unverified |

---

## Dropped / out of scope

| Algorithm | Reason |
|---|---|
| DROID-SLAM | Historical exclusion retained. Original attribution is documented in the audit; saved results are under `results/vo/`, outside campaign comparisons. |
| Stella-VSLAM | "Mostly reimplementation of ORB-SLAM3, adds nothing" (supervisor). |
| VINS-Fusion | Overlaps Basalt + OpenVINS; ROS1 only. |
| SVO Pro Open | ROS1 Melodic only; frozen toolchain. |
| DSO / Stereo-DSO | Misaligned with stereo-IMU direction. |
| cuVSLAM | Closed-source (NVIDIA). Cite KITTI numbers only. |
| Kimera-VIO | Overlaps OpenVINS. |
| MegaSaM | Excluded from the current and future campaign manifest; old memory failures do not establish a 4090 limit. |

---

## Adding a new algorithm

Complete the current matrix gaps and reporting repairs before expanding scope.

1. Build / containerize under `src/<algo>/`.
2. Write `scripts/run/run_<algo>.sh` with signature `<dataset> <seq> [run_id=1] [run_type=vo]`.
3. Write config(s) under `configs/<algo>/`.
4. Add a row to each table above.
5. Smoke-test on EuRoC MH_01_easy first.

## Adding a new dataset

1. Write extraction script in `scripts/data/`.
2. Create `docs/private/dataset-specific/dataset_<name>.md`.
3. Extract to `datasets/<name>/<seq>/mav0/` with standard layout.
4. Add a column to each table above.

---

## DONE (Phase 1 - VO benchmark)

> Historical Phase 1 record. The unchecked items below are retained history, not
> current campaign obligations. IMU extraction and later runs have occurred; exclusions
> persist. The current run status and exact required actions are in the matrices above.

All Phase 1 VO runs are complete (N=3) and evaluated. See PROGRESS.md Phase 1 for the full
results table. Summary:

- ORB-SLAM3 (LC-on): rosariov2 seq1+seq5, hortimulti str02+str03 - results in `obsolete/` (LC-on confound)
- Basalt VO: all agri + EuRoC - done-N3 / done-N1
- MAC-VO: all agri + EuRoC - done-N3 / done-N1
- AirSLAM VO: all agri + EuRoC - done-N3 / done-N1
- DROID-SLAM: all agri + EuRoC - done-N3 / done-N1
- OKVIS2 VO: rosariov2/seq1+seq5 - done-N1

Kept as Phase 2 restructure (Phase 4.5):
- [ ] Rebuild ORB-SLAM3 with loop closure disabled (or wire up the
      stereo-inertial example) so it slots back into `vo` / `vio` / `vio-lc`.
- [ ] Re-run AirSLAM with `run_type=vio` and `vio-lc` on Rosario v2 and
      HortiMulti once `mav0/imu0/data.csv` is available for both datasets.
- [ ] Re-run Basalt with `run_type=vio` on Rosario v2 and HortiMulti.
- [ ] Extract IMU streams: HortiMulti needs `mav0/imu0/data.csv` from the
      `/ms/imu/data` topic (`scripts/data/_hortimulti_extract.py`).
      Rosario v2 needs the same generated from its `imu.csv`.
- [ ] Download MegaSaM checkpoints, run on EuRoC sanity sequence, then on
      Rosario / HortiMulti (`run_type=vo`).
- [ ] Download MASt3R-SLAM checkpoints, run on EuRoC sanity sequence, then
      on the agricultural sequences (`run_type=vo` and `vo-lc`).
- [ ] Add a `vio_slam` ORB-SLAM3 binary path and configs once the build
      lands.

## How to read this file

- `[x]` = done   `[ ]` = pending   `[~]` = partially done / blocked
- Sections are organised by **dataset → algorithm**; add new blocks using the
  same template when extending to more algorithms or datasets.
- The **cross-algorithm comparison** section at the bottom is filled after
  every algorithm on a dataset is complete.

---

## Standard vSLAM benchmarking pipeline (reference)

See [evaluation](docs/evaluation.md) for current implementation limitations: translation
uses point-distance residuals, and rotational accuracy needs valid orientation GT.

The community-standard evaluation workflow (Sturm 2012, TUM RGB-D; Geiger 2012,
KITTI; Grupp 2017, evo) has the following stages:

1. **Data prep** — extract bag → EuRoC layout (`cam0/`, `cam1/`, `times.txt`),
   create `gt_tum.txt` in TUM format (timestamp tx ty tz qx qy qz qw, seconds).
2. **Algorithm config** — write a correctly-named YAML config file for each
   (algorithm, dataset) pair; verify all required parameters are present.
3. **Run** — execute the algorithm, capture trajectory + runtime metadata
   (FPS, peak GPU MB); save to `results/<type>/<dataset>/<seq>/<algo>/`.
4. **Timestamp normalisation** — ensure all estimated trajectories use
   second-epoch timestamps matching the GT file's epoch.
5. **ATE / APE** (`evo_ape`) — absolute trajectory error after rigid SE(3)
   alignment; primary global accuracy metric.  Report RMSE and mean.
6. **RPE** (`evo_rpe`) — relative pose error over a fixed window (~1 s);
   measures local drift.  Report RMSE of translational and rotational error.
7. **Coverage** — inspect time support and tracking outages. Output-pose count divided
   by input-frame count measures output rate, not reliable trajectory coverage.
8. **Runtime metrics** — wall-clock FPS, peak GPU memory, CPU usage.
9. **Multi-run benchmark** — run algorithm N times (N=3); `run_orbslam3.sh <dataset> <seq> <run_id>`.
10. **Per-run evaluation** — `scripts/eval/_evaluate_run.py <dataset> <seq> <algo> <run_id>` → `run_eval.json`.
11. **Aggregate runs** — `scripts/eval/_aggregate_runs.py <dataset> <seq> <algo>` → `metrics.csv`, `report.md`.
12. **Segment visualisation** — `scripts/eval/_plot_segments.py <dataset> <seq>` → `segment_map.png`.

---

## Phase 0 – Infrastructure

> Historical implementation checklist. Current evaluation limitations are tracked above.

| Task | Status |
|---|---|
| Clone + build ORB-SLAM3 (UZH upstream) | `[x]` |
| Patch ORB-SLAM3 for C++14 (sigslot) | `[x]` |
| Fix ORB-SLAM3 `Rectified` null-ptr bug (`Settings.cc`) | `[x]` |
| Build Pangolin v0.9.5 | `[x]` |
| Install `evo` evaluation toolkit | `[x]` |
| Script layout: `build/`, `data/`, `run/`, `eval/` | `[x]` |
| `run_orbslam3.sh` — multi-run with resource monitoring | `[x]` |
| `_resource_monitor.py` — GPU+CPU+RAM every 1s | `[x]` |
| `_interpolate_gt.py` — sparse GT → camera timestamps (Slerp) | `[x]` |
| `_segment_trajectory.py` — **v2: 2 m sliding-window path-length, 10° heading / 20 cm chord deviation** | `[x]` |
| `_evaluate_run.py` — full per-run evaluation (ATE Sim3 + **SE3**) → `run_eval.json` | `[x]` |
| `_aggregate_runs.py` — N runs → `metrics.csv` + `report.md` (Sim3 + SE3 columns) | `[x]` |
| `_plot_segments.py` — **8 K segment map, 3 hierarchies (per-run, per-algo, cross-algo)** | `[x]` |
| `run_benchmark.sh` — one-shot pipeline: run N times + interpolate GT + segment + evaluate + aggregate | `[x]` |
| RPE metric: use `point_distance` not `trans_part` (frame mismatch fix) | `[x]` |
| **Sim(3) vs SE(3) reporting**: both alignments computed every run | `[x]` |
| **Body↔camera mount mismatch documented** (Strawberry-03 RPE rot artefact) | `[x]` |
| `run_droidslam.sh` / `run_macvo.sh` upgraded to **multi-run framework** (`<run_id>` arg, `_resource_monitor.py`) | `[x]` |
| DROID-SLAM conda env (`droidenv`) | `[x]`; lietorch, torch_scatter, droid_backends all built |
| MAC-VO conda env | `[x]`; `macvo` env created; models downloaded |
| **Basalt binary install** (`~/.local/bin/basalt_vio`, v0.1.7) | `[x]`; Binary installer for Ubuntu 22.04; sources `~/.basalt/env` |
| `run_basalt.sh` | `[x]`; EuRoC format, auto-generates `mav0/cam*/data.csv`, `--use-imu false` |
| `configs/basalt/hortimulti_calib.json` + `rosariov2_calib.json` + `vo_config.json` | `[x]`; Pinhole + `vio_min_triangulation_dist: 0.03` |
| **AirSLAM Docker** (`air_slam` container, `xukuanhit/air_slam:v4`) | `[x]`; Docker Engine + nvidia-container-toolkit; catkin_make inside container |
| `scripts/setup/setup_airslam_docker.sh` | `[x]`; One-shot pull + create + build |
| `run_airslam.sh` | `[x]`; Polls `trajectory_v0.txt`, `pkill roslaunch`, `mv -f`, FPS from input frames |
| `configs/airslam/{hortimulti,rosariov2}_{camera,vo}.yaml` | `[x]`; Per-dataset intrinsics + TRT engine name |

---

## Phase 1 – Dataset: Rosario v2

> Historical experiments and values; superseded as current status by the matrices above.

> Agricultural field rows, stereo + GPS GT, 15 fps, 1280×720.
> Full sequence 1 = 13 821 frames, ~18 min.
> Official evaluation: https://github.com/CIFASIS/rosariov2

### 1-A  Data preparation

| Task | Status |
|---|---|
| `scripts/data/convert_rosario_to_tum.sh` — OOM-safe streaming extractor | `[x]` |
| Extract sequence 1 (13 821 frames) | `[x]` |
| `gt_tum.txt` present (GPS PGT, second-epoch timestamps) | `[x]` |
| Extract sequence 5 (11 640 frames) | `[x]` |
| Extract sequences 2–4 (if needed) | `[ ]` |

### 1-B  ORB-SLAM3

| Task | Status | Notes |
|---|---|---|
| Config `configs/orbslam3/rosariov2_stereo.yaml` | `[x]` | Rectified, fx=648.86 |
| Run full sequence 1 (single, old format) | `[x]` | 13 821 frames, 12.55 fps, 1101 s |
| ATE on sequence 1 (old single run) | `[x]` | **RMSE 1.361 m**, mean 1.311 m |
| RPE (15-frame window) on sequence 1 | `[x]` | trans RMSE **0.115 m**, rot RMSE **3.56 °** |
| Interpolate GT for seq1 (`gt_interp_tum.txt`) | `[x]` | 13821 poses at camera timestamps |
| Auto-segment seq1 (`segments_auto.csv`) | `[x]` | 145 segs: 125 row (863 s), 20 turn (60 s) |
| **Run seq1 × 3 (multi-run benchmark)** | `[x]` | ATE 1.176 ± 0.317 m, 100%, 5-6 loops |
| **Evaluate + aggregate seq1 × 3** | `[x]` | `metrics.csv` + `report.md` + `segment_map.png` done |
| Run sequence 5 (single, old format) | `[x]` | 11 640 frames, 11.55 fps, 1008 s, 100% completion |
| Evaluate sequence 5 (old single run) | `[x]` | **ATE RMSE 8.274 m** (Sim3 alignment) |
| Interpolate GT for seq5 (`gt_interp_tum.txt`) | `[x]` | 11640 poses at camera timestamps |
| Auto-segment seq5 (`segments_auto.csv`) | `[x]` | 101 segs: 95 row (756 s), 6 turn (19 s) |
| **Run seq5 × 3 (multi-run benchmark)** | `[x]` | ATE 20.207 ± 4.204 m, 91% avg, 0 loops |
| **Evaluate + aggregate seq5 × 3** | `[x]` | `metrics.csv` + `report.md` + `segment_map.png` done |
| Segment map visualisation seq1 | `[x]` | `results/rosariov2/sequence1/segment_map.png` |
| Segment map visualisation seq5 | `[x]` | `results/rosariov2/sequence5/segment_map.png` |
| Run remaining sequences | `[ ]` |  |
| Evaluate remaining sequences | `[ ]` |  |

### 1-C  DROID-SLAM

| Task | Status | Notes |
|---|---|---|
| Set up conda env + install dependencies | `[x]` | torch 2.7+cu126, lietorch 0.2, torch_scatter 2.1.2 |
| `scripts/run/run_droidslam.sh` + `_droid_demo_wrapper.py` | `[x]` | stereo, TUM trajectory output |
| `configs/droidslam/rosariov2.txt` intrinsics file | `[x]` | fx=fy=648.86, cx=645.01, cy=348.24 |
| `droid.pth` pretrained weights | `[x]` | downloaded to `src/DROID-SLAM/` |
| Run sequence 1 | `[x]` | full sequence (6911 frames, stride=2), skip_backend |
| Evaluate sequence 1 | `[x]` | **ATE RMSE 45.05 m** (Sim3 alignment) |
| Sequence 5 trajectory | `[x]` | 3 runs provided by collaborator; timestamps converted ns→s |
| Evaluate sequence 5 | `[x]` | **ATE RMSE 50.02 m** (Sim3, mean of 3 runs) |

### 1-D  MAC-VO

| Task | Status | Notes |
|---|---|---|
| Set up conda env + install dependencies | `[x]` | `macvo` env created; models downloaded |
| `scripts/run/run_macvo.sh` | `[x]` | fixed: conda set-u, upstream odom config, `--useRR`, correct Results path |
| `configs/macvo/rosario_v2_sequence.yaml` | `[x]` | GeneralStereo format; intrinsics=648.86, bl=0.04973; `left/right` symlinks created |
| Run sequence 1 | `[x]` | 13821 frames, 100% completion |
| Evaluate sequence 1 | `[x]` | **ATE RMSE 13.277 m** (Sim3 alignment) |
| `configs/macvo/rosariov2_sequence5.yaml` | `[x]` | same intrinsics/bl; root→sequence5; `left/right` symlinks created |
| Run sequence 5 | `[x]` | 11 640 frames, 100% completion (3 runs done) |
| Evaluate sequence 5 | `[x]` | **ATE RMSE 19.384 ± 0.006 m** (Sim3, 3 runs) |

### 1-E  Cross-algorithm comparison (Rosario v2)

| Task | Status |
|---|---|
| All four algorithms run on sequence 1 (single run) | `[x]` |
| ORB-SLAM3 + DROID-SLAM run on sequence 5 | `[x]` |
| MAC-VO on sequence 5 × 3 | `[x]`; ATE Sim3 **19.384 ± 0.006 m** (3 runs; scale=0.933, 100% tracking) |
| ORB-SLAM3 × 3 multi-run benchmark seq1 | `[x]`; ATE 1.176 ± 0.317 m, `report.md` + `segment_map.png` |
| ORB-SLAM3 × 3 multi-run benchmark seq5 | `[x]`; ATE 20.207 ± 4.204 m, `report.md` + `segment_map.png` |
| Segment maps for seq1 and seq5 | `[x]`; seq1 ✓, seq5 ✓ |
| `metrics.csv` + `report.md` for seq1 | `[x]`; done |
| `metrics.csv` + `report.md` for seq5 | `[x]`; done |
| Comparison table for thesis chapter | `[ ]`; Final LaTeX/PDF table for thesis |

### 1-F  Basalt (stereo VO)

| Task | Status | Notes |
|---|---|---|
| `configs/basalt/rosariov2_calib.json` | `[x]` | EuRoC format, pinhole, `vio_min_triangulation_dist: 0.03` |
| Run seq1 × 3 + evaluate | `[x]` | ATE Sim3 **14.279 ± 0.302 m**, SE3 **18.693 ± 0.586 m**, 100% |
| Run seq5 × 3 + evaluate | `[x]` | ATE Sim3 **15.035 ± 0.062 m**, SE3 **15.425 ± 0.068 m**, 100% |
| Segment maps with Basalt | `[x]` | seq1 + seq5 regenerated |

### 1-G  AirSLAM (deep-feature stereo VO)

| Task | Status | Notes |
|---|---|---|
| `configs/airslam/rosariov2_camera.yaml` + `rosariov2_vo.yaml` | `[x]` | 1280×720, baseline 0.04973m |
| TensorRT engine compiled for rosariov2 (1280×720) | `[x]` | Compiled on seq1 run1 startup |
| Run seq1 × 3 + evaluate | `[x]` | **DONE** (9.888 ± 0.059 m Sim3, 9.891 ± 0.058 m SE3, 100% × 3) |
| Run seq5 × 3 + evaluate | `[x]` | **DONE** (12.722 ± 0.991 m Sim3, 12.777 ± 1.014 m SE3, 100% × 3) |



---

## GNSS-VIO (stereo + IMU + GNSS) - `results-gnss-vio/`

> Historical infrastructure/experiment record. Use the GNSS matrix above for current
> artifact validation status; server GNSS repeats were excluded.

Phase F: GPS-aware algorithms with full Sim(3)+SE(3) eval pipeline.

Infrastructure status:
- [x] `run_type=gnss-vio` registered in `_paths.sh` and `_run_type.py`
- [x] `results-gnss-vio/` + `benchmark-gnss-vio.csv` wired into the eval pipeline
- [x] Shared GPS data players (`gnss_data_player.py` ROS 1, `gnss_data_player_ros2.py` ROS 2)
- [x] HortiMulti GPS extraction added to `_hortimulti_extract.py` (`--gps-only`,
      `--no-gps`, `--gps`); topic default `/antobot_gps`. Handles the upstream
      quirk where `header.stamp` is constant in `/antobot_gps` (falls back to
      bag-arrival time) and altitude is published in millimetres (auto-rescales
      when `max(alt) > 1000 m`).
- [x] CIFASIS GNSS-SI: clone + Dockerfile + setup script + configs for rosariov2
      seq1/seq5 + hortimulti str02/str03 + runner.
- [x] RTAB-Map: configs (rosariov2, hortimulti) + ROS 2 launch runner.
      `gnss_data_player_ros2.py` publishes `/cam{0,1}/camera_info` from per-dataset
      rectified intrinsics passed via `run_rtabmap_gps.sh`.
- [x] VINS-Fusion: clone + Dockerfile + setup script + configs for rosariov2
      seq1/seq5 + hortimulti str02/str03 (incl. per-cam YAMLs) + runner.
      Ceres pinned to `1.14.0` (2.1+ uses `std::integer_sequence`, incompatible
      with VINS-Fusion's hard-coded `-std=c++11`). All `CV_*` legacy macros are
      sed-rewritten to `cv::*` after `COPY src/VINS-Fusion` in the Dockerfile.
      HortiMulti `body_T_cam0` is `T_imu_cam0_raw @ blkdiag(R1.T, 1)` where
      `R1` comes from `cv2.fisheye.stereoRectify` in `_hortimulti_extract.py`.
- [x] OpenVINS+GPS: OpenVINS odometry + `robot_localization` EKF runner and four N=1 artifacts.
- [x] HortiMulti GPS extraction completed for str02/str03 (7620/1939 fixes;
      consumer-grade fixes with large vertical covariance).
- [x] CIFASIS GNSS-SI N=1 on rosariov2 seq1/seq5 + HortiMulti str02/str03; N=3 pending.
- [x] RTAB-Map N=1 on all four sequences; seq5 PPK is partial/nondeterministic; N=3 pending.
- [x] VINS-Fusion N=1 on all four sequences; N=3 pending.
- [~] OpenVINS+GPS N=1 on all four sequences; validate all rows and rerun HortiMulti with the
      corrected extrinsic before N=3.
- [x] Rosario sequence5 PPK-versus-conventional four-algorithm study completed.
