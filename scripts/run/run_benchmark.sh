#!/usr/bin/env bash
# Safely run/resume a cell, evaluating each repetition before starting the next.
# Existing attempts are preserved. See run_repetitions.py --help for recovery and
# dry-run options. Scientific qualification is separate from process completion.
set -euo pipefail
WS=$(cd "$(dirname "$0")/../.." && pwd)
exec python3 "$WS/scripts/campaign/run_repetitions.py" "$@"
