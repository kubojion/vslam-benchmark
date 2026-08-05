#!/usr/bin/env bash
# Run MegaSaM (monocular structure-and-motion) on a sequence.
#
# Usage: scripts/run/run_megasam.sh <dataset> <seq> [run_id=1] [run_type=vo]
#
# MegaSaM is monocular, no IMU, no LC. Only run_type=vo is supported.
#
# Upstream has no single entrypoint: it is a multi-stage pipeline driven by
# example shell scripts with hard-coded paths (tools/evaluate_demo.sh etc.).
# This runner reproduces the three stages needed for a camera trajectory:
#
#   1a. Depth-Anything/run_videos.py          -> relative mono-depth per frame
#   1b. UniDepth/scripts/demo_mega-sam.py     -> metric depth prior
#   2.  camera_tracking_scripts/test_demo.py  -> reconstructions/<scene>/poses.npy
#
# Upstream's 4th stage (cvd_opt) refines depth only; it does not change the
# camera trajectory, so it is skipped.
#
# Reads:
#   datasets/<dataset>/<seq>/cam0/*.png    (or mav0/cam0/data/*.png)
#   datasets/<dataset>/<seq>/times.txt     (one timestamp per frame)
#
# Writes (under $RESULTS_ROOT/<dataset>/<seq>/megasam/run<N>/):
#   trajectory.txt   TUM (timestamp_s tx ty tz qx qy qz qw)
#   run_log.txt      stdout
#   resources.csv    CPU+RAM+GPU sampled every 1s
#   run_meta.json    frames / duration / fps
set -eo pipefail

DATASET=$1; SEQ=$2; RUN_ID=${3:-1}; RUN_TYPE=${4:-vo}
WS=$(cd "$(dirname "$0")/../.." && pwd)
source "$WS/scripts/_paths.sh"
canonicalize_dataset "$DATASET"
resolve_run_type "$RUN_TYPE"
if [[ "$RUN_TYPE" != "vo" ]]; then
    echo "[megasam] ERROR: MegaSaM is monocular VO only; run_type must be 'vo'" >&2
    exit 2
fi

SEQ_DIR="$WS/datasets/$DATASET/$SEQ"
OUT_DIR="$RESULTS_ROOT/$DATASET/$SEQ/megasam/run${RUN_ID}"
LOG="$WS/logs/${DATASET}_${SEQ}_megasam_${RUN_TYPE}_run${RUN_ID}.log"
REPO="$WS/src/mega-sam"

[[ -d "$REPO" ]] || { echo "[megasam] ERROR: repo missing at $REPO (run scripts/build/setup_megasam_env.sh)" >&2; exit 2; }

# Monocular: cam0 only.
IMG_DIR=""
for candidate in "$SEQ_DIR/cam0" "$SEQ_DIR/mav0/cam0/data"; do
    if [[ -d "$candidate" ]]; then IMG_DIR="$candidate"; break; fi
done
[[ -n "$IMG_DIR" ]] || { echo "[megasam] ERROR: no cam0 image folder under $SEQ_DIR" >&2; exit 2; }
[[ -f "$SEQ_DIR/times.txt" ]] || { echo "[megasam] ERROR: missing $SEQ_DIR/times.txt" >&2; exit 2; }

for ck in "$REPO/checkpoints/megasam_final.pth" \
          "$REPO/Depth-Anything/checkpoints/depth_anything_vitl14.pth"; do
    [[ -f "$ck" ]] || { echo "[megasam] ERROR: missing checkpoint $ck" >&2; exit 2; }
done

mkdir -p "$OUT_DIR" "$WS/logs"
: > "$OUT_DIR/run_log.txt"

# The pipeline keys its intermediate + output directories off the scene name,
# inside the repo, so make it unique per run to avoid cross-run contamination.
SCENE="bench_${DATASET}_${SEQ}_run${RUN_ID}"

echo "[megasam] $DATASET/$SEQ run=${RUN_ID} -> $OUT_DIR" | tee "$LOG"
echo "[megasam] images=$IMG_DIR scene=$SCENE" | tee -a "$LOG"

set +u
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate megasam
set -u

python3 "$WS/scripts/run/_resource_monitor.py" "$OUT_DIR/resources.csv" 1 &
MONPID=$!
trap "kill $MONPID 2>/dev/null || true" EXIT

cd "$REPO"
# None of these are installed as packages: base/droid_slam holds the vendored
# DROID backend that test_demo.py imports as `droid`; Depth-Anything holds the
# `depth_anything` module used by stage 1a; UniDepth holds `unidepth`.
export PYTHONPATH="$REPO/base/droid_slam:$REPO/Depth-Anything:$REPO/UniDepth:${PYTHONPATH:-}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"

rm -rf "$REPO/reconstructions/$SCENE" "$REPO/Depth-Anything/video_visualization/$SCENE"

# Scratch RGB copy for stage 1b (see note below). Removed on exit.
UNIDEPTH_RGB_DIR="$(mktemp -d -t megasam_rgb_XXXXXX)"
trap 'kill $MONPID 2>/dev/null || true; rm -rf "$UNIDEPTH_RGB_DIR"' EXIT

START=$(date +%s.%N)
{
    echo "=== stage 1a: Depth-Anything (relative mono-depth) ==="
    python3 Depth-Anything/run_videos.py \
        --encoder vitl \
        --load-from Depth-Anything/checkpoints/depth_anything_vitl14.pth \
        --img-path "$IMG_DIR" \
        --outdir "$REPO/Depth-Anything/video_visualization/$SCENE"

    # UniDepth loads frames with PIL: `np.array(Image.open(p))[..., :3]`.
    # Our datasets are grayscale (PIL mode "L"), so that yields a 2-D array and
    # the slice takes the first 3 *columns* instead of 3 channels, which then
    # blows up on .permute(2,0,1). Stages 1a and 2 use cv2.imread and are
    # unaffected (it expands grayscale to 3-channel BGR). Feed stage 1b an RGB
    # copy rather than patching the submodule.
    echo "=== stage 1b: UniDepth (metric depth prior) ==="
    RGB_DIR="$UNIDEPTH_RGB_DIR"
    python3 - "$IMG_DIR" "$RGB_DIR" <<'RGBPY'
import sys, pathlib
from PIL import Image
src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
imgs = sorted([p for p in src.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")])
n = 0
for p in imgs:
    o = dst / (p.stem + ".png")
    if o.exists():
        continue
    im = Image.open(p)
    (im if im.mode == "RGB" else im.convert("RGB")).save(o)
    n += 1
print(f"[megasam] stage 1b: {len(imgs)} frames, {n} converted to RGB -> {dst}")
RGBPY
    python3 UniDepth/scripts/demo_mega-sam.py \
        --scene-name "$SCENE" \
        --img-path "$RGB_DIR" \
        --outdir "$REPO/UniDepth/outputs"

    echo "=== stage 2: camera tracking ==="
    python3 camera_tracking_scripts/test_demo.py \
        --datapath "$IMG_DIR" \
        --weights checkpoints/megasam_final.pth \
        --scene_name "$SCENE" \
        --mono_depth_path "$REPO/Depth-Anything/video_visualization" \
        --metric_depth_path "$REPO/UniDepth/outputs" \
        --disable_vis
} 2>&1 | python3 -u -c "
import sys, time
t0 = time.time()
for line in sys.stdin:
    sys.stdout.write(f'{time.time()-t0:.3f} {line}')
    sys.stdout.flush()
" | tee -a "$OUT_DIR/run_log.txt" "$LOG"
END=$(date +%s.%N)

POSES="$REPO/reconstructions/$SCENE/poses.npy"
if [[ ! -f "$POSES" ]]; then
    echo "[megasam] ERROR: no poses at $POSES — pipeline failed" | tee -a "$LOG"
    exit 1
fi

# poses.npy holds lietorch SE3 7-vectors (tx ty tz qx qy qz qw) for world->cam;
# TUM wants camera->world, hence .inv(). MegaSaM emits one pose per processed
# frame in order, so pair them with the leading timestamps of times.txt.
python3 - "$POSES" "$SEQ_DIR/times.txt" "$OUT_DIR/trajectory.txt" <<'PY'
import sys, numpy as np, torch
from lietorch import SE3

poses_p, times_p, out_p = sys.argv[1:4]
poses = np.load(poses_p)
ts = [l.split()[0] for l in open(times_p) if l.strip()]

c2w = SE3(torch.as_tensor(poses, dtype=torch.float32)).inv()
d = c2w.data.numpy()          # tx ty tz qx qy qz qw
n = d.shape[0]
if n > len(ts):
    raise SystemExit(f"[megasam] {n} poses but only {len(ts)} timestamps in times.txt")

with open(out_p, "w") as f:
    for t, r in zip(ts[:n], d):
        t_s = float(t) / 1e9 if "." not in t else float(t)
        f.write(f"{t_s:.9f} " + " ".join(f"{v:.9f}" for v in r[:7]) + "\n")
print(f"[megasam] wrote {out_p} ({n} poses)")
PY

DUR=$(python3 -c "print($END-$START)")
NFR=$(wc -l < "$OUT_DIR/trajectory.txt" 2>/dev/null || echo 0)
python3 -c "
import json
print(json.dumps({'algo':'megasam','dataset':'$DATASET','seq':'$SEQ','run_id':$RUN_ID,
                  'run_type':'$RUN_TYPE','use_imu':False,'use_lc':False,
                  'duration_s':$DUR,'frames':$NFR,'fps':$NFR/$DUR if $DUR>0 else 0}))
" > "$OUT_DIR/run_meta.json"
python3 "$(dirname "$0")/_enrich_run_meta.py" "$OUT_DIR/run_meta.json" \
    --config "${CONFIG:-${CONFIG_FILE:-${CFG:-}}}" --container "${CONTAINER:-}" \
    --playback-rate "${PLAYBACK_RATE:-${OV2SLAM_PLAYBACK_RATE:-${OPENVINS_RATE:-}}}" || true
echo "[megasam] run ${RUN_ID} done in ${DUR}s, ${NFR} poses" | tee -a "$LOG"
