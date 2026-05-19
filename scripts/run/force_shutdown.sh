#!/usr/bin/env bash
# Usage: sudo ./force_shutdown.sh [minutes]   (default: 60)
# Schedules a forced power-off after N minutes, with warnings at 10/5/1 min.

set -euo pipefail

MINUTES="${1:-60}"

if ! [[ "$MINUTES" =~ ^[0-9]+$ ]] || [ "$MINUTES" -lt 1 ]; then
  echo "Error: minutes must be a positive integer" >&2
  exit 1
fi

if [ "$EUID" -ne 0 ]; then
  echo "Re-run with sudo." >&2
  exit 1
fi

echo "[force_shutdown] System will be FORCE shut down in ${MINUTES} minute(s)."
echo "[force_shutdown] PID: $$  (kill this process to cancel)"

notify() {
  wall "*** SYSTEM FORCE SHUTDOWN in $1 ***" 2>/dev/null || true
}

SECS=$(( MINUTES * 60 ))
WARNS=(600 300 60)   # 10m, 5m, 1m

while [ "$SECS" -gt 0 ]; do
  for w in "${WARNS[@]}"; do
    if [ "$SECS" -eq "$w" ]; then
      notify "$((w/60)) minute(s)"
    fi
  done
  sleep 1
  SECS=$((SECS - 1))
done

notify "NOW"
sleep 2

# Force: kill processes, do not wait for clean unmounts/services.
# Use 'poweroff -f' (single -f) for a slightly safer forced poweroff.
# Use '-ff' for an immediate, hard power-off (higher risk of FS corruption).
systemctl poweroff -ff
