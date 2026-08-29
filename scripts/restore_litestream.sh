#!/usr/bin/env bash
# Restore omega_memory.db from Litestream S3 backup.
# AP: AP-LITESTREAM-BACKUP-v1.0.0
#
# Usage:
#   sudo ./restore_litestream.sh /tmp/restored.db
#   sudo ./restore_litestream.sh /tmp/restored.db 2026-08-29T03:00:00Z   # PITR
set -euo pipefail

TARGET="${1:-/tmp/omega_memory_restored.db}"
TIMESTAMP="${2:-}"  # Optional: ISO 8601 UTC timestamp for point-in-time
LITESTREAM_CONFIG="${LITESTREAM_CONFIG:-/etc/litestream.yml}"

EXTRA_ARGS=()
if [[ -n "${TIMESTAMP}" ]]; then
    EXTRA_ARGS+=("-timestamp" "${TIMESTAMP}")
fi

# Litestream refuses to overwrite an existing file — safe default.
[[ -f "${TARGET}" ]] && mv "${TARGET}" "${TARGET}.existing-$(date +%s)"

echo "==> Restoring to ${TARGET} ${TIMESTAMP:+(at $TIMESTAMP)}..."
sudo litestream restore -config "${LITESTREAM_CONFIG}" \
    -o "${TARGET}" "${EXTRA_ARGS[@]}" \
    "${OMEGA_MEMORY_DB:-/var/lib/omega/omega_memory.db}"

# Verify integrity
echo "==> Verifying restored database..."
sqlite3 "${TARGET}" "PRAGMA integrity_check; SELECT COUNT(*) FROM sqlite_master WHERE type='table';"

# Fix ownership
sudo chown omega:omega "${TARGET}" 2>/dev/null || true

echo "==> Restored to ${TARGET}. Integrity check should be 'ok'."
echo "    To replace the live DB:"
echo "      sudo systemctl stop omega-engine"
echo "      sudo mv /var/lib/omega/omega_memory.db /var/lib/omega/omega_memory.db.broken"
echo "      sudo mv /var/lib/omega/omega_memory.db-wal /var/lib/omega/omega_memory.db-wal.broken 2>/dev/null || true"
echo "      sudo mv /var/lib/omega/omega_memory.db-shm /var/lib/omega/omega_memory.db-shm.broken 2>/dev/null || true"
echo "      sudo mv ${TARGET} /var/lib/omega/omega_memory.db"
echo "      sudo chown omega:omega /var/lib/omega/omega_memory.db*"
echo "      sudo systemctl start omega-engine"
