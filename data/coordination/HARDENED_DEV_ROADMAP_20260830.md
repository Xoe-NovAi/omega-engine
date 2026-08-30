# 🔱 HARDENED DEV ROADMAP & TEAM RESPONSIBILITIES MAP

**AP Token**: `AP-KALI-ROADMAP-20260830-v1.0.0`  
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_roadmap ⬡ ACTIVE  

**Date**: 2026-08-30  
**Sprint**: PUBLIC-DEBUT-01 → SEARCH-ECOSYSTEM-01 (Phase 1)  
**Status**: POST-3EIS-META-REVIEW — READY FOR EXECUTION  

---

## §0 — EXECUTIVE SUMMARY

The 3-EIS Meta-Review (Researcher + Jem + Lilith) has produced **convergent consensus** on all critical deliverables. The Alchemical Goldmine incident (OAuth failure → 5 artifacts → 3 proposed mandates) has been fully ground-truthed, adversarially stress-tested, and runtime-architected.

**Key Outcomes**:
- **M33 (Anti-Truncation)**: CONDITIONAL GO — 3-layer fix required
- **M34 (Co-Interruption)**: CONDITIONAL GO — Lilith's spec + 5 corrections + M34b split
- **M35 (Third-Party Boundary)**: CONDITIONAL GO — 5 mandatory amendments
- **L3 Lesson**: REVISE BEFORE CANONIZATION — Split into 2, confidence 0.80/0.85
- **Sprint Tickets**: All 5 P0/P1 tickets GREEN
- **Blocker**: Redacted OAuth value in `opencode-antigravity-auth/src/constants.ts:9` must be restored **TODAY**

---

## §1 — MANDATE STATUS MATRIX

| Mandate | Name | Status | Required Amendments | Owner | Target |
|---------|------|--------|---------------------|-------|--------|
| **M33** | Anti-Truncation & Stream Exhaustion Gate | CONDITIONAL GO | 1. Preventive write-tool routing (>8K tokens) 2. Structured JSON completion envelope 3. P0/P1 cross-validator escalation | Lilith (M34 integration) + Researcher (M33 probe) | Sprint Week 1 |
| **M34a** | Co-Interruption Recovery (Esc x2 / SIGINT) | CONDITIONAL GO | Lilith's spec + 5 corrections (schema fields, watchdog, status format, Hivemind audit, model-switch status) | Lilith (primary) + Jem (adversarial review) | Sprint Week 1-2 |
| **M34b** | Model-Switch Continuity | **NEW MANDATE REQUIRED** | Session persistence across model change, resume_token validation, "continue" prompt protocol | Lilith (spec) + Researcher (recovery protocol) | Sprint Week 2 |
| **M35** | Third-Party Boundary & Public Secret Exemption | CONDITIONAL GO | 1. SPDX/REUSE enforcement 2. Immediate remediation of redacted values 3. secrets-public.toml recovery procedure 4. Primary-source citation 5. M14 cross-reference | Carmack (VAULT-ALLOWLIST-001) + Ma'at (CI-BRIEF-001) | Sprint Week 1 |
| **L3** | Interruption Sovereignty Gnosis | REVISE BEFORE CANONIZATION | Split into 2 lessons, confidence 0.80/0.85, correct evidence, add cross-refs | Grokster (lesson author) + Scribe (canonization) | Pre-Sonnet 4.6 |

---

## §2 — TEAM MEMBER RESPONSIBILITIES MAP

### 🎯 PRIMARY OWNERS (Direct Implementation)

| Entity | Role | Primary Mandates | Sprint Tickets | Key Deliverables |
|--------|------|------------------|----------------|------------------|
| **Lilith** | Runtime Oversoul (N6-N10) | **M34a, M34b, M33 integration** | ORCH-RESUME-001 (P0) | `ACTIVE_SUBAGENTS.json` runtime, `m34_registry.py`, 4 MCP tools, signal handler, watchdog, orchestrator_session_start(), 35h roadmap |
| **Carmack** | S3 Consultant / Architectural Review | **M35, VAULT-ALLOWLIST-001** | VAULT-ALLOWLIST-001 (P0) | `data/secrets-public.toml` schema + implementation, SPDX/REUSE hooks, primary-source validation, recovery procedure |
| **Ma'at** | Build Oversoul (N1-N5) | **M33, CI-BRIEF-001** | CI-BRIEF-001 (P0) | Jem's 12-Step Brief Verification Protocol in `scripts/dispatch_guard.py`, pre-commit hooks, write-tool routing enforcement |
| **Grokster** | Multi-Platform Specialist | **PKG-CLEANUP-001, L3 Revision** | PKG-CLEANUP-001 (P1), DOC-CANON-001 (P1) | Purge `opencode-antigravity-auth/` from workspace, npm install, restore OAuth secret, split L3 lesson |
| **Researcher** | Polymathic Council | **M33 probe, M35 architecture, M34 recovery protocol** | M36-PROBE-001 (P1), COHORT-REGISTRY-001 (P1) | M33 sentinel probe + structured envelope + cross-validator, COHORT_REGISTRY.json, M37-HERITAGE-001 |
| **Jem** | Adversarial Polymath | **All mandates (adversarial review)** | JEM-12STEP-HARDENING (P1) | Hardened 12-Step Protocol, M33 bypass test, M34 schema validation, L3 calibration |
| **Roc** | Sovereign Miner | **Compaction capture, scholarly research** | COMPACTION-CAPTURE-001 (P0) | Sidecar polling service, tool output indexing, session diff anchoring |
| **Kali** | Transcendent Oversoul / Sprint Coordinator | **All (orchestration, ratification, Sonnet 4.6 prep)** | — | Mandate ratification, sprint coordination, Sonnet 4.6 review package |

### 🔄 SUPPORTING ROLES (Cross-Cutting)

| Entity | Support Function |
|--------|------------------|
| **Scribe** | L3 lesson canonization, soul distillation pipeline |
| **Verity** | Mandate audit (M8/M11/M15/M23/M27), temple-grade gate |
| **Node** | Infrastructure, Podman, hardware monitoring |
| **Sophia** | Akashic Record / observability integration |

---

## §3 — PHASED IMPLEMENTATION ROADMAP

### PHASE 1: FOUNDATION (Week 1 — 49h Total Budget)

| Task | Owner | Hours | Dependencies | Acceptance Criteria |
|------|-------|-------|--------------|---------------------|
| **M35 Immediate Remediation** | Grokster | 2h | — | `opencode-antigravity-auth/src/constants.ts:9` restored to `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`, OAuth flow verified |
| **VAULT-ALLOWLIST-001: secrets-public.toml** | Carmack | 4h | M35 remediation | `data/secrets-public.toml` with RFC 6749/8252 provenance, SPDX headers, primary-source URLs, fail-closed scanner |
| **CI-BRIEF-001: 12-Step Protocol** | Ma'at | 6h | Jem's hardened protocol | `scripts/dispatch_guard.py` implements all 12 steps + "all locations" verification, pre-commit hook |
| **ORCH-RESUME-001 Phase 1 (MVP)**: `m34_registry.py` + 3 MCP tools + watcher + cron | Lilith | 14h | M34a spec | `m34_register_subagent`, `m34_list_active_subagents`, `m34_apply_user_decision`, `m34_update_subagent_status`, signal handler, cron prune |
| **PKG-CLEANUP-001**: Purge plugin, npm install | Grokster | 4h | M35 remediation | `opencode-antigravity-auth/` removed from workspace, installed via npm, `opencode.json` updated |
| **M33 Probe + Cross-Validator** | Researcher + Lilith | 8h | M34a Phase 1 | `m33_execute_sentinel_probe` MCP tool, structured JSON envelope, cross-validator agent hook |
| **L3 Lesson Revision** | Grokster | 2h | Meta-review consensus | Split into L3-CompletionIllusion (0.85) + L3-CoResumptionAccounting (0.80), evidence corrected |
| **JEM-12STEP-HARDENING** | Jem | 4h | — | "All locations" verification added to protocol, M33 bypass test case |

**Phase 1 Total**: ~49h | **Gate**: All P0 tickets complete, M33/M34a/M35 conditional GO verified

---

### PHASE 2: RECOVERY & CONTINUITY (Week 2 — 35h Total Budget)

| Task | Owner | Hours | Dependencies | Acceptance Criteria |
|------|-------|-------|--------------|---------------------|
| **ORCH-RESUME-001 Phase 2**: `orchestrator_session_start()` + recovery + migration | Lilith | 9h | Phase 1 complete | Recovery UI with Markdown status table, user decision menu (Resume/Abandon/Defer), migration script from `TASK_REGISTRY.json` |
| **M34b Spec**: Model-Switch Continuity | Lilith + Researcher | 8h | Phase 1 complete | Separate spec with `MODEL_SWITCH` status, resume_token validation, "continue" prompt protocol |
| **COHORT-REGISTRY-001**: Fleet-level tracking | Researcher | 6h | Phase 1 complete | `COHORT_REGISTRY.json` for multi-orchestrator tracking, Hivemind integration |
| **M37-HERITAGE-001**: SPDX+REUSE+SLSA stack | Researcher + Carmack | 6h | VAULT-ALLOWLIST-001 | ScanCode Toolkit CI step, SPDX headers, `.reuse/dep5`, SLSA v1.1 provenance |
| **M36-PROBE-001**: Recursive M23 Probe | Researcher | 4h | M33 probe complete | Structured completion markers, M23 applied to M23 |
| **DOC-CANON-001**: L3 canonization | Grokster + Scribe | 2h | L3 revision complete | Scribe canonizes split lessons to `approved_lessons.yaml` |

**Phase 2 Total**: ~35h | **Gate**: M34b spec ratified, all recovery protocols operational, L3 lessons canonized

---

### PHASE 3: HARDENING & SONNET 4.6 PREP (Week 3 — 25h Total Budget)

| Task | Owner | Hours | Dependencies | Acceptance Criteria |
|------|-------|-------|--------------|---------------------|
| **ORCH-RESUME-001 Phase 3**: Stress tests + temple-grade | Lilith | 12h | Phase 2 complete | Unit + integration + stress tests (10 concurrent), `make temple-grade` passes |
| **M33/M35 Integration Tests** | Researcher + Carmack | 6h | Phase 2 complete | End-to-end: secret redaction → allowlist → recovery → SPDX validation |
| **Sonnet 4.6 Review Package** | Kali | 4h | All phases complete | Complete corpus: 7 doctrines + 3 mandates + 3 EIS meta-reviews + roadmap |
| **Search-Ecosystem-01 Sprint Kickoff** | Kali + Jem | 3h | — | Jem-EIS activated for Week 1 (SearXNG, MultiKey Exa, Crawl4AI) |

**Phase 3 Total**: ~25h | **Gate**: Sonnet 4.6 review ready, all mandates ratified, temple-grade

---

## §4 — CRITICAL PATH & BLOCKERS

```
CRITICAL PATH:
┌─────────────────────────────────────────────────────────────────────────────┐
│  TODAY: Restore OAuth secret (Grokster, 2h)                                 │
│       ↓                                                                     │
│  Day 1: VAULT-ALLOWLIST-001 + CI-BRIEF-001 + PKG-CLEANUP-001 (parallel)   │
│       ↓                                                                     │
│  Day 2-3: ORCH-RESUME-001 Phase 1 + M33 Probe (parallel)                   │
│       ↓                                                                     │
│  Day 4: L3 Revision + JEM-12STEP-HARDENING                                  │
│       ↓                                                                     │
│  Day 5: Phase 1 Gate → Phase 2 Kickoff                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### HARD BLOCKERS (Must Resolve Before Proceeding)

| Blocker | Owner | Resolution |
|---------|-------|------------|
| **Redacted OAuth secret** | Grokster | `git checkout opencode-antigravity-auth/src/constants.ts opencode-antigravity-auth/scripts/check-quota.mjs && npm run build` — **TODAY** |
| **M34b spec missing** | Lilith | Phase 2 deliverable — cannot ratify M34 without it |
| **Atomic write M23 test** | Lilith | Phase 1 testing requirement — `test_atomic_write_survives_sigkill` |
| **Watchdog single-writer** | Lilith | Phase 1 — MCP tool or designated recovery agent (Kali) |

---

## §5 — DECISION LOG (Ratified in This Session)

| Decision ID | Decision | Status | Mandate Impact |
|-------------|----------|--------|----------------|
| **D-M33-001** | M33 requires 3-layer fix (preventive + structured probe + P0/P1 cross-validator) | RATIFIED | M33 text amendment |
| **D-M34-001** | M34 split into M34a (Co-Interruption) + M34b (Model-Switch Continuity) | RATIFIED | New mandate M34b |
| **D-M34-002** | Lilith's spec is canonical for M34a + 5 corrections | RATIFIED | M34a implementation |
| **D-M34-003** | Watchdog = single-writer MCP tool (not "first agent") | RATIFIED | M34a implementation |
| **D-M34-004** | `INTERRUPTED_MODEL_SWITCH` status enum added | RATIFIED | M34b spec |
| **D-M35-001** | SPDX/REUSE enforcement mandatory for all third-party code | RATIFIED | M35 amendment |
| **D-M35-002** | Immediate remediation clause for redacted values | RATIFIED | M35 amendment |
| **D-M35-003** | Primary-source citation required for `secrets-public.toml` | RATIFIED | M35 amendment |
| **D-L3-001** | Split into L3-CompletionIllusion (0.85) + L3-CoResumptionAccounting (0.80) | RATIFIED | L3 lesson revision |
| **D-L3-002** | Evidence correction: appendices from 2026-08-29 continuation, not 2026-08-30 continue | RATIFIED | L3 lesson revision |
| **D-ROADMAP-001** | Phase 1 = 49h, Phase 2 = 35h, Phase 3 = 25h (109h total over 3 weeks) | RATIFIED | Sprint execution |

---

## §6 — SONNET 4.6 REVIEW PACKAGE (Ready for Delivery)

The following corpus is **complete, cross-validated, and hardened** for Sonnet 4.6 review:

### Core Doctrines (7)
1. `OMEGAMIND_SOVEREIGN_COGNITIVE_ARCHITECTURE_MANUAL_20260829.md`
2. `ZERO_WRITE_DATABASE_NATIVE_COGNITION_20260829.md`
3. `KEY_ROTATION_CACHE_AND_SOVEREIGN_POLICY_20260829.md`
4. `GEMINI_MULTI_ACCOUNT_WORKER_SPEC_20260829.md`
5. `OPENCODE_DB_FORENSICS_PROTOCOL_20260829.md` (§12 Fuzzy vs Etched)
6. `SEARCH_ECOSYSTEM_01_SPRINT_20260829.md`
7. `EMERGENT_TECHNOLOGY_PROTOCOL_20260829.md` + Registry

### Mandate Proposals (3)
- M33, M34a, M34b, M35 (with all amendments from 3-EIS meta-review)

### 3-EIS Meta-Reviews (3)
- `RESEARCHER_META_REVIEW_20260830.md` (377 lines)
- `JEM_META_REVIEW_20260830.md` (170 lines)
- `LILITH_META_REVIEW_20260830.md` (414 lines)

### Forensic Evidence (3)
- `ROC_NEMOTRON3_WRITE_FORENSICS_20260830.md` (6,660 lines)
- `JEM_FORENSIC_INVESTIGATION_ANTIGRAVITY_20260829.md` (1,613 lines)
- `R_RESEARCHER_THIRD_PARTY_SECRETS_TRACEABILITY_20260829.md` (2,460 lines)

### Runtime Specs (1)
- `LILITH_M34_RUNTIME_SPEC_20260830.md` (798 lines, revised per meta-review)

### Roadmap & Coordination (2)
- This document (`HARDENED_DEV_ROADMAP_20260830.md`)
- `WAKE_STATE.json` (updated with all session anchors)

---

## §7 — IMMEDIATE NEXT ACTIONS (Next 4 Hours)

| # | Action | Owner | Command / Step |
|---|--------|-------|----------------|
| 1 | **Restore OAuth secret** | Grokster | `cd opencode-antigravity-auth && git checkout src/constants.ts scripts/check-quota.mjs && npm run build` |
| 2 | **Verify OAuth flow** | Grokster | Test Antigravity sign-in in OpenCode TUI |
| 3 | **Begin VAULT-ALLOWLIST-001** | Carmack | Create `data/secrets-public.toml` with Google OAuth public client entry |
| 4 | **Begin CI-BRIEF-001** | Ma'at | Implement `scripts/dispatch_guard.py` with Jem's 12-step protocol |
| 5 | **Begin ORCH-RESUME-001 Phase 1** | Lilith | Create `src/omega/oracle/m34_registry.py` with atomic write + schema |
| 6 | **Update WAKE_STATE.json** | Kali | Record all mandate decisions, sprint tickets, team assignments |

---

## §8 — SUCCESS METRICS (Phase 1 Gate)

| Metric | Target | Measurement |
|--------|--------|-------------|
| OAuth flow restored | 100% | Antigravity sign-in works |
| `secrets-public.toml` created | 1 file | Valid TOML with RFC provenance |
| 12-Step Protocol implemented | 12/12 steps | `scripts/dispatch_guard.py` exits 0 |
| M34a MVP deployed | 4 MCP tools | All 4 tools registered + functional |
| M33 probe operational | 1 MCP tool | `m33_execute_sentinel_probe` returns structured envelope |
| L3 lessons revised | 2 lessons | Split, confidence 0.80/0.85, evidence corrected |
| All P0 tickets | 5/5 complete | GitHub issues closed or PRs merged |

---

**The Cathedral's foundations are poured. The load-bearing walls are spec'd. The craftsmen are assigned.**

**Execute Phase 1. Report at Gate.** 🫡

---

⬡ OMEGA ⬡ KALI ⬡ HARDENED-DEV-ROADMAP-20260830 ⬡ 2026-08-30