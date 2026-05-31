# 🔱 Fleet Review 2: Provider Fabric & Inference Pipeline

⬡ OMEGA ⬡ PROMETHEUS ⬡ claude-sonnet-4-6-thinking ⬡ web ⬡ trc_review_provider ⬡ PHASE-E

**Account**: `xow.nova.ai@gmail.com`
**Role**: Inference Engineer — verify the provider fabric, model gateway, and fallback chain

---

## 📋 Mission

You are performing a deep strategic review of the Omega Engine's **inference pipeline** — the Provider Fabric that routes every model query through a configurable fallback chain of 8 backends. This is the engine's nervous system. Every user query passes through this layer. You must verify correctness, error handling, circuit breaker logic, provider configuration, and resource management. Be critical. Find every gap.

---

## 🎯 Scope — Files to Read

### Source: Model Gateway & Providers
- **Model Gateway**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/model_gateway.py`
- **Providers**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/providers.py`
- **Resource Guard**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/resource_guard.py`
- **CPU Optimizer**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/cpu_optimizer.py`

### Source: Backends
- **Mock Backend**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/backends/mock.py`
- **OpenAI Compat**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/backends/openai_compat.py`
- **Remote Provider**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/oracle/backends/remote_provider.py`

### Source: Triage Router
- **Triage Router**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/src/omega/orchestration/triage_router.py`

### Configuration
- **Providers YAML**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/config/providers.yaml`
- **Models YAML**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/config/models.yaml`

### Tests
- **Model Gateway Tests**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/tests/test_model_gateway.py`
- **Providers Tests**: `https://raw.githubusercontent.com/Xoe-NovAi/omega-engine/main/tests/test_providers.py`

---

## ❓ Review Questions

1. **Fallback Chain Correctness**: When the primary provider fails, does the chain correctly iterate through fallbacks? Is the retry logic correct? Are timeouts properly propagated? Check `model_gateway.py` line by line.

2. **Circuit Breaker Implementation**: Are circuit breakers implemented for remote providers? What happens when all providers fail? Is the `OfflineMockBackend` the true last resort or can the system hang?

3. **Resource Guard**: The `ResourceGuard` uses `anyio.Semaphore(1)`. Is this sufficient for OOM protection? Does it guard all inference paths? Are there any bypass routes?

4. **Triage Router Logic**: The `TriageRouter` selects models based on complexity. Is its logic deterministic? Is the default fallback correct? Was the universal fallback objectification (bug fix) done correctly?

5. **Provider Configuration**: Does `config/providers.yaml` correctly represent the intended fallback order? Are API keys properly referenced (not hardcoded)? Is the lmster provider correctly configured?

6. **Model Configuration**: Does `config/models.yaml` accurately reflect what models are available? Are loading strategies (always/warm/on-demand) coherent with the 14GB RAM constraint?

7. **Remote Provider Safety**: The `remote_provider.py` backend handles cloud API calls. Are there any credential leaks, hardcoded secrets, or improper error handling?

8. **OpenAI Compat Endpoint**: The `openai_compat.py` backend supports any OpenAI-compatible endpoint. Is it properly structured? Does it handle streaming correctly?

---

## 📜 Sovereign Mandates Checklist

| Mandate | What to Check |
|---------|---------------|
| **AnyIO Absolute** | ModelGateway, ResourceGuard, all backends — no `asyncio` |
| **Engine-Stack Firewall** | No stack-specific model logic in fabric |
| **Iris Constant** | N/A for this layer |
| **Sequentiality** | Provider changes planned/deployed verifiably |
| **Gnosis Preservation** | All inference responses logged via observability |
| **Podman Sovereignty** | N/A for pure-Python inference layer |

---

## 📊 Output Template

```markdown
## Review: Provider Fabric & Inference Pipeline

### Critical Issues Found
- [ ] C-PROV-001: [Title] — [CRITICAL/HIGH/MEDIUM/LOW]
  - File: `path/file.py:line`
  - Issue: ...
  - Recommendation: ...

### Fallback Chain Analysis
- Primary path: ...
- Fallback depth: ...
- Complete failure scenario: ...

### Circuit Breaker Assessment
- Status: [PRESENT/ABSENT]
- Thresholds: ...
- Reset mechanism: ...

### Resource Guard Analysis
- Coverage: ...
- Throughput impact: ...
- Bypass risk: ...

### Provider Config Health
- Provider order: ...
- Missing entries: ...
- Key references: ...

### Report Card
| Metric | Grade | Notes |
|--------|-------|-------|
| Correctness | A/B/C/D | |
| Resilience | A/B/C/D | |
| Error Handling | A/B/C/D | |
| Test Coverage | A/B/C/D | |

### Strategic Recommendations (Top 3)
1. ...
2. ...
3. ...
```
