<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# SOVEREIGN MANDATES — CONDENSED (Tier 0 Injection)

**36 lines | 27 mandate rows | ~1.5K tokens | Repo root: `MANDATES_CONDENSED.md`**  
*(Remediated 2026-08-21: line-count claim corrected — original "57 lines" matched the stale v3.7.0 codex snapshot by coincidence. CI-1 gate is now CONTENT-BASED per Architect ruling Q1. See `09_SPEC_DEVIATIONS.md` DEV-01. Hazard ref: N7_DOMAIN_INDEX D1.)*  
**Full detail**: `SOVEREIGN_MANDATES.md` (27 mandates, v3.8.0)

| # | Mandate | One-Liner | Status |
|---|---------|-----------|--------|
| M1 | AnyIO Absolute | All async uses AnyIO; never `asyncio` directly; wrap blocking in `anyio.to_thread.run_sync` | ✅ |
| M2 | Engine-Stack Firewall | Core (`src/omega/`, `config/omega.yaml`) separate from Stacks (`config/wads/`); no stack logic in core | ✅ |
| M3 | Iris Constant | Iris = messenger bridge, NOT a Node; no N1-N10 assignment | ✅ |
| M4 | Sequentiality | Plan → Verify → Execute loop for architectural changes; no cowboy coding | ✅ |
| M5 | Gnosis Preservation | Every session ends with L1→L2→L3 distillation to `proposed_lessons.yaml` | ✅ |
| M6 | Podman Sovereignty | Quadlets: `UserNS=keep-id` + `User=1000`; `:U` flag FORBIDDEN on shared volumes | ✅ |
| M7 | Local-First | Local inference PRIMARY (native-gguf → lmster → Ollama); cloud FALLBACK only | ⚠️→✅ |
| M8 | Zero Telemetry | No external analytics/phone-home; local observability in `data/` acceptable | ✅ |
| M9 | Error Integrity | Typed, traceable, testable errors; no bare `except:`; `OmegaError` subtypes at API boundaries | ✅ |
| M10 | Fleet Integrity | Lean agent fleet; map capabilities to N1-N10/Lattice slots before new agents; max 14 agents | ✅ |
| M11 | Soul Integrity | No session close without Soul Distillation (L1→L2→L3 → `proposed_lessons.yaml`) | ✅ |
| M12 | Queue Integrity | Every request = atomic contract; terminal states only; dead-letter for failures | ⚠️ Advisory |
| M13 | Temple-Grade | All code passes T1-T11 gates; `make temple-grade` before release; T11 exempted | ✅ |
| M14 | Heritage Vetting | `[id-soft:]` tags require vet record in `HERITAGE_VET_LOG.md`; score ≥7/10; Qualification Gate | ✅ |
| M15 | Sovereign Continuity | Maintain `session_gnosis.md` + `SESSION_ANCHOR.md`; no reliance on `/compact` for state | ✅ |
| M16 | Modularization | Core engine portable; no hardcoded paths/env assumptions; MCP Hub abstraction layer | ✅ |
| M17 | Cognitive Integrity | Verify memory consistency; Qliphoth taxonomy for contradiction detection | ✅ |
| M18 | Token Efficiency | No waste; but NEVER compress to semantic loss (sane-boundary: precision > brevity) | ✅ |
| M19 | Adversarial Alchemy | Weaponize systemic constraints; but simple bugs = simple fixes (sane-boundary) | ✅ |
| M20 | SomaticState Serialization | ctypes `llama_copy_state_data`/`llama_set_state_data` via `anyio.to_thread.run_sync` | ✅ |
| M21 | Gate Integrity | Every typed return path has contract test validating `isinstance(result, ExpectedType)` | ✅ |
| M22 | Response Provenance | Log actual provider at response receipt (`GenerateResult.provider_name`), not dispatch intent | ✅ |
| M23 | Failure Integrity | No soft-failures; mandatory tool failure → `[TOOL-CHAIN-COLLAPSE]` + log + stop | ✅ |
| M24 | Venv Sovereignty | All Python in `.venv`; no `--break-system-packages`; no `pip install --user` for deps | ✅ |
| M25 | Streaming Resilience | Chunk timeout 30s + heartbeat (continue); total timeout 5min → graceful fallback | ✅ |
| M26 | Doc Standards | All ref docs pass `make doc-llm-validate`; sprint plans in `docs/sprints/<name>/` | ✅ |
| M27 | Tracking Integrity | 5-Tier architecture; `GAP_REGISTRY.json` authority; Tier-0 statuses fixed; `validate_tracking_state.py` | ✅ |

**Injection Point**: Pre-compaction hook (`experimental.session.compacting`) via `sovereign-compaction.ts` plugin.  
**Tier 0**: This file (1.5K tokens). **Tier 1/2**: Full `SOVEREIGN_MANDATES.md` + `AGENTS.md`.