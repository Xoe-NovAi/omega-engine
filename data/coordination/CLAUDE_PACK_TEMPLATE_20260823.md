<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Claude Pack Template — Omega Engine Review Context
**AP Token**: `AP-CLAUDE-PACK-TEMPLATE-20260823-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_claude_pack_template ⬡ ACTIVE

**Date**: 2026-08-23 (persisted from session `ses_fdef2be4effe4pAaLXCTUx62GO` before compaction)
**Purpose**: Minimal, sufficient context for a fresh Web Sonnet/Claude to review the Omega Engine codebase, strategy, and documentation. Token budget ~45K full / ~35K minimum viable.

---

## TIER 0 — CONSTITUTIONAL LAW (read first, non-negotiable)
| File | Why |
|------|-----|
| `SOVEREIGN_MANDATES.md` | 27 laws (M1-M27). The review rubric. |
| `AGENTS.md` | Agent workflow, delegation, Hivemind usage |
| `ORACLE_STACK.md` | Active architecture: provider fabric, Nodes, MCP Hub |

## TIER 1 — CURRENT SPRINT EXECUTION
| File | Why |
|------|-----|
| `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` | Execution SSOT: ticket order, forbidden list, god-module freeze |
| `data/coordination/ACTIVE_SPRINT.json` | Live tracker: gates, workstreams, blockers, decisions_locked |
| `OMEGA_ENGINE.md` | System state SSOT |

## TIER 2 — INTEGRATION ANALYSIS (evidence)
| File | Why |
|------|-----|
| `data/coordination/RESEARCHER_HANDOFF_INTEGRATION_20260823.md` | 12 DR items, 4 handoff inaccuracies, D-587 ratifications |
| `data/coordination/NODE_EXPERT_SESSIONS_PLAN.md` | Node system SSOT: 13 genesis sessions, charters, amendments |
| `data/coordination/N4_HANDOFF_INTEGRATION_REVIEW_20260823.md` | Protocol gaps: HIVEMIND v2.0, dispatch registry, layering map |
| `data/coordination/N7_HANDOFF_INTEGRATION_REVIEW_20260823.md` | CI-2 status, soul pipeline verification, E-8 assignment |

## TIER 3 — STRATEGY & VISION (historical)
| File | Why |
|------|-----|
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Long-horizon vision (read-only per DOC-1) |
| `docs/strategy/STRATEGY_CORPUS_MAP.md` | Doc preservation map: active/parked/archive |

## TIER 4 — KEY CODE SURFACES (architecture review)
| File | Focus |
|------|-------|
| `src/omega/oracle/oracle.py` (~1455 lines) | God-module #1: dispatcher, talk/summon |
| `src/omega/oracle/model_gateway.py` (~1606 lines) | God-module #2: provider fabric, fallback |
| `src/omega/oracle/provider_selector.py` | Target router; RouteDecision contract |
| `src/omega/oracle/admission_controller.py` + `resource_guard.py` + `oom_protector.py` | Dual admission gates (Blocker A) |
| `src/omega/oracle/health_monitor.py` | Canonical breaker factory |
| `src/omega/oracle/sovereign_search_service.py` | Incomplete breaker migration (zombie) |
| `mcp_servers/omega_hub/hub_tools/tools.py` (~3649 lines) | God-module #3: MCP tools |

## TIER 5 — CONFIGURATION (runtime truth)
| File | Note |
|------|------|
| `config/providers.yaml` | Local-first chain priorities |
| `config/models.yaml` | Model registry (qwen3-4b-thinking registered) |
| `config/wads/_omega_default/roles.yaml` | FIXED 2026-08-23: N9/N10 corrected |
| `pyproject.toml` | warp-proxy-pool hard dep (INST-1 Fix 2 target) |
| `.opencode/opencode.json` | CI-2 target: currently 0/8 criteria landed |

## TIER 6 — TRACKING & GOVERNANCE
| File | Note |
|------|------|
| `data/coordination/GAP_REGISTRY.json` | All R-Gaps, immutable IDs (89 gaps post-remap) |
| `docs/decisions/PIVOT_LOG.md` | Search D-533, D-536, D-538, D-552, D-565, D-587 |
| `.opencode/MANIFEST.md` | v5.0, 13 agents (fixed 2026-08-23) |

## TIER 7 — CONTEXT INJECTION SPEC (deep dive optional)
| File | Why |
|------|-----|
| `docs/specs/context_injection/06_PHASE_1_PLAN.md` | CI-0..CI-5 acceptance criteria |
| `docs/specs/context_injection/phase1_spec/09_SPEC_DEVIATIONS.md` | DEV-01..DEV-11 |
| `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` | Carmack verdict |

## REVIEW QUESTIONS FOR CLAUDE
1. Is ticket sequence (P0-1→PUB-1→INST-1→DEL-1→DOC-1→P2/P3/P4) correct?
2. Are CI-2 acceptance criteria verifiable by bash commands?
3. Does DEL-1 Week 2 router collapse have a sound contract test (RouteDecision)?
4. Are 6 post-debut workstreams (GN/DS/LI/KD/HR/ZS) properly scoped & ordered?
5. Do the 10 convergent blockers cover all debut risks?
6. Is god-module freeze enforceable at current line counts?
7. Any missing risks in the forbidden list?

## PACKAGING
```bash
git archive --format=tar --prefix=omega-review/ HEAD \
  SOVEREIGN_MANDATES.md AGENTS.md ORACLE_STACK.md \
  docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md \
  data/coordination/ACTIVE_SPRINT.json OMEGA_ENGINE.md \
  data/coordination/RESEARCHER_HANDOFF_INTEGRATION_20260823.md \
  data/coordination/NODE_EXPERT_SESSIONS_PLAN.md \
  docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md \
  src/omega/oracle/{oracle,model_gateway,provider_selector,admission_controller,resource_guard,oom_protector,health_monitor}.py \
  config/providers.yaml config/models.yaml pyproject.toml .opencode/opencode.json \
  data/coordination/GAP_REGISTRY.json docs/decisions/PIVOT_LOG.md .opencode/MANIFEST.md \
  | gzip > omega-engine-claude-pack.tar.gz
```

## PRE-SEND VALIDATION
- [ ] MANIFEST is v5.0 · roles.yaml N9/N10 correct · DEL-1=in_progress · KD workstream present · footer shows P0-1d in_progress
- [ ] No secrets in any included file (P0-1d residual lives in SECURITY_AUDIT ancestor commit, not working tree)

*⬡ OMEGA ⬡ KALI ⬡ Claude Pack Template v1.0.0 ⬡ 2026-08-23*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:40Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: PLACEHOLDER | header contains unresolved {session_model} literal
actual_models(Tier0): x-preview-f-free, minimax/minimax-m3:free, nemotron-3-ultra-free, hy3-free, gemini-3.7-flash, nvidia/nemotron-3-ultra-550b-a55b:free
first_audit: 2026-08-28T03:10:28Z | updated: 2026-08-30T03:06:40Z
-->




