#!/usr/bin/env bash
# Build the untracked private state of this worktree. Live paths are only ever read or linked.
set -euo pipefail
L=/data/imoroz/vslam-benchmark
W=$(cd "$(dirname "$0")/.." && pwd); cd "$W"
mkdir -p results logs datasets/.timing-imu
for s in okvis2 okvis2x ORB_SLAM3 cuvslam mast3r_fusion svo_pro open_vins voxel_svio airslam; do
    [[ -L src/$s ]] && continue
    rmdir "src/$s"; ln -s "$L/src/$s" "src/$s"
    git update-index --skip-worktree "src/$s"
done
for e in gtsam-mast3r-fusion gtsam-mast3r-fusion.commit mast3r-fusion-checkpoints mast3r-fusion-checkpoints.sha256 wheels; do
    [[ -e third_party/$e ]] || ln -s "$L/third_party/$e" "third_party/$e"
done
for p in citrusfarm/seq04 citrusfarm/seq07 zed2i/field1_110426_full_10fps_q90; do
    mkdir -p "datasets/$p/mav0"
    for e in "$L/datasets/$p"/*; do b=$(basename "$e"); [[ $b == mav0 || -e datasets/$p/$b || -L datasets/$p/$b ]] || ln -s "$e" "datasets/$p/$b"; done
    for e in "$L/datasets/$p/mav0"/*; do b=$(basename "$e"); [[ -d $e && $b != imu0 && ! -e datasets/$p/mav0/$b ]] && ln -s "$e" "datasets/$p/mav0/$b"; done
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
[[ -e results/zed-preparation-20261002/orb-build ]] || ln -s "$L/results/zed-preparation-20261002/orb-build" results/zed-preparation-20261002/orb-build
mounts=(-v "$W/configs:/benchmark_configs:ro" -v "$W/scripts:/benchmark_scripts:ro" -v "$W/datasets:/datasets:ro" -v "$W/results:/results" -v "$L/datasets:$L/datasets:ro")
docker inspect vslam_corrected_voxel_20261031 >/dev/null 2>&1 || docker run -d --name vslam_corrected_voxel_20261031 --cpuset-cpus 6-7 \
    --memory 68719476736 --memory-swap 68719476736 "${mounts[@]}" -v "$L/src/voxel_svio:/root/catkin_ws/src/voxel_svio:ro" \
    vslam-noise-search-voxel:20261009 /bin/bash -c 'exec tail -f /dev/null'
docker inspect vslam_corrected_air_20261031 >/dev/null 2>&1 || docker run -d --name vslam_corrected_air_20261031 --gpus all --cpuset-cpus 16-23 \
    --memory 53687091200 --memory-swap 53687091200 "${mounts[@]}" -v "$L/src/airslam:/root/catkin_ws/src/air_slam:ro" \
    vslam-noise-search-airslam:20261009 /bin/bash -c 'exec tail -f /dev/null'
