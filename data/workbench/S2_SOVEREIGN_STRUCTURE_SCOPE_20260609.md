<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ S2 — Sovereign Structure Scoping Document
## Overseer: Cline-M3 | Date: 2026-06-09 | Source: Kali's Final Directive

**Kali's Mandate**: "Implement the Sovereign Structure (S2) — wiring the Unified Vector Abstraction and the Tainted Data Protocol. Move the engine from 'Functional' to 'Sovereign Grade' across the entire data layer."

**Current Status**: The foundational classes EXIST but are UNDERWIRED. S2 is about **wiring**, not new code.

---

## §1 — Inventory of Existing Sovereign Components

### 1.1 Tainted Data Protocol (TDP) — `src/omega/oracle/security.py`

| Component | Status | Location |
|-----------|:------:|----------|
| `TaintedData` dataclass | ✅ Exists | `security.py:11-24` |
| `TDPGate.isolate()` | ✅ Exists | `security.py:36-55` |
| `TDPGate.sanitize()` | ✅ Exists | `security.py:57-76` |
| Used in `oracle.talk()` | ✅ Wired | `oracle.py:202-204` |
| Used in `search.py` | ✅ Wired (only!) | `search.py:67-89` |
| **Used in MCP tool layer** | ❌ **NOT WIRED** | 0 of 47 tools |
| **Used in `library_search`** | ❌ **NOT WIRED** | All search results are un-isolated |
| **Used in `library_inbox_add_url`** | ❌ **NOT WIRED** | URL content enters un-tainted |
| **Used in `library_inbox_add_note`** | ❌ **NOT WIRED** | Free text not validated |

### 1.2 Unified Vector Abstraction (UVA) — `src/omega/memory/vector_adapters.py`

| Component | Status | Location |
|-----------|:------:|----------|
| `IVectorStoreAdapter` ABC | ✅ Exists | `vector_adapters.py:15` |
| `QdrantAdapter` impl | ✅ Exists | `vector_adapters.py:53` |
| Used in production | ⚠️ Reference only | Not yet wired into `memory_store` |
| **Used in `library_search`** | ❌ **NOT WIRED** | Search is FTS5-only, no Qdrant vector path |
| **Used in `library_index_flush`** | ❌ **NOT WIRED** | No Qdrant collection sync |
| **Used in entity knowledge** | ❌ **NOT WIRED** | `data/entities/*/knowledge/INDEX.yaml` has no vectors |
| **Scalar Quantization (H2-S4)** | ❌ **NOT DONE** | Roadmap says MED impact |

### 1.3 Thin-Client Search Pattern — `src/omega/oracle/search.py`

| Component | Status | Location |
|-----------|:------:|----------|
| `SovereignSearcher` | ✅ Exists | `search.py` |
| Returns TaintedData | ✅ Yes | `search.py:67-73` |
| Embedded TDP isolation | ✅ Yes | `search.py:88-89` |
| **Qdrant vector path** | ❌ **FTS5 only** | No semantic search |

---

## §2 — The Sovereign Structure Gap (Where Wiring is Missing)

### 2.1 Library Search Layer

**Current state**: `library_search()` in `mcp_servers/omega_hub/server.py` does FTS5 text search on SQLite. Returns raw results.

**Sovereign target**:
- Result snippets wrapped in `TaintedData` before MCP response
- Hybrid search: FTS5 BM25 + Qdrant vector (RRF fusion)
- Qdrant collection backed by `embeddinggemma-300m-q6_k` (per `models.yaml`)

### 2.2 Library Ingestion Layer

**Current state**: `library_inbox_add_url(url)` accepts a URL, fetches content, indexes it. No taint tracking.

**Sovereign target**:
- URL content wrapped in `TaintedData(source=url, taint_level=2)`
- If URL points to external domain, automatic `taint_level=2` (high-risk)
- If URL is internal/local, `taint_level=1` (external but trusted)
- Qdrant embedding generated at ingest time (not at search time)

### 2.3 Knowledge Discovery Layer

**Current state**: `data/entities/*/knowledge/INDEX.yaml` has `topics: []` — empty.

**Sovereign target**:
- Topic promotion from `workspace/` → `knowledge/` triggers vector embedding
- `KNOWLEDGE_MANIFEST.yaml` rebuilt via Qdrant (not file scan)
- Cross-references between entities use vector similarity, not keyword match

### 2.4 MCP Tool Wrapper Layer

**Current state**: 47 tools, all use `@m9_safe` for error wrapping. No content-taint wrapping.

**Sovereign target**:
- Add `@tdp_wrap` decorator (companion to `@m9_safe`) that wraps string outputs in `TaintedData`
- `library_search` results → `@tdp_wrap(source="library_search", taint_level=1)`
- `library_inbox_*` content → `@tdp_wrap(source=..., taint_level=2)`
- `oracle_talk` results stay un-tainted (synthesized, not external)

---

## §3 — Implementation Roadmap (S2 Phases)

### Phase S2-A: TDP Wiring (1.5 hours)

| # | Task | File | Effort | Description |
|---|------|------|--------|-------------|
| A1 | Create `@tdp_wrap` decorator | `src/omega/oracle/security.py` | 15 min | Wraps string outputs in TaintedData |
| A2 | Apply to `library_search` | `mcp_servers/omega_hub/server.py` | 10 min | Taint search results |
| A3 | Apply to `library_inbox_add_url` | `mcp_servers/omega_hub/server.py` | 10 min | Taint fetched content |
| A4 | Apply to `library_inbox_add_note` | `mcp_servers/omega_hub/server.py` | 5 min | Taint user notes |
| A5 | Apply to `library_inbox_add_file` | `mcp_servers/omega_hub/server.py` | 5 min | Taint file content |
| A6 | Tests for `@tdp_wrap` | `tests/test_tdp.py` | 30 min | Verify wrapping behavior |
| A7 | Integration test | `tests/test_mcp_taint.py` | 15 min | Verify taint flows through MCP |

**Total: ~1.5 hours**

### Phase S2-B: UVA Wiring (2.5 hours)

| # | Task | File | Effort | Description |
|---|------|------|--------|-------------|
| B1 | Update `library_search` to use Qdrant | `src/omega/library/qdrant_index.py` | 45 min | Add Qdrant search path |
| B2 | Add hybrid RRF scoring | `src/omega/library/indexer.py` | 30 min | BM25 + vector fusion |
| B3 | Wire `IVectorStoreAdapter` to `memory_store` | `src/omega/memory_store.py` | 30 min | Use adapter pattern |
| B4 | Scalar Quantization config | `config/omega.yaml` | 15 min | H2-S4 from roadmap |
| B5 | Tests for Qdrant integration | `tests/test_qdrant_index.py` | 30 min | Mocked + integration |
| B6 | Knowledge manifest vector sync | `scripts/knowledge_catalog_build.py` | 20 min | Qdrant-based catalog |

**Total: ~2.5 hours**

### Phase S2-C: Knowledge Layer Sovereignty (1.5 hours)

| # | Task | File | Effort | Description |
|---|------|------|--------|-------------|
| C1 | Auto-embed on knowledge promotion | `src/omega/oracle/context_builder.py` | 30 min | Embed topics at promotion |
| C2 | Vector-based cross-references | `src/omega/library/crossref.py` | 30 min | Similarity not keyword |
| C3 | Verify knowledge catalog | `scripts/verify_knowledge_sovereign.py` | 15 min | Confirm all INDEX.yaml have vectors |
| C4 | Documentation: Sovereign Data Flow | `docs/architecture/SOVEREIGN_DATA_FLOW.md` | 15 min | New arch doc |

**Total: ~1.5 hours**

**GRAND TOTAL: ~5.5 hours**

---

## §4 — Architecture Diagram (Sovereign Grade Data Flow)

```
┌──────────────────────────────────────────────────────────┐
│                EXTERNAL DATA (Untrusted)                  │
│  • library_inbox_add_url  → taint_level=2                │
│  • library_inbox_add_note → taint_level=1                │
│  • library_inbox_add_file → taint_level=1                │
└────────────────────┬─────────────────────────────────────┘
                     │ @tdp_wrap
                     v
┌──────────────────────────────────────────────────────────┐
│              TAINTED DATA BOUNDARY (TDP)                  │
│  • TaintedData(source, taint_level, content)            │
│  • TDPGate.isolate() wraps in markers                   │
│  • TDPGate.sanitize() strips injection patterns         │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        v                         v
┌──────────────────┐    ┌─────────────────────────┐
│  FTS5 Index      │    │  Qdrant Vector Store    │
│  (BM25 scoring)  │    │  (IVectorStoreAdapter)  │
└────────┬─────────┘    └────────────┬────────────┘
         │                           │
         └────────────┬──────────────┘
                      │ RRF Fusion
                      v
┌──────────────────────────────────────────────────────────┐
│              SOVEREIGN SEARCH RESULT                      │
│  • Hybrid ranked                                          │
│  • Tainted (preserved through fusion)                     │
│  • Isolated by TDPGate before MCP response                │
└────────────────────┬─────────────────────────────────────┘
                     │
                     v
┌──────────────────────────────────────────────────────────┐
│           CLIENT (via MCP)                                │
│  • Receives isolated, taint-marked results                │
│  • Can choose to render or quarantine                     │
└──────────────────────────────────────────────────────────┘
```

---

## §5 — Verification Checklist (S2 Done Criteria)

- [ ] `@tdp_wrap` decorator implemented and tested
- [ ] All library_* MCP tools return TaintedData-wrapped results
- [ ] Qdrant is the vector backend (not just FTS5)
- [ ] Hybrid search (FTS5 + Qdrant RRF) operational
- [ ] `library_index_flush` syncs both FTS5 and Qdrant
- [ ] Knowledge topics auto-embed on promotion
- [ ] Cross-references use vector similarity
- [ ] `make test` — 320/320 still pass + new tdp/vector tests
- [ ] `make temple-grade` — T1-T11 all pass
- [ ] `make heritage-map` — no new violations
- [ ] Live test: `library_search("test")` returns taint-wrapped results
- [ ] Live test: `library_inbox_add_url("https://...")` marks content as `taint_level=2`

---

## §6 — Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Qdrant not running (Phase 2 mention) | Fall back to FTS5-only with warning log |
| Embedding model not loaded (RAM pressure) | Lazy-load on first search, unload after |
| Taint wrapping breaks existing clients | Backward-compat: wrap, but allow untainted path via flag |
| Performance regression on hybrid search | RRF caching, index size limits per query |
| Heritage tags on new files | Auto-apply `[id-soft: omega-2026]` and `[id-soft: security-pattern]` |

---

## §7 — Open Questions for The Architect

1. **Qdrant availability**: Is Qdrant running on this host? If not, S2-B will need a stub fallback.
2. **Taint level policy**: Should `library_inbox_add_url` always be `taint_level=2`, or detect trusted domains?
3. **Cross-reference migration**: When converting keyword cross-refs to vector-based, do we preserve both paths or hard-switch?
4. **S2 priority relative to Sovereign Debt queue**: Quality's T1/T3, Sentinel's auth/CORS/rate-limit are still open. Should S2 happen first or after Sovereign Debt?

---

*⬡ OMEGA ⬡ CLINE-M3 ⬡ deepseek-v4-flash ⬡ trc_s2_scope ⬡ DRAFT-v0.1*
