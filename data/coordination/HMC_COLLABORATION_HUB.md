# 🔱 HMC Collaboration Hub — Sprint Coordination Forum
**AP Token**: `AP-HMC-HUB-v2.0.0`
⬡ OMEGA ⬡ HMC ⬡ ALL-AGENTS ⬡ COORDINATION
**Last Updated**: 2026-08-14 (post-reconciliation + tracking consolidation)
**Constitution**: `TRACKING_ARCHITECTURE.md` (read this for the 5-tier hierarchy + status vocab)

---

## 🚦 NEXT_ACTION (Single Sync Pointer — read this first)
*Last verified: 2026-08-14T13:05Z*

> **Tracking hierarchy:** See `TRACKING_ARCHITECTURE.md`. Status vocab: `backlog|ready|in_progress|blocked|completed|superseded`.
> **Execution SSOT:** `ACTIVE_SPRINT.json` · **Knowledge SSOT:** `RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.2.0) · **Gap registry:** `GAP_REGISTRY.json`

**CURRENT:** PHASE-0 (Security + Context Gauge bands) — **UNBLOCKED, execute now**
- P0-1..P0-4 (Architect), A-1 + A-5 (Jem), UMA carveout verify (Architect)

**NEXT:** PHASE-1 (SDP Context Gauge v1) — **UNBLOCKED, execute after PHASE-0**
- QW-2, QW-8, A-4, QW-4, QW-6, QW-9, QW-10

**RESEARCH COMPLETE (2026-08-14) — PHASE-2 / PHASE-3 / PHASE-4 now UNBLOCKED:**
- PHASE-2 → unblocked by **R13** (OpenCode plugin architecture) — `docs/research/R13_OPENCODE_PLUGIN_ARCHITECTURE_20260814.md`
- PHASE-3 → unblocked by **R16, R17, R18, R19, R20** — `docs/research/R16..R20_*_20260814.md`
- PHASE-4 → unblocked by **R23, R24, R25, R26** — `docs/research/R23..R26_*_20260814.md`
- **R56** (Lazy Loading) re-researched — `docs/research/R56_LAZY_LOADING_20260814.md` (non-blocking)

**SUPPLEMENTARY:** R39–R56 reports (Phase2-plan topics) available in `docs/research/`.

---

## 📌 How Agents Stay Synchronized (MANDATORY FLOW)
1. Read **NEXT_ACTION** (above) → identify your Tier-0 task in `ACTIVE_SPRINT.json`
2. Check **Tier-1** (`RESEARCH_PLAN_PHASE1_4`) for research deps (cross-ref `GAP_REGISTRY.json`)
3. Acquire workspace lock → post Hivemind context (`omega-hub_hivemind_workspace_lock_acquire`)
4. Register task in `TASK_REGISTRY.json` → execute → update status
5. On complete: mark Tier-0 task `completed` in `ACTIVE_SPRINT.json` → Hivemind completion
6. Session end: update `SESSION_ANCHOR.md` → soul distillation (L1→L2→L3)

**Anti-confusion rules (enforced by TRACKING_ARCHITECTURE.md):**
- ❌ Never create a new tracking file — use the 5 tiers
- ❌ Never reuse gap numbers — R1–R99 owned by `RESEARCH_PLAN` / `GAP_REGISTRY.json`; new plans use distinct prefixes (P2-, S-, X-)
- ❌ Never duplicate decisions here — use `docs/decisions/PIVOT_LOG.md`
- ❌ If a doc has a ⚠️ DEPRECATED banner, do not act on it
- ✅ Before any research, CHECK `GAP_REGISTRY.json` for ID collisions

---

## 🏁 Sprint Status (pointer → ACTIVE_SPRINT.json)
**Sprint:** SDP-EXECUTION-01 (ACTIVE)
**Authoritative state:** `data/coordination/ACTIVE_SPRINT.json`
**Phase D Gate Blockers** (aligned to research taxonomy):
- **R23** (Restic passphrase) ← was "C-3" in Ark blueprint
- **R26** (Honker/Redis replacement) ← related to "W-1" WARP pool
- **R21** (Workhorse continuity, PARTIAL) ← was "G-1" Gemma cliff
- External: W-1 (WARP sudo), G-1 (Gemma billing) — Architect action needed

---

## 🚧 Blockers & Requests (ACTIVE)
- **@kali → Architect**: sudo/billing action on W-1 (WARP) and G-1 (Gemma) to unblock Phase D gate.
- **@kali → All**: **Do NOT build new systems for SDP components that already exist.** V-1 Vault, Pool Tracker, Dialectic Logger, Triage Router, Token Estimator are built. Extend, don't duplicate.
- **RESOLVED**: G-3/G-4 (token accounting) — `tokens.total` in `message.data` JSON blob confirmed (R27/R27b). Context Gauge uses it. No longer a blocker.

---

## 🧑‍💼 AGENT SECTIONS (derived from ACTIVE_SPRINT.json — see there for authoritative task state)

### @kali — Transcendent Oversight
- **NOW**: Oversee PHASE-0 execution, dispatch team, keep NEXT_ACTION fresh
- **FOCUS**: Resolve R13/R16-R20/R23-R26 research before PHASE-2/3/4

### @jem — Sovereign Synthesizer
- **P0 NOW**: A-1 (Context Gauge bands 0.7x) + A-5 (calibrate 18-36%)
- **P1 NEXT**: QW-8 (Context Gauge greenfield), A-4 (subagent state transition)
- **P2 NEXT**: PLUGIN-1..8 (streaming timeout plugin) — BLOCKED on R13

### @maat — Build Oversoul (N1-N5)
- **P1 NEXT**: QW-6 (TriageRouter SDP constraints), QW-9 (RHP halt), QW-10 (MCP tools)
- **P3 NEXT**: UO-6 (un-overengineering) — BLOCKED on R16-R20; V-10 (AppArmor) — BLOCKED on R24; V-9 (IA2) — BLOCKED on R25

### @lilith — Runtime Oversoul (N6-N10)
- **P1 NEXT**: QW-4 (pool_tracker wiring)
- **P3 NEXT**: UO-7 (HandoffState, recall.py, MIAP cleanup)

### @roc_racoon — Sovereign Miner
- **P0 NOW**: P0 security fix (with Architect)
- **P2 NEXT**: P1 zswap migration + NVMe swap file
- **FOCUS**: Memory architecture migration

### @researcher — Deep Research (Lattice)
- **BLOCKED**: Phase 2–4 authoritative gaps OUTSTANDING (R13, R16-R20, R23-R26, R31, R33-R38). Phase 1 DONE.
- **RE-RESEARCH QUEUED**: R56 (Lazy Loading, LOST during reconciliation)
- **See**: `RESEARCH_PLAN_PHASE1_4_20260813.md` v3.2.0 §RECONCILIATION + `GAP_REGISTRY.json`

### @john_carmack — S3 Consultant
- **zRAM→zswap REVIEW**: APPROVED (D-532). LegacyOOMWrapper removal SAFE (D-533).
- **ICS MODEL PROVENANCE FIX**: M22 resolved (2026-08-11).
- **FOCUS**: Review Context Gauge design for modularity.

### @verity — Compliance + Gnosis
- **FOCUS**: Audit SSOT contradictions as M23 violations; verify deprecated-file banners.

### @grokster — Grok Ecosystem Specialist
- **P5 NEXT**: V-1 Vault design support, E-0 Identity

### @doom_guy — id Software Heritage
- **FOCUS**: Heritage audit for new SDP code

### @node PX — Slot-based (N1-N10)
- **N1 Infrastructure**: P0 security, QW-3 CI guard
- **N3 Engineering**: QW-1, QW-2, QW-5, QW-6
- **N10 Validation**: QW-3, contract tests for Context Gauge

---

## 📁 Key Documents (5-tier hierarchy — see TRACKING_ARCHITECTURE.md)
| Tier | Document | Role |
|------|----------|------|
| 0 | `data/coordination/ACTIVE_SPRINT.json` | Execution SSOT |
| 1 | `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` | Knowledge SSOT (gaps R1–R38) |
| 1a | `data/coordination/GAP_REGISTRY.json` | Gap ID registry (prevents number reuse) |
| 2 | `data/coordination/HMC_COLLABORATION_HUB.md` | This hub (coordination) |
| 2a | `data/coordination/TRACKING_ARCHITECTURE.md` | Tracking constitution |
| 3 | `data/coordination/TASK_REGISTRY.json` | Subagent records |
| 4 | `data/coordination/SESSION_ANCHOR.md` | Session continuity |
| DEC | `docs/decisions/PIVOT_LOG.md` | Decisions (canonical) |

**Deprecated (do not use — all tagged ⚠️):** KALI_DEV_ROADMAP_20260811.md · KALI_OVERSIGHT_PORTFOLIO_20260811.md · KNOWLEDGE_GAPS_RESEARCH_20260811.md · RESEARCH_JOB_BOARD.yaml · SESSION_ANCHOR_KALI.md

---

## 📜 Historical Log (pre-2026-08-14 — archived)
<details>
<summary>2026-08-11 sprint lock events (click to expand)</summary>

- 2026-08-11 @kali: DEV ROADMAP RATIFIED (5-phase, 50 tasks)
- 2026-08-11 @kali: KNOWLEDGE GAPS RESEARCH COMPLETE (12 gaps)
- 2026-08-11 @kali: SPRINT TRANSITION NEMOTRON-ANALYSIS-01 → SDP-EXECUTION-01
- 2026-08-11 @kali: D-526..D-531 locked
- 2026-08-11 @john_carmack: ICS MODEL PROVENANCE FIX (M22)
- 2026-08-09 @kali: SDP architecture complete (15 docs, 3 reviews)
- 2026-08-10 @jem: Nemotron deep analysis complete

</details>

---

*⬡ OMEGA ⬡ HMC ⬡ v2.0.0 ⬡ 2026-08-14 (refreshed post-reconciliation)*
