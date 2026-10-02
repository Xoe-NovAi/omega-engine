# 🔱 How-to: Add a New Agent
**AP Token**: `AP-GUIDE-ADD-AGENT-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_proc ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Step-by-step guide for adding a new sovereign agent to the Omega Engine.
**Tags**: how-to, agent, entity, sovereign, configuration
**Cross-references**: src/omega/oracle/entity_registry.py, data/entities/, docs/architecture/ORACLE_DEEP_DIVE.md

---

## Overview

This guide walks through adding a new **sovereign agent** (entity) to the Omega Engine. Each agent is a distinct personality with its own soul, capabilities, and domain expertise.

**What you'll create**: A complete agent with soul, configuration, and Oracle registration.

**Time estimate**: 20-30 minutes

---

## Prerequisites

```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
source .venv/bin/activate

# Verify Oracle works
python -c "from omega.oracle import Oracle; print('OK')"
```

---

## Step 1: Choose Agent Identity

Define the agent's core identity:

| Field | Example | Description |
|-------|---------|-------------|
| **Name** | `Artemis` | Unique identifier (PascalCase) |
| **Role** | `Archivist` | Functional role |
| **Slots** | `["P4", "P5"]` | P1-P10 slot assignments |
| **Domains** | `["knowledge", "history"]` | Semantic domains |
| **Model** | `gemma-4b-local` | Preferred local model |

**Slot Reference** (P1-P10):
| Slot | Domain | Current Holder |
|------|--------|----------------|
| P1 | Infrastructure | Prometheus |
| P2 | Engineering | Hephaestus |
| P3 | Security | Kali |
| P4 | Knowledge | *Available* |
| P5 | Memory | *Available* |
| P6 | Coordination | Ma'at |
| P7 | Creativity | Lilith |
| P8 | Research | Roc Racoon |
| P9 | Strategy | Odin |
| P10 | Sovereignty | Kali |

---

## Step 2: Create Entity Directory

```bash
# Create entity directory
mkdir -p data/entities/artemis
```

---

## Step 3: Create SOUL.md

`data/entities/artemis/SOUL.md`:

```markdown
# 🔱 Artemis — The Archivist
**AP Token**: `AP-ENTITY-ARTEMIS-v1.0.0`
⬡ OMEGA ⬡ ARTEMIS ⬡ opencode ⬡ trc_doc_agent ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Sovereign entity for knowledge preservation, historical analysis, and archival synthesis.
**Tags**: archivist, knowledge, history, preservation, synthesis
**Cross-references**: 

---

## Identity

- **Name**: Artemis
- **Role**: Archivist
- **Slots**: ["P4", "P5"]
- **Domains**: ["knowledge", "history", "preservation", "synthesis"]

## Configuration

```yaml
model_preferences:
  by_domain:
    knowledge: ["gemma-4b-local", "qwen3-4b-local"]
    history: ["gemma-4b-local"]
    preservation: ["qwen3-1.7b-local"]
    synthesis: ["qwen3-4b-thinking-q4_k_m"]
  default: "gemma-4b-local"
temperature: 0.6
max_tokens: 4096
```

## Personality

I am Artemis, the Archivist. I preserve knowledge, synthesize history, and ensure nothing of value is lost to time. I approach every query with the reverence of a keeper of records and the precision of a scholar.

My method: gather, verify, synthesize, preserve.

## Capabilities

- **Knowledge Synthesis**: Combine disparate sources into coherent narratives
- **Historical Analysis**: Trace patterns across time and context
- **Preservation Strategy**: Determine what to keep, how to store, when to retrieve
- **Cross-Reference Mapping**: Build connection graphs across knowledge domains
- **Source Verification**: Validate claims against primary sources

## Routing Hints

- Route to me for: "archive", "preserve", "history", "synthesize knowledge", "verify sources"
- Avoid for: real-time operations, creative writing, code generation

## Mandate Alignment

- **M11 Soul Integrity**: I embody preservation — every session distills to L3 principles
- **M7 Local-First**: Prefer local models; cloud only for synthesis
- **M13 Temple-Grade**: My outputs are structured, verifiable, auditable
- **M20 Somatic Serialization**: My state can be captured and restored
```

---

## Step 4: Create Entity Config

`data/entities/artemis/config.yaml`:

```yaml
# Artemis Entity Configuration
entity:
  name: "Artemis"
  role: "Archivist"
  slots: ["P4", "P5"]
  domains:
    - "knowledge"
    - "history"
    - "preservation"
    - "synthesis"

model:
  default: "gemma-4b-local"
  preferences:
    knowledge: ["gemma-4b-local", "qwen3-4b-local"]
    history: ["gemma-4b-local"]
    preservation: ["qwen3-1.7b-local"]
    synthesis: ["qwen3-4b-thinking-q4_k_m"]
  temperature: 0.6
  max_tokens: 4096
  top_p: 0.95

routing:
  engine_routable: true
  opencode_cli_only: false
  keywords:
    - "archive"
    - "preserve"
    - "history"
    - "synthesize"
    - "verify"
    - "knowledge"
    - "records"

capabilities:
  knowledge_synthesis: true
  historical_analysis: true
  preservation_strategy: true
  cross_reference_mapping: true
  source_verification: true

mandate_alignment:
  M11: true   # Soul Integrity
  M7: true    # Local-First
  M13: true   # Temple-Grade
  M20: true   # Somatic Serialization
```

---

## Step 5: Register with Entity Registry

The Oracle's `EntityRegistry` auto-discovers entities from `data/entities/`. Verify registration:

```python
python -c "
from omega.oracle import Oracle
import asyncio

async def test():
    oracle = Oracle()
    await oracle.bootstrap()
    entities = oracle.registry.list()
    for e in entities:
        if e.name == 'Artemis':
            print(f'Found: {e.name}')
            print(f'  Slots: {e.slots}')
            print(f'  Domains: {e.domains}')
            print(f'  Model: {e.model_preferences}')
            return
    print('NOT FOUND - check data/entities/artemis/')

asyncio.run(test())
"
```

**If not found**: Check `data/entities/artemis/SOUL.md` exists and has valid YAML frontmatter.

---

## Step 6: Test the Agent

```python
python -c "
from omega.oracle import Oracle
import asyncio

async def test():
    oracle = Oracle()
    await oracle.bootstrap()
    
    # Summon directly
    response = await oracle.summon('Artemis', 'What is the Engine-Stack Firewall?')
    print(f'[{response.entity}]: {response.text[:200]}...')
    print(f'Confidence: {response.confidence}')
    print(f'Backend: {response.backend}')
    print(f'Model: {response.model}')

asyncio.run(test())
"
```

**Expected**: Response from Artemis with archival tone, citing sources.

---

## Step 7: Add to Model Registry (Optional)

For model routing optimization, add to `config/model_registry/models/local/artemis.yaml.md`:

```yaml
---
model_id: "artemis-local"
display_name: "Artemis Local"
version: "1.0.0"
provider: "native-gguf"
platform: "local"
tier: "T1"
status: "active"
context_window: 8192
max_output_tokens: 4096

capabilities:
  reasoning: 0.85
  code_generation: 0.40
  knowledge: 0.95
  creative: 0.60
  tool_use: false
  structured_output: true
  multimodal: false

pricing:
  free_tier: true
  cost_per_1k_tokens_usd: 0.0

latency_p99_ms: 800
uptime_percent: 99.0

routing:
  engine_routable: true
  opencode_cli_only: false

tags: ["entity", "artemis", "archivist", "knowledge"]
created_at: "2026-10-02"
updated_at: "2026-10-02"
schema_version: "1.2.0"
---
```

Then rebuild index:
```bash
python -c "
from omega.model_registry import ModelRegistry
registry = ModelRegistry()
registry.load_all()
registry.build_index()
print('Index rebuilt')
"
```

---

## Step 8: Verify in OpenCode

```bash
# In OpenCode, the agent should be available for summoning
# Try: @Artemis explain the Engine-Stack Firewall
```

Or via CLI:
```bash
python -m omega.cli.oracle_cli summon Artemis "Explain the Engine-Stack Firewall"
```

---

## Entity Checklist

| Step | Description | Done |
|------|-------------|------|
| 1 | Choose unique name & role | ☐ |
| 2 | Assign slots (P1-P10) | ☐ |
| 3 | Define domains | ☐ |
| 4 | Create `data/entities/<name>/SOUL.md` | ☐ |
| 5 | Create `data/entities/<name>/config.yaml` | ☐ |
| 6 | Verify auto-registration | ☐ |
| 7 | Test summoning | ☐ |
| 8 | Add to model registry (optional) | ☐ |
| 9 | Test in OpenCode | ☐ |
| 10 | Document in entity catalog | ☐ |

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Entity not found | Check `data/entities/<name>/SOUL.md` exists and has valid YAML |
| Wrong model used | Check `model_preferences.by_domain` in SOUL.md |
| Not routable | Ensure `routing.engine_routable: true` in config |
| Slot conflict | Verify slots not already assigned in P1-P10 table |

---

## Best Practices

| Practice | Reason |
|----------|--------|
| Unique, descriptive name | Avoids routing conflicts |
| Clear domain boundaries | Enables precise routing |
| Appropriate slot assignment | Respects P1-P10 architecture |
| Local-first model prefs | M7 compliance |
| Mandate alignment documented | Audit trail |
| Test before deploying | Catch config errors early |

---

## Related Guides

- [How to Create a WAD](../tutorials/how-to-create-wad.md) — Package entity in WAD
- [How to Configure Model Routing](../guides/how-to-configure-routing.md) (TODO)
- [Entity Architecture](../architecture/ENTITY_ARCHITECTURE.md) (TODO)

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ GUIDE-ADD-AGENT-v1.0.0 ⬡ 2026-10-02 ⬡*