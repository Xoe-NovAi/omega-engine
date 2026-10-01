<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# N10 + N8 Genesis Charters — Gap Sweep (persisted pre-compaction)
**Source**: kali session 2026-08-22 · **Status**: DESIGNED, not yet launched · **Dispatch via**: Lilith (Runtime Oversoul, task:allow) · **Coordination**: Roc already running local discovery via researcher chain — reconcile, don't duplicate

## Launch mechanics
- Lilith fires BOTH genesis launches in ONE function_calls block (task() is blocking; parallelism only within one block)
- Agent type: existing `general` or `researcher` — NO new agent files (M10)
- Inline-context rule (SUBAGENT_DISPATCH_PROTOCOL §0): embed charters verbatim in prompts

## Onboarding sequence (embed in both)
1. Read OMEGA_CODEX.md first → SESSION_ANCHOR.md → ACTIVE_SPRINT.json
2. Hivemind post_context intent=handoff + heartbeat 5-10min
3. TASK_REGISTRY entry (M27 flow) + workspace lock (validation-sweep | observability-sweep)
4. Create session_gnosis file (M15); EOS lesson seeds (M11)
5. M23 hard-stop on tool failure

## N10 VALIDATION charter — "Reported vs Verified" diff
For EVERY done/resolved/completed/passing claim in: ACTIVE_SPRINT gates+blockers · GAP_REGISTRY.json (89 gaps) · Makefile verification targets · docs/specs/PROJECT_INDEX.md → verify against disk/code (grep/read/run). Known false-resolves seeding the sweep: BLOCKER-B bare-excepts live at oracle_cli.py; Fix 5 marked ready-but-done. Acceptance: every claim classified VERIFIED / STALE / FALSE-RESOLVED / UNVERIFIABLE with file:line evidence.

## N8 OBSERVABILITY charter — "Quiet-Failure" scan
Interrogate each subsystem: "What would this look like if it failed silently?" Surfaces: provider fabric health-signal gaps · streaming/degradation telemetry (sensor caught SLOW_DRIBBLE ×2; synchronized cross-instance stalls = shared bottleneck) · queue paths without terminal-state proof · soul/memory writes without read-back verification · gates that pass while content fails. Acceptance: ranked silent-failure classes with failure mode + detection gap + cheapest sensor fix.

## Constraints (both)
READ-ONLY sweep — no commits, no tracked-file edits. Write ONLY to data/coordination/GAP_SWEEP_20260822/N10_GAP_DELTA.md | N8_GAP_DELTA.md. Diff-before-dig vs GAP_REGISTRY + UNKNOWN_UNKNOWNS_AUDIT_20260721 + RESEARCH_PLAN_PHASE1_4. Single-level nesting. Grounding-Cline lens: "Does Cline need to know this? Is it written down?"

## Completion path
Each session: delta report → Hivemind handoff to lilith w/ session_id → Lilith reconciles declared-vs-fired → consolidates LILITH_GAP_SWEEP_OVERSIGHT_20260822.md → packet to kali. Sessions persist as pageable presences (D-586).
