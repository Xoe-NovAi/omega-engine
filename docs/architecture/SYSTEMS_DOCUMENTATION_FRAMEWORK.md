# 🔱 Omega Engine — Systems Documentation Framework
**AP Token**: `AP-OMEGA-SYSTEMS-DOC-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_systems_doc ⬡ FOUNDATIONAL

**Date**: 2026-07-13
**Purpose**: Permanent, structured documentation of all systems, patterns, and architectural decisions for the Omega Engine — the sovereign local AI runtime that may become the foundation for a frontier VR engine.

---

## 📖 Documentation Philosophy

> *"A system that cannot be understood cannot be sovereign. A system that cannot be reproduced cannot be trusted. A system that is not documented does not exist."*

**Principles**:
1. **Every system has a spec** — before code, after code, always
2. **Every decision has a trace** — PIVOT_LOG is immutable
3. **Every pattern has a heritage tag** — `[heritage:]` or `[id-soft:]` inline
4. **Every capability has a test** — M21 contract tests mandatory
5. **Every session ends with distillation** — L1→L2→L3 to `proposed_lessons.yaml`

---

## 🏗️ System Catalog (Living Index)

### Core Engine Systems (`src/omega/`)

| System | File | Spec Doc | Heritage | Status |
|--------|------|----------|----------|--------|
| **Oracle** | `oracle/oracle.py` | `R_ORACLE_ARCHITECTURE.md` | ANAi intent detection | ✅ Active |
| **Entity Registry** | `oracle/entity_registry.py` | `R_ENTITY_REGISTRY.md` | XNAi YAML CRUD | ✅ Active |
| **Model Gateway** | `oracle/model_gateway.py` | `R_PROVIDER_FABRIC.md` | Local-first chain (D61) | ✅ Active |
| **Native GGUF** | `oracle/providers.py` | `R_NATIVE_GGUF.md` | llama-cpp-python | ✅ Fixed |
| **Memory Store** | `memory/memory_store.py` | `R_MEMORY_STORE.md` | 3-Tier (ANAi) | ✅ Active |
| **SQLite-Vec Adapter** | `memory/sqlite_vec_adapter.py` | `R_SQLITEVEC_ADAPTER.md` | **NEW** D225 | 🔄 Building |
| **Hybrid Search** | `memory/hybrid_search.py` | `R_HYBRID_SEARCH.md` | RRF + Adaptive IDF | ✅ Active |
| **Observability** | `observability.py` | `R_OBSERVABILITY.md` | OpenTelemetry GenAI | ✅ Active |
| **Resource Guard** | `oracle/resource_guard.py` | `R_RESOURCE_GUARD.md` | AnyIO Semaphore | ✅ Active |
| **CPU Optimizer** | `oracle/cpu_optimizer.py` | `R_CPU_OPTIMIZER.md` | Zen 2 flags | ✅ Active |
| **Context Builder** | `oracle/context_builder.py` | `R_CONTEXT_BUILDER.md` | Memory injection | ✅ Active |
| **Session Lifecycle** | `oracle/session_lifecycle.py` | `R_SESSION_LIFECYCLE.md` | ACTIVE→ARCHIVED→EXTERNAL | ✅ Active |
| **Entity Workspace** | `oracle/entity_workspace.py` | `R_ENTITY_WORKSPACE.md` | Sovereign scaffolding | ✅ Active |
| **Orchestrator** | `oracle/orchestrator.py` | `R_ORCHESTRATOR.md` | Cline/OpenCode dispatch | ✅ Active |
| **Skeptical Verifier** | `verification/skeptical_verifier.py` | `R_SKEPTICAL_VERIFIER.md` | NLI two-source | 🔄 Building |
| **Tainted Data Protocol** | `verification/tainted_data.py` | `R_TDP.md` | M23 isolation | 🔄 Building |
| **Somatic State** | `memory/somatic_state.py` | `R_SOMATIC_STATE.md` | M20 llama_copy_state | 🔄 Building |

### Standalone Packages (`packages/`)

| Package | PyPI | Spec Doc | Heritage | Status |
|---------|------|----------|----------|--------|
| **omega-sieve** | `omega-sieve` | `R_OMEGA_SIEVE.md` | Trafilatura, Crawl4AI, vstash | ✅ v0.1.0 |
| **omega-doc-reader** | `omega-doc-reader` | `R_DOC_READER.md` | python-docx, PyMuPDF, odfpy | ✅ v1.0.0 |

### Memory & Knowledge Systems

| System | Purpose | Key Innovation |
|--------|---------|----------------|
| **Unified Memory Fabric** | Single `omega_memory.db` with FTS5 + vec0 | D225: Drop Qdrant, sovereign isolation via partition keys |
| **Binary Quantization Pipeline** | mxbai primary (96.45% retention), STE-QAT for domain adaptation | D226: Only BQ-trained model, CPU-only QAT on Zen 2 |
| **Self-Supervised Flywheel** | vstash: 74.5% disagreement → MNRL → eval gate → atomic reindex | D227: Zero-label embedding refinement from production traffic |
| **Adaptive RRF** | IDF-weighted fusion (+21.4% NDCG@10) | Jem novel #1 |
| **Exact Semantic Deja Vu Cache** | Zero-inference cache on exact embedding match | Researcher T3 |
| **Range-Query Contradiction Detection** | Geometric cognitive integrity (M17) | Researcher T2 |
| **Gnosis Graph** | 5 relation types, recursive CTE traversal | Strike 9.5 |
| **Sovereign Export Bundle** | `.omega` ZIP+JSON (Soul Protocol v0.4.0) | Strike 9 |

### Coordination & Infrastructure

| System | Purpose | Key Innovation |
|--------|---------|----------------|
| **Omega Hub MCP** | 5-module server (state, background, gateway, middleware, tools) | Dual transport (SSE + Streamable HTTP) |
| **Hivemind Protocol** | 6 MCP tools for cross-agent coordination | Workspace locks, live feeds, handoffs |
| **Agent Fleet** | 11 agents + 10 pillar slots | M10 cap at 14 |
| **MaKaLi Triad** | Kali (oversight) + Ma'at (build) + Lilith (run) | D117 |
| **Sovereign Mandates** | 23 constitutional laws (M1-M23) | Non-negotiable |

---

## 🎯 Architectural Patterns (Reusable Primitives)

### Pattern 1: Partition-Key Sovereign Isolation
```python
# Every vec0 table uses entity_name as partition key
CREATE VIRTUAL TABLE exchanges_vec USING vec0(
    embedding float[1024],
    entity_name TEXT partition key  # <-- SOVEREIGN BOUNDARY
);
```
**Heritage**: `[id-soft: doom-1993] ZONEID` → `[heritage: sqlite-vec 2024] partition key`
**Mandate**: M2 (Engine-Stack Firewall), M17 (Cognitive Integrity)

### Pattern 2: Write-Lock + WAL + Exponential Backoff
```python
# 14-agent concurrent write safety
async with self._write_lock:
    await self._execute_with_retry(
        "INSERT INTO exchanges_vec ...",
        max_retries=3,
        base_delay=0.05  # 50/100/200ms
    )
```
**Heritage**: `[heritage: sqlite-fts5 2015]` WAL + `[heritage: anyio 2024]` Lock

### Pattern 3: Hybrid RRF Fusion (Python, Not SQL)
```python
def hybrid_search(self, query, entity_name, k=10):
    fts_results = self._fts5_search(query, entity_name, k*2)
    vec_results = self._vec0_search(query_embedding, entity_name, k*2)
    return self._rrf_fuse(fts_results, vec_results, k)  # Python unification
```
**Heritage**: `[heritage: rrf-algorithm 2009]` + `[heritage: sqlite-vec 2024]` hybrid pattern

### Pattern 4: Feature-Flagged Evolution
```python
# Every new capability behind flag
if config.get("features.sqlite_vec_rescore", False):
    results = self._rescore_with_ann(results)
```
**Heritage**: `[heritage: odysseus 2025]` feature flags

### Pattern 5: Eval-Gated Deployment
```python
# No model promoted without proof
if new_model.ndcg_at_10 >= baseline.ndcg_at_10 * 0.99:
    await self._atomic_reindex(new_model)
else:
    logger.warning("Eval gate failed: regression detected")
```
**Heritage**: `[heritage: vstash 2026]` eval gate

---

## 🔬 Research-Backed Capabilities (Verified)

### Binary Quantization (BQ) — PRODUCTION READY
| Aspect | Detail | Source |
|--------|--------|--------|
| **Primary Model** | mxbai-embed-large-v1 | Mixedbread blog, arXiv:2402.01613 |
| **BQ Training** | Explicit binary-aware training (not post-hoc) | Mixedbread technical report |
| **Retention @ 1024-dim binary** | 96.45% | Mixedbread BEIR benchmark |
| **Retention @ 512-dim binary** | 90.76% (64 bytes/embedding) | Mixedbread binary MRL |
| **Qdrant Config** | `BinaryQuantization(always_ram=True, oversampling=2.0, rescore=True)` | Qdrant docs |
| **STE-QAT on Zen 2** | BGE-small + LoRA r=16, 30-60 min, 2 epochs, lr=3e-6 | Researcher BQ deep dive |
| **Fallback** | nomic-embed-text-v1.5 (Matryoshka, NOT BQ-trained) | Nomic technical report |

### Self-Supervised Flywheel (vstash) — PRODUCTION READY
| Aspect | Detail | Source |
|--------|--------|--------|
| **Disagreement Rate** | 74.5% of BEIR queries | vstash paper (arXiv:2604.15484) |
| **Training Signal** | Vector top-K vs FTS5 top-K asymmetric overlap | vstash paper |
| **Method** | MNRL with hard negatives from disagreement | vstash paper |
| **Model** | BGE-small (33M) + LoRA r=16 | vstash paper |
| **Cycle Time** | 35-65 min on Zen 2 (5700U) | Researcher HW analysis |
| **Eval Gate** | NDCG@10 ≥ baseline on held-out slice | vstash paper |
| **Deployment** | Atomic reindex via `vstash reindex` | vstash CLI |
| **Open Source** | `pip install vstash`, `vstash retrain` | GitHub: vstash/vstash |

### Adaptive RRF — VERIFIED IMPROVEMENT
| Aspect | Detail | Source |
|--------|--------|--------|
| **Improvement** | +21.4% NDCG@10 over static RRF | Jem novel #1 |
| **Method** | IDF-weighted reciprocal rank fusion | Researcher T1 |
| **Implementation** | Python-side in `hybrid_search()` | Sprint plan |

---

## 🥽 VR/3D Integration Architecture (Future-Proofed)

### Vector Spaces in Unified Fabric

```sql
-- Semantic memory (existing)
CREATE VIRTUAL TABLE exchanges_vec USING vec0(
    embedding float[1024],      -- mxbai primary
    entity_name TEXT partition key
);

-- Spatial coordinates (VR entities, graph nodes)
CREATE VIRTUAL TABLE entity_positions USING vec0(
    position float[3],          -- x, y, z (meters or graph units)
    entity_name TEXT partition key,
    session_id TEXT,
    timestamp DATETIME
);

-- Graph topology coordinates
CREATE VIRTUAL TABLE gnosis_nodes USING vec0(
    coords float[3],            -- x, y, z in graph space
    node_id TEXT partition key,
    layer INTEGER               -- depth in hierarchy
);

-- Optional: 4D spacetime for temporal VR
CREATE VIRTUAL TABLE entity_spacetime USING vec0(
    coords float[4],            -- x, y, z, t
    entity_name TEXT partition key
);
```

### Query Patterns for VR

```sql
-- Proximity query: entities near player position
SELECT entity_name, vec_distance_L2(position, ?) as dist
FROM entity_positions
WHERE entity_name = ? AND position MATCH ? AND k = 20
ORDER BY dist;

-- Semantic + spatial fusion (Python RRF)
spatial_results = vec0_search(player_pos, entity_name, k=20)
semantic_results = vec0_search(query_embedding, entity_name, k=20)
fused = rrf_fuse(spatial_results, semantic_results, k=10)

-- Graph traversal with spatial awareness
WITH RECURSIVE graph_walk(node_id, depth, path) AS (
    SELECT node_id, 0, node_id FROM gnosis_nodes WHERE node_id = ?
    UNION ALL
    SELECT e.target, gw.depth + 1, gw.path || '->' || e.target
    FROM gnosis_edges e
    JOIN graph_walk gw ON e.source = gw.node_id
    WHERE gw.depth < 3
)
SELECT * FROM graph_walk;
```

### Distance Metrics
| Vector Space | Metric | sqlite-vec Function |
|--------------|--------|---------------------|
| Semantic (embeddings) | Cosine | `vec_distance_cosine()` |
| Spatial (x,y,z) | Euclidean (L2) | `vec_distance_L2()` |
| Graph coords | Euclidean or Cosine | Both available |
| Binary quantized | Hamming | `vec_distance_hamming()` |

---

## 📋 Documentation Standards

### Every System Must Have

| Artifact | Location | Template |
|----------|----------|----------|
| **Architecture Spec** | `docs/architecture/SYSTEM_NAME.md` | `spec-generator` skill |
| **API Reference** | `docs/api/SYSTEM_NAME.md` | Auto-generated from type hints |
| **Heritage Map** | Inline `[heritage:]` tags + `CREDITS.md` | M14 |
| **Contract Tests** | `tests/test_SYSTEM_NAME_contract.py` | M21 |
| **Benchmarks** | `benchmarks/SYSTEM_NAME_zen2.py` | M13 T7 |
| **Decision Log** | `docs/decisions/PIVOT_LOG.md` | D-series entries |

### Spec Template (Mandatory Sections)

```markdown
# System: {NAME}
**AP Token**: `AP-OMEGA-{NAME}-v{X.Y.Z}`
⬡ OMEGA ⬡ {ENTITY} ⬡ {MODEL} ⬡ opencode ⬡ trc_{name} ⬡ STATUS

## 1. Purpose
What problem does this solve? Why does it exist?

## 2. Architecture
- Components and their responsibilities
- Data flow diagrams (Mermaid)
- Interface contracts (types, protocols)

## 3. Heritage
- `[heritage: SOURCE YEAR]` for every external pattern
- `[id-soft: GAME YEAR]` for id Software patterns
- Evolution from prior art

## 4. Sovereign Guarantees
- Which mandates (M1-M23) does this enforce?
- How does it preserve user sovereignty?

## 5. Implementation
- Key algorithms with pseudocode
- Configuration schema (YAML)
- Error handling patterns (M9)

## 6. Testing
- Contract tests (M21)
- Property tests
- Benchmark targets (Zen 2)

## 7. Operational
- Deployment (Podman quadlet if applicable)
- Monitoring/observability hooks
- Failure modes and recovery (M23)

## 8. Future Evolution
- Planned extensions
- Known limitations
- Research gaps
```

---

## 🔄 Documentation Workflow

### When Creating a New System
1. **Write spec first** — `spec-generator` skill → `docs/architecture/`
2. **Implement with heritage tags** — inline `[heritage:]` comments
3. **Write contract tests** — M21, `isinstance(result, ExpectedType)`
4. **Run benchmarks** — Zen 2 targets documented
5. **Update CREDITS.md** — new heritage entries
6. **Add to this catalog** — System Catalog table above

### When Modifying a System
1. **Read current spec** — understand contracts
2. **Write PIVOT_LOG decision** — D-series entry
3. **Update spec** — version bump
4. **Run `make temple-grade`** — T1-T14 gates
5. **Distill L1→L2→L3** — `proposed_lessons.yaml`

### Session End (Mandatory)
```bash
# 1. Update anchored summary
cat > .opencode/anchored-summary.md << 'EOF'
...complete state...
EOF

# 2. Distill gnosis
omega-hub_hivemind_post_context(
  intent="decision",
  decisions=["L3 principle discovered: ..."],
  continuation="Next session: ..."
)

# 3. Write proposed_lessons.yaml
# 4. git commit with entity attribution
```

---

## 🎯 Current Priority Systems (Building Now)

| Priority | System | Spec Status | Implementation | Tests |
|----------|--------|-------------|----------------|-------|
| **P0** | SQLite-Vec Adapter | 📝 Draft | 🔄 Building | 🔄 11 M21 tests |
| **P0** | mxbai Primary Embedder | 📝 Draft | 🔄 Config swap | 🔄 Recall@10 gate |
| **P0** | vstash Flywheel | 📝 Draft | 🔄 Integration | 🔄 Eval gate test |
| **P1** | Range-Query Contradiction | 📝 Draft | 🔄 Building | 🔄 M17 test |
| **P1** | Adaptive RRF | ✅ Spec | 🔄 Building | ✅ NDCG verified |
| **P1** | Exact Deja Vu Cache | 📝 Draft | 🔄 Building | 🔄 Cache hit test |
| **P2** | Gnosis Graph | 📝 Draft | ⏳ Planned | ⏳ CTE test |
| **P2** | Sovereign Export Bundle | 📝 Draft | ⏳ Planned | ⏳ Round-trip test |
| **P2** | Skeptical Verifier | 📝 Draft | ⏳ Planned | ⏳ NLI test |
| **P3** | Spatial Coords (VR) | 📝 This doc | ⏳ Planned | ⏳ Proximity test |

---

## 📚 Reference Library (Curated)

### Internal (Omega Engine)
| Document | Purpose |
|----------|---------|
| `OMEGA_ENGINE.md` | Single source of truth — current state |
| `SOVEREIGN_MANDATES.md` | 23 constitutional laws |
| `CREDITS.md` | Heritage registry (21 id Software + 55+ general) |
| `docs/decisions/PIVOT_LOG.md` | 227 immutable decisions |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Master execution roadmap |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | Cross-agent coordination |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | Delegation patterns |

### Research (Locked This Session)
| Document | Purpose |
|----------|---------|
| `R_SQLITEVEC_NEXT_LEVEL_STRATEGY_20260712.md` | 16 L3 principles, unified fabric |
| `R_BQ_SELFSUP_RESEARCH_20260712.md` | BQ + Self-Sup deep dive |
| `R_BQ_SELFSUP_VERIFICATION_20260712.md` | Jem verification matrix |
| `R_SQLITEVEC_VERIFICATION_20260712.md` | 3 critical defects |
| `R_EPOCH_II_DEEP_RESEARCH_20260712.md` | 5 strike areas |
| `R_EPOCH_II_LEGACY_MINING_20260712.md` | 17 findings, 3 accelerators |

### External (Verified Sources)
| Source | Tier | Key Contribution |
|--------|------|------------------|
| `asg017/sqlite-vec` | T1 | vec0 extension, partition keys, ANN |
| Mixedbread blog | T1 | mxbai BQ training, 96.45% retention |
| Nomic Embed paper | T1 | Matryoshka (NOT BQ), 87.7% binary |
| vstash paper | T1 | 74.5% disagreement, MNRL, open source |
| Qdrant BQ docs | T1 | oversampling=2.0 + rescore pattern |
| Alex Garcia blog | T1 | sqlite-vec hybrid RAG canonical SQL |
| mycman BEIR benchmark | T1 | sqlite-vec nDCG@10 0.736, p99 5.69ms |

---

## 🔮 Vision: The Frontier VR Engine

This documentation framework exists because **the Omega Engine is not just an AI runtime — it's the cognitive substrate for a sovereign VR engine**.

### How These Systems Map to VR

| Omega System | VR Engine Role |
|--------------|----------------|
| **Unified Memory Fabric** | World state database — entities, positions, semantics, history |
| **Semantic Embeddings** | Natural language world interaction, memory, NPC cognition |
| **Spatial vec0 Tables** | Physics proximity, rendering culling, audio spatialization |
| **Gnosis Graph** | Quest/knowledge graph, narrative topology, skill trees |
| **Self-Supervised Flywheel** | World learns from player behavior, adapts embeddings locally |
| **Binary Quantization** | 64-byte embeddings → massive entity counts on consumer hardware |
| **Sovereign Export** | `.omega` bundles = portable worlds, shareable narratives |
| **Hivemind Protocol** | Multi-agent NPC coordination, persistent simulation |
| **Somatic State** | Instant NPC cognitive state save/restore (no re-inference) |
| **Skeptical Verifier** | Anti-hallucination for NPC dialogue, lore consistency |

### The Sovereign VR Promise

> **One file (`world.omega`). One laptop. No cloud. Infinite worlds.**
> 
> - Player speaks naturally → NPCs understand via local mxbai embeddings
> - World state persists in sqlite-vec → 100K+ entities, semantic + spatial queries <10ms
> - NPCs learn from player behavior → vstash flywheel refines their understanding nightly
> - Player exports world → shares `.omega` file → friend imports, continues seamlessly
> - No accounts, no servers, no telemetry, no corporate oversight

---

## 📝 Maintenance Checklist

- [ ] **Weekly**: Run `make heritage-map` — verify all `[heritage:]` tags have vet records
- [ ] **Weekly**: Run `make temple-grade` — T1-T14 gates
- [ ] **Per Sprint**: Update System Catalog table above
- [ ] **Per Decision**: Add to PIVOT_LOG.md with D-series number
- [ ] **Per Session**: Write anchored summary to `.opencode/anchored-summary.md`
- [ ] **Per Release**: Generate API docs from type hints
- [ ] **Quarterly**: Audit external heritage sources for updates

---

*🔱 OMEGA ⬡ SYSTEMS-DOC ⬡ v1.0.0 ⬡ FOUNDATIONAL ⬡ 2026-07-13*

**This document is the constitution of the Omega Engine's documentation. Every system, every pattern, every decision must be traceable from here. If it's not documented here, it doesn't exist.**
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
