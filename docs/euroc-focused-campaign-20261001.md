# Focused EuRoC OpenVINS / corrected AirSLAM campaign

> Historical completion checkpoint. Current tick semantics and publisher-thread diagnosis are in [the protocol review](protocol-review-20261002.md) and [diagnostic report](airslam-refinement-diagnostic-20261002.md).

Completed 2026-10-01 UTC (2026-10-02 local). Exactly **six missing OpenVINS VIO repetitions and 18 corrected AirSLAM VIO/VIO-LC repetitions** were executed once. Twenty-three have clean native exits and immediate schema-3 evaluations; one MH05 VIO-LC attempt retains a native refinement SIGSEGV before final export. No accuracy parameters were tuned, no production slot was retried, and no other dataset/algorithm path was run. No push occurred.

**All 45 previously accepted N=3 cells and all historical attempts are preserved.** The later [protocol review](protocol-review-20261002.md) supersedes the clean-success tick convention used at this checkpoint. AirSLAM supports sparse-keyframe accuracy; OpenVINS retains original run1 limitations and its separate implementation cohort. MH05 coverage is disclosed per repetition.

## Fixed scope and evidence

- OpenVINS: MH_01_easy, MH_03_medium and MH_05_difficult, physical/logical runs2–3. Original run1 remains, including native shutdown and coverage limits.
- AirSLAM VIO and VIO-LC: the same sequences, physical runs4–6 mapped to logical repetitions1–3 before production. Original affected runs1–3 stay in place.
- The fixed [24-action plan](../configs/campaigns/euroc-focused-20261001.json) and [AirSLAM selection](../configs/campaigns/euroc-focused-attempts-20261001.json) predate every production output. Selection is independent of score/outcome.
- [Execution validation](campaigns/euroc-focused-validation-20261001.json) pins every new raw artifact, source/input/runtime identity, configuration comparison and numerical evaluation digest. The [acceptance ledger](campaigns/paper-acceptance-20261001.json) records claim decisions separately.

## Repairs and configuration choices

AirSLAM now composes the IMU extrinsic with the inverse left-image rectification rotation: `T_body_rectified = T_body_raw * T_raw_rectified`. An executable verifier linked to the new library matches independent OpenCV composition within 1.55e-14; camera translation is unchanged. The new build is `/root/catkin_ws_rectified_20261001`, with source commit `1e0ad79`; the original workspace/binaries remain intact. A live first-full process map verifies the corrected executable/library was loaded. See [the rectification audit](airslam-rectification-audit.md).

OpenVINS native shutdown originally segfaulted after SIGINT even after repairing the player. Direct supervision exposed native exit -11, previously hidden by ROS launch exit zero. GDB located publisher destruction during global teardown after DDS resources had become invalid. Commit `7a496c5` drains background work and destroys the visualizer/state before static teardown. The isolated `openvins:humble-shutdown-20261001` image rebuilds those three files over the unchanged original image/dependencies. The original image remains available.

Both EuRoC runners supervise native exits directly and retain process ownership evidence. AirSLAM waits for map serialization before advancing; appearance of a trajectory alone no longer ends a stage. There is one refinement attempt, with no automatic retry. Process-state JSONs are readable by the host even when the container runs as root.

Every new saved numeric camera/IMU/estimator/refinement configuration equals its original run1 configuration. AirSLAM camera-comment corrections do not change values. OpenVINS retains benchmark-enabled author-supported dynamic initialization. The AirSLAM implementation repair, retry policy and native supervision are disclosed cohort differences. No test-set ATE was used to choose settings.

Production root HEAD was `b0617b57d1381fc6f27ee521f49aa1a4b0064547`. All 153 AirSLAM and 442 OpenVINS tracked build-source files matched their frozen checkouts. Prepared inputs, source archives and known binaries/models were checked before and after each attempt. Generic metadata linkage flags remain as originally recorded; independent build/native evidence supports the explicit review. Complete loaded-library closure was not independently captured for every repetition.

## Integration and full-sequence gates

The diagnostic input was the fixed first 40 seconds of MH01, with 801 stereo pairs and the original preceding IMU samples. Diagnostics have separate dataset names and never count toward N=3. VIO, VIO-LC refinement, native shutdown and output capture passed. A bounded OpenVINS interruption stopped its unique container; evaluation-only recovery preserved the consumed attempt without restarting estimation.

Diagnostic failures remain: the first subset used host-absolute image links unavailable in Docker; the second uses portable links to identical bytes. An AirSLAM attempt exposed root-owned metadata permissions. The original OpenVINS shutdown crashes and debugger reproduction remain preserved. None is silently turned into a production success.

The first complete MH01 repetition of OpenVINS VIO, AirSLAM VIO and AirSLAM VIO-LC was evaluated and inspected before the remaining batch. All attempts follow the unchanged native input policy; successful runs export finite monotonic trajectories and exit zero without forced kills. AirSLAM excludes MH05’s first image, 20 ms before its first IMU sample: 2,272 eligible images out of 2,273 dataset camera stamps. This is recorded upstream loader behavior, not a wrapper drop. AirSLAM IMU initialization and map completion are recorded, and the selected native stage export equals the evaluated file. Each evaluation or recorded no-final-export outcome completes before the next attempt starts.

## New repetitions and permitted claims

ATE values below are SE(3) RMSE in metres for these new repetitions only. They are not pooled with the historical implementations. Runtime is measured wrapper elapsed time, not processing latency or a real-time guarantee.

| Algorithm / mode | Sequence | New physical runs | ATE median (range), m | Dense export coverage | Successful-wrapper seconds, range | Claim |
|---|---|---|---|---|---|---|
| airslam / vio | MH_01_easy | 4, 5, 6 | 0.09896 (0.09895–0.09930) | unknown (keyframes) | 70.1–71.1 | 3 accepted_with_limitation |
| airslam / vio | MH_03_medium | 4, 5, 6 | 0.09902 (0.09892–0.09915) | unknown (keyframes) | 58.9–59.0 | 3 accepted_with_limitation |
| airslam / vio | MH_05_difficult | 4, 5, 6 | 0.07345 (0.07321–0.07492) | unknown (keyframes) | 43.9–44.0 | 3 accepted_with_limitation |
| airslam / vio-lc | MH_01_easy | 4, 5, 6 | 0.03876 (0.03876–0.03876) | unknown (keyframes) | 119.1–121.1 | 3 accepted_with_limitation |
| airslam / vio-lc | MH_03_medium | 4, 5, 6 | 0.02445 (0.02432–0.02445) | unknown (keyframes) | 112.2–114.1 | 3 accepted_with_limitation |
| airslam / vio-lc | MH_05_difficult | 4, 5, 6 | 0.05311 (0.05301–0.05320) | unknown (keyframes) | 69.1–70.0 | 1 valid_observed_failure; 2 accepted_with_limitation |
| openvins / vio | MH_01_easy | 2, 3 | 0.05863 (0.04965–0.06762) | 98.37–98.37% | 191.7–191.8 | 2 accepted |
| openvins / vio | MH_03_medium | 2, 3 | 0.13703 (0.13698–0.13708) | 95.85–95.85% | 142.8–142.8 | 2 accepted |
| openvins / vio | MH_05_difficult | 2, 3 | 0.19552 (0.19194–0.19911) | 94.10–94.15% | 120.8–120.9 | 2 accepted_with_limitation |

**Retained failure:** MH05 VIO-LC physical run4 exited -11 in the native refiner (wrapper139) after global optimization, while building the junction database. No final LC trajectory or final map was saved. Its existing odometry trajectory and map are preserved; a benchmark-evaluator diagnostic is in `results/euroc-focused-20261001/stage-diagnostics/action-21-odometry.json`. It is not substituted for an LC result. The root cause remains unresolved; later declared runs5–6 succeeded. The cell therefore has two final evaluations and one observed failure, not three successes.

AirSLAM VIO-LC reports the final offline-refined keyframe trajectory. Keyframe sparsity is not proof of tracking failure and cannot certify dense camera-frame coverage. OpenVINS run1 remains in its historical implementation cohort; new clean shutdowns do not erase its old recorded exit. These controls do not settle agricultural generalization.

## Reconciled outputs

The five root CSVs retain 666 selected/default-variant rows; `benchmark-historical-cohorts.csv` retains all 18 replaced AirSLAM rows. Each historical cell has its own report under `results/historical-cohorts/`. Original attempt folders remain intact and browsable. Tables, figures, acceptance handoff and all five TODO matrices use the same inventory. Green cells are unchanged.

Source captures previously split identical repetitions because their receipt JSONs contain timestamps. Cohort grouping now verifies capture hashes and compares stable source-tree/runtime content. Source/config/model/binary differences still separate cohorts; all historical cohort hashes remain unchanged.

Current checks and backup identities are in `results/euroc-focused-20261001/output-validation.json` and `final-backup.json`. The first 593 evaluations retain exactly the same numerical content; only their claim-review metadata is refreshed. New and diagnostic evaluations are staged and promoted with prior versions archived.

Validation passed 173 tests and three subtests. The preservation audit checks all
3,471 original raw-evidence files, 1,186 canonical/staged copies of the earlier 593
evaluations, and 579 historical existing-attempt CSV rows. Only declared cohort/cell
labels changed in those CSV rows. The browser contains 716 records and 722 pages;
all 15,060 local links resolve. All five TODO matrix layouts and 45 green cells are
unchanged.

## Preservation and remaining work

The prior complete backup is `/data/imoroz/vslam-repair-backups/20261001T204310Z-reference-complete`. The verified preproduction backup is `/data/imoroz/vslam-repair-backups/20261001T220304Z-euroc-before-production`: 1,195 independent files and verified root/AirSLAM/OpenVINS Git bundles. Final independent preservation includes the new attempts and reconciled outputs; see its recorded location above. Historical author hashes remain historical and the rewrite mapping is unchanged.

The focused campaign has no remaining execution slots. The MH05 AirSLAM native refinement segfault is a concrete unresolved issue; later diagnostics localized a reproduction to its asynchronous map publisher; its failure remains an outcome, not a request to resample for success. Other native paths still need their own validation; agricultural projection/reference/timing, GNSS and ZED serial/physical-quality prerequisites remain as listed in [the handoff](acceptance-handoff-20261001.md). The field ZED clock offset remains unknown and uncorrected; the benchmark sensitivity check closes it only as a disclosed limitation. No additional run, algorithm expansion, history rewrite or push is authorized.
