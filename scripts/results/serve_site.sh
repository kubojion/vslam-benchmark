#!/usr/bin/env bash
set -euo pipefail

WS=$(cd "$(dirname "$0")/../.." && pwd)
PORT=${1:-8080}
exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$WS/results/site"
