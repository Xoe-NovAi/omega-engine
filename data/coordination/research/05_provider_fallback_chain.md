<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Provider Fallback Chain — Deep Research
**AP Token**: `AP-PROVIDER-FALLBACK-20260726`
**Date**: 2026-07-26 | **Priority**: P0 — Core routing infrastructure
**Researcher**: Sovereign Researcher

---

## Executive Summary

The provider fallback chain design exists in config (`providers.yaml` priority order) but the **actual implementation** of the loop, health pre-check, and circuit breaker state check before dispatch is not wired. The gateway fallback loop needs to be built.

## Current State

- `config/providers.yaml`: Defines priority order (native-gguf → lmster → Ollama → Antigravity → Google → OCZ → OpenRouter)
- `HealthMonitor`: Provides `get_breaker(name)` for per-provider circuit state
- `AdmissionController`: Provides `acquire()` for local admission control
- **Missing**: The actual loop that tries provider N, checks health, falls back to N+1 on failure

## Recommended Architecture

```python
async def fallback_dispatch(prompt, model, providers):
    """Try providers in priority order. First healthy, non-circuit-open wins."""
    for provider in sorted(providers, key=lambda p: p.priority):
        breaker = health_monitor.get_breaker(provider.name)
        if breaker.state == CircuitState.OPEN:
            continue  # Circuit open — skip
        
        if provider.type == "local":
            decision = await admission_controller.acquire(provider.name, model.ram_mb)
            if not decision.granted:
                continue  # OOM risk — skip to cloud
        
        try:
            result = await provider.generate(prompt, model)
            return result  # Success
        except (ProviderError, TimeoutError):
            health_monitor.record_failure(provider.name)
            continue  # Try next provider
    
    raise AllProvidersFailedError("All providers exhausted")
```

## Provider Chain (M7 Local-First)

| Priority | Provider | Type | Breaker Name | Notes |
|----------|----------|------|--------------|-------|
| 0 | native-gguf | Local | `native-gguf` | Qwen3-1.7B, CPU-only |
| 1 | lmster | Local | `lmster` | LM Studio |
| 2 | Ollama | Local | `ollama` | Ollama daemon |
| 3 | Antigravity | Cloud | `antigravity` | OAuth pool, primary cloud |
| 4 | Google | Cloud | `google` | Gemini |
| 5 | OpenCode Zen | Cloud | `opencode-zen` | OCZ |
| 6 | OpenRouter | Cloud | `openrouter` | Multi-model router |

## Integration Points

1. **HealthMonitor.get_breaker(name).state** — check before dispatch
2. **AdmissionController.acquire()** — local admission control
3. **HealthMonitor.record_failure(name)** — on provider error
4. **HealthMonitor.record_success(name)** — on successful response
5. **GenerateResult.provider_name** — actual provider (M22 provenance)
