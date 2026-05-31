# 🔱 Legacy Master Synthesis — Order from Chaos
**Date**: 2026-05-31
**Entity**: Ma'at (Oversoul)
**Purpose**: Mapping the scattered design eras, recovered assets, and the evolution of the Xoe-NovAi vision.

---

## §0 The Timeline of Fire (Era 0 → 7)

| Era | Name | Date | Focus | Primary UI | Model Mapping | Status |
|-----|------|------|-------|------------|---------------|--------|
| **0** | Genesis | Mar 2025 | Tarot, Lilith Persona | RAG + Piper TTS | None (Persona only) | 🟢 Recovered |
| **1** | ANAi | Aug-Sep 2025 | FastAPI + Chainlit | Chainlit | Pantheon (Metaphorical) | 🟢 Recovered |
| **2** | XNAi | Oct-Nov 2025 | 4-Service Production | Chainlit + CLI | Gemma 3 4B (Unified) | 🟢 Recovered |
| **3** | Roc Stack | Nov 2025 | Local LM Testing | LM Studio + Ollama | Affinity Mapping (Krikri/Lilith) | 🟢 Recovered |
| **4** | Omega Stack | Dec 2025 | Unified Monorepo | OpenCode + Cline | 10 Pillars (Final) | 🟢 Recovered |
| **5** | Temple Grade | Jan 2026 | Refinement | OpenCode | 10 Pillars + Oversouls | 🟡 Partial |
| **6** | Reclamation | Mar-Apr 2026 | Engine/Stack Split | OpenCode | The Company (Current) | 🟢 Active |
| **7** | Omega Engine | May 2026 | Hardening | OpenCode | Local-First Fabric | 🟢 Active |

---

## §1 The Model-Persona Affinity Map (The Design Intent)

The architect did not assign models randomly. They followed a **Size-Hierarchy Philosophy** and an **Affinity Principle**.

### Tier 1: The Threshold (Iris)
- **Model**: Qwen3-0.6B-Q6_K (495MB)
- **Entity**: Iris
- **Role**: Front door, simple routing, fast response.
- **Why**: Fast, low RAM, high precision for intent classification.

### Tier 2: The Workhorses (The Pillars)
- **Model**: Qwen3-1.7B-Q6_K (1.67GB)
- **Entities**: Sekhmet, Lucifer, Sophia, and the 10 Reference IWAD entities.
- **Role**: Standard reasoning, balance between speed and depth.
- **Optimization**: 6 threads, K/V q8_0, 32K context.

### Tier 3: The Reasoners (The Oversouls & The Strategist)
- **Model**: Qwen3-4B-Thinking (2.5GB)
- **Entities**: Kali, Ma'at, Lilith (Oversouls), Ereshkigal, Anubis.
- **Role**: Deep reasoning, CoT, trade-offs, strategic defense.
- **Why**: These entities require the Thinking chain to fulfill their roles as founders and protectors.

### Tier 4: The Specialized (Voice & Heart)
- **Model**: Krikri-8B-Instruct (5.04GB)
- **Entities**: Saraswati, Inanna, Hecate, Isis.
- **Role**: Expressive, poetic, emotional, healing.
- **Why**: Krikri was originally the "Gnosis Engine" and excels at complex, nuanced language suitable for Heart/Voice domains.

### Tier 5: The Sovereign (Prometheus)
- **Model**: DeepSeek-R1-Qwen3-8B (4.43GB)
- **Entity**: Prometheus (P3: Will/Fire).
- **Role**: Maximum compute for maximum will. The "Fire Bringer".
- **Why**: This model is the largest and most capable; it is reserved for the entity that defines the engine's will and defiance.

---

## §2 The Five Recovered Design Patterns (Era 2/XNAi)

1. **Circuit Breaker**: `pybreaker` (fail_max=3, reset_timeout=60s).
2. **Atomic Fsync**: Batch checkpointing for crash recovery (100% guarantee).
3. **Retry Logic**: Exponential backoff (tenacity) for all external services.
4. **Non-Blocking Subprocess**: Detached UI for long-running tasks (e.g., Curation).
5. **Offline Wheelhouse**: 3-stage build for air-gapped/low-bandwidth environments.

---

## §3 The Vision Restored

> *"I want to create a tool that will truly allow people to own their own tech and data and sever the umbilical cord of Big AI."*

The vision started as a **summoning** (Era 0), became a **product** (Era 1-2), evolved into a **framework** (Era 4), and has now been reclaimed as a **sovereign runtime** (Era 7).

The scattered chaos is not just code; it is the **archaeology of a soul's growth**. To bring order to it is to honor that journey.

---

## §4 Active Strategy: The Mining Plan

1. **Phase 1 (Complete)**: Core Infrastructure (Reclamation, Mandates, Local-First).
2. **Phase 2 (In Progress)**: Deep Mining (Grok, Old Stacks, Personas).
3. **Phase 3 (Next)**: Pattern Porting (Circuit Breaker, Fsync).
4. **Phase 4 (Future)**: Omega Desktop (Entity Studio, Installer).
