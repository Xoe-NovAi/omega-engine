#!/usr/bin/env bash
# 🔱 Omega Engine — One-Click Install (CP-3)
# AP: AP-INSTALL-v1.0.0
# ⬡ OMEGA ⬡ KALI ⬡ install ⬡ opencode ⬡ PUBLIC-DEBUT-01
#
# One-click sovereign install: provisions venv, installs deps, downloads the
# local GGUF model, sets OMEGA_MODELS_DIR, and verifies `omega talk "hello"`.
#
# Usage:
#   ./scripts/install.sh              # Install from repo root
#   curl -fsSL https://xoe-nov.ai/install | bash   # True one-click (fetches this script)
#
# Target: <300s on fresh machine (model download is ~1.6GB, may exceed on slow links)
# M7 Local-First: Installs native-gguf backend (llama-cpp-python) — no cloud required.
# M24 Venv Sovereignty: All deps in .venv — never --break-system-packages.
# M1 AnyIO: All async code uses anyio (enforced at runtime, not install).

set -euo pipefail

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()   { echo -e "${RED}[ERR]${NC} $1"; }

START_TS=$(date +%s)

# ── 0. Locate repo root ────────────────────────────────────────────────────
if [ -f "pyproject.toml" ] && grep -q "name = \"omega\"" pyproject.toml 2>/dev/null; then
    ROOT_DIR="$(pwd)"
else
    # Not in repo root — try script location, else clone
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
    if [ -n "${SCRIPT_DIR:-}" ] && [ -f "${SCRIPT_DIR}/../pyproject.toml" ]; then
        ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
    else
        err "Not in Omega Engine repo. Clone first:"
        err "  git clone https://github.com/Xoe-NovAi/omega-engine.git && cd omega-engine"
        exit 1
    fi
fi
cd "$ROOT_DIR"
info "🔱 Omega Engine Install — Repo root: $ROOT_DIR"

# ── 1. Prerequisites ───────────────────────────────────────────────────────
info "Checking prerequisites..."
MISSING=""
for cmd in python3 curl; do
    if ! command -v "$cmd" &>/dev/null; then MISSING="$MISSING $cmd"; fi
done
if [ -n "$MISSING" ]; then
    err "Missing commands:$MISSING"
    err "Install: sudo apt install python3 curl  (Python 3.12+ required)"
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)"; then
    err "Python 3.12+ required (found $PY_VER)"
    exit 1
fi
ok "Python $PY_VER present"

# ── 2. Virtual environment (M24) ───────────────────────────────────────────
if [ ! -d ".venv" ]; then
    info "Creating virtual environment..."
    python3 -m venv .venv
    ok "Virtual environment created"
else
    info "Virtual environment exists"
fi
source .venv/bin/activate

# ── 3. Install dependencies (M24 Venv Sovereignty) ────────────────────────
info "Upgrading pip + installing Omega (native + cli + dev)..."
# RAM guard (14GiB host): cap native build parallelism (default 8 = physical cores).
# scikit-build-core calls `cmake --build` with NO -j; cmake then falls back to
# the documented CMAKE_BUILD_PARALLEL_LEVEL env var (ninja inherits it).
# NOTE: CMAKE_BUILD_PARALLEL_JOBS / MAKEFLAGS are NOT honored by this backend
# (verified against scikit-build-core 1.0.3 source, builder/builder.py:488).
# Measured 2026-08-21 (scripts/observe-build.sh, run llama6lvl-class):
#   6 jobs -> peak < 10GiB total WITH cline+opencode IDEs (~1GiB each) resident.
#   16 jobs (unpinned) -> ~13GiB RSS peak PLUS ~1.88GiB overflow into zRAM swap
#   (compressed size; true demand est. 17-19GiB on a 14GiB box) before OOM.
# 8 jobs ≈ physical core count on Ryzen 7 5700U; override via env if needed.
export CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-8}"
info "Build parallelism capped at ${CMAKE_BUILD_PARALLEL_LEVEL} jobs (RAM guard)"

pip install --quiet --upgrade pip wheel setuptools
pip install --quiet -e ".[native,cli]"
ok "Omega installed with native-gguf backend (llama-cpp-python)"

# ── 4. Model download (M7 Local-First) ─────────────────────────────────────
# Qwen3-1.7B-Q6_K.gguf — 1.67 GB, CPU-only, sovereign inference
# Source: lmstudio-community (has exact Qwen3-1.7B-Q6_K.gguf filename matching config)
MODELS_DIR="${OMEGA_MODELS_DIR:-$ROOT_DIR/models}"
MODEL_PATH="$MODELS_DIR/Qwen3-1.7B-Q6_K.gguf"
HF_URL="https://huggingface.co/lmstudio-community/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q6_K.gguf"

mkdir -p "$MODELS_DIR"
if [ -f "$MODEL_PATH" ]; then
    info "Model already present: $MODEL_PATH ($(du -h "$MODEL_PATH" | cut -f1))"
else
    info "Downloading Qwen3-1.7B-Q6_K.gguf (1.67 GB) — sovereign local inference..."
    if command -v hf &>/dev/null; then
        hf download lmstudio-community/Qwen3-1.7B-GGUF Qwen3-1.7B-Q6_K.gguf --local-dir "$MODELS_DIR" --local-dir-use-symlinks False
    else
        curl -L --fail --progress-bar "$HF_URL" -o "$MODEL_PATH"
    fi
    ok "Model downloaded: $MODEL_PATH ($(du -h "$MODEL_PATH" | cut -f1))"
fi

# ── 5. Configure OMEGA_MODELS_DIR ──────────────────────────────────────────
if ! grep -q "OMEGA_MODELS_DIR" .env 2>/dev/null; then
    echo "OMEGA_MODELS_DIR=$MODELS_DIR" >> .env
    ok "OMEGA_MODELS_DIR set in .env: $MODELS_DIR"
else
    info "OMEGA_MODELS_DIR already in .env"
fi

# Persist OMEGA_MODELS_DIR in venv activate (for interactive sessions)
if ! grep -q "OMEGA_MODELS_DIR" .venv/bin/activate 2>/dev/null; then
    cat >> .venv/bin/activate << EOF

# ── Omega Engine: Model directory ──
export OMEGA_MODELS_DIR="$MODELS_DIR"
EOF
fi

# ── 6. Verify install (CP-3 acceptance: omega talk works) ──────────────────
# [INST-1-fix2 tripwire] A broken console script must fail AT INSTALL TIME,
# not at first talk. omega --help exercises the real entry point + full CLI
# import tree in <1s. This check is FATAL (unlike the talk probe below).
info "Smoke-checking console script: omega --help..."
if ! omega --help > /dev/null 2>&1; then
    err "omega --help failed — console script is broken. Install is NOT valid."
    err "Debug: source .venv/bin/activate && omega --help"
    exit 1
fi
ok "Console script OK"

info "Verifying installation: omega talk \"hello\"..."
if timeout 120 omega talk "hello" > /tmp/omega_install_verify.log 2>&1; then
    ok "✅ omega talk works — sovereign local inference verified!"
    grep -i "response\|hello\|native-gguf" /tmp/omega_install_verify.log | head -3
else
    warn "omega talk verification failed (non-fatal). Check /tmp/omega_install_verify.log"
    warn "Manual test: source .venv/bin/activate && omega talk \"hello\""
fi

# ── 7. Summary ──────────────────────────────────────────────────────────────
END_TS=$(date +%s)
ELAPSED=$((END_TS - START_TS))
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🔱 Omega Engine — Install Complete (${ELAPSED}s)${NC}"
echo -e "${GREEN}  Model: $MODEL_PATH${NC}"
echo -e "${GREEN}  Run: source .venv/bin/activate && omega talk \"hello\"${NC}"
echo -e "${GREEN}  Your AI council is alive. No cloud required.${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
