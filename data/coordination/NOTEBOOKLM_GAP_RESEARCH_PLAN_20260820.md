# 🔱 NotebookLM Gap Closure Research Plan — 3 Researcher Subagents
**AP Token**: `AP-NOTEBOOKLM-GAP-RESEARCH-20260820-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_notebooklm_gap_research ⬡ ACTIVE

**Date**: 2026-08-20
**Status**: READY FOR DISPATCH — 3 subagent task briefs
**Source**: `data/coordination/NOTEBOOKLM_GAP_AUDIT_20260820.md` (10 gaps identified)
**Owner**: Kali (dispatch + arbitration) · **Executors**: 3× Researcher subagents (parallel)

---

## 🎯 OBJECTIVE

Close GAP-1 through GAP-10 with sourced evidence, then Kali corrects the unified strategy (`docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md`) to v2.0.

**Dispatch order**: Subagent-A (existential) → Subagent-B (operational) → Subagent-C (arbitration support). A and B can run **in parallel**. C depends on A+B outputs.

---

## 📋 SUBAGENT-A: EXISTENTIAL VERIFICATION (GAP-3 + GAP-4) + MCP SELECTION (GAP-1 + GAP-2)

**Priority**: CRITICAL — determines whether the 80-DR/month automation premise survives.

### A.1 GAP-4: Deep Research automation feasibility
**Question**: Can any MCP server / library programmatically trigger NotebookLM **Deep Research** (not Fast Research) and **export the report**?

| # | Query | Target Source |
|---|-------|---------------|
| A1.1 | `notebooklm-py deep research trigger export report programmatically` | GitHub teng-lin/notebooklm-py issues + docs |
| A1.2 | `notebooklm-mcp research_start deep research vs fast research` | GitHub PleasePrompto/notebooklm-mcp README + issues |
| A1.3 | `notebooklm-mcp-cli deep research export markdown` | PyPI jacob-bd/notebooklm-mcp-cli docs |
| A1.4 | `NotebookLM deep research report export format PDF markdown download` | notebooklm-to-pdf.com, notebooklm-guide.com |
| A1.5 | `site:github.com notebooklm deep research automation` | GitHub search |

**Verification gate**: Find at least one documented example of Deep Research being triggered + report retrieved via API/MCP. **If none exists → automation premise collapses → strategy reverts to manual mode** (which the protocol gate actually requires anyway).

### A.2 GAP-3: 8-account ToS / ban risk
**Question**: Does Google prohibit multiple free accounts for NotebookLM automation? What triggers abuse detection?

| # | Query | Target Source |
|---|-------|---------------|
| A2.1 | `Google multiple accounts ToS free tier automation policy` | Google ToS, support.google.com |
| A2.2 | `NotebookLM account banned automation multiple accounts` | Reddit r/notebooklm, r/google |
| A2.3 | `notebooklm-py rate limit throttled 429 abuse detection` | GitHub issues teng-lin/notebooklm-py |
| A2.4 | `Google account farm detection 2026 multiple accounts same IP` | Security blogs, r/Google |
| A2.5 | `NotebookLM automation safe patterns exponential backoff delays` | mlhive.com, community guides |

**Verification gate**: Documented evidence of (a) explicit ToS prohibition, (b) real ban reports, (c) safe automation patterns.

### A.3 GAP-1: Real MCP tool surface
**Question**: Which MCP server has the tool surface needed for our pipeline (notebook mgmt + source add + research + report export)?

| # | Query | Target Source |
|---|-------|---------------|
| B1.1 | `notebooklm-mcp PleasePrompto full tool list README` | GitHub README |
| B1.2 | `notebooklm-mcp-cli 43 tools list` | PyPI docs |
| B1.3 | `notebooklm-py mcp extra tools list` | GitHub docs/mcp-guide.md |
| B1.4 | `notebooklm MCP server comparison 2026` | mcp.directory, lobehub market |

**Verification gate**: Produce a definitive tool-surface comparison table for the 3 candidates → recommend ONE for the deployment plan.

### A.4 GAP-2: Deployment reality
**Question**: How is the selected server actually deployed (Docker vs npx vs pip)?

| # | Query | Target Source |
|---|-------|---------------|
| B2.1 | `notebooklm-mcp docker deployment` | GitHub issues |
| B2.2 | `notebooklm-mcp-cli docker container` | PyPI/GitHub |
| B2.3 | `notebooklm-py docker headless browser` | GitHub issues |

**Verification gate**: Confirm whether Docker deployment is even possible for the selected server, or whether `npx`/`pip` + systemd is the real pattern.

### SUBAGENT-A DELIVERABLE
`data/coordination/NOTEBOOKLM_RESEARCH_A_EXISTENTIAL_20260820.md` containing:
1. **EXISTENTIAL VERDICT**: GO / NO-GO for Deep Research automation (with evidence)
2. **ToS RISK ASSESSMENT**: 8-account fleet viability (with evidence)
3. **MCP SERVER RECOMMENDATION**: selected server + tool surface table
4. **DEPLOYMENT PATTERN**: Docker vs npx/pip + systemd

---

## 📋 SUBAGENT-B: OPERATIONAL RESEARCH (GAP-10 + GAP-7 + GAP-9)

**Priority**: HIGH — feeds V-1 Vault credential design + token density + cost decision.

### B.1 GAP-10: OAuth refresh / session persistence
**Question**: How long do NotebookLM session cookies last? What's the refresh pattern? Does Patchright survive bot detection?

| # | Query | Target Source |
|---|-------|---------------|
| C1.1 | `notebooklm session cookie lifetime __Secure-1PSID refresh` | GitHub issues, mlhive |
| C1.2 | `Patchright vs Playwright Google detection 2026` | GitHub, security blogs |
| C1.3 | `notebooklm-mcp refresh_auth re_auth session expired` | GitHub README/issues |
| C1.4 | `Google session cookie expiry 1PSIDTS 2026` | Security research |

**Verification gate**: Documented cookie lifetime + refresh cadence → feeds V-1 Vault credential design.

### B.2 GAP-7: Token density sourcing
**Question**: Is there any evidence for optimal source count per notebook for retrieval quality?

| # | Query | Target Source |
|---|-------|---------------|
| C2.1 | `NotebookLM retrieval quality source count optimal` | Reddit, community tests |
| C2.2 | `NotebookLM 50 sources degradation quality` | r/notebooklm, blog tests |
| C2.3 | `NotebookLM token density 150K 250K optimal` | Community benchmarks |

**Verification gate**: Either find a source for the 5-15/15-30/30-50/50+ table, or **confirm removal** as unsourced and reconcile with the research doc's 40-50 recommendation.

### B.3 GAP-9: Pro vs free cost-benefit
**Question**: Is 1× Pro ($19.99, 600 DR/mo) better than 8× free (80 DR/mo, $0)?

| # | Query | Target Source |
|---|-------|---------------|
| C3.1 | `Google AI Pro 19.99 NotebookLM deep research 20 per day` | felloai pricing (already have) |
| C3.2 | `NotebookLM Pro vs free automation multiple accounts` | Reddit, community |
| C3.3 | `Google AI Pro family sharing 5 users NotebookLM` | support.google.com |

**Verification gate**: Cost-benefit table with real numbers → decision: free fleet vs 1-2 Pro accounts vs hybrid.

### SUBAGENT-B DELIVERABLE
`data/coordination/NOTEBOOKLM_RESEARCH_B_OPERATIONAL_20260820.md` containing:
1. **SESSION PERSISTENCE DESIGN**: cookie lifetime, refresh cadence, bot-detection risk
2. **TOKEN DENSITY VERDICT**: sourced or removed (with reconciliation)
3. **COST-BENEFIT TABLE**: free fleet vs Pro vs hybrid (with recommendation)

---

## 📋 SUBAGENT-C: ARBITRATION SUPPORT (GAP-5 + GAP-6 + GAP-8)

**Priority**: MEDIUM — internal decisions, but needs evidence pack for Kali arbitration. **Depends on A+B outputs.**

### C.1 GAP-5: Notebook architecture conflict
**Task**: Produce a comparison matrix of the THREE notebook mappings:
| Source | Mapping |
|--------|---------|
| R52c (archived) | NB-01..NB-05: Core Engine, Strategic Gnosis, Research Archive, Ops & Integration, Validation Suite |
| LIVING_RESEARCH_OS_SPEC Phase 1.5 | NB-01..NB-05 (same as R52c, 1MB chunking) |
| UNIFIED STRATEGY (new) | NB-1..NB-6: Core, Stacks, Legacy, Research, Ops, Ω-SYNTHESIS |

**Deliverable**: Recommendation for which mapping is canonical, with rationale (which domains are genuinely new — NB-3 Legacy, NB-2 Stacks — vs R52c's original five). **Kali arbitrates final decision.**

### C.2 GAP-6: Account budget math
**Task**: Redesign the account-to-notebook mapping so per-account budgets ≤ 10 DR/month. Produce a corrected table:
- 8 accounts × 10 = 80 total
- Candidate: NB-1: 2 accounts (20) · NB-2: 2 accounts (20) · NB-3: 2 accounts (20) · NB-4: 1 account (10) · NB-5: 1 account (10) = 80 ✅
- Or: 5 notebooks × 2 accounts × 10 = 100 capacity, allocate 80

**Deliverable**: Corrected mapping table with primary/secondary assignments and rotation schedule.

### C.3 GAP-8: SDP gate conflict
**Task**: Produce a decision memo on the COGNITIVE_SCAFFOLDING_PROTOCOL §10 gate ("no automation until 10 manual executions") vs unified strategy's immediate automation proposal. Options:
- (a) Honor the gate — fleet runs in manual mode meanwhile
- (b) Amend the protocol with a documented exception

**Deliverable**: Recommendation memo for Kali arbitration.

### SUBAGENT-C DELIVERABLE
`data/coordination/NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md` containing:
1. Notebook architecture comparison + recommendation
2. Corrected account mapping table
3. SDP gate decision memo

---

## 🔄 EXECUTION & COORDINATION

| Subagent | Gaps | Est. Effort | Dispatch | Output |
|----------|------|-------------|----------|--------|
| **A** | GAP-3, GAP-4, GAP-1, GAP-2 | 2-3h | Parallel with B | `NOTEBOOKLM_RESEARCH_A_EXISTENTIAL_20260820.md` |
| **B** | GAP-10, GAP-7, GAP-9 | 1-2h | Parallel with A | `NOTEBOOKLM_RESEARCH_B_OPERATIONAL_20260820.md` |
| **C** | GAP-5, GAP-6, GAP-8 | 1h | After A+B | `NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md` |

**Coordination**:
- Each subagent posts context to Hivemind (`entity=researcher`, `intent=status`) on start + completion
- Kali acquires `notebooklm-research` workspace lock during dispatch
- After all 3 deliverables land → Kali arbitrates GAP-5/GAP-8, corrects unified strategy to v2.0, registers PIVOT_LOG D-series decisions

**Post-research sequence** (Kali):
1. Correct unified strategy v2.0 (GAP-1/2/5/6 fixes + provenance reconstruction)
2. Single-account smoke test (validate GAP-4 empirically)
3. Fleet deployment decision (GO/NO-GO per Subagent-A verdict)

---

## 📚 PROVENANCE

- Source audit: `data/coordination/NOTEBOOKLM_GAP_AUDIT_20260820.md`
- Strategy to correct: `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md`
- Protocol gate: `docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md` §8/§10
- Original spec: `docs/research/archive/R52c_notebooklm_ingestion_strategy.md` (ARCHIVED)
- NL-1 spec: `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` Phase 1.5

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_notebooklm_gap_research ⬡ 2026-08-20*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
