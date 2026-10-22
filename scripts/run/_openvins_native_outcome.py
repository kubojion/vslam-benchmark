#!/usr/bin/env python3
"""Attribute a failed OpenVINS attempt: estimator failure or input delivery, from evidence only.

With flow control the player waits for the native receipt of every stereo pair. When
the estimator itself stops (OpenVINS calls std::exit on a negative covariance
diagonal; the static teardown can then segfault while ROS threads still publish), the
player only sees missing acknowledgements and reports a stall. This separates:

- the native process ending on its own, before the player gave up, with exact delivery
  up to the last acknowledged pair: an estimator failure (a measured result);
- a stall while the native process was still alive: an input-delivery fault.

It reads the attempt's records, never ATE, and changes nothing. CLI: prints JSON.
"""
import argparse
import json
from pathlib import Path
import re
import sys

# OpenVINS prints these right before its own std::exit(EXIT_FAILURE) (ov_msckf/src/state).
NUMERICAL = re.compile(r'StateHelper::EKF(?:Update|Propagation)\(\) - diagonal at \d+ is [-+0-9.eEnaif]+')
TIME_ORDER = re.compile(r'Propagator::propagate_and_clone\(\): [^\n]*')
OTHER_ABORT = re.compile(r'StateHelper::[A-Za-z_]+\(\) - Called [^\n]*')
ANSI = re.compile(r'\x1b\[[0-9;]*m')
# The player's stall wait is 30 s; a native process that ended on its own did so well before.
NATIVE_FIRST_MARGIN_S = 1.0


def load(path):
    path = Path(path)
    return json.loads(path.read_text()) if path.is_file() else None


def delivery_before_failure(delivery):
    """Exact native receipt through the last acknowledged pair, from the flow-control record."""
    if not delivery or not (delivery.get('flow_control') or {}).get('enabled'):
        return dict(flow_control=False, exact_through_last_acknowledgement=None)
    ack = delivery['flow_control'].get('last_acknowledgement')
    published = dict(imu=delivery.get('published_imu'), left=delivery.get('published_left'),
                     right=delivery.get('published_right'))
    if not (isinstance(ack, list) and len(ack) == 4 and ack[0] == 1):
        return dict(flow_control=True, acknowledged=ack, published=published,
                    exact_through_last_acknowledgement=False)
    acknowledged = dict(imu=ack[1], left=ack[2], right=ack[3])
    in_flight = published['left'] - acknowledged['left']
    # The player publishes one pair (and its IMU) and then waits for its receipt.
    exact = (acknowledged['left'] == acknowledged['right'] and published['left'] == published['right']
             and in_flight in (0, 1) and 0 <= acknowledged['imu'] <= published['imu'])
    return dict(flow_control=True, acknowledged=acknowledged, published=published,
                pairs_in_flight=in_flight, exact_through_last_acknowledgement=exact)


def classify(run):
    run = Path(run)
    node, player = load(run / 'processes/node.json') or {}, load(run / 'processes/player.json') or {}
    delivery = load(run / 'openvins_delivery.json')
    log = run / 'openvins_node.log'
    text = ANSI.sub('', log.read_text(errors='replace')) if log.is_file() else ''
    messages = dict(numerical=NUMERICAL.findall(text)[:8], time_order=TIME_ORDER.findall(text)[:8],
                    other=OTHER_ABORT.findall(text)[:8])
    exit_code = node.get('exit_code')
    player_error = (delivery or {}).get('player_error')
    native_end, player_end = node.get('finished_unix'), player.get('finished_unix')
    native_first = (isinstance(native_end, (int, float)) and isinstance(player_end, (int, float))
                    and native_end + NATIVE_FIRST_MARGIN_S <= player_end)
    prefix = delivery_before_failure(delivery)
    failed_alone = exit_code not in (None, 0) and native_first
    if failed_alone and messages['time_order']:
        # Time order can come from the input stream; never call it an estimator result unreviewed.
        classification = 'native_time_order_abort'
    elif failed_alone and prefix['exact_through_last_acknowledgement'] is not False:
        classification = ('estimator_numerical_abort' if messages['numerical'] else
                          'estimator_abort' if messages['other'] else 'estimator_crash')
    elif player_error and 'stalled' in player_error and not failed_alone:
        classification = 'input_delivery_stall'
    else:
        classification = 'unclassified'
    return dict(schema=1, classification=classification,
                estimator_failure=classification.startswith('estimator_'),
                native=dict(status=node.get('status'), exit_code=exit_code, finished_unix=native_end,
                            ended_before_player=native_first, abort_messages=messages),
                player=dict(error=player_error, finished_unix=player_end),
                delivery_before_failure=prefix,
                note=('estimator_* means the native estimator ended on its own after exact delivery up to its last '
                      'acknowledged pair: a measured failure, not an input fault. Other classes need review.'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('run', type=Path, help='physical attempt directory')
    args = parser.parse_args(argv)
    try:
        report = classify(args.run)
    except Exception as exc:  # never hide a failed attempt behind a classifier error
        report = dict(schema=1, classification='unclassified', estimator_failure=False,
                      error=f'{type(exc).__name__}: {exc}')
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
