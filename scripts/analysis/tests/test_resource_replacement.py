"""Resource repair must not erase failed evidence or alter random seeds."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import noise_campaign_engine as engine
import noise_execution_policy as policy


class ReplacementChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.args = ('okvis2x_citrusfarm', 'rule_c', 'seq07', 'vio', 1, 'full')
        self.key = 'full__okvis2x_citrusfarm__rule_c__seq07__vio__rep1'
        self.old = dict(key=self.key, state='finished', returncode=137,
                        result=dict(failed=True), params=dict(g=1.))
        self.review = dict(revision='memory32-v1', resource_censored_attempts=[self.key])
        self.record = self.root/'archived.json'
        self.report = self.root/'review.json'
        self.record.write_text(json.dumps(self.old))
        self.report.write_text(json.dumps(self.review))
        self.item = dict(revision='memory32-v1', record=str(self.record),
                        record_sha256=hashlib.sha256(self.record.read_bytes()).hexdigest(),
                        review=str(self.report),
                        review_sha256=hashlib.sha256(self.report.read_bytes()).hexdigest())
        self.protocol = dict(physical_attempt_revisions={self.key:self.item},run_ids=dict(fold_blocks={'okvis2x_citrusfarm':[70000,70099]}))
        self.plain = dict(run_ids=dict(fold_blocks={'okvis2x_citrusfarm':[70000,70099]}))

    def tearDown(self):
        self.tmp.cleanup()

    def test_replacement_changes_only_physical_id_not_key_or_native_seed(self):
        with patch.object(engine,'CAMPAIGN','campaign'), patch.object(engine,'PROTOCOL',self.plain), patch.object(engine,'ART',self.root):
            original=engine.identities(*self.args)
        with patch.object(engine,'CAMPAIGN','campaign'), patch.object(engine,'PROTOCOL',self.protocol), patch.object(engine,'ART',self.root):
            revised=engine.identities(*self.args)
            self.assertEqual(revised,engine.identities(*self.args))
        self.assertEqual(original[0],revised[0])
        self.assertEqual(original[2],revised[2])
        self.assertNotEqual(original[1],revised[1])

    def test_unlisted_attempt_identity_unchanged(self):
        args=list(self.args);args[2]='seq04'
        with patch.object(engine,'CAMPAIGN','campaign'), patch.object(engine,'PROTOCOL',self.plain), patch.object(engine,'ART',self.root):
            original=engine.identities(*args)
        with patch.object(engine,'CAMPAIGN','campaign'), patch.object(engine,'PROTOCOL',self.protocol), patch.object(engine,'ART',self.root):
            self.assertEqual(original,engine.identities(*args))

    def test_changed_or_missing_predecessor_cannot_trigger_rerun(self):
        self.record.write_text('{}')
        with self.assertRaisesRegex(RuntimeError,'evidence missing or changed'):
            policy.reviewed_attempt_revision(self.protocol,self.key)
        self.record.unlink()
        with self.assertRaises(RuntimeError):policy.reviewed_attempt_revision(self.protocol,self.key)

    def test_successful_or_unfinished_attempt_cannot_be_replaced(self):
        for updates in [dict(returncode=0),dict(state='running'),dict(result=dict(failed=False))]:
            old=copy.deepcopy(self.old);old.update(updates);self.record.write_text(json.dumps(old))
            self.item['record_sha256']=hashlib.sha256(self.record.read_bytes()).hexdigest()
            with self.assertRaisesRegex(RuntimeError,'reviewed failed attempt'):
                policy.reviewed_attempt_revision(self.protocol,self.key)

    def test_review_must_list_the_exact_attempt(self):
        self.review['resource_censored_attempts']=[];self.report.write_text(json.dumps(self.review))
        self.item['review_sha256']=hashlib.sha256(self.report.read_bytes()).hexdigest()
        with self.assertRaisesRegex(RuntimeError,'absent from resource amendment'):
            policy.reviewed_attempt_revision(self.protocol,self.key)

    def test_cached_pre_amendment_failure_is_rejected(self):
        path=self.root/'attempts'/f'{self.key}.json';path.parent.mkdir()
        old=copy.deepcopy(self.old);old['campaign_id']='campaign';path.write_text(json.dumps(old))
        with patch.object(engine,'CAMPAIGN','campaign'),patch.object(engine,'PROTOCOL',self.protocol),patch.object(engine,'ART',self.root):
            with self.assertRaisesRegex(RuntimeError,'another revision'):
                engine.run_attempt(dict(id=self.args[0]),'rule_c',dict(g=1.),'seq07','vio',1,'full')

    def test_replacement_cannot_change_noise_parameters(self):
        with patch.object(engine,'CAMPAIGN','campaign'),patch.object(engine,'PROTOCOL',self.protocol),patch.object(engine,'ART',self.root):
            with self.assertRaisesRegex(RuntimeError,'parameters differ'):
                engine.run_attempt(dict(id=self.args[0]),'rule_c',dict(g=2.),'seq07','vio',1,'full')

    def test_uniform_32_gib_scope_and_container_limits(self):
        protocol=dict(campaign_id='test',attempt_resource_limits={
            name:dict(memory_gib=32,swap_gib=0) for name in ['okvis2x','openvins','svo_pro']})
        for name,docker in [('okvis2x',False),('openvins',True),('svo_pro',True)]:
            env={'TIMING_MEM':str(32*1024**3)} if docker else {}
            command=policy.bounded_command(['true'],protocol,name,1,env)
            self.assertIn('MemoryMax=32G',command)
            self.assertIn('MemorySwapMax=0',command)
        with self.assertRaisesRegex(RuntimeError,'Docker limits differ'):
            policy.bounded_command(['true'],protocol,'openvins',1,{'TIMING_MEM':str(16*1024**3)})


if __name__=='__main__': unittest.main()
