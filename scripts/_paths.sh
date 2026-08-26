#!/usr/bin/env bash
# Resolve filesystem paths based on benchmark run-type.
#
# Source this from any run/eval shell script:
#   source "$WS/scripts/_paths.sh"
#   resolve_run_type "${RUN_TYPE:-vo}"   # sets RESULTS_ROOT and CSV_PATH
#
# Run types:
#   vo       : visual-only / no IMU, no loop closure        -> results/vo/        benchmark-vo.csv
#   vo-lc    : visual-only + loop closure                    -> results/vo-lc/     benchmark-vo-lc.csv
#   vio      : visual-inertial, no loop closure              -> results/vio/       benchmark-vio.csv
#   vio-lc   : visual-inertial + loop closure                -> results/vio-lc/    benchmark-vio-lc.csv
#   gnss-vio : visual-inertial + loose/tight GPS fusion      -> results/gnss-vio/  benchmark-gnss-vio.csv
#
# Exported on success: RESULTS_ROOT (abs path), CSV_PATH (abs path),
#                      RUN_TYPE (normalised), USE_IMU (true|false), USE_LC (true|false),
#                      USE_GNSS (true|false).

# Canonical repository identifier for dataset aliases. Call this before deriving
# config, dataset or result paths so one dataset cannot split across multiple trees.
canonicalize_dataset() {
    local ds="${1:?dataset name required}"
    case "$ds" in
        EuRoC-MAV|euroc|euroc_mav)
            export DATASET="euroc_mav"
            ;;
        *)
            export DATASET="$ds"
            ;;
    esac
}

resolve_run_type() {
    local rt="${1:-vo}"
    export RESULTS_BASE="$WS/results"
    case "$rt" in
        vo)
            export RUN_TYPE="vo"
            export RESULTS_ROOT="$RESULTS_BASE/vo"
            export CSV_PATH="$WS/benchmark-vo.csv"
            export USE_IMU="false"
            export USE_LC="false"
            export USE_GNSS="false"
            ;;
        vo-lc|vol-c|vo_lc)
            export RUN_TYPE="vo-lc"
            export RESULTS_ROOT="$RESULTS_BASE/vo-lc"
            export CSV_PATH="$WS/benchmark-vo-lc.csv"
            export USE_IMU="false"
            export USE_LC="true"
            export USE_GNSS="false"
            ;;
        vio)
            export RUN_TYPE="vio"
            export RESULTS_ROOT="$RESULTS_BASE/vio"
            export CSV_PATH="$WS/benchmark-vio.csv"
            export USE_IMU="true"
            export USE_LC="false"
            export USE_GNSS="false"
            ;;
        vio-lc|viol-c|vio_lc)
            export RUN_TYPE="vio-lc"
            export RESULTS_ROOT="$RESULTS_BASE/vio-lc"
            export CSV_PATH="$WS/benchmark-vio-lc.csv"
            export USE_IMU="true"
            export USE_LC="true"
            export USE_GNSS="false"
            ;;
        gnss-vio|gnss_vio|gnssvio)
            export RUN_TYPE="gnss-vio"
            export RESULTS_ROOT="$RESULTS_BASE/gnss-vio"
            export CSV_PATH="$WS/benchmark-gnss-vio.csv"
            export USE_IMU="true"
            export USE_LC="false"
            export USE_GNSS="true"
            ;;
        *)
            echo "ERROR: unknown run-type '$rt'. Use one of: vo | vo-lc | vio | vio-lc | gnss-vio" >&2
            return 2
            ;;
    esac
}

# Create a run directory only when it is absent or empty.  Direct runner use
# must never merge a new execution with stale files from an earlier attempt.
prepare_fresh_run_dir() {
    local out="${1:?output directory required}"
    local root_real out_real
    root_real=$(readlink -m "${RESULTS_ROOT:?resolve_run_type must run first}")
    out_real=$(readlink -m "$out")
    case "$out_real" in
        "$root_real"/*) ;;
        *)
            echo "ERROR: refusing result path outside $root_real: $out_real" >&2
            return 2
            ;;
    esac
    if [[ -d "$out_real" ]] && [[ -n "$(find "$out_real" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
        echo "ERROR: result directory already exists and is nonempty: $out_real" >&2
        echo "Run through run_benchmark.sh to replace the whole algorithm cell, or move/remove it explicitly." >&2
        return 2
    fi
    if [[ -e "$out_real" && ! -d "$out_real" ]]; then
        echo "ERROR: result path exists but is not a directory: $out_real" >&2
        return 2
    fi
    mkdir -p "$out_real"
}

# Provenance wrappers shared by every runner. Enrichment is intentionally not
# best-effort: if reproducibility metadata cannot be recorded, the run must not
# become a complete benchmark result.
enrich_run_meta() {
    local meta_path="${1:?run_meta.json path required}"
    shift
    python3 "$WS/scripts/run/_enrich_run_meta.py" "$meta_path" "$@"
}

record_failed_run_meta() {
    local meta_path="${1:?meta path required}"
    local algo="${2:?algorithm required}"
    local dataset="${3:?dataset required}"
    local sequence="${4:?sequence required}"
    local run_id="${5:?run id required}"
    local run_type="${6:?run type required}"
    local exit_code="${7:?exit code required}"
    local reason="${8:?failure reason required}"
    shift 8
    python3 "$WS/scripts/run/_enrich_run_meta.py" "$meta_path" \
        --create --algo "$algo" --dataset "$dataset" --sequence "$sequence" \
        --run-id "$run_id" --run-type "$run_type" \
        --process-exit-code "$exit_code" --failure-reason "$reason" "$@"
}

# Delimit the exact estimator/pipeline interval sampled by _resource_monitor.
# Runners may start the monitor before containers or ROS graphs exist; samples
# begin only after mark_resource_start and are flushed before metadata/eval.
prepare_resource_window() {
    local out="${1:?run directory required}"
    rm -f "$out/.resource_start" "$out/.resource_stop"
}

mark_resource_start() {
    local out="${1:?run directory required}"
    : > "$out/.resource_start"
}

finish_resource_window() {
    local out="${1:?run directory required}"
    local monitor_pid="${2:?monitor PID required}"
    : > "$out/.resource_stop"
    wait "$monitor_pid" 2>/dev/null || true
    rm -f "$out/.resource_start" "$out/.resource_stop"
}
