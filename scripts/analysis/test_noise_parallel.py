import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import noise_parallel as runner


class ParallelTests(unittest.TestCase):
    def test_layout_never_overlaps_shared_airslam_container(self):
        protocol=json.loads(runner.search.PROTOCOL.read_text())
        layout=runner.lanes(protocol)
        self.assertEqual(len(layout),3)
        self.assertEqual(len(layout['airslam']),3)
        self.assertEqual(sum(map(len,layout.values())),len(protocol['studies']))

    def test_resume_preserves_observations_and_rejects_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            art=Path(d)
            parallel=art/'parallel'
            (art/'main-before.json').write_text('{}')
            first=dict(key='screen__orb__x',study='orb',state='finished',run='/immutable/run1',result={'loss':.1})
            runner.ENGINE.write(art/'attempts'/'first.json',first)
            trial=dict(params={'noise':.03},loss=.1)
            runner.ENGINE.write(art/'studies'/'orb'/'screen_seed0'/'trial00.json',trial)
            with patch.object(runner,'ART',art),patch.object(runner,'PARALLEL',parallel):
                lane=runner.prepare_lane('orbslam3',['orb'])
                self.assertEqual(json.loads((lane/'attempts/first.json').read_text()),first)
                self.assertEqual(json.loads((lane/'studies/orb/screen_seed0/trial00.json').read_text()),trial)
                pending=dict(key='screen__orb__y',study='orb',state='running',run='/immutable/run2')
                runner.ENGINE.write(lane/'attempts/second.json',pending)
                runner.collect({'orbslam3':lane})
                done=dict(pending,state='finished',result={'loss':.2})
                runner.ENGINE.write(lane/'attempts/second.json',done)
                runner.collect({'orbslam3':lane})
                self.assertEqual(json.loads((art/'attempts/second.json').read_text()),done)
                # Collector may see engine's finished measurement before the
                # caller appends its warning annotation; that is not a rerun.
                annotated=dict(done,solver_warnings={'cholesky_failure':2})
                runner.ENGINE.write(lane/'attempts/second.json',annotated)
                runner.collect({'orbslam3':lane})
                self.assertEqual(json.loads((art/'attempts/second.json').read_text()),annotated)
                runner.prepare_lane('orbslam3',['orb'])
                changed=copy.deepcopy(annotated);changed['result']['loss']=0
                runner.ENGINE.write(lane/'attempts/second.json',changed)
                with self.assertRaises(RuntimeError):
                    runner.collect({'orbslam3':lane})
                self.assertEqual(json.loads((art/'attempts/second.json').read_text()),annotated)
                changed=copy.deepcopy(annotated);changed['solver_warnings']['cholesky_failure']=0
                runner.ENGINE.write(lane/'attempts/second.json',changed)
                with self.assertRaises(RuntimeError):
                    runner.collect({'orbslam3':lane})


if __name__=='__main__':
    unittest.main()
