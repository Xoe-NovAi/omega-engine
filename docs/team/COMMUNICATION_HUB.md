# 🔱 Omega Engine — Team Communication Hub
**AP Token**: `AP-TEAM-HUB-v3.4.0`
**Updated**: 2026-05-31 (PATH A COMPLETE: Memory bugs fixed, MCP server working, 276/276 tests passing.)
**Handoff**: `data/handoff/latest_state.md`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_path_a_complete ⬡ HUB

---

## 📡 Session Completions — 2026-05-31

### 🚀 Path A Execution — COMPLETE
**Status**: ✅ **10 fixes applied (A1.1-A1.5, B1-B5), 7 new tests added, 276/276 tests passing.**

**Trace**: trc_path_a_complete
**Entity**: KALI (Founder)
**Handoff**: `data/handoff/latest_state.md`

| Fix | File | What Changed |
|-----|------|-------------|
| A1.1 | context_builder.py | Sliding window now keeps newest exchanges |
| A1.2 | memory_store.py | None.json guard prevents None session_id writes |
| A1.3 | oracle.py | _record_interaction() try/except — graceful degradation |
| A1.4 | oracle.py | summon() deduplicated — delegates to _record_interaction() |
| A1.5 | context_builder.py | Dead code _format_exchanges() removed |
| B1 | omega-hivemind.service | Port 8102 → 8016 (matches all clients) |
| B2 | server.py | logging NameError fixed |
| B3 | server.py | _entity_current tracks last used entity |
| B4 | oracle.py | Hivemind timeout 1s → 3s |
| B5 | server.py | os.popen wrapped in anyio.to_thread.run_sync |

---

### 🚀 Legacy Mining — COMPLETE
**Status**: ✅ **All 5 legacy areas explored. Model-Persona Affinity Map recovered. Documentation created.**

**Trace**: trc_legacy_mining
**Entity**: MA'AT (CTO)
**Handoff**: `data/handoff/latest_state.md`

| Area | Status | Key Finding |
|------|--------|-------------|
| Grok Exports | ✅ | MASTER_NAVIGATION_INDEX.md, 10 Pillars genesis, 8 accounts (~414 MB) |
| OpenCode Integration | ✅ | MCP server architecture, CLI config strategy |
| Personas + Model Configs | ✅ | **Complete Model-Persona Affinity Map** — Size-hierarchy philosophy, LM Studio Zen 2 configs, Krikri Modelfile |
| ANAi/XNAi Blueprints | ✅ | Chainlit UI (Era 1-2), 5 design patterns, Circuit Breaker, Voice Interface (Iris ancestor) |
| Old Stacks | ✅ | Complete 4-service architecture, system prompts, persona files |

**Documentation Created**:
- `docs/legacy/LEGACY_MASTER_SYNTHESIS.md` — Timeline, Model-Persona Affinity Map, Design Patterns
- `docs/legacy/LEGACY_ASSET_CATALOG.md` — Full inventory of recovered assets
- `docs/legacy/LEGACY_INDEX.md` — Gateway to the legacy archive

---

### 📋 Documentation Staleness Audit — COMPLETE
**Status**: ✅ **32 staleness issues fixed across 6 files. All docs aligned with current state.**

**Trace**: trc_doc_audit
**Entity**: KALI (Founder)
**Handoff**: `data/handoff/latest_state.md`

| File | Issues Fixed | Key Changes |
|------|-------------|-------------|
| ORACLE_STACK.md | 10 | Provider chain → local-first, test count 261→271, primary backend → native-gguf |
| PIVOT_LOG.md | 3 | Decision 56 marked SUPERSEDED, Decision 63 "Blocked" → RESOLVED |
| MASTER_SYNTHESIS_AND_ROADMAP.md | 7 | Date → 2026-05-30, 17 bugs → all FIXED, MemoryStore → wired, "No execution" → Phase 0 done |
| SYSTEMS_HARDENING_PLAN.md | 3 | Date → 2026-05-30, MemoryStore → wired, test count 41→271 |
| OMEGA_IWAD_ARCHITECTURE.md | 5 | Kali "CEO" → "Founder", provider fabric → local-first, Native GGUF → IMPLEMENTED |
| MASTER_LEDGER.md | 4 | Removed duplicates, Decision 063→63, added Phase 0, removed duplicate rows |

---

### 🎯 Path A Selected: Continuity (Memory + Handoff)
**Status**: ✅ **Path A chosen. Handoff file created with full execution plan.**

**Trace**: trc_path_a_continuity
**Entity**: KALI (Founder)
**Handoff**: `data/handoff/handoff_path_a_continuity.md`

**Path A = Horizon 1, Tier 1 (Core Continuity)**: The system must remember.

| Phase | What | Files | Effort |
|-------|------|-------|--------|
| A1.1 | Fix sliding window direction | context_builder.py:126 | 15 min |
| A1.2 | Fix None.json guard | memory_store.py:129 | 10 min |
| A1.3 | Add try/except to memory writes | oracle.py:390-405 | 15 min |
| A1.4 | Deduplicate summon() | oracle.py:311-333 | 15 min |
| A2.1 | HandoffState schema | handoff.py (NEW) | 1 hr |
| A2.2 | MCP tools | omega_hub/server.py | 1 hr |
| A2.3 | CLI command | oracle_cli.py | 1 hr |
| A2.4 | Wire into oracle.py | oracle.py | 30 min |

---

### 🚀 Fleet Deep Discovery — COMPLETE
**Status**: ✅ **10/10 pillar subagents returned. 30 CRITICAL, 36 HIGH, 54 MEDIUM findings. Phase 0 remediation 92% complete.**

**Trace**: trc_fleet_synthesis
**Entity**: LILITH (CISO, Dark Oversoul)
**Handoff**: `data/handoff/latest_state.md`

| Pillar | Domain | Verdict | Critical | High | Medium | Low |
|--------|--------|---------|----------|------|--------|-----|
| P1 SysAdmin | Infrastructure | 🔴 NO-GO | 6 | 7 | 4 | 3 |
| P2 DataStore | Data Engineering | 🟡 COND | 5 | 6 | 4 | 3 |
| P3 BuildMaster | Build & Release | 🔴 NO-GO | 4 | 6 | 8 | 4 |
| P4 Bridge | API & Integration | 🟡 COND | 2 | 2 | 6 | 2 |
| P5 Sentinel | Security | 🔴 NO-GO | 4 | 3 | 5 | 2 |
| P6 ModelGate | AI & Inference | 🔴 NO-GO | 3 | 1 | 6 | 3 |
| P7 Context | Memory & State | 🟡 COND | 0 | 2 | 4 | 3 |
| P8 WatchTower | Observability | 🔴 NO-GO | 2 | 3 | 7 | 3 |
| P9 Link | Coordination | 🔴 NO-GO | 3 | 2 | 5 | 2 |
| P10 Verifier | QA & Testing | 🟡 COND | 1 | 4 | 5 | 3 |
| **TOTAL** | | **6 NO-GO / 4 COND** | **30** | **36** | **54** | **28** |

**6 Critical Cross-Cutting Gaps**:
1. 🔴 UID drift (1693 files wrong ownership) — `:U` flag on docker-compose volumes
2. 🔴 ALL model paths broken (missing `/local/all/`)
3. 🔴 API keys in git-tracked docs (C-8 never fixed)
4. 🔴 Hivemind silently broken since Hub consolidation (wrong URL)
5. 🔴 No handoff protocol (agents have amnesia)
6. 🔴 trace_id lost in provider chain (observability blind)

**Phase 0 Remediation**: 11/12 fixes applied. 1 blocked on sudo.

---

### 🚀 Default IWAD Transformation — COMPLETE
**Status**: ✅ **_omega_default rewritten as "The Company" with 16 alive entities. active_iwad switched. Engine-WAD firewall confirmed. 261/261 tests.**

**Trace**: trc_wad_transform
**Entity**: KALI (MaKaLi Unification, OpenCode CLI)
**Handoff**: `data/handoff/handoff_wad_transform_20260530.md`

| Domain | Category | Status | Description |
|--------|----------|--------|-------------|
| 🏢 Default IWAD | The Company | ✅ COMPLETE | 16 entities with alive personalities: Founder → CTO/CISO → 10 department heads |
| 🏛️ Hierarchy | Company Structure | ✅ COMPLETE | Kali (Founder) → Ma'at (CTO, P1-P5) + Lilith (CISO, P6-P10) |
| 📋 Manifest | v1.0.0 | ✅ COMPLETE | Production mode, all 16 entities listed |
| ⚙️ Active IWAD | _omega_default | ✅ COMPLETE | Switched from arcana_novai to _omega_default |
| 🔧 Hierarchy Code | Suffix Support | ✅ COMPLETE | get_rank() now finds _founder/_cto/_ciso suffixes |
| 🧪 Tests | Updated | ✅ COMPLETE | Entity refs changed to default WAD entities |
| 🏗️ Engine-WAD Firewall | Confirmed | ✅ COMPLETE | Engine never imports entity names, WADs never import engine code |

**Key Design Decisions**:
1. **Kali is the Founder, not CEO** — She built the vision. She directs. She doesn't manage.
2. **Ma'at is the CTO, not just "order"** — She measures truth with data. She pushes back with evidence.
3. **Lilith is the CISO, not just "dark"** — She assumes everything fails. She plans for it.
4. **Arcana-NovAi stays as IWAD** — Not a PWAD overlay. Complete, standalone, alternative.
5. **Each entity has a real opinion** — Not job descriptions. Living personalities with voices.

---

## 📡 Session Completions — 2026-05-30 (LOCAL-FIRST CONFIG CENTRALIZATION)

### 🚀 Local-First Config Centralization — COMPLETE
**Status**: ✅ **Provider fabric reordered local-first. All config centralized. NativeGGUFProvider upgraded to full Zen 2 engine. 261/261 tests passing.**

**Trace**: trc_local_first_config
**Entity**: SOPHIA (via mimo-v2.5-free, OpenCode CLI)
**Handoff**: `data/handoff/handoff_local_first_config_20260530.md`

| Domain | Category | Status | Description |
|--------|----------|--------|-------------|
| 🔀 Provider Fabric | Local-First Reorder | ✅ COMPLETE | native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenRouter(4) → OpenCode(5) → Copilot(6) |
| 📊 Models Config | v2.0.0 | ✅ COMPLETE | Realistic context windows (4K-16K), removed phantom krikri-7b, OMP_NUM_THREADS fixed to 6 |
| ⚙️ Omega Config | v2.2.0 | ✅ COMPLETE | Added `inference.hardware` section with Zen 2 topology |
| 🖥️ NativeGGUFProvider | Zen 2 Engine | ✅ COMPLETE | CPU pinning, memory-aware context, dynamic reload, status reporting |
| 🧠 CpuOptimizer | New Methods | ✅ COMPLETE | enforce_affinity, get_cpu_topology, pin_external_process, build_pinned_command |
| 🔗 ModelGateway | Models.yaml Wiring | ✅ COMPLETE | _merge_native_gguf_config(), fixed priority sorting |
| 🧪 Tests | Fixed + Expanded | ✅ COMPLETE | 3 broken tests fixed, 5 new tests added |
| 📝 Other | greek.py, opencode.json | ✅ COMPLETE | krikri-7b→8b, context limits aligned |

**Key Architecture Decisions**:
1. **Local-First is non-negotiable** — native-gguf is primary inference backend, cloud is fallback
2. **models.yaml is single source of truth** for model paths, context, threads, KV cache
3. **Context windows sized to use case** — 4K for short Q&A, 8K for medium work, 16K for deep analysis
4. **CPU affinity: physical cores [0,2,4,6] only** — SMT siblings reserved for I/O

---

## 📡 Session Completions — 2026-05-27 (Sovereign Steward v2 — Overseer Mode)

### 🚀 Sovereign Steward v2 (Empirical Mapping) & Omega Gateway Deployment — INITIATED
**Status**: 🔄 **Sovereign Steward v2 (Empirical Mapping) and local Omega Gateway (port 8018) deployment initiated. 259/259 tests passing.**

**Trace**: trc_sovereign_steward_v2
**Entity**: SOPHIA / KALI (Overseer mode via OpenCode CLI)
**Duration**: Single session (strategic planning + builder dispatch)

| Domain | Category | Status | Description |
|--------|----------|--------|-------------|
| 🛡️ Provider Fabric | Empirical Steward | 🔄 IN PROGRESS | Reactive backoff (60s $\rightarrow$ 120s $\rightarrow$ 240s) to empirically map Google API rate limits. |
| 🌐 Local Gateway | Omega Gateway | 🔄 IN PROGRESS | Host-side FastAPI server on port 8018 exposing OpenAI-compatible `/v1/chat/completions` for OpenCode/Cline. |
| 📊 Cost Observability | Metric Engine | 🔄 IN PROGRESS | Local SQLite `metrics.db` tracking 429 events, retry success depths, and total costs. |
| ⚙️ Systemd | Service Deployment | 🔄 IN PROGRESS | `omega-gateway.service` systemd user unit for background persistence. |
| 🛠️ OpenCode Sync | Configuration | 🔄 IN PROGRESS | `opencode.json` updated to route Gemini 1.5 Flash requests through `http://localhost:8018/v1`. |
| 🔐 Infrastructure | UID Guard | ✅ COMPLETE | Purged `:Z,U` flags from Quadlets; implemented `scripts/uid_guard.sh` to prevent UID drift. |

**Key Architecture Decisions**:
1. **Empirical Mapping**: Instead of avoiding 429s, we use a high-threshold reactive backoff to determine the actual provider boundaries.
2. **The 3-Strike Rule**: A key is only rotated and moved to COOLDOWN after 3 consecutive failures (at the 240s mark).
3. **Centralized Proxy Gateway**: All local tools route through the `omega-gateway` on port 8018, ensuring a unified traffic pattern and centralized metrics.
4. **Sovereign Permission Protocol**: Absolute ban on `:U` and `:Z` flags; enforced via `UserNS=keep-id` and `User=1000`.

---

## 📡 Session Completions — 2026-05-26 (DEEP AUDIT REMEDIATION: Provider chain reorder + 5 runtime bugs + doc accuracy. 259/259 tests. Commit `e09fed3`)

### 🚀 Deep Audit Full Remediation — COMPLETE
**Status**: ✅ **All 4 audit findings, 5 runtime bugs, and 14 test sovereign violations fixed. 259/259 tests passing.**

**Trace**: trc_deep_audit_remediation
**Entity**: KALI (Overseer mode via OpenCode CLI)
**Commit**: `e09fed3`
**Duration**: Single session (parallel dispatch)

| Domain | Category | Count | Status |
|--------|----------|-------|--------|
| 🐛 Runtime Bugs | UnboundLocalError, AttributeError, copy-paste path, lock deadlock, sync subprocess in async | 5 fixed | ✅ |
| 📚 Doc Accuracy | ORACLE_STACK, AGENTS.md, INDEX.md, OMEGA_IWAD_ARCHITECTURE.md | 4 files fixed | ✅ |
| 🧪 Test Sovereign Compliance | @pytest.mark.asyncio → @pytest.mark.anyio (82 occurrences), missing assertion, asyncio.run → anyio.run | 14 files fixed | ✅ |
| 🧹 Stale Artifacts | 58 stale entity directories removed | ~58 deletions | ✅ |
| 🆕 New Entity | Movie-Expert added to entities.yaml | `pillar: personal` | ✅ |

**Provider Chain (final)**:
```
BEFORE:                    AFTER:
native-gguf → lmster →    Google(0) → OpenRouter(1) → OpenCode(2) →
Ollama → OpenRouter        Copilot(3) → Lmster(4) → Ollama(5) →
                            native-gguf(98, deferred) → mock(99)
```

**5 Runtime Bugs Fixed**:
| Bug | File | Root Cause | Fix |
|-----|------|-----------|-----|
| B1 | `model_gateway.py` | `_generate_local` — `response` used before assignment on final retry | Initialized `response = None` before loop |
| B2 | `iris/server.py` | `Entity` has `pillars` (plural), endpoint used `e.pillar` (singular) → `AttributeError` | Changed to `e.pillars` + fixed `ChatResponse` model |
| B3 | `entity_roc_racoon.py` | Copy-paste: read `fpath1` instead of resolved `fpath2` | Fixed lambda target |
| B4 | `session_manager.py` | Lock persistence → stale lock files cause infinite hang | Added 30s stale-lock TTL detection |
| B5 | `model_gateway.py` | Sync `subprocess.run()` in async context → event loop blocked | Migrated to `anyio.run_process()` |

**Test Migration**: 14 files bulk-migrated from `@pytest.mark.asyncio` to `@pytest.mark.anyio`. Missing assertion in `test_entity_registry_errors.py` replaced with proper `pytest.raises`. `verify_jem_pipeline.py` and `test_bug_001_fix.py` migrated from `asyncio.run()` to `anyio.run()`.

**Documentation Fixed**:
- **ORACLE_STACK.md**: Removed Nova speculative decoder references, updated provider chain and test counts (241→259), added 5 new test modules, corrected rule #9 from "lmster primary" to "Gemma 4 31B primary"
- **AGENTS.md**: Removed SambaNova/Cerebras (providers that never existed), updated provider chain to cloud-first, research index count 52→180+, test count 241→259
- **INDEX.md**: Deduplicated 11 duplicate research entries, fixed 2 broken `.md` links, updated date to 2026-05-26
- **OMEGA_IWAD_ARCHITECTURE.md**: Provider fabric §10 reordered, WAD status table §9 corrected (`--iwad` flag ✅, startup personality ✅)

**Cleanup & New Entity**:
- Removed 58 stale `entity_N` test directories + 9 named test artifacts from `data/entities/`
- Added Movie-Expert entity definition to `config/entities.yaml` — seed for Arcana-NovAi personal OS (`pillar: personal`, film/cinema domain, 0.8 temp)

**Key Files Changed**:
- `config/providers.yaml` — Complete chain reorder + OpenCode provider added
- `config/entities.yaml` — Movie-Expert entity added
- `src/omega/oracle/model_gateway.py` — B1, B5 fixes + provider_map + health check + AnyIO run_process
- `src/omega/iris/server.py` — B2 fix (pillar → pillars)
- `src/omega/oracle/entity_registry.py` — B3-adjacent yaml.YAMLError handling
- `src/omega/oracle/session_manager.py` — B4 stale lock detection
- `src/omega/entity_roc_racoon.py` — B3 copy-paste fix
- `ORACLE_STACK.md` — Full documentation accuracy pass
- `AGENTS.md` — Full documentation accuracy pass
- `docs/strategy/OMEGA_IWAD_ARCHITECTURE.md` — Provider fabric + WAD status correction
- `docs/research/INDEX.md` — Dedup + broken link fix
- 14 test files — Bulk asyncio→anyio migration + missing assertion fixes
