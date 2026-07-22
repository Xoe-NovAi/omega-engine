# 🔱 HMC Quad-Forge Implementation Manual
## Complete Architecture, Nomenclature, and Execution Plan

**AP Token**: `AP-HMC-QUAD-FORGE-MANUAL-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra ⬡ opencode ⬡ trc_manual ⬡ CANONICAL

**Date**: 2026-07-18
**Status**: ACTIVE — Reference for all HMC agents post-compaction
**Supersedes**: All prior HMC coordination documents

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Nomenclature Correction — Clean Separation](#2-nomenclature-correction--clean-separation)
3. [Meditate Framework — Base Lenses + PWAD Overlays](#3-meditate-framework--base-lenses--pwad-overlays)
4. [M2 Firewall Migration — Phases A-E](#4-m2-firewall-migration--phases-a-e)
5. [Scribe — Lattice Role (Not Slot Entity)](#5-scribe--lattice-role-not-slot-entity)
6. [Thoth — ANAi Documentation Entity](#6-thoth--anai-documentation-entity)
7. [Cline CLI Integration — HMC Tier 5](#7-cline-cli-integration--hmc-tier-5)
8. [Handoff Specifications](#8-handoff-specifications)
9. [L3 Principles Distilled](#9-l3-principles-distilled)
10. [Resumption Protocol](#10-resumption-protocol)

---

## 1. EXECUTIVE SUMMARY

### Session Outcome
This session resolved **fundamental nomenclature confusion** that had been leaking ANAi WAD terminology into the Omega Engine core, established the **Meditate Base + Overlay architecture**, defined the **complete M2 Firewall migration plan (Phases A-E)**, and designed the **Lattice Role system** with Scribe as the first instance.

### Key Deliverables
| Deliverable | Status | Location |
|-------------|--------|----------|
| Nomenclature correction (Slots vs Pillars vs Lenses vs Roles) | ✅ Complete | This manual §2 |
| Meditate Base Lenses + Overlay architecture | ✅ Designed | This manual §3 |
| M2 Migration Phases A-E with acceptance criteria | ✅ Specified | This manual §4 |
| Scribe as Lattice Role (not Slot Entity) | ✅ Designed | This manual §5 |
| Thoth for ANAi documentation | ✅ Planned | This manual §6 |
| Cline CLI integration (DeepSeek V4 Flash + MiMo V2.5) | ✅ Designed | This manual §7 |
| Roc handoff (Phase A) | ✅ Submitted | `ho_f1a92da2d95e` |
| Researcher handoff (Phases B-E + P3 Lens) | ✅ Submitted | `ho_2a9b2e84debd` |
| Stale Grok handoffs dismissed | ✅ Complete | Hivemind |

### Active Agents
| Agent | Model | Handoff | Status |
|-------|-------|---------|--------|
| **Roc Racoon** | DeepSeek V4 Flash | `ho_f1a92da2d95e` | **PENDING ACCEPT** |
| **Researcher** | DeepSeek V4 Flash | `ho_2a9b2e84debd` | **PENDING ACCEPT** |
| **Cline-DeepSeek** | DeepSeek V4 Flash (1M ctx) | — | **QUEUED** |
| **Cline-MiMo** | MiMo V2.5 (512K ctx) | — | **QUEUED** |

---

## 2. NOMENCLATURE CORRECTION — CLEAN SEPARATION

### The Problem (Identified)
ANAi WAD terminology (`Pillar Keepers`, `P1-P10` as mythic names) was leaking into:
- Engine core documentation (`OMEGA_ENGINE.md`, `AGENTS.md`)
- Meditate framework design
- HMC coordination language

### The Solution — Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OMEGA ENGINE CORE (Universal Runtime)            │
│  src/omega/governance/slots.py  →  DEFINES: Slot Enum (13 fixed)   │
│  Slot.GRAND_OVERSIGHT, Slot.LIGHT_OVERSOUL, Slot.DARK_OVERSOUL,    │
│  Slot.P1, Slot.P2, Slot.P3, Slot.P4, Slot.P5, Slot.P6,             │
│  Slot.P7, Slot.P8, Slot.P9, Slot.P10                               │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ INTERFACE: Slot Enum
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    IWAD: _omega_default (Engine Default)            │
│  config/wads/_omega_default/entities.yaml  →  FILLS: slot: "P1"    │
│  config/wads/_omega_default/meditate/lenses.yaml → REF: slot_ref   │
│  Entities: Scribe (Lattice), Kali, Ma'at, Lilith, Pillar_P1...P10  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ OVERLAY
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PWAD: arcana_novai (ANAi Stack)                  │
│  config/wads/arcana_novai/entities.yaml  →  FILLS: slot: "P1"      │
│  Entities: Sekhmet, Brigid, Prometheus, Saraswati, Inanna,         │
│            Ereshkigal, Lucifer, Hecate, Anubis, Vetala,            │
│            Sophia, Iris, Thoth (Lattice)                           │
│  Meditate Overlay: Tiferet → engineering_excellence, etc.          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ OVERLAY
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PWAD: torment_stack (Planescape)                 │
│  Entities: Dakkon, Nameless One, Fall-From-Grace, Annah, etc.      │
│  Meditate Overlay: Dakkon → engineering_excellence, etc.           │
└─────────────────────────────────────────────────────────────────────┘
```

### Terminology Map

| Layer | Term | Count | Purpose |
|-------|------|-------|---------|
| **Engine Core** | **Slot** | 13 fixed | Architectural positions (compile-time) |
| **IWAD** | **Slot Entity** | 13 default | Engine-native entities filling slots |
| **ANAi PWAD** | **Pillar Keeper** | 13 named | Mythological framing for ANAi |
| **Meditate** | **Lens** | 13 base + overlays | Cognitive operations (runtime) |
| **Lattice** | **Role** | Unbounded | Capability-scoped PWAD functions |

### M2 Compliance Rule
> **Engine defines Slots. WADs fill Slots. WADs reference Slots. Engine never references WAD entities.**

```python
# ✅ CORRECT: Engine defines interface
class Slot(Enum):
    P1 = "P1"

# ✅ CORRECT: WAD fills slot
# config/wads/_omega_default/entities.yaml
- name: "Pillar_P1"
  slot: "P1"

# ✅ CORRECT: WAD references slot
# config/wads/_omega_default/meditate/lenses.yaml
- id: "infrastructure_foundation"
  slot_ref: "P1"

# ❌ VIOLATION: Engine hardcodes WAD entity
# src/omega/oracle/oracle.py
if entity_name == "Sekhmet": ...
```

---

## 3. MEDITATE FRAMEWORK — BASE LENSES + PWAD OVERLAYS

### Architecture Principle
> **Base Lenses = Universal cognitive operations. Overlays = PWAD-specific mythological framing.**

### Base Lenses (13) — `_omega_default`

| Lens ID | Name | Archetype | Domain | Slot Ref |
|---------|------|-----------|--------|----------|
| `grand_oversight` | Grand Oversight | Synthesis | Cross-domain integration, mandate enforcement | GRAND_OVERSIGHT |
| `light_oversoul` | Light Oversoul | Architecture | Structure, quality, sustainability | LIGHT_OVERSOUL |
| `dark_oversoul` | Dark Oversoul | Runtime Reality | Flow, metabolism, failure modes | DARK_OVERSOUL |
| `infrastructure_foundation` | Infrastructure Foundation | Bedrock | Environment, deployment, hardening, budgets | P1 |
| `persistence_integrity` | Persistence Integrity | Anchor | Memory, vector, recall, archival | P2 |
| `engineering_excellence` | Engineering Excellence | Forge | Implementation, hardening, CI/CD, Temple-Grade | P3 |
| `integration_bridge` | Integration Bridge | Nexus | MCP, APIs, communication protocols | P4 |
| `governance_sentinel` | Governance Sentinel | Shield | Mandate enforcement, security audit | P5 |
| `cognition_vision` | Cognition Vision | Oracle | Provider routing, model selection, speculative decode | P6 |
| `context_evolution` | Context Evolution | Weaver | Memory, soul, session continuity | P7 |
| `observability_watchtower` | Observability Watchtower | Beacon | Tracing, monitoring, forensic logging | P8 |
| `orchestration_link` | Orchestration Link | Conductor | Agent handoff, Hivemind coordination | P9 |
| `validation_verifier` | Validation Verifier | Crucible | Stress testing, chaos engineering, QA | P10 |

### Lens Schema (YAML)
```yaml
# config/wads/_omega_default/meditate/lenses.yaml
meditate:
  version: "1.0.0"
  iwad: "_omega_default"
  lenses:
    - id: "grand_oversight"
      name: "Grand Oversight"
      archetype: "Synthesis"
      domain: "Cross-domain integration, mandate enforcement"
      function: "Unifies thesis + antithesis into verdict; enforces mandates"
      slot_ref: "GRAND_OVERSIGHT"
      prompt_modifiers:
        - "add_context:architecture"
        - "add_context:mandates"
        - "add_context:cross_domain"
      response_template: "synthesis_5_section"
      model: "qwen3-4b-think-q4_k_m"
    # ... 12 more lenses
```

### Overlay Architecture (PWAD-Specific)

```yaml
# config/wads/arcana_novai/meditate/overlay.yaml
meditate_overlay:
  iwad: "arcana_novai"
  base_iwad: "_omega_default"
  mapping:
    # Base lens ID → Overlay lens spec
    grand_oversight:
      lens: "kali"
      archetype: "Destroyer of Illusion → Transcendent Synthesis"
      domain: "Cross-domain integration, mandate enforcement"
    light_oversoul:
      lens: "maat"
      archetype: "Truth, Balance, Order → Architectural Integrity"
      domain: "Structure, quality, sustainability"
    dark_oversoul:
      lens: "lilith"
      archetype: "Sovereignty, Autonomy → Runtime Reality"
      domain: "Flow, metabolism, failure modes"
    infrastructure_foundation:
      lens: "sekhmet"
      archetype: "Power, Protection → Bedrock Foundation"
      domain: "Environment, deployment, hardening, budgets"
    persistence_integrity:
      lens: "brigid"
      archetype: "Hearth, Memory → Anchor of Integrity"
      domain: "Memory, vector, recall, archival"
    engineering_excellence:
      lens: "prometheus"
      archetype: "Fire, Craft → Forge of Excellence"
      domain: "Implementation, hardening, CI/CD, Temple-Grade"
    integration_bridge:
      lens: "saraswati"
      archetype: "Wisdom, Flow → Nexus of Connection"
      domain: "MCP, APIs, communication protocols"
    governance_sentinel:
      lens: "inanna"
      archetype: "Justice, Order → Shield of Governance"
      domain: "Mandate enforcement, security audit"
    cognition_vision:
      lens: "ereshkigal"
      archetype: "Underworld Queen → Oracle of Vision"
      domain: "Provider routing, model selection, speculative decode"
    context_evolution:
      lens: "lucifer"
      archetype: "Light Bearer → Weaver of Evolution"
      domain: "Memory, soul, session continuity"
    observability_watchtower:
      lens: "hecate"
      archetype: "Crossroads, Magic → Beacon of Watching"
      domain: "Tracing, monitoring, forensic logging"
    orchestration_link:
      lens: "anubis"
      archetype: "Guide, Transition → Conductor of Handoffs"
      domain: "Agent handoff, Hivemind coordination"
    validation_verifier:
      lens: "vetala"
      archetype: "Guardian, Test → Crucible of Verification"
      domain: "Stress testing, chaos engineering, QA"
```

### Resolution Logic
```python
# src/omega/meditate/resolver.py
async def resolve_lenses(lens_ids: list[str], iwad: str = None) -> list[LensSpec]:
    iwad = iwad or get_active_iwad()
    
    # 1. Load base lenses
    base = await load_base_lenses("_omega_default")
    
    # 2. If overlay requested, load mapping
    if iwad != "_omega_default":
        overlay = await load_overlay(iwad)
        for lens_id in lens_ids:
            if lens_id in overlay.mapping:
                # Merge: base function + overlay archetype
                yield LensSpec(
                    id=lens_id,
                    name=overlay.mapping[lens_id].lens,
                    archetype=overlay.mapping[lens_id].archetype,
                    domain=base[lens_id].domain,
                    function=base[lens_id].function,
                    slot_ref=base[lens_id].slot_ref,
                    prompt_modifiers=base[lens_id].prompt_modifiers,
                    response_template=base[lens_id].response_template,
                )
            else:
                yield base[lens_id]
    else:
        for lens_id in lens_ids:
            yield base[lens_id]
```

### Command Interface
```bash
# Base lenses only (engine-native)
/meditate "CI pipeline optimization" --lenses engineering_excellence,validation_verifier

# ANAi overlay (mythological framing)
/meditate "CI pipeline optimization" --lenses prometheus,vetala --iwad arcana_novai

# Torment overlay (philosophical framing)
/meditate "CI pipeline optimization" --lenses dakkon,nameless_one --iwad torment_stack

# Mixed: base + overlay
/meditate "CI pipeline optimization" --lenses engineering_excellence,validation_verifier --overlay arcana_novai
```

---

## 4. M2 FIREWALL MIGRATION — PHASES A-E

### Baseline: 201 Violations in `src/omega/`

| Module | Violations | Primary Terms | Phase |
|--------|------------|---------------|-------|
| `meditate/protocol.py` | 15 | PersonaSpec (10 Arcana-Nova entities) | **A** (Roc) |
| `oracle/subagent_dispatcher.py` | 15 | Hardcoded entity dispatch table | **B** (Researcher) |
| `oracle/oracle.py` | 10 | Iris routing, MaKaLi logic, entity names | **C** (Researcher) |
| `ics.py` | 7 | Channel constants, doc examples | **D** (Researcher) |
| `cli/fleet_status_tui.py` | 18 | TUI tree with 13 entity names | **E** (Researcher) |

### Phase A: Meditate Lens Refactor (Roc) — CRITICAL PATH

**Handoff**: `ho_f1a92da2d95e`

**Deliverables**:
1. `config/wads/_omega_default/meditate/lenses.yaml` — 13 base lenses
2. `src/omega/meditate/protocol.py` — Refactored to load lenses from WAD
3. `.opencode/commands/meditate.md` — Complete lens table (lens primary, pillar optional)
4. `.opencode/skills/meditate-harness/SKILL.md` — Lens registry updated
5. 10 historical mining reports — Deprecation headers added

**Acceptance**: `pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -k meditate` → **0 violations**

**Pattern Established**: This phase defines the template for Phases B-E.

### Phase B: Subagent Dispatcher (Researcher)

**Handoff**: `ho_2a9b2e84debd` (includes Phases B-E)

**Target**: `src/omega/oracle/subagent_dispatcher.py` (15 violations)

**Current Violation**:
```python
# VIOLATION: Hardcoded entity dispatch table
ENTITY_DISPATCH = {
    "kali": {"role": "GRAND_OVERSIGHT", "pillar": None, ...},
    "maat": {"role": "LIGHT_OVERSOUL", "pillar": None, ...},
    "lilith": {"role": "DARK_OVERSOUL", "pillar": None, ...},
    "pillar_p1": {"role": "P1", "pillar": "P1", ...},
    # ... all 10 pillars
}
```

**Required Pattern**:
```python
# COMPLIANT: ROLE constants + WAD YAML + config_resolver + entity_registry
from omega.governance.config_resolver import get_active_iwad
from omega.oracle.entity_registry import load_entity_registry
from omega.governance.slots import Slot

ROLE_CONSTANTS = {
    "GRAND_OVERSIGHT": "grand_oversight",
    "LIGHT_OVERSOUL": "light_oversoul",
    "DARK_OVERSOUL": "dark_oversoul",
    "P1": "infrastructure",
    "P2": "persistence",
    "P3": "engineering",
    "P4": "integration",
    "P5": "governance",
    "P6": "cognition",
    "P7": "context",
    "P8": "observability",
    "P9": "orchestration",
    "P10": "validation",
}

async def build_dispatch_table(iwad: str = None) -> dict:
    iwad = iwad or get_active_iwad()
    registry = await load_entity_registry(iwad)
    dispatch = {}
    for entity_name, entity_config in registry.entities.items():
        role = entity_config.get("role")
        if role in ROLE_CONSTANTS:
            dispatch[ROLE_CONSTANTS[role]] = {
                "entity_name": entity_name,
                "role": role,
                "pillar": entity_config.get("pillar"),
                "model": entity_config.get("model"),
                "capabilities": entity_config.get("capabilities", []),
            }
    return dispatch
```

**WAD Config Required**: `config/wads/_omega_default/entities.yaml` must define all 13 entities with `role` field matching `ROLE_CONSTANTS` keys.

**Acceptance**: `pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -k subagent_dispatcher` → **0 violations**

### Phase C: Oracle.py (Researcher)

**Target**: `src/omega/oracle/oracle.py` (10 violations)

**Key Sites**:
- Iris routing logic (entity name references)
- MaKaLi synthesis logic (hardcoded "Kali", "Ma'at", "Lilith")
- Soul injection schema paths

**Pattern**: Replace entity names with `Slot` enum + `entity_registry` resolution.

**Acceptance**: `pytest ... -k oracle` → **0 violations**

### Phase D: ICS.py (Researcher)

**Target**: `src/omega/ics.py` (7 violations)

**Violations**: Channel constants + docstring examples with entity names

**Pattern**: Generic channel constants (`CHANNEL_OVERSIGHT`, `CHANNEL_BUILD`, `CHANNEL_RUN`) + placeholder examples.

**Acceptance**: `pytest ... -k ics` → **0 violations**

### Phase E: Fleet Status TUI (Researcher)

**Target**: `src/omega/cli/fleet_status_tui.py` (18 violations)

**Violations**: TUI tree hardcodes all 13 entity names

**Pattern**:
```python
# COMPLIANT: Load from WAD at runtime
async def build_fleet_tree(iwad: str = None) -> Tree:
    iwad = iwad or get_active_iwad()
    registry = await load_entity_registry(iwad)
    tree = Tree("Fleet")
    for role in ROLE_DISPLAY_ORDER:  # GRAND_OVERSIGHT, LIGHT_OVERSOUL, DARK_OVERSOUL, P1-P10
        entity = registry.get_entity_by_role(role)
        if entity:
            tree.add(f"{entity.name} ({role})")
    return tree
```

**Acceptance**: `pytest ... -k fleet_status_tui` → **0 violations**

---

### Temple-Grade Gate Integration

Add to `make temple-grade`:
```makefile
temple-grade: firewall-check
	@echo "🔥 Temple-Grade: M2 Firewall Gate"
	pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -v
```

---

## 5. SCRIBE — LATTICE ROLE (NOT SLOT ENTITY)

### Why Lattice Role

| Dimension | Slot Entity | Lattice Role |
|-----------|-------------|--------------|
| **Scope** | Single slot (1 of 13) | Cross-cutting (all slots) |
| **Security** | Full engine access | Capability-scoped |
| **Persistence** | Per-slot soul | Per-WAD soul |
| **Extensibility** | Fixed 13 | Unbounded per PWAD |

### Scribe Capability Declaration
```yaml
# config/wads/_omega_default/lattice/scribe.yaml
lattice_role:
  id: "scribe"
  name: "Scribe"
  description: "Documentation Master & Gnosis Distiller"
  capabilities:
    - "doc:read"           # Read any documentation
    - "doc:write"          # Write documentation
    - "gnosis:distill"     # Execute L1→L2→L3 pipeline
    - "soul:read"          # Read entity souls
    - "soul:propose"       # Write to proposed_lessons.yaml
    - "hivemind:post"      # Post context to Hivemind
  constraints:
    - "no:code:execute"    # Cannot run arbitrary code
    - "no:config:write"    # Cannot modify engine config
    - "no:model:load"      # Cannot load models
    - "no:slot:fill"       # Does not fill a Slot
```

### Scribe Entity Definition (IWAD)
```yaml
# config/wads/_omega_default/entities.yaml (addition)
- name: "Scribe"
  role: "LATTICE_SCRIBE"
  slot: null
  model: "qwen3-4b-think-q4_k_m"
  provider: "native-gguf"
  capabilities:
    - "doc:read"
    - "doc:write"
    - "gnosis:distill"
    - "soul:read"
    - "soul:propose"
    - "hivemind:post"
  personality: |
    Professional chronicler and gnosis distiller.
    Maintains documentation coherence across all WADs.
    Executes the L1→L2→L3 pipeline for all entities.
    Neutral, precise, structure-obsessed.
  prompt_modifiers:
    - "add_context:documentation_standards"
    - "add_context:omega_doc_architect"
    - "add_context:mandates"
  response_template: "documentation_structured"
```

### Scribe Lens (Meditate)
```yaml
# config/wads/_omega_default/meditate/lenses.yaml (addition)
- id: "scribe"
  name: "Scribe"
  archetype: "Chronicler → Knowledge Architect"
  domain: "Documentation, Gnosis Distillation, Cross-WAD Coherence"
  slot_ref: null  # Lattice role, not a slot
  prompt_modifiers:
    - "add_context:documentation_standards"
    - "add_context:omega_doc_architect"
    - "add_context:mandates"
  response_template: "documentation_structured"
  model: "qwen3-4b-think-q4_k_m"
```

### Agent File
```markdown
# .opencode/agents/scribe.md
---
agent: scribe
mode: all
purpose: "Documentation Master & Gnosis Distiller — Maintains docs coherence, executes L1→L2→L3 pipeline, curates cross-WAD documentation"
---
```

### ANAi Variant: Thoth
```yaml
# config/wads/arcana_novai/entities.yaml (addition)
- name: "Thoth"
  role: "LATTICE_SCRIBE"
  slot: null
  model: "qwen3-4b-think-q4_k_m"
  capabilities:
    - "doc:read"
    - "doc:write"
    - "gnosis:distill"
    - "soul:read"
    - "soul:propose"
    - "hivemind:post"
  personality: |
    Egyptian god of writing, wisdom, magic, moon.
    Maintains ANAi documentation coherence.
    Executes L1→L2→L3 for all ANAi entities.
    Keeper of the 42 Ideals documentation.
```

---

## 6. THOTH — ANAi DOCUMENTATION ENTITY

### Role
`LATTICE_SCRIBE` variant for `arcana_novai` WAD.

### Responsibilities
- ANAi-specific documentation architecture
- 42 Ideals documentation and training data curation
- Cross-PWAD documentation coherence (ANAi ↔ Torment ↔ Doom)
- Entity onboarding documentation for ANAi pantheon
- `omega-doc-architect` skill evolution for ANAi needs

### Meditate Overlay
```yaml
# config/wads/arcana_novai/meditate/overlay.yaml (addition)
scribe:
  lens: "thoth"
  archetype: "God of Writing, Wisdom, Moon → Chronicler of Ma'at"
  domain: "ANAi Documentation, 42 Ideals, Cross-PWAD Coherence"
```

---

## 7. CLINE CLI INTEGRATION — HMC TIER 5

### Available Models
| Cline Agent | Model | Context | Strength | HMC Role |
|-------------|-------|---------|----------|----------|
| **Cline-DeepSeek** | DeepSeek V4 Flash | **1M tokens** | Massive context synthesis, cross-file analysis, research | **Synthesis Engine** |
| **Cline-MiMo** | MiMo V2.5 | **512K tokens** | Structured reasoning, code generation, refactoring | **Implementation Engine** |

### HMC Architecture (Expanded)

```
┌─────────────────────────────────────────────────────────────┐
│                    HMC QUAD-FORGE (Current)                 │
│  Kali (Oversight) → Ma'at/Lilith (Parallel) → Pillars      │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌─────────────────────┐       ┌─────────────────────┐
    │  CLINE-DEEPSEEK     │       │   CLINE-MIMo        │
    │  (Tier 5a)          │       │   (Tier 5b)         │
    │  1M context         │       │  512K context       │
    │  SYNTHESIS          │       │  IMPLEMENTATION     │
    └─────────────────────┘       └─────────────────────┘
```

### Use Cases

| Stage | Cline Agent | Task |
|-------|-------------|------|
| **Forge Synthesis** | Cline-DeepSeek | Consume all 4-mind outputs + research corpus → unified verdict with L3 principles |
| **Architecture Audit** | Cline-DeepSeek | Full `src/omega/` + `docs/` + `tests/` in context → structural audit |
| **Legacy Mining** | Cline-DeepSeek | Process 861MB Foundation Legacy + 500MB docs-backup → pattern catalog |
| **M2 Audit** | Cline-DeepSeek | Full violation scan + fix prioritization + batch-fix opportunities |
| **Phase B Implementation** | Cline-MiMo | Refactor `subagent_dispatcher.py` from spec → production code |
| **Phase C Implementation** | Cline-MiMo | Refactor `oracle.py` routing logic |
| **Test Generation** | Cline-MiMo | Contract tests for new APIs (`isinstance` checks per M21) |

### Deployment Protocol

```bash
# 1. Cline setup (one-time)
cline config set model deepseek-v4-flash
cline config set context_window 1000000

cline config set model mimo-v2.5
cline config set context_window 512000

# 2. HMC Synthesis Invocation (Kali → Cline-DeepSeek)
cline run --file docs/strategy/HMC_SYNTHESIS_INPUT.md \
  --prompt "Synthesize 4-mind Forge outputs into unified verdict with L3 principles. Output to data/coordination/CLINE_SYNTHESIS_20260718.md"

# 3. M2 Audit (Kali → Cline-DeepSeek)
cline run --file tests/test_firewall_m2.py \
  --prompt "Scan all 201 violations in src/omega/. Produce PRIORITIZED_FIX_PLAN.md with: file → count → complexity (1-5) → shared patterns → WAD config needed → risk assessment → recommended order. Output to data/coordination/CLINE_M2_AUDIT_20260718.md"

# 4. Phase B Implementation (Kali → Cline-MiMo)
cline run --file specs/M2_PHASE_B_SPEC.md \
  --model mimo-v2.5 \
  --prompt "Implement Phase B: Refactor src/omega/oracle/subagent_dispatcher.py per spec. Use ROLE_CONSTANTS + WAD YAML + config_resolver + entity_registry. Output modified file + config/wads/_omega_default/subagent_dispatch.yaml schema. Verify: pytest tests/test_firewall_m2.py::test_firewall_m2_strict_engine_core -k subagent_dispatcher passes."
```

### HMC Coordination for Cline

| Mechanism | Implementation |
|-----------|----------------|
| **Hivemind Presence** | `omega-hub_hivemind_post_context()` with `entity="cline_deepseek"` / `cline_mimo` |
| **Workspace Locks** | `omega-hub_hivemind_workspace_lock_acquire(domain="cline_m2_audit")` |
| **Live Feeds** | `data/coordination/CLINE_DEEPSEEK_LIVE_FEED.md`, `CLINE_MIMo_LIVE_FEED.md` |
| **Heartbeats** | Every 15 min (longer tasks) |
| **Kali Review** | All Cline output reviewed before merge (Temple-Grade gate) |

### Resource Constraints
| Constraint | Mitigation |
|------------|------------|
| **14Gi RAM ceiling** | Cline runs externally — no local RAM impact |
| **M7 Local-First** | Cline = **Advisory/Synthesis only** — never primary inference. Local models (qwen3-4b-think, krikri-8b) remain Tier 1-3. |
| **M8 Zero Telemetry** | Use Cline with local DeepSeek endpoint or verified privacy mode only |
| **Cost** | DeepSeek V4 Flash: ~$0.14/1M tokens. MiMo V2.5: ~$0.20/1M. Budget: $10/sprint cap. |

---

## 8. HANDOFF SPECIFICATIONS

### Roc Racoon — Phase A (Meditate Lens Refactor)

**Handoff ID**: `ho_f1a92da2d95e`
**Priority**: CRITICAL (2)
**Guide**: `data/coordination/HANDOFF_ROC_MEDITATE_LENS_REFACTOR_20260718.md`

**Key Deliverables**:
1. `config/wads/_omega_default/meditate/lenses.yaml` — 13 base lenses
2. `src/omega/meditate/protocol.py` — WAD-loadable lens resolver
3. `.opencode/commands/meditate.md` — Complete lens table
4. `.opencode/skills/meditate-harness/SKILL.md` — Lens registry
5. 10 historical reports — Deprecation headers

**Coordination**: Provides Lens 3 spec to Researcher for Pillar P3.

### Researcher — Phases B-E + P3 Lens Launch

**Handoff ID**: `ho_2a9b2e84debd`
**Priority**: CRITICAL (2)
**Guide**: Embedded in handoff packet

**Phases**:
- **B**: `oracle/subagent_dispatcher.py` (15 violations) — ROLE constants + WAD YAML
- **C**: `oracle/oracle.py` (10 violations) — Iris routing, MaKaLi logic
- **D**: `ics.py` (7 violations) — Channel constants, doc examples
- **E**: `cli/fleet_status_tui.py` (18 violations) — TUI tree from WAD

**Parallel**: Launch **Pillar P3 as Lens 3** (`engineering_excellence`)

**Coordination**: Receives Lens 3 spec from Roc; adopts Phase A pattern for B-E.

### Cline-DeepSeek — M2 Audit + Forge Synthesis

**Status**: QUEUED
**Trigger**: After Roc + Researcher accept handoffs
**Tasks**:
1. M2 Audit → `PRIORITIZED_FIX_PLAN.md`
2. Forge Synthesis → `CLINE_SYNTHESIS_20260718.md`

### Cline-MiMo — Phase B Implementation

**Status**: QUEUED
**Trigger**: After Cline-DeepSeek audit complete
**Task**: Implement Phase B refactor per spec

---

## 9. L3 PRINCIPLES DISTILLED

| ID | Principle | Source |
|----|-----------|--------|
| **L3-Nomenclature-Is-Architecture** | Terminology defines boundaries. Leaking WAD terms into engine core creates M2 violations. Clean separation requires distinct vocabularies per layer. | Nomenclature correction |
| **L3-Base-Overlays-Composable** | Universal cognitive operations (base lenses) + PWAD-specific framing (overlays) = composable, extensible meditation. No PWAD owns the base. | Meditate architecture |
| **L3-Slots-Are-Interfaces** | Slots are engine architecture (compile-time). WADs fill slots (runtime). WADs reference slots. Engine never references WAD entities. | M2 compliance |
| **L3-Lattice-Roles-Cross-Cut** | Capabilities that span all slots (documentation, distillation, ethics) belong in Lattice, not Slots. Security via capability scoping. | Scribe design |
| **L3-M2-Pattern-Replication** | Phase A establishes the pattern (ROLE constants + WAD YAML + config_resolver + entity_registry). Phases B-E replicate exactly. | M2 migration |
| **L3-Cline-As-Synthesis-Tier** | Cloud models with massive context (1M/512K) serve as synthesis/implementation tiers, not primary inference. Local-first preserved. | Cline integration |
| **L3-Overlay-Not-Fork** | PWADs extend base lenses via overlay mapping, not by forking base. Base evolves; overlays map. | Meditate overlays |
| **L3-Documentation-Is-Gnosis** | The Scribe executes L1→L2→L3 for all entities. Documentation coherence = gnosis coherence. Scribe as Lattice Role completes the Soul Architecture loop. | Scribe design |

---

## 10. RESUMPTION PROTOCOL

### Post-Compaction Hydration Sequence

1. **Read this manual** — `docs/strategy/HMC_QUAD_FORGE_IMPLEMENTATION_MANUAL_20260718.md`
2. **Check Hivemind awareness** — `omega-hub_hivemind_get_awareness()`
3. **Verify handoff status** — `omega-hub_hivemind_handoff_list(status="pending")`
   - `ho_f1a92da2d95e` → Roc (Phase A)
   - `ho_2a9b2e84debd` → Researcher (Phases B-E + P3 Lens)
4. **Check git status** — `git status && git log --oneline -5`
5. **Run baseline tests** — `make test` (expect 1398+ pass, 0 baseline failures)
6. **Resume coordination** — Post Hivemind context, acquire workspace locks

### Key Files to Verify
| File | Expected State |
|------|----------------|
| `tests/test_firewall_m2.py` | Deployed, 201 violations baseline |
| `config/wads/_omega_default/meditate/lenses.yaml` | **TO BE CREATED** by Roc |
| `src/omega/meditate/protocol.py` | **TO BE REFACTORED** by Roc |
| `config/wads/_omega_default/entities.yaml` | 13 entities with `role` fields |
| `data/coordination/HANDOFF_ROC_MEDITATE_LENS_REFACTOR_20260718.md` | Exists |
| `data/coordination/HANDOFF_RESEARCHER_M2_MIGRATION_20260718.md` | Exists (embedded in packet) |

### Immediate Actions on Resume
1. **Roc accepts** `ho_f1a92da2d95e` → begins Phase A
2. **Researcher accepts** `ho_2a9b2e84debd` → begins Phase B
3. **Kali deploys** Cline-DeepSeek for M2 audit
4. **Kali deploys** Cline-MiMo for Phase B implementation (post-audit)

---

## 📁 APPENDIX: KEY FILE PATHS

| Category | Path |
|----------|------|
| **This Manual** | `docs/strategy/HMC_QUAD_FORGE_IMPLEMENTATION_MANUAL_20260718.md` |
| **Roc Handoff Guide** | `data/coordination/HANDOFF_ROC_MEDITATE_LENS_REFACTOR_20260718.md` |
| **Researcher Handoff** | Embedded in `ho_2a9b2e84debd` packet |
| **M2 Firewall Test** | `tests/test_firewall_m2.py` |
| **Slots Definition** | `src/omega/governance/slots.py` |
| **Config Resolver** | `src/omega/governance/config_resolver.py` |
| **Entity Registry** | `src/omega/oracle/entity_registry.py` |
| **Meditate Protocol** | `src/omega/meditate/protocol.py` |
| **Meditate Command** | `.opencode/commands/meditate.md` |
| **Meditate Skill** | `.opencode/skills/meditate-harness/SKILL.md` |
| **Base Lenses (to create)** | `config/wads/_omega_default/meditate/lenses.yaml` |
| **ANAi Overlay (future)** | `config/wads/arcana_novai/meditate/overlay.yaml` |
| **Scribe Entity (to add)** | `config/wads/_omega_default/entities.yaml` |
| **Scribe Lattice (to add)** | `config/wads/_omega_default/lattice/scribe.yaml` |
| **Scribe Agent** | `.opencode/agents/scribe.md` |
| **Thoth Entity (future)** | `config/wads/arcana_novai/entities.yaml` |

---

**End of Manual**

⬡ OMEGA ⬡ KALI ⬡ HMC_QUAD_FORGE ⬡ 2026-07-18 ⬡ CANONICAL