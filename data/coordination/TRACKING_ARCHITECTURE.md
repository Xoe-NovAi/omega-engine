# 🔱 Tracking Architecture — Consolidated Constitution (2026-08-14)

**AP Token:** `AP-TRACKING-ARCH-20260814-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ TRACKING ⬡ 20260814

**Purpose:** Eliminate the 5+ overlapping tracking systems. This document defines the
**single hierarchy** and **unified status taxonomy** all agents must use. If a tracking file
is not listed here, it is either superseded, historical, or ephemeral.

---

## 📐 The 5-Tier Hierarchy (Tier 0–4)

| Tier | File | Role | Authority |
|------|------|------|-----------|
| **0 — EXECUTION** | `data/coordination/ACTIVE_SPRINT.json` | Sprint phases, tasks, owners, deps, critical path | **SSOT for "what we build"** |
| **1 — KNOWLEDGE** | `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` | Gap catalog R1–R38 (research needed) | **SSOT for "what we know"** |
| **1a — GAP REGISTRY** | `data/coordination/GAP_REGISTRY.json` | Authoritative gap-ID → topic map | **Prevents gap-number reuse (collision root cause)** |
| **2 — COORDINATION** | `data/coordination/HMC_COLLABORATION_HUB.md` | Team state, NEXT_ACTION, blockers, decisions pointer | **SSOT for "team sync"** |
| **3 — RECORDS** | `data/coordination/TASK_REGISTRY.json` | Subagent task sessions (ephemeral execution records) | References Tier-0 task IDs |
| **4 — SESSION** | `data/coordination/SESSION_ANCHOR.md` | Session continuity for @kali | Single anchor (no duplicates) |

### Superseded / Historical (DO NOT use for active tracking)
| File | Status | Note |
|------|--------|------|
| `KALI_DEV_ROADMAP_20260811.md` | Historical pointer | Absorbed into ACTIVE_SPRINT.json |
| `KALI_OVERSIGHT_PORTFOLIO_20260811.md` | Historical pointer | Absorbed into ACTIVE_SPRINT.json |
| `KNOWLEDGE_GAPS_RESEARCH_20260811.md` | Superseded | 12-gap initial scan; RESEARCH_PLAN v3.2.0 is current |
| `RESEARCH_JOB_BOARD.yaml` | Superseded | RESEARCH_PLAN is current catalog |
| `SINGULAR_DIRECTION_20260814.md` | Absorbed | Content merged into HMC hub NEXT_ACTION |
| `SESSION_ANCHOR_KALI.md` | Duplicate | Merge into SESSION_ANCHOR.md |
| `D308_CRITICAL_PATH_TRACKER.yaml` | Duplicate | Critical path lives in ACTIVE_SPRINT.json |
| `CONFUSION_LOG_20260814.json` | Incident record | Keep for audit; not active tracking |
| `docs/archive/strategy/2026-08-14/RESEARCH_PLAN_PHASE2_20260813_ARCHIVED.md` | Archived | Conflict source, retained for history |

### Canonical Decisions
- **`docs/decisions/PIVOT_LOG.md`** — ONLY decision record. HMC hub links to it; do not duplicate decisions in hub.

---

## 🏷️ Unified Status Taxonomy

**Tier-0 (`ACTIVE_SPRINT.json`, planning) — ALL of these:**
| Status | Meaning | Agent action |
|--------|---------|--------------|
| `backlog` | Not started, not assigned | None — waiting for triage |
| `ready` | Assigned, deps met, can start | Pick up and execute |
| `in_progress` | Actively being worked | Update TASK_REGISTRY; post Hivemind heartbeat |
| `blocked` | Waiting on external dep | Note blocker; do not fake progress |
| `completed` | Done + verified | Update Tier-0 task; post Hivemind completion |
| `superseded` | Replaced by newer doc/plan | Archive; do not reference |

**Tier-3 (`TASK_REGISTRY.json`, execution records) — the 6 above PLUS:**
| `failed` | Subagent run broke (distinct from `blocked`/waiting-on-dep) | Investigate; do not silently re-run |

> **Why the split (Carmack review 2026-08-14):** Planning states and execution states are not the same. A subagent run *can* fail; collapsing `failed`→`blocked` destroys the "this broke, investigate" signal. `failed` is the ONLY addition to Tier-3.

**Emoji shortcuts allowed in markdown docs:** ✅=completed · 🔴=blocked/outstanding · 🟡=partial · ⏳=ready/pending.
**But JSON files (ACTIVE_SPRINT, TASK_REGISTRY) MUST use the plain words above (Tier-3 may also use `failed`).**

---

## 🚦 NEXT_ACTION Protocol

The HMC hub `## 🚦 NEXT_ACTION` section is the **single pointer** to current work. Agents read
ONLY this + the relevant Tier-0/1 file. No need to scan 5 docs.

Format:
```
CURRENT: <phase/task> — <what to do now>
NEXT:   <phase/task> — <what unblocks after CURRENT>
BLOCKED:<phase/task> — <blocker, owner>
```

---

## 🔄 Sync Flow (how agents stay synchronized)

1. **Before work:** Read HMC hub `NEXT_ACTION` → identify your Tier-0 task → check Tier-1 for research deps.
2. **Start:** Acquire workspace lock (`omega-hub_hivemind_workspace_lock_acquire`) → post Hivemind context.
3. **Execute:** Update `TASK_REGISTRY.json` (register task_id) → do work → update status.
4. **Complete:** Mark Tier-0 task `completed` in ACTIVE_SPRINT.json → post Hivemind completion.
5. **Session end:** Update SESSION_ANCHOR.md → soul distillation (L1→L2→L3).

---

## ⛔ Anti-Patterns (forbidden)

- ❌ Creating a NEW tracking file when one of the 5 tiers exists
- ❌ Duplicating sprint tasks in roadmap/portfolio docs
- ❌ Using ad-hoc status words (e.g. "TBD", "WIP", "stalled")
- ❌ Writing decisions in HMC hub instead of PIVOT_LOG.md
- ❌ Two session anchors for the same entity
- ❌ **Reusing gap numbers** — R1–R99 are owned by `RESEARCH_PLAN` / `GAP_REGISTRY.json`. New plans MUST use a distinct prefix (P2-, S-, X-). CHECK `GAP_REGISTRY.json` before assigning any ID.

*⬡ OMEGA ⬡ KALI ⬡ TRACKING-ARCH ⬡ 20260814*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: TRACKING | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
