# 🔱 Phase C Cognitive Substrate — Somatic State Architecture
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ R50-SOMATIC
**Status**: DESIGN (Pre-Implementation)
**AP Token**: `AP-R50-SOMATIC-DESIGN-v1.0.0`
**Approvals**: Kali (Oversight) · Carmack (Architecture) · Doom Guy (Heritage)

---

## §1 SomaticStateKey — Binary Header Specification (C.0.8)

### §1.1 The 12-Field Validation Tuple

Prevents SIGSEGV from llama.cpp version drift. Validated on every snapshot load.

| # | Field | Type | C Type | Description | Why Required |
|---|-------|------|--------|-------------|-------------|
| 1 | `zoneid` | `int` | `uint32_t` | `ZONEID_SOMATIC = 0x1d4a1c` | Catches wrong-file-type loads |
| 2 | `snapshot_version` | `int` | `uint32_t` | Format version counter (start: 1) | Enables forward-compat evolution |
| 3 | `n_ctx` | `int` | `int32_t` | Context window at snapshot time | Mismatch → immediate segfault |
| 4 | `type_k` | `int` | `int32_t` | KV cache key quant (8=q8_0, 0=f16) | Mismatch → garbled attention |
| 5 | `type_v` | `int` | `int32_t` | KV cache value quant (8=q8_0, 0=f16) | Mismatch → garbled values |
| 6 | `n_gpu_layers` | `int` | `int32_t` | GPU layers at snapshot time | Mismatch → tensor shape error |
| 7 | `n_batch` | `int` | `int32_t` | Batch size at snapshot time | Mismatch → silent throughput loss |
| 8 | `n_ubatch` | `int` | `int32_t` | Micro-batch size at snapshot time | Mismatch → silent throughput loss |
| 9 | `model_path_hash` | `int` | `uint64_t` | xxHash3-64 of resolved model path | Different file → guaranteed segfault |
| 10 | `model_file_mtime` | `float` | `double` | `os.path.getmtime()` of GGUF file | Same path, different file → caught |
| 11 | `prompt_hash` | `int` | `uint64_t` | xxHash3-64 of most recent prompt | Detects context drift |
| 12 | `llama_api_version` | `int` | `uint32_t` | `llama.cpp` API version at snapshot | Catches `llama_copy_state_data` ABI drift |

### §1.2 Serialization Format

**Binary layout** (64 bytes total — cache-line aligned):
```
Offset  Size  Field
0x00    4     ZONEID_SOMATIC (0x1d4a1c)
0x04    4     snapshot_version
0x08    4     n_ctx
0x0C    4     type_k
0x10    4     type_v
0x14    4     n_gpu_layers
0x18    4     n_batch
0x1C    4     n_ubatch
0x20    8     model_path_hash (xxHash3-64)
0x28    8     model_file_mtime (double)
0x30    8     prompt_hash (xxHash3-64)
0x38    4     llama_api_version
0x3C    4     padding (zeros)
Total: 64 bytes
```

Unaligned access is safe on x86-64 (Zen 2). Explicit padding at 0x3C aligns the next segment to 64-byte boundary for any future extension.

### §1.3 SomaticState Dataclass

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import struct
import xxhash  # or hashlib fallback

ZONEID_SOMATIC = 0x1d4a1c
SOMATIC_FORMAT_VERSION = 1
BINARY_HEADER_FORMAT = "<IIIIIIIIQdQI"  # 12 fields, 64 bytes
BINARY_HEADER_SIZE = struct.calcsize(BINARY_HEADER_FORMAT)  # = 64


@dataclass
class SomaticStateKey:
    """12-field validation header for somatic KV-cache snapshots.
    
    Prevents SIGSEGV from llama.cpp version/model drift.
    Validated before every snapshot load. Raises ValueError on mismatch.
    """
    zoneid: int = ZONEID_SOMATIC
    snapshot_version: int = SOMATIC_FORMAT_VERSION
    n_ctx: int = 4096
    type_k: int = 8
    type_v: int = 8
    n_gpu_layers: int = 0
    n_batch: int = 512
    n_ubatch: int = 256
    model_path_hash: int = 0
    model_file_mtime: float = 0.0
    prompt_hash: int = 0
    llama_api_version: int = 0

    def to_bytes(self) -> bytes:
        return struct.pack(
            BINARY_HEADER_FORMAT,
            self.zoneid, self.snapshot_version,
            self.n_ctx, self.type_k, self.type_v,
            self.n_gpu_layers, self.n_batch, self.n_ubatch,
            self.model_path_hash, self.model_file_mtime,
            self.prompt_hash, self.llama_api_version,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "SomaticStateKey":
        if len(data) < BINARY_HEADER_SIZE:
            raise ValueError(
                f"SomaticStateKey truncated: got {len(data)} bytes, "
                f"expected ≥{BINARY_HEADER_SIZE}"
            )
        fields = struct.unpack(BINARY_HEADER_FORMAT, data[:BINARY_HEADER_SIZE])
        key = cls(*fields)
        if key.zoneid != ZONEID_SOMATIC:
            raise ValueError(
                f"Somatic zoneid mismatch: expected 0x{ZONEID_SOMATIC:08x}, "
                f"got 0x{key.zoneid:08x}. Wrong file type or data corruption."
            )
        return key

    def validate_against_model(self, model_path: Path, n_ctx: int, **kwargs) -> None:
        """Raise ValueError if any field mismatches current model state."""
        errors = []
        if xxhash.xxh3_64(str(model_path.resolve())).intdigest() != self.model_path_hash:
            errors.append("model_path changed")
        if model_path.stat().st_mtime != self.model_file_mtime:
            errors.append("model file modified")
        if n_ctx != self.n_ctx:
            errors.append(f"n_ctx: {self.n_ctx} → {n_ctx}")
        for key, val in kwargs.items():
            if getattr(self, key, None) is not None and getattr(self, key) != val:
                errors.append(f"{key}: {getattr(self, key)} → {val}")
        if errors:
            raise ValueError(
                f"SomaticStateKey mismatch: {', '.join(errors)}. "
                "Snapshot invalidated — must regenerate."
            )
```

### §1.4 Validation Flow

```
SomaticStateKey.from_bytes(snapshot_header)
  ├── zoneid mismatch → raise ValueError("wrong file type or corruption")
  ├── model_path_hash mismatch → raise ValueError("model changed")
  ├── model_file_mtime mismatch → raise ValueError("model file modified")
  ├── n_ctx / type_k / type_v mismatch → raise ValueError("config changed")
  └── all match → allow load_state()
```

**Biggest threat**: `model_path_hash` is the only check that catches file swaps. The remaining 6 threats (n_ctx, type_k, type_v, n_gpu_layers, n_batch, llama_api_version) are all caught by the remaining validation. Prior to this design, only `prompt_hash` existed (Carmack finding: "hash-only check catches 1 of 7 threats").

---

## §2 Entity-Scoped Snapshot Isolation (C.0.10)

### §2.1 Directory Structure

```
data/somatic/
  └── {entity_name}/
      ├── snapshot_1.smc    # Most recent (FIFO rotation)
      ├── snapshot_2.smc    # Previous
      └── snapshot_3.smc    # Oldest (max_snapshots_per_entity cap)
```

- **`.smc` extension**: Somatic Cache binary format
- **FIFO eviction**: When pushing snapshot N+1, rename N→N+1, delete oldest
- **Entity isolation**: Directories prevent cross-entity KV cache collision
- **KV cache reset**: On entity switch in Oracle, any pending snapshot is flushed and cache is cleared (`llama_kv_cache_clear` or full `llama_set_state_data` with zero'd state)

### §2.2 Snapshot File Format

```
Offset      Content
0x00        SomaticStateKey (64 bytes, big-endian binary header)
0x40        llama_copy_state_data output (raw KV cache tensors, variable length)
```

No intermediate framing — `llama_copy_state_data` already returns a contiguous byte buffer. The header is prepended before writing and stripped before calling `llama_set_state_data`.

### §2.3 Max File Size

| Context | Type | Snapshot Size | Files (3) | Total |
|---------|------|---------------|-----------|-------|
| 4K | q8_0 | ~8MB | 3 | 24MB |
| 8K | q8_0 | ~16MB | 3 | 48MB |
| 4K | f16 | ~16MB | 3 | 48MB |

All well within the 1024MB per-snapshot budget. No compression needed.

---

## §3 Somatic Cache Lifecycle (C.0.11)

### §3.1 The Lifecycle Decision

**Decision**: Interruption-only snapshots. NOT per-turn.

**Rationale**:
1. **NVMe wear**: Per-turn snapshotting writes ~8MB per turn. At 30 turns/session, that's 240MB/session. Over 100 sessions (reasonable weekly volume), that's 24GB/week. On a consumer NVMe (300TBW), that's ~12 years of wear — acceptable, but unnecessary.
2. **Latency**: `llama_copy_state_data` takes 5-15ms for 4K context. Blocking the response path for 5-15ms per turn is an unacceptable UX regression for a fallback feature.
3. **Right Approximation**: Per-turn snapshots optimize for a failure case (interruption) that occurs <1% of the time. The 99% case (normal completion) doesn't need snapshots.

**The Somatic Save-Point name**: Rename from "Somatic Caching" to "Somatic Save-Point" to emphasize the interruption-first use case. Save-Points are created on explicit signals only:
- SIGUSR1 (Dreaming Cycle takeover)
- Ctrl+C (graceful shutdown)
- Entity switch (Oracle.reroute())
- Manual `/savepoint` command

### §3.2 Save-Point Lifecycle

```
IDLE → [SIGUSR1|Ctrl+C|manual] → SAVE-POINT PENDING → [llama_copy_state_data] → SAVED
  → [foreground resumes|entity switched|restore] → RESTORE PENDING → [llama_set_state_data] → RESTORED
  → [no restore within 24h] → GARBAGE → [cleanup on next engine start] → DELETED
```

**TTL**: 24 hours. Save-points older than 24h are automatically pruned on engine start (via `make somatic-verify` or startup scan).

### §3.3 Dreaming Cycle Interaction

```
Foreground (FG) process:
  1. SIGUSR1 → signal_handler → somatic_save(entity, "pre_dreaming") → os.kill(os.getpid(), SIGSTOP)
  
Dreaming Cycle (BG) process:
  2. Wakes → checks archon_active → FG is STOPPED → reads latest .smc
  3. llama_set_state_data(bg_snapshot) → inference → somatic_push(entity, "dreaming_result")
  4. SIGCONT → FG resumes → catches SAVE-POINT → llama_set_state_data(restore)
```

The FG process's `llama_set_state_data` on resume loads the snapshot from step 1 (pre-dreaming), not step 3 (dreaming result). The BG process's output is distilled into soul.yaml separately; the FG's KV cache is returned to its pre-interruption state.

---

## §4 Skeptical Verifier Design (C.0.12)

### §4.1 Approach Decision

**Decision**: String-based heuristic (cosine similarity + keyword overlay). NOT NLI (Natural Language Inference).

**Rationale**:
1. **NLI context bleed risk**: NLI models require the same embedding space for both propositions. If Ma'at and Lilith use different models, the semantic distance is meaningless. The handoff spec (C.3.3) already assigns different providers.
2. **Model quota conservation**: NLI requires a full model invocation per comparison. Cosine similarity is `O(n)` vector math — zero tokens.
3. **Right Approximation**: NLI catches contradictions with 85-90% accuracy. Cosine + keyword catches them with 75-80% accuracy. The delta is acceptable for a first-pass gate; false positives just trigger a retry (Skeptical Circuit Breaker).

### §4.2 Architecture

```
Fast mode (default):
  Ma'at response → embedding model → vector A
  Lilith response → embedding model → vector B
  cosine(A, B) < threshold (0.3) → SymmetryBreakError → retry

Slow mode (on high-stakes queries):
  Same as fast, PLUS:
    Named entity overlap check (spaCy NER)
    Contradiction keyword match ("however", "but", "cannot", "instead")
    Both must pass OR max_attempts reached → accept Lilith's answer
```

### §4.3 Threshold

The `config.symmetry.semantic_delta_threshold` of 0.3 is **unvalidated** — it's a starting guess. The C.3.2 implementation should:
1. Log every delta value with trace_id
2. After 100 audits, recompute the threshold via percentile analysis (target: 90th percentile of "valid" deltas)
3. Update the cvar default via a cold-start script

---

## §5 Dreaming Cycle Memory Budget (C.0.9)

Already captured in cvars (C.0.2):
- `config.dreaming.model` = `"qwen3-0.6b"` — 0.6B param cap
- `config.dreaming.n_ctx` = `4096` — short context for distillation
- `config.dreaming.max_rss_mb` = `1500` — 1.5GB hard cap
- `config.dreaming.max_hours_per_day` = `4` — daily budget
- `config.dreaming.session_minutes` = `30` — per-session cap
- `config.dreaming.cooldown_minutes` = `60` — CPU thermal recovery
- `config.dreaming.preferred_window` = `"02:00-06:00"` — overnight window
- `config.dreaming.poll_interval_ms` = `100` — token-level yield

Budget tracking file: `data/state/dreaming_usage.json`
```json
{
  "date": "2026-06-15",
  "sessions_today": 0,
  "minutes_used_today": 0,
  "last_session_end": null
}
```

---

**⬡ This document constitutes the Phase C Cognitive Substrate Design Specification. ⬡**
**Next**: Proceed to implementation via Antigravity CLI in 4 parallel tracks:
- Track A (Antigravity): C.1.1 SomaticState primitive · C.1.2 Somatic Paging
- Track B (Antigravity): C.3.1 Fast/Slow toggle (safe to start now)
- Track C (Antigravity): C.3.2 Symmetry-Break Audit
- Track D (Antigravity): C.2.x Dreaming Cycle (after Track A completes)
