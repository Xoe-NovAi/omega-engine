#!/bin/bash
# 🔱 Omega Engine — Model Download Script
# Purpose: Download the primary local model (Qwen3 1.7B GGUF) with verification.
# Usage: make model-download  OR  ./scripts/download_model.sh

set -e

# --- Configuration ---
MODEL_NAME="Qwen3-1.7B-Q6_K"
MODEL_URL="https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/resolve/main/qwen3-1.7b-q6_k.gguf"

# Resolve model directory: OMEGA_MODELS_DIR env var > relative models/gguf
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODEL_DIR="${OMEGA_MODELS_DIR:-${PROJECT_ROOT}/models/gguf}"
MODEL_PATH="${MODEL_DIR}/${MODEL_NAME}.gguf"

# Colors
COLOR_CYAN='\033[0;36m'
COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[0;33m'
COLOR_NC='\033[0m'

echo -e "${COLOR_CYAN}🔱 Omega Engine Model Downloader${COLOR_NC}"
echo "--------------------------------------------------"
echo "  Model:  ${MODEL_NAME}"
echo "  Target: ${MODEL_PATH}"
echo ""

# 1. Create model directory if needed
mkdir -p "$MODEL_DIR"

# 2. Check Disk Space (need ~2GB for 1.7B Q6_K)
echo -n "Checking disk space... "
FREE_SPACE=$(df -BG "$MODEL_DIR" | awk 'NR==2 {print $4}' | tr -d 'G')
if [ "$FREE_SPACE" -lt 2 ]; then
    echo -e "${COLOR_RED}FAILED${COLOR_NC}"
    echo "Error: Less than 2GB free on ${MODEL_DIR} (${FREE_SPACE}GB available)."
    exit 1
fi
echo -e "${COLOR_GREEN}OK${COLOR_NC} (${FREE_SPACE}GB free)"

# 3. Check if model already exists
if [ -f "$MODEL_PATH" ]; then
    echo -e "${COLOR_GREEN}✅ Model already exists:${COLOR_NC} ${MODEL_PATH}"
    echo "   Size: $(du -h "$MODEL_PATH" | cut -f1)"
    exit 0
fi

# 4. Download with retries and progress
echo -e "Downloading ${MODEL_NAME}..."
MAX_RETRIES=3
COUNT=0
SUCCESS=false

while [ $COUNT -lt $MAX_RETRIES ]; do
    COUNT=$((COUNT + 1))
    echo -n "  Attempt $COUNT/$MAX_RETRIES... "
    if wget --progress=bar:force:noscroll -O "${MODEL_PATH}.tmp" "$MODEL_URL" 2>&1; then
        # Atomic move on success
        mv "${MODEL_PATH}.tmp" "$MODEL_PATH"
        echo -e "${COLOR_GREEN}SUCCESS${COLOR_NC}"
        SUCCESS=true
        break
    else
        echo -e "${COLOR_RED}FAILED${COLOR_NC}"
        rm -f "${MODEL_PATH}.tmp"
        sleep 5
    fi
done

if [ "$SUCCESS" = false ]; then
    echo -e "${COLOR_RED}Error: Failed to download model after $MAX_RETRIES attempts.${COLOR_NC}"
    exit 1
fi

# 5. Verify file is a valid GGUF (check magic bytes)
echo -n "Verifying GGUF format... "
MAGIC=$(xxd -l 4 -p "$MODEL_PATH" 2>/dev/null || echo "00000000")
if [ "$MAGIC" = "47475546" ]; then
    echo -e "${COLOR_GREEN}OK${COLOR_NC} (GGUF magic bytes valid)"
else
    echo -e "${COLOR_YELLOW}WARNING: File may not be a valid GGUF (magic: $MAGIC)${COLOR_NC}"
fi

echo "--------------------------------------------------"
echo -e "${COLOR_GREEN}✅ Model ${MODEL_NAME} installed to ${MODEL_PATH}${COLOR_NC}"
echo "   Size: $(du -h "$MODEL_PATH" | cut -f1)"
echo ""
echo "  Run 'make test' to verify inference works."
