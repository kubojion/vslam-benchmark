#!/usr/bin/env python3
"""Freeze the Sielinko (zed2i) IMU Allan analysis into one hash-pinned source record.

Reads the reviewed analysis outputs (default /data/imoroz/PROGRESS/.data/sielinko-imu-analysis) and writes
configs/sensors/sources/zed2i/allan-20261018.json. The record holds:
- engine_off_static.reference: the Rule C input (user decision 2026-10-21), unchanged from recommendation.json;
- engine_on_standstill.selected: the white-noise densities of the labelled engine-on sensitivity profile,
  derived here with the same fit and the same rounding as the engine-off reference.
No trajectory result is read.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'configs/sensors/sources/zed2i/allan-20261018.json'
KEYS = ('gyroscope_noise_density', 'accelerometer_noise_density', 'gyroscope_random_walk', 'accelerometer_random_walk')
FIT = '0.1-1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def round_up(value, digits=2):
    """Round up to `digits` significant figures, the convention of the engine-off reference."""
    scale = 10 ** (math.floor(math.log10(value)) - digits + 1)
    return float(f'{math.ceil(value / scale - 1e-9) * scale:.{digits}g}')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--analysis', type=Path, default=Path('/data/imoroz/PROGRESS/.data/sielinko-imu-analysis'))
    ap.add_argument('--out', type=Path, default=OUT)
    args = ap.parse_args()
    a = args.analysis
    recommendation = json.loads((a/'recommendation.json').read_text())
    summary = json.loads((a/'summary.json').read_text())
    sources = json.loads((a/'source-sha256.json').read_text())

    reference = {k: float(recommendation['recommended_100Hz_reference'][k]) for k in KEYS}
    surrogate = recommendation['white_noise_delivery_surrogate_axis_values']
    walks = recommendation['random_walk_axis_values']
    # The reference must be exactly the documented rounding of its own axis maxima.
    for key, axes in (('gyroscope_noise_density', surrogate[:3]), ('accelerometer_noise_density', surrogate[3:]),
                      ('gyroscope_random_walk', walks[:3]), ('accelerometer_random_walk', walks[3:])):
        if round_up(max(axes)) != reference[key]:
            raise ValueError(f'reference {key} is not the rounded-up axis maximum')

    rpm = {}
    for name in ('engine1450', 'engine1550'):
        fit = summary[name]['fits'][FIT]
        rpm[name] = dict(duration_s=summary[name]['duration_s'], analysis_fs_hz=summary[name]['analysis_fs'],
                         white_noise_axis_values=fit['white_N'], free_slopes=fit['free_slope'])
    gyro = max(max(v['white_noise_axis_values'][:3]) for v in rpm.values())
    accel = max(max(v['white_noise_axis_values'][3:]) for v in rpm.values())
    recordings = {Path(p).name: dict(path=p, **v) for p, v in sources.items()}

    record = dict(
        schema=1,
        dataset='zed2i',
        display_name='Sielinko',
        sensor='ZED 2i internal IMU, /zed/zed_node/imu/data_raw, same mounting as the field sequence (user-confirmed)',
        units={k: recommendation['units'][k] for k in KEYS},
        engine_off_static=dict(
            role='Rule C input (user decision 2026-10-21)',
            recording=recordings['zed2i_imu_allan_20261017_234925.zip'],
            condition=recommendation['source_condition'],
            interval_elapsed_s=recommendation['primary_calibration_interval_elapsed_s'],
            interval_reason=recommendation['interval_reason'],
            white_noise_method=recommendation['white_noise_method'],
            white_noise_axis_values_100Hz=surrogate,
            random_walk_method=recommendation['random_walk_method'],
            random_walk_axis_values=walks,
            reference=reference,
            rounding='largest axis, rounded up to two significant figures',
        ),
        engine_on_standstill=dict(
            role='labelled sensitivity profile only (user decision 2026-10-21); never the Rule C input',
            recordings={rpm_name: recordings[f'zed-imu-engine-{rpm_name[6:]}rpm-' + stamp + '.zip']
                        for rpm_name, stamp in (('engine1450', '20261016_104126'), ('engine1550', '20261016_101120'))},
            condition='engine running at fixed rpm, robot stationary, same mounting',
            white_noise_method=f'same fixed slope -1/2 fit over {FIT} s on the delivered ~100 Hz stream, whole recordings',
            fits=rpm,
            selection='largest axis, then the larger of the two rpm settings, per quantity',
            unrounded=dict(gyroscope_noise_density=gyro, accelerometer_noise_density=accel),
            selected=dict(gyroscope_noise_density=round_up(gyro), accelerometer_noise_density=round_up(accel)),
            rounding='rounded up to two significant figures, as the engine-off reference',
            random_walks='not identifiable from 20-30 min recordings; the profile keeps the engine-off random walks',
            qualification='Engine vibration is periodic (free slopes -0.6 to -0.8, peaks at engine orders), so this '
                          'density is an operating-condition amplitude, not a sensor calibration.',
        ),
        analysis=dict(
            directory=str(a),
            outputs={n: sha(a/n) for n in ('recommendation.json', 'summary.json', 'source-sha256.json')},
            scripts={Path(p).name: v['sha256'] for p, v in sources.items() if p.endswith('.py')},
        ),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + '\n')
    print(args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out)


if __name__ == '__main__':
    main()
