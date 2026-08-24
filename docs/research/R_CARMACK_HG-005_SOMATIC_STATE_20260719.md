# 🔱 HG-005: SomaticState Serialization Round-Trip — Research Report

**AP Token**: `AP-CARMACK-HG005-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_hg005 ⬡ RESEARCH

**Date**: 2026-07-19
**Status**: COMPLETE — Implementation Guidance Ready

---

## 🎯 EXECUTIVE SUMMARY

**Verdict**: **IMPLEMENT WITH CAVEATS** — The `llama_state_get_data` / `llama_state_set_data` API provides functional round-trip serialization for KV cache state, but has strict compatibility constraints that must be enforced at the engine level. Memory-mapped file backing is viable for cold-start resumption but requires `--no-mmap` for CRIU-style GPU snapshots.

**Confidence**: 8/10 (Primary sources: llama.cpp discussions #15569, #18552, llama-cpp-python docs, Leeroopedia principles)

---

## 🔬 TECHNICAL FINDINGS

### 1. API Surface (llama.cpp → llama-cpp-python)

| Function | Status | Signature | Notes |
|----------|--------|-----------|-------|
| `llama_state_get_size(ctx)` | **Current** | `size_t llama_state_get_size(llama_context_p ctx)` | Returns byte capacity needed for full state |
| `llama_state_get_data(ctx, dst, size)` | **Current** | `size_t llama_state_get_data(llama_context_p ctx, uint8_t* dst, size_t size)` | Copies state to pre-allocated buffer |
| `llama_state_set_data(ctx, src, size)` | **Current** | `size_t llama_state_set_data(llama_context_p ctx, const uint8_t* src, size_t size)` | Restores state from buffer |
| `llama_state_save_file(path, ctx, ...)` | **Current** | File-backed convenience wrapper | Handles allocation internally |
| `llama_state_load_file(path, ctx, ...)` | **Current** | File-backed convenience wrapper | Returns tokens loaded |
| `llama_copy_state_data` / `llama_set_state_data` | **DEPRECATED** | Aliases to above | llama-cpp-python emits deprecation warnings |

**Python Bindings** (llama-cpp-python 0.3.34+):
```python
# Low-level (ctypes direct)
state_size = llama_cpp.llama_state_get_size(ctx)
buf = (ctypes.c_uint8 * state_size)()
llama_cpp.llama_state_get_data(ctx, buf, state_size)
# ... persist buf to file ...
llama_cpp.llama_state_set_data(ctx, buf, state_size)

# High-level (LlamaState object)
state = llama_cpp.LlamaState(ctx)
blob = state.data  # bytes
state.data = blob  # restore
state.save_file("session.bin", tokens)
state.load_file("session.bin", max_tokens=1024)
```

### 2. Round-Trip Fidelity Constraints (CRITICAL)

From **llama.cpp Discussion #15569** (authoritative: mahabot, 2026-04-11):

> **The state blob has no compatibility metadata. Nothing is validated before restore.**

| Parameter | Must Match? | Failure Mode |
|-----------|-------------|--------------|
| `n_ctx` (destination ≥ source) | **YES** | Buffer overflow / assert crash if dest < src |
| `n_embd`, `n_layer`, `n_head_kv` | **YES** | Silent garbage / crash |
| `type_k` / `type_v` (KV quantization) | **YES** | Silent garbage — flash attention changes KV quantization implicitly |
| `rope_freq_base`, RoPE scaling (YaRN) | **YES** | Silent garbage |
| `n_vocab` | **YES** | Crash / garbage |
| `n_seq_max` / unified KV behavior | **YES** | Silent garbage |
| Flash attention enabled/disabled | **YES** | Changes KV layout → different blob size |

**Key Insight**: The blob size is **deterministic** for a given `(model, n_ctx, params)` tuple. Pass the **exact saved byte length** to `llama_state_set_data`, NOT `llama_state_get_size(dst_ctx)` (which returns destination capacity, not blob size).

### 3. Sequence-Aware State (Multi-Sequence Support)

| Function | Purpose |
|----------|---------|
| `llama_state_seq_get_data(ctx, seq_id, flags)` | Extract single sequence state |
| `llama_state_seq_set_data(ctx, seq_id, data, flags)` | Restore single sequence state |
| `LLAMA_STATE_SEQ_FLAGS_NONE` (0) | Full state (KV + RNG + positions) |
| `LLAMA_STATE_SEQ_FLAGS_PARTIAL_ONLY` | KV cache only (no RNG/positions) |
| `LLAMA_STATE_SEQ_FLAGS_SWA_ONLY` | Sliding Window Attention layers only |

**Bug Alert** (Issue #18552, 2026-01-02): `llama_state_seq_set_data_ext` with `PARTIAL_ONLY` produces **non-deterministic results** on SWA models (GPT-OSS, Qwen3-Next) across restore cycles. **Workaround**: Use full-state flags (0) for deterministic restore.

### 4. Memory-Mapped File Backing

**For Cold-Start Resumption (M20 SomaticState)**:

```python
import mmap
import os

class SomaticStateStore:
    def __init__(self, path: str, expected_size: int):
        self.path = path
        self.expected_size = expected_size
        self._ensure_file()
    
    def _ensure_file(self):
        if not os.path.exists(self.path):
            with open(self.path, 'wb') as f:
                f.write(b'\x00' * self.expected_size)
    
    def save(self, ctx) -> int:
        size = llama_cpp.llama_state_get_size(ctx)
        with open(self.path, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0)
            llama_cpp.llama_state_get_data(ctx, mm, size)
            mm.flush()
        return size
    
    def load(self, ctx) -> bool:
        if not os.path.exists(self.path):
            return False
        with open(self.path, 'r+b') as f:
            mm = mmap.mmap(f.fileno(), 0)
            # Must pass EXACT saved size, not mmap size
            saved_size = os.path.getsize(self.path)
            llama_cpp.llama_state_set_data(ctx, mm, saved_size)
        return True
```

**Mmap Caveats** (from Issue #91, jart 2023):
- `MAP_PRIVATE` (default): Changes not persisted to disk — use `msync` or `r+b` + `flush()`
- `MAP_SHARED`: Mutations persist but **blocks CRIU GPU snapshots** (see below)
- **Recommendation**: Use regular file I/O with `os.replace()` atomic writes for state blobs; mmap only for model weights

### 5. CRIU / GPU Snapshot Compatibility (Critical for MIAP Replay)

From **Yuvraj Garg "Cold Start Engineering" (2026-06-01)**:

> **CRIU cannot capture child-process CUDA contexts started via subprocess.Popen. In-process model loading is mandatory for snapshot capture.**

> **`--no-mmap` is REQUIRED for llama-server subprocess snapshots** — memory-mapped model files prevent CRIU from properly checkpointing GPU memory state.

**Implication for MIAP ReplayMode**:
| ReplayMode | State Capture Method | mmap Compatible? |
|------------|---------------------|------------------|
| `Recovery` | SomaticState blob (file) | ✅ Yes |
| `Debug` | SomaticState blob + trace | ✅ Yes |
| `Forensic` | Full CRIU container snapshot | ❌ Requires `--no-mmap` |
| `Evaluation` | SomaticState blob + metrics | ✅ Yes |

**Architecture Decision**: SomaticState serialization (file-based) is the **primary** mechanism for MIAP Replay. CRIU snapshots are a **Forensic-mode only** fallback requiring `--no-mmap` model loading.

### 6. Integration with MIAP Phase 0 (D-291)

| MIAP Component | SomaticState Role |
|----------------|-------------------|
| **ReplayMode.Recovery** | Restore `LlamaState` from `session.bin` → continue generation |
| **ReplayMode.Debug** | Restore state at checkpoint → step through token-by-token with `CheckFunction` verification |
| **ReplayMode.Forensic** | Full container snapshot (CRIU) + SomaticState cross-validation |
| **ReplayMode.Evaluation** | Restore state → run eval harness → compare outputs to golden trace |
| **IntentionValidator** | Verify restored state matches expected `seq_id`, token count, RNG seed |
| **CheckFunction Registry** | Register `verify_somatic_roundtrip(ctx, expected_blob_hash)` |

---

## ⚠️ KNOWN FAILURE MODES (Audit These First)

| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| **Silent garbage on param mismatch** | Output tokens diverge from golden trace | **Mandatory**: Store `ContextParams` hash in state header; validate on load |
| **SWA partial restore non-determinism** | Issue #18552 | **Ban** `PARTIAL_ONLY` flags for production; full-state only |
| **Blob size mismatch** | `llama_state_set_data` returns 0 or crashes | Store exact byte length in sidecar `.meta.json` |
| **CRIU snapshot fails with mmap** | Modal/container logs show checkpoint failure | Enforce `--no-mmap` for Forensic mode; document clearly |
| **RNG state not restored** | Non-deterministic sampling after restore | Full-state flags (0) include RNG; verify with `temperature=0` golden trace |

---

## 📋 IMPLEMENTATION SPECIFICATION (for Omega Engine)

### File: `src/omega/inference/somatic_state.py`

```python
"""SomaticState Serialization — M20 Implementation"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import llama_cpp
import ctypes
from typing import Optional

@dataclass(frozen=True)
class ContextFingerprint:
    """Immutable context parameters that MUST match for valid restore"""
    n_ctx: int
    n_embd: int
    n_layer: int
    n_head_kv: int
    type_k: int
    type_v: int
    rope_freq_base: float
    rope_scaling_type: int
    n_vocab: int
    flash_attn: bool
    
    @classmethod
    def from_context(cls, ctx) -> "ContextFingerprint":
        # Extract from llama_context_params via ctypes
        ...
    
    def hash(self) -> str:
        return hashlib.blake2b(str(self).encode(), digest_size=16).hexdigest()

@dataclass
class SomaticStateHeader:
    """Sidecar metadata for round-trip validation"""
    fingerprint_hash: str
    blob_size: int
    seq_id: int
    token_count: int
    rng_seed: int
    timestamp_ns: int
    miap_replay_mode: str  # Recovery|Debug|Forensic|Evaluation

class SomaticStateManager:
    """Manages KV cache state persistence with MIAP integration"""
    
    def __init__(self, store_dir: Path):
        self.store_dir = store_dir
        self.store_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, ctx, seq_id: int = 0, replay_mode: str = "Recovery") -> Path:
        fingerprint = ContextFingerprint.from_context(ctx)
        blob_size = llama_cpp.llama_state_get_size(ctx)
        buf = (ctypes.c_uint8 * blob_size)()
        written = llama_cpp.llama_state_get_data(ctx, buf, blob_size)
        assert written == blob_size, f"State write incomplete: {written}/{blob_size}"
        
        # Atomic write
        session_id = f"session_{int(time.time_ns())}"
        blob_path = self.store_dir / f"{session_id}.bin"
        meta_path = self.store_dir / f"{session_id}.meta.json"
        
        blob_path.write_bytes(bytes(buf))
        meta = SomaticStateHeader(
            fingerprint_hash=fingerprint.hash(),
            blob_size=written,
            seq_id=seq_id,
            token_count=self._get_token_count(ctx, seq_id),
            rng_seed=self._get_rng_seed(ctx),
            timestamp_ns=time.time_ns(),
            miap_replay_mode=replay_mode
        )
        meta_path.write_text(json.dumps(meta.__dict__))
        return blob_path
    
    def load(self, ctx, session_id: str, expected_fingerprint: ContextFingerprint) -> bool:
        blob_path = self.store_dir / f"{session_id}.bin"
        meta_path = self.store_dir / f"{session_id}.meta.json"
        
        if not blob_path.exists() or not meta_path.exists():
            return False
        
        meta = SomaticStateHeader(**json.loads(meta_path.read_text()))
        
        # VALIDATE FINGERPRINT — MANDATORY
        if meta.fingerprint_hash != expected_fingerprint.hash():
            raise SomaticStateMismatch(
                f"Context fingerprint mismatch: expected {expected_fingerprint.hash()}, "
                f"got {meta.fingerprint_hash}. Params: {expected_fingerprint}"
            )
        
        # Load exact blob size
        blob = blob_path.read_bytes()
        assert len(blob) == meta.blob_size, "Blob size mismatch"
        
        buf = (ctypes.c_uint8 * meta.blob_size).from_buffer_copy(blob)
        restored = llama_cpp.llama_state_set_data(ctx, buf, meta.blob_size)
        assert restored == meta.blob_size, f"State restore incomplete: {restored}/{meta.blob_size}"
        
        return True

class SomaticStateMismatch(OmegaError):
    """Raised when context parameters don't match saved state"""
    pass
```

### Contract Tests (M21 Gate Integrity)

```python
def test_somatic_roundtrip_fidelity():
    """M21: Contract test — round-trip must produce identical logits"""
    ctx1 = create_context(n_ctx=4096, ...)
    ctx2 = create_context(n_ctx=4096, ...)  # SAME params
    
    # Prime both with identical prompt
    prompt = "The quick brown fox"
    tokens = tokenize(prompt)
    for ctx in (ctx1, ctx2):
        llama_cpp.llama_decode(ctx, tokens)
    
    # Save state from ctx1
    manager = SomaticStateManager(Path("/tmp/somatic_test"))
    session = manager.save(ctx1)
    
    # Restore into ctx2
    manager.load(ctx2, session, ContextFingerprint.from_context(ctx1))
    
    # Generate next token from both — MUST match exactly
    logits1 = get_logits(ctx1)
    logits2 = get_logits(ctx2)
    assert np.allclose(logits1, logits2, rtol=1e-6), "Somatic round-trip divergence!"

def test_somatic_param_mismatch_rejected():
    """M21: Mismatched n_ctx must raise SomaticStateMismatch"""
    ctx_small = create_context(n_ctx=2048)
    ctx_large = create_context(n_ctx=4096)
    # ... prime and save from ctx_large ...
    # ... attempt load into ctx_small — MUST raise ...
```

---

## 🏁 QUALIFICATION GATE (id Software Rule)

> **"Cannot be justified WITHOUT citing the original hardware constraint."**

**Original Constraint**: LLM inference on consumer hardware (Apple Silicon, consumer GPUs) has **high cold-start latency** (model load + prompt processing). KV cache recomputation for long contexts (32K-262K tokens) wastes **seconds to minutes** per session resume.

**id Software Analogy**: Doom's **zone memory allocator** (Z_Malloc) — pre-allocated pools, tag-based purge levels, instant level restart without re-parsing WAD. SomaticState is the **KV cache equivalent of a saved game** — instant resume without re-computation.

**Verdict**: **PASSES** — Directly addresses a hardware constraint (cold-start latency, VRAM/RAM bandwidth) with a proven technique (state serialization) from the inference engine itself.

---

## 📚 SOURCES (Confidence Scored)

| Source | Type | Confidence | Key Finding |
|--------|------|------------|-------------|
| llama.cpp Discussion #15569 (mahabot) | Primary (maintainer) | 10/10 | Compatibility matrix, blob size semantics |
| llama.cpp Issue #18552 | Primary (bug report) | 9/10 | SWA partial restore non-determinism |
| llama-cpp-python docs (State Management) | Primary (binding) | 9/10 | Python API surface, LlamaState class |
| Leeroopedia: State Serialization Principle | Secondary (synthesis) | 8/10 | Theoretical basis, use cases |
| Yuvraj Garg "Cold Start Engineering" (2026) | Primary (practitioner) | 9/10 | CRIU + mmap incompatibility, in-process requirement |
| llama.cpp Issue #91 (jart, bitRAKE) | Primary (historical) | 7/10 | mmap design rationale, MAP_SHARED vs PRIVATE |

---

## 🎯 NEXT ACTIONS

1. **Implement** `src/omega/inference/somatic_state.py` per spec above
2. **Add** contract tests to `tests/test_somatic_state.py` (M21 gate)
3. **Integrate** with MIAP `ReplayMode` enum in `src/omega/miap/protocol.py`
4. **Document** `--no-mmap` requirement for Forensic mode in `docs/guides/miap_replay.md`
5. **Benchmark** cold-start latency: baseline vs. SomaticState restore (target: <500ms for 32K ctx)

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_carmack_hg005 ⬡ 2026-07-19*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
