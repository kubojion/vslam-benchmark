# Independent verification of the machine-B campaign — 2026-08-06 (Jion's machine)

Five parallel verifications were run against commits `ab60a06…dbb0ada` on the Ryzen/RTX-3080
machine (which does NOT hold the EuRoC/HortiMulti/zed2i datasets — everything below is verified
from committed artifacts and git history).

## Confirmed

- **CSV determinism across machines**: rebuilding all five `benchmark-*.csv` here reproduces
  machine B's push **byte-identically** (after refreshing `_seq_meta_cache.json` — see gap 1),
  and `make_report_tables.py --check` + `verify_claims.py` regenerate `docs/generated/`
  byte-identically. 259 rows = one per run dir, no duplicates/orphans.
- **Every checkable number in the machine-B report is exact**: MH01 basalt 3682→3638 pairs /
  0.034765→0.033306; str02 9530→8823; MH03 2700→2631; the six Rosario GT hashes; 259/259 at
  `eval_schema: 2`; the largest-movers table; zed2i shifts (median 0.070%, max 0.52%); the
  Task-0 explanation (44 = 22+22 out-of-range frames); the `plot_comparison.py` bug.
- **No machine-identity damage**: zero machine blocks lost or overwritten across all 173
  re-evaluated files; 48 runs honestly gained `collected_at: "evaluation"` stamps (excluded
  from CSV attribution by design).
- **GT uniformity**: within every (dataset, sequence), all provenance-bearing runs carry the
  identical GT sha256. rosariov2 results untouched by machine B, byte-level, as instructed.

## Corrections to the machine-B report (prose, not data)

1. *"Every shifted cell improved"* is **false**: `hortimulti/str02 vins_fusion_gps` (+2.32%)
   and `voxel_svio` (+2.09%) regressed, plus 5 EuRoC changed-set cells worsened <1%. This is
   still consistent with artifact removal (deleting flattering fake correspondences can raise
   measured error) — but the universal-improvement claim should not be quoted.
2. The EuRoC unchanged/changed split is **57/18**, not 58/17 (max-noise claim holds for the 57).
3. The 18 provenance-less runs were **not** all Ryzen-stamped (12 Ryzen / 5 i9 / 1 none).
   Moot now: all 18 were re-evaluated on Jion's machine — **gt_provenance is 259/259**, seq1
   uniformly on `5b2bc209…`.
4. *"Nothing has been committed"* was stale by push time (4 commits, authored 11:21–11:22,
   report committed last, unamended).

## Gaps found and their fixes

| gap | status |
|---|---|
| `_seq_meta_cache.json` stale after machine B's GT changes → dataset-less rebuilds off by the metadata columns | **fixed here**: cache regenerated from the pushed CSVs; rebuild now byte-identical (staged) |
| 18 rosariov2/seq1 runs lacked `gt_provenance` | **fixed here**: re-evaluated (18/18, values unchanged, CSVs identical) — provenance 259/259 (staged) |
| `plot_comparison.py` rejected `vo-lc`/`gnss-vio` | **fixed here** (one-line, staged) |
| **`results-vio/zed2i` (and vo-lc) `segment_map*.png` were NOT regenerated** — as pushed they still render the superseded 1.86 m raw GT (contrary to the report's Task-3 claim; only the vo tree was refreshed) | **needs machine B**: re-run `_plot_segments.py` for zed2i vio + vo-lc (vo-lc unblocked by the plot fix), commit |
| zed2i auto-segmentation produces 2 pseudo-"row" segments spanning the whole 4621 s and **0 turns** for a 6-row field with headland turns → `ate_row` on zed2i is effectively global ATE and turn performance is unmeasured | **open**: fix `_segment_trajectory.py`'s turn detection for this trajectory (RTK-heading yaw available now) before any zed2i row/turn claims |
| Local-only prerequisites had no home (no forks exist) | **fixed here**: vendored into `vendor/prerequisites/` with `install.sh` (staged); long-term fork decision still open |
| `datasets/` gitignore hid GT — root cause of the seq1 divergence | **fixed here**: `.gitignore` exception + rosario GT/times/segments tracked (staged); machine B should commit its euroc/hortimulti/zed2i GT files the same way on next push |
