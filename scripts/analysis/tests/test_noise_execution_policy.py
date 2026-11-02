import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import noise_execution_policy as p


class PolicyChecks(unittest.TestCase):
    def setUp(self):
        self.schedule = dict(resource_class={a:'cpu' for a in ['openvins','okvis2','okvis2x','basalt','svo_pro','orbslam3','voxel_svio']},
            slots=dict(cpu=3,gpu=0),validated_concurrent_groups=[['openvins','okvis2','svo_pro'],['openvins','okvis2x','basalt']])
        self.schedule['resource_class']['airslam']='gpu'
        self.protocol = dict(campaign_id='policy-test',scheduling=self.schedule,
            attempt_resource_limits={a:dict(memory_gib=16,swap_gib=0) for a in self.schedule['resource_class']})

    def launch(self, candidate, active):
        return p.can_launch(dict(algorithm=candidate),[dict(algorithm=a) for a in active],self.schedule)

    def test_validated_triples_and_subsets(self):
        self.assertTrue(self.launch('svo_pro',['openvins','okvis2']))
        self.assertTrue(self.launch('basalt',['openvins','okvis2x']))
        self.assertTrue(self.launch('openvins',['okvis2x']))

    def test_free_slots_do_not_authorize_unvalidated_mix(self):
        self.assertFalse(self.launch('okvis2x',['okvis2']))
        self.assertFalse(self.launch('orbslam3',['openvins']))
        self.assertFalse(self.launch('basalt',['openvins','okvis2']))

    def test_algorithm_exclusion_and_resource_exclusion(self):
        self.assertFalse(self.launch('openvins',['openvins']))
        self.assertFalse(self.launch('airslam',[]))
        self.assertFalse(self.launch('airslam',['openvins']))

    def test_empty_evidence_is_serial_only(self):
        self.schedule.pop('validated_concurrent_groups')
        self.assertTrue(self.launch('openvins',[]))
        self.assertFalse(self.launch('okvis2',['openvins']))

    def test_declared_slot_limit_remains_binding(self):
        self.schedule['slots']['cpu']=1
        self.assertFalse(self.launch('okvis2',['openvins']))

    def test_command_uses_argument_vector_and_exact_limits(self):
        command=['bash','/a path/run.sh','sequence']
        result=p.bounded_command(command,self.protocol,'okvis2',123,{})
        self.assertEqual(result[-3:],command)
        self.assertIn('MemoryMax=16G',result)
        self.assertIn('MemorySwapMax=0',result)
        self.assertEqual(result,p.bounded_command(command,self.protocol,'okvis2',123,{}))

    def test_missing_limits_fail_closed(self):
        self.protocol['attempt_resource_limits'].pop('okvis2')
        with self.assertRaisesRegex(RuntimeError,'No reviewed resource'):
            p.bounded_command(['bash'],self.protocol,'okvis2',1,{})

    def test_docker_daemon_children_require_their_own_limits(self):
        with self.assertRaisesRegex(RuntimeError,'Docker limits differ'):
            p.bounded_command(['bash'],self.protocol,'openvins',1,{})
        env={'TIMING_MEM':str(16*1024**3)}
        self.assertTrue(p.bounded_command(['bash'],self.protocol,'openvins',1,env))

    def test_gpu_lane_keeps_the_rule_c_memory_high_mark(self):
        self.protocol['attempt_resource_limits']['airslam']=dict(memory_gib=50,memory_high_gib=40,swap_gib=0)
        command=p.bounded_command(['bash'],self.protocol,'airslam',1,{})
        self.assertIn('MemoryMax=50G',command)
        self.assertIn('MemoryHigh=40G',command)
        self.assertIn('MemorySwapMax=0',command)

    def test_bad_or_boolean_memory_limits_rejected(self):
        for value in [True,0,-1,65,1.5,'16']:
            with self.subTest(value=value):
                self.protocol['attempt_resource_limits']['okvis2']['memory_gib']=value
                with self.assertRaisesRegex(RuntimeError,'Invalid native memory'):
                    p.validated_limits(self.protocol,'okvis2')

    def test_persistent_resource_or_gpu_mismatch_rejected(self):
        item={'HostConfig':dict(Memory=16*1024**3,MemorySwap=16*1024**3,DeviceRequests=None)}
        p.verify_persistent_limits(self.protocol,'voxel_svio',item)
        bad=copy.deepcopy(item);bad['HostConfig']['Memory']=0
        with self.assertRaisesRegex(RuntimeError,'resource limits differ'):
            p.verify_persistent_limits(self.protocol,'voxel_svio',bad)
        bad=copy.deepcopy(item);bad['HostConfig']['DeviceRequests']=[{'Count':-1}]
        with self.assertRaisesRegex(RuntimeError,'GPU-enabled'):
            p.verify_persistent_limits(self.protocol,'voxel_svio',bad)

    def test_input_identity_depends_on_the_actual_clip_or_full_sequence(self):
        self.protocol.update(frozen_input_sha256={'rosariov2/sequence1':'a'*64,'rosariov2/sequence1_noise180':'b'*64},
            frozen_runtime_sha256={'openvins':'c'*64},frozen_source_sha256={'openvins':'d'*64})
        full=p.identity_environment(self.protocol,'openvins','rosariov2','sequence1')
        short=p.identity_environment(self.protocol,'openvins','rosariov2','sequence1_noise180')
        self.assertEqual(full['VSLAM_EXPECTED_INPUT_SHA256'],'a'*64)
        self.assertEqual(short['VSLAM_EXPECTED_INPUT_SHA256'],'b'*64)

    def test_incomplete_frozen_identity_refuses_execution(self):
        with self.assertRaisesRegex(RuntimeError,'Complete frozen'):
            p.identity_environment(self.protocol,'openvins','rosariov2','sequence1')

    def test_two_phases_and_restart_keep_one_deadline(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory)/'first', Path(directory)/'second'
            first.mkdir();second.mkdir()
            protocol = dict(shared_budget_file='overall-search-budget.json', max_wall_hours=264)
            with patch.object(p.time, 'time', return_value=1000):
                initial = p.campaign_budget(first, protocol, 'citrusfarm')
            with patch.object(p.time, 'time', return_value=2000):
                self.assertEqual(p.campaign_budget(second, protocol, 'citrusfarm'), initial)
                self.assertEqual(p.campaign_budget(first, protocol, 'citrusfarm'), initial)
            with patch.object(p.time, 'time', return_value=2000):
                self.assertNotEqual(p.campaign_budget(first, protocol, 'hortimulti'), initial)
            with patch.object(p.time, 'time', return_value=initial['deadline_unix']):
                with self.assertRaises(InterruptedError):
                    p.campaign_budget(second, protocol, 'citrusfarm')

    def test_phase_deadline_cannot_be_extended(self):
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory)/'phase';art.mkdir()
            protocol = dict(shared_budget_file='overall-search-budget.json', max_wall_hours=264)
            value = p.campaign_budget(art, protocol, 'citrusfarm')
            value['deadline_unix'] += 1
            (art/'budget-citrusfarm.json').write_text(json.dumps(value))
            with self.assertRaisesRegex(RuntimeError, 'Phase deadline'):
                p.campaign_budget(art, protocol, 'citrusfarm')

    def test_missing_shared_budget_does_not_restart_clock(self):
        with tempfile.TemporaryDirectory() as directory:
            art = Path(directory)/'phase';art.mkdir()
            protocol = dict(shared_budget_file='overall-search-budget.json', max_wall_hours=264)
            p.campaign_budget(art, protocol, 'citrusfarm')
            (art.parent/'citrusfarm-overall-search-budget.json').unlink()
            with self.assertRaisesRegex(RuntimeError, 'requires review'):
                p.campaign_budget(art, protocol, 'citrusfarm')


if __name__=='__main__':
    unittest.main()
