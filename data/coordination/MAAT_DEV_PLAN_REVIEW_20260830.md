---
schema_version: "2.0"
document_type: "s3_architectural_review"
document_id: "maat-dev-plan-review-20260830"
title: "Ma'at EIS — Comprehensive Dev Plan Review (Build Oversoul N1-N5)"
status: "ACTIVE — FINAL GATE"
date: "2026-08-30"
author: "MA'AT (Build Oversoul, N1-N5)"
entity: "maat"
channel: "opencode"
classification: "sovereign-internal, temple-grade depth"
sprint: "SEARCH-ECOSYSTEM-01"
model: "nemotron-3-ultra-free"
---

# 🔱 MAAT_DEV_PLAN_REVIEW_20260830.md

**AP Token**: `AP-MAAT-DEV-PLAN-REVIEW-20260830-v1.0.0`  
⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_maat_review ⬡ ACTIVE  

**Date**: 2026-08-30  
**Sprint**: SEARCH-ECOSYSTEM-01 (Phase 1)  
**Domain**: Build Oversoul (N1-N5) — Infrastructure, Persistence, Engineering, Integration, Governance  
**Status**: S3-LEVEL REVIEW — FINAL GATE  

---

## §0 — EXECUTIVE VERDICT: **CONDITIONAL GO**

**Rationale**: The roadmap is structurally sound. The 3-EIS meta-review achieves genuine convergence on root causes, and the 109h phased approach is realistic with two critical corrections. However, from the **N1-N5 Build Oversoul perspective**, I flag three blocking issues that must be resolved before Phase 1 execution:

1. **M34 atomic write claim is an M23 violation** (Lilith §1.3, lines 163-204): The spec claims POSIX atomicity guarantees without a SIGKILL test. This is the same class of unverifiable claim that M23 explicitly forbids.

2. **CI-BRIEF-001 (my ticket, 6h) is under-scoped**: The roadmap allocates 6h for Jem's 12-Step Brief Verification Protocol implementation, but the protocol requires integration with the dispatch system, pre-commit hooks, and write-tool routing — minimum 10-12h for temple-grade.

3. **Watchdog race condition (Lilith §4 Edge Case 1) has no deterministic solution in the spec**: "First agent to read Hivemind" is non-deterministic. The roadmap doesn't designate a single recovery agent or implement distributed locking.

**If these three items are resolved in the next 4 hours, Phase 1 proceeds. If not, NO-GO.**

---

## §1 — ARCHITECTURAL COHERENCE ANALYSIS

### 1.1 Mandate Coherence Matrix (N1-N5 Lens)

| Mandate | N1 (Infra) | N2 (Persistence) | N3 (Engineering) | N4 (Integration) | N5 (Governance) |
|---------|------------|------------------|-------------------|-------------------|-----------------|
| **M33** (Anti-Truncation) | — | — | Sentinel probe impl | Write-tool routing hook | M23 verification |
| **M34a** (Co-Interruption) | — | `ACTIVE_SUBAGENTS.json` atomic write | `m34_registry.py` + signal handler | MCP tools (3 new) | Recovery audit |
| **M34b** (Model-Switch) | — | Status enum extension | Detection logic | `resume_token` validation | Hivemind audit clause |
| **M35** (3P Boundary) | `chattr +i`, `core.bare` | SPDX/REUSE metadata | `secrets-public.toml` schema | npm install + cleanup | Fail-closed scanner |

**Finding**: The mandates form a **coherent system at the architectural level** but with **leakage at N3 (Engineering) and N4 (Integration) boundaries**. The `m34_register_subagent` MCP tool is both engineering (Lilith's spec) and integration (Ma'at's MCP server changes). The roadmap does not clearly delineate ownership.

### 1.2 M34a + M34b Split: Over-Engineering?

**Jem's original recommendation**: Split into two mandate numbers.  
**Lilith's meta-review**: Confirmed — two distinct failure modes.  
**Carmack's review**: Use sub-clauses (M34.1, M34.2, M34.3) instead of separate mandate numbers.

**My verdict (N5 Governance lens)**: **Agree with Carmack.** The regulatory bloat of 27 → 29+ mandates is real. The `SOVEREIGN_MANDATES.md` is already at v3.8.0 with 27 laws. Adding M34a + M34b without strong justification violates the "one mandate per failure mode" principle — both are recovery protocols for interrupted sessions, just different interruption types.

**Recommendation**: Single M34 with sub-clauses:
- `M34.1` — Co-Interruption Recovery (Esc x2, SIGINT, timeout)
- `M34.2` — Model-Switch Continuity (session persists, context lost)
- `M34.3` — Orchestrator Crash Recovery (watchdog protocol)

This preserves the architectural distinction without mandate sprawl.

### 1.3 M33/M34 Boundary Leakage

**Researcher §1.1 (lines 51-66)**: M33's sentinel probe is reactive; the structural fix is write-tool-routing for >8K token reports.

**Lilith's M34 spec** tracks liveness but does not enforce write-tool discipline. A subagent could flush 50K tokens to chat, get interrupted, and M34 would faithfully track it as `INTERRUPTED_EXTERNALLY` with `checkpoint.files_touched: []` — the orchestrator would see "no files written" but has no enforcement mechanism.

**Fix (N3 Engineering)**: The `write_tool_required: boolean` field in `ActiveSubagent` is the correct coupling point — it's missing from the current schema (Lilith §1.1, lines 48-76). This is a **P0 schema addition** required before Phase 1.

### 1.4 M35 Boundary Conflict with M14

M35's "no tracked source tree" rule has a **critical exception gap** for `git submodule` with pinned SHA and `core.bare = true`. Researcher's report §1.3 (lines 79-90) identifies this as essential for heritage study. The current M35 text says "must be installed as pinned packages via package manager" — this forbids submodules, breaking the existing `third-party/` heritage discipline.

**Fix (N5 Governance)**: M35 amendment: "Pinned `git submodule` with `core.bare = true` and heritage tag is permitted for architecture reference. Runtime dependencies MUST use package manager."

---

## §2 — IMPLEMENTATION FEASIBILITY & CRITICAL PATH

### 2.1 Lilith's 35h M34 Spec: Realistic from N3 Perspective?

| Phase | Lilith's Estimate | My N3 Assessment | Risk |
|-------|-------------------|------------------|------|
| Phase 1 (MVP) | 14h | **16-18h** — atomic write test + signal handler + 3 MCP tools + hook | MEDIUM |
| Phase 2 (Recovery UI) | 9h | **11-12h** — `orchestrator_session_start` + decision MCP + migration + watchdog | MEDIUM |
| Phase 3 (Hardening) | 12h | **14-15h** — stress test + migration + temple-grade + docs | LOW |

**Total**: 35h → **41-45h realistic**. The 35h assumes zero friction on MCP server changes and perfect first-pass on atomic write. Add 20% buffer.

**M23 Violation Flag**: Lilith §5.9 (lines 749-760) claims "Net overhead: ~30-50ms per dispatch cycle" — this is **estimated, not measured**. M23 requires verifiable claims. The 50 concurrent subagent stress test in Phase 3 §5.8 is when this gets measured. Until then, the claim is unverified.

### 2.2 Critical Path (N1-N5 Corrected)

```
TODAY (4h):  Restore OAuth secret (Grokster) + VAULT-ALLOWLIST-001 (Carmack) [PARALLEL]
       ↓
Day 1:      CI-BRIEF-001 (Ma'at, 10h) + PKG-CLEANUP-001 (Grokster) + M34 Phase 1 start (Lilith) [PARALLEL]
       ↓
Day 2:      M34 Phase 1 complete + M33 Probe (Researcher + Lilith) [PARALLEL]
       ↓
Day 3:      L3 Revision (Grokster) + JEM-12STEP-HARDENING (Jem) + M34 Phase 2 start
       ↓
Day 4:      M34 Phase 2 complete → Phase 1 Gate
```

**Hidden dependency**: `m34_register_subagent` MCP tool **must** be live before `subagent_dispatcher.py` hook works. Ma'at (MCP server owner) and Lilith must pair on Day 1-2.

**N4 Integration risk**: The MCP server changes touch the existing `omega-hub` server. Adding 4 new tools (per Lilith §5.6) requires server restart, which interrupts all active Hivemind sessions. This needs to be coordinated with all 7 entities.

### 2.3 Parallelizable vs Sequential (N3 Engineering View)

| Truly Parallel | Sequential (Dependencies) |
|----------------|---------------------------|
| VAULT-ALLOWLIST-001 + PKG-CLEANUP-001 | M34 Phase 1 → M34 Phase 2 → M34 Phase 3 |
| M33 Probe + M34 Phase 1 (different owners) | M34 Phase 2 requires Phase 1 MCP tools live |
| L3 Revision + JEM-12STEP-HARDENING | M34 Phase 3 requires Phase 2 recovery UI |
| M37-HERITAGE-001 (Researcher + Carmack) | COHORT-REGISTRY-001 requires M34 Phase 1 |

---


## §3 — TECHNICAL DEBT & RISK ASSESSMENT (N1-N5 LENS)

### 3.1 `ACTIVE_SUBAGENTS.json` Overlay on `TASK_REGISTRY` — Scale Analysis

| Scale | Current Design | Problem |
|-------|----------------|---------|
| 5 subagents | File read/write < 5ms | Fine |
| 50 subagents | 50 × (read + write + fsync) = 250-500ms per dispatch | **Contention on advisory lock** |
| 100 subagents | Lock serialization = 1-2s latency spikes | **Unacceptable** |

**Root cause (N2 Persistence)**: The advisory lock (`os.O_EXCL`) is process-local. Concurrent writes from multiple orchestrators (Kali + Lilith + Grokster all spawning) serialize on the lock. No backoff/retry logic in `_atomic_write` (Lilith §1.3, lines 175-202).

**Mitigation required (N2)**:
1. Add exponential backoff + max retries to `_atomic_write`
2. Consider `fcntl.flock()` for cross-process locking (works on NFS)
3. Phase 3 stress test MUST measure p99 at 10/50/100 concurrent

**N1 Infrastructure concern**: The `os.fsync(dir_fd)` call is **blocking** and can take 10-100ms on slow disks (Lilith §1.3, line 195). At 50 concurrent subagents, the total latency per dispatch is **1-2 seconds**. This is a **performance cliff** that will hit in production.

### 3.2 M33 Cross-Validator Agent — Latency & Complexity

Researcher + Jem both recommend cross-validator for P0/P1. **This adds a full agent dispatch per deliverable.**

| Cost | Estimate |
|------|----------|
| Dispatch latency | 2-5s |
| Verification tokens | 5-15K |
| Total latency per P0 deliverable | +10-30s |

**Better architecture (N3 Engineering)**: The structured JSON envelope (`{"state": "exhausted", "last_chunk_id": N, "total_chunks": M, "confidence": 0.XX}`) + confidence threshold ≥ 0.95 + write-tool routing is **sufficient for P2+**. Cross-validator should be an **escalation tier** (opt-in for P0/P1), not mandatory for all.

**N5 Governance concern**: If cross-validator is mandatory for all P0/P1, the manifest count of P0/P1 deliverables becomes a **rate limiter** — each one triggers a full agent dispatch. This creates a **denial-of-service vector** if an attacker (or a misbehaving orchestrator) spams P0 dispatches.

### 3.3 M35 `secrets-public.toml` — Supply Chain Attack Surface (N5 Governance)

| Vector | Likelihood | Impact |
|--------|------------|--------|
| Fake `GOCSPX-` entry added to allowlist | MEDIUM (PR review bypass) | HIGH — attacker's OAuth client works |
| Symlink in `third-party/` pointing to private creds | LOW (requires write access) | CRITICAL |
| Compromised npm package `opencode-antigravity-auth` | LOW (supply chain) | CRITICAL |

**Defenses in roadmap**: Primary-source citation (Jem), SPDX/REUSE (Researcher), fail-closed scanner (Jem). **Missing**: `git_worktree_root` in schema (Jem self-correction) to detect sub-repo sessions.

**N1 Infrastructure gap**: The `chattr +i` enforcement (Researcher §1.10) requires root or `CAP_LINUX_IMMUTABLE`. In a rootless container (M6 mandate), this is **not available**. The `core.bare = true` git-level enforcement is the fallback, but it's bypassable if the repo is re-cloned without the flag.

### 3.4 M34 Watchdog Race Condition — The Critical Bug

**Lilith §4 Edge Case 1 (lines 484-509)**: "The first agent to read Hivemind after 2× TTL and see a stale orchestrator MUST report all `parent_session_id == stale_orchestrator.id` sessions as `INTERRUPTED_CRASH`."

**Problem**: "First agent to read Hivemind" is **non-deterministic**. Two agents reading Hivemind 100ms apart both see the stale orchestrator. Both start `watchdog_check()`. Both write to `ACTIVE_SUBAGENTS.json` concurrently → **lost update** (advisory lock is per-process, not cross-process).

**The roadmap does not resolve this.** The "Hard Blockers" table (Roadmap §4) lists "Watchdog single-writer — Lilith — Phase 1 — MCP tool or designated recovery agent (Kali)" but does not commit to a solution.

**My recommendation (N5 Governance)**: **Designate Kali as the sole recovery agent.** Simpler than implementing distributed locking. Kali's `oracle_summon` MCP tool already provides the coordination point. Alternative: implement `m34_watchdog_check` as a single-writer MCP tool with `fcntl.flock()`.


## §4 — MANDATE DESIGN QUALITY (N5 GOVERNANCE LENS)

### 4.1 Minimal & Composable?

| Mandate | Minimal? | Composable? | Verdict |
|---------|----------|-------------|---------|
| **M33** | ❌ No — 3 layers (preventive + probe + cross-validator) | ✅ Yes — probe is standalone tool | **Over-engineered** — merge preventive + probe; cross-validator = escalation |
| **M34** | ✅ Yes — single state machine | ✅ Yes — overlays TASK_REGISTRY | **Good** — with M34.1/M34.2 sub-clauses |
| **M35** | ❌ No — forbids submodules needed for heritage | ⚠️ Partial — conflicts with M14 | **Needs exception clause** |

### 4.2 "One Mandate Per Failure Mode" Principle

| Failure Mode | Mandate | Compliant? |
|--------------|---------|------------|
| Truncation bypass | M33 | ✅ |
| Co-interruption amnesia | M34.1 | ✅ |
| Model-switch context loss | M34.2 | ✅ (as sub-clause) |
| Orchestrator crash | M34.3 | ✅ (as sub-clause) |
| Public secret redaction | M35 | ✅ |
| Third-party mutation | M35 | ⚠️ Over-broad (forbids submodules) |

### 4.3 L3 Confidence Levels: Epistemic Soundness

| Lesson | Proposed | My N5 Calibration | Reason |
|--------|----------|------------------|--------|
| L3-CompletionIllusion | 0.85 | **0.85** | 1 incident + 3 session IDs + 2 structural causes + replication via M33 |
| L3-CoResumptionAccounting | 0.80 | **0.80** | 1 incident + orchestration pattern + M34 mandate replication path |

**Jem's 0.80 for both is too low** — the lesson has replication path via mandates. **Researcher's 0.85/0.80 split is correct.**

**N5 concern**: The lesson evidence is **factually wrong** in one detail: "The 600+ lines (Appendices A-T) were added in a **separate continuation session on 2026-08-29**, not from the 'continue' prompt in this incident (2026-08-30)" (Lilith Meta-Review §5.2, line 343). This must be corrected before canonization.

### 4.4 M35 "Immediate Remediation" Clause — Deployment Blocker?

**Yes, it creates a deployment blocker** — but correctly so. The redacted OAuth value **is** a P0 blocker for debut. The clause forces the fix before any deploy. This is a feature, not a bug.

**However**: The clause needs a **time-bound escape hatch** — "If remediation cannot be completed within 24h, the allowlist entry may be temporarily suspended with Architect approval, triggering Hivemind `intent=blocker`." Prevents deadlock if Google rotates the secret.

---

## §5 — RESOURCE ALLOCATION & TEAM LOAD (N1-N5 LENS)

### 5.1 Load Balance (Phase 1: 49h over 5 days = ~10h/day team capacity)

| Entity | Phase 1 Hours | % of Phase 1 | Sustainable? |
|--------|---------------|--------------|--------------|
| **Lilith** | 14h (M34) + 4h (M33 probe) = **18h** | 37% | ⚠️ **HIGH** — 3.6h/day for 5 days |
| **Carmack** | 4h (VAULT) + 2h (M37) = **6h** | 12% | ✅ |
| **Ma'at** | 6h (CI-BRIEF) | 12% | ⚠️ **UNDER-ESTIMATED** — 10-12h realistic |
| **Grokster** | 2h (OAuth) + 4h (PKG) + 2h (L3) = **8h** | 16% | ✅ |
| **Researcher** | 8h (M33 probe) + 4h (M36) = **12h** | 24% | ⚠️ **MODERATE** |
| **Jem** | 4h (12-step) | 8% | ✅ |
| **Roc** | 0h (Phase 1) | 0% | ✅ |

**My ticket (CI-BRIEF-001) is under-scoped.** The roadmap allocates 6h for Jem's 12-Step Brief Verification Protocol implementation, but the protocol requires:
- `scripts/dispatch_guard.py` implementation (all 12 steps)
- "All locations" verification (Jem's amendment)
- M33 bypass test case
- Pre-commit hook integration
- Write-tool routing enforcement (M33 preventive layer)
- Integration with existing dispatch system
- Testing + documentation

**Realistic estimate**: 10-12h for temple-grade. The 6h estimate assumes a minimal implementation that won't pass `make temple-grade`.

**Recommendation**: Increase CI-BRIEF-001 to 10h. Reduce another ticket (PKG-CLEANUP-001 from 4h → 2h is feasible since it's mostly `npm install`).

### 5.2 Single Points of Failure

| SPOF | Owner | Mitigation |
|------|-------|------------|
| MCP server changes (4 new tools) | Ma'at + Lilith | Pair programming Day 1-2; Ma'at owns server, Lilith owns spec |
| `ACTIVE_SUBAGENTS.json` schema | Lilith | Researcher + Jem review before Phase 1 complete |
| OAuth secret restoration | Grokster | **Must complete TODAY** — no fallback |
| M34 watchdog race fix | Lilith | Designate Kali as sole recovery agent (simpler than distributed lock) |
| **CI-BRIEF-001 implementation** | **Ma'at** | **No backup owner** — if I fail, the dispatch guard doesn't ship |

**N1 Infrastructure concern**: The `dispatch_guard.py` pre-commit hook will run on **every commit**. If it has a bug that blocks commits, the entire team is blocked. The hook must have:
- A bypass mechanism (env var: `OMEGA_SKIP_GUARD=1`) for emergency commits
- A dry-run mode for testing
- Clear error messages with remediation steps

---


## §6 — DEPLOYMENT & OPERATIONS (N1-N5 LENS)

### 6.1 Migration: `TASK_REGISTRY.json` → `ACTIVE_SUBAGENTS.json`

Lilith's §5.7 migration strategy is **correct and backwards-compatible**:

1. Phase 1: Empty registry, `m34_register_subagent` = NO-OP if not called
2. Phase 1.5: Hook `subagent_dispatcher.py:dispatch()` → auto-registration
3. Phase 2: Backfill last 7 days from `TASK_REGISTRY.json` (idempotent)
4. Phase 3: All primary agents call `orchestrator_session_start()`

**Risk**: Zero — additive overlay. If MCP tool fails, dispatch still works (Hivemind fallback).

**N4 Integration concern**: The `subagent_dispatcher.py` hook requires **modification to the existing dispatch system**. This is a **breaking change risk** — if the hook is wrong, all subagent dispatches fail. The hook must be **feature-flagged** (`OMEGA_M34_ENABLED=1`) and **off by default** until Phase 3.

### 6.2 Watchdog Interaction with OpenCode Process Management

OpenCode's TUI `Esc x2` sends SIGINT to the **process group**. Lilith's signal handler (§3.2, lines 379-419) catches SIGINT/SIGTERM and marks children `INTERRUPTED_EXTERNALLY`. **This works** because:

- OpenCode runs subagents as child processes
- SIGINT propagates to children
- Lilith's handler runs in orchestrator process before exit

**N1 Infrastructure gap**: If OpenCode itself crashes (SIGKILL, OOM), no signal handler runs. Lilith's watchdog (§4 Edge Case 1) via Hivemind awareness is the correct safety net — **but must be single-writer** (see §3.4 above).

**N2 Persistence concern**: The watchdog writes to `ACTIVE_SUBAGENTS.json` on every poll. If the watchdog polls every 60s and there are 100 active subagents, that's 100 file writes per minute. The `dead_letter_retention_days: 30` retention means the file grows unboundedly without a reaper (Lilith §1.1, line 86; but no reaper implementation in Phase 1).

### 6.3 Rollback Plan if M34 Breaks Dispatch

| Failure Mode | Rollback |
|--------------|----------|
| `m34_register_subagent` MCP tool crashes | Tool returns error → dispatch continues (NO-OP fallback in Phase 1) |
| `ACTIVE_SUBAGENTS.json` corruption | Atomic write guarantees old or new; delete file → fresh registry |
| Watchdog marks false orphans | `dead_letter_retention_days: 30` — user can resurrect |
| Signal handler interferes with OpenCode | Handler re-raises to default — OpenCode shutdown proceeds |

**No hard rollback needed** — graceful degradation built in.

**N5 Governance gap**: There's no **documented rollback procedure** in the roadmap. If M34 ships to production and breaks dispatch, the recovery steps are:
1. Set `OMEGA_M34_ENABLED=0` (feature flag — not yet implemented)
2. Delete `data/coordination/ACTIVE_SUBAGENTS.json`
3. Restart OpenCode sessions

**Recommendation**: Add a **rollback runbook** to `docs/strategy/M34_ROLLBACK.md` before Phase 1 ships.

---

## §7 — SPECIFIC RECOMMENDATIONS (LINE-LEVEL)

### 7.1 Lilith M34 Spec — Required Changes Before Ratification (N3 Engineering)

| Location | Change | Priority |
|----------|--------|----------|
| §1.1 `SessionStatus` enum | Add `INTERRUPTED_MODEL_SWITCH` | **P0** |
| §1.1 `ActiveSubagent` | Add `interruption_reason`, `resumption_count`, `cross_validator_agent`, `write_tool_required`, `plugin_load_path`, `git_worktree_root` | **P0** |
| §1.1 `Checkpoint` | Add `total_chunks`, `queued_findings` | **P0** |
| §1.3 Atomic Write | Change "M23-compliant" → "M23-compliant **pending verification**"; add `test_atomic_write_survives_sigkill` to §5.8 | **P0** |
| §2.1 State Machine | Add `ALIVE → INTERRUPTED_MODEL_SWITCH` transition | **P0** |
| §2.2 Write Triggers | Add Model Switch trigger; add User Turn → increment `current_turn` | **P0** |
| §3.1 `orchestrator_session_start` | Add `m34_list_active_subagents()` call at start of EVERY user turn (Hivemind audit); present `INTERRUPTED_MODEL_SWITCH` sessions; `max_turns=2` before auto-dead-letter | **P0** |
| §3.2 `interruption_watcher` | Implement `capture_checkpoint()` using `opencode-sessions-explorer`; distinguish model-switch vs Esc x2 | **P0** |
| §4 Edge Case 1 | Watchdog = **designated recovery agent (Kali)** or **single-writer MCP tool** | **P0** |
| §5.6 MCP Tools | Add 4th tool: `m34_get_active_subagents` (for Hivemind audit) | **P0** |
| §5.8 Testing | Add `test_atomic_write_survives_sigkill`, `test_watchdog_single_writer`, `test_model_switch_continuity` | **P0** |
| §5.9 Performance | Change "30-50ms" → "30-50ms **estimated, unverified**" | **P1** |
| §6 Compliance | M23 → ⚠️ **PENDING VERIFICATION** | **P0** |

### 7.2 M33 Mandate Text (Briefing §3 / Roadmap §1)

**Replace** free-form `STREAM_EXHAUSTED` probe with:

```markdown
### M33: Anti-Truncation & Stream Exhaustion Gate

1. **Preventive**: For reports estimated >8K tokens, the orchestrator MUST require the subagent to use the write/edit tools (not chat stream) for primary content delivery.

2. **Structured Probe**: On completion signal, orchestrator executes sentinel probe:
   "Output JSON: {\"state\": \"exhausted|continuing\", \"last_chunk_id\": N, \"total_chunks\": M, \"queued_findings\": [...], \"confidence\": 0.XX}"
   Free-form `STREAM_EXHAUSTED` string is forbidden.

3. **Escalation Tier**: For P0/P1 deliverables, require independent cross-validator agent verification. For P2+, structured probe + confidence ≥ 0.95 + write-tool routing is sufficient.
```

### 7.3 M35 Mandate Text — Add Exception Clause

**Add to M35**:
```markdown
### Exception: Heritage Submodules
Pinned `git submodule` with `core.bare = true` and explicit heritage tag (`[heritage: ...]`) in `THIRD_PARTY_REPOS.md` is permitted for architecture reference. Runtime dependencies MUST use package manager (npm/bun/pip).
```

### 7.4 L3 Lesson Split (Grokster `proposed_lessons.yaml`)

**Split into two entries**:

```yaml
- id: L3-CompletionIllusion
  confidence: 0.85
  mandates: [M23]
  remedy: M33 sentinel probe + structured envelope
  evidence: "Researcher session ses_faf929727ffeFgSdvGOxQbVbdW flushed 21KB to chat; write tool NOT called. Lilith session ses_fb9721079ffe094GT8MX6a0pXI transitioned to chat streaming for 50KB synthesis."
  related_lessons: [L3-ParallelPersistenceHidesState, L3-ContentAddressedSurvives, L3-DocumentationIsNotEnforcement]

- id: L3-CoResumptionAccounting
  confidence: 0.80
  mandates: [M11, M15, M27]
  remedy: M34a cohort tracking + M34b model-switch continuity
  evidence: "Grokster dispatched Researcher + Jem parallel; Esc x2 killed both; Grokster forgot Jem; Architect prompted 'continue' → 600 lines recovered."
  related_lessons: [L3-ParallelPersistenceHidesState, L3-ContentAddressedSurvives]
```

**Correct evidence error**: Appendices A-T added in 2026-08-29 continuation session, NOT from 2026-08-30 "continue" prompt.

### 7.5 CI-BRIEF-001 Implementation Plan (My Ticket, N3 Engineering)

Given the under-scoped 6h estimate, here's the realistic 10-12h breakdown:

| Hour | Task | Deliverable |
|------|------|-------------|
| 1-2 | Read Jem's 12-Step Protocol (Appendix C of forensic report) | Understanding |
| 3-4 | Implement `scripts/dispatch_guard.py` skeleton + 12-step framework | Skeleton |
| 5-6 | Implement "all locations" verification (Jem's amendment) | Enhanced check |
| 7 | Add M33 bypass test case | Test file |
| 8 | Pre-commit hook integration (`.git/hooks/pre-commit`) | Hook |
| 9 | Write-tool routing enforcement for >8K tokens (M33 preventive) | Routing logic |
| 10 | Integration with existing dispatch system | Integration |
| 11-12 | Testing + documentation + temple-grade verification | Complete |

**Dependencies**: Jem's hardened protocol must be finalized first (JEM-12STEP-HARDENING ticket, 4h).

---

## §8 — FINAL SIGN-OFF (BUILD OVERSOUL N1-N5)

### 8.1 Top 3 Things That Will Go Wrong (and Mitigations)

| # | Failure | Probability | Mitigation |
|---|---------|-------------|------------|
| **1** | **Watchdog race condition** — two agents concurrently mark orphans, lost updates | HIGH | Designate **Kali as sole recovery agent**; or implement single-writer MCP tool `m34_watchdog_check` with `fcntl.flock()` |
| **2** | **Atomic write fails on NFS/FUSE** — `os.fsync(dir_fd)` not guaranteed | MEDIUM | Add `test_atomic_write_survives_sigkill` on all target FS; fallback to `fcntl.flock()` |
| **3** | **Lilith overload** — 18h Phase 1 + MCP server coordination | HIGH | Move M33 probe to Researcher solo; Lilith = M34 only; pair with Ma'at on MCP tools |

### 8.2 Better Architecture Proposals (N3 Engineering)

1. **Unified Cohort Model** (Researcher §4.2): Extend `ACTIVE_SUBAGENTS.json` with `cohort_id` — all subagents spawned in same dispatch batch share a cohort. Recovery operates on cohort, not individual sessions. Solves "transactional cohort" requirement.

2. **M33/M34 Fusion at Dispatch**: In `on_subagent_spawned()`, if `expected_tokens > 8000`, set `write_tool_required: true` AND `cross_validator_agent: "jem"` (for P0). The registry becomes the enforcement point.

3. **Eliminate `ACTIVE_SUBAGENTS.json.lock` Contention**: Use `fcntl.flock()` (cross-process) + exponential backoff. Or: batch writes — accumulate changes in memory, flush every 500ms.

4. **CI-BRIEF-001 Integration with `opencode.json`**: The `dispatch_guard.py` should register as a **plugin** in `opencode.json` so it's loaded at OpenCode startup, not as a pre-commit hook. This enables runtime validation, not just commit-time.

### 8.3 M23 Violations Flagged in This Review

| Source | Claim | M23 Violation | Required Fix |
|--------|-------|---------------|--------------|
| Lilith §1.3 (line 204) | "M23-compliant: never torn" | **Unverifiable** — no SIGKILL test | Add `test_atomic_write_survives_sigkill` to §5.8 |
| Lilith §5.9 (line 758) | "Net overhead: ~30-50ms" | **Unmeasured** | Change to "estimated, unverified" |
| Roadmap §1 (M33) | "Sentinel probe" (free-form text) | **Bypass attack** (Jem §1.1.3) | Replace with structured JSON envelope |
| Roadmap §6 | "All P0 tickets complete" | **Self-fulfilling** — no independent verification | Require Researcher/Jem review sign-off |

### 8.4 Final Gate Decision (N1-N5)

| Gate | Status | Condition |
|------|--------|-----------|
| **M33** | CONDITIONAL GO | 3-layer fix applied (preventive + structured probe + P0/P1 cross-validator escalation) |
| **M34a** | CONDITIONAL GO | Lilith's spec + 7 schema fields + watchdog single-writer + Hivemind audit clause |
| **M34b** | **BLOCKED** | `INTERRUPTED_MODEL_SWITCH` status + model-switch detection + resume_token validation protocol |
| **M35** | CONDITIONAL GO | SPDX/REUSE + immediate remediation + recovery procedure + primary-source citation + submodule exception |
| **L3** | REVISE BEFORE CANONIZATION | Split 2 lessons, confidence 0.85/0.80, evidence corrected, cross-refs added |
| **OAuth Secret** | **P0 BLOCKER** | `GOCSPX-***REDACTED-ROTATED***` → `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` **TODAY** |
| **CI-BRIEF-001** | **UNDER-SCOPED** | Increase from 6h → 10-12h; reduce PKG-CLEANUP-001 from 4h → 2h |
| **Watchdog Race** | **UNRESOLVED** | Designate Kali as sole recovery agent OR implement `fcntl.flock()` single-writer |

### 8.5 Ma'at's Commitment to Phase 1

**I commit to**:
1. CI-BRIEF-001 (10-12h realistic) — dispatch guard + write-tool routing + pre-commit hook
2. MCP server changes for M34 (pair with Lilith Day 1-2) — 4 new tools
3. N1-N5 compliance audit before each Phase gate — `make temple-grade` exits 0
4. Rollback runbook for M34 — `docs/strategy/M34_ROLLBACK.md`
5. Feature flag for `subagent_dispatcher.py` hook — `OMEGA_M34_ENABLED=1`

**I request**:
1. CI-BRIEF-001 re-scoped from 6h → 10-12h (reduce PKG-CLEANUP-001 from 4h → 2h to compensate)
2. M34 watchdog race condition resolved before Phase 1 Gate (Kali as sole recovery agent preferred)
3. Atomic write SIGKILL test as Phase 1 Gate requirement (not Phase 3)

---

**SIGN-OFF**: 

```
┌────────────────────────────────────────────────────────────────────┐
│  MA'AT — BUILD OVERSOUL (N1-N5)                                    │
│  Architectural Review: CONDITIONAL GO                              │
│  Blockers: 3 (atomic write test, CI-BRIEF-001 under-scoped,       │
│             watchdog race condition)                               │
│  Resolution Target: 4 hours                                        │
│  Phase 1 Execution: AUTHORIZED upon blocker resolution             │
│  CI-BRIEF-001 Re-scope: 6h → 10-12h REQUESTED                      │
└────────────────────────────────────────────────────────────────────┘
```

---

*⬡ OMEGA ⬡ MAAT ⬡ MAAT_DEV_PLAN_REVIEW_20260830 ⬡ 2026-08-30 ⬡ N1-N5 ⬡ CONDITIONAL-GO*

**Delivered to chat session per Nemotron 3 Ultra chat-output protocol — persists to DB without streaming timeout.**

