import json
from pathlib import Path
import tempfile
import unittest
import noise_voxel_delivery as audit


class NativeGateTests(unittest.TestCase):
    def test_rejected_frame_does_not_move_last_accepted_time(self):
        prediction=audit.native_rate_prediction([0,33_000_000,60_000_000,100_000_000],20.)
        self.assertEqual(prediction['queued'],2)
        self.assertEqual([r['index'] for r in prediction['rate_skipped']],[1,3])

    def test_exact_native_boundary_is_accepted(self):
        self.assertEqual(audit.native_rate_prediction([0,50_000_000,100_000_000],20.)['queued'],3)

    def test_invalid_rate_cannot_silently_skip_everything(self):
        for rate in [0.,-1.,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):
                audit.native_rate_prediction([0,1],rate)

    def fixture(self,root):
        run=root/'run';dataset=root/'dataset';(run/'native').mkdir(parents=True)
        stamps=[0,33_000_000,100_000_000]
        for name in ['cam0','cam1','imu0']:
            path=dataset/'mav0'/name/'data.csv';path.parent.mkdir(parents=True)
            path.write_text('#timestamp\n'+'\n'.join(str(t)+',data' for t in stamps)+'\n')
        tx=dict(camera_frames_expected=3,camera_frames_published=3,imu_messages_published=3,camera_read_failures=0)
        rx=dict(stereo_received=3,imu_received=3,stereo_queued_after_rate_gate=2,
                first_camera_s=0.,last_camera_s=.1,first_imu_s=0.,last_imu_s=.1)
        (run/'transport_stats.json').write_text(json.dumps(tx))
        (run/'native/input_receipt.json').write_text(json.dumps(rx))
        (run/'native/parameter_list.txt').write_text('track_frequency: 20.0\n')
        (run/'effective_ros_parameters.yaml').write_text('odometry_parameter:\n  track_frequency: 20.0\n')
        return run,dataset

    def test_expected_gate_is_distinguished_from_input_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            run,dataset=self.fixture(Path(directory))
            self.assertTrue(audit.audit(run,dataset)['passed'])
            receipt=run/'native/input_receipt.json';rx=json.loads(receipt.read_text())
            rx['stereo_queued_after_rate_gate']=1;receipt.write_text(json.dumps(rx))
            self.assertFalse(audit.audit(run,dataset)['passed'])

    def test_frequency_or_input_delivery_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            run,dataset=self.fixture(Path(directory))
            (run/'native/parameter_list.txt').write_text('track_frequency: 30.0\n')
            self.assertFalse(audit.audit(run,dataset)['passed'])
            (run/'native/parameter_list.txt').write_text('track_frequency: 20.0\n')
            receipt=run/'native/input_receipt.json';rx=json.loads(receipt.read_text())
            rx['imu_received']=2;receipt.write_text(json.dumps(rx))
            self.assertFalse(audit.audit(run,dataset)['passed'])


if __name__=='__main__':
    unittest.main()
