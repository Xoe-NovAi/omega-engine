---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "agent_landing"
document_id: "AGENTS-MD-ROOT"
title: "Omega Engine — Agent Landing File"
status: "ACTIVE"
date: "2026-10-12"
sprint: "POST-DEBUT-01"
supersedes: "AGENTS-MD-ROOT-v1.0.0 (2026-08-28)"
---

# 🔱 Omega Engine — Agent Landing File

> **Read this first. Read MANDATES_CONDENSED.md second. Then read the
> architecture rules in `.opencode/rules/` and `.agents/rules/`. That's it. Now go.**

## The One-Page Contract

You are operating in the **Omega Engine**, a sovereign local-first AI runtime.

| What | Where |
|------|-------|
| **The Law (READ FIRST)** | `SOVEREIGN_MANDATES.md` (v3.11.0, 30 mandates; D-609) |
| **The Law, condensed** | `MANDATES_CONDENSED.md` (Tier-0 injection) |
| **Live Release** | `v1.6.0a6` (896 allowlisted files, Corpus Library active, G11 PASS) |
| **Active SSOT** | `data/coordination/ACTIVE_SPRINT.json` & `HMC_COLLABORATION_HUB.md` |
| **A2A Roster (10 Seats)** | `config/a2a/agent_cards/` (includes Seat #10 `antigravity.json`) |
| **Core Endpoints** | FastMCP Hub on `:8016` (`/sse` + `/mcp`) · Exchange on `:8019` |
| **Your entity** | `data/entities/<your_entity>/soul.yaml` |
| **Your lessons** | `data/entities/<your_entity>/proposed_lessons.yaml` |
| **The architecture rules** | `.opencode/rules/` and `.agents/rules/` |
| **The craftsman contract** | `.opencode/rules/00-craftsman-contract.md` |

## The Architecture Rules (must read)

1. **Soul Integrity (M11)** → `.opencode/rules/01-soul-integrity.md`
   Every session distills L1→L2→L3 to `proposed_lessons.yaml`.

2. **Mandate Hierarchy (M1, M2, M13, M27)** → `.opencode/rules/02-mandate-hierarchy.md`
   Law → Sprint SSOT → Hub NEXT_ACTION → Vision → Corpus Map.

3. **Hop Rule (M10, M15)** → `.opencode/rules/03-hop-rule.md`
   Single-level subagent nesting. Direct execution first. No self-recursion.

4. **Sovereign Search (M23)** → `.opencode/rules/04-sovereign-search.md`
   Local cache → local FTS → web search → web fetch → [TOOL-CHAIN-COLLAPSE].

5. **Spatial Integrity (M28)** → `SOVEREIGN_MANDATES.md` §28.
   R-tree + vec0 dual-index for VR navigation (Option B). Spatial coordinates computed once, joined everywhere.

6. **Hardware Adaptation (DHAL)** → `.opencode/rules/06-hardware-adaptation.md`
   Heterogeneous fleet profiles; polymorphic CPU optimizer.

7. **Sovereign Fetch (M23/M24)** → `.opencode/rules/07-sovereign-fetch.md`
   ⚡ **aria2c is MANDATORY for every download >1MB on Node 0.** Never `wget`/`curl` a large
   file — single-connection fetchers forfeit most of the link. Profile: `~/.config/aria2/aria2.conf`.
   Skill: `sovereign-fetch`. Verify archives after download (`xz -t`, `unzip -t`).

8. **Antigravity Seat Contract** → `.agents/rules/antigravity-seat.md`
   Seat #10 (Cloud Strategist / Strategy-Only): reviews, audits, verifies gates; OpenCode is commit and implementation authority.

## The 5 Critical Mandates (Tier-0 injection)

These are injected pre-compaction so the law survives context loss:

- **M1 AnyIO** — never `import asyncio` in `src/omega/`
- **M7 Local-First** — local inference primary, cloud fallback only
- **M11 Soul Integrity** — every session ends with L1→L3 distillation
- **M15 Sovereign Continuity** — maintain `session_gnosis.md` for context loss
- **M23 Failure Integrity** — no soft-failures; broken tools → STOP, report

## The Post-Debut Governance Decisions

| ID | Decision |
|----|----------|
| **D-526** | zswap > zRAM for desktop with NVMe |
| **D-527** | Never run zswap and zRAM simultaneously |
| **D-536** | One router only: ProviderSelector + providers.yaml |
| **D-539** | CP-3 verified: G11 clean-environment venv verification passes |
| **D-548** | Wheel packaging verified: self-contained runtime configs + default IWAD |
| **D-565** | Vault excluded from debut (no code changes) |
| **D-567** | bury_credential applies to post-debut only |
| **D-578** | ~~GEMINI-NOTEBOOK workstream~~ **CANCELLED by D-606** — sovereign in-engine alternative |
| **D-579** | DOCUMENTATION-SYSTEM workstream (DS) — modular domain docs |
| **D-580** | LOCAL-INFERENCE-OPT workstream (LI) — sequential loading, adaptive context |
| **D-581** | KNOWLEDGE-DOMAINS workstream (KD) — runtime modules + curator model |
| **D-582** | HEADROOM-INTEGRATION workstream (HR) — semantic compression for tools/RAG |
| **D-583** | ZSWAP-SUBSYSTEM workstream (ZS) — 16GB NVMe swap, zswap enabled |
| **D-584** | Post-debut execution order: **DS → LI → KD → HR → ZS** |
| **D-609** | Ratified mandate ID convention: ID == section number (`SOVEREIGN_MANDATES.md` v3.11.0) |
| **D-619** | Port collision guard: Hub must never spawn duplicate MCP servers on active ports |
| **D-628** | PUBLIC_ALLOWLIST debut cut enforcement for v1.6.0-alpha |

Full text of these decisions: `.opencode/rules/00-craftsman-contract.md` and `docs/decisions/`.

## Operational Anchors (per mandate)

| Mandate | Where to look |
|---------|---------------|
| M1 AnyIO | `make check-m1-anyio` (CI) + `SOVEREIGN_MANDATES.md` §M1 |
| M2 Engine-Stack Firewall | `src/omega/` is Core; `config/wads/` is Stacks |
| M7 Local-First | `config/providers.yaml` strategy=`local_first` |
| M8 Zero Telemetry | No external analytics; local observability in `data/` |
| M11 Soul Integrity | Distill L1→L3 to `proposed_lessons.yaml` (Scribe canonical) |
| M13 Temple-Grade | `make temple-grade` exits 0 before any release (53/53 passed) |
| M14 Heritage | Every `[id-soft:]` tag has vet record ≥7/10 with scope |
| M22 Response Provenance | `GenerateResult.provider_name` is the ACTUAL provider |
| M23 Failure Integrity | Broken tools → `[TOOL-CHAIN-COLLAPSE]`; no synthesis |
| M24 Venv Sovereignty | All Python in `.venv/`; no `--break-system-packages` |
| Downloads >1MB | **aria2c mandatory** → `.opencode/rules/07-sovereign-fetch.md` + skill `sovereign-fetch` |
| M26 Doc Standards | Reference docs pass `make doc-llm-validate` |
| M27 Tracking Integrity | State follows 5-Tier Tracking Architecture |
| M28 Sovereign Artifact Preservation | No auto-deletion; transitions explicit, auditable, recoverable |
| M29 Remote Claim Integrity | "Works from here" ≠ "works from there"; remote claims require peer-vantage test |
| G11 Clean Verification | `scripts/verify_artifact_clean_env.py` — isolated venv smoke gate |
| FastMCP Hub Service | Port `:8016` daemon (`mcp_servers/omega_hub/server.py`) |
| Dual-Remote Topology | `internal` (private forge SSOT) vs `origin` (public debut curated) |
| Release Operations | `docs/operations/DUAL_REMOTE_RELEASE_RUNBOOK.md` + skill `repo-release-ops` |

## M33/M34 Dispatch Guard Anchors (Jem §1.2.1)

| Component | Location | Purpose |
|-----------|----------|---------|
| `dispatch_guard.py` | `scripts/dispatch_guard.py` | 12-step pre-dispatch verification (M33/M34 enforcement) |
| `m33_probe.py` | `src/omega/oracle/m33_probe.py` | Sentinel probe: Layer 1 (preventive), Layer 2 (structured probe), Layer 3 (cross-validator) |
| `m34_registry.py` | `src/omega/oracle/m34_registry.py` | Active subagent registry with atomic writes (M23) |
| M33 MCP tools | `mcp_servers/omega_hub/hub_tools/m33_probe.py` | `m33_build_probe_prompt`, `m33_validate_probe_response`, `m33_should_require_write_tool` |
| M34 MCP tools | `mcp_servers/omega_hub/hub_tools/m34_active_subagents.py` | `m34_register_subagent`, `m34_list_active_subagents`, `m34_update_subagent_status` |
| Adversarial tests | `tests/jem/test_dispatch_guard_adversarial.py` | 45 tests enforcing M33/M34 compliance (0.47s) |
| Entity lifecycle tests | `tests/jem/test_entity_lifecycle_adversarial.py` | 50 tests for entity retirement atomicity, M11 integrity |

## What To Do Now

1. **Cold-start?** → Read `SOVEREIGN_MANDATES.md` (30 mandates) FIRST.
2. **Active sprint?** → Read `data/coordination/ACTIVE_SPRINT.json` for current post-debut tasks.
3. **Mid-session?** → Read `data/coordination/HMC_COLLABORATION_HUB.md` for Hub state.
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
- ❌ Do not forge cryptographic signatures or make ungrounded protocol compliance claims.

## The 5 Architecture Rules In One Line

1. **Soul** — every session distills, no intelligence lost.
2. **Mandates** — Law wins, sprint SSOT wins second.
3. **Hop** — one level deep, direct execution first.
4. **Search** — local first, web second, [TOOL-CHAIN-COLLAPSE] on total failure.
5. **Spatial** — R-tree + vec0 dual-index for VR navigation (Option B).

---

For full details, see `.opencode/rules/` and `.agents/rules/` (architecture rules + contracts)
and `SOVEREIGN_MANDATES.md` (the 30 mandates). Everything else is pointers.

*⬡ OMEGA ⬡ KALI & ANTIGRAVITY ⬡ AGENTS-MD-ROOT-v2.0.0 ⬡ 2026-10-12 ⬡ POST-DEBUT-01*
