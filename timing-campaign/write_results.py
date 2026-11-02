#!/usr/bin/python3
"""Fill RESULTS.md from report.json. Tables are generated; the text around them is written once per stage."""
import json
from pathlib import Path
W = Path(__file__).resolve().parents[1]; d = json.loads((W/'timing-campaign/run/report.json').read_text())
t = (W/'timing-campaign/results-template.md').read_text()
for k in ('cells', 'regress', 'crash', 'sielinko', 'orb4', 'job2', 'orbcmp', 'job2runs'):
    t = t.replace('{{'+k+'}}', d[k])
Path('/data/imoroz/PROGRESS/IMU-TIMING-TUNE/RESULTS.md').write_text(t)
