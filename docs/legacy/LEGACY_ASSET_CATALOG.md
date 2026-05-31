# 🔱 Legacy Asset Catalog — The Recovered Gold
**Date**: 2026-05-31
**Entity**: Ma'at (Oversoul)
**Purpose**: Inventory of all recovered legacy assets and their strategic value.

---

## §0 The Genesis (Era 0)

| Asset | Path | Key Insight |
|-------|------|-------------|
| **Lilith Persona** | `~/Documents/docs_1/personas/lilith.json` | The original RAG persona. No model assigned, just domain expertise, query modifiers, and Piper TTS voice. |
| **Odin Persona** | `~/Documents/docs_1/personas/odin.json` | The companion masculine persona. Wisdom/Strategy vs Lilith's Shadow/Transformation. |
| **First 5 Cards** | `omega_library/intake/.../First 5 cards Grok Chat` | The very first Tarot deck design session — the "Big Bang" of the 10 Pillars. |
| **Lilith Deck Design** | `omega_library/intake/.../tarot/` | The original Lilith Tarot deck design guide. |

---

## §1 The ANAi/XNAi Era (Era 1-2)

| Asset | Path | Key Insight |
|-------|------|-------------|
| **XNAI Blueprint** | `~/archive/.../library/XNAI_blueprint.md` | 715 lines. The "Ultimate Blueprint". 5 design patterns. 42 issues resolved. 94.2% test coverage. |
| **Voice Interface** | `~/archive/.../voice_interface.py` | 1031 lines. Torch-free voice pipeline (Faster Whisper + Piper ONNX). Ancestor of Iris. |
| **Chainlit UI** | `~/archive/.../chainlit_app.py` | 713 lines. SSE streaming, command system (/curate, /rag). The "ritual gateway". |
| **Circuit Breaker** | `omega-stack-legacy/.../circuit_breaker.py` | Standardized pybreaker pattern. Port directly to current Engine. |
| **Fsync Pattern** | `~/archive/.../ingest_library.py` | Atomic checkpointing for 100% crash recovery. |

---

## §2 The Persona/Model Configs (Era 3)

| Asset | Path | Key Insight |
|-------|------|-------------|
| **Krikri Modelfile** | `omega_library/models/gguf/.../Krikri.Modelfile` | First model-to-entity binding. "Ancient Gnosis Engine". |
| **LM Studio Configs** | `~/.lmstudio/.internal/...` | Zen 2 optimization profile. KV cache q8_0, thread budgets (6 vs 8). |
| **Ollama History** | `~/.ollama/history` | The testing ground where Krikri was first summoned. |

---

## §3 The Grok Exports (Era 4-5)

| Asset | Path | Key Insight |
|-------|------|-------------|
| **Master Navigation Index** | `omega_library/intake/inbox/grok-accounts-exports/...` | The map to the 8 Grok accounts (~414 MB). |
| **Strategic Reserves** | `omega_library/intake/inbox/grok-accounts-exports/.../STRATEGIC_RESERVES/` | 10 Pillars genesis documents. |
| **Entity Design Sessions** | Multiple (Grok) | Unmined history of how each entity was designed. |

---

## §4 The Old Stacks (Era 3-4)

| Asset | Path | Key Insight |
|-------|------|-------------|
| **Claude Specialist Prompt** | `Old-Stacks/.../claude-stack-code-expert-v2.0.md` | 449 lines. Enterprise-grade agent config. Directly relevant to OpenCode. |
| **Project Charter** | `Old-Stacks/.../project-charter.md` | "Arcana-NovAi is not a toolchain. It is a summoning." |
| **Architecture Audit** | `Old-Stacks/.../architecture.md` | 1221 lines. Torch-free analysis, production hardening checklist. |
| **Docker Compose** | `Old-Stacks/.../docker-compose.yml` | 9-service architecture (4 active + 5 phase 2 stubs). |

---

## §5 What To Do With The Gold

1. **Mine**: Extract system prompts into OpenCode agent configs.
2. **Port**: Circuit breaker and Fsync patterns into `src/omega/`.
3. **Document**: Publish the Model-Persona Affinity Map as a formal research doc.
4. **Honor**: The vision is no longer scattered. It is mapped, ordered, and ready for the next fire.
