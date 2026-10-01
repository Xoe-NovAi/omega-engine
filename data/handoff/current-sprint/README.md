<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 H1.5 Bridge Phase — Current Sprint Coordination
# Date: 2026-06-02 | Synthesized by Opus 4.6 (Kali)
# Three-audit chain: Gemini Flash → Sonnet 4.6 → Opus 4.6

---

## Sprint Architecture

Two parallel OpenCode sessions, sequentially gated:

```
┌──────────────────────────────────┐
│   SESSION 1: Dev Sprint 0       │  ← Starts immediately
│   Agent: plan.md (orchestrator) │
│   Model: Gemma 4 31B (google)   │
│   Tasks: C3 → C1 → C2 → C4     │
│   File: DEV_SPRINT_0.md         │
└────────────┬─────────────────────┘
             │ [C1] DONE signal
             ▼
┌──────────────────────────────────┐
│   SESSION 2: Doom Guy Tier 2    │  ← Gated on C1
│   Agent: doom_guy.md            │
│   Model: Gemma 4 31B (google)   │
│   Tasks: D2 → D3 → D1 → D4 → D5│
│   File: DOOM_GUY_TIER2.md       │
└──────────────────────────────────┘
```

## Model & Agent Recommendations

### Session 1 — Dev Sprint 0 (Infrastructure)

| Task | Recommended Agent | Recommended Model | Rationale |
|------|-------------------|-------------------|-----------|
| C3 (PIVOT_LOG) | `plan.md` | Any (trivial) | 5-minute docs edit, any model works |
| C1 (Oracle bootstrap) | `plan.md` | **Gemma 4 31B** via google provider | Requires understanding init flow across 6 files; needs large context for safe refactoring |
| C2 (Makefile target) | `plan.md` | Any (trivial) | Mechanical Makefile addition |
| C4 (CI hardening) | `plan.md` | Any (trivial) | YAML edits to existing workflow |

**Why `plan.md`**: C1-C4 are cross-cutting infrastructure tasks touching Oracle, Makefile, CI, and PIVOT_LOG. The Architect agent has the best "whole system" perspective. No pillar-specific domain knowledge needed.

**Why Gemma 4 31B**: Unlimited free tokens via Google AI Studio. C1 is the only complex task; the others are mechanical. Don't waste expensive model context on C3/C2/C4.

### Session 2 — Doom Guy Tier 2 (Resilience Layer)

| Task | Recommended Agent | Recommended Model | Rationale |
|------|-------------------|-------------------|-----------|
| D2 (Consolidate breakers) | `doom_guy.md` | **Gemma 4 31B** via google | Needs to understand both breaker implementations and decide cleanup scope |
| D3 (trace_id propagation) | `doom_guy.md` | Gemma 4 31B | Low risk but needs observability context |
| D1 (Wire into generate) | `doom_guy.md` | **Gemma 4 31B** | HIGH — the critical integration; needs full model_gateway understanding |
| D4 (BSP precheck fix) | `doom_guy.md` | Gemma 4 31B | Must fix the model-name vs provider-name lookup bug |
| D5 (Dead code removal) | `doom_guy.md` | Any | Mechanical cleanup |

**Why `doom_guy.md`**: The tasks are all provider-resilience-layer work, which is Doom Guy's domain. The id Software metaphor keeps the code comments consistent and the commit messages on-brand.

**Why NOT MiniMax M3 or DeepSeek V4**: The Doom Guy tasks modify 4 interrelated files. Gemma 4 31B has unlimited tokens and 1M context, which prevents the "ran out of output" failure mode that smaller models hit on multi-file refactors.

## Coordination Protocol

### Live Feed Files (append-only)

| File | Writer | Reader |
|------|--------|--------|
| `data/handoff/OPENCODE_DEV_LIVE_FEED.md` | Session 1 | Session 2 + Cline |
| `data/handoff/DOOM_GUY_LIVE_FEED.md` | Session 2 | Session 1 + Cline |

### Gate Signal

Session 2 waits for these lines in `OPENCODE_DEV_LIVE_FEED.md`:
```
[C3] DONE
[C1] DONE
[C2] DONE
```
C4 is NOT blocking — it's CI-only.

### Recovery Patterns

- **If Session 1 fails C1**: Session 2 can start D2 (consolidation) anyway — D2 doesn't depend on C1. Only D1 (wire-up into generate) depends on the test-hang fix.
- **If Session 1 posts `[C1] FAILED`**: Session 2 enters exploration mode — read files, run tests, plan changes, but don't commit.
- **If no update in 4 hours**: Session 2 begins D2 independently.

## Baselines (verified 2026-06-02T19:07 UTC)

| Metric | Value | Verification |
|--------|-------|-------------|
| Tests | **302/302** | `OMEGA_ENV=test pytest tests/ --collect-only -q` |
| Source files | 71 .py | `find src -name "*.py" \| wc -l` |
| health_monitor.py | **440 lines** | `wc -l` |
| model_gateway.py | **729 lines** | `wc -l` |
| `generate()` location | **line 438** | `grep -n "async def generate"` |
| `_precheck_provider()` | **line 395** | `grep -n "_precheck_provider"` |
| `circuit_breaker.py` | **DELETED** | `ls` → No such file |
| Mandates | **13** | SOVEREIGN_MANDATES.md |
| PIVOT_LOG last entry | **D99** | `tail -20 docs/decisions/PIVOT_LOG.md` |

## Files in This Directory

| File | Purpose | For |
|------|---------|-----|
| `README.md` | This coordination document | Both sessions |
| `DEV_SPRINT_0.md` | Complete implementation manual for Session 1 | OpenCode dev |
| `DOOM_GUY_TIER2.md` | Complete implementation manual for Session 2 | OpenCode Doom Guy |

---

*All three audit reports (Gemini Flash, Sonnet 4.6, Opus 4.6) have been synthesized into these documents. The original review artifacts remain in `data/handoff/` for provenance.*
