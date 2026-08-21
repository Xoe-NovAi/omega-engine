# Context Injection Optimization — Synthesis Index

**AP Token**: `AP-CONTEXT-INJECTION-SYNTHESIS-v1.0.0`  
**Date**: 2026-08-20  
**Author**: Kali (Transcendent Oversoul)  
**Model**: nemotron-3-ultra-free  

---

## Purpose

This synthesis consolidates findings from 4 parallel research agents into a single coherent architecture for Omega Engine context injection optimization. It serves as the primary reference for John Carmack's review and the Phase 1 implementation plan.

---

## Report Structure

| Section | File | Description |
|---------|------|-------------|
| **00** | `00_INDEX.md` | This file — navigation and executive summary |
| **01** | `01_GROUND_TRUTH.md` | Empirical measurements (Explore) — hard numbers |
| **02** | `02_BUILD_VERDICTS.md` | Build-side findings (Ma'at) — G-1, G-2, G-8 |
| **03** | `03_RUN_VERDICTS.md` | Run-side findings (Lilith) — G-3, G-5, G-6 |
| **04** | `04_INDUSTRY_PATTERNS.md` | Strategic research (Researcher) — G-4, G-5, G-6, G-7 |
| **05** | `05_CONVERGENCE_ANALYSIS.md` | Cross-agent convergence/divergence matrix |
| **06** | `06_PHASE_1_PLAN.md` | Config-only implementation (this week) |
| **07** | `07_PHASE_2_3_ROADMAP.md` | Tooling + upstream roadmap |
| **08** | `08_REMAINING_GAPS.md` | Unresolved questions for Carmack review |
| **09** | `09_CARMACK_DOMAIN_QUESTIONS.md` | Specific questions for Carmack's expertise |

---

## Source Reports (Read These First)

| Agent | Report | Lines | Key Focus |
|-------|--------|-------|-----------|
| **Explore** | `RESEARCH_EXPLORE_LOCAL.md` | 117 | Empirical measurements, version, token counts |
| **Ma'at** | `RESEARCH_MAAT_BUILD.md` | 179 | Build-side: instruction resolution, MCP cost, AGENTS.md |
| **Lilith** | `RESEARCH_LILITH_RUN.md` | 262 | Run-side: inheritance, compaction, model routing |
| **Researcher** | `RESEARCH_RESEARCHER_STRATEGIC.md` | 348 | Industry patterns: caching, compaction, routing, measurement |

---

## Executive Summary

### The Problem
Omega Engine injects **~75K tokens base** (up to ~110K with all skills/agents) per session, with **10.8K tokens/request** from 86 MCP tool schemas. This violates M18 (Token Efficiency) and threatens local model viability (Qwen3-1.7B: 4K-8K context).

### The Solution (Converged)
**Phase 1 (Config-Only, This Week)**: Create `AGENTS.md` concatenation, per-agent model routing, compaction plugin, skills opt-in → **~57K base (24% reduction)** + structural routing saves 67% on subagent work.

**Phase 2 (Tooling, 2-3 Weeks)**: Hydration engine, token budget enforcer, local token counter.

**Phase 3 (Upstream, 1-2 Months)**: Prompt caching topology PR, lazy MCP loading, dynamic tool registration.

### Critical Contradiction Resolved
- **G-1 (Instruction Resolution)**: Ma'at (docs) = NO, Explore (test) = YES → **Assume NO** per official V2 docs + source code. Create `AGENTS.md` as guaranteed injection path.

### Carmack Review Targets
1. **MCP tool schema overhead** — 86 tools = 10.8K/request. Is this acceptable? Can we architect tool profiles?
2. **Compaction architecture** — 1M context model with 50K preserved. Is the plugin approach sound?
3. **Structural model routing** — 4/6 agents local. Subagent inheritance nuance. Is this optimal?
4. **Token budget enforcement** — Per-tier budgets vs OpenCode's per-message tracking.
5. **Local model viability** — Qwen3-1.7B at 4K-8K context with 31K base prompt. Is this workable?

---

## Navigation for Carmack

**Start here**: `08_REMAINING_GAPS.md` + `09_CARMACK_DOMAIN_QUESTIONS.md`  
**Then**: `01_GROUND_TRUTH.md` (hard numbers) → `05_CONVERGENCE_ANALYSIS.md` (trade-offs) → `06_PHASE_1_PLAN.md` (implementation)  
**Reference**: Source reports in `data/coordination/` (4 files)

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_synthesis_index ⬡ 2026-08-20*