"""OpenVINS failure attribution (estimator vs input delivery), from records only; no runs."""
import io
import json
from pathlib import Path
import sys
from contextlib import redirect_stdout

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'scripts/run'))
import _openvins_native_outcome as outcome  # noqa: E402

RUNNER = (REPO / 'scripts/run/run_openvins.sh').read_text()
# The Sielinko clip run13011 (22 Oct): native SIGSEGV 38 s after start, player stalled 30 s later.
NODE_END, PLAYER_END = 1792687854.39, 1792687884.41
NUMERICAL = '\x1b[31mStateHelper::EKFUpdate() - diagonal at 78 is -0.00\n\x1b[0m'


def attempt(tmp_path, *, exit_code=-11, node_end=NODE_END, player_end=PLAYER_END, log='[TIME]: 0.01 seconds total\n',
            ack=(1, 3422, 345, 345), published=(3436, 346, 346), flow=True,
            error='RuntimeError: Native input receipt stalled at [1, 3436, 346, 346]; last acknowledgement [1, 3422, 345, 345]'):
    run = tmp_path / 'run13011'
    (run / 'processes').mkdir(parents=True)
    (run / 'processes/node.json').write_text(json.dumps(dict(status='exited', exit_code=exit_code, finished_unix=node_end)))
    (run / 'processes/player.json').write_text(json.dumps(dict(status='exited', exit_code=1, finished_unix=player_end)))
    (run / 'openvins_node.log').write_text(log)
    (run / 'openvins_delivery.json').write_text(json.dumps(dict(
        published_imu=published[0], published_left=published[1], published_right=published[2], player_error=error,
        flow_control=dict(enabled=flow, completed_checkpoints=346, last_acknowledgement=list(ack) if ack else None))))
    return run


def test_numerical_abort_after_exact_delivery_is_an_estimator_failure(tmp_path):
    report = outcome.classify(attempt(tmp_path, log='[TIME]: 0.01\n' + NUMERICAL))
    assert report['classification'] == 'estimator_numerical_abort'
    assert report['estimator_failure'] is True
    assert report['native']['abort_messages']['numerical'] == ['StateHelper::EKFUpdate() - diagonal at 78 is -0.00']
    prefix = report['delivery_before_failure']
    assert prefix['exact_through_last_acknowledgement'] is True and prefix['pairs_in_flight'] == 1
    assert prefix['acknowledged'] == dict(imu=3422, left=345, right=345)


def test_teardown_crash_without_a_message_is_still_the_estimator(tmp_path):
    report = outcome.classify(attempt(tmp_path))
    assert report['classification'] == 'estimator_crash' and report['estimator_failure']


def test_stall_while_the_native_process_lives_is_an_input_fault(tmp_path):
    # The native process ended only after the player gave up (stopped by the cleanup).
    for exit_code, node_end in ((0, PLAYER_END + 2), (-2, PLAYER_END + 2), (-11, PLAYER_END - 0.5)):
        report = outcome.classify(attempt(tmp_path / str(node_end) / str(exit_code), exit_code=exit_code, node_end=node_end))
        assert report['classification'] == 'input_delivery_stall', (exit_code, node_end)
        assert report['estimator_failure'] is False


def test_missing_acknowledged_pairs_are_never_called_an_estimator_failure(tmp_path):
    for ack in ((1, 3422, 343, 343), (1, 3422, 345, 344), (1, 3500, 345, 345), (0, 3422, 345, 345)):
        report = outcome.classify(attempt(tmp_path / '-'.join(map(str, ack)), ack=ack, log=NUMERICAL))
        assert report['classification'] == 'unclassified', ack
        assert report['delivery_before_failure']['exact_through_last_acknowledgement'] is False


def test_time_order_abort_needs_review_even_when_the_estimator_exits(tmp_path):
    log = 'Propagator::propagate_and_clone(): Propagation called trying to propagate backwards in time!!!!\n'
    report = outcome.classify(attempt(tmp_path, exit_code=1, log=log))
    assert report['classification'] == 'native_time_order_abort' and report['estimator_failure'] is False


def test_without_flow_control_delivery_is_unknown_not_assumed(tmp_path):
    report = outcome.classify(attempt(tmp_path, flow=False, error=None, log=NUMERICAL))
    assert report['classification'] == 'estimator_numerical_abort'
    assert report['delivery_before_failure'] == dict(flow_control=False, exact_through_last_acknowledgement=None)


def test_missing_records_fail_closed(tmp_path):
    run = tmp_path / 'empty'
    run.mkdir()
    assert outcome.classify(run)['classification'] == 'unclassified'
    (run / 'openvins_delivery.json').write_text('{not json')
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        assert outcome.main([str(run)]) == 0
    report = json.loads(buffer.getvalue())
    assert report['classification'] == 'unclassified' and report['estimator_failure'] is False and 'error' in report


def test_runner_keeps_native_output_buffering_and_attributes_failures():
    # Line buffering changed OpenVINS's result on CitrusFarm seq04 (0.8380 vs 0.8532 m); never add it.
    assert 'owned_run node $NODE_PREFIX /colcon_ws/install/lib/ov_msckf/run_subscribe_msckf' in RUNNER
    assert 'stdbuf' not in RUNNER.replace('line buffering', '')
    failure = RUNNER[RUNNER.index('if (( OPENVINS_RC != 0 )); then'):]
    failure = failure[:failure.index('\nfi\n')]
    assert '_openvins_native_outcome.py' in failure and 'native_outcome=' in failure
    assert 'native outcome: $OUTCOME' in failure
    # Successful attempts and the delivery gate are unchanged.
    assert RUNNER.count('_openvins_native_outcome.py') == 1


def test_gdb_diagnostic_requires_the_validated_image_plus_one_layer():
    block = RUNNER[RUNNER.index('if [[ "${OPENVINS_GDB:-0}" == 1 ]]; then'):]
    block = block[:block.index('\nfi\n')]
    assert 'len(debug) == len(base) + 1 and debug[:len(base)] == base' in block
    assert 'diagnostic_gdb_image=' in block
    assert RUNNER.index('OPENVINS_IMAGE_ID=sha256:2f74b56e') < RUNNER.index('if [[ "${OPENVINS_GDB:-0}" == 1 ]]; then')
