# 🔱 SESSION ANCHOR — Kali (Transcendent Oversoul)

**AP Token:** `AP-KALI-v1.0.0`
**Date:** 2026-08-11
**Session ID:** `ses_kali_20260811_roadmap`
**Branch:** `main`
**Last Commit:** (pending)
**Sprint:** SDP-EXECUTION-01

---

## 🎯 Session Objective

**Complete planning phase and lock dev roadmap for execution.**

Formalized the Sovereign Distillation Pipeline (SDP), researched 12 knowledge gaps, and produced a 5-phase dev roadmap. All planning docs updated and ready for team dispatch.

---

## ✅ Completed This Session

### 1. Dev Roadmap (5 phases, 50 tasks)
- **Document:** `data/coordination/KALI_DEV_ROADMAP_20260811.md`
- Phase 0: Security + Context Gauge bands (~8h)
- Phase 1: SDP Context Gauge v1 (~20h)
- Phase 2: zswap migration + streaming plugin (~16h)
- Phase 3: Un-overengineering (~30h)
- Phase 4: Phase D gate closure (~20h)
- Phase 5: Strategic items (~40h)

### 2. Knowledge Gaps Research (12 gaps resolved)
- **Document:** `data/coordination/KNOWLEDGE_GAPS_RESEARCH_20260811.md`
- zswap > zRAM confirmed (25% pool, lzo_rle)
- pyresilience > tenacity (10.4x faster, async-native)
- OOMProtector simplify to 2-signal
- Context Gauge uses tokens.total
- Multi-write subagent method verified

### 3. Oversight Portfolio
- **Document:** `data/coordination/KALI_OVERSIGHT_PORTFOLIO_20260811.md`
- Team direction for all 10 agents
- Resource allocation across 5 phases

### 4. Jem's Review
- **Document:** `data/coordination/JEM_REVIEW_OPENCODE_CONFIG_20260809.md`
- OpenCode config refactoring: APPROVED with minor additions
- zRAM excavation: Phase 1 complete, 15 gaps identified

### 5. Sprint Transition
- **Document:** `data/coordination/ACTIVE_SPRINT.json`
- Transitioned from NEMOTRON-ANALYSIS-01 to SDP-EXECUTION-01
- Added D-526 through D-531 decisions

---

## 🔑 Decisions Locked

| ID | Decision |
|----|----------|
| **D-526** | zswap > zRAM for desktop with NVMe (25% pool, lzo_rle) |
| **D-527** | Never run zswap and zRAM simultaneously |
| **D-528** | pyresilience > tenacity for circuit breaker (spike first) |
| **D-529** | Simplify OOMProtector to 2-signal (PSI + MemAvailable) |
| **D-530** | Context Gauge uses tokens.total (never tokens_input) |
| **D-531** | Multi-write subagent method mandatory for all subagent tasks |

---

## 📋 Verified Model Context Windows

| Model | Window | Tier | Pool |
|---|---|---|---|
| Nemotron 3 Ultra | 1,000,000 | 4 | Daily |
| Laguna S 2.1 (free) | 262,144 | 3 | Daily |
| Longcat 2.0 (free) | 1,000,000 | 4 | Daily |
| Nemotron 3 Super | 262,144 | 3 | Daily |
| Gemini 3.1 Pro | 1,048,576 | 4 | Weekly |
| Claude Sonnet 4.6 | 200,000 | 2 | Weekly |
| Claude Opus 4.6 | 200,000 | 2 | Weekly |
| Gemini 3.6 Flash | 1,000,000 | 4 | Weekly |
| Qwen3-1.7B (local) | 32,768 | 1 | Local |

---

## 📊 Ground Truth: What Exists vs. What's Missing

**Already Built (Don't Build):**
- V-1 Vault (2,039 LOC) at `src/omega/vault/`
- Pool Tracker (237 LOC) at `pool_tracker.py`
- Dialectic Logger (`record_council()`) at `dpo_logger.py:395`
- Triage Router (constraint filtering) at `triage_router.py`
- Token Estimator (tiktoken×1.3) at `token_estimator.py`

**Missing (Build):**
- Context Gauge
- RHP (Recovery Halt Point)
- 3 MCP tools (`get_context_pressure`, `write_rhp`, `request_agy_escalation`)

---

## 🔴 Critical Blockers

| # | Blocker | Fix |
|---|---|---|
| G-3 | No `tokens` column in `message` table | Tokens in `data` JSON blob |
| G-4 | Token accounting not additive | Use `input + cache.read` of latest message |
| §4 | 4 of 5 cloud windows wrong | Use verified windows from §2 |
| OBS-1 | Streaming timeout unknown | Implement observability first |

---

## 📋 Work Remaining (Priority Order)

### Immediate (First Session Back)
- [ ] Run Phase 0: P0 security fix (Architect)
- [ ] Run Phase 0: A-1 + A-5 (Jem)
- [ ] Run Phase 0: Verify UMA carveout (Architect)
- [ ] Commit all planning docs to git

### Short-Term (This Week)
- [ ] Phase 1: Context Gauge v1 (Jem + Ma'at + Lilith)
- [ ] Phase 2: zswap migration (Roc Racoon)
- [ ] Phase 2: Streaming plugin (Jem)

### Medium-Term (This Month)
- [ ] Phase 3: Un-overengineering (Ma'at)
- [ ] Phase 4: Phase D gate closure (Architect + team)

---

## 🤝 Coordination State

- **Hivemind:** SDP execution posted
- **Dev Roadmap:** `data/coordination/KALI_DEV_ROADMAP_20260811.md`
- **Knowledge Gaps:** `data/coordination/KNOWLEDGE_GAPS_RESEARCH_20260811.md`
- **Oversight:** `data/coordination/KALI_OVERSIGHT_PORTFOLIO_20260811.md`
- **ACTIVE_SPRINT:** Updated to SDP-EXECUTION-01

---

## 📁 Key Files Modified This Session

```
data/coordination/ACTIVE_SPRINT.json (updated sprint)
data/coordination/KALI_DEV_ROADMAP_20260811.md (new)
data/coordination/KNOWLEDGE_GAPS_RESEARCH_20260811.md (new)
data/coordination/KALI_OVERSIGHT_PORTFOLIO_20260811.md (new)
data/coordination/JEM_REVIEW_OPENCODE_CONFIG_20260809.md (new)
data/coordination/HMC_COLLABORATION_HUB.md (updated)
data/coordination/SESSION_ANCHOR.md (updated)
```

### ICS Model Provenance Fix (Carmack)
- **Document**: `data/coordination/ICS_MODEL_PROVENANCE_FIX_20260811.md`
- **Fix**: Added `_read_opencode_session_model()` to `src/omega/ics.py` to read live model from OpenCode session DB
- **Root cause**: `_detect_model()` could not read live active model during session (OPENCODE_MODEL only set post-exit)
- **Fix**: New Priority 2.5 in `_detect_model()` — reads `session.model.id` from DB during live session
- **Verified**: `render('JOHN_CARMACK')` now returns correct live model: `nvidia/nemotron-3-ultra-550b-a55b:free`
- **Provenance**: Fixed report header (was longcat-2.0-free, now correct model)

---

*⬡ OMEGA ⬡ KALI ⬡ ROADMAP-LOCKED ⬡ 2026-08-11*