<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# (R) CLINE DEEP REVIEW — Subagent Steering Architecture & Four-Model Synthesis
**AP Token**: `AP-CLINE-DEEP-REVIEW-SUBAGENT-STEERING-v1.0.0`
( OMEGA ) ( CLINE ) ( deepseek-v4-flash ) ( cline ) ( trc_deep_review ) ( COMPLETE )

**Date**: 2026-08-22
**Reviewer**: cline/omega-engine (independent, code-verified)
**For**: kali + Architect — final architectural gate before SS-1 sprint
**Artifacts reviewed**: SUBAGENT_STEERING_RESEARCH (339L), CARMCK_SUBAGENT_STEERING_REVIEW (334L),
GEMINI_DEFINITIVE_SUBAGENT_STEERING_REVIEW (193L) + supporting artifacts

---

## 1. VERDICT: CONDITIONAL GO

Direction is correct; ~85% of claimed primitives are code-confirmed. The 70%-exists core is REAL:
ModelGateway, EntityRegistry dual-index, WADLoader topo sort, HealthMonitor breaker factory, A2ABridge
Agent Cards are all present and production-grade. The work IS wiring, not invention.

Three conditions block unqualified GO:
1. **Heritage correction (M14)**: the claimed `[id-soft: quake-1996] Thinker Chain` tag does NOT exist in
   code. The only matching text self-describes as a *metaphor* — re-classify (see §4).
2. **Overlap resolution**: `delegation.py` should NOT be a new file — `subagent_dispatcher.py` already
   implements HandoffPacket + capability registry + dispatch. The real gap is ONLY `a2a_transport.py`.
3. **Secret provisioning**: `OMEGA_INGESTION_SECRET` must be in env before HMAC task-token tests run
   (SovereignSigner raises otherwise).

---

## 2. CODE REALITY CONFIRMATIONS (all file reads verified 2026-08-22)

| Claim | Cited location | Actual | Verdict |
|---|---|---|---|
| ModelGateway = Orchestrator | model_gateway.py:100,184,189 | class @100; `generate()` @ **1079** (not 184/189) | ( concept true / citations wrong ) |
| EntityRegistry._capability_index + get_by_capability | entity_registry.py:338,448-454,573 | all at cited lines, capability index built in _load() 448-454, getter 573 | ( ok ) |
| WADLoader topo sort + IWAD/PWAD priority | wad_loader.py:177-263,376-401 | Kahn + effective_priority(IWAD=100/PWAD=0) 198-263; manifest validation (required/type/extra=forbid) 376-401 | ok |
| HealthMonitor.get_breaker + AsyncCircuitBreaker | health_monitor.py:125,751 | both exact | ok |
| A2ABridge.register_entity/build_agent_card/generate_well_known_json | a2a_bridge.py:225,329,366 | all three exact | ok |
| WAD adapter whitelist | wad_loader.py:482-489 | ADAPTER_MODULE_WHITELIST enforced | ok |
| WAD entity field validation | wad_loader.py:610-667 | type/extra=forbid/range/name-len/domain-limit | ok |
| D-590 P0 fix (SovereignSigner fail-closed) | ingestion.py:76 | raises OmegaError when env missing; NO hardcoded default | ok |
| a2a_transport.py MISSING | src/omega/oracle/ | confirmed absent | gap |
| delegation.py MISSING | src/omega/oracle/ | **subagent_dispatcher.py EXISTS** (HandoffPacket+cap registry+dispatch) | overlap - do NOT create |
| AGENT_REGISTRY.json MISSING | data/coordination/ | absent; BUT runtime capability registry exists (subagent_dispatcher._build_capability_registry) | overlap - do NOT create |
| DELEGATION_LOG.jsonl | data/ | absent | gap confirmed |
| MCP Hub Agent Card endpoint | mcp_servers/omega_hub/server.py | no well-known/agent route | gap confirmed |
| call_with_retry exists | src/omega/oracle/retry_policy.py:33 | present | ok |

---

## 3. MANDATE COMPLIANCE AUDIT (per-mandate)

| M | Ruling | Evidence |
|---|---|---|
| M1 AnyIO | PASS | Oracle core anyio-only. Single `import asyncio` in agents/tty_agent.py:14 (human TTY carve-out, NOT on SS-1 path) |
| M2 Firewall | PASS | WAD whitelist + extra=forbid both active |
| M3 Engine/Stack | PASS | entities only via config/wads |
| M7 Local-First | PASS | provider priorities 0-10 ordered local-first |
| M8 Zero Telemetry | PASS | env-gated secrets only; D-590 verified |
| M9 Typed errors | PASS | OmegaError hierarchy + typed SovereignSigner failure |
| M11 Soul staging | PARTIAL | proposed_lessons.yaml exists 10+ entities; staged_lessons->lessons sink NOT wired to delegation |
| M15 Disk-Proof | PASS | SoulStore atomic writer + capability map persists |
| M16 Scope | PASS | no hardcoded stack names in src/omega |
| M17 Contradiction | **PARTIAL — FAIL-ADJACENT** | Carmack claims 13/17 PASS + 4 PARTIAL (=17) but lists only 3 PARTIAL (M11/M17/M26); auditable off-by-one |
| M22 Provenance | PASS | GenerateResult.provider_name + M22 comment in model_gateway.py |
| M23 No soft-fail | PASS | fail-closed signer verified |
| M24 Venv | PASS | .venv only |
| M25 Streaming | PASS | M25 block present; breakers per-provider timeout |
| M26 Doc gates | PARTIAL | new SS-1 files must run doc-llm-validate before merge |
| M27 Tracking | PASS | ACTIVE_SPRINT/GAP/TASK registries present; 3 N11 tasks recorded completed |

---

## 4. HERITAGE VALIDATION (M14 gate) — WHERE THE REVIEWS SWERVED

The reviews claim: `[id-soft: quake-1996] Thinker Chain` LEGITIMATE, cited at model/entity/a2a_bridge lines.

**Code truth**: grep of entire src/ shows NO such tag. The only occurrences:
- `src/omega/oracle/subagent_dispatcher.py` header: "Heritage: Thinker chain — used for lifecycle tracking metaphor (inspired by Quake 1996)". And critical: the same file ALREADY says "Core concept (agent dispatch) is the user's original design."
- `src/omega/observability/regression_watcher.py:8`: `[id-soft: vet-011] Thinker Chain — periodic background task` (a DIFFERENT, vetted, direct-port pattern: the tick loop).
- The cited `model_gateway.py:100` = class definition (no heritage); `entity_registry.py:338` = doom-1993 Multi-Index Entity (NOT quake Thinker); `a2a_bridge.py:225` = register_entity (no heritage).

**M14 ruling**: **METAPHORICAL — not LEGITIMATE.** The tag does not exist in code; the VET-011 Thinker Chain (the tick-loop port) IS legitimate, but that is a different subsystem. Claims that the delegation architecture inherits the Quake 1996 Thinker Chain as a direct port are OVER-ATTRIBUTED. Per mandates, strip the tag from delegation (or tag it as metaphor), keep vet-011 as-is.

---

## 5. GAPS & RISKS (real vs over-engineered)

REAL (write these):
1. `a2a_transport.py` — genuinely missing, genuinely needed. <80 lines.
2. `DELEGATE_LOG.jsonl` atomic-append — M22 provenance + retest.
3. MCP Hub Agent-Card endpoint — discovery parity.
4. Resource-level admission at delegation-time — Carmack's central catch is REAL: no per-delegation RAM+ctx admit exists today (OOMProtector is process-global; no call on the delegation path).
5. HMAC task-token wrapping — SovereignSigner exists, wrapper doesn't.

OVER-ENGINEERED / DON'T-BUILD:
1. `delegation.py` — extend existing `subagent_dispatcher.py`.
2. `AGENT_REGISTRY.json` — runtime capability registry already exists; DON'T create a second source of truth.
3. Full 3D admission (RkN+KB+concurrent) — the context-rehydration term is the ONLY term that matters free-tier; RAM is global-guard covered.
4. CBOR 40001-40008 / COSE_Sign1 / IETF EAT deep-embed — YAGNI intra-fleet. HMAC task token + SPIFFE + ZONEID already prove identity locally. Defer without EAT until SQ-005 external.

---

## 6. IMPLEMENTATION PLAN CRITIQUE (Carmack vs Gemini vs code truth)

- Carmack Line (2.5d / 3 files) is the correct scale. Gemini 5-phase is over-scoped.
- But the corrected file list is: a2a_transport.py (new) + extensions to subagent_dispatcher.py (NO new delegation.py) + DELEGATE_LOG + MCP agent-card endpoint + admission hook in dispatcher.
- Order risk from Ox Alpha: contract tests must be written for a2a_transport BEFORE dispatcher changes (M21).
- Context cliff risk (16k G-1 modelo): admission must account KB re-hydration tokens or free-tier VMIR silently truncates.

---

## 7. FORWARD RESEARCH PRIORITIZATION (R55-58)

1. R58 Local IPC benchning — run FIRST: de-risks transport claim ('~50-80 lines JSON-RPC vs binary on Zen2'). Small, cheap.
2. R56 Chaos harness — HIGH: ReliabilityBench/Maestro align; catches silent-end drop.
3. R57 AMD memory distillation — MEDIUM (fund post-R58/R56 verifiable, aligns neglect-loop/would win).
4. R55 Agent Capability Attestation (IETF EAT/ACT) — SPECULATIVE for debut. HMAC+SPIFFE+ZONE_ID covers intra-fleet. Defer until SQ-005 external node; then re-land.

---

## 8. SS-1 SPRINT READINESS: READY-WITH-3-BLOCKS-BEFORE-ENTRY

Blocks (must be G-0 of sprint):
1. OMEGA_INGESTION_SECRET provisioned in env/gauntlet (else SovereignSigner raises on CI task-token path).
2. Contract tests for a2a_transport as the first code slice (M21).
3. Heritage correction applied (comment + CREDITS/vet note) so M14 CI gate does not block merge.

Suggested ordering:
- G0: heritage fix + env secret + test skeleton
- G1: a2a_transport + tests
- G2: dispatcher extension + admission
- G3: DELEGATE_LOG + Agent-Card endpoint + CLI
- G4: shadow 50 runs divergence

---

*END REVIEW — evidence files checked live in repo 2026-08-22*
