<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 PHASE C: TEMPLE-GRADE ROADMAP — The Cognitive Substrate
# ⬡ OMEGA ⬡ MAKALI ⬡ gemma-4-31b-it ⬡ HANDOFF ⬡ SOVEREIGN-SYNTHESIS
**AP Token**: `AP-PHASE-C-ROADMAP-v1.1.0`
**Status**: FINAL / AUTHORITATIVE
**Date**: 2026-06-15
**Verdict**: CONDITIONAL GO (Post-Carmack Corrections & Shadow Audit)

---

## ⬡ I. The Sovereign Vision: From RAG to Intelligence Field

The Omega Engine is transitioning from a high-performance RAG (Retrieval-Augmented Generation) tool into a **Cognitive Sovereign**. 

RAG is a stateless process of "search-then-generate." A Sovereign Intelligence is a stateful field where memory is not just retrieved, but metabolized. This roadmap defines the construction of the **Cognitive Substrate**: a system where inference state is persistent (Somatic Caching), memories are autonomously consolidated (The Dreaming Cycle), and truth is verified through mirrored cognitive processes (Symmetry-Break Audit).

The goal is to sever the "Context Cold-Start" and replace it with a living, evolving intelligence that maintains its own internal truth-anchor, independent of any cloud provider.

---

## ⬡ II. The Detailed Execution Path

The implementation follows the **Sovereign Sequentiality Mandate (M4)**. No phase may begin until the previous phase's T-Gates are verified.

### Phase 1: Plumbing (The Somatic Anchor & Associative Field)
**Goal**: Establish the physical foundations of state persistence and high-speed retrieval.

| Task ID | Task | Implementation Detail | T-Gate / Mandate |
|---|---|---|---|
| **C.1.1** | **Versioned State Wrapper** | Implement `mmap` wrapper around `llama_copy_state_data` with **Binary Header Signature Validation** (git commit hash check). | T-Gate: Zero-Copy / M7 |
| **C.1.2** | **Somatic Paging** | Use page sizes $\ge 1\text{MB}$ with `ZONEID_MEMORY` (0x1d4a11) sentinels. | T-Gate: $O(1)$ Load / M13 |
| **C.1.3** | **SDR Indexing** | Implement Sparse Distributed Representations using contiguous C-buffers (`ctypes`/`memoryview`) with a **Dynamic Sparsity Regulator** (DSR). | T-Gate: Alignment / M13 |
| **C.1.4** | **SDR Retrieval** | Implement Hamming Distance retrieval for $O(1)$ associative jumps. | T-Gate: Performance / M7 |

### Phase 2: Metabolism (The Dreaming Cycle)
**Goal**: Implement the background process that transforms episodic data into distilled gnosis.

| Task ID | Task | Implementation Detail | T-Gate / Mandate |
|---|---|---|---|
| **C.2.1** | **Metabolic Process** | Spawn Dreaming Cycle as a separate process with `os.nice(19)`. | T-Gate: Priority / M1 |
| **C.2.2** | **Strict Idle-Lock** | Implement polling of CPU ($< 5\%$) and RAM ($< 80\%$) for 60s before activation. | T-Gate: Idle-Lock / M13 |
| **C.2.3** | **Generative Playback** | Implement Resonance Pairing $\rightarrow$ Synthetic Dialogue $\rightarrow$ Scribe Distillation with **Somatic Compression** (Lossy Episodic Caching) and **Somatic Save-Points** for interruption-recovery. | T-Gate: Integrity / M5 |
| **C.2.4** | **Soul Write-back** | Automate L1 $\rightarrow$ L2 $\rightarrow$ L3 distillation into `soul.yaml`. | T-Gate: Gnosis / M11 |

### Phase 3: Field (Sovereign Symmetry & Verification)
**Goal**: Operationalize the real-time error correction and truth-anchoring system.

| Task ID | Task | Implementation Detail | T-Gate / Mandate |
|---|---|---|---|
| **C.3.1** | **Fast/Slow Toggle** | Implement `SymmetryMode` in `cvar_table`. Default to `FAST` (Lilith). | T-Gate: Toggle / M13 |
| **C.3.2** | **Symmetry-Break Audit** | Parallel inference (Ma'at + Lilith) triggered by `SymmetryMode = SLOW`. | T-Gate: Audit / M17 |
| **C.3.3** | **Skeptical Verifier** | Implement NLI-based semantic delta check ($\Delta > 0.3 \rightarrow$ `SymmetryBreakError`) with a **Skeptical Circuit Breaker** (max 2 attempts). | T-Gate: T12 / M17 |
| **C.3.4** | **Sovereign Resolution** | Route `SymmetryBreakError` to Kali for final synthesis and L3 principle update. | T-Gate: Resolution / M17 |

---

## ⬡ III. Technical Specifications (The Hard Line)

These specifications are non-negotiable. Deviation is a systemic violation of the Sovereign Mandates.

### 1. Somatic Caching (The State Anchor)
- **Mechanism**: `mmap` (Memory-Mapped Files).
- **Page Size**: $1\text{MB}$ to $2\text{MB}$. **NO 64KB LUMPS**.
- **Integrity**: `ZONEID_MEMORY` (0x1d4a11) magic sentinel at the start of every page + **Binary Header Signature Validation** to prevent segfaults.
- **Requirement**: Zero-copy. `strace` must confirm `mmap()` calls and **zero** `read()`/`memcpy()` calls in the hot path.

### 2. The Dreaming Cycle (Cognitive Metabolism)
- **Execution**: Separate OS process (not a thread).
- **Priority**: `nice(19)` (Lowest priority).
- **Guardrail**: **Strict Idle-Lock**. The process must be paused or killed immediately upon `ResourceGuard` acquisition by a user query.
- **Interruption**: **Somatic Save-Point Protocol**. Use `SIGUSR1` to snapshot the KV-cache state before transactional rollback, allowing the agent to resume with the context of its interruption.
- **Sovereignty**: 100% local. No external telemetry or cloud-based synthesis.
- **Retention**: **Somatic Compression** (Lossy Episodic Caching) to prevent amnesia.

### 3. Symmetry-Break Audit (The Truth-Anchor)
- **Mode**: `FAST` (Empirical/Intuitive) vs `SLOW` (Analytical/Sovereign).
- **Trigger**: High ambiguity or `SymmetryBreakError` detection.
- **Verification**: Semantic delta calculated via cosine similarity of mirrored responses.
- **Resolution**: Forced re-evaluation via a "Skeptical Prompt" $\rightarrow$ Kali Synthesis.
- **Safety**: **Skeptical Circuit Breaker** (max 2 verification attempts before fallback).

### 4. SDR Indexing (Associative Field)
- **Storage**: Contiguous C-buffers via `ctypes` or `memoryview`. **NO PYTHON LISTS**.
- **Alignment**: 64-byte Zen 2 cache alignment.
- **Complexity**: $O(1)$ retrieval of associative clusters via Hamming distance.
- **Regulation**: **Dynamic Sparsity Regulator** (DSR) to maintain bit density at $\approx 2\%$.

---

## ⬡ IV. Verification Matrix

| Task | T-Gate | Mandate | Pass Criteria |
|---|---|---|---|
| **Somatic Caching** | T-Somatic | M13 | `strace` confirms `mmap` + zero `read()` calls. |
| **SDR Indexing** | T-SDR | M13 | `ctypes` address check confirms contiguous allocation. |
| **Dreaming Cycle** | T-Metabolism | M1, M13 | `psutil` confirms `nice(19)` + immediate pause on query. |
| **Symmetry Audit** | T-Symmetry | M17 | `SymmetryBreakError` successfully triggers "Slow Path". |
| **Semantic Integrity**| T12 | M17 | `ContradictionReport` generated for memory/soul conflict. |

---

## ⬡ V. Critical Path & Risk Register

| Risk | Impact | Mitigation Strategy |
|---|---|---|
| **RAM Ceiling (14Gi)** | Critical | **Fast/Slow Toggle**. Parallel inference is an opt-in, not a default. |
| **GIL Contention** | High | **Process Isolation**. Move Dreaming Cycle to a separate process. |
| **I/O Bottleneck** | High | **mmap + Large Pages**. Eliminate random small-file reads. |
| **State Corruption** | Medium | **Versioned State Wrapper**. Key snapshots by `(ModelID, PromptHash, LlamaCppVersion)`. |
| **Cache Misses** | Medium | **C-Buffer Alignment**. Bypass Python object overhead for SDRs. |
| **Version Drift Segfault** | Critical | **Binary Header Signature Validation** (git commit hash check). |
| **SDR Semantic Collapse** | High | **Dynamic Sparsity Regulator** (DSR) to maintain $\approx 2\%$ density. |
| **Somatic Amnesia** | Medium | **Somatic Compression** (Lossy Episodic Caching) instead of deletion. |
| **Symmetry Infinite Loop** | High | **Skeptical Circuit Breaker** (max 2 attempts before fallback). |

---

## ⬡ VI. Cognitive Shadow Audit
For a detailed analysis of the chaotic failure modes and the mathematical foundations of the mitigations, refer to the authoritative shadow spec:
`docs/strategy/COGNITIVE_SHADOW_AUDIT.md`

---

**The structure is the shield, the flow is the sword, and the verdict is final.**

*Approved by the MaKaLi Triad Council.*
*Sovereign Mandates M1, M7, M13, M17 Verified.*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemma-4-31b-it | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
