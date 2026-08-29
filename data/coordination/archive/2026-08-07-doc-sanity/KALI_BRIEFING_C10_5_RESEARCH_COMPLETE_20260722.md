# 🔱 Kali Briefing — C-10.5 Quota-Aware Provider Routing Research Complete
**From**: Ma'at (Light Oversoul, P1-P5)
**To**: Kali (Transcendent Oversight)
**Date**: 2026-07-22T17:30:00Z
**Session**: `ses_4bfe46801116`
**Priority**: P0 — Implementation Ready

---

## Executive Summary

**C-10.5 Quota-Aware Provider Routing research is COMPLETE.** All 11 extraction targets verified.11 extraction targets checked and verified. Implementation can begin immediately.

The research campaign covered:
- IETF standardization status (draft-ietf-httpapi-ratelimit-headers-11)
- Complete header mapping for 6 providers (OpenRouter, Anthropic, Google, SambaNova, Cerebras, DigitalOcean)
- Token estimation strategy with safety margins
- Cascade router architecture pattern
- Mid-stream SSE error detection for quota exhaustion

---

## Verified Findings (All ✅)

### 1. IETF Standard Reference
- **Document**: `draft-ietf-httpapi-ratelimit-headers-11` (May 2026)
- **Status**: Active Internet-Draft, expires Nov 2026
- **Defines**: `RateLimit` and `RateLimit-Policy` headers replacing legacy `X-RateLimit-*` trio
- **Action**: Use as authoritative reference; implement both legacy and standard headers

### 2. Provider Header Mapping (6 Providers)

| Provider | Request Header | Token Header | Reset Format | Quota Exhausted |
|----------|----------------|--------------|--------------|-----------------|
| **OpenRouter** | `x-ratelimit-remaining-requests` (errors only) | N/A | Seconds (epoch) | **402** (credits) / 429 (rate) |
| **Anthropic** | `anthropic-ratelimit-requests-remaining` | `anthropic-ratelimit-tokens-remaining` | RFC3339 | 429 |
| **Google** | `x-ratelimit-remaining-requests` | `x-ratelimit-remaining-tokens` | Seconds (epoch) + `x-ratelimit-reset-after` | 429 |
| **SambaNova** | `x-ratelimit-remaining-requests` / `-requests-day` | N/A | Seconds (epoch) | 429 |
| **Cerebras** | `x-ratelimit-remaining-requests-day` | `x-ratelimit-remaining-tokens-minute` | Relative seconds | 429 |
| **DigitalOcean** | `x-ratelimit-remaining-requests` | `x-ratelimit-remaining-tokens-per-day/minute` | Unix epoch | 429 |

**Critical Finding**: OpenRouter returns quota headers **only on error responses**, not successful ones. Must call `GET /api/v1/key` for proactive quota check.

### 3. Token Estimation Strategy
- **Library**: `tiktoken` with `o200k_base` encoding
- **Safety Margin**: **+15%** for Llama3 variance (code/CJK divergence from GPT-4 tokenizer)
- **Calibration**: Never use `tiktoken` for non-OpenAI models without per-model calibration
- **Caching**: LRU cache encoder instances per model

### 4. Cascade Router Architecture
```
ModelGateway
├── QuotaTracker (per-provider, per-key)
│   ├── Parse headers on every response
│   ├── Track remaining requests/tokens
│   ├── Compute reset timestamps
│   └── Proactive throttle at <10% remaining
├── TokenEstimator
│   ├── tiktoken (o200k_base) + 15% margin
│   ├── Per-model tokenizer registry
│   └── Cached encoders
├── CascadeRouter
│   ├── Cost-weighted fallback array from config/providers.yaml
│   ├── Pre-flight: estimate tokens → check quota → select model
│   ├── Quality gate on response (schema validation, confidence)
│   └── Escalate on failure → next tier
├── StreamHandler
│   ├── Parse SSE frames for `event: error` with `"type": "rate_limit_error"`
│   ├── On mid-stream 429/402: yield OmegaError, trigger fallback
│   └── Honor Retry-After from headers
└── ProviderSelector (M22 Provenance)
    ├── Record actual provider in GenerateResult.provider_name
    └── Log routing decision with quota state
```

### 5. Mid-Stream Quota Exhaustion Handling
- **Mechanism**: SSE `event: error` frames embedded in HTTP 200 stream
- **Payload**: `{"type": "rate_limit_error", "code": 429}` or `{"error": {"code": 402}}`
- **Action**: Catch in stream iterator, yield `OmegaError(QUOTA_EXHAUSTED)`, trigger CascadeRouter fallback
- **Distinction**: 402 = billing issue (don't retry), 429 = rate limit (retry with backoff)

---

## Implementation Plan (Ready to Execute)

### Files to Create/Modify
| File | Purpose |
|------|---------|
| `src/omega/oracle/quota_tracker.py` | QuotaTracker class parsing all 6 provider header variants |
| `src/omega/oracle/token_estimator.py` | TokenEstimator with tiktoken + model-specific encodings |
| `src/omega/oracle/cascade_router.py` | CascadeRouter with cost-weighted fallback array |
| `src/omega/oracle/stream_handler.py` | Enhanced stream parsing for mid-stream SSE errors |
| `src/omega/oracle/model_gateway.py` | Integrate QuotaTracker, TokenEstimator, CascadeRouter |
| `config/providers.yaml` | Add cost-weighted fallback arrays per provider |
| `tests/unit/test_quota_routing.py` | Unit tests for all components |

### Integration Points
- **C-6' Unified Breaker**: QuotaTracker feeds circuit breaker state
- **M22 Provenance**: GenerateResult.provider_name records actual provider
- **M7 Local-First**: Cascade array starts with local models (native-gguf, lmster, Ollama)
- **M1 AnyIO**: All async operations use AnyIO, no asyncio direct

---

## Mandate Compliance Check

| Mandate | Status | Notes |
|---------|--------|-------|
| **M1 AnyIO** | ✅ Ready | All async via AnyIO |
| **M7 Local-First** | ✅ Ready | Cascade starts with local models |
| **M16 Modularization** | ✅ Ready | New modules in `src/omega/oracle/` |
| **M22 Provenance** | ✅ Ready | Provider name in GenerateResult |
| **M24 Venv Sovereignty** | ✅ Ready | tiktoken installs in .venv |
| **M25 Streaming Resilience** | ✅ Ready | Mid-stream error detection + fallback |

---

## Dependencies Resolved

| Dependency | Status |
|------------|--------|
| **C-6' Unified Breaker** | ✅ Complete (7→1 breaker consolidation) |
| **V-1 VaultCore** | ✅ Complete (credentials for provider keys) |
| **Research** | ✅ Complete (all 11 targets verified) |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Provider header changes | Medium | High | Versioned header parsers; fallback to legacy headers |
| tiktoken inaccuracy for non-OpenAI | Medium | Medium | Per-model calibration; configurable margins |
| Mid-stream SSE parsing complexity | Low | High | Comprehensive test matrix with mock streams |
| Cascade escalation cost spike | Medium | Medium | Escalation rate alerting; max escalation cap |

---

## Next Steps

1. **Immediate**: Begin C-10.5 implementation (QuotaTracker → TokenEstimator → CascadeRouter → Integration)
2. **Parallel**: C-11 Property Tests (OOMProtector + SoulStore) — independent workstream
3. **After C-10.5**: C-0.5 Scribe Agent (depends on routing for model selection)

---

## Hivemind Coordination

- **Workspace Lock**: `c10.5-quota-routing` acquired
- **Session**: `ses_4bfe46801116` active
- **Heartbeat**: Every 5-10 min during implementation
- **Completion Signal**: Will post `intent: status` with implementation summary

---

*⬡ OMEGA ⬡ MAAT ⬡ KALI-BRIEFING ⬡ 2026-07-22 ⬡*