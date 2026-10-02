#!/usr/bin/env python3
"""Build a dependency-free static browser for the current result manifest."""

from __future__ import annotations

import getpass
import argparse
import hashlib
import html
import csv
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS = REPO / "results"
SITE = RESULTS / "site"
TEMP = RESULTS / ".site.tmp"
SENSITIVE_TEXT = {"run_log.txt", "run_meta.json", "run_eval.json"}
RUN_TYPES = ("vo", "vo-lc", "vio", "vio-lc", "gnss-vio")
sys.path.insert(0,str(REPO/'scripts/eval'))
from build_benchmark_csv import load_inventory, build_rows, csv_text


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def redact(text: str) -> str:
    replacements = {
        str(REPO): "<repo>",
        str(Path.home()): "<home>",
        socket.gethostname(): "<host>",
        getpass.getuser(): "<user>",
    }
    for source, replacement in sorted(replacements.items(), key=lambda x: -len(x[0])):
        if source:
            text = text.replace(source, replacement)
    text = re.sub(r"/(?:home|data)/[^/\s\"']+", "/<private>", text)
    return text


def safe_source(relative_run: str, relative_artifact: str) -> Path | None:
    run_dir = (RESULTS / relative_run).resolve()
    source = (run_dir / relative_artifact).resolve()
    if RESULTS.resolve() not in source.parents or run_dir not in source.parents:
        return None
    return source if source.is_file() else None


def artifact_copy(run: dict, artifact: dict, output: Path) -> Path | None:
    if artifact.get('source_path'):
        if artifact['source_path']!=run.get('evaluation_path'):return None
        source=(REPO/artifact['source_path']).resolve()
        if RESULTS.resolve() not in source.parents or not source.is_file():return None
        if hashlib.sha256(source.read_bytes()).hexdigest()!=run.get('evaluation_sha256'):
            raise ValueError('current evaluation changed since manifest generation')
    else:
        source = safe_source(run["path"], artifact["path"])
    if source is None:
        return None
    output.parent.mkdir(parents=True, exist_ok=True)
    if source.name in SENSITIVE_TEXT:
        output.write_text(redact(source.read_text(errors="replace")))
    else:
        relative_target = os.path.relpath(source, output.parent)
        output.symlink_to(relative_target)
    return output


def metric(run: dict, name: str) -> str:
    value = (run.get("metrics") or {}).get(name)
    if isinstance(value, float):
        return f"{value:.4f}"
    return "" if value is None else str(value)


def run_page(run: dict, page_name: str, file_key: str) -> str:
    artifacts = run.get("artifacts") or []
    links = []
    previews = []
    for artifact in artifacts:
        rel = artifact["path"]
        output = TEMP / "files" / file_key / rel
        if artifact_copy(run, artifact, output) is None:
            continue
        href = f"../files/{file_key}/{rel}"
        links.append(
            f'<li><a href="{esc(href)}">{esc(rel)}</a> '
            f'({artifact.get("size_bytes", 0):,} bytes; {esc(artifact.get("interpretation","saved evidence"))})</li>'
        )
        if artifact.get('interpretation')=='current_figure' and Path(rel).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            previews.append(
                f'<figure><figcaption>{esc(rel)}</figcaption>'
                f'<a href="{esc(href)}"><img loading="lazy" src="{esc(href)}"></a></figure>'
            )
    validation = "".join(f"<li>{esc(e)}</li>" for e in run.get("validation_errors", []))
    blockers = "".join(f"<li>{esc(e)}</li>" for e in sorted(set(
        run.get("scientific_blockers", []) + run.get("protocol_blockers", []))))
    limits = "".join(f"<li>{esc(e)}</li>" for e in run.get("claim_limits", []) + run.get('reproducibility_disclosures', []))
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="../assets/style.css"><title>{esc(run['algorithm'])}</title></head>
<body><nav><a href="../index.html">All results</a></nav>
<h1>{esc(run['algorithm'])}: {esc(run['dataset'])}/{esc(run['sequence'])}</h1>
<dl><dt>Run type</dt><dd>{esc(run['run_type'])}</dd><dt>Repeat</dt><dd>{esc(run['repeat'])}</dd>
<dt>Status</dt><dd class="status-{esc(run['status'])}">{esc(run['status'])}</dd>
<dt>Execution</dt><dd>{esc(run.get('execution_status','unknown'))}; exit {esc(run.get('process_exit_code','unknown'))}</dd>
<dt>Qualification</dt><dd>{esc(run.get('scientific_status','unreviewed'))}</dd>
<dt>Experimental protocol</dt><dd>{esc(run.get('protocol_status','unreviewed'))}; cell: {esc(run.get('protocol_state','unreviewed'))}</dd>
<dt>Observed outcome</dt><dd>{esc(run.get('observed_outcome','unknown'))}</dd>
<dt>Implementation</dt><dd>{esc(run.get('implementation_label','historical'))}</dd>
<dt>Accepted claim</dt><dd>{esc(run.get('accepted_claim') or 'none')}</dd>
<dt>Native error log observations</dt><dd>{esc(run.get('native_error_observation_count',0))}</dd>
<dt>Membership</dt><dd>{esc(run.get('campaign_membership','unknown'))}</dd>
<dt>Input variant</dt><dd>{esc(run.get('input_variant','default'))}</dd>
<dt>Recorded cohort</dt><dd>{esc(run.get('cohort','unknown'))}</dd>
<dt>Provenance</dt><dd class="provenance-{esc(run.get('provenance_status', 'legacy'))}">{esc(run.get('provenance_status', 'legacy'))}</dd>
<dt>Measurements</dt><dd class="measurement-{esc(run.get('measurement_status', 'legacy'))}">{esc(run.get('measurement_status', 'legacy'))}</dd>
<dt>Machine</dt><dd>{esc(run.get('machine_id', 'unknown'))}</dd>
<dt>Primary ATE [m]</dt><dd>{esc(metric(run, 'primary_ate_rmse_m'))} ({esc(metric(run, 'primary_alignment'))})</dd>
<dt>Position validity</dt><dd>{esc(metric(run, 'position_metric_validity'))}</dd>
<dt>Sim3 ATE RMSE</dt><dd>{esc(metric(run, 'ate_rmse'))}</dd>
<dt>SE3 ATE RMSE</dt><dd>{esc(metric(run, 'ate_se3_rmse'))}</dd>
<dt>Export type</dt><dd>{esc(metric(run, 'export_kind'))}</dd>
<dt>Dense coverage [%]</dt><dd>{esc(metric(run, 'coverage_gap_pct')) or 'unknown'}</dd>
<dt>Camera pose coverage [%]</dt><dd>{esc(metric(run, 'camera_pose_coverage_pct')) or 'unknown'}</dd>
<dt>Reference paired [%]</dt><dd>{esc(metric(run, 'reference_pairs_pct_of_input')) or 'unknown'}</dd>
<dt>Processing FPS</dt><dd>{esc(metric(run, 'processing_fps'))}</dd>
<dt>Nominal input FPS</dt><dd>{esc(metric(run, 'end_to_end_fps'))} (available inputs / wrapper elapsed time)</dd>
<dt>Command input FPS</dt><dd>{esc(metric(run, 'command_input_fps'))} (available inputs / command time)</dd>
<dt>Measurement note</dt><dd>{esc(metric(run, 'measurement_warning'))}</dd>
<dt>Trajectory pose rate</dt><dd>{esc(metric(run, 'trajectory_pose_rate'))}</dd>
<dt>Dataset/wall factor</dt><dd>{esc(metric(run, 'realtime_factor'))} (does not establish latency or complete processing)</dd>
<dt>Resource scope</dt><dd>{esc(metric(run, 'resource_scope'))}</dd></dl>
{f'<h2>Validation</h2><ul>{validation}</ul>' if validation else ''}
{f'<h2>Scientific blockers</h2><ul>{blockers}</ul>' if blockers else ''}
{f'<h2>Claim limits and disclosures</h2><ul>{limits}</ul>' if limits else ''}
<p>Numerical evaluation, execution and qualification are separate. Historical plots remain artifacts; they are not repaired figures.</p>
<h2>Current plots</h2><div class="plots">{''.join(previews) or '<p>No validated current plots.</p>'}</div>
<h2>Artifacts</h2><ul>{''.join(links)}</ul></body></html>"""


def index_page(manifest: dict, page_map: dict[str, str]) -> str:
    rows = []
    for run in manifest.get("runs", []):
        key = run["path"]
        membership=run.get('campaign_membership','unknown')
        headline=membership in ('original_n3_campaign','gnss_default_future_n3','legacy_gnss_variant')
        rows.append(f"""<tr data-headline="{'yes' if headline else 'no'}" data-type="{esc(run['run_type'])}" data-search="{esc(' '.join(str(run.get(k, '')) for k in ('dataset','sequence','algorithm','status','scientific_status','campaign_membership','input_variant')).lower())}">
<td>{esc(run['run_type'])}</td><td>{esc(run['dataset'])}</td><td>{esc(run['sequence'])}</td>
<td><a href="runs/{esc(page_map[key])}">{esc(run['algorithm'])}</a></td><td>{esc(run['repeat'])}</td>
<td class="status-{esc(run['status'])}">{esc(run['status'])}</td>
<td>{esc(run.get('scientific_status','unreviewed'))}<br>protocol: {esc(run.get('protocol_status','unreviewed'))}<br>{esc(run.get('observed_outcome','unknown'))}</td><td>{esc(membership)}</td><td>{esc(run.get('input_variant','default'))}</td>
<td class="provenance-{esc(run.get('provenance_status', 'legacy'))}">{esc(run.get('provenance_status', 'legacy'))}</td>
<td class="measurement-{esc(run.get('measurement_status', 'legacy'))}">{esc(run.get('measurement_status', 'legacy'))}</td><td>{esc(metric(run, 'primary_ate_rmse_m'))} {esc(metric(run,'primary_alignment'))}</td>
<td>{esc(metric(run, 'ate_se3_rmse'))}</td><td>{esc(metric(run, 'coverage_gap_pct'))}</td><td>{esc(metric(run, 'processing_fps'))}</td><td>{esc(metric(run, 'realtime_factor'))}</td></tr>""")
    buttons = "".join(f'<button data-type="{t}">{t}</button>' for t in ("all", *RUN_TYPES))
    comparisons = " · ".join(
        f'<a href="comparisons/{esc(run_type)}.html">{esc(run_type)} comparison</a>'
        for run_type in RUN_TYPES
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="assets/style.css"><title>VSLAM results</title></head><body>
<h1>VSLAM benchmark results</h1><p>Audit: {esc(manifest.get('audit_status','unreviewed'))} · Generator Git: {esc((manifest.get('git_commit') or '')[:12])}</p>
<p>Missing and failed repetitions are retained. Numerical validity is not publication qualification. Per-run hardware is recorded on each detail page.</p>
<p>{comparisons}</p>
<div class="controls">{buttons}<input id="filter" placeholder="Filter dataset, sequence, algorithm, or status"><label><input type="checkbox" id="outside">Show historical/smoke artifacts</label></div>
<table><thead><tr><th>Type</th><th>Dataset</th><th>Sequence</th><th>Algorithm</th><th>Run</th><th>Numerical status</th><th>Qualification</th><th>Membership</th><th>Input variant</th><th>Provenance</th><th>Measurements</th><th>Primary ATE [m] / alignment</th><th>SE3 ATE [m]</th><th>Dense coverage %</th><th>Processing FPS</th><th>RTF</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table><script src="assets/site.js"></script></body></html>"""


def comparison_page(run_type: str, source: Path, csv_href: str) -> str:
    if not source.is_file():
        body = "<p>The tracked comparison CSV is not present in this checkout.</p>"
    else:
        with source.open(newline="") as stream:
            rows = list(csv.reader(stream))
        if rows:
            head = "".join(f"<th>{esc(value)}</th>" for value in rows[0])
            table_rows = "".join(
                "<tr>" + "".join(f"<td>{esc(value)}</td>" for value in row) + "</tr>"
                for row in rows[1:]
            )
            body = (
                f'<p><a href="{esc(csv_href)}">Download benchmark-{esc(run_type)}.csv</a></p>'
                f'<div class="table-scroll"><table><thead><tr>{head}</tr></thead>'
                f'<tbody>{table_rows}</tbody></table></div>'
            )
        else:
            body = "<p>The tracked comparison CSV is empty.</p>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="../assets/style.css"><title>{esc(run_type)} comparison</title></head><body>
<nav><a href="../index.html">All results</a></nav><h1>{esc(run_type)} comparison</h1>{body}</body></html>"""


def main() -> int:
    global SITE,TEMP
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=RESULTS/'manifest.json')
    parser.add_argument('--output',type=Path,default=SITE)
    parser.add_argument('--csv-dir',type=Path,default=REPO)
    args=parser.parse_args();manifest_path=args.manifest;SITE=args.output
    if not manifest_path.is_file():
        raise SystemExit("results/manifest.json missing; run build_manifest.py first")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('schema_version')!=2:raise SystemExit('browser requires the reconciled schema-2 manifest')
    inventory_path=REPO/manifest['inventory_path']
    if hashlib.sha256(inventory_path.read_bytes()).hexdigest()!=manifest['inventory_sha256']:
        raise SystemExit('manifest is stale: inventory changed')
    rows=build_rows(load_inventory(inventory_path))
    for mode in RUN_TYPES:
        path=args.csv_dir/f'benchmark-{mode}.csv'
        if not path.is_file() or path.read_text()!=csv_text([r for r in rows if r['run_type']==mode]):
            raise SystemExit('stale comparison CSV: '+str(path))
    SITE.parent.mkdir(parents=True,exist_ok=True)
    TEMP=Path(tempfile.mkdtemp(prefix='.site-build-',dir=SITE.parent))
    (TEMP / "assets").mkdir(parents=True)
    (TEMP / "runs").mkdir()
    (TEMP / "comparisons").mkdir()
    (TEMP / "catalog.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (TEMP / "assets" / "style.css").write_text("""
body{font:15px system-ui,sans-serif;max-width:1500px;margin:2rem auto;padding:0 1rem;color:#202124}a{color:#1558b0}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #ddd;padding:.45rem;text-align:left;white-space:nowrap}th{position:sticky;top:0;background:#fff}.table-scroll{overflow:auto;max-height:75vh}.controls{display:flex;gap:.4rem;flex-wrap:wrap;margin:1rem 0}.controls input{min-width:22rem;padding:.45rem}button{padding:.4rem .7rem}.status-complete,.provenance-complete,.measurement-complete{color:#147a37;font-weight:600}.status-invalid,.status-failed,.provenance-invalid,.measurement-invalid{color:#b42318;font-weight:600}.status-incomplete,.provenance-legacy,.measurement-legacy{color:#9a6700;font-weight:600}.plots{display:flex;flex-wrap:wrap;gap:1rem}.plots figure{margin:0;max-width:48%}.plots img{max-width:100%;max-height:520px}dt{font-weight:600;float:left;clear:left;width:10rem}dd{margin-left:11rem;margin-bottom:.35rem}nav{margin-bottom:1rem}@media(max-width:700px){.plots figure{max-width:100%}.controls input{min-width:100%}}
""".strip() + "\n")
    (TEMP / "assets" / "site.js").write_text("""
let active='all';const rows=[...document.querySelectorAll('tbody tr')],input=document.querySelector('#filter'),outside=document.querySelector('#outside');function apply(){const q=input.value.toLowerCase();for(const row of rows)row.hidden=!((outside.checked||row.dataset.headline==='yes')&&(active==='all'||row.dataset.type===active)&&row.dataset.search.includes(q))}for(const b of document.querySelectorAll('button[data-type]'))b.onclick=()=>{active=b.dataset.type;apply()};input.oninput=apply;outside.onchange=apply;apply();
""".strip() + "\n")
    page_map = {}
    for run in manifest.get("runs", []):
        key = hashlib.sha256(run["path"].encode()).hexdigest()[:16]
        page_name = f"{key}.html"
        page_map[run["path"]] = page_name
        (TEMP / "runs" / page_name).write_text(run_page(run, page_name, key))
    for run_type in RUN_TYPES:
        source = args.csv_dir / f"benchmark-{run_type}.csv"
        csv_target = TEMP / "comparisons" / f"benchmark-{run_type}.csv"
        if source.is_file():
            shutil.copy2(source, csv_target)
        (TEMP / "comparisons" / f"{run_type}.html").write_text(
            comparison_page(run_type, source, f"benchmark-{run_type}.csv")
        )
    (TEMP / "index.html").write_text(index_page(manifest, page_map))
    if SITE.exists():
        archive=RESULTS/'.derived-sites'/uuid.uuid4().hex
        archive.parent.mkdir(parents=True,exist_ok=True)
        SITE.rename(archive)
    TEMP.replace(SITE)
    print(f"[site] {len(page_map)} run page(s) -> {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
