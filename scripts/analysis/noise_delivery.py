"""Native receipt checks for experimental OpenVINS runs; no ATE-based decisions."""
import csv
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re


@lru_cache(maxsize=24)
def timestamp_fingerprint(path, expected_sha256):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise RuntimeError('Timestamp input changed while auditing delivery')
    stamps = [int(row[0]) for row in csv.reader(data.decode().splitlines())
              if row and row[0].strip() and not row[0].lstrip().startswith('#')]
    if any(b <= a for a, b in zip(stamps, stamps[1:])):
        raise ValueError('Input timestamps must be strictly increasing')
    xor = 0
    for value in stamps:
        xor ^= value
    return dict(count=len(stamps), sum_u64=sum(stamps) % (1 << 64), xor_u64=xor)


def expected(path):
    path = Path(path)
    return timestamp_fingerprint(str(path), hashlib.sha256(path.read_bytes()).hexdigest())


def audit_openvins(run, sequence, *, allowed_pending_tail):
    """Separate receipt from processing and permit only a declared tiny tail.

    A camera may await a future IMU sample after the recording ends. The tail
    allowance is frozen by the campaign protocol, never adjusted to improve ATE.
    All published IMU samples and stereo pairs must still be received exactly.
    """
    run, sequence = Path(run), Path(sequence)
    received = json.loads((run / 'openvins_input_receipt.json').read_text())
    published = json.loads((run / 'transport_stats.json').read_text())
    imu = expected(sequence / 'mav0/imu0/data.csv')
    left = expected(sequence / 'mav0/cam0/data.csv')
    right = expected(sequence / 'mav0/cam1/data.csv')
    checks = {'stereo_input_timestamps_agree': left == right}
    for name, fingerprint in (('imu', imu), ('stereo', left)):
        checks[name + '_count'] = received[name + '_received'] == fingerprint['count']
        checks[name + '_timestamp_sum'] = received[name + '_stamp_sum_u64'] == fingerprint['sum_u64']
        checks[name + '_timestamp_xor'] = received[name + '_stamp_xor_u64'] == fingerprint['xor_u64']
    checks['publisher_imu_count'] = published['imu_messages_published'] == imu['count']
    checks['publisher_camera_count'] = published['camera_frames_published'] == left['count']
    checks['no_camera_read_failures'] = published['camera_read_failures'] == 0
    checks['no_frontend_rate_drops'] = received['camera_rate_dropped'] == 0
    checks['all_received_cameras_queued'] = received['camera_queued'] == received['stereo_received']
    checks['queue_accounted_for'] = received['camera_processed'] + received['camera_remaining'] == received['camera_queued']
    checks['bounded_pending_tail'] = 0 <= received['camera_remaining'] <= allowed_pending_tail
    log = (run / 'openvins_node.log').read_text(errors='replace')
    feeds = len(re.findall(r'\[TIME\]: [0-9.eE+-]+ seconds total', log))
    checks['native_log_matches_receipt'] = feeds == received['camera_processed']
    return dict(schema=1, passed=all(checks.values()), checks=checks, native=received,
                publisher=published, expected=dict(imu=imu, stereo=left),
                allowed_pending_tail=allowed_pending_tail,
                note='Counts and timestamp fingerprints audit receipt; processed cameras are completed feed calls, not successful tracking updates.')
