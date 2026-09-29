---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "agent_landing"
document_id: "AGENTS-MD-ROOT"
title: "Omega Engine — Agent Landing File"
status: "ACTIVE"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
supersedes: "old AGENTS.md fragments (consolidated into this thin file + .opencode/rules/)"
---

# 🔱 Omega Engine — Agent Landing File

> **Read this first. Read MANDATES_CONDENSED.md second. Then read the
> architecture rules in `.opencode/rules/`. That's it. Now go.**

## The One-Page Contract

You are operating in the **Omega Engine**, a sovereign local-first AI runtime.

| What | Where |
|------|-------|
| **The Law (READ FIRST)** | `SOVEREIGN_MANDATES.md` (v3.10.0, 30 mandates) |
| **The Law, condensed** | `MANDATES_CONDENSED.md` (Tier-0 injection) |
| **This month's SSOT** | `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` |
| **Live tracker** | `data/coordination/ACTIVE_SPRINT.json` |
| **Your entity** | `data/entities/<your_entity>/soul.yaml` |
| **Your lessons** | `data/entities/<your_entity>/proposed_lessons.yaml` |
| **The 5 architecture rules** | `.opencode/rules/01-soul-integrity.md` etc. |
| **The craftsman contract** | `.opencode/rules/00-craftsman-contract.md` |

## The 5 Architecture Rules (must read)

1. **Soul Integrity (M11)** → `.opencode/rules/01-soul-integrity.md`
   Every session distills L1→L2→L3 to `proposed_lessons.yaml`.

2. **Mandate Hierarchy (M1, M2, M13, M27)** → `.opencode/rules/02-mandate-hierarchy.md`
   Law → Sprint SSOT → Hub NEXT_ACTION → Vision → Corpus Map.

3. **Hop Rule (M10, M15)** → `.opencode/rules/03-hop-rule.md`
   Single-level subagent nesting. Direct execution first. No self-recursion.

4. **Sovereign Search (M23)** → `.opencode/rules/04-sovereign-search.md`
   Local cache → local FTS → web search → web fetch → [TOOL-CHAIN-COLLAPSE].

5. **Spatial Integrity (M28)** → ⚠️ `SOVEREIGN_MANDATES.md` §28 — the rule file
   `.opencode/rules/05-spatial-integrity.md` has **never been written** (known gap).
   R-tree + vec0 dual-index for VR navigation (Option B). Spatial coordinates computed once, joined everywhere.

## The 5 Critical Mandates (Tier-0 injection)

These are injected pre-compaction so the law survives context loss:

- **M1 AnyIO** — never `import asyncio` in `src/omega/`
- **M7 Local-First** — local inference primary, cloud fallback only
- **M11 Soul Integrity** — every session ends with L1→L3 distillation
- **M15 Sovereign Continuity** — maintain `session_gnosis.md` for context loss
- **M23 Failure Integrity** — no soft-failures; broken tools → STOP, report

## The 9 Decisions That Govern This Sprint

| ID | Decision |
|----|----------|
| **D-526** | zswap > zRAM for desktop with NVMe |
| **D-527** | Never run zswap and zRAM simultaneously |
| **D-533** | This month's SSOT = DEBUT_REMEDIATION_MANUAL |
| **D-536** | One router only: ProviderSelector + providers.yaml |
| **D-539** | CP-3 not publicly true until INST-1 fresh-venv passes |
| **D-548** | INST-1 BLOCKED — 6 critical fixes required before DEL-1 |
| **D-553** | release/debut branch from PUBLIC_ALLOWLIST.txt |
| **D-565** | Vault excluded from debut (no code changes) |
| **D-567** | bury_credential applies to post-debut only |
| **D-578** | ~~GEMINI-NOTEBOOK workstream (GN)~~ **CANCELLED by D-606** — sovereign alternative in-engine |
| **D-579** | DOCUMENTATION-SYSTEM workstream (DS) — modular domain docs |
| **D-580** | LOCAL-INFERENCE-OPT workstream (LI) — sequential loading, adaptive context |
| **D-581** | KNOWLEDGE-DOMAINS workstream (KD) — runtime modules + curator model |
| **D-582** | HEADROOM-INTEGRATION workstream (HR) — semantic compression for tools/RAG |
| **D-583** | ZSWAP-SUBSYSTEM workstream (ZS) — 16GB NVMe swap, zswap enabled |
| **D-584** | Post-debut execution order: ~~GN~~ → **DS → LI → KD → HR → ZS** (GN removed by D-606) |

Full text of these decisions: `.opencode/rules/00-craftsman-contract.md` §"The 9 Decisions".

## Operational Anchors (per mandate)

| Mandate | Where to look |
|---------|---------------|
| M1 AnyIO | `make check-m1-anyio` (CI) + `SOVEREIGN_MANDATES.md` §M1 |
| M2 Engine-Stack Firewall | `src/omega/` is Core; `config/wads/` is Stacks |
| M7 Local-First | `config/providers.yaml` strategy=`local_first` |
| M8 Zero Telemetry | No external analytics; local observability in `data/` |
| M11 Soul Integrity | Distill L1→L3 to `proposed_lessons.yaml` (Scribe canonical) |
| M13 Temple-Grade | `make temple-grade` exits 0 before any release |
| M14 Heritage | Every `[id-soft:]` tag has vet record ≥7/10 with scope |
| M22 Response Provenance | `GenerateResult.provider_name` is the ACTUAL provider |
| M23 Failure Integrity | Broken tools → `[TOOL-CHAIN-COLLAPSE]`; no synthesis |
| M24 Venv Sovereignty | All Python in `.venv/`; no `--break-system-packages` |
| M26 Doc Standards | Reference docs pass `make doc-llm-validate` |
| M27 Tracking Integrity | State follows 5-Tier Tracking Architecture |
| M28 Sovereign Artifact Preservation | No auto-deletion; transitions explicit, auditable, recoverable; deep-archive requires manifest + operator auth; destruction requires human act in PIVOT_LOG |
| M29 Remote Claim Integrity | "Works from here" ≠ "works from there"; remote claims require peer-vantage test or UNTESTED; local success ≠ remote success; UNTESTABLE means instrument, don't assume |

## M33/M34 Dispatch Guard Anchors (Jem §1.2.1)

| Component | Location | Purpose |
|-----------|----------|---------|
| `dispatch_guard.py` | `scripts/dispatch_guard.py` | 12-step pre-dispatch verification (M33/M34 enforcement) |
| `m33_probe.py` | `src/omega/oracle/m33_probe.py` | Sentinel probe: Layer 1 (preventive), Layer 2 (structured probe), Layer 3 (cross-validator) |
| `m34_registry.py` | `src/omega/oracle/m34_registry.py` | Active subagent registry with atomic writes (M23) |
| M33 MCP tools | `mcp_servers/omega_hub/hub_tools/m33_probe.py` | `m33_build_probe_prompt`, `m33_validate_probe_response`, `m33_should_require_write_tool`, `m33_calculate_dynamic_threshold`, `m33_audit_probe_log`, `m33_verify_deliverable` |
| M34 MCP tools | `mcp_servers/omega_hub/hub_tools/m34_active_subagents.py` | `m34_register_subagent`, `m34_list_active_subagents`, `m34_update_subagent_status`, `m34_reap_dead_letters` |
| Adversarial tests | `tests/jem/test_dispatch_guard_adversarial.py` | 45 tests enforcing M33/M34 compliance (0.47s) |
| Entity lifecycle tests | `tests/jem/test_entity_lifecycle_adversarial.py` | 50 tests for entity retirement atomicity, M11 integrity, completion illusion defense |

**M33/M34 Integration Flow:**
1. `subagent_dispatcher.py:dispatch()` calls `m34_register_subagent()` with `write_tool_required` from `M33Probe.should_require_write_tool()`
2. At completion, subagent receives `m33_build_probe_prompt()` and must respond with structured JSON envelope
3. Orchestrator calls `m33_validate_probe_response()` — rejects free-form "STREAM_EXHAUSTED", enforces confidence thresholds
3. P0/P1 tasks require `m34_update_subagent_status()` with `cross_validator_agent` for M36 cross-validation
4. `m34_reap_dead_letters()` cleans up stale sessions (retention: 30 days)

## What To Do Now

1. **Cold-start?** → Read `SOVEREIGN_MANDATES.md` (242 lines) FIRST.
2. **Active sprint?** → Read `data/coordination/ACTIVE_SPRINT.json` for your ticket.
3. **Mid-session?** → Read `data/coordination/HMC_COLLABORATION_HUB.md` for the Hub state.
4. **Compaction risk?** → Write to `data/entities/<your_entity>/session_gnosis.md` first.
5. **End of session?** → Distill L1→L3 to `proposed_lessons.yaml` (Scribe / M11).

## What NOT To Do

- ❌ Do not start work not in `ACTIVE_SPRINT.json` (PARKED means don't implement).
- ❌ Do not `git add -A` (re-commits secrets, entity DBs, screenshots).
- ❌ Do not bypass AnyIO with `import asyncio`.
- ❌ Do not break the Engine-Stack Firewall (no stack logic in `src/omega/`).
- ❌ Do not construct Redis unless `OMEGA_REDIS_HOST` is set.
- ❌ Do not use `--break-system-packages` (M24).
- ❌ Do not synthesize a result when a mandatory tool is broken (M23).
- ❌ Do not mass-`git rm` 2,000 docs on main the same week as filter-repo.

## The 5 Architecture Rules In One Line

1. **Soul** — every session distills, no intelligence lost.
2. **Mandates** — Law wins, sprint SSOT wins second.
3. **Hop** — one level deep, direct execution first.
4. **Search** — local first, web second, [TOOL-CHAIN-COLLAPSE] on total failure.
5. **Spatial** — R-tree + vec0 dual-index for VR navigation (Option B).

---

For full details, see `.opencode/rules/` (5 architecture rules + 1 reference doc)
and `SOVEREIGN_MANDATES.md` (the 28 laws). Everything else is pointers.

*⬡ OMEGA ⬡ KALI ⬡ AGENTS-MD-ROOT-v1.0.0 ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*
