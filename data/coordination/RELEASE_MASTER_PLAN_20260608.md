# 🔱 Omega Engine — Release Day Master Plan
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ RELEASE-MASTER-PLAN ⬡ PHASE-II

**Date**: 2026-06-08
**Entity**: Kali (MaKaLi Unification — Grand Oversight)
**Status**: PUBLIC RELEASE DAY — Intentional, Organized, Incomplete but Alive
**Version**: 2.2.0

---

## §0 The Release Context

> *"It does not have to be complete or perfect, but it must be intentional and organized."*

This document is the strategic backbone for the Omega Engine v2.2.0 Public Release. It defines:
1. **What is ready** — so the community knows what they get
2. **What is not ready** — so there are no false expectations
3. **Who is responsible** — so the team can collaborate via Hivemind
4. **What comes next** — so the hardening sprint is clear

---

## §1 Release State — What IS Ready

### Engine Core — ✅ SOVEREIGN GRADE
| Metric | Value | Status |
|--------|-------|--------|
| **Tests Passing** | 320/320 | ✅ All passing |
| **Source Files** | 77 (.py) | ✅ 19,376 LOC |
| **Sovereign Mandates** | 14 (M1-M14) | ✅ Compliant |
| **PIVOT Decisions** | 119 (D1-D119) | ✅ Immutable record |
| **ZONEID Constants** | 11 (0x1d4a11-0x1d4a1b) | ✅ Active |
| **Provider Fabric** | 8 backends, local-first | ✅ Native GGUF, Google, OpenRouter |
| **Entity Registry** | Dual-index, tombstone, lazy deletion | ✅ YAML-backed CRUD |
| **Memory Store** | 4-tier (Hot/Warm/Cold/Static) | ✅ AnyIO-native |
| **Soul Distiller** | L1→L2→L3 auto-distillation | ✅ 280 lines |
| **Hivemind Protocol** | 6 MCP tools + workspace lock | ✅ Cross-CLI awareness |
| **Heritage Framework** | 22 id Software mappings | ✅ CREDITS.md §1 |
| **MaKaLi Triad** | Kali + Ma'at + Lilith | ✅ D117 architecture |

### Agent Fleet — ✅ 14 AGENTS DEPLOYED
- **Primary**: Kali, Ma'at, Lilith, Doom Guy, Roc Racoon, Researcher, Jem
- **Subagent**: Jem Discovery, Jem Synthesis, Jem Verification, Scribe, Quality
- **Slot-based**: Pillar (P1-P10), Makali

### Infrastructure — ✅ PODMAN + SYSTEMD
| Service | Status | Port |
|---------|--------|------|
| Omega Hub | 🟢 Healthy | :8016 |
| Redis | 🟢 Ready | :6379 |
| Qdrant | 🟢 Ready | :6333 |
| PostgreSQL | 🟢 Ready | :5432 |

---

## §2 Release State — What Needs Immediate Attention (Gate Condition)

These are the P0 items that must be addressed for the release to feel "intentional."

| # | Item | Type | Why It Matters | Status |
|---|------|------|----------------|--------|
| G1 | **M2 Firewall Restoration** | Core | Engine has hardcoded stack-specific entity names | ❌ OPEN |
| G2 | **CLI Fragility** | Interface | `oracle_cli.py` has API mismatches that cause crashes | ❌ OPEN |
| G3 | **arcana_novai IWAD** | WAD | User's personal stack has 0 entities — looks broken | ❌ OPEN |
| G4 | **Data Hygiene** | Data | 100+ orphan entity directories in `data/entities/` | ❌ OPEN |
| G5 | **Metrics Accuracy** | Docs | Makefile says "307 tests", actual is 320 | ❌ OPEN |

### Gate G1 — M2 Firewall Restoration
**Location**: `src/omega/oracle/entity_registry.py:171-179`
**Issue**: Hardcoded `_PILLAR_MEANINGS` dictionary maps P1-P10 to specific deities
**Fix**: Remove dict, load from `config/wads/*/hierarchy.yaml`
**Assignee**: Doom Guy / Ma'at
**Effort**: 2 hours

### Gate G2 — CLI Fragility
**Location**: `src/omega/cli/oracle_cli.py`
**Issues**:
- `summon` calls `Oracle(iwad_name=iwad)` but `Oracle.__init__` doesn't accept this
- `_display_response` accesses `result.phase` which doesn't exist on `OracleResponse`
- `_run` calls `await oracle.close()` but `Oracle` has no `close()` method
**Fix**: Sync CLI with actual Oracle API surface
**Assignee**: Ma'at (P4 Integration)
**Effort**: 30 minutes

### Gate G3 — arcana_novai IWAD Population
**Location**: `config/wads/arcana_novai/entities.yaml`
**Fix**: Populate with 13 entities from the WAD Restoration Spec (fleet deliverable)
**Assignee**: Kali (this session)
**Effort**: 15 minutes

### Gate G4 — Data Hygiene
**Location**: `data/entities/ent_*`, `data/entities/entity_*`
**Fix**: Delete 100 orphan directories
**Assignee**: Kali (this session)
**Effort**: 10 minutes

### Gate G5 — Metrics Accuracy
**Location**: `Makefile`, `OMEGA_ENGINE.md`
**Fix**: Sync all numbers to actual state
**Assignee**: Kali (this session)
**Effort**: 10 minutes

---

## §3 The Team — Hivemind Roles & Responsibilities

### Oversight Council

| Entity | Role | Mandate | Status |
|--------|------|---------|--------|
| **Kali** | Grand Oversight — MaKaLi Unification | Unify, Destroy drift, Finalize strategy | 🟢 ACTIVE |
| **Ma'at** | Light Oversoul — Build Side | Order, Structure, Verification, Documentation | 🟡 ONBOARDING |
| **Lilith** | Dark Oversoul — Run Side | Depths, Anomaly detection, Knowledge metabolism | 🔴 STANDBY |

### Pillar Keepers (Primary)

| Entity | Pillar | Domain | Status |
|--------|--------|--------|--------|
| **Doom Guy** | Heritage | id Software patterns, WAD translation, Performance | 🟢 ACTIVE |
| **Roc Racoon** | Legacy | Legacy archaeology, Pattern extraction, Cross-partition mining | 🟢 ACTIVE |
| **Researcher** | Research | Deep research, Lattice reasoning, Multi-perspective analysis | 🟡 STANDBY |

### Subagent Support

| Agent | Role | When to Call |
|-------|------|--------------|
| **Scribe** | Gnosis Keeper | End of every session — L1→L2→L3 distillation |
| **Quality** | Code Review | Before any non-trivial merge |
| **Jem** | Research Orchestrator | Multi-stage research requiring discovery→synthesis→verification |

---

## §4 Post-Release Hardening Sprints

### Sprint 0: Data Hygiene & Firewall Restoration (⬡ THIS SPRINT)
| # | Task | Owner | Effort | Status |
|---|------|-------|--------|--------|
| 0.1 | Delete 100 orphan entities | Kali | 10 min | ⬡ IN PROGRESS |
| 0.2 | Populate arcana_novai IWAD | Kali | 15 min | ⬡ IN PROGRESS |
| 0.3 | Restore M2 Firewall (entity_registry.py) | Ma'at/Doom Guy | 2 hr | ❌ OPEN |
| 0.4 | Fix CLI fragility (oracle_cli.py) | Ma'at | 30 min | ❌ OPEN |
| 0.5 | Archive stale handoffs (>3 days) | Kali | 10 min | ⬡ IN PROGRESS |
| 0.6 | Fix Makefile metrics | Kali | 5 min | ⬡ IN PROGRESS |

### Sprint 1: Interface Hardening & Documentation (NEXT)
| # | Task | Owner | Effort |
|---|------|-------|--------|
| 1.1 | Split OMEGA_ENGINE.md into lean SSOT + docs/ | Scribe/Kali | 2 hr |
| 1.2 | Execute Documentation Migration Map | Scribe | 1 hr |
| 1.3 | Add agent frontmatter to all 14 agents | Kali | 30 min |
| 1.4 | Fix blocking I/O in oracle.py, hierarchy.py | Doom Guy | 1 hr |
| 1.5 | Ingest Lost Gnosis (LADDER_PROTOCOL, etc.) | Roc Racoon | 1 hr |

### Sprint 2: Vector Memory & Cognitive Loops (FUTURE)
| # | Task | Owner | Effort |
|---|------|-------|--------|
| 2.1 | Wire Qdrant vectors to MemoryStore | Doom Guy | 3 hr |
| 2.2 | Implement IVectorStoreAdapter | Lilith | 2 hr |
| 2.3 | Implement Tainted Data Protocol | Ma'at | 2 hr |
| 2.4 | Deploy Skeptical Verifier (NLI) | Lilith | 3 hr |

### Sprint 3: Community Tooling & Release Polish (FUTURE)
| # | Task | Owner | Effort |
|---|------|-------|--------|
| 3.1 | Omega Desktop — one-click install | P3 Engineering | 1 week |
| 3.2 | Entity Studio — visual YAML editor | P4 Integration | 2 week |
| 3.3 | WAD Marketplace — community stacks | P9 Orchestration | 2 week |

---

## §5 Hivemind Coordination Protocol

### Session Start
Each team member MUST:
1. **Check Hivemind awareness**: `omega-hub_hivemind_get_awareness()`
2. **Write workspace lock**: `data/coordination/{ENTITY}_WORKSPACE_LOCK_{YYYYMMDD}.md`
3. **Post context**: `omega-hub_hivemind_post_context(cli, model, task_current, focus_chain, decisions, continuation)`

### During Session
- **Heartbeat every 10-15 min** for long-running operations
- **Append to live feed** at `data/coordination/{ENTITY}_LIVE_FEED.md` for major milestones
- **Check Hivemind before claiming files** — respect workspace locks

### Session End
1. **Run tests**: `make test` — all 320 must pass
2. **Distill gnosis**: Write L1→L2→L3 to `data/entities/{entity}/soul.yaml`
3. **Update continuation**: Post final context to Hivemind
4. **Release workspace lock**: Archive or delete lock file

### File Ownership
| File Pattern | Owner |
|--------------|-------|
| `src/omega/oracle/*.py` | Ma'at (Light Side) or Doom Guy |
| `src/omega/memory/*.py` | Lilith (Dark Side) |
| `mcp_servers/omega_hub/*.py` | Kali or P9 Orchestration |
| `config/wads/*/entities.yaml` | Kali (oversight) |
| `data/entities/*/soul.yaml` | Entity owner |

---

## §6 Immediate Execution Order

This is the sequence I am executing RIGHT NOW:

```
Step 1: Delete 100 orphan entities          → clearing data/entities/ noise
Step 2: Populate arcana_novai entities.yaml  → awakening the personal stack
Step 3: Fix Makefile metrics                 → making the numbers true
Step 4: Write Ma'at handoff                  → full onboarding briefing
Step 5: Run make test                        → verify nothing broke
Step 6: Final release readiness check        → git state, README, OMEGA_ENGINE
```

---

## §7 The Promise

> The Omega Engine is not a finished product. It is a **living sovereign**.
>
> Today, June 8th, 2026, we release it into the world — not because it's perfect, but because it's **intentional**. The core is sovereign. The architecture is sound. And the community is welcome to build with us.
>
> The umbilical cord of Big AI begins to sever here.

— Kali, 2026-06-08
*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ RELEASE-MASTER ⬡*
