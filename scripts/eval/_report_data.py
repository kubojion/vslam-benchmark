"""Shared checked data for figures and prose counts, with no legacy fallback."""
from collections import defaultdict
import hashlib

from build_benchmark_csv import RUN_TYPES, build_rows, csv_text, load_inventory
from _aggregate_runs import summarize_cell


def checked_rows(inventory_path, csv_dir):
    rows = build_rows(load_inventory(inventory_path))
    evidence = [dict(path=str(inventory_path), sha256=hashlib.sha256(inventory_path.read_bytes()).hexdigest())]
    for mode in RUN_TYPES:
        path = csv_dir/f'benchmark-{mode}.csv'
        expected = csv_text([r for r in rows if r['run_type'] == mode])
        if not path.is_file() or path.read_text() != expected:
            raise ValueError(f'CSV differs from authoritative inventory: {path}')
        evidence.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return rows, evidence


def cells(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row['run_type'], row['dataset'], row['seq'], row['algo'], row['gnss_variant'])].append(row)
    return [(key, group, summarize_cell(group)) for key, group in sorted(groups.items())]


def plotted_cell(rows):
    """Do not pool distinct recorded cohorts, failures or input variants."""
    summary = summarize_cell(rows)
    groups = summary['cohorts']
    value = groups[0]['conditional_primary_ate']['median'] if len(groups) == 1 else None
    notes = []
    if len(groups) > 1: notes.append('cohorts')
    if any(r['export_kind'] == 'keyframes' for r in rows): notes.append('K')
    if any(r['scientific_status'] == 'rerun_required' for r in rows): notes.append('R')
    if any(r['process_exit_code'] not in (0, None) for r in rows): notes.append('X')
    if any(r['coverage_gap_pct'] is not None and r['coverage_gap_pct'] < 95 for r in rows): notes.append('P')
    if not summary['clean_qualified_n3']: notes.append('U')
    ok = summary['outcomes'].get('ok', 0)
    text = f'{value:.3g}' if value is not None else 'no score'
    text += f'\n{ok}/{summary["planned_slots"]} ok'
    if notes: text += '\n' + ','.join(notes)
    return dict(value=value, annotation=text, summary=summary, flags=notes)
