import copy
import fcntl
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import noise_concurrency as runner


class ConcurrencyTests(unittest.TestCase):
    def test_lease_rejects_wrong_or_unlocked_descriptor(self):
        with tempfile.TemporaryDirectory() as d:
            lock=Path(d)/'execution.lock'
            wrong=Path(d)/'wrong.lock'
            lock.touch(); wrong.touch()
            with patch.object(runner,'LOCK',lock), patch.object(runner.ENGINE,'production_processes',return_value=[]):
                with lock.open('rb') as descriptor:
                    with self.assertRaises(RuntimeError):
                        with runner.leased_slot(descriptor.fileno(),os.getppid()):
                            pass
                    fcntl.flock(descriptor,fcntl.LOCK_EX)
                    with runner.leased_slot(descriptor.fileno(),os.getppid()):
                        pass
                    with wrong.open('rb') as other:
                        with self.assertRaises(RuntimeError):
                            with runner.leased_slot(other.fileno(),os.getppid()):
                                pass

    def test_assessment_rejects_accuracy_regression_and_dropped_inputs(self):
        protocol=runner.protocol()
        rows=[]
        for case in protocol['cases']:
            for condition in protocol['conditions']:
                for rep in range(3):
                    rows.append(dict(study=case['spec']['id'],phase=runner.CONDITION_PHASE[condition],
                        state='finished',timeout=False,returncode=0,wall_s=100,
                        result=dict(failed=False,ate_se3_rmse_m=.3,export_support_fraction=.98)))
        batches=[dict(condition='serial',wall_s=300),dict(condition='parallel',wall_s=150)]
        with patch.object(runner,'receipt',return_value=dict(imu_received=36000,stereo_received=1800,stereo_queued_after_rate_gate=1799)):
            self.assertTrue(runner.assess(rows,batches,protocol)['passed'])
            changed=copy.deepcopy(rows)
            changed[-1]['result']['ate_se3_rmse_m']=.8
            self.assertFalse(runner.assess(changed,batches,protocol)['passed'])
            changed[-1]['result']['ate_se3_rmse_m']=None
            self.assertFalse(runner.assess(changed,batches,protocol)['passed'])
        with patch.object(runner,'receipt',side_effect=lambda r:dict(stereo_received=1790 if r['phase']==runner.CONDITION_PHASE['parallel'] else 1800)):
            self.assertFalse(runner.assess(rows,batches,protocol)['passed'])


if __name__=='__main__':
    unittest.main()
