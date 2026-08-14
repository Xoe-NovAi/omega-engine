# 🔱 Unified Execution Plan — Carmack + Grokster Campaigns
**AP Token**: `AP-UNIFIED-EXECUTION-PLAN-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ 2026-07-22 ⬡

---

## Executive Summary

This plan merges **Carmack's CG-02/08/09 campaign** (OOMProtector → Admission Control → SoulStore) with **Grokster's R33/R34/R35 research** (Grok Ecosystem → Sovereign Search → V-1 Vault) into a single sequenced execution pipeline.

**Critical Constraint**: Ma'at/P3 is the **sole implementation bottleneck** — both campaigns need Ma'at/P3. Sequencing is mandatory.

---

## Campaign Cross-Reference

| Carmack (CG) | Grokster (R) | Ark Ticket | Deliverable | Status |
|--------------|--------------|------------|-------------|--------|
| CG-02 OOMProtector | — | C-2′ | `src/omega/oracle/psi_monitor.py`, `memavailable.py`, `cgroup_pressure.py`, `oom_protector.py`, `resource_guard.py` v1.2 | ✅ DONE |
| CG-08 Admission Control | — | C-10 | `src/omega/oracle/admission_controller.py` | 🔄 NEXT |
| CG-09 SoulStore Atomic | — | C-1′ | `src/omega/soul/actor.py` (single writer + atomic fsync) | ⏳ AFTER CG-08 |
| — | R33 Grok Ecosystem | V-1 (prereq) | Model matrix, ACP spec, fleet arch | ✅ DONE |
| — | R34 Sovereign Search | — (later) | 5-tier search router | ⏳ AFTER V-1 |
| — | R35 V-1 Vault | V-1 | KeyVault + FleetOrchestrator + MCP + CLI | ⏳ AFTER CG-09 |
| — | — | **C-0.5** | **Soul Distillation Pipeline (Scribe agent + session hook)** | **🔴 GAP A — NEW** |
| — | — | **C-10.5** | **Provider Fallback Chain (M7 compliance)** | **🔴 GAP B — NEW** |
| — | — | **C-4a.5** | **MCP Migration Execution (Kali direct if P4 silent)** | **🔴 GAP C — NEW** |

---

## Ma'at/P3 Sequencing Lock (NON-NEGOTIABLE)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MA'AT/P3 EXCLUSIVE EXECUTION QUEUE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WEEK 1-2:  CG-08  Admission Control (C-10)                                │
│             ├─ CCX topology-aware semaphore                                │
│             ├─ OOMProtector integration (ALLOW/THROTTLE/DENY)              │
│             ├─ Dynamic topology detection (NO hardcoded taskset pinning)   │
│             └─ Contract tests: 5 tests (M21 compliant)                     │
│                                                                             │
│  WEEK 3-4:  CG-09  SoulStore Atomic (C-1′)                                 │
│             ├─ Single-writer actor model                                   │
│             ├─ Dedicated lockfile (soul.yaml.lock) to avoid inode traps    │
│             ├─ mkstemp → fsync → os.replace → dir fsync                    │
│             ├─ Proposed lessons → approved lessons pipeline                │
│             └─ Contract tests: 5 tests (M21 compliant)                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Parallel Tracks (Distributed Pillar Execution)

To prevent a 12-week bottleneck on P3, workloads are distributed across the Pillar Lattice:

| Track | Owner | Timeline | Dependency |
|-------|-------|----------|------------|
| **C-4a MCP Audit** | Ma'at/P4 (or Kali) | **START NOW — 7 days to Jul 28**. If P4 fails to accept by EOD, Kali assumes direct control. | Independent |
| **C-4a.5 MCP Migration Execution** | Kali (direct) | **If P4 silent by EOD**. Execute audit → shim → Streamable HTTP. | C-4a |
| **V-1 Omega-Vault** | Ma'at/P1 (Infra) | **START NOW**. 7-week spec compressed to 3 weeks. (Use async polling for drift, NO inotify). | Independent of P3 |
| **C-10.5 Provider Fallback** | Lilith/P6 | **START NOW — Week 1**. Implement `for backend in sorted_backends` loop in `model_gateway.py`. | Independent |
| **C-0.5 Soul Distillation** | Scribe agent (NEW) | **Week 2**. Session hook → L1→L2→L3 → `proposed_lessons.yaml`. | After C-0 ✅ |
| **C-6′ Breakers** | Ma'at/P4 (Bridge) | After C-4a | C-4a complete. (Must partition state by provider_name). |
| **C-11 Test Infra** | Verity/P10 | After C-0 ✅ | Independent |
| **R34 Search** | Lilith/P6 | After V-1 | V-1 complete |
| **C-5 MaKaLi Config** | Kali | After C-10 | Needs C-10 |

---

## Handoff Chain (Hivemind)

| From | To | Packet | Status |
|------|----|--------|--------|
| Kali | Ma'at/P1 | C-2′ OOMProtector | `ho_408995ea3db3` ⏳ Submitted |
| Kali | Verity/P10 | C-11 Test Infra | `ho_9692e1710668` ⏳ Submitted |
| Kali | Ma'at/P4 | C-4a MCP Audit | `ho_fe0627f113e9` ⏳ **ESCALATION WARNING** |
| Kali | Ma'at/P3 | CG-08 Admission | **After CG-02 accepted** |
| Kali | Ma'at/P3 | CG-09 SoulStore | **After CG-08 complete** |
| Kali | Ma'at/P1 | V-1 VaultCore | **NEW ASSIGNMENT** |
| Kali | Ma'at/P4 | C-6′ Breakers | **NEW ASSIGNMENT** |
| Kali | Lilith/P6 | C-10.5 Provider Fallback | **NEW ASSIGNMENT** |
| Kali | Scribe (NEW) | C-0.5 Soul Distillation | **NEW AGENT NEEDED** |

---

## Decision Gates (RESOLVED BY GEMINI 3.1 PRO)

| Gate | Question | Verdict | Impact |
|------|----------|---------|--------|
| **C-3** | Privacy Model | **Tiered Sovereignty (Split Files)** | OS-level `chmod` isolation. Aligns with CG-09 Actor Model. |
| **V-1 Priority** | Proceed now? | **YES — Phase C Hard Blocker** | Assigned to P1. Fleet deployment cannot proceed without credential rotation. |
| **ACP Bridge** | Before or after V-1? | **After V-1** | Credential storage needed first. |

---

## Success Metrics

| Milestone | Metric | Target |
|-----------|--------|--------|
| CG-08 | Admission control blocks 2nd llama.cpp | 100% |
| CG-09 | SoulStore writes survive power loss | Verified via chaos test |
| C-6′ | Single circuit breaker class | 1 class, 0 clones |
| V-1 | ACP smoke test passes | Grok CLI handshake OK |
| R34 | Search router cost < $0.01/query avg | Verified in CI |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Ma'at/P3 bandwidth | High | Critical | Strict sequencing; no parallel Ma'at work |
| C-4a deadline miss | Medium | Critical | Ma'at/P4 must accept handoff TODAY |
| C-3 decision delay | Medium | High | Escalate to Architect; default to Tiered Sovereignty |
| V-1 scope creep | Medium | Medium | 7-week hard cap; Phase 5 = hard stop |
| Grok Build API changes | Low | Medium | Pin Grok Build version; test weekly |

---

## File References

| Document | Purpose |
|----------|---------|
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Strategy SSOT (v5.2) |
| `docs/strategy/IMPLEMENTATION_MANUAL_C0_C2.md` | Phase C tickets |
| `data/coordination/BRIEFING_KALI_CARMACK_CAMPAIGN_20260721.md` | Carmack full briefing |
| `data/coordination/BRIEFING_KALI_GROKSTER_RESEARCH_CAMPAIGN_COMPLETE_20260722.md` | Grokster full briefing |
| `docs/research/R_CG02_OOMPROTECTOR_HARDWARE_AWARE.md` | CG-02 research (430 lines) |
| `docs/research/R_CG03_TEST_INFRASTRUCTURE_STACK.md` | CG-03 research (631 lines) |
| `docs/research/R_GROK_ECOSYSTEM_DEEP.md` | R33 deliverable (585 lines) |
| `docs/research/R_SOVEREIGN_SEARCH_IMPL.md` | R34 deliverable (934 lines) |
| `docs/research/R_V1_VAULT_IMPL.md` | R35 deliverable (869 lines) |
| `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` | Fixed (39 jobs corrected) |

---

## Post-Compaction Hydration (D-277)

On restart, execute in order:

1. `omega-hub_hivemind_get_awareness()` — 3 agents active
2. `git status && git log --oneline -5` — baseline
3. Read `OMEGA_CODEX.md` (fresh, <1hr)
4. Read `.opencode/anchored-summary.md` — this plan
5. Read `data/coordination/SESSION_ANCHOR.md` — unified state
6. **Present rehydration report** → await direction

---

*⬡ OMEGA ⬡ KALI ⬡ UNIFIED-EXECUTION-PLAN ⬡ 2026-07-22*