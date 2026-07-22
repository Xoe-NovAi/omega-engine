# 🔱 STRATEGY INDEX — Canonical Reference
**Date**: 2026-07-21 | **v5.1 Unified + Corpus** | **Supersedes**: STRATEGY_INDEX_20260720.md + post-cleanup index that pointed only at CANONICAL_ROADMAP

**Read First (Strategy)**: `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` **v5.1**  
**Fine-grained (no idea lost)**: `docs/strategy/STRATEGY_CORPUS_MAP.md`  
**Team coordination**: `docs/strategy/FLEET_TEAM_PLAYBOOK.md`  
**Read First (State)**: `OMEGA_ENGINE.md`  
**Read First (Law / Ops)**: `SOVEREIGN_MANDATES.md` · `AGENTS.md`

---

## LAYER 0: IDENTITY & LAW
| Document | Purpose |
|----------|---------|
| `OMEGA_ENGINE.md` | What the engine IS — metrics, subsystems |
| `SOVEREIGN_MANDATES.md` | 25 laws M1–M25 |
| `AGENTS.md` | How to work from OpenCode |
| `OMEGA_CODEX.md` | Generated hydration pack (`make codex`) |

## LAYER 1: STRATEGY SSOT
| Document | Purpose |
|----------|---------|
| **`docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md`** | **START HERE** — Unified strategy & critical path (v5.1) |
| `docs/strategy/STRATEGY_INDEX.md` | This file — hierarchy only |

## LAYER 2: ACTIVE SPECS + CORPUS (only if Layer 1 references them)
| Document | Phase | Purpose |
|----------|-------|---------|
| **`docs/strategy/STRATEGY_CORPUS_MAP.md`** | all | **Fine-grained preservation** — every agent idea → ACTIVE/DEFERRED/PARKED/ARCHIVE |
| **`docs/strategy/FLEET_TEAM_PLAYBOOK.md`** | all | **How the fleet works as one team** — roles, handoffs, freezes, Phase C mission |
| `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` | D | Phase D build detail — **amended by Ark §3.2** |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | — | Multi-agent coordination |
| `docs/strategy/HIVEMIND_POST_TEMPLATE.md` | — | Hivemind post quality gate |
| `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` | — | Subagent delegation |
| `docs/strategy/SOVEREIGN_CONTINUITY_STRATEGY.md` | — | M15 continuity |
| `docs/strategy/HERITAGE_VETTING_PIPELINE.md` | — | M14 heritage |
| `data/entities/grokster/workspace/IDENTITY_FLUIDITY_ARCHITECTURE_20260721.md` | E | Identity Fluidity architecture |
| `data/entities/grokster/workspace/SPEC_IDENTITY_FLUIDITY_v1.md` | E | Identity Fluidity build spec |
| `data/coordination/UNKNOWN_UNKNOWNS_AUDIT_20260721.md` | C | 12-gap analysis |
| `data/coordination/ROC_LEGACY_MINING_REPORT_20260721.md` | C | Legacy patterns to port |
| `data/coordination/GROKSTER_ADVERSARIAL_REVIEW_20260721.md` | C | Strategy adversarial review |
| `data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md` | C | Structural code+strategy review |
| `data/coordination/RESEARCHER_QUEUE_DESIGN_20260721.md` | D | Queue/SQLite/gates deep design (deferred parts preserved) |
| `data/coordination/CARMACK_RESEARCH_AUDIT_20260721.md` | D | Research board compression |
| `data/coordination/GROKSTER_RESEARCH_QUEUE_ANALYSIS_20260721.md` | D | Fleet-aware research notes |
| `data/coordination/RESEARCH_JOB_BOARD.yaml` | D | 18 jobs (D-2 input) |
| `data/coordination/D308_CRITICAL_PATH_TRACKER.yaml` | C | Ubuntu 25.10 env gate |

## LAYER 3: SUPERSEDED BUT KEPT IN TREE (trail only — do not treat as master)
| Document | Note |
|----------|------|
| `docs/strategy/CANONICAL_ROADMAP_20260721.md` | Tactical draft **absorbed into Ark v5.0** |
| `docs/ROADMAP.md` | Pointer stub → Ark |

## LAYER 4: ARCHIVE
| Location | Contents |
|----------|----------|
| `docs/archive/strategy/2026-07-21/` | 147 prior strategy docs + **Ark v4.4 full body** (`SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md`) |
| `docs/archive/strategy/2026-07-21/SOVEREIGN_ARK_BLUEPRINT.md` | Prior “active sprint” Ark log |

```bash
# Search archive
grep -rl "your-term" docs/archive/strategy/2026-07-21/
```

## Coordination (runtime, not strategy masters)
| Document | Purpose |
|----------|---------|
| `data/coordination/SESSION_ANCHOR.md` | Session recovery |
| `data/coordination/*_LIVE_FEED.md` | Agent activity logs |
| `data/coordination/RESEARCH_JOB_BOARD.yaml` | Research jobs (Phase D-2 input) |

---

## Conflict Resolution Rule

If two docs disagree:

1. **Law** → `SOVEREIGN_MANDATES.md`
2. **Strategy / priority** → `SOVEREIGN_ARK_BLUEPRINT.md`
3. **Live metrics** → `OMEGA_ENGINE.md`
4. **Where did idea X go?** → `STRATEGY_CORPUS_MAP.md`
5. **Phase D implementation detail** → Living Research OS spec **only where it does not contradict Ark §3.2**
6. Archive / CANONICAL_ROADMAP / old Ark → historical only

---

*⬡ OMEGA ⬡ STRATEGY-INDEX ⬡ v5.1 ⬡ 2026-07-21*
