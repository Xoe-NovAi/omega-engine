#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Model Download Script
# Downloads qwen3-1.7b-q6_k GGUF with sha256 verification, retry logic, progress bar, disk check
# AP Token: AP-MODEL-DOWNLOAD-v1.0.0

set -euo pipefail

# Configuration
MODEL_REPO="Qwen/Qwen3-1.7B-GGUF"
MODEL_FILE="Qwen3-1.7B-Q6_K.gguf"
MODEL_URL="https://huggingface.co/${MODEL_REPO}/resolve/main/${MODEL_FILE}"
EXPECTED_SHA256="8f3b2c1e9d4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c"  # Placeholder - will be fetched
TARGET_DIR="${OMEGA_MODELS_DIR:-/media/arcana-novai/omega_library/models/gguf}"
MAX_RETRIES=3
RETRY_DELAY=5
MIN_DISK_GB=5

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# Check disk space
check_disk_space() {
    local available_kb=$(df "$TARGET_DIR" 2>/dev/null | tail -1 | awk '{print $4}')
    local available_gb=$((available_kb / 1024 / 1024))
    
    if [[ $available_gb -lt $MIN_DISK_GB ]]; then
        log_error "Insufficient disk space: ${available_gb}GB available, ${MIN_DISK_GB}GB required"
        return 1
    fi
    log_info "Disk space check passed: ${available_gb}GB available"
    return 0
}

# Fetch expected sha256 from Hugging Face
fetch_expected_sha256() {
    log_info "Fetching expected SHA256 from Hugging Face..."
    local api_url="https://huggingface.co/api/models/${MODEL_REPO}"
    local sha256=$(curl -sL "$api_url" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for sibling in data.get('siblings', []):
    if sibling.get('rfilename') == '$MODEL_FILE':
        print(sibling.get('lfs', {}).get('sha256', ''))
        break
" 2>/dev/null || echo "")
    
    if [[ -n "$sha256" && "$sha256" != "None" ]]; then
        EXPECTED_SHA256="$sha256"
        log_info "Expected SHA256: ${EXPECTED_SHA256:0:16}..."
    else
        log_warn "Could not fetch SHA256 from API, will verify after download"
    fi
}

# Download with progress bar and retry
download_model() {
    local attempt=1
    local output_path="$TARGET_DIR/$MODEL_FILE"
    local temp_path="${output_path}.part"
    
    while [[ $attempt -le $MAX_RETRIES ]]; do
        log_info "Download attempt $attempt/$MAX_RETRIES"
        
        # Use curl with progress bar, resume support, and follow redirects
        if curl -L \
            --retry 3 \
            --retry-delay 2 \
            --retry-connrefused \
            --continue-at - \
            --progress-bar \
            --fail \
            -o "$temp_path" \
            "$MODEL_URL"; then
            
            mv "$temp_path" "$output_path"
            log_success "Download completed: $output_path"
            return 0
        else
            log_warn "Download failed (attempt $attempt/$MAX_RETRIES)"
            [[ -f "$temp_path" ]] && rm -f "$temp_path"
            if [[ $attempt -lt $MAX_RETRIES ]]; then
                log_info "Waiting ${RETRY_DELAY}s before retry..."
                sleep $RETRY_DELAY
            fi
            ((attempt++))
        fi
    done
    
    log_error "All download attempts failed"
    return 1
}

# Verify SHA256
verify_sha256() {
    local file_path="$TARGET_DIR/$MODEL_FILE"
    
    if [[ ! -f "$file_path" ]]; then
        log_error "File not found: $file_path"
        return 1
    fi
    
    log_info "Verifying SHA256..."
    local actual_sha256=$(sha256sum "$file_path" | awk '{print $1}')
    
    if [[ "$actual_sha256" == "$EXPECTED_SHA256" ]]; then
        log_success "SHA256 verification PASSED"
        return 0
    else
        log_error "SHA256 verification FAILED"
        log_error "Expected: $EXPECTED_SHA256"
        log_error "Actual:   $actual_sha256"
        return 1
    fi
}

# Main
main() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║     Omega Engine — Model Download Script v1.0.0             ║"
    echo "║     Model: qwen3-1.7b-q6_k.gguf                             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    
    # Create target directory
    mkdir -p "$TARGET_DIR"
    
    # Check disk space
    check_disk_space || exit 1
    
    # Fetch expected SHA256
    fetch_expected_sha256
    
    # Check if already exists and verified
    if [[ -f "$TARGET_DIR/$MODEL_FILE" ]]; then
        log_info "Model file already exists, verifying..."
        if verify_sha256; then
            log_success "Model already present and verified"
            exit 0
        else
            log_warn "Existing file failed verification, re-downloading..."
        fi
    fi
    
    # Download
    download_model || exit 1
    
    # Verify
    verify_sha256 || exit 1
    
    # Final info
    local size_mb=$(du -m "$TARGET_DIR/$MODEL_FILE" | awk '{print $1}')
    log_success "Model ready: $TARGET_DIR/$MODEL_FILE (${size_mb}MB)"
    log_info "Add to config: model_path = \"$TARGET_DIR/$MODEL_FILE\""
}

main "$@"