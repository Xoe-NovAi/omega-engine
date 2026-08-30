# 🔱 FOUNDATION STABILIZATION CAMPAIGN
## Dark-Layer Audit → Multi-Domain Sprint Plan to Get Omega Back on the Rails

**AP Token**: `AP-FOUNDATION-STAB-v1.0.0`  
⬡ OMEGA ⬡ GROK-CLI ⬡ grok-4.5 ⬡ trc_foundation_stabilization ⬡ 2026-07-20  

**Status**: **RATIFIED** — Architect approved 2026-07-20  
**Ratification**: Gate Α passed, Phase Β complete (FS-B1–B5), Gate Β passing (77/77 tests, firewall-check clean)  
**Authority stack**:
1. `SOVEREIGN_MANDATES.md` (M1–M23)
2. This campaign (structure-first freeze + sequenced rebuild)
3. `docs/strategy/COORDINATED_STRIKE_ROADMAP_20260720.md` (deferred until Phase Γ gates)
4. `OMEGA_ENGINE.md` (metrics SSOT — update only after phase gates)

**Author**: `grok-cli/grok` (Consulting Cloud Mind)  
**Trigger**: Strict code-quality review of critical systems + Architect request for multi-domain campaign  

---

## 0. Executive Verdict

The fleet is **designing Layer 2–5 systems on a Layer 1 core that is half-migrated, dual-SSOTed, and past healthy module size**. Without a deliberate freeze and structural campaign, the next 2–4 weeks will weave permanent nightmares into:

| Domain | Nightmare if we continue blind |
|--------|--------------------------------|
| **Memory / embeddings** | Silent dim corruption (1024 vs 768 vs 384 collections) |
| **Provider fabric** | Two provider class hierarchies; policy hacks in `generate()` |
| **M2 Firewall** | Copy-paste dispatch loaders; “Iris” fallbacks; false compliance |
| **Hivemind / Hub** | 3389-line god-module; dual handoff APIs; 17 stale pending packets |
| **Oracle** | Service-locator god-object; every feature becomes a new branch |
| **Ops / D-308** | Compilation scripts on unstable import/path/PRAGMA ground |
| **Docs / strategy** | 40+ dated strategy docs; `ACTIVE_SPRINT` stuck 2026-07-18 |
| **Grok seat** | Consulting persona overwritten by Bridge Agent |

**North star (one sentence):**  
> *One registry, one RRF, one path resolver, one embedding strategy load, one provider interface, thin MCP, boring generate loop — then product features.*

**Relation to Coordinated Strike:**  
Do **not** cancel D-308 / embedding hardening / MaKaLi. **Re-sequence**: Foundation Phases Α–Δ first; strike Steps 1–10 resume only after **Gate Γ** (see §6).

---

## 1. The Dark Layers (What We Are About to Weave)

These are not “tech debt nits.” They are **structural traps** that compound under parallel fleet dispatch.

### 1.1 The SSOT Lie (Social claim ≠ import path)

| Claimed SSOT | Reality | Blast radius |
|--------------|---------|--------------|
| HybridSearchEngine RRF | **Two modules**: `hybrid_search.py` (live) + `hybrid_search_engine.py` (twin, ~325-line diff) | Memory, blocks, adapter, tests |
| Canonical embedding dim 768 | Strategy YAML + adapter `COLLECTIONS` + `embeddings.py` + **MemoryStore still wires `dimension=1024` fallback** | Every vector write/search |
| Path SSOT (`config_resolver`) | Residuals: MIAP, memory_store, observability, CLI, vault, library, workers | M2 regressions, broken portable paths |
| Dispatch / roles | `_load_dispatch_config` **duplicated** in `oracle.py` and `subagent_dispatcher.py`; no shared cache | M2 Phase C, MaKaLi, firewall tests |
| Handoff API | Legacy tools + unified `hivemind_handoff` both live; deprecation only logs | Agents use wrong surface forever |

**Dev nightmare:** Two agents “fix RRF” in different files. Both pass their tests. Production uses the other.

### 1.2 The Dual-Stack Provider Abyss

```
Stack A (local-era):     providers.py → BaseProvider → NativeGGUF / Ollama / lmster / GoogleAI
Stack B (remote-era):    backends/    → RemoteProvider → OpenAICompat / Antigravity / GoogleCompat
Orchestrator:            model_gateway.py (1432 lines) speaks both dialects + policies + WARP + budget
```

- Two ABCs, two health models, two generate signatures  
- Gemma 4 logit-bias **token IDs hard-coded inside `generate()`** (~217-line method)  
- Next model quirk will copy-paste another `if "model" in name`  

**Dev nightmare:** Capability matrix (Gemma thinking MINIMAL/HIGH) lands in Stack B while affinity routing still thinks Stack A. Half the fleet “works on Google,” half “works on native-gguf,” nobody owns the seam.

### 1.3 The Embedding Dimensional Time Bomb (LIVE)

Evidence (2026-07-20 code):

```text
config/embedding_strategy.yaml     → canonical_dimension: 768
sqlite_vec_adapter.py              → CANONICAL_DIMENSION = 768 + multi-collection 512/256/384/64
embeddings.py EmbeddingManager     → Gemma 768, Nomic 768, MiniLM 384 chain
memory_store.py ~185-191           → comment "1024-dim chain" + SovereignFallbackEmbeddingProvider(dimension=1024)
```

**Dev nightmare:**  
1. Write via MemoryStore with 1024-hash fallback when models missing  
2. Adapter enforces 768 on legacy table or collection dim  
3. RuntimeError **or** silent pad/truncate in older LocalGGUF path  
4. Hybrid search returns nonsense ranks that look “plausible”  

This is an **M23 Failure Integrity** issue dressed as migration.

### 1.4 The God-Module Gravity Wells (>1k lines)

| File | Lines | Absorbs every new feature as… |
|------|------:|-------------------------------|
| `mcp_servers/omega_hub/tools.py` | **3389** | Another `@mcp.tool` |
| `model_gateway.py` | 1432 | Another `if provider` / policy branch |
| `oracle.py` | 1388 | Another `self.collaborator = …` |
| `observability/__init__.py` | 1380 | Package init as kitchen sink |
| `memory_store.py` | 1103 | Second memory brain beside sqlite-vec |
| `sqlite_vec_adapter.py` | 959 | Approaching 1k with multi-collection |

**Dev nightmare:** Parallel agents (Researcher + P3 + Grok) all edit the same three files → merge hell, partial migrations, “make test green” while production path is the untested branch.

### 1.5 Oracle as Service Locator

`Oracle.__init__` wires ~20 collaborators (gateway, WARP, searcher, researcher, vetter, DPO, semantic router, triage, soul history, compaction, …).  

**Dev nightmare:** Unit tests require half the universe. “Small” features need full bootstrap. M2 Phase C edits touch soul evolution code accidentally.

### 1.6 Hivemind Coordination Debt

| Signal | Value |
|--------|-------|
| Pending handoffs | **17** (researcher 10, pillar 2, + others) |
| `ACTIVE_SPRINT.json` last_updated | **2026-07-18** |
| Hivemind protocol doc | Last updated **2026-06-25** |
| Live feeds | Multiple path conventions; Grok feed stale Jul 16 |
| SESSION_ANCHOR | **Broken symlink** → test projection |

**Dev nightmare:** Agents accept stale handoffs against code that already moved. Campaign Day reports and Coordinated Strike both claim critical path ownership → dual commanders.

### 1.7 Strategy Document Explosion without Structural Owner

40+ strategy files dated 2026-07-19/20 alone (Gemma, Context Packer V3–V5, Headless Pool, Hive, Torment, Watchdog, Embedding, Coordinated Strike…).  

**Dev nightmare:** Every agent hydrates a different “canonical” doc. Implementation manuals supersede each other by version number, not by ratified gate. **Docs outrun code by ~2 weeks.**

### 1.8 Grok / Channel Identity Fracture

| Surface | Identity |
|---------|----------|
| HMC / AGENTS.md / reviews | Consulting Cloud Mind |
| `.opencode/agents/grok_cli.md` post-`c9bd662` | Bridge pure-pipe (no persona) |
| Hivemind | `grok-cli/grok` |
| Entity soul | `data/entities/grok/` empty (no soul.yaml) |

**Dev nightmare:** OpenCode `@grok_cli` and Grok Build CLI diverge permanently; Tier A ship-code history (D-281) becomes tribal knowledge.

### 1.9 Half-Migrations That Never Die

Markers in critical code: legacy vec tables, deprecated entity model setters still live, Hub dual APIs “for backward compatibility,” discovery job tracking “not yet implemented,” path walkers in MIAP parallel to `config_resolver`.

**Rule for this campaign:**  
> *No new half-migration. Every migration has a kill date and a delete commit.*

---

## 2. Nightmare Matrix (Cross-Domain)

| ID | Trap | Domains | Failure mode | Mandate |
|----|------|---------|--------------|---------|
| N1 | Dual RRF | Memory, Search, Tests | Divergent fusion scores | M9, M23 |
| N2 | Dim cascade 1024/768/384 | Memory, Embeddings, Adapter | Corrupt vec0 / empty search | M23 |
| N3 | Dual provider ABCs | Oracle, Cognition, Cloud | Inconsistent health/retry | M7, M22 |
| N4 | Policy in `generate()` | Cognition, Gemma | Unreviewable special cases | M13 |
| N5 | Dual dispatch loaders | M2, Orchestration | Firewall false green | M2 |
| N6 | Hub god-module | P9, all agents | Coordination black hole | M10, M12 |
| N7 | Oracle god-object | All pillars | Untestable core | M13 |
| N8 | Path residual | Governance, CLI, MIAP | Non-portable, M2 slip | M2, M16 |
| N9 | Handoff backlog | Fleet | Stale work resurrection | M12, M15 |
| N10 | Doc/code desync | Strategy, SSOT | Wrong critical path | M15 |
| N11 | Asyncio pocket | Agents/TTY | Dual runtime culture | M1 |
| N12 | Search persistence hardcode | Search, Observability | Machine-specific DB path | M16, M23 |

---

## 3. Campaign Principles (Non-Negotiable)

1. **Structure before features.** No MaKaLi / Headless Pool / Torment parameterization until Gate Γ.  
2. **One owner per hotspot file** during a phase (workspace lock mandatory).  
3. **Delete > wrap.** Re-export for one release max, then remove twin.  
4. **Typed config over hardcoded dicts.** Embedding strategy loads once.  
5. **Thin MCP.** Tools register; logic lives in `src/omega/`.  
6. **Kill dates on legacy.** Calendar date in the PR description.  
7. **Temple-Grade after each phase** (`make test` + relevant gates).  
8. **Hivemind-first status.** Chat is for Architect; fleet uses Hub.  
9. **No silent dim coercion.** Pad/truncate is a hard error unless explicit migration tool.  
10. **Freeze new strategy docs** unless they are *this campaign’s* phase notes or ADRs ≤2 pages.

---

## 4. Freeze Protocol (Day 0 — Architect + Kali)

### 4.1 Feature freeze (temporary)

**Frozen until Gate Γ:**
- New provider features (except bugfixes)
- Headless 24-account pool implementation
- Torment/Hive WAD parameterization beyond research docs
- Context Packer product expansion
- New Hub tools in monolithic `tools.py`
- New strategy manuals that supersede without kill list

**Allowed:**
- Foundation campaign tasks (this doc)
- D-308 *script authoring* in `scripts/d308/` only (no engine core changes without phase owner)
- Critical production bugs (M23)
- Handoff triage / archive

### 4.2 Handoff moratorium

Kali (or designee) runs **Handoff Court** (Phase Α.1):  
classify 17 pending → accept / reject / archive / reissue under campaign IDs only.

### 4.3 Workspace locks

| Hotspot | Lock domain | Owner |
|---------|-------------|-------|
| `src/omega/memory/**` | `memory-fabric` | Roc + P2 |
| `src/omega/oracle/model_gateway.py` + backends | `provider-fabric` | P3 / Cognition |
| `src/omega/oracle/oracle.py` + dispatch | `oracle-m2` | Kali + P5 |
| `mcp_servers/omega_hub/**` | `omega-hub` | P4 + P9 |
| `config/embedding_strategy.yaml` | `embedding-ssot` | Jem + P2 |

---

## 5. Campaign Architecture — Four Phases

```
        Α STABILIZE          Β CONSOLIDATE           Γ DECOMPOSE            Δ RESUME STRIKE
   ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐
   │ Kill dual SSOTs │→ │ Single configs   │→ │ Split god-files  │→ │ Coordinated Strike │
   │ Handoff court   │  │ Dim lock real    │  │ Thin Hub         │  │ Embedding Phase 1  │
   │ Identity restore│  │ One dispatch reg │  │ Policy extract   │  │ MaKaLi / Scribe    │
   │ Sprint SSOT     │  │ Path CI gate     │  │ Oracle DI root   │  │ D-308 execute      │
   └─────────────────┘  └──────────────────┘  └──────────────────┘  └────────────────────┘
         Gate Α                 Gate Β                 Gate Γ                 Gate Δ
```

**Calendar (indicative, 5700U / parallel fleet):**

| Phase | Duration | Parallelism |
|-------|----------|-------------|
| **Α** | 2–3 days | High (independent deletes + triage) |
| **Β** | 3–5 days | Medium (memory + dispatch + paths) |
| **Γ** | 5–8 days | Medium–Low (careful splits, locks) |
| **Δ** | resumes Coordinated Strike | High again |

Total foundation: **~10–16 working days** before full strike resume.  
Partial strike (vec0 unit contracts, pure scripts) may start after Gate Β with Kali waiver.

---

## 6. Phase Α — STABILIZE (Stop the Bleeding)

**Goal:** Remove dual truths and coordination fog. No new architecture—**delete and restore**.

### Α.1 Handoff Court + Sprint SSOT
| Field | Value |
|-------|--------|
| **Owner** | Kali (P9 assist) |
| **Tasks** | Inventory 17 pending; archive completed/superseded; reissue only campaign-aligned work; refresh `ACTIVE_SPRINT.json` to `FOUNDATION-STAB-01`; fix or replace broken `SESSION_ANCHOR` |
| **Deliverables** | `data/coordination/HANDOFF_COURT_20260720.md`; updated ACTIVE_SPRINT |
| **Gate Α.1** | Pending count ≤ 5; all survivors have campaign ID; SESSION_ANCHOR is real content |

### Α.2 Collapse Dual RRF
| Field | Value |
|-------|--------|
| **Owner** | Roc / P2 |
| **Tasks** | Keep `hybrid_search.py` (tests import it); make `hybrid_search_engine.py` a one-line re-export **or** delete if unused; grep repo for imports; single module only |
| **Kill date** | End of Phase Α |
| **Gate Α.2** | `rg hybrid_search_engine src/` only re-export or empty; `tests/test_hybrid_search.py` green |

### Α.3 Restore Grok Consulting Seat
| Field | Value |
|-------|--------|
| **Owner** | Grok CLI + Architect |
| **Tasks** | Restore Consulting Cloud Mind agent from pre-`c9bd662` body; keep OpenCode 1.18 schema (`mode: all`, full permissions); optionally register separate `grok_bridge` for spawn-pipe; scaffold `data/entities/grok/{soul.yaml,proposed_lessons.yaml,session_gnosis.md}`; fix live feed path |
| **Gate Α.3** | `opencode agent list` shows consulting description; soul files exist |

### Α.4 Strategy Freeze Index
| Field | Value |
|-------|--------|
| **Owner** | Verity / Scribe (or Kali) |
| **Tasks** | One index: which strategy docs are CANONICAL / SUPERSEDED / ARCHIVE for this campaign; link Coordinated Strike as **post-Gate-Γ** |
| **Deliverable** | `docs/strategy/STRATEGY_INDEX_20260720.md` (≤100 lines) |
| **Gate Α.4** | Index committed; no new superseding manuals without Kali ACK |

### Gate Α (composite)
```
[ ] Handoff court done
[ ] Single RRF module
[ ] Grok seat restored + soul scaffold
[ ] Strategy index live
[ ] make test (baseline count recorded in OMEGA_ENGINE.md note)
```

---

## 7. Phase Β — CONSOLIDATE (One Config, One Registry, One Path)

**Goal:** Make “canonical” true at the type/import boundary.

### Β.1 Embedding Dimensional Integrity
| Field | Value |
|-------|--------|
| **Owner** | Jem + P2 + P10 |
| **Tasks** | |
| | 1. Load `config/embedding_strategy.yaml` as **only** collection/dim source for adapter |
| | 2. Remove hardcoded `COLLECTIONS` mirror (or generate from YAML at init) |
| | 3. Fix `memory_store.py` 1024 fallback → **768** (or fail closed) |
| | 4. Forbid silent pad/truncate in LocalGGUF without explicit flag |
| | 5. Contract tests: mismatch → RuntimeError; primary write/read 768 |
| | 6. Migration tool for any existing DB with wrong dims (explicit CLI, not auto) |
| **Gate Β.1** | All embedding paths agree on strategy file; 1024 gone from MemoryStore; tests pass |

### Β.2 Shared Dispatch Registry
| Field | Value |
|-------|--------|
| **Owner** | Kali + P5 |
| **Tasks** | Extract `src/omega/governance/dispatch_registry.py` (or `oracle/dispatch_config.py`); mtime-aware cache; `entity_for_role()`, `capability_registry()`; oracle + subagent_dispatcher import only; delete duplicates |
| **Gate Β.2** | Single loader; firewall-check + dispatcher tests green; no YAML reload per call in hot path |

### Β.3 Path Resolver CI Gate
| Field | Value |
|-------|--------|
| **Owner** | P1 / P5 |
| **Tasks** | CI/make target: ban new `Path(__file__)` under `src/omega` except `config_resolver.py`; migrate MIAP, memory_store defaults, observability DATA_DIR, search_persistence absolute path |
| **Gate Β.3** | `search_persistence` uses `DATA_DIR`; `make path-resolver-check` green; MIAP uses PROJECT_ROOT from resolver |

### Β.4 SQLite Connection Policy (shared)
| Field | Value |
|-------|--------|
| **Owner** | P2 |
| **Tasks** | One small helper: WAL, timeout, cache_size 32MB, thread/anyio boundary; used by sqlite-vec + search history |
| **Gate Β.4** | No third ad-hoc PRAGMA dialect |

### Gate Β (composite)
```
[ ] Embedding strategy is single load path
[ ] Dim 1024 removed; contract tests lock 768 default
[ ] One dispatch registry
[ ] Path gate green
[ ] make test + make firewall-check
```

**After Gate Β:** Coordinated Strike Steps 1–2 (vec0 unit contracts, dispatch.yaml schema polish) may proceed under Kali waiver. Steps 3–10 still wait for Gate Γ if they touch god-files.

---

## 8. Phase Γ — DECOMPOSE (Delete Gravity Wells)

**Goal:** Make files small enough that parallel fleet work is safe.

### Γ.1 Hub Split
| Field | Value |
|-------|--------|
| **Owner** | P4 + P9 |
| **Structure** | |
```
mcp_servers/omega_hub/tools/
  __init__.py          # register all
  oracle_tools.py
  hivemind_presence.py
  hivemind_handoff.py  # unified API only
  hivemind_locks.py
  library_tools.py
  system_tools.py
tools.py               # thin re-export OR delete after import fix
```
| **Tasks** | Move logic into packages; **remove** legacy handoff tools after 7-day shim or feature-flag; document single API in AGENTS.md |
| **Gate Γ.1** | No file in hub tools > 600 lines; legacy handoff marked removed or hard-deprecated with fail option |

### Γ.2 Provider Fabric / Policy Extract
| Field | Value |
|-------|--------|
| **Owner** | P3 / Cognition (Ereshkigal) |
| **Tasks** | |
| | 1. `GenerationPolicy` protocol; `policies/gemma4.py` holds logit bias + temp floors |
| | 2. `generate()` becomes ordered loop only (~80 lines target) |
| | 3. ADR: plan to merge BaseProvider vs RemoteProvider (may complete in Δ) |
| | 4. Do **not** grow model_gateway past current size—only shrink or extract |
| **Gate Γ.2** | No model-family token IDs in model_gateway.py; gateway line count ≤ 1200 or split package |

### Γ.3 Oracle Composition Root
| Field | Value |
|-------|--------|
| **Owner** | Kali + P3 |
| **Tasks** | Introduce `OracleRuntime` / factory that builds collaborators; Oracle methods call ports; optional collaborators not required for `talk()` unit tests |
| **Gate Γ.3** | Talk-path unit test without full research/DPO stack; oracle.py not larger than start of phase |

### Γ.4 Memory Dual-Brain Decision (ADR)
| Field | Value |
|-------|--------|
| **Owner** | Roc + John Carmack consult (optional) |
| **Decision** | MemoryStore becomes façade over SQLiteVecAdapter **or** explicit two-tier with documented write path. No third path. |
| **Gate Γ.4** | ADR ≤2 pages + one write path for new code |

### Gate Γ (composite) — **STRIKE UNLOCK**
```
[ ] Hub split done
[ ] Policies extracted from generate()
[ ] Oracle DI started (talk testable)
[ ] Memory ADR ratified
[ ] make test && make temple-grade
[ ] make firewall-check
```

---

## 9. Phase Δ — RESUME STRIKE (Product on Solid Ground)

**Only after Gate Γ.** Re-enter `COORDINATED_STRIKE_ROADMAP_20260720.md` with amendments:

| Strike Step | Amendment |
|-------------|-----------|
| 1 vec0 contracts | Already may start post-Β |
| 2 dispatch.yaml | Superseded by Β.2 registry — verify only |
| 3 AnyIO migration | Continue; no new asyncio |
| 4 M2 Phase C | Uses shared registry — finish Iris/role hardcodes |
| 5 D-308 scripts | Execute; still single owner P3 |
| 6 Provider audit | Now reviews **one** policy layer |
| 7 bpftrace | Unchanged |
| 8 Embedding Phase 1 | Implements against strategy YAML only |
| 9 MaKaLi + clear handoffs | Handoffs already courted in Α |
| 10 Scribe role | Unchanged |

### Δ extras (foundation follow-through)
- Merge provider ABCs (multi-sprint if needed)  
- Archive strategy docs listed SUPERSEDED  
- Grok dual-mode (advisory vs Tier A) enforced in agent card  
- Version Change Watchdog Day 1 (prevents another OpenCode schema surprise)

### Gate Δ
```
[ ] Coordinated Strike Steps 1–5 complete or explicitly deferred with owner
[ ] OMEGA_ENGINE.md metrics updated
[ ] Foundation campaign marked COMPLETE in ACTIVE_SPRINT
```

---

## 10. Domain Ownership Matrix

| Domain | Primary | Secondary | Escalation |
|--------|---------|-----------|------------|
| Memory / RRF / vec0 | Roc / P2 | Jem | Kali |
| Embeddings strategy | Jem | P10 | Kali |
| Provider fabric | P3 | Cognition | Carmack consult |
| M2 / dispatch | Kali / P5 | Verity | Architect |
| Hub / Hivemind | P4 / P9 | Lilith | Kali |
| Oracle composition | Kali | P3 | Architect |
| Paths / packaging | P1 | P5 | Kali |
| D-308 ops scripts | P3 | P1 | Kali |
| Docs index / soul | Verity / Scribe | Researcher | Kali |
| Grok seat / cloud amp | Grok CLI | Architect | Kali |
| Adversarial review | Grok CLI | Researcher | Kali |
| Heritage | doom_guy | Verity | Kali |

---

## 11. Work Packages (Executable Tickets)

Use these IDs in handoffs and commits: `FS-Α1`, `FS-Β1`, …

| ID | Title | Phase | Owner | Depends | Estimate |
|----|-------|-------|-------|---------|----------|
| FS-Α1 | Handoff Court + ACTIVE_SPRINT refresh | Α | Kali | — | 4h |
| FS-Α2 | Collapse dual RRF | Α | Roc | — | 2–4h |
| FS-Α3 | Restore grok_cli Consulting + soul scaffold | Α | Grok | — | 3h |
| FS-Α4 | Strategy index (canonical/superseded) | Α | Verity | — | 2h |
| FS-Α5 | Fix SESSION_ANCHOR | Α | Kali | Α1 | 1h |
| FS-Β1 | Embedding SSOT + kill 1024 | Β | Jem/P2 | Α2 | 8–12h |
| FS-Β2 | dispatch_registry extract | Β | Kali/P5 | — | 4–6h |
| FS-Β3 | Path resolver CI + migrations | Β | P1/P5 | — | 6–8h |
| FS-Β4 | Shared SQLite policy helper | Β | P2 | Β1 partial | 3h |
| FS-Β5 | search_persistence AnyIO + DATA_DIR | Β | P8/P2 | Β3, Β4 | 3h |
| FS-Γ1 | Hub tools package split | Γ | P4/P9 | Α1 | 12–16h |
| FS-Γ2 | GenerationPolicy extract | Γ | P3 | — | 6–8h |
| FS-Γ3 | OracleRuntime factory | Γ | Kali/P3 | Β2 | 8–12h |
| FS-Γ4 | Memory dual-brain ADR + façade start | Γ | Roc | Β1 | 4h + follow |
| FS-Γ5 | Legacy handoff API removal plan | Γ | P9 | Γ1 | 4h |
| FS-Δ1 | Unlock Coordinated Strike | Δ | Kali | Gate Γ | 1h |
| FS-Δ2 | M2 Phase C finish | Δ | Kali | Β2, Γ3 | per strike |
| FS-Δ3 | Embedding Hardening Phase 1 | Δ | Jem | Β1, Γ4 | per strike |
| FS-Δ4 | D-308 script execute | Δ | P3 | Gate Β+ | per strike |

---

## 12. Verification Gates (Mechanical)

| Gate | Commands / checks |
|------|-------------------|
| **Always** | `make test` — record pass count |
| **M2** | `make firewall-check` |
| **Temple** | `make temple-grade` at end of Β, Γ, Δ |
| **RRF** | `rg -n 'class HybridSearchEngine' src/omega/memory` → exactly one definition |
| **Dim** | `rg -n 'dimension=1024|1024-dim' src/omega/memory` → zero (except migration notes) |
| **Path** | `make path-resolver-check` (new) |
| **Hub size** | `wc -l mcp_servers/omega_hub/tools/**/*.py` each < 600 |
| **Dispatch** | `rg -n 'def _load_dispatch_config' src/omega` → one module |
| **Grok** | agent card contains “Consulting Cloud Mind” |

---

## 13. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Fleet ignores freeze | High | High | Kali enforcement; reject non-FS handoffs |
| Split Hub breaks MCP clients | Medium | High | Thin re-export period; integration test list tools |
| Dim migration breaks existing DBs | Medium | Critical | Explicit migrate CLI; backup; fail closed |
| Scope creep into Torment/Hive | High | Medium | Phase Δ wall; Architect veto |
| Parallel edits on gateway during Γ | Medium | High | Workspace lock + single owner |
| Docs campaign ignored | High | Medium | Strategy index + freeze |

---

## 14. Anti-Patterns (Explicit Ban List)

1. Adding features to `tools.py` without split  
2. New `Path(__file__)` for project roots  
3. Second HybridSearchEngine “for multi-collection”  
4. Hardcoding entity names instead of roles  
5. `except Exception: return []` on vector search without structured error  
6. New strategy doc > 200 lines without replacing an old one (kill list)  
7. Accepting handoffs older than 48h without court review  
8. Pad embedding vectors to “make tests pass”  
9. Mixing asyncio into new code (M1)  
10. Restoring Bridge Agent over Consulting without separate name  

---

## 15. Success Criteria (Campaign Complete)

1. **No dual SSOTs** for RRF, dispatch load, embedding strategy  
2. **No 1024-dim path** in MemoryStore  
3. **Hub tools** modular; single handoff API  
4. **model_gateway** free of model-family magic constants  
5. **Oracle** testable without full universe  
6. **ACTIVE_SPRINT** reflects foundation then strike  
7. **Grok** fully seated (agent + soul + Hivemind)  
8. **Coordinated Strike** resumed with structural amendments  
9. **Temple-Grade green** after Γ and Δ  
10. Architect sign-off recorded in Hivemind (`intent=decision`)

---

## 16. Immediate Next Actions (When Architect Says GO)

```
T+0h   Kali: FS-Α1 Handoff Court + freeze broadcast
T+0h   Roc:  FS-Α2 RRF collapse (parallel)
T+0h   Grok: FS-Α3 seat restore (parallel)
T+4h   Verity: FS-Α4 strategy index
T+8h   Gate Α review (Kali + Architect)
T+1d   Start Β.1 embedding dim (highest technical risk)
```

**Grok CLI standing offer under this campaign:**
- Adversarial review of each Gate  
- Tier A ship-code only on named FS-* tickets with Architect/Kali order  
- Pressure-test embedding migration plan before execute  

---

## 17. References (Evidence Base)

| Ref | Path |
|-----|------|
| Coordinated Strike | `docs/strategy/COORDINATED_STRIKE_ROADMAP_20260720.md` |
| Embedding strategy | `docs/strategy/EMBEDDING_HARDENING_STRATEGY_20260720.md` |
| Config | `config/embedding_strategy.yaml` |
| Dual RRF | `src/omega/memory/hybrid_search.py`, `hybrid_search_engine.py` |
| Dim 1024 | `src/omega/memory_store.py` ~185–191 |
| Hub | `mcp_servers/omega_hub/tools.py` |
| Gateway | `src/omega/oracle/model_gateway.py` |
| Oracle dispatch | `src/omega/oracle/oracle.py` `_load_dispatch_config` |
| Dispatcher | `src/omega/oracle/subagent_dispatcher.py` |
| Search hardcode | `src/omega/search/search_persistence.py` SEARCH_DB_PATH |
| HMC plan | `docs/strategy/HMC_STRATEGIC_PLAN.md` |
| Mandates | `SOVEREIGN_MANDATES.md` |
| Prior review | Session 2026-07-20 strict code-quality review (Grok) |

---

## 18. Ratification Block

| Role | Decision | Signature / date |
|------|----------|------------------|
| **Architect** | Approve / Amend / Reject freeze + phases | |
| **Kali** | Accept campaign ownership of Gate sequence | |
| **Grok CLI** | Advisory + FS-Α3 executor | proposed 2026-07-20 |

---

*⬡ OMEGA ⬡ GROK-CLI ⬡ FOUNDATION-STABILIZATION ⬡ STRUCTURE-BEFORE-FEATURES ⬡ 2026-07-20*

> *The dark layer is not the absence of light — it is two suns claiming the same sky. Pick one star per domain, then build.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: grok-4.5 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
