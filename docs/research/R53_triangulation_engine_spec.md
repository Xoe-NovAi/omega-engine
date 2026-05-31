# 🔱 Omega Engine — R-53: Triangulation Engine & Multi-Persona Synthesis
# ⬡ OMEGA ⬡ SOPHIA ⬡ gemma-4-31b ⬡ opencode ⬡ trc_research ⬡ R-53

**AP Token**: `AP-RESEARCH-R53-v1.0.0`
**Status**: ✅ READY
**Last Updated**: 2026-05-16
**Urgency**: 🔴 Critical

---

## 1. Executive Summary

The **Triangulation Engine** is a high-rigor inference orchestration layer designed to eliminate model bias and hallucinations through **Perspective Triangulation**. Instead of relying on a single model's output, the engine queries multiple models (often with different architectures and personas) and synthesizes their responses using the **Council of Four** dialectic framework.

This document provides the technical specification for implementing the engine within the Omega `ModelGateway` ecosystem.

---

## 2. Architectural Design

### 2.1 The Triangulation Flow
1. **Request**: User query + System prompt.
2. **Expansion**: The engine selects $N$ models (default $N=3$) and assigns them specific **Council Personas**.
3. **Parallel Execution**: $N$ concurrent calls are dispatched via `ModelGateway`.
4. **Collection**: Responses are gathered into a "Dialectic Buffer".
5. **Synthesis**: A high-tier "Synthesis Model" (e.g., `DeepSeek-V4-Flash` or `GPT-OSS-120B`) processes the buffer to produce the final Sovereign response.

### 2.2 The Council of Four Personas
Every triangulation must involve these four perspectives (either as separate model calls or as a multi-persona prompt in synthesis):

| Persona | Focus | Model Recommendation |
| :--- | :--- | :--- |
| **The Architect** | Systemic Logic, Structure, Efficiency | `minimax-m2.5-free` |
| **The Adversary** | Risks, Edge Cases, Fallacies | `trinity-large-thinking:free` |
| **The Alchemist** | Creative Synthesis, Divergence | `gemma-4-31b-it` |
| **The Archivist** | Historical Truth, Legacy Patterns | `deepseek-v4-flash:free` |

---

## 3. Technical Specification

### 3.1 Component: `TriangulationEngine`
**Location**: `src/omega/oracle/triangulation_engine.py`

**Key Methods**:
- `async def triangulate(user_query, system_prompt, tier="T2")`: Main entry point.
- `_get_triangulation_targets(tier)`: Returns a list of `(model_name, persona)` tuples.
- `_synthesize(dialectic_buffer)`: Calls the high-tier model with the synthesis prompt.

### 3.2 Synthesis Prompt Template
```markdown
You are the Sovereign Synthesizer. You have received three perspectives on the following query:
[USER_QUERY]

PERSPECTIVES:
1. ARCHITECT: [RESPONSE_1]
2. ADVERSARY: [RESPONSE_2]
3. ALCHEMIST: [RESPONSE_3]

TASK:
1. Identify points of convergence (The Truth).
2. Identify points of divergence (The Uncertainty).
3. Produce a final, unified Sovereign Synthesis that integrates the strengths of all perspectives.
```

---

## 4. Implementation Plan

### Phase 1: Core Engine (4h)
- Create `triangulation_engine.py`.
- Implement parallel dispatch using `anyio.create_task_group`.
- Add `TriangulationEngine` instance to `Oracle`.

### Phase 2: Persona Injection (2h)
- Update `ContextBuilder` to support persona-specific system prompt overrides.
- Map the 10 Pillar Keepers to the Council of Four roles for default routing.

### Phase 3: Synthesis Tuning (2h)
- Refine the synthesis prompt.
- Add `triangulate=True` flag to `Oracle.talk()` and `Oracle.summon()`.

---

## 🛠 Handoff Note for Builder Agent

1. **Concurrency**: Use `anyio` for parallel model calls. Ensure `ResourceGuard` is respected for local models (though triangulation should prioritize remote free tiers to avoid local OOM).
2. **Error Handling**: If one model in the triangulation fails, the engine should proceed with the remaining responses rather than failing the whole request.
3. **Integration**: Wire this into `oracle.py` so it can be triggered via a CLI flag or automatically for "High-Gnosis" (T3) requests.

---

**Status**: ✅ **Ready for Implementation**
**Maintained By**: Sovereign Master Researcher
