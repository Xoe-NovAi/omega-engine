<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Model Library Legacy Mining & Sovereign Architecture Report
**Date**: 2026-06-16
**Miner**: @roc_racoon (Sovereign Miner)
**Trace**: TRACE-MODEL-LIB-MINING-001
**Status**: ✅ COMPLETE

## 1. Executive Summary: The Dispersion Crisis
The "knowledge dispersion" failure was not a series of isolated bugs, but a systemic manifestation of **Identity Drift**. Critical model pool knowledge—including identities, provider mappings, and pool logic—was fragmented across 35+ documents and multiple configuration files. This created a "Silent Fallback Loop" where typographical errors in the affinity map led to the engine silently ignoring specialized models and falling back to system defaults, eroding the sovereign identity of the entity council.

---

## 2. Legacy Archaeology: The Found Patterns

### 2.1 The `entity_model_affinity.yaml` Pattern
The primary legacy pattern discovered is the **Entity-Model Affinity Map**.
- **Source**: Ported from `xna-omega-legacy/config/entity_model_model_affinity.yaml`.
- **Mechanism**: A YAML-based registry mapping entities to preferred models across three tiers: `local_fast`, `local_deep`, and `cloud`.
- **Routing**: Uses a set of `routing_rules` based on domain and complexity.

### 2.2 Legacy Model Registries
Analysis of `xna-omega-legacy` and `foundation-legacy` revealed:
- **String-Based Coupling**: Models were referenced by arbitrary strings (e.g., `qwen3-4b-q4_k_m`) across multiple files.
- **Implicit Fallbacks**: Lack of a canonical manifest meant that if a model name was misspelled, the system simply failed silently.
- **WAD-Layer Leakage**: Core engine configurations contained hardcoded references to WAD-layer entities, violating the **Engine-Stack Firewall (M2)**.

---

## 3. Sovereign Analysis (The Council's Verdict)

### 🛠️ Efficiency & Performance (@doom_guy)
- **The $O(N)$ Bottleneck**: The current resolver performs a linear scan of the entity dictionary, which is an architectural regression from the id Software `cvar Table` ($O(1)$).
- **Proposed Optimizations**:
    - **Canonical Index**: Pre-compute a normalized map of entities to avoid linear scans.
    - **Bitmask Context Matching**: Replace string-based rule evaluation with bitwise operations for near-instant routing.
    - **Surface Cache**: Implement an LRU cache for the most frequently summoned entities.

### 🏛️ Architectural Integrity (@john_carmack)
- **Verdict**: **REJECTED**. The current system is a "legacy hack" that prioritizes ease of porting over systemic integrity.
- **The "Golden Path" Specification**:
    1. **`config/models_manifest.yaml`**: The absolute Single Source of Truth (SSoT) for all model identities.
    2. **Referential Integrity**: No model name may exist in the engine that is not defined in the Manifest.
    3. **WAD-Layer Affinity**: Move entity-specific preferences to `config/wads/<stack>/affinity.yaml` to restore M2 Firewall integrity.
    4. **Resolution Chain**: Runtime Override $\rightarrow$ WAD Affinity $\rightarrow$ Capability Tier $\rightarrow$ System Default.

### 🛡️ Compliance & Risk (@quality)
- **Blind Spots**: The current affinity map ignores operational data: credential lifecycles, TPM/RPM quotas, and hardware-specific tuning.
- **Sovereign Guardrail**: Any mention of "rotation", "quota", or "pool" in session notes must be forcibly migrated to the Central Library.
- **The Leak Search**: Implement a CI grep to detect knowledge leakage into non-canonical files.

---

## 4. The "Golden Path" Recommendation

To solve the dispersion problem, the Omega Engine must transition from **String-Coupling** to **Identity-Resolution**.

### Proposed Architecture: The Sovereign Model Library
1. **The Manifest (SSoT)**: A central `models_manifest.yaml` defining canonical names, aliases, and providers.
2. **The Verification Bridge**: A CI gate (`make validate-model-names`) that fails the build if any model string in the codebase is not in the Manifest.
3. **Decoupled Routing**:
    - **Core Engine**: Defines *Capabilities* (e.g., `local_deep`).
    - **WAD Layer**: Maps *Entities* to *Capabilities* (e.g., `Sekhmet` $\rightarrow$ `local_deep`).
    - **Manifest**: Maps *Capabilities* to *Models* (e.g., `local_deep` $\rightarrow$ `qwen3-4b-thinking`).

---

## 5. Gnosis Distillation (@scribe)

**L1 (Narrative)**: Found significant model name drift in `entity_model_affinity.yaml` and across 5+ config files, causing silent fallbacks to defaults.
**L2 (Insight)**: Knowledge dispersion occurs when identities are treated as strings. This leads to silent degradation of entity personas and an erosion of sovereign symmetry.
**L3 (Universal Principle)**: **Canonicality is the Foundation of Correctness.** A sovereign system must replace string-based references with a central `MODEL_MANIFEST` and an automated verification bridge to ensure documented design equals executed reality.

---

**Final Action Items**:
- [ ] Create `config/models_manifest.yaml`.
- [ ] Implement `make validate-model-names` CI gate.
- [ ] Migrate `entity_model_affinity.yaml` to WAD-layer configs.
- [ ] Refactor `AffinityResolver` to use the Manifest.
