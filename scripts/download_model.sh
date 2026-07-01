#!/usr/bin/env bash
# 🔱 Omega Engine — Model Download Script
# AP: AP-MODEL-DOWNLOAD-v1.0.0
# Downloads the recommended Qwen 1.7B GGUF for local inference.
# Source: HuggingFace — https://huggingface.co/Qwen/
set -euo pipefail

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'
COLOR_NC='\033[0m'

MODEL_DIR="$(cd "$(dirname "$0")/.." && pwd)/models/gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/resolve/main/qwen3-1.7b-q6_k.gguf"
MODEL_FILENAME="qwen3-1.7b-q6_k.gguf"
MODEL_SIZE_GB="~1.6"
SHA256_URL="https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/resolve/main/qwen3-1.7b-q6_k.gguf.sha256"
SHA256_FILENAME="${MODEL_FILENAME}.sha256"

# ── Pre-flight checks ────────────────────────────────────────────────

echo -e "${COLOR_CYAN}🔱 Omega Engine — Model Download${COLOR_NC}"
echo ""

# Check for curl or wget
if command -v curl &>/dev/null; then
    DL_CMD="curl -L -o"
    DL_PROGRESS="#"
elif command -v wget &>/dev/null; then
    DL_CMD="wget -O"
    DL_PROGRESS="--show-progress"
else
    echo -e "${COLOR_RED}❌ Need curl or wget to download models.${COLOR_NC}"
    echo "  Install one and try again."
    exit 1
fi

# Check disk space
mkdir -p "$MODEL_DIR"
AVAILABLE_KB=$(df "$MODEL_DIR" | awk 'NR==2 {print $4}')
AVAILABLE_GB=$((AVAILABLE_KB / 1024 / 1024))
NEEDED_GB=3
if [ "$AVAILABLE_GB" -lt "$NEEDED_GB" ]; then
    echo -e "${COLOR_RED}❌ Insufficient disk space. Need ~3GB, have ${AVAILABLE_GB}GB.${COLOR_NC}"
    echo "  Free some space or specify a different model directory."
    exit 1
fi
echo -e "  Disk: ${AVAILABLE_GB}GB available (need ~3GB for download + decompress)"
echo ""

# ── Check if already downloaded ──────────────────────────────────────

if [ -f "${MODEL_DIR}/${MODEL_FILENAME}" ]; then
    FILE_SIZE_MB=$(du -m "${MODEL_DIR}/${MODEL_FILENAME}" | cut -f1)
    echo -e "${COLOR_GREEN}✅ Model already exists: ${MODEL_DIR}/${MODEL_FILENAME} (${FILE_SIZE_MB}MB)${COLOR_NC}"
    echo "  Run 'make model-clean' to re-download."
    exit 0
fi

# ── Download ─────────────────────────────────────────────────────────

echo -e "${COLOR_YELLOW}📥 Downloading ${MODEL_FILENAME}${COLOR_NC}"
echo -e "  URL: ${MODEL_URL}"
echo -e "  Size: ${MODEL_SIZE_GB}"
echo -e "  To: ${MODEL_DIR}/"
echo ""
echo -e "  This is the recommended local model for Omega Engine."
echo -e "  It runs entirely on CPU (~2GB RAM) with no GPU required."
echo ""

if echo "$DL_CMD" | grep -q "curl"; then
    curl -L -o "${MODEL_DIR}/${MODEL_FILENAME}" "$MODEL_URL" -#
else
    wget -O "${MODEL_DIR}/${MODEL_FILENAME}" "$MODEL_URL" --show-progress -q
fi

echo ""
echo -e "${COLOR_GREEN}✅ Download complete!${COLOR_NC}"

# ── SHA256 verification (optional) ───────────────────────────────────

echo ""
echo -e "${COLOR_YELLOW}🔍 Verifying checksum...${COLOR_NC}"
if echo "$DL_CMD" | grep -q "curl"; then
    curl -sL "$SHA256_URL" -o "${MODEL_DIR}/${SHA256_FILENAME}" 2>/dev/null || true
else
    wget -q "$SHA256_URL" -O "${MODEL_DIR}/${SHA256_FILENAME}" 2>/dev/null || true
fi

if [ -f "${MODEL_DIR}/${SHA256_FILENAME}" ]; then
    EXPECTED=$(cat "${MODEL_DIR}/${SHA256_FILENAME}" | awk '{print $1}')
    ACTUAL=$(sha256sum "${MODEL_DIR}/${MODEL_FILENAME}" | awk '{print $1}')
    if [ "$EXPECTED" = "$ACTUAL" ]; then
        echo -e "${COLOR_GREEN}✅ SHA256 checksum verified.${COLOR_NC}"
        rm -f "${MODEL_DIR}/${SHA256_FILENAME}"
    else
        echo -e "${COLOR_RED}❌ SHA256 mismatch! File may be corrupted.${COLOR_NC}"
        echo "  Expected: $EXPECTED"
        echo "  Actual:   $ACTUAL"
        echo "  Delete the file and re-download."
        exit 1
    fi
else
    echo -e "${COLOR_YELLOW}⚠️  Could not fetch SHA256 checksum for verification.${COLOR_NC}"
    echo "  File downloaded but not verified. Use at your own risk."
fi

# ── Done ───────────────────────────────────────────────────────────

echo ""
echo -e "${COLOR_GREEN}✅ Model ready at: ${MODEL_DIR}/${MODEL_FILENAME}${COLOR_NC}"
echo ""
echo "  Try it:  omega talk 'hello'"
echo "  Models:   make model-list"
echo "  Clean:    make model-clean"
