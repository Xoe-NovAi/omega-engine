#!/bin/bash
# 🔱 GenLabs Sovereign Validator
# Use this to test your rotated API key locally without exposing it to AI chat.

if [ -z "$GENLABS_API_KEY" ]; then
    echo "❌ Error: GENLABS_API_KEY not found in environment."
    echo "Please run: export GENLABS_API_KEY=your_rotated_key_here"
    exit 1
fi

echo "⬡ Testing GenLabs Connectivity..."

# 1. Test Models Endpoint
RESPONSE=$(curl -s -w "\n%{http_code}" https://api.genlabs.ai/v1/models \
  -H "Authorization: Bearer $GENLABS_API_KEY")

HTTP_STATUS=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ Models Endpoint: ONLINE"
    echo "Found $(echo "$BODY" | grep -o '"id":' | wc -l) models."
else
    echo "❌ Models Endpoint: FAILED (HTTP $HTTP_STATUS)"
    echo "Body: $BODY"
    exit 1
fi

# 2. Test Simple Inference
echo "⬡ Testing Simple Inference..."
INF_RESPONSE=$(curl -s -w "\n%{http_code}" https://api.genlabs.ai/v1/chat/completions \
  -H "Authorization: Bearer $GENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Hello, Omega Engine."}]}')

INF_STATUS=$(echo "$INF_RESPONSE" | tail -n1)
if [ "$INF_STATUS" -eq 200 ]; then
    echo "✅ Inference: ONLINE"
else
    echo "❌ Inference: FAILED (HTTP $INF_STATUS)"
    exit 1
fi

echo -e "\n🔱 GenLabs Integration Validated. You may now add the key to your .env file."
