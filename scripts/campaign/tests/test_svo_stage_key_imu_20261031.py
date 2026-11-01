"""The SVO Pro stage must change with the IMU data, or a corrected file reuses a stale stage."""
from pathlib import Path
import hashlib, re

RUNNER = Path(__file__).resolve().parents[3]/'scripts/run/run_svo_pro.sh'


def key(files):
    return hashlib.sha256(b''.join(Path(f).read_bytes() for f in files)).hexdigest()[:16]


def test_runner_keys_stage_on_imu_data():
    line = re.search(r'^STAGE_KEY_FILES=\((.*)\)$', RUNNER.read_text(), re.M).group(1)
    assert '"$SEQ_DIR/mav0/imu0/data.csv"' in line


def test_key_changes_when_imu_data_changes(tmp_path):
    sensor, imu = tmp_path/'sensor.json', tmp_path/'data.csv'
    sensor.write_text('{}'); imu.write_text('1,0\n')
    before = key([sensor, imu]); imu.write_text('2,0\n')
    assert key([sensor, imu]) != before
