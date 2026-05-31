---
name: "provider-validator"
description: "Cross-references config/providers.yaml against live API connectivity and validates curl requests for each provider."
---

# Provider Validator Skill

Use this skill to verify that an inference provider's API endpoint is reachable, correctly authenticated, and returns expected responses.

## Validation Workflow

### Step 1: Load Provider Config
Read `config/providers.yaml` and extract the target provider's entry:
- `base_url` or `detect` field
- `api_key` (resolve `env:` prefix to actual env var)
- `models` list

### Step 2: Health Check
For HTTP-based providers, send a lightweight probe:
```bash
# OpenAI-compatible endpoint
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $API_KEY" \
  "https://api.example.com/v1/models"

# Google AI Studio
curl -s -o /dev/null -w "%{http_code}" \
  "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"
```

### Step 3: Model Availability Check
Verify that the models listed in `providers.yaml` are actually available:
```bash
curl -s -H "Authorization: Bearer $API_KEY" \
  "https://api.example.com/v1/models" | jq '.data[].id'
```

### Step 4: Minimal Inference Test
Send a trivial prompt to verify end-to-end:
```bash
curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"model-name","messages":[{"role":"user","content":"Say hello"}],"max_tokens":10}' \
  "https://api.example.com/v1/chat/completions"
```

### Step 5: Record Results
Document in the corresponding `R##_*.md` file:
- HTTP status codes received
- Response time (ms)
- Any error messages
- Whether the endpoint matches the OpenAI-compatible format or requires a custom adapter

## Important Notes
- **NEVER log API keys** in research documents. Use `$ENV_VAR_NAME` placeholders.
- **Rate limit awareness**: Space validation requests at least 2 seconds apart to avoid hitting free-tier limits.
- If a provider requires a key you don't have, document the expected auth flow and mark the test as SKIPPED.
