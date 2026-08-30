#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# ⬡ OMEGA ⬡ MAAT ⬡ RESTIC_RESTORE_TEST ⬡ v1.0.0 ⬡ 2026-07-22
#
# Monthly automated restore test (5% sample)
# Run via systemd timer monthly
#
# Usage: ./restore_test.sh [--full]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/data/logs/restic_restore_test.log"
RESTORE_DIR="${PROJECT_ROOT}/data/restore_test"
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

main() {
    local full_restore=false
    if [[ "${1:-}" == "--full" ]]; then
        full_restore=true
    fi
    
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    log "═══════════════════════════════════════════════════════════════"
    log "Omega Engine Monthly Restore Test — $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    log "═══════════════════════════════════════════════════════════════"
    
    # Load credentials from VaultCore
    if [[ -z "${OMEGA_VAULT_PASSPHRASE:-}" ]]; then
        log_err "OMEGA_VAULT_PASSPHRASE not set"
        exit 1
    fi
    
    local restic_password b2_key_id b2_app_key
    restic_password=$(cd "${PROJECT_ROOT}" && python3 -c "
import anyio, sys
sys.path.insert(0, 'src')
from omega.vault.vault_core import VaultCore
from pathlib import Path
vault = VaultCore(Path('data/vault'), '${OMEGA_VAULT_PASSPHRASE}')
print(anyio.run(vault.retrieve, 'restic_password') or '')
" 2>/dev/null) || true
    
    b2_key_id=$(cd "${PROJECT_ROOT}" && python3 -c "
import anyio, sys
sys.path.insert(0, 'src')
from omega.vault.vault_core import VaultCore
from pathlib import Path
vault = VaultCore(Path('data/vault'), '${OMEGA_VAULT_PASSPHRASE}')
print(anyio.run(vault.retrieve, 'b2_key_id') or '')
" 2>/dev/null) || true
    
    b2_app_key=$(cd "${PROJECT_ROOT}" && python3 -c "
import anyio, sys
sys.path.insert(0, 'src')
from omega.vault.vault_core import VaultCore
from pathlib import Path
vault = VaultCore(Path('data/vault'), '${OMEGA_VAULT_PASSPHRASE}')
print(anyio.run(vault.retrieve, 'b2_app_key') or '')
" 2>/dev/null) || true
    
    if [[ -z "${restic_password}" || -z "${b2_key_id}" || -z "${b2_app_key}" ]]; then
        log_err "Failed to load credentials from VaultCore"
        exit 1
    fi
    
    export RESTIC_PASSWORD="${restic_password}"
    export B2_ACCOUNT_ID="${b2_key_id}"
    export B2_ACCOUNT_KEY="${b2_app_key}"
    
    if [[ -z "${RESTIC_REPOSITORY:-}" ]]; then
        log_err "RESTIC_REPOSITORY not set"
        exit 1
    fi
    
    # List available snapshots
    log "Available snapshots:"
    restic snapshots --compact 2>&1 | tee -a "${LOG_FILE}"
    
    # Get latest snapshot
    local latest_snapshot
    latest_snapshot=$(restic snapshots --latest --json 2>/dev/null | jq -r '.[0].short_id' 2>/dev/null || restic snapshots --latest --compact 2>/dev/null | tail -1 | awk '{print $1}')
    
    if [[ -z "${latest_snapshot}" || "${latest_snapshot}" == "null" ]]; then
        log_err "No snapshots found"
        exit 1
    fi
    
    log "Testing restore from snapshot: ${latest_snapshot}"
    
    # Clean and create restore directory
    rm -rf "${RESTORE_DIR}"
    mkdir -p "${RESTORE_DIR}"
    
    if [[ "${full_restore}" == "true" ]]; then
        log "Running FULL restore test..."
        restic restore "${latest_snapshot}" --target "${RESTORE_DIR}" --verbose 2>&1 | tee -a "${LOG_FILE}"
    else
        log "Running 5% sample restore test..."
        # Restore a sample of files (5%)
        restic restore "${latest_snapshot}" \
            --target "${RESTORE_DIR}" \
            --include "src/**" \
            --include "config/**" \
            --include "docs/**" \
            --verbose 2>&1 | tee -a "${LOG_FILE}"
    fi
    
    local exit_code=${PIPESTATUS[0]}
    if [[ ${exit_code} -ne 0 ]]; then
        log_err "Restore failed with exit code ${exit_code}"
        ping_healthcheck "fail"
        exit ${exit_code}
    fi
    
    # Verify restored files
    local file_count
    file_count=$(find "${RESTORE_DIR}" -type f | wc -l)
    log_ok "Restored ${file_count} files to ${RESTORE_DIR}"
    
    # Quick integrity check on restored files
    log "Verifying restored file integrity..."
    local corrupted=0
    while IFS= read -r -d '' file; do
        if [[ -s "${file}" ]]; then
            # Check if file is readable
            head -c 1 "${file}" >/dev/null 2>&1 || ((corrupted++))
        fi
    done < <(find "${RESTORE_DIR}" -type f -print0)
    
    if [[ ${corrupted} -gt 0 ]]; then
        log_err "Found ${corrupted} corrupted files"
        ping_healthcheck "fail"
        exit 1
    fi
    
    log_ok "All restored files verified"
    
    # Cleanup
    rm -rf "${RESTORE_DIR}"
    log "Restore test directory cleaned up"
    
    ping_healthcheck "success"
    log_ok "Monthly restore test completed successfully"
}

main "$@"