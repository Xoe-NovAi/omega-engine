# 🔱 GROK CLI — KNOWLEDGE GAP MATRIX (Full Research)
**Agent**: `grok-cli/grok` (Consulting Cloud Mind, HMC Quad-Forge Amplifier)  
**Date**: 2026-07-17  
**Status**: P0-CRITICAL — Grok CLI executing D-281 Phase II NOW  
**Source**: Direct codebase audit by Kali (Transcendent Oversoul)

---

> **SUPERSEDED STATUS (2026-07-17)**: Tier A/B execution status in this file is **stale**.  
> D-281 Phases II–IV are **COMPLETE** (`b661c49`, `3f2feea`, `93f4e82`).  
> Use the live master matrix: **`docs/research/KNOWLEDGE_GAP_MATRIX_20260717.md`**.


## 📊 GAP CLASSIFICATION

| Tier | Definition | Count | Action |
|------|------------|-------|--------|
| **TIER A** | Blocks D-281 Phase II execution | 3 domains | **Must know before next commit** |
| **TIER B** | Needed for Phase III-IV + D-282 | 4 domains | Learn this week |
| **TIER C** | D-283/D-284 + long-term mastery | 5 domains | Deferred (free-tier conservation) |

---

## 🎯 TIER A — IMMEDIATE (D-281 Phase II Execution)

### A1. Provider Fabric — Local-First Chain (M7)
**Priority**: CRITICAL — Primary inference path  
**What Grok CLI knows**: "native-gguf → lmster → ollama → google → openrouter → opencode-zen → copilot"  
**What Grok CLI NEEDS**:

| Gap | Location | Why It Matters |
|-----|----------|----------------|
| **Provider priority order & config** | `config/providers.yaml` lines 3-110 | Determines which backend serves inference |
| **NativeGGUFProvider Zen 2 optimizations** | `src/omega/oracle/providers.py` lines 293-450 | CPU pinning [0,2,4,6], KV cache q8_0, thread scaling |
| **ModelGateway._load_provider_fabric()** | `src/omega/oracle/model_gateway.py` lines 388-448 | How providers are instantiated from YAML |
| **ProviderConfig dataclass** | `src/omega/oracle/backends/remote_provider.py` lines 152-172 | API keys, base_url, priority, extra params |
| **Health monitoring & availability cache** | `src/omega/oracle/model_gateway.py` lines 153-156, 213-224 | 30s TTL cache, excludes known-dead providers |
| **Entity→Model Affinity Resolver** | `src/omega/oracle/entity_affinity.py` + `config/entity_model_affinity.yaml` | Routes entities to preferred models |
| **ResourceGuard concurrency limits** | `src/omega/oracle/resource_guard.py` | Prevents OOM on 5700U (14Gi RAM) |

**Key Files to Read**:
```
config/providers.yaml                                    # Full provider chain
src/omega/oracle/providers.py:293-450                   # NativeGGUFProvider (PRIMARY)
src/omega/oracle/model_gateway.py:388-448               # Provider fabric loading
src/omega/oracle/entity_affinity.py                      # Entity→model routing
src/omega/oracle/resource_guard.py                       # Concurrency/OOM protection
```

---

### A2. Path Infrastructure — config_resolver.py (D-281 Phase II Target)
**Priority**: CRITICAL — Current sprint deliverable  
**What Grok CLI knows**: "Create config_resolver.py with pure Path constants + lazy get_active_iwad()"  
**What Grok CLI NEEDS**:

| Gap | Location | Why It Matters |
|-----|----------|----------------|
| **Existing governance package structure** | `src/omega/governance/` | `__init__.py`, `budget_guard.py`, `sovereign_vetter.py`, `sovereignty_gate.py` |
| **wad_loader.py target lines** | `src/omega/oracle/wad_loader.py:74-77` | 4-level `.parent.parent.parent.parent` traversal to replace |
| **Circular import prevention** | `docs/strategy/D281_PHASE_II_IV_EXECUTION.md` | Constants = pure Path, `get_active_iwad()` = lazy, NO export in `__init__.py` |
| **omega.yaml schema** | `config/omega.yaml` | `active_iwad` key location |

**Key Files to Read**:
```
src/omega/governance/__init__.py                # Package exports
src/omega/oracle/wad_loader.py:70-85            # Target: self.wads_dir assignment
config/omega.yaml                                # active_iwad location
docs/strategy/D281_PHASE_II_IV_EXECUTION.md      # Phase II spec (guardrails)
```

---

### A3. Mandate Compliance for Coding (M1, M2, M4, M9, M13, M16, M21, M23)
**Priority**: CRITICAL — Every commit must pass these  
**What Grok CLI knows**: Mandate list from orientation  
**What Grok CLI NEEDS — Code-Level Patterns**:

| Mandate | Code Pattern | Where Enforced |
|---------|--------------|----------------|
| **M1 AnyIO Absolute** | `anyio.to_thread.run_sync()` for blocking I/O, NO `asyncio` | `src/omega/memory/block_store.py:43-65`, `src/omega/oracle/model_gateway.py` |
| **M2 Engine-Stack Firewall** | NO `src/omega/` writes to `config/wads/`, use `config_resolver.WADS_DIR` | `src/omega/governance/sovereign_vetter.py:_check_firewall()` |
| **M4 Sequentiality** | Plan → Verify → Execute (no cowboy coding) | HMC Forge Cycles, `docs/strategy/D281_PHASE_II_IV_EXECUTION.md` |
| **M9 Error Integrity** | Typed `OmegaError` subtypes, NO bare `except:`, trace_id propagation | `src/omega/errors.py`, `src/omega/oracle/providers.py` |
| **M13 Temple-Grade** | `make temple-grade` gates T1-T11 | `Makefile`, `tests/contracts/test_firewall_checker.py` |
| **M16 Modularization** | NO hardcoded paths in `src/omega/` | `src/omega/governance/sovereign_vetter.py:_check_modularization()` |
| **M21 Gate Integrity** | `isinstance(result, ExpectedType)` contract tests | `tests/test_contract_m21.py` |
| **M23 Failure Integrity** | Tool failure = hard stop + `[TOOL-CHAIN-COLLAPSE]` | `SOVEREIGN_MANDATES.md` |

---

## 🔧 TIER B — THIS WEEK (Phase III-IV + D-282)

### B1. M2 Firewall Remediation (Phase III — 4 files)
**Target**: `src/omega/oracle/hierarchy.py`, `entity_registry.py`, `oracle.py:251`, `scraper.py:43`  
**Pattern**: Replace hardcoded WAD path constructions with `config_resolver` + `WadLoader`  
**Scope Correction**: `mandate_auditor.py` and `sovereign_vetter.py` are NOT violations (relative paths)

### B2. Codex Mechanism Separation (Phase IV)
**Target**: `scripts/hydration_header.md`, `scripts/codex_cat.py`, `Makefile`  
**Guardrail**: `make codex || (mv scripts/groups.json.bak scripts/groups.json && exit 1)` — restore on failure

### B3. sqlite-vec Strike 10 (D-282)
**Target**: WAL mode + `BEGIN IMMEDIATE` + checkpointing + concurrency tests  
**Key Files**: `src/omega/memory/sqlite_vec_adapter.py`, `tests/test_sqlite_vec_concurrency.py`  
**Researcher's Forge 2 Gaps**: Pydantic v2, WAL PRAGMA stack, power-law decay, 5700U optimizations

### B4. Testing & Quality Gates
**Commands**: `make test` (492+), `make temple-grade` (T1-T11), `make firewall-check` (M2), `make heritage-map` (M14), `make sovereignty` (M7)

---

## 🧠 TIER C — DEFERRED (D-283/D-284 + Mastery)

### C1. Mnemosyne Memory System (D-283)
- **Phase 1 DONE**: HybridSearchEngine (RRF k=60) + 20 contract tests + Memory Blocks (blocks.py, block_tools.py, block_store.py, sleep_time.py)
- **Phase 2 PENDING**: Three-tier persistence (Recall/Archival), SleepTimeAgent skeleton, ArchivalMemory integration
- **Architecture**: Core (HOT) → Recall (WARM) → Archival (COLD) — maps to Letta 2026 / Sefirot BEAM

### C2. Cognitive Acceleration (D-283)
- **cpu_optimizer.py** (821 lines, Zen 2 optimized) → EAGLE-3/DFlash speculative decoding
- **Iris interface** — speculative decode bridge
- **ContextBuilder** — token-aware sliding window + ACON compaction pipeline

### C3. Sovereign Hub (D-284)
- **OAuth 2.1 PKCE** + **SHIELDMCP Proxy** (Intent Digest)
- **T11 Temple-Grade** — IA2 Agent Security
- **Streamable HTTP** migration for MCP (Firecrawl SSE 405 issue)

### C4. Legacy Pattern Mining (Roc's Domain)
- **Enterprise RAG Pipeline** (xna-omega-legacy)
- **Circuit Breaker** patterns (omega-stack-legacy)
- **FAISS → sqlite-vec** migration
- **Stack-Cat snapshots** (versioned architecture)

### C5. SOTA Research (Researcher's Forge 2 — 8 Gaps)
1. Pydantic v2 migration patterns
2. sqlite-vec WAL + `BEGIN IMMEDIATE` on 5700U
3. Mnemosyne 3-pillar vs Letta/Mem0/Sefirot/Cognee
4. Power-law decay parameters (0.01-0.60/day)
5. Qliphoth → TDP two-label IFC bridge
6. Sleep-time agent patterns (Da'at daemon, Git-backed MemFS)
7. Cross-pollination integration patterns
8. 5700U-specific optimizations (AVX2, thermal, zRAM)

---

## 📋 LEARNING PATH

| Week | Focus | Deliverable |
|------|-------|-------------|
| **Week 1** | Tier A (A1, A2, A3) | D-281 Phase II commit + Phase III-IV ready |
| **Week 2** | Tier B (B1, B2, B3, B4) | D-281 complete PR + D-282 sqlite-vec Strike 10 PR |
| **Week 3+** | Tier C (C1-C5) | D-283 Mnemosyne Phase 2 + D-284 Sovereign Hub |

---

## 🔑 QUICK REFERENCE

| Need | Command / File |
|------|----------------|
| Run tests | `source .venv/bin/activate && python -m pytest tests/ -x -q` |
| Temple-Grade | `make temple-grade` |
| Firewall check | `make firewall-check` |
| Heritage map | `make heritage-map` |
| Sovereignty ratio | `make sovereignty` |
| Provider health | `omega-hub_get_omega_metrics()` |
| Hardware stats | `omega-hub_system_stats("hardware")` |
| Hivemind awareness | `omega-hub_hivemind_get_awareness()` |
| Post context | `omega-hub_hivemind_post_context(...)` |
| Submit handoff | `omega-hub_hivemind_submit_handoff(...)` |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ GROK_CLI_GAPS ⬡ P0-CRITICAL ⬡ 2026-07-17*