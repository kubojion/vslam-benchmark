# Generated results and publication status

Updated 2026-10-01. These outputs now match the root schema-3 CSVs and the
hash-checked attempt inventory. They are **provisional scientific results**, not
certified paper comparisons. See [qualification](../publication-qualification-20261001.md)
and [TODO](../../TODO.md). No current cell has a qualified clean N=3 tick.

- [Tables](tables.md): all five modes, 666 planned/variant rows, separate cohorts,
  explicit failures and missing repetitions.
- [Evidence counts](verified-claims.md): current counts and claim boundaries;
  no hard-coded IMU/loop-closure causal conclusions or invented processing FPS.
- [Outcome overview](figures/fig_campaign_outcomes.png): all default repetitions.
- [VO](figures/fig_accuracy_vo_default.png), [VO-LC](figures/fig_accuracy_vo-lc_default.png),
  [VIO](figures/fig_accuracy_vio_default.png), [VIO-LC](figures/fig_accuracy_vio-lc_default.png),
  [GNSS-VIO](figures/fig_accuracy_gnss-vio_default.png): provisional conditional ATE,
  with monocular Sim(3) separate from metric SE(3). GNSS variants have separate files.
- Matching PDFs are available beside every PNG. `figures/figure-data.json` records
  input hashes, per-cell data and figure hashes. Failure denominators are retained;
  separate cohorts are not averaged into one color/value.
- [Historical generated outputs](historical-before-repair-20261001/README.md):
  18 superseded files, archived with verified hashes. Their conclusions are not current.

Regenerate and check with the commands in [evaluation](../evaluation.md). The
reporting tools reject stale CSVs and preserve previous derived bytes before replacement.
Do not transcribe or manually adjust numerical output. Raw historical per-run plots
remain in the result browser as labelled artifacts, without current-result previews.
