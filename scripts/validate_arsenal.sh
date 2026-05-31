#!/bin/bash
# 🔱 Omega Arsenal Validator
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ scripts ⬡ VALIDATE-ARSENAL
#
# Validates connectivity and inference for all purified free-tier providers.

# Load .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

validate_provider() {
    local NAME=$1
    local ENDPOINT=$2
    local KEY_VAR=$3
    local MODEL=$4
    local KEY=${!KEY_VAR}

    echo "------------------------------------------------"
    echo "⬡ Testing $NAME ($ENDPOINT)..."

    if [ -z "$KEY" ]; then
        echo "⚠️  Skip: $KEY_VAR not found in environment."
        return
    fi

    # 1. Test Models Endpoint
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT/models" \
      -H "Authorization: Bearer $KEY")

    if [ "$STATUS" -eq 200 ]; then
        echo "✅ Models Endpoint: ONLINE"
    else
        echo "❌ Models Endpoint: FAILED (HTTP $STATUS)"
    fi

    # 2. Test Simple Inference
    echo "⬡ Testing Inference with $MODEL..."
    INF_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT/chat/completions" \
      -H "Authorization: Bearer $KEY" \
      -H "Content-Type: application/json" \
      -d "{\"model\": \"$MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello, Omega Engine.\"}]}")

    if [ "$INF_STATUS" -eq 200 ]; then
        echo "✅ Inference: ONLINE"
    else
        echo "❌ Inference: FAILED (HTTP $INF_STATUS)"
    fi
}

# Provider List
# validate_provider "Name" "Endpoint" "EnvVar" "TestModel"

validate_provider "OpenRouter" "https://openrouter.ai/api/v1" "OPENROUTER_API_KEY" "openrouter/free"
validate_provider "Google AI Studio" "https://generativelanguage.googleapis.com/v1beta/openai" "GOOGLE_API_KEY" "gemini-2.0-flash"
validate_provider "Groq" "https://api.groq.com/openai/v1" "GROQ_API_KEY" "llama-3.3-70b-versatile"
validate_provider "SambaNova" "https://api.sambanova.ai/v1" "SAMBANOVA_API_KEY" "Meta-Llama-3.1-8B-Instruct"
validate_provider "Together AI" "https://api.together.xyz/v1" "TOGETHER_API_KEY" "mistralai/Mistral-7B-Instruct-v0.1"
validate_provider "OpenCode Zen" "https://opencode.ai/zen/v1" "OPENCODE_ZEN_API_KEY" "opencode/gpt-5-nano"
validate_provider "GenAI Labs" "https://api.genlabs.ai/v1" "GENLABS_API_KEY" "gpt-4o"

echo "------------------------------------------------"
echo "🔱 Arsenal Validation Complete."
