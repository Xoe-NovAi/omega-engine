# 🔱 Phase 3: Unified Free-Tier Rotation Fabric Specification
**AP Token**: `AP-RESEARCHER-PHASE3-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ jem ⬡ opencode ⬡ trc_phase3_synthesis ⬡ ACTIVE
**Date**: 2026-07-23
**Sources**: Phase 1A–1F reports (6 providers, 32 credentials, 8 fleet slots)
**Architect Constraints**: D-432 (Zero paid), D-437 (Free-tier only, no proxy), D-436 (Fabric Gateway Pattern ratified)

---

## 🎯 Executive Synthesis (L1)

The **Omega Engine Free-Tier Rotation Fabric** manages **32 credentials across 6 providers** in **8 fleet slots** using **VaultCore as Control Plane** and **ModelGateway as Client Plane** — **no Data Plane proxy** (deferred per D-434). Each fleet slot = 1 logical "account" with credentials for all providers. Rotation = lease acquisition from VaultCore with quota-aware selection, TTL-based cooldown, and per-provider fallback chains.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OMEGA ENGINE FREE-TIER ROTATION FABRIC                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    LEASE (TTL + Quota)    ┌──────────────────────────┐   │
│  │  VAULTCORE   │ ◄─────────────────────────► │      MODELGATEWAY        │   │
│  │ (Control)    │    CREDENTIAL + METADATA    │      (Client)            │   │
│  └──────────────┘                             └──────────────────────────┘   │
│        │                                               │                     │
│        │ 8 Fleet Slots                                 │ 8 Fleet Slots       │
│        ▼                                               ▼                     │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    FLEET SLOT ARCHETYPE (×8)                          │   │
│  ├──────────────────────────────────────────────────────────────────────┤   │
│  │  Google (1)    │ Antigravity (1) │ Cline (1)  │ OpenRouter (1)      │   │
│  │  Exa (1)       │ Firecrawl (1)   │ Grok (1)   │ Local (GGUF/Ollama) │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Deep Dialectic (L2)

### 1. The Architect (Systemic Logic)
**Three-Layer Architecture** (Phase 0.5 Addendum, adapted for free tier):
- **Control Plane (VaultCore)**: Encrypted credential store, lease manager, quota reconciliation, health scoring
- **Client Plane (ModelGateway)**: Lease acquisition, request execution, rotation on 429/402, fallback chains
- **Local Plane (GGUF/Ollama)**: Bypasses fabric entirely (M7 Local-First)

**Fleet Slot = Atomic Rotation Unit**: 8 slots × 4 LLM providers + 2 search + 1 scrape = 56 credential bindings. Each slot independent — failure in slot 3 doesn't affect slot 7.

### 2. The Adversary (Critical Rigor)
**Free-Tier Failure Modes**:
| Provider | Hard Limit | Soft Limit | Rotation Trigger | Recovery |
|----------|------------|------------|------------------|----------|
| Google (per project) | RPD (100-1500) | RPM (5-15) | 429 + quota >90% | Midnight PT reset |
| Antigravity | Dual quota (AGY + CLI) | 90% threshold | 429 + quota cache stale | 15-min refresh |
| Cline | Per-config-dir | N/A | Manual switch | Config dir swap |
| OpenRouter | 50/day (free) / 1K/day ($10+) | 20 RPM | 429 + daily >90% | Midnight UTC |
| OpenRouter BYOK | 1M req/mo/key | Provider limits | Analytics API >90% | Monthly reset |
| Exa | 10 QPS/key | 150/day/key | 429 + credits low | Daily reset |
| Firecrawl | 1K credits/mo | 10 RPM | 402 + credits < estimated | Monthly reset |
| Grok | Weekly pool | gRPC quota | 402 "balance exhausted" | Weekly reset |

**Cascading Failure Risk**: OpenRouter BYOK routes to provider keys → provider 429 → OpenRouter failover → VaultCore must detect and rotate provider key, not OpenRouter key.

### 3. The Alchemist (Creative Synthesis)
**Unified Quota Model**: All providers map to VaultCore `VaultState`:
```yaml
used_today: 0           # Requests or credits consumed today
daily_limit: 1500       # Provider-specific (RPD or credits)
quota_reset_at: 1721703600000  # Epoch ms (midnight PT/UTC/weekly)
cooldown_until: 0       # M25 lease TTL + heartbeat
health_score: 100       # 0-100, failure penalty, hourly recovery
rotation_cursor: 0      # Per-family cursor (Antigravity pattern)
```

**Cross-Provider Fallback Chain** (ModelGateway logic):
```
User Request
    │
    ├─► Local Inference (GGUF/Ollama) ──► SUCCESS → Return
    │
    ├─► Lease Google (Antigravity OAuth) ──► 429/402 → Cooldown → Next
    │
    ├─► Lease OpenRouter (BYOK) ──► Provider 429 → Rotate provider key → Retry
    │       │
    │       └─► OpenRouter 429 (daily cap) → Cooldown ORB key → Next
    │
    ├─► Lease Cline (Anthropic/OpenAI) ──► 429 → Config dir swap → Next
    │
    ├─► Lease Exa (search) + Firecrawl (scrape) ──► Pipeline
    │
    └─► Lease Grok (ACP) ──► 402 → Cooldown → Next
    │
    └─► EXHAUSTED → Raise FleetExhaustedError
```

### 4. The Archivist (Historical Truth)
**Phase 0 L3 Principle**: "Sovereign intelligence routing requires a sovereign data plane" — **adapted**: Free tier = sovereign CONTROL plane (VaultCore), client-side DATA plane (ModelGateway). Proxy layer deferred to paid tier.

**Phase 1 Evidence Base**: 6 reports, 25 queries, 32 credential specs, all mandate-aligned.

---

## 📋 Unified VaultCore Schema (L3)

### Master Credential Registry (32 entries × 8 slots = 256 leased credentials max)
```yaml
# VaultCore Schema v2 — Free-Tier Rotation Fabric
VaultSecret:
  id: "uuid"
  provider: "google|antigravity|cline|openrouter|exa|firecrawl|grok|local"
  cred_type: "api_key|oauth|gcp_sa|grok_auth|cline_config|local_gguf"
  encrypted_blob: "<age-encrypted>"
  tier: "free"  # All free tier per D-432
  daily_limit: 1500          # Provider-specific
  used_today: 0
  quota_reset_at: 1721703600000  # Epoch ms
  cooldown_until: 0
  status: "active|cooldown|exhausted|error"
  rotated_at: 1721700000000
  metadata: {}  # Provider-specific (see below)

VaultState (per fleet slot):
  slot_id: 0-7
  rotation_cursors:
    google: 0
    antigravity_claude: 0
    antigravity_gemini: 0
    cline: 0
    openrouter: 0
    exa: 0
    firecrawl: 0
    grok: 0
  health_scores: {}  # provider → 0-100
  last_quota_sync: 1721700000000
```

### Provider-Specific Metadata
```yaml
# Google (8 keys = 8 GCP projects)
google:
  gcp_project_id: "omega-google-03"
  service_account_email: "exa-quota@omega-google-03.iam.gserviceaccount.com"
  models: ["gemini-3-flash", "gemini-3-pro"]
  rpm_limit: 10
  rpd_limit: 1500

# Antigravity OAuth (8 accounts)
antigravity:
  email: "user@gmail.com"
  project_id: "omega-agy-03"
  managed_project_id: "omega-agy-03"
  model_families: ["claude", "gemini"]
  quota_groups: ["gemini-3-flash", "gemini-3-flash-lite"]
  agy_sdk_fallback: true

# Cline CLI (8 config dirs)
cline:
  config_dir: "/home/arcana-novai/.cline-fleet/acct-03"
  provider: "anthropic"  # or openai, google
  model: "claude-sonnet-4.6"

# OpenRouter (8 keys + BYOK)
openrouter:
  key_id: "or_sk_..."
  management_key: "or_mgmt_..."
  byok_providers:
    openai: ["sk-proj-...", "sk-proj-..."]
    anthropic: ["sk-ant-..."]
    google: ["ya29..."]
  free_tier_status: "has_credits"  # $10+ purchased once
  daily_limit: 1000
  byok_monthly_limit: 1_000_000

# Exa (8 keys)
exa:
  search_types: ["instant", "fast", "auto", "deep-lite", "deep", "deep-reasoning"]
  output_schema_enabled: true
  daily_soft_limit: 150

# Firecrawl (8 keys)
firecrawl:
  plan: "free"
  monthly_credits: 1000
  concurrency: 2
  modifiers_cost:
    json_format: 4
    enhanced_mode: 4
    pdf_parsing: 1

# Grok CLI (8 accounts)
grok:
  config_dir: "/home/arcana-novai/.grok-fleet/acct-03"
  auth_file: "auth.json"
  config_file: "config.toml"
```

---

## 🛡️ Mandate Compliance Matrix

| Mandate | Implementation | Evidence |
|---------|---------------|----------|
| **M1 AnyIO** | All VaultCore/ModelGateway async via AnyIO | `anyio.create_task_group`, `anyio.to_thread.run_sync` |
| **M2 Firewall** | VaultCore in `src/omega/`; stacks in `config/wads/` | No stack logic in core |
| **M7 Local-First** | Local GGUF/Ollama bypasses VaultCore entirely | `model_gateway.py` routes local first |
| **M8 Zero Telemetry** | No analytics, no phone-home, debug logs local only | `TELEMETRY_DISABLED=1` everywhere |
| **M14 Heritage** | OAuth PKCE = [id-soft: doom3-2004]; Zone alloc = [id-soft: doom-1993] | Vet records in `HERITAGE_VET_LOG.md` |
| **M23 Failure Integrity** | 429/402 → explicit rotation; no silent fallback | `RotationDecision` enum, exhaustive matching |
| **M25 Streaming Resilience** | Lease TTL = min(1hr, token_expiry - 5min); heartbeat chunk on stall | `VaultState.cooldown_until` + SSE heartbeat |

---

## 🚀 Implementation Roadmap (Carmack Mode)

### P0-1 (This Week) — VaultCore MVP + AGY Fix
| Task | Owner | Effort | Leverage |
|------|-------|--------|----------|
| VaultCore `VaultSecret`/`VaultState` schema + age encryption | @maat/P3 | Medium | **High** (unblocks all) |
| AGY OAuth persistence fix (atomic write-back) | @pillar P4 | Low | **High** (saves 8× re-auth) |
| 8 GCP projects via `gcp-seeder --preset ai` | @researcher | Manual | **High** (enables Google 8-key) |
| 8 OpenRouter keys + $10 credits + Management Key | @researcher | Low | **High** (unlocks 1K/day) |

### P0-2 (This Week) — Grok CLI Workflow
| Task | Owner | Effort | Leverage |
|------|-------|--------|----------|
| `src/omega/integrations/grok_cli.py` (AnyIO subprocess + JSON-RPC) | @pillar P3 | Medium | **High** (dev leverage) |
| 8 `~/.grok-fleet/acct-XX/` dirs with `auth.json` | @grokster | Low | **High** |

### P1-1 (Next Week) — ModelGateway Integration
| Task | Owner | Effort | Leverage |
|------|-------|--------|----------|
| `ModelGateway.lease_credential(provider, slot, estimated_cost)` | @maat/P3 | Medium | **High** |
| Per-provider fallback chain (Google → OpenRouter → Cline → Grok) | @maat/P3 | Medium | **High** |
| Quota reconciliation daemon (15-min, Analytics APIs) | @lilith/P7 | Medium | Medium |

### P1-2 (Next Week) — Search/Scrape Pipeline
| Task | Owner | Effort | Leverage |
|------|-------|--------|----------|
| Exa router (search type policy + structured output) | @maat/P3 | Medium | Medium |
| Firecrawl safe crawl (pre-flight cost estimation) | @maat/P3 | Low | Medium |
| Exa → Firecrawl pipeline (URLs → content) | @maat/P3 | Medium | Medium |

### P2 (Deferred) — Proxy Layer (Paid Tier)
| Task | Status | Trigger |
|------|--------|---------|
| LLMCycle embed / LiteLLM sidecar | ⏸️ Deferred (D-434) | Paid accounts exist |
| Mid-stream failover | ⏸️ Deferred | Streaming resilience need |
| WARP proxy pool (W-1) | 🟡 CARMACK MODE | Architect sudo |

---

## 📦 Phase 3 Deliverables Checklist

| Artifact | Location | Status |
|----------|----------|--------|
| VaultCore Schema v2 (Free Tier) | `docs/research/R_VAULT_SCHEMA_V2.md` | ✅ Extended |
| AGY OAuth Persistence Fix | `docs/research/R_AGY_OAUTH_PERSISTENCE_FIX.md` | ✅ |
| gcp-seeder Manifest (8 projects) | `config/gcp-seeder-antigravity.yaml` | 📋 TODO |
| OpenRouter BYOK Provisioning | `scripts/provision_openrouter_byok.py` | 📋 TODO |
| Grok CLI Integration | `src/omega/integrations/grok_cli.py` | 📋 TODO |
| ModelGateway Lease/Rotation | `src/omega/model_gateway.py` | 📋 TODO |
| Exa Search Router | `src/omega/model_gateway/exa_router.py` | 📋 TODO |
| Firecrawl Safe Crawl | `src/omega/model_gateway/firecrawl_router.py` | 📋 TODO |
| Quota Reconciliation Daemon | `src/omega/vaultcore/reconciler.py` | 📋 TODO |
| Fleet Exhaustion Tests | `tests/integration/test_fleet_rotation.py` | 📋 TODO |

---

## 🔗 Cross-Reference Index

| Phase 1 Report | Provider | Key Spec |
|----------------|----------|----------|
| `PHASE1A_GOOGLE_API_FREE_TIER_ROTATION_20260723.md` | Google API | 8 GCP projects, per-project quota |
| `PHASE1B_ANTIGRAVITY_OAUTH_PERSISTENCE_ROTATION_20260723.md` | Antigravity | Dual-family cursor, projectId mandatory |
| `PHASE1C_CLINE_CLI_MULTI_ACCOUNT_20260723.md` | Cline CLI | 8 config dirs, providers.json injection |
| `PHASE1D_OPENROUTER_FREE_TIER_BYOK_20260723.md` | OpenRouter | 1M BYOK/mo, Analytics API, $10 unlock |
| `PHASE1E_EXA_SEARCH_API_20260723.md` | Exa | 7 search types, output_schema, 3 QPS MCP |
| `PHASE1F_FIRECRAWL_CREDITS_20260723.md` | Firecrawl | 1K credits/mo, modifiers stack, 402 handling |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ PHASE3-SYNTHESIS-COMPLETE ⬡ 2026-07-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: jem | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
