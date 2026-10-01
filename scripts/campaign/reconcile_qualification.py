#!/usr/bin/env python3
"""Refresh claim reviews without recomputing or altering numerical results."""
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO/'scripts/eval'))
from build_benchmark_csv import load_inventory, preserved_write
from qualification_review import apply_review


def main():
    inventory = load_inventory(REPO/'results/repair-20261001/inventory.json')
    count = 0
    for attempt in [a for c in inventory['cells'] for a in c['attempts']]+inventory['other_artifacts']:
        if not attempt.get('evaluation_path'):
            continue
        path = REPO/attempt['evaluation_path']
        value = json.loads(path.read_text())
        before = {k: v for k, v in value.items() if k not in ('qualification', 'qualification_provenance')}
        apply_review(REPO, REPO/attempt['path'], value)
        assert before == {k: v for k, v in value.items() if k not in ('qualification', 'qualification_provenance')}
        assert value['qualification'] == attempt['qualification']
        preserved_write(path, json.dumps(value, indent=2, allow_nan=False)+'\n')
        count += 1
    print(f'Reviewed {count} saved evaluations; numerical fields unchanged. Rebuild the inventory next.')


if __name__ == '__main__':
    main()
