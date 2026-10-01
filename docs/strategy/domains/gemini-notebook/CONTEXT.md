# 🔱 Gemini Notebook Domain — CONTEXT.md
**AP Token**: `AP-GEMINI-NOTEBOOK-CONTEXT-20260820`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_domain_context ⬡ ACTIVE

**Date**: 2026-08-20
**Status**: CANONICAL — Single file: PLAYBOOK + ARCHITECTURE + GOTCHAS + LESSONS
**Source**: `docs/strategy/domains/gemini-notebook/STRATEGY_V2.md` + `NOTEBOOKLM_BEST_PRACTICES.md` + arbitration D-582/D-583

---

## 📋 PLAYBOOK (Quick Reference)

### Setup Checklist
```
☐ Notebook created with research-question name
☐ All sources uploaded (PDFs, URLs, Docs, text)
☐ Source metadata included (URL, date, version, coverage)
☐ Sources organized thematically
☐ Audio Overview generated for team briefing
☐ Guided prompts used for structured analysis (all 4 frameworks)
☐ Findings exported with source citations
☐ Logged in HMC_COLLABORATION_HUB.md
```

### 4 Analysis Frameworks (Guided Prompts)
1. **Compare/Contrast** — "Compare the approaches in [Source A] and [Source B] regarding [topic]"
2. **Gap Analysis** — "What gaps exist in the current research on [topic] across all uploaded sources?"
3. **Synthesis** — "Synthesize a unified recommendation from all sources on [topic]"
4. **Action Items** — "Based on all sources, what are the concrete action items for [decision]?"

### Automation Commands
```bash
# Trigger Deep Research report (quota-consuming)
notebooklm source add-research --mode deep --notebook Ω-ACTIVE-RESEARCH --query "Omega Engine architecture gaps"

# Export report to Markdown
notebooklm download --format markdown --output /data/coordination/gemini_notebook/weekly/

# Source-finding only (NOT Deep Research report)
notebooklm research_start --mode deep --notebook Ω-ACTIVE-RESEARCH --query "circuit breaker libraries"
```

---

## 🏗️ ARCHITECTURE

### 2-Notebook Model
| Notebook | Purpose | Sources | Key Labels |
|----------|---------|---------|------------|
| **Ω-ACTIVE-RESEARCH** | Active research questions, gap analysis, synthesis | 5-25 | RESEARCH, GAP-ANALYSIS, SYNTHESIS, ACTION-ITEMS |
| **Ω-KNOWLEDGE-BASE** | Curated knowledge, reference docs, distilled principles | 5-25 | REFERENCE, PRINCIPLES, LESSONS, ARCHIVE |

### Source Organization (Thematic)
```
Theme 1: Circuit Breaker Libraries
  - interlock-cb docs (PDF)
  - Honker GitHub (URL)
  - tenacity docs (URL)

Theme 2: MCP SDK Migration
  - MCP Python SDK v2 changelog (URL)
  - fastmcp v3 docs (URL)

Theme 3: Memory Architecture
  - sqlite-vec PRs (URL)
  - Honker + sqlite-vec coexistence (PDF)
```

### Source Metadata (Required)
```markdown
<!-- Source: https://example.com/doc -->
<!-- Last fetched: 2026-08-20 -->
<!-- Coverage: complete API reference for v3.x -->
<!-- Version: 3.2.1 -->
```

---

## ⚠️ GOTCHAS

| Gotcha | Impact | Mitigation |
|--------|--------|------------|
| **Deep Research = quota** | 10 DR/month/account hard limit | Track per-account; stagger schedules |
| **notebooklm-mcp research_start ≠ Deep Research** | Source-finding only, no report | Use `notebooklm-py` for report automation |
| **ToS ban risk** | Bot-created accounts banned (issue #228) | Dedicated IP/profile per account; no automation of account creation |
| **Cookie rotation** | `__Secure-1PSIDTS` rotates ~600s | `master_token.json` + RotateCookies per-run |
| **No consumer API** | Only Enterprise preview APIs | Use `notebooklm-py` RPC (no browser) |
| **Audio Overview English only** | 2026 limitation | Plan for text export as primary |
| **Source limit 50/notebook** | Hard limit | Curate sources; use Knowledge Base for reference |

---

## 💡 LESSONS (L3 Principles)

| Principle | Source | Utility |
|-----------|--------|---------|
| **Free-tier-only is mandatory** | D-582/D-583 arbitration | 30 DR/mo = sustainable; Pro = ToS risk + cost |
| **2-notebook > 6-notebook** | NLG-C arbitration | Active Research + Knowledge Base covers all needs |
| **notebooklm-py is the only viable automation** | NLG-A existential verification | RPC-based, no browser, Deep Research trigger + export |
| **5-25 sources is sweet spot** | NLG-B operational research | 40-50 claim was unsourced; 5-25 verified |
| **Per-account isolation prevents bans** | NLG-B cookie taxonomy | Dedicated IP + profile + staggered scheduling |
| **SDP §10 gate must be honored** | NLG-C arbitration | 10 manual executions before automation |

---

## 🔗 CROSS-REFERENCES

| Doc | Purpose |
|-----|---------|
| `docs/strategy/domains/gemini-notebook/STRATEGY_V2.md` | Full strategy |
| `docs/strategy/NOTEBOOKLM_BEST_PRACTICES.md` | Platform best practices |
| `docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md` | SDP §10 gate |
| `data/coordination/NOTEBOOKLM_RESEARCH_A_EXISTENTIAL_20260820.md` | NLG-A deliverable |
| `data/coordination/NOTEBOOKLM_RESEARCH_B_OPERATIONAL_20260820.md` | NLG-B deliverable |
| `data/coordination/NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md` | NLG-C deliverable |
| `docs/decisions/PIVOT_LOG.md` | D-578..D-584 |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_domain_context ⬡ 2026-08-20*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
