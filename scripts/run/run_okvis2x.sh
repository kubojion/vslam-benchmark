#!/usr/bin/env bash
# Run OKVIS2-X on a converted sequence (EuRoC-ASL layout under datasets/).
# Usage: scripts/run/run_okvis2x.sh <dataset> <seq> [run_id=1] [run_type=vio]
#
# run_type -> config file + results tree:
#   vo       -> configs/okvis2x/<dataset>_<seq>_vo.yaml
#               -> results-vo/<dataset>/<seq>/okvis2x/run<N>/
#   vio      -> configs/okvis2x/<dataset>_<seq>_vio.yaml
#               -> results-vio/<dataset>/<seq>/okvis2x/run<N>/
#   vio-lc   -> configs/okvis2x/<dataset>_<seq>_vio_lc.yaml
#               -> results-vio-lc/<dataset>/<seq>/okvis2x/run<N>/
#   gnss-vio -> configs/okvis2x/<dataset>_<seq>_gnss_vio.yaml
#               -> results-gnss-vio/<dataset>/<seq>/okvis2x/run<N>/
#
# OKVIS2-X is the successor to OKVIS2 (tightly-coupled GNSS, LiDAR, dense depth).
# Only the sparse estimator app `okvis_app_synchronous` is used here.
#
# Notes:
#  * OKVIS2-X is fundamentally a Visual-INERTIAL estimator. Running with
#    `imu_parameters.use: false` (vo) is accepted by the parameter reader but
#    the front-end is not designed for IMU-less stereo; results may be poor or
#    the run may fail to initialise. Logged as best-effort.
#  * mav0/imu0/data.csv is required for EVERY run type, including vo: the
#    dataset reader opens it unconditionally, regardless of imu_parameters.use.
#  * Unlike OKVIS2, the app takes an explicit output directory as argv[3], so
#    nothing is written into datasets/ and no copy-back is needed.
set -euo pipefail
DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vio}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
resolve_run_type "$RUN_TYPE"

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/okvis2x/run${RUN_ID}"
LOG_GLOBAL="$WS/logs/${DATASET}_${SEQ}_okvis2x_${RUN_TYPE}_run${RUN_ID}.log"

case "$RUN_TYPE" in
    vo)       CFG="$WS/configs/okvis2x/${DATASET}_${SEQ}_vo.yaml"       ;;
    vio)      CFG="$WS/configs/okvis2x/${DATASET}_${SEQ}_vio.yaml"      ;;
    vio-lc)   CFG="$WS/configs/okvis2x/${DATASET}_${SEQ}_vio_lc.yaml"   ;;
    gnss-vio) CFG="$WS/configs/okvis2x/${DATASET}_${SEQ}_gnss_vio.yaml" ;;
    *)        echo "[okvis2x] unknown run_type: $RUN_TYPE" >&2; exit 2 ;;
esac
# Parameter sweeps: point at an alternative config without touching the
# run-type -> file mapping. Pair it with a distinct run_id so the sweep lands in
# its own run<N>/ dir, e.g.
#   OKVIS2X_CONFIG=configs/okvis2x/sweeps/foo.yaml \
#     bash scripts/run/run_okvis2x.sh rosariov2 sequence1 9002 vio
if [[ -n "${OKVIS2X_CONFIG:-}" ]]; then
    CFG="$OKVIS2X_CONFIG"
    [[ "$CFG" = /* ]] || CFG="$WS/$CFG"
    echo "[okvis2x] config override: $CFG"
fi
[[ -f "$CFG" ]] || { echo "[okvis2x] missing config: $CFG" >&2; exit 2; }

# OKMODE mirrors how the app names its own output files, and the app derives
# those names from the *config*, not from our run_type: "slam" when
# estimator_parameters.do_loop_closures is true (else "vio"), plus a "-calib"
# suffix when camera_parameters.online_calibration.do_extrinsics is true.
# Read it back from the config so an overridden config can't desync the names.
if grep -qE '^\s*do_loop_closures:\s*true' "$CFG"; then OKMODE=slam; else OKMODE=vio; fi
if grep -qE '^\s*do_extrinsics:\s*true' "$CFG"; then OKMODE="${OKMODE}-calib"; fi
[[ -d "$SEQ_DIR/mav0/cam0/data" && -d "$SEQ_DIR/mav0/cam1/data" ]] \
    || { echo "[okvis2x] missing $SEQ_DIR/mav0/cam{0,1}/data" >&2; exit 2; }
[[ -f "$SEQ_DIR/mav0/imu0/data.csv" ]] \
    || { echo "[okvis2x] missing IMU $SEQ_DIR/mav0/imu0/data.csv" >&2;
         echo "[okvis2x] hint: python3 scripts/data/imu_to_euroc.py $SEQ_DIR" >&2;
         exit 2; }

APP="$WS/src/okvis2x/build/okvis_app_synchronous"
[[ -x "$APP" ]] || { echo "[okvis2x] missing $APP — run scripts/build/build_okvis2x.sh first" >&2; exit 2; }
# The app loads the DBoW2 vocabulary from its own directory and exits if absent.
[[ -f "$WS/src/okvis2x/build/small_voc.yml.gz" ]] \
    || { echo "[okvis2x] missing small_voc.yml.gz next to $APP — re-run scripts/build/build_okvis2x.sh" >&2; exit 2; }

# GNSS: the geodetic reader expects mav0/gps0/data_raw.csv.
if [[ "$RUN_TYPE" == "gnss-vio" ]]; then
    if [[ ! -f "$SEQ_DIR/mav0/gps0/data_raw.csv" ]]; then
        [[ -f "$SEQ_DIR/gps.csv" ]] \
            || { echo "[okvis2x] missing $SEQ_DIR/gps.csv (needed for gnss-vio)" >&2; exit 2; }
        echo "[okvis2x] generating mav0/gps0/data_raw.csv from gps.csv ..."
        python3 "$WS/scripts/data/gps_to_okvis2x.py" "$SEQ_DIR"
    fi
fi

mkdir -p "$OUT_DIR" "$WS/logs"
echo "[okvis2x] $DATASET/$SEQ type=${RUN_TYPE} run=${RUN_ID} -> $OUT_DIR" | tee "$LOG_GLOBAL"

# ── Generate EuRoC data.csv manifests if missing ─────────────────────────────
# OKVIS2-X's DatasetReader reads the image list from mav0/cam<N>/data.csv and
# aborts ("no images found for camera N") if it is absent -- it does NOT fall
# back to listing the data/ directory. Same manifest run_basalt.sh generates.
python3 -c "
import glob, os, sys

seq_dir = '$SEQ_DIR'
for cam in ['cam0', 'cam1']:
    data_dir = f'{seq_dir}/mav0/{cam}/data'
    csv_path = f'{seq_dir}/mav0/{cam}/data.csv'
    if os.path.exists(csv_path):
        n = sum(1 for _ in open(csv_path)) - 1
        print(f'[okvis2x] {cam}/data.csv already has {n} entries', flush=True)
        continue
    # Deduplicate by timestamp stem: the zed2i tree carries both <ts>.jpg and a
    # <ts>.png symlink to it, so a naive png+jpg glob lists every frame twice.
    by_stem = {}
    for ext in ('png', 'jpg'):          # png wins when both exist (same image)
        for img in glob.glob(f'{data_dir}/*.{ext}'):
            by_stem.setdefault(os.path.splitext(os.path.basename(img))[0], os.path.basename(img))
    if not by_stem:
        print(f'[okvis2x] ERROR: no images found in {data_dir}', file=sys.stderr)
        sys.exit(1)
    with open(csv_path, 'w') as f:
        f.write('#timestamp [ns],filename\n')
        for ts in sorted(by_stem, key=int):
            f.write(f'{ts},{by_stem[ts]}\n')
    print(f'[okvis2x] wrote {cam}/data.csv ({len(by_stem)} entries)', flush=True)
" 2>&1 | tee -a "$LOG_GLOBAL"

# Resource monitor (matches the other run_*.sh wrappers)
python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

# The configs disable every display, so no window should ever open. Guard anyway:
# OpenCV highgui can still initialise a backend on some builds.
RUN_PREFIX=()
if [[ -z "${DISPLAY:-}" ]]; then
    if command -v xvfb-run >/dev/null; then
        RUN_PREFIX=(xvfb-run -a -s "-screen 0 1280x720x24")
    else
        export QT_QPA_PLATFORM=offscreen
        echo "[okvis2x] no DISPLAY and xvfb-run missing; setting QT_QPA_PLATFORM=offscreen" | tee -a "$LOG_GLOBAL"
    fi
fi

# argv: <config> <dataset-folder> <output-dir>. The dataset folder is the one
# holding cam0/ imu0/ (gps0/) directly -- i.e. mav0/, not the sequence root.
#
# Run from $OUT_DIR: besides the trajectory CSVs (which honour the output-dir
# argument), the app also drops debug images into its *working directory* --
# ViSlamBackend.cpp does cv::imwrite("fullBa.png") after a final BA, and
# okvis_app_synchronous writes okvis2_final_ba.png. Without the cd those land
# in whatever directory the runner was invoked from, i.e. the repo root.
START=$(date +%s.%N)
( cd "$OUT_DIR" && "${RUN_PREFIX[@]}" "$APP" "$CFG" "$SEQ_DIR/mav0" "$OUT_DIR" ) 2>&1 | \
  python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}')
    sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG_GLOBAL" || true
END=$(date +%s.%N)

# Which CSV is the run's answer?
#   vo / vio / gnss-vio : the causal (real-time) estimate.
#   vio-lc              : the loop-closed estimate after the final full BA,
#                         falling back to the pre-BA loop-closed one. This is
#                         the SLAM result the vio-lc bucket is meant to measure,
#                         and mirrors AirSLAM's vio-lc using its map_refinement
#                         output rather than its odometry output.
CAUSAL="$OUT_DIR/okvis2-${OKMODE}_trajectory.csv"
FINAL="$OUT_DIR/okvis2-${OKMODE}-final_trajectory.csv"
FINAL_BA="$OUT_DIR/okvis2-${OKMODE}-final-ba_trajectory.csv"

# has_poses: the CSV always carries a header line, so `-s` is not enough --
# a crashed run leaves a header-only file that would otherwise look like success.
has_poses() { [[ -f "$1" ]] && (( $(wc -l < "$1") > 1 )); }

if [[ "$RUN_TYPE" == "vio-lc" ]]; then
    for cand in "$FINAL_BA" "$FINAL" "$CAUSAL"; do
        has_poses "$cand" && { RAW="$cand"; break; }
    done
else
    RAW="$CAUSAL"
fi
if ! has_poses "${RAW:-}"; then
    echo "[okvis2x] ERROR: no poses produced in $OUT_DIR — run failed" | tee -a "$LOG_GLOBAL"
    echo "[okvis2x] check $OUT_DIR/run_log.txt for the abort reason" | tee -a "$LOG_GLOBAL"
    exit 1
fi
echo "[okvis2x] trajectory source: $(basename "$RAW")" | tee -a "$LOG_GLOBAL"

# Convert the OKVIS2-X CSV (ns timestamp, comma-separated; cols 0-7 are
# timestamp,px,py,pz,qx,qy,qz,qw followed by velocity + biases) into TUM:
#   timestamp_s tx ty tz qx qy qz qw
python3 - "$RAW" "$OUT_DIR/trajectory.txt" <<'PY'
import csv, sys
src, dst = sys.argv[1], sys.argv[2]
n = 0
with open(src) as fin, open(dst, "w") as fout:
    rd = csv.reader(fin)
    next(rd, None)   # skip header
    for row in rd:
        if not row:
            continue
        t_ns = int(row[0].strip())
        vals = [row[i].strip() for i in range(1, 8)]   # px py pz qx qy qz qw
        fout.write(f"{t_ns/1e9:.9f} " + " ".join(vals) + "\n")
        n += 1
print(f"[okvis2x] wrote {dst} ({n} poses)")
PY

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt")
python3 -c "
import json
print(json.dumps({
    'algo':'okvis2x','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
    'run_type':'$RUN_TYPE',
    'duration_s':$DUR,'frames':$NFR,
    'fps':$NFR/$DUR if $DUR>0 else 0
}))
" > "$OUT_DIR/run_meta.json"
echo "[okvis2x] run ${RUN_ID} done in ${DUR}s, ${NFR} poses"
