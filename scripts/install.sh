#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

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
# RAM guard: cap native build parallelism BEFORE any pip install runs.
# scikit-build-core calls `cmake --build` with NO -j; cmake then falls back to
# the documented CMAKE_BUILD_PARALLEL_LEVEL env var (ninja inherits it).
# NOTE: CMAKE_BUILD_PARALLEL_JOBS / MAKEFLAGS are NOT honored by this backend
# (verified against scikit-build-core 1.0.3 source, builder/builder.py:488).
# Measured 2026-08-21 (scripts/observe-build.sh, run llama6lvl-class):
#   6 jobs -> peak < 10GiB total WITH cline+opencode IDEs (~1GiB each) resident.
#   16 jobs (unpinned) -> ~13GiB RSS peak PLUS ~1.88GiB overflow into zRAM swap
#   (compressed size; true demand est. 17-19GiB on a 14GiB box) before OOM.
# 2026-10-13: default lowered 8 -> 6. A run observed at -j16 (all logical
# CPUs, SMT included) visibly thrashed the box while the export sat below
# the pre-fetch block. 6 jobs stays well inside the measured RAM envelope
# and keeps the machine responsive; override via env if you disagree.
# The export MUST precede the aria2c sdist pre-fetch below — a build triggered
# before the export silently inherits ninja's -j<nproc> (observed 2026-10-13).
export CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-6}"
info "Build parallelism capped at ${CMAKE_BUILD_PARALLEL_LEVEL} jobs (RAM guard)"

# M23 sovereign-fetch: llama-cpp-python ships NO wheel on PyPI (sdist only,
# ~76 MB) — the largest non-model download in this path. Pre-fetch it via
# aria2c into .vendor/ and hand it to pip; every failure mode is non-fatal
# (pip's own resume-capable downloader resolves it normally).
SDIST_DIR="$ROOT_DIR/.vendor"
if command -v aria2c &>/dev/null; then
    mkdir -p "$SDIST_DIR"
    info "Pre-fetching llama-cpp-python sdist via aria2c (M23)..."
    LCP_URL=$(curl -fsSL https://pypi.org/simple/llama-cpp-python/ \
        | grep -oE 'https://[^"#]+\.tar\.gz' | tail -1 || true)
    if [ -n "$LCP_URL" ]; then
        LCP_FILE="$SDIST_DIR/$(basename "$LCP_URL")"
        if aria2c -x16 -s16 -c --file-allocation=none -d "$SDIST_DIR" \
                  -o "$(basename "$LCP_FILE")" "$LCP_URL" >/dev/null 2>&1; then
            ok "sdist pre-fetched via aria2c: $(basename "$LCP_FILE")"
            info "Installing pre-fetched sdist (builds + caches wheel)..."
            if pip install "$LCP_FILE"; then
                ok "llama-cpp-python installed from pre-fetched sdist"
            else
                warn "pre-fetched sdist install failed — pip will resolve normally"
            fi
        else
            warn "aria2c fetch failed — pip will resolve normally"
        fi
    fi
else
    info "aria2c not present — pip will fetch llama-cpp-python directly (M23 prefers aria2c)"
fi

info "Upgrading pip + installing Omega (native + cli + dev)..."

pip install --quiet --upgrade pip wheel setuptools
pip install --quiet -e ".[native,cli]"
ok "Omega installed with native-gguf backend (llama-cpp-python)"

# ── 4. Model download (M7 Local-First) ─────────────────────────────────────
# LFM2.5-2.6B-Q4_K_M.gguf — 1.67 GB, CPU-only, sovereign inference
# Source: lmstudio-community (has exact LFM2.5-2.6B-Q4_K_M.gguf filename matching config)
# MODELS_DIR default mirrors scripts/serve_native_gguf.sh; env override wins.
# (Fixed 2026-10-13: MODELS_DIR was used-but-unset → instant death under `set -u`.)
MODELS_DIR="${OMEGA_MODELS_DIR:-/media/arcana-novai/omega_library/models/gguf}"
MODEL_PATH="$MODELS_DIR/LFM2.5-2.6B-Q4_K_M.gguf"
HF_URL="https://huggingface.co/lmstudio-community/LFM2.5-2.6B-GGUF/resolve/main/LFM2.5-2.6B-Q4_K_M.gguf"

mkdir -p "$MODELS_DIR"
if [ -f "$MODEL_PATH" ]; then
    info "Model already present: $MODEL_PATH ($(du -h "$MODEL_PATH" | cut -f1))"
else
    info "Downloading LFM2.5-2.6B-Q4_K_M.gguf (1.67 GB) — sovereign local inference..."
    if command -v aria2c &>/dev/null; then
        # M23: aria2c is MANDATORY for >1MB downloads (.opencode/rules/07-sovereign-fetch.md).
        # 16 splits/16 conns per ~/.config/aria2/aria2.conf; -c resumes.
        aria2c -x16 -s16 -c --file-allocation=none \
            -d "$MODELS_DIR" -o "$(basename "$MODEL_PATH")" "$HF_URL"
        ok "Model downloaded via aria2c: $MODEL_PATH ($(du -h "$MODEL_PATH" | cut -f1))"
    elif command -v hf &>/dev/null; then
        # aria2c absent (fresh non-Node-0 machine) — hf has native resume.
        hf download lmstudio-community/LFM2.5-2.6B-GGUF LFM2.5-2.6B-Q4_K_M.gguf --local-dir "$MODELS_DIR" --local-dir-use-symlinks False
        ok "Model downloaded via hf: $MODEL_PATH ($(du -h "$MODEL_PATH" | cut -f1))"
    else
        warn "aria2c not found — falling back to curl (single-connection; M23 prefers aria2c)"
        curl -L --fail --progress-bar "$HF_URL" -o "$MODEL_PATH"
        ok "Model downloaded via curl: $MODEL_PATH ($(du -h "$MODEL_PATH" | cut -f1))"
    fi
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

info "Verifying installation: omega talk \"hello\" (mock provider, no network)..."
# Mock-forced probe: deterministic, no keys, no inference backends.
# (Fixed 2026-10-13: bare `omega talk` attempted real inference with no keys
# and hung 60s to turn-layer timeout. dee63d49 made OMEGA_PROVIDER=mock
# deterministic — the install probe must use it.)
if OMEGA_PROVIDER=mock timeout 120 omega talk "hello" > /tmp/omega_install_verify.log 2>&1; then
    ok "✅ omega talk works (mock provider) — install verified!"
    grep -i "response\|hello\|mock" /tmp/omega_install_verify.log | head -3
else
    warn "omega talk verification failed (non-fatal). Check /tmp/omega_install_verify.log"
    warn "Manual test: source .venv/bin/activate && OMEGA_PROVIDER=mock omega talk \"hello\""
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
