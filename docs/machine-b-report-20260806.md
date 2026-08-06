# Machine-B report — 2026-08-06

Machine: **Intel i9-14900HX / RTX 4080 Laptop** (holds EuRoC, HortiMulti, ZED2i).
Executed against `docs/machine-b-brief.md` (written on Jion's machine after commit `39a4a4c`).
Repo state at start: `main`, clean, 0 unpushed commits, `39a4a4c` already present (HEAD `023c58e`).

**Headline:** all six tasks executed. 173 runs re-evaluated (155 EuRoC/HortiMulti + 18 ZED2i),
**zero failures**; all 259 runs across the repo are now at `eval_schema: 2`. One acceptance check
(Task 0) did not pass *as written*; its premise is shown below to be incorrect, and no problem with
this machine was found. The ZED2i GT was regenerated from source — no method deviation remains.
Task 4 could not be completed as specified (no fork remotes exist); see "Decisions needed".

Nothing has been committed — this machine operates under a standing "no commits without explicit
instruction" rule from its owner, which overrides the brief's "push in small commits". All work is
on disk awaiting sign-off.

---

## Environment

| item | value |
|---|---|
| evo | **1.36.4** (downgraded from 1.37.0 to match the reference machine) |
| numpy / scipy / pandas | 1.26.4 / 1.15.3 / 2.3.3 |
| python env | conda `macvo` (the env every previous evaluation on this machine used) |
| `evo_ape` | `/home/iman/miniconda3/envs/macvo/bin/evo_ape` |

**evo version is provably irrelevant here.** Before concluding anything from the Task-0 mismatch, the
same code was run under both versions on the same input:

| field | evo 1.36.4 | evo 1.37.0 |
|---|---|---|
| ate.rmse | 0.033306 | 0.033306 |
| ate_se3.rmse | 0.071437 | 0.071437 |
| rpe_trans_1m.rmse | 0.007721 | 0.007721 |
| scale_factor | 1.0148902317593855 | 1.0148902317593855 |
| n_pairs_ate | 3638 | 3638 |

Bit-identical. We nonetheless remain pinned at 1.36.4 to match the reference.
Revert if ever needed: `conda run -n macvo pip install 'evo==1.37.0'`.

---

## Task 0 — Preflight: FAILED AS WRITTEN, but the premise is wrong

The smoke test (`basalt / MH_01_easy / vio`) differed on all five legacy fields:

| field | before | after |
|---|---|---|
| ate.rmse | 0.034765 | 0.033306 |
| ate_se3.rmse | 0.072309 | 0.071437 |
| rpe_trans_1m.rmse | 0.007412 | 0.007721 |
| scale_factor | 1.0148991702848897 | 1.0148902317593855 |
| **n_pairs_ate** | **3682** | **3638** |

The brief assumed "GT unchanged at this point → legacy fields must match exactly". That assumption
does not hold: the **GT-interpolation fix changes which frames are matched even with an unchanged GT
file**. `n_pairs_ate` differing proves a different *point set*, not a numerical disagreement.

Cause, verified exactly: **22 camera frames fall before the Vicon GT starts and 22 after it ends
(22 + 22 = 44 = 3682 − 3638)**. The old code clamped these to the first/last GT pose (frozen poses,
artificial error); the fixed code drops them.

**Conclusion: PASS on the question the check was actually asking** (environment compatibility).
Suggest rewording this check on the reference machine — as written it will fail on any machine.

---

## Task 1 — Rosario seq1 GT: PASS

### Forensic capture (before any change)

`datasets/rosariov2/sequence1/` contained a stray `conv.py` (1508 B, mtime 2026-05-24 12:36) that
reads `gps.csv`, projects lat/lon/alt to ENU, and writes `0 0 0 1` for every orientation.

| file | rows | sha256 (16) | mtime |
|---|---|---|---|
| `gt_tum.txt` | 4703 | `6b1a0b5d79513492` | 2026-05-24 12:38 |
| `gt_interp_tum.txt` | 13821 | `b7a7ceb0a0456537` | 2026-05-24 12:54 |

Confirmation it was raw GPS, not PGT: **`gt_tum.txt` had exactly 4703 rows — identical to
`gps.csv`** — at 5.00 Hz with identity quaternions throughout. By contrast seq5's `gt_tum.txt`
(7577 rows vs its 3982 GPS rows, real quaternions) came from the proper PGT path. The mtimes agree:
seq5 GT was produced 2026-05-17/18 by the standard pipeline, seq1 a week later by the local script.

### Repair

Archived (not deleted): `gt_tum.txt.divergent-raw-gps`, `gt_interp_tum.txt.divergent-raw-gps`,
`conv.py.divergent-raw-gps` (de-executabled). seq5's `gt_tum.txt` was already correct; only its
interp was stale (`gt_interp_tum.txt.superseded-clamped`).

### Acceptance — all six hashes match the brief's table

| file | sha256 (16) | status |
|---|---|---|
| sequence1/gt_tum.txt | `6eef4e8ed3f0ce8f` | OK |
| sequence1/gt_interp_tum.txt | `5b2bc209a5119873` | OK |
| sequence1/times.txt | `2df7d34b8e144e6b` | OK |
| sequence5/gt_tum.txt | `a886d339de70f9ac` | OK |
| sequence5/gt_interp_tum.txt | `4b68867faf6fe8c8` | OK |
| sequence5/times.txt | `896e64e6d5d88375` | OK |

No rosariov2 run was re-evaluated (brief rule 3).

---

## Task 2 — EuRoC + HortiMulti: PASS

### GT re-interpolation, dropped frames

| sequence | dropped | of | note |
|---|---|---|---|
| MH_01_easy | 44 | 3682 | outside GT range |
| MH_03_medium | 69 | 2700 | outside GT range |
| MH_05_difficult | 52 | 2273 | outside GT range |
| strawberry02 | **707** | 9530 | **564 inside GT gaps > 0.60 s**, rest out of range |
| strawberry03 | 6 | 2425 | outside GT range |

### Re-evaluation

**155/155 succeeded, 0 failures.** CSVs full-rebuilt (259 rows across 5 files),
`make_report_tables.py --check` **OK**, `verify_claims.py` OK, figures regenerated.

### Old → new shift

| dataset | cells | median \|shift\| | max |
|---|---|---|---|
| EuRoC | 75 | **0.00 %** | 22.5 % |
| HortiMulti | 80 | 0.35 % | 9.2 % |

30 cells shifted > 2 %. The brief asks to investigate EuRoC moves > 1 %; the split is decisive:

- **58 EuRoC cells whose frame set was unchanged: max shift 0.002 %** — numerical noise only.
- **17 EuRoC cells that lost out-of-range frames: every one shifted, and every one improved.**

Largest movers:

| mode | cell | algo | old | new | shift | pairs |
|---|---|---|---|---|---|---|
| vo | euroc/MH_01_easy | basalt | 0.057 | 0.044 | −22.5 % | 3682→3638 |
| vo | horti/str02 | ov2slam | 5.763 | 5.232 | −9.2 % | 9530→8823 |
| vo | horti/str02 | orbslam3 | 1.380 | 1.255 | −9.1 % | 4437→3828 |
| vio-lc | horti/str02 | orbslam3 | 0.883 | 0.807 | −8.6 % | 9505→8823 |
| vio | horti/str02 | orbslam3 | 1.476 | 1.371 | −7.1 % | 9505→8823 |
| vo | euroc/MH_03_medium | basalt | 0.137 | 0.130 | −5.5 % | 2700→2631 |

**Interpretation.** Basalt moves most on EuRoC because it tracks from frame 0 and genuinely had
poses in the 44 frames outside Vicon coverage, where clamped GT inflated its error; later-initialising
algorithms never had poses there and did not move. On HortiMulti str02 every algorithm improved 5–9 %,
because 564 frames were being matched against GT bridged across gaps > 0.6 s. **All shifts are
removals of GT artifacts — the fix behaving as designed.** No shift is an accuracy regression.

---

## Task 3 — ZED2i lever arm: PASS (genuine regeneration from source)

### Both prescribed routes were initially blocked — both turned out to be solvable

1. *"Promote the existing `gt_measured_2p86*` data"* — only the **interpolated** 2.86 m file exists;
   there is no raw 2.86 m `gt_tum.txt` to promote. Genuinely unavailable.
2. *"Re-run the extractor's GT stage"* — first attempts failed with
   `No module named 'rosbag2_py._reader'`. **This was NOT a broken ROS install.** Conda's
   `droid_slam` env (Python **3.9**) shadows system Python **3.10** on this machine, and ROS 2 Humble
   builds `rosbag2_py` for 3.10. With `/usr/bin/python3` after sourcing ROS, it imports fine.

Two further findings removed the remaining obstacles:

- **The 151 GB camera MCAP is not needed for GT.** `extract_gps_gt()` reads only `/gps/fix` and
  `/ublox_rover/fix` from `--rtk_bag`; the MCAP supplies images/IMU/camera_info only. (`--zed_bag`
  is `required=True` in argparse, but the GT function can be called directly.)
- **The correct source bag is named in the dataset's own `manifest.json`:**
  `rtk_bag: /home/iman/Downloads/field-test-0703/field1/field1-all-rows-follow-0703-nav2-3`,
  alongside `gps_gt.lever_x_m: 1.86` — the error's provenance in writing. An initial attempt used
  `~/03.06-no-camera-bags/field1-path-follow`, which is the **3 June** trip (26 min) and produced
  `no /gps/fix messages found in overlap`.

### Route taken: GENUINE REGENERATION (no deviation)

Once the correct robot bag was supplied, the GT was regenerated with the pipeline's own unmodified
function against the 3 July bag (2026-07-03 09:04 UTC, 77.2 min, 23160 `/gps/fix`,
23156 `/ublox_rover/fix`):

```
extract_gps_gt(field1-all-rows-follow-0703-nav2-3, out, start_ns, end_ns,
               lever_x_m=2.86, lever_z_m=0.0)
  -> gps_rows 23106 | gt_rows 23106 | heading_rows 23106
```

All 23106 rows carry a valid RTK heading — no fallbacks. **No method deviation and no sign-off
required.**

An interim reconstruction (offset-field derivation from the known-good interp) was produced while
the bag was unavailable and has been superseded; it is archived as
`gt_tum.txt.reconstructed-superseded`. Cross-check between the two:

| comparison | mean | max |
|---|---|---|
| regenerated vs reconstruction | 0.434 mm | 52.3 mm |
| regenerated vs reference 2.86 interp | 0.338 mm | 51.1 mm |
| reconstruction vs reference 2.86 interp | 0.092 mm | 21.7 mm |

The reconstruction scores "closer" to the reference only because it was derived from it — that
comparison is circular. The regeneration is independent, and 0.43 mm agreement between the two
confirms the interim method was sound. The regenerated file is authoritative and installed.

Independent confirmation of the value, from `robot-camera-gps-params.txt`: the position antenna
(`moving_base`, rear) sits 0.320 m ahead of the rear axle and the ZED optical centre 3.180 m, so the
lever arm is **3.180 − 0.320 = 2.860 m**. Both from the same datum, so the CAR/4WS `base_link`
convention cancels — mixing those conventions is exactly how 1.86 m arose.

### Results

- `gt_tum.txt` regenerated (23106 rows, sha256 `d5c25dce4641dadd`); 1.86 m archived as
  `gt_tum.txt.wrong-1p86-lever`, interim reconstruction as `gt_tum.txt.reconstructed-superseded`.
- Re-interpolated: 46205 poses, 78 dropped.
- `segments_auto.csv` regenerated: 2 segments (2 row, 4621.2 s, 424.8 m; 0 turn).
- Segment maps + `plot_comparison` figures regenerated for `vo` and `vio`.
- **18/18 runs re-evaluated, 0 failures**; **18/18 now carry `gt_provenance`** (file, source, sha256, mtime).

**Shift: median 0.070 %, max 0.52 %** — confirming published ZED2i ATEs already used the correct
2.86 m interp. The residual is attributable to the 76 dropped frames alone. Largest movers:
orbslam3 vo-lc 0.202→0.201 (−0.52 %), orbslam3 vo 0.256→0.254 (−0.48 %), dpvo vo 1.431→1.425 (−0.43 %).

`docs/zed2i_setup.md` updated: corrected file descriptions, the 2.86 m derivation, the archived
1.86 m file, the `--gps_to_camera_z = 0` caveat (GT altitude is the antenna's, not the camera's
1.31 m), and the 0.10 s camera↔robot clock offset.

---

## Task 4 — Runtime prerequisites: INVENTORY ONLY (cannot commit)

**All submodules except ORB_SLAM3 point at upstream, not our forks** — there is nowhere to push,
and pushing to third-party upstreams would be wrong.

| submodule | origin | local-only state |
|---|---|---|
| `src/airslam` | `sair-lab/AirSLAM` (upstream) | untracked `launch/visual_odometry/vio_euroc.launch` (20 lines) |
| `src/open_vins` | `rpng/open_vins` (upstream) | untracked `Dockerfile.benchmark` (37 lines) |
| `src/okvis2` | `ethz-mrl/okvis2` (upstream) | modified `external/DBoW2`, `external/opengv` pointers |
| `src/okvis2x` | `ethz-mrl/OKVIS2-X` (upstream) | modified `.gitmodules` + same two pointers |
| `src/ORB_SLAM3` | `kubojion/ORB_SLAM3` (**fork**) | clean |
| `src/DPVO` | `princeton-vl/DPVO` (upstream) | `saved_trajectories/` (output, not a prerequisite) |

The AirSLAM launch file is the one behind the VIO-LC launch fix and is genuinely required for
reproducibility. Contents of both text files are preserved in this campaign's working notes.

---

## Bug found (reported, not fixed — rule 5)

**`scripts/eval/plot_comparison.py` rejects two of the five run types.** Its `--type` choices are
`{vo, vio, vio-lc}`; **`vo-lc` and `gnss-vio` are missing**, so those trees exit with an argparse
error. Consequences: ZED2i `vo-lc` overlay plots (5 runs) could not be regenerated, and any earlier
bulk figure regeneration silently skipped `vo-lc`/`gnss-vio`. One-line fix (extend the choices list)
— left to the pipeline owner.

---

## Acceptance summary

| task | result |
|---|---|
| 0 preflight | FAILED as written; **PASS** on the real question (evo proven irrelevant) |
| 1 Rosario GT | **PASS** — 6/6 hashes match |
| 2 EuRoC + HortiMulti | **PASS** — 155/155, `--check` OK, all shifts explained |
| 3 ZED2i | **PASS** — 18/18, gt_provenance 18/18; GT genuinely regenerated from source |
| 4 prerequisites | **INVENTORY ONLY** — no fork remotes exist |
| 5 report | this file |

All 259 runs repo-wide are now `eval_schema: 2`.

**Gap found during final verification (reference machine, not this one):** `gt_provenance` is present
on **241/259** runs. The 18 without it are all **rosariov2**, and all carry
`machine.cpu = AMD Ryzen 9 5900HX` — i.e. they were evaluated on the other machine. They are at
`eval_schema: 2`, so they went through the fixed pipeline, but predate (or missed) the
GT-provenance recording. Rule 3 forbids re-evaluating rosariov2 here, so this is reported rather than
fixed: **re-evaluating those 18 on the reference machine would complete provenance coverage to
259/259.**

---

## Decisions needed from the team

1. ~~Sign off the reconstructed ZED2i GT~~ — **RESOLVED**: regenerated from the correct 3 July robot
   bag with unmodified pipeline code. No decision needed.
2. ~~Fix `rosbag2_py`~~ — **RESOLVED**: never broken; invoke the extractor with `/usr/bin/python3`
   after sourcing ROS 2 Humble (conda's Python 3.9 shadows the system 3.10 it is built for).
   Worth documenting so the next person does not repeat the diagnosis.
3. **Git-track the GT files.** `datasets/` is gitignored, which is the direct cause of the seq1
   divergence: git carried Jion's fix everywhere except the data. A `.gitignore` exception for
   `datasets/**/gt_*.txt` + `times.txt` (~4 MB) would prevent recurrence. **Strongly recommended.**
4. **Where do local-only runtime prerequisites live?** No forks exist for AirSLAM / OpenVINS /
   OKVIS2 / OKVIS2-X. Either create them, or vendor the files into this repo (note `patches/` is
   currently gitignored).
5. **`plot_comparison.py` run-type choices** — accept the one-line fix above?
6. **The ~14 equalized tuning re-runs** (config-deviation findings in `PROGRESS.md`) — out of scope
   here per rule 6; still outstanding.
7. **N≥5 replication campaign** and **uniform feeding-protocol re-runs** — still outstanding.
8. **Commit/push policy for this machine.** The brief says commit per task; this machine's owner
   requires explicit approval. Nothing is committed. Jion's independent verification (GT hashes,
   spot re-evaluations, CSV diffs) cannot proceed until this is resolved.

---

## Not done / out of scope

- No `rosariov2` run was re-evaluated (rule 3).
- No SLAM re-runs, no tuning re-runs, no N≥5 replication (rule 6).
- No pipeline code was modified (rule 5) — the `plot_comparison.py` bug is reported, not patched.
- Nothing committed or pushed (owner's standing instruction).
