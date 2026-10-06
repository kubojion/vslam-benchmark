#!/usr/bin/env python3
"""IMU noise rule "authors' operating point" (user decision 2026-10-05).

Each estimator receives the dataset's published Allan-variance values, each quantity multiplied by
the factor its authors applied to the EuRoC Kalibr calibration in their released EuRoC configuration
(configs/sensors/imu-noise-rule.json, docs/imu-noise-rule-20261005.md). Only the datasets listed in
the rule use it; elsewhere every caller keeps its previous behaviour.
"""
import hashlib
import json
from pathlib import Path

RULE = Path(__file__).resolve().parents[2] / 'configs/sensors/imu-noise-rule.json'
EXTENSION = RULE.with_name('imu-noise-rule-20261006.json')


def load(path=None):
    extend = path is None
    path = path or RULE
    rule = json.loads(Path(path).read_text())
    if rule.get('schema') != 1 or rule.get('rule') != 'authors_operating_point':
        raise ValueError(f'unsupported IMU noise rule: {path}')
    if extend:
        extra = json.loads(EXTENSION.read_text())
        if extra['schema'] != 1 or extra['rule'] != rule['rule']:
            raise ValueError('unsupported IMU noise rule extension')
        for dataset in extra['datasets']:
            if dataset in rule['datasets']:
                raise ValueError('duplicate noise policy dataset')
            source = extra['dataset_allan'][dataset]
            raw = (RULE.parents[2] / source['source']).read_bytes()
            if hashlib.sha256(raw).hexdigest() != source['sha256']:
                raise ValueError('IMU calibration source changed: ' + dataset)
            rule['datasets'].append(dataset)
            rule['dataset_allan'][dataset] = source
    return rule


def applies(dataset, rule=None):
    rule = rule or load()
    return dataset in rule['datasets']


def factors(algorithm, rule=None):
    """Authors' EuRoC value / EuRoC Kalibr value, per noise quantity (1 where the authors copied Kalibr)."""
    rule = rule or load()
    authors = rule['authors_euroc'][algorithm]
    reference = rule['euroc_reference']
    if authors.get('copies_reference'):
        return {k: 1.0 for k in rule['keys']}
    return {k: float(authors[k]) / float(reference[k]) for k in rule['keys']}


def noise(algorithm, dataset, rule=None):
    """The rule's noise for one estimator on one dataset: dataset Allan value x authors' factor."""
    rule = rule or load()
    if not applies(dataset, rule):
        raise ValueError(f'{dataset} does not use the authors-operating-point IMU noise rule')
    allan = rule['dataset_allan'][dataset]
    return {k: float(allan[k]) * f for k, f in factors(algorithm, rule).items()}


def record(path=RULE, *, dataset=None):
    path = Path(path)
    if dataset in ('rosariov2', 'citrusfarm'):
        rule = load()
        files = [record(path), record(EXTENSION)]
        for item in files:
            item['path'] = str(Path(item['path']).relative_to(RULE.parents[2]))
        source = rule['dataset_allan'][dataset]
        files.append(dict(path=source['source'], sha256=source['sha256']))
        digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
        return dict(dataset=dataset, files=files, sha256=digest)
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == '__main__':
    import sys
    rule = load()
    dataset = sys.argv[1] if len(sys.argv) > 1 else rule['datasets'][0]
    for algorithm in rule['authors_euroc']:
        f, n = factors(algorithm, rule), noise(algorithm, dataset, rule)
        print(f'{algorithm:14s} ' + '  '.join(f'{k.split("_")[0][:5]}/{"rw" if "walk" in k else "nd"} x{f[k]:<8.4g} -> {n[k]:.6g}' for k in rule['keys']))
