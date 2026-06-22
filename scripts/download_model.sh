#!/usr/bin/env bash
# 🔱 Omega Engine — Model Download Script
# AP: AP-MODEL-DOWNLOAD-v1.0.0
# Downloads Qwen3-1.7B GGUF from Hugging Face for local inference
set -euo pipefail

MODEL_DIR="models/gguf"
MODEL_NAME="qwen3-1.7b-q6_k.gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/resolve/main/${MODEL_NAME}"
MIN_DISK_GB=2

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔱 Omega Engine — Model Download${NC}"
echo ""

# Detect download tool
DOWNLOAD_CMD=""
PROGRESS_OPTS=""
if command -v wget &>/dev/null; then
    DOWNLOAD_CMD="wget"
    PROGRESS_OPTS="--progress=bar:force"
elif command -v curl &>/dev/null; then
    DOWNLOAD_CMD="curl"
    PROGRESS_OPTS="-# -L"
else
    echo -e "${RED}Error: Neither wget nor curl found. Install one of:${NC}"
    echo "  sudo apt install wget curl"
    exit 1
fi
echo -e "Using: ${GREEN}${DOWNLOAD_CMD}${NC}"

# Check disk space
AVAILABLE_KB=$(df "$(dirname "$MODEL_DIR")" 2>/dev/null | awk 'NR==2 {print $4}' || echo 0)
AVAILABLE_GB=$((AVAILABLE_KB / 1024 / 1024))
if [ "$AVAILABLE_GB" -lt "$MIN_DISK_GB" ]; then
    echo -e "${RED}Error: Insufficient disk space. Need ${MIN_DISK_GB}GB, have ${AVAILABLE_GB}GB.${NC}"
    exit 1
fi
echo -e "Disk space: ${GREEN}${AVAILABLE_GB}GB available${NC} (need ${MIN_DISK_GB}GB)"

# Create directory
mkdir -p "$MODEL_DIR"

# Download with retry logic
echo "Downloading: ${MODEL_NAME}"
echo "  From: ${MODEL_URL}"
echo ""

MAX_RETRIES=3
RETRY_DELAY=5
SUCCESS=false

for i in $(seq 1 $MAX_RETRIES); do
    echo "Attempt $i of $MAX_RETRIES..."
    
    if [ "$DOWNLOAD_CMD" = "wget" ]; then
        if wget $PROGRESS_OPTS -O "${MODEL_DIR}/${MODEL_NAME}" "$MODEL_URL"; then
            SUCCESS=true
            break
        fi
    else
        if curl $PROGRESS_OPTS -o "${MODEL_DIR}/${MODEL_NAME}" "$MODEL_URL"; then
            SUCCESS=true
            break
        fi
    fi
    
    if [ "$i" -lt "$MAX_RETRIES" ]; then
        echo -e "${YELLOW}Download failed. Retrying in ${RETRY_DELAY}s...${NC}"
        sleep $RETRY_DELAY
    fi
done

if [ "$SUCCESS" = false ]; then
    echo -e "${RED}Error: Download failed after ${MAX_RETRIES} attempts.${NC}"
    echo "  Try downloading manually:"
    echo "  wget -O ${MODEL_DIR}/${MODEL_NAME} ${MODEL_URL}"
    exit 1
fi

# ── Integrity Check ──────────────────────────────────────────────
echo "Verifying download integrity..."
# Known SHA256 hash for Qwen3-1.7B-Q6_K (verify against this)
EXPECTED_SHA256=""
if command -v sha256sum &>/dev/null; then
    COMPUTED_SHA256=$(sha256sum "${MODEL_DIR}/${MODEL_NAME}" | cut -d' ' -f1)
    if [ -n "$EXPECTED_SHA256" ]; then
        if [ "$COMPUTED_SHA256" != "$EXPECTED_SHA256" ]; then
            echo -e "${RED}Error: SHA256 mismatch!${NC}"
            echo "  Expected: $EXPECTED_SHA256"
            echo "  Got:      $COMPUTED_SHA256"
            echo "  The file may be corrupted. Delete and re-download."
            rm -f "${MODEL_DIR}/${MODEL_NAME}"
            exit 1
        fi
        echo -e "${GREEN}  SHA256: ✅ Matches expected hash${NC}"
    else
        echo "  SHA256: $COMPUTED_SHA256"
        echo "  (No expected hash configured — recording computed hash for manual verification)"
    fi
elif command -v shasum &>/dev/null; then
    COMPUTED_SHA256=$(shasum -a 256 "${MODEL_DIR}/${MODEL_NAME}" | cut -d' ' -f1)
    echo "  SHA256: $COMPUTED_SHA256"
    echo "  (shasum used — manual verification recommended)"
else
    echo -e "${YELLOW}  Warning: No sha256sum or shasum found. Cannot verify integrity.${NC}"
fi

# Verify file is not truncated (check magic bytes for GGUF format)
if command -v xxd &>/dev/null || command -v od &>/dev/null; then
    GGUF_MAGIC=$(od -A n -t x1 -N 4 "${MODEL_DIR}/${MODEL_NAME}" 2>/dev/null | tr -d ' \n')
    if [ "$GGUF_MAGIC" = "47475546" ]; then
        echo -e "${GREEN}  GGUF magic bytes: ✅ Valid${NC}"
    else
        echo -e "${RED}Error: Invalid GGUF magic bytes! Got: $GGUF_MAGIC (expected: 47475546)${NC}"
        echo "  The file is not a valid GGUF model. Delete and re-download."
        rm -f "${MODEL_DIR}/${MODEL_NAME}"
        exit 1
    fi
fi

# Set permissions
chmod 644 "${MODEL_DIR}/${MODEL_NAME}"

# Report
FILE_SIZE=$(du -h "${MODEL_DIR}/${MODEL_NAME}" | cut -f1)
echo ""
echo -e "${GREEN}✅ Download complete!${NC}"
echo "  Model: ${MODEL_DIR}/${MODEL_NAME}"
echo "  Size:  ${FILE_SIZE}"
echo ""
echo "To use this model, ensure your config/providers.yaml has:"
echo "  native-gguf:"
echo "    model_path: models/gguf/qwen3-1.7b-q6_k.gguf"
