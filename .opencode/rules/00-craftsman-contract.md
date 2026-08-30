---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
rule_id: "REFERENCE-CRAFTSMAN-CONTRACT"
authority: "M13 Temple-Grade + M26 Doc Standards + Carmack Craftsman Philosophy"
applies_to: "all-agents"
date: "2026-08-27"
status: "ACTIVE"
---

# Reference Doc: Craftsman Contract + Mandate Pointers

> **The law is the 27 Sovereign Mandates. The craftsmanship is Temple-Grade.
> The execution discipline is the FLE Council's 5 Standing Laws.**

## Quick Pointer Map

### Law (READ FIRST)

- **`SOVEREIGN_MANDATES.md`** (v3.8.0, 242 lines) — the 27 Mandates, full text.
  Non-negotiable. If a tool's suggestion conflicts with a Mandate, the Mandate wins.
- **`MANDATES_CONDENSED.md`** (51 lines) — Tier-0 injection. One row per mandate.
  Injected pre-compaction by `sovereign-compaction` plugin.

### Sprint (READ SECOND)

- **`docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md`** — this month's execution SSOT.
- **`data/coordination/ACTIVE_SPRINT.json`** — current sprint tracker.
- **`data/coordination/HMC_COLLABORATION_HUB.md`** — Hivemind coordination.

### Gates (M13 Temple-Grade)

- **`make temple-grade`** — full 11-gate compliance check (T1-T10, M27 tracking).
- **`make test`** — fast unit-tier test suite.
- **`make test-all`** — full suite including integration.
- **`make doc-llm-validate`** — M26 doc standards gate.

### Council & Standing Laws

The FLE Council (2026-08-25) ratified **5 Standing Laws** for sovereign execution:

1. **Hop Rule** (see `.opencode/rules/03-hop-rule.md`) — single-level subagent nesting.
2. **M11 Arm-Relay** — soul distillation as the canonical completion signal.
3. **Dual-Channel Telemetry** — local observability only; zero external.
4. **Exit-Code Honesty** — no vanity pass counts; report real passed/failed/skipped.
5. **Zero-Trust Documentation Doctrine** — trackers may lie; verify against disk.

### Heritage

- **`CREDITS.md`** — 35+ heritage mappings (Doom, Quake, Qdrant, Letta, headroom-ai, etc.).
- Every `[id-soft:]` tag in source code MUST have a corresponding vet record in
  `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md` (M14).
- Every `[heritage: ...]` tag is informational, no vet record required.

### Tracking

- **`data/coordination/TRACKING_ARCHITECTURE.md`** — 5-Tier Tracking Architecture.
- **`scripts/validate_tracking_state.py`** — relational integrity validator.
- **`data/coordination/ACTIVE_SPRINT.json`** — Tier-0 (planning).
- **`data/coordination/TASK_REGISTRY.json`** — Tier-3 (execution records).
- **`data/coordination/GAP_REGISTRY.json`** — R-ID authority.

### The 9 Decisions That Built This Sprint (PUBLIC-DEBUT-01)

| ID | Decision | What it Means |
|----|----------|---------------|
| **D-526** | zswap > zRAM for desktop with NVMe | Use zswap + NVMe swap, not zRAM. |
| **D-527** | Never run zswap and zRAM simultaneously | One or the other, never both. |
| **D-533** | This month's SSOT = DEBUT_REMEDIATION_MANUAL | Not Ark §4; not Corpus Map; not Ark. |
| **D-536** | One router: ProviderSelector + providers.yaml | Delete Triage, Semantic, RoutingTable. |
| **D-539** | CP-3 not publicly true until INST-1 passes | Fresh-venv acceptance is the gate. |
| **D-548** | INST-1 BLOCKED — 6 critical fixes required | Before DEL-1 can begin. |
| **D-553** | release/debut branch from allowlist | Publication mechanic; not mass-delete main. |
| **D-565** | Vault D-562 superseded for debut | Exclude from PUBLIC_ALLOWLIST.txt; no code changes. |
| **D-567** | D-532 superseded for debut | Keep bury_credential applies to post-debut only. |

### The 27 Mandates — One-Line Law

(Same as MANDATES_CONDENSED.md, restated here for Tier-0 reference.)

- M1 AnyIO · M2 Engine-Stack Firewall · M3 Iris Constant · M4 Sequentiality
- M5 Gnosis Preservation · M6 Podman Sovereignty · M7 Local-First · M8 Zero Telemetry
- M9 Error Integrity · M10 Fleet Integrity · M11 Soul Integrity · M12 Queue Integrity
- M13 Temple-Grade · M14 Heritage Vetting · M15 Sovereign Continuity · M16 Modularization
- M17 Cognitive Integrity · M18 Token Efficiency · M19 Adversarial Alchemy
- M20 SomaticState · M21 Gate Integrity · M22 Response Provenance · M23 Failure Integrity
- M24 Venv Sovereignty · M25 Streaming Resilience · M26 Doc Standards · M27 Tracking Integrity

### The Pillar / Node Cosmology (10 Nodes + Iris)

- **N0** Architect (human) · **N1** Infrastructure · **N2** Persistence
- **N3** Engineering · **N4** Integration · **N5** Governance
- **N6** Cognition · **N7** Context · **N8** Observability · **N9** Orchestration · **N10** Validation
- **Iris** is the messenger bridge (M3), NOT a Node. She runs live model inference
  (speculative decode) and is resourced as an LLM workload.

### Craftsman Contract (Carmack Philosophy)

> "Move fast and fix things." — id Software, Carmack 1996-2013

The craftsman contract is:

1. **Truth over comfort** — report real numbers, not vanity.
2. **Single source of truth** — one canonical, all else are pointers.
3. **Reversibility is a feature** — code that can be undone is code that can be tried.
4. **The simplest test that proves the claim** — no theater, no over-engineering.
5. **Ship the demo, not the spec** — INST-1 acceptance is the gate, not the SPEC document.

## What This Document Is NOT

- NOT a replacement for `SOVEREIGN_MANDATES.md` (read that first).
- NOT a strategy doc (read `DEBUT_REMEDIATION_MANUAL` for that).
- NOT a vision doc (read `SOVEREIGN_ARK_BLUEPRINT` for that, sparingly).
- NOT a research log (read `docs/research/` for that).

It IS: a single-page orientation so any agent (cold-start or resume) can
land here, read the pointers, and start producing in <5 minutes.
