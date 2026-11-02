#!/usr/bin/env bash
# Build the untracked private state of this worktree. Live paths are only ever read or linked.
#
#   setup_private.sh files        links, CitrusFarm corrected IMU, unchanged IMU links, .venv, clips. No Docker.
#   setup_private.sh containers   creates the two private containers (docker run; starts no estimator).
#
# Lanes: Voxel-SVIO on 8-11, AirSLAM on 16-23 with the GPU. Memory caps as Rule C, no swap.
set -euo pipefail
L=/data/imoroz/vslam-benchmark
W=$(cd "$(dirname "$0")/.." && pwd); cd "$W"
[[ "$W" != "$L" ]] || { echo 'run from the search worktree' >&2; exit 2; }
PY=/data/imoroz/conda/envs/macvo/bin/python
SEARCH_VENV=/data/imoroz/vslam-sielinko-search-20261022/.venv/lib/python3.10/site-packages

files() {
    mkdir -p results logs datasets/.timing-imu
    for s in okvis2 okvis2x ORB_SLAM3 cuvslam mast3r_fusion svo_pro open_vins voxel_svio airslam; do
        [[ -L src/$s ]] && continue
        rmdir "src/$s"; ln -s "$L/src/$s" "src/$s"
        git update-index --skip-worktree "src/$s"
    done
    for e in gtsam-mast3r-fusion gtsam-mast3r-fusion.commit mast3r-fusion-checkpoints mast3r-fusion-checkpoints.sha256 wheels; do
        [[ -e third_party/$e ]] || ln -s "$L/third_party/$e" "third_party/$e"
    done
    for p in citrusfarm/seq04 citrusfarm/seq07 hortimulti/strawberry02 hortimulti/strawberry03 rosariov2/sequence1 rosariov2/sequence5; do
        mkdir -p "datasets/$p/mav0"
        for e in "$L/datasets/$p"/*; do b=$(basename "$e"); [[ $b == mav0 || -e datasets/$p/$b || -L datasets/$p/$b ]] || ln -s "$e" "datasets/$p/$b"; done
        for e in "$L/datasets/$p/mav0"/*; do b=$(basename "$e"); if [[ -d $e && $b != imu0 && ! -e datasets/$p/mav0/$b ]]; then ln -s "$e" "datasets/$p/mav0/$b"; fi; done
    done
    # CitrusFarm: the corrected IMU, regenerated from the live file and checked against the plan's hashes.
    for row in seq04:9ec219ee1fa598ede605cb5c55b5dc98f57a47512c64b63dc8c09598d7625336 seq07:1629baf2b4af799cd9ab652c60bc97edb1f385f96690fe50e24b1ce8d7247f65; do
        s=${row%%:*}; want=${row##*:}
        python3 -B scripts/setup/generate_imu_timing.py --dataset citrusfarm --sequence "$s"
        have=$(sha256sum "datasets/.timing-imu/citrusfarm__$s/corrected/data.csv" | cut -d' ' -f1)
        [[ "$have" == "$want" ]] || { echo "corrected IMU hash differs: $s" >&2; exit 2; }
        [[ -L datasets/citrusfarm/$s/mav0/imu0 ]] || ln -s "../../../.timing-imu/citrusfarm__$s/corrected" "datasets/citrusfarm/$s/mav0/imu0"
    done
    # HortiMulti and Rosario: the authors' values, so the live IMU unchanged.
    for p in hortimulti/strawberry02 hortimulti/strawberry03 rosariov2/sequence1 rosariov2/sequence5; do
        [[ -L datasets/$p/mav0/imu0 ]] || ln -s "$L/datasets/$p/mav0/imu0" "datasets/$p/mav0/imu0"
    done
    python3 -B - "$L" "$W" <<'P'
import json,os,shutil,sys
L,W=sys.argv[1:]
wanted=['results/acceptance-20261001/evidence.json']
wanted+=[r['path'] for r in json.load(open(W+'/docs/campaigns/paper-acceptance-20261001.json')).get('supporting_evidence',[])]
for p in wanted:
    if p.startswith('results/') and os.path.isfile(f'{L}/{p}') and not os.path.exists(f'{W}/{p}'):
        os.makedirs(os.path.dirname(f'{W}/{p}'),exist_ok=True); shutil.copy2(f'{L}/{p}',f'{W}/{p}')
P
    mkdir -p results/zed-preparation-20261002
    [[ -e results/zed-preparation-20261002/orb-build ]] || ln -s "$L/results/zed-preparation-20261002/orb-build" results/zed-preparation-20261002/orb-build
    # Optuna: a private view of the search's interpreter. Nothing goes into any shared environment.
    if ! .venv/bin/python -c 'import optuna' 2>/dev/null; then
        "$PY" -m venv --system-site-packages --without-pip .venv
        cp -a "$SEARCH_VENV"/{alembic,colorlog,greenlet,mako,optuna,sqlalchemy}* .venv/lib/python3.10/site-packages/
    fi
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B scripts/analysis/prepare_timing_search.py views
}

containers() {
    mounts=(-v "$W/configs:/benchmark_configs:ro" -v "$W/scripts:/benchmark_scripts:ro" -v "$W/datasets:/datasets:ro" -v "$W/results:/results" -v "$L/datasets:$L/datasets:ro")
    docker inspect vslam_search_voxel_20261031 >/dev/null 2>&1 || docker run -d --name vslam_search_voxel_20261031 --cpuset-cpus 8-11 \
        --memory 68719476736 --memory-swap 68719476736 "${mounts[@]}" -v "$L/src/voxel_svio:/root/catkin_ws/src/voxel_svio:ro" \
        vslam-noise-search-voxel:20261009 /bin/bash -c 'exec tail -f /dev/null'
    docker inspect vslam_search_air_20261031 >/dev/null 2>&1 || docker run -d --name vslam_search_air_20261031 --gpus all --cpuset-cpus 16-23 \
        --memory 53687091200 --memory-swap 53687091200 "${mounts[@]}" -v "$L/src/airslam:/root/catkin_ws/src/air_slam:ro" \
        vslam-noise-search-airslam:20261009 /bin/bash -c 'exec tail -f /dev/null'
}

case "${1:-}" in
    files) files ;;
    containers) containers ;;
    *) echo 'usage: setup_private.sh files|containers' >&2; exit 2 ;;
esac
