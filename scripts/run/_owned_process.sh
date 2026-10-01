# Attempt-scoped process control. Source after WS, OUT_DIR and (for Docker)
# CONTAINER are set. These helpers never kill a process by its program name.
owned_stage_args() {
    local label=$1
    [[ "$label" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo 'invalid stage label' >&2; return 2; }
    OWNED_ARGS=(--state "$OUT_DIR/processes/$label.json")
    if [[ -n "${CONTAINER:-}" ]]; then
        case "$OUT_DIR" in
            "$WS/results/"*) ;;
            *) echo 'container process state must be under workspace/results' >&2; return 2 ;;
        esac
        OWNED_ARGS+=(--container "$CONTAINER" --container-state "/results/${OUT_DIR#"$WS/results/"}/processes/$label.json")
    fi
}
owned_run() {
    local label=$1; shift
    owned_stage_args "$label" || return
    python3 "$WS/scripts/run/_owned_process.py" "${OWNED_ARGS[@]}" run -- "$@"
}
owned_stop() {
    owned_stage_args "$1" || return
    python3 "$WS/scripts/run/_owned_process.py" "${OWNED_ARGS[@]}" --grace "${OWNED_STOP_GRACE:-5}" stop
}
owned_running() {
    local label=$1; shift
    owned_stage_args "$label" || return
    python3 "$WS/scripts/run/_owned_process.py" "${OWNED_ARGS[@]}" "$@" status >/dev/null
}
owned_require_idle() {
    local args=() name
    [[ -z "${CONTAINER:-}" ]] || args+=(--container "$CONTAINER")
    for name in "$@"; do args+=(--name "$name"); done
    python3 "$WS/scripts/run/_owned_process.py" "${args[@]}" idle
}
owned_ros1_port() {
    local args=()
    if [[ -n "${CONTAINER:-}" ]]; then
        docker inspect -f '{{json .Mounts}}' "$CONTAINER" | python3 -c '
import json,sys
from pathlib import Path
mounts=json.load(sys.stdin)
valid=[m for m in mounts if m.get("Destination")=="/results" and m.get("RW")
       and Path(m.get("Source","")).resolve()==Path(sys.argv[1]).resolve()]
if len(valid)!=1:raise SystemExit("container /results must bind this workspace results directory read-write")
' "$WS/results" || return
        args+=(--container "$CONTAINER")
    fi
    ROS_PORT=$(python3 "$WS/scripts/run/_owned_process.py" "${args[@]}" free-port) || return
    [[ "$ROS_PORT" =~ ^[0-9]+$ ]] || return 2
    ROS_MASTER_URI="http://127.0.0.1:$ROS_PORT"
    export ROS_MASTER_URI
    printf '%s\n' "$ROS_MASTER_URI" > "$OUT_DIR/ros_master_uri.txt"
}
owned_ros2_domain() {
    local domain candidates
    candidates=${VSLAM_ROS_DOMAIN_ID:-"80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99"}
    mkdir -p "$WS/logs/.resource-locks"
    for domain in $candidates; do
        [[ "$domain" =~ ^[0-9]+$ ]] || { echo 'invalid ROS domain ID' >&2; return 2; }
        exec {OWNED_DOMAIN_LOCK_FD}>"$WS/logs/.resource-locks/ros-domain-$domain.lock"
        if flock -n "$OWNED_DOMAIN_LOCK_FD" && python3 "$WS/scripts/run/_owned_process.py" --domain "$domain" domain-free; then
            export ROS_DOMAIN_ID=$domain
            export ROS_LOCALHOST_ONLY=1
            printf '%s\n' "$ROS_DOMAIN_ID" > "$OUT_DIR/ros_domain_id.txt"
            return 0
        fi
        exec {OWNED_DOMAIN_LOCK_FD}>&-
    done
    echo 'no unused, unlocked ROS 2 domain available; preserve other processes' >&2
    return 2
}
