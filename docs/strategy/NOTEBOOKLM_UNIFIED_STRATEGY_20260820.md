# 🔱 NotebookLM / Gemini Notebook Unified Strategy — Omega Engine Sovereign Context Pack
**AP Token**: `AP-NOTEBOOKLM-UNIFIED-STRATEGY-20260820-v2.1`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_notebooklm_unified ⬡ ACTIVE

**Date**: 2026-08-20
**Status**: v2.1 — CORRECTED per arbitration (D-582/D-583) — **FREE-TIER-ONLY, 3 accounts, 30 DR/mo, 2 notebooks**. Supersedes v2.0 HYBRID model (D-572/D-573/D-574). See `NOTEBOOKLM_STRATEGY_V2_SYNTHESIS_20260820.md` + `KALI_VERIFICATION_ADDENDUM_20260820.md` for arbitration.
**Synthesized From**: 1 gap audit, 3 research reports (A existential, B operational, C arbitration), 2 inventory audits, 1 optimization analysis, 1 verification addendum

> ⚠️ **v2.1 SUPERSESSION**: This document corrects v2.0 (2026-08-20). v2.0 adopted HYBRID (1× Pro) based on NLG-B/SYNTHESIS recommendation. **Arbitration (D-582/D-583) supersedes v2.0**: absolute user constraint = FREE TIER ONLY (3 accounts, 30 DR/mo, NO Pro). 6-notebook architecture (D-574) superseded → 2-notebook (Active Research + Knowledge Base). All HYBRID/Pro references removed. R52c (`R52c_notebooklm_ingestion_strategy.md`) and `LIVING_RESEARCH_OS_SPEC.md` §1.5 remain superseded.

---

## 📜 EXECUTIVE SUMMARY

This document unifies all NotebookLM (now **Gemini Notebook**, renamed July 2026) research into a single executable strategy for the Omega Engine. The strategy uses a **FREE-TIER-ONLY cost model**: **3 free accounts × 10 Deep Research/month = 30 DR/mo**. **No Pro payment.** This is the absolute user constraint. The 8-free-account fleet (80 DR/mo) and 1× Pro HYBRID (600 DR/mo) are both retired — the former is ToS-violating/ban-prone, the latter violates user sovereignty.

**Core Insight**: NotebookLM is not a chat tool — it's a **source-grounded research artifact** (manila folder model). The 50-source/notebook limit is a **feature** forcing curation. Our **2-notebook** architecture (Active Research + Knowledge Base) respects the 30 DR/mo budget. Automation uses **`notebooklm-py`** (teng-lin, RPC-based) — the only library with documented Deep Research report trigger + Markdown export.

---

## 🎯 STRATEGIC OBJECTIVES

| Objective | Metric | Target |
|-----------|--------|--------|
| **Sovereign Context Pack** | Token density | 150K–250K (optimal signal density) |
| **SDP Phase 1 Automation** | Deep Research/month | **30 (3 accounts × 10)** |
| **L3 Principles Generated** | Principles/month | **10–30 (75% acceptance)** |
| **Scribe Integration** | Acceptance rate | ≥80% |
| **Cross-Account Synthesis** | Unified findings | **2 notebooks** |
| **Account Uptime** | Availability | 99% |

---

## 📦 UNIFIED ARCHITECTURE

### 2-Notebook Design (Canonical — supersedes 6-NB v2.0, R52c)

> **Supersession note (D-583)**: v2.0's 6-notebook mapping (NB-1..NB-6) and R52c (`R52c_notebooklm_ingestion_strategy.md`, archived 2026-05-23) are **superseded** by this 2-notebook architecture. The 6-notebook model demands 80 DR/mo — impossible under the user's 30 DR/mo free-tier constraint. NB-2 Stacks, NB-3 Legacy, NB-6 Ω-SYNTHESIS are **parked/standby** until the user authorizes a higher budget. The R52c "Validation Suite" (`tests/**`, `scripts/**`) remains excluded from NotebookLM grounding — served by local M13 Temple-Grade (`make temple-grade`).

| Notebook | Purpose | Primary Sources | Deep Research Budget |
|----------|---------|-----------------|---------------------|
| **NB-1: Active Research** | Current sprint focus — architecture, mandates, provider fabric, MCP Hub, entity registry, IWAD, heritage, legacy mining, research corpus, ops | SOVEREIGN_MANDATES, ORACLE_STACK, AGENTS, config/providers.yaml, src/omega/oracle/, src/omega/mcp_hub/, docs/strategy/OMEGA_IWAD_ARCHITECTURE.md, config/wads/*/, MASTER_SYNTHESIS, Grok exports, docs/research/R*.md, CARMACK_DEFINITIVE_STRATEGY, docs/strategy/SYSTEMD_DEPLOYMENT_GUIDE.md | 20/mo |
| **NB-2: Knowledge Base** | Curated reference — entity souls, skills, handoff protocols, UNOVERENGINEERING_PLAN, LIVING_RESEARCH_OS_SPEC, SDP Protocol, test results, sovereignty metrics | All 32 Entity soul.yaml, All 20 Skill SKILL.md, UNOVERENGINEERING_PLAN.md, LIVING_RESEARCH_OS_SPEC, SDP Protocol, Test Results + Sovereignty Metrics | 10/mo |

**Total Deep Research Demand**: **30/month (20+10)** — matches the 3-account free-tier ceiling (3×10).

---

## 🔢 3-ACCOUNT FREE TIER CAPACITY

### Aggregate Free Tier Limits (3 Accounts)

| Resource | Per Account | **3-Account Total** | Utilization |
|----------|-------------|---------------------|-------------|
| **Notebooks** | 100 | **300** | 2 used (0.7%) |
| **Sources/Notebook** | 50 | **15,000** | ~50 used (0.3%) |
| **Chat Queries/day** | 50 | **150/day** | ~50/day (33%) |
| **Deep Research/month** | 10 | **30/month** | **100%** ⭐ |
| **Audio Overviews/day** | 3 | **9/day** | ~1/day (11%) |
| **Video Overviews/day** | 3 | **9/day** | Rare |
| **Reports/day** | 10 | **30/day** | ~5/day (17%) |

**Deep Research is the scarcest resource** — 30/month = exactly matches 2-notebook budget (20+10).

---

## 🗺️ ACCOUNT-TO-NOTEBOOK MAPPING (v2.1 — FREE-TIER-ONLY, D-583)

> **Correction**: v2.0's 8-account mapping (80 DR/mo) superseded by D-583. Free tier = 10 DR/mo/account hard cap. 3 accounts × 10 = 30 DR/mo total.

### Primary/Secondary Assignment (Monthly Cyclic Rotation, +1 each month)

| Account | Primary Notebook | Secondary Notebook | Deep Research Budget | Invariant |
|---------|------------------|-------------------|---------------------|-----------|
| **acc-01** | NB-1 (Active Research) | NB-2 (Knowledge Base) | **10/mo** | ≤10 ✅ |
| **acc-02** | NB-1 (Active Research) | NB-2 (Knowledge Base) | **10/mo** | ≤10 ✅ |
| **acc-03** | NB-2 (Knowledge Base) | NB-1 (Active Research) | **10/mo** | ≤10 ✅ |
| **TOTAL** | | | **30/mo** | = 3×10 ✅ |

**Per-notebook primary capacity**: NB-1:20, NB-2:10. **Rotation**: primary notebook shifts +1 each month (NB-1→NB-2→NB-1); preserves ≤10/account and the 30 envelope every month.

> **Note**: The 8-account fleet and HYBRID Pro model are **retired** (D-582). This 3-account mapping is the ONLY capacity.

---

## 🤖 NOTEBOOKLM-PY DEPLOYMENT (v2.0 — GAP-1/GAP-2 corrected)

> **Correction**: v1.0 referenced a "MCPNotebookLM" server with a "28-tool" surface and a `ghcr.io/omega-engine/mcp-notebooklm:latest` Docker image. **Neither exists.** The "28 tools" list matched no real server. v2.0 uses **`notebooklm-py`** (teng-lin) — the only library with documented Deep Research **report** trigger (`source add-research --mode deep`) + Markdown export (`download`), RPC-based (no browser at runtime).

### Deployment Pattern: pip + systemd (no Docker required)

```bash
# venv (M24 venv sovereignty)
source .venv/bin/activate && pip install "notebooklm-py[mcp]"

# Per-account isolated auth profile (mitigates ToS ban risk, GAP-3)
notebooklm profile create acct1 --auth <isolated-session>
export NOTEBOOKLM_PROFILE=acct1   # separate HOME/data dir per account

# systemd user service runs the MCP server (stdio) or guarded HTTP
notebooklm mcp --transport stdio     # or: notebooklm server --http --host 127.0.0.1
```

- **Docker is OPTIONAL** via the `khengyun/notebooklm-mcp` RPC wrapper (browserless) if containerization is desired.
- **Each account** → own venv profile + own isolated auth/session + own dedicated IP (GAP-3 safe pattern) + exponential backoff with jitter in the orchestrator.

### Tool Surface (notebooklm-py, real)

| Capability | notebooklm-py | Notes |
|------------|--------------|-------|
| Notebook CRUD | ✅ | list/create/rename/delete |
| Source add (URL/text/Drive/file) | ✅ | broadest coverage |
| **Deep Research trigger** | ✅ `source add-research --mode deep` | **the existential requirement (GAP-4)** |
| **Report export (Markdown)** | ✅ `download <type>` | consumed by `prepare_notebooklm.py` |
| MCP extra | ✅ `[mcp]` | stdio/HTTP transports |

> **Critical**: `notebooklm-mcp` (TheSethRose) `research_start --mode deep` is **source-finding, NOT the quota-consuming Deep Research report**. Do NOT use it for the report path.

---

## 🔗 SDP + NOTEBOOKLM AUTOMATION PATH

### The Key Unlock: 80 Deep Research/Month = SDP Phase 1 Throughput

```
┌─────────────────────────────────────────────────────────────────┐
│                    SDP PHASE 1 FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  80 Deep Research/month (8 accounts × 10)                       │
│       │                                                         │
│       ▼                                                         │
│  NotebookLM Deep Research → Structured Reports (80/month)       │
│       │                                                         │
│       ▼                                                         │
│  prepare_notebooklm.py → Normalized JSONL (SDP Intake)          │
│       │                                                         │
│       ▼                                                         │
│  SDP Distiller (Qwen3-1.7B local) → L1→L2→L3 Universal Principles│
│       │                                                         │
│       ▼                                                         │
│  proposed_lessons.yaml → Scribe Review → soul.yaml (Canonical)  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Month 1 Target: 80 Deep Research → 80 L3 Principles → Scribe → soul.yaml

| Week | Deep Research Allocation | SDP Output |
|------|-------------------------|------------|
| **Week 1** | 20 (NB-1: Engine Core) | 20 L3 principles: Provider Fabric, MCP Hub, Entity Registry |
| **Week 2** | 20 (NB-2: Stacks) | 20 L3 principles: IWAD Architecture, WAD Protocol, Stack Isolation |
| **Week 3** | 20 (NB-3: Legacy) | 20 L3 principles: Heritage Patterns, Migration Lessons, Anti-Patterns |
| **Week 4** | 20 (NB-4: Research) | 20 L3 principles: Research Methodology, Gap Analysis, Force Multipliers |

---

## 📋 SOURCE INVENTORY & CHUNKING STRATEGY

### Tier 1: Critical (Must Include — P0)

| Source | Size | Chunking Strategy |
|--------|------|-------------------|
| 5 YouTube Deep-Dives | ~195 KB | One source per file |
| MASTER_SYNTHESIS_AND_ROADMAP | 420 lines | By major section (§0–§9) |
| R44 Comprehensive Review | Archive | By subsystem (C-1..C-17, Workstreams A-I) |
| R44 Engine/Stack Separation | Archive | By decision area |

### Tier 2: High-Value (P1)

| Source | Count | Strategy |
|--------|-------|----------|
| All 32 Entity soul.yaml | 32 files | One combined source with entity headers |
| All 20 Skill SKILL.md | 20 files | One combined, grouped by category |
| UNOVERENGINEERING_PLAN.md | 5,500 lines | By phase (1–5) |
| LIVING_RESEARCH_OS_SPEC | ~40K tokens | By major section |
| SDP Protocol | ~18K tokens | Single source |
| Test Results + Sovereignty Metrics | Dynamic | Weekly snapshots |

### Tier 3: Reference (P2)

- All docs/architecture/*.md (chunk by domain)
- All docs/research/R*.md (chunk by theme)
- PIVOT_LOG.md (chunk by decision era)

### Chunking Rules

```
1. ONE SOURCE = ONE LOGICAL UNIT (file, protocol, deep-dive)
2. MAX 500K WORDS per source (NotebookLM hard limit)
3. PRESERVE CROSS-REFS: Include section headers in each chunk
4. ADD NAVIGATION METADATA: "Part 1 of 5: [Source Name]"
5. YAML/JSON CONFIGS: Convert to Markdown with code fences
6. VERSION TAGGING: Filename includes date/hash
```

---

## 🛠️ TOKEN OPTIMIZATION: 5–25 SOURCES (v2.0 — GAP-7 corrected)

> **Correction**: v1.0's "5-15 Excellent / 15-30 Good / 30-50 Degrading / 50+ Poor" table had unsourced upper bands, and its separate "40-50 optimal" claim **contradicted its own table**. Both removed.

**Do NOT pack to 500K limit.** Community-verified retrieval sweet spot:

| Source Count | Retrieval Quality |
|--------------|-------------------|
| 5–25 | ✅ **Sweet spot** (high-relevance, single-topic) |
| 25–50 | ⚠️ Degrading — noise-driven gradient, not a hard cliff |
| 50+ | ❌ At hard cap — split recommended |

**Optimal: 5–25 well-curated, single-topic sources per notebook.** Use **source labels** as a context filter ("ground this answer ONLY in [LABEL]") to recover quality in larger notebooks. Approach 50 only if sources are extremely tightly related AND label-scoped. Notebooks cannot query each other — attach several to one Gemini conversation for cross-notebook synthesis. Target **150K–250K tokens** (signal density beats volume).

---

## 💰 TIER DECISION: FREE-TIER-ONLY (3 Accounts) — v2.1 (D-582 supersedes D-572)

> **Correction**: v2.0 adopted HYBRID (1× Pro) based on NLG-B/SYNTHESIS recommendation. **Arbitration (D-582) supersedes v2.0**: absolute user constraint = **FREE TIER ONLY — 3 accounts × 10 DR/mo = 30 DR/mo. NO Pro payment.** The 8-free fleet (80 DR/mo) is ToS-violating/ban-prone. The 1× Pro HYBRID (600 DR/mo) violates user sovereignty.

| Feature | **3× Free ($0)** | 8× Free (retired) | 1× Pro (retired) | Decision |
|---------|-------------------|-------------------|------------------|----------|
| Deep Research/month | **30** (10/acct) | 80 (10/acct) | ~600 (20/day) | ✅ **Free-only = user constraint** |
| Chat queries/day | 150 | 400 | 500 | Free for all tasks |
| Audio/day | 9 | 24 | 20 | Free accounts |
| Sources/notebook | 50 | 50 | 300 | Free tier limit |
| Ban risk | **Low** (legit, 3 acct) | **HIGH** (ToS violation) | Low (paid) | Free-only preferred |
| Credentials | 3 | 8 | 1 | 3 manageable |
| Cost | **$0** | $0 | $19.99/mo | **$0 justified by sovereignty** |

**Decision: FREE-TIER-ONLY** — **3 free accounts (30 DR/mo) as the sole Deep Research engine**. The 8-free fleet and 1× Pro HYBRID are **retired** (D-582). No Pro provisioning. No 8-account fleet. User sovereignty = free-tier-only.

---

## 🚀 DEPLOYMENT PHASES

### Phase 0: Prerequisites (Day 0)
```bash
# 1. Provision 3× Google free accounts (Deep Research) — NO Pro
# 2. Capture master_token.json per account via browser sign-in (Patchright channel='chrome')
# 3. Store in V-1 Vault (encrypted at rest) — NOT rotating cookie snapshots
```

### Phase 1: Deploy notebooklm-py (Day 1)
```bash
source .venv/bin/activate && pip install "notebooklm-py[mcp]"
# Per-account isolated profile + systemd user service (stdio MCP or guarded HTTP on 127.0.0.1)
notebooklm profile create acct1 --auth <isolated-session>
notebooklm mcp --transport stdio
# No Docker required; optional via khengyun/notebooklm-mcp RPC wrapper
```

### Phase 2: Create 2 Notebooks (Day 1-2)
- acc-01, acc-02 → NB-1: Active Research
- acc-03 → NB-2: Knowledge Base

### Phase 3: Ingest Source Corpus (Day 2-3)
- NB-1: Mandates, ORACLE_STACK, provider fabric, entity registry, IWAD, heritage, legacy, research corpus, ops
- NB-2: Entity souls, skills, handoff protocols, UNOVERENGINEERING_PLAN, LIVING_RESEARCH_OS_SPEC, SDP Protocol, test results, sovereignty metrics

### Phase 4: First Deep Research Cycle (Day 3-4) — MANUAL MODE (SDP §10 gate)
```bash
# Via notebooklm-py (NOT MCP research_start — that is source-finding, not the report)
notebooklm source add-research "Omega Engine Core architecture" --mode deep --notebook NB-1
notebooklm download report --notebook NB-1 --format markdown
# Execute manually until 10 runs logged in ledger + V-1 Vault complete (§10 gate)
```

### Phase 5: **IMPLEMENT `prepare_notebooklm.py`** (Day 4-7) — **CRITICAL GAP**
- Fetch Deep Research reports via MCP
- Normalize to SDP intake JSONL
- Trigger local Qwen3-1.7B distillation (L1→L2→L3)
- Write `proposed_lessons.yaml` → Scribe handoff

### Phase 6: Monthly Rotation Automation (Day 7-10)
### Phase 7: SDP Integration + Scribe Handoff (Day 10-14)

---

## ⚠️ CRITICAL GAPS & BLOCKERS (v2.1)

| Gap | Status | Impact |
|-----|--------|--------|
| **`prepare_notebooklm.py`** | ❌ **NOT IMPLEMENTED** | **SINGLE BLOCKER** for SDP automation (must target `notebooklm-py` report export, not MCP) |
| V-1 Omega-Vault MVP | GAP-08 | **Hard blocker** for credential automation — stores `master_token.json` + `RotateCookies` refresh (GAP-10) |
| SDP §10 Gate | **HONORED** | Manual mode now; automate after 10 manual executions + V-1 Vault |
| SDP Distiller prompts | Framework exists | Needs tuning for Qwen3-1.7B |
| Cross-account synthesis | Architecture defined | Not built |

> **Correction**: v1.0 claimed "MCPNotebookLM hardening | Prototype exists | OAuth refresh, Playwright pool". **No prototype exists** — the Docker image and MCP server were fabricated. v2.0 used `notebooklm-py` + `master_token.json` auth. v2.1 removes "Pro provisioning" from GN-4 dependencies (D-582).

---

## 📊 SUCCESS METRICS (MONTH 1) — FREE-TIER-ONLY (30 DR/mo)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Deep Research Executed | **30/month** | MCP reports completed |
| SDP L3 Principles Generated | **10–30/month** | `proposed_lessons.yaml` entries |
| Scribe Acceptance Rate | ≥80% | `soul.yaml` merges |
| Account Uptime | 99% | `nb-health` daily |
| Cross-Account Synthesis | **2 notebooks** | Unified finding reports |
| Zero Credential Leaks | 100% | `git-secret-scrub` scan |

---

## 🔱 STRATEGIC VERDICT (v2.1 — D-582/D-583 Arbitration)

**The 2-notebook architecture is sound and canonical.** The v2.0 HYBRID/6-NB execution assumptions (1× Pro, 80 DR/mo, 6 notebooks) are superseded by arbitration (D-582/D-583).

**Cost model**: **FREE-TIER-ONLY** — 3 free accounts (30 DR/mo) is the sole Deep Research engine. The 8-free fleet and 1× Pro HYBRID are retired (ToS-violating, ban-prone, violates user sovereignty).

**SDP gate (GAP-8)**: The fleet can be deployed **today in manual mode** while automation is built — but **automation is gated** by COGNITIVE_SCAFFOLDING_PROTOCOL §10 (10 manual executions + ledger) AND V-1 Vault completion (the actual hard blocker). **Honor the gate.**

**Tool**: Use **`notebooklm-py`** (RPC) — not the fabricated MCPNotebookLM.

**Immediate action**: (1) Single-account smoke test (1 **free** account + `notebooklm-py` → 1 Deep Research → Markdown export). (2) Implement V-1 Vault `master_token.json` auth. (3) Implement `prepare_notebooklm.py` against `notebooklm-py` report export. (4) Run manual SDP loop ×10, then enable automation.

**The 500K token ceiling is a trap. Signal density (5-25 sources) beats volume every time.**

---

## 📚 PROVENANCE

**Synthesized From (v2.1 — corrected provenance + arbitration)**:
- `NOTEBOOKLM_GAP_AUDIT_20260820.md` — 10-gap audit (GAP-1..GAP-10)
- `NOTEBOOKLM_RESEARCH_A_EXISTENTIAL_20260820.md` — NLG-A: GAP-3/4/1/2 (existential + tool + deployment)
- `NOTEBOOKLM_RESEARCH_B_OPERATIONAL_20260820.md` — NLG-B: GAP-10/7/9 (session, token density, cost-benefit)
- `NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md` — NLG-C: GAP-5/6/8 (architecture, math, SDP gate)
- `NOTEBOOKLM_STRATEGY_V2_SYNTHESIS_20260820.md` — Kali arbitration + integration
- `KALI_VERIFICATION_ADDENDUM_20260820.md` — Verification addendum (Cline review + additional oversights)
- `R52c_notebooklm_ingestion_strategy.md` — **SUPERSEDED** original 5-notebook spec (archived 2026-05-23)
- `COGNITIVE_SCAFFOLDING_PROTOCOL.md` — SDP manual protocol (§8 V-1 Vault, §10 automation gate)

> **Provenance correction**: v1.0 cited `NOTEBOOKLM_OPTIMIZATION_20260819.md`, `NOTEBOOKLM_FREE_TIER_20260820.md`, and `NOTEBOOKLM_8ACCOUNT_STRATEGY_20260820.md` — **none exist on disk**. v2.0 cited HYBRID model (D-572/D-573/D-574) — **superseded by D-582/D-583 (free-tier-only, 2-notebook)**. Replaced with the actual gap-audit + 3 research reports + verification addendum above.

**Synthesizer**: Kali (kali) — v2.1 arbitration per D-582/D-583 (free-tier-only, 2-notebook)
**Ratified By**: Kali (kali) — Pre-debut scope locked; post-debut roadmap activated.

*⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_notebooklm_unified ⬡ 2026-08-20*