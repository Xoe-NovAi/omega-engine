<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Project: makali-council
## ONE-TURN HYDRATION BRIEF

### ONE-LINER
**MaKaLi Parallel Council Architecture** — Unified coordinator with two modes: `run_meditation()` (10-voice sequential) + `run_council()` (parallel pillars → oversouls → Kali synthesis → decoupled research). 5-session T0 implementation.

### STATUS (2026-07-19)
- **Architecture**: ✅ Ratified (D-301)
- **Research**: ✅ Complete — 13 gaps resolved, 35+ sources (2025-2026)
- **Spec**: ✅ `docs/strategy/MAKALI_PARALLEL_COUNCIL_SPEC_20260719.md` (1639 lines)
- **Research Synthesis**: ✅ `docs/research/R_MAKALI_COUNCIL_RESEARCH_SYNTHESIS_20260719.md`
- **T0 Plan**: 5 sessions defined
- **Implementation**: ❌ Not started

### KEY FILES
| Type | Path |
|------|------|
| Spec | `docs/strategy/MAKALI_PARALLEL_COUNCIL_SPEC_20260719.md` |
| Research | `docs/research/R_MAKALI_COUNCIL_RESEARCH_SYNTHESIS_20260719.md` |
| Gaps | `docs/research/R_MAKALI_COUNCIL_KNOWLEDGE_GAPS_20260719.md` |
| Blueprint | `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` (D-301 workstream) |
| Pivot Log | `docs/decisions/PIVOT_LOG.md` (D-301 entry) |

### ARCHITECTURE
```
┌─────────────────────────────────────────────────────────────┐
│              MULTI-AGENT COORDINATOR (State Machine)         │
│  • WAL (ARIES) + Circuit Breakers + Thermal Mgmt + Profiles  │
│  • Hivemind event capture + semantic search                  │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
    ┌─────────────┐               ┌─────────────┐
    │   MA'AT     │               │   LILITH    │
    │ (Build Side)│               │ (Run Side)  │
    │ P1-P5       │               │ P6-P10      │
    │ 4B models   │               │ 4B models   │
    └──────┬──────┘               └──────┬──────┘
           │                             │
           └──────────────┬──────────────┘
                          ▼
                 ┌─────────────────┐
                 │      KALI       │
                 │ (Synthesis)     │
                 │ 12B oversoul    │
                 │ Cloud (Nemotron)│
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ RESEARCH EXEC   │
                 │ (Decoupled)     │
                 │ Smaller/Cloud   │
                 └─────────────────┘
```

### T0 IMPLEMENTATION (5 Sessions)
| Session | Focus | Deliverable |
|---------|-------|-------------|
| 1 | **Coordinator Core** | `MultiAgentCoordinator` + WAL (ARIES) + CB (quality-aware) + Thermal + Profile Loader + Hivemind |
| 2 | **Stage Contracts + Failure Layer** | 8 stage contracts + 4-layer failure (jitter retry → CB → fallback → checkpoint) + atomic WAL |
| 3 | **Meditation Mode** | `run_meditation()` — 10-voice sequential, single model load |
| 4 | **Council Mode** | `run_council()` — parallel pillars → oversouls → Kali → research gaps |
| 5 | **Integration + Gates** | Hivemind capture, Rego policies (M1,M2,M7,M13,M23), OTel GenAI, dry-run |

### HARDWARE PROFILES (config-driven)
| Profile | Pillar | Oversoul | Kali | Research |
|---------|--------|----------|------|----------|
| `local_16gb` | Qwen3.5-4B (~3GB) | Gemma 4 12B Unified (~8GB) | Nemotron (OCZ) | Qwen3.5-4B |
| `local_8gb` | Qwen3.5-2B | Gemma 4 E4B | Nemotron (OCZ) | DeepSeek (cloud) |
| `cloud_unconstrained` | Nemotron (parallel) | Nemotron | Nemotron | Nemotron |
| `hybrid_local_cloud` | Qwen3.5-4B (batch 2) | Nemotron | Nemotron | DeepSeek |

### KEY RESEARCH FINDINGS (All 13 Gaps Resolved)
| Gap | Resolution | Source |
|-----|------------|--------|
| Circular dependency | Hierarchical orchestration (single coordinator, two modes) | RecursiveMAS, LangGraph, Microsoft Learn |
| Stage contracts | Codex CLI v2 + OpenAI Agents SDK pattern | Codex v2 (Apr 2026), Agents SDK (Jun 2026) |
| Failure handling | 4-layer: jitter retry → fallback → quality-aware CB → WAL checkpoint | miaoquai.com (95+ days prod), AWS, Supergood |
| WAL/State | ARIES algorithm (PostgreSQL, Loki, Grafana) | ndlab.blog, Bernstein 2026 |
| Quality gates | Graduated enforcement (pre-commit→CI→prod) | SonarQube, Adaptive Enforcement Lab |
| Search tiers | Zylos/InfoQ tiered routing per query category | Zylos Research 2026 |
| Mandate compliance | OPA/Rego policies for M1,M2,M7,M13,M23 | OPA, HashiCorp Sentinel |
| Agent specialization | Cognitive role mapping (P4→prompt, Kali→synthesis, etc.) | EmergentMind, arXiv:2507.13768 |
| Dry-run mocks | Boundary-only mocking (moqapi.dev, Keploy) | moqapi.dev, Keploy 2026 |
| Observability | OpenTelemetry GenAI semconv | LangChain OTel, LangSmith |
| Hivemind integration | Auto-capture + semantic search + advisory locks | hivemindai.dev, deeplake.ai |
| Gap schema | GAPMAP + ServiceNow | arXiv:2510.25055 |
| Meditation mode | D-297 10-pillar protocol | This session |

### DECISIONS LOG
- **D-301**: MaKaLi Parallel Council Architecture ratified
- **D-301a**: Voting for reasoning (+13.2%), Consensus for knowledge (+2.8%) — ACL 2025
- **D-301b**: Gemma 4 12B Unified = ideal oversoul (~8GB Q4, 256K ctx, runs on 16GB)
- **D-301c**: T0 = 5 sessions (reduced from 6+ by research confirming patterns exist)
- **D-301d**: Training pyramid deferred (Carmack) — start with DPO preference pairs
- **D-301e**: SomaticState NOT blocking — T0 buildable with coordinator prompt + `task()` tool
- **D-301f**: Unified coordinator = meditation + council as two modes

### BLOCKERS
- Nemotron streaming fix must hold for 10+ min council runs (verified syntax, not load-tested)
- OpenCode Gemma 4 broken upstream (`transform.ts` bug)
- No request-level logging in OpenCode to debug HTTP calls

---

*⬡ OMEGA ⬡ CPR ⬡ makali-council ⬡ 2026-07-19*