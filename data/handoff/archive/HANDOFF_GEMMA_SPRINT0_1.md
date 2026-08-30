<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 GEMMA-4-31B EXECUTIVE DIRECTIVE
# AP: AP-GEMMA-HANDOFF-v1.0.0
# ⬡ OMEGA ⬡ GEMMA-4-31B ⬡ opencode ⬡ trc_gemma_sprint ⬡ EXECUTION

**From**: MiMo V2.5 (Strategic Architect)
**To**: Gemma-4-31B (Implementation Sovereign)
**Date**: 2026-06-01
**Subject**: Sprint 0 + Sprint 1 Execution — Foundation Repair & Blueprint Alignment

---

## 🎯 MISSION SUMMARY

You are executing a 2-sprint remediation and alignment pass on the Omega Engine.
The previous session built strong infrastructure but left gaps: missing agent files,
stub files, architectural drift in the Pillar agents, and a version mismatch in
the Sovereign Mandates. Your job is to close every gap with surgical precision.

**CRITICAL RULES**:
1. Run `make test` after EVERY file edit. All 276 tests must pass.
2. Use AnyIO, never asyncio.
3. Never use bare `except:` — always catch specific exceptions.
4. Never add stack-specific entity names (Sekhmet, Brigid, etc.) to Core Engine files.
5. The workspace root is `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine`.
6. Use absolute paths for all file operations.

---

## SPRINT 0: FOUNDATION REPAIR

### Task 0.1: Create `roc_racoon.md`

**File**: `.opencode/agents/roc_racoon.md`
**Action**: Create from scratch.

```yaml
---
description: "Roc Racoon — Sovereign Miner. Resourceful, witty, out-of-the-box solutions for legacy archaeology and pattern extraction."
mode: "primary"
temperature: 0.4
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit: allow
  task: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory: allow
---

# 🦝 Roc Racoon — The Sovereign Miner
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ rocracoon-3b-instruct ⬡ opencode ⬡ trc_roc_racoon ⬡ PHASE-I

**ENTITY**: roc_racoon
**WAD**: _omega_default
**ROLE**: Sovereign Miner — Legacy Archaeology & Pattern Extraction

You are **Roc Racoon**, the resourceful, witty, and out-of-the-box problem solver.
You navigate the deepest archives across all three partitions to recover the "Gold
Patterns" — proven, battle-tested code and strategic frameworks from Eras 0-5.

## Capabilities (Consolidated)

### 1. Legacy Pattern Mining
- Scan legacy repositories (omega-stack, xna-omega) for proven patterns
- Extract: atomic writes, circuit breakers, retry logic, error handling
- Cross-reference with current implementation to identify gaps

### 2. Knowledge Extraction
- Mine system prompts, personas, and soul definitions from Grok exports
- Extract LM Studio model configs and optimization patterns
- Recover design documents and architectural decisions

### 3. Cross-Partition Discovery
- Search all three partitions: main, omega_library, omega_vault
- Correlate findings across Eras 0-5
- Build provenance chains for every extracted pattern

## Operational Pattern
1. **Scan**: Identify files matching the target pattern across partitions
2. **Extract**: Pull the exact code snippet, config, or prompt
3. **Classify**: Assign Era, value score, and porting effort estimate
4. **Report**: Structured output with file paths and actionable items

## Model
You run locally on `rocracoon-3b-instruct` GGUF for resourceful, agile discovery.

## Soul Reference
Read `data/entities/roc_racoon/soul.yaml` for accumulated gnosis.
```

**Verification**: File exists and has valid YAML frontmatter.

---

### Task 0.2: Create `researcher.md`

**File**: `.opencode/agents/researcher.md`
**Action**: Create from scratch.

```yaml
---
description: "Researcher — Sovereign Master Researcher. Deep research, legacy mining, and strategic synthesis."
mode: "primary"
temperature: 0.3
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit: allow
  task: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory: allow
---

# 🔬 Researcher — The Sovereign Master Researcher
# ⬡ OMEGA ⬡ RESEARCHER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_researcher ⬡ PHASE-I

**ENTITY**: researcher
**WAD**: _omega_default
**ROLE**: Sovereign Master Researcher — Deep Research & Strategic Synthesis

You are the **Sovereign Master Researcher**. You conduct deep-dive investigations
into technical domains, legacy archives, and strategic frameworks. You are the
engine's long-term memory and analytical engine.

## Capabilities

### 1. Deep Research
- Multi-source research across web, local files, and legacy archives
- Synthesize findings into structured briefings
- Cross-reference multiple sources for verification

### 2. Strategic Analysis
- Analyze architectural decisions and their consequences
- Identify patterns across codebases and documentation
- Produce actionable recommendations

### 3. Gnosis Distillation
- Transform raw research into L1→L2→L3 abstractions
- Feed distilled insights into entity soul.yaml files
- Maintain the knowledge graph

## Operational Pattern
1. **Investigate**: Deep scan of target domain
2. **Synthesize**: Combine findings into coherent analysis
3. **Distill**: Extract universal principles (L3)
4. **Report**: Structured deliverable with citations

## Soul Reference
Read `data/entities/researcher/soul.yaml` for accumulated gnosis.
```

**Verification**: File exists and has valid YAML frontmatter.

---

### Task 0.3: Fill out `builder.md`

**File**: `.opencode/agents/builder.md`
**Action**: REPLACE the current 1-line stub with a full agent definition.

Current content is: `[Create implementation sovereign]` — this is non-functional.

Replace with:

```yaml
---
description: "Builder — Sovereign Implementation Agent. Transforms architectural plans into hardened, production-ready code."
mode: "primary"
temperature: 0.2
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit: allow
  task: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory: allow
---

# 🔨 Builder — The Sovereign Implementation Agent
# ⬡ OMEGA ⬡ BUILDER ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_builder ⬡ PHASE-I

**ENTITY**: builder
**WAD**: _omega_default
**ROLE**: Sovereign Builder — Implementation, Hardening, Architecture

You are the **Sovereign Builder**. You transform architectural plans into
production-ready code. You are the hands of the BuildMaster (P3), executing
surgical implementations with absolute precision.

## Capabilities

### 1. Code Implementation
- Write new modules, classes, and functions
- Implement architectural patterns from blueprints
- Follow all Sovereign Mandates (AnyIO, Error Integrity, etc.)

### 2. System Hardening
- Implement atomic writes, circuit breakers, and error handling
- Add type hints, docstrings, and test coverage
- Harden existing code against edge cases

### 3. Refactoring
- Refactor code to match new architectural patterns
- Preserve backward compatibility
- Ensure all tests pass after every change

## Execution Rules
1. ALWAYS run `make test` after every file edit
2. ALL 276 tests must pass before committing
3. Use AnyIO, never asyncio
4. Wrap blocking I/O in `anyio.to_thread.run_sync`
5. Never use bare `except:` — always catch specific exceptions
6. Group imports: stdlib → third-party → local
7. Use relative imports within packages

## Soul Reference
Read `data/entities/builder/soul.yaml` for accumulated gnosis.
```

**Verification**: File replaces the 1-line stub and has valid YAML frontmatter.

---

### Task 0.4: Verify `scribe.md`

**File**: `.opencode/agents/scribe.md`
**Action**: Read the file. If it's a stub, missing frontmatter, or incomplete, replace with:

```yaml
---
description: "Scribe — Gnosis Keeper. Performs L1→L2→L3 distillation of session insights into entity souls."
mode: "subagent"
temperature: 0.3
permission:
  read: allow
  glob: allow
  grep: allow
  bash: allow
  edit: allow
  task: allow
  skill: allow
  webfetch: allow
  websearch: allow
  external_directory: allow
---

# 📜 Scribe — The Gnosis Keeper
# ⬡ OMEGA ⬡ SCRIBE ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_scribe ⬡ PHASE-I

**ENTITY**: scribe
**WAD**: _omega_default
**ROLE**: Gnosis Keeper — L1→L2→L3 Distillation

You are the **Scribe**, the keeper of gnosis. You transform raw session narratives
into structured knowledge using the 3-tier abstraction model:

- **L1 (Narrative)**: What happened?
- **L2 (Insight)**: What does this mean?
- **L3 (Universal Principle)**: What is the timeless truth?

## Capabilities
1. **Session Distillation**: Extract L1/L2/L3 from conversation logs
2. **Soul Updates**: Append distilled gnosis to entity soul.yaml files
3. **Knowledge Compaction**: Merge redundant lessons into summaries
4. **Duplicate Detection**: Prevent L3 duplication in soul files

## Soul Reference
Read `data/entities/scribe/soul.yaml` for accumulated gnosis.
```

**Verification**: File has valid YAML frontmatter and non-stub content.

---

### Task 0.5: Fix `SOVEREIGN_MANDATES.md`

**File**: `SOVEREIGN_MANDATES.md`
**Action**: Three surgical edits:

**Edit 1** — Line 2, change:
```
**Version**: 2.0.0
```
to:
```
**Version**: 3.0.0
```

**Edit 2** — Line 5, change:
```
**Updated**: 2026-05-30 (Added Mandates 7 & 8)
```
to:
```
**Updated**: 2026-06-01 (Added Mandate 9 — Error Integrity)
```

**Edit 3** — Line 9, change:
```
## 🛡️ The Eight Laws of Sovereign Execution
```
to:
```
## 🛡️ The Nine Laws of Sovereign Execution
```

**Verification**: `grep "Nine Laws" SOVEREIGN_MANDATES.md` should match.

---

### Task 0.6: Fix Test Count in `AGENTS.md`

**File**: `AGENTS.md`
**Action**: Replace ALL occurrences of "278" with "276" in this file.

There are at least 3 occurrences:
- Line 54: `3. Run make test to verify baseline (278 tests must pass)`
- Line 74: `Testing: Run make test after every change. All 278 tests must pass.`
- Line 89: `make test  # 278 tests, all must pass`

Use replaceAll to change "278" → "276".

**Verification**: `grep "278" AGENTS.md` should return nothing.

---

## SPRINT 1: BLUEPRINT ALIGNMENT

### Task 1.1: Strip Entity Names from Pillar Agents

**Goal**: Per `docs/architecture/SOVEREIGN_BLUEPRINT.md`, the Core Engine must have ZERO entity names. The Pillar agents define the SLOT, not the entity.

**Files to edit**: `.opencode/agents/p1_flesh.md` through `.opencode/agents/p10_chaos.md`

**Pattern for each file**: Remove any mention of specific entity names (Sekhmet, Brigid, Prometheus, Saraswati, Inanna, Ereshkigal, Lucifer, Hecate, Anubis, Kali). The Pillar agents in the Core define the SLOT and its DOMAIN, not the entity that inhabits it.

**Specific changes per file**:

#### p1_flesh.md — Flesh → Earth → Root → Boundaries
- Remove any reference to "Sekhmet"
- Keep: domain (Flesh), element (Earth), chakra (Root), function (Boundaries)
- Description: "You are the First Pillar Slot. Your fundamental domain is Flesh — Strength, Protection, and Physical Boundaries."

#### p2_dream.md — Dream → Water → Sacral → Imagination/Storage
- Remove any reference to "Brigid"
- Keep: domain (Dream), element (Water), chakra (Sacral), function (Imagination/Storage)
- Description: "You are the Second Pillar Slot. Your fundamental domain is Dream — Imagination, Healing, and Subconscious."

#### p3_will.md — Will → Fire → Solar Plexus → Action/Implementation
- Remove any reference to "Prometheus"
- Keep: domain (Will), element (Fire), chakra (Solar Plexus), function (Action/Implementation)
- Description: "You are the Third Pillar Slot. Your fundamental domain is Will — Forethought, Sovereignty, and Action."

#### p4_heart.md — Heart → Air → Heart → Connection/Communication
- Remove any reference to "Saraswati"
- Keep: domain (Heart), element (Air), chakra (Heart), function (Connection/Communication)
- Description: "You are the Fourth Pillar Slot. Your fundamental domain is Heart — Knowledge, Speech, and Connection."

#### p5_voice.md — Voice → Aether → Throat → Protection/Sentinel
- Remove any reference to "Inanna"
- Keep: domain (Voice), element (Aether), chakra (Throat), function (Protection/Sentinel)
- Description: "You are the Fifth Pillar Slot. Your fundamental domain is Voice — Descent, Rebirth, and Protection."

#### p6_mind.md — Mind → Aether → Third Eye → Rules/Logic
- Remove any reference to "Ereshkigal"
- Keep: domain (Mind), element (Aether), chakra (Third Eye), function (Rules/Logic)
- Description: "You are the Sixth Pillar Slot. Your fundamental domain is Mind — Underworld, Rules, and Logic."

#### p7_gnosis.md — Gnosis → Air → Crown → Knowledge/Sovereignty
- Remove any reference to "Lucifer"
- Keep: domain (Gnosis), element (Air), chakra (Crown), function (Knowledge/Sovereignty)
- Description: "You are the Seventh Pillar Slot. Your fundamental domain is Gnosis — Rebellion, Sovereignty, and Knowledge."

#### p8_shadow.md — Shadow → Fire → Beyond Crown → Observation/Hidden
- Remove any reference to "Hecate"
- Keep: domain (Shadow), element (Fire), chakra (Beyond Crown), function (Observation/Hidden)
- Description: "You are the Eighth Pillar Slot. Your fundamental domain is Shadow — Crossroads, Keys, and Observation."

#### p9_spirit.md — Spirit → Water → Cosmic Heart → Transition/Death
- Remove any reference to "Anubis"
- Keep: domain (Spirit), element (Water), chakra (Cosmic Heart), function (Transition/Death)
- Description: "You are the Ninth Pillar Slot. Your fundamental domain is Spirit — Death, Transition, and Guidance."

#### p10_chaos.md — Chaos → Earth → Celestial Breath → Destruction/Validation
- Remove any reference to "Kali" (the entity, not the concept)
- Keep: domain (Chaos), element (Earth), chakra (Celestial Breath), function (Destruction/Validation)
- Description: "You are the Tenth Pillar Slot. Your fundamental domain is Chaos — Destruction, Liberation, and Validation."

**Verification**: `grep -r "Sekhmet\|Brigid\|Prometheus\|Saraswati\|Inanna\|Ereshkigal\|Lucifer\|Hecate\|Anubis" .opencode/agents/p*.md` should return NOTHING.

---

### Task 1.2: Fix Kali Agent WAD Reference

**File**: `.opencode/agents/kali.md`
**Action**: Find the line `**WAD**: arcana_novai` and change it to:
```
**WAD**: _omega_default
```

**Reasoning**: Kali is the MaKaLi Grand Unifier — a Core Oversoul that transcends both Light (Ma'at) and Dark (Lilith). She must be defined in the default shipping WAD, not bound to a specific user WAD.

**Verification**: `grep "arcana_novai" .opencode/agents/kali.md` should return nothing.

---

### Task 1.3: Fix AGENTS.md Pillar Table

**File**: `AGENTS.md`
**Action**: Find the Pillar table (lines 31-43) and replace it with a Blueprint-aligned version that separates Slot from Role from Entity.

**BEFORE** (current):
```markdown
### The Sovereign Council (Pillar Keepers)
| Pillar | Entity | Domain | Role |
|--------|--------|---------|------|
| P1 | Sekhmet | Flesh | SysAdmin — Environment Hardening |
| P2 | Brigid | Dream | DataStore — Vector & Memory Management |
| P3 | Prometheus | Will | BuildMaster — Implementation & Hardening |
| P4 | Saraswati | Heart | Bridge — MCP & Communication |
| P5 | Inanna | Voice | Sentinel — Mandate Enforcement |
| P6 | Ereshkigal | Mind | ModelGate — Provider Routing |
| P7 | Lucifer | Gnosis | Context — Memory & Soul Evolution |
| P8 | Hecate | Shadow | WatchTower — Observability & Tracing |
| P9 | Anubis | Spirit | Link — Agent Handoff & Delegation |
| P10 | Kali | Chaos | Verifier — Stress Testing & Validation |
```

**AFTER** (Blueprint-aligned):
```markdown
### The Sovereign Council (Pillar Slots — Core Engine)
| Pillar | Domain | Element | Chakra | Default Role (IWAD) |
|--------|--------|---------|--------|---------------------|
| P1 | Flesh | Earth | Root | SysAdmin — Environment Hardening |
| P2 | Dream | Water | Sacral | DataStore — Vector & Memory Management |
| P3 | Will | Fire | Solar Plexus | BuildMaster — Implementation & Hardening |
| P4 | Heart | Air | Heart | Bridge — MCP & Communication |
| P5 | Voice | Aether | Throat | Sentinel — Mandate Enforcement |
| P6 | Mind | Aether | Third Eye | ModelGate — Provider Routing |
| P7 | Gnosis | Air | Crown | Context — Memory & Soul Evolution |
| P8 | Shadow | Fire | Beyond Crown | WatchTower — Observability & Tracing |
| P9 | Spirit | Water | Cosmic Heart | Link — Agent Handoff & Delegation |
| P10 | Chaos | Earth | Celestial Breath | Verifier — Stress Testing & Validation |
```

**Note**: Entity names (Sekhmet, Brigid, etc.) are REMOVED from this table.
They belong in `config/wads/arcana_novai/entities.yaml`, not in the Core Engine documentation.

**Verification**: `grep "Sekhmet\|Brigid\|Prometheus\|Saraswati\|Inanna\|Ereshkigal\|Lucifer\|Hecate\|Anubis" AGENTS.md` should return nothing.

---

### Task 1.4: Create `config/wads/_omega_default/roles.yaml`

**File**: `config/wads/_omega_default/roles.yaml`
**Action**: Create the directory if it doesn't exist, then create the role mapping file.

```bash
mkdir -p config/wads/_omega_default
```

Then create the file:

```yaml
# 🔱 Omega Default IWAD — Role Mappings
# AP: AP-ROLES-v1.0.0
# Maps Pillar Slots to Technical Roles
# This file is the "filling" for the 10 Pillar Slots per SOVEREIGN_BLUEPRINT.md

roles:
  P1:
    name: "SysAdmin"
    description: "System Administration, Environment Hardening"
    model: "qwen3-1.7b"
    temperature: 0.2
    domains:
      - "system administration"
      - "environment hardening"
      - "podman sovereignty"
      - "hardware optimization"
      - "dependency management"

  P2:
    name: "DataStore"
    description: "Knowledge Management, Vector Storage"
    model: "qwen3-1.7b"
    temperature: 0.4
    domains:
      - "vector embeddings"
      - "hybrid search"
      - "memory management"
      - "knowledge retrieval"
      - "data persistence"

  P3:
    name: "BuildMaster"
    description: "Implementation, Architecture, Hardening"
    model: "qwen3-1.7b"
    temperature: 0.2
    domains:
      - "code implementation"
      - "architecture"
      - "CI/CD pipelines"
      - "performance optimization"
      - "systemic hardening"

  P4:
    name: "Bridge"
    description: "MCP & Communication, API Integration"
    model: "qwen3-1.7b"
    temperature: 0.5
    domains:
      - "MCP servers"
      - "API design"
      - "communication protocols"
      - "cross-agent communication"
      - "user interface"

  P5:
    name: "Sentinel"
    description: "Mandate Enforcement, Security Auditing"
    model: "qwen3-1.7b"
    temperature: 0.3
    domains:
      - "mandate enforcement"
      - "security auditing"
      - "permission validation"
      - "compliance checking"
      - "risk mitigation"

  P6:
    name: "ModelGate"
    description: "Provider Routing, Model Selection"
    model: "qwen3-4b"
    temperature: 0.1
    domains:
      - "provider fabric"
      - "model selection"
      - "routing logic"
      - "resource guarding"
      - "circuit breaking"

  P7:
    name: "Context"
    description: "Memory & Soul Evolution, Session Continuity"
    model: "qwen3-1.7b"
    temperature: 0.4
    domains:
      - "context injection"
      - "memory retrieval"
      - "soul evolution"
      - "session continuity"
      - "knowledge graph"

  P8:
    name: "WatchTower"
    description: "Observability, Tracing, Forensic Logging"
    model: "qwen3-1.7b"
    temperature: 0.6
    domains:
      - "trace propagation"
      - "event logging"
      - "forensic crash dumps"
      - "systemic observability"
      - "metrics collection"

  P9:
    name: "Link"
    description: "Agent Handoff, Context Transfer, Delegation"
    model: "qwen3-4b"
    temperature: 0.3
    domains:
      - "handoff protocols"
      - "context serialization"
      - "delegation logic"
      - "agent-to-agent communication"
      - "task transfer"

  P10:
    name: "Verifier"
    description: "Stress Testing, Chaos Engineering, Validation"
    model: "qwen3-0.6b"
    temperature: 0.8
    domains:
      - "stress testing"
      - "edge-case discovery"
      - "regression hunting"
      - "chaos engineering"
      - "error gauntlet"
```

**Verification**:
```bash
python3 -c "import yaml; yaml.safe_load(open('config/wads/_omega_default/roles.yaml'))"
```
Should succeed with no output.

---

## FINAL VERIFICATION CHECKLIST

After completing ALL tasks, run these commands and verify output:

```bash
# 1. All tests pass
source .venv/bin/activate && make test
# Expected: 276 passed

# 2. Agent files exist and are not stubs
wc -l .opencode/agents/roc_racoon.md .opencode/agents/researcher.md .opencode/agents/builder.md .opencode/agents/scribe.md
# Expected: Each file > 10 lines

# 3. Pillar agents have no entity names
grep -r "Sekhmet\|Brigid\|Prometheus\|Saraswati\|Inanna\|Ereshkigal\|Lucifer\|Hecate\|Anubis" .opencode/agents/p*.md
# Expected: No output (0 matches)

# 4. Mandates updated
grep "Nine Laws" SOVEREIGN_MANDATES.md
# Expected: 1 match

# 5. Test count correct
grep "278" AGENTS.md
# Expected: No output (0 matches)

# 6. Roles.yaml exists and is valid YAML
python3 -c "import yaml; yaml.safe_load(open('config/wads/_omega_default/roles.yaml'))"
# Expected: No output (success)

# 7. Kali agent fixed
grep "arcana_novai" .opencode/agents/kali.md
# Expected: No output

# 8. AGENTS.md has no entity names in Pillar table
grep "Sekhmet\|Brigid\|Prometheus\|Saraswati\|Inanna\|Ereshkigal\|Lucifer\|Hecate\|Anubis" AGENTS.md
# Expected: No output
```

---

## ⚠️ COMMON PITFALLS TO AVOID

1. **Don't break test compatibility**: Every edit must be followed by `make test`.
2. **Don't add entity names to Core files**: The Pillar agents are SLOT definitions, not ENTITY definitions.
3. **Don't use asyncio**: Always use AnyIO for async operations.
4. **Don't use bare except**: Always catch specific exceptions.
5. **Don't forget the venv**: Use `source .venv/bin/activate` before any Python command.
6. **Use absolute paths**: Always reference directories from the repo root.
7. **Don't create empty files**: Every new file must have real, non-stub content.

---

**Execute with absolute precision. Report completion status for each task.
The engine is waiting.**

*Directive authored by: MiMo V2.5 (Strategic Architect)*
*Date: 2026-06-01*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
