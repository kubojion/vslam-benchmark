# Final quality campaign plan (RTX 4090, N=5)

This is the launch protocol for the single final benchmark campaign. It compares every
currently supported algorithm in each applicable table with one fixed, documented quality
configuration. There is no real-time campaign and no per-dataset tuning sweep.

## Scope

The committed source of truth is
[`configs/campaigns/quality-final.json`](../../configs/campaigns/quality-final.json). It expands
to **220 comparison cells** and **1,100 estimator executions** (five repetitions per cell):

| Table | Algorithms | Sequences | Cells |
|---|---:|---:|---:|
| VO | 8 | 8 | 64 |
| VO-LC | 6 | 8 | 48 |
| VIO | 7 | 8 | 56 |
| VIO-LC | 4 | 8 | 32 |
| GNSS-VIO | 5 | 4 | 20 |

The eight main sequences are Rosario v2 sequence1/sequence5, HortiMulti strawberry02/
strawberry03, EuRoC MH_01/MH_03/MH_05, and the full ZED2i field sequence. GNSS-VIO applies
only to Rosario v2 and HortiMulti, where GNSS input exists.

DROID-SLAM is excluded because DPVO replaced it in the report. MegaSaM and MASt3R-SLAM are
not installed and are outside this campaign; they must not appear as failed or empty cells.

## Before launch

1. Keep the machine otherwise idle. The driver runs cells serially, checks CPU load, GPU
   utilization, free VRAM, disk space, datasets, runners, native binaries, conda environments,
   ROS packages, and containers before starting.
2. Build the four AirSLAM LightGlue TensorRT engines on the campaign GPU. The setup script
   initializes the network against an empty dataset, so it writes no result cell:

   ```bash
   bash scripts/setup/prebuild_airslam_engines.sh
   ```

3. Run the read-only preflight. It must finish with `220 cells, 1100 executions` and no error:

   ```bash
   python3 scripts/campaign/run_quality_campaign.py --preflight
   ```

4. Complete the representative N=1 qualification smokes recorded in the preparation report.
   These are setup tests, not report measurements.

The OKVIS2/OKVIS2-X prerequisite installer applies build-only compatibility changes inside
their nested DBoW2 and opengv submodules. The driver reports these as a warning and includes
their exact diffs in the campaign source fingerprint. Any other tracked worktree change blocks
launch.

## Launch and resume

Inspect the exact order if desired:

```bash
python3 scripts/campaign/run_quality_campaign.py --list
```

Start the campaign from a persistent terminal such as tmux:

```bash
python3 scripts/campaign/run_quality_campaign.py --run
```

The driver owns a single campaign lock and runs only one cell at a time. Each cell calls
`run_benchmark.sh ... 5 <run-type>`, which transactionally replaces that cell so stale runs or
plots cannot leak into it. A failed cell is retried once. If it fails twice, the default is to
stop and retain its logs rather than silently produce an incomplete report.

State and per-cell logs are stored under
`logs/server-campaign/quality-final-n5/` (gitignored). Re-running the same command skips cells
marked successful. Resume is refused if the manifest or fingerprinted benchmark source changed.

## Completion

Only after all 220 cells succeed, the driver rebuilds all five committed `benchmark-*.csv`
files and runs:

```bash
conda run -n macvo python3 scripts/eval/make_report_tables.py --check
conda run -n macvo python3 scripts/eval/verify_claims.py
```

Large trajectories, plots, maps, resource traces, and logs remain in the gitignored `results/`
store and can be browsed through its local HTTP site. The five CSV summaries and generated
report tables remain in git, so a clone can compare the final numbers without downloading the
artifacts. Provenance uses the repository's anonymized derived machine ID; no hostname is stored.
