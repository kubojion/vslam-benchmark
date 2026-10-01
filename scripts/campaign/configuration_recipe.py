"""Read-only identities of the default configurations a future runner selects.

This records selection/materialization, not execution readiness or proof that
an old run used the current files. Embedded ROS parameters are bound to runner
source as well as YAML/INI files. No estimator or container is invoked.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'run'))
from _config_preflight import select_basalt_config, select_orb_config


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def config_recipe(repo, cell):
    repo = Path(repo)
    dataset, sequence, algorithm, mode = [cell[k] for k in ('dataset','sequence','algorithm','run_type')]
    root = repo/'configs'; files = []; effective = []; operations = []; errors = []
    def selected(role, path, transform=None):
        path = Path(path)
        relative = path.relative_to(repo).as_posix()
        if not path.is_file():
            errors.append('missing_selected_input:'+relative); return
        raw = path.read_bytes()
        files.append(dict(role=role, path=relative, sha256=sha(raw)))
        if transform:
            normalized = transform(raw.decode())
            effective.append(dict(role=role, normalized_sha256=sha(normalized.encode()),
                                  substitutions='portable <repo>/<attempt> placeholders; not runtime verification'))
        else:
            effective.append(dict(role=role, normalized_sha256=sha(raw), substitutions='unchanged input bytes'))
    def first(paths):
        return next((p for p in paths if p.is_file()), paths[0])
    def sequence_or_dataset(folder, suffix=''):
        return first([root/folder/f'{dataset}_{sequence}{suffix}.yaml', root/folder/f'{dataset}{suffix}.yaml'])
    try:
        if algorithm == 'orbslam3':
            path = select_orb_config(repo,dataset,sequence,mode)
            def orb(text):
                lines=[line for line in text.splitlines() if not re.match(r'^(loopClosing|System\.LoopClosing):\s*',line)]
                return '\n'.join(lines)+f'\nloopClosing: {int(mode.endswith("lc"))}\n'
            selected('estimator_config',path,orb)
            operations.append('remove both historical LC keys; append one canonical loopClosing integer')
        elif algorithm == 'basalt':
            selected('estimator_config',select_basalt_config(repo,dataset,mode))
            selected('camera_calibration',root/'basalt'/f'{dataset}_calib.json')
        elif algorithm in ('okvis2','okvis2x'):
            path=root/algorithm/f'{dataset}_{sequence}_{mode.replace("-","_")}.yaml'
            transform=None
            if algorithm=='okvis2' and mode=='vio-lc' and not path.is_file():
                path=root/algorithm/f'{dataset}_{sequence}_vio.yaml'
                transform=lambda text: re.sub(r'(?m)^(\s*do_loop_closures:\s*)(true|false)',r'\g<1>true',text)
                operations.append('materialize VIO-LC from VIO by changing only do_loop_closures')
            selected('estimator_config',path,transform)
        elif algorithm == 'airslam':
            tag={'vo':'vo','vo-lc':'vo_lc','vio':'vio','vio-lc':'vio_slam'}[mode]
            if mode=='vio-lc' and not (root/'airslam'/f'{dataset}_{tag}.yaml').is_file(): tag='vio'
            selected('odometry_config',root/'airslam'/f'{dataset}_{tag}.yaml')
            camera_mode='vio' if mode.startswith('vio') else 'vo'
            selected('camera_config',first([root/'airslam'/f'{dataset}_camera_{camera_mode}.yaml',root/'airslam'/f'{dataset}_camera.yaml']))
            if mode.endswith('lc'):
                selected('map_refinement_config',root/'airslam'/f'{dataset}_mr.yaml')
                operations.append('one map-refinement attempt after odometry; preserve failed refinement')
        elif algorithm == 'ov2slam':
            selected('estimator_config',sequence_or_dataset('ov2slam','_'+mode.replace('-','_')))
        elif algorithm in ('voxel_svio','cifasis_gnss_si','vins_fusion_gps'):
            folder='vins_fusion' if algorithm=='vins_fusion_gps' else algorithm
            selected('estimator_config',sequence_or_dataset(folder))
            if algorithm=='vins_fusion_gps':
                for i in (0,1): selected(f'camera{i}_config',root/folder/f'{dataset}_cam{i}.yaml')
            if algorithm=='voxel_svio':operations.append('ROS output_path := <container_attempt>/native')
        elif algorithm in ('openvins','openvins_gps'):
            for role,name in [('estimator_config','estimator_config'),('imu_calibration','kalibr_imu_chain'),('camera_imu_calibration','kalibr_imucam_chain')]:
                selected(role,root/'openvins'/dataset/(name+'.yaml'))
            if algorithm=='openvins_gps':
                selected('ekf_config',root/'robot_loc_openvins/ekf_gps.yaml')
                selected('navsat_config',root/'robot_loc_openvins/navsat.yaml')
                operations.append('static TF, camera calibration and topic arguments are embedded in pinned runner source')
        elif algorithm == 'rtabmap_gps':
            selected('estimator_config',root/'rtabmap_gps/benchmark.ini')
            operations.append('static TF, camera calibration and ROS launch parameters are embedded in pinned runner source')
        elif algorithm == 'dpvo':
            selected('camera_calibration',root/'dpvo'/f'{dataset}.txt')
            selected('algorithm_config',repo/'src/DPVO/config/default.yaml')
            selected('compiled_default_settings_source',repo/'src/DPVO/dpvo/config.py')
            operations.append('stride=1; skip=0; seed=1000+physical_run_id; CLASSIC_LOOP_CLOSURE=False; LOOP_CLOSURE='+str(mode=='vo-lc'))
        elif algorithm == 'macvo':
            selected('odometry_config',repo/'src/MAC-VO/Config/Experiment/MACVO/MACVO_Performant.yaml')
            selected('preprocess_config',repo/'src/MAC-VO/Config/Experiment/Common/Preprocess.yaml')
            selected('dataset_config',root/'macvo'/f'{dataset}_{sequence}.yaml',lambda text:text.replace('__WS__','<repo>'))
            operations.append('override experiment Data using dataset config; viewer off; matmul_precision=medium; resultRoot=<attempt>/native')
        else:
            errors.append('unsupported_recipe_algorithm:'+algorithm)
    except (OSError,ValueError,KeyError) as exc:
        errors.append('config_selection_failed:'+str(exc))
    runner=repo/'scripts/run'/f'run_{algorithm}.sh'
    selected('runner_with_embedded_parameters',runner)
    recipe=dict(schema=1,source_files=files,planned_effective_inputs=effective,operations=operations,
        selection_errors=errors,scope='default source selection and deterministic materialization identity only',
        runtime_materialization_verified=False,
        unresolved=['verify_effective_native_config_after_runtime_materialization',
                    'verify_native_build_source_linkage_and_loaded_runtime_dependency_closure'])
    recipe['sha256']=sha(json.dumps(recipe,sort_keys=True,separators=(',',':')).encode())
    return recipe
