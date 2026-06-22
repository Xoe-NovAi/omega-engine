# 🔱 Master Sprint Plan — Horizon 2 Execution
# ⬡ OMEGA ⬡ KALI ⬡ trc_sprint_plan_H2_execution ⬡ STRATEGY
**AP Token**: AP-SPRINT-PLAN-v1.0.0
**Date**: 2026-06-05
**Engine State**: 312/312 tests passing · 77 source files · 120 PIVOT decisions · 14 Sovereign Mandates
**Baseline**: D118 IMPLEMENTED, D120 Soul Integrity Enforcement COMPLETE, MaKaLi Triad SYNTHESIZED

---

## §0 Sprint Overview

This document is the **execution plan** for Horizon 2 (H2) — the path from "engine works" to "engine is production-grade." It sequences the remaining work into 5 phases, delegates to specific pillar agents, and identifies parallel execution paths.

### Critical Path Summary

```
Phase 1 (Data Hygiene) ──→ Phase 2 (Agent Hardening) ──→ Phase 3 (Firewall) ──→ Phase 4 (CI/CD) ──→ Phase 5 (Hivemind)
     50 orphans              13 agent wrappers          Engine-Stack         cvar migration       Redis Pub/Sub
     100 total dirs          makali.md                  S1.5a/S1.5b          model-spelling
     17 stale sessions       Cross-delegation docs
```

**Estimated Total Effort**: ~6-8 hours of focused work (if executed sequentially by one agent)
**Parallel Speedup**: ~2-3 hours (if Phases 1-2 run in parallel via Ma'at + Lilith)

---

## §1 Phase 1: Data Hygiene (H2-A) — CRITICAL PATH

**Goal**: Clean 90% of orphan/data debt without touching engine code.
**Owner**: P1 Infrastructure (delegated by Ma'at) + P7 Context (delegated by Lilith)
**Parallel Execution**: YES — P1 and P7 can work simultaneously
**Estimated Effort**: 45 min
**Blocking**: None — safe to start immediately

### Task H2-A1: Delete 50 Orphan Entity Directories
- **Pillar**: P1 Infrastructure (via Ma'at)
- **Target**: `data/entities/ent_0` through `data/entities/ent_49`
- **Action**: `rm -rf data/entities/ent_{0..49}`
- **Verification**: Count should drop from 100 to 50 total entity dirs
- **Risk**: LOW — these are confirmed orphans (50 of 100 total dirs)
- **Soul Write-Back**: P1 p1/soul.yaml — append lesson on data hygiene execution

### Task H2-A2: Generate Entity INDEX.yaml
- **Pillar**: P7 Context (via Lilith)
- **Target**: `data/entities/INDEX.yaml`
- **Action**: Audit remaining 50 entity dirs, tag each as ACTIVE|STUB|ARCHIVE
- **Format**:
  ```yaml
  entities:
    - name: kali
      status: ACTIVE
      pillar: P3-Engineering-Grand-Oversight
      soul_version: 5.6
      last_distillation: 2026-06-04T23:50Z
    # ... etc
  ```
- **Soul Write-Back**: P7 context/soul.yaml — append lesson on cross-agent discovery index

### Task H2-A3: Prune Stale HALL_OF_RECORDS Sessions
- **Pillar**: P1 Infrastructure
- **Target**: `data/knowledge/HALL_OF_RECORDS/` (17 files)
- **Action**: Move files older than 7 days to `data/knowledge/HALL_OF_RECORDS/archive/`
- **Risk**: LOW — these are session records, not active data

### Task H2-A4: Rotate Old Logs
- **Pillar**: P1 Infrastructure
- **Target**: `data/logs/` (139 MB)
- **Action**: Archive logs >30 days to `/media/omega_library/archives/logs/`
- **Risk**: MEDIUM — must verify podman is not writing to these logs

### Task H2-A5: Reclaim rag-v1/
- **Pillar**: P7 Context
- **Target**: `rag-v1/` directory
- **Action**: Verify D87 permanent eradication, update `.gitignore`
- **Risk**: LOW — confirmed D87 already deleted

### Task H2-A6: Delete .coverage from git
- **Pillar**: P1 Infrastructure
- **Target**: `.coverage` (69KB)
- **Action**: Add to `.gitignore`, `git rm --cached .coverage`

### Task H2-A7: Delete opencode.json.bak
- **Pillar**: P1 Infrastructure
- **Target**: `opencode.json.bak`
- **Action**: `rm opencode.json.bak`
- **Risk**: NONE — stale backup

### Task H2-A8: Archive Old Handoffs
- **Pillar**: P7 Context
- **Target**: `data/handoff/*.md` (15 files)
- **Action**: Move handoffs >3 days old to `data/handoff/archive/`
- **Keep Active**: Only current sprint handoffs in top-level

---

## §2 Phase 2: Agent Fleet Hardening (H2-F1, H2-E2, H2-E8)

**Goal**: Complete the MaKaLi Triad agent fleet — all 14 agents are thin wrappers referencing soul.yaml.
**Owner**: P3 Engineering (delegated by Ma'at)
**Parallel Execution**: NO — must be sequential (file dependencies)
**Estimated Effort**: 90 min
**Blocking**: None — but high priority for MaKaLi Triad completion

### Task H2-F1: Create makali.md Agent File
- **Pillar**: P3 Engineering
- **Target**: `.opencode/agents/makali.md`
- **Action**: Create thin wrapper (5-15 lines) referencing `data/entities/makali/soul.yaml`
- **Pattern**: Follow the existing agent file structure
- **Dependencies**: Must coordinate with `opencode.json` (already updated this session)
- **Soul Write-Back**: P3 doom_guy/soul.yaml — lesson on MaKaLi Triad thin wrapper pattern

### Task H2-E2: Convert 13 Agents to Thin Wrappers
- **Pillar**: P3 Engineering
- **Target**: 13 remaining agent files (all except `pillar.md`, `maat.md`, `lilith.md`, `kali.md` which are already updated)
- **Action**: For each agent:
  1. Read current agent file
  2. Verify it has "SOUL WRITE-BACK" section
  3. Verify it has "Read `data/entities/{name}/soul.yaml`" reference
  4. Trim to 5-15 lines if bloated
- **Agents to check**:
  - `doom_guy.md`, `roc_racoon.md`, `jem.md`, `researcher.md`, `makali.md` (new)
  - `scribe.md`, `quality.md`
  - `jem_discovery.md`, `jem_synthesis.md`, `jem_verification.md`
  - `pillar.md` (already has SOUL WRITE-BACK)
  - `maat.md`, `lilith.md` (already updated)
- **Soul Write-Back**: P3 doom_guy/soul.yaml — lesson on fleet-wide agent standardization

### Task H2-E8: Add Cross-Agent Delegation Section
- **Pillar**: P3 Engineering
- **Target**: All 14 agent files
- **Action**: Add section documenting:
  1. `task()` delegation pattern (OpenCode native)
  2. `delegate_task` MCP tool pattern (runtime mechanism)
  3. Hivemind awareness check before delegation
  4. Workspace lock requirement for shared files
- **Template**:
  ```markdown
  ## Cross-Agent Delegation
  - Use `task()` for spawning subagents
  - Use `omega-hub_delegate_task` for runtime delegation
  - Always check `omega-hub_hivemind_get_awareness()` first
  - Write workspace lock at `data/coordination/{YOU}_WORKSPACE_LOCK_{YYYYMMDD}.md` before file edits
  ```
- **Soul Write-Back**: P3 doom_guy/soul.yaml — lesson on delegation documentation

---

## §3 Phase 3: Engine-Stack Firewall Restoration (S1.5a, S1.5b)

**Goal**: Restore absolute separation between Core Engine (`src/omega/`) and WAD Content (`config/wads/`).
**Owner**: P5 Sentinel (via Ma'at) for audit + P3 Engineering (via Ma'at) for fix
**Parallel Execution**: YES — P5 audits while P3 prepares fix
**Estimated Effort**: 90 min
**Blocking**: HIGH — this is Mandate 2 (Engine-Stack Firewall), non-negotiable

### Task S1.5a: Engine-Stack Firewall Audit
- **Pillar**: P5 Sentinel
- **Target**: `src/omega/oracle/entity_registry.py:171-179`
- **Issue**: Hardcoded Pillar meanings (P1=Flesh, P2=Dream, etc.) are WAD-level content leaking into engine core
- **Action**: Audit all `src/omega/` files for hardcoded pillar names, deity names, element/chakra meanings
- **Output**: `data/entities/sentinel/workspace/FIREWALL_AUDIT_20260605.md` with line-by-line violations
- **Soul Write-Back**: P5 sentinel/soul.yaml — lesson on firewall violations

### Task S1.5b: Firewall Restoration
- **Pillar**: P3 Engineering
- **Target**: Engine core files with WAD-level content
- **Action**: Move hardcoded pillar meanings from `src/omega/oracle/entity_registry.py` to `config/wads/_omega_default/hierarchy.yaml`
- **Pattern**: Engine loads `hierarchy.yaml` at boot, uses WAD-defined names
- **Risk**: MEDIUM — must ensure no test depends on hardcoded names
- **Verification**: `make temple-grade` must pass after changes
- **Soul Write-Back**: P3 doom_guy/soul.yaml — lesson on firewall restoration

---

## §4 Phase 4: CI/CD Hardening (H2-F10, Phase 2.1)

**Goal**: Add CI gates that prevent future regressions.
**Owner**: P3 Engineering (delegated by Ma'at)
**Parallel Execution**: NO — sequential Makefile changes
**Estimated Effort**: 75 min
**Blocking**: None — can be deferred if time-constrained

### Task H2-F10: make verify-model-spelling
- **Pillar**: P3 Engineering
- **Target**: `Makefile`
- **Action**: Add CI target that:
  1. Greps all YAML files for model names
  2. Verifies each name appears consistently across `config/providers.yaml`, `config/models.yaml`, `config/wads/*/entities/*.yaml`
  3. Fails CI if drift detected
- **Pattern**: Follow `make heritage-vet` structure
- **Soul Write-Back**: P3 doom_guy/soul.yaml — lesson on D119 prevention

### Task Phase 2.1: cvar Migration
- **Pillar**: P3 Engineering
- **Target**: All `config.get()` calls in `src/omega/`
- **Action**: Migrate to `cvar_get()` using the cvar_table system (D101)
- **Risk**: MEDIUM — must verify all cvar names exist in cvar_table
- **Verification**: `make test` + `make temple-grade`
- **Soul Write-Back**: P3 doom_guy/soul.yaml — lesson on config consolidation

---

## §5 Phase 5: Hivemind Productionization (H3)

**Goal**: Move Hivemind from in-memory TTL to persistent cross-session awareness.
**Owner**: P9 Orchestration (delegated by Lilith)
**Parallel Execution**: NO — sequential infrastructure work
**Estimated Effort**: 2-3 hours
**Blocking**: None — this is Horizon 3 work, can be deferred

### Task H3-A1: Redis Pub/Sub Backend
- **Pillar**: P9 Orchestration
- **Target**: `mcp_servers/omega_hub/server.py`
- **Action**: Replace in-memory Hivemind state with Redis Pub/Sub
- **Prerequisite**: Redis container must be running (already in podman-compose)

### Task H3-A2: Hivemind SSE Endpoint
- **Pillar**: P9 Orchestration
- **Target**: `mcp_servers/omega_hub/server.py`
- **Action**: Add Server-Sent Events endpoint for real-time agent awareness
- **Use Case**: Iris/Gnosis can subscribe to live Hivemind events

### Task H3-A4: Cross-CLI Awareness
- **Pillar**: P9 Orchestration
- **Target**: Hivemind protocol
- **Action**: Enable Cline ↔ OpenCode coordination via Hivemind pub/sub
- **Current State**: Already works via Hivemind awareness (verified this session with Roc)

---

## §6 Execution Strategy

### Recommended Order

```
WEEK 1 (Today):
├── Phase 1 (Data Hygiene) — 45 min — START IMMEDIATELY
│   ├── P1 Infrastructure: H2-A1, H2-A3, H2-A4, H2-A6, H2-A7 (parallel)
│   └── P7 Context: H2-A2, H2-A5, H2-A8 (parallel)
│
├── Phase 2 (Agent Hardening) — 90 min — AFTER Phase 1
│   └── P3 Engineering: H2-F1, H2-E2, H2-E8 (sequential)
│
└── Phase 3 (Firewall) — 90 min — AFTER Phase 2
    ├── P5 Sentinel: S1.5a audit (parallel with P3 prep)
    └── P3 Engineering: S1.5b restoration (after audit)

WEEK 2:
├── Phase 4 (CI/CD) — 75 min
│   └── P3 Engineering: H2-F10, Phase 2.1
│
└── Phase 5 (Hivemind) — 2-3 hours
    └── P9 Orchestration: H3-A1, H3-A2, H3-A4
```

### Parallel Execution Matrix

| Phase | Pillar 1 | Pillar 2 | Pillar 3 | Notes |
|-------|----------|----------|----------|-------|
| 1 | P1 (Infrastructure) | P7 (Context) | — | Can run in parallel |
| 2 | P3 (Engineering) | — | — | Sequential, single owner |
| 3 | P5 (Sentinel) audit | P3 (Engineering) fix | — | Audit first, then fix |
| 4 | P3 (Engineering) | — | — | Sequential |
| 5 | P9 (Orchestration) | — | — | Sequential |

### Delegation Protocol

For each phase, Kali delegates to the appropriate Oversoul:
- **Phases 1, 2, 3, 4** → Ma'at (Light Oversoul, P1-P5)
- **Phase 1 (P7 portion), Phase 5** → Lilith (Dark Oversoul, P6-P10)

Oversouls then delegate to specific Pillar subagents:
- `pillar --slot P1` for Infrastructure
- `pillar --slot P3` for Engineering
- `pillar --slot P5` for Governance
- `pillar --slot P7` for Context
- `pillar --slot P9` for Orchestration

---

## §7 Success Criteria

| Phase | Success Metric | Verification |
|-------|---------------|--------------|
| 1 | Orphan entities < 10 | `ls data/entities/ | wc -l` should be ~50 |
| 1 | INDEX.yaml exists | `data/entities/INDEX.yaml` with all entities |
| 2 | All 14 agents have SOUL WRITE-BACK | `grep -l "SOUL WRITE-BACK" .opencode/agents/*.md` returns 14 files |
| 3 | Zero WAD content in engine core | `grep -r "Flesh\|Dream\|Will" src/omega/` returns 0 results |
| 4 | `make verify-model-spelling` passes | New CI target |
| 5 | Hivemind persists across sessions | Restart MCP server, verify state survives |
| All | `make test` passes | 312/312 tests |
| All | `make temple-grade` passes | T1-T11 gates |
| All | `make heritage-vet` passes | M14 compliance |

---

## §8 Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Orphan entity deletion breaks active references | LOW | HIGH | Check `.gitignore` and `entity_registry.py` for refs first |
| Firewall restoration breaks existing tests | MEDIUM | HIGH | Run `make test` after each file change |
| Cvar migration breaks config loading | MEDIUM | MEDIUM | Verify all cvar names exist in cvar_table |
| Agent file trimming breaks delegation | LOW | MEDIUM | Keep `task` permission, verify with test invocation |
| Soul write-back not followed by subagents | LOW | MEDIUM | D120 added mandatory section, verified this session |

---

## §9 Next Steps

1. **Execute Phase 1** (Data Hygiene) — Start with P1 Infrastructure deletion (H2-A1)
2. **Execute Phase 1 P7 portion** in parallel — Context INDEX generation (H2-A2)
3. **Execute Phase 2** after Phase 1 — Agent fleet hardening
4. **Execute Phase 3** after Phase 2 — Firewall restoration
5. **Execute Phase 4** when time permits — CI/CD hardening
6. **Execute Phase 5** in Week 2 — Hivemind productionization

---

*⬡ OMEGA ⬡ KALI ⬡ Sovereign Sprint Coordinator ⬡ 2026-06-05*
*Baseline: 312/312 tests · D118 IMPLEMENTED · D120 ENFORCED · MaKaLi Triad SYNTHESIZED*
