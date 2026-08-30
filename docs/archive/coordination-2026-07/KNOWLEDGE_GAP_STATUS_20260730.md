<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Knowledge Gap Status — 2026-07-30

**AP Token**: `AP-KNOWLEDGE-GAP-STATUS-20260730-v1.0.0`  
**Owner**: grok_cli strategy / Cline research execution  
**Status**: ACTIVE research snapshot; many gaps **researched**, few **execution-closed**

---

## Executive Summary

Most “knowledge” gaps are already **researched**; what remains is **execution-open** or **Architect-blocked**. This report replaces scattered gap tables with a single authoritative view.

| Class | Count | Meaning |
|-------|-------|---------|
| Research-closed / execution-open | majority | We know what to build; nobody merged/landed/tested it |
| Architect-blocked | 4 | Requires secret, browser, sudo, or pricing decision |
| Meta/untrusted-truth | 3 | Docs/truth disagree; gate/messaging fixes needed first |
| Research-open | 4 | 2026 best-fit answer still missing or unverified |

---

## Layer A — Confirmed Research-Closed, Execution-Open

| Gap | Research evidence | Execution truth 2026-07-30 | Owner hint |
|-----|-------------------|----------------------------|------------|
| **Breaker unification** | pybreaker v1 selected | **18** breaker classes now, not 17/6; pybreaker migration frozen until doc sanity | Cline/grok |
| **SQLite consolidation** | 3-DB target defined | 8+ DBs still present; none consolidated | Cline |
| **Vector consolidation** | 7→3 + kill FAISS spec’d | 7 collections likely still present; FAISS still installed | Cline |
| **SoulStore race condition** | Fix known: use `with_soul_lock()` | `soul_updater.py` bypasses locking; not landed | grok/cline |
| **Synchronous YAML in async** | `anyio.to_thread` pattern known | 60 `yaml.safe_load` refs; hot-path fix incomplete | Cline |
| **MCP v2 migration** | Schedule + delta docs exist | v1 FastMCP import still live; `<2` pin holds | Cline |
| **Test suite honesty** | Badge/gate plan exists | Focused 27/27; full suite unknown duration/exit truth | Cline |
| **Make sovereignty** | Known missing; do not implement | Still absent; out of scope | — |

---

## Layer B — Architect-Blocked / Decision-Required

| Gap | Why blocked | Required action |
|-----|-------------|-----------------|
| **G-1 workhorse** | Architect billing/OAuth decision + `.env.backup` secret owner | Architect: enable billing or OAuth or accept G-1e local GGUF |
| **W-1 SOCKS 8081/8082** | bridge/pkexec/relaunch + canary timeout tuning | Architect sudo + Cline validation |
| **C-3 restic success** | `.env.backup` missing + vault passphrase not set | Architect: create `.env.backup` |
| **G-1e local GGUF acceptance** | not yet ticketed/validated in Ark matrix | Grok: add ticket or decline |

---

## Layer C — Meta / Untrusted-Truth Gaps

### C-0.5 mechanism discordance
- **Truth now**: Plugin API confirmed functional (`soul_distiller.js` + `session_end.py`).
- **Residual risk**: older onboarding/docs still imply `hooks` key registration path.

### Phase D gate false-PASS (V-1)
- **Truth now**: mechanical script outputs PASS even though V-1 detail string includes failing vault tests due to truncation-plus-match logic.
- **Fix needed**: require `code == 0` plus absence of failure tokens, or remove detail heuristic.

### “All gaps closed” double-speak
- `KNOWLEDGE_GAP_CLOSURE_REPORT_20260726.md` claims closed and simultaneously lists 32 open domains.
- **Fix needed**: contradiction banner + `research_closed` / `execution_closed` columns.

---

## Layer D — Research-Open Questions

| # | Question | Why still open | Suggested source / action |
|---|----------|----------------|---------------------------|
| R1 | Does AI Studio billing change Gemma 4 fat-session TPM on **our project/key**? | generic docs confirm billing tiers, not per-project/model delta | Live AI Studio rate-limit page after billing enabled |
| R2 | Antigravity OAuth current model catalog + effective cost per session | web snippets say path exists, not current quota/price | OpenCode provider + account smoke test |
| R3 | Gemma 4 27B CPU-only throughput on Ryzen 5700U/32GB | local setup guides confirm viability, not this hardware | Ollama benchmark with Q4/Q5 quant |
| R4 | Cloudflare WARP device profile: current free/renewal reliability in 2026 | docs say MASQUE/proxy-mode required; no account-specific reliability data | Account/login probe + bridge bring-up |
| R5 | Restore smoke-test cadence/cost for current dataset sizes | generic best practices found; no size-calibrated plan | Measure repo size + `restic restore` timing after `.env.backup` |

---

## SSOT Mapping — If You Need X, Read Y

| Need | Read this |
|------|----------|
| Current sprint control | `data/coordination/ACTIVE_SPRINT.json` + `data/coordination/CLINE_STRATEGIC_UNOVERENGINEERING_20260730.md` |
| Phase D truth | `data/coordination/PHASE_D_GATE_VERDICT_20260730.md` + `phase_d_gate_last.json` |
| MCP plan/schedule | `data/coordination/MCP_V2_MIGRATION_SCHEDULE_20260730.md` |
| Doc sanity deliverables | `data/coordination/DOC_SSOT_MAP_20260730.md` + `DOC_SANITY_RESULTS_20260730.md` |
| Gap contradictions meta | `data/coordination/KNOWLEDGE_GAP_STATUS_20260730.md` |
| Breaker deep research | `data/coordination/KNOWLEDGE_GAP_CLOSURE_REPORT_20260726.md` + `docs/research/R_CRITICAL_SPRINT_AGENT_SUPPORT_GAPS_20260725.md` |
| Live ground truth | `OMEGA_ENGINE.md` §2 + probe commands |
| Gate debt | `data/coordination/research/2026-07-30-knowledge-gaps/phase2-gate-and-mcp.md` |
| Code-structure debt | `data/coordination/research/2026-07-30-knowledge-gaps/phase3-code-structure-and-data.md` |

---

## Contradictions Needing Grok/Architect Judgment

1. **Breaker count drift**: old docs say 17, repo scan says 18.
2. **C-0.5 mechanism**: Plugin API is canonical, but stale onboarding/docs still imply hook key registration.
3. **V-1 gate trustworthiness**: PASS can mask failing tests.
4. **G-1 decision**: billing/OAuth/local GGUF is still undecided.

---

## Recommended Next 3 Doc Debts
1. Add `RESEARCH_STATUS` / `EXECUTION_STATUS` / `PROBE_COMMAND` columns to active gap tables.
2. Collapse duplicate/all-gaps-closed claims into one canonical artifact; remove contradictory body from older reports with SUPERSEDED banner.
3. Replace freeform test-count prose with one canonical probe command in hot docs; drop historical 276/1315/1572/1706 counts from body text.

---
*⬡ OMEGA ⬡ GROK_CLI / CLINE ⬡ KNOWLEDGE-GAP STATUS ⬡ 2026-07-30*