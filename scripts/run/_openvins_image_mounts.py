#!/usr/bin/env python3
"""Resolve image bytes for read-only Docker binds, including copied prefixes."""
import csv
import json
from pathlib import Path
import sys


def image_mounts(sequence):
    sequence = Path(sequence)
    parents = set()
    counts = {}
    for camera in ('cam0', 'cam1'):
        directory = sequence / 'mav0' / camera
        count = 0
        with (directory / 'data.csv').open() as stream:
            for row in csv.reader(stream):
                if not row or row[0].lstrip().startswith('#'):
                    continue
                image = (directory / 'data' / row[1].strip()).resolve(strict=True)
                if not image.is_file():
                    raise ValueError('Image target is not a regular file: ' + str(image))
                parent = str(image.parent)
                if any(x in parent for x in (':', '\n', '\r')) or image.parent == Path('/'):
                    raise ValueError('Unsupported Docker image-directory path')
                parents.add(parent)
                count += 1
        if count == 0:
            raise ValueError('Empty camera table: ' + camera)
        counts[camera] = count
    return dict(schema=1, policy='Resolved image directories mounted read-only at their absolute paths',
                directories=sorted(parents), frames=counts)


if __name__ == '__main__':
    print(json.dumps(image_mounts(sys.argv[1]), indent=2))
