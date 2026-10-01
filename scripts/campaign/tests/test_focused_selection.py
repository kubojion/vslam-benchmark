import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_repair_inventory import selected_attempts, SELECTION


def recipe():
    return {'schema':1,'cells':{f'{mode}/euroc_mav/{seq}/airslam':[4,5,6]
        for mode in ('vio','vio-lc') for seq in ('MH_01_easy','MH_03_medium','MH_05_difficult')}}


def test_corrected_selection_is_fixed_even_before_any_results_exist(tmp_path):
    path=tmp_path/SELECTION;path.parent.mkdir(parents=True)
    path.write_text(json.dumps(recipe()))
    assert selected_attempts(tmp_path)==recipe()['cells']
    assert not (tmp_path/'results').exists()


def test_no_outcome_driven_replacement_or_scope_expansion(tmp_path):
    path=tmp_path/SELECTION;path.parent.mkdir(parents=True)
    for change in ('replacement','scope','omission'):
        value=recipe();key=next(iter(value['cells']))
        if change=='replacement':value['cells'][key]=[4,5,7]
        elif change=='scope':value['cells']['vo/euroc_mav/MH_01_easy/airslam']=[4,5,6]
        else:del value['cells'][key]
        path.write_text(json.dumps(value))
        with pytest.raises(ValueError):selected_attempts(tmp_path)
