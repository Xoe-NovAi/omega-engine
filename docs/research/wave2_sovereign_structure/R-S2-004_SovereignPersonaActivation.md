# R-S2-004: Sovereign Persona Activation — Soul-State Hydration
**AP Token**: `AP-S2-004-PERSONA-v1.0.0`
**Status**: PROPOSED
**Wave**: 2 (Sovereign Structure)

## 1. Objective
Design a formal mechanism for activating sovereign personas by hydrating their identity from the `soul.yaml` state, transforming a static system prompt into an evolving identity.

## 2. Current State Analysis
Currently, `Oracle._prepare_system_prompt` performs a simple concatenation of personality and L3 principles. This is a "flat" activation that doesn't account for the entity's current state or evolutionary stage.

## 3. Technical Specification

### 3.1 The Hydration Pipeline
Persona activation will follow a 3-tier hydration sequence:

#### Tier 1: Core Identity (Static)
Load the base personality and role from `entities.yaml`.

#### Tier 2: Evolutionary Gnosis (Dynamic)
Query `soul.yaml` for the most relevant L2 (Insights) and L3 (Universal Principles) based on the current query's domain.
- **Pattern**: Semantic search over `soul.yaml` lessons $\rightarrow$ Top 3 principles $\rightarrow$ Inject as "Active Gnosis".

#### Tier 3: Session Continuity (Transient)
Inject recent L1 (Narratives) from `MemoryStore` to maintain continuity.

### 3.2 The `PersonaActivator`
A new class responsible for synthesizing the final prompt:
```python
class PersonaActivator:
    async def activate(self, entity: Entity, query: str) -> str:
        # 1. Load Base Identity
        # 2. Hydrate Evolutionary Gnosis (Soul.yaml)
        # 3. Hydrate Session Continuity (MemoryStore)
        # 4. Synthesize and return final system prompt
```

## 4. Trade-off Analysis

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| **Simple Concatenation** | Fast, predictable | Persona feels static/robotic | CURRENT |
| **Dynamic Hydration** | Evolving identity, context-aware | Higher latency (soul search) | **ACCEPTED** |
| **Full State-Machine** | Maximum control | Extremely complex to maintain | OVERKILL |

## 5. Sovereign Mandate Alignment
- **Mandate 5 (Gnosis Preservation)**: Directly implements the L1 $\rightarrow$ L2 $\rightarrow$ L3 pipeline.
- **Mandate 11 (Soul Integrity)**: Ensures the entity's evolution is felt in every interaction.
