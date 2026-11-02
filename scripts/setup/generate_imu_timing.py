#!/usr/bin/env python3
"""Write corrected copies of mav0/imu0/data.csv into datasets/.timing-imu/ and record their hashes.

t_corrected = t - (a + b (t - t0)), t0 = first IMU stamp, a in ms, b in ms per second. Only stamps change.
The live dataset is read, never edited. Selecting a variant for a sequence is a separate link in the
private dataset view; listing a sequence in the offset file does not apply it.
"""
import argparse, hashlib, json, os
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIVE = Path('/data/imoroz/vslam-benchmark/datasets')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            h.update(chunk)
    return h.hexdigest()


def write(source, target, a_ms, b_ms_per_s):
    """Exact integer stamps: constant shifts must reproduce byte for byte."""
    a = Fraction(Decimal(str(a_ms)))*10**6
    b = Fraction(Decimal(str(b_ms_per_s)))/1000
    tmp = target.with_name('.'+target.name+'.tmp'); t0 = None; last = None; n = 0
    with source.open('rb') as src, tmp.open('wb') as dst:
        for line in src:
            if line.startswith(b'#') or not line.strip():
                dst.write(line); continue
            stamp, sep, rest = line.partition(b',')
            t = int(stamp); t0 = t if t0 is None else t0
            new = t-round(a+b*(t-t0))
            if last is not None and new <= last:
                raise ValueError('stamps must stay strictly increasing')
            dst.write(str(new).encode()+sep+rest); last = new; n += 1
    os.replace(tmp, target)
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--offsets', type=Path, default=REPO/'configs/sensors/imu-time-offsets-20261031.json')
    ap.add_argument('--dataset'); ap.add_argument('--sequence')
    args = ap.parse_args()
    doc = json.loads(args.offsets.read_text())
    for row in doc['sequences']:
        if args.dataset and (row['dataset'], row['sequence']) != (args.dataset, args.sequence):
            continue
        source = (LIVE/row['dataset']/row['sequence']/'mav0/imu0/data.csv').resolve(strict=True)
        folder = REPO/'datasets/.timing-imu'/f"{row['dataset']}__{row['sequence']}"/row['variant']
        folder.mkdir(parents=True, exist_ok=True)
        n = write(source, folder/'data.csv', row['a_ms'], row['b_ms_per_s'])
        sensor = source.parent/'sensor.yaml'
        if sensor.exists() and not (folder/'sensor.yaml').exists():
            (folder/'sensor.yaml').symlink_to(sensor)
        record = dict(row, source=str(source), source_sha256=sha(source), output_sha256=sha(folder/'data.csv'), samples=n)
        (folder/'record.json').write_text(json.dumps(record, indent=1)+'\n')
        print(row['dataset'], row['sequence'], row['variant'], n, record['output_sha256'][:12])


if __name__ == '__main__':
    main()
