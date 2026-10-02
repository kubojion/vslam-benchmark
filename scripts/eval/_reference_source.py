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
    physical_sequence=sequence
    if config.get('diagnostic_parent_sequence'):
        if config.get('diagnostic_only') is not True:
            raise ValueError('parent reference is only supported for labelled diagnostic subsets')
        physical_sequence=config['diagnostic_parent_sequence']
        subset=bound(config['subset_times']).read_text().splitlines()
        parent=bound(config['parent_times']).read_text().splitlines()
        if not subset or subset!=parent[:len(subset)]:
            raise ValueError('diagnostic times are not an exact parent prefix')
        actual=ws/'datasets'/dataset/sequence/'times.txt'
        if file_evidence(actual,ws)['sha256']!=config['subset_times']['sha256']:
            raise ValueError('diagnostic time identity mismatch')
    document=json.loads(bound(config['reference']).read_text())
    if document['dataset']!=dataset or document['sequence']!=physical_sequence:
        raise ValueError('reference recording mismatch')
    variant=config['variant'];entry=document['variants'][variant]
    trajectory=bound(entry['trajectory']);support=json.loads(bound(entry['support']).read_text())
    return dict(path=trajectory,evidence=evidence,valid_intervals=support['valid_intervals'],physical_sequence=physical_sequence,
                version=document['version'],variant=variant,limitations=document['limitations'],
                orientation_valid=document['orientation_valid'],nominal_geometry=document['nominal_geometry'])
