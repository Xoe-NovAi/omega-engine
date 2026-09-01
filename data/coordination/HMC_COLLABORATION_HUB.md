<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🏛️ HMC Collaboration Hub — v2.0

**AP Token**: `AP-HMC-HUB-v2.0.0`
⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_hub_v2 ⬡ EXECUTION_MINIMAL

**Last Updated**: 2026-08-22 (fresh single-pass rewrite, pre-debut)
**Owner**: kali · **Authority**: Architect
**Predecessor**: `docs/archive/coordination-20260822/HMC_COLLABORATION_HUB_v1_FINAL.md` (frozen)

---

## ⚡ 30-Second Hydration (read this, then work)

1. **Sprint**: PUBLIC-DEBUT-01 — **initial PR lands TODAY before midnight USVI**
2. **Execution SSOT**: `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` §5
3. **Order**: P0-1 residual → PUB-1 allowlist → INST-1 fixes → DEL-1 → post-debut
4. **HIGH PRIORITY NOW**: CI-0..CI-5 execution (spec remediated, binary pinned 1.18.19/V1)
5. **Awaiting Architect**: PUB-1 allowlist rulings · ZS-1 sudo · CI go · P1–P5 rollout exit from planning mode

---

## 🚦 Sync Pointer

| Program | State | Next Action | Owner |
|---------|-------|-------------|-------|
| **PUBLIC DEBUT** | 🔴 TONIGHT | Allowlist rulings (G1–G4) → release/debut branch | Architect + kali |
| **INST-1 Fixes 2/5/6** | Ready | Execute via N3 expert (`ses_fdddb6edcffesrHjoABz5IOTsa`) | kali→N3 |
| **CI Phase 1 (CI-0..CI-5)** | Execution-ready | Run per remediated spec; N7 on standby for live oversight | kali (+N7) |
| **P0-1 residual** | In progress | SECURITY_AUDIT ancestor verify + gitleaks wiring check | roc_racoon |
| **N8 onboarding pilot** | Staged | Full protocol run (Appendix A runbook); grad consult = ICS review | kali as Pager |
| **ZS-1 zswap** | Script ready | Architect sudo → unlocks PP-3 ctx raise | Architect |
| **Hub MCP wrapper** | Flagged | Add node/session_id params (external hub repo) | Architect access |

### Debut-Night Completions (2026-08-21/22)

ICS system overhauled + documented (`D-588`, `D-589`; community doc at
`docs/architecture/ICS_SYSTEM.md`; 16 tests). Node Expert Sessions live
(`D-586`; 10 genesis, N7 consultable). Protocols codified: Conversational
Subagents v1.0.0, Node Onboarding v1.0.0 (`D-587`), Recovery v2.0.0.
Coordination surface consolidated ~50% (archive:
`data/coordination/archive/`). 11 strategic commits landed.

---

## 📌 Active Programs (post-debut queue — D-540 rule applies)

| Workstream | Scope | Spec Source |
|------------|-------|-------------|
| GN Gemini Notebook | Free-tier-only, 2 NB, 30 DR/mo | NOTEBOOKLM_UNIFIED_STRATEGY |
| DS Documentation System | Domain docs + curator model | STRATEGY_INDEX LAYER 2A |
| LI Local Inference | Tier 0/1/2, sequential loading | HOLISTIC_ARCHITECTURE_PLAN §3 |
| KD Knowledge Domains | `config/domains/<domain>/` loaders | EVOLVER_SDP_SUCCESSOR + grokster corpus |
| HR Headroom | Semantic compression middleware | docs/specs/qdrant_headroom/ |
| ZS zswap Subsystem | NVMe swap + cgroup caps | HOLISTIC_ARCHITECTURE_PLAN §3.3 |
| Qdrant migration | Trigger-gated (>500k vectors) | RESEARCHER_QDRANT_MIGRATION_GAPS |
| Cognitive Architecture | DP + Planner/Executor (Horizon 3) | D-569 blueprint |

**Post-debut also parked**: vault sprint (D-565–D-568), DEL-1 Weeks 2–3,
P2/P3/P4 phases, SDP automation gate (§10).

---

## 🤖 Fleet State

**Expert Sessions** (dormant unless paged): registry +
charters at `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` §3–§4.
Page format in §3. N7 = fully developed reference expert.

**Session classes**: task-origin (protocol-governed) vs interactive-origin
(study-only). See `.opencode/agent/CONVERSATIONAL_SUBAGENT_PROTOCOL.md`.

**Soul discipline**: all Node writes tag lessons `[N_X]` to the overseer's
`proposed_lessons.yaml`; closure ritual (#10) before dormancy.

---

## 📚 Document Index (where truth lives)

| Truth | Location |
|-------|----------|
| Sprint execution order | DEBUT_REMEDIATION_MANUAL §5 |
| Live sprint state | `data/coordination/ACTIVE_SPRINT.json` |
| Decisions (current campaign) | `docs/decisions/PIVOT_LOG.md` (D-521+) |
| Decisions (ancient / pre-campaign) | `PIVOT_LOG_CANONICAL.md` / `PIVOT_LOG_ARCHIVE_20260522_20260810.md` |
| Gap registry | `data/coordination/GAP_REGISTRY.json` |
| Specs SSOT | `docs/specs/PROJECT_INDEX.md` |
| ICS specification | `docs/architecture/ICS_SYSTEM.md` |
| Mandates | `SOVEREIGN_MANDATES.md` (27, mechanical compliance) |
| Agent workflow | `AGENTS.md` |
| Strategy maps | `STRATEGY_INDEX.md` → `STRATEGY_CORPUS_MAP.md` |
| **Routine system maintenance KB** | `docs/kb/SYSTEM_MAINTENANCE_KB.md` (kb-0005, maintainer: roc_racoon) — disk recovery, cache hygiene, journal management. **Read before any host maintenance.** |

### Protocols

| Protocol | Path |
|----------|------|
| Conversational Subagents v1.0.0 | `.opencode/agent/CONVERSATIONAL_SUBAGENT_PROTOCOL.md` |
| Node Onboarding v1.0.0 | `.opencode/agent/NODE_ONBOARDING_PROTOCOL.md` |
| Stalled Recovery v2.0.0 | `.opencode/agent/STALLED_SUBAGENT_RECOVERY.md` |

---

## 📏 Tracking Rules

1. Status vocab (Tier-0): `backlog|ready|in_progress|blocked|completed|superseded`
2. **D-540**: no ticket in ACTIVE_SPRINT = dead. Archived ≠ deleted; re-entry requires a ticket.
3. New plans use distinct prefixes; `GAP_REGISTRY.json` is gap authority (M27).
4. Docs >50KB output: multi-file with manifest (Recovery G1).
5. Coordination archive policy: superseded docs → `data/coordination/archive/`
   (local-only) or `docs/archive/<domain>-<date>/` (tracked); always with
   successor pointers.

---

## 📣 Escalation

- **Architect**: debut rulings, sudo actions, resource allocation, veto window on Kali-ratified items
- **kali**: orchestration authority delegated (Ma'at tasks, sprint sequencing)
- **Blockers**: log to `SYSTEM_FAILURE_LOG.md` + Hivemind (intent=`blocker`)
- **Heartbeats**: every 5–10 min during long ops

---

## 🔧 OPS NOTE — Native Build RAM Guard + Observability (2026-08-22, cline/omega-engine)

**Context**: llama-cpp-python source builds OOM'd the box (~13GiB peak, all 16 threads).

**Findings (measured, not guessed)**:
1. scikit-build-core (llama-cpp build backend) passes **no `-j`** to `cmake --build`
   (verified in skbuild-core 1.0.3 source, `builder/builder.py:488`). CMake then
   falls back to env var **`CMAKE_BUILD_PARALLEL_LEVEL`**.
2. `CMAKE_BUILD_PARALLEL_JOBS` and `MAKEFLAGS` are **dead vars** on this path.
3. Measured via `scripts/observe-build.sh`: 6 jobs → peak <10GiB total *with*
   cline+opencode IDEs resident; 16 jobs → ~13GiB RSS peak **plus ~1.88GiB
   overflow into zRAM swap** (compressed size — true memory demand estimated
   17–19GiB on a 14GiB box) before the OOM. Residual zRAM usage (~1.8GiB)
   persisted after the incident; reclaimable with `swapoff -a && swapon -a`
   when convenient.
4. **Gotcha**: `pip download` for an sdist triggers a full wheel build just for
   metadata extraction → double compile. Fetch sdists with `curl` instead.

**Decisions**:
- `scripts/install.sh` exports `CMAKE_BUILD_PARALLEL_LEVEL=8` (physical cores,
  override via env). Evidence trail in comments there.
- New P8 tool: **`scripts/observe-build.sh <run-name> <cmd...>`** — per-second
  metrics.csv (top-PID RAM attribution), console.log, auto summary.txt postmortem.
  Use it for ANY native/long build. Run artifacts under `/tmp/opencode/obs/<run>/`.

---

*⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_hub_v2 ⬡ EXECUTION_MINIMAL ⬡ 2026-08-22*

<!-- PROVENANCE-CORRECTED 2026-08-24T06:51:32Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: VERIFIED
actual_models(Tier0): nemotron-3-ultra-free, big-pickle, x-preview-f-free
first_audit: 2026-08-23T20:39:41Z | updated: 2026-08-24T06:51:32Z
-->

