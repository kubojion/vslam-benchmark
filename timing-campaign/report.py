#!/usr/bin/python3
"""Generate PROGRESS/IMU-TIMING-TUNE/results.csv and the tables of RESULTS.md from run outputs. Never typed by hand."""
import csv, hashlib, json, math, statistics as st, sys
from pathlib import Path
W = Path(__file__).resolve().parents[1]; P = Path('/data/imoroz/PROGRESS/IMU-TIMING-TUNE')
s = json.loads((W/'timing-campaign/run/state.json').read_text())
sha = {}
def H(p):
    if p not in sha: sha[p] = hashlib.sha256(Path(p).read_bytes()).hexdigest()
    return sha[p]
def find(x, key):
    if isinstance(x, dict):
        if key in x and not isinstance(x[key], (dict, list)): return x[key]
        for v in x.values():
            r = find(v, key)
            if r is not None: return r
base = {(c['mode'], c['seq'], c['alg']): c for c in csv.DictReader(open('/data/imoroz/PAPER/vslam-paper/paper/generated/cells.csv'))}
test = {}
for r in csv.DictReader(open('/data/imoroz/PAPER/vslam-paper/notes/timing-test-20261030/results.csv')):
    if r['block'] == 'B': test.setdefault((r['seq'], r['alg']), []).append(r)
rows = []
for d in s['done'].values():
    if d['block'] == 'CHECK': continue
    run = W/'results'/d['mode']/d['ds']/d['seq']/d['alg']/f"run{d['run']}"
    doc = json.loads((run/'run_eval.json').read_text()) if (run/'run_eval.json').is_file() else {}
    inputs = (run/'provenance/inputs.json').read_text() if (run/'provenance/inputs.json').is_file() else ''
    state = W/'results/.attempt-state'/'__'.join((d['mode'], d['ds'], d['seq'], d['alg']))/f"run{d['run']}.json"
    st_doc = json.loads(state.read_text()) if state.is_file() else {}
    rows.append(dict(cohort=d['cohort'], block=d['block'], mode=d['mode'], dataset=d['ds'], seq=d['seq'], alg=d['alg'], run=d['run'], rep=d['rep'],
        variant=d['variant'], counted=d.get('counted'), replaced_by=d.get('replaced_by', ''), replacement_of=d.get('replacement', ''), run_status=doc.get('run_status') or 'no_trajectory',
        ate_m=d.get('ate_m'), scale=d.get('scale'), time_coverage_pct=find(doc, 'trajectory_time_coverage_pct'), estimator_exit=d.get('estimator_exit_code'),
        recorded_exit=d.get('process_exit_code'), crash=d.get('crash', ''), infra=d.get('infra', ''), duration_s=round(d.get('duration_s') or 0, 1),
        validation_passed=st_doc.get('validation_passed'), imu_hash_ok=H(W/f"datasets/.timing-imu/{d['ds']}__{d['seq']}/{d['variant']}/data.csv") in inputs))
with (P/'results.csv').open('w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
def f2(x): return '-' if x in (None, '') or not math.isfinite(float(x)) else f'{float(x):.2f}'
A = 'okvis2 okvis2x orbslam3 openvins voxel_svio svo_pro basalt cuvslam airslam mast3r_fusion'.split()
def cells(blocks):
    o = ['| Mode | Sequence | System | Old ok/runs | Old median | New ok/runs | New median | New range | Timing test |', '|---|---|---|---|---|---|---|---|---|']
    for m in ('vio', 'vio-lc'):
        for q in sorted({r['seq'] for r in rows if r['block'] in blocks}, reverse=True):
            for a in A:
                x = [r for r in rows if r['block'] in blocks and r['mode'] == m and r['seq'] == q and r['alg'] == a and r['counted'] and r['variant'] != 'unchanged']
                if not x: continue
                ok = [r['ate_m'] for r in x if r['run_status'] == 'ok']; c = base.get((m, q, a), {})
                t = [float(r['ate']) for r in test.get((q, a), []) if r['status'] == 'ok'] if m == 'vio' else []
                old = f"{c.get('n_ok', '-')}/{c.get('n_terminal', '-')}"
                o.append(f"| {m} | {q[:6]} | {a} | {old} | {f2(c.get('value'))} | {len(ok)}/{len(x)} | {f2(st.median(ok)) if ok else '-'} | {(f2(min(ok))+' to '+f2(max(ok))) if ok else '-'} | {f2(st.median(t)) if t else '-'} |")
    return '\n'.join(o)
def regress():
    o = ['| Sequence | System | Timing test median | New runs |', '|---|---|---|---|']
    for q in ('seq07', 'seq04'):
        for a in ('openvins', 'basalt', 'mast3r_fusion'):
            o.append(f"| {q} | {a} | {st.median(float(r['ate']) for r in test[(q, a)]):.3f} | "+', '.join(f"{r['ate_m']:.3f}" for r in rows if r['block'] == 'CITRUS' and r['mode'] == 'vio' and r['seq'] == q and r['alg'] == a)+' |')
    return '\n'.join(o)
def attempts(pred):
    o = ['| Cell | Run | Status | Estimator / recorded exit | What happened |', '|---|---|---|---|---|']
    for r in rows:
        if pred(r):
            what = f"replaced by run {r['run']+200}" if r['replaced_by'] else 'replacement, counted' if r['replacement_of'] else 'counted'
            o.append(f"| {r['mode']} {r['seq'][:6]} {r['alg']} | {r['run']} | {r['run_status']} | {r['estimator_exit']} / {r['recorded_exit']} | {what} |")
    return '\n'.join(o)
def orb():
    o = ['| Mode | Sequence | Old median | 3-core ok | 3-core median | 3-core range | 4-core ok, the result | 4-core median | 4-core range |', '|---|---|---|---|---|---|---|---|---|']
    for m in ('vio', 'vio-lc'):
        for q in ('seq07', 'seq04'):
            g = lambda b: [r for r in rows if r['block'] == b and r['mode'] == m and r['seq'] == q and r['alg'] == 'orbslam3' and r['counted']]
            x, y = [r['ate_m'] for r in g('CITRUS') if r['run_status'] == 'ok'], [r['ate_m'] for r in g('ORB4') if r['run_status'] == 'ok']
            o.append(f"| {m} | {q} | {f2(base[(m, q, 'orbslam3')]['value'])} | {len(x)}/3 | {st.median(x):.2f} | {min(x):.2f} to {max(x):.2f} | {len(y)}/3 | {st.median(y):.2f} | {min(y):.2f} to {max(y):.2f} |")
    return '\n'.join(o)
out = dict(orbcmp=orb(), cells=cells(('CITRUS',)), regress=regress(), crash=attempts(lambda r: r['crash'] or r['replacement_of']), sielinko=attempts(lambda r: r['block'] == 'SIELINKO'), job2runs=attempts(lambda r: r['block'] == 'SIELINKO2'),
           orb4=cells(('ORB4',)), job2=cells(('SIELINKO2',)),
           n=len(rows), counted=sum(1 for r in rows if r['counted']), imu_bad=[r['run'] for r in rows if not r['imu_hash_ok'] and r['run_status'] != 'no_trajectory'],
           no_validate=[(r['alg'], r['run'], r['run_status']) for r in rows if r['validation_passed'] is not True and r['block'] in ('CITRUS', 'SIELINKO')][:30])
json.dump(out, open(W/'timing-campaign/run/report.json', 'w'), indent=1)
print(out['n'], out['counted'], out['imu_bad'], out['no_validate'])
