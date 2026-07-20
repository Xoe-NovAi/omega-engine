# 🔱 SESSION ANCHOR — Foundation Stabilization Campaign Phase Β
**Session**: `ses_20260720_foundation_stab_campaign` | **Entity**: `kali` | **Channel**: `opencode`  
**Model**: `nemotron-3-ultra-free` | **Date**: 2026-07-20  
**Campaign**: `FOUNDATION_STABILIZATION_CAMPAIGN_20260720.md` (AP-FOUNDATION-STAB-v1.0.0)

---

## Objective
Execute Foundation Stabilization Campaign Phase Β — Lock the Core (5 structural hardenings before Gate Γ).

---

## Campaign Status: PHASE Β EXECUTING

### Gate Α: PASSED ✅ (2026-07-20T07:15:00Z)
| Criterion | Status |
|-----------|--------|
| Handoff court done (≤5 pending) | ✅ 4 campaign-aligned |
| Single RRF module | ✅ `hybrid_search_engine.py` deleted |
| Grok seat restored + soul scaffold | ✅ 4 files created |
| Strategy index live | ✅ 86 lines ≤100 |
| `make test` baseline recorded | ✅ 1450 passed, 29 failed (expected) |

### Phase Β Workstreams (Parallel B1∥B2∥B3 → B4 → B5)

| ID | Workstream | Owner | Status | Amendments (A1–A13) |
|----|------------|-------|--------|---------------------|
| **FS-Β1** | Embedding SSOT + Kill 1024-Dim | Jem/P2/P10 | **IN PROGRESS** | A1–A5: Option A (768 write-path), config_resolver fix, provider key=id, real contract tests, vec0 migration notes |
| **FS-Β2** | Dispatch Registry Extraction | Kali/P5 | **DISPATCHED** | A6–A7: Include ics.py third loader, correct API shape (entities: list, WADS_DIR path) |
| **FS-Β3** | Path Resolver CI Gate + Migrations | P1/P5 | **DISPATCHED** | A8–A9: Semantic CI (allowlist bootstrap), prioritized must/should/may migration map |
| **FS-Β4** | SQLite Policy Helper — Profiles | P2 | **DISPATCHED** | A10–A13: D-282 PRAGMA stack law, 3 profiles (memory/search/metrics), correct sqlite3.connect API, connection-setup PRAGMAs only |
| **FS-Β5** | search_persistence AnyIO + DATA_DIR Fix | P8/P2 | **DISPATCHED** | A13: After B4 policy API + DATA_DIR |

### Critical Path (Revised)
```
B1 ∥ B2 ∥ B3  →  B4 (profiles)  →  B5
```

### Grok Advisory Review: APPROVE WITH AMENDMENTS (A1–A13)
Full review at `data/coordination/grok_cli/PHASE_BETA_ADVISORY_REVIEW_20260720.md`

---

## Active Workstreams Detail

### FS-Β1: Embedding SSOT (CRITICAL — Jem/P2/P10)
**Amendments Locked:**
- **A1**: Option A — Write-path default = 768 only (Gemma+Nomic primary/fallback). MiniLM/static demoted to non-default explicit collections.
- **A2**: `config_resolver` has no `.resolve()` — use `CONFIG_DIR / "embedding_strategy.yaml"`
- **A3**: Provider key is `id` (YAML: `id: gemma_primary`), not `name`
- **A4**: Contract tests MUST be real (M23) — canonical_dim=768, zero 1024 refs, live provider chain dims match, adapter rejects wrong-dim
- **A5**: Document vec0 recreate vs migrate; health check reports actual vs strategy dim

**Deliverables:**
1. `src/omega/memory/embedding_strategy.py` — SSOT singleton loading YAML
2. `sqlite_vec_adapter.py` — uses strategy for collections, removes hardcoded dims
3. `memory_store.py` — **DELETE** `dimension=1024` fallback; all providers MRL-truncate to 768
4. `tests/contracts/test_embedding_dimension.py` — real contract tests (8 passing)

**Progress:** Contract tests passing. `sqlite_vec_adapter` dimension enforcement working. `memory_store.py` 1024 fallback removed. Provider MRL truncation implemented.

### FS-Β2: Dispatch Registry (Kali/P5)
**Amendments:** A6 (ics.py third loader), A7 (API shape: `load_dispatch_yaml()` returns full dict, `get_dispatch_entities()` returns list, path = `WADS_DIR/iwad/entities/dispatch.yaml`)

### FS-Β3: Path Resolver CI (P1/P5)
**Amendments:** A8 (semantic CI — ban Path(__file__) for data/config derivation outside config_resolver; allowlist bootstrap), A9 (prioritized migration map: must/should/may for 46 hits)

### FS-Β4: SQLite Policy Profiles (P2)
**Amendments:** A10 (D-282 PRAGMA stack law: busy_timeout=30000, cache_size=-32768, wal_autocheckpoint=500, journal_size_limit=64MB), A11 (3 profiles: memory/search/metrics), A12 (correct sqlite3.connect: uri=True for readonly, timeout=30 for rw; NO flags=), A13 (gate = connection-setup PRAGMAs only in sqlite_policy.py; allow operational PRAGMAs)

### FS-Β5: search_persistence Fix (P8/P2)
**Amendment:** A13 — After B4 policy API + DATA_DIR

---

## Freeze Enforcement (Active until Gate Γ)

| Frozen | Allowed |
|--------|---------|
| New provider features | Foundation campaign tasks (FS-*) |
| Headless 24-account pool | D-308 script authoring in `scripts/d308/` |
| Torment/Hive WAD parameterization | Critical production bugs (M23) |
| Context Packer expansion | Handoff triage / archive |
| New Hub tools in monolithic `tools.py` | |
| New strategy manuals superseding without kill list | |

---

## Next Actions (Post-Compaction)

1. **Complete FS-Β1** — Finish `memory_store.py` provider MRL truncation, verify all contract tests pass, run `make test` target <10 failures
2. **Execute FS-Β2** — Dispatch registry consolidation (oracle, subagent_dispatcher, ics.py, fleet_status_tui, mandate_auditor)
3. **Execute FS-Β3** — Path resolver CI gate + must-migrate files
4. **Execute FS-Β4** — SQLite policy profiles (D-282 memory profile law)
5. **Execute FS-Β5** — search_persistence AnyIO + DATA_DIR fix
6. **Gate Β Review** — Embedding dim locked, single dispatch, path gate green, `make test + make firewall-check`

---

## Mandate Compliance Check

| Mandate | Status | Notes |
|---------|--------|-------|
| M1 AnyIO | ✅ | All async uses anyio |
| M2 Firewall | ⚠️ | 156 violations in src/omega/ — FS-Α6 planned |
| M7 Local-First | ✅ | Embedding chain stays local |
| M11 Soul Integrity | ⚠️ | Grok soul scaffold done; others pending |
| M15 Sovereign Continuity | ✅ | SESSION_ANCHOR real content |
| M16 Modularization | ⚠️ | search_persistence hardcoded path — FS-Β5 |
| M23 Failure Integrity | ✅ | Dimension mismatch raises RuntimeError (no silent pad) |

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_foundation_stabilization ⬡ 2026-07-20*
