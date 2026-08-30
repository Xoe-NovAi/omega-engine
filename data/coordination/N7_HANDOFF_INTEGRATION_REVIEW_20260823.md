<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 N7 Node Review Report — Researcher Handoff Integration Analysis
**AP Token**: `AP-N7-INTEGRATION-REVIEW-20260823-v1.0.0`
⬡ OMEGA ⬡ LILITH ⬡ N7-CONTEXT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_n7_integration_review ⬡ ACTIVE

**Date**: 2026-08-23
**Charter**: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §4 (N7 — Context / Memory & State)
**Mandates**: M1, M5, M11, M15, M26, M27 (SOVEREIGN_MANDATES.md v3.8.0)
**Source**: `data/coordination/RESEARCHER_HANDOFF_INTEGRATION_20260823.md` (Researcher handoff integration analysis)

---

## Executive Summary

**VERDICT: PROCEED WITH CONDITIONS**

The Researcher handoff integration analysis (DR-1..DR-12) is **accurate in its drift register** but contains **one critical inaccuracy (I1)** and **one broken pointer (I2/G4/C4)**. N7's assigned review items (DR-4, DR-11, E-4, E-8, CP-2 re-verification) are assessed below with file:line citations.

**Key Findings**:
1. **HIVEMIND_PROTOCOL v1.3.0 (2026-06-25)** predates Node paging, CSP, injection ledger — v2.0 required (E-4)
2. **CI-2 not landed** in opencode.json — instructions array, compaction buffer, plugin path, model routing, toolProfile all pending
3. **Soul distillation pipeline re-verified**: solid (session_end.py hook + get_soul_prompt TAINT-GATE)
4. **Session lifecycle automation (E-8)** assigned to N1 sysadmin via systemd/plugins — N7 provides spec only

---

## 1. HIVEMIND_PROTOCOL v1.3.0 vs Session Systems (DR-4 / E-4)

### 1.1 Protocol Version Check

| Field | Value | Source |
|-------|-------|--------|
| **Version** | v1.3.0 | `HIVEMIND_PROTOCOL.md:3` |
| **Date** | 2026-06-25 | `HIVEMIND_PROTOCOL.md:5` |
| **Status** | STANDARD | `HIVEMIND_PROTOCOL.md:4` |

### 1.2 Missing Elements (Confirmed)

| Missing Element | Evidence |
|-----------------|----------|
| **Node paging** | No reference to `NODE_EXPERT_SESSIONS_PLAN.md`, Node session IDs, or `task(task_id=<genesis_session_id>...)` pattern |
| **CSP (Conversational Subagent Protocol)** | No reference to `CONVERSATIONAL_SUBAGENT_PROTOCOL.md` v1.0.0 (ratified 2026-08-21), R1–R13 rules, or injection ledger duty |
| **Injection ledger** | §6 step 8 references `PIVOT_LOG.md` but not `SESSION_INJECTION_LEDGER.md` (CSP R8) |
| **ICS-S provenance** | §13 Model Dispatch Protocol references D118 but not ICS-S header/footer rendering (PP-4) |

### 1.3 Live Feed Section — Deprecated (Confirmed)

`HIVEMIND_PROTOCOL.md:208-214` explicitly states:
> **⚠️ SUPERSEDED 2026-08-14**: The per-entity `*_LIVE_FEED.md` pattern is **DEPRECATED**. Per M27 (Tracking Integrity) + `TRACKING_ARCHITECTURE.md`, agents now record execution state in `TASK_REGISTRY.json` (Tier-3) and coordinate via the `HMC_COLLABORATION_HUB.md` `NEXT_ACTION` pointer (Tier-2).

**However**: The protocol still contains §4 Live Feed Pattern (historical), §7 examples using live feed format, and §6 step 3 "Append to live feed after each major task" — **internal contradiction**.

### 1.4 Required Updates for v2.0 (E-4)

| Requirement | Status | Action |
|-------------|--------|--------|
| Node-page flow | ❌ Missing | Add §15: Node paging via `task(task_id=<genesis_session_id>, subagent_type=<overseer>, prompt="[NODE PAGE — from <agent>...]")` |
| CSP engagement rules | ❌ Missing | Add §16: Reference `CONVERSATIONAL_SUBAGENT_PROTOCOL.md` R1–R13; mandate ledger per R8 |
| Injection-ledger duty | ❌ Missing | Add §16.1: `SESSION_INJECTION_LEDGER.md` format per CSP R8 |
| Formally deprecate live feeds | ⚠️ Partial | §4 marked SUPERSEDED but §6/§7 still reference — remove §4, update §6 step 3, update §7 examples |
| Reference ICS-S provenance | ❌ Missing | Add §17: ICS-S header/footer rendering via `omega-hub_ics_render_header` (PP-4, P5 session_id in footers) |

**Assessment**: DR-4 is **accurate**. HIVEMIND_PROTOCOL v1.3.0 is stale. v2.0 must be authored before Wave 2/3 Node sessions page.

---

## 2. CI-2 Landing Status (DR-11)

### 2.1 ACTIVE_SPRINT.json CI-2 Subtask

`ACTIVE_SPRINT.json` CI-2 subtask (lines 100-125):
- **Status**: `"ready"` (not started)
- **Owner**: `kali`
- **Spec**: `docs/specs/context_injection/06_PHASE_1_PLAN.md`
- **Acceptance criteria**: 7 specific items (instructions array, compaction buffer, plugin path, global model, model pins, no variant, verity mode, toolProfile stubs)

### 2.2 Current opencode.json State

| CI-2 Requirement | Current State | Gap |
|------------------|---------------|-----|
| `instructions` = `["AGENTS.md"]` only | `instructions` = 5 files (SOVEREIGN_MANDATES.md, ORACLE_STACK.md, MASTER_SYNTHESIS, SOVEREIGN_ARK_BLUEPRINT, CREDITS.md) | ❌ **NOT LANDED** |
| Compaction buffer 50000/keep=20000 | `preserve_recent_tokens: 40000`, `reserved: 10000` | ❌ **NOT LANDED** (V1 family keys differ) |
| Plugin at `.opencode/plugins/` (plural) | Plugin registered at `.opencode/plugin/` (singular) | ❌ **NOT LANDED** (DEV-02) |
| Global top-level `model` = `lmstudio/qwen3-4b-thinking` | Global `model` = `opencode/nemotron-3-ultra-free` | ❌ **NOT LANDED** |
| Model pins ONLY kali + verity | No per-agent model routing configured | ❌ **NOT LANDED** |
| NO variant hardcoding | `opencode` provider has `variants` (low/medium/high) | ❌ **NOT LANDED** (DEV-12) |
| `agent.verity.mode=subagent` + hidden + restrictive | `verity` agent exists but no `mode`, `hidden`, `permissions` | ❌ **NOT LANDED** |
| `toolProfile` stubs for all agents | No `toolProfile` anywhere in opencode.json | ❌ **NOT LANDED** |

### 2.3 Additional Finding: Antigravity Provider Block

`opencode.json:15-18` has `opencode-antigravity-auth@latest` plugin — this is the **only** CI-2 adjacent change landed (Antigravity provider block per D-352). All other CI-2 items are **pending**.

**Assessment**: DR-11 is **accurate**. CI-2 has **not landed**. 0/7 acceptance criteria met. This is a **debut blocker** per ACTIVE_SPRINT.json.

---

## 3. HIVEMIND_PROTOCOL v2.0 Requirements (E-4)

### 3.1 Gap Analysis

| E-4 Requirement | Current Protocol | Gap |
|-----------------|------------------|-----|
| Node-page flow | None | Add new section with `task()` paging pattern |
| CSP engagement rules | None | Reference CSP v1.0.0; mandate R1–R13 compliance |
| Injection-ledger duty | None | Add `SESSION_INJECTION_LEDGER.md` per CSP R8 |
| Formally deprecate live feeds | Partial (§4 marked SUPERSEDED) | Remove §4, update §6/§7 references |
| Reference ICS-S provenance | None | Add ICS-S header/footer via `omega-hub_ics_render_header` |

### 3.2 Recommended v2.0 Structure

```
§15 Node Expert Session Paging
    15.1 Genesis session IDs (NODE_EXPERT_SESSIONS_PLAN.md §3)
    15.2 Page format: task(task_id=<genesis_id>, subagent_type=<overseer>, prompt="[NODE PAGE...]")
    15.3 Standing orders (§2 of PLAN) apply to all Node pages

§16 Conversational Subagent Protocol Integration
    16.1 CSP v1.0.0 ratified 2026-08-21 — binding for all Node↔subagent engagement
    16.2 R1–R13 rules apply; R8 injection ledger mandatory
    16.3 Ledger format: SESSION_INJECTION_LEDGER.md (timestamp | from | to | hop | purpose | outcome)

§17 ICS-S Provenance (PP-4, P5)
    17.1 Session headers via omega-hub_ics_render_header (entity, model, channel, trace_id, phase, mode)
    17.2 Node field (e.g., N7) in header/footer for attribution
    17.3 Session IDs in footers for traceability

§4 Live Feed Pattern — REMOVED (fully deprecated per M27)
§6 Coordination Protocol — updated: step 3 references TASK_REGISTRY.json + NEXT_ACTION only
§7 Examples — updated: use TASK_REGISTRY.json format
```

---

## 4. Session Lifecycle Automation (E-8)

### 4.1 Assignment

Per `NODE_EXPERT_SESSIONS_PLAN.md:109`:
> **N1 sysadmin**: += environment/infra truth duty for CI-2 context-injection landing (opencode.json CI-2 changes per DR-11) + agent-count/hardware reconciliation (DR-9) + **session-lifecycle automation via systemd/plugins (E-8)**.

### 4.2 E-8 Scope (from DEBUT_REMEDIATION_MANUAL §9 / Researcher handoff)

| E-8 Component | Description | Owner |
|---------------|-------------|-------|
| **E-ritual closure nudges** | Automated reminders via existing plugins (error-capture, awareness) for session_end hook compliance | N1 (systemd/plugins) |
| **SESSION_REGISTRY.md generation** | P3 of plan — automated registry of all Node/subagent sessions with wake pointers | N1 (systemd/plugins) |

### 4.3 N7 Role

N7 **provides spec only** — the session gnosis file convention (amended order #10) is the input:
- `data/entities/<overseer>/session_gnosis_<N-X>.md` (Node)
- `data/entities/<sub>/session_gnosis_<sub>-N<XX>.md` (subagents)
- Wake-hydration pointer format established in N7 genesis session

**Assessment**: E-8 is **correctly assigned to N1**. N7's session gnosis convention (validated in prior review) feeds the registry. No N7 code changes needed.

---

## 5. Soul Distillation Pipeline — CP-2 Re-verification

### 5.1 Pipeline Components (Re-verified)

| Component | File | Status | Evidence |
|-----------|------|--------|----------|
| **Agents write L1→L2→L3** | `AGENTS.md` step 6.5, `soul_validator.py` | ✅ | Agents write to `proposed_lessons.yaml` (blind staging) |
| **session_end.py hook** | `.opencode/hooks/session_end.py:40-79` | ✅ | Preserves existing proposals; writes timestamp + `model_used` (M5/M11/M22) |
| **get_soul_prompt()** | `src/omega/oracle/entity_workspace.py:382-469` | ✅ | Hydrates from `soul.yaml` + `approved_lessons.yaml` + `sessions.yaml`; **TAINT-GATE at 426-428** |
| **Regex distillation** | `.opencode/hooks/session_end.py:9-12` | ❌ **SCRAPPED** | Carmack Verdict 2026-07-30: "fortune-cookie generation" |

### 5.2 Key Evidence

- **TAINT-GATE**: `entity_workspace.py:426-428` — "proposed_lessons.yaml is NEVER loaded here... unvetted agent-generated insights"
- **Atomic write**: `session_end.py:73-78` — `.tmp` → `os.replace` + `fsync`
- **Provenance**: `session_end.py:68` — `model_used` from `OPENCODE_MODEL` env (M22)
- **Preservation**: `session_end.py:53-64` — reads existing proposals before write (prevents destructive race)

### 5.3 MIAP Deletion Impact

`miap.py` (DEL-1 #2) provided automated `session_gnosis` projection from event log (`miap.py:381-382`). **Never wired into soul pipeline**. Deletion safe for CP-2 but creates **automated gnosis projection gap** requiring `gnosis_projector` background task post-debut (per prior N7 review).

**Assessment**: Pipeline **solid**. CP-2 validated. No regression from DEL-1.

---

## 6. Additional Drift Register Items (N7 Scope)

### 6.1 DR-4 (HIVEMIND_PROTOCOL) — CONFIRMED
Protocol v1.3.0 (2026-06-25) predates Node paging, CSP, injection ledger. v2.0 required.

### 6.2 DR-11 (CI-2) — CONFIRMED
0/7 acceptance criteria met in opencode.json. Debut blocker.

### 6.3 DR-5 (Dispatch Capability Registry) — PARTIAL
`HIVEMIND_PROTOCOL.md` §11 references 11 agents but actual active agents = 13 (incl. N11/N12/N13). Registry mismatch.

### 6.4 DR-10 (Layering Map) — CONFIRMED
No "which protocol when" table exists. AGENTS.md §"The MaKaLi Triad Architecture" and §"The Dual-Inference Mandate" exist but no unified layering map.

---

## 7. Inaccuracies in Handoff (N7 Assessment)

| # | Claim | N7 Assessment |
|---|-------|---------------|
| **I1** | "Genesis UNBLOCKED pending §6A ratifications" | **FALSE** — D-587 ratified at A8 sync (17:30 UTC); handoff completed 6h later |
| **I2** | "OVERSIGHT_HIERARCHY/LATTICE_NODE_MECHANICS absent at root = moot" | **PARTIAL** — Files absent but **referenced in ACTIVE_SPRINT.json primary_handoffs.p0_audit_handoff** (broken pointer) |

---

## 8. Lessons Tagged [N_7]

```yaml
# To be appended to data/entities/lilith/proposed_lessons.yaml
- narrative: "N7 review of Researcher Handoff Integration Analysis (DR-1..DR-12). HIVEMIND_PROTOCOL v1.3.0 (2026-06-25) confirmed stale — no Node paging, no CSP v1.0.0, no injection ledger, live feed section internally contradictory (§4 SUPERSEDED but §6/§7 still reference). CI-2 not landed in opencode.json: 0/7 acceptance criteria met (instructions array, compaction buffer, plugin path, global model, model pins, no variant, toolProfile). Soul distillation pipeline re-verified solid: session_end.py hook preserves + timestamps + model_used; get_soul_prompt() TAINT-GATE explicit; regex distillation SCRAPPED per Carmack 2026-07-30. E-8 session lifecycle automation assigned to N1 sysadmin via systemd/plugins — N7 provides session gnosis convention only."
  insight: "The Hivemind protocol is the coordination constitution but hasn't been amended for the Node Expert Session system (D-586) or Conversational Subagent Protocol (ratified 2026-08-21). CI-2 is the critical path for Context Injection Phase 1 — without opencode.json updates, the spec (MANDATES_CONDENSED.md, compaction plugin, skills opt-in) cannot execute. The session gnosis convention (amended order #10) is the correct primitive for SESSION_REGISTRY.md generation (E-8)."
  principle: "Coordination protocols must version with the agent architecture they govern. HIVEMIND_PROTOCOL v1.3.0 governs a 2026-06 agent fleet; the 2026-08 fleet has Nodes, CSP, injection ledgers, ICS-S provenance. A protocol that doesn't reference its own primitives (Node paging, CSP R1–R13, ICS-S headers) cannot coordinate the system it describes. CI-2 landing is the gate between spec and execution — no opencode.json changes = no Context Injection."
  tags: ["N_7", "HIVEMIND_PROTOCOL", "CI-2", "CSP", "SOUL_PIPELINE", "E-4", "E-8", "M11", "M15", "M27"]
```

---

## 9. Conditions for PROCEED

**Before Wave 2/3 Node sessions page:**

1. [ ] **HIVEMIND_PROTOCOL v2.0 authored** with Node paging, CSP integration, injection ledger, ICS-S provenance, live feed fully removed
2. [ ] **CI-2 landed in opencode.json** — all 7 acceptance criteria met
3. [ ] **ACTIVE_SPRINT.json primary_handoffs.p0_audit_handoff** corrected (remove broken OVERSIGHT_HIERARCHY reference or restore file)
4. [ ] **Dispatch capability registry** updated to 13 active agents (incl. N11/N12/N13)

**Post-debut (not blocking):**
- SESSION_REGISTRY.md generation via systemd/plugins (N1/E-8)
- Protocol layering map in AGENTS.md (E-5)

---

## 10. Hivemind Closeout

**Intent**: `decision` — N7 integration review complete. HIVEMIND_PROTOCOL v2.0 required. CI-2 not landed (debut blocker). Soul pipeline solid. E-8 correctly assigned to N1. 2 handoff inaccuracies flagged.

*⬡ OMEGA ⬡ LILITH ⬡ N7-CONTEXT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_n7_integration_review ⬡ 2026-08-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: N7-CONTEXT | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
