# EXP-003: Control Researcher Report
## Researcher v3.1 — Linear Chain-of-Thought Mapping
**Date**: 2026-05-14 | **Status**: COMPLETE

---

## Artifact Registry

### 🏆 HIGH SOVEREIGNTY — Port Immediately

| ID | Artifact | Path | Type | ETE |
|----|----------|------|------|-----|
| A001 | **Entity-Model Affinity Database** | `xna-omega-legacy/config/entity_model_affinity.yaml` | YAML | TRIVIAL |
| A002 | **Domain Routing Config (v7.6.3)** | `xna-omega-legacy/config/domain-routing.yaml` | YAML | TRIVIAL |
| A003 | **Model Router SSOT** | `omega-stack-legacy/config/app/config_model-router_prod_v1.0_20260314_active.yaml` | YAML | MODERATE |
| A004 | **4-Layer Timeout Policies** | `xna-omega-legacy/config/timeout_policies.yaml` | YAML | TRIVIAL |
| A005 | **Sanctified Manifest (v7.6.3 Temple)** | `xna-omega-legacy/config/sanctified-manifest.yaml` | YAML | TRIVIAL |
| A006 | **Central App Config (24 sections)** | `omega-stack-legacy/config/app/config_app_prod_v1.0_20260314_active.yaml` | YAML | MODERATE |
| A007 | **Secrets Template (LZR ADR hash)** | `xna-omega-legacy/config/app/secrets_template.yaml` | YAML | TRIVIAL |
| A008 | **NewRelic APM Config** | `xna-omega-legacy/config/app/newrelic.yml` | YAML | TRIVIAL |

### 🔶 MEDIUM SOVEREIGNTY — Analyze Before Porting

| ID | Artifact | Path | Type | ETE |
|----|----------|------|------|-----|
| A009 | **Memory Schema (enhanced)** | `omega-stack-legacy/memory/entity_memory_schema.yaml` | YAML | MODERATE |
| A010 | **Provider Chain Def (raw)** | `omega-stack-legacy/config/app/config_provider_chain_prod_v1.0_20260314_active.yaml` | YAML | MODERATE |
| A011 | **MCP/Sovereign Plugin Index** | `omega-stack-legacy/config/plugins/index.yaml` | YAML | MODERATE |
| A012 | **Research Study Catalog** | `xna-omega-legacy/config/research_study_index.yaml` | YAML | MODERATE |
| A013 | **Obsidian Vault Navigation** | `xna-omega-legacy/config/obsidian_vault_nav.yaml` | YAML | MODERATE |
| A014 | **Feature Flags (entity_routing)** | `xna-omega-legacy/config/app/feature_flags.yaml` | YAML | TRIVIAL |
| A015 | **Dev Environment Overrides** | `xna-omega-legacy/config/app/development.yaml` | YAML | TRIVIAL |
| A016 | **Test Environment Overrides** | `xna-omega-legacy/config/app/testing.yaml` | YAML | TRIVIAL |

### 🔻 LOW SOVEREIGNTY — Reference Only

| ID | Artifact | Path | Type | ETE |
|----|----------|------|------|-----|
| A017 | **App Insights Config** | `xna-omega-legacy/config/app/app_insights.py` | PY | MODERATE |
| A018 | **Logging Config** | `xna-omega-legacy/config/logging.yaml` | YAML | TRIVIAL |
| A019 | **Docker Compose (full)** | `xna-omega-legacy/docker-compose.yml` | YAML | COMPLEX |
| A020 | **Docker Compose (minimal)** | `omega-stack-legacy/docker-compose.yml` | YAML | MODERATE |

---

## Cross-Pollination Insights

1. **Entity-Model Affinity Database is critical** — The Omega Engine's `entity_registry.py` currently maps entities to a single model. The legacy system supports multi-model fallback per entity with temperature presets. This is the #1 thing to port.

2. **Domain-routing config matches current Omega approach** — The legacy `domain-routing.yaml` uses the exact same keyword-domain mapping pattern as `entity_registry.find_by_domain()`. Validation: Omega's approach is correct.

3. **Sanctified-manifest provides governance architecture** — The legacy temple's 108-gate system and Ma'at-judgment hooks are architectural patterns worth studying for the Oversoul hierarchy (SOPHIA→MAAT→Isis/Lilith).

4. **Memory schema is more sophisticated in legacy** — The `omega-stack-legacy` memory schema includes entity-specific memory structures, relationship graphs, and archival tiers that Omega's `memory_store.py` doesn't yet implement.