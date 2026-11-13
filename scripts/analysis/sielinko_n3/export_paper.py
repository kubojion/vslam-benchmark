#!/usr/bin/env python3
"""Paper records of the Sielinko N=3 repetitions (Update 10 B, C, D search; RESULTS-ORGANISATION.md section 3).

Reads the dispatcher's frozen manifest and attempt records of each campaign (never changes them) and writes, per
campaign directory <out>/<cpu|gpu>/:

  attempts-paper/final_n1__<study>__<label>__<sequence>__<mode>__rep<N>.json
      one file per finished new repetition, in the schema the paper's loader reads for the first runs (state, study,
      label, sequence, mode, repetition, params, run, wall_s, result.{failed, ate_se3_rmse_m, export_support_fraction,
      numerical_status, ...}), plus source_attempt, run_dir and origin. The first run (rep 1) of a VIO-LC test whose
      first run lives outside the first campaigns (the supplemental validation runs named by the manifest as
      ``first_run_of_this_test``) is exported too, with origin ``first_run_outside_first_campaign``, so that the loader
      sees all three repetitions. VIO first runs stay in the first campaigns' attempts/ and are not copied.
  studies/<study>/selection.json
      a byte copy of the first campaign's frozen selection, checked against the hash the manifest pinned.
  final-completion-review-n3.json (+ .sha256)
      the generated completion review; passed only if every gating check holds (see review()).

Nothing here launches, stops or locks anything. Re-running on unchanged inputs gives the same bytes (no timestamps).

Usage: python -B export_paper.py [--campaign cpu|gpu ...] [--out /data/imoroz/sielinko-n3-20261110] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    __package__ = 'sielinko_n3'

from .common import OUT, load, sha, write_json  # noqa: E402

FIRST = {'cpu': Path('/data/imoroz/sielinko-cpu-search-20261024'),
         'gpu': Path('/data/imoroz/sielinko-gpu-search-20261026')}
TERMINAL = ('ok', 'scientific_failure', 'timeout_failure')
STOP_NAMES = ('FAULT', 'FAULT.json', 'STOP', 'STOP_AFTER_CURRENT')
REPRODUCIBLE = 'match_within_1pct'
TOLERANCE = 0.01
PAPER_FIELDS = ('state', 'study', 'label', 'sequence', 'mode', 'repetition', 'params', 'run')
SEQ = {'field1_sielinko_h2_20261022': 'h2', 'field1_110426_full_10fps_q90': 'full'}


def git_identity():
    root = Path(__file__).resolve().parents[3]

    def git(*args):
        return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, check=True).stdout.strip()
    try:
        script = str(Path(__file__).resolve().relative_to(root))
        return dict(repository=str(root), branch=git('rev-parse', '--abbrev-ref', 'HEAD'), commit=git('rev-parse', 'HEAD'),
                    script=script, script_uncommitted=bool(git('status', '--porcelain', '--', script)))
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return dict(repository=str(root), branch=None, commit=None, script=Path(__file__).name, script_uncommitted=None)


def paper_name(record):
    return '__'.join(('final_n1', record['study'], record['label'], record['sequence'], record['mode'],
                      'rep' + str(record['repetition']))) + '.json'


def test_id(item):
    return '|'.join((item['study'], item['test'], item['label'], item['sequence'], item['mode']))


def paper_record(record, source, origin, item, manifest_sha, identity):
    """The loader's schema, copied from the attempt record; never recomputed."""
    out = {k: record[k] for k in PAPER_FIELDS}
    out['stage'] = 'final_n1'
    out.update(run_dir=record['run'], run_id=Path(record['run']).name, wall_s=record.get('wall_s'),
               returncode=record.get('returncode'), timeout=record.get('timeout'),
               classification=record.get('classification'), result=record.get('result'),
               campaign_id=record.get('campaign_id'), phase=record.get('phase'),
               item=item['id'] if origin == 'paper_n3_new_run' else None, group=item['group'], test=item['test'],
               origin=origin, pooled_cohort='paper-n3-20261110: pooled with the first runs (user, 10 Nov 2026)',
               source_attempt=dict(path=str(source), sha256=sha(source), key=record.get('key')),
               manifest_sha256=manifest_sha, exported_by=identity)
    return out


def failed_value(record):
    r = record.get('result') or {}
    return math.inf if r.get('failed', True) else r.get('ate_se3_rmse_m')


def amendment_blocks(text):
    """Top-level bullets of amendment-notes.md (each with its sub-bullets)."""
    blocks, current = [], []
    for line in text.splitlines():
        if line.startswith('- '):
            if current:
                blocks.append('\n'.join(current))
            current = [line]
        elif current and (line.startswith('  ') or not line.strip()):
            current.append(line)
    if current:
        blocks.append('\n'.join(current))
    return [b.rstrip() for b in blocks]


class Campaign:
    def __init__(self, name, out=OUT, first=None):
        self.name = name
        self.dir = Path(out) / name
        self.first = Path(first) if first else FIRST[name]
        self.manifest_path = self.dir / 'manifest.json'
        self.manifest = load(self.manifest_path)
        self.manifest_sha = sha(self.manifest_path)
        self.items = self.manifest['items']
        self.records = {i['id']: (load(i['record']) if Path(i['record']).is_file() else None) for i in self.items}
        self.notes_path = self.dir / 'amendment-notes.md'
        self.notes = self.notes_path.read_text() if self.notes_path.is_file() else ''

    # ------------------------------------------------------------ records for the loader
    def paper_records(self, identity):
        """{file name: record} for every finished new run, plus first runs outside the first campaigns."""
        out, problems = {}, []
        for item in self.items:
            record = self.records[item['id']]
            if record is None or record.get('state') != 'finished':
                continue
            for k, v in (('study', item['study']), ('label', item['label']), ('sequence', item['sequence']),
                         ('mode', item['mode']), ('repetition', item['repetition']), ('run', item['run_dir'])):
                if record.get(k) != v:
                    problems.append(f"{item['id']}: record {k}={record.get(k)!r}, manifest {v!r}")
            name = paper_name(record)
            if name in out:
                problems.append('two records map to ' + name)
            out[name] = paper_record(record, item['record'], 'paper_n3_new_run', item, record.get('manifest_sha256'), identity)
        for test, first in self.first_runs().items():
            ref = first['reference']
            if ref['outside_first_campaign'] and first['record'] is not None:
                record = first['record']
                name = paper_name(record)
                if name in out:
                    problems.append('first run collides with a new run: ' + name)
                out[name] = paper_record(record, ref['record'], 'first_run_outside_first_campaign', first['item'],
                                         None, identity)
        return out, problems

    def first_runs(self):
        """Per test whose first repetition predates this dispatcher: the manifest's reference record of rep 1."""
        tests = {}
        for item in self.items:
            ref = item['reference']
            if ref.get('kind') != 'first_run_of_this_test':
                continue
            t = tests.setdefault(test_id(item), dict(item=item, refs=set()))
            t['refs'].add((ref['record'], ref['record_sha256']))
        out = {}
        for test, t in tests.items():
            path, pinned = sorted(t['refs'])[0]
            exists = Path(path).is_file()
            record = load(path) if exists else None
            out[test] = dict(item=t['item'], record=record, reference=dict(
                record=path, pinned_sha256=pinned, sha256=sha(path) if exists else None,
                consistent=len(t['refs']) == 1, outside_first_campaign=not str(path).startswith(str(self.first) + '/')))
        return out

    def selections(self):
        out, problems = {}, []
        studies = sorted({i['study'] for i in self.items})
        for study in studies:
            src = self.first / 'studies' / study / 'selection.json'
            pins = {(e['path'], e['sha256']) for i in self.items if i['study'] == study
                    for e in i['pinned_evidence'] if e['role'] == 'selection'}
            labels = {i['label'] for i in self.items if i['study'] == study and i['test'] != 'h2_aop'}
            if not src.is_file():
                problems.append(f'{study}: no selection in the first campaign ({src})')
                continue
            digest = sha(src)
            if {p[1] for p in pins} != {digest}:
                problems.append(f'{study}: selection sha256 {digest} differs from the manifest pin(s) {sorted(pins)}')
            winner = load(src)['winner']['label']
            if labels != {winner}:
                problems.append(f'{study}: selected-setting items use {sorted(labels)}, selection winner {winner}')
            out[study] = dict(source=str(src), sha256=digest, winner=winner, pinned=sorted(p[0] for p in pins))
        return out, problems

    # ------------------------------------------------------------ review
    def review(self, exported, export_problems, selections, selection_problems, identity):
        checks = {}

        def check(name, passed, **detail):
            checks[name] = dict(passed=bool(passed), **detail)

        # 0. manifest integrity: equal to its sidecar; every record ran under it or a predecessor documented in the notes
        sidecar = Path(str(self.manifest_path) + '.sha256')
        recorded = sidecar.read_text().split()[0] if sidecar.is_file() else None
        under = sorted({r.get('manifest_sha256') for r in self.records.values() if r})
        undocumented = [h for h in under if h != self.manifest_sha and (not h or h not in self.notes)]
        check('manifest_integrity', recorded == self.manifest_sha and not undocumented, manifest=str(self.manifest_path),
              sha256=self.manifest_sha, sidecar=recorded, record_manifests=under, undocumented=undocumented,
              amendments_in_place=self.manifest.get('amendments_in_place'))

        # 1. every manifest item terminal
        states = {}
        pending = []
        for item in self.items:
            r = self.records[item['id']]
            state = 'no_record' if r is None else r.get('state')
            cls = r and r.get('classification')
            states[item['id']] = dict(state=state, classification=cls)
            if state != 'finished' or cls not in TERMINAL:
                pending.append(dict(item=item['id'], state=state, classification=cls))
        counts = dict(items=len(self.items), finished=sum(s['state'] == 'finished' for s in states.values()),
                      pending=len(pending))
        for c in TERMINAL + ('infrastructure',):
            counts[c] = sum(s['classification'] == c for s in states.values())
        check('all_items_terminal', not pending, counts=counts, not_terminal=pending)

        # 2. no unresolved FAULT/STOP; renamed FAULT files are resolved by a recorded decision
        live = [str(p) for p in (self.manifest['stops']['stop_files'] + self.manifest['stops']['fault_files'])
                if Path(p).exists()]
        live += [str(self.dir / n) for n in STOP_NAMES if (self.dir / n).exists() and str(self.dir / n) not in live]
        blocks = amendment_blocks(self.notes)
        resolved, unresolved_renamed = [], []
        for path in sorted(self.dir.glob('FAULT*')) + sorted(self.dir.glob('STOP*')):
            if path.name in STOP_NAMES:
                continue
            suffix = path.name.split('.')[-1]
            decision = [b for b in blocks if '.' + suffix in b]
            entry = dict(file=str(path), sha256=sha(path), content=path.read_text().strip()[:600],
                         decision_source=str(self.notes_path) if decision else None, decision='\n'.join(decision) or None)
            (resolved if decision else unresolved_renamed).append(entry)
        infra = [i for i, s in states.items() if s['state'] == 'fault' or s['classification'] == 'infrastructure']
        check('no_unresolved_fault_or_stop', not live and not unresolved_renamed and not infra,
              live_stop_or_fault_files=live, resolved_renamed_faults=resolved,
              renamed_without_decision=unresolved_renamed, infrastructure_records=infra,
              superseded_directories=sorted(p.name for p in self.dir.glob('superseded-*')))

        # 3. identity gates
        gates = sorted((self.dir / 'identity-gates').glob('*.json'))
        failed_gates = [str(g) for g in gates if not load(g).get('passed')]
        missing = [i for i, r in self.records.items()
                   if r and r.get('state') == 'finished' and not (r.get('identity_gate') or {}).get('passed')]
        systems = sorted({i['system'] for i in self.items})
        no_full = [s for s in systems if not (self.dir / 'identity-gates' / (s + '.json')).is_file()]
        check('identity_gates_passed', bool(gates) and not failed_gates and not missing and not no_full,
              gate_files=len(gates), failed=failed_gates, records_without_passed_gate=missing,
              systems_without_full_gate=no_full)

        # 4. reproduction: the agreed rule (first new run of a reproducible system within 1 % of its test's first run,
        #    enforced by the dispatcher) gates; every other repetition of those systems is reported against its first run
        rows, gate_fail = [], []
        for item in self.items:
            r = self.records[item['id']]
            if not r or r.get('state') != 'finished':
                continue
            ref = item['reference'].get('ate_se3_rmse_m')
            ate = (r.get('result') or {}).get('ate_se3_rmse_m')
            rel = abs(ate - ref) / ref if isinstance(ate, (int, float)) and isinstance(ref, (int, float)) and ref else None
            rep = r.get('repeat') or {}
            row = dict(item=item['id'], system=item['system'], rule=item['repeat_check'], reference_ate_m=ref, ate_m=ate,
                       relative_difference=rel, within_1pct=None if rel is None else rel <= TOLERANCE,
                       enforced=bool(rep.get('enforced')), dispatcher_passed=rep.get('passed'))
            if rep.get('relative_difference') is not None and rel is not None and not math.isclose(rep['relative_difference'], rel, rel_tol=1e-9):
                row['recorded_relative_difference'] = rep['relative_difference']
                gate_fail.append(item['id'] + ': recorded repeat check disagrees with the records')
            if item['repeat_check'] == REPRODUCIBLE and row['enforced'] and not (rep.get('passed') and row['within_1pct']):
                gate_fail.append(item['id'])
            rows.append(row)
        reproducible = sorted({i['system'] for i in self.items if i['repeat_check'] == REPRODUCIBLE})
        enforced = [r for r in rows if r['rule'] == REPRODUCIBLE and r['enforced']]
        for system in reproducible:
            if not any(r['system'] == system for r in enforced):
                gate_fail.append(system + ': no enforced first-run reproduction check')
        misses = [r['item'] for r in rows if r['rule'] == REPRODUCIBLE and not r['enforced'] and r['within_1pct'] is False]
        check('reproduction_within_1pct', not gate_fail, systems_checked=reproducible,
              rule='first new run of each reproducible system vs the first run of its test, |d| <= 1 % (dispatcher repeat '
                   'check, amendment of 11 Nov 2026); other systems are record-only',
              failures=gate_fail, gating=[r for r in rows if r['rule'] == REPRODUCIBLE and r['enforced']],
              reported_not_gating_outside_1pct=misses,
              record_only_systems=sorted({i['system'] for i in self.items if i['repeat_check'] != REPRODUCIBLE}),
              all_items=rows)

        # 5. pooling with the first runs declared
        pooling = self.manifest.get('pooling') or {}
        check('pooling_declared', pooling.get('approved_by') == 'user' and str(pooling.get('at', '')).startswith('2026-11-10')
              and 'pooled' in self.notes, pooling=pooling, disclosure=self.manifest.get('disclosure'))

        # 6. every test at N=3 (first run + new repetitions)
        firsts = self.first_runs()
        tests, short = [], []
        for t in sorted({test_id(i) for i in self.items}):
            items = [i for i in self.items if test_id(i) == t]
            reps = {}
            first = firsts.get(t)
            if first:
                ref = first['reference']
                ok = (ref['consistent'] and ref['sha256'] == ref['pinned_sha256'] and first['record'] is not None
                      and first['record'].get('state') == 'finished' and first['record'].get('repetition') == 1)
                reps[1] = dict(source='first_run', record=ref['record'], sha256=ref['sha256'], valid=ok,
                               outside_first_campaign=ref['outside_first_campaign'], value=failed_value(first['record'] or {}),
                               failed=(first['record'] or {}).get('result', {}).get('failed', True), run=(first['record'] or {}).get('run'))
            for i in items:
                r = self.records[i['id']]
                terminal = bool(r and r.get('state') == 'finished' and r.get('classification') in TERMINAL)
                if i['repetition'] in reps:
                    short.append(f"{t}: repetition {i['repetition']} twice")
                reps[i['repetition']] = dict(source='new_run', item=i['id'], record=i['record'], valid=terminal,
                                             value=failed_value(r) if terminal else None,
                                             failed=(r.get('result') or {}).get('failed', True) if terminal else None,
                                             run=i['run_dir'])
            valid = sorted(k for k, v in reps.items() if v['valid'])
            values = [reps[k]['value'] for k in valid]
            med = statistics.median(values) if values else None
            study, test, label, seq, mode = t.split('|')
            row = dict(test=t, study=study, kind=test, label=label, sequence=seq, half=SEQ.get(seq), mode=mode,
                       n=len(valid), repetitions=valid, n_failed=sum(bool(reps[k]['failed']) for k in valid),
                       median_primary_reference_m=None if med is None or math.isinf(med) else med,
                       median_is_failure=bool(med is not None and math.isinf(med)),
                       runs={str(k): dict(source=v['source'], run=v['run'], failed=v['failed'],
                                          ate_m=None if v['value'] is None or math.isinf(v['value']) else v['value'])
                             for k, v in sorted(reps.items())})
            tests.append(row)
            if valid != [1, 2, 3]:
                short.append(f'{t}: repetitions {valid}')
        check('every_test_n3', not short, tests=len(tests), short=short,
              note='median over the pooled N=3 against the primary reference (failed = +inf); the paper scores ZED runs '
                   'against the RTK-fixed reference (derived/zed-fixed-only.json), which must be computed for the new runs')

        # 7. the export itself
        check('paper_export', not export_problems and not selection_problems, files=len(exported),
              problems=export_problems + selection_problems)

        first_reviews = [dict(file=str(p), sha256=sha(p), passed=load(p).get('passed'))
                         for p in sorted(self.first.glob('final-completion-review*.json'))]
        gating = ('manifest_integrity', 'all_items_terminal', 'no_unresolved_fault_or_stop', 'identity_gates_passed',
                  'reproduction_within_1pct', 'pooling_declared', 'every_test_n3', 'paper_export')
        return dict(
            schema=1, kind='sielinko-n3-completion-review', campaign=self.name,
            campaign_id=self.manifest['campaign_id'], amendment=self.manifest['amendment'],
            passed=all(checks[k]['passed'] for k in gating), gating_checks=list(gating),
            counts=dict(counts, tests=len(tests), tests_at_n3=sum(t['n'] == 3 for t in tests),
                        exported_files=len(exported),
                        exported_new_runs=sum(v['origin'] == 'paper_n3_new_run' for v in exported.values()),
                        exported_first_runs=sum(v['origin'] != 'paper_n3_new_run' for v in exported.values())),
            checks=checks, per_test=tests, selections=selections, first_runs_reviews=first_reviews,
            first_campaign=str(self.first), independent_test=False,
            qualification='The second half shares recording, site and day with the development half, and the full '
                          'recording contains it (first campaigns\' qualification, unchanged).',
            sources=dict(manifest=str(self.manifest_path), manifest_sha256=self.manifest_sha,
                         amendment_notes=str(self.notes_path), amendment_notes_sha256=sha(self.notes_path)
                         if self.notes_path.is_file() else None,
                         events=str(self.dir / 'events.jsonl')),
            generated_by=identity)

    # ------------------------------------------------------------ write
    def run(self, dry_run=False):
        identity = git_identity()
        exported, export_problems = self.paper_records(identity)
        selections, selection_problems = self.selections()
        value = self.review(exported, export_problems, selections, selection_problems, identity)
        if dry_run:
            return value, None
        target = self.dir / 'attempts-paper'
        for name, record in exported.items():
            write_json(target / name, record)
        for stale in target.glob('final_n1__*.json'):
            if stale.name not in exported:
                stale.unlink()
        for study, s in selections.items():
            dest = self.dir / 'studies' / study / 'selection.json'
            dest.parent.mkdir(parents=True, exist_ok=True)
            data = Path(s['source']).read_bytes()
            if not dest.is_file() or dest.read_bytes() != data:
                tmp = dest.with_name(dest.name + '.tmp')
                tmp.write_bytes(data)
                tmp.replace(dest)
        path = self.dir / 'final-completion-review-n3.json'
        write_json(path, value)
        digest = sha(path)
        Path(str(path) + '.sha256').write_text(f'{digest}  {path.name}\n')
        return value, digest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--campaign', action='append', choices=sorted(FIRST))
    parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--dry-run', action='store_true', help='print the verdicts, write nothing')
    args = parser.parse_args(argv)
    for name in args.campaign or sorted(FIRST):
        value, digest = Campaign(name, args.out).run(args.dry_run)
        failing = {k: v for k, v in value['checks'].items() if not v['passed']}
        print(json.dumps(dict(campaign=name, passed=value['passed'], sha256=digest, counts=value['counts'],
                              failing={k: v.get('not_terminal') or v.get('failures') or v.get('short') or v.get('problems')
                                       or v.get('live_stop_or_fault_files') or v.get('failed') or True
                                       for k, v in failing.items()}), default=str))
    return 0


if __name__ == '__main__':
    sys.exit(main())
