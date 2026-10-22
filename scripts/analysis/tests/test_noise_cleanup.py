"""Cancellation must never interpret container PIDs in the host namespace."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import noise_cleanup as cleanup


class OwnershipChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run = self.root / 'results/vio/citrusfarm/seq04/openvins/run99'
        (self.run / 'processes').mkdir(parents=True)
        (self.run / 'processes/node.json').write_text('{}')
        self.cid = 'a' * 64
        (self.run / 'docker.cid').write_text(self.cid)
        self.container = dict(Id=self.cid, Name='/vslam_openvins_citrusfarm_seq04_99_10',
            Mounts=[dict(Source=str(self.root), Destination='/ws')], State=dict(Running=True))
        self.process = Mock()
        self.process.poll.return_value = 0

    def tearDown(self):
        self.temporary.cleanup()

    def test_wrong_workspace_cannot_be_stopped(self):
        self.container['Mounts'][0]['Source'] = '/production'
        with patch.object(cleanup, 'inspect_container', return_value=self.container):
            with self.assertRaisesRegex(RuntimeError, 'ownership mismatch'):
                cleanup.stop_owned_attempt(self.process, self.run, self.root)

    def test_other_attempt_cannot_be_stopped(self):
        self.container['Name'] = '/vslam_openvins_citrusfarm_seq04_100_10'
        with patch.object(cleanup, 'inspect_container', return_value=self.container):
            with self.assertRaisesRegex(RuntimeError, 'ownership mismatch'):
                cleanup.stop_owned_attempt(self.process, self.run, self.root)

    def test_container_state_is_always_checked_in_container_namespace(self):
        with patch.object(cleanup, 'inspect_container', side_effect=[self.container, None]), \
                patch.object(cleanup.subprocess, 'run') as execute:
            cleanup.stop_owned_attempt(self.process, self.run, self.root)
        command = execute.call_args.args[0]
        self.assertIn('--container', command)
        self.assertEqual(command[command.index('--container') + 1], self.cid)
        self.assertEqual(command[command.index('--container-state') + 1],
            '/ws/results/vio/citrusfarm/seq04/openvins/run99/processes/node.json')

    def test_removed_container_never_falls_back_to_host_process_records(self):
        with patch.object(cleanup, 'inspect_container', return_value=None), \
                patch.object(cleanup.subprocess, 'run') as execute:
            cleanup.stop_owned_attempt(self.process, self.run, self.root)
        execute.assert_not_called()

    def test_detached_host_child_is_cleaned_even_when_wrapper_has_exited(self):
        run = self.root / 'results/vio/citrusfarm/seq04/basalt/run100'
        (run / 'processes').mkdir(parents=True)
        (run / 'processes/estimator.json').write_text('{}')
        with patch.object(cleanup.subprocess, 'run') as execute:
            cleanup.stop_owned_attempt(self.process, run, self.root)
        command = execute.call_args.args[0]
        self.assertEqual(command[-1], 'stop')
        self.assertNotIn('--container', command)

    def test_docker_permission_failure_is_not_treated_as_container_removed(self):
        with patch.object(cleanup.subprocess, 'run', return_value=Mock(returncode=1,
                stderr='permission denied connecting to Docker daemon')):
            with self.assertRaisesRegex(RuntimeError, 'Cannot verify'):
                cleanup.inspect_container(self.cid)


if __name__ == '__main__':
    unittest.main(verbosity=2)
