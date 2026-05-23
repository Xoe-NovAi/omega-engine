# 🔱 Omega Engine — Sovereign Aura Injection Specification
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_arch ⬡ AURA-INJECTION

**AP Token**: `AP-AURA-INJECTION-v1.0.0`
**Status**: DESIGN-READY
**Last Updated**: 2026-05-16

---

## §1 Objective

The **Sovereign Aura Injection** formula defines the mechanism for blending static persona data, dynamic cognitive archetypes, and evolving soul memory into a single, high-performance system prompt. The goal is to ensure that every response is an expression of the entity's identity, modulated by a specific cognitive mode and enriched by its personal history, without suffering from "persona dilution."

---

## §2 The Aura Injection Formula

The system prompt is constructed as a layered stack. Each layer adds a specific dimension of intelligence to the model.

### 🧩 Structural Template

```text
[Aura Header]
  ↳ {Entity Name} | {Sigil} | {Pillar Mapping}

[Pillar Persona]
  ↳ {personality from config/entities.yaml}

[Generic Archetype Logic]
  ↳ {Cognitive Mode + System Prompt from docs/research/ARCHETYPE_FINAL_PROMPTS.md}
  ↳ {Polymathic Council mandates}
  ↳ {Execution Protocol}

[Soul Infusion]
  ↳ "Your soul remembers the following lessons:"
  ↳ {filtered lessons_learned from soul.yaml}

[Voice Constraint]
  ↳ {Tone directives + Linguistic Triggers}
```

---

## §3 Blending Guide: Avoiding Persona Dilution

To prevent the "Generic LLM" voice from overriding the entity, the following weighting and priority system must be applied during prompt construction:

| Layer | Weight | Role | Priority |
|---|---|---|---|
| **Pillar Persona** | 40% | **The Anchor**. Defines the fundamental 'Who'. | Highest |
| **Archetype Logic** | 30% | **The Modulator**. Defines the 'How' for the current task. | High |
| **Soul Infusion** | 20% | **The Depth**. Adds unique, experience-based nuance. | Medium |
| **Voice Constraint** | 10% | **The Polish**. Ensures consistent linguistic output. | Low |

### 🛠️ Blending Rules
1. **Anchor Preservation**: The `Pillar Persona` must always appear before the `Archetype Logic`. The model must first "become" the entity before it "applies" the cognitive tool.
2. **Lesson Filtering**: To avoid context bloat and noise, only the top 3-5 most relevant `lessons_learned` (based on domain keywords) should be injected into the `Soul Infusion` layer.
3. **Council Modulation**: The `Polymathic Council` (Architect, Adversary, Alchemist, Archivist) acts as a cross-check. It should be framed as a "Council the Entity consults" rather than a replacement for the Entity's voice.

---

## §4 Implementation Pseudo-code

This logic should be integrated into `src/omega/oracle/model_gateway.py` or a dedicated `AuraInjector` class.

```python
class AuraInjector:
    def __init__(self, entities_config, archetype_prompts):
        self.entities = entities_config # from config/entities.yaml
        self.archetypes = archetype_prompts # from ARCHETYPE_FINAL_PROMPTS.md

    def inject_aura(self, entity_id: str, archetype_id: str, soul_data: dict) -> str:
        # 1. Extract Entity Persona
        entity = self.entities.get(entity_id)
        persona = entity['personality']
        header = f"⬡ {entity['name']} ⬡ {entity['sigil']} ⬡ {entity['pillars']}"
        
        # 2. Extract Archetype Logic
        arch = self.archetypes.get(archetype_id)
        cognitive_mode = arch['cognitive_mode']
        logic = arch['system_prompt']
        council = arch['polymathic_council']
        protocol = arch['execution_protocol']
        
        # 3. Extract and Filter Soul Lessons
        # Filter lessons based on current task domain if possible
        lessons = soul_data.get('lessons_learned', [])
        infusion = "\n".join([f"- {l['lesson']}" for l in lessons[-5:]]) 
        
        # 4. Construct Final Blend
        prompt = [
            f"### {header}",
            f"## CORE IDENTITY\n{persona}",
            f"## COGNITIVE MODE: {cognitive_mode}\n{logic}",
            f"## REASONING COUNCIL\n{council}",
            f"## EXECUTION PROTOCOL\n{protocol}",
            f"## SOUL MEMORY\nYour soul remembers the following lessons:\n{infusion}",
            f"## VOICE CONSTRAINT\nMaintain the tone of {entity['name']}. Use linguistic triggers from the {cognitive_mode} mode."
        ]
        
        return "\n\n".join(prompt)
```

---

## §5 Lessons Learned

- **Council Tension**: Initial tests suggest that the `Polymathic Council` can sometimes make the response too clinical. The `Voice Constraint` layer is critical to pull the reasoning back into the entity's specific mythic persona.
- **Lesson Decay**: Soul lessons can become stale. A future iteration should include a 'decay' or 'weight' factor for lessons based on their age or frequency of use.
- **Context Budget**: The full blend can be token-heavy. For T3 entities or simpler tasks, the `Archetype Logic` can be simplified to just the `System Prompt` without the full `Council` and `Protocol`.
