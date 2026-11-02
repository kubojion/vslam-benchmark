# Corrected CitrusFarm Rule C and Sielinko timing test: results

Commit `b653776` on `campaign/imu-timing-corrected-20261031`. Tables are generated from `results.csv`. Nothing here is in main, and promotion waits for the user.
Corrected CitrusFarm counts as the planned benchmark result once promoted. The Sielinko numbers do not.

## Summary

- **CitrusFarm:** all 102 runs finished. 9 of 10 systems are 6 of 6 ok in VIO, and 6 of 7 in VIO-LC. **AirSLAM fails everywhere**, 0 of 12 across VIO and VIO-LC.
- **3 + 1 lanes did not change results:** OpenVINS, Basalt and MASt3R-Fusion match the timing test, nearly all to three decimals.
- **Sielinko test verdict: partial.** 2 of 6 key systems recovered (OKVIS2, OKVIS2-X). AirSLAM could not be judged properly: it was killed at the memory cap.
- **The Sielinko control held:** OKVIS2 on the unchanged IMU collapsed, and on the corrected IMU reached 3.21 m.
- **Job 1 is done:** ORB-SLAM3 on 4 cores, 12 of 12 ok. These runs are the CitrusFarm ORB-SLAM3 result.
- **Job 2 is done, status pending:** the Sielinko recovery does not hold reliably at N=3. OKVIS2 is 2 of 3 ok, OKVIS2-X 1 of 3, and OpenVINS, ORB-SLAM3 and Voxel-SVIO 0 of 3. cuVSLAM went from 3 of 3 to 2 of 3 and from 12.36 to 18.68 m.

## CitrusFarm, per cell (ATE, m)

"Old" is the existing Rule C cell from `paper/generated/cells.csv`. Old VIO-LC AirSLAM has no terminal runs: these are the held slots. ORB-SLAM3 in this table is the 3-core result, replaced by Job 1 below.

{{cells}}

- OKVIS2 and OKVIS2-X on seq04 VIO read 2.54 and 2.19 m against the test's 2.04 and 2.03 m, and ORB-SLAM3 on seq07 VIO reads 2.01 m against 1.46 m. None of these is a regression-stop system.
- cuVSLAM was 12 of 12 ok. The collapse in the gate check run (59003) did not recur in these runs, so that one is 1 in 13.
- cuVSLAM stays worse on seq04 than old Rule C (4.15 against 2.84 m). OKVIS2-X and cuVSLAM on seq04 VIO-LC are also slightly worse.

## Regression check against the timing test

{{regress}}

## Failures and replacements

{{crash}}

- **AirSLAM VIO:** `scale_collapse` in all 6 runs, exit 0. A result, not retried.
- **AirSLAM VIO-LC:** seq07 failed all 3 repetitions with no trajectory: the native process exited 139 and the replacement crashed the same way, so they count as failures. On seq04, 3 of 3 end in `scale_collapse`, two of them after a crash and a clean replacement.
- **SVO Pro VIO-LC seq04 r1:** exit 134, replaced, the replacement was ok, so it is not counted as a failure.
- Job 2 attempts are in the same table, and discussed in its section.
- No infrastructure failures, no timeouts, no host reset. Every run with a trajectory recorded the intended IMU file by hash.

## Sielinko timing test

Corrected IMU: t_corrected = t - (22.189 ms + 0.0055755 ms/s × t), about 22 ms rising to 47 ms. Cohort `sielinko-timing-test-20261101`. N=1, default noise, not Rule C, never in benchmark tables.

{{sielinko}}

| Key system | Old Rule C | With correction | Recovered |
|---|---|---|---|
| OKVIS2 | 0 of 3 | ok, 3.21 m | yes |
| OKVIS2-X | 0 of 3 | ok, 2.07 m | yes |
| OpenVINS | 0 of 3 | `scale_collapse` | no |
| ORB-SLAM3 | 0 of 3 | `scale_collapse` | no |
| Voxel-SVIO | 0 of 3 | `scale_collapse`, twice | no |
| AirSLAM | 0 of 3 | no trajectory, killed at the 50 GiB cap, twice | no |

**Verdict under the fixed rule: partial** (2 of 6; works needs at least 3, fails at most 1). SVO Pro, not a key system, gave 0.99 m; old Rule C had it at 2 of 3 ok, 0.89 m.

- **Control:** OKVIS2 on the unchanged IMU (run 60008): `scale_collapse`, as required. The same system on the corrected IMU gave 3.21 m, which is the strongest single piece of evidence here.
- **OpenVINS online offset:** 0.66 ms at the end of run 60004, about 0 as predicted. That run diverged, so this is weak support.
- **Limit on this test:** every number is one run. The offset came from these same recordings, with correlation only 0.11-0.16. The gate passed only after one fit correction, and OKVIS2 Q4 at the limit (see `gates.md`).

## Why AirSLAM gave no trajectory on Sielinko

Both runs exited 137 at about 22-23 minutes, with Docker reporting `OOMKilled=true` at the 50 GiB cap. This is not caused by the harness: old Rule C used the same cap, peaked up to 49.9 GiB, and old run 20001 also ended 137. A fix would mean raising a memory cap, which the plan forbids, so **AirSLAM is left out of Job 2**.

## What went wrong on my side

- **A safety trip went unnoticed.** Update 3 says to stop launching if a safety check trips. The container's memory cap killed AirSLAM twice and the controller kept launching, because its OOM check read only its own scope, which cannot see a Docker container. I found it only on 1 Nov at night, reviewing the failure for Update 4. The cap itself worked and the host stayed safe. Exit 137 now stops launching.
- **A scientific failure was retried once.** Voxel-SVIO's run 60006 finished the recording and diverged; exit 143 is the node answering the runner's normal stop. The controller called that a crash and replaced it, costing 78 minutes. The replacement also collapsed, so the verdict is unchanged. This is fixed for Job 2.
- **Job 1 ran serially at first.** My one-run-per-system rule also held back ORB-SLAM3, which does not need it. I fixed that with no run active after 4 of 12 runs. Basalt in Job 2 had the same kind of problem: being alone, it waited for the lanes to clear, so its last two runs came at the end.
- **Time:** the campaign took about 14.5 h from release, not the 10 h expected, mainly because OKVIS2 VIO-LC took about 4 times as long as VIO. Hourly messages giving "x of 102 done" counted replaced attempts too, so they overstated progress slightly.

## Controller changes

Controller changes after launch are in `timing-campaign/run/controller-changes.md`, made with no run active and left uncommitted so HEAD stays at `b653776`. `scripts/` and `configs/` have not changed since launch.

## Job 1: ORB-SLAM3 on 4 cores

Finished 2 Nov, 12 of 12 ok, all validated. Cohort `timing-corrected-orbslam3-4core-20261101`, run IDs 51001-51003. As fixed before the runs, **these replace the 3-core ORB-SLAM3 runs as the CitrusFarm result, whatever they show.** The 3-core runs stay on disk.

{{orbcmp}}

Differences between the two are within or close to each cell's own spread, so core count did not clearly change ORB-SLAM3. The seq07 VIO median improved and its spread is wide, and seq04 VIO is slightly worse. Job 1's first 4 runs ran one at a time and the other 8 on both lanes, because of the controller rule noted in `run/controller-changes.md`.

## Job 2: Sielinko Rule C on corrected IMU

**Pending: not the Sielinko result until the user says so.** Finished 2 Nov at 15:01 CET, about 11 h after Job 1. Cohort `sielinko-corrected-rule-c-20261101`, run IDs 61001-61003, IMU file `0348ff1f`, 9 systems, N=3, 4-core lanes. AirSLAM is left out, see above. No judging rule was set for this job, so none is applied here.

{{job2}}

"Old" is the existing Rule C cell.

- **The correction helps OKVIS2 and OKVIS2-X sometimes, not reliably.** Both were 0 of 3 before. They are 2 of 3 and 1 of 3 now, where the single-run test showed both ok. This agrees with "partial", but the test's result was on the good side of the spread.
- **No change for OpenVINS, ORB-SLAM3 and Voxel-SVIO:** 0 of 3, all `scale_collapse`. ORB-SLAM3's r1 crashed with exit 139, and its replacement collapsed.
- **cuVSLAM is worse:** 2 of 3 ok, one collapse, and 18.68 m against 12.36 m. Old cuVSLAM was 3 of 3.
- **SVO Pro:** 2 of 3 ok, as before. r2 aborted with exit 134, and so did its replacement, so it counts as a failure. Median 1.09 m against 0.89 m.
- **Basalt and MASt3R-Fusion** are unchanged at 3 of 3: 0.44 m against 0.47 m, and 20.14 m against 19.74 m.
- **OpenVINS online offset:** 0.51 ms at the end of all three runs, about 0, but these runs diverged, so this is weak support.
- The Voxel-SVIO exit 143 runs were not replaced this time, and no exit 137 occurred. No infrastructure failures. Replacements were 2.

Every attempt:

{{job2runs}}
