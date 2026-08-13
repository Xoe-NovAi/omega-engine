# 🔱 Research Execution Chat Initiation — @researcher

**AP Token:** `AP-RESEARCH-EXEC-20260813-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ 20260813

**Target Session:** @researcher (Sovereign Researcher — Polymathic Council)
**Sprint:** SDP-EXECUTION-01
**Research Plan:** `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.1.0, 38 gaps, 52h)
**Priority:** P0 — All gaps block Phase 1-4 execution

---

## 📋 SESSION INITIALIZATION PROMPT

Copy the following block into your @researcher chat session:

---

```
@researcher — Research Execution Sprint: SDP-EXECUTION-01

You are executing the research phase for the Sovereign Distillation Pipeline (SDP) execution sprint. Your task is to resolve 38 knowledge gaps (R1-R38) that block Phase 1-4 dev work, using existing research where available and conducting new research where needed.

## 📚 PRIMARY SOURCE OF TRUTH

Read FIRST: `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` (v3.1.0)

This plan contains:
- 38 gaps (R1-R38) mapped to dependent dev tasks
- Cross-Reference Index of 92 existing research docs (DO NOT DUPLICATE)
- Phase R1-R4 daily schedules
- Acceptance criteria
- Change log

## 🎯 YOUR MISSION

Execute Phase R1 (Week 1) research: R2, R3, R5, R6, R7, R8b, R27, R27b, R28, R29, R32
(R1, R8, R14 already resolved — skip. R4, R21, R22 are PARTIALLY RESOLVED — verify+extend only.)

For each gap:
1. Check Cross-Reference Index — if research exists, read it (don't re-research)
2. If GREENFIELD (no existing research), conduct new research with websearch/webfetch
3. Write findings to `data/entities/researcher/workspace/research_reports/PHASE1_RESEARCH_20260813.md`
4. Post resolution to Hivemind (intent: decision|observation)
5. Update TASK_REGISTRY.json with completion status

## 🔴 CRITICAL GAPS (P0 — Must Resolve First)

**R27b (NULL tokens.total handling)** — VERIFIED: live DB returns NULL for some assistant messages.
- Gauge must handle NULL (fallback to input+cache.read, or skip+sum rest)
- QW-2 acceptance MUST include NULL handling
- This blocks QW-2 (Token Gauge Fix) — resolve Monday

**R30 (5-way CB spike)** — D-528 locked pyresilience, but interlock-cb was prior front-runner.
- Spike: pyresilience vs tenacity vs stamina vs pybreaker vs interlock-cb
- Use live benchmarks, not assumptions
- This blocks UO-6.1 (circuit breaker library) — resolve Week 3

**R2 (Model window detection)** — windows known (D-522), but detection CODE PATH is the gap.
- Dynamic (config/API) vs static mapping
- This blocks QW-8 (Context Gauge v1)

## 🟢 PARTIALLY RESOLVED (Verify + Extend, DON'T Re-Research)

**R4 (AGY pool)** — `data/entities/researcher/workspace/research_reports/SDP_KNOWLEDGE_GAP_RESEARCH_20260809.md` exists
- Verify pool numbers are current (Aug 2026)
- Extend: pool_tracker.py wiring specifics for QW-4

**R21 (Workhorse)** — `docs/strategy/CRITICAL_PATH_OPENCODE_WORKHORSE_20260722.md` exists
- Verify billing/OAuth/OCZ paths are current
- Extend: implementation specifics for G-1

**R22 (WARP)** — `docs/archive/strategy/2026-07-22/GEMMA4_FREE_TIER_FORENSIC_REPORT_20260722.md` exists
- Verify WARP pool bring-up status
- Extend: implementation specifics for W-1

## 📡 HIVEMIND COORDINATION (MANDATORY)

Before starting: `omega-hub_hivemind_get_awareness()` — check who's working
During: `omega-hub_hivemind_heartbeat(channel="opencode", entity="researcher")` every 5-10 min
After each gap: `omega-hub_hivemind_post_context(...)` with intent=decision

## ✅ ACCEPTANCE CRITERIA

Research phase complete when:
- [ ] All genuinely open gaps in phase resolved with authoritative sources
- [ ] Already-resolved gaps verified (pointer exists, no re-research)
- [ ] Reports written to `data/entities/researcher/workspace/research_reports/`
- [ ] Hivemind posts made for each gap resolution
- [ ] Dependent task owners (@jem, @maat, @lilith, @roc_racoon) acknowledge receipt
- [ ] TASK_REGISTRY.json updated with completion status

## 🛡️ SOVEREIGN MANDATES (NON-NEGOTIABLE)

- **M1 AnyIO**: No asyncio. Wrap blocking I/O in anyio.to_thread.run_sync
- **M7 Local-First**: Local inference PRIMARY, cloud FALLBACK
- **M8 Zero Telemetry**: No analytics, no phone-home
- **M23 Failure Integrity**: If mandatory tool broken → [TOOL-CHAIN-COLLAPSE], no soft-fail
- **M24 Venv Sovereignty**: Use .venv, never --break-system-packages

## 📊 PHASE R1 SCHEDULE (Week 1)

| Day | Gaps | Deliverable |
|-----|------|-------------|
| Mon | R27 (verify tokens.total query), R27b (NULL handling), R8b | Gauge query validation + NULL strategy + streaming observability impl plan |
| Tue | R2, R3 | Model window detection spec + subagent state machine |
| Wed | R4 (verify+extend), R5 | AGY pool verification + TriageRouter constraint mapping |
| Thu | R6, R7, R28 | RHP schema + MCP tool patterns (greenfield) + Streamable HTTP |
| Fri | Integration | Consolidated Phase 1 research package |

**Output:** `data/entities/researcher/workspace/research_reports/PHASE1_RESEARCH_20260813.md`

---

## 🔍 RESEARCH TOOL PROTOCOL (T0-T6)

| Tier | Tool | When to Use |
|------|------|-------------|
| T0 | Local cache (`.firecrawl/`) | Check before any external search |
| T1 | `websearch` | Primary search (free, no telemetry) |
| T2 | `webfetch` | Deep extraction from specific URLs |
| T3 | `searxng_searxng_search` | Semantic/neural search refinement |
| T4 | `omega-hub_sovereign_search` | High-precision seeds (Exa API) |
| T5 | `firecrawl_firecrawl_scrape` | Full-page scrape (credits) |
| T6 | `sieve research` | Full research pipeline (local-first) |

**TEMPORAL MANDATE:** Include "2026" or "latest" in all queries — it's 2026, not 2024/2025.

## 📝 EXAMPLE WORKFLOW FOR R7 (MCP tool patterns)

1. Check Cross-Reference Index → R7 is GREENFIELD (`src/omega/mcp/tools/` does NOT exist, only `mcp_runtime.py`)
2. No existing research to duplicate — proceed with greenfield implementation research
3. Reference `docs/research/R_CG01_MCP_STREAMABLE_HTTP_OAUTH.md` and `R_CG01_MCP_STREAMABLE_HTTP_OAUTH_AUDIT.md` for MCP patterns
4. Reference `RESEARCH_TECH_ARCHITECTURE_DECISIONS_20260808.md` for interlock-cb considerations (though D-528 supersedes with pyresilience)

## 📝 EXAMPLE WORKFLOW FOR R4 (AGY pool)

1. Check Cross-Reference Index → R4 is PARTIALLY RESOLVED (`SDP_KNOWLEDGE_GAP_RESEARCH_20260809.md` exists)
2. Read the existing research — it has 8 accounts, 1M pool, ~27K tokens/session, Redzone rule, attestation header
3. Verify numbers are current (Aug 2026)
4. Extend only: pool_tracker.py wiring specifics for QW-4
5. Do NOT re-research the AGY pool structure from scratch

## 🚨 ESCALATION

If you hit a blocker (missing tool, contradictory research, unclear requirement):
1. Post to Hivemind (intent: blocker)
2. Write to `data/coordination/SYSTEM_FAILURE_LOG.md` if tool-chain collapse
3. Wait for @kali ratification before proceeding

---

## 📋 RESEARCH PLAN v3.1.0 — GAP SUMMARY

| Phase | Gaps | Count | Hours |
|-------|------|-------|-------|
| Phase 1 (Week 1) | R2, R3, R5, R6, R7, R8b, R27, R27b, R28, R29, R32 | 11 | 14h |
| Phase 2 (Week 2-3) | R13, R14b, R26, R31, R33, R34, R35, R36 | 8 | 14h |
| Phase 3 (Week 3-4) | R30, R15(subsumed), R16, R17, R18, R19, R20, R37, R38 | 9 | 16h |
| Phase 4 (Week 4-6) | R23, R24, R25 | 3 | 8h |
| Resolved (pointer) | R1, R8, R9, R10, R11, R12, R14 | 7 | 0h |
| Partially Resolved | R4, R21, R22 | 3 | 0h |
| **TOTAL** | **R1-R38** | **38** | **52h** |

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-EXEC ⬡ v1.0.0 ⬡ 20260813*
