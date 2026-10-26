import hashlib
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _reference_source import selected_reference


def test_hash_bound_offset_window_and_prefix(tmp_path):
    def save(name,value):
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(value if isinstance(value,str) else json.dumps(value))
        return {'path':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    parent=save('parent.txt','0\n1\n2\n3\n4\n')
    subset=save('datasets/d/window/times.txt','2\n3\n')
    trajectory=save('ref.tum','0 0 0 0 0 0 0 1\n')
    support=save('support.json',{'valid_intervals':[[0,4]]})
    ref=save('reference.json',dict(dataset='d',sequence='parent',version='v1',limitations=[],orientation_valid=False,
        nominal_geometry=True,variants={'primary':dict(trajectory=trajectory,support=support)}))
    config=dict(schema=1,dataset='d',sequence='window',diagnostic_parent_sequence='parent',diagnostic_only=True,
        subset_times=subset,parent_times=parent,parent_offset=2,reference=ref,variant='primary')
    selector='configs/references/d_window.json'
    save(selector,config)
    assert selected_reference(tmp_path,'d','window')['physical_sequence']=='parent'
    for offset in (1,0,-1,True,2.0,5):
        save(selector,dict(config,parent_offset=offset))
        with pytest.raises(ValueError):selected_reference(tmp_path,'d','window')
    subset=save('datasets/d/window/times.txt','0\n1\n')
    config.update(subset_times=subset);config.pop('parent_offset')
    save(selector,config)
    assert selected_reference(tmp_path,'d','window')['physical_sequence']=='parent'
    save('datasets/d/window/times.txt','0\n2\n')
    with pytest.raises(ValueError,match='evidence changed'):selected_reference(tmp_path,'d','window')
