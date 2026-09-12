#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Wedge-proof sdist fetch + local source install
# AP: AP-FETCH-SDIST-v1.0.0
# ⬡ OMEGA ⬡ P3 ⬡ build ⬡ RAM-GUARD
#
# WHY THIS EXISTS:
#   `pip download --no-binary :all:` is NOT a cheap metadata fetch —
#   scikit-build-core runs a FULL CMake configure inside PEP 517 metadata
#   extraction, which wedged for 52+ min on llama-cpp-python (2026-08-22).
#   This script fetches the sdist ONCE via curl (cache-friendly), then
#   installs from the local tarball — no metadata dance, no re-resolution.
#
# Usage (from an activated venv):
#   scripts/fetch-sdist.sh llama-cpp-python==0.3.35
#   scripts/fetch-sdist.sh numpy==2.5.2 --no-deps
#
# Cache: ~/.cache/omega-sdists (override via OMEGA_SDIST_CACHE)

set -euo pipefail
SPEC="${1:?usage: fetch-sdist.sh <package>==<version> [extra pip args...]}"; shift
PKG="${SPEC%%==*}"; VER="${SPEC##*==}"
CACHE_DIR="${OMEGA_SDIST_CACHE:-$HOME/.cache/omega-sdists}"
mkdir -p "$CACHE_DIR"

command -v curl >/dev/null || { echo "[ERR] curl required" >&2; exit 1; }

URL=$(curl -fsSL "https://pypi.org/pypi/$PKG/$VER/json" \
      | python3 -c 'import json,sys; d=json.load(sys.stdin); print(next(u["url"] for u in d["urls"] if u["packagetype"]=="sdist"))') \
  || { echo "[ERR] could not resolve sdist URL for $SPEC" >&2; exit 1; }
TGZ="$CACHE_DIR/$(basename "$URL")"

if [ -f "$TGZ" ]; then
    info="cached"
else
    info="downloaded"
    echo "[INFO] fetching $URL"
    curl -fSL --retry 3 "$URL" -o "$TGZ"
fi
echo "[OK] sdist $info: $TGZ"
echo "[INFO] installing from local path (always compiles fresh, zero network re-resolution)"
exec pip install -v --no-deps --force-reinstall "$@" "$TGZ"
