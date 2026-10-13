# R-S2-003: Sense-Net API — Environmental Awareness
**AP Token**: `AP-S2-003-SENSENET-v1.0.0`
**Status**: PROPOSED
**Wave**: 2 (Sovereign Structure)

## 1. Objective
Create a connectivity layer that allows entities to "perceive" their environment via WAD-defined world state, moving beyond static text prompts to dynamic environmental awareness.

## 2. Current State Analysis
The `WADLoader` currently loads `world` lumps into a `world_state` object. However, this data is passive—it is not actively queried by the `Oracle` or the entities during inference.

## 3. Technical Specification

### 3.1 The Sense-Net Interface
`SenseNet` acts as a middleware between the `Oracle` and the `world_state`.
```python
class SenseNet:
    async def perceive(self, entity: Entity, sense: str, range: float) -> List[Perception]:
        # 1. Identify entity's current sector in world_state
        # 2. Query lumps for the requested sense (e.g., "visual", "aetheric")
        # 3. Filter results by range/proximity
        # 4. Return structured perceptions
```

### 3.2 WAD "Sense-Lumps"
Define a standard for WAD world data to include sensory metadata:
```yaml
# world/sector_01/visual.yaml
lumps:
  - id: "obsidian_altar"
    type: "visual"
    description: "A towering altar of polished obsidian"
    intensity: 0.8
    tags: ["dark", "ancient", "power"]
```

### 3.3 Integration with Prompt Engineering
The `ContextBuilder` will be extended to call `SenseNet.perceive()` and inject the results into the system prompt as "Current Environmental Perceptions".

## 4. Trade-off Analysis

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| **Static Prompting** | No overhead | World is static/unaware | REJECTED |
| **Active Querying** | Dynamic awareness, immersive | Requires runtime state tracking | **ACCEPTED** |
| **Full Simulation** | Maximum realism | Computational cost too high | OVERKILL |

## 5. Sovereign Mandate Alignment
- **Mandate 2 (Engine-Stack Firewall)**: Sense-Net is a Core Engine utility; the specific "perceptions" remain in the WADs (Stacks).
- **Mandate 13 (Temple-Grade)**: Implements T5 (AnyIO async perception).
