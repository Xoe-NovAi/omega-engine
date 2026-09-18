#!/bin/bash
# thermal_bench.sh — repeatable sustained-load thermal experiment (Node 1, i7-13620H)
#
# Usage: scripts/thermal_bench.sh --label <cooling-condition> [--seconds N] [--workers N]
#   e.g. scripts/thermal_bench.sh --label flat-nofan --seconds 300
#
# Both load (stress-ng) and monitor (turbostat) self-terminate; the wrapper
# just waits. Launch DETACHED (setsid) so tool-call teardown can't kill it:
#   setsid nohup scripts/thermal_bench.sh --label X --seconds 300 < /dev/null > /dev/null 2>&1 &
#
# Between runs: idle-soak until PkgTmp < 55C or it starts heat-soaked.
set -euo pipefail

LABEL="run"
SECONDS=300
WORKERS=10
while [[ $# -gt 0 ]]; do case "$1" in
  --label) LABEL="$2"; shift 2 ;;
  --seconds) SECONDS="$2"; shift 2 ;;
  --workers) WORKERS="$2"; shift 2 ;;
  *) echo "unknown arg: $1" >&2; exit 1 ;;
esac; done

INTERVAL=5
ITERS=$((SECONDS / INTERVAL))
mkdir -p logs/thermal
LOG="logs/thermal/thermal_${LABEL}_$(date +%Y%m%d_%H%M%S).log"
echo "$LOG" > logs/thermal/.latest

AC=$(cat /sys/class/power_supply/AC*/online 2>/dev/null \
  || cat /sys/class/power_supply/ADP*/online 2>/dev/null \
  || echo unknown)
GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
EPP=$(cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference)
MAXPCT=$(cat /sys/devices/system/cpu/intel_pstate/max_perf_pct)

{
  echo "=== START $(date -u +%FT%TZ) label=$LABEL seconds=$SECONDS workers=$WORKERS"
  echo "=== governor=$GOV epp=$EPP max_perf_pct=$MAXPCT AC_online=$AC"
} >> "$LOG"

stress-ng --cpu "$WORKERS" --cpu-method fft --timeout "$SECONDS" >> "$LOG" 2>&1 &
sudo turbostat --interval "$INTERVAL" --num_iterations "$ITERS" --quiet >> "$LOG" 2>&1 &
wait
echo "=== END $(date -u +%FT%TZ)" >> "$LOG"
echo "done: $LOG"
