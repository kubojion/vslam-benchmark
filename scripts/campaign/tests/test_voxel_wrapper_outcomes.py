"""Exercise wrapper completion branches without Docker, data playback or estimation."""
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.mark.parametrize('node_exit,player_exit,saved,expected', [
    (134, 0, True, 134), (134, 0, False, 134),
    (0, 7, True, 7), (0, 0, False, 1), (0, 0, True, 0)])
def test_native_failure_cannot_be_hidden_by_trajectory(tmp_path, node_exit, player_exit, saved, expected):
    root = Path(__file__).resolve().parents[3]
    scripts = tmp_path/'scripts/run'; scripts.mkdir(parents=True)
    shutil.copy2(root/'scripts/run/run_voxel_svio.sh', scripts/'run_voxel_svio.sh')
    shutil.copy2(root/'scripts/run/_rosario_profile.sh', scripts/'_rosario_profile.sh')
    (tmp_path/'configs/voxel_svio').mkdir(parents=True)
    (tmp_path/'configs/voxel_svio/test.yaml').write_text('timeshift_cam_imu_left: 0.0\n')
    for name in ('cam0/data','cam1/data','imu0'):
        (tmp_path/'datasets/test/seq/mav0'/name).mkdir(parents=True)
    (tmp_path/'datasets/test/seq/mav0/imu0/data.csv').touch()
    (tmp_path/'scripts/_paths.sh').write_text('''
canonicalize_dataset() { :; }
resolve_run_type() { RESULTS_ROOT="$WS/results/$1"; }
prepare_fresh_run_dir() { mkdir -p "$1"; }
prepare_resource_window() { :; }
mark_resource_start() { :; }
finish_resource_window() { :; }
record_failed_run_meta() { printf '{"exit_code":%s}' "$7" > "$1"; }
enrich_run_meta() { touch "$OUT_DIR/enriched"; }
''')
    (scripts/'_owned_process.sh').write_text('''
owned_require_idle() { :; }
owned_ros1_port() { ROS_MASTER_URI=http://localhost:12345; ROS_PORT=12345; }
owned_stop() { :; }
owned_run() {
    case "$1" in
        node)
            echo native-node-log
            if [[ "$FAKE_SAVED" == 1 ]]; then
                echo '1 0 0 0 0 0 0 1' > "$OUT_DIR/native/pose.txt"
            fi
            return "$FAKE_NODE_EXIT" ;;
        player) return "$FAKE_PLAYER_EXIT" ;;
        *) return 0 ;;
    esac
}
''')
    (scripts/'_resource_monitor.py').write_text('')
    commands = tmp_path/'bin'; commands.mkdir()
    for name, body in [('docker', 'echo voxel_svio'), ('sleep', ':')]:
        path = commands/name; path.write_text('#!/bin/bash\n'+body+'\n'); path.chmod(0o755)
    env = dict(os.environ, PATH=str(commands)+os.pathsep+os.environ['PATH'],
        FAKE_NODE_EXIT=str(node_exit), FAKE_PLAYER_EXIT=str(player_exit), FAKE_SAVED=str(int(saved)))
    result = subprocess.run(['bash', str(scripts/'run_voxel_svio.sh'), 'test', 'seq', '1', 'vio'],
        env=env, capture_output=True, text=True, timeout=10)
    run = tmp_path/'results/vio/test/seq/voxel_svio/run1'
    assert result.returncode == expected, result.stdout+result.stderr
    assert 'native-node-log' in (run/'run_log.txt').read_text()
    assert (run/'trajectory.txt').is_file() == saved
    if expected:
        assert json.loads((run/'run_meta.json').read_text())['exit_code'] == expected
        assert not (run/'enriched').exists()
    else:
        assert (run/'enriched').exists()
