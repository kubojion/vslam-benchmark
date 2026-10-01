import hashlib
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from configuration_recipe import config_recipe
from test_repair_plan import manifest
from run_future_manifest import validate


def write(root,path,text):
    target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
    return target


def cell(algo,mode):
    return dict(dataset='test',sequence='sequence',algorithm=algo,run_type=mode)


def test_orb_recipe_has_one_effective_lc_key_and_rejects_camera_rate_mismatch(tmp_path):
    write(tmp_path,'scripts/run/run_orbslam3.sh','runner')
    write(tmp_path,'datasets/test/sequence/times.txt','0\n100000000\n200000000\n')
    config=write(tmp_path,'configs/orbslam3/test_stereo_lc.yaml',
                 'Camera.fps: 10\nloopClosing: 0\nSystem.LoopClosing: 0\nSystem.LoopClosing: 0\n')
    recipe=config_recipe(tmp_path,cell('orbslam3','vo-lc'))
    assert not recipe['selection_errors']
    expected=b'Camera.fps: 10\nloopClosing: 1\n'
    assert recipe['planned_effective_inputs'][0]['normalized_sha256']==hashlib.sha256(expected).hexdigest()
    config.write_text('Camera.fps: 15\n')
    assert any('disagrees' in e for e in config_recipe(tmp_path,cell('orbslam3','vo-lc'))['selection_errors'])


def test_okvis_fallback_preserves_every_other_setting_and_missing_config_is_blocked(tmp_path):
    write(tmp_path,'scripts/run/run_okvis2.sh','runner')
    config=write(tmp_path,'configs/okvis2/test_sequence_vio.yaml',
        'estimator_parameters:\n  do_loop_closures: false\n  do_final_ba: false\n')
    recipe=config_recipe(tmp_path,cell('okvis2','vio-lc'))
    expected=config.read_text().replace('do_loop_closures: false','do_loop_closures: true')
    assert recipe['planned_effective_inputs'][0]['normalized_sha256']==hashlib.sha256(expected.encode()).hexdigest()
    assert not recipe['runtime_materialization_verified']
    config.unlink()
    assert config_recipe(tmp_path,cell('okvis2','vio-lc'))['selection_errors']


def test_manifest_rejects_mutated_or_removed_recipe(tmp_path):
    write(tmp_path,'scripts/run/run_rtabmap_gps.sh','embedded calibration')
    write(tmp_path,'configs/rtabmap_gps/benchmark.ini','key=value')
    recipe=config_recipe(tmp_path,cell('rtabmap_gps','gnss-vio'))
    m=manifest();m['configuration_recipe_schema']=1
    for action in m['actions']:action['configuration_recipe']=recipe
    assert validate(tmp_path,m,check_files=False)==[]
    recipe['operations'].append('unrecorded change')
    assert 'configuration recipe digest mismatch' in validate(tmp_path,m,check_files=False)
    del m['actions'][0]['configuration_recipe']
    assert 'action is missing its configuration recipe' in validate(tmp_path,m,check_files=False)
