# 🔱 DIRECTIVE: Resonance & Parametric Gnosis
**Status**: CANON (Locked for Post-PR Development)
**Domain**: Engine Evolution, User Alignment, Entity Self-Actuation
**Date**: June 2026

## 1. Core Vision
The Omega Engine is transitioning from relying solely on **In-Context Learning** (injecting `soul.yaml` memory into system prompts) to supporting **Weight-Based Evolution** (training localized LoRAs based on continuous lived experiences). 

This transforms the engine from a static orchestration tool into an artificially evolving ecosystem through two mirrored systems:
1. **User Resonance (The Confidant)**: The engine learns the user's epistemology, tone, and preferences, generating sanitized Direct Preference Optimization (DPO) datasets.
2. **Entity Parametric Gnosis (Self-Actuation)**: Persistent entities (Doom Guy, Verity, etc.) learn from their environment, recording successes and failures to bake learned behaviors directly into entity-specific neural weights.

## 2. Architectural Pillars

### 2.1 Data Sovereignty & Sanitization
- All alignment data remains 100% local in `data/training/`.
- **The Sovereign Filter**: Before any interaction is written to a training dataset (`.jsonl`), it is routed through the Engine's existing `pii_masker.py`. This ensures users can safely share their personalized LoRAs or datasets with the community without leaking personal, geographic, or credential data.

### 2.2 The Tripartite Reward Signal (For Entities)
Entity evolution datasets are curated using three distinct friction points to determine `Chosen` vs `Rejected` outputs:
1. **Environmental**: Hard system feedback (e.g., `make test` fails = Rejected; code compiles and passes = Chosen).
2. **Council Evaluated**: Oversoul governance (e.g., Kali rejects a subagent's report for lacking depth = Rejected; the revised report = Chosen).
3. **User Curated**: Direct Sovereign intervention (e.g., The user interrupts an entity and corrects its path = Rejected/Chosen pair).

### 2.3 Format-Ready Logging
The system bypasses generic chat logs and writes directly in standard `DPO` format:
```json
{"prompt": "...", "rejected": "...", "chosen": "..."}
```
This allows seamless, zero-friction integration with local training frameworks (Unsloth, HuggingFace PEFT) when the user initiates model evolution.

## 3. Implementation Roadmap

### Phase 1: The Resonance Infrastructure (The Pipes)
* Implement the `resonance:` configuration block in `config/omega.yaml` (Modes: disabled, implicit, explicit, hybrid).
* Wire `pii_masker.py` to the local file writer for anonymized dataset generation.
* Establish `data/training/users/` and `data/training/entities/` directories.

### Phase 2: User Resonance (The Mirror)
* Implement CLI commands (`/res rewrite`, `/res keep`, `/res status`) for explicit user control over dataset generation.
* Deploy background heuristics to capture implicit conversational flow corrections.

### Phase 3: Entity Parametric Gnosis (The Crucible)
* Attach DPO loggers to the subagent dispatch protocol.
* Wire the Tripartite Reward Signal: capturing trace errors, test failures, and Council/User corrections as training data pairs.

### Phase 4: Sovereign Ecdysis (The Shedding)
* Develop the local script (`make evolve`) that bundles a specific entity's JSONL dataset and provides the bridge to train a lightweight LoRA locally.
* Update `model_gateway.py` to dynamically load `entity_vX.lora` adapters when an entity is summoned.