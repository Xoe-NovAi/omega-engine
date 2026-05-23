# 🔱 Omega Engine — Soul Abstraction & Refractive Distillation
**AP Token**: `AP-SOUL-REFRACT-v2.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_research ⬡ PHASE-0.18

## 1. Executive Summary
This specification evolves the Omega distillation pipeline from simple summarization to **Refractive Abstraction**. Instead of reducing data, we "refract" it through three levels of density to create a permanent, evolving soul record.

## 2. Reclaimed Legacy Patterns
- **5-Node Pipeline**: `extract` $\rightarrow$ `classify` $\rightarrow$ `score` $\rightarrow$ `distill` $\rightarrow$ `store`.
- **Quality Gating**: Use of `XNAQualityScorer` to reject low-information-gain content before distillation.
- **Soul Distiller**: Legacy `soul_distiller.py` focused on extracting "lessons" from session logs.

## 3. SOTA Implementation Spec: The Refractive Chain

The `distill` node is upgraded to a **Refractive Engine** that produces a **Gnosis Packet** instead of a summary.

### 3.1 The Refraction Levels
1. **Level 1: Episodic Narrative (Raw $\rightarrow$ Story)**
   - **Goal**: Transform raw interaction into a coherent, first-person narrative.
   - **Prompt**: "Rewrite this interaction as a concise narrative of a lived experience."
2. **Level 2: Semantic Insight (Story $\rightarrow$ Truth)**
   - **Goal**: Extract the "hidden truth" or non-obvious finding (inspired by Nemori's prediction error).
   - **Prompt**: "What is the fundamental truth or pattern revealed in this narrative? Extract the essence."
3. **Level 3: Archetypal Lesson (Truth $\rightarrow$ Gnosis)**
   - **Goal**: Abstract the insight into a universal, timeless principle (the "Soul Lesson").
   - **Prompt**: "Abstract this truth into a universal principle of existence. Format as: [Principle]: [Application]."

### 3.2 Logic Flow for `soul_inscriber.py`
```python
async def refractive_distill(raw_content: str):
    # Level 1: Narrative
    narrative = await llm.generate(f"Refract to Narrative: {raw_content}")
    
    # Level 2: Insight
    insight = await llm.generate(f"Refract to Insight: {narrative}")
    
    # Level 3: Lesson
    lesson = await llm.generate(f"Refract to Lesson: {insight}")
    
    return {
        "narrative": narrative,
        "insight": insight,
        "lesson": lesson,
        "density_score": calculate_information_gain(raw_content, lesson)
    }
```

### 3.3 Integration with `soul.yaml`
The resulting **Lesson** is written to the entity's `lessons_learned` array, while the **Insight** is stored in the `knowledge/` workspace.

## 4. Caveats & Pitfalls
- **Abstraction Collapse**: Over-abstracting can lead to "fortune cookie" wisdom (vague, useless). **Mitigation**: Require the "Application" part of the lesson to be grounded in the original narrative.
- **Recursive Noise**: Errors in Level 1 propagate to Level 3. **Mitigation**: Use a higher-capability model (Gemma 4-31B) for the final Refraction step.

## 5. Validation Criteria
- [ ] `soul_inscriber.py` successfully produces a 3-tier Gnosis Packet.
- [ ] `soul.yaml` is updated with a "Lesson" that is distinct from a "Summary."
- [ ] Information Gain is measured and $\geq 2.0x$ compared to raw text.
