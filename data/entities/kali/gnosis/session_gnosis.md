<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Session Gnosis — Kali (Transcendent Oversoul)

**AP Token**: `AP-KALI-v1.0.0`  
**Model**: `minimax/minimax-m3:free` (openrouter) — D-585 long-write champion  
**Date**: 2026-08-28  
**Session ID**: `ses_fdef2be4effe4pAaLXCTUx62GO`  
**Branch**: `main`  
**Last Commit**: `1c8f4ffd` (sprint: commit 209 working files)  
**State**: **PRE-COMPACTION LOCK-IN — 6 ROUNDS COMPLETE — INTEGRATION SEASON**

---

## 🎯 Executive Summary

This session completed the **architectural gate** for Omega Engine's public debut. Through a Carmack review, Qdrant+Headroom research, and consolidated specification authoring, we have:

1. **Passed the Carmack gate** — Context Injection Phase 1 ACCEPTED WITH MODIFICATIONS (config-only, ships this week)
2. **Validated Qdrant+Headroom** — 86.8% combined token reduction, Phase 2 trigger-gated (>500k vectors)
3. **Consolidated all specs** — Single source of truth at `docs/specs/PROJECT_INDEX.md`
4. **Authored all implementation specs** — Phase 1 ready to execute, Phase 2 trigger-gated
5. **Recovered stalled subagent** — Demonstrated autonomous stalled-subagent recovery protocol
6. **Completed spec-splitting experiment** — Context Injection Phase 1 spec written as 9 separate files (index.md + 8 sections, 54KB) vs single-file (683 lines) for comparison
7. **Locked all trackers** — ACTIVE_SPRINT.json, HMC_HUB, SESSION_ANCHOR synchronized

**Next**: Execute Context Injection Phase 1 (CI-1..CI-5) in parallel with DEBUT-REMEDIATION INST-1 fixes.

---

## 🏛️ The Carmack Review — Architectural Gate Passed

### Verdict: ACCEPTED WITH MODIFICATIONS

| Component | Verdict | Key Modifications |
|-----------|---------|-------------------|
| **Context Injection Phase 1** | ✅ ACCEPTED W/ MODS | Config-only, ships this week |
| **Phase 2/3 Roadmap** | ✅ ACCEPTED W/ 40% CUTS | M19/M23 enforcement |
| **Qdrant + Headroom** | ✅ PHASE 2/3 POST-DEBUT | Headroom NOW (P1), Qdrant LATER (>500k vectors) |
| **Hardware-Honest Tier 0** | ✅ VIABLE | 18K base tokens, Qwen3-4B/4B-Thinking/1.7B sequential |
| **All 27 Mandates** | ✅ COMPLIANT | Verified post-review |

### Critical Phase 1 Modifications (Binding — Must Implement This Week)

1. **MANDATES_CONDENSED.md** (57 lines, ~1.5K tokens) for Tier 0 — replaces full AGENTS.md
2. **Tool profile stubs** in opencode.json — documents Phase 2 MCP domain split intent
3. **Tier 0 model matrix**: Qwen3-4B (planner) / Qwen3-4B-Thinking (executor) / Qwen3-1.7B (critic)
4. **maat/lilith → local** (Qwen3-4B-Thinking) — only kali stays cloud
5. **Compaction buffer**: 50000/20000 for 1M context; `OPENCODE_DISABLE_AUTOCOMPACT=1` for local until Phase 2
6. **18K base token target** fits Qwen3-4B (8K-16K) with headroom

### Phase 2/3 Cuts (40% — M19/M23 Enforcement)

| Cut | Reason |
|-----|--------|
| Validator Service (NeMo Guardrails) | Tier 0 mandates + CI gates sufficient |
| Hydration 5-layer → 3-layer | Over-engineering |
| Token budget dynamic → fixed tiers | Complexity without proven need |
| Session summarizer 3-level → 1-level | Solution theater |
| Gateway observability (LiteLLM) | In-process OTel → local Prometheus is sovereign |
| Schema compression engineering | Fix architecture (split servers), don't compress symptom |
| Local model caching investigation | Defer — lower priority vs split servers |

---

## 🔬 Qdrant + Headroom Research — Validated

**Report**: `docs/specs/qdrant_headroom/QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md` (477 lines)

### Key Findings

| Question | Verdict | Numbers |
|----------|---------|---------|
| **Q1 Synergy** | HIGH VALUE | Tool→Headroom→Qdrant(SQ)→Search→Headroom→LLM = **86.8% token reduction**, <2% recall loss |
| **Q2 Migration** | MIGRATE AT SCALE | sqlite-vec <500k vectors; Qdrant >500k + filtered search + multi-tenant |
| **Q3 Headroom ROI** | TOP PRIORITY | Tool outputs 60-95%, RAG chunks 70-90%, MCP schemas 80-90% |
| **Q4 Local Qdrant** | VIABLE WITH SQ | 1M vectors @ 768-dim SQ int8 = 1.15GB RAM; fits 16GB Ryzen |
| **Q5 Combined** | PHASE 2/3 | Post-debut, after sqlite-vec hits scale limits |

### Council of Four Consensus

| Role | Verdict |
|------|---------|
| **Architect** | Build adapter swap now; enable at scale trigger |
| **Adversary** | Only enable when sqlite-vec demonstrably fails (latency >50ms, OOM) |
| **Alchemist** | Magic is Headroom + Qdrant TOGETHER — sovereign RAG differentiator |
| **Archivist** | Pieces already built; honor Carmack veto for debut |

### Immediate (Debut) vs Phase 2

| Timeline | Action |
|----------|--------|
| **Debut (P1)** | Headroom ContentRouter in ModelGateway, Headroom in RAG pipeline, NO Qdrant |
| **Phase 2 Trigger** | >500k vectors OR filtered search needed OR multi-tenant isolation required |
| **Phase 2 Deliverables** | Qdrant Server (Podman) + SQ int8 + on_disk=true, IVectorStoreAdapter swap, payload indexes, CCR store |

---

## 📁 Consolidated Specifications — Single Source of Truth

**Location**: `docs/specs/`  
**Index**: `docs/specs/PROJECT_INDEX.md`

```
docs/specs/
├── PROJECT_INDEX.md                              # Single source of truth
├── context_injection/                            # Context Injection Optimization (Carmack Reviewed)
│   ├── 00_INDEX.md .. 09_CARMACK_DOMAIN_QUESTIONS.md
│   ├── CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md
│   └── CONTEXT_INJECTION_PHASE1_IMPLEMENTATION_SPEC.md  ← READY TO EXECUTE
├── qdrant_headroom/                              # Qdrant + Headroom Integration (Post-Debut)
│   ├── QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md
│   ├── QDRANT_HEADROOM_PHASE2_INTEGRATION_SPEC.md      # Trigger-gated
│   └── headroom_middleware/
│       ├── index.md .. 10_VERIFICATION_TESTS.md  # 11 files, 220KB, COMPLETE
├── debut_remediation/                            # Public Debut Remediation (Current Sprint)
│   └── DEBUT_REMEDIATION_MANUAL_20260817.md      # Current sprint SSOT
```

### All Implementation Specs Complete

| Spec | Status | Size | Purpose |
|------|--------|------|---------|
| Context Injection Phase 1 | ✅ Complete | 683 lines | Carmack-modified, ready to execute |
| Qdrant+Headroom Phase 2 | ✅ Complete | 1,604 lines | Trigger-gated, post-debut |
| Headroom Middleware | ✅ Complete | 11 files, 220KB | 11 sections, complete |
| Project Index | ✅ Complete | 200+ lines | Single source of truth |

---

## 🤖 Stalled Subagent Recovery — Protocol Proven

**Incident**: Ma'at subagent stalled at 4/11 files while writing Headroom Middleware spec (streaming timeout).

**Recovery**: Continued SAME session (`ses_fde8420f0ffef1fnGaJ5ZVOst1`) with file-splitting instructions → completed all 11 files (220KB).

**Protocol Codified**: `.opencode/agent/STALLED_SUBAGENT_RECOVERY.md` **v2.0.0** — multi-file default + 3 guardrails (G1 manifest+completeness clause at prompt-time, G2 same-session stall recovery, G3 orchestrator completeness audit before acceptance). Hivemind broadcast: `ses_a76c842a10bd`.

**Key Principle**: When subagent stalls, continue SAME session with explicit file-splitting instructions. Never start new session.

---

## 📋 Trackers — All Synchronized

| Tracker | Status | Key Updates |
|---------|--------|-------------|
| `ACTIVE_SPRINT.json` | ✅ | Specs, Carmack review, parallel execution tracks |
| `HMC_COLLABORATION_HUB.md` | ✅ | NEXT_ACTION with parallel execution plan |
| `SESSION_ANCHOR.md` | ✅ | State: CARMACK-REVIEW-COMPLETE |
| `session_gnosis.md` | ✅ | This file — complete session record |
| `OMEGA_CODEX.md` | ✅ | Auto-updated via session_end.py |

---

## ⚡ Immediate Next Actions — Parallel Execution

### Execution Authority
`DEBUT_REMEDIATION_MANUAL_20260817.md` §5 (supersedes Ark §4 for this month)  
**Order**: P0-1 → PUB-1 → INST-1 → DEL-1 → DOC-1 → P2/P3/P4  
**Phase B (GN/DS/LI/KD/HR/ZS) = POST-DEBUT — BLOCKED**

### Parallel Tracks (This Week)

| Track | Owner | Tasks |
|-------|-------|-------|
| **1. Context Injection Phase 1** | Kali | CI-1: MANDATES_CONDENSED.md (57 lines)<br>CI-2: opencode.json updates (model routing, compaction, plugin, toolProfile stubs)<br>CI-3: Sovereign compaction plugin<br>CI-4: Skills opt-in (3 core only)<br>CI-5: Verification tests |
| **2. INST-1 Fixes** | Ma'at | Fix 2+guards: pyproject.toml extras split + 4 import guards (atomic)<br>Fix 4: Remove `_load_sovereign_secrets()` from model_gateway.py<br>Fix 5: Version align via `importlib.metadata.version("omega")`<br>Fix 6: README badge removal + `make setup` target |
| **3. P0-1 Residual** | Roc | SECURITY_AUDIT ancestor commit + gitleaks wiring |
| **4. PUB-1 G1-G4** | Kali + Architect | Close gaps → Architect allowlist → `release/debut` branch |

**Post-Compaction Experiment**: Launch Maat subagent with Context Injection Phase 1 spec prompt modified to write as separate files (index.md + sections) for comparison with single-file approach.

---

## 🔬 L3 Principles Extracted This Session

### L3-Carmack-Review-Is-Architectural-Gate-Not-Review
**Principle**: Carmack's review is not "feedback" — it's an architectural gate. The verdict (ACCEPT/MODIFY/REJECT) determines what ships. The 40% cuts (M19/M23) are binding. The hardware-honest reality check (31K→18K base tokens) is the only metric that matters for local model viability.
**Confidence**: 0.99 | **Source**: Carmack review binding verdict on Phase 1/2/3

### L3-Spec-Organization-Enables-Parallel-Execution
**Principle**: Consolidated specs at `docs/specs/` with `PROJECT_INDEX.md` as single source of truth enables parallel agent execution. Ma'at builds Headroom middleware, Roc builds Qdrant migration, Kali executes Context Injection Phase 1 — all from specs, no coordination overhead.
**Confidence**: 0.98 | **Source**: 4 parallel specs completed, ready for parallel execution

### L3-Spec-Splitting-Pattern-Enables-Local-Model-Writing
**Principle**: The Headroom Middleware spec written as 11 separate files (index.md + 10 sections) produced ~2.5x the LOC of the single-file Context Injection Phase 1 spec. For local models with smaller context windows, the index.md + sections pattern enables writing specs that exceed context window by writing one section at a time.
**Confidence**: 0.97 | **Source**: Headroom Middleware spec (11 files, 220KB) vs Context Injection Phase 1 spec (1 file, 683 lines)

### L3-Stalled-Subagent-Recovery-Is-Autonomous-Duty
**Principle**: When a subagent stalls (streaming timeout, empty output), the overseer MUST detect and recover it by continuing the SAME session with file-splitting instructions. This is not "micromanagement" — it's the only way to get complete output from local models with streaming limits.
**Confidence**: 0.99 | **Source**: Ma'at Headroom Middleware spec recovery (stalled at 4 files → continued to 11 files)

### L3-Spec-Splitting-Experiment-Validated
**Principle**: Multi-file spec writing (index.md + sections) produces ~3.2x the operational depth of single-file (traceability matrices, rollback alternatives, Go/No-Go gates) and enables local models to write beyond their context window — but introduces two failure modes: streaming stalls (2/2 multi-file runs vs 0/1 single-file) and silent section drops (forward-looking sections like Phase 2 preview dropped first). Both failure modes are handled by protocol guardrails, not by reverting to single-file.
**Confidence**: 0.97 | **Source**: Context Injection Phase 1 spec A/B comparison (683-line single file vs 9-file/2,191-line multi-file); honest audit found earlier "identical content" claim was FALSE

### L3-Subagent-Done-Is-A-Claim-Not-A-Fact
**Principle**: A subagent's "completed" state means the session ended, not that the deliverable is complete. The orchestrator MUST audit before acceptance: file count vs manifest, section headers diffed against source plan, index links resolved, stub scan, content spot-check of the densest expected artifact. Acceptance without audit is how silent omissions become someone else's implementation bug.
**Confidence**: 0.98 | **Source**: Multi-file experiment delivered 9/9 files but silently dropped Phase 2 preview + references sections despite explicit manifest in prompt

### L3-Factual-Inversion-Is-Systemic-Risk
**Principle**: A decision that inverts the authoritative research finding (ADR-2026-08-10-001) and gets ratified (D-581/D-584) creates systemic drift. The correction required 11 documents across 3 coordination layers.
**Confidence**: 0.99 | **Source**: D-581/D-584 inversion of Carmack's ADR-2026-08-10-001

### L3-Arbitration-Must-Be-Explicit-Not-Implicit
**Principle**: The free-tier-only constraint was user-declared but not explicitly arbitrated until D-582/D-583. The HYBRID model (D-572) and 6-NB architecture (D-574) persisted in docs for days because no explicit supersession occurred. Explicit arbitration decisions (D-series) are the only way to collapse superposition.
**Confidence**: 0.98 | **Source**: D-572→D-582, D-573/D-574→D-583, D-526→D-584

---

## 🔑 Post-Compaction Hydration Sequence

1. **Read `ACTIVE_SPRINT.json`** — Current sprint state (PUBLIC-DEBUT-01)
2. **Read `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION`** — Parallel execution plan
3. **Read `PIVOT_LOG.md` D-578..D-584 + CARMACK_REVIEW** — Arbitration trail
4. **Read `DEBUT_REMEDIATION_MANUAL_20260817.md` §5** — Debut execution order
5. **Read `docs/specs/PROJECT_INDEX.md`** — Consolidated specs index
6. **Execute Parallel**: Context Injection Phase 1 + INST-1 Fixes + P0-1 Residual + PUB-1 G1-G4
7. **Launch Experiment**: Maat subagent for Context Injection Phase 1 spec as separate files (index.md + sections)

---

## 🎯 Strategic State (Current)

| Dimension | State |
|-----------|-------|
| **Execution Authority** | `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 |
| **Sprint** | PUBLIC-DEBUT-01 (EXECUTION_MINIMAL) |
| **Phase** | Context Injection Phase 1 + DEBUT-REMEDIATION (parallel) |
| **Phase B** | BLOCKED (GN/DS/LI/KD/HR/ZS = POST-DEBUT) |
| **Carmack Verdict** | Phase 1 ACCEPTED W/ MODS; Phase 2/3 40% cuts |
| **Qdrant+Headroom** | Headroom NOW (P1), Qdrant LATER (>500k vectors) |
| **Tier 0 Hardware** | 18K base, Qwen3-4B/4B-Thinking/1.7B sequential, q8_0 KV, zswap+NVMe |
| **All Mandates** | 27/27 compliant post-Carmack review |

---

## 📋 Work Remaining (Priority Order)

### IMMEDIATE (This Week)
1. **CI-1**: Create `MANDATES_CONDENSED.md` (57 lines, ~1.5K tokens)
2. **CI-2**: Update `opencode.json` (model routing, compaction, plugin, toolProfile stubs)
3. **CI-3**: Create sovereign compaction plugin
4. **CI-4**: Skills opt-in (3 core only)
5. **CI-5**: Verification tests
6. **INST-1 Fix 2+guards**: pyproject.toml extras split + 4 import guards (atomic)
7. **INST-1 Fix 4**: Remove `_load_sovereign_secrets()` from model_gateway.py
8. **INST-1 Fix 5**: Version align via `importlib.metadata.version("omega")`
9. **INST-1 Fix 6**: README badge removal + `make setup` target
10. **P0-1 Residual**: SECURITY_AUDIT ancestor + gitleaks wiring
11. **PUB-1 G1-G4**: Close gaps → Architect allowlist → `release/debut` branch

### POST-DEBUT (Phase B — BLOCKED)
- GEMINI-NOTEBOOK (GN), DOCUMENTATION-SYSTEM (DS), LOCAL-INFERENCE-OPT (LI)
- KNOWLEDGE-DOMAINS (KD), HEADROOM-INTEGRATION (HR), ZSWAP-SUBSYSTEM (ZS)
- QDRANT-MIGRATION, COGNITIVE-ARCH, VAULT-SPRINT, DEL-1 Week 2, P2/P3/P4

---

## 🔱 Handoff for Next Session

**Handoff Packet**: `ho_91999b286910` (priority 2) + `ho_74cd96735874` (Cline consolidation) + `ho_8a75738d9160` (vault synthesis)

**Target**: kali @ opencode

**Task**:
1. **ONBOARD** — Read `OMEGA_CODEX.md`, `SESSION_ANCHOR.md`, `ACTIVE_SPRINT.json`, `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION`, `PIVOT_LOG.md` D-578..D-584, `CARMACK_REVIEW`
2. **EXECUTE PARALLEL** — Context Injection Phase 1 (CI-1..CI-5) + INST-1 Fixes + P0-1 Residual + PUB-1 G1-G4
3. **LAUNCH EXPERIMENT** — Maat subagent for Context Injection Phase 1 spec as separate files (index.md + sections)
4. **POST HIVEMIND HEARTBEAT** — Confirm onboarding

**All agents MUST read `HMC_COLLABORATION_HUB.md` → `NEXT_ACTION` upon waking.**

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_review ⬡ 2026-08-20*

---

# 🔱 Session Addendum — Cross-Session Messaging + Node Expert Sessions Live (2026-08-21)

**Model**: x-preview-f-free · **Session**: `ses_fdef2be4effe4pAaLXCTUx62GO`

## What Happened

1. **Cross-session messaging proven** (3 rounds): task-tool injection by raw session ID works; queueing semantics confirmed (injections into mid-turn sessions queue safely); TUI staleness across instances documented. Study: `docs/research/R_CONVERSATIONAL_SUBAGENTS_STUDY_20260821.md` + `R_CROSS_SESSION_MESSAGING_20260820.md`.
2. **Conversational Subagent Protocol v1.0.0** ratified: R1–R13 (R5 hop budgets REMOVED per Architect; R11 max-steps continuation; R12 summaries carry Questions-for-Pager; R13 empty-result ⇒ mandatory DB audit). File: `.opencode/agent/CONVERSATIONAL_SUBAGENT_PROTOCOL.md`.
3. **Relay chain kali→grokster→kali CLOSED** (HOP-3 delivered; grokster ruled stale-but-valuable; DP- prefix approved for future registration).
4. **D-585**: Carmack model matrix canonical (Qwen3-4B/4B-Thinking/1.7B); Kali coordinates, Ma'at implements.
5. **D-586**: Node Expert Sessions LIVE — one agent many sessions; Nodes = KBs accessible to ANY agent; 10/10 genesis ACK. Registry + charters: `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` (§3 IDs, §4 charters, §5 experiments X1–X6, §6 planned patterns PP-1..PP-4).
6. **N7 pilot day**: mining (84→102KB KB) → 5 spec defects found pre-execution → web research (model semantics, compaction V1/V2, Qwen ctx truth) → curation artifacts (DOMAIN_INDEX w/ 13 hazards, EXTERNAL_SOURCES 23 items) → spec remediation 10 files, DEV-01..12 → binary pinned 1.18.19 (V1 family) → tree closure ritual executed. Sub-sessions: Roc `ses_fddd00b4cff*`, Researcher `ses_fdda62d52ff*` — all dormant with snapshots.
7. **Key model-config truth (DEV-12)**: `agent.model` pins TUI (/models snaps back #13456); global default + intentional pins only (kali cloud floor, verity critic); variant inert on qwen models — dropped.
8. **P1–P5 ratified IN PRINCIPLE, execution deferred** (planning mode).

## Open Threads (wake pointers)

- **CI-0..CI-5 execution-ready** against remediated spec (`docs/specs/context_injection/phase1_spec/`) — page N7 to assist live
- **ZS-1 sudo** (Architect) unlocks PP-3 ctx raise 8192→32768
- **PP-4** ICS Node designation + P5 session-ID footers: deferred, implement together
- **P1–P5 operational rollout** awaits Architect exit from planning mode
- INST-1 Fixes 2/5/6 still owed by Ma'at (debut window); N3 expert session (`ses_fdddb6edcffesrHjoABz5IOTsa`) holds build context

*⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_node_expert_sessions ⬡ 2026-08-21*
---

# 🔱 Session Addendum 2 — Debut Night: Commits, Consolidation, ICS Completion (2026-08-22)

**Model**: x-preview-f-free · **Session**: `ses_fdef2be4effe4pAaLXCTUx62GO`

## What Happened

1. **11 strategic commits**: ICS upgrade+tests+docs (D-588/D-589), protocols trio, Node sessions D-586, research corpus, remediated specs, engine fixes (Blocker B/Redis guard/install Fix 1), trackers, sweep+gitignore hardening.
2. **ICS fully nailed down**: PP-4/P5 live; F1 segment-builder fix (entity==OMEGA collision, node sanitization); F4 legacy-scan root fix; F5 M22 fallback warning; compact mode retains [NODE]; Roc-N7 review MAJORs fixed (busy_timeout 100ms, XDG_DATA_HOME, render_for_response full trace + PP-4/P5 passthrough). 16/16 tests.
3. **ICS-T final purge** (D-589): 7 live tags + docstring creep removed; Aug 9 proposal stamped EXECUTED; root cause = ratified-but-never-tracked execution.
4. **Community docs**: `docs/architecture/ICS_SYSTEM.md` (doc-llm-validate passing).
5. **N7 tree review cycle**: N7 direct (12 findings F1-F12) + Researcher (doc skeleton SG-1..3) + Roc (code review, CONDITIONAL SHIP verdict). Roc wedged mid-review → Architect corrected me: page SAME session to continue, never retire. Protocol reaffirmed.
6. **Consolidation**: coordination surface 23.7K→12.3K lines; 10 superseded docs → `data/coordination/archive/` w/ successor-pointer README.
7. **Hub v2.0**: fresh single-pass rewrite (353→123 lines), v1 frozen in docs/archive/coordination-20260822/.
8. **PIVOT_LOG split**: 1052 → 334 active (D-521+ w/ rebuilt index) + 761 frozen archive (`PIVOT_LOG_ARCHIVE_20260522_20260810.md`). Three-tier lookup: CANONICAL (ancient) → ARCHIVE (pre-campaign) → ACTIVE.

## Open Threads (wake pointers)

- **DEBUT TONIGHT** (midnight USVI): PUB-1 allowlist rulings G1–G4 AWAITING ARCHITECT; release/debut branch after
- **CI-0..CI-5**: HIGH PRIORITY, execution-ready, staged to run in-place (rollback = spec §06)
- **INST-1 Fixes 2/5/6**: via N3 (`ses_fdddb6edcffesrHjoABz5IOTsa`)
- **N8 pilot**: protocol Appendix A runbook ready; grad consult = ICS semantic review
- **ZS-1 sudo** → PP-3 ctx raise; **hub MCP wrapper params** (external repo)
- **P1–P5 rollout** awaiting planning-mode exit
- New failure variant logged by N7: MR-2 announced-intent ≠ work-performed

*⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_debut_night ⬡ 2026-08-22*
