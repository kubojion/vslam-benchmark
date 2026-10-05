# ZED remaining N=3 campaign — 2026-10-02

Prepared only; no production execution is authorized. This replaces the overlapping ZED selection in the all-mode manifest. Do not execute both plans.

Retain 50 qualified observations. Preserve 0 completed predeclared attempts pending claim review, without scheduling their first slots again. Prepare 55 remaining attempts: **16 setup replacements, 36 missing slots and 3 cohort-completion attempts**. All displaced history and failures remain preserved.

**Readiness:** 52/55 remaining attempts have reviewed bounded execution checks and no unresolved plan prerequisites. Others retain their listed blockers. Voxel initialization/export and any mixed-cohort questions remain explicit. A short check does not certify full-sequence stability; completed outputs do not automatically pass claim review.

| Mode | Algorithm | New physical IDs | Logical slot reasons (r1 / r2 / r3) | Bounded readiness | Cost proxy per attempt |
|---|---|---|---|---|---:|
| vo | orbslam3 | run10001, run10002, run10003 | required_rerun / required_rerun / required_rerun | 3/3 checked; see prerequisites | 1.57 h |
| vo | cuvslam | run10003, run10004 | reusable / missing / missing | 2/2 checked; see prerequisites | unknown |
| vo | svo_pro | run10003, run10004 | reusable / missing / missing | 2/2 checked; see prerequisites | unknown |
| vo | dsol | run10001, run10002, run10003 | missing / missing / missing | 3/3 checked; see prerequisites | unknown |
| vo-lc | orbslam3 | run10001, run10002, run10003 | required_rerun / required_rerun / required_rerun | 3/3 checked; see prerequisites | 1.59 h |
| vo-lc | okvis2 | run10001, run10002, run10003 | cohort_completion / cohort_completion / missing | 3/3 checked; see prerequisites | 6.17 h |
| vo-lc | okvis2x | run10001, run10002, run10003 | cohort_completion / missing / missing | 3/3 checked; see prerequisites | unknown |
| vo-lc | airslam | run10001, run10002, run10003 | required_rerun / required_rerun / required_rerun | 3/3 checked; see prerequisites | 1.30 h |
| vo-lc | cuvslam | run10001, run10002, run10003 | missing / missing / missing | 3/3 checked; see prerequisites | unknown |
| vio | openvins | run10004, run10005, run10006 | required_rerun / required_rerun / required_rerun | 0/3 checked; see prerequisites | 1.29 h |
| vio | cuvslam | run10003, run10004 | reusable / missing / missing | 2/2 checked; see prerequisites | unknown |
| vio | svo_pro | run10003, run10004 | reusable / missing / missing | 2/2 checked; see prerequisites | unknown |
| vio | mast3r_fusion | run10004, run10005 | reusable / missing / missing | 2/2 checked; see prerequisites | unknown |
| vio-lc | orbslam3 | run10001, run10002, run10003 | required_rerun / missing / missing | 3/3 checked; see prerequisites | unknown |
| vio-lc | okvis2 | run10001, run10002, run10003 | required_rerun / missing / missing | 3/3 checked; see prerequisites | 2.69 h |
| vio-lc | okvis2x | run10001, run10002, run10003 | required_rerun / missing / missing | 3/3 checked; see prerequisites | 3.38 h |
| vio-lc | airslam | run10001, run10002, run10003 | required_rerun / missing / missing | 3/3 checked; see prerequisites | 1.14 h |
| vio-lc | cuvslam | run10001, run10002, run10003 | missing / missing / missing | 3/3 checked; see prerequisites | unknown |
| vio-lc | svo_pro | run10001, run10002, run10003 | missing / missing / missing | 3/3 checked; see prerequisites | unknown |
| vio-lc | mast3r_fusion | run10001, run10002, run10003 | missing / missing / missing | 3/3 checked; see prerequisites | unknown |

The indicative serialized cost subtotal is **57.4 hours for 24 attempts**; 31 have no defensible complete historical proxy. This includes blocked attempts where a proxy exists. It is not a full-campaign runtime estimate. Paced ORB/OpenVINS/Voxel inputs alone take approximately 77.2 minutes per complete attempt; optimization, startup, capture and evaluation add time.

These are historical wrapper wall-cost proxies, including configurations/builds that now require replacement and the old Voxel shutdown failure. They do not qualify those results or establish processing throughput. New calibration, loop closures, final optimization and host contention may change costs; no confidence interval or linear extrapolation from short checks is claimed. Serialize runs on shared GPU/containers.

The six cohort-completion attempts comprise two OKVIS2 VO-LC, one OKVIS2-X VO-LC and three AirSLAM VO-LC slots. They create consistent current cohorts; they are not six additional proven configuration defects or retries selected for success. OKVIS2 run2 remains interrupted; OKVIS2-X run1 remains exit 141 with only a recovered causal prefix; AirSLAM retains its individually qualified N=1 and N=2 historical cohorts.

## Retained complete cohorts

| Cell | Retained physical attempts |
|---|---|
| `vo/zed2i/field1_110426_full_10fps_q90/okvis2` | run1, run2, run3 |
| `vo/zed2i/field1_110426_full_10fps_q90/okvis2x` | run1, run2, run3 |
| `vo/zed2i/field1_110426_full_10fps_q90/airslam` | run1, run2, run3 |
| `vo/zed2i/field1_110426_full_10fps_q90/basalt` | run1, run2, run3 |
| `vo/zed2i/field1_110426_full_10fps_q90/ov2slam` | run1, run2, run3 |
| `vo/zed2i/field1_110426_full_10fps_q90/dpvo` | run1, run2, run3 |
| `vo/zed2i/field1_110426_full_10fps_q90/macvo` | run1, run2, run3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/ov2slam` | run1, run2, run3 |
| `vo-lc/zed2i/field1_110426_full_10fps_q90/dpvo` | run1, run2, run3 |
| `vio/zed2i/field1_110426_full_10fps_q90/orbslam3` | run10001, run10003, run10004 |
| `vio/zed2i/field1_110426_full_10fps_q90/okvis2` | run10001, run10003, run10004 |
| `vio/zed2i/field1_110426_full_10fps_q90/okvis2x` | run10001, run10003, run10004 |
| `vio/zed2i/field1_110426_full_10fps_q90/airslam` | run10001, run10002, run10003 |
| `vio/zed2i/field1_110426_full_10fps_q90/basalt` | run10001, run10002, run10003 |
| `vio/zed2i/field1_110426_full_10fps_q90/voxel_svio` | run10001, run10002, run10003 |

## Completed first repetitions awaiting claim review

The stopped controller is not an active scheduler. These recorded attempts have no
new command in this manifest; preserved exit/evaluation evidence does not itself award a tick.


## Executable manifest and verification

The full paths, commands, prior evidence, runtime samples and prerequisites are in `results/zed-preparation-20261002/campaign/manifest.json`. Each new attempt uses `run_repetitions.py` with one explicit physical ID, logical repetition and cohort. It preserves prior attempts, evaluates saved output immediately and refuses unsafe overwrite/resumption.

Read-only verification (no estimator execution):

```bash
/data/imoroz/conda/envs/macvo/bin/python scripts/campaign/run_future_manifest.py results/zed-preparation-20261002/campaign/manifest.json
```

After source/config/build changes, refresh reviewed execution assets and regenerate both manifests; do not hand-edit hashes or widen readiness flags. Use `--action` to select an exact action and `--require-ready --check-inputs --check-implementations` for its strict read-only preflight from a clean execution environment. Voxel must fail readiness preflight until its export prerequisite is independently resolved. No `--run` command is authorized by this preparation.

The broader all-five-mode audit and existing algorithm exclusions remain intact. Rosario, HortiMulti and GNSS blockers are unchanged; the non-ZED ORB native build still needs separate ABI/shutdown validation. See [preparation and limitations](zed-preparation-20261002.md), [historical validation](zed-validation-20261002.md) and [main integration reconciliation](rosario-main-integration-20261002.md).
