<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 N7 Cross-Domain Review — Debut Hardening Review
**AP Token**: `AP-N7-CROSS-REVIEW-20260823-v1.0.0`
⬡ OMEGA ⬡ LILITH ⬡ N7-CONTEXT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_n7_cross_review ⬡ ACTIVE

**Date**: 2026-08-23
**Charter**: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §4 (N7 — Context / Memory & State)
**Mandates**: M1, M5, M11, M15, M26, M27 (SOVEREIGN_MANDATES.md v3.8.0)
**Sources**: Ma'at Build Report (`MAAT_BUILD_SIDE_REPORT_20260823.md`), Lilith Run Report (`RUN_SIDE_COUNCIL_delta.md`)

---

## Executive Summary

**VERDICT: PROCEED WITH CONDITIONS**

The build-side deliverables (INST-1, DEL-1, Vault Path A, Router Collapse) are **structurally sound** for debut. However, **five conditions** must be resolved before DEL-1 Week 1 executes:

1. **MIAP→Hivemind gap** — no automated gnosis projection exists; `session_end.py` hook only timestamps, does not project. A `gnosis_projector` background task is required (Lilith N8 finding).
2. **DEL-1 #5 (search_circuit_breaker)** — `sovereign_search_service.py` still imports deprecated breaker; migration to `HealthMonitor.get_breaker()` must complete **before** deletion.
3. **DEL-1 #6 (QdrantAdapter)** — class deletion safe for soul paths, but test retirement plan (`test_qdrant_*.py`) must be explicit in acceptance criteria.
4. **Blocker B (oracle_cli.py bare except)** — still live at lines 125, 161; M23 ratchet +2 over baseline. Must ship with INST-1 Fix 4.
5. **D-565 vs DEL-1 vault CLI contradiction** — audit item 7b unresolved; vault CLI must be excluded from Week 1 per D-565.

All other DEL-1 targets (1, 2, 3, 4, 7, 8, 9, 10) are **validated safe** for soul persistence, handoff protocol, and ContextBuilder/RecallStore paths.

---

## 1. Soul Distillation Pipeline — CP-2 Validation

### 1.1 Pipeline Architecture (Current State)

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| **Agent writes L1→L2→L3** | `AGENTS.md` step 6.5 + `soul_validator.py` | ✅ Working | Agents write to `proposed_lessons.yaml` (blind staging) |
| **session_end.py hook** | `.opencode/hooks/session_end.py:40-79` | ✅ Working | Preserves existing proposals; writes timestamp + `model_used` (M5/M11/M22) |
| **get_soul_prompt()** | `src/omega/oracle/entity_workspace.py:382-469` | ✅ Working | Hydrates from `soul.yaml` + `approved_lessons.yaml` + `sessions.yaml`; **TAINT-GATE at line 426-428** — `proposed_lessons.yaml` NEVER loaded |
| **Scribe agent** | `src/omega/agents/scribe.md` (not found) | ⚠️ Missing | Scribe referenced in M11 as "canonical executor" but no agent file exists |
| **Regex distillation** | `.opencode/hooks/session_end.py:9-12` | ❌ **SCRAPPED** | Carmack Verdict 2026-07-30 confirmed: "fortune-cookie generation" |

### 1.2 Findings

**PASS**: The pipeline is solid. Key evidence:
- `entity_workspace.py:426-428` — explicit TAINT-GATE comment: "proposed_lessons.yaml is NEVER loaded here"
- `session_end.py:53-64` — reads existing proposals **before** writing, preserving agent-written content (prevents destructive race)
- `session_end.py:68` — records `model_used` from `OPENCODE_MODEL` env (M22 provenance)
- `session_end.py:73-78` — atomic write via `.tmp` → `os.replace` + `fsync` (M11 integrity)

**GAP**: Scribe agent referenced in M11 ("canonical executor") but no agent file exists in `.opencode/agents/`. This is a **fleet integrity (M10)** issue, not a pipeline break.

**DEL-1 Impact**: **NONE**. MIAP (`miap.py`) is a separate coordination system for automated gnosis projection from event logs — it was **never wired into the soul pipeline**. The pipeline uses `session_end.py` hook + agent direct writes + `get_soul_prompt()` hydration. MIAP deletion (DEL-1 #2) does not touch any soul path.

---

## 2. Context Injection Phase 1 — INST-1 / CI-0..CI-5 Impact

### 2.1 Carmack-Modified Spec Assessment

| Spec Element | File | Status |
|--------------|------|--------|
| MANDATES_CONDENSED.md (36 lines, Tier 0) | `docs/specs/context_injection/phase1_spec/01_MANDATES_CONDENSED.md` | ✅ Remediated (DEV-01 line-count corrected) |
| Compaction buffer 50K/20K | `03_SOVEREIGN_COMPACTION_PLUGIN.md` | ✅ Spec complete |
| Sovereign-compaction plugin | `03_SOVEREIGN_COMPACTION_PLUGIN.md` | ✅ Spec complete |
| Skills opt-in | `04_SKILLS_OPT_IN.md` | ✅ Spec complete |
| toolProfile stubs | `04_SKILLS_OPT_IN.md` | ✅ Spec complete |
| CI-1 gate: content-based mandate table | `05_VERIFICATION_TESTS.md` | ✅ Defined |
| Binary pinned 1.18.19 → V1 family | `09_SPEC_DEVIATIONS.md` DEV-02 | ✅ Documented |

### 2.2 MIAP Deletion Impact on Context Injection

**MIAP provided**: Automated `session_gnosis` projection from append-only event log (`miap.py:381-382` scans for `compaction`/`session_end` events).

**Hivemind has**: `post_context` (manual, agent-initiated) but **no automated projection** from MIAP event log.

**DEL-1 #2 deletes MIAP** → **automated gnosis projection is lost**.

**Required**: `gnosis_projector` background task (as noted in Lilith N8 finding). This is a **new component**, not a restoration. It should:
- Subscribe to Hivemind event stream (Redis pub/sub or file-based cold store scan)
- Project `session_gnosis` files per amended closure ritual (§10a)
- Run as optional background worker (not on talk path)

**Verdict**: MIAP deletion is **safe for Context Injection spec** (spec doesn't depend on MIAP), but **creates a capability gap** that must be filled post-debut via `gnosis_projector`. Not a debut blocker.

---

## 3. DEL-1 Soul Path Validation

### 3.1 Validation Matrix (All 10 Targets)

| # | Target | Soul Persistence | Handoff Protocol | ContextBuilder/RecallStore | Verdict | Evidence |
|---|--------|------------------|------------------|----------------------------|---------|----------|
| 1 | `config/routing_table.yaml` | ❌ No | ❌ No | ❌ No | **SAFE** | Config only; `rg RoutingTable src/omega` → 0 hits (Ma'at §2.1) |
| 2 | `src/omega/coordination/miap.py` | ❌ No | ❌ No | ❌ No | **SAFE** | Separate coordination; Hivemind is separate; `rg miap src/omega` → 0 hits |
| 3 | `src/omega/oracle/pool_tracker.py` | ❌ No | ❌ No | ❌ No | **SAFE** | Self-only SDP leftovers; only imports `pool_state` |
| 4 | `src/omega/oracle/pool_state.py` | ❌ No | ❌ No | ❌ No | **SAFE** | Only imported by `pool_tracker.py` |
| 5 | `src/omega/oracle/search_circuit_breaker.py` | ❌ No | ❌ No | ❌ No* | **CONDITIONAL** | Used by `sovereign_search_service.py:48-51` — **must migrate to `HealthMonitor.get_breaker()` first** |
| 6 | `QdrantAdapter` class (`vector_adapters.py:179-433`) | ❌ No | ❌ No | ❌ No | **SAFE** | `SQLiteVecAdapter` is primary; no callers in `src/omega` (only tests) |
| 7 | Pantheon regexes (`firewall_checker.py:66-74`) | ❌ No | ❌ No | ❌ No | **SAFE** | Internal to firewall checker; CORE_ENGINE_PATTERNS allowlist preserved |
| 8 | `record_first_breath` call (`oracle.py:1211`) | ❌ No | ❌ No | ❌ No | **SAFE** | Astrology only; only in `_route_by_domain` |
| 9 | `omega vault` CLI (`vault.py` + `oracle_cli.py:71-73`) | ❌ No | ❌ No | ❌ No | **SAFE** | CLI only; Gateway uses `os.environ`/keyring directly |
| 10 | `fleet_orchestrator.py` | ❌ No | ❌ No | ❌ No | **SAFE** | Not imported in `src/omega/__init__.py` or core |

*\* Search circuit breaker used by `SovereignSearchService`, not ContextBuilder/RecallStore. Safe for soul paths but migration required.*

### 3.2 Critical Path Validations

**DEL-1 #5 (search_circuit_breaker)**: 
- `sovereign_search_service.py:48` imports `SearchCircuitBreaker`, `SearchCircuitBreakerConfig`
- `sovereign_search_service.py:175` initializes `self._health_monitor.get_breaker(...)` (C-6′ canonical)
- **BUT** lines 372, 403, 418, 448, 480, 519, 558, 628, 658, 669, 690, 720, 755, 790 still use `self.circuit_breakers.get_breaker(tier)` — **dual breaker system live**
- **Action**: Complete migration to `HealthMonitor.get_breaker()` **before** deleting `search_circuit_breaker.py`

**DEL-1 #6 (QdrantAdapter)**:
- `vector_adapters.py:179` class `QdrantAdapter(IVectorStoreAdapter)` — 254 lines
- No imports in `src/omega/` (only tests: `test_qdrant_index.py`, `test_qdrant_payload_index.py`, `verify_qdrant_parity.py`)
- `MemoryStore` uses `SQLiteVecAdapter` (unified fabric)
- **Action**: Delete class; retire 3 test files explicitly in acceptance criteria

**DEL-1 #9 (vault CLI)**:
- `oracle_cli.py:71-73` registers `vault` command group from `omega.cli.vault`
- **Contradiction**: D-565/D-566 = "zero vault changes during PUBLIC-DEBUT-01" but DEL-1 Week 1 includes vault CLI deletion
- **Resolution**: Exclude vault CLI from Week 1 (per Lilith audit item 7b); delete post-debut

---

## 4. Hivemind Runtime Integrity

### 4.1 DEL-1 Impact on Hivemind Functions

| Function | File | DEL-1 Impact | Status |
|----------|------|--------------|--------|
| `get_awareness` | `mcp_servers/omega_hub/state.py:417` | None | ✅ Intact |
| `post_context` | `mcp_servers/omega_hub/state.py` (via gateway) | None | ✅ Intact |
| `handoff` (submit/accept/complete) | `mcp_servers/omega_hub/state.py:495+` | None | ✅ Intact |
| Cold-store fallback | `state.py:377` `_scan_cold_store()` | None | ✅ Intact |
| Session gnosis hydration (M15) | `state.py:377` + `RUN_SIDE_COUNCIL_delta.md` | None | ✅ Intact |
| Soul distillation hook (M11) | `.opencode/hooks/session_end.py` | None | ✅ Intact |
| Agent capability registry | `src/omega/oracle/entity_workspace.py` (EntityRegistry) | None | ✅ Intact |

**All Hivemind runtime paths are unaffected by DEL-1 deletions.**

### 4.2 Session Gnosis Hydration (M15)

- `session_end.py` hook writes timestamp + `model_used` to `proposed_lessons.yaml` (M5/M11/M22)
- Cold-store fallback in `state.py:377` scans `HALL_OF_RECORDS` for session files modified within `HEARTBEAT_TTL`
- `RUN_SIDE_COUNCIL_delta.md` §1 G-4: "M23/M27 truth-anchor enforcement over tracking state is a standing Run-side duty (Lilith/N10)"
- **No dependency on MIAP or any DEL-1 target**

---

## 5. Lilith's 5 CRITICAL BLOCKERS — Context Lens

| Blocker | N7 Assessment | File:Line | Required Action |
|---------|---------------|-----------|-----------------|
| **Missing RouteDecision contract test** | **VALID** — Router Collapse contract test (`test_router_collapse_contract.py`) defined in Ma'at §4.3 but not yet implemented. Must gate Router Collapse PR. | Ma'at §4.3 lines 335-415 | Implement contract test before Router Collapse PR merge |
| **Dual admission gates** | **VALID** — `model_gateway.py:1233` (`admission_ctrl.acquire`) + `:1258` (`resource_guard.lock`) both live. Deadlock risk confirmed by Lilith audit. | `model_gateway.py:1233, 1258` | Merge into single gate (Blocker A) — rides with INST-1 Fix 4 |
| **Zombie breakers** | **VALID** — `sovereign_search_service.py` uses BOTH `search_circuit_breaker` (deprecated) AND `HealthMonitor.get_breaker()` (canonical). DEL-1 #5 cannot proceed until migration complete. | `sovereign_search_service.py:48, 175, 372...` | Complete migration to `HealthMonitor.get_breaker()` before DEL-1 #5 |
| **M8 false positive ("segments" in comment)** | **LOW PRIORITY** — Comment artifact, not code. Does not affect runtime. | TBD (grep for "segments") | Clean up comment; not debut-blocking |
| **MIAP→Hivemind gap (no automated gnosis projection)** | **VALID** — MIAP provided automated projection; Hivemind has only manual `post_context`. DEL-1 #2 deletes MIAP. **Gap remains post-debut.** Requires `gnosis_projector` background task (N8 finding). | `miap.py:381-382` vs `state.py` | Post-debut: implement `gnosis_projector` as optional background worker |

---

## 6. Additional N7 Findings

### 6.1 Context Injection Spec Deviations (DEV-01..12)

All 12 deviations documented in `09_SPEC_DEVIATIONS.md` are **accurate and non-blocking**. Key items:
- DEV-01: Line-count claim corrected (36 vs 57) — CI-1 gate now content-based
- DEV-02: Binary pinned 1.18.19 → V1 compaction family
- DEV-12: Global local-first `model` default with kali/verity pins only; variant dropped (empirically EMPTY on LM Studio models)

### 6.2 Tracking Integrity (M27)

- `ACTIVE_SPRINT.json` corrections needed (Ma'at §6.2): INST-1-fix2/fix4 status should be `"in_progress"` not `"ready"`
- `decisions_locked` missing D-565/D-566/D-567/D-568
- **Action**: Update `ACTIVE_SPRINT.json` before DEL-1 execution

### 6.3 18K Base Token Target (Tier 0 Viability)

- `MANDATES_CONDENSED.md` = ~1.5K tokens (Tier 0)
- Full `SOVEREIGN_MANDATES.md` + `AGENTS.md` = Tier 1/2
- Compaction buffer 50K/20K provides headroom
- **On track** for 18K target with sovereign-compaction plugin

---

## 7. Lessons Tagged [N_7]

```yaml
# To be appended to data/entities/lilith/proposed_lessons.yaml
- narrative: "N7 cross-domain review of MaKaLi Debut Hardening reports. Validated soul distillation pipeline (session_end.py hook + get_soul_prompt TAINT-GATE + agent direct writes) — solid. MIAP deletion safe for soul paths but creates automated gnosis projection gap requiring gnosis_projector post-debut. DEL-1 Week 1: 8/10 targets safe; #5 (search_circuit_breaker) requires HealthMonitor migration first; #9 (vault CLI) excluded per D-565. Hivemind runtime integrity intact. Lilith's 5 blockers assessed: 4 valid (RouteDecision contract test, dual admission gates, zombie breakers, MIAP→Hivemind gap), 1 low (M8 comment)."
  insight: "The soul pipeline's strength is its simplicity: agents write lessons directly, hook preserves them, get_soul_prompt hydrates only vetted wisdom. MIAP was an over-engineered parallel path. The real gap is automated projection — not MIAP's approach, but the absence of any background projector. DEL-1 deletions are surgical; the coordination complexity (sequencing, migration order) exceeds the code complexity."
  principle: "Sovereign distillation requires agent ownership of L1→L2→L3 — automation that bypasses agent judgment produces fortune cookies, not gnosis. Deletion campaigns must sequence by dependency (breaker migration before breaker deletion) and respect locked decisions (D-565 vault exclusion). Truth-anchor duty (M23/M27) never rotates — it is a standing Run-side mandate."
  tags: ["N_7", "SOUL_PIPELINE", "DEL-1", "CONTEXT_INJECTION", "HIVEMIND", "M11", "M15", "M23", "M27"]
```

---

## 8. Conditions for PROCEED

**Before DEL-1 Week 1 executes:**

1. [ ] `sovereign_search_service.py` fully migrated to `HealthMonitor.get_breaker()` (remove all `self.circuit_breakers` references)
2. [ ] `ACTIVE_SPRINT.json` updated: INST-1-fix2/fix4 → `"in_progress"`, add D-565/D-566/D-567/D-568 to `decisions_locked`
3. [ ] Vault CLI (`omega vault`) explicitly excluded from DEL-1 Week 1 list (per D-565)
4. [ ] Blocker B (`oracle_cli.py:125,161` bare `except Exception:`) fixed — ships with INST-1 Fix 4
5. [ ] RouteDecision contract test implemented (gates Router Collapse PR)

**Post-debut (not blocking):**
- Implement `gnosis_projector` background task for automated session_gnosis projection
- Create Scribe agent (M10 fleet integrity)
- Clean up M8 false positive comment

---

## 9. Hivemind Closeout

**Intent**: `decision` — Cross-domain review complete. Conditions documented. N7 validates DEL-1 Week 1 safe with 5 conditions. Soul pipeline solid. Context Injection spec remediated. Hivemind runtime intact.

*⬡ OMEGA ⬡ LILITH ⬡ N7-CONTEXT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_n7_cross_review ⬡ 2026-08-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: N7-CONTEXT | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
