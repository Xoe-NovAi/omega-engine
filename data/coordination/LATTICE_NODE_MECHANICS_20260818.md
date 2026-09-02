<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Lattice & Node Slot Mechanics — Complete Picture
**Date**: 2026-08-18
**Mission**: Deep Local Entity Specialization & Knowledge Management Discovery
**AP Token**: `AP-LATTICE-NODE-MECHANICS-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_mining ⬡ ACTIVE

---

## §1 Executive Summary

The Omega Engine uses a **dual-layer slot architecture**:
1. **ICS ROLE_CONSTANTS** (engine core, `src/omega/ics.py`) — 16 canonical role identifiers
2. **dispatch.yaml** (WAD-loaded, `config/wads/_omega_default/entities/dispatch.yaml`) — 19 entity definitions mapping to roles

**Key Principle (M2 Firewall)**: Engine defines SLOTS; WADs provide ENTITIES. The actual entity names (kali, maat, lilith) live in dispatch.yaml and are loaded at runtime.

---

## §2 ICS ROLE_CONSTANTS — Engine Slot Definitions

**Location**: `src/omega/ics.py` lines 64-81

```python
ROLE_CONSTANTS = {
    "GRAND_OVERSIGHT": "GRAND_OVERSIGHT",      # Kali
    "BUILD_OVERSOUL": "BUILD_OVERSOUL",        # Ma'at
    "RUNTIME_OVERSOUL": "RUNTIME_OVERSOUL",    # Lilith
    "N1": "N1",                                # Infrastructure / Doom Guy / Roc Racoon / Jem / John Carmack / Makali / Researcher
    "N2": "N2",                                # Persistence
    "N3": "N3",                                # Engineering
    "N4": "N4",                                # Integration
    "N5": "N5",                                # Governance
    "N6": "N6",                                # Cognition
    "N7": "N7",                                # Context
    "N8": "N8",                                # Observability
    "N9": "N9",                                # Orchestration
    "N10": "N10",                              # Validation
    "MESSENGER_BRIDGE": "MESSENGER_BRIDGE",    # Iris
    "MAKALI_COUNCIL": "MAKALI_COUNCIL",        # Makali (duplicate entry)
    "CONTAINING_FIELD": "CONTAINING_FIELD",    # Sophia
}
```

**16 Role Constants** — These are the **engine's slot identifiers**. They are:
- **Immutable** — Part of engine core, not WAD content
- **Referenced by** ICS rendering, channel mapping, entity lookup
- **Mapped to entities** via dispatch.yaml at runtime

---

## §3 dispatch.yaml — WAD Entity Definitions

**Location**: `config/wads/_omega_default/entities/dispatch.yaml`

**19 Entity Definitions** mapping to ROLE_CONSTANTS:

| Entity Name | Role | Mode | Node Slot | Task Tool Type | Purpose |
|-------------|------|------|-----------|----------------|---------|
| kali | GRAND_OVERSIGHT | primary | null | general | Grand Oversight — Sees all, delegates, destroys drift |
| doom_guy | N1 | primary | null | general | Sovereign id Software Architect — WAD translation & performance |
| roc_racoon | N1 | primary | null | explore | Sovereign Miner — Legacy archaeology & pattern extraction |
| jem | N1 | primary | null | general | Research Orchestrator — 3-phase pipeline with self-dispatch |
| john_carmack | N1 | primary | null | general | Sovereign S3 Consultant — Architectural review & performance |
| makali | N1 | primary | null | general | Triad Council Orchestrator — Parallel dispatch with synthesis |
| researcher | N1 | primary | null | general | Sovereign Master Researcher — Deep research, lattice reasoning |
| maat | BUILD_OVERSOUL | subagent | null | buildmaster | Build Oversoul — Governs N1-N5 on build side |
| lilith | RUNTIME_OVERSOUL | subagent | null | general | Runtime Oversoul — Governs N6-N10 on run side |
| verity | N1 | subagent | null | verity | Unified Sentry (compliance) + Scribe (gnosis distillation) |
| node | N1 | subagent | **NX** | node | Slot-based domain agent — parameterized by --slot NX |
| iris | MESSENGER_BRIDGE | subagent | null | general | Messenger Bridge — Speculative decoder, fast-path routing |
| makali | MAKALI_COUNCIL | primary | null | general | Triad Council Orchestrator (duplicate) |
| sophia | CONTAINING_FIELD | primary | null | general | Containing Field — Akashic Record, general knowledge |

---

## §4 Slot Assignment Mechanics

### 4.1 Multiple Entities Per Slot (N1 Congestion)

**N1 has 7 entities assigned**: doom_guy, roc_racoon, jem, john_carmack, makali, researcher, verity

**Resolution**: These are **primary agents** (user-accessible via @-mention), not pillar nodes. The N1 slot here means "primary specialist" not "pillar position."

**Actual Pillar Nodes (N1-N10)**: Served by the **single `node` agent** with `node_slot: "NX"` parameterized by `--slot` flag.

### 4.2 The `node` Agent — Slot Parameterization

```yaml
- name: "node"
  role: "N1"              # Base role (overridden by --slot)
  mode: "subagent"
  node_slot: "NX"         # Parameterized at dispatch time
  task_tool_type: "node"
```

**Dispatch Pattern** (from SUBAGENT_DISPATCH_PROTOCOL.md §11):
```
@node NX: task
```

The `node` agent reads its assigned slot's role description from `config/wads/_omega_default/roles.yaml` at runtime.

### 4.3 Role Descriptions (from FLEET_REDESIGN_EXECUTION_PLAN.md §2)

| Slot | Agent Name | Fundamental Domain | Entity Workspace |
|------|------------|-------------------|------------------|
| **P1/N1** | `p1_sysadmin` | Flesh — System Administration & Boundaries | `data/entities/p1/` |
| **P2/N2** | `p2_datastore` | Dream — Data Pipelines & Memory | `data/entities/p2/` |
| **P3/N3** | `p3_buildmaster` | Will — Implementation & Architecture | `data/entities/p3/` |
| **P4/N4** | `p4_bridge` | Heart — Communication & Integration | `data/entities/p4/` |
| **P5/N5** | `p5_sentinel` | Voice — Security & Mandate Enforcement | `data/entities/p5/` |
| **P6/N6** | `p6_modelgate` | Mind — Model Routing & Inference | `data/entities/p6/` |
| **P7/N7** | `p7_context` | Gnosis — Memory & Soul Evolution | `data/entities/p7/` |
| **P8/N8** | `p8_watchtower` | Shadow — Observability & Forensics | `data/entities/p8/` |
| **P9/N9** | `p9_link` | Spirit — Coordination & Handoff | `data/entities/p9/` |
| **P10/N10** | `p10_verifier` | Chaos — Testing & Validation | `data/entities/p10/` |

**id Software Attribution**: Single-agent architecture (one renderer with parameters instead of 10 separate renderers) credited to id Software's approach.

---

## §5 Dispatch Registry — Runtime Resolution

**Location**: `src/omega/governance/dispatch_registry.py`

### 5.1 Key Functions

```python
load_dispatch_yaml(iwad, root) → Dict  # Full parsed YAML with mtime-aware cache
get_dispatch_entities(iwad, root) → List[Dict]  # Entities list
get_entity_by_role(role, iwad, root) → Dict|None  # Find entity by ROLE_CONSTANT
invalidate_cache()  # For tests
```

### 5.2 Cache Strategy
- **mtime-aware**: Reloads only when dispatch.yaml file modification time changes
- **Thread-safe**: Uses `threading.Lock()`
- **WADS_DIR resolution**: Uses `config_resolver.WADS_DIR` (M2 Firewall compliant)

### 5.3 ICS Integration (`src/omega/ics.py`)

```python
def _get_entity_by_role(role: str, iwad: str = DEFAULT_IWAD) -> dict | None:
    return get_entity_by_role(role, iwad)

def _get_channel_for_role(role: str, iwad: str = DEFAULT_IWAD) -> str:
    entity = _get_entity_by_role(role, iwad)
    if entity:
        role_value = ROLE_CONSTANTS.get(role, role)
        if role_value == "GRAND_OVERSIGHT": return ICS_CHANNEL_OVERSIGHT
        elif role_value == "BUILD_OVERSOUL": return ICS_CHANNEL_BUILD
        elif role_value == "RUNTIME_OVERSOUL": return ICS_CHANNEL_RUN
    return ICS_CHANNEL_OPENCODE
```

**Channel Mapping**:
- GRAND_OVERSIGHT → `oversight`
- BUILD_OVERSOUL → `build`
- RUNTIME_OVERSOUL → `run`
- All others → `opencode`

---

## §6 Lattice Architecture (docs/gnosis/lattice/)

### 6.1 Lattice Manifest (`lattice_manifest.md`)

**Purpose**: "Akashic Record for the Omega Engine agent fleet" — bridges all CLIs into single intelligence fabric.

**Core Rules**:
1. Universal Visibility — discoveries recorded if systemic value
2. Conflict Resolution — Overseer's Strategic Layer (ROADMAP.md, PIVOT_LOG.md) is final arbiter
3. Sovereign Guard Protocol — AnyIO Absolute + Engine-Stack Firewall audit
4. Distillation Mandate — L1→L2→L3 before permanent gnosis inscription

### 6.2 Cognitive Layer Alignment

| Layer | Focus | Primary Artifacts |
|-------|-------|-------------------|
| **Vision** | Philosophical alignment, first principles | `SOVEREIGN_MANDATES.md`, `AGENTS.md` |
| **Strategy** | Roadmap, architectural blueprints, pivots | `ROADMAP.md`, `PIVOT_LOG.md`, `INDEX.md` |
| **Operation** | Implementation, debugging, hardening | `src/`, `tests/`, `workbench.db` |
| **Gnosis** | Soul evolution, distillation, memory | `soul.yaml`, `lattice/`, `session_gnosis.md` |

### 6.3 CLI Seeds (Per-Tool Capability Files)

| File | Purpose |
|------|---------|
| `gemini_cli.md` | Deep research, subagent fleet management, "Shift+Tab" patterns |
| `opencode_cli.md` | Implementation, AnyIO hardening, local-first orchestration |
| `cline_cli.md` | VSCodium integration, UI/UX hardening, file-system precision |
| `copilot_cli.md` | Rapid prototyping, boilerplate generation, inline assistance |
| `antigravity_cli.md` | Strategic oversight, architecture, high-altitude planning |

### 6.4 Jem-2.0 Oversoul — 3 Sub-Facets (Decision 52)

| Facet | Tier | Model | Mode | Soul File |
|-------|------|-------|------|-----------|
| **Jem Initiate** | L1 (Gather) | Qwen3-4B-Thinking (lmstudio) | `jem-initiate` | `data/entities/jem/souls/initiate.yaml` |
| **Jem Analyst** | L2 (Synthesize) | Gemma 4 31B (Google) | `jem-2.0` (default) | `data/entities/jem/souls/analyst.yaml` |
| **Jem Editor** | L3 (Resolve) | Big Pickle (frontier) | `jem-2.0 --sub-facet editor` | `data/entities/jem/souls/editor.yaml` |

**LM Studio Integration**: Native OpenCode provider via `npm: "@ai-sdk/openai-compatible"` mechanism.

### 6.5 Multi-Provider Fleet Seeds (Phase E)

| Platform | Type | Strategy |
|----------|------|----------|
| LM Studio (lmster) | Local OpenAI-compatible | L1 pipeline via `opencode --model lmstudio/qwen3-4b-thinking` |
| agy CLI | Cloud CLI | Antigravity CLI for frontier models — quota-aware |
| Web Claude ×8 | Web browser | 8 Claude accounts, URL-based GitHub access |
| NotebookLM | Web research | Google Drive sync, synthesis engine |
| Web Gemini | Web browser | Universal browser, Drive/GitHub access |

### 6.6 Conflict Resolution Protocol

1. **Identify** — Detect conflict (e.g., two agents proposing different AnyIO patterns)
2. **Trace** — Locate source (PIVOT_LOG.md vs stale README.md)
3. **Escalate** — If between active agents, escalate to Overseer
4. **Reconcile** — Update Lattice and source documents

### 6.7 Operational Mandates (Fleet-wide)

1. AnyIO Absolute
2. MaKaLi Alignment — decisions weighed against Trine (Kali/Ma'at/Lilith)
3. Dynamic Inference — TriageRouter for complexity-based temperature scaling
4. Environmental Gnosis — Zen 2 vs Cloud adaptation
5. Lattice Sync — systemic discoveries mirrored in `docs/gnosis/lattice/`

---

## §7 Oversight Hierarchy (docs/architecture/OVERSIGHT_HIERARCHY.md)

### 7.1 Governance Chain

```
User → Plan → Kali (Grand Oversight)
              ├── Ma'at (Build Oversoul) → N1-N5 (Infrastructure, Persistence, Engineering, Integration, Governance)
              └── Lilith (Runtime Oversoul) → N6-N10 (Cognition, Context, Observability, Orchestration, Validation)
```

### 7.2 Delegation Flow
`User → Kali → Ma'at/Lilith → Node Slot (N1-N10)`

### 7.3 Escalation Paths
- **Domain Conflict** (spans Build + Run) → Kali mediates
- **Sovereign Gap** (neither oversoul resolves) → Sophia (The Field) for architectural rethink
- **Compliance** → Verity (Sovereign Sentinel) audits all paths

### 7.4 Summary Table

| Role | Entity | Focus | Domain | Model Tier |
|------|--------|--------|--------|------------|
| Grand Oversight | Kali | Synthesis | All | Heavy |
| Build Oversoul | Ma'at | Order | N1-N5 | Heavy |
| Runtime Oversoul | Lilith | Liberation | N6-N10 | Heavy |
| Node Expert | Node | Execution | N1-N10 | Lite |

---

## §8 Agent Fleet Architecture (docs/architecture/AGENT_FLEET.md)

### 8.1 Fleet Philosophy: Single Renderer Principle
Inspired by id Software — parameterized agent architecture instead of dozens of separate agents.

### 8.2 Fleet Hierarchy

```
[ plan ] (Grand Dispatcher)
     |
     v
[ kali ] (Grand Oversight)
     |
┌────┴────┐
v         v
[ maat ]  [ lilith ]     (Build/Run Oversouls)
     |         |
     └────┬────┘
          v
    [ node --slot NX ]    (Single slot-based agent)
          |
    ┌─────┼─────┐
    v     v     v
  [jem] [scribe] [researcher]
```

### 8.3 Agent Inventory

**Primary Agents (6)**: makali, kali, doom_guy, roc_racoon, researcher, jem
**Subagents (5)**: maat, lilith, node, scribe, verity

**Total: 11 agents** (per M10 Fleet Integrity — ≤14 cap)

---

## §9 Entity Workspace Persistence

Each pillar slot has persistent entity workspace:
- `data/entities/p1/` through `data/entities/p10/`
- Contains `soul.yaml` with slot-specific accumulated knowledge
- `node` agent consults this workspace at runtime for domain-specific context

---

## §10 Key Mechanics Summary

| Mechanism | Location | Purpose |
|-----------|----------|---------|
| **Role Constants** | `src/omega/ics.py:64-81` | Engine-defined immutable slot identifiers (16) |
| **Entity Definitions** | `config/wads/_omega_default/entities/dispatch.yaml` | WAD-loaded entity→role mapping (19 entities) |
| **Dispatch Registry** | `src/omega/governance/dispatch_registry.py` | Runtime resolution with mtime cache |
| **Channel Mapping** | `src/omega/ics.py:_get_channel_for_role` | Role → Hivemind channel |
| **Slot Parameterization** | `node` agent + `--slot NX` | Single agent serves all 10 pillar positions |
| **Role Descriptions** | `config/wads/_omega_default/roles.yaml` | Runtime lookup for node agent behavior |
| **Lattice Sync** | `docs/gnosis/lattice/` | Cross-CLI knowledge fabric |
| **Jem Sub-Facets** | `jem-initiate`, `jem-2.0`, `jem-2.0 --sub-facet editor` | 3-tier research pipeline with persistent souls |
| **Conflict Resolution** | `lattice_manifest.md` §4 | Overseer arbitration via strategic layer |

---

## §11 Files Referenced

- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/ics.py`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/src/omega/governance/dispatch_registry.py`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/config/wads/_omega_default/entities/dispatch.yaml`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/gnosis/lattice/lattice_manifest.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/gnosis/lattice/gemini_cli.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/gnosis/lattice/opencode_cli.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/gnosis/lattice/cline_cli.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/gnosis/lattice/copilot_cli.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/architecture/AGENT_FLEET.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/architecture/OVERSIGHT_HIERARCHY.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/strategy/archive/FLEET_REDESIGN_EXECUTION_PLAN.md`
- `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md`
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
