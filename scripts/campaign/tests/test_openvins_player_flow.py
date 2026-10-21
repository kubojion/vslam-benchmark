"""Execute actual player control methods without requiring ROS or an estimator."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'scripts/run/openvins_data_player.py'


class Clock:
    def __init__(self):self.t=0.
    def monotonic(self):return self.t
    def sleep(self, seconds):self.t+=seconds


class Condition:
    def __init__(self,clock):self.clock=clock
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def wait(self,timeout):self.clock.sleep(timeout)
    def notify_all(self):pass


def player_methods(clock):
    tree=ast.parse(SOURCE.read_text())
    definition=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Player')
    wanted={'_on_progress_ack','wait_for_input_receipt','wait_for_input_subscribers','write_delivery'}
    definition.bases=[]
    definition.body=[n for n in definition.body if isinstance(n,ast.FunctionDef) and n.name in wanted]
    namespace=dict(time=clock,UInt64MultiArray=SimpleNamespace,
        write_transport_stats=lambda path,**kwargs:Path(path).write_text(json.dumps(kwargs)))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[definition],type_ignores=[])),str(SOURCE),'exec'),namespace)
    return namespace['Player']()


class PlayerFlowChecks(unittest.TestCase):
    def setUp(self):
        self.clock=Clock();self.player=player_methods(self.clock)
        self.player.progress_condition=Condition(self.clock)
        self.player.progress_ack=None;self.player.progress_checkpoints=0
        self.player.progress_wait_s=0.;self.player.progress_last_imu=0
        self.player.published_imu=10;self.player.published_cam0=2;self.player.published_cam1=2

    def test_only_matching_application_ack_releases_sender(self):
        requests=[]
        def publish(request):
            requests.append(list(request.data))
            reply=[1,9,2,2] if len(requests)==1 else [1,10,2,2]
            self.player._on_progress_ack(SimpleNamespace(data=reply))
        self.player.pub_progress=SimpleNamespace(publish=publish)
        self.player.wait_for_input_receipt()
        self.assertEqual(requests,[[1,10,2],[1,10,2]])
        self.assertEqual(self.player.progress_checkpoints,1)
        self.assertEqual(self.player.progress_last_imu,10)

    def test_no_ack_has_a_bounded_failure_not_sensor_retransmission(self):
        requests=[];self.player.pub_progress=SimpleNamespace(publish=lambda m:requests.append(list(m.data)))
        with self.assertRaisesRegex(RuntimeError,'receipt stalled'):
            self.player.wait_for_input_receipt()
        self.assertTrue(30.<=self.clock.t<30.1)
        self.assertEqual(self.player.progress_checkpoints,0)
        self.assertTrue(all(r==[1,10,2] for r in requests))
        self.assertEqual(self.player.published_imu,10)

    def test_stale_and_malformed_acks_do_not_count_as_new_receipt(self):
        self.player.progress_ack=[1,9,2,2]
        self.player._on_progress_ack(SimpleNamespace(data=[1,10,2,1]))
        self.assertEqual(self.player.progress_ack,[1,9,2,2])
        self.player._on_progress_ack(SimpleNamespace(data=[2,10,2,2]))
        self.assertEqual(self.player.progress_ack,[1,9,2,2])

    def test_half_pair_cannot_deadlock_waiting_for_its_unpublished_partner(self):
        self.player.published_cam1=1
        with self.assertRaisesRegex(RuntimeError,'half'):
            self.player.wait_for_input_receipt()

    def test_zero_count_readiness_barrier_is_supported(self):
        self.player.published_imu=self.player.published_cam0=self.player.published_cam1=0
        self.player.pub_progress=SimpleNamespace(publish=lambda m:self.player._on_progress_ack(
            SimpleNamespace(data=[1,0,0,0])))
        self.player.wait_for_input_receipt()
        self.assertEqual(self.player.progress_checkpoints,1)

    def test_start_wait_requires_all_sensor_and_control_matches(self):
        ready=SimpleNamespace(get_subscription_count=lambda:1)
        absent=SimpleNamespace(get_subscription_count=lambda:0)
        p=self.player;p.pub_imu=p.pub_cam0=p.pub_progress=ready;p.pub_cam1=absent
        p.count_publishers=lambda topic:1
        with self.assertRaisesRegex(RuntimeError,'did not become ready'):
            p.wait_for_input_subscribers()
        p.pub_cam1=ready;p.wait_for_input_subscribers()

    def test_partial_failure_counts_and_error_are_persisted(self):
        with tempfile.TemporaryDirectory() as temporary:
            p=self.player;p.delivery=dict(schema=1);p.flow_control=True
            p.poses=[];p.update_poses=[];p.cam0=p.cam1=[1,2,3]
            p.out_traj=Path(temporary)/'trajectory.txt';p.stats_out=Path(temporary)/'transport_stats.json'
            p.write_delivery('RuntimeError: receipt stalled')
            evidence=json.loads((Path(temporary)/'openvins_delivery.json').read_text())
            counts=json.loads(p.stats_out.read_text())
            self.assertEqual(evidence['player_error'],'RuntimeError: receipt stalled')
            self.assertEqual(counts['imu_messages_published'],10)
            self.assertEqual(counts['camera_frames_published'],2)
            self.assertEqual(counts['camera_frames_expected'],3)


if __name__=='__main__':unittest.main()
