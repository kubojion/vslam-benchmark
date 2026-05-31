#!/usr/bin/env bash
# Resolve filesystem paths based on benchmark run-type.
#
# Source this from any run/eval shell script:
#   source "$WS/scripts/_paths.sh"
#   resolve_run_type "${RUN_TYPE:-vo}"   # sets RESULTS_ROOT and CSV_PATH
#
# Run types:
#   vo       : visual-only / no IMU, no loop closure        -> results-vo/        benchmark-vo.csv
#   vio      : visual-inertial, no loop closure              -> results-vio/       benchmark-vio.csv
#   vio-lc   : visual-inertial + loop closure                -> results-vio-lc/    benchmark-vio-lc.csv
#   gnss-vio : visual-inertial + loose/tight GPS fusion      -> results-gnss-vio/  benchmark-gnss-vio.csv
#
# Exported on success: RESULTS_ROOT (abs path), CSV_PATH (abs path),
#                      RUN_TYPE (normalised), USE_IMU (true|false), USE_LC (true|false),
#                      USE_GNSS (true|false).

resolve_run_type() {
    local rt="${1:-vo}"
    case "$rt" in
        vo)
            export RUN_TYPE="vo"
            export RESULTS_ROOT="$WS/results-vo"
            export CSV_PATH="$WS/benchmark-vo.csv"
            export USE_IMU="false"
            export USE_LC="false"
            export USE_GNSS="false"
            ;;
        vio)
            export RUN_TYPE="vio"
            export RESULTS_ROOT="$WS/results-vio"
            export CSV_PATH="$WS/benchmark-vio.csv"
            export USE_IMU="true"
            export USE_LC="false"
            export USE_GNSS="false"
            ;;
        vio-lc|viol-c|vio_lc)
            export RUN_TYPE="vio-lc"
            export RESULTS_ROOT="$WS/results-vio-lc"
            export CSV_PATH="$WS/benchmark-vio-lc.csv"
            export USE_IMU="true"
            export USE_LC="true"
            export USE_GNSS="false"
            ;;
        gnss-vio|gnss_vio|gnssvio)
            export RUN_TYPE="gnss-vio"
            export RESULTS_ROOT="$WS/results-gnss-vio"
            export CSV_PATH="$WS/benchmark-gnss-vio.csv"
            export USE_IMU="true"
            export USE_LC="false"
            export USE_GNSS="true"
            ;;
        *)
            echo "ERROR: unknown run-type '$rt'. Use one of: vo | vio | vio-lc | gnss-vio" >&2
            return 2
            ;;
    esac
}
