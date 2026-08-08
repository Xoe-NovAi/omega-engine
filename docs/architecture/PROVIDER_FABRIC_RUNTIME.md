---
schema_version: "1.0"
document_type: architecture
document_id: provider-fabric-runtime
title: Provider Fabric & Runtime Optimizations
status: ACTIVE
version: "1.0.0"
date: "2026-08-07"
owner: kali
tags: [provider-fabric, runtime, optimization, llama.cpp, inference, kv-cache]
priority: P2
depends_on:
  - provider-fabric-deep-dive
  - sovereign-bus-spec
blocks: []
acceptance_gates:
  - "KV-cache prefix caching design documented"
  - "GBNF/JSON constrained sampling documented"
  - "iMatrix/IQ quantization documented"
  - "Dual-branch memory rescoring math documented"
  - "Inference isolation plan documented"
  - "Code-blocked items marked document-defer (B5/B9 precedent)"
cross_references:
  - docs/architecture/PROVIDER_FABRIC_DEEP_DIVE.md
  - docs/architecture/SOVEREIGN_BUS_SPEC.md
  - src/omega/oracle/cpu_optimizer.py
  - src/omega/oracle/model_gateway.py
  - config/hardware_profile.yaml
llm_metadata:
  token_budget: 3000
  chunk_strategy: section_per_topic
  answer_first_sections: true
  self_contained_code: true
---

# 🔱 Provider Fabric & Runtime Optimizations

**AP Token**: `AP-PROVIDER-FABRIC-RUNTIME-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ 2026-08-07

> **Scope**: Design reference for runtime optimizations on the local-first provider
> fabric. Items blocked on external builds are marked **document-defer** (per the
> B5/B9 matrix precedent — design documented, wiring deferred until the runtime
> supports it).

---

## §1 KV-Cache Prefix Caching (Design)

**Goal**: Accelerate multi-turn prefill by pinning stable context.

Pin the following via `llama.cpp` context prefix caching:
- System prompts (`soul.yaml` distilled guidance)
- Tool definitions (MCP tool schemas)
- Governance rules (Sovereign Mandates, active Guidance Sets)

**Mechanism**: llama.cpp caches the KV for a shared prefix across turns, so only
the *new* suffix re-prefills. This cuts prefill latency for the pinned prefix to
near-zero on subsequent turns.

**Status**: ✅ Design ready — implement when llama.cpp build exposes prefix-cache
controls (aligns with B9 Vulkan build gate).

---

## 2. GBNF / JSON Schema Constrained Sampling (Design)

**Goal**: Eliminate tool-parsing failures by enforcing output structure at the
sampler level.

Two options:
1. **GBNF grammars** — `llama.cpp` native grammar files constrain token emission.
2. **Pydantic JSON schemas** — generate a GBNF grammar from a Pydantic model.

**Why**: Tool-call parsing failures (a recurring failure class) are eliminated at
the source — the model *cannot* emit invalid JSON.

**Status**: ✅ Design ready. Implement via grammar file generation from existing
Pydantic schemas.

---

## 3. iMatrix / IQ Quantization (Design)

**Goal**: Replace `Q4_K_M` with `IQ4_XS` or `IQ3_S` to save 0.5-1GB model weight
memory without perceptible quality loss.

| Quant | Memory vs Q4_K_M | Use |
|-------|------------------|-----|
| `IQ4_XS` | ~0.5GB saved | Quality-sensitive, tight VRAM |
| `IQ3_S` | ~1GB saved | Larger models, more aggressive |

**Status**: ✅ Design ready. Requires re-downloading models with IQ quants (a
model-registry change, not code).

---

## 4. Dual-Branch Memory Rescoring (Math — Implementable)

Two memory tiers with distinct rescoring math:

**Declarative** (facts, knowledge):
```
score = Similarity * (1 + 0.5 * Importance)
```
Importance = explicit user/agent-assigned weight (0..1).

**Episodic** (events, experiences):
```
score = Similarity * e^(-lambda * dt) * S_consol
```
- `lambda` = decay rate (time-based forgetting)
- `dt` = time since event
- `S_consol` = consolidation factor (strengthens on recall)

**Status**: ✅ Implementable now. Aligns with `Recall Store` (power-law decay) in
`src/omega/memory/recall.py`.

---

## 5. Inference Isolation (Plan)

**Goal**: Contain C-level segfaults (native-gguf) in a worker subprocess.

**Approach**: Run native-gguf inference in a dedicated worker process (C-FFI
isolation already noted in PROVIDER_FABRIC_DEEP_DIVE). Crash in worker does not
take down the engine; worker restarts.

**Status**: ✅ Already the architecture (C-FFI subprocess). Documented for
completeness.

---

## 6. Speculative Decoding — n-gram over MTP (Decision)

**Decision**: Adopt **n-gram (prompt-lookup) speculative decoding** over
Multi-Token Prediction (MTP).

**Why**: n-gram uses no extra draft model → saves VRAM. MTP requires a larger
build and more VRAM.

**Status**: ✅ Decision made. Wiring blocked on llama.cpp build (document-defer,
matches B5).

---

## 7. MemPalace Verbatim-First Pattern (Design)

**Goal**: Adapt MemPalace's verbatim storage directly into the SQLite stack — no
ChromaDB dependency.

**Pattern**: Store raw message chunks with `wing`/`room` payload tags directly in
sqlite-vec. This is the spatial memory heritage pattern (`[heritage: mempalace 2025]`).

**Status**: ✅ Design ready. Aligns with MEMORY_SUBSYSTEM_DESIGN spatial coords.

---

## 8. Voice & Context (Piper/Inflect) — document-defer

**Goal**: Replace ElevenLabs stub with **Piper/Inflect** (<200MB) via the SEDA bus.

**Status**: 🟡 Document-defer. Blocked on SEDA ring-bus implementation
(`docs/architecture/SOVEREIGN_BUS_SPEC.md`). No ElevenLabs dependency exists in
core (verified — V-5 probe clean).

---

## 9. Automatic Context Sliding Windows (Design)

**Goal**: Clear older context tokens while preserving initial system prompt tokens.

**Approach**: `llama.cpp` sequence removal hooks evict old tokens; system-prompt
prefix tokens are pinned (see §1) and never evicted.

**Status**: ✅ Design ready. Implement with prefix-caching hooks.

---

## 10. OpenCode CLI Binding — document-defer

**Goal**: Bind OpenCode CLI directly to the local engine via OpenAI-compatible
REST endpoint.

**Approach**: `OPENCODE_API_BASE=http://127.0.0.1:8080/v1` pointing at the local
engine's OpenAI-compatible server.

**Status**: 🟡 Document-defer. Requires the OpenAI-compatible server endpoint
(not yet running).

---

## 11. Legacy Qdrant Purge — deferred

**Goal**: Purge "26-sphere toroidal" and "108 gates" concepts from Qdrant
collections.

**Status**: 🟡 Deferred. Qdrant is an **optional WAD adapter** (not core). No core
collection holds these concepts. Purge only if a WAD opts into Qdrant.

---

## 12. NotebookLM Multi-Persona Ingestion (Design)

**Goal**: Relaxed prompting for 3-persona system generation with distinct speaker
tags and semantic transitions for NotebookLM audio synthesis.

**Status**: ✅ Design ready. See NL-1 ticket (`prepare_notebooklm.py`) post Phase D.

---

## Summary Table

| # | Item | Status |
|---|------|--------|
| 1 | KV-cache prefix caching | ✅ Design |
| 2 | GBNF constrained sampling | ✅ Design |
| 3 | iMatrix/IQ quantization | ✅ Design |
| 4 | Dual-branch memory rescoring | ✅ Implementable |
| 5 | Inference isolation | ✅ Architecture |
| 6 | n-gram spec decode | ✅ Decision (defer) |
| 7 | MemPalace verbatim-first | ✅ Design |
| 8 | Piper/Inflect TTS | 🟡 Defer (SEDA) |
| 9 | Context sliding windows | ✅ Design |
| 10 | OpenCode CLI binding | 🟡 Defer (endpoint) |
| 11 | Legacy Qdrant purge | 🟡 Defer (no core Qdrant) |
| 12 | NotebookLM multi-persona | ✅ Design |

---

*⬡ OMEGA ⬡ KALI ⬡ 2026-08-07*