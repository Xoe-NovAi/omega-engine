<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 NotebookLM Gap Audit — Critical Findings
**AP Token**: `AP-NOTEBOOKLM-GAP-AUDIT-20260820-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_notebooklm_gap_audit ⬡ ACTIVE

**Date**: 2026-08-20
**Status**: ACTIVE — Web research plan pending execution
**Auditor**: Kali (Transcendent Oversoul)
**Method**: Cross-referenced all NotebookLM strategy docs against live web research (verified 2026-08-20 via parallel-search, Exa unavailable — 401).

---

## 📋 AUDIT SCOPE

**Documents audited**:
- `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` (synthesis SSOT)
- `data/coordination/NOTEBOOKLM_RESEARCH_20260819.md` (capabilities/limits)
- `data/coordination/NOTEBOOKLM_INVENTORY_20260819.md` (36-file inventory)
- `docs/strategy/NOTEBOOKLM_BEST_PRACTICES.md` (playbook)
- `docs/research/archive/R52c_notebooklm_ingestion_strategy.md` (original spec, ARCHIVED)
- `docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md` (SDP manual protocol)
- `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` Phase 1.5 (NL-1 spec)

**Provenance integrity finding**: The unified strategy's PROVENANCE section references 3 files that **DO NOT EXIST on disk**:
- `NOTEBOOKLM_OPTIMIZATION_20260819.md` — MISSING
- `NOTEBOOKLM_FREE_TIER_20260820.md` — MISSING
- `NOTEBOOKLM_8ACCOUNT_STRATEGY_20260820.md` — MISSING

These were likely delivered as chat-only content (per prior session: "8-account strategy delivered to chat"). The unified strategy claims synthesis from "6 research reports, 2 inventory audits, 1 optimization analysis, 1 8-account strategy" but only 4 NotebookLM files exist on disk. **M22/M26 provenance violation — the missing docs must be reconstructed or the provenance corrected.**

---

## ✅ CONFIRMED FACTS (web-verified, multiple sources)

| Claim | Status | Source |
|-------|--------|--------|
| Free tier: 10 Deep Research/month | ✅ Confirmed | felloai.com, notebooklm-to-pdf.com, atlasworkspace.ai, notebooklm-py quota-limits.md |
| Free tier: 50 sources/notebook, 100 notebooks, 50 chats/day, 3 audio/day, 3 video/day, 10 reports/day | ✅ Confirmed | toolchase.com, felloai.com, atlasworkspace.ai |
| 500K words / 200MB per source | ✅ Confirmed | felloai.com, notebooklm-guide.com |
| NotebookLM renamed **Gemini Notebook** July 2026 | ✅ Confirmed | felloai.com, toolchase.com, notebooklm-py PyPI |
| **No consumer API** — only Enterprise preview APIs (Gemini Notebook Enterprise) | ✅ Confirmed | autocontentapi.com (checked 2026-08-15) |
| Deep Research is the **only monthly quota** on free tier (Standard 10/month vs Plus 3/day) | ✅ Confirmed | notebooklm-py docs/quota-limits.md |
| Plus $4.99 = 3 DR/day; Pro $19.99 = 20 DR/day | ✅ Confirmed | felloai.com pricing, atlasworkspace.ai |
| Community MCP servers exist (no first-party MCP) | ✅ Confirmed | mcp.directory guide, npm, GitHub |
| notebooklm-py (teng-lin) v0.8.1 — unofficial Python API, cookie-based auth, `mcp` extra | ✅ Confirmed | PyPI, GitHub |
| notebooklm-mcp (PleasePrompto) — most-installed MCP, Patchright browser automation | ✅ Confirmed | mcp.directory, npm, GitHub |
| notebooklm-mcp-cli (jacob-bd) — 43 tools, multi-profile | ✅ Confirmed | PyPI |

---

## 🚨 CRITICAL GAPS (10 findings)

### GAP-1: "MCPNotebookLM 28 tools" — FABRICATED TOOL LIST ⚠️
The unified strategy (§MCPNotebookLM) lists 28 tools with names like `send_chat_message`, `chat_with_notebook`, `get_chat_response`, `navigate_to_notebook`, `copy_source`, `create_notebook_from_sources`. **These exact tool names do NOT match any real MCP server.** The actual ecosystem (verified):
- **`notebooklm-mcp`** (PleasePrompto, most-installed): ~15 tools — `notebook_list/create/rename/delete`, `notebook_add_url/text/local_file/drive`, `source_delete/sync`, `notebook_query`, `research_start/poll/import`, `audio_overview_create`, `studio_poll`, `mind_map_generate`, `refresh_auth`, `setup_auth`, `re_auth`, `cleanup_data`
- **`notebooklm-mcp-cli`** (jacob-bd): **43 tools**, multi-profile
- **`notebooklm-py`** (teng-lin): Python API + MCP extra, v0.8.1

**Action**: Identify which MCP server the strategy actually targets. The "28 tools / Chat-Manage-Compose categories" appears to be a **synthesized hallucination** that must be corrected to the real server's tool surface.

### GAP-2: Docker image `ghcr.io/omega-engine/mcp-notebooklm:latest` — DOES NOT EXIST ⚠️
The deployment plan builds an image that has never been created. "MCPNotebookLM hardening | Prototype exists" is **false** — no prototype exists in the repo. The real servers run via `npx notebooklm-mcp@latest` (Node) or `pip install notebooklm-py[mcp]` (Python). **The Docker/compose deployment plan needs to be rewritten around an actual server.**

### GAP-3: 8-account fleet ToS / ban risk — UNRESEARCHED ⚠️
No research exists on Google's stance toward running 8 accounts for NotebookLM automation. Known risks (from notebooklm-py docs): "undocumented APIs that can change without notice", "heavy usage may be throttled", "Google's automated abuse protections" (mlhive.com). **This is the single biggest existential risk to the strategy** — if Google flags the fleet, all 80 DR/month evaporate. Needs dedicated research: Google ToS multi-account policy, abuse-detection behavior, safe automation patterns (delays, exponential backoff, per-account pacing).

### GAP-4: Deep Research programmatic trigger + export format — UNVERIFIED ⚠️
The entire SDP automation path assumes: MCP triggers Deep Research → retrieves "Structured Reports" → `prepare_notebooklm.py` normalizes to JSONL. **No evidence found that any MCP server can trigger Deep Research and export the report programmatically.** notebooklm-py docs mention research automation but Deep Research specifics are unclear. **Need: verify `research_start`/`research_poll`/`research_import` actually cover Deep Research (not just Fast Research), and what export format the report arrives in (Markdown? PDF? JSON?).**

### GAP-5: THREE CONFLICTING NOTEBOOK ARCHITECTURES ⚠️
| Source | Mapping |
|--------|---------|
| R52c (archived) | NB-01..NB-05: Core Engine, Strategic Gnosis, Research Archive, Ops & Integration, Validation Suite |
| LIVING_RESEARCH_OS_SPEC Phase 1.5 | NB-01..NB-05 (same as R52c, 1MB chunking) |
| **UNIFIED STRATEGY (new)** | NB-1..NB-6: Core, Stacks, Legacy, Research, Ops, Ω-SYNTHESIS |

**The unified strategy silently REPLACED the R52c mapping without a supersession banner.** `prepare_notebooklm.py` cannot be implemented until this is resolved — which mapping is canonical?

### GAP-6: MATH ERROR — Account budgets exceed free-tier limit ⚠️
The account-to-notebook mapping assigns **acc-05, acc-06, acc-07 = 20/mo each** — but free tier caps at **10 DR/month per account**. The table's per-account budgets sum to **130/mo**, not 80. **The 80/month capacity claim is mathematically broken** — max real capacity is 8 accounts × 10 = 80, so the 15-20/mo budget assignments are impossible. The mapping needs a redesign (e.g., 2 accounts per notebook × 10 = 20/notebook, or accept 80 total with different allocation).

### GAP-7: Token density table — UNSOURCED ⚠️
"5–15 sources Excellent, 15–30 Good, 30–50 Degrading, 50+ Poor" — cited as "Research shows" but **no source exists in any research doc**. This is an unsupported claim. The research doc actually recommends **40-50 sources per notebook** (50-source limit is "a feature"). **Direct contradiction between unified strategy (15-25 optimal) and research doc (40-50 optimal).** Needs resolution or sourced evidence.

### GAP-8: SDP automation gate conflicts with protocol ⚠️
COGNITIVE_SCAFFOLDING_PROTOCOL §10: "Until this protocol has been executed manually at least 10 times... **no automation is permitted**." The unified strategy proposes SDP Phase 1 automation immediately. **This violates the protocol's own gate.** Also §8: V-1 Vault is a **hard prerequisite** for automation — the unified strategy lists V-1 as a gap but doesn't sequence it as a blocker.

### GAP-9: Free-tier comparison misleading ⚠️
"Deep Research/month: Free=80 vs Pro=20/day" — Pro gives **20/day = ~600/month** for $19.99. The comparison frames 80/month as "exact match" but a single Pro account provides 7.5× more capacity at $19.99. **The cost-benefit analysis needs re-evaluation** — 8 free accounts (80/mo, $0, 8× ToS risk) vs 1 Pro account (600/mo, $19.99, 1× risk). M7 Local-First doesn't apply here (both are cloud). This is a legitimate strategic question.

### GAP-10: OAuth refresh / session persistence — UNRESEARCHED ⚠️
The strategy says "OAuth refresh, Playwright pool" needs hardening, but no research covers: cookie lifetime (`__Secure-1PSID`/`1PSIDTS`), refresh cadence, headless detection risk (Patchright vs plain Playwright), and multi-profile isolation. notebooklm-mcp uses Patchright (stealth fork) — needs verification it survives Google's bot detection at 8-account scale.

---

## 📋 RECOMMENDED NEXT ACTIONS (priority order)

1. **Resolve GAP-5 first** (notebook architecture conflict) — it blocks `prepare_notebooklm.py` spec.
2. **Correct GAP-1/GAP-2** — pick the real MCP server (recommend `notebooklm-mcp` PleasePrompto or `notebooklm-py[mcp]`), rewrite the deployment section.
3. **Fix GAP-6 math** — redesign account mapping to respect 10 DR/account/month.
4. **Research GAP-3 + GAP-4** — these are the two existential unknowns (ToS risk + Deep Research automation feasibility). **If Deep Research can't be triggered programmatically, the entire 80-DR/month automation premise collapses** and the strategy reverts to manual-mode (which is still viable per the protocol's 10-manual-executions gate).
5. **Re-evaluate GAP-9** — 1× Pro account vs 8× free accounts is a genuine open question.

**Kali recommendation**: Before any deployment, run a **single-account smoke test** (create 1 account, deploy 1 MCP instance, trigger 1 Deep Research, export the report) to validate GAP-4 empirically. This is the cheapest way to de-risk the entire strategy.

---

## 📚 PROVENANCE

- Web sources verified 2026-08-20: felloai.com, toolchase.com, atlasworkspace.ai, notebooklm-to-pdf.com, notebooklm-guide.com, mcp.directory, autocontentapi.com, PyPI (notebooklm-py, notebooklm-mcp-cli), npm (notebooklm-mcp), GitHub (teng-lin/notebooklm-py, moodRobotics/notebooklm-mcp-server, PleasePrompto/notebooklm-mcp)
- Exa search unavailable (401 Invalid API key) — used parallel-search + websearch fallback per SR-V1.

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_notebooklm_gap_audit ⬡ 2026-08-20*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
