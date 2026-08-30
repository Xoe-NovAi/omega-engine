#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Upload All — Omega Hub Claude Project Knowledge Files
# Run this script to populate the outbox/ folder with all files
# needed for Claude.ai Project Knowledge.
#
# Usage: bash upload-all.sh
# Then open the outbox/ folder and drag all files into Claude.ai Project Knowledge.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTBOX="$HERE/outbox"
SRC="$HERE/.."  # docs/hardening/omega-hub/

echo "🔱 Populating Claude.ai outbox..."
echo "Source: $SRC"
echo "Outbox: $OUTBOX"
echo ""

# Empty and recreate outbox
rm -rf "$OUTBOX"
mkdir -p "$OUTBOX"

# --- New extract files (lowercase names) ---
echo "  [1/15] hub-system-overview.md ........... $(wc -l < "$SRC/hub-system-overview.md") lines"
cp "$SRC/hub-system-overview.md" "$OUTBOX/"

echo "  [2/15] target-module-architecture.md ..... $(wc -l < "$SRC/target-module-architecture.md") lines"
cp "$SRC/target-module-architecture.md" "$OUTBOX/"

echo "  [3/15] carmack-audit-findings.md ......... $(wc -l < "$SRC/carmack-audit-findings.md") lines"
cp "$SRC/carmack-audit-findings.md" "$OUTBOX/"

echo "  [4/15] phase-0-fixes.md ................. $(wc -l < "$SRC/phase-0-fixes.md") lines"
cp "$SRC/phase-0-fixes.md" "$OUTBOX/"

echo "  [5/15] m9-compliance-analysis.md ........ $(wc -l < "$SRC/m9-compliance-analysis.md") lines"
cp "$SRC/m9-compliance-analysis.md" "$OUTBOX/"

echo "  [6/15] sovereign-gateway-spec.md ........ $(wc -l < "$SRC/sovereign-gateway-spec.md") lines"
cp "$SRC/sovereign-gateway-spec.md" "$OUTBOX/"

echo "  [7/15] m15-continuity-spec.md ........... $(wc -l < "$SRC/m15-continuity-spec.md") lines"
cp "$SRC/m15-continuity-spec.md" "$OUTBOX/"

echo "  [8/15] search-protocol.md ............... $(wc -l < "$SRC/search-protocol.md") lines"
cp "$SRC/search-protocol.md" "$OUTBOX/"

echo "  [9/15] sovereign-mandates.md ............ $(wc -l < "$SRC/sovereign-mandates.md") lines"
cp "$SRC/sovereign-mandates.md" "$OUTBOX/"

echo " [10/15] temple-grade-gates.md ............ $(wc -l < "$SRC/temple-grade-gates.md") lines"
cp "$SRC/temple-grade-gates.md" "$OUTBOX/"

echo " [11/15] heritage-patterns-in-hub.md ...... $(wc -l < "$SRC/heritage-patterns-in-hub.md") lines"
cp "$SRC/heritage-patterns-in-hub.md" "$OUTBOX/"

# --- Existing files (rename for RAG-friendly flat names) ---
echo " [12/15] carmack-reconstruction-plan.md ... $(wc -l < "$SRC/CARMACK_RECONSTRUCTION_PLAN.md") lines"
cp "$SRC/CARMACK_RECONSTRUCTION_PLAN.md" "$OUTBOX/carmack-reconstruction-plan.md"

echo " [13/15] active-tracker.md ............... $(wc -l < "$SRC/TRACKER.md") lines"
cp "$SRC/TRACKER.md" "$OUTBOX/active-tracker.md"

echo " [14/15] sprint-v2-briefing.md ........... $(wc -l < "$SRC/OMEGA_HUB_HARDENING_SPRINT_v2_20260609.md") lines"
cp "$SRC/OMEGA_HUB_HARDENING_SPRINT_v2_20260609.md" "$OUTBOX/sprint-v2-briefing.md"

echo " [15/15] server-snapshot.py .............. $(wc -l < "$SRC/server_monolith_snapshot_20260613.py") lines"
cp "$SRC/server_monolith_snapshot_20260613.py" "$OUTBOX/server-snapshot.py"

# --- Additional engine files ---
echo " [EXTRA] mcp-runtime.py .................. $(wc -l < "$HERE/../../../../src/omega/mcp_runtime.py") lines"
cp "$HERE/../../../../src/omega/mcp_runtime.py" "$OUTBOX/mcp-runtime.py"

echo ""
echo "✅ Done! Outbox ready at:"
echo "   file://$OUTBOX"
echo ""
echo "=== NEXT STEPS ==="
echo "1. Open the outbox folder in your file manager"
echo "2. Select ALL files in outbox/"
echo "3. Drag into Claude.ai Project Knowledge (the files area)"
echo "4. Open system-prompt.md and paste contents into Custom Instructions"
echo ""
echo "=== FILE COUNT ==="
ls -1 "$OUTBOX" | wc -l | tr -d ' ' | xargs echo "  $OUTBOX files ready for upload"
