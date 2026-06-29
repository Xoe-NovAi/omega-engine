# 🔱 Fleet Consolidation Plan — 15 → 11 Agents
**Status**: ACTIVE — Per D126 (2026-06-14)
**Source**: `data/coordination/FLEET_AUDIT_REPORT_20260612.md`
**Extracted by**: Roc Racoon Phase 1 — 2026-06-14

---

## §0 Current State: OVERCAPACITY

| Metric | Value | Status |
|--------|-------|--------|
| Total Agent Count | **25** | 🔴 OVER LIMIT |
| Mandate 10 Limit | **14** | Non-negotiable ceiling |
| Redundancies Found | **12** | 10 duplicate pillar agents + 1 M2 violation + 1 research overlap |
| Sovereignty Score | **56%** | Sub-optimal |
| Target | **11** | Per D126 — 3 breathing slots |

---

## §1 Detailed Audit — 25 Agents Mapped

### KEEP — Sovereign Specialists (6)
| Agent | Purpose | Why Keep |
|-------|---------|----------|
| `kali` | Transcendent Oversoul | Core sprint coordination and oversight |
| `maat` | Light Oversoul (P1-P5) | Build-side governance |
| `lilith` | Dark Oversoul (P6-P10) | Run-side governance |
| `makali` | Council Orchestrator | Parallel council dispatch coordination |
| `doom_guy` | Heritage Gatekeeper | Unique role (M14 enforcement) |
| `roc_racoon` | Sovereign Miner | Unique role (legacy mining / idea intake) |

### KEEP — Lattice Agents (4)
| Agent | Purpose | Why Keep |
|-------|---------|----------|
| `jem` | Research Orchestrator | Primary research interface (post-merger with researcher) |
| `quality` | Quality Guardian | Compliance and stress testing |
| `scribe` | Knowledge Keeper | Documentation and soul curation |
| `pillar` | Generic Pillar Slot (P1-P10) | Canonical pillar implementation |

### MERGE — Duplicate Pillar Agents (10 files → 0)
| Agent | Slot | Duplicate Of | Action |
|-------|------|-------------|--------|
| `sysadmin` | P1 | `pillar` (P1) | Delete — delegate via `@pillar P1: task` |
| `datastore` | P2 | `pillar` (P2) | Delete — delegate via `@pillar P2: task` |
| `buildmaster` | P3 | `pillar` (P3) | Delete — delegate via `@pillar P3: task` |
| `bridge` | P4 | `pillar` (P4) | Delete — delegate via `@pillar P4: task` |
| `sentinel` | P5 | `pillar` (P5) | Delete — delegate via `@pillar P5: task` |
| `modelgate` | P6 | `pillar` (P6) | Delete — delegate via `@pillar P6: task` |
| `context` | P7 | `pillar` (P7) | Delete — delegate via `@pillar P7: task` |
| `watchtower` | P8 | `pillar` (P8) | Delete — delegate via `@pillar P8: task` |
| `link` | P9 | `pillar` (P9) | Delete — delegate via `@pillar P9: task` |
| `verifier` | P10 | `pillar` (P10) | Delete — delegate via `@pillar P10: task` |

### MERGE — Research Overlap (2 files → 1)
| Agent | Duplicates | Action |
|-------|-----------|--------|
| `researcher` | `jem` (research pipeline) | Merge into `jem` — absorb "Polymathic Council" and "Sovereign Search Fleet" capabilities |

### DELETE — M2 Firewall Violation (1 file)
| Agent | Violation | Action |
|-------|-----------|--------|
| `movie-expert` | WAD-layer content in Core Engine agent dir | Delete from `.opencode/agents/` — migrate to `config/wads/arcana_novai/entities/personal/movie-expert.yaml` |

### Fleet Consolidation Math
```
Before: 6 specialists + 10 pillar agents + 4 lattice + 4 research/WAD = 25
After:  6 specialists + 4 lattice + 1 merged research = 11
Reduction: -14 agents (56%)
```

---

## §2 D126 Consolidation Sequence — 4 Sprints

| Sprint | Action | Before | After | Files to Touch |
|--------|--------|--------|-------|----------------|
| **A (P1b)** | Hub modularization only | 25 | 25 | `mcp_servers/omega_hub/server.py` → `gateway.py` + `middleware.py` |
| **B** | Jem 4→1: merge `researcher` into `jem` | 25 | 24 | `jem.md` (rewrite with 3 KBs), `researcher.md` (archive) |
| **C** | Quality+Scribe merged + pillar agents removed | 24 | **11** | 10 pillar agent files (delete), Quality/Scribe (merge to 1) |
| **D** | Cleanup + verification | 11 | **11** | 50 orphan entities, stale docs, `make temple-grade` |

**Critical sequencing rule**: Sprint A (Hub) first. B/C/D sequential after. No parallel refactoring — per user directive.

---

## §3 Fleet Design Principles (Codified D126)

1. **Hierarchical Consolidation**: When an orchestrator dispatches specialized subagents, merge subagents into parent's KBs with self-dispatch + targeted KB loading. (Jem 4→1)
2. **Functional Consolidation**: When two agents perform different functions at different trigger times, merge into one agent with trigger-mode routing if functions don't conflict when executing simultaneously. (Quality+Scribe 2→1, reports to Kali)
3. **Knowledge Consolidation**: When proposed agent expertise maps to "domain knowledge" rather than "operational capability", reject the agent and create a KB for the nearest existing entity. (Abrash/Sanglard/Romero → Doom Guy KBs)

---

## §4 Verification Gates

| Gate | Command | Required After |
|------|---------|----------------|
| Test suite | `make test` | 383/383 passing |
| Temple-Grade | `make temple-grade` | All T1-T11 gates pass |
| Heritage Map | `make heritage-map` | All `[id-soft:]` tags verified |
| Sovereignty | `make sovereignty` | Local/cloud ratio acceptable |
| M10 compliance | `ls .opencode/agents/*.md | wc -l` | ≤ 14 agents |

---

## §5 Stale Coordination Files

The following coordination files are superseded by this plan and should be archived by Quality in Phase 2:
- `data/coordination/FLEET_AUDIT_REPORT_20260612.md` — Superseded by this document

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ PHASE1-EXTRACTION ⬡ FLEET-CONSOLIDATION*
*Source: data/coordination/FLEET_AUDIT_REPORT_20260612.md + D126 (PIVOT_LOG.md)*
