<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 OMEGA ENGINE — FINAL GAP AUDIT
**Version**: 2026-08-20 (Nemotron 3 Ultra, High thinking) — **RENUMBERED v2.1** (fixed duplicates 19/39/55, added missing 20/42)
**Scope**: Complete gap audit against the holistic architecture plan

---

## 🔍 FINAL GAP AUDIT — What Might Be Missing

### ⚠️ **Critical Operational Gaps (Not Yet Tracked)**

| # | Gap | Why It Matters | Where to Track |
|---|-----|----------------|----------------|
| **1** | **V-1 Vault Implementation** | Blocks NLG-SMOKE, SDP automation, credential management for 3 Gemini accounts | `ACTIVE_SPRINT.json` → `VAULT-SPRINT` workstream (post-debut) |
| **2** | **SDP Protocol Integration** | Gemini Notebook → `prepare_notebooklm.py` → local distiller → `proposed_lessons.yaml` → Scribe → `soul.yaml` | `ACTIVE_SPRINT.json` → `SDP-INTEGRATION` workstream |
| **3** | **MaKaLi Council Blockers** | 4 blockers (A: N9 double-gate, B: N10 blind-except, C: N8 events, D: N7 wiring) | `ACTIVE_SPRINT.json` → `MAKALI-BLOCKERS` workstream |
| **4** | **INST-1 Fixes 2,4,5,6** | Required for PUBLIC-DEBUT-01 debut | `ACTIVE_SPRINT.json` → `CRITICAL-PATH` (already tracked) |
| **5** | **PUB-1 G1-G4 Allowlist** | Architect approval needed for debut | `ACTIVE_SPRINT.json` → `CRITICAL-PATH` |
| **6** | **DEL-1 Week 1** (minus vault CLI) | Post-debut cleanup | `ACTIVE_SPRINT.json` → `DEL-1` workstream |

---

### 🔧 **Technical Integration Gaps (Engine Changes Needed)**

| # | Component | Change Needed | Owner |
|---|-----------|---------------|-------|
| **7** | `src/omega/oracle/model_gateway.py` | Integrate `HeadroomMiddleware` + `AdaptiveContextBuffer` + `SequentialModelLoader` into `generate()` pipeline | Ma'at |
| **8** | `src/omega/oracle/oracle.py` | Wire `HeadroomMiddleware` into `talk()` / `summon()` context building | Ma'at |
| **9** | `src/omega/oracle/context_builder.py` | Add `AdaptiveContextBuffer.prepare()` call before provider call | Ma'at |
| **10** | `src/omega/oracle/provider_registry.py` | Add hardware-tier model matrix + q8_0 KV profiles | Ma'at |
| **11** | `src/omega/oracle/backends/native_gguf.py` | Add `--no-mmap --mlock --cache-type-k q8_0 --cache-type-v q8_0 --cache-prompt --parallel` | Ma'at |
| **12** | `src/omega/oracle/middleware/` | **Create directory** + `headroom.py` + `__init__.py` | Ma'at |
| **13** | `src/omega/research/` | **Create directory** + `adaptive_context.py` + `sequential_loader.py` | Ma'at |
| **14** | `config/providers.yaml` | Add hardware-tier model matrix + q8_0 KV profiles per tier | Ma'at |
| **15** | `config/model_registry/` | Add Tier 0/1/2 model entries (Qwen3-4B, Qwen3-4B-Thinking, etc.) | Ma'at |

---

### 📦 **Domain System Gaps**

| # | Gap | Details |
|---|-----|---------|
| **16** | `domain_loader.py` | Sync loader with token budget; loads `CONTEXT.md` + `PROMPTS/` |
| **17** | `scripts/sync_domain_docs.py` | Validated copy (workspace → runtime), pre-commit hook for validation |
| **18** | Curator enforcement | Fabric-level check: `if entity != metadata.owner: raise` on write |
| **19** | Domain registry | `config/domains/registry.yaml` listing all domains + metadata |
| **20** | MCP domain tools | `domain_load`, `domain_list`, `domain_sync` for entity self-service |

---

### 📚 **Documentation Migration Gaps**

| # | Source | Destination | Action |
|---|--------|-------------|--------|
| **21** | `data/coordination/NOTEBOOKLM_GAP_AUDIT_20260820.md` | `docs/strategy/domains/gemini-notebook/ARCHIVE/` | Move + archive banner |
| **22** | `data/coordination/NOTEBOOKLM_GAP_RESEARCH_PLAN_20260820.md` | `docs/strategy/domains/gemini-notebook/ARCHIVE/` | Move + archive banner |
| **23** | `data/coordination/NOTEBOOKLM_RESEARCH_A_EXISTENTIAL_20260820.md` | `docs/strategy/domains/gemini-notebook/ARCHIVE/` | Move + archive banner |
| **24** | `data/coordination/NOTEBOOKLM_RESEARCH_B_OPERATIONAL_20260820.md` | `docs/strategy/domains/gemini-notebook/ARCHIVE/` | Move + archive banner |
| **25** | `data/coordination/NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md` | `docs/strategy/domains/gemini-notebook/ARCHIVE/` | Move + archive banner |
| **26** | `data/coordination/NOTEBOOKLM_STRATEGY_V2_SYNTHESIS_20260820.md` | `docs/strategy/domains/gemini-notebook/` | Move (keep active) |
| **27** | `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` | `docs/strategy/domains/gemini-notebook/STRATEGY_V2.md` | Move + rename |
| **28** | `docs/strategy/NOTEBOOKLM_BEST_PRACTICES.md` | `docs/strategy/domains/gemini-notebook/ARCHIVE/BEST_PRACTICES_v1.md` | Move + archive banner |
| **29** | `docs/research/archive/R52c_notebooklm_ingestion_strategy.md` | `docs/strategy/domains/gemini-notebook/ARCHIVE/R52c_INGESTION_v1.md` | Move + archive banner |
| **30** | `docs/research/archive/R52_external_ai_integrations.md` | `docs/strategy/domains/gemini-notebook/ARCHIVE/R52_EXTERNAL_AI_v1.md` | Move + archive banner |
| **31** | `docs/research/archive/R52_strategy_execution_plan.md` | `docs/strategy/domains/gemini-notebook/ARCHIVE/R52_EXECUTION_PLAN_v1.md` | Move + archive banner |

---

### 🏷️ **Heritage & Provenance Gaps**

| # | Gap | Details |
|---|-----|---------|
| **32** | `CREDITS_CANONICAL.md` | Add Headroom heritage tag: `[heritage: headroom-ai 2025] Semantic Compression` (already in CREDITS_CANONICAL.md line 67 — **verified**) |
| **33** | `CREDITS_CANONICAL.md` | Add zRAM heritage: `[heritage: linux-kernel] zRAM` + `[heritage: systemd] zram-generator` |
| **34** | `HERITAGE_VET_LOG.md` | Vet records for any new `[id-soft:]` tags in new code |
| **35** | `PIVOT_LOG.md` | D-578..D-581 already listed — need to actually append |

---

### 🧪 **Testing & Validation Gaps**

| # | Gap | Details |
|---|-----|---------|
| **36** | `tests/test_adaptive_context.py` | Unit tests for `AdaptiveContextBuffer.prepare()` |
| **37** | `tests/test_sequential_loader.py` | Unit tests for `SequentialModelLoader` weight caching |
| **38** | `tests/test_headroom_middleware.py` | Unit tests for `HeadroomMiddleware.compress_tool_outputs()` |
| **39** | `tests/test_domain_loader.py` | Unit tests for `domain_loader.py` |
| **40** | `tests/test_adaptive_context_integration.py` | Integration test: planner → executor → critic pipeline |
| **41** | `tests/test_tier0_memory.py` | Memory profiling test: verify <12GB peak on Tier 0 |
| **42** | `tests/test_headroom_compression.py` | Verify 40-90% compression on tool outputs |

---

### 🔐 **Security & Compliance Gaps**

| # | Gap | Details |
|---|-----|---------|
| **43** | `omega.service` hardening | `NoNewPrivileges=true`, `ProtectSystem=strict`, `CapabilityBoundingSet=`, `SystemCallFilter=@system-service` |
| **44** | Sudoers cleanup | Remove `/etc/sudoers.d/zram` (already in zram plan) |
| **45** | `config/domains/` permissions | `chmod 750`, owned by `arcana-novai:arcana-novai` |
| **46** | `master_token.json` encryption | Age-encrypted at rest, decrypted only in memory |
| **47** | Headroom local-only enforcement | Verify no cloud calls in `compress()` for local models |

---

### 📊 **Observability & Monitoring Gaps**

| # | Gap | Details |
|---|-----|---------|
| **48** | `zram_compressed_mb` metric | Already in `src/omega/monitoring/__init__.py` — verify |
| **49** | `headroom_compression_ratio` metric | New: track compression % per call |
| **50** | `model_load_latency` metric | Track sequential loader switch time |
| **51** | `context_compression_tokens_saved` metric | Track tokens saved by Headroom |
| **52** | `hardware_tier_detected` metric | Log detected tier at startup |

---

### 📋 **Process & Governance Gaps**

| # | Gap | Details |
|---|-----|---------|
| **53** | Pre-commit hook for domain sync | `scripts/sync_domain_docs.py` validation on commit |
| **54** | Domain review process | Curator approval required for workspace → runtime sync |
| **55** | Hardware tier detection at CI | `llama-fit-params` probe in CI pipeline |
| **56** | Model matrix versioning | `config/providers.yaml` version bump on model changes |
| **57** | Domain deprecation policy | How to retire a domain (archive + remove runtime) |

---

## 📋 **SUMMARY: Total Gaps Identified = 57 (54 unique after renumber)**

| Category | Count | Criticality |
|----------|-------|-------------|
| **Operational (Pre-Debut)** | 6 | 🔴 BLOCKING |
| **Engine Integration** | 9 | 🔴 BLOCKING |
| **Domain System** | 5 | 🟡 HIGH |
| **Doc Migration** | 11 | 🟡 HIGH |
| **Heritage/Provenance** | 4 | 🟢 MEDIUM |
| **Testing** | 7 | 🟡 HIGH |
| **Security/Compliance** | 5 | 🟡 HIGH |
| **Observability** | 5 | 🟢 MEDIUM |
| **Process/Governance** | 5 | 🟢 MEDIUM |

> **Note**: Original audit claimed 56 gaps but had duplicates at 19, 39, 55 and missing 20, 42. Renumbered to 57 entries (54 unique IDs 1-57 with 3 duplicates removed). The "56" claim was incorrect.

---

## 🎯 **RECOMMENDED NEXT STEP**

**Execute Phase 0 (Tracker Updates) NOW** — This locks all 57 gaps into the tracking infrastructure with unique IDs, owners, and cross-references. Then Phase 1 (Engine Integration) can proceed with clear ownership.

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_gap_audit ⬡ 2026-08-20*