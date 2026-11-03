"""Amendment of 3 Nov 2026: P-core lanes only; one Voxel-SVIO container moved to the attempt's lane."""
import json
from pathlib import Path
import sys
import tempfile
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


class PCoreLanes(unittest.TestCase):
    def test_only_p_core_cpu_lanes(self):
        cpu = {k: v for k, v in PROTOCOL['lanes'].items() if not v.get('gpu')}
        self.assertEqual({k: v['cpus'] for k, v in cpu.items()}, dict(cpu_a='0-3', cpu_b='4-7', exclusive='0-7'))
        self.assertTrue(all(v['core_type'] == 'P' for v in cpu.values()))

    def test_every_cpu_system_uses_both_p_core_lanes(self):
        for fold in PROTOCOL['folds']:
            if fold['algorithm'] in ('orbslam3', 'okvis2', 'okvis2x', 'openvins', 'voxel_svio', 'svo_pro'):
                self.assertEqual(fold['lanes'], ['cpu_a', 'cpu_b'])

    def test_gate_ids_do_not_reuse_earlier_freezes(self):
        self.assertTrue(all(b[0] >= 76500 for b in PROTOCOL['run_ids']['gate_blocks'].values()))
        self.assertEqual(prepare.SUPERSEDED_FREEZE_IDS, (76000, 76499))

    def test_amendment_is_recorded(self):
        self.assertTrue(any(d['topic'].startswith('P-core lanes only') for d in PROTOCOL['decisions']))

    def test_voxel_container_moves_to_the_lane(self):
        run = Recorder('4-7')
        after = policy.move_persistent_to_lane(PROTOCOL, 'voxel_svio', container('0-3'), 'cpu_b', run=run)
        self.assertEqual(run.calls[0], ['docker', 'update', '--cpuset-cpus', '4-7', 'vslam_search_voxel_20261031'])
        policy.verify_persistent_limits(PROTOCOL, 'voxel_svio', dict(after, HostConfig=dict(after['HostConfig'],
            Memory=64*1024**3, MemorySwap=64*1024**3)), lane='cpu_b')

    def test_no_move_when_already_on_the_lane_or_for_other_systems(self):
        run = Recorder('0-3')
        policy.move_persistent_to_lane(PROTOCOL, 'voxel_svio', container('0-3'), 'cpu_a', run=run)
        policy.move_persistent_to_lane(PROTOCOL, 'airslam', container('16-23'), 'cpu_a', run=run)
        self.assertEqual(run.calls, [])

    def test_a_failed_move_is_refused(self):
        with self.assertRaises(RuntimeError):
            policy.move_persistent_to_lane(PROTOCOL, 'voxel_svio', container('0-3'), 'cpu_b', run=Recorder('0-3'))


class ActivationPerDataset(unittest.TestCase):
    def test_only_the_started_dataset_must_be_ready(self):
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
