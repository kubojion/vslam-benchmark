#!/usr/bin/env bash
# Run Basalt stereo VO / VIO on a sequence.
# Usage: scripts/run/run_basalt.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# run_type selects results tree AND whether IMU is used:
#   vo      -> results-vo/<dataset>/<seq>/basalt/run<N>/         (--use-imu false)
#   vio     -> results-vio/<dataset>/<seq>/basalt/run<N>/        (--use-imu true)
#   vio-lc  -> results-vio-lc/<dataset>/<seq>/basalt/run<N>/     (--use-imu true)
#               (Basalt has no LC; vio-lc is logged but treated like vio)
#
# Outputs:
#   trajectory.txt  - TUM format (timestamp_s tx ty tz qx qy qz qw)
#   run_log.txt     - timestamped console output
#   resources.csv   - CPU+RAM sampled every 1 s
#   run_meta.json   - frames, duration, fps
#
# Dependencies:
#   basalt_vio must be on PATH (source ~/.basalt/env or add ~/.local/bin to PATH)
#   configs/basalt/<dataset>_calib.json  - stereo calibration (pinhole, rectified)
#   configs/basalt/vo_config.json        - VIO optimisation config
set -euo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"
SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/basalt/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_basalt_${RUN_TYPE}_run${RUN_ID}.log"
CALIB="$WS/configs/basalt/${DATASET}_calib.json"
VO_CFG="$WS/configs/basalt/vo_config.json"

if [[ "$RUN_TYPE" == "vio-lc" ]]; then
    echo "[basalt] WARNING: Basalt has no built-in loop closure; running plain VIO" >&2
fi

mkdir -p "$OUT_DIR" "$WS/logs"

# ── PATH: source Basalt env to ensure basalt_vio is available ────────────────
if [[ -f "$HOME/.basalt/env" ]]; then
    # shellcheck source=/dev/null
    source "$HOME/.basalt/env"
fi
if ! command -v basalt_vio &>/dev/null; then
    echo "[basalt] ERROR: basalt_vio not found. Run: curl -LsSf https://gitlab.com/VladyslavUsenko/basalt/-/raw/master/scripts/install.sh | sh" >&2
    exit 1
fi

echo "[basalt] $DATASET/$SEQ run=${RUN_ID} -> $OUT_DIR" | tee "$LOG_GLOBAL"

# ── Generate EuRoC data.csv manifests if missing ─────────────────────────────
python3 -c "
import glob, os, sys

seq_dir = '$SEQ_DIR'
for cam in ['cam0', 'cam1']:
    data_dir = f'{seq_dir}/mav0/{cam}/data'
    csv_path = f'{seq_dir}/mav0/{cam}/data.csv'
    if os.path.exists(csv_path):
        n = sum(1 for _ in open(csv_path)) - 1
        print(f'[basalt] {cam}/data.csv already has {n} entries', flush=True)
        continue
    imgs = sorted(glob.glob(f'{data_dir}/*.png') + glob.glob(f'{data_dir}/*.jpg'))
    if not imgs:
        print(f'[basalt] ERROR: no images found in {data_dir}', file=sys.stderr)
        sys.exit(1)
    with open(csv_path, 'w') as f:
        f.write('#timestamp [ns],filename\n')
        for img in imgs:
            ts = os.path.splitext(os.path.basename(img))[0]
            f.write(f'{ts},{ts}.png\n')
    print(f'[basalt] wrote {cam}/data.csv ({len(imgs)} entries)', flush=True)
" 2>&1 | tee -a "$LOG_GLOBAL"

# ── Resource monitor: CPU + RAM sampled every 1 s ────────────────────────────
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

# ── Run Basalt VIO (vision-only, no IMU) ─────────────────────────────────────
# basalt_vio saves trajectory.txt in the CWD; cd to $OUT_DIR so it lands there.
cd "$OUT_DIR"

START=$(date +%s.%N)
basalt_vio \
    --show-gui 0 \
    --dataset-path "$SEQ_DIR" \
    --dataset-type euroc \
    --cam-calib "$CALIB" \
    --config-path "$VO_CFG" \
    --use-imu "$USE_IMU" \
    --save-trajectory tum \
    --num-threads 0 > "$OUT_DIR/run_log.txt" 2>&1 || true
# Mirror run_log.txt to the global log
cat "$OUT_DIR/run_log.txt" >> "$LOG_GLOBAL" || true
END=$(date +%s.%N)

# ── Verify output ─────────────────────────────────────────────────────────────
# basalt_vio writes trajectory.txt in TUM format (timestamp in seconds).
# Timestamps are already in seconds - no conversion needed.
if [[ ! -f "$OUT_DIR/trajectory.txt" ]]; then
    echo "[basalt] ERROR: trajectory.txt not found - Basalt likely failed" | tee -a "$LOG_GLOBAL"
    exit 1
fi

NFR=$(grep -vc '^#' "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
DUR=$(python3 -c "print($END-$START)")
python3 -c "
import json
print(json.dumps({
    'algo':     'basalt',
    'dataset':  '$DATASET',
    'seq':      '$SEQ',
    'run_id':   $RUN_ID,
    'duration_s': $DUR,
    'frames':   $NFR,
    'fps':      $NFR/$DUR if $DUR > 0 else 0,
}))
" > "$OUT_DIR/run_meta.json"

echo "[basalt] run ${RUN_ID} done in ${DUR}s, ${NFR} frames"
