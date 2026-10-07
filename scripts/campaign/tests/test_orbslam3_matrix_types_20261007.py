"""ORB-SLAM3 converts IMU.T_b_c1 (and Stereo.T_c1_c2) with cv::Mat::at<float> (Converter::toSophus): a dt: d
matrix is read as garbage and aborts at map creation (Rosario check, 2026-10-07). Every configuration must store
them as dt: f."""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def test_orbslam3_float_matrices_are_declared_float():
    seen = 0
    for path in sorted((REPO / 'configs/orbslam3').glob('*.yaml')):
        text = path.read_text()
        for name in ('IMU.T_b_c1', 'Stereo.T_c1_c2'):
            for m in re.finditer(re.escape(name) + r': !!opencv-matrix\s*\n\s*rows:\s*4\s*\n\s*cols:\s*4\s*\n\s*dt:\s*(\w)', text):
                seen += 1
                assert m.group(1) == 'f', (path.name, name)
    assert seen >= 10
