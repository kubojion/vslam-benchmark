"""Controller checks without launching estimators or touching real run records."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import noise_reliable as runner


def observation(failed=False, residual=0.1):
    return {'result':{'failed':failed,'loss':10*int(failed)+residual}}


class ProtocolTests(unittest.TestCase):
    def test_failure_priority_at_both_cohort_sizes(self):
        for size in (2,6):
            clean=[observation(residual=1.99) for _ in range(size)]
            failed=[observation(True,0)]+[observation(residual=0) for _ in range(size-1)]
            self.assertLess(runner.combined(clean),runner.combined(failed))

    def test_worst_repeat_changes_ranking_at_equal_mean(self):
        steady=[observation(residual=.2),observation(residual=.2)]
        unstable=[observation(residual=.01),observation(residual=.39)]
        self.assertLess(runner.combined(steady),runner.combined(unstable))

    def test_staged_search_replay_controls_and_frozen_selection(self):
        protocol=json.loads(runner.PROTOCOL.read_text())
        spec=copy.deepcopy(protocol['studies'][0])
        cache={}
        def fake_attempt(spec,params,seq,mode='vio',repetition=1,phase='screen'):
            key=runner.record_key(spec,params,seq,mode,repetition,phase)
            if key not in cache:
                # Deliberately different full/short objectives and repeat noise.
                values=[params[k]/spec['rule_c'][k] for k in runner.KEYS]
                target=3 if phase=='full' else .3
                raw=sum(abs(__import__('math').log10(v/target)) for v in values)
                residual=raw/(20+raw)+.0001*repetition
                cache[key]=dict(key=key,params=params,result=dict(failed=False,loss=residual))
            return copy.deepcopy(cache[key])
        with tempfile.TemporaryDirectory() as tmp:
            art=Path(tmp)
            with patch.object(runner,'ART',art),patch.object(runner.engine,'ART',art),patch.object(runner,'attempt',fake_attempt),patch.object(runner.engine,'event'):
                screens=runner.screening(spec,protocol)
                self.assertEqual(len(screens),2)
                self.assertNotEqual(screens[0][2]['params'],screens[1][2]['params'])
                self.assertEqual(screens[0][0]['records'],screens[1][0]['records'])
                seeds=runner.choose_full_seeds(spec,screens)
                self.assertEqual(seeds[0]['params'],spec['rule_c'])
                self.assertEqual(seeds[1]['params'],spec['legacy'])
                full=runner.full_search(spec,protocol,screens)
                self.assertEqual(len(full),12)
                self.assertTrue(all('noise180' not in k for c in full for k in c['records']))
                selected=runner.repeated_selection(spec,protocol,full)
                repeated=selected['repeated_candidates']
                self.assertTrue(all(len(c['records'])==6 for c in repeated))
                self.assertIn(runner.identity(spec['rule_c']),[runner.identity(c['params']) for c in repeated])
                self.assertIn(runner.identity(spec['legacy']),[runner.identity(c['params']) for c in repeated])
                frozen=(art/'studies'/spec['id']/'selection.json').read_bytes()
                count=len(cache)
                replay=runner.full_search(spec,protocol,runner.screening(spec,protocol))
                self.assertEqual([c['params'] for c in full],[c['params'] for c in replay])
                runner.repeated_selection(spec,protocol,replay)
                self.assertEqual(count,len(cache))
                runner.lc_checks(spec,selected)
                self.assertEqual(frozen,(art/'studies'/spec['id']/'selection.json').read_bytes())


if __name__=='__main__':
    unittest.main()
