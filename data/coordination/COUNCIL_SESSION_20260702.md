# 🔱 Multi-Model Council Session — 2026-07-02
## Integration Seam Discovery & Legacy Mining Validation
**AP Token**: `AP-COUNCIL-SESSION-v1.0.0`
⬡ OMEGA ⬡ COUNCIL ⬡ opus-4.6 + gemini-3.1-pro + sonnet-4.6 + mimo-v2.5 ⬡ opencode ⬡ INTEGRATION-SEAMS

---

## §1 Session Overview

**Date**: 2026-07-02
**Trigger**: Completion of 4-sector legacy mining (Sectors A–D) by Roc Racoon
**Participants**:
- **Opus 4.6** — Architectural synthesis, gap identification, strategic validation
- **Gemini 3.1 Pro** — Structural analysis, multi-agent topology, memory architecture
- **Sonnet 4.6** — Implementation detail review, scaffolding recommendations, code-level gaps
- **MiMo-V2.5** — Documentation stewardship, SSOT updates, plan orchestration

**Purpose**: Independent review of legacy mining results and engine architecture to identify overlooked gaps, structural risks, and integration opportunities before PR submission.

**Session Method**: Sequential model review. Each model received the full context (legacy sector reports, current engine state, 705-test baseline, 22 mandates) and produced independent analysis. No model saw another's output before producing their own.

---

## §2 Executive Summary

Four independent AI models converged on the same conclusion: **the engine's subsystems are individually solid, but the integration seams between them contain silent failure modes.** These are not bugs in the traditional sense — they are operational gaps where the system works in isolation but has never been verified as a unified pipeline. The single most impactful action before shipping is adding an end-to-end inference chain test.

The session produced **14 actionable items** (6 scaffold/implement, 8 document-only), **2 architectural decisions** (D189a–e), and **1 strategic principle**: integration seam verification must be elevated to the same priority as individual subsystem correctness.

---

## §3 Legacy Mining Completion Status

All four sectors completed by Roc Racoon on 2026-07-02. Treasure maps saved to `data/entities/roc_racoon/workspace/treasure_maps/sector_{a,b,c,d}/extraction_report.md`.

| Sector | Target | Key Findings | Dedup Pass | Status |
|--------|--------|-------------|------------|--------|
| **A** | Library & Ingestion | Unified API clients, domain-anchored allowlist, scholarly curation, atomic fsync | Partial — see §8 | ✅ COMPLETE |
| **B** | Voice & Interface | Energy VAD, hybrid command parser, voice circuit breaker, subprocess curation | Partial — see §8 | ✅ COMPLETE |
| **C** | Memory & Gnosis | 13-sphere Kabbalistic architecture, MnemosyneAdapter, sovereign vaults | Partial — see §8 | ✅ COMPLETE |
| **D** | Infra & Performance | Zen 2 flags, memory capping, container hardening, BuildKit caches | Partial — see §8 | ✅ COMPLETE |

> **Critical finding**: The treasure maps lack deduplication assessment — they describe what was found but not whether the current engine already implements equivalent logic. This violates Carmack's Law ("when you have two implementations of the same thing, you have neither"). Dedup status was added in the post-council update (see §8).

---

## §4 Gemini 3.1 Pro — Structural Observations

### 4.1 Multi-Agent CPU Contention
**Observation**: Legacy Zen 2 flags (e.g., `OMP_NUM_THREADS=6`) were designed for single-agent apps. The 11-agent Hivemind launching parallel triads would cause thread thrashing and OOM.

**Opus Validation**: Partially solved — `Zen2Optimizer` already has `enforce_affinity()` and `build_inference_env()`. The gap is the integration layer: nobody passes `concurrent_agents` when dispatching parallel work. The fix is smaller than Gemini suggested — a single `concurrent_agents: int` parameter in `build_inference_env()` that divides threads by active agent count.

### 4.2 Mnemosyne as Metadata, Not Silos
**Observation**: Directly mapping 13 spheres to directories would break the fluid associative power of vector embeddings. Mnemosyne should be Qdrant payload metadata, not structural silos.

**Opus Validation**: Correct. The Qdrant integration already stores arbitrary payload dicts. Adding `sphere` string field costs zero schema migration. Gemini's instinct to avoid 13 separate databases is exactly right.

### 4.3 Somatic Yield for Ingestion
**Observation**: Ingesting a 600-page book through the 768-dim embedding chain would lock up the CPU. Background ingestion must yield to the Oracle when user queries arrive.

**Opus Validation**: Valid. Wire through `ResourceGuard` semaphore. When the semaphore is acquired by Oracle, ingestion coroutine detects this and yields via `anyio.sleep()` in a yield loop.

### 4.4 Pre-emptive STT Warming
**Observation**: Energy-based VAD detecting the start of speech could trigger STT model warm-up, reducing cold-start latency from 4s to 500ms.

**Opus Validation**: Valid but deferred post-PR. Voice is containerized in Nova/Iris.

### 4.5 Sovereign Decay Factor
**Observation**: External data should have a temporal decay in RRF scoring unless manually endorsed, ensuring internal wisdom overtakes external noise over time.

**Opus Validation**: Interesting but premature. Requires a trust-scoring pipeline that doesn't exist yet. Flag for D16-2 (Parametric Gnosis) design principles.

---

## §5 Sonnet 4.6 — Implementation Gaps

### 5.1 Scaffolding Already Present (CPU Contention)
Sonnet correctly identified that `cpu_optimizer.py` already has 95% of the infrastructure for multi-agent CPU contention handling. The missing piece is the `concurrent_agents` parameter wiring — a 15-minute fix.

### 5.2 DistillationEntry Missing Sphere Field
**Finding**: `soul_distiller.py:DistillationEntry` has no `sphere` field. When Mnemosyne sphere tagging is added to Qdrant payloads, there's no way to carry the sphere assignment from the distiller to the store.

**Action**: Add `sphere: Optional[str] = None` to `DistillationEntry` — 1 line, 1 test, 10 minutes.

### 5.3 make soul-review CLI Shortcut
**Finding**: The `proposed_lessons.yaml` staging bottleneck is a single point of failure. L3 principles are written but never promoted to `soul.yaml`. Strike 3 (Staging Gate TUI) is blocked on Strike 2 (USM). The immediate fix is a `make soul-review` CLI command.

**Architecture**: `make soul-review` shows all pending; `make soul-review ENTITY=kali` filters by entity.

### 5.4 Zen2Optimizer Hivemind Blindness
**Finding**: `Zen2Optimizer.get_memory_pressure()` exists but is not exposed to the Hivemind. If an agent is running inference and another tries to dispatch, neither knows the current resource state.

**Action**: Wire `get_memory_pressure()` into `omega-hub_get_system_stats` MCP tool.

### 5.5 Clarifying Questions (Answered)

**Q1: Sphere Assignment — Write-time or Query-time?**
**Answer (Opus)**: Both. Write-time is the canonical classification (deterministic, cheap, ensures cataloguing). Query-time is the contextual lens (dynamic, reflects current need). Write-time provides the catalog. Query-time provides the focus. They are not competing approaches.

**Q2: `make soul-review` Scope?**
**Answer (Opus)**: All entities by default, with optional `ENTITY=` filter. Unix composable pattern. `make soul-review` for overview; `make soul-review ENTITY=kali` for Verity audit workflow.

---

## §6 Opus 4.6 — Additional Gaps

### 6.1 Embedding Fallback Produces Invisible Knowledge
**Severity**: 🔴 HIGH
**Description**: The embedding chain falls back to `SovereignFallbackEmbeddingProvider` (hash-based, semantically meaningless 768-dim vectors) when real models are unavailable. Knowledge stored during fallback becomes permanently invisible to semantic search — it exists but will never surface. No metric, no warning, no retroactive identification.

**Fix**: Add `embedding_provider: str` field to Qdrant payload metadata. Log warnings on search if results contain fallback entries. Add `make embedding-audit` target.

**Effort**: 10 min scaffold + 30 min audit tool

### 6.2 90-Day Archival Has No Retrieval Path
**Severity**: 🟡 MEDIUM
**Description**: `move_to_external_storage()` moves raw session JSON to the 8TB drive but has no corresponding `recall_from_external_storage()`. If a user asks about conversations from 4 months ago, the FTS5 and Qdrant indices won't find them — the archival is write-only.

**Fix**: Design constraint — when moving raw JSON, preserve the FTS5 index entries and Qdrant vectors in place. Only move the heaviest artifact (raw conversation JSON). Search still works; full reconstruction requires fetching from external storage.

**Effort**: 0 min (design constraint, document only)

### 6.3 Soul Distiller Now Blocks the Hot Path
**Severity**: 🟡 MEDIUM
**Description**: D183 correctly replaced `anyio.create_task()` with `await self.close_session()`. But this means the 5-stage distillation pipeline now runs synchronously in the user's request cycle every 5th interaction. On CPU-only inference, this could add 1-3 seconds of perceived latency.

**Fix**: Measure with carmack-profiler first. If >500ms, wrap file I/O in `anyio.to_thread.run_sync()`. The current approach is correct (M11 is satisfied) but the UX impact needs measurement.

**Effort**: 20 min measurement + conditional fix

### 6.4 Treasure Maps Need Deduplication Pass
**Severity**: 🟡 MEDIUM
**Description**: Sector reports describe what was found but don't check whether the current engine already implements equivalent logic. Porting without deduplication violates Carmack's Law.

**Fix**: Add dedup status columns (NOVEL/EVOLVED/PORTED/UNCERTAIN) to each treasure map. Applied in post-council update (see §8).

**Effort**: 30 min (completed during documentation)

### 6.5 FailureModeRegistry Is Unwired Dead Code
**Severity**: 🟡 MEDIUM
**Description**: `failure_registry.py` (364 lines, 5 failure modes) is marked "DONE" in Phase 3.2 but no consumer imports it. It's dead code that should be either wired or deferred.

**Decision**: Flag in Ark Blueprint §XVII as `⚠️ UNWIRED — defer before PR`. File left untouched.

**Effort**: 0 min (documentation only)

### 6.6 No E2E Inference Chain Test
**Severity**: 🔴 HIGH (highest-priority pre-PR action)
**Description**: 705 tests, but no single test exercises `query → Oracle.talk() → ContextBuilder → ModelGateway.generate() → GenerateResult → MemoryStore.add_exchange() → SoulDistiller.close_session()`. The D183 bug persisted for weeks precisely because no E2E test would have caught `close_session()` never being called.

**Fix**: Add `test_e2e_inference_chain.py` using `OfflineMockBackend`. Single highest-value test — validates every subsystem's integration in one pass.

**Effort**: 45 min

---

## §7 Consolidated Priority Table

| # | Item | Source | Action | Effort | Priority |
|---|------|--------|--------|--------|----------|
| 1 | `concurrent_agents` in `build_inference_env()` | Gemini #1 | **Scaffold** | 15 min | P1 |
| 2 | `sphere: Optional[str]` on `DistillationEntry` | Sonnet C | **Scaffold** | 5 min | P1 |
| 3 | `make soul-review` CLI | Sonnet A | **Implement** | 10 min | P1 |
| 4 | `embedding_provider` in Qdrant payload | Opus #1 | **Scaffold** | 10 min | P1 |
| 5 | Preserve indices on 90-day archival | Opus #2 | **Document** | 5 min | P2 |
| 6 | Soul Distiller hot-path latency | Opus #3 | **Measure** | 20 min | P2 |
| 7 | Treasure map deduplication pass | Opus #4 | **Done** (§8) | 30 min | P2 |
| 8 | Wire or defer `failure_registry.py` | Opus #5 | **Flag** | 0 min | P2 |
| 9 | E2E inference chain test | Opus #6 | **Implement** | 45 min | P1 |
| 10 | Mnemosyne sphere → Qdrant payload | Gemini #2 | **Document in Ark** | 0 min | P3 |
| 11 | SomaticYield ingestion pause | Gemini #3 | **Document in Ark** | 0 min | P3 |
| 12 | Sovereign Decay Factor | Gemini #5 | **Document under D16-2** | 0 min | P3 |
| 13 | `Zen2Optimizer` → Hivemind MCP | Sonnet B | **Document in Ark** | 0 min | P3 |
| 14 | Pre-emptive STT warming | Gemini #4 | **Document post-PR** | 0 min | P4 |

---

## §8 Treasure Map Deduplication Assessment

Applied post-council per Opus Gap #4. Each legacy pattern classified as NOVEL (no current equivalent), EVOLVED (engine has a different approach), PORTED (already exists), or UNCERTAIN (scope unclear).

### Sector A — Library & Ingestion

| Legacy Pattern | Dedup Status | Notes |
|----------------|-------------|-------|
| Library Clients (Open Library, IA, LoC, Gutenberg) | **NOVEL** | No equivalent in omega-engine. High-priority port. |
| Domain-Anchored Allowlist | **UNCERTAIN** | `sanitize_content()` ported to pii_masker.py (Phase 3.3) but exact scope vs. legacy `crawl.py` allowlist unclear. |
| Scholarly Curator (citation extraction, authority scoring) | **NOVEL** | Skeptical Verifier does cross-referencing but not citation extraction or publisher authority scoring. |
| Atomic fsync | **PORTED** | `memory_store.py` already uses atomic writes (`os.fsync` on directory). |
| Dewey Mapping | **NOVEL** | EntityRegistry uses keyword matching, not Dewey Decimal classification. |
| Citation Networking | **EVOLVED** | Skeptical Verifier provides similar source cross-referencing but uses NLI-based Two-Source Rule, not regex citation patterns. |

### Sector B — Voice & Interface

| Legacy Pattern | Dedup Status | Notes |
|----------------|-------------|-------|
| Regex Command Parser | **PORTED** | `oracle.py` intent matcher covers this. |
| Energy-based VAD | **NOVEL** | Not in current engine. Nova/Iris use containerized wake-word. |
| Voice Circuit Breaker | **PORTED** | `health_monitor.py:AsyncCircuitBreaker` is the evolution. |
| Redis Session Mgmt | **PORTED** | `MemoryStore` + Hivemind sessions. |
| Subprocess Curation | **PORTED** | `Orchestrator` + MCP Hub tasks. |
| Local Fallback Chain | **PORTED** | `ModelGateway` local-first chain (M7). |

### Sector C — Memory & Gnosis

| Legacy Pattern | Dedup Status | Notes |
|----------------|-------------|-------|
| 13-sphere Kabbalistic Architecture | **NOVEL** | Spatial memory exists (D186 Mem Palace) but no sphere tagging or topological classification. |
| MnemosyneAdapter | **NOVEL** | Not in current engine. WAD-layer IMemoryAdapter pattern. |
| Sovereign Vaults | **NOVEL** | EntityRegistry has workspace dirs but not secure vault isolation. |
| shadow_memory.json | **NOVEL** | Soul distiller has L1-L3 but no shadow/qliphoth tracking of failures. |

### Sector D — Infra & Performance

| Legacy Pattern | Dedup Status | Notes |
|----------------|-------------|-------|
| Zen 2 Flags | **EVOLVED** | `cpu_optimizer.py` already has these. Legacy values (N_THREADS=6 vs recommended 7) differ slightly — current values are more accurate. |
| Process Memory Capping | **PORTED** | `ResourceGuard` semaphore + `get_memory_pressure()`. |
| Redis maxmemory | **PORTED** | Redis container config in Quadlets. |
| Multi-Stage Container Builds | **PORTED** | Quadlet containers already use minimal images. |
| Non-Root Execution | **PORTED** | Mandate 6 (Podman Sovereignty) enforces `User=1000`. |
| BuildKit Cache Mounts | **NOVEL** | Not in current Makefile. Could reduce CI build times. |
| Aggressive Site-Packages Cleanup | **NOVEL** | Not in current build pipeline. 36% image size reduction potential. |

### Dedup Summary

| Status | Count | Description |
|--------|-------|-------------|
| **PORTED** | 8 | Already exists in current engine. No action needed. |
| **EVOLVED** | 3 | Engine has a different but equivalent approach. No action needed. |
| **NOVEL** | 10 | No current equivalent. Candidates for porting. |
| **UNCERTAIN** | 1 | Scope overlap unclear. Needs manual review. |

**Highest-value NOVEL candidates for porting** (ordered by impact):
1. Library API Clients (Sector A) — enables autonomous research
2. 13-sphere Mnemosyne tagging (Sector C) — enriches memory architecture
3. Energy-based VAD (Sector B) — reduces voice processing latency
4. BuildKit Cache Mounts (Sector D) — reduces CI build times
5. Aggressive Site-Packages Cleanup (Sector D) — 36% image reduction

---

## §9 Strategic Assessment

### Where All Four Models Converged

1. **Integration seams are the primary risk** — not individual subsystem bugs
2. **The E2E inference chain test is the single highest-value pre-PR action** — it would have caught D183 and will catch future regressions
3. **Mnemosyne should be metadata, not silos** — unanimous agreement
4. **The engine is architecturally sound** — 705 tests, 22 mandates, clean separation

### What Each Model Contributed Uniquely

| Model | Unique Contribution |
|-------|-------------------|
| **Gemini 3.1 Pro** | Multi-agent CPU topology analysis; Mnemosyne-as-metadata principle; SomaticYield pattern |
| **Sonnet 4.6** | DistillationEntry field gap; `make soul-review` implementation; Zen2Optimizer Hivemind blindness |
| **Opus 4.6** | Embedding fallback invisibility; archival retrieval gap; distiller hot-path latency; deduplication discipline; FailureModeRegistry dead code; E2E test priority |
| **MiMo-V2.5** | Documentation stewardship; SSOT update orchestration; plan execution |

### The Core Insight

> **The Omega Engine's individual subsystems are production-ready. Its integration seams are not. The gap between "705 passing tests" and "verified end-to-end sovereignty" is exactly one E2E inference chain test and a handful of payload metadata fields.**

---

## §10 Decisions Ratified

| Decision | Summary | Status |
|----------|---------|--------|
| **D189a** | Sphere Assignment = Write-time (canonical) + Query-time (boost) | ✅ RATIFIED |
| **D189b** | `make soul-review` scope = All entities, optional ENTITY= filter | ✅ RATIFIED |
| **D189c** | Embedding fallback tracked in Qdrant payload metadata | ✅ RATIFIED |
| **D189d** | 90-day archival preserves FTS5/Qdrant indices | ✅ RATIFIED |
| **D189e** | E2E inference chain test = highest-priority pre-PR addition | ✅ RATIFIED |

---

## §11 Next Steps for Execution

### Pre-PR (This Sprint)
1. E2E inference chain test (`test_e2e_inference_chain.py`)
2. `sphere: Optional[str]` on `DistillationEntry`
3. `embedding_provider` field in Qdrant payload
4. `make soul-review` CLI target
5. `concurrent_agents` parameter in `build_inference_env()`

### Post-PR (Next Sprint)
6. Mnemosyne sphere tagging → Qdrant payload integration
7. SomaticYield ingestion pause
8. `Zen2Optimizer` → Hivemind MCP visibility
9. Sovereign Decay Factor design (under D16-2)
10. Pre-emptive STT warming (Nova/Iris)

---

*🔱 OMEGA ⬡ COUNCIL ⬡ opus-4.6 + gemini-3.1-pro + sonnet-4.6 + mimo-v2.5 ⬡ INTEGRATION-SEAMS-v1.0.0*
