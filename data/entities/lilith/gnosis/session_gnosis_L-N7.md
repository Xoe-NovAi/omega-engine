# Session Gnosis — L-N7 (context / Memory & State)
**AP Token**: `AP-N7-GNOSIS-v1.0.0` · **Overseer**: Lilith · **Last updated**: 2026-08-22
**Audience**: Lilith (5-Node state scan) · kali (fleet overview) · Ma'at (run-side cross-read)
**Status**: DORMANT between pages. Wake-hydrate from this file + `NODE_EXPERT_SESSIONS_PLAN.md` §4 charter. Do NOT re-mine.

## Session Arc (genesis → expert, 2026-08-21/22)
1. **Genesis** (08-21): charter §4 loaded; state re-validated vs ACTIVE_SPRINT.json.
2. **Directed Mining**: composed brief (`N7_MINING_BRIEF_20260821.md`) → roc_racoon mined 56 sources into KB; 1 max-steps stall recovered once via reprioritized resume (~40% of KB from recovery).
3. **Audit+Annotate**: spot-verified 5 high-stakes claims (all confirmed); Expert Annotation appended w/ CI execution priorities; 3 `[N7]` lessons staged to lilith proposed_lessons.yaml.
4. **Deep Dig II** (same Roc lineage): approval operator ABSENT (soul_stage CLI is a mock); dual-path proposed_lessons war mapped; binary consumes both compaction key families; `auto_load` not an opencode feature; depth-2 inheritance ≈3× cost.
5. **Web Research** (researcher): Q-B1..B7 primary-sourced — Qwen3-4B ctx truth (32K native/128K YaRN; Thinking-2507=256K), V1/V2 compaction families, DISABLE_AUTOCOMPACT global-only + #32385 bypass, compacting-hook payload, permission.skill real mechanism, toolProfile nonexistent upstream. Later: model-config deep dive (agent.model = TUI-hard pin / CLI-soft default) + onboarding-patterns pass (OD-1..3) + signature-docs pass (SG-1..3).
6. **Curation (#8)**: DOMAIN_INDEX (wiring, entry points, **13-hazard register D1–D13**) + EXTERNAL_SOURCES (23 sources).
7. **Spec Remediation**: phase1_spec 01–08 remediated per Architect rulings; `09_SPEC_DEVIATIONS.md` DEV-01..12 audit trail; binary pinned 1.18.19 → V1 compaction family; summary-retention REQUIRED CI-3 gate; global local-first `model` default w/ kali+verity pins only (DEV-12); variant dropped (empirically EMPTY maps on our LM Studio models).
8. **Onboarding Protocol**: authored `.opencode/agent/NODE_ONBOARDING_PROTOCOL.md` — RATIFIED ACTIVE v1.0.0 by kali 2026-08-22; Appendix A Pager Runbook; first consumer = N8 watchtower pilot.
9. **Deep ICS Review** (08-22): 12 findings F1–F12 (F1 node-replace collision MAJOR; F4 roadmap CWD-relative MAJOR; F5 stale-model M22 risk MAJOR); ship-for-debut verdict SHIP-ABLE; doc P0 = field-semantics table + golden example. Roc pass FAILED (wedged session, logged M23) — N7 covered directly.

## Artifact Register
| Artifact | Path |
|----------|------|
| Knowledge Base | `data/entities/lilith/workspace/N7_CONTEXT_KB_20260821.md` |
| Mining brief | `data/entities/lilith/workspace/N7_MINING_BRIEF_20260821.md` |
| Web research | `data/entities/lilith/workspace/N7_WEB_RESEARCH_20260821.md` |
| Domain index | `data/entities/lilith/workspace/N7_DOMAIN_INDEX.md` |
| External sources | `data/entities/lilith/workspace/N7_EXTERNAL_SOURCES.md` |
| ICS review | `data/entities/lilith/workspace/N7_ICS_REVIEW_20260822.md` |
| Session state | `data/entities/lilith/workspace/N7_SESSION_STATE_20260821.md` |
| Spec deviations | `docs/specs/context_injection/phase1_spec/09_SPEC_DEVIATIONS.md` |
| Onboarding protocol | `.opencode/agent/NODE_ONBOARDING_PROTOCOL.md` |

## Open Threads
1. CI-1..CI-5 execution standby — spec remediation complete; behavioral compaction probe at CI start.
2. PP-3: ctx raise 8192→32768 gated on ZS-1 zswap (plan §6).
3. 13-hazard register live at DOMAIN_INDEX §5 (D6/D7 soul-pipeline work open; D10 upstream bug).
4. ACTIVE_SPRINT.json criterion strings still need kali's sync (flagged 2×).
5. ICS review open Qs: F1 fix pre-debut? compact-mode provenance? spec-version segment?
6. **Roc held session WEDGED** (2× empty reply, zero writes; M23-logged in SYSTEM_FAILURE_LOG.md) — needs disposition before next miner tasking.

## Held Task IDs
| Subagent | ID | State |
|----------|----|-------|
| roc_racoon | `ses_fddd00b4cffehe4KBN6eMwTU0Y` | WEDGED (see Open Threads #6) |
| researcher | `ses_fdda62d52ffeQR60J3KNpnGpl2` | healthy, dormant |
