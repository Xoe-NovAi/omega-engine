#!/bin/bash
set -e

# Configuration
# Note: Replace with actual URL if this placeholder is incorrect
MODEL_URL="https://huggingface.co/Qwen/Qwen3-1.7B-Instruct-GGUF/resolve/main/qwen3-1.7b-q6_k.gguf"
MODEL_FILENAME="Qwen3-1.7B-Q6_K.gguf"
DOWNLOAD_DIR="/media/arcana-novai/omega_library/models/gguf"

echo "🚀 Starting download of $MODEL_FILENAME..."

# Ensure directory exists
mkdir -p "$DOWNLOAD_DIR"

TARGET_PATH="$DOWNLOAD_DIR/$MODEL_FILENAME"

if [ -f "$TARGET_PATH" ]; then
    echo "✅ Model already exists at $TARGET_PATH. Skipping download."
    exit 0
fi

echo "📥 Downloading from $MODEL_URL..."
wget --continue --tries=3 --progress=bar -O "$TARGET_PATH" "$MODEL_URL"

if [ $? -eq 0 ]; then
    echo "✅ Download complete: $TARGET_PATH"
else
    echo "❌ Download failed."
    exit 1
fi
