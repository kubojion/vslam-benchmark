# Sielinko CPU extended search (RUN-PLAN Phase 4): protocol and procedure

Branch `experiment/sielinko-cpu-search-20261022`, from main `ad1470c`, in the checkout
`/data/imoroz/vslam-sielinko-search-20261022`. It is a separate, labelled oracle result,
never a Rule C ranking. Nothing has run yet.

## Protocol
- **Estimators:** ORB-SLAM3, OKVIS2, OKVIS2-X, OpenVINS, Voxel-SVIO, SVO Pro and Basalt, all in VIO.
- **Split:** at the recording's time midpoint.
  - The first half (0–2314.6 s, 23,141 frames) is the only material selection sees.
  - Two 180 s clips come from it: its start, and the window starting at its own midpoint
    (1157.3 s).
  - The second half (23,142 frames) and the full run are the final test sequences.
- **Reference:** the GNSS reference keeps 97–99 % support on both halves (197 m and 207 m of
  path) and on both clips (16 m each).
- **Stages, per estimator:** the same as the earlier CPU searches (cpu15/cpu6), with the same seeds
  and counts.
  1. Preliminary: 16 TPE proposals on both clips, then the top 2 at N=3.
  2. Screen: 2 seeds × 16 proposals on both clips.
  3. Full: 6 seeded + 6 TPE proposals on the first half.
  4. Repeated selection: the top 2 plus the controls at N=3 on the first half.
  5. Final: the selected setting, fresh N=1, on the second half and on the full run.
- **Score:** unchanged. 10 × failures + 0.5·mean + 0.5·max of [RMSE/(path+RMSE) + unsupported
  export], with the 90 % export gate.
- **Controls** (enqueued first in every stage):
  - Rule C engine-off (the production configs);
  - engine-on (`configs/sensitivity/zed2i-engine-on-20261021`);
  - the historical envelope (g 0.0195, a 0.18, bg 7.400196e-4, ba 0.0202).
- **Bounds**, per component: [min(controls)/10, max(100 × Rule C, 3 × engine-on, 3 × envelope)],
  never changed after the start.
- **Files:**
  - the draft protocol: `configs/experiments/sielinko-cpu-search-20261022.json`;
  - the reference selectors: `configs/references/zed2i_field1_sielinko_*.json`, which use the exact
    parent window offset (`parent_offset`).

## Execution
- **Lanes:**
  - lane 1 = cores 0–3, lane 2 = cores 4–7, each with 50 GiB and no swap;
  - exclusive = cores 0–7, for Basalt.
- **Scheduling:**
  - One study per lane at a time. Within a study, attempts stay serial (ask, measure, tell).
  - Voxel-SVIO keeps lane 2, because its private container is pinned there.
  - Basalt starts last, alone.
- **Pinning:**
  - Host processes use `taskset`. This user cgroup has only memory and pids, so `AllowedCPUs`
    would be ignored.
  - Docker estimators get `--cpuset-cpus` and `--memory` from the lane (`_docker_limits.sh`).
  - The private Voxel container carries the lane's CPU set.
  - A sampler checks every attempt: thread affinity, container CPU set and, for Basalt, that
    nothing else runs.
- **Launch gate:**
  - at least 40 GiB free;
  - no other benchmark run on the lane's cores;
  - nothing launches while any Basalt run is active;
  - Basalt itself launches only with no run and no GPU job on the host.
- **A run is recognised by its wrapper process** (`scripts/run/run_<algorithm>.sh`, from any
  checkout), so other controllers need no shared registry to follow the same rule.
- **Estimated cost:** ≈135 h of runs: ≈64 h on two lanes plus ≈6 h of Basalt alone.

## Procedure (each step needs the user's go)
1. **Lane owner (Rule C runner):**
   - creates `results/.locks/cpu-lane-1.lock` and `cpu-lane-2.lock` in main;
   - when Rule C CPU is done, writes the handover (format below).
2. **Preparation, without runs:**
   - `scripts/setup/prepare_sielinko_private_sources.py` copies the private source/build trees;
   - `scripts/setup/create_sielinko_search_voxel_container.sh` creates the private Voxel container;
   - `scripts/analysis/prepare_sielinko_search.py views` builds the recording views.
3. **Freeze:** `prepare_sielinko_search.py freeze --art <dir> --handover <file>`. It records the
   input, source and runtime identities, the main pins (only the files the search reads; main's
   HEAD may move) and the execution identity.
4. **Check clips:** `scripts/analysis/sielinko_search.py --art <dir> --execute --stage check`.
   - This is one sentinel attempt per estimator on clip 1, at 2 × Rule C, so the native receipts
     prove that the candidate reaches the estimator.
   - Review `check-report.json`, the receipts and the lane samples, then write `readiness.json`.
5. **Search:** `--stage develop`, then `--stage final` (or `--stage all`).
   - `STOP_AFTER_CURRENT` in `<dir>` stops at the next attempt boundary.
   - A lane finding stops the search after the attempt. The attempt is kept for review, never
     silently retried.

Interpreter: `.venv/bin/python` (the `macvo` env plus optuna 4.5.0, as in the earlier campaigns).

## Handover format (written by the lane owner)
```json
{"schema": 1, "from": "rule-c-runner", "to": "extended-search-runner", "effective_utc": "...",
 "lanes": {"lane1": {"cpus": "0-3", "memory_gib": 50, "handed_over": true},
           "lane2": {"cpus": "4-7", "memory_gib": 50, "handed_over": true}},
 "rule_c_cpu_complete": true, "note": "..."}
```

## Limitations
- There is one recording, so the two halves share the platform, field and day.
- The recording was inspected before, through the Rule C and envelope runs.
- Only the second half is unseen by selection. The full-run test includes the development half.
- The reference is position-only, so ATE uses SE3 position alignment.
- Runtimes from concurrent lanes are labelled as overlapped.
