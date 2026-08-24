# 🔱 Gemini Notebook Domain Strategy v2.0
**AP Token**: `AP-GEMINI-NOTEBOOK-STRATEGY-V2-20260820`
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_domain_strategy ⬡ ACTIVE

**Date**: 2026-08-20
**Status**: CANONICAL — Free-tier-only, 2-notebook architecture
**Supersedes**: `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` (v2.1)
**Source**: Arbitration D-582/D-583 (free-tier-only, 2-NB, 30 DR/mo)

---

## 🎯 EXECUTIVE SUMMARY

**Gemini Notebook** (formerly NotebookLM) is the **primary platform** for source-grounded research synthesis, literature review, and multi-document analysis. Best for: source-cited verification, audio overview generation, collaborative research.

**Backend**: Gemini model (Google)
**Effective Context**: ~200K tokens (source-based, not raw context)
**Cost**: Free tier only — 3 accounts × 10 DR/month = 30 DR/month total
**Architecture**: 2 notebooks (Active Research + Knowledge Base)
**Automation**: `notebooklm-py[mcp]` (RPC-based, no browser at runtime)
**Auth**: `master_token.json` + RotateCookies (per-account isolated profiles)

---

## 📋 ARCHITECTURE

### 2-Notebook Architecture

| Notebook | Purpose | Sources | Key Labels |
|----------|---------|---------|------------|
| **Ω-ACTIVE-RESEARCH** | Active research questions, gap analysis, synthesis | 5-25 | RESEARCH, GAP-ANALYSIS, SYNTHESIS, ACTION-ITEMS |
| **Ω-KNOWLEDGE-BASE** | Curated knowledge, reference docs, distilled principles | 5-25 | REFERENCE, PRINCIPLES, LESSONS, ARCHIVE |

### Source Organization

Organize sources by **theme**, not chronology:
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

### Source Metadata (Critical)

Every source must include:
```markdown
<!-- Source: https://example.com/doc -->
<!-- Last fetched: 2026-08-20 -->
<!-- Coverage: complete API reference for v3.x -->
<!-- Version: 3.2.1 -->
```

---

## 🔧 AUTOMATION — `notebooklm-py[mcp]`

**Recommended automation library**: **`notebooklm-py`** (teng-lin) with `[mcp]` extra — the ONLY library with documented Deep Research **report** trigger (`source add-research --mode deep`) + Markdown export (`download`). RPC-based (no browser at runtime) → best fit for local-first (M7) headless systemd deployment.

```bash
# Deployment (per account, M24 venv sovereignty)
source .venv/bin/activate && pip install "notebooklm-py[mcp]"

# Per-account isolated auth profile (mitigates ToS ban risk)
notebooklm profile create acct1 --auth <isolated-session>
export NOTEBOOKLM_PROFILE=acct1   # separate HOME/data dir per account

# systemd user service runs the MCP server (stdio) or guarded HTTP
notebooklm mcp --transport stdio     # or: notebooklm server --http --host 127.0.0.1
```

> **Critical**: `notebooklm-mcp` (TheSethRose) `research_start --mode deep` is **source-finding, NOT the quota-consuming Deep Research report**. Do NOT use it for the report path. Use `notebooklm-py` for Deep Research automation.

---

## 📊 FREE-TIER CONSTRAINTS

| Constraint | Value | Source |
|------------|-------|--------|
| Accounts | 3 (max) | ToS + operational burden |
| Deep Research / month / account | 10 | Verified 2026-08-20 |
| Total DR / month | 30 | 3 × 10 |
| Sources / notebook | 50 | Official limit |
| Notebooks / account | 100 | Official limit |
| Chats / day | 50 | Official limit |
| Audio / day | 3 | Official limit |
| Reports / day | 10 | Official limit |
| Words / source | 500K | Official limit |

**ToS Risk Mitigation**:
- Dedicated IP per account (no shared egress)
- Isolated browser profile per account (`notebooklm profile create`)
- Staggered scheduling + backoff + jitter
- No bot-created accounts (explicit ban — issue #228)

---

## 🔄 WEEKLY SYNC PIPELINE

```bash
# systemd timer: weekly (Sunday 02:00)
notebooklm source add-research --mode deep --notebook Ω-ACTIVE-RESEARCH --query "Omega Engine architecture gaps"
notebooklm download --format markdown --output /data/coordination/gemini_notebook/weekly/
# Feed to SDP intake → local distillation (Qwen3-1.7B) → proposed_lessons.yaml
```

---

## 🔗 SDP INTEGRATION

**Gate**: SDP §10 — Honor the manual study phase (10 manual executions + ledger data) before automation.

**Pipeline**:
1. Deep Research report → Markdown export
2. `prepare_notebooklm.py` normalizes to SDP intake format
3. Local distillation (Qwen3-1.7B) → L1→L2→L3
4. `proposed_lessons.yaml` → Scribe → `soul.yaml`
5. V-1 Vault unblocks automation phase

---

## ⚖️ SOVEREIGN BOUNDARY PROTOCOLS

| Mandate | Impact |
|---------|--------|
| **M7 Local-First** | NotebookLM is cloud-only — use for research ONLY, never for production inference |
| **M8 Zero Telemetry** | Google may collect usage data — treat as advisory, not sovereign |
| **M23 Failure Integrity** | Verify all claims against source citations — no soft failures |

---

## 📁 PROVENANCE

**Arbitration**: D-582 (supersedes D-572 HYBRID), D-583 (supersedes D-573/D-574 6-NB/80DR)
**Research**: NLG-A (existential), NLG-B (operational), NLG-C (arbitration)
**Tool**: `notebooklm-py[mcp]` validated (NLG-A)
**Auth**: `master_token.json` + RotateCookies (NLG-B)
**Token Density**: 5-25 sweet spot (NLG-B, corrects 40-50 claim)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_domain_strategy ⬡ 2026-08-20*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
