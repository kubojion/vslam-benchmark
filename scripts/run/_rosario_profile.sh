# Explicit indexed candidate selection. Source after WS/DATASET/SEQ/RUN_TYPE.
# Default runner profiles remain unchanged when ROSARIO_VIO_PROFILE is absent.
check_rosario_candidate() {
    ROSARIO_PROFILE_ALGORITHM=$1
    PROFILE_PROV_ARGS=()
    [[ -n "${ROSARIO_VIO_PROFILE:-}" ]] || return 0
    if [[ -n "${BASALT_CONFIG:-}${BASALT_CALIBRATION:-}" ]]; then
        echo 'indexed Rosario profiles cannot be mixed with Basalt overrides' >&2
        return 2
    fi
    python3 "$WS/scripts/run/_rosario_profile.py" "$WS" "$1" "$DATASET" "$SEQ" \
        "$RUN_TYPE" "$ROSARIO_VIO_PROFILE" >/dev/null
}

snapshot_rosario_candidate() {
    [[ -n "${ROSARIO_VIO_PROFILE:-}" ]] || return 0
    ROSARIO_PROFILE_DIR="$OUT_DIR/configuration-profile"
    python3 "$WS/scripts/run/_rosario_profile.py" "$WS" "$ROSARIO_PROFILE_ALGORITHM" \
        "$DATASET" "$SEQ" "$RUN_TYPE" "$ROSARIO_VIO_PROFILE" \
        --snapshot-to "$ROSARIO_PROFILE_DIR" >/dev/null
    PROFILE_PROV_ARGS=(--param "cohort_artifact_semantics=2"
        --artifact "candidate_selection=$ROSARIO_PROFILE_DIR/selection.json"
        --param "rosario_vio_profile=$ROSARIO_VIO_PROFILE"
        --param "production_camera_profile_confirmed=false")
}
