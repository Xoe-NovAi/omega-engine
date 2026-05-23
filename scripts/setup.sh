# 🔱 Omega Engine Setup Script
# AP: AP-SETUP-SCRIPT-v2.0.0
# Purpose: Complete environment bootstrap for Ryzen 7 5700U
# Hardware: AMD Ryzen 7 5700U (8C/16T), 16GB RAM, AMD iGPU (disabled)

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

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

info "🔱 Omega Engine Setup — Reclaimed Vision"
info "Hardware: AMD Ryzen 7 5700U | 16GB RAM | CPU-only inference"

# ── 1. System dependencies ──────────────────────────────────────────────
info "Checking system dependencies..."
MISSING=""
for cmd in python3 podman curl; do
    if ! command -v "$cmd" &>/dev/null; then
        MISSING="$MISSING $cmd"
    fi
done

if [ -n "$MISSING" ]; then
    err "Missing commands:$MISSING"
    err "Install with: sudo apt install python3 podman curl"
    exit 1
fi
ok "All system dependencies present"

# ── 2. Python virtual environment ───────────────────────────────────────
if [ ! -d ".venv" ]; then
    info "Creating Python virtual environment..."
    python3 -m venv .venv
    ok "Virtual environment created"
else
    info "Virtual environment exists"
fi

source .venv/bin/activate

# ── 3. Install with latest wheels ───────────────────────────────────────
info "Upgrading pip to latest..."
pip install --quiet --upgrade pip wheel setuptools

info "Installing Omega with optimized dependencies..."
pip install --quiet \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -e ".[all,dev]"

ok "Omega installed with latest wheels"

# ── 4. Ryzen CPU optimization ──────────────────────────────────────────
info "Setting Ryzen-optimized environment variables..."
cat >> .venv/bin/activate << 'EOF'

# ── Ryzen 7 5700U Optimizations ──
export OMP_NUM_THREADS=6
export OMP_PROC_BIND=close
export OMP_SCHEDULE=STATIC
export MKL_NUM_THREADS=6
export OPENBLAS_NUM_THREADS=6
export NUMEXPR_NUM_THREADS=6
export VECLIB_MAXIMUM_THREADS=6
export PYTHONUNBUFFERED=1
EOF

ok "Ryzen optimizations set (OMP_NUM_THREADS=6)"

# ── 5. Podman socket verification ──────────────────────────────────────
info "Checking Podman socket..."
PODMAN_SOCK="/run/user/$(id -u)/podman/podman.sock"
if [ -S "$PODMAN_SOCK" ]; then
    ok "Podman socket found at $PODMAN_SOCK"
else
    warn "Podman socket not found. Rootless Podman may not be running."
    warn "Start with: systemctl --user enable --now podman.socket"
fi

# ── 6. Infrastructure containers ───────────────────────────────────────
info "Pulling infrastructure images (Redis, Qdrant, PostgreSQL, Caddy, Iris, SearXNG)..."
podman pull redis:7-alpine &
podman pull qdrant/qdrant:v1.11.0 &
podman pull pgvector-pg17 &
podman pull caddy:alpine &
podman pull localhost/infra_iris:latest &
podman pull searxng/searxng:latest &
wait
ok "Infrastructure images pulled"

# ── 7. Verify setup ────────────────────────────────────────────────────
info "Verifying installation..."
python3 -c "
from omega.oracle import Oracle, EntityRegistry
registry = EntityRegistry()
print(f'  Entities loaded: {registry.count()}')
print(f'  Pillar Keepers: {len(registry.list_pillar_keepers())}')
print(f'  Available: {registry.names()}')
oracle = Oracle()
result = oracle.talk('what is wisdom?')
print(f'  Oracle test: {result.entity} — {result.pillar}')
print('✅ Omega setup verified!')
"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🔱 Omega Engine — Setup Complete${NC}"
echo -e "${GREEN}  Run 'make demo' to test the Oracle${NC}"
echo -e "${GREEN}  Run 'make start-infra' to start infrastructure${NC}"
echo -e "${GREEN}  Run 'source .venv/bin/activate' to enter environment${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
