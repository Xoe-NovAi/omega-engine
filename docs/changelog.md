<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Omega Engine - Changelog

## 2026-07-25 - Process Reform and Sprint Prep Complete

### Process Audit - 10 Systemic Failures Corrected
- **Archived stale Game Plan docs**: GAME_PLAN_PART1-4B + GAME_PLAN_COMPLETE moved to docs/archive/strategy/2026-07-25/.
- **Corrected OMEGA_ENGINE.md**: 5 false claims fixed (W-1, V-1, C-3, MCP pin, phase label) with probe-backed truth.
- **Added research-vs-execution banners**: KNOWLEDGE_GAP_CLOSURE.md and FULL.md now explicitly state research closed != execution closed.
- **Superseded guard-and-distill sprint**: Status SUPERSEDED; agents pointed to docs/sprints/current/EXECUTION_PLAN_20260725.md.
- **Updated STRATEGY_INDEX to v6.0**: New doc hierarchy, archive entries, process rules in conflict resolution.
- **Created PROCESS_IMPROVEMENT_PLAN_20260725.md**: 240-line comprehensive plan with 10 process failures, DB/vector consolidation, reordered phases, 7 web-research domains.
- **Updated FLEET_TEAM_PLAYBOOK**: Quick reference card now includes process rules, RESEARCH/EXECUTION columns, probe instructions.
- **Banners on historical docs**: HARDENING_PLAN_COMPLETE.md, RESEARCH_EXECUTION_UPDATE.md marked as historical reference.

### Sprint Plan v1.2 - Ready for Execution
- **Execution Plan updated to v1.2**: Fresh probe data (9 DBs, 5+ breaker clones, age missing).
- **Added P-1..P-7 tickets**: Process Reform phase after Integrity Gate (B1-B5).
- **Reordered dev phases**: Integrity Gate > Process Reform > Phase D > Observability > Phase E > Phase F.
- **Web research completed**: 7 domains researched (pybreaker ADOPT, SOPS+Age ADOPT, prometheus_client ADOPT, sqlite-vec CONFIRMED, sentence-transformers CONSIDER, Pydantic v2 ADOPT, restic CONFIRMED).

### Key Probe Findings (2026-07-25)
- Omega Hub :8016 OK | Firecrawl :8015 OK
- W-1 SOCKS :8081-8083 FAIL - still not deployed
- Restic timer FAIL - not enabled
- age binary FAIL - missing on system
- C-0.5 hook FAIL - not registered in opencode.json
- prometheus_client 0.24.1 OK - installed but unused
- pybreaker FAIL - not installed
- Duplicate DBs FAIL - 2 omega_memory.db copies (118M + 22M)
- 9 SQLite databases total - target: 3

---

