"""Native receipt checks for experimental OpenVINS runs; no ATE-based decisions.

The receipt audit is main's production delivery gate (scripts/run/_openvins_delivery.py),
itself ported from this module on experiment/imu-noise-reliable-20261009. One
implementation keeps the search and Rule C on the same gate.
"""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'run'))
from _openvins_delivery import audit_openvins, expected, timestamp_fingerprint, timing_log_evidence  # noqa: E402,F401


def verify_native_noise(run, parameters):
    receipt = json.loads((Path(run) / 'openvins_input_receipt.json').read_text())
    native = receipt.get('native_imu_noise')
    if native != parameters:
        raise RuntimeError('OpenVINS native noise differs from the proposed four-parameter vector')
    return native
