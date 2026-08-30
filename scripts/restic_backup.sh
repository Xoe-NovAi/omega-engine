#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ MAAT ⬡ RESTIC_BACKUP ⬡ v1.0.0 ⬡ 2026-07-22
#
# Daily backup script for Omega Engine using restic
# Reads credentials from VaultCore (V-1)
# Runs via systemd timer (randomized 3am ± 15min)
#
# Usage: ./restic_backup.sh [--dry-run]
#
# Environment:
#   OMEGA_VAULT_PASSPHRASE - Vault passphrase (required)
#   OMEGA_VAULT_DIR - Vault directory (default: data/vault)
#   HEALTHCHECK_URL - Healthchecks.io ping URL (optional)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VAULT_DIR="${OMEGA_VAULT_DIR:-${PROJECT_ROOT}/data/vault}"
LOG_FILE="${PROJECT_ROOT}/data/logs/restic_backup.log"
EXCLUDE_FILE="${PROJECT_ROOT}/config/omega/restic_exclude.txt"
HEALTHCHECK_URL="${HEALTHCHECK_URL:-}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date -u +'%Y-%m-%dT%H:%M:%SZ')]${NC} $*" | tee -a "${LOG_FILE}"; }
log_ok() { echo -e "${GREEN}[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ✓${NC} $*" | tee -a "${LOG_FILE}"; }
log_warn() { echo -e "${YELLOW}[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ⚠${NC} $*" | tee -a "${LOG_FILE}"; }
log_err() { echo -e "${RED}[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ✗${NC} $*" | tee -a "${LOG_FILE}"; }

ping_healthcheck() {
    local status="$1"
    if [[ -n "${HEALTHCHECK_URL}" ]]; then
        curl -fsS -m 10 --retry 3 "${HEALTHCHECK_URL}/${status}" >/dev/null 2>&1 || true
    fi
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || { log_err "Required command '$1' not found"; exit 1; }
}

sqlite_backup() {
    local db_path="$1"
    local backup_dir="$2"
    
    if [[ -f "${db_path}" ]]; then
        log "Backing up SQLite database: ${db_path}"
        local backup_file="${backup_dir}/$(basename "${db_path}").backup"
        sqlite3 "${db_path}" ".backup '${backup_file}'" 2>&1 | tee -a "${LOG_FILE}"
        log_ok "SQLite backup: ${backup_file}"
    else
        log_warn "Database not found: ${db_path}"
    fi
}

qdrant_snapshot() {
    local collection="$1"
    local qdrant_url="${QDRANT_URL:-http://localhost:6333}"
    
    log "Creating Qdrant snapshot for collection: ${collection}"
    local response
    response=$(curl -fsS -X POST "${qdrant_url}/collections/${collection}/snapshots" 2>&1) || {
        log_warn "Failed to create Qdrant snapshot for ${collection}"
        return 1
    }
    log_ok "Qdrant snapshot created: ${response}"
}

main() {
    local dry_run=false
    
    for arg in "$@"; do
        case "${arg}" in
            --dry-run) dry_run=true ;;
            *) log_err "Unknown argument: ${arg}"; exit 1 ;;
        esac
    done
    
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    log "═══════════════════════════════════════════════════════════════"
    log "Omega Engine Restic Backup — $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    log "═══════════════════════════════════════════════════════════════"
    
    require_cmd restic
    require_cmd sqlite3
    require_cmd python3
    
    if [[ -z "${OMEGA_VAULT_PASSPHRASE:-}" ]]; then
        log_err "OMEGA_VAULT_PASSPHRASE not set"
        exit 1
    fi
    
    # Load credentials from VaultCore
    log "Loading credentials from VaultCore..."
    local restic_password b2_key_id b2_app_key
    restic_password=$(cd "${PROJECT_ROOT}" && python3 -c "
import anyio, sys
sys.path.insert(0, 'src')
from omega.vault.vault_core import VaultCore
from pathlib import Path
async def get_cred(key):
    vault = VaultCore(Path('${VAULT_DIR}'), '${OMEGA_VAULT_PASSPHRASE}')
    return await vault.retrieve(key)
result = anyio.run(get_cred, 'restic_password')
print(result or '')
" 2>/dev/null) || true
    
    b2_key_id=$(cd "${PROJECT_ROOT}" && python3 -c "
import anyio, sys
sys.path.insert(0, 'src')
from omega.vault.vault_core import VaultCore
from pathlib import Path
async def get_cred(key):
    vault = VaultCore(Path('${VAULT_DIR}'), '${OMEGA_VAULT_PASSPHRASE}')
    return await vault.retrieve(key)
result = anyio.run(get_cred, 'b2_key_id')
print(result or '')
" 2>/dev/null) || true
    
    b2_app_key=$(cd "${PROJECT_ROOT}" && python3 -c "
import anyio, sys
sys.path.insert(0, 'src')
from omega.vault.vault_core import VaultCore
from pathlib import Path
async def get_cred(key):
    vault = VaultCore(Path('${VAULT_DIR}'), '${OMEGA_VAULT_PASSPHRASE}')
    return await vault.retrieve(key)
result = anyio.run(get_cred, 'b2_app_key')
print(result or '')
" 2>/dev/null) || true
    
    if [[ -z "${restic_password}" || -z "${b2_key_id}" || -z "${b2_app_key}" ]]; then
        log_err "Failed to retrieve credentials from VaultCore"
        exit 1
    fi
    
    export RESTIC_PASSWORD="${restic_password}"
    export B2_ACCOUNT_ID="${b2_key_id}"
    export B2_ACCOUNT_KEY="${b2_app_key}"
    
    log_ok "Credentials loaded"
    
    # Create staging directory for pre-backup dumps
    local staging_dir
    staging_dir=$(mktemp -d -t omega_backup_XXXXXX)
    log "Staging directory: ${staging_dir}"
    
    # Pre-backup: SQLite databases
    log "Pre-backup: Dumping SQLite databases..."
    sqlite_backup "${PROJECT_ROOT}/data/memory/memory_store.sqlite" "${staging_dir}"
    sqlite_backup "${PROJECT_ROOT}/data/memory/memory_store_wal.sqlite" "${staging_dir}" 2>/dev/null || true
    
    # Pre-backup: Qdrant snapshots
    log "Pre-backup: Creating Qdrant snapshots..."
    qdrant_snapshot "omega_memory" || true
    qdrant_snapshot "omega_entities" || true
    
    # Run restic backup
    local restic_args=(
        backup
        "${PROJECT_ROOT}"
        --exclude-file "${EXCLUDE_FILE}"
        --exclude "${staging_dir}"  # Don't back up staging dir itself
        --verbose
        --compression auto
        --pack-size 128
    )
    
    if [[ "${dry_run}" == "true" ]]; then
        restic_args+=(--dry-run)
        log "DRY RUN MODE"
    fi
    
    log "Running restic backup..."
    if restic "${restic_args[@]}" 2>&1 | tee -a "${LOG_FILE}"; then
        log_ok "Backup completed successfully"
    else
        local exit_code=${PIPESTATUS[0]}
        log_err "Backup failed with exit code ${exit_code}"
        ping_healthcheck "fail"
        exit ${exit_code}
    fi
    
    # Prune old snapshots per retention policy
    log "Applying retention policy (7 daily, 4 weekly, 6 monthly, 1 yearly)..."
    restic forget \
        --keep-daily 7 \
        --keep-weekly 4 \
        --keep-monthly 6 \
        --keep-yearly 1 \
        --prune \
        --verbose 2>&1 | tee -a "${LOG_FILE}"
    
    log_ok "Retention policy applied"
    
    # Verify backup integrity (5% sample)
    log "Verifying backup integrity (5% sample)..."
    restic check --read-data-subset 5% --verbose 2>&1 | tee -a "${LOG_FILE}"
    log_ok "Integrity check passed"
    
    # Cleanup staging
    rm -rf "${staging_dir}"
    log "Staging directory cleaned up"
    
    ping_healthcheck "success"
    log_ok "Backup completed successfully"
}

main "$@"