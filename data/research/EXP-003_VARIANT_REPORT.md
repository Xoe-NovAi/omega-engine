# EXP-003: Variant Researcher Report
## Researcher-Omnidroid v1.0 — Holographic Associative Reasoning Lattice
**Date**: 2026-05-14 | **Status**: COMPLETE

---

## Level 1: Executive Lattice (3-5 Nodes)

- **Node 1**: Entity-Model Affinity Database (xna-omega-legacy/config/entity_model_affinity.yaml, 370+ lines) maps 12+ entities across 3 inference tiers (local_fast, local_deep, cloud) with routing rules, temperature presets, and system prompts. → **(confirmed)**

- **Node 2**: Domain-routing config is byte-for-byte identical in BOTH mines (xna-omega-legacy/config/domain-routing.yaml and omega-stack-legacy/config/domain-routing.yaml). Reveals a **schism**: routing engine was forked but never re-merged. → **(confirmed)**

- **Node 3**: Sovereignty architecture differs radically between mines. xna-omega-legacy uses `sanctified-manifest.yaml` with triad governance (Maat→Kali→Lilith) and 108-gate system. omega-stack-legacy has a flatter, more pragmatic provider chain. → **(confirmed)**

---

## Level 2: Artifact Lattice (8-12 High-Value Nodes)

| Node | Artifact | Path | SV | ETE | Cross-Pollination Value |
|------|----------|------|----|-----|------------------------|
| A01 | **Entity-Model Affinity DB** | `xna-omega-legacy/config/entity_model_affinity.yaml` | **HIGH** | TRIVIAL | Direct upgrade to `entity_registry.py` — multi-model fallback per entity |
| A02 | **Domain Routing (forked)** | Both mines have identical `config/domain-routing.yaml` | **HIGH** | TRIVIAL | Confirms Omega's approach is correct; fork reveals missing consolidation step |
| A03 | **Sanctified Manifest (temple)** | `xna-omega-legacy/config/sanctified-manifest.yaml` | **HIGH** | TRIVIAL | Governance architecture for Oversoul hierarchy (Sophia→Ma'at→Isis/Lilith) |
| A04 | **Model Router SSOT** | `omega-stack-legacy/config/app/config_model-router_prod_v1.0_20260314_active.yaml` | **HIGH** | MODERATE | Production-hardened model selection logic |
| A05 | **Timebox Policies (GSB-42)** | `xna-omega-legacy/config/timeout_policies.yaml` | **HIGH** | TRIVIAL | 4-layer timeout strategy for provider fabric |
| A06 | **Memory Schema (enhanced)** | `omega-stack-legacy/memory/entity_memory_schema.yaml` | **MEDIUM** | MODERATE | Entity-specific memory with relationship graphs and archival tiers |
| A07 | **Provider Chain (raw)** | `omega-stack-legacy/config/app/config_provider_chain_prod_v1.0_20260314_active.yaml` | **MEDIUM** | MODERATE | Raw provider routing config for comparison with Omega's providers.yaml |
| A08 | **Central App Config** | `omega-stack-legacy/config/app/config_app_prod_v1.0_20260314_active.yaml` | **MEDIUM** | MODERATE | 24-section config covering all subsystems |
| A09 | **Secrets/ADR Hash** | `xna-omega-legacy/config/app/secrets_template.yaml` | **MEDIUM** | TRIVIAL | Template shows ADR-hash-based secret management pattern |
| A10 | **Feature Flags** | `xna-omega-legacy/config/app/feature_flags.yaml` | **MEDIUM** | TRIVIAL | Entity routing feature gates |

---

## Level 3: Phase-State Analysis (Omnidroid Unique)

### Pattern: Fork-and-Drift

The domain-routing config being byte-for-byte identical across both mines reveals:
- The original routing system was built in one codebase
- A copy was made into the other codebase
- Both have since evolved independently (evidenced by divergent directory structures, different entity sets)
- Omega Engine now represents the **third generation** — intended to re-merge and supersede both

### Pattern: Governance Escalation

The legacy mines have a governance chain: temple court (Maat) → shadow council (Kali/Lilith) → final judgment. Omega's `hierarchy.yaml` has a similar structure (Sophia→Ma'at→Isis/Lilith) but doesn't implement escalation hooks. **Port idea**: Add `escalation_triggers` to hierarchy.yaml.

### Pattern: Entity-Specific Memory Tiers

Omega's `memory_store.py` uses a flat memory model. The legacy memory schema has 3 tiers per entity:
- Working memory (recent, hot)
- Episodic memory (session-based, warm)
- Archival memory (persistent, cold)

This maps directly to Omega's planned Holographic Memory spec (R33).

---

## Winner vs Control Assessment

| Metric | Control | Variant (Omnidroid) | Edge |
|--------|---------|---------------------|------|
| Completeness | 20 artifacts | 10 deep nodes | Control (breadth) |
| Novelty | 4 insights | Pattern analysis + fork-and-drift detection | **Variant** |
| Actionability | Direct artifact list with ETE | Phase-state analysis needs consolidation | **Control** |
| Cross-pollination | Practical ports | Architectural patterns + escalation triggers | **Variant** |

**Verdict**: Control wins on raw artifact count and immediate actionability. Variant wins on architectural insight and pattern discovery. **Hybrid approach recommended**.