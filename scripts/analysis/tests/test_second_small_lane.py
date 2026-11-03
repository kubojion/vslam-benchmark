"""Amendment of 3 Nov 2026: a second small lane on 12-15, one Voxel-SVIO container moved between lanes."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import noise_campaign
import noise_execution_policy as policy
import prepare_timing_search as prepare

PROTOCOL = json.loads(prepare.PROTOCOL.read_text())


def container(cpus):
    return dict(Name='/vslam_search_voxel_20261031', HostConfig=dict(CpusetCpus=cpus))


class Recorder:
    def __init__(self, after):
        self.calls, self.after = [], after

    def __call__(self, command, **kwargs):
        self.calls.append(command)
        class Done:
            stdout = json.dumps([container(self.after)])
        return Done()


class SecondSmallLane(unittest.TestCase):
    def test_lane_and_memory(self):
        self.assertEqual(PROTOCOL['lanes']['small_b'], dict(cpus='12-15', memory_gib=64, core_type='E'))
        self.assertEqual(PROTOCOL['lanes']['small']['cpus'], '8-11')

    def test_repro_gate_runs_on_the_new_lane(self):
        self.assertEqual(PROTOCOL['gates']['repro']['lane'], 'small_b')

    def test_gate_ids_do_not_reuse_the_first_freeze(self):
        blocks = [b for b in PROTOCOL['run_ids']['gate_blocks'].values()]
        self.assertTrue(all(b[0] >= 76400 for b in blocks))
        self.assertEqual(prepare.SUPERSEDED_FREEZE_IDS, (76000, 76399))

    def test_amendment_is_recorded(self):
        self.assertTrue(any(d['topic'].startswith('Second small lane') for d in PROTOCOL['decisions']))

    def test_voxel_container_moves_to_the_lane(self):
        run = Recorder('12-15')
        after = policy.move_persistent_to_lane(PROTOCOL, 'voxel_svio', container('8-11'), 'small_b', run=run)
        self.assertEqual(run.calls[0], ['docker', 'update', '--cpuset-cpus', '12-15', 'vslam_search_voxel_20261031'])
        self.assertEqual(after['HostConfig']['CpusetCpus'], '12-15')
        policy.verify_persistent_limits(PROTOCOL, 'voxel_svio', dict(after, HostConfig=dict(after['HostConfig'],
            Memory=64*1024**3, MemorySwap=64*1024**3)), lane='small_b')

    def test_no_move_when_already_on_the_lane_or_for_other_systems(self):
        run = Recorder('8-11')
        policy.move_persistent_to_lane(PROTOCOL, 'voxel_svio', container('8-11'), 'small', run=run)
        policy.move_persistent_to_lane(PROTOCOL, 'airslam', container('16-23'), 'small_b', run=run)
        self.assertEqual(run.calls, [])

    def test_a_failed_move_is_refused(self):
        with self.assertRaises(RuntimeError):
            policy.move_persistent_to_lane(PROTOCOL, 'voxel_svio', container('8-11'), 'small_b', run=Recorder('8-11'))


class ActivationPerDataset(unittest.TestCase):
    def test_only_the_started_dataset_must_be_ready(self):
        import tempfile
        art = Path(tempfile.mkdtemp())
        (art/'protocol.json').write_text('{}'); (art/'execution-identity.json').write_text('{}')
        citrus = {f['id']: dict(ready=True) for f in PROTOCOL['folds'] if f['dataset'] == 'citrusfarm'}
        readiness = dict(passed=True, pending=[], protocol_sha256=noise_campaign.BASE.sha(art/'protocol.json'),
                         execution_manifest_sha256=noise_campaign.BASE.sha(art/'execution-identity.json'),
                         studies=citrus, validated_scheduling=PROTOCOL['scheduling'], evidence=[])
        (art/'readiness.json').write_text(json.dumps(readiness))
        self.assertEqual(noise_campaign.verify_activation(art, PROTOCOL, 'citrusfarm')['studies'], citrus)
        with self.assertRaises(RuntimeError):
            noise_campaign.verify_activation(art, PROTOCOL, 'hortimulti')
        with self.assertRaises(RuntimeError):
            noise_campaign.verify_activation(art, PROTOCOL)
