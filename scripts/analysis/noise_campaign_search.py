"""Uniform development search policy; execution is supplied by the coordinator.

No CLI and no work starts on import. Independent studies may run concurrently,
but each study always asks, measures, and tells its optimizer in serial order.
Fresh final measurements never feed selection, including loop-closure results.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import optuna

from noise_adapters import KEYS


def identity(params):
    return tuple(float(params[key]) for key in KEYS)


def label_for(spec, params):
    if identity(params) == identity(spec['rule_c']):
        return 'rule_c'
    if identity(params) == identity(spec['legacy']):
        return 'legacy'
    return 'noise_' + hashlib.sha256(json.dumps(identity(params)).encode()).hexdigest()[:16]


def unique(items):
    seen = set()
    for item in items:
        key = identity(item['params'])
        if key not in seen:
            seen.add(key)
            yield item


def combined(records, objective='mean_worst'):
    if not records:
        raise ValueError('An empty cohort cannot be scored')
    failed = sum(int(record['result']['failed']) for record in records)
    residuals = [record['result']['loss'] - 10 * int(record['result']['failed'])
                 for record in records]
    if not all(np.isfinite(x) and -1e-12 <= x <= 2 + 1e-12 for x in residuals):
        raise ValueError('Invalid normalized error/coverage residual')
    if objective == 'mean':
        residual = np.mean(residuals)
    elif objective == 'mean_worst':
        residual = .5 * np.mean(residuals) + .5 * max(residuals)
    else:
        raise ValueError('Unknown objective')
    return float(10 * failed + residual)


def controls(spec):
    return list(unique([dict(params=spec['rule_c']), dict(params=spec['legacy'])]))


class DevelopmentSearch:
    def __init__(self, engine, spec, protocol):
        self.engine, self.spec, self.protocol = engine, spec, protocol
        self.directory = Path(engine.ART) / 'studies' / spec['id']

    def immutable(self, name, value):
        target = self.directory / name
        if target.exists():
            previous = json.loads(target.read_text())
            if previous != value:
                raise RuntimeError('Frozen development state differs on replay: ' + str(target))
            return previous
        self.engine.base.write(target, value)
        return value

    def attempt(self, params, sequence, phase, repetition=1, mode='vio'):
        return self.engine.run_attempt(self.spec, label_for(self.spec, params), params,
                                       sequence, mode, repetition, phase)

    def candidate(self, params, records, objective='mean_worst', **extra):
        return dict(label=label_for(self.spec, params), params=params,
                    loss=combined(records, objective), records=[r['key'] for r in records],
                    failures=sum(int(r['result']['failed']) for r in records), **extra)

    def optimize(self, *, seed, count, startup, seeds, phase, sequences, name,
                 objective='mean_worst', preliminary_labels=False):
        sampler = optuna.samplers.TPESampler(seed=seed, n_startup_trials=startup,
                                             multivariate=True)
        study = optuna.create_study(direction='minimize', sampler=sampler)
        for candidate in unique(seeds):
            study.enqueue_trial(candidate['params'])
        trials = []
        for index in range(count):
            trial = study.ask()
            params = {key: trial.suggest_float(key, *self.spec['bounds'][key], log=True)
                      for key in KEYS}
            path = self.directory / name / f'trial{index:02}.json'
            if path.exists() and json.loads(path.read_text())['params'] != params:
                raise RuntimeError('Optimizer proposal differs on replay: ' + str(path))
            records = [self.attempt(params, seq, phase) for seq in sequences]
            result = self.candidate(params, records, objective, trial=index,
                                    optimizer_seed=seed, phase=phase)
            if preliminary_labels:
                # Retain the original 16-proposal pilot's declared tie order.
                label = label_for(self.spec, params)
                result['tie_label'] = label if label in ('rule_c', 'legacy') else f'candidate{index:02}'
            study.tell(trial, result['loss'])
            self.immutable(str(Path(name) / path.name), result)
            trials.append(result)
            self.engine.base.event('candidate_scored', study=self.spec['id'], phase=phase,
                                   seed=seed, trial=index, label=result['label'], loss=result['loss'])
        return trials

    def preliminary(self):
        policy = self.protocol['preliminary']
        trials = self.optimize(seed=policy['seed'], count=policy['candidates'],
            startup=policy['startup'], seeds=controls(self.spec), phase='preliminary',
            sequences=self.spec['clips'], name='preliminary', objective='mean',
            preliminary_labels=True)
        ranked = sorted(unique(trials), key=lambda r: (r['loss'], r['tie_label']))
        finalists = []
        for trial in ranked[:policy['finalists']]:
            records = [self.attempt(trial['params'], seq, 'preliminary', rep)
                       for rep in range(1, policy['repetitions'] + 1)
                       for seq in self.spec['clips']]
            finalists.append(self.candidate(trial['params'], records, 'mean',
                                             tie_label=trial['tie_label']))
        finalists.sort(key=lambda r: (r['loss'], r['tie_label']))
        return self.immutable('preliminary-selection.json', dict(
            finalists=finalists, proposals=trials, objective='mean', independent_test=False))

    def screening(self):
        policy = self.protocol['screen']
        return [self.optimize(seed=seed, count=policy['candidates_per_seed'],
                startup=policy['startup'], seeds=controls(self.spec), phase='screen',
                sequences=self.spec['clips'], name=f'screen_seed{index}')
                for index, seed in enumerate(policy['seeds'])]

    def full_search(self, preliminary, screens):
        policy = self.protocol['full']
        winners = [min(group, key=lambda r: (r['loss'], r['label'])) for group in screens]
        ranked = sorted([row for group in screens for row in group],
                         key=lambda r: (r['loss'], r['label']))
        seeds = list(unique(controls(self.spec) + preliminary['finalists'] + winners + ranked))
        seeds = seeds[:policy['seed_candidates']]
        if len(seeds) != policy['seed_candidates']:
            raise RuntimeError('Too few distinct full-search seeds')
        self.immutable('full-seeds.json', seeds)
        return self.optimize(seed=policy['seed'], count=policy['candidates'],
            startup=policy['seed_candidates'], seeds=seeds, phase='full',
            sequences=self.spec['full_sequences'], name='full_search')

    def repeated_selection(self, trials):
        policy = self.protocol['full']
        ranked = sorted(unique(trials), key=lambda r: (r['loss'], r['label']))
        finalists = []
        for trial in unique(ranked[:policy['finalists']] + controls(self.spec)):
            records = [self.attempt(trial['params'], seq, 'full', rep)
                       for rep in range(1, policy['repetitions'] + 1)
                       for seq in self.spec['full_sequences']]
            finalists.append(self.candidate(trial['params'], records))
        finalists.sort(key=lambda r: (r['loss'], r['label']))
        result = dict(winner=finalists[0], repeated_candidates=finalists,
                      full_trial_ranking=ranked, independent_test=False,
                      note='One frozen setting per algorithm/dataset, selected on full development VIO. LC never changes selection.')
        target = self.directory / 'selection.json'
        if target.exists():
            previous = json.loads(target.read_text())
            if {k: v for k, v in previous.items() if k != 'selected_at'} != result:
                raise RuntimeError('Frozen VIO selection changed on replay')
            return previous
        result['selected_at'] = self.engine.base.now()
        self.engine.base.write(target, result)
        return result

    def develop(self):
        preliminary = self.preliminary()
        screens = self.screening()
        return self.repeated_selection(self.full_search(preliminary, screens))

    def final_n1(self):
        # Only the serial final coordinator may call this after development.
        selection = json.loads((self.directory / 'selection.json').read_text())
        records = []
        modes = ['vio', 'vio-lc'] if self.spec['supports_lc'] else ['vio']
        for mode in modes:
            for sequence in self.spec['full_sequences']:
                records.append(self.attempt(selection['winner']['params'], sequence,
                                             'final_n1', mode=mode))
        return self.immutable('final-n1.json', dict(selected_at=selection['selected_at'],
            parameters=selection['winner']['params'], records=[r['key'] for r in records],
            independent_test=False,
            note='Fresh executions with frozen settings; these same recordings remain development data.'))
