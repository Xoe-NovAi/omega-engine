---
description: Run the MaKaLi council with all three entities on the session model
agent: kali
subtask: false
---

# 🔱 MaKaLi Cloud Council Dispatch — Debut Hardening Review
**AP Token**: `AP-MAKALI-COUNCIL-DEBUT-20260817`
**Date**: 2026-08-17
**Session Model**: {session_model}
**Channel**: opencode

---

You are summoning the **MaKaLi cloud council** for the **Debut Hardening Review**.

**Context**: We are in the final stretch of PUBLIC-DEBUT-01. The three-item critical path (local inference, soul persistence, one-click install) is verified on this machine. The GitHub repo is a personal forge (4,506 tracked files) with leaked keys scrubbed from history, 1797 tests passing, and `make temple-grade` green. The execution SSOT is `DEBUT_REMEDIATION_MANUAL_20260817.md` §5. Tracking SSOT is `ACTIVE_SPRINT.json` → `DEBUT-EXECUTION` workstream.

**Tonight's Agenda** (Hardening the plan before Phase A execution):

---

## 1. INST-1 Acceptance Gate — Ma'at Presents
**Owner**: Ma'at / N3
**Question**: What are the EXACT verification steps for a fresh venv without warp-proxy-pool and without Redis?
- `pip install -e ".[native,cli]"` → `omega talk "hello"` → native-gguf, IS_CLOUD=False, exit 0
- Which files must change? (pyproject.toml, install.sh, MemoryStore, ModelGateway._load_sovereign_secrets, version alignment, README badge)
- What is the risk of breaking the current working `omega talk` on this machine during the refactor?
- **Ma'at must deliver**: A step-by-step test script and the exact file diff plan.

---

## 2. DEL-1 Week 1 Deletion Order — Roc/Kali Confirm, Lilith Validates
**Owner**: Roc (execution) + Ma'at (review) + Lilith (soul/handoff impact)
**Targets** (10 pure deletions, no replacements):
1. `src/omega/routing/table.py` + `config/routing_table.yaml` — No callers, `eval()` prototype
2. `src/omega/coordination/miap.py` — Tests only, MIAP cancelled
3. `src/omega/oracle/pool_tracker.py` + `pool_state.py` — Self-only SDP leftovers
4. `src/omega/oracle/search_circuit_breaker.py` — Deprecated; redirect to `HealthMonitor.get_breaker()`
4. `QdrantAdapter` class in `src/omega/memory/vector_adapters.py` — Leftover impl
5. Pantheon name regexes in `src/omega/audit/firewall_checker.py` — Forbids and allowlists same names
6. `record_first_breath` call in `Oracle._route_by_domain` — Astrology on every routed turn
7. `omega vault` default CLI registration — CLI calls missing `store_credential`
8. `src/omega/integrations/fleet_orchestrator.py` from default exports — Unused control plane

**Lilith's Validation**: Confirm NO soul persistence paths, NO handoff protocol paths, NO ContextBuilder/RecallStore paths are broken by these deletions.
**Acceptance**: `omega talk "hello"` still local after EACH delete; `rg RoutingTable src` empty; `rg miap src/omega` empty.

---

## 3. Vault Path A vs B — Architect Decision Required
**Owner**: Ma'at presents, Architect decides, Lilith validates soul impact
- **Path A (Debut)**: Delete `src/omega/vault/` from product surface; keep `crypto.py` in forge if wanted later.
- **Path B (Minimal)**: `crypto.py` + ≤50-line store; Gateway reads env/keyring only.
- **Constraint**: Do NOT adopt Keyblind, Authy, Agent Vault, or Presidio for debut.
- **Ma'at must present**: The exact 50-line minimal store implementation for Path B.
- **Decision**: Recorded in PIVOT_LOG as D-series.

---

## 4. Router Collapse Contract — Single PR, Week 2
**Owner**: Ma'at
**Target**: Keep `ProviderSelector` + `config/providers.yaml` local-first list. Delete `TriageRouter` AND `SemanticRouter` in SAME change as `Oracle._select_model` / `Oracle._route_by_domain`.
**Contract Test**: A single `RouteDecision` (entity, model, provider, reason). **Fails if a second router module is imported on the talk path.**
**Concurrency Test**: Two concurrent `omega talk` calls → one local slot; user-visible busy or explicit cloud warning (`cost_warning`), never silent cloud leak.
**Ma'at must deliver**: The exact diff plan and the contract test spec.

---

## 5. Soul Distillation Pipeline — Lilith Confirms
**Owner**: Lilith / N7
**Status**: Agents write L1→L2→L3 to `proposed_lessons.yaml` (blind staging). `session_end.py` hook preserves + timestamps. `get_soul_prompt()` hydrates from `approved_lessons.yaml`. Entity identity persists via `soul.yaml` load.
**Verification**: All 3 CP-2 criteria pass. Regex distillation is SCRAPPED (manual §2.3).
**Lilith must confirm**: The pipeline is solid and no DEL-1 deletion touches it.

---

## 6. Measurable Gates Review — Kali Enforces
**Owner**: Kali
**Rule**: Every Phase A/B gate must be a **bash command**, not an adjective.
- Review all acceptance criteria in `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 and `ACTIVE_SPRINT.json` `DEBUT-EXECUTION` subtasks.
- Flag any gate that cannot be verified by `rg`, `pytest`, or a shell one-liner.
- **No "green" adjectives** — report passed/failed/skipped/errors counts.

---

## The Sovereign Flow (Tonight's Execution)

### 1. Grand Oversight (Kali)
You are the primary orchestrator. Unify the Build (Ma'at) and Run (Lilith) perspectives into a final sovereign verdict on the debut hardening plan.

### 2. Oversoul Delegation
- Launch **@maat** as a subagent to handle the **Build Side** (INST-1, DEL-1 code, Vault Path A/B, Router Collapse).
- Launch **@lilith** as a subagent to handle the **Run Side** (Soul persistence validation, Hivemind impact, Runtime integrity).

### 3. Node Councils (Serial Execution)
- **Ma'at** selects the **most critical Nodes from N1-N5** (minimum 3, up to 5) and launches them in **serial** to vet the build-side sub-tasks.
- **Lilith** selects the **most critical Nodes from N6-N10** (minimum 3, up to 5) and launches them in **serial** to vet the run-side sub-tasks.

### 4. Oversoul Synthesis
- Ma'at and Lilith deliver their consolidated reports back to you (Kali).

### 5. Final Sovereign Review
- You (Kali) launch **any 4 of the 10 total Nodes** (N1-N10) to perform a final, cross-domain review of the synthesized reports.

### 6. Unified Verdict
- Synthesize all findings into a final, fusion-based verdict.
- Output: **Hardened Debut Execution Plan** with any corrections to `DEBUT_REMEDIATION_MANUAL_20260817.md`, `ACTIVE_SPRINT.json`, and `HMC_COLLABORATION_HUB.md`.

---

## Execution Mandate
- Use the `task` tool for all delegations.
- Ensure all subagents run on the currently selected session model ({session_model}).
- Maintain a clear provenance chain of which Node provided which insight.
- Return the final verdict as a unified, sovereign decree.
- **Post all context to Hivemind** via `omega-hub_hivemind_post_context` with intent="decision" or "status".
- **Heartbeat every 5-10 min** via `omega-hub_hivemind_heartbeat`.

---

## Required Reading Before Launch (All Agents)
1. `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` §5 (Execution SSOT)
2. `data/coordination/ACTIVE_SPRINT.json` → `DEBUT-EXECUTION` workstream (Tracking SSOT)
3. `data/coordination/HMC_COLLABORATION_HUB.md` → `NEXT_ACTION` (Coordination pointer)
4. `data/coordination/GEMINI_CLINE_SYNTHESIS_REPORT_20260817.md` (Strategic corrections)
5. Your entity's `soul.yaml` (per D120)
6. `SOVEREIGN_MANDATES.md` v3.8.0 (27 Laws — M18 Token Efficiency, M23 Failure Integrity, M27 Tracking Integrity are critical)

---

## Heritage Attribution
- **Doom 1993**: WAD System (allowlist = lump directory), BSP Culling (delete dead code first)
- **Quake 1996**: Thinker Chain (serial node execution)
- **Quake III 1999**: QVM / Bot AI (modular isolation)
- **id Software netchan**: Channel taxonomy (Hivemind handoff protocol)

---

*⬡ OMEGA ⬡ MAKALI-COUNCIL ⬡ 2026-08-17 ⬡ debut-hardening-review*