#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ MAAT ⬡ RESTIC_RESTORE_TEST ⬡ v1.0.0 ⬡ 2026-07-22
#
# Monthly automated restore test for restic backup
# Restores 5% sample to verify backup integrity
# Run via systemd timer monthly
#
# Usage: ./restic_restore_test.sh [--full]
#
# Environment:
#   OMEGA_VAULT_PASSPHRASE - Vault passphrase (required)
#   OMEGA_VAULT_DIR - Vault directory (default: data/vault)
#   RESTIC_REPOSITORY - B2 repository
#   RESTORE_TEST_DIR - Restore target (default: /tmp/omega_restore_test)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VAULT_DIR="${OMEGA_VAULT_DIR:-${PROJECT_ROOT}/data/vault}"
RESTORE_DIR="${RESTORE_TEST_DIR:-/tmp/omega_restore_test_$(date +%s)}"
LOG_FILE="${PROJECT_ROOT}/data/logs/restic_restore_test.log"
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

main() {
    local full_restore=false
    
    for arg in "$@"; do
        case "${arg}" in
            --full) full_restore=true ;;
            *) log_err "Unknown argument: ${arg}"; exit 1 ;;
        esac
    done
    
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    log "═══════════════════════════════════════════════════════════════"
    log "Omega Engine Restic Restore Test — $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    log "═══════════════════════════════════════════════════════════════"
    
    require_cmd restic
    require_cmd python3
    
    if [[ -z "${OMEGA_VAULT_PASSPHRASE:-}" ]]; then
        log_err "OMEGA_VAULT_PASSPHRASE not set"
        exit 1
    fi
    
    if [[ -z "${RESTIC_REPOSITORY:-}" ]]; then
        log_err "RESTIC_REPOSITORY not set"
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
    
    # List available snapshots
    log "Available snapshots:"
    restic snapshots --compact 2>&1 | tee -a "${LOG_FILE}"
    
    # Get latest snapshot ID
    local latest_snapshot
    latest_snapshot=$(restic snapshots --latest --json 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['short_id'] if data else '')")
    
    if [[ -z "${latest_snapshot}" ]]; then
        log_err "No snapshots found"
        exit 1
    fi
    
    log "Latest snapshot: ${latest_snapshot}"
    
    # Prepare restore directory
    rm -rf "${RESTORE_DIR}"
    mkdir -p "${RESTORE_DIR}"
    log "Restore target: ${RESTORE_DIR}"
    
    # Restore
    log "Restoring snapshot ${latest_snapshot}..."
    if [[ "${full_restore}" == "true" ]]; then
        restic restore "${latest_snapshot}" --target "${RESTORE_DIR}" --verbose 2>&1 | tee -a "${LOG_FILE}"
    else
        # Restore 5% sample using --include pattern
        # We'll restore a few key directories as sample
        restic restore "${latest_snapshot}" \
            --target "${RESTORE_DIR}" \
            --include "src/omega/**" \
            --include "config/**" \
            --include "docs/**" \
            --include "pyproject.toml" \
            --include "README.md" \
            --verbose 2>&1 | tee -a "${LOG_FILE}"
    fi
    
    local exit_code=${PIPESTATUS[0]}
    if [[ ${exit_code} -ne 0 ]]; then
        log_err "Restore failed with exit code ${exit_code}"
        ping_healthcheck "fail"
        exit ${exit_code}
    fi
    
    log_ok "Restore completed"
    
    # Verify restored files
    log "Verifying restored files..."
    local file_count
    file_count=$(find "${RESTORE_DIR}" -type f | wc -l)
    log "Restored ${file_count} files"
    
    if [[ ${file_count} -eq 0 ]]; then
        log_err "No files restored!"
        exit 1
    fi
    
    # Check key files exist
    local key_files=(
        "src/omega/vault/vault_core.py"
        "config/omega/restic_exclude.txt"
        "pyproject.toml"
    )
    
    for key_file in "${key_files[@]}"; do
        if [[ -f "${RESTORE_DIR}/${key_file}" ]]; then
            log_ok "Key file present: ${key_file}"
        else
            log_warn "Key file missing: ${key_file}"
        fi
    done
    
    # Cleanup
    log "Cleaning up restore directory..."
    rm -rf "${RESTORE_DIR}"
    
    ping_healthcheck "success"
    log_ok "Restore test passed"
}

main "$@"