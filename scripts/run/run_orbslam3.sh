#!/usr/bin/env bash
# Run ORB-SLAM3 on a converted sequence (cam0/, cam1/, times.txt).
# Usage: scripts/run/run_orbslam3.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# run_type selects binary + config + results tree:
#   vo      -> stereo_euroc          + <dataset>_stereo.yaml          (LC off)
#              -> results-vo/<dataset>/<seq>/orbslam3/run<N>/
#   vio     -> stereo_inertial_euroc + <dataset>_stereo_inertial.yaml (LC off)
#              -> results-vio/<dataset>/<seq>/orbslam3/run<N>/
#   vio-lc  -> stereo_inertial_euroc + <dataset>_stereo_inertial_lc.yaml (LC on)
#              -> results-vio-lc/<dataset>/<seq>/orbslam3/run<N>/
#
# vio / vio-lc require:
#   - <dataset_seq>/mav0/cam0/data, /mav0/cam1/data, /mav0/imu0/data.csv  (EuRoC)
#   - <dataset_seq>/times.txt                                              (ns)
# The stereo_inertial_euroc binary reads the IMU CSV from mav0/imu0/data.csv.
set -euo pipefail
DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/orbslam3/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_orbslam3_${RUN_TYPE}_run${RUN_ID}.log"

case "$RUN_TYPE" in
    vo)
        BIN=./Examples/Stereo/stereo_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo.yaml"
        ;;
    vio)
        BIN=./Examples/Stereo-Inertial/stereo_inertial_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo_inertial.yaml"
        ;;
    vio-lc)
        BIN=./Examples/Stereo-Inertial/stereo_inertial_euroc
        CFG="$WS/configs/orbslam3/${DATASET}_stereo_inertial_lc.yaml"
        ;;
    *)
        echo "[orbslam3] unknown run_type: $RUN_TYPE (expected vo|vio|vio-lc)" >&2
        exit 2
        ;;
esac
BIN_PATH="${BIN#./}"
mkdir -p "$OUT_DIR" "$WS/logs"
: > "$OUT_DIR/run_log.txt"

if [[ ! -d "$SEQ_DIR" ]]; then
    echo "[orbslam3] ERROR: sequence directory not found: $SEQ_DIR" >&2
    exit 1
fi
if [[ ! -f "$SEQ_DIR/times.txt" ]]; then
    echo "[orbslam3] ERROR: times.txt not found: $SEQ_DIR/times.txt" >&2
    exit 1
fi
if [[ "$RUN_TYPE" =~ vio && ! -f "$SEQ_DIR/mav0/imu0/data.csv" ]]; then
    echo "[orbslam3] missing IMU: $SEQ_DIR/mav0/imu0/data.csv" >&2
    echo "[orbslam3] hint: python3 scripts/data/imu_to_euroc.py $SEQ_DIR" >&2
    exit 2
fi

if [[ -n "${ORB_CONFIG:-}" ]]; then
    CFG="$ORB_CONFIG"
else
    CFG=""
    candidates=(
        "$WS/configs/orbslam3/${DATASET}_${SEQ}.yaml"
        "$WS/configs/orbslam3/${SEQ}.yaml"
    )
    case "$RUN_TYPE" in
        vo)
            candidates+=("$WS/configs/orbslam3/${DATASET}_stereo.yaml")
            ;;
        vio)
            candidates+=("$WS/configs/orbslam3/${DATASET}_stereo_inertial.yaml")
            ;;
        vio-lc)
            candidates+=("$WS/configs/orbslam3/${DATASET}_stereo_inertial_lc.yaml")
            ;;
    esac
    for candidate in \
        "${candidates[@]}"
    do
        if [[ -f "$candidate" ]]; then
            CFG="$candidate"
            break
        fi
    done
fi
if [[ -z "$CFG" || ! -f "$CFG" ]]; then
    echo "[orbslam3] ERROR: no ORB-SLAM3 config found for $DATASET/$SEQ" >&2
    echo "[orbslam3] Tried sequence-specific configs plus the ${RUN_TYPE} dataset default" >&2
    echo "[orbslam3] Or set ORB_CONFIG=/path/to/config.yaml" >&2
    exit 1
fi

ORB_DIR=${ORB_SLAM3_DIR:-}
if [[ -z "$ORB_DIR" ]]; then
    for candidate in \
        "$WS/src/ORB_SLAM3" \
        "/home/iman/slam_tests/orb_slam_test/ORB-SLAM3-ROS2-Docker/ORB_SLAM3"
    do
        if [[ -x "$candidate/$BIN_PATH" ]]; then
            ORB_DIR="$candidate"
            break
        fi
    done
fi
if [[ -z "$ORB_DIR" || ! -x "$ORB_DIR/$BIN_PATH" ]]; then
    echo "[orbslam3] ERROR: ORB-SLAM3 executable not found: $BIN_PATH" >&2
    echo "[orbslam3] Set ORB_SLAM3_DIR=/path/to/ORB_SLAM3 or build src/ORB_SLAM3." >&2
    exit 1
fi

CFG_REL=$(realpath --relative-to="$WS" "$CFG" 2>/dev/null || true)
SEQ_REL=$(realpath --relative-to="$WS" "$SEQ_DIR" 2>/dev/null || true)

echo "[orbslam3] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG_GLOBAL"
echo "[orbslam3] binary=$BIN  cfg=$CFG" | tee -a "$LOG_GLOBAL"
echo "[orbslam3] ORB_SLAM3_DIR: $ORB_DIR" | tee -a "$LOG_GLOBAL"

# Resource monitor: GPU + CPU + RAM sampled every 1 s
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

START=$(date +%s.%N)
# ORB-SLAM3 may crash in Pangolin destructor after saving trajectories; that is
# harmless — we only care that the trajectory file was written before exit.
# Pipe through a Python timestamper so each log line gets a relative offset (s).
RUN_NAME="${DATASET}_${SEQ}_orbslam3"
timestamp_log() {
    python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}')
    sys.stdout.flush()
"
}

if [[ "${ORB_USE_DOCKER:-auto}" != "0" ]] && docker image inspect "${ORB_DOCKER_IMAGE:-orb-slam3-humble:22.04}" >/dev/null 2>&1; then
    if [[ -z "$CFG_REL" ]]; then
        echo "[orbslam3] ERROR: Docker mode requires the config inside $WS" >&2
        exit 1
    fi
    # The sequence dir may be a symlink whose real path is OUTSIDE $WS (e.g.
    # datasets/hortimulti/strawberry03 -> /home/.../data/horti/Strawberry-03).
    # realpath then yields ../data/... which, as /bench/../data/... inside the
    # container, escapes the /bench mount and is invisible -> ORB-SLAM3 hangs on
    # an empty sequence. Detect that and bind-mount the real path at /seq instead.
    SEQ_REAL=$(realpath "$SEQ_DIR")
    SEQ_MOUNT=()
    if [[ -n "$SEQ_REL" && "$SEQ_REL" != ../* ]]; then
        SEQ_IN="/bench/$SEQ_REL"                 # stays inside /bench
    else
        SEQ_IN="/seq"                            # external symlink: mount it
        SEQ_MOUNT=(-v "$SEQ_REAL:/seq:ro")
        echo "[orbslam3] sequence resolves outside \$WS ($SEQ_REAL); bind-mounting at /seq" | tee -a "$LOG_GLOBAL"
    fi
    docker run --rm \
        -v "$ORB_DIR:/orb" \
        -v "$WS:/bench" \
        -v "$OUT_DIR:/out" \
        "${SEQ_MOUNT[@]}" \
        -w /out \
        "${ORB_DOCKER_IMAGE:-orb-slam3-humble:22.04}" \
        bash -lc "export LD_LIBRARY_PATH=/orb/lib:/orb/Thirdparty/DBoW2/lib:/orb/Thirdparty/g2o/lib:\$LD_LIBRARY_PATH; /orb/$BIN_PATH /orb/Vocabulary/ORBvoc.txt /bench/$CFG_REL $SEQ_IN $SEQ_IN/times.txt $RUN_NAME" 2>&1 | \
      timestamp_log | tee -a "$OUT_DIR/run_log.txt" "$LOG_GLOBAL" || true
    docker run --rm -v "$OUT_DIR:/out" alpine:latest sh -lc 'chown -R 1000:1000 /out' >/dev/null 2>&1 || true
else
    (
        cd "$OUT_DIR"
        export LD_LIBRARY_PATH="$ORB_DIR/lib:$ORB_DIR/Thirdparty/DBoW2/lib:$ORB_DIR/Thirdparty/g2o/lib:${LD_LIBRARY_PATH:-}"
        "$ORB_DIR/$BIN_PATH" \
            "$ORB_DIR/Vocabulary/ORBvoc.txt" \
            "$CFG" \
            "$SEQ_DIR" \
            "$SEQ_DIR/times.txt" \
            "$RUN_NAME"
    ) 2>&1 | timestamp_log | tee -a "$OUT_DIR/run_log.txt" "$LOG_GLOBAL" || true
fi
END=$(date +%s.%N)

TRAJ_SRC="$OUT_DIR/f_${RUN_NAME}.txt"
if [[ ! -f "$TRAJ_SRC" ]]; then
    echo "[orbslam3] ERROR: trajectory file not found — SLAM likely failed" | tee -a "$LOG_GLOBAL"
    exit 1
fi
mv "$TRAJ_SRC" "$OUT_DIR/trajectory.txt"
mv "$OUT_DIR/kf_${RUN_NAME}.txt" "$OUT_DIR/keyframes.txt" 2>/dev/null || true
mv "$OUT_DIR/map_points_${RUN_NAME}.ply" "$OUT_DIR/map_points.ply" 2>/dev/null || true

# stereo_euroc emits nanosecond timestamps; evo and gt_tum.txt use seconds.
# Convert in-place: divide column 1 by 1e9, preserve full 9-decimal precision.
awk '{printf "%.9f %s %s %s %s %s %s %s\n",$1/1e9,$2,$3,$4,$5,$6,$7,$8}' \
    "$OUT_DIR/trajectory.txt" > "$OUT_DIR/trajectory_s.txt"
mv "$OUT_DIR/trajectory_s.txt" "$OUT_DIR/trajectory.txt"
[[ -f "$OUT_DIR/keyframes.txt" ]] && \
awk '{printf "%.9f %s %s %s %s %s %s %s\n",$1/1e9,$2,$3,$4,$5,$6,$7,$8}' \
    "$OUT_DIR/keyframes.txt" > "$OUT_DIR/keyframes_s.txt" && \
mv "$OUT_DIR/keyframes_s.txt" "$OUT_DIR/keyframes.txt"

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 -c "
import json
print(json.dumps({
    'algo':'orbslam3','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,    'run_type':'$RUN_TYPE',    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0
}))
" > "$OUT_DIR/run_meta.json"
echo "[orbslam3] run ${RUN_ID} done in ${DUR}s, ${NFR} frames"
