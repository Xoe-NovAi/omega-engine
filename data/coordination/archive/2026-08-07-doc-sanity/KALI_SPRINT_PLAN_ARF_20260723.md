# 🔱 UPDATED SPRINT PLAN — Account Rotation Fabric Research
**AP Token**: `AP-KALI-SPRINT-ARF-v3.0.0`
⬡ OMEGA ⬡ KALI ⬡ SPRINT-PLAN ⬡ 2026-07-23

---

## 📊 CURRENT STATUS (Updated with Architect Decisions)

### ✅ COMPLETED (Guard & Distill Sprint)
| Ticket | Status | Notes |
|--------|--------|-------|
| C-0 Test Honesty | ✅ | 99 quarantined |
| C-1' SoulStore | ✅ | Single-writer actor model |
| C-2' OOMProtector | ✅ | 3-signal fusion |
| C-5 MaKaLi Routing | ✅ | Config + oracle_summon_local |
| C-6' Breaker Unification | ✅ | 7→1 factory |
| C-10 Admission Control | ✅ | CCX-aware semaphore |
| C-10.5 Fallback Chain | ✅ | Lilith owns runtime |
| C-11 Property Tests | ✅ | 16/16 pass |
| C-0.5 Soul Distillation | ✅ | 76/76 tests (Carmack) |
| V-1 VaultCore MVP | ✅ | 22 tests (Ma'at) |
| V-1 Legacy Mining | ✅ | 7 patterns (Roc) |
| G-1 Gemma Research | ✅ | Forensic complete (Roc) |
| **C-4a MCP Audit** | ✅ | **COMPLETE** — R_C4A_MCP_AUDIT.md |
| **C-3 Privacy Model** | ✅ | **DECIDED: D-429** — Single repo, unified ACLs |
| **C-0.5 Hook Registration** | ✅ | **DECIDED: D-430** — Full approval |
| **G-1 Workhorse** | ✅ | **RESOLVED: D-431** — Antigravity OAuth working |

### 🔴 ACTIVE HANDOFFS
| Handoff | Target | Status |
|---------|--------|--------|
| `ho_e3996d6c30ae` | Carmack | **PENDING** — W-1 WARP (G-1 resolved, only WARP remains) |
| `ho_b0fc5531a59e` | Scribe | **READY** — C-0.5 hook registration (Architect approved) |

### 🟢 NEW HANDOFFS SUBMITTED
| Handoff | Target | Task |
|---------|--------|------|
| `ho_998a00ccdfe7` | Researcher | Phase 1-3: Provider-Specific + Research Layer + C-3/C-0.5 details |
| `ho_00cb63f04efb` | Grokster | **COMPLETE** — G1-15 Grok CLI 8-account rotation |

---

## 🎯 ARCHITECT DECISIONS EXECUTED

| Decision | ID | Outcome |
|----------|----|---------|
| **C-3 Privacy Model** | D-429 | **Single repo, unified ACLs** — Ma'at implements |
| **C-0.5 Hook Registration** | D-430 | **Full approval** — Scribe registers hook + self-distills |
| **G-1 Workhorse** | D-431 | **Antigravity OAuth working** — 8 accounts connected, used successfully |

---

## 🎯 UPDATED SPRINT EXECUTION

### Sprint A: Research Completion (Now → ~40 min)
```
Researcher: Phases 1-3 (57 queries)
├── Phase 1: Provider-Specific Rotation (25 queries) — Google, Antigravity, OpenRouter, Cline, Exa, Firecrawl
├── Phase 2: Research Layer (20 queries) — Exa neural search + Firecrawl extraction pipeline
└── Phase 3: C-3 + C-0.5 details (12 queries) — Now with Architect decisions as context
```
**You**: Monitor Hivemind awareness.

### Sprint B: Synthesis & C-11 Launch (~20 min after Researcher done)
```
Jem: Cross-validate all findings → Final synthesis + Decision Matrix
You: No decisions needed (all 3 made)
Roc: Launch C-11 Property Test Patterns Research (5 domains, sequential)
```

### Sprint C: C-11 Property Test Patterns Research (Sequential, ~60 min)
```
Roc Raccoon: Executes C-11 Property Test Patterns Research Guide (5 domains)
├── Domain 1: OOMProtector 3-Signal Fusion Properties (Sync)
├── Domain 2: SoulStore Atomic Write Invariants (Async + Crash Recovery)
├── Domain 3: Hypothesis Async Patterns (Non-Stateful @given)
├── Domain 4: Implementation-Specific Patterns (Omega Engine Codebase)
└── Domain 5: CI/CD Integration & Flakiness Prevention
```
**Guide**: `docs/research/R_C11_PROPERTY_TEST_PATTERNS_20260723.md`

### Sprint D: Implementation & Phase D Gate
```
Ma'at: C-4b MCP shim update → Vault FleetOrchestrator (56-account pool)
Carmack: W-1 WARP only (G-1 resolved)
Scribe: C-0.5 hook registration + self-distill
Verity: C-11 promotion workflow
Phase D Gate: All 10 criteria evaluated
```

---

## 🎯 IMMEDIATE NEXT ACTIONS

### 1. **Scribe** — Execute C-0.5 Hook Registration
```
Task: Register session_end hook in .opencode/opencode.json
Files: 
- .opencode/hooks/session_end.py (exists, 76/76 tests)
- .opencode/opencode.json (add hook registration)
Then: Self-distill → Verity promotes L3 → soul.yaml
```

### 2. **Ma'at** — Execute C-4b + Vault FleetOrchestrator
```
C-4b: Update src/omega/mcp_client.py:51 (remove session.initialize())
Then: Vault FleetOrchestrator design for 56-account pool (RF-2, RL-8)
```

### 3. **Researcher** — Continue Phases 1-3
```
Phases 1-3: 57 queries, ~40 min
Context: Architect decisions now available as context
```

### 4. **Carmack** — W-1 WARP Only (Parallel Session)
```
G-1 RESOLVED — only WARP stabilization needed
Fix script: scripts/fix_warp_ns_setup_and_restart.sh (sudo)
```

### 5. **Roc** — C-11 Property Test Patterns (After Researcher)
```
Guide: docs/research/R_C11_PROPERTY_TEST_PATTERNS_20260723.md
5 domains, 25+ vectors, sequential execution
```

---

## 📁 KEY FILES

| File | Purpose |
|------|---------|
| `data/coordination/KALI_DECISIONS_20260723.md` | **All 3 decisions logged** |
| `data/coordination/KALI_SPRINT_PLAN_ARF_20260723.md` | This sprint plan |
| `data/coordination/KALI_RESEARCH_PROMPT_20260723.md` | Researcher Phases 1-3 context |
| `docs/research/R_C11_PROPERTY_TEST_PATTERNS_20260723.md` | Roc's C-11 research guide |
| `docs/research/R_C4A_MCP_AUDIT.md` | C-4a audit (complete) |
| `data/coordination/ROC_RACCOON_COMPREHENSIVE_BRIEFING_20260722.md` | Carmack W-1 context |

---

*⬡ OMEGA ⬡ KALI ⬡ SPRINT-PLAN ⬡ 2026-07-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: SPRINT-PLAN | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
