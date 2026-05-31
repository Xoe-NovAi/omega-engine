#!/bin/bash
# 🔱 Omega Engine — Sovereign UID Guard
# Prevents and remediates UID drift caused by Podman :U flags.

set -eu

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST_UID=1000
HOST_GID=1000

echo "🛡️  Sovereign UID Guard: Scanning for ownership drift..."
echo "=========================================================="

# 1. Scan for files not owned by host user
DRIFT_FILES=$(find "$PROJECT_ROOT" -maxdepth 4 -not -user "$HOST_UID" -not -path "*/.git/*" -not -path "*/.venv/*" 2>/dev/null | head -n 20)

if [ -z "$DRIFT_FILES" ]; then
    echo "✅ No UID drift detected. All files owned by $HOST_UID."
    exit 0
fi

echo "🚨 SOVEREIGN BOUNDARY VIOLATION: UID Drift Detected!"
echo "The following files are owned by container UIDs (e.g., 100999):"
echo "$DRIFT_FILES"
echo "..."
echo ""
echo "🛠️  Initiating automatic reclamation via podman unshare..."

# 2. Reclaim ownership
if command -v podman &> /dev/null; then
    podman unshare chown -R "$HOST_UID:$HOST_GID" "$PROJECT_ROOT"
    echo "✓ Reclamation command executed."
else
    echo "❌ Error: podman not found. Cannot reclaim files automatically."
    exit 1
fi

# 3. Final Verification
FINAL_CHECK=$(find "$PROJECT_ROOT" -maxdepth 4 -not -user "$HOST_UID" -not -path "*/.git/*" -not -path "*/.venv/*" 2>/dev/null)

if [ -z "$FINAL_CHECK" ]; then
    echo "✅ Drift successfully remediated. Ownership restored to $HOST_UID."
else
    echo "❌ Reclamation failed. Some files still have incorrect ownership."
    echo "$FINAL_CHECK"
    exit 1
fi
