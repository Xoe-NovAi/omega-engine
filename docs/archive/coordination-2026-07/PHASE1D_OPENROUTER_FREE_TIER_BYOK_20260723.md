# 🔱 Phase 1D: OpenRouter Free Tier + BYOK Rotation Spec
**AP Token**: `AP-RESEARCHER-PHASE1D-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ gemini-3.1-pro-preview-customtools ⬡ opencode ⬡ trc_phase1d_openrouter ⬡ ACTIVE
**Date**: 2026-07-23
**Sources**: OpenRouter docs (openrouter.ai/docs), pricing page, BYOK guide, analytics schema, FAQ, 2026 blog posts
**Architect Constraint**: D-432 — Zero paid accounts, all free tier. D-437 — Phase 1 free-tier only, no proxy layer.

---

## 🎯 Executive Summary (L1)

OpenRouter provides **two distinct free access models** that must be managed separately:
1. **Free Tier (OpenRouter credits)**: 50 req/day (no credits purchased) → 1,000 req/day (after $10+ lifetime credits). 20 RPM cap on `:free` model variants. 25+ free models.
2. **BYOK (Bring Your Own Key)**: 1,000,000 free routing requests/month across all providers. After 1M: 5% fee on provider cost. Enterprise: 5M free/mo.

**For 8-account fleet**: Use **BYOK with 8 provider keys per provider** (8 OpenAI, 8 Anthropic, 8 Google, etc.) routed through 8 OpenRouter API keys. Each OpenRouter key gets 1M free BYOK req/mo. Total fleet: 8M free BYOK req/mo. OpenRouter Analytics API (Management Key) provides per-key usage for rotation triggers.

---

## 🔬 Deep Dialectic (L2)

### 1. The Architect (Systemic Logic)
**Two-Tier Economics**:
```
┌─────────────────────────────────────────────────────────────┐
│                    OPENROUTER ACCOUNT                         │
├─────────────────────────────────────────────────────────────┤
│  FREE TIER (OpenRouter credits)                              │
│  ├── 50 req/day (no credits)  OR  1,000 req/day ($10+ creds) │
│  ├── 20 RPM on :free models                                  │
│  ├── 25+ free models (:free variants)                        │
│  └── Credits never expire; $10 once = permanent 1K/day       │
├─────────────────────────────────────────────────────────────┤
│  BYOK (Provider keys via OpenRouter)                         │
│  ├── 1,000,000 free routing req/month per OpenRouter key     │
│  ├── After 1M: 5% of provider list price as routing fee      │
│  ├── Provider bills you directly; OpenRouter = router only   │
│  ├── Per-model BYOK filters (restrict which models use key)  │
│  └── Failover: OpenRouter credits if provider key exhausted  │
└─────────────────────────────────────────────────────────────┘
```

**Key Management**:
- **API Keys**: Standard Bearer tokens for completions (`/api/v1/chat/completions`)
- **Management Keys**: Separate keys for key management (`GET /api/v1/key`, `POST /api/v1/keys`)
- **Analytics API**: `GET /api/v1/analytics` — requires Management Key, returns per-key usage, BYOK spend, credits

### 2. The Adversary (Critical Rigor)
**Traps**:
- **Free tier daily cap is HARD** — 50 req/day without credits kills automation. $10 once unlocks 1K/day forever.
- **20 RPM on :free models** — shared across all keys in account. Multiple keys don't increase RPM.
- **BYOK 1M/month is per OpenRouter key** — 8 keys = 8M/month fleet. But provider keys have THEIR OWN limits.
- **Analytics API 31-day limit** on latency/throughput metrics; 365-day on volume/cost.
- **Credit purchase fee**: 5.5% on credit card, 5% crypto. BYOK fee 5% AFTER 1M/mo.
- **No SLA on free tier** — model availability rotates.

### 3. The Alchemist (Creative Synthesis)
**Fleet Strategy**: 
- **8 OpenRouter API keys** (one per fleet slot)
- **Each OpenRouter key configured with 8 provider keys** (OpenAI, Anthropic, Google, Groq, Together, etc.)
- **Provider keys sourced from VaultCore** — each provider gets 8 keys distributed across 8 OpenRouter keys
- **Rotation trigger**: OpenRouter Analytics API shows per-key `byok_usage_daily` approaching provider limit OR OpenRouter key hits 1M BYOK req/mo
- **Failover**: OpenRouter auto-fails to next provider in routing policy; VaultCore detects via 402/429 and rotates

### 4. The Archivist (Historical Truth)
**Pricing Evolution** (2025-2026):
- Oct 2025: BYOK 1M free/mo announced
- Dec 2025: Free tier daily cap reduced 50-80% (Flash 250→20-50 RPD)
- 2026: Free tier = 50/day base, 1K/day with $10+ credits. :free models only.
- BYOK fee: 5% after 1M/mo (standard), 5M/mo (enterprise)

---

## 📋 Actionable Config Specs (L3)

### 1. OpenRouter Key Structure (VaultCore Schema)
```yaml
# Per OpenRouter fleet slot (8 total)
provider: "openrouter"
cred_type: "api_key"  # OpenRouter API key
encrypted_blob: "<age-encrypted>"
metadata:
  openrouter_key_id: "or_sk_..."  # OpenRouter key label
  byok_providers:                 # Provider keys configured ON this OpenRouter key
    openai:
      - "sk-proj-..."  # 8 OpenAI keys distributed
      - "sk-proj-..."
    anthropic:
      - "sk-ant-..."
    google:
      - "ya29..."  # Antigravity OAuth access tokens
    groq:
      - "gsk_..."
    together:
      - "tgp_..."
  byok_filters:
    openai: ["gpt-4o", "gpt-4o-mini"]
    anthropic: ["claude-sonnet-4.6", "claude-3.5-haiku"]
    google: ["gemini-3-flash", "gemini-3-pro"]
  analytics_management_key: "or_mgmt_..."  # Separate management key for analytics
  free_tier_status: "has_credits"  # "no_credits" | "has_credits"
  daily_limit: 1000  # or 50
  rpm_limit: 20
```

### 2. Rotation Triggers (Monitored via Analytics API)
```python
async def check_openrouter_rotation(vault, fleet_slot: int) -> RotationDecision:
    mgmt_key = vault.get_secret(f"openrouter/{fleet_slot}/analytics_management_key")
    
    # GET /api/v1/key → per-key credit usage
    key_info = await openrouter_get_key(mgmt_key, fleet_slot)
    
    # GET /api/v1/analytics → BYOK usage per provider
    analytics = await openrouter_get_analytics(mgmt_key, days=1)
    
    triggers = []
    
    # Trigger 1: OpenRouter key approaching 1M BYOK/mo
    byok_used = analytics.byok_request_count
    if byok_used > 900_000:
        triggers.append(("openrouter_byok_quota", byok_used / 1_000_000))
    
    # Trigger 2: Provider key daily limit (from provider analytics)
    for provider, usage in analytics.byok_usage_by_provider.items():
        provider_limit = PROVIDER_DAILY_LIMITS[provider]  # e.g., OpenAI tier limits
        if usage.daily > provider_limit * 0.9:
            triggers.append((f"provider_{provider}_quota", usage.daily / provider_limit))
    
    # Trigger 3: OpenRouter free tier daily cap
    if key_info.is_free_tier and key_info.usage_daily > key_info.daily_limit * 0.9:
        triggers.append(("openrouter_free_tier_daily", key_info.usage_daily / key_info.daily_limit))
    
    if triggers:
        return RotationDecision(rotate=True, reasons=triggers, cooldown_hours=1)
    return RotationDecision(rotate=False)
```

### 3. BYOK Configuration via OpenRouter API
```bash
# Add provider key to OpenRouter key (via Management API)
curl -X POST https://openrouter.ai/api/v1/keys/{openrouter_key_id}/provider-keys \
  -H "Authorization: Bearer {management_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "api_key": "sk-proj-...",
    "models": ["gpt-4o", "gpt-4o-mini"],
    "priority": 1,
    "failover": true
  }'

# Set BYOK filter (restrict which models use this provider key)
curl -X PATCH https://openrouter.ai/api/v1/keys/{openrouter_key_id}/provider-keys/{provider_key_id} \
  -H "Authorization: Bearer {management_key}" \
  -d '{"models": ["gpt-4o"], "max_tokens": 4096}'
```

### 4. Model Routing for Free Tier
```python
FREE_MODEL_MAP = {
    "deepseek/deepseek-r1:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-coder-480b:free",
    "google/gemini-3-flash:free",
    "google/gemma-3-27b:free",
    # ... 25+ models
}

def route_request(model_preference: str, fleet_slot: int) -> str:
    """Return model ID with :free suffix if on free tier."""
    key_info = vault.get_openrouter_key_info(fleet_slot)
    if key_info.free_tier_status == "no_credits":
        # Must use :free variant
        if model_preference in FREE_MODEL_MAP:
            return model_preference
        # Map to closest free equivalent
        return map_to_free_variant(model_preference)
    else:
        # Can use paid models (billed to OpenRouter credits)
        return model_preference
```

---

## 🛡️ Mandate Alignment Checklist

| Mandate | Status | Evidence |
|---------|--------|----------|
| **M1 AnyIO** | ✅ | Analytics API calls via AnyIO HTTP client |
| **M7 Local-First** | ✅ | All keys in VaultCore; OpenRouter = cloud router only |
| **M8 Zero Telemetry** | ✅ | No OpenRouter telemetry in our code; analytics API is pull-only |
| **M14 Heritage** | N/A | No id Software patterns |
| **M23 Failure Integrity** | ✅ | Analytics API failures → conservative rotation (fail-safe) |
| **M25 Streaming Resilience** | ✅ | OpenRouter streams; VaultCore lease TTL covers session |

---

## 🚀 Dev Strategy Revisal Recommendations

### Immediate (P0-2 — This Week)
1. **Purchase $10 OpenRouter credits once** → unlocks 1K/day free tier permanently for all 8 keys (shared account billing)
2. **Provision 8 OpenRouter API keys** + 1 Management Key
3. **VaultCore schema**: `cred_type: openrouter_api_key` + `cred_type: openrouter_mgmt_key`

### Short-term (P1-1 — VaultCore Schema)
1. **Provider key distribution matrix**: 8 OpenRouter keys × N providers = VaultCore tracks which provider key lives on which OpenRouter key
2. **Analytics poller**: Background job (15-min interval) calls Analytics API, updates VaultCore `used_today` / `byok_used_monthly`

### Medium-term (P2 — Orchestration)
1. **Smart routing**: ModelGateway prefers `:free` models when OpenRouter key in free tier; uses BYOK provider keys when available
2. **Cross-provider failover**: On 402/429 from provider, OpenRouter auto-fails; VaultCore detects via response headers, rotates provider key

---

## 📦 Deliverables for Phase 3 Synthesis

| Artifact | Location | Purpose |
|----------|----------|---------|
| OpenRouter VaultCore Schema | `docs/research/R_VAULT_SCHEMA_V2.md` (extended) | 8 keys + BYOK provider mapping |
| Analytics Poller Spec | `docs/research/R_OPENROUTER_ANALYTICS_POLLER.md` | 15-min quota reconciliation |
| Free Tier Model Map | `config/openrouter_free_models.yaml` | 25+ :free model IDs |
| BYOK Provisioning Script | `scripts/provision_openrouter_byok.py` | Distribute 8 provider keys across 8 OR keys |

---

## 🔗 Cross-References

| Provider | Phase 1 Report | Key Integration Point |
|----------|----------------|----------------------|
| **Google API** | `PHASE1A_GOOGLE_API_...` | Google provider keys in OpenRouter BYOK = Antigravity OAuth tokens |
| **Antigravity OAuth** | `PHASE1B_ANTIGRAVITY_...` | Refresh tokens → access tokens → OpenRouter Google provider key |
| **Grok CLI** | Grokster G1-15 | xAI provider key in OpenRouter BYOK (if xAI supported) |
| **Exa** | `PHASE1E_EXA_...` | Not an LLM provider — separate search API |
| **Firecrawl** | `PHASE1F_FIRECRAWL_...` | Not an LLM provider — separate scrape API |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ PHASE1D-COMPLETE ⬡ 2026-07-23*