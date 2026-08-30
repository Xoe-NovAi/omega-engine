#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Build Observability Harness v1.1.0
# AP: AP-BUILD-OBS-v1.1.0
# ⬡ OMEGA ⬡ P8-OBSERVABILITY ⬡ install ⬡ PUBLIC-DEBUT-01
#
# Wraps any build command with full telemetry:
#   scripts/observe-build.sh <run-name> <command> [args...]
#   BUILD_TIMEOUT_SECS=1800 scripts/observe-build.sh ...   # hard kill after 30m
#   STALL_SAMPLES=300        # samples (~5 min @1s) of zero log growth => STALL
#
# Captures (under /tmp/opencode/obs/<run-name>/):
#   console.log    full stdout+stderr of the command
#   metrics.csv    per-second: ts,mem_used_mb,mem_avail_mb,load1,top_pid,top_cmd,top_rss_mb
#   STALL          created when console.log stops growing for $STALL_SAMPLES samples
#                  (delete-and-resume is automatic if growth restarts)
#   summary.txt    postmortem: duration, peak RAM, peak offender, stalls, exit code
#
# Policy: docs/guides/BUILD_OBSERVABILITY.md — REQUIRED for native/long builds.

set -uo pipefail
RUN="${1:?usage: observe-build.sh <run-name> <cmd> [args...]}"; shift
DIR="/tmp/opencode/obs/${RUN}"
mkdir -p "$DIR"
CSV="$DIR/metrics.csv"; LOG="$DIR/console.log"; SUM="$DIR/summary.txt"; STALLF="$DIR/STALL"
echo "ts,mem_used_mb,mem_avail_mb,load1,top_pid,top_cmd,top_rss_mb" > "$CSV"
rm -f "$STALLF"
STALL_LIMIT="${STALL_SAMPLES:-300}"
TIMEOUT="${BUILD_TIMEOUT_SECS:-0}"

sample() {
  local last_size=0 still=0
  while kill -0 "$CMD_PID" 2>/dev/null; do
    ps -eo pid,comm,rss --sort=-rss --no-headers | awk -v ts="$(date +%s)" \
      -v mu="$(free -m | awk '/^Mem:/{print $3}')" \
      -v ma="$(free -m | awk '/^Mem:/{print $7}')" \
      -v l1="$(cut -d' ' -f1 /proc/loadavg)" \
      'NR==1{printf "%s,%s,%s,%s,%s,%s,%d\n", ts,mu,ma,l1,$1,$2,$3/1024}' >> "$CSV"
    # --- stall detection: console.log frozen? ---
    local size; size=$(stat -c %s "$LOG" 2>/dev/null || echo 0)
    if [ "$size" -eq "$last_size" ]; then
      still=$((still+1))
      if [ "$still" -eq "$STALL_LIMIT" ] && [ ! -f "$STALLF" ]; then
        echo "STALL_SINCE=$(date +%T) last_growth_bytes=$size" > "$STALLF"
      fi
    else
      still=0; rm -f "$STALLF"
    fi
    last_size=$size
    sleep 1
  done
}

timeout_guard() {
  [ "$TIMEOUT" -gt 0 ] || return 0
  local waited=0
  while kill -0 "$CMD_PID" 2>/dev/null; do
    sleep 5; waited=$((waited+5))
    if [ "$waited" -ge "$TIMEOUT" ]; then
      echo "TIMED_OUT_AT=$(date +%T) after ${TIMEOUT}s" >> "$STALLF" 2>/dev/null
      kill -TERM "-${CMD_PID}" 2>/dev/null || kill -TERM "$CMD_PID" 2>/dev/null
      return 0
    fi
  done
}

START=$(date +%s)
("$@" > "$LOG" 2>&1) &
CMD_PID=$!
sample &
SAMPLER_PID=$!
timeout_guard &
GUARD_PID=$!
wait "$CMD_PID"; EXIT=$?
kill "$SAMPLER_PID" "$GUARD_PID" 2>/dev/null; wait 2>/dev/null
END=$(date +%s)

{
  echo "run:        $RUN"
  echo "exit_code:  $EXIT"
  [ -f "$STALLF" ] && { echo "*** STALL DETECTED ***"; cat "$STALLF"; }
  echo "duration_s: $((END-START))"
  echo "peak_mem_used_mb: $(tail -n +2 "$CSV" | cut -d, -f2 | sort -n | tail -1)"
  echo "peak_offender_at_peak: $(tail -n +2 "$CSV" | sort -t, -k2 -rn | head -1 | cut -d, -f5,6,7)"
  echo "top_5_pids_by_peak_rss_mb:"
  tail -n +2 "$CSV" | awk -F, '{if ($7>m[$6]) m[$6]=$7; p[$6]=$5} END {for (c in m) printf "  %8.2f  pid=%s  %s\n", m[c], p[c], c}' | sort -rn | head -5
  echo "console_tail:"; tail -5 "$LOG" | sed 's/^/  /'
} > "$SUM"
cat "$SUM"
exit "$EXIT"
