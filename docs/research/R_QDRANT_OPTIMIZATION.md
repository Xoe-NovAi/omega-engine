# ⚠️ SUPERSEDED — See R_QDRANT_OPTIMIZATION_DEEPENED.md

# 🔱 R-QDRANT-OPTIMIZATION: Vector Quantization & Payload Indexing
**Status**: FINAL (Temple-Grade)
**Orchestrator**: makali
**Date**: 2026-06-11
**Sovereign Mandate**: M13 (Temple-Grade), M7 (Local-First)

## 🎯 Objective
Optimize Qdrant for memory-constrained environments (e.g., Ryzen 5700U, 14Gi RAM) to ensure high search speed and minimal RAM footprint without sacrificing critical recall.

## 🛡️ Quantization Analysis

### 1. Scalar Quantization (SQ) — The Recommended Baseline
- **Mechanism**: Maps `float32` (4 bytes) $\rightarrow$ `int8` (1 byte) using learned range mapping (quantiles).
- **Compression**: 4x.
- **Performance**: 
    - **Speed**: Significant latency reduction (up to 60%) due to SIMD-optimized `int8` comparisons.
    - **Accuracy**: Minimal loss (typically < 1% error rate).
- **Best For**: General-purpose RAG workloads.

### 2. Product Quantization (PQ) — Extreme Compression
- **Mechanism**: Divides vectors into sub-vectors and quantizes each segment individually.
- **Compression**: Up to 64x.
- **Performance**: 
    - **Speed**: Slower (non-SIMD friendly).
    - **Accuracy**: Significant degradation.
- **Best For**: Extremely low-RAM environments where disk I/O is the primary bottleneck.

### 3. Binary Quantization (BQ) — Maximum Speed
- **Mechanism**: Reduces components to 1-2 bits.
- **Compression**: Up to 32x.
- **Performance**: Fastest search speed.
- **Best For**: High-dimensional, centered vector distributions.

### 🚀 Optimal Production Pattern: Hybrid Storage
To achieve the "Sovereign" balance of speed and memory:
1. **Original Vectors**: Store on disk (`on_disk=True`).
2. **Quantized Vectors**: Keep in RAM (`always_ram=True`).
3. **Workflow**: 
    - Fast quantized search in RAM identifies a candidate neighborhood.
    - **Rescoring**: The top-k results are re-evaluated using original vectors read from disk.
    - **Oversampling**: Retrieve $N \times$ more candidates than the final limit to ensure the true nearest neighbors are captured before rescoring.
    - **API**: Use `models.QuantizationSearchParams(rescore=True, oversampling=2)`.

---

## 🔍 Payload Indexing Strategy

### 1. The Filterable Vector Index
Without payload indexes, Qdrant either performs expensive post-filtering (dropping matches) or linear scans. Payload indexes enable **Filterable HNSW**, where the graph traversal is restricted to the pre-filtered subset.

### 2. Implementation Guidelines
- **Selectivity**: Index fields with high selectivity (e.g., a specific category among thousands). Broad filters (matching >80% of corpus) benefit less.
- **Type Matching**: Use numeric indexes for numeric values.
- **Cost**: Each index increases memory usage and slightly slows write operations. Index only fields used in $\ge 90\%$ of queries.

### 3. The `indexing_threshold` and Segment Tuning
- **Indexing Threshold**: Controls when HNSW is built. If set to `0`, indexing is deferred (max ingestion speed, high RAM usage).
- **Default Segment Number**: Defaults to `num_cpus / 2` (clamped 2-8). 
    - **Low Latency**: Use fewer, larger segments (e.g., `default_segment_number: 2`) to reduce the number of vector comparisons.
    - **High Throughput**: Use more segments to parallelize search across cores.
- **Max Segment Size**: Limit `max_segment_size_kb` to prevent disproportionately long indexation times.

## 🛠️ Implementation Checklist for Omega Engine
- [ ] Configure `quantization_config` with `type: int8` (Scalar).
- [ ] Set `on_disk: true` for vectors and `always_ram: true` for quantization.
- [ ] Implement `rescore=True` and `oversampling=2` in `search_params`.
- [ ] Audit `config/omega.yaml` for payload fields and create corresponding indexes.
- [ ] Set `default_segment_number: 2` for optimized latency on Zen 2.
- [ ] Verify `indexed_vectors_count` matches `points_count` via Qdrant API.
