"""Tests for the Sielinko N=3 paper export and completion review (export_paper.py). Synthetic campaigns only, plus a
read-only dry run on the real ones when present. Nothing here launches anything."""
import json
import math
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sielinko_n3 import export_paper as E  # noqa: E402
from sielinko_n3.common import sha  # noqa: E402

H2, FULL = 'field1_sielinko_h2_20261022', 'field1_110426_full_10fps_q90'
P = {'gyroscope_noise_density': 1e-3, 'accelerometer_noise_density': 1e-2, 'gyroscope_random_walk': 1e-5,
     'accelerometer_random_walk': 1e-4}


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')
    return path


def attempt(study, label, seq, mode, rep, run, ate, *, failed=False, state='finished', cls='ok', key=None, gate=True,
            manifest_sha=None, repeat=None):
    return dict(key=key or f'paper_n3__{study}__{label}__{seq}__{mode}__rep{rep}', state=state, study=study, label=label,
                sequence=seq, mode=mode, repetition=rep, params=P, run=run, wall_s=100.0, returncode=0, timeout=False,
                classification=cls if state == 'finished' else None, campaign_id='c', phase='paper_n3',
                identity_gate=dict(full=False, passed=gate), manifest_sha256=manifest_sha, repeat=repeat or {},
                result=dict(failed=failed, ate_se3_rmse_m=ate, export_support_fraction=1.0,
                            numerical_status='scale_collapse' if failed else 'ok', loss=0.1))


class World:
    """One CPU campaign: basalt (reproducible) h2_sel and a VIO-LC test whose first run is outside the first campaign."""

    def __init__(self, root):
        self.root = Path(root)
        self.out, self.first = self.root / 'n3', self.root / 'first'
        self.dir = self.out / 'cpu'
        sel = dump(self.first / 'studies' / 'basalt_zed2i' / 'selection.json', dict(winner=dict(label='noise_b', params=P)))
        self.sel_sha = sha(sel)
        refs = {
            'h2_sel': dump(self.first / 'workers' / 'basalt_zed2i' / 'attempts' / 'final_n1__h2.json',
                           attempt('basalt_zed2i', 'noise_b', H2, 'vio', 1, '/r/h2/run1', 0.50, key='final_n1__x')),
            'full_sel_lc': dump(self.root / 'supplemental' / 'validation_n1__lc.json',
                                attempt('basalt_zed2i', 'noise_b', FULL, 'vio-lc', 1, '/r/lc/run1', 0.70,
                                        key='validation_n1__x')),
        }
        self.items = []
        for test, seq, mode, check in (('h2_sel', H2, 'vio', 'match_within_1pct'), ('full_sel_lc', FULL, 'vio-lc', 'record_only')):
            for rep in (2, 3):
                iid = f'B-basalt-{test}-r{rep}'
                self.items.append(dict(
                    id=iid, group='B', system='basalt', study='basalt_zed2i', test=test, sequence=seq, mode=mode,
                    repetition=rep, label='noise_b', run_dir=f'/r/{test}/run{rep}', record=str(self.dir / 'attempts' / (iid + '.json')),
                    repeat_check=check, reference=dict(kind='first_run_of_this_test', record=str(refs[test]),
                                                       record_sha256=sha(refs[test]),
                                                       ate_se3_rmse_m=0.50 if test == 'h2_sel' else 0.70),
                    pinned_evidence=[dict(role='selection', path=str(sel), sha256=self.sel_sha)]))
        self.manifest = dict(campaign_id='c', amendment='paper-n3-20261110', items=self.items,
                             stops=dict(stop_files=[str(self.dir / 'STOP')], fault_files=[str(self.dir / 'FAULT')]),
                             pooling=dict(approved_by='user', at='2026-11-10T23:00Z'), disclosure='d')
        self.write_manifest()
        (self.dir / 'amendment-notes.md').write_text(
            '# Notes\n\n- **User, 10 Nov 2026:** the new repetitions are pooled with their first runs.\n'
            '- **11 Nov 2026, evaluator fix (engineer decision):** manifest rebuilt.\n'
            '  - The FAULT files are kept as `FAULT*.20261111-evaluator`.\n'
            f'  - New manifest sha256: `{self.digest}`.\n')
        dump(self.dir / 'identity-gates' / 'basalt.json', dict(passed=True))
        for item in self.items:
            first = item['id'] == 'B-basalt-h2_sel-r2'
            ate = 0.501 if item['test'] == 'h2_sel' else 0.72
            self.finish(item['id'], ate, repeat=dict(enforced=first and item['repeat_check'] == 'match_within_1pct',
                                                     passed=True if first else None,
                                                     relative_difference=abs(ate - item['reference']['ate_se3_rmse_m'])
                                                     / item['reference']['ate_se3_rmse_m']))

    def write_manifest(self):
        path = dump(self.dir / 'manifest.json', self.manifest)
        self.digest = sha(path)
        (self.dir / 'manifest.json.sha256').write_text(f'{self.digest}  manifest.json\n')

    def item(self, iid):
        return next(i for i in self.items if i['id'] == iid)

    def finish(self, iid, ate, **kw):
        i = self.item(iid)
        dump(i['record'], attempt(i['study'], i['label'], i['sequence'], i['mode'], i['repetition'], i['run_dir'], ate,
                                  **dict(dict(manifest_sha=self.digest), **kw)))

    def campaign(self):
        return E.Campaign('cpu', self.out, self.first)


@pytest.fixture
def world(tmp_path):
    return World(tmp_path)


def test_complete_campaign_exports_loader_records_and_passes(world):
    value, digest = world.campaign().run()
    assert value['passed'], {k: v for k, v in value['checks'].items() if not v['passed']}
    assert value['reported_deviations'] == []
    names = sorted(p.name for p in (world.dir / 'attempts-paper').iterdir())
    assert names == sorted([
        f'final_n1__basalt_zed2i__noise_b__{H2}__vio__rep2.json', f'final_n1__basalt_zed2i__noise_b__{H2}__vio__rep3.json',
        f'final_n1__basalt_zed2i__noise_b__{FULL}__vio-lc__rep1.json',   # first run outside the first campaign
        f'final_n1__basalt_zed2i__noise_b__{FULL}__vio-lc__rep2.json', f'final_n1__basalt_zed2i__noise_b__{FULL}__vio-lc__rep3.json'])
    rec = json.loads((world.dir / 'attempts-paper' / names[0]).read_text())
    for k in ('state', 'study', 'label', 'sequence', 'mode', 'repetition', 'params', 'run', 'run_dir', 'source_attempt'):
        assert k in rec
    for k in ('failed', 'ate_se3_rmse_m', 'export_support_fraction', 'numerical_status'):
        assert k in rec['result']
    lc1 = json.loads((world.dir / 'attempts-paper' / f'final_n1__basalt_zed2i__noise_b__{FULL}__vio-lc__rep1.json').read_text())
    assert lc1['origin'] == 'first_run_outside_first_campaign' and lc1['result']['ate_se3_rmse_m'] == 0.70
    assert lc1['source_attempt']['path'].endswith('validation_n1__lc.json')
    # the VIO first run stays in the first campaign and is not copied
    assert not any('__vio__rep1' in n for n in names)
    # selection copied byte for byte
    assert (world.dir / 'studies' / 'basalt_zed2i' / 'selection.json').read_bytes() == \
        (world.first / 'studies' / 'basalt_zed2i' / 'selection.json').read_bytes()
    assert value['counts']['tests'] == 2 and value['counts']['tests_at_n3'] == 2
    h2 = next(t for t in value['per_test'] if t['kind'] == 'h2_sel')
    assert h2['repetitions'] == [1, 2, 3] and h2['median_primary_reference_m'] == 0.501
    review = world.dir / 'final-completion-review-n3.json'
    assert (world.dir / 'final-completion-review-n3.json.sha256').read_text().split()[0] == digest == sha(review)
    # deterministic: a second run writes the same bytes
    _, again = world.campaign().run()
    assert again == digest


def test_pending_item_is_not_exported_and_fails_terminal_and_n3(world):
    i = world.item('B-basalt-full_sel_lc-r3')
    rec = json.loads(Path(i['record']).read_text())
    rec.update(state='running', classification=None, result=None)
    dump(i['record'], rec)
    value, _ = world.campaign().run()
    assert not value['passed']
    assert not value['checks']['all_items_terminal']['passed']
    assert value['checks']['all_items_terminal']['not_terminal'][0]['item'] == 'B-basalt-full_sel_lc-r3'
    assert value['checks']['every_test_n3']['short'] == [f'basalt_zed2i|full_sel_lc|noise_b|{FULL}|vio-lc: repetitions [1, 2]']
    assert not (world.dir / 'attempts-paper' / f'final_n1__basalt_zed2i__noise_b__{FULL}__vio-lc__rep3.json').exists()


def test_stale_paper_file_is_removed(world):
    stale = dump(world.dir / 'attempts-paper' / 'final_n1__x__y__z__vio__rep9.json', {})
    world.campaign().run()
    assert not stale.exists()


def test_faults(world):
    (world.dir / 'FAULT.20261111-evaluator').write_text('refusal')
    value, _ = world.campaign().run(dry_run=True)
    check = value['checks']['no_unresolved_fault_or_stop']
    assert check['passed'] and 'evaluator fix' in check['resolved_renamed_faults'][0]['decision']
    (world.dir / 'FAULT.20261112-other').write_text('x')
    value, _ = world.campaign().run(dry_run=True)
    assert not value['checks']['no_unresolved_fault_or_stop']['passed']
    (world.dir / 'FAULT.20261112-other').unlink()
    (world.dir / 'FAULT').write_text('live')
    value, _ = world.campaign().run(dry_run=True)
    assert not value['passed'] and value['checks']['no_unresolved_fault_or_stop']['live_stop_or_fault_files']


def test_failed_identity_gate_fails(world):
    dump(world.dir / 'identity-gates' / 'B-basalt-h2_sel-r3.light.json', dict(passed=False))
    value, _ = world.campaign().run(dry_run=True)
    assert not value['checks']['identity_gates_passed']['passed']


def test_reproduction_rule(world):
    # a non-enforced repetition outside 1 % is reported, not gating
    world.finish('B-basalt-h2_sel-r3', 0.55, repeat=dict(enforced=False, passed=None, relative_difference=0.1))
    value, _ = world.campaign().run(dry_run=True)
    check = value['checks']['reproduction_within_1pct']
    assert check['passed'] and check['reported_not_gating_outside_1pct'] == ['B-basalt-h2_sel-r3']
    dev = value['reported_deviations']
    assert len(dev) == 1 and dev[0]['items'] == ['B-basalt-h2_sel-r3'] and dev[0]['gating'] is False
    assert dev[0]['ate_m'] == {'B-basalt-h2_sel-r3': 0.55} and dev[0]['reference_ate_m'] == 0.50
    assert dev[0]['new_runs_of_test'] == ['B-basalt-h2_sel-r2', 'B-basalt-h2_sel-r3']
    assert dev[0]['new_runs_spread_relative'] == pytest.approx(0.55 / 0.501 - 1)
    # the enforced first new run outside 1 % fails the review
    world.finish('B-basalt-h2_sel-r2', 0.52, repeat=dict(enforced=True, passed=False, relative_difference=0.04))
    value, _ = world.campaign().run(dry_run=True)
    assert not value['checks']['reproduction_within_1pct']['passed'] and not value['passed']


def test_selection_must_match_the_pin_and_the_items(world):
    dump(world.first / 'studies' / 'basalt_zed2i' / 'selection.json', dict(winner=dict(label='other', params=P)))
    value, _ = world.campaign().run(dry_run=True)
    problems = value['checks']['paper_export']['problems']
    assert any('differs from the manifest pin' in p for p in problems)
    assert any('selection winner other' in p for p in problems)


def test_reference_record_changed_since_the_manifest_fails_n3(world):
    ref = Path(world.item('B-basalt-h2_sel-r2')['reference']['record'])
    ref.write_text(ref.read_text().replace('0.5', '0.6'))
    value, _ = world.campaign().run(dry_run=True)
    assert not value['checks']['every_test_n3']['passed']


def test_record_under_an_undocumented_manifest_fails(world):
    world.finish('B-basalt-h2_sel-r3', 0.5, manifest_sha='f' * 64)
    value, _ = world.campaign().run(dry_run=True)
    assert value['checks']['manifest_integrity']['undocumented'] == ['f' * 64]


def test_loader_reading_of_the_export(world):
    """The paper loader's per-file logic (search.lpit): stage from the name, finished, known sequence, failed -> inf."""
    world.campaign().run()
    rows = []
    for f in sorted((world.dir / 'attempts-paper').glob('*.json')):
        a = json.loads(f.read_text())
        assert f.name.split('__')[0] == 'final_n1' and a.get('state') == 'finished'
        r = a.get('result') or {}
        rows.append((a['study'], a['label'], a['sequence'], a['mode'], int(a['repetition']),
                     math.inf if bool(r.get('failed', True)) else r['ate_se3_rmse_m'], r.get('numerical_status')))
    assert len(rows) == 5 and {r[3] for r in rows} == {'vio', 'vio-lc'}   # mode is recorded: the loader must filter on it


@pytest.mark.skipif(not (E.OUT / 'gpu' / 'manifest.json').is_file(), reason='real campaigns not on this host')
def test_real_campaigns_dry_run():
    for name, items in (('cpu', 52), ('gpu', 24)):
        value, digest = E.Campaign(name).run(dry_run=True)
        assert digest is None and value['counts']['items'] == items
        for k in ('manifest_integrity', 'no_unresolved_fault_or_stop', 'identity_gates_passed', 'reproduction_within_1pct',
                  'pooling_declared', 'paper_export'):
            assert value['checks'][k]['passed'], (name, k, value['checks'][k])
