#!/usr/bin/env python3
"""Build a dependency-free static browser for the current result manifest."""

from __future__ import annotations

import getpass
import hashlib
import html
import csv
import json
import os
import re
import shutil
import socket
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS = REPO / "results"
SITE = RESULTS / "site"
TEMP = RESULTS / ".site.tmp"
SENSITIVE_TEXT = {"run_log.txt", "run_meta.json", "run_eval.json"}
RUN_TYPES = ("vo", "vo-lc", "vio", "vio-lc", "gnss-vio")


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
            f'({artifact.get("size_bytes", 0):,} bytes)</li>'
        )
        if Path(rel).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            previews.append(
                f'<figure><figcaption>{esc(rel)}</figcaption>'
                f'<a href="{esc(href)}"><img loading="lazy" src="{esc(href)}"></a></figure>'
            )
    validation = "".join(f"<li>{esc(e)}</li>" for e in run.get("validation_errors", []))
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="../assets/style.css"><title>{esc(run['algorithm'])}</title></head>
<body><nav><a href="../index.html">All results</a></nav>
<h1>{esc(run['algorithm'])}: {esc(run['dataset'])}/{esc(run['sequence'])}</h1>
<dl><dt>Run type</dt><dd>{esc(run['run_type'])}</dd><dt>Repeat</dt><dd>{esc(run['repeat'])}</dd>
<dt>Status</dt><dd class="status-{esc(run['status'])}">{esc(run['status'])}</dd>
<dt>Provenance</dt><dd class="provenance-{esc(run.get('provenance_status', 'legacy'))}">{esc(run.get('provenance_status', 'legacy'))}</dd>
<dt>Machine</dt><dd>{esc(run.get('machine_id', 'unknown'))}</dd>
<dt>ATE RMSE</dt><dd>{esc(metric(run, 'ate_rmse'))}</dd>
<dt>SE3 ATE RMSE</dt><dd>{esc(metric(run, 'ate_se3_rmse'))}</dd>
<dt>Coverage</dt><dd>{esc(metric(run, 'coverage_gap_pct'))}%</dd>
<dt>FPS</dt><dd>{esc(metric(run, 'fps'))}</dd></dl>
{f'<h2>Validation</h2><ul>{validation}</ul>' if validation else ''}
<h2>Plots</h2><div class="plots">{''.join(previews) or '<p>No preview plots.</p>'}</div>
<h2>Artifacts</h2><ul>{''.join(links)}</ul></body></html>"""


def index_page(manifest: dict, page_map: dict[str, str]) -> str:
    rows = []
    for run in manifest.get("runs", []):
        key = run["path"]
        rows.append(f"""<tr data-type="{esc(run['run_type'])}" data-search="{esc(' '.join(str(run.get(k, '')) for k in ('dataset','sequence','algorithm','status')).lower())}">
<td>{esc(run['run_type'])}</td><td>{esc(run['dataset'])}</td><td>{esc(run['sequence'])}</td>
<td><a href="runs/{esc(page_map[key])}">{esc(run['algorithm'])}</a></td><td>{esc(run['repeat'])}</td>
<td class="status-{esc(run['status'])}">{esc(run['status'])}</td>
<td class="provenance-{esc(run.get('provenance_status', 'legacy'))}">{esc(run.get('provenance_status', 'legacy'))}</td><td>{esc(metric(run, 'ate_rmse'))}</td>
<td>{esc(metric(run, 'ate_se3_rmse'))}</td><td>{esc(metric(run, 'coverage_gap_pct'))}</td><td>{esc(metric(run, 'fps'))}</td></tr>""")
    buttons = "".join(f'<button data-type="{t}">{t}</button>' for t in ("all", *RUN_TYPES))
    comparisons = " · ".join(
        f'<a href="comparisons/{esc(run_type)}.html">{esc(run_type)} comparison</a>'
        for run_type in RUN_TYPES
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="assets/style.css"><title>VSLAM results</title></head><body>
<h1>VSLAM benchmark results</h1><p>Machine: {esc(manifest.get('machine_id'))} · Git: {esc((manifest.get('git_commit') or '')[:12])}</p>
<p>{comparisons}</p>
<div class="controls">{buttons}<input id="filter" placeholder="Filter dataset, sequence, algorithm, or status"></div>
<table><thead><tr><th>Type</th><th>Dataset</th><th>Sequence</th><th>Algorithm</th><th>Run</th><th>Status</th><th>Provenance</th><th>ATE</th><th>SE3 ATE</th><th>Coverage %</th><th>FPS</th></tr></thead>
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
    manifest_path = RESULTS / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit("results/manifest.json missing; run build_manifest.py first")
    manifest = json.loads(manifest_path.read_text())
    if TEMP.exists():
        shutil.rmtree(TEMP)
    (TEMP / "assets").mkdir(parents=True)
    (TEMP / "runs").mkdir()
    (TEMP / "comparisons").mkdir()
    (TEMP / "catalog.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (TEMP / "assets" / "style.css").write_text("""
body{font:15px system-ui,sans-serif;max-width:1500px;margin:2rem auto;padding:0 1rem;color:#202124}a{color:#1558b0}table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #ddd;padding:.45rem;text-align:left;white-space:nowrap}th{position:sticky;top:0;background:#fff}.table-scroll{overflow:auto;max-height:75vh}.controls{display:flex;gap:.4rem;flex-wrap:wrap;margin:1rem 0}.controls input{min-width:22rem;padding:.45rem}button{padding:.4rem .7rem}.status-complete,.provenance-complete{color:#147a37;font-weight:600}.status-invalid,.status-failed,.provenance-invalid{color:#b42318;font-weight:600}.status-incomplete,.provenance-legacy{color:#9a6700;font-weight:600}.plots{display:flex;flex-wrap:wrap;gap:1rem}.plots figure{margin:0;max-width:48%}.plots img{max-width:100%;max-height:520px}dt{font-weight:600;float:left;clear:left;width:10rem}dd{margin-left:11rem;margin-bottom:.35rem}nav{margin-bottom:1rem}@media(max-width:700px){.plots figure{max-width:100%}.controls input{min-width:100%}}
""".strip() + "\n")
    (TEMP / "assets" / "site.js").write_text("""
let active='all';const rows=[...document.querySelectorAll('tbody tr')],input=document.querySelector('#filter');function apply(){const q=input.value.toLowerCase();for(const row of rows)row.hidden=!((active==='all'||row.dataset.type===active)&&row.dataset.search.includes(q))}for(const b of document.querySelectorAll('button[data-type]'))b.onclick=()=>{active=b.dataset.type;apply()};input.oninput=apply;
""".strip() + "\n")
    page_map = {}
    for run in manifest.get("runs", []):
        key = hashlib.sha256(run["path"].encode()).hexdigest()[:16]
        page_name = f"{key}.html"
        page_map[run["path"]] = page_name
        (TEMP / "runs" / page_name).write_text(run_page(run, page_name, key))
    for run_type in RUN_TYPES:
        source = REPO / f"benchmark-{run_type}.csv"
        csv_target = TEMP / "comparisons" / f"benchmark-{run_type}.csv"
        if source.is_file():
            shutil.copy2(source, csv_target)
        (TEMP / "comparisons" / f"{run_type}.html").write_text(
            comparison_page(run_type, source, f"benchmark-{run_type}.csv")
        )
    (TEMP / "index.html").write_text(index_page(manifest, page_map))
    if SITE.exists():
        shutil.rmtree(SITE)
    TEMP.replace(SITE)
    print(f"[site] {len(page_map)} run page(s) -> {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
