#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Heritage Vet Gate — Verify all [id-soft:] tags have vet records
# ⬡ OMEGA ⬡ KALI ⬡ heritage_vet ⬡ v1.0.0
#
# Usage: ./scripts/heritage_vet.sh
# Called by: make heritage-vet
#
# Each [id-soft:] tag in src/omega/ must have a corresponding record
# in data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md
# that is either ADOPT, ADAPT, or REJECTED.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
VET_LOG="$REPO_DIR/data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md"
FAIL=0

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e " 🏛️  Heritage Vet Gate — All [id-soft:] tags must have vet records"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -f "$VET_LOG" ]; then
    echo -e "  ${RED}❌ HERITAGE_VET_LOG.md not found at $VET_LOG${NC}"
    echo -e "  ${YELLOW}Run 'make heritage-vet-create' first, see docs/strategy/HERITAGE_VETTING_PIPELINE.md${NC}"
    exit 1
fi

# Find all Python files with heritage tags
for f in $(find "$REPO_DIR/src/omega" -name '*.py' \
    -path '*/oracle/*' -o \
    -name '*.py' -path '*/omega/constants.py' -o \
    -name '*.py' -path '*/omega/cvar_table.py' -o \
    -name '*.py' -path '*/omega/observability.py'); do
    # Extract each [id-soft:] pattern from the file
    while IFS= read -r tagline; do
        pattern=$(echo "$tagline" | sed -n 's/.*\[id-soft: \([^]]*\)\].*/\1/p')
        if [ -n "$pattern" ]; then
            # Check if this pattern appears in the vet log
            if ! grep -qi "$pattern" "$VET_LOG" 2>/dev/null; then
                echo -e "  ${RED}❌ Unvetted tag${NC}: [id-soft: $pattern] in $(basename "$f")"
                FAIL=$((FAIL + 1))
            fi
        fi
    done < <(grep '\[id-soft:' "$f" 2>/dev/null || true)
done

echo ""
if [ "$FAIL" -gt 0 ]; then
    echo -e "  ${RED}❌ $FAIL unvetted heritage tag(s) found.${NC}"
    echo -e "  ${YELLOW}Each [id-soft:] tag must have a corresponding vet record in HERITAGE_VET_LOG.md${NC}"
    echo -e "  ${YELLOW}See the Heritage Vetting Pipeline: docs/strategy/HERITAGE_VETTING_PIPELINE.md${NC}"
    exit 1
else
    echo -e "  ${GREEN}✅ All heritage tags have vet records. Heritage Vetting Pipeline compliant.${NC}"
fi
echo ""
