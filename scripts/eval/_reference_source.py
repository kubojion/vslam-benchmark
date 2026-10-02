"""Select an explicitly reviewed, hash-bound reference version when configured."""
import json
from pathlib import Path

from _pose_frames import file_evidence


def selected_reference(ws, dataset, sequence):
    ws=Path(ws)
    selector=ws/'configs/references'/f'{dataset}_{sequence}.json'
    if not selector.is_file():return None
    config=json.loads(selector.read_text())
    if config.get('schema')!=1 or config.get('dataset')!=dataset or config.get('sequence')!=sequence:
        raise ValueError('reference selector does not match requested recording')
    evidence=[file_evidence(selector,ws)]
    def bound(item):
        path=ws/item['path'];actual=file_evidence(path,ws)
        if actual['sha256']!=item['sha256']:raise ValueError('reference evidence changed: '+str(path))
        evidence.append(actual);return path
    document=json.loads(bound(config['reference']).read_text())
    if document['dataset']!=dataset or document['sequence']!=sequence:
        raise ValueError('reference recording mismatch')
    variant=config['variant'];entry=document['variants'][variant]
    trajectory=bound(entry['trajectory']);support=json.loads(bound(entry['support']).read_text())
    return dict(path=trajectory,evidence=evidence,valid_intervals=support['valid_intervals'],
                version=document['version'],variant=variant,limitations=document['limitations'],
                orientation_valid=document['orientation_valid'],nominal_geometry=document['nominal_geometry'])
