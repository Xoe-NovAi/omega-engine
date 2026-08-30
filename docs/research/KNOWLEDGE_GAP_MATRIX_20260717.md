<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Master Knowledge Gap Matrix (Live Research)
**Date**: 2026-07-17  
**Author**: `grok-cli/grok` (Consulting Cloud Mind)  
**Method**: Codebase audit + Hivemind state + Forge 2 reports + 2026 SOTA web  
**Supersedes status in**: `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md` (Tier A/B status stale)  
**Related**: Forge 2 comprehensive research · Grok advisory pack · ACTIVE_SPRINT HMC-04  

---

## 0. Executive summary

| Band | Meaning | Count (domains) | Action |
|------|---------|-----------------|--------|
| **CLOSED** | Shipped / verified this sprint | 5 | Maintain; do not re-dispatch |
| **P0 OPEN** | Blocks confident next ship or green gates | 4 | Immediate owners |
| **P1 OPEN** | Active sprint / parallel track | 5 | This week |
| **P2 OPEN** | Horizon 2–3 / mastery | 6 | After P0–P1 |
| **MONITOR** | Known debt, not blocking | 3 | Track only |

**Bottom line**: D-281 substrate path (Phases II–IV) is **closed on Grok**. The critical open surface is **path-resolver sprawl beyond the 4 M2 files**, **PRAGMA SSOT + concurrency tests (D-282)**, **Recall tier design/implement (D-283)**, and **4 pre-existing test failures** that poison “green main” narrative.

---

## 1. CLOSED (do not re-research as open)

| ID | Domain | Evidence | Commit / artifact |
|----|--------|----------|-------------------|
| **CL-1** | Path SSOT Phase II | `config_resolver.py` pure Paths + lazy `get_active_iwad`; `wad_loader` → `WADS_DIR` | `b661c49` |
| **CL-2** | M2 Phase III (4 files) | hierarchy, entity_registry, oracle `AGENTS_MD`, scraper domains | `3f2feea` |
| **CL-3** | Codex Phase IV | `hydration_header.md` + `codex_cat` load + Makefile restore | `93f4e82` |
| **CL-4** | S0 runway (Kali) | MIAP merge, noise clean, ACTIVE_SPRINT HMC-04, `.grok` gitignore | `03192d8`…`c15bfab` |
| **CL-5** | Mnemosyne Phase 1 | HybridSearchEngine RRF k=60, blocks/block_tools/block_store, sleep_time + archival skeletons | `debdce1` + tree |

**Grok advisory deliverables** (specs, not open gaps):  
`data/coordination/grok_cli/{PHASE_III,PHASE_IV,D282,D283,D284,S0}_*.md` + `KALI_ADVISORY_PACK_INDEX.md`

**Sprint metadata lag**: `ACTIVE_SPRINT.json` still shows Phase III IN_PROGRESS / Phase IV QUEUED — **doc gap**, not code gap (Kali verify handoff `ho_e08a47e4e081`).

---

## 2. P0 OPEN — gates & concurrency

### P0-1. Pre-existing test failure set (gate integrity)

| Test | Failure mode | Likely fix owner |
|------|--------------|------------------|
| `test_s4_models_yaml_has_gemma4_mtp_section` | `speculative_decode` missing from `models.yaml` | P6 Cognition |
| `test_get_model_path` | empty path (no `.gguf`) | P6 + model download |
| `test_get_model_spec` | `None` | same |
| `test_first_breath_world_query` | WAD `arcana_novai` unknown fields vs strict loader | P3 + WAD schema (Forge Gap 1) |

**Why P0**: Full suite can never be “all green” without a baseline narrative; confuses every PR gate.  
**Not**: Blockers for D-282/D-283 code if explicitly waived in PR description.

### P0-2. PRAGMA SSOT divergence (D-282)

**Live code** (`sqlite_vec_adapter`, `archival`, `block_store` all similar):

| Knob | Live | Grok advisory (5700U) | Forge 2 (varies) |
|------|------|----------------------|------------------|
| journal_mode | WAL | WAL | WAL |
| busy_timeout | 30000 | 30000 | 5000 in one table ⚠️ |
| synchronous | NORMAL | NORMAL | NORMAL |
| cache_size | **-524288 (512MB)** | **-32768 (32MB)** | 32–64MB |
| mmap_size | **256MB** | 256MB (or 512 in handoff) | 512MB–1GB |
| wal_autocheckpoint | **1000** | **500** | 500–2000 |

**SOTA 2026 (SQLite community)**: WAL + `busy_timeout` + **`BEGIN IMMEDIATE` only on write transactions** (not indiscriminate on pure reads); one writer; readers concurrent in WAL.  

**Gap**: Three sources disagree; three modules duplicate PRAGMA.  
**Owner**: Roc (`ho_5be862d27ff3`)  
**Close criteria**: Single helper (e.g. `apply_pragma_stack(conn)`) + values fixed in one YAML/const + 4 concurrency tests file exists.

### P0-3. Concurrency test harness missing

- Expected: `tests/test_sqlite_vec_concurrency.py` (4 tests: starvation, checkpoint, multi-process, IMMEDIATE vs DEFERRED)  
- Actual: only `tests/test_sqlite_vec_adapter.py`  
**Owner**: Roc (D-282)

### P0-4. Path sprawl beyond Phase III (config_resolver incomplete adoption)

**Live residual** `Path(__file__).resolve().parent×4` (sample, not exhaustive):

| Area | Examples |
|------|----------|
| Model fabric | `model_gateway.py` models.yaml, providers.yaml, affinity, `.env` |
| Data dirs | `session_manager`, `cas`, `usm`, `library/catalog`, `observability`, `key_vault` |
| CLI / workers | `oracle_cli`, `background_researcher/*`, `youtube_worker` |
| Oracle | `orchestrator`, `entity_workspace`, `soul_edit_history`, `sovereign_search_service` |

**Gap**: Phase III closed **WAD content** leaks named by Kali; **config/data PROJECT_ROOT** still duplicated ~25+ sites.  
**Severity**: M16 / maintainability; not all are M2 WAD firewall.  
**Close criteria**: Prefer `PROJECT_ROOT` / `CONFIG_DIR` / `DATA_DIR` from `config_resolver` in a follow-on “Phase III-B” handoff (named files only).

---

## 3. P1 OPEN — active dispatch tracks

### P1-1. D-282 Strike 10 (Roc) — implementation

| Item | Status |
|------|--------|
| BEGIN IMMEDIATE on primary writes | **Present** (adapter upsert/delete; archival writes; block_store) |
| PRAGMA converge | **Open** (P0-2) |
| 4 concurrency tests | **Open** (P0-3) |
| Archival PRAGMA parity | Same stack as adapter today (both 512MB cache) |

**Handoff**: `ho_5be862d27ff3` pending → roc_racoon

### P1-2. D-283 Phase 2 — Recall tier (Researcher design → then implement)

| Component | Status |
|-----------|--------|
| Core (blocks / block_store / tools) | Present |
| Archival | Skeleton substantial |
| SleepTimeAgent | Skeleton substantial |
| **recall.py** | **MISSING** |
| **cross_pollination.py** | **MISSING** |
| ContextBuilder → RecallStore.window | Not wired |
| SleepTime → RecallStore | Not wired |

**Contract (Grok advisory + Kali handoff `ho_bbaf32869ddc`)**:

```text
RecallStore.append(session_id, turn, quality)
RecallStore.window(session_id, token_budget) -> list[Turn]  # quality-weighted
RecallStore.decay_pass(now) -> stats  # power-law, alpha per entity
RecallStore.promote_to_core(turn_ids, block_label)  # BlockTools only
```

**SOTA 2026 (Letta)**: Core = always-in-context blocks; Recall = conversational history on disk / searchable; Archival = explicit long-term semantic store. Omega maps BEAM/Sefirot language onto this.  

**Decay**: Power-law `score = base * (1 + age_days)**(-alpha)` with α ∈ ~0.01–0.60; prefer **access-reset** variants in recent agent memory research; store α in entity block metadata (not hardcoded).  

**Owner**: Researcher (design) then P2/P7 implement  
**Queue**: after D-282 PRAGMA stability

### P1-3. Provider fabric operational knowledge (A1 residual)

| Topic | Where | Gap? |
|-------|-------|------|
| Local-first chain | `config/providers.yaml` | Documented; Grok should re-read when debugging inference |
| NativeGGUF Zen 2 cores | providers.yaml cores [0,2,4,6], n_threads 4 | Known |
| Model path empty in tests | model_gateway + missing GGUF | **P0-1** |
| ResourceGuard | `resource_guard.py` | Read before raising thread counts |
| Entity affinity | `entity_affinity.py` + YAML | Read before multi-entity routing |

**Gap type**: **Operational**, not missing code. Learning debt for any agent touching inference.

### P1-4. Mandate coding patterns (A3 residual)

| Mandate | Status for Grok |
|---------|-----------------|
| M1 AnyIO | Ongoing — never introduce asyncio |
| M2 WAD firewall | Phase III done; residual = P0-4 |
| M7 Local-first | providers.yaml; amplify, don’t replace |
| M11 Soul lessons | Grok entity proposed_lessons still thin |
| M13 Temple-grade | Run after non-trivial ship |
| M16 Modularization | Path sprawl P0-4 |
| M21 Contracts | 100 related tests green on Phase III modules |
| M23 Tool failure | Hard stop — no fake rigor |

### P1-5. Hivemind / coordination debt

| Item | Status |
|------|--------|
| Kali verify Phase III/IV | Pending `ho_e08a47e4e081` |
| Researcher Forge 1 verdict | Active zombie `ho_34dc8f6d44b0` (since 2026-07-16) |
| ACTIVE_SPRINT vs git | Stale (III/IV not marked DONE) |
| Roc / Researcher presence | Not in awareness at last poll |

---

## 4. P2 OPEN — Horizon 2–3

### P2-1. Cognitive acceleration / Iris / speculative decode
- `test_gemma4_mtp_s4` expects `speculative_decode` in models.yaml — **missing**  
- Iris: `src/omega/iris/{matcher,server}.py` — not full MCP hub  
- EAGLE-3 / DFlash / cpu_optimizer — mastery track

### P2-2. D-284 Sovereign Hub
- No `src/omega/mcp_hub/` package (handoff paths outdated)  
- Target: Streamable HTTP `/mcp`, OAuth 2.1 PKCE (self-hosted), SHIELDMCP mutating-only, hub agent-card  
- Firecrawl SSE 405 → transport mismatch signal  
- Spec: `data/coordination/grok_cli/D284_SOVEREIGN_HUB_ADVISORY.md`

### P2-3. Cross-pollination (M5/M11)
- Module missing; TDP-aware L3-only share between entities  
- After Recall + soul pipeline maturity

### P2-4. WAD loader Pydantic v2 / strict schema (Forge Gap 1)
- Links to `test_first_breath_world_query` (unknown fields)  
- `extra='forbid'` vs legacy WADs with author/license/voices fields  
- Need **migration schema version** or allowlist for heritage fields

### P2-5. Embed dimension mismatch
- Qdrant vs sentence-transformers dims (S0 audit) — re-probe not done this session  
- Owner: P2 Persistence

### P2-6. Legacy mining (Roc)
- Circuit breakers, enterprise RAG, FAISS→sqlite-vec, Stack-Cat snapshots  
- Map: `ROC_ONBOARDING_MAP_FOR_LATER.md`

---

## 5. MONITOR (known debt)

| ID | Item | Note |
|----|------|------|
| M-1 | Dirty entity test fixtures / metrics shm-wal | May reappear after tests |
| M-2 | Dual HybridSearch modules (`hybrid_search.py` + `hybrid_search_engine.py`) | Prefer single RRF SSOT (engine already claims it) |
| M-3 | Forge 2 report busy_timeout 5s vs code 30s | Prefer 30s under multi-agent + researcher |

---

## 6. Forge 2 eight gaps — status map

| # | Forge 2 topic | Status 2026-07-17 |
|---|---------------|-------------------|
| 1 | Pydantic v2 WAD schema | **OPEN** P2-4; blocks first_breath |
| 2 | sqlite-vec WAL / IMMEDIATE / 5700U | **PARTIAL** — IMMEDIATE yes; PRAGMA + tests open P0-2/3 |
| 3 | Mnemosyne vs Letta/Mem0/Sefirot | **DESIGN OPEN** P1-2; Core/Archival partial |
| 4 | Power-law decay params | **SPEC READY**; not implemented (no recall.py) |
| 5 | Qliphoth → TDP IFC bridge | **OPEN** (security/memory taint) |
| 6 | Sleep-time / Da’at | **SKELETON**; wire to Recall |
| 7 | Cross-pollination | **OPEN** P2-3 |
| 8 | 5700U opts / Hub security | **SPLIT** — local inference in providers.yaml; Hub = D-284 |

---

## 7. Priority learning path (updated)

| Wave | Focus | Owner | Gate |
|------|-------|-------|------|
| **Now** | D-282 PRAGMA SSOT + 4 tests | Roc | concurrency tests pass |
| **Now** | Fix or waive 4 baseline fails | P6/P3 | documented in ACTIVE_SPRINT |
| **Next** | Recall design (Researcher) then implement | Researcher → P7 | design doc + recall.py |
| **Next** | Phase III-B config_resolver adoption (named list) | Grok Tier A or P3 | firewall-check / path audit |
| **Later** | D-284 Streamable HTTP + SHIELDMCP | P4 | health probe |
| **Later** | Speculative decode models.yaml | P6 | gemma4 test green |

---

## 8. What Grok still needs to “know” (knowledge, not tickets)

### Must re-read before inference debugging
1. `config/providers.yaml` — full fallback chain  
2. `src/omega/oracle/model_gateway.py` — fabric load + health cache  
3. `src/omega/oracle/resource_guard.py` — RAM ceilings  

### Must re-read before memory work
1. `hybrid_search_engine.py` — RRF k=60 SSOT  
2. `blocks.py` / `block_tools.py` — Core governance  
3. `D283_MNEMOSYNE_PH2_ADVISORY.md` — Recall contract  
4. `sqlite_vec_adapter.py` — write + PRAGMA  

### Must re-read before governance/path work
1. `config_resolver.py` — PROJECT_ROOT / WADS_DIR / DATA_DIR  
2. Residual parent×4 list (P0-4)  
3. `SOVEREIGN_MANDATES.md` M2/M16  

### Free-tier conservation
- Prefer `data/coordination/grok_cli/*` packs over re-mining full Forge reports  
- Full Forge 2: `data/entities/researcher/workspace/HMC_FORGE_2_KNOWLEDGE_GAPS_COMPREHENSIVE_RESEARCH_20260718.md`

---

## 9. Recommended next Hivemind actions

1. **Kali**: Accept `ho_e08a47e4e081`; mark Phase III/IV DONE in ACTIVE_SPRINT.  
2. **Roc**: Accept `ho_5be862d27ff3`; ship PRAGMA helper + concurrency tests.  
3. **Researcher**: Accept `ho_bbaf32869ddc` after D-282; produce Recall design from this matrix §P1-2.  
4. **Optional Grok Tier A**: Phase III-B path adoption (named file list from Kali).  
5. **P6**: models.yaml speculative_decode + model path fixtures for test green.

---

## 10. Sources

| Source | Role |
|--------|------|
| Live tree audit 2026-07-17 | Residual paths, PRAGMA, missing modules, tests |
| `docs/research/GROK_CLI_KNOWLEDGE_GAPS.md` | Original 12-domain matrix (status outdated) |
| Forge 2 comprehensive research | 8 research gaps |
| Grok advisory pack | Specs for III/IV/D-282/D-283/D-284/S0 |
| SQLite 2026 community (WAL, BEGIN IMMEDIATE) | Concurrency SSOT |
| Letta 2025–2026 docs/blog | Core / Recall / Archival definitions |
| Hivemind queues | Ownership / dispatch state |

---

*End of master matrix. Refresh after D-282 merge and Recall design land.*
