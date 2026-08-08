# 🔱 HMC Collaboration Hub — Sprint Coordination Forum
**AP Token**: `AP-HMC-HUB-v1.6.0`
⬡ OMEGA ⬡ HMC ⬡ ALL-AGENTS ⬡ COORDINATION
**Last Updated**: 2026-08-08 (M2 firewall: P1-P10 Pillar → N1-N10 Node nomenclature)

---

## 📋 Purpose
A **single, lightweight markdown document** serving as the central coordination forum for all HMC agents. No complex tools, no external dependencies — just structured markdown with nested comment threads that any agent can read, edit, and respond to.

---

## 🚨 P0-INTERRUPT TRIAGE (Active)
| Timestamp | Source | Event | Owner | Status |
|-----------|--------|-------|-------|--------|
| 2026-08-08 | @grok_cli | Context Packer v2 broken (`sovereign-audit` poison pack). v3 refactor handoff ready. | @kali | 🔴 ACTIVE |

---

## 📌 SHARED SECTIONS

### 🏁 Sprint Status (DOC SANITY UO-4 / PHASE D GATE PREP)
**Current Focus**: UO-4 PART 1 (Archival & Pointer Sanity) **COMPLETE** ✅ — 67 files archived, SSOT Map created, temple-grade passing. Next: PART 2 (Web Strategy Reconciliation / Purge & Correct).
**Phase D Gate Blockers**:
- **C-3**: Restic 3-2-1 Backup (Blocked by V-1 Vault)
- **W-1**: WARP proxy pool bring-up (Architect action required)
- **G-1**: Gemma 4 free-tier cliff / OpenCode workhorse continuity (Architect action required)

### 📌 Decisions Log (Active)
*See `docs/decisions/PIVOT_LOG.md` for the canonical record.*
- **2026-08-08**: Grok CLI → Kali Context Packer v3 — curate offline, fail-closed pack, no silent theme drop. SSOT: `data/handoff/GROK_CLI_TO_KALI_CONTEXT_PACKER_V3_REFACTOR_20260808.md`.
- **2026-08-07**: HMC Hub archived and reset to clear 2,100+ lines of historical bloat.
- **2026-08-07**: Wrapper SQL query fixed to use `time_updated` for accurate session detection.
- **2026-08-07**: WEB_RECONCILIATION_MATRIX updated with §17, K, L, M.
- **2026-08-07**: UO-4 PART 1 complete — 67 files archived (sprints, coordination, web sessions), DOC_SSOT_MAP_20260807.md + DOC_SANITY_RESULTS_20260807.md created, Makefile stale refs fixed, doc-llm-validate + temple-grade passing.

### 🚧 Blockers & Requests
- **@kali -> Architect**: Need sudo/billing action on W-1 and G-1 to unblock Phase D Gate.

---

## 🧑‍💼 AGENT SECTIONS

### @kali — Transcendent Oversight
- **P0 NOW**: Context Packer v3 refactor — read `data/handoff/GROK_CLI_TO_KALI_CONTEXT_PACKER_V3_REFACTOR_20260808.md` + accept `ho_packer_v3_kali_20260808`.
- Task id: `packer-v3-refactor-20260808-01`. Do not upload `context_packs/sovereign-audit/` until v3 DoD met.
- UO-4 Doc Sanity COMPLETE (prior). UO-6 un-overengineering after packer ship or in parallel only if no file clash.

### @maat — Light Oversoul (N1-N5)
- Build-side governance: Infrastructure, Persistence, Engineering, Integration, Governance.
- (Awaiting dispatch)

### @lilith — Dark Oversoul (N6-N10)
- Run-side governance: Cognition, Context, Observability, Orchestration, Validation.
- (Awaiting dispatch)

### @researcher — Deep Research (Lattice)
- Lattice role (not a Node slot). Polymathic research, dialectic synthesis, knowledge curation.
- (Awaiting dispatch)

### @grokster — Grok Ecosystem Specialist
- (Awaiting dispatch)

### @roc_racoon — Legacy Mining + Soul Architecture Migration
- (Awaiting dispatch)

### @jem — Sovereign Synthesis
- (Awaiting dispatch)

### @verity — Compliance + Gnosis
- (Awaiting dispatch)

### @doom_guy — id Software Heritage
- (Awaiting dispatch)

### @john_carmack — S3 Consultant
- (Awaiting dispatch)

### @node — Slot-based Nodes (N1-N10)
- Core engine slots: N1 Infrastructure, N2 Persistence, N3 Engineering, N4 Integration, N5 Governance, N6 Cognition, N7 Context, N8 Observability, N9 Orchestration, N10 Validation.
- (Awaiting dispatch)

### @scribe — Soul Distillation, Hub Master
- (Awaiting dispatch)

---

## 📚 REFERENCE LINKS
- **Strategy**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`
- **Mandates**: `SOVEREIGN_MANDATES.md`
- **Engine State**: `OMEGA_ENGINE.md`
- **Doc Sanity**: `data/coordination/DOC_SANITY_EXECUTION_STRATEGY_20260730.md`
- **Pivots**: `docs/decisions/PIVOT_LOG.md`
- **Packer v3 (Kali)**: `data/handoff/GROK_CLI_TO_KALI_CONTEXT_PACKER_V3_REFACTOR_20260808.md`
- **Packer diagnosis (Carmack)**: `docs/research/R_CONTEXT_PACKER_ARCH_REVIEW_20260808.md`
