#!/bin/bash
set -euo pipefail

LOG=~/thermal_bench_$(date +%Y%m%d_%H%M%S).csv
echo "timestamp,CPU,Core,CPU%,BUSY%,MHz,Temp_C,Watt" > "$LOG"

stress-ng --cpu 10 --cpu-method fft --timeout 600 &
STRESS_PID=$!

turbostat --interval 1 --show CPU,Core,CPU%,BUSY%,MHz,Temp,Watt --quiet 600 >> "$LOG" &
TURBO_PID=$!

wait $STRESS_PID
kill $TURBO_PID 2>/dev/null || true

echo "Benchmark complete. Log: $LOG"
echo "Throttling check:"
grep -E "PROCHOT|THERMAL_THROTTLE" /var/log/kern.log || echo "No kernel throttling logs"
