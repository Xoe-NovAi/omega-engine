<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Grok Advisory — Phase Β Execution Strategy Review
**AP**: `AP-PHASE-BETA-ADVISORY-v1.0.0`  
**Handoff**: `ho_80b0399b2717`  
**Strategy**: `docs/strategy/PHASE_BETA_EXECUTION_STRATEGY_20260720.md`  
**Reviewer**: `grok-cli/grok` (Consulting Cloud Mind) · grok-4.5  
**Date**: 2026-07-20  
**Verdict**: **APPROVE WITH AMENDMENTS**

---

## 0. Executive Verdict

Phase Β correctly targets the five highest-leverage structural traps after Gate Α. Direction is sound: embedding SSOT, one dispatch registry, path CI, SQLite policy, search_persistence M16/M1.

**Do not execute the pseudocode as written.** Several snippets will fail at import or regress D-282. Apply the amendments below, then execute.

| Workstream | Soundness | Execute? |
|------------|-----------|----------|
| FS-Β1 Embedding SSOT | Core intent right; multi-dim YAML contradiction + API bugs | **Yes, after A1–A5** |
| FS-Β2 Dispatch Registry | Right extract; **scope incomplete** (ics.py third loader) | **Yes, after A6–A7** |
| FS-Β3 Path Resolver CI | Right gate idea; CI recipe too blunt | **Yes, after A8–A9** |
| FS-Β4 SQLite Policy | Right helper; **PRAGMA stack regresses D-282** | **Yes, after A10–A12** |
| FS-Β5 search_persistence | Clear win (absolute path + AnyIO) | **Yes, after B4 + A13** |

---

## 1. Architectural Soundness (Mandates)

| Mandate | Assessment |
|---------|------------|
| **M1 AnyIO** | FS-Β5 correctly requires `anyio.to_thread.run_sync`. Do not introduce `asyncio`. Threading locks in Β1/Β2 loaders are acceptable for sync module load. |
| **M2 Firewall** | Β2 reduces copy-paste dispatch; good. Β3 reduces path sprawl. Do not hardcode WAD entity names in new modules. |
| **M7 Local-first** | Embedding chain stays local; no cloud embedding forced. Good. |
| **M16 Modularization** | Absolute path in `search_persistence.py:30` is a real M16 crime — Β5 is mandatory. |
| **M23 Failure Integrity** | Β1 must **fail closed** on dim mismatch (YAML already says `error_on_mismatch: true`). No silent pad-to-768. |
| **Temple-Grade** | Wire `path-resolver-check` into `temple-grade` only after allowlist is correct (else permanent red gate). |

No mandate *violation* in intent. Several proposed implementations would *create* M23/M16 failures if shipped as-is.

---

## 2. Research Grounding Validation

| Claim | Verdict | Notes |
|-------|---------|-------|
| sqlite-vec multi-collection / dim at table create | **Valid** | Matches adapter design + live COLLECTIONS |
| ZeroEntropy “don’t mix index/query dims” | **Valid & critical** | Strengthens fail-closed contract |
| MRL prefix slice for Nomic/Gemma-class models | **Valid when native ≥ target** | Invalid as universal rule (MiniLM 384, static 64) |
| Toolbox365 PRAGMA list (WAL/NORMAL/64MB/5s) | **Partially valid** | Generic blog defaults ≠ Omega D-282 hardware-tuned stack |
| OpenCode V2 config migration (prompt→system) | **Peripheral** | Not blocking for dispatch extract; don’t couple |
| mtime cache for YAML | **Valid** | Standard hot-reload pattern |

**2026 SQLite / MRL:** Keep MRL only for models that advertise it. Prefer **D-282 PRAGMA stack as sovereign default** over generic 5s/64MB blogs for the memory fabric DB.

---

## 3. Missing Risks & Implementation Gaps

### 3.1 FS-Β1 — CRITICAL amendments

**A1 — Multi-collection policy (YAML contradiction)**  
Live `config/embedding_strategy.yaml` has:

- `canonical_dimension: 768`
- collections at **768 / 512 / 256 / 384 / 64**

Strategy text says “all providers MUST output 768.” That cannot apply to MiniLM (384) or static (64) without **padding** (geometry-breaking) or **killing** those providers.

**Required decision before code (pick one):**

| Option | Policy | Recommendation |
|--------|--------|----------------|
| **A (recommended for Gate Β)** | **Write-path default = 768 only.** Gemma + Nomic primary/fallback. MiniLM/static demoted to non-default / experimental collections; MemoryStore must not chain them into the default 768 path. | **Choose A** for Gate Β clarity |
| **B** | Collection-scoped dims forever; provider always writes to its mapped collection; no global “must be 768” assertion on every provider. | Defer full B to Phase Γ if chosen |

**A2 — Fix API surface in pseudocode**  
`config_resolver` has **no** `.resolve()` method. Actual API:

```python
from omega.governance.config_resolver import CONFIG_DIR, DATA_DIR, PROJECT_ROOT, WADS_DIR
path = CONFIG_DIR / "embedding_strategy.yaml"
```

**A3 — Provider key is `id`, not `name`**  
YAML providers use `id: gemma_primary` etc. `get_provider_config(name)` must match on `id` (and optionally `class`).

**A4 — Contract tests must not be stubs**  
Parametrized test that `pass`es is theater (M23). Gate Β.1 requires:

1. `canonical_dimension == 768`
2. `rg -n 'dimension=1024' src/omega/memory` → zero (except comments migration notes if any)
3. Live provider/manager path: default MemoryStore chain dimensions all equal strategy write-path dim
4. Adapter rejects wrong-dim upsert with explicit error (already partially present — keep)

**A5 — Existing vec0 tables**  
If any DB already created at wrong dim, code-only SSOT does not heal disk. Add:

- Document recreate vs migrate  
- Health check reports actual table dim vs strategy  
- No silent ALTER (vec0 typically recreate)

Also align MemoryStore default chain comments (`1024-dim` / mxbai) with reality — they are **stale lies** next to live code.

### 3.2 FS-Β2 — Scope incomplete

**A6 — Third loader: `src/omega/ics.py`**  
Ground truth:

| Module | Return shape | Path resolution |
|--------|--------------|-----------------|
| `oracle.py` | `list[dict]` entities | `WADS_DIR / iwad / entities / dispatch.yaml` |
| `subagent_dispatcher.py` | same as oracle | same |
| `ics.py` | **full YAML `dict`** | `Path.cwd()/config/wads/...` (cwd-relative!) |
| Consumers | `fleet_status_tui`, `mandate_auditor` import **ics** | |

Registry that only rewires oracle + subagent_dispatcher leaves a **third SSOT** and cwd-relative path bug.

**A7 — Registry API shape**  
Pseudocode `get_dispatch_config()` treating top-level YAML as list is wrong. Real files have `entities:` list. Prefer:

```python
def load_dispatch_yaml(iwad: str | None = None) -> dict[str, Any]: ...
def get_dispatch_entities(iwad: str | None = None) -> list[dict[str, Any]]: ...
def get_entity_by_role(role: str, iwad: str | None = None) -> dict | None: ...
def invalidate_cache() -> None: ...
```

Path: `WADS_DIR / iwad / "entities" / "dispatch.yaml"` — **not** `resolve("dispatch.yaml")`.

Cache identity: `cfg1 is cfg2` is fine; document that callers must not mutate returned structures (or return copies).

### 3.3 FS-Β3 — CI gate too blunt

**A8 — Allowlist, not ban-all-`Path(__file__)`**  
Live count: **~46** `Path(__file__)` under `src/omega/`. Required bootstrap lives in `config_resolver.py`. Legitimate uses: firewall self-path, some `sys.path` hacks (migrate carefully).

**Gate recipe (replace Makefile one-liner):**

```text
FAIL if Path(__file__) is used to derive DATA_DIR / CONFIG_DIR / WADS / vault / search DB
  outside config_resolver.py
ALLOW bootstrap Path(__file__) only in config_resolver.py
ALLOW Path(__file__) for module-relative non-data resources only with explicit allowlist
```

Do **not** `grep -v test_ && exit 1` on every hit — permanent false red.

**A9 — Migration map incomplete**  
Strategy lists ~15 files; grep finds more (model_gateway, sovereign_search_service, request_queue, benchmarks, iris, skills, …). For Gate Β:

- **Must migrate**: search_persistence absolute path, memory_store DATA_DIR, miap PROJECT_ROOT, vault keys path, session/entity workspace DATA_DIR  
- **Should migrate**: model_gateway config paths, library/*, observability  
- **May defer**: pure sys.path bootstrap in CLI entrypoints (track as Β3.1 debt)

### 3.4 FS-Β4 — Do not regress D-282

**A10 — Sovereign default = memory fabric stack, not blog defaults**

Live `sqlite_vec_adapter` (D-282, hardware-validated on 14Gi + inference + zRAM):

| PRAGMA | D-282 value | Strategy draft | Action |
|--------|-------------|----------------|--------|
| busy_timeout | **30000** | 5000 | **Keep 30000** for memory/vec |
| cache_size | **-32768 (32MB)** | -65536 (64MB) | **Keep 32MB** default (OOM risk documented) |
| mmap_size | 256MB | 256MB | OK |
| wal_autocheckpoint | 500 | missing | **Include** |
| journal_size_limit | 64MB | missing | **Include** |
| optimize | 0x10002 | missing | Optional profile |

**A11 — Profiles, not one stack for all DBs**

```text
profile=memory  → D-282 stack (vec, fts memory)
profile=search  → WAL + NORMAL + busy 5–30s + moderate cache
profile=metrics → existing metrics_db stack
```

Blind replace of `sqlite_vec_adapter._get_conn()` with 5s timeout is a **concurrency regression** under Hivemind + researcher load.

**A12 — Python `sqlite3.connect` API bug in pseudocode**  
`sqlite3.connect(..., flags=SQLITE_OPEN_*)` is not the portable stdlib pattern used elsewhere. Use:

```python
sqlite3.connect(f"file:{path}?mode=ro", uri=True)  # readonly
sqlite3.connect(str(path), timeout=30.0)           # readwrite
```

**Gate criterion fix:**  
`rg PRAGMA src/omega → only sqlite_policy.py` is **false**. Keep operational PRAGMAs (`table_info`, `wal_checkpoint`, health). Gate = **connection-setup PRAGMAs** only live in `sqlite_policy.py`.

### 3.5 FS-Β5

**A13 — Depends on B4 profiles + DATA_DIR**  
- Path: `DATA_DIR / "search" / "search_history.db"` ✅  
- Thread-local connection reuse can stay; policy applies on open  
- All sync DB I/O behind `anyio.to_thread.run_sync`  
- No `asyncio`

---

## 4. Execution Order (Revised Critical Path)

Strategy serializes Β1→Β2→Β3→Β4→Β5. That over-constrains.

```
         ┌── FS-Β1 Embedding SSOT (CRITICAL) ──┐
         │                                      ├──► FS-Β4 SQLite policy (profiles)
FS-Β2 Dispatch ──────────────────────────────┤      └──► FS-Β5 search_persistence
FS-Β3 Path CI + must-migrate set ────────────┘
```

| Stream | Parallel? | Depends on |
|--------|-----------|------------|
| FS-Β1 | Yes | — |
| FS-Β2 | Yes (parallel with Β1) | — |
| FS-Β3 | Yes (parallel); absolute path in search can land early as Β5-path-only | — |
| FS-Β4 | After Β1 if touching vec adapter same PR; else parallel with care | Prefer after Β1 freeze of adapter init |
| FS-Β5 | After Β4 policy API exists | Β4 (+ DATA_DIR from resolver, already exists) |

**Est. hours:** 19h still plausible if Β1 multi-dim decision is made in first hour (not rediscovered mid-PR).

---

## 5. Integration: Omega-Vault (D-299) / MIAP (D-291)

| System | Risk | Guidance |
|--------|------|----------|
| **Vault** | Path-only migration of `keys.json.enc` | Do **not** change crypto API, key format, or encryption. Path → `DATA_DIR / "vault" / ...` only. |
| **MIAP** | Custom `_find_project_root()` + Path(__file__) | Replace root discovery with `PROJECT_ROOT` from config_resolver; keep session/coord semantics. |
| **Dual provider ABCs** | Not in Phase Β | Correctly deferred. Do **not** expand Β into provider ABC merge. |
| **RRF** | FS-Α2 marked COMPLETE | Confirm single `HybridSearchEngine` remains; no Β work reopens dual RRF. |

---

## 6. Gate Β Criteria — Amended

| Criterion | Strategy | Amendment |
|-----------|----------|-----------|
| Dim locked 768 | Yes | **Write-path default** 768; non-768 collections explicit non-default; 1024 gone from MemoryStore |
| Single dispatch loader | oracle+subagent only | **+ ics.py consumers** rewired; cwd-relative path dead |
| path-resolver-check | ban all Path(__file__) | **Semantic ban** on data/config derivation; allowlist bootstrap |
| SQLite unified | all PRAGMA only in policy | **Connection-setup** PRAGMAs only; D-282 defaults for memory |
| search_persistence M16 | absolute path gone | + AnyIO wrap; uses policy helper |
| make test failures <10 | aspirational | Accept if Β1 contract + prior 29 dim failures fixed; don’t pad vectors to green tests |
| firewall-check <50 | aspirational | Full 156→0 is **not** Gate Β (FS-Α6 / later). Gate Β = no **new** M2 from these workstreams + dispatch extract green |

---

## 7. Forbidden Moves (M23)

1. Pad MiniLM/static vectors to 768 to “pass” contract tests  
2. Leave `dimension=1024` fallback “just for hash” without matching collection  
3. Ship empty `pass` contract tests  
4. Reduce busy_timeout to 5s on vec adapter without load re-validation  
5. Touch `tools.py` god-module or provider ABC merge under Phase Β freeze  
6. New strategy manuals superseding this without kill list  

---

## 8. Verdict

### **APPROVE WITH AMENDMENTS**

Kali may open execution handoffs for FS-Β1…Β5 **after** incorporating:

1. **A1** multi-collection write-path policy (recommend Option A)  
2. **A2–A3** config_resolver + provider `id` API fixes  
3. **A4–A5** real contracts + vec0 disk migration notes  
4. **A6–A7** ics.py + correct registry API / WAD path  
5. **A8–A9** semantic path CI + prioritized migration set  
6. **A10–A12** D-282 PRAGMA profiles + correct sqlite3 connect  
7. **A13** Β5 after policy API  
8. Parallelize Β1 ∥ Β2 ∥ Β3  

**Reject only if** fleet insists on universal 768 truncation for all providers **and** silent padding — that is an M23 dim-corruption path.

---

## 9. Suggested next actions for Kali

1. ACK this advisory on Hivemind (`intent=decision` mirror)  
2. Patch `PHASE_BETA_EXECUTION_STRATEGY_20260720.md` with A1–A13 (or short `PHASE_BETA_AMENDMENTS_20260720.md`)  
3. Dispatch:
   - Jem/P2/P10 → FS-Β1 (with Option A locked)  
   - Kali/P5 → FS-Β2 (include ics)  
   - P1/P5 → FS-Β3 path CI  
   - P2 → FS-Β4 profiles  
   - P8/P2 → FS-Β5  
4. Update `ACTIVE_SPRINT.json` status → `PHASE_Β_EXECUTING` after ACK  

---

*⬡ OMEGA ⬡ GROK ⬡ grok-4.5 ⬡ grok-cli ⬡ trc_foundation_stabilization ⬡ PHASE_Β_ADVISORY ⬡ 2026-07-20*
