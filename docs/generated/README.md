# Generated results and publication status

Updated after the focused EuRoC campaign, 2026-10-02 local. These outputs now match the root schema-3 CSVs and the
hash-checked attempt inventory. They combine explicitly accepted, limited and blocked claims, identified in each
cell; only the stated accepted comparisons are paper-usable. See [qualification](../publication-qualification-20261001.md)
and [TODO](../../TODO.md). There are 45 clean accepted EuRoC N=3 cells; see the [current handoff](../acceptance-handoff-20261001.md).

The EuRoC AirSLAM VIO/VIO-LC comparison uses corrected physical runs4–6, declared before execution. The 18 original affected runs remain in `benchmark-historical-cohorts.csv` and `results/historical-cohorts/`. OpenVINS original/new implementation cohorts remain separate. These changes add no automatic green ticks.

- [Tables](tables.md): all five modes, 666 planned/variant rows, separate cohorts,
  explicit failures and missing repetitions.
- [Evidence counts](verified-claims.md): current counts and claim boundaries;
  no hard-coded IMU/loop-closure causal conclusions or invented processing FPS.
- [Outcome overview](figures/fig_campaign_outcomes.png): all default repetitions.
- [VO](figures/fig_accuracy_vo_default.png), [VO-LC](figures/fig_accuracy_vo-lc_default.png),
  [VIO](figures/fig_accuracy_vio_default.png), [VIO-LC](figures/fig_accuracy_vio-lc_default.png),
  [GNSS-VIO](figures/fig_accuracy_gnss-vio_default.png): conditional ATE with acceptance flags,
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
