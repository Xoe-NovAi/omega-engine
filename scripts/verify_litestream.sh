#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# Litestream backup health check — verify replication is alive and current.
# AP: AP-LITESTREAM-BACKUP-v1.0.0
#
# Usage:  scripts/verify_litestream.sh
#         scripts/verify_litestream.sh --strict    # exit 1 on any warning
#
# Exit codes:
#   0  — OK (replication current, service running, integrity good)
#   1  — WARNING (replication lag > 5min, or no snapshots in 24h)
#   2  — ERROR (service down, or integrity check failed)
#   3  — CRITICAL (cannot find litestream binary, or no DB present)
set -uo pipefail

STRICT=0
[[ "${1:-}" == "--strict" ]] && STRICT=1

LITESTREAM_CONFIG="${LITESTREAM_CONFIG:-/etc/litestream.yml}"
OMEGA_MEMORY_DB="${OMEGA_MEMORY_DB:-/var/lib/omega/omega_memory.db}"
MAX_LAG_SECONDS="${MAX_LAG_SECONDS:-300}"   # 5 min — warn if older
MAX_AGE_HOURS="${MAX_AGE_HOURS:-24}"        # 24h — warn if no snapshot

# ── Helpers ──────────────────────────────────────────────────────────────
fail() { echo "  ✗ $*" >&2; }
ok()   { echo "  ✓ $*"; }
warn() { echo "  ! $*"; }
section() { echo; echo "── $* ──"; }

EXIT_CODE=0

# ── 1. Binary present ────────────────────────────────────────────────────
section "Litestream binary"
if ! command -v litestream >/dev/null 2>&1; then
    fail "litestream not on PATH (run scripts/setup_litestream.sh)"
    exit 3
fi
LITESTREAM_VERSION="$(litestream version 2>/dev/null | head -1 || echo 'unknown')"
ok "litestream installed: ${LITESTREAM_VERSION}"

# ── 2. Service running ───────────────────────────────────────────────────
section "systemd service"
if command -v systemctl >/dev/null 2>&1; then
    if systemctl is-active --quiet litestream.service 2>/dev/null; then
        ok "litestream.service is active"
    else
        fail "litestream.service is NOT active (sudo systemctl status litestream)"
        EXIT_CODE=2
        if [[ $STRICT -eq 1 ]]; then exit 2; fi
    fi
else
    warn "systemctl not available — skipping service check (non-systemd host?)"
fi

# ── 3. Config present + parseable ────────────────────────────────────────
section "Configuration"
if [[ ! -f "${LITESTREAM_CONFIG}" ]]; then
    fail "Config not found: ${LITESTREAM_CONFIG}"
    exit 3
fi
ok "Config present: ${LITESTREAM_CONFIG}"

# Required env vars (read from systemd EnvironmentFile)
ENV_FILE="/etc/litestream.env"
if [[ ! -f "${ENV_FILE}" ]]; then
    warn "Env file ${ENV_FILE} not present (creds may be in systemd unit instead)"
else
    # shellcheck disable=SC1090
    set -a; source "${ENV_FILE}"; set +a
    if [[ -z "${LITESTREAM_BUCKET:-}" ]]; then
        fail "LITESTREAM_BUCKET not set"
        EXIT_CODE=1
    else
        ok "LITESTREAM_BUCKET=${LITESTREAM_BUCKET}"
    fi
    if [[ -z "${LITESTREAM_ACCESS_KEY_ID:-}" || -z "${LITESTREAM_SECRET_ACCESS_KEY:-}" ]]; then
        fail "Access credentials not set in ${ENV_FILE}"
        EXIT_CODE=1
    else
        ok "Access credentials set"
    fi
fi

# ── 4. Source database present ───────────────────────────────────────────
section "Source database"
if [[ ! -f "${OMEGA_MEMORY_DB}" ]]; then
    fail "Database not found: ${OMEGA_MEMORY_DB}"
    exit 3
fi
DB_SIZE_BYTES="$(stat -c%s "${OMEGA_MEMORY_DB}" 2>/dev/null || stat -f%z "${OMEGA_MEMORY_DB}")"
ok "DB present: ${OMEGA_MEMORY_DB} (${DB_SIZE_BYTES} bytes)"

# ── 5. Snapshots list (liveness test) ────────────────────────────────────
section "Remote snapshots"
SNAPSHOT_OUTPUT="$(litestream snapshots -config "${LITESTREAM_CONFIG}" 2>&1)" || true
if [[ -z "${SNAPSHOT_OUTPUT}" || "${SNAPSHOT_OUTPUT}" == *"no snapshots"* ]]; then
    fail "No snapshots uploaded yet. Replication may have never started."
    EXIT_CODE=1
else
    # Find newest snapshot timestamp (ISO 8601)
    LATEST_TS="$(echo "${SNAPSHOT_OUTPUT}" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}' | head -1)"
    if [[ -n "${LATEST_TS}" ]]; then
        LATEST_EPOCH="$(date -u -d "${LATEST_TS}" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "${LATEST_TS}" "+%s" 2>/dev/null || echo 0)"
        NOW_EPOCH="$(date -u +%s)"
        LAG=$((NOW_EPOCH - LATEST_EPOCH))
        if [[ $LAG -lt $MAX_LAG_SECONDS ]]; then
            ok "Latest snapshot: ${LATEST_TS} (${LAG}s ago — within threshold)"
        elif [[ $((LAG / 3600)) -lt $MAX_AGE_HOURS ]]; then
            warn "Latest snapshot: ${LATEST_TS} (${LAG}s = ~$((LAG / 60))min ago — exceeds ${MAX_LAG_SECONDS}s)"
            EXIT_CODE=1
        else
            fail "Latest snapshot: ${LATEST_TS} (${LAG}s = ~$((LAG / 3600))h ago — exceeds ${MAX_AGE_HOURS}h)"
            EXIT_CODE=2
        fi
    else
        warn "Could not parse snapshot timestamp from output:"
        echo "${SNAPSHOT_OUTPUT}" | head -5 | sed 's/^/      /'
    fi
fi

# ── 6. Local DB integrity ────────────────────────────────────────────────
section "Local DB integrity"
if command -v sqlite3 >/dev/null 2>&1; then
    INTEGRITY="$(sqlite3 "${OMEGA_MEMORY_DB}" 'PRAGMA integrity_check;' 2>&1)"
    if [[ "${INTEGRITY}" == "ok" ]]; then
        ok "PRAGMA integrity_check = ok"
    else
        fail "PRAGMA integrity_check = ${INTEGRITY}"
        EXIT_CODE=2
    fi
else
    warn "sqlite3 CLI not installed — skipping integrity check"
fi

# ── 7. WAL size sanity (Litestream should keep this bounded) ─────────────
WAL_FILE="${OMEGA_MEMORY_DB}-wal"
if [[ -f "${WAL_FILE}" ]]; then
    WAL_BYTES="$(stat -c%s "${WAL_FILE}" 2>/dev/null || stat -f%z "${WAL_FILE}")"
    WAL_MB=$((WAL_BYTES / 1024 / 1024))
    if [[ $WAL_MB -gt 100 ]]; then
        warn "WAL file is ${WAL_MB}MB (>100MB) — replication may be stalled"
        EXIT_CODE=$(( EXIT_CODE > 1 ? EXIT_CODE : 1 ))
    else
        ok "WAL file: ${WAL_MB}MB (healthy)"
    fi
fi

# ── Summary ──────────────────────────────────────────────────────────────
echo
case $EXIT_CODE in
    0) echo "✓ Litestream backup: HEALTHY" ;;
    1) echo "! Litestream backup: WARNING (investigate)" ;;
    2) echo "✗ Litestream backup: ERROR (action required)" ;;
    *) echo "? Litestream backup: UNKNOWN (exit ${EXIT_CODE})" ;;
esac
exit $EXIT_CODE
