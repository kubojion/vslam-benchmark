# Non-headline experiment artifacts

This directory preserves diagnostic runs that must not be discovered by the benchmark aggregators.

**Audit 2026-10-01:** five COMPLETE smoke artifacts still exist under
`results/{vo,vio}/euroc_mav/smoke_mh_01_easy_200/` and are accepted by the current CSV
builder. Their quarantine/exclusion is pending; they are not part of the N=3 campaign.
See [the status audit](../docs/campaigns/server-status-20261001.md).

- `smoke/` contains short pipeline checks (formerly `run9001` under benchmark result roots).
- `failed/` contains incomplete attempts with no valid trajectory or evaluation, including the
  ORB-SLAM3 EuRoC MH_03 wrong-dataset-path attempt formerly named `run9`.

These artifacts are evidence for debugging only. Do not include them in headline CSVs or thesis
tables. Promote a result only after a complete trajectory, evaluation metadata and standard run ID
exist under the appropriate `results/<run-type>/` tree.
