# Optional per-attempt Docker limits for an experiment lane: memory cap and CPU pinning.
#
# A container runs under dockerd, outside the caller's systemd scope and CPU affinity,
# so a lane's limits have to reach `docker run` itself. Unset, nothing changes.
#
#   docker_limit_args PREFIX
#
# reads PREFIX_MEMORY_LIMIT, PREFIX_MEMORY_SWAP_LIMIT and PREFIX_CPUSET and sets
# DOCKER_LIMIT_ARGS (for docker run) and DOCKER_LIMIT_PROV (provenance parameters).
docker_limit_args() {
    local prefix=$1
    local memory_name="${prefix}_MEMORY_LIMIT" swap_name="${prefix}_MEMORY_SWAP_LIMIT" cpuset_name="${prefix}_CPUSET"
    local memory="${!memory_name:-}" swap="${!swap_name:-}" cpuset="${!cpuset_name:-}"
    DOCKER_LIMIT_ARGS=()
    DOCKER_LIMIT_PROV=()
    if [[ -n "$memory" || -n "$swap" ]]; then
        [[ -n "$memory" && -n "$swap" ]] \
            || { echo "[$prefix] a memory limit requires an explicit total RAM+swap limit, and vice versa" >&2; return 2; }
        DOCKER_LIMIT_ARGS+=(--memory "$memory" --memory-swap "$swap")
        DOCKER_LIMIT_PROV+=(--param "memory_limit=$memory" --param "total_ram_swap_limit=$swap")
    fi
    if [[ -n "$cpuset" ]]; then
        [[ "$cpuset" =~ ^[0-9]+(-[0-9]+)?(,[0-9]+(-[0-9]+)?)*$ ]] \
            || { echo "[$prefix] invalid CPU set: $cpuset" >&2; return 2; }
        DOCKER_LIMIT_ARGS+=(--cpuset-cpus "$cpuset")
        DOCKER_LIMIT_PROV+=(--param "cpuset_cpus=$cpuset")
    fi
    return 0
}
