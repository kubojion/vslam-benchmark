"""Tests for loss detection and independent attempt/seed identities, without runs."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ART = Path(__file__).resolve().parent
WORK = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(WORK / 'scripts/analysis'), str(WORK / 'scripts/analysis')]
import noise_delivery
import noise_campaign_engine as engine


class DeliveryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='noise-delivery-', dir=ART)
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

    def test_full_receipt_passes(self):
        self.assertTrue(self.audit()['passed'])

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

    def test_final_run_has_fresh_identity_and_valid_seed(self):
        engine.CAMPAIGN = 'test-only'
        first = engine.identities('fusion_citrus', 'candidate1', 'seq04', 'vio', 1, 'full')
        second = engine.identities('fusion_citrus', 'candidate2', 'seq04', 'vio', 1, 'full')
        final = engine.identities('fusion_citrus', 'candidate1', 'seq04', 'vio', 1, 'final_n1')
        self.assertNotEqual(first[1], second[1])
        self.assertEqual(first[2], second[2])
        self.assertNotEqual(first[1], final[1])
        self.assertNotEqual(first[2], final[2])
        self.assertTrue(0 <= first[2] < 2**32)
        self.assertEqual(first, engine.identities('fusion_citrus', 'candidate1', 'seq04', 'vio', 1, 'full'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
