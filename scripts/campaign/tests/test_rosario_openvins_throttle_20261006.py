"""Rosario OpenVINS front-end throttle above the camera rate (user decision 2026-10-06), as on
HortiMulti, ZED2i and CitrusFarm: no frame of either sequence is rejected by track_frequency."""
from pathlib import Path

import numpy as np
import yaml

REPO = Path(__file__).resolve().parents[3]


def kept(stamps, frequency):
    last, n = None, 0
    for t in stamps:
        if last is None or t - last >= 1.0 / frequency:
            last, n = t, n + 1
    return n


def test_rosario_openvins_keeps_every_frame():
    text = (REPO / "configs/openvins/rosariov2/estimator_config.yaml").read_text()
    config = yaml.safe_load("\n".join(l for l in text.splitlines() if not l.startswith("%YAML")))
    assert config["track_frequency"] == 31.0
    for seq in ("sequence1", "sequence5"):
        path = REPO / "datasets/rosariov2" / seq / "mav0/cam0/data.csv"
        if path.is_file():
            stamps = np.loadtxt(path, delimiter=",", comments="#", usecols=0, dtype=np.int64) * 1e-9
            assert kept(stamps, config["track_frequency"]) == len(stamps), seq
