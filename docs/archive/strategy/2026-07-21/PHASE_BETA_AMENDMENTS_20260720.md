# 🔱 Phase Β Amendments — Grok Advisory Review
**AP Token**: `AP-PHASE-BETA-AMEND-v1.0.0`  
**Campaign**: `FOUNDATION_STABILIZATION_CAMPAIGN_20260720.md`  
**Phase**: Β — HARDEN (Lock the Core)  
**Source**: Grok CLI advisory `data/coordination/grok_cli/PHASE_BETA_ADVISORY_REVIEW_20260720.md`  
**Date**: 2026-07-20  
**Status**: ACK'D — APPROVE WITH AMENDMENTS

---

## Amendments Summary (A1–A13)

| # | Amendment | Impact |
|---|-----------|--------|
| **A1** | **Multi-collection write-path policy: Option A locked** | Write-path default = 768 only (Gemma primary, Nomic fallback); MiniLM/static demoted to non-default explicit collections |
| **A2** | **config_resolver API fix** | Use `CONFIG_DIR / "embedding_strategy.yaml"` — no `.resolve()` method |
| **A3** | **Provider key = `id`** | YAML uses `id: gemma_primary`, not `name` |
| **A4** | **Real contract tests** | Canonical dim=768, zero 1024 refs, live provider chain dims match, adapter rejects wrong-dim |
| **A5** | **vec0 disk migration notes** | Document recreate vs migrate; health check reports actual vs strategy dim |
| **A6** | **Include ics.py third loader** | Dispatch registry must cover ics.py cwd-relative loader |
| **A7** | **Registry API shape** | `load_dispatch_yaml()` returns full dict; `get_dispatch_entities()` returns list; path = `WADS_DIR/iwad/entities/dispatch.yaml` |
| **A8** | **Semantic path CI** | Ban `Path(__file__)` for data/config derivation outside config_resolver; allowlist bootstrap |
| **A9** | **Prioritized migration set** | Must/should/may defer classification for 46 `Path(__file__)` hits |
| **A10** | **D-282 PRAGMA profiles** | Memory: busy_timeout=30000, cache_size=-32768, wal_autocheckpoint=500, journal_size_limit=64MB |
| **A11** | **Profiles not one stack** | Separate profiles: memory / search / metrics |
| **A12** | **Correct sqlite3.connect API** | `uri=True` for readonly, `timeout=30` for rw; gate = connection-setup PRAGMAs only in sqlite_policy.py |
| **A13** | **Β5 after Β4 policy API** | search_persistence uses policy helper + DATA_DIR |

---

## Execution Order (Revised Critical Path)

```
          ┌── FS-Β1 Embedding SSOT (CRITICAL) ──┐
          │                                      ├──► FS-Β4 SQLite policy (profiles)
FS-Β2 Dispatch ──────────────────────────────┤      └──► FS-Β5 search_persistence
FS-Β3 Path CI + must-migrate set ────────────┘
```

| Stream | Parallel? | Depends On |
|--------|-----------|------------|
| FS-Β1 | Yes | — |
| FS-Β2 | Yes (parallel with Β1) | — |
| FS-Β3 | Yes (parallel); absolute path in search can land early as Β5-path-only | — |
| FS-Β4 | After Β1 if touching vec adapter same PR; else parallel with care | Prefer after Β1 freeze of adapter init |
| FS-Β5 | After Β4 policy API exists | Β4 (+ DATA_DIR from resolver, already exists) |

**Est. hours**: 19h still plausible if Β1 multi-dim decision made in first hour.

---

## Forbidden Moves (M23 — Non-Negotiable)

1. ❌ Pad MiniLM/static vectors to 768 to "pass" contract tests
2. ❌ Leave `dimension=1024` fallback "just for hash" without matching collection
3. ❌ Ship empty `pass` contract tests
4. ❌ Reduce busy_timeout to 5s on vec adapter without load re-validation
5. ❌ Touch `tools.py` god-module or provider ABC merge under Phase Β freeze
6. ❌ New strategy manuals superseding this without kill list

---

## Integration Notes

| System | Risk | Guidance |
|--------|------|----------|
| **Omega-Vault (D-299)** | Path-only migration of `keys.json.enc` | Do NOT change crypto API, key format, or encryption. Path → `DATA_DIR / "vault" / ...` only. |
| **MIAP (D-291)** | Custom `_find_project_root()` + Path(__file__) | Replace root discovery with `PROJECT_ROOT` from config_resolver; keep session/coord semantics. |
| **Dual provider ABCs** | Not in Phase Β | Correctly deferred. Do NOT expand Β into provider ABC merge. |
| **RRF** | FS-Α2 marked COMPLETE | Confirm single `HybridSearchEngine` remains; no Β work reopens dual RRF. |

---

## Gate Β Criteria — Amended

| Criterion | Strategy | Amendment |
|-----------|----------|-----------|
| Dim locked 768 | Yes | **Write-path default** 768; non-768 collections explicit non-default; 1024 gone from MemoryStore |
| Single dispatch loader | oracle+subagent only | **+ ics.py consumers** rewired; cwd-relative path dead |
| path-resolver-check | ban all Path(__file__) | **Semantic ban** on data/config derivation; allowlist bootstrap |
| SQLite unified | all PRAGMA only in policy | **Connection-setup** PRAGMAs only; D-282 defaults for memory |
| search_persistence M16 | absolute path gone | + AnyIO wrap; uses policy helper |
| make test failures <10 | aspirational | Accept if Β1 contract + prior 29 dim failures fixed; don't pad vectors to green tests |
| firewall-check <50 | aspirational | Full 156→0 is **not** Gate Β (FS-Α6 / later). Gate Β = no **new** M2 from these workstreams + dispatch extract green |

---

## Next Actions for Kali

1. ✅ ACK this advisory on Hivemind (`intent=decision` mirror)
2. ✅ Create amendments doc (this file)
3. 🔄 Dispatch:
   - Jem/P2/P10 → FS-Β1 (with Option A locked)
   - Kali/P5 → FS-Β2 (include ics.py)
   - P1/P5 → FS-Β3 path CI
   - P2 → FS-Β4 profiles
   - P8/P2 → FS-Β5
4. 🔄 Update `ACTIVE_SPRINT.json` status → `PHASE_Β_EXECUTING` after ACK

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_foundation_stabilization ⬡ PHASE_Β_AMENDMENTS ⬡ 2026-07-20*
