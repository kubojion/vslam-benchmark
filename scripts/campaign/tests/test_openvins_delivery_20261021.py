"""OpenVINS input-delivery gate (scripts/run/_openvins_delivery.py), without runs.

Ported from the noise experiment's delivery tests; search-campaign cases removed.
"""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'run'))
import _openvins_delivery as noise_delivery


class DeliveryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='openvins-delivery-')
        self.root = Path(self.temp.name)
        self.run = self.root / 'run'
        self.run.mkdir()
        self.sequence = self.root / 'sequence'
        for sensor, stamps in [('cam0', [1000000000, 1100000000]),
                               ('cam1', [1000000000, 1100000000]),
                               ('imu0', [990000000, 1000000000, 1010000000, 1100000000, 1110000000])]:
            path = self.sequence / 'mav0' / sensor / 'data.csv'
            path.parent.mkdir(parents=True)
            path.write_text('#timestamp,payload\n' + ''.join(f'{t},unused\n' for t in stamps))
        self.received = dict(schema=1, camera_queued=2, camera_processed=2,
                             camera_rate_dropped=0, camera_remaining=0)
        for name, sensor in [('imu', 'imu0'), ('stereo', 'cam0')]:
            values = noise_delivery.expected(self.sequence / 'mav0' / sensor / 'data.csv')
            self.received[name + '_received'] = values['count']
            self.received[name + '_stamp_sum_u64'] = values['sum_u64']
            self.received[name + '_stamp_xor_u64'] = values['xor_u64']
        self.write_receipt()
        (self.run / 'transport_stats.json').write_text(json.dumps(dict(
            imu_messages_published=5, camera_frames_published=2, camera_read_failures=0)))
        (self.run / 'openvins_node.log').write_text('[TIME]: 0.01 seconds total\n' * 2)

    def tearDown(self):
        self.temp.cleanup()

    def write_receipt(self):
        (self.run / 'openvins_input_receipt.json').write_text(json.dumps(self.received))

    def audit(self, allowed=0):
        return noise_delivery.audit_openvins(self.run, self.sequence, allowed_pending_tail=allowed)

    def test_glog_interleaving_preserves_complete_feed_count(self):
        original = ('[TIME]: 0.0022 sWARNING: Logging before InitGoogleLogging() is written to STDERR\n'
                    'E1011 14:29:37.108036   549 covariance_impl.cc:651] Jacobian matrix is rank deficient.\n'
                    'econds total (447.8 hz, 0.20 ms behind)\n'
                    '[TIME]: 0.01 seconds total\n')
        path = self.run / 'openvins_node.log'
        path.write_text(original)
        report = self.audit()
        self.assertTrue(report['passed'])
        counts = report['timing_log_evidence']
        self.assertEqual(counts['raw_complete_messages'], 1)
        self.assertEqual(counts['complete_messages'], 2)
        self.assertEqual(counts['glog_warnings_removed'], 1)
        self.assertEqual(counts['glog_messages_removed'], 1)
        self.assertEqual(path.read_text(), original)

    def test_incomplete_or_unknown_split_message_still_fails(self):
        for text in ('[TIME]: 0.01 seconds total\n[TIME]: 0.02 s',
                     '[TIME]: 0.01 seconds total\n[TIME]: 0.02 sUNKNOWN WARNING\neconds total\n'):
            (self.run / 'openvins_node.log').write_text(text)
            self.assertFalse(self.audit()['checks']['native_log_matches_receipt'])

    def test_duplicate_feed_messages_still_fail(self):
        (self.run / 'openvins_node.log').write_text('[TIME]: 0.01 seconds total\n' * 3)
        self.assertFalse(self.audit()['checks']['native_log_matches_receipt'])

    def test_other_debug_timing_messages_are_not_feed_calls(self):
        with (self.run / 'openvins_node.log').open('a') as stream:
            stream.write('[TIME]: 0.01 seconds for tracking\n[TIME]: 0.02 sec total for initialization\n')
        self.assertTrue(self.audit()['passed'])

    def test_log_repair_cannot_hide_sensor_loss(self):
        (self.run / 'openvins_node.log').write_text(
            '[TIME]: 0.01 seconds total\n'
            '[TIME]: 0.02 sE1011 14:29:37.108036   549 covariance_impl.cc:651] warning\neconds total\n')
        self.received['imu_received'] -= 1
        self.write_receipt()
        report = self.audit()
        self.assertTrue(report['checks']['native_log_matches_receipt'])
        self.assertFalse(report['checks']['imu_count'])
        self.assertFalse(report['passed'])

    def test_full_receipt_passes(self):
        self.assertTrue(self.audit()['passed'])

    def exact_receipt(self):
        (self.run / 'openvins_input_receipt.json.imu-stamps.txt').write_text(
            '990000000\n1000000000\n1010000000\n1100000000\n1110000000\n')
        self.received.update(last_received_imu_ns=1110000000,
            final_camera_imu_offset_s=0., pending_camera_timestamps_s=[])
        self.write_receipt()

    def test_complete_exact_receipt_is_required_by_expanded_campaign(self):
        self.assertFalse(noise_delivery.audit_openvins(self.run,self.sequence,
            allowed_pending_tail=0,require_exact=True)['passed'])
        self.exact_receipt()
        self.assertTrue(noise_delivery.audit_openvins(self.run,self.sequence,
            allowed_pending_tail=0,require_exact=True)['passed'])

    def test_reordering_is_detected_even_when_count_sum_and_xor_match(self):
        self.exact_receipt()
        (self.run / 'openvins_input_receipt.json.imu-stamps.txt').write_text(
            '1000000000\n990000000\n1010000000\n1100000000\n1110000000\n')
        report=self.audit()
        self.assertTrue(report['checks']['imu_count'])
        self.assertTrue(report['checks']['imu_timestamp_sum'])
        self.assertTrue(report['checks']['imu_timestamp_xor'])
        self.assertFalse(report['passed'])

    def test_tail_allowance_cannot_hide_a_missing_interior_frame(self):
        self.exact_receipt()
        self.received.update(camera_processed=1,camera_remaining=1,
                             pending_camera_timestamps_s=[1.0])
        self.write_receipt()
        (self.run / 'openvins_node.log').write_text('[TIME]: 0.01 seconds total\n')
        self.assertFalse(self.audit(allowed=1)['passed'])
        self.received['pending_camera_timestamps_s']=[1.1]
        self.write_receipt()
        report=self.audit(allowed=1)
        self.assertTrue(report['passed'])
        self.assertEqual(report['exact_receipt']['pending_camera_has_later_imu'],[True])

    def test_equal_counts_do_not_hide_wrong_imu_timestamps(self):
        self.received['imu_stamp_sum_u64'] += 1000000
        self.write_receipt()
        report = self.audit()
        self.assertFalse(report['passed'])
        self.assertTrue(report['checks']['imu_count'])
        self.assertFalse(report['checks']['imu_timestamp_sum'])

    def test_native_loss_detected_despite_complete_publisher(self):
        self.received['imu_received'] -= 1
        self.write_receipt()
        report = self.audit()
        self.assertFalse(report['passed'])
        self.assertTrue(report['checks']['publisher_imu_count'])

    def test_tail_allowance_is_explicit_and_rate_drops_never_hidden(self):
        self.received.update(camera_processed=1, camera_remaining=1)
        self.write_receipt()
        (self.run / 'openvins_node.log').write_text('[TIME]: 0.01 seconds total\n')
        self.assertFalse(self.audit()['passed'])
        self.assertTrue(self.audit(allowed=1)['passed'])
        self.received.update(camera_rate_dropped=1)
        self.write_receipt()
        self.assertFalse(self.audit(allowed=1)['passed'])

    def completed(self,processed=2,pending=(),offset=0.):
        self.exact_receipt()
        self.received.update(camera_processed=processed,camera_remaining=len(pending),
            pending_camera_timestamps_s=list(pending),final_camera_imu_offset_s=offset,
            end_of_stream=dict(enabled=True,complete=True,expected_imu=5,expected_stereo=2,
                               eligible_cameras_drained=processed))
        self.write_receipt()
        (self.run/'openvins_node.log').write_text('[TIME]: 0.01 seconds total\n'*processed)
        (self.run/'openvins_end_ack.json').write_text(json.dumps(dict(schema=1,
            request=[1,5,2],acknowledgement=[1,5,2,2,processed,len(pending),processed])))

    def audit_end(self):
        return noise_delivery.audit_openvins(self.run,self.sequence,allowed_pending_tail=None,
                                    require_exact=True,require_end_of_stream=True)

    def test_completed_drain_passes(self):
        self.completed();self.assertTrue(self.audit_end()['passed'])

    def test_eligible_tail_rejected_even_with_end_ack(self):
        self.completed(processed=1,pending=[1.1])
        result=self.audit_end();self.assertFalse(result['passed'])
        self.assertFalse(result['checks']['no_eligible_camera_left_pending'])

    def test_real_imu_support_can_leave_two_unprocessable_final_cameras(self):
        self.completed(processed=0,pending=[1.,1.1],offset=.2)
        self.assertTrue(self.audit_end()['passed'])

    def test_end_ack_required_and_must_match_actual_received_counts(self):
        self.completed();p=self.run/'openvins_end_ack.json';value=json.loads(p.read_text())
        value['acknowledgement'][1]-=1;p.write_text(json.dumps(value))
        self.assertFalse(self.audit_end()['passed'])
        p.unlink();self.assertFalse(self.audit_end()['passed'])

    def test_stale_last_imu_and_nonfinite_offset_are_rejected(self):
        self.completed();self.received['last_received_imu_ns']=1100000000;self.write_receipt()
        self.assertFalse(self.audit_end()['passed'])
        self.completed();self.received['final_camera_imu_offset_s']=float('nan');self.write_receipt()
        self.assertFalse(self.audit_end()['passed'])

    def test_complete_flag_does_not_override_missing_imu(self):
        self.completed();self.received['imu_received']-=1;self.write_receipt()
        self.assertFalse(self.audit_end()['passed'])

    def test_numeric_tail_allowance_cannot_enable_end_policy(self):
        self.completed()
        self.assertFalse(noise_delivery.audit_openvins(self.run,self.sequence,allowed_pending_tail=2,
            require_exact=True,require_end_of_stream=True)['passed'])

    def flow_completed(self):
        self.completed()
        self.received.update(left_received=2,right_received=2,
                             flow_control=dict(enabled=True,acknowledgements_sent=4))
        self.write_receipt()
        for stream in ('left','right','stereo'):
            (self.run/f'openvins_input_receipt.json.{stream}-stamps.txt').write_text('1000000000\n1100000000\n')
        (self.run/'openvins_delivery.json').write_text(json.dumps(dict(player_error=None,
            flow_control=dict(enabled=True,completed_checkpoints=4,last_acknowledgement=[1,5,2,2]))))

    def audit_flow(self):
        return noise_delivery.audit_openvins(self.run,self.sequence,allowed_pending_tail=None,
            require_exact=True,require_end_of_stream=True,require_flow_control=True)

    def test_complete_application_receipt_barriers_pass(self):
        self.flow_completed();self.assertTrue(self.audit_flow()['passed'])

    def test_every_raw_camera_stream_requires_exact_order(self):
        for stream in ('left','right','stereo'):
            with self.subTest(stream=stream):
                self.flow_completed()
                (self.run/f'openvins_input_receipt.json.{stream}-stamps.txt').write_text('1100000000\n1000000000\n')
                self.assertFalse(self.audit_flow()['passed'])

    def test_stale_ack_cannot_qualify_even_with_complete_native_counts(self):
        self.flow_completed();path=self.run/'openvins_delivery.json';row=json.loads(path.read_text())
        row['flow_control']['last_acknowledgement']=[1,4,2,2];path.write_text(json.dumps(row))
        self.assertFalse(self.audit_flow()['passed'])

    def test_partial_output_after_player_error_is_not_a_success(self):
        self.flow_completed();path=self.run/'openvins_delivery.json';row=json.loads(path.read_text())
        row['player_error']='RuntimeError: receipt stalled';path.write_text(json.dumps(row))
        self.assertFalse(self.audit_flow()['passed'])

    def test_missing_raw_stream_and_disabled_native_flow_fail(self):
        self.flow_completed();(self.run/'openvins_input_receipt.json.left-stamps.txt').unlink()
        self.assertFalse(self.audit_flow()['passed'])
        self.flow_completed();self.received['flow_control']['enabled']=False;self.write_receipt()
        self.assertFalse(self.audit_flow()['passed'])


    def gate(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = noise_delivery.main([str(self.run), str(self.sequence)])
        return code, json.loads(out.getvalue())

    def test_production_gate_cli_passes_complete_flow_controlled_delivery(self):
        self.flow_completed()
        code, report = self.gate()
        self.assertEqual(code, 0)
        self.assertTrue(report['passed'])
        self.assertTrue(report['flow_control_required'] and report['end_of_stream_required'])
        self.assertIsNone(report['allowed_pending_tail'])

    def test_production_gate_cli_fails_closed_on_loss_or_missing_receipt(self):
        self.flow_completed()
        self.received['imu_received'] -= 1
        self.write_receipt()
        code, report = self.gate()
        self.assertEqual(code, 1)
        self.assertFalse(report['passed'])
        (self.run / 'openvins_input_receipt.json').unlink()
        code, report = self.gate()
        self.assertEqual(code, 1)
        self.assertFalse(report['passed'])
        self.assertIn('FileNotFoundError', report['error'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
