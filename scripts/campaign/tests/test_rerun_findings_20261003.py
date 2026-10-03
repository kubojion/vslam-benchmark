"""The 3 October findings are well formed and appear in the TODO matrices with a label."""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'scripts/campaign'))

from protocol_findings import historical_findings  # noqa: E402
from update_todo_matrices import RERUN_LABELS  # noqa: E402

FINDINGS = REPO / 'docs/campaigns/rerun-findings-20261003.json'


def test_records_are_complete_and_labelled():
    attempts = json.loads(FINDINGS.read_text())['attempts']
    assert len(attempts) == 24
    for relative, record in attempts.items():
        mode, dataset, sequence, algorithm, run = relative.split('/')
        assert run.startswith('run') and mode in ('vio', 'vio-lc')
        assert record['disposition'] == 'required_rerun'
        assert record['code'] in RERUN_LABELS, record['code']
        assert len(record['config_sha256']) == 64 and record['role']
        assert all((REPO / path).is_file() for path in record['evidence'])


def test_finding_applies_only_to_the_pinned_attempt(tmp_path):
    """A matching saved snapshot raises the finding; any other bytes do not."""
    import hashlib
    relative = 'vio/hortimulti/strawberry02/basalt/run1'
    record = json.loads(FINDINGS.read_text())['attempts'][relative]
    for content, expected in ((None, True), (b'{"other": 1}', False)):
        root = tmp_path / ('match' if expected else 'other')
        (root / 'docs/campaigns').mkdir(parents=True)
        (root / 'docs/campaigns/rerun-findings-20261003.json').write_text(FINDINGS.read_text())
        run = root / 'results' / relative / 'provenance'
        run.mkdir(parents=True)
        data = content if content is not None else b'saved-calibration'
        snapshot = run / 'calib.json'
        snapshot.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        if expected:   # pin the synthetic snapshot as the reviewed one
            doc = json.loads(FINDINGS.read_text())
            doc['attempts'][relative]['config_sha256'] = digest
            (root / 'docs/campaigns/rerun-findings-20261003.json').write_text(json.dumps(doc))
        meta = {'provenance': {'artifacts': [
            {'role': record['role'], 'snapshot': 'provenance/calib.json', 'snapshot_sha256': digest},
            {'role': 'estimator_config', 'snapshot': 'provenance/calib.json', 'snapshot_sha256': digest}],
            'sources': []}}
        codes = [f['code'] for f in historical_findings(root, relative, meta)]
        assert (record['code'] in codes) == expected
