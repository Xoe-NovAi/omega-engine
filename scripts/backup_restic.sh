#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ MAAT ⬡ RESTIC_BACKUP ⬡ v1.0.0 ⬡ 2026-07-22
#
# Restic 3-2-1 Backup Script for Sovereign Data
# Uses VaultCore for credential retrieval
# Target: Backblaze B2 with Object Lock (Compliance Mode)
#
# Usage: ./backup_restic.sh [--dry-run] [--verify]
#
# Environment:
#   OMEGA_VAULT_PASSPHRASE - Vault passphrase (required)
#   OMEGA_VAULT_DIR - Vault directory (default: data/vault)
#   RESTIC_REPOSITORY - B2 repository (e.g., b2:bucket-name:path)
#   RESTIC_PASSWORD - Restic repository password (from VaultCore)
#   B2_ACCOUNT_ID - B2 Key ID (from VaultCore)
#   B2_ACCOUNT_KEY - B2 Application Key (from VaultCore)

set -euo pipefail

# ─── Configuration ──────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VAULT_DIR="${OMEGA_VAULT_DIR:-${PROJECT_ROOT}/data/vault}"
EXCLUDE_FILE="${PROJECT_ROOT}/config/omega/restic_exclude.txt"
BACKUP_LOG="${PROJECT_ROOT}/data/logs/restic_backup.log"
HEALTHCHECK_URL="${HEALTHCHECK_URL:-}"  # Optional: healthchecks.io ping URL

# ─── Colors ──────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date -u +'%Y-%m-%dT%H:%M:%SZ')]${NC} $*" | tee -a "${BACKUP_LOG}"; }
log_ok() { echo -e "${GREEN}[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ✓${NC} $*" | tee -a "${BACKUP_LOG}"; }
log_warn() { echo -e "${YELLOW}[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ⚠${NC} $*" | tee -a "${BACKUP_LOG}"; }
log_err() { echo -e "${RED}[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] ✗${NC} $*" | tee -a "${BACKUP_LOG}"; }

# ─── Helpers ─────────────────────────────────────────────────────────────
ping_healthcheck() {
    local status="$1"
    if [[ -n "${HEALTHCHECK_URL}" ]]; then
        curl -fsS -m 10 --retry 3 "${HEALTHCHECK_URL}/${status}" >/dev/null 2>&1 || true
    fi
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || { log_err "Required command '$1' not found"; exit 1; }
}

# ─── Main ────────────────────────────────────────────────────────────────
main() {
    local dry_run=false
    local verify_only=false
    
    # Parse args
    for arg in "$@"; do
        case "${arg}" in
            --dry-run) dry_run=true ;;
            --verify) verify_only=true ;;
            *) log_err "Unknown argument: ${arg}"; exit 1 ;;
        esac
    done
    
    # Ensure log directory exists
    mkdir -p "$(dirname "${BACKUP_LOG}")"
    
    log "═══════════════════════════════════════════════════════════════"
    log "Omega Engine Restic Backup — $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    log "═══════════════════════════════════════════════════════════════"
    
    # Check required commands
    require_cmd restic
    require_cmd python3
    
    # Load credentials from VaultCore
    log "Loading credentials from VaultCore..."
    if [[ -z "${OMEGA_VAULT_PASSPHRASE:-}" ]]; then
        log_err "OMEGA_VAULT_PASSPHRASE environment variable not set"
        exit 1
    fi
    
    # Retrieve credentials using VaultCore
    local restic_password b2_key_id b2_app_key
    restic_password=$(cd "${PROJECT_ROOT}" && python3 -c "
import anyio
import sys
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
import anyio
import sys
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
import anyio
import sys
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
        log_err "Ensure vault contains: restic_password, b2_key_id, b2_app_key"
        exit 1
    fi
    
    export RESTIC_PASSWORD="${restic_password}"
    export B2_ACCOUNT_ID="${b2_key_id}"
    export B2_ACCOUNT_KEY="${b2_app_key}"
    
    log_ok "Credentials loaded from VaultCore"
    
    # Check repository
    if [[ -z "${RESTIC_REPOSITORY:-}" ]]; then
        log_err "RESTIC_REPOSITORY environment variable not set"
        log_err "Example: b2:my-bucket-name:omega-backups"
        exit 1
    fi
    
    log "Repository: ${RESTIC_REPOSITORY}"
    
    # Initialize repository if needed
    if ! restic snapshots >/dev/null 2>&1; then
        log "Repository not initialized, initializing..."
        if [[ "${dry_run}" == "true" ]]; then
            log_warn "[DRY RUN] Would run: restic init"
        else
            restic init
            log_ok "Repository initialized"
        fi
    fi
    
    # Verify exclude file exists
    if [[ ! -f "${EXCLUDE_FILE}" ]]; then
        log_warn "Exclude file not found: ${EXCLUDE_FILE}, creating default..."
        cat > "${EXCLUDE_FILE}" <<'EOF'
# Restic exclude patterns for Omega Engine
**/cache/**
**/caches/**
**/logs/**
**/tmp/**
**/temp/**
**/__pycache__/**
**/*.pyc
**/*.pyo
**/.pytest_cache/**
**/.mypy_cache/**
**/.ruff_cache/**
**/node_modules/**
**/.git/**
**/locks/**
**/*.lock
**/*.pid
**/*.sock
data/coordination/locks/**
data/coordination/*.lock
data/vault/**
!data/vault/audit.log
EOF
    fi
    
    if [[ "${verify_only}" == "true" ]]; then
        log "Running verification only..."
        verify_backup
        return
    fi
    
    # Run backup
    run_backup "${dry_run}"
    
    # Run prune (retention policy)
    if [[ "${dry_run}" == "false" ]]; then
        run_prune
    fi
    
    # Verify backup integrity
    if [[ "${dry_run}" == "false" ]]; then
        verify_backup
    fi
    
    ping_healthcheck "success"
    log_ok "Backup completed successfully"
}

run_backup() {
    local dry_run="$1"
    
    log "Starting backup..."
    
    local backup_cmd=(
        restic backup
        --exclude-file="${EXCLUDE_FILE}"
        --verbose
        --compression=auto
        "${PROJECT_ROOT}"
    )
    
    if [[ "${dry_run}" == "true" ]]; then
        log_warn "[DRY RUN] Would run: ${backup_cmd[*]}"
        return
    fi
    
    # Run backup with progress
    "${backup_cmd[@]}" 2>&1 | tee -a "${BACKUP_LOG}"
    
    local exit_code=${PIPESTATUS[0]}
    if [[ ${exit_code} -ne 0 ]]; then
        log_err "Backup failed with exit code ${exit_code}"
        ping_healthcheck "fail"
        exit ${exit_code}
    fi
    
    log_ok "Backup completed"
}

run_prune() {
    log "Applying retention policy (7 daily / 4 weekly / 6 monthly / 1 yearly)..."
    
    # Retention: keep 7 daily, 4 weekly, 6 monthly, 1 yearly = max 18 snapshots
    restic forget \
        --keep-daily 7 \
        --keep-weekly 4 \
        --keep-monthly 6 \
        --keep-yearly 1 \
        --prune \
        --verbose 2>&1 | tee -a "${BACKUP_LOG}"
    
    local exit_code=${PIPESTATUS[0]}
    if [[ ${exit_code} -ne 0 ]]; then
        log_err "Prune failed with exit code ${exit_code}"
        exit ${exit_code}
    fi
    
    log_ok "Retention policy applied"
}

verify_backup() {
    log "Verifying backup integrity (--read-data-subset 5%)..."
    
    restic check \
        --read-data-subset=5% \
        --verbose 2>&1 | tee -a "${BACKUP_LOG}"
    
    local exit_code=${PIPESTATUS[0]}
    if [[ ${exit_code} -ne 0 ]]; then
        log_err "Integrity check failed with exit code ${exit_code}"
        exit ${exit_code}
    fi
    
    log_ok "Integrity check passed"
}

# Run main
main "$@"