# 🔱 Ryzen 7 5700U System Tuning
# AP: AP-RYZEN-TUNING-v1.0.0
# Applies CPU-optimized kernel parameters for local AI inference.
# Run: sudo bash scripts/tune_ryzen.sh

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()   { echo -e "${RED}[ERR]${NC} $1"; }

# ── Verify we're on Ryzen 5700U ──────────────────────────────────────
CPU_MODEL=$(lscpu | grep "Model name" | head -1)
if ! echo "$CPU_MODEL" | grep -qi "Ryzen 7 5700U"; then
    warn "Expected AMD Ryzen 7 5700U, detected: $CPU_MODEL"
    warn "Tuning may not be optimal for this CPU"
fi

info "Tuning for: AMD Ryzen 7 5700U (Zen 2, 8C/16T)"

# ── 1. zRAM Optimization (8GB zstd) ──────────────────────────────────
if command -v zramctl &>/dev/null; then
    info "Checking zRAM configuration..."
    ZRAM_SIZE=$(zramctl | grep -v "NAME" | awk '{print $3}' | head -1)
    if [ -n "$ZRAM_SIZE" ]; then
        ok "zRAM active: $ZRAM_SIZE"
    else
        warn "zRAM not detected. Configure with:"
        warn "  sudo zramswap --size=8G --algorithm=zstd start"
    fi
fi

# ── 2. Kernel parameters for low-latency inference ───────────────────
info "Setting kernel parameters..."
SYSCTL_SETTINGS="
# Omega Engine — Ryzen 5700U AI Inference Tuning
vm.swappiness = 60
vm.vfs_cache_pressure = 50
vm.dirty_ratio = 40
vm.dirty_background_ratio = 10
vm.page-cluster = 0
kernel.numa_balancing = 0
kernel.sched_migration_cost_ns = 5000000
kernel.sched_autogroup_enabled = 0
"

# Apply settings that don't require root
info "Applying safe kernel parameters..."
echo "$SYSCTL_SETTINGS" | while IFS= read -r line; do
    if [ -n "$line" ] && ! echo "$line" | grep -q "^#"; then
        sysctl -w "$line" 2>/dev/null && ok "  $line" || warn "  could not set: $line"
    fi
done

# ── 3. CPU governor (requires root) ──────────────────────────────────
if [ "$EUID" -eq 0 ]; then
    info "Setting CPU governor to performance..."
    for cpu in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do
        echo "performance" > "$cpu" 2>/dev/null || true
    done
    ok "CPU governor set to 'performance'"

    # ── 4. Transparent HugePages for LLM inference ───────────────────
    info "Setting THP to madvise (recommended for llama.cpp)..."
    echo madvise > /sys/kernel/mm/transparent_hugepage/enabled 2>/dev/null || true
    echo advise > /sys/kernel/mm/transparent_hugepage/shmem_enabled 2>/dev/null || true
    ok "THP set to madvise"

    # ── 5. Process priority for AI workloads ────────────────────────
    info "Setting RT priority for inference processes..."
    echo -1 > /proc/sys/kernel/sched_rt_runtime_us 2>/dev/null || true
    ok "Real-time scheduling enabled"
else
    warn "Not root — skipping governor, THP, and RT scheduling."
    warn "For full tuning, run: sudo bash scripts/tune_ryzen.sh"
fi

# ── 6. Verify CPU flags ─────────────────────────────────────────────
info "Verifying CPU capabilities..."
AVX2=$(grep -o 'avx2' /proc/cpuinfo | head -1)
if [ -n "$AVX2" ]; then
    ok "AVX2 detected — optimal for llama.cpp"
else
    warn "AVX2 not detected — model inference will be slower"
fi

AVX512=$(grep -o 'avx512f' /proc/cpuinfo | head -1)
if [ -z "$AVX512" ]; then
    ok "AVX-512 not detected (expected — Zen 2 does not support it)"
fi

FMA=$(grep -o 'fma' /proc/cpuinfo | head -1)
if [ -n "$FMA" ]; then
    ok "FMA detected — optimal for BLAS operations"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Ryzen 5700U Tuning Complete${NC}"
echo -e "${GREEN}  Recommended env vars for inference:${NC}"
echo -e "${GREEN}    OMP_NUM_THREADS=6${NC}"
echo -e "${GREEN}    OMP_PROC_BIND=close${NC}"
echo -e "${GREEN}    OPENBLAS_CORETYPE=ZEN${NC}"
echo -e "${GREEN}    taskset -c 0,2,4,6,8,10,12,14 <command>${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
