#!/usr/bin/env bash
# 🔱 clone_all_third_party.sh — Clone all third-party repos for Omega Engine
# AP Token: AP-CLONE-THIRD-PARTY-v1.0.0
# Run from: omega-engine root directory

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THIRD_PARTY_DIR="${REPO_ROOT}/third-party"

mkdir -p "${THIRD_PARTY_DIR}"
cd "${THIRD_PARTY_DIR}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Omega Engine — Third-Party Repository Cloner               ║"
echo "║  Cloning 19 repos to: ${THIRD_PARTY_DIR}"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════════
# P0 — Critical Runtime Dependencies (MUST HAVE)
# ═══════════════════════════════════════════════════════════════
echo "┌────────────────────────────────────────────────────────────┐"
echo "│ P0 — Critical Runtime Dependencies                         │"
echo "└────────────────────────────────────────────────────────────┘"

clone_p0() {
    local name="$1"
    local url="$2"
    local tag="${3:-}"
    
    if [[ -d "${name}" ]]; then
        echo "  ⏭️  ${name} already exists, pulling latest..."
        cd "${name}" && git pull --ff-only && cd ..
    else
        echo "  📥 Cloning ${name}..."
        if [[ -n "${tag}" ]]; then
            git clone --branch "${tag}" --depth 1 "${url}" "${name}"
        else
            git clone "${url}" "${name}"
        fi
    fi
}

clone_p0 "sqlite-vec"       "https://github.com/asg017/sqlite-vec.git"
clone_p0 "headroom"         "https://github.com/headroomlabs-ai/headroom.git"
clone_p0 "llama.cpp"         "https://github.com/ggml-org/llama.cpp.git"
clone_p0 "qdrant-client"     "https://github.com/qdrant/qdrant-client.git"

# ═══════════════════════════════════════════════════════════════
# P1 — Architecture Reference Repos
# ═══════════════════════════════════════════════════════════════
echo ""
echo "┌────────────────────────────────────────────────────────────┐"
echo "│ P1 — Architecture Reference Repos                          │"
echo "└────────────────────────────────────────────────────────────┘"

clone_p1() {
    local name="$1"
    local url="$2"
    
    if [[ -d "${name}" ]]; then
        echo "  ⏭️  ${name} already exists, pulling latest..."
        cd "${name}" && git pull --ff-only && cd ..
    else
        echo "  📥 Cloning ${name}..."
        git clone "${url}" "${name}"
    fi
}

clone_p1 "mempalace"       "https://github.com/mempalace/mempalace.git"
clone_p1 "grok-build"       "https://github.com/xai-org/grok-build.git"
clone_p1 "DOOM"             "https://github.com/id-Software/DOOM.git"
clone_p1 "Quake"            "https://github.com/id-Software/Quake.git"
clone_p1 "letta"            "https://github.com/letta-ai/letta.git"

# ═══════════════════════════════════════════════════════════════
# P2 — Research & Legacy Mining
# ═══════════════════════════════════════════════════════════════
echo ""
echo "┌────────────────────────────────────────────────────────────┐"
echo "│ P2 — Research & Legacy Mining                              │"
echo "└────────────────────────────────────────────────────────────┘"

clone_p2() {
    local name="$1"
    local url="$2"
    
    if [[ -d "${name}" ]]; then
        echo "  ⏭️  ${name} already exists, pulling latest..."
        cd "${name}" && git pull --ff-only && cd ..
    else
        echo "  📥 Cloning ${name}..."
        git clone "${url}" "${name}"
    fi
}

clone_p2 "Quake-III-Arena"  "https://github.com/id-Software/Quake-III-Arena.git"
clone_p2 "Quake-2"           "https://github.com/id-Software/Quake-2.git"
clone_p2 "DOOM-3"            "https://github.com/id-Software/DOOM-3.git"
clone_p2 "chocolate-doom"    "https://github.com/chocolate-doom/chocolate-doom.git"
clone_p2 "omega-stack-legacy" "https://github.com/Xoe-NovAi/omega-stack-legacy.git"
clone_p2 "xna-omega-legacy"  "https://github.com/Xoe-NovAi/xna-omega-legacy.git"

# ═══════════════════════════════════════════════════════════════
# P3 — Ecosystem & Tooling
# ═══════════════════════════════════════════════════════════════
echo ""
echo "┌────────────────────────────────────────────────────────────┐"
echo "│ P3 — Ecosystem & Tooling                                   │"
echo "└────────────────────────────────────────────────────────────┘"

clone_p3() {
    local name="$1"
    local url="$2"
    
    if [[ -d "${name}" ]]; then
        echo "  ⏭️  ${name} already exists, pulling latest..."
        cd "${name}" && git pull --ff-only && cd ..
    else
        echo "  📥 Cloning ${name}..."
        git clone "${url}" "${name}"
    fi
}

clone_p3 "sqlite-vec-hnsw"  "https://github.com/brianmacy/sqlite-vec-hnsw.git"
clone_p3 "better-sqlite3"   "https://github.com/WiseLibs/better-sqlite3.git"
clone_p3 "litestream"        "https://github.com/benbjohnson/litestream.git"
clone_p3 "sqlite-anyio"     "https://github.com/davidbrochart/sqlite-anyio.git"

# ═══════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Clone Complete — 19 repositories in third-party/        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Directory structure:"
ls -1 "${THIRD_PARTY_DIR}" | sed 's/^/  /'
echo ""
echo "📖 See THIRD_PARTY_REPOS.md for heritage tags, usage patterns, and M14 compliance."