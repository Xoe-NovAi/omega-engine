# 🔱 NotebookLM / Gemini Notebook Strategy v2.0 — Synthesis & Integration
**AP Token**: `AP-NOTEBOOKLM-SYNTHESIS-v2.0-20260820`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_notebooklm_synthesis ⬡ ACTIVE

**Date**: 2026-08-20
**Status**: RATIFIED SYNTHESIS — supersedes `docs/strategy/NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md` (v1.0) for all factual claims
**Source reports**:
- `NOTEBOOKLM_GAP_AUDIT_20260820.md` (10 gaps)
- `NOTEBOOKLM_RESEARCH_A_EXISTENTIAL_20260820.md` (NLG-A: GAP-3/4/1/2)
- `NOTEBOOKLM_RESEARCH_B_OPERATIONAL_20260820.md` (NLG-B: GAP-10/7/9)
- `NOTEBOOKLM_RESEARCH_C_ARBITRATION_20260820.md` (NLG-C: GAP-5/6/8)

**Product note**: NotebookLM was renamed **Gemini Notebook** in July 2026 (same product, same limits). "NotebookLM" retained below for search-artifact continuity.

---

## 🎯 V2.0 STRATEGIC DIRECTION (Kali Arbitration)

The v1.0 strategy was **fundamentally sound in architecture but factually broken in execution assumptions**. v2.0 keeps the 6-notebook + synthesis design and the SDP automation path, but corrects the tooling, the cost model, the account math, and the deployment pattern.

| Dimension | v1.0 (BROKEN) | v2.0 (CORRECTED) |
|-----------|---------------|------------------|
| **Tool** | "MCPNotebookLM 28 tools" (fabricated) | **`notebooklm-py`** (teng-lin, RPC, `[mcp]` extra) — only lib with Deep Research report trigger + Markdown export |
| **Deployment** | Docker `ghcr.io/omega-engine/mcp-notebooklm:latest` (does not exist) | **`pip install notebooklm-py[mcp]` + systemd** (Docker optional via khengyun RPC wrapper) |
| **Cost model** | 8× Free accounts = 80 DR/mo, $0 | **HYBRID: 1× Pro ($19.99, ~600 DR/mo) primary + free for non-quota tasks** |
| **Account math** | 130 DR/mo (impossible) | **80 DR/mo (8×10, each ≤10)** |
| **Token density** | "5-15 Excellent … 50+ Poor" + "40-50 optimal" (contradictory, unsourced) | **5-25 sources = sweet spot; up to 50 only if tightly coherent + label-scoped** |
| **Notebook map** | "R52c 5-notebook" (silent replacement) | **Unified 6-notebook (NB-1..NB-6) canonical** + supersession banner over R52c/LIVING §1.5 |
| **SDP gate** | Immediate automation proposed | **Honor §10: manual mode now, automate after 10 manual runs + V-1 Vault** |
| **Auth** | "OAuth refresh, Playwright pool" (prototype false) | **`master_token.json` + `RotateCookies` ≤600s + Patchright `channel='chrome'`** |

---

## 📋 GAP RESOLUTIONS (all 10)

### GAP-1 — MCP tool surface → `notebooklm-py`
**Resolution**: Adopt **`notebooklm-py`** (teng-lin) with `[mcp]` extra. It is the ONLY candidate with documented Deep Research **report** trigger (`source add-research --mode deep`) + Markdown export (`download`). RPC-based (no browser at runtime) → best fit for local-first (M7) headless systemd deployment. The v1.0 "28 tools / Chat-Manage-Compose" list matched no real server and is **deleted**.

### GAP-2 — Deployment reality → pip + systemd
**Resolution**: `pip install "notebooklm-py[mcp]"` in the Omega venv (M24), run as a systemd user service (stdio MCP or guarded HTTP on 127.0.0.1). Docker is OPTIONAL via the khengyun/notebooklm-mcp RPC wrapper (browserless). The `ghcr.io/omega-engine/mcp-notebooklm:latest` image and `Makefile.notebooklm` targets **do not exist** and are removed from the plan.

### GAP-3 — 8-account ToS/ban → HIGH RISK, mitigated or avoided
**Resolution**: Google ToS explicitly prohibits "multiple accounts to misuse our services" (XDA) and "accounts created by a bot" (policies.google.com/terms). Real bans: notebooklm-py issue #228 (account disabled after 1 automated request, TLS-fingerprint correlation), IP-level 5-account lockout (167h). **If a free fleet is used**, it MUST have: dedicated static IP per account + isolated browser profile + staggered human-like scheduling + exponential backoff with jitter + browser-identical TLS. **v2.0 default: avoid the free fleet for Deep Research** (see GAP-9).

### GAP-4 — Deep Research automation → GO (conditional)
**Resolution**: Automation is FEASIBLE via `notebooklm-py` (`source add-research --mode deep` → Markdown) and `notebooklm-go` (RPC, no browser). **Critical correction**: `notebooklm-mcp` (TheSethRose) `research_start --mode deep` is **source-finding, NOT the quota-consuming Deep Research report**. The v1.0 flow assumed the MCP server triggers Deep Research — it does not. v2.0 uses `notebooklm-py` for the report path.

### GAP-5 — Notebook architecture → Unified 6-notebook canonical
**Resolution** (per NLG-C): Adopt the **unified 6-notebook mapping (NB-1..NB-6)** as canonical. R52c is explicitly ARCHIVED/STALE (predates IWAD, heritage vetting, synthesis); LIVING_RESEARCH_OS_SPEC §1.5 is a verbatim copy of R52c. NB-2 Stacks, NB-3 Legacy, NB-6 Ω-SYNTHESIS are genuinely new domains. **Action**: add a supersession banner to the unified strategy; resolve the dropped Validation Suite (exclude from NotebookLM — better served by local M13 `make temple-grade`).

### GAP-6 — Account budget math → 80 DR/mo corrected
**Resolution** (per NLG-C): Each account ≤10 DR/mo. Corrected envelope: NB-1:20, NB-2:20, NB-3:20, NB-4:10, NB-5:10, NB-6:0. Monthly cyclic rotation (primary +1 each month) preserves ≤10/account and the 80 envelope. The v1.0 130/mo sum (acc-05/06/07 = 20 each) is mathematically impossible and deleted.

### GAP-7 — Token density → 5-25 sweet spot
**Resolution** (per NLG-B): Lower bands (5-15/15-30) are sourced; upper bands (30-50/50+) are unsourced extrapolation. The v1.0 "40-50 optimal" claim **contradicts its own table and is wrong**. Corrected: target **5-25 high-relevance, single-topic sources**; use source labels as context filter; approach 50 only if tightly coherent + label-scoped. Re-label 30-50 as "Degrading (noise-driven, not a hard cliff)", 50+ as "At hard cap — split recommended."

### GAP-8 — SDP gate → Honor §10
**Resolution** (per NLG-C): **Honor the COGNITIVE_SCAFFOLDING_PROTOCOL §10 gate** — deploy fleet in manual mode now, automate only after (1) 10 manual SDP executions logged in the ledger + (2) V-1 Vault completion (the actual hard blocker regardless of §10). The unified strategy's own line "deploy today in manual mode" aligns; the immediate-automation proposal is withdrawn pending the gate.

### GAP-9 — Pro vs free → HYBRID
**Resolution** (per NLG-B): **1× Google AI Pro ($19.99, ~600 DR/mo) as primary Deep Research engine + free accounts for non-quota tasks** (50 chats/day, 3 audio/day, source ingestion). 1 Pro = 7.5× the entire 8-free fleet at lower risk and 1 credential. Scale to 2× Pro ($39.98, ~1,200/mo) before ever considering a free fleet. **Reject the 8-free fleet for Deep Research** — highest-risk, lowest-yield, ToS-violating.

### GAP-10 — OAuth/session → master_token design
**Resolution** (per NLG-B): NotebookLM has no public OAuth — auth = Google session cookies. **Do NOT store rotating cookie snapshots** (die in minutes). Store **`master_token.json`** (durable) + mint per-run session via `RotateCookies` (≤600s cadence). Cookie set completeness matters (`__Secure-1PSIDTS` + sibling required). Use **Patchright `channel='chrome'`** for bot-evasion if a browser is needed. One account per Vault slot; never share cookie sets across workers.

---

## 🔧 INTEGRATION INTO RESEARCH & STRATEGY

### A. Unified Strategy doc (`NOTEBOOKLM_UNIFIED_STRATEGY_20260820.md`) → v2.0 corrections applied:
1. Header status → "v2.0 — CORRECTED per gap audit + 3-subagent research"
2. Executive summary → 8-account framing corrected to HYBRID
3. §MCPNotebookLM deployment → replaced with `notebooklm-py` + systemd
4. §Account-to-Notebook mapping → corrected 10/account = 80/mo
5. §Token Optimization → 5-25 sweet spot
6. §Tier Decision → HYBRID (1× Pro + free)
7. §Critical Gaps → V-1/MCP hardening corrected
8. §Strategic Verdict → SDP gate note added
9. §Provenance → 3 missing docs removed; research reports added

### B. Research docs to update:
- `NOTEBOOKLM_RESEARCH_20260819.md` — token-density section: replace "40-50 optimal" with 5-25 sweet spot (cross-ref NLG-B)
- `NOTEBOOKLM_BEST_PRACTICES.md` — add `notebooklm-py` as the recommended tool; remove Docker-first assumption
- `COGNITIVE_SCAFFOLDING_PROTOCOL.md` — no change needed (§10/§8 honored); add NotebookLM-specific ledger reference

### C. PIVOT_LOG D-series (registered separately):
- D-571: Adopt `notebooklm-py` (RPC) as the NotebookLM automation tool (supersedes fabricated MCPNotebookLM)
- D-572: HYBRID cost model — 1× Pro primary Deep Research + free for non-quota
- D-573: Corrected 80 DR/mo account budget (8×10, ≤10/account) + cyclic rotation
- D-574: Unified 6-notebook (NB-1..NB-6) canonical; R52c + LIVING §1.5 superseded
- D-575: Honor SDP §10 gate — manual mode now, automate after 10 runs + V-1 Vault
- D-576: Token density 5-25 sweet spot (40-50 claim retracted)
- D-577: `master_token.json` + RotateCookies auth model for V-1 Vault

### D. Next actions (post-synthesis):
1. **Single-account smoke test** (NLG-SMOKE): 1 Pro account + `notebooklm-py` → 1 Deep Research → Markdown export → validate GAP-4 empirically
2. **V-1 Vault**: implement `master_token.json` storage + RotateCookies refresh (GAP-10) — hard blocker for any automation
3. **`prepare_notebooklm.py`** (NL-1): implement against `notebooklm-py` report export (not MCP)
4. **Manual SDP loop ×10**: log in ledger; then enable automation per §10

---

## 📊 V2.0 CAPACITY MODEL (HYBRID)

| Resource | 1× Pro | 8× Free | Used for |
|----------|--------|---------|----------|
| Deep Research/mo | **~600** | 80 | Pro = primary (SDP automation) |
| Chats/day | 500 | 400 | Free accounts (non-quota) |
| Audio/day | 3 | 24 | Free accounts |
| Sources/notebook | 300 | 50 | Pro (deep corpus) / Free (curated) |
| Ban risk | Low | HIGH | Pro preferred |

**Net**: 1 Pro delivers 7.5× the DR of the 8-free fleet at lower risk. The 8-free fleet is retired from the Deep Research path; free accounts remain useful for ingestion/synthesis/chat.

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_notebooklm_synthesis ⬡ 2026-08-20*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-v4-flash-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
