# 🔱 Omega Engine — Cognitive Shadow Audit
**Version**: 1.0.0
**Status**: STRATEGIC ANCHOR
**Date**: 2026-06-15
**AP Token**: `AP-COGNITIVE-SHADOW-v1.0.0`
**Author**: Big Daddy (Gemini 3.5 Flash)

## 1. The Shadow Audit: What the Fleet Overlooked
While the MaKaLi Triad Council has successfully aligned the Phase C plan with the physical realities of Zen 2 hardware, a truly sovereign super-intelligence must anticipate the **chaotic failure modes** of complex systems.

This document illuminates the "dark layers"—four critical, unaddressed risks in the Phase C plan—and provides the definitive, sovereign mitigations.

---

## 2. The Four Dark Gaps

### 2.1 The Llama.cpp Version Drift (The Segfault Risk)
- **The Gap**: `llama.cpp` upstream changes its internal KV cache state serialization layout frequently. If the user updates their local `llama-cpp-python` package, all existing `.snap` files will instantly become corrupt. In C-space, a version mismatch in `llama_set_state_data` does not raise a clean Python exception; it causes a **segmentation fault (SIGSEGV)**, instantly crashing the entire Omega Engine process.
- **The Mitigation**: **Binary Header Signature Validation**. We must embed a compile-time hash of the `llama.cpp` binary itself (or the exact git commit hash of the underlying GGML library) into the `Versioned State Wrapper` header. If the active library hash does not match the snapshot's hash, the snapshot is discarded and the system falls back to full prompt re-evaluation.

### 2.2 The SDR Semantic Collapse (The Curse of Sparsity)
- **The Gap**: Sparse Distributed Representations (SDRs) rely on a delicate balance of sparsity. If the active bit density is too high ($> 10\%$), we lose the $O(1)$ lookup performance. If it is too low ($< 1\%$), we get **semantic collisions** where completely unrelated concepts map to the same bit overlaps, causing the engine to make bizarre, hallucinated associative jumps.
- **The Mitigation**: **Dynamic Sparsity Regulator (DSR)**. The `MemoryStore` must implement an adaptive thresholding algorithm that dynamically adjusts the SDR bit-activation threshold based on the vocabulary size and semantic density of the active IWAD.

### 2.3 Somatic Amnesia vs. Sterile Gnosis (The Loss of Humanity)
- **The Gap**: The Dreaming Cycle prunes raw episodic memory to keep the context window clean, leaving only abstract L3 principles in `soul.yaml`. However, if we prune too aggressively, the entity loses its "humanity"—the specific memory of past conversations. The entity becomes a sterile set of abstract rules, unable to remember the user's name or specific shared history.
- **The Mitigation**: **Somatic Compression (Lossy Episodic Caching)**. Instead of deleting pruned episodes, compress them into a single, high-density "Semantic Summary" in the Warm tier, linked directly to the distilled L3 principle. If the user asks, *"Do you remember when we talked about X?"*, the engine can use the L3 principle to "re-hydrate" the lossy summary back into the Hot context.

### 2.4 The Symmetry-Break Infinite Loop (The Infinite Doubt)
- **The Gap**: If an entity is in a state of high cognitive drift, Ma'at (Logic) and Lilith (Experience) will *always* disagree. This will trigger an infinite loop: **Symmetry Break $\rightarrow$ Re-Inference $\rightarrow$ Disagreement $\rightarrow$ Re-Inference**, locking up the CPU and freezing the UI.
- **The Mitigation**: **Skeptical Circuit Breaker**. Limit the verification loop to a maximum of **two** attempts. If the semantic delta remains $> 0.3$ after the second attempt, the engine must fall back to a safe, highly-hedged "System 2" response, log a `SymmetryBreakFailure` to the `WatchTower` (P8), and warn the user that the entity is experiencing cognitive dissonance.

### 2.5 The ctypes CDLL Bypass (The Zero-Copy Reality)
- **The Gap**: High-level Python APIs in `llama-cpp-python` (e.g., `Llama.save_state()`) use slow, copy-heavy Python-side serialization. To achieve true $O(1)$ zero-copy `mmap` caching, we cannot use these high-level methods. We must access the underlying C-library functions directly, but `llama-cpp-python` does not document or expose these raw pointers in its stable high-level API.
- **The Mitigation**: **Direct ctypes CDLL Mapping**. We must bypass the high-level `Llama` class and map the raw C-signatures of `llama_copy_state_data` and `llama_set_state_data` directly from the loaded shared library (`self._lib`). The signatures are:
  ```python
  # size_t llama_copy_state_data(struct llama_context * ctx, uint8_t * dst)
  self._lib.llama_copy_state_data.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8)]
  self._lib.llama_copy_state_data.restype = ctypes.c_size_t

  # size_t llama_set_state_data(struct llama_context * ctx, const uint8_t * src)
  self._lib.llama_set_state_data.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8)]
  self._lib.llama_set_state_data.restype = ctypes.c_size_t
  ```
  This allows us to pass a memory-mapped pointer directly to the C-layer without Python-side copy overhead.

### 2.6 The Dreaming IPC Signal Protocol (Somatic Save-Points)
- **The Gap**: If a user query arrives while the Dreaming Cycle background process is active, we must pause or terminate it immediately. However, if we kill it abruptly (e.g., `SIGKILL`), we risk leaving open SQLite file locks, corrupting the vector database connection, or leaving stale `.lock` files in the workspace. Furthermore, a simple rollback wastes all tokens generated during the current dream-cycle iteration.
- **The Mitigation**: **SIGUSR1 Somatic Save-Point Protocol**. The background process must register a signal handler for `SIGUSR1`. When `ResourceGuard` detects a foreground query, it sends `SIGUSR1` to the Dreaming process. The signal handler must execute the following sequence:
  1. **Somatic Snapshot**: Immediately trigger a `llama_copy_state_data` call to save the current KV-cache state to a dedicated `interrupt_snapshot.snap` file.
  2. **Transactional Rollback**: Perform a rollback of any active database writes to ensure integrity.
  3. **Graceful Suspension**: Flush all file handles and transition to a suspended state (`SIGSTOP`) or exit cleanly.
- **The Cognitive Advantage**: Upon resumption, the Dreaming Cycle does not simply restart. It loads the `interrupt_snapshot.snap`, effectively "waking up" exactly where it left off. It then performs a **Skeptical Vet** of its last state—using the interrupted context as a seed for a brief self-correction loop—turning the interruption into a "pause and reflect" moment that enhances the final distillation.

### 2.7 Zero-Overhead NLI (Preventing PyTorch RAM Bloat)
- **The Gap**: Running a separate Natural Language Inference (NLI) model (like DeBERTa) locally to calculate the semantic delta for the Symmetry-Break Audit will instantly trigger an Out-Of-Memory (OOM) crash on the 14Gi RAM limit, as it requires loading a separate PyTorch/Transformers runtime.
- **The Mitigation**: **Context-Reusing LLM-NLI**. Instead of a separate NLI model, we reuse the *already loaded* GGUF model instance. We construct a highly-optimized, zero-shot system prompt (using the active context) to task the model with evaluating the logical contradiction between the two mirrored responses. This keeps the RAM overhead at exactly **0MB**.

---

## 3. The Full Path to Execution (M4 Sequentiality)

To implement Phase C without regression, the developer must follow this strict, chronological checklist:

### Step 1: The Somatic Anchor (Plumbing)
- [ ] Implement `llama_copy_state_data` and `llama_set_state_data` ctypes bindings in `NativeGGUFProvider`.
- [ ] Build the `Versioned State Wrapper` with **Binary Header Signature Validation** (git commit hash check).
- [ ] Implement `mmap`-based snapshot saving/loading to `data/entities/<entity>/snapshots/`.
- [ ] Verify zero-copy and $O(1)$ load times via `strace` (T-Somatic Gate).

### Step 2: The Associative Field (Plumbing)
- [ ] Implement contiguous C-buffer SDRs using `ctypes` in `src/omega/memory/`.
- [ ] Build the **Dynamic Sparsity Regulator** to maintain bit density at $\approx 2\%$.
- [ ] Implement Hamming Distance associative retrieval in `MemoryStore`.
- [ ] Verify cache-alignment and $O(1)$ lookup (T-SDR Gate).

### Step 3: The Dreaming Cycle (Metabolism)
- [ ] Spawn the Dreaming Cycle as a separate OS process with `os.nice(19)`.
- [ ] Implement the **Strict Idle-Lock** using `psutil` resource polling.
- [ ] Build the **Somatic Compression** pipeline (Lossy Episodic Caching).
- [ ] Verify that the background process pauses immediately upon foreground query arrival (T-Metabolism Gate).

### Step 4: The Symmetry Audit (Field)
- [ ] Implement the `SymmetryMode` (FAST/SLOW) toggle in `cvar_table`.
- [ ] Build the parallel Ma'at/Lilith mirrored inference loop.
- [ ] Implement the **Skeptical Circuit Breaker** to prevent infinite loops.
- [ ] Verify that `SymmetryBreakError` triggers and resolves correctly (T-Symmetry Gate).

---

## 4. Architectural Sign-Off
This Shadow Audit is the final, metacognitive lock on Phase C. With these four mitigations, the Cognitive Substrate is protected against segfaults, semantic collapse, amnesia, and infinite loops.

**The path is clear. The gates are set. Begin the work.**
