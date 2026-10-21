#!/usr/bin/env python3
"""Post-run input-delivery gate for OpenVINS: native receipts, never ATE.

Ported from the noise experiment (scripts/analysis/noise_delivery.py on
experiment/imu-noise-reliable-20261009). run_openvins.sh calls the CLI after
every run under the production delivery policy; a failed gate marks the
attempt as an infrastructure fault.
"""
import argparse
import csv
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
import sys


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


def timing_log_evidence(log):
    """Count completed-feed timing lines despite interleaved Ceres/glog stderr.

    The native counter and exact sensor receipts remain authoritative. This
    redundant log check still requires a complete timing message: remove only
    recognized, newline-terminated glog messages from an in-memory copy. Never
    accept a timing prefix alone or change the preserved estimator log.
    """
    pattern = r'\[TIME\]: [0-9.eE+-]+ seconds total'
    without_warning, warnings = re.subn(
        r'WARNING: Logging before InitGoogleLogging\(\) is written to STDERR\r?\n', '', log)
    normalized, messages = re.subn(
        r'[IWEF]\d{4} \d{2}:\d{2}:\d{2}\.\d+ +\d+ '
        r'[A-Za-z0-9_.-]+:\d+\] [^\r\n]*\r?\n', '', without_warning)
    return dict(raw_complete_messages=len(re.findall(pattern, log)),
                complete_messages=len(re.findall(pattern, normalized)),
                glog_warnings_removed=warnings, glog_messages_removed=messages,
                raw_log_sha256=hashlib.sha256(log.encode()).hexdigest())


def audit_openvins(run, sequence, *, allowed_pending_tail, require_exact=False, require_end_of_stream=False,
                   require_flow_control=False):
    """Separate receipt from processing with a fixed or native-eligibility tail policy.

    A final camera may await future IMU or a processing trigger when playback
    ends. Detailed receipts identify its timestamp and IMU eligibility. The tail
    allowance is frozen by the campaign protocol, never adjusted to improve ATE.
    All published IMU samples and stereo pairs must still be received exactly.
    With an explicit end-of-stream drain, allowed_pending_tail must be None:
    every remaining camera must be in the true suffix and lack later real IMU
    support at the native estimated offset. An eligible unprocessed frame fails.
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
    if require_end_of_stream:
        # This policy allows only the actual recording suffix that has no
        # later real IMU sample at the native estimated clock offset. It does
        # not increase a fixed lost-frame allowance to make a run pass.
        checks['end_policy_requires_exact_receipt'] = require_exact and allowed_pending_tail is None
    else:
        checks['bounded_pending_tail'] = (isinstance(allowed_pending_tail, int)
            and 0 <= received['camera_remaining'] <= allowed_pending_tail)
    log = (run / 'openvins_node.log').read_text(errors='replace')
    log_evidence = timing_log_evidence(log)
    checks['native_log_matches_receipt'] = log_evidence['complete_messages'] == received['camera_processed']
    exact_path = run / 'openvins_input_receipt.json.imu-stamps.txt'
    exact = None
    if require_exact or exact_path.exists():
        checks['exact_imu_receipt_present'] = exact_path.is_file()
        checks['pending_camera_timestamps_present'] = 'pending_camera_timestamps_s' in received
        if exact_path.is_file():
            stamps = [int(x) for x in exact_path.read_text().splitlines() if x.strip()]
            reference = [int(row[0]) for row in csv.reader((sequence / 'mav0/imu0/data.csv').read_text().splitlines())
                         if row and not row[0].lstrip().startswith('#')]
            checks['exact_ordered_imu_timestamps'] = stamps == reference
            expected_set, got_set = set(reference), set(stamps)
            missing = [t for t in reference if t not in got_set]
            extra = [t for t in stamps if t not in expected_set]
            exact = dict(sha256=hashlib.sha256(exact_path.read_bytes()).hexdigest(),
                         received=len(stamps), missing_count=len(missing), extra_count=len(extra),
                         missing_first20=missing[:20], extra_first20=extra[:20],
                         duplicate_count=len(stamps)-len(got_set))
        if 'pending_camera_timestamps_s' in received:
            pending = received['pending_camera_timestamps_s']
            cameras = [int(row[0]) for row in csv.reader((sequence / 'mav0/cam0/data.csv').read_text().splitlines())
                       if row and not row[0].lstrip().startswith('#')]
            tail = cameras[-len(pending):] if pending else []
            checks['pending_camera_is_recording_tail'] = (len(pending) == received['camera_remaining']
                and len(pending) == len(tail)
                and all(abs(t - stamp / 1e9) <= 5e-7 for t, stamp in zip(pending, tail)))
            if exact is not None:
                last_ns = received['last_received_imu_ns']
                last_imu = last_ns // 1000000000 + (last_ns % 1000000000) * 1e-9
                offset = received['final_camera_imu_offset_s']
                exact['pending_camera_has_later_imu'] = [t < last_imu - offset for t in pending]
                exact['pending_note'] = ('Eligibility is diagnostic: an eligible final frame may lack a later '
                    'callback to trigger processing. No frame is synthesized or replayed.')
    if require_end_of_stream:
        end = received.get('end_of_stream', {})
        checks['native_end_of_stream_complete'] = (end.get('enabled') is True
            and end.get('complete') is True and end.get('expected_imu') == imu['count']
            and end.get('expected_stereo') == left['count'])
        ack_path = run / 'openvins_end_ack.json'
        checks['end_acknowledgement_present'] = ack_path.is_file()
        if ack_path.is_file():
            ack = json.loads(ack_path.read_text())
            checks['end_acknowledgement_matches_native_receipt'] = (ack.get('schema') == 1
                and ack.get('request') == [1, imu['count'], left['count']]
                and ack.get('acknowledgement') == [1, received['imu_received'], received['stereo_received'],
                    received['camera_queued'], received['camera_processed'], received['camera_remaining'],
                    end.get('eligible_cameras_drained')])
        checks['native_last_imu_is_input_end'] = (exact is not None and bool(reference)
            and received.get('last_received_imu_ns') == reference[-1])
        pending = received.get('pending_camera_timestamps_s')
        offset = received.get('final_camera_imu_offset_s')
        finite = (isinstance(offset, (int,float)) and math.isfinite(offset)
            and isinstance(pending, list) and all(isinstance(t,(int,float)) and math.isfinite(t) for t in pending))
        checks['finite_native_end_clock'] = finite
        checks['no_eligible_camera_left_pending'] = (finite and exact is not None
            and len(exact.get('pending_camera_has_later_imu', [])) == received['camera_remaining']
            and not any(exact.get('pending_camera_has_later_imu', [])))
        if exact is not None:
            exact['pending_note'] = 'After explicit end-of-recording drain, every pending camera must lack later real IMU support. No sensor sample is synthesized or replayed.'
    if require_flow_control:
        checks['flow_requires_exact_end_policy'] = require_exact and require_end_of_stream
        flow = received.get('flow_control', {})
        checks['native_flow_control_enabled'] = (flow.get('enabled') is True
            and flow.get('acknowledgements_sent', 0) > 0)
        for stream, sensor in [('left','cam0'), ('right','cam1'), ('stereo','cam0')]:
            path = run / f'openvins_input_receipt.json.{stream}-stamps.txt'
            checks[f'exact_{stream}_receipt_present'] = path.is_file()
            if path.is_file():
                actual = [int(x) for x in path.read_text().splitlines() if x.strip()]
                wanted = [int(row[0]) for row in csv.reader((sequence/f'mav0/{sensor}/data.csv').read_text().splitlines())
                          if row and not row[0].lstrip().startswith('#')]
                checks[f'exact_ordered_{stream}_timestamps'] = actual == wanted
                checks[f'{stream}_raw_count_matches'] = received.get(stream+'_received') == len(wanted)
        player_path = run/'openvins_delivery.json'
        checks['flow_player_receipt_present'] = player_path.is_file()
        if player_path.is_file():
            player = json.loads(player_path.read_text())
            flow = player.get('flow_control', {})
            checks['player_flow_control_completed'] = (flow.get('enabled') is True
                and flow.get('completed_checkpoints',0) >= left['count'] + 2
                and flow.get('last_acknowledgement') == [1,imu['count'],left['count'],left['count']]
                and player.get('player_error') is None)
    return dict(schema=1, passed=all(checks.values()), checks=checks, native=received,
                publisher=published, expected=dict(imu=imu, stereo=left),
                timing_log_evidence=log_evidence,
                exact_receipt=exact, exact_required=require_exact,
                allowed_pending_tail=allowed_pending_tail,
                end_of_stream_required=require_end_of_stream,
                flow_control_required=require_flow_control,
                note='Counts and timestamp fingerprints audit receipt; processed cameras are completed feed calls, not successful tracking updates.')


def main(argv=None):
    ap = argparse.ArgumentParser(description='Production OpenVINS delivery gate: exact native receipts, '
                                             'explicit end-of-recording drain and flow control.')
    ap.add_argument('run', type=Path, help='physical attempt directory')
    ap.add_argument('sequence', type=Path, help='EuRoC-layout sequence the player replayed')
    args = ap.parse_args(argv)
    try:
        report = audit_openvins(args.run, args.sequence, allowed_pending_tail=None, require_exact=True,
                                require_end_of_stream=True, require_flow_control=True)
    except Exception as exc:  # missing or malformed receipts fail closed, with evidence
        report = dict(schema=1, passed=False, error=f'{type(exc).__name__}: {exc}')
    json.dump(report, sys.stdout, indent=2, default=str)
    sys.stdout.write('\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
