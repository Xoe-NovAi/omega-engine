# 🔱 Omega Engine — R-P001: Unified Provider Configuration Guide
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_anchor ⬡ KNOWLEDGE-ANCHOR

**AP Token**: `AP-KNOWLEDGE-ANCHOR-v1.0.0`
**Status**: ✅ ACTIVE
**Last Updated**: 2026-05-15
**Target**: Provider Fabric Implementation & User Configuration

---

## 1. Overview
The Omega Engine utilizes a **Provider Fabric** to ensure high-capability reasoning and local sovereignty. This guide defines the configuration standards for integrating local (Sovereign) and remote (Frontier) inference backends.

## 2. Configuration Patterns

### 2.1 Provider Fabric Schema (`config/providers.yaml`)
The primary configuration for the `ModelGateway` follows this YAML structure:

```yaml
inference:
  strategy: local_first # Options: local_first, cloud_priority, balanced
  fallback_chain:
    - provider: native-gguf
      priority: 1
      model_path: /path/to/model.gguf
      n_ctx: 4096
    - provider: google
      priority: 2
      api_key: env:GEMMA_API_KEY
      n_ctx: 4096
    - provider: lmster
      priority: 3
      endpoint: http://127.0.0.1:1234/v1
    - provider: ollama
      priority: 4
      endpoint: http://127.0.0.1:11434/v1
    - provider: mock
      priority: 10
      enabled: true
```

### 2.2 Authentication & Secret Management
Secrets are managed via environment variables or a local `auth.json` for specialized tools.

**Environment Variable Pattern**:
- `GEMMA_API_KEY`: For Google AI Studio.
- `CEREBRAS_API_KEY`: For Cerebras.
- `SAMBANOVA_API_KEY`: For SambaNova.

**`auth.json` Structure (Optional)**:
```json
{
  "providers": {
    "google": { "key": "AIza...", "project": "omega-engine" },
    "cerebras": { "key": "c-..." },
    "sambanova": { "key": "sn-..." }
  }
}
```

### 2.3 OpenCode Provider Block (`opencode.json`)
For OpenCode agents to utilize the Engine as a backend, use the following provider block:

```json
{
  "providers": {
    "omega": {
      "type": "openai",
      "baseUrl": "http://127.0.0.1:8080/v1",
      "apiKey": "omega-sovereign-token",
      "models": ["SOPHIA", "MAAT", "LILITH", "PROMETHEUS"]
    }
  }
}
```

---

## 3. Connectivity & Validation

### 3.1 Connectivity Tests (cURL)

| Provider | Validation Command | Expected Result |
| :--- | :--- | :--- |
| **Google** | `curl https://generativelanguage.googleapis.com/v1beta/openai/models -H "Authorization: Bearer $GEMMA_API_KEY"` | JSON list of Gemini models |
| **Cerebras** | `curl https://api.cerebras.ai/v1/models -H "Authorization: Bearer $CEREBRAS_API_KEY"` | JSON list of Llama/Qwen models |
| **SambaNova** | `curl https://api.sambanova.ai/v1/models -H "Authorization: Bearer $SAMBANOVA_API_KEY"` | JSON list of DeepSeek models |
| **lmster** | `curl http://127.0.0.1:1234/v1/models` | JSON list of loaded GGUFs |
| **Ollama** | `curl http://127.0.0.1:11434/api/tags` | JSON list of Ollama models |

---

## 4. Cross-References
- **R-01**: Google AI Studio API Reference
- **R-02**: SambaNova Integration Spec
- **R-03**: Cerebras Integration Spec
- **R-04**: Provider Fabric Fallback Chain Design
- **Implementation**: `src/omega/oracle/model_gateway.py`

---
**Implementation Note**: Ensure that `env:` prefix in `providers.yaml` is correctly parsed by the `ModelGateway` to load variables from the system environment before initializing the provider client.
