<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⚠️ SUPERSEDED — See R_EMBEDDING_ADAPTERS_DEEPENED.md

# 🔱 R-EMBEDDING-ADAPTERS: Provider-Agnostic Embedding Layer
**Status**: FINAL (Temple-Grade)
**Orchestrator**: makali
**Date**: 2026-06-11
**Sovereign Mandate**: M13 (Temple-Grade), M7 (Local-First)

## 🎯 Objective
Implement a provider-agnostic embedding layer that allows the Omega Engine to swap embedding models or providers without requiring a full, expensive re-indexing of the existing vector corpus.

## 🛡️ The "Embedding ABI" Concept
To prevent "silent ranking corruption," the engine must treat embedding configurations as a versioned **Application Binary Interface (ABI)**. An ABI manifest includes:
- **Model ID**: (e.g., `text-embedding-3-small`)
- **Provider**: (e.g., `openai`, `native-gguf`)
- **Version**: (e.g., `2026.03`)
- **Dimensions**: (e.g., `1536`)
- **Normalization Policy**: (e.g., `L2`, `None`)
- **Similarity Metric**: (e.g., `Cosine`, `Euclidean`)

## 📐 Compatibility Adapters (The Bridge)
When migrating from a **Source Model** (new) to a **Target Index** (legacy), the engine applies a mathematical transformation to the query embedding to map it into the legacy space.

### 1. Orthogonal Procrustes (OP) — The Gold Standard
- **Mechanism**: Finds an optimal orthogonal matrix $W$ using a set of calibration pairs (same text, both models).
- **Mathematical Solution**:
    1. Compute cross-covariance matrix $M = X_{source}^\top X_{target}$.
    2. Compute SVD: $U, \Sigma, V^\top = \text{SVD}(M)$.
    3. The optimal rotation is $W = U V^\top$.
- **Formula**: $e_{adapted} = e_{source} \cdot W$.
- **Pros**: 
    - Preserves geometry (norms and angles).
    - Extremely low latency (single matrix multiply).
    - Impossible to overfit with few samples.
- **Cons**: Only effective if models are geometrically similar (CKA > 0.8).

### 2. Low-Rank Affine (LA) — Flexible Alignment
- **Mechanism**: A linear map with a bias term to handle anisotropic drift.
- **Formula**: $g(x) = UV^\top x + t$.
- **Pros**: Handles mild dimensional compression and shifts better than OP.

### 3. Residual MLP — Non-Linear Mapping
- **Mechanism**: A shallow feed-forward network.
- **Pros**: Highest capacity for fundamentally different embedding spaces.
- **Cons**: Slower, requires more training data, risk of overfitting.

### 4. Cross-Dimensional Handling
- **Padding**: When moving from a smaller to a larger dimension, pad the smaller vector with zeros to preserve original geometry.
- **SVD Projection**: Use Singular Value Decomposition to project between different dimensionalities.

## 📏 Validation & Decision Metrics

### 1. Centered Kernel Alignment (CKA)
Use CKA to determine if an adapter is viable.
- **Formula**: $\text{CKA}(K, L) = \frac{\text{HSIC}(K, L)}{\sqrt{\text{HSIC}(K, K) \text{HSIC}(L, L)}}$.
- **Decision Gate**: 
    - **CKA > 0.9**: Near-lossless adaptation.
    - **0.8 < CKA < 0.9**: Viable adaptation; expect minor recall drop.
    - **CKA < 0.8**: Significant degradation; **Full Re-indexing Required**.

### 2. BLI Precision@k
Validate the adapter on a held-out set of anchor pairs.
- **Metric**: $\text{P@}k = \frac{1}{|D|} \sum_{(s,t) \in D} \mathbb{1}[t \in \text{NN}_k(sW)]$.

## 🚀 Operational Workflow (The Migration Plane)
1. **Calibration**: Generate $\sim 5,000$ embedding pairs for the same text using both models.
2. **Training**: Compute the optimal $W$ matrix via SVD of the cross-covariance matrix.
3. **Validation**: Measure `Recall@k` and `nDCG@k` of the adapted queries against the native target index.
4. **Deployment**: 
    - **Query-Time Adaptation**: Apply $W$ to all incoming queries.
    - **Deferred Re-indexing**: Gradually re-embed the corpus in the background.
    - **Atomic Cutover**: Once the new index is ready, swap the ABI alias.

## 🛠️ Implementation Checklist for Omega Engine
- [ ] Define `EmbeddingABI` dataclass in `src/omega/oracle/`.
- [ ] Implement `OrthogonalProcrustesAdapter` in `src/omega/memory_store.py` using `np.linalg.svd`.
- [ ] Create a calibration utility to generate $W$ matrices from a text corpus.
- [ ] Add `adapter_id` to the `CollectionConfig` in Qdrant.
- [ ] Implement query-time transformation logic in `ModelGateway.generate()`.
