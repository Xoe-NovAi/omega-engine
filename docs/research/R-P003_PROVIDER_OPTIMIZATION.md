# 🔱 Omega Engine — Provider Chain Optimization
**AP Token**: `AP-PROVIDER-OPT-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ PROVIDER-OPT

## 1. Current Chain Analysis
**Existing Chain (`providers.yaml`)**:
`native-gguf` (P1) $\rightarrow$ `google` (P2) $\rightarrow$ `lmster` (P3) $\rightarrow$ `ollama` (P4) $\rightarrow$ `mock` (P10)

### Bottlenecks & Issues
1. **Native-GGUF Latency**: On the Ryzen 5700U, native GGUF inference is slow for complex reasoning. Using it as P1 for all queries creates a "sluggish" feel.
2. **Google AI Studio Rate Limits**: The 8-key pool is powerful but can be exhausted by recursive agent loops.
3. **Local Server Redundancy**: `lmster` and `ollama` often serve the same models; having both in the chain adds unnecessary check-latency.

## 2. Proposed Optimized Chain
Instead of a linear fallback, we propose a **Capability-Based Routing** strategy.

### Recommended Priority Order
| Priority | Provider | Use Case | Rationale |
|----------|----------|----------|-----------|
| **P1** | `lmster` | General / Fast | Lowest latency local server; handles most 1B-8B models efficiently. |
| **P2** | `google` | Complex / Reasoning | High-capability remote model (Gemma 4-31B) for architectural tasks. |
| **P3** | `native-gguf` | Sovereign / Offline | Final local fallback; guaranteed availability without server overhead. |
| **P4** | `ollama` | Secondary Local | Backup for `lmster` failures. |
| **P10** | `mock` | Dev/Test | Deterministic responses for CI/CD. |

### Updated `providers.yaml` Recommendation
```yaml
inference:
  strategy: capability_aware
  fallback_chain:
    - provider: lmster
      priority: 1
    - provider: google
      priority: 2
      api_key: env:GEMMA_API_KEY
    - provider: native-gguf
      priority: 3
      model_path: /media/arcana-novai/omega_library/models/gguf/phi-4-mini.gguf
    - provider: ollama
      priority: 4
    - provider: mock
      priority: 10
```

## 3. Google AI Studio (8-Key Pool) Management
To maximize the 8-key pool and avoid `429 Too Many Requests`:

1. **Round-Robin Rotation**: The `GoogleAIProvider` should rotate through the 8 keys on every request.
2. **Circuit Breaker**: If a key returns a 429, mark it as "Cooling Down" for 60 seconds and move to the next key.
3. **Token Budgeting**: Limit remote calls for "Transient" sessions to preserve quota for "Persistent" soul-evolution sessions.

## 4. Fallback Timing & Thresholds
- **Local Server Timeout**: 2.0s (Check `is_available`).
- **Remote API Timeout**: 60.0s.
- **Escalation Trigger**: If `lmster` returns a confidence score $< 0.6$ (via Nova/Iris), automatically escalate to `google` regardless of priority.

---
**Implementation Note for @Cline / @Antigravity**:
Update `ModelGateway._load_provider_fabric` to support the new priority order. Implement key rotation in `GoogleAIProvider.generate`.
