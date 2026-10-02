# Rosario VIO calibration candidates

Prepared for sequences 1 and 5 only. **Not execution-ready; not selected by the
current runners.** See the [review and prerequisites](../../../docs/rosario-vio-candidates-20261002.md)
and [validation record](../../../docs/rosario-vio-candidate-validation-20261002.json).

`index.json` pins the generated files and separates the Kalibr sensor bundle from
the author's OpenVINS bundle. `sources/index.json` identifies 15 preserved source
files, their original paths and checksums. No calibration was fitted to benchmark
scores. No historical result is replaced by these files.

From `/data/imoroz/vslam-benchmark` on main:

```bash
/data/imoroz/conda/envs/macvo/bin/python scripts/campaign/prepare_rosario_vio_candidates.py
/data/imoroz/conda/envs/macvo/bin/python scripts/campaign/prepare_rosario_vio_candidates.py --inspect openvins-author --sequence sequence1
/data/imoroz/conda/envs/macvo/bin/python -m pytest -q scripts/campaign/tests/test_rosario_vio_candidates.py
```

The inspection command does not launch anything or certify readiness. These
candidates remain inactive; do not replace runner defaults until the intended
published profile is established and the native checks pass.
