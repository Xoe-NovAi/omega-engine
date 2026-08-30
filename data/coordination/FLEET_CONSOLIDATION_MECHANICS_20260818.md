<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Fleet Consolidation Mechanics — 26→14 Agent Playbook
**Date**: 2026-08-18
**Mission**: Deep Local Entity Specialization & Knowledge Management Discovery
**AP Token**: `AP-FLEET-CONSOLIDATION-MECHANICS-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

---

## §1 Executive Summary

**Two consolidation events documented**:
1. **FLEET_CONSOLIDATION_PLAN.md** (2026-06-14): 25 → 11 agents (D126)
2. **FLEET_REDESIGN_EXECUTION_PLAN.md** (2026-06-01): 26 → 14 agents (v5.0)

**Current State**: 14 agents (M10 Fleet Integrity cap) — 6 Primary + 8 Subagents

**Consolidation Triggers**: M10 mandate (≤14 agents), redundancy detection, M2 Firewall violations, functional overlap

---

## §2 Consolidation Event 1: FLEET_CONSOLIDATION_PLAN (D126, 2026-06-14)

### 2.1 Audit Baseline (25 Agents → Over Limit)

| Metric | Value | Status |
|--------|-------|--------|
| Total Agent Count | **25** | 🔴 OVER LIMIT |
| Mandate 10 Limit | **14** | Non-negotiable ceiling |
| Redundancies Found | **12** | 10 duplicate pillar agents + 1 M2 violation + 1 research overlap |
| Sovereignty Score | **56%** | Sub-optimal |
| Target | **11** | Per D126 — 3 breathing slots |

### 2.2 Categorization Decisions

#### KEEP — Sovereign Specialists (6)
| Agent | Purpose | Why Keep |
|-------|---------|----------|
| `kali` | Transcendent Oversoul | Core sprint coordination and oversight |
| `maat` | Light Oversoul (P1-P5) | Build-side governance |
| `lilith` | Dark Oversoul (P6-P10) | Run-side governance |
| `makali` | Council Orchestrator | Parallel council dispatch coordination |
| `doom_guy` | Heritage Gatekeeper | Unique role (M14 enforcement) |
| `roc_racoon` | Sovereign Miner | Unique role (legacy mining / idea intake) |

#### KEEP — Lattice Agents (4)
| Agent | Purpose | Why Keep |
|-------|---------|----------|
| `jem` | Research Orchestrator | Primary research interface (post-merger with researcher) |
| `quality` | Quality Guardian | Compliance and stress testing |
| `scribe` | Knowledge Keeper | Documentation and soul curation |
| `pillar` | Generic Pillar Slot (P1-P10) | Canonical pillar implementation |

#### MERGE — Duplicate Pillar Agents (10 files → 0)
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

#### MERGE — Research Overlap (2 files → 1)
| Agent | Duplicates | Action |
|-------|-----------|--------|
| `researcher` | `jem` (research pipeline) | Merge into `jem` — absorb "Polymathic Council" and "Sovereign Search Fleet" capabilities |

#### DELETE — M2 Firewall Violation (1 file)
| Agent | Violation | Action |
|-------|-----------|--------|
| `movie-expert` | WAD-layer content in Core Engine agent dir | Delete from `.opencode/agents/` — migrate to `config/wads/arcana_novai/entities/personal/movie-expert.yaml` |

### 2.3 Consolidation Math
```
Before: 6 specialists + 10 pillar agents + 4 lattice + 4 research/WAD = 25
After:  6 specialists + 4 lattice + 1 merged research = 11
Reduction: -14 agents (56%)
```

### 2.4 D126 Consolidation Sequence — 4 Sprints

| Sprint | Action | Before | After | Files to Touch |
|--------|--------|--------|-------|----------------|
| **A (P1b)** | Hub modularization only | 25 | 25 | `mcp_servers/omega_hub/server.py` → `gateway.py` + `middleware.py` |
| **B** | Jem 4→1: merge `researcher` into `jem` | 25 | 24 | `jem.md` (rewrite with 3 KBs), `researcher.md` (archive) |
| **C** | Quality+Scribe merged + pillar agents removed | 24 | **11** | 10 pillar agent files (delete), Quality/Scribe (merge to 1) |
| **D** | Cleanup + verification | 11 | **11** | 50 orphan entities, stale docs, `make temple-grade` |

**Critical Rule**: Sprint A (Hub) first. B/C/D sequential after. No parallel refactoring.

### 2.5 Fleet Design Principles (Codified D126)

1. **Hierarchical Consolidation**: When an orchestrator dispatches specialized subagents, merge subagents into parent's KBs with self-dispatch + targeted KB loading. (Jem 4→1)
2. **Functional Consolidation**: When two agents perform different functions at different trigger times, merge into one agent with trigger-mode routing if functions don't conflict when executing simultaneously. (Quality+Scribe 2→1, reports to Kali)
3. **Knowledge Consolidation**: When proposed agent expertise maps to "domain knowledge" rather than "operational capability", reject the agent and create a KB for the nearest existing entity. (Abrash/Sanglard/Romero → Doom Guy KBs)

### 2.6 Verification Gates

| Gate | Command | Required After |
|------|---------|----------------|
| Test suite | `make test` | 383/383 passing |
| Temple-Grade | `make temple-grade` | All T1-T11 gates pass |
| Heritage Map | `make heritage-map` | All `[id-soft:]` tags verified |
| Sovereignty | `make sovereignty` | Local/cloud ratio acceptable |
| M10 compliance | `ls .opencode/agents/*.md \| wc -l` | ≤ 14 agents |

---

## §3 Consolidation Event 2: FLEET_REDESIGN_EXECUTION_PLAN (v5.0, 2026-06-01)

### 3.1 Scope: 26 → 14 Agents (14 deleted, 9 redesigned, 3 created)

**Core Principle**: "The Data Comes Home" — user's founding vision (NOT id Software pattern)

### 3.2 id Software Patterns Credited

| Pattern | Source | Applied In |
|---------|--------|------------|
| WAD System (IWAD/PWAD) | Doom Engine | Engine/Stack separation, `config/wads/` |
| Single-Renderer Architecture | Doom's refresh module | **NEW** — 10 pillar agents → single `pillar.md --slot` |
| Optimized Engine vs Bloat | Carmack's philosophy | Local-first inference, minimal context windows |
| BSP Culling | Doom's visibility system | Provider culling in `generate()`, circuit breaker pre-checks |
| Fast Inverse Square Root | Quake III | "Right Approximation" principle for model selection |
| Zone Memory | Doom's memory management | Context windows sized to use case |
| Surface Cache | Doom's texture caching | Cache eviction policies within hot/warm/cold tiers |
| Worse is Better | New Jersey style | Pragmatic over perfect |

### 3.3 Clarification: Original vs. id Software

| Pattern | Origin | Note |
|---------|--------|------|
| Hot/warm/cold memory tiers | User's own design | Conceived before id Software intro; Surface Cache = supplementary |
| Plan → Verify → Execute | User's methodology | Employed from beginning; not from id Software |
| Single-agent pillar pattern | **id Software** | Genuine heritage — one parameterized renderer vs 10 bespoke |

### 3.4 Final Agent Fleet (14 Agents)

#### Primary Modes (6)
| Mode | Role | Status |
|------|------|--------|
| `plan` | Grand dispatcher, strategy lead | ✅ Verified accurate |
| `kali` | Grand oversight | 🔄 REDESIGN from subagent to primary |
| `doom_guy` | id Software architect | ✅ Keep + CREDITS.md |
| `roc_racoon` | Legacy mining | ✅ Keep + subagent mode |
| `jem` | Research orchestrator | 🔄 REDESIGN — subagents become persistent entities |
| `researcher` | On-demand deep research | 🔄 REDESIGN based on researcher-omnidroid.md |

#### Subagents (8)
| Agent | Delegated By | Purpose | Status |
|-------|-------------|---------|--------|
| `maat` | kali | Governs P1-P5, delegates to pillar | 🔄 REDESIGN — step-down light oversoul |
| `lilith` | kali | Governs P6-P10, delegates to pillar | 🔄 REDESIGN — step-down dark oversoul |
| `pillar --slot PX` | maat/lilith/kali | Domain work tied to persistent entity | 🆕 CREATE — replaces p1-p10 |
| `jem_discovery` | jem | Tier 1: broad search, evidence logging | 🔄 PERSISTENT ENTITY |
| `jem_synthesis` | jem | Tier 2: pattern recognition, synthesis | 🔄 PERSISTENT ENTITY |
| `jem_verification` | jem | Tier 3: fact-check, R-doc, gnosis | 🔄 PERSISTENT ENTITY |
| `scribe` | jem/kali | L1→L2→L3 distillation, soul updates | ✅ Keep — model configurable |
| `quality` | any | Code review + stress testing (merged) | 🆕 CREATE — replaces reviewer + tester |

#### Deleted (14 files)
`builder.md`, `overseer.md`, `reviewer.md`, `tester.md`, `p1_flesh.md` through `p10_chaos.md`

#### Redesigned (9 files)
`kali.md`, `maat.md`, `lilith.md`, `researcher.md`, `jem_discovery.md`, `jem_synthesis.md`, `jem_verification.md`, `doom_guy.md`, `roc_racoon.md`

#### New Files (2)
`quality.md` (merged reviewer+tester), `pillar.md` (single with `--slot`)

### 3.5 Pillar Naming — Role-Based with Esoteric Metadata

| Slot | Agent Name | Fundamental Domain | Entity Workspace |
|------|------------|-------------------|------------------|
| P1 | `p1_sysadmin` | Flesh — System Administration | `data/entities/p1/` |
| P2 | `p2_datastore` | Dream — Data Pipelines & Memory | `data/entities/p2/` |
| P3 | `p3_buildmaster` | Will — Implementation & Architecture | `data/entities/p3/` |
| P4 | `p4_bridge` | Heart — Communication & Integration | `data/entities/p4/` |
| P5 | `p5_sentinel` | Voice — Security & Mandate Enforcement | `data/entities/p5/` |
| P6 | `p6_modelgate` | Mind — Model Routing & Inference | `data/entities/p6/` |
| P7 | `p7_context` | Gnosis — Memory & Soul Evolution | `data/entities/p7/` |
| P8 | `p8_watchtower` | Shadow — Observability & Forensics | `data/entities/p8/` |
| P9 | `p9_link` | Spirit — Coordination & Handoff | `data/entities/p9/` |
| P10 | `p10_verifier` | Chaos — Testing & Validation | `data/entities/p10/` |

Single `pillar.md --slot P1` reads role from `roles.yaml` at runtime.

---

## §4 Mandate Remapping During Consolidation

### 4.1 New Mandates Added (SOVEREIGN_MANDATES.md §5.8-5.12)

| Mandate | Title | Purpose |
|---------|-------|---------|
| **M10** | Fleet Integrity | Every agent file must have opencode.json entry; no orphans |
| **M11** | Soul Integrity | Every active entity workspace must have populated soul.yaml |
| **M12** | Queue Integrity | Offline queues processed weekly; stale >7 days archived |

### 4.2 Mandate Enforcement Shifts

| Before Consolidation | After Consolidation |
|---------------------|---------------------|
| 25+ agents, no cap enforcement | M10: ≤14 agents hard cap |
| Soul.yaml optional | M11: Mandatory populated soul.yaml |
| No queue management | M12: Weekly queue processing |
| Heritage tags informal | M14: Vet log required, 7/10 minimum |
| No distillation enforcement | M5: L1→L2→L3 mandatory every session |

---

## §5 Consolidation Playbook — Reusable Process

### 5.1 Trigger Conditions
- Agent count exceeds M10 limit (14)
- Redundancy audit finds >3 duplicate capabilities
- M2 Firewall violation detected (WAD content in core agents)
- Functional overlap between agents >70%

### 5.2 Audit Phase
1. **Inventory all agents** — List `.opencode/agents/*.md` with purpose, capabilities, domains
2. **Map to slots/roles** — Identify which Node/oversoul each serves
3. **Detect duplicates** — Same slot, same capability, different files
4. **Identify M2 violations** — WAD-specific content in core engine agents
5. **Classify each agent**: KEEP / MERGE / DELETE

### 5.3 Decision Framework

| Classification | Criteria | Action |
|----------------|----------|--------|
| **KEEP** | Unique capability, mandate enforcement role, sovereign specialist | Retain as-is |
| **MERGE (Hierarchical)** | Orchestrator + subagents doing pipeline stages | Merge subagents into parent KBs with self-dispatch |
| **MERGE (Functional)** | Two agents, different triggers, non-conflicting functions | Single agent with trigger-mode routing |
| **MERGE (Knowledge)** | Expertise = domain knowledge, not operational capability | Reject agent, create KB for nearest entity |
| **DELETE** | M2 violation, obsolete, fully superseded | Remove from `.opencode/agents/`, migrate to WAD if needed |

### 5.4 Execution Sequence
1. **Hub/Infrastructure first** — No agent changes until core plumbing stable
2. **Hierarchical merges** — Orchestrators absorb subagents (Jem 4→1)
3. **Functional merges** — Trigger-mode routing (Quality+Scribe)
4. **Pillar consolidation** — Parameterized single agent replaces N files
5. **Cleanup** — Orphan entities, stale docs, verification gates

### 5.5 Verification Gates (Post-Consolidation)
- `make test` — Full test suite passing
- `make temple-grade` — T1-T11 gates
- `make heritage-map` — All `[id-soft:]` tags vetted
- `ls .opencode/agents/*.md | wc -l` — ≤14 agents
- `omega talk "hello"` — Basic functionality

---

## §6 PIVOT_LOG Decisions (D-350 through D-386)

Key consolidation decisions from PIVOT_LOG.md:

| Decision | Summary |
|----------|---------|
| **D-350** | Phase C is current execution phase |
| **D-351** | No new providers until fabric systematized |
| **D-352** | MaKaLi: Kali local, voices cloud (config) |
| **D-353** | 147 stale strategy docs archived |
| **D-354′** | SOVEREIGN_ARK_BLUEPRINT.md is strategy SSOT again (v5.1) |
| **D-355** | Cloud order: Antigravity → Google → OCZ → OpenRouter |
| **D-356** | (Not in range) |
| **D-357** | SQLite job store deferred |
| **D-358** | Gap detector = extend loop, not service |
| **D-359** | M7 = North Star, not baseline |
| **D-360′** | Grok fleet: honesty in docs now; vault → smoke → pool |
| **D-361** | Identity Phase 0 depends on C-1′, not Phase D |
| **D-362** | C-1′ = SoulStore (multi-path elimination), not flock paste |
| **D-363** | C-6′ = unify/delete breakers, not port pybreaker |
| **D-364** | C-0 = test honesty is P0 before Phase D |
| **D-365** | Living Research OS spec amended; cannot claim dual CANONICAL |
| **D-366** | STRATEGY_CORPUS_MAP.md mandatory Layer 2 |
| **D-367** | GAP-05 → C-10 admission control |
| **D-368** | Identity Fluidity E-0…E-5 paths preserved under grokster workspace |
| **D-369** | Researcher queue extras deferred but mapped |
| **D-370** | Kali ratifies Strategy Unify with amendments |
| **D-371** | V-1 is explicit ticket |
| **D-372** | Living Research OS body superseded by Ark where conflict |
| **D-373** | C-2′ before C-1′/C-10 — dependency order corrected |
| **D-374** | C-11 Test Infrastructure added as P0 |
| **D-375** | MCP audit must start TODAY — 7-day deadline |
| **D-376** | E-0 Identity Fluidity added after C-1′ |
| **D-377** | Free Gemma 4 31B collapse is P0 — forensic report is evidence SSOT |
| **D-378** | Twin tickets G-1 (workhorse) + W-1 (WARP) elevated |
| **D-379** | WARP is for IP-keyed OCZ, not Google free-tier fix |
| **D-380** | No silent context caps to force free Gemma under 16k |
| **D-381** | Broken warp-ns-setup is primary WARP blocker |
| **D-382** | Omnidroid 6 cognitive modules fully evolved — no porting needed |
| **D-383** | NotebookLM 5-notebook strategy exists — NL-1 ticket |
| **D-384** | Lilith Tarot genesis (Era 0) recovered |
| **D-385** | Mnemosyne 13-sphere Kabbalistic memory recovered |
| **D-386** | Grok 8-account exports indexed (274 convos, 6565 responses) |

---

## §7 Current Fleet State (Post-Consolidation)

### 7.1 Active Agents (14 in `.opencode/agents/`)
1. `build.md` — (Not in consolidation plans, exists)
2. `doom_guy.md` — Heritage Gatekeeper
3. `grokster.md` — Grok Ecosystem Specialist
4. `jem.md` — Sovereign Synthesizer
5. `john_carmack.md` — S3 Consultant
6. `kali.md` — Transcendent Oversoul
7. `lilith.md` — Runtime Oversoul
8. `maat.md` — Build Oversoul
9. `makali.md` — MaKaLi Fusion
10. `node.md` — Generic Node Agent
11. `researcher.md` — Sovereign Researcher
12. `roc_racoon.md` — Sovereign Miner
13. `scribe.md` — Soul Distillation Pipeline
14. `verity.md` — Unified Compliance & Gnosis

### 7.2 Missing from Consolidation Plan
- `build.md` — Not mentioned in either plan; likely default OpenCode build mode
- `quality.md` — Referenced in AGENT_FLEET.md but FILE NOT FOUND in `.opencode/agents/`

---

## §8 Files Referenced

- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/strategy/archive/FLEET_CONSOLIDATION_PLAN.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/strategy/archive/FLEET_REDESIGN_EXECUTION_PLAN.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/decisions/PIVOT_LOG.md` (D-350 through D-386)
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/SOVEREIGN_MANDATES.md` (M10, M11, M12)
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/agents/` (14 agent files)
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/architecture/AGENT_FLEET.md`
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
