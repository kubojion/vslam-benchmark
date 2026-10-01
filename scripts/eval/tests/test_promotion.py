import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from promote_repaired_evaluations import plan_promotion, apply_plan


def fixture(tmp_path):
    path='results/vo/test/seq/macvo/run1'
    run=tmp_path/path; run.mkdir(parents=True)
    (run/'run_eval.json').write_text('old evaluation\n')
    (run/'trajectory.txt').write_text('evidence\n')
    staged=tmp_path/'staging/run_eval.json'; staged.parent.mkdir()
    value=dict(run_type='vo', dataset='test', seq='seq', algo='macvo',run_directory='run1',eval_schema=3,
               evaluation_provenance={'evaluator':{'sha256':'current'}}, qualification={'status':'blocked'},
               qualification_provenance={'evidence':[]})
    staged.write_text(json.dumps(value))
    attempt=dict(path=path,evaluation_path='staging/run_eval.json',qualification=value['qualification'])
    inv=dict(cells=[{'attempts':[attempt]}],other_artifacts=[],qualification_review=value['qualification_provenance'])
    return inv,run,staged


def test_promotion_preserves_previous_bytes_and_is_idempotent(tmp_path):
    inv,run,staged=fixture(tmp_path)
    plan=plan_promotion(inv,tmp_path,evaluator='current')
    assert (run/'run_eval.json').read_text()=='old evaluation\n'
    apply_plan(plan,tmp_path)
    assert (tmp_path/plan[0]['archive']).read_text()=='old evaluation\n'
    assert (run/'run_eval.json').read_bytes()==staged.read_bytes()
    assert (run/'trajectory.txt').read_text()=='evidence\n'
    assert plan_promotion(inv,tmp_path,evaluator='current')[0]['already_current']


def test_identity_and_concurrent_change_fail_before_writing(tmp_path):
    inv,run,staged=fixture(tmp_path)
    with pytest.raises(ValueError,match='stale'):plan_promotion(inv,tmp_path,evaluator='different')
    plan=plan_promotion(inv,tmp_path,evaluator='current')
    staged.write_text('changed')
    with pytest.raises(ValueError,match='staging changed'):apply_plan(plan,tmp_path)
    assert (run/'run_eval.json').read_text()=='old evaluation\n'
