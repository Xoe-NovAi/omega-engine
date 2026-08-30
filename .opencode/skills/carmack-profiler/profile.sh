#!/bin/bash
# ⬡ OMEGA ⬡ JOHN_CARMACK ⬡ PROFILER ⬡ 2026-07-01
# Deterministic cProfile wrapper for architectural auditing.

if [ -z "$1" ]; then
    echo "Usage: $0 <python_script.py> [args...]"
    echo "Example: $0 src/omega/oracle/oracle.py"
    exit 1
fi

TARGET_SCRIPT=$1
shift
ARGS=$@

# Ensure we are in the workspace root and venv is active
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Warning: .venv/bin/activate not found. Running in current environment."
fi

echo "============================================================"
echo " 🔍 CARMACK PROFILER: Executing Target"
echo " Target: $TARGET_SCRIPT $ARGS"
echo "============================================================"

# Run the script under cProfile, outputting binary stats
PYTHONPATH=src python3 -m cProfile -o .carmack_profile.stats "$TARGET_SCRIPT" $ARGS

# Check if profiling succeeded
if [ $? -ne 0 ]; then
    echo "Error: Target script execution failed."
    exit 1
fi

echo "============================================================"
echo " 📊 CARMACK PROFILER: Bottleneck Report (Top 50 by CumTime)"
echo "============================================================"

# Parse the binary stats and print the top 50 bottlenecks by cumulative time
python3 -c "
import pstats
from pstats import SortKey
try:
    p = pstats.Stats('.carmack_profile.stats')
    p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(50)
except Exception as e:
    print(f'Failed to parse stats: {e}')
" > .carmack_profile.txt

cat .carmack_profile.txt
echo "============================================================"
echo " Full report saved to: .carmack_profile.txt"
echo " Binary stats saved to: .carmack_profile.stats"
echo "============================================================"
