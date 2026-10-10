"""Explicit, validated noise overrides for the isolated development experiment.

All quantities are continuous-time standard deviations, never variances. Merely
importing this module does not change Rule C or any estimator configuration.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

KEYS = ('gyroscope_noise_density', 'accelerometer_noise_density',
        'gyroscope_random_walk', 'accelerometer_random_walk')


def validate_parameters(parameters):
    if not isinstance(parameters, dict) or set(parameters) != set(KEYS):
        raise ValueError('Exactly the four IMU noise parameters are required')
    result = {}
    for key in KEYS:
        value = parameters[key]
        if isinstance(value, bool) or not isinstance(value, (float, int)):
            raise ValueError('IMU noise must be numeric: ' + key)
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError('IMU noise must be finite and positive: ' + key)
        result[key] = value
    return result


def document(algorithm, dataset, parameters):
    return dict(schema=1, algorithm=algorithm, dataset=dataset,
                units='continuous_time_standard_deviation',
                parameters=validate_parameters(parameters))


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate noise-document key: ' + key)
        result[key] = value
    return result


def load(path, algorithm, dataset):
    path = Path(path)
    raw = path.read_bytes()
    data = json.loads(raw, object_pairs_hook=_unique_object)
    expected = {'schema', 'algorithm', 'dataset', 'units', 'parameters'}
    if not isinstance(data, dict) or set(data) != expected:
        raise ValueError('Unexpected noise-override document structure')
    if type(data['schema']) is not int or data['schema'] != 1:
        raise ValueError('Unsupported noise-override schema')
    if (data['algorithm'], data['dataset']) != (algorithm, dataset):
        raise ValueError('Noise override belongs to a different algorithm or dataset')
    if data['units'] != 'continuous_time_standard_deviation':
        raise ValueError('Noise override must contain continuous-time standard deviations')
    parameters = validate_parameters(data['parameters'])
    receipt = dict(path=str(path.resolve()), sha256=hashlib.sha256(raw).hexdigest(),
                   **document(algorithm, dataset, parameters))
    return parameters, receipt
