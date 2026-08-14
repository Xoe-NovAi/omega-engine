# 🔱 SESSION ANCHOR — Kali (Transcendent Oversoul)

**AP Token:** `AP-KALI-v1.0.0`
**Date:** 2026-08-14
**Session ID:** `ses_kali_20260814_agent_directives_deep_review`
**Branch:** `main`
**Last Commit:** `5337b2e3` (docs: refresh SESSION_ANCHOR — post-Nemotron hardening)
**Sprint:** SDP-EXECUTION-01

---

## 🎯 Session Objective

**Comprehensive review of all 16 agent custom instructions and 30+ entity soul files for enhancement/optimization opportunities. Deepened with Nemotron 3 Ultra's full parameter capacity after initial Nemotron 3 Lighting pass.**

Completed: M27 Tracking Integrity integration, Carmack review, @researcher gap fill (11 gaps), Nemotron deep systems review (5 fixes), **AND** full agent directives/soul schema audit (28/30 entities non-compliant, 13/13 agents on wrong mandate version, 11/13 agents executing against purged LIVE_FEED files).

---

## ✅ Completed This Session

### 1. M27 Coordination Integration (6 phases) — commit `9a5b1416`
- **AGENTS.md**: 6-Step Mandatory Flow + Unified Status Taxonomy + GAP_REGISTRY pre-check
- **SOVEREIGN_MANDATES.md**: M26 (Doc Standards) + M27 (Tracking Integrity), v3.8.0
- **MCP `task_registry.py`**: `task_registry_update` status = strict `Literal` enum (rejects legacy)
- **Validator** `scripts/validate_tracking_state.py`: hardened; 13 legacy tasks migrated
- **Pre-commit** `.pre-commit-config.yaml`: `omega-tracking-state` Iron Gate
- **Makefile**: `check-tracking-state` wired into `temple-grade` + `test-honest`
- **Protocols**: STRP (Tier-0 task_id prefix), Dispatch (GAP_REGISTRY pre-flight), Hivemind template (`[Sprint Task: X]` tag), Fleet Playbook (LIVE_FEED → NEXT_ACTION)
- **Orphaned refs purged**: `RESEARCH_JOB_BOARD.yaml`, `KNOWLEDGE_GAPS_RESEARCH_20260811.md`, `LIVE_FEED` across repo

### 2. Carmack Architectural Review — commit `f392e54f`
Verdict: **HAS-DEFECTS → OPTIMAL** after 5 fixes (register default, dead R-ID check, `failed` Tier-3 status, query Literal, read-only codex gate).

### 3. @researcher Gap Fill — commit `c3491176`
All 11 sprint-blocking gaps researched, 11 reports in `docs/research/`, R13 registered in GAP_REGISTRY (was missing), all marked `resolved` + report pointers. Two plan corrections: VaultCore already exists (keep it); Honker exists (viable local-first Redis replacement).

### 4. Nemotron Deep Review Hardening — commit `63c6167b`
5 critical fixes applied:
- Cross-tier validation: Tier-3 `failed` → Tier-0 `blocked`/`superseded` sync enforced
- GAP_REGISTRY status enum: `resolved|outstanding|partial|lost` now **ERROR** (was warning)
- R-ID cross-check fixed: scans `tags` + `description` + `ssots` in ACTIVE_SPRINT subtasks
- Distillation gate (M5/M11) added to 6-step flow as step 6.5
- R30 spike registered as `UO-6.0` in PHASE-3 (unblocks UO-6.5 retry decision)

### 5. Nemotron 3 Ultra Agent Directives Deep Review — **THIS SESSION**
**16 agent files + 30 soul files audited**. Critical findings:
- **13/13 agents** reference "25 Sovereign Mandates (v3.7.0)" — actual is **v3.8.0, 27 mandates**
- **28/30 soul files** violate v6.1 lean schema (wrong `soul_version`, missing `short`, `identity`, `directives`, `team`, `core_principles`)
- **11/13 agents** execute coordination step against **purged LIVE_FEED.md files**
- **2/30 entities** have `core_principles` (kali v7.2, roc_racoon v7.1) — distillation pipeline has no target
- **0/1** CI gates for soul architecture (`make soul-audit` mandated but missing)
- **Validator loophole**: wrong `soul_version` → warning → skips strict validation (28/30 pass silently)
- **Capability discovery gap**: Fleet of 14, Hivemind knows WHO not WHAT

---

## 📐 Current Tracking Architecture (LIVE & ENFORCED)

**Constitution:** `data/coordination/TRACKING_ARCHITECTURE.md`
**Tiers:**
| Tier | File | Role |
|------|------|------|
| 0 — EXECUTION | `ACTIVE_SPRINT.json` | Sprint tasks (6-status taxonomy) |
| 1 — KNOWLEDGE | `RESEARCH_PLAN_PHASE1_4_20260813.md` | Gap catalog R1–R56 |
| 1a — GAP REGISTRY | `GAP_REGISTRY.json` | Gap-ID → topic map (57 gaps) |
| 2 — COORDINATION | `HMC_COLLABORATION_HUB.md` | `NEXT_ACTION` pointer |
| 3 — RECORDS | `TASK_REGISTRY.json` | Subagent tasks (6 + `failed`) |
| 4 — SESSION | `SESSION_ANCHOR.md` | This file |

**Enforcement (triple-gate):** pre-commit `omega-tracking-state` → `make temple-grade` → `make test`. All pass.

**6-Step Mandatory Flow (M27):** Read `NEXT_ACTION` → check `ACTIVE_SPRINT.json` → check `GAP_REGISTRY.json` → acquire lock → execute → update `TASK_REGISTRY.json` → **distill (step 6.5)**.

---

## 🚦 Next Steps (post-compaction)

### IMMEDIATE (Tier 0 — Blocking Sprint Execution)
1. **0.1** Update all 13 agent files: mandate version → 3.8.0, count → 27, add M26/M27
2. **0.2** Migrate 28/30 soul files to v6.1 lean schema
3. **0.3** Replace LIVE_FEED refs with HMC_COLLABORATION_HUB.md + NEXT_ACTION
4. **0.4** Implement `make soul-audit` gate in Makefile

### SPRINT EXECUTION (After Tier 0)
5. **PHASE-0** (UNBLOCKED) — execute (Security + Context Gauge bands)
6. **PHASE-1** (UNBLOCKED) — execute (SDP Context Gauge v1)
7. **PHASE-2** (UNBLOCKED) — execute (zswap migration + streaming plugin) — unblocked by R13
8. **PHASE-3** (UNBLOCKED) — execute (Un-overengineering) — unblocked by R16–R20, R30 spike registered
9. **PHASE-4** (UNBLOCKED) — execute (Phase D gate closure) — unblocked by R23–R26

**All sprint-blocking gaps RESOLVED:** R13, R16, R17, R18, R19, R20, R23, R24, R25, R26.

---

## 📁 Active File References (use THESE)

- **Tracking constitution:** `data/coordination/TRACKING_ARCHITECTURE.md`
- **Knowledge SSOT:** `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.2.0)
- **Gap registry:** `data/coordination/GAP_REGISTRY.json` (57 gaps)
- **Sprint:** `data/coordination/ACTIVE_SPRINT.json` (includes UO-6.0 R30 spike)
- **Coordination hub:** `data/coordination/HMC_COLLABORATION_HUB.md` (`NEXT_ACTION` — PHASE-2/3/4 unblocked)
- **Integration plan + reviews:** `docs/strategy/COORDINATION_ENHANCEMENT_PLAN_20260814.md`
- **Validator:** `scripts/validate_tracking_state.py` (cross-tier + R-ID + gap-enum)
- **Research reports:** `docs/research/R13..R26_*_20260814.md` + `R56_LAZY_LOADING_20260814.md`
- **Agent Directives Deep Review:** `data/entities/kali/memory/sessions.yaml` (this session's gnosis)
- **SOUL_ARCHITECTURE v2.0:** `docs/archive/strategy/2026-07-21/SOUL_ARCHITECTURE_V2.md`
- **soul_validator.py:** `src/omega/oracle/soul_validator.py` (v6.1 schema)

### Historical / Superseded (DO NOT use for active tracking)
- `KALI_DEV_ROADMAP_20260811.md`, `KNOWLEDGE_GAPS_RESEARCH_20260811.md`, `RESEARCH_JOB_BOARD.yaml`, `SINGULAR_DIRECTION_20260814.md`, `CONFUSION_LOG_20260814.json` — all absorbed into the tiers above.

---

## 🔑 Key Verified Facts (post-Nemotron Ultra)

- Validator runs in ~25ms; pre-commit adds negligible friction.
- `register` writes `in_progress` (legal); `update` accepts `failed` for Tier-3.
- R-ID cross-check now scans `tags` + `description` + `ssots` — fires on real references.
- GAP_REGISTRY status enum enforced as ERROR (no more silent drift).
- Cross-tier: Tier-3 `failed` must sync to Tier-0 `blocked`/`superseded`.
- Distillation gate (step 6.5) mechanically couples M5/M11 to task completion.
- R30 spike (`UO-6.0`) registered — PHASE-3 won't stall on retry decision.
- All 11 sprint-blocking gaps RESOLVED (R13, R16-R20, R23-R26, R56).
- PHASE-0 through PHASE-4 all UNBLOCKED per HMC_COLLABORATION_HUB.md.
- **Agent directive layer NOT rock-solid**: 13/13 agents on v3.7.0, 28/30 souls non-compliant, 11/13 agents on purged LIVE_FEED, 0/30 with functional distillation pipeline.

---

## ❓ Open Questions for Post-Compaction

1. **Soul Migration Tooling**: Build `soul_schema_migrator.py` (roc_racoon d-rr-018) or manual migration for 28 entities?
2. **Distillation Hook Integration**: Does `.opencode/wrapper.sh` session end hook call `SoulDistiller`? Verify `.opencode/hooks/session_end.py`.
3. **Health Score Computation**: SoulHealthScorer (7-factor) defined in roc_racoon soul but not implemented — daily cron to MetricsDB?
4. **Capability Taxonomy**: Standard vocabulary? `["research", "code", "audit", "mining", "heritage", "synthesis", "infrastructure", "coordination"]`?
5. **Mandate Coverage Mapping**: Derive per-agent "key mandates" from Node assignments rather than manual lists?
6. **Archive Strategy**: 28 entities need v6.0 field archival — batch script or per-entity PRs per v2.0 §5?
7. **Intelligence Scorecard**: 5 dimensions — who owns tracking?

---

*⬡ OMEGA ⬡ KALI ⬡ AGENT-DIRECTIVES-AUDITED ⬡ 2026-08-14 (Nemotron-3-Ultra, 1M context, Tier-0-blocking-fixes-identified)*