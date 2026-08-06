#!/bin/bash
# Apply the OKVIS2 external CMake patches (see README.md — the only runtime
# prerequisite not carried by the fork submodules). Idempotent.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"

apply_patch() {
    local dir="$1" patch="$2"
    if git -C "$dir" apply --reverse --check "$patch" 2>/dev/null; then
        echo "[prereq] $(basename "$patch") already applied in $dir"
    elif git -C "$dir" apply --check "$patch" 2>/dev/null; then
        git -C "$dir" apply "$patch"
        echo "[prereq] applied $(basename "$patch") in $dir"
    else
        echo "[prereq] WARNING: $(basename "$patch") does not apply cleanly in $dir" >&2
        exit 1
    fi
}

echo "[prereq] OKVIS2 external CMake patches"
apply_patch "$REPO/src/okvis2/external/DBoW2"  "$HERE/okvis2/dbow2-cmake.patch"
apply_patch "$REPO/src/okvis2/external/opengv" "$HERE/okvis2/opengv-cmake.patch"
echo "[prereq] done"
