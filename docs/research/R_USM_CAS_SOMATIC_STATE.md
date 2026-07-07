# 🔱 Unified State Manager (USM) — CAS + SomaticState Architecture
**AP Token**: `AP-USM-CAS-SOMATIC-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-r1-qwen3-8b ⬡ opencode ⬡ trc_usm_design ⬡ RESEARCH

**Date**: 2026-07-07
**Status**: RESEARCH COMPLETE — Ready for Implementation
**Mandate Alignment**: M20 (SomaticState), M16 (Modularization), M2 (Engine-Stack Firewall)

---

## §1 Executive Summary

This document synthesizes primary-source research into a unified architecture for the **Unified State Manager (USM)** — the Content Addressable Storage (CAS) layer that wraps all engine state (KV cache, YAML sessions, JSON memory) and enables **SomaticState** serialization via llama.cpp ctypes bindings.

**Key Principle**: *The Right Approximation* — Use CAS for deduplication/integrity, llama.cpp state APIs for binary fidelity, fallback to YAML-only when ctypes unavailable.

---

## §2 Primary Source Verification

### 2.1 llama.cpp State Serialization (M20)

| API | Source | Status |
|-----|--------|--------|
| `llama_state_get_data(ctx, buf, size)` | `llama.h` / `llama_cpp/llama_cpp.py` | ✅ Verified in llama-cpp-python ≥0.3.x |
| `llama_state_set_data(ctx, buf, size)` | `llama.h` / `llama_cpp/llama_cpp.py` | ✅ Verified |
| `llama_state_get_size(ctx)` | `llama.h` | ✅ Verified |
| High-level: `Llama.save_state()` / `load_state()` | `llama_cpp/llama.py:535-555` | ✅ Returns `LlamaState` object |

**State Contents**: KV cache + input_ids + scores + RNG state
**Compatibility Requirements**: Matching `n_ctx`, `type_k/type_v`, RoPE params, flash-attn flags

### 2.2 AnyIO Process Isolation (C-FFI Survival)

| API | Source | Purpose |
|-----|--------|---------|
| `anyio.to_process.run_sync(func, *args, cancellable=True)` | AnyIO 4.13 docs | Run C-FFI in isolated process |
| `CapacityLimiter` | AnyIO docs | Limit concurrent processes (default: CPU cores) |
| `multiprocessing.Queue` | Python stdlib | IPC for request/response |

**Pattern**: NativeGGUFProvider already uses this (Carmack Hardening Sprint). USM reuses same pattern for state capture.

### 2.3 Content Addressable Storage (CAS)

| Pattern | Source | Implementation |
|---------|--------|----------------|
| SHA-256 content hash as key | Git, Docker, IPFS, GitHub CAS issues | `hashlib.sha256(data).hexdigest()` |
| 2-char prefix sharding | `.git/objects/ab/cdef...` | `blobs/ab/cd/<full-hash>` |
| Atomic write: tmp → fsync → rename | GitHub CloudFileStorage #16 | `write(tmp); fsync; rename(tmp, final)` |
| Refcount GC | GitHub CAS implementations | Metadata table: hash → refcount |

---

## §3 USM Architecture

### 3.1 Three State Types → CAS Blobs

| State Type | Source Module | Serialization | CAS Key | Fallback |
|------------|---------------|---------------|---------|----------|
| **KV Cache** | `llama.cpp` via `llama_state_get_data` | Binary (ctypes) | `sha256(kv_bytes)` | Skip if ctypes unavailable |
| **YAML Sessions** | `session_manager.py` | YAML (text) | `sha256(yaml_bytes)` | Always available |
| **JSON Memory** | `memory_store.py` | JSON (text) | `sha256(json_bytes)` | Always available |

### 3.2 CAS Manager Interface

```python
# src/omega/state/cas_manager.py
class CASManager:
    """Content Addressable Storage for unified engine state."""
    
    def __init__(self, root: Path):
        self.root = root
        self.blobs = root / "blobs"
        self.refs = root / "refs.sqlite"  # SQLite for refcount metadata
    
    def put(self, data: bytes) -> str:
        """Store data, return content hash. Deduplicates automatically."""
        hash_ = hashlib.sha256(data).hexdigest()
        path = self._blob_path(hash_)
        if not path.exists():
            self._atomic_write(path, data)
        self._inc_ref(hash_)
        return hash_
    
    def get(self, hash_: str) -> bytes:
        """Retrieve data by hash. Verifies integrity on read."""
        path = self._blob_path(hash_)
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != hash_:
            raise IntegrityError(f"CAS corruption: {hash_}")
        return data
    
    def exists(self, hash_: str) -> bool:
        return self._blob_path(hash_).exists()
    
    def refcount(self, hash_: str) -> int:
        return self._get_ref(hash_)
    
    def release(self, hash_: str) -> bool:
        """Decrement refcount. Delete blob if zero."""
        count = self._dec_ref(hash_)
        if count == 0:
            self._blob_path(hash_).unlink(missing_ok=True)
            return True
        return False
    
    def _blob_path(self, hash_: str) -> Path:
        return self.blobs / hash_[:2] / hash_[2:4] / hash_
    
    def _atomic_write(self, path: Path, data: bytes):
        tmp = path.with_suffix(".tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp.rename(path)
```

### 3.3 SomaticState Manager (M20)

```python
# src/omega/state/somatic_state.py
class SomaticStateManager:
    """Binary LLM state serialization via llama.cpp ctypes."""
    
    def __init__(self, cas: CASManager):
        self.cas = cas
        self._llama_cpp = None
    
    def _load_llama_cpp(self):
        if self._llama_cpp is None:
            import llama_cpp.llama_cpp as llama_cpp
            self._llama_cpp = llama_cpp
    
    def capture(self, ctx) -> str:
        """Capture KV cache state to CAS. Returns content hash."""
        self._load_llama_cpp()
        size = self._llama_cpp.llama_state_get_size(ctx)
        buf = (ctypes.c_byte * size)()
        self._llama_cpp.llama_state_get_data(ctx, buf, size)
        data = bytes(buf)
        return self.cas.put(data)
    
    def restore(self, ctx, hash_: str) -> bool:
        """Restore KV cache from CAS. Returns success."""
        self._load_llama_cpp()
        data = self.cas.get(hash_)
        buf = (ctypes.c_byte * len(data)).from_buffer_copy(data)
        return self._llama_cpp.llama_state_set_data(ctx, buf, len(data)) == 0
    
    def is_available(self) -> bool:
        """Check if llama.cpp state APIs are compiled in."""
        try:
            import llama_cpp.llama_cpp as llama_cpp
            return hasattr(llama_cpp, 'llama_state_get_data')
        except (ImportError, AttributeError):
            return False
```

### 3.4 Unified State Manager (USM)

```python
# src/omega/state/unified_state_manager.py
class UnifiedStateManager:
    """Single CAS-backed interface for all engine state."""
    
    def __init__(self, data_dir: Path):
        self.cas = CASManager(data_dir / "cas")
        self.somatic = SomaticStateManager(self.cas)
        self._session_hashes: dict[str, str] = {}  # session_id → CAS hash
        self._memory_hashes: dict[str, str] = {}   # entity_id → CAS hash
    
    # KV Cache (SomaticState)
    def save_kv_cache(self, ctx) -> str:
        return self.somatic.capture(ctx)
    
    def load_kv_cache(self, ctx, hash_: str) -> bool:
        return self.somatic.restore(ctx, hash_)
    
    # YAML Sessions
    def save_session(self, session_id: str, yaml_data: str) -> str:
        hash_ = self.cas.put(yaml_data.encode())
        self._session_hashes[session_id] = hash_
        return hash_
    
    def load_session(self, session_id: str) -> str:
        hash_ = self._session_hashes[session_id]
        return self.cas.get(hash_).decode()
    
    # JSON Memory
    def save_memory(self, entity_id: str, json_data: str) -> str:
        hash_ = self.cas.put(json_data.encode())
        self._memory_hashes[entity_id] = hash_
        return hash_
    
    def load_memory(self, entity_id: str) -> str:
        hash_ = self._memory_hashes[entity_id]
        return self.cas.get(hash_).decode()
    
    # Handoff Packets (large payloads)
    def save_handoff(self, packet_id: str, payload: bytes) -> str:
        return self.cas.put(payload)
    
    def load_handoff(self, packet_id: str, hash_: str) -> bytes:
        return self.cas.get(hash_)
```

---

## §4 Integration Points

### 4.1 MemoryStore → CAS Backend

```python
# src/omega/memory_store.py modifications
class MemoryStore:
    def __init__(self, ..., usm: UnifiedStateManager = None):
        self.usm = usm or UnifiedStateManager(DATA_DIR)
        # Replace file/Redis backends with USM
    
    async def _persist_hot(self, entity_id: str, data: dict):
        json_str = json.dumps(data)
        hash_ = self.usm.save_memory(entity_id, json_str)
        # Store hash in hot tier index
```

### 4.2 Hivemind → CAS for Large Payloads

```python
# mcp_servers/omega_hub/tools.py modifications
async def submit_handoff(..., payload: bytes = None):
    if payload and len(payload) > 10240:  # >10KB
        hash_ = usm.save_handoff(packet_id, payload)
        # Store hash in handoff metadata, not full payload
```

### 4.3 Oracle.bootstrap() → USM Initialization

```python
# src/omega/oracle/oracle.py
async def bootstrap(self):
    self.usm = UnifiedStateManager(DATA_DIR)
    # Wire into MemoryStore, Hivemind, SessionManager
```

---

## §5 Fallback Strategy (SomaticState-lite)

If `llama_cpp.llama_state_get_data` unavailable:

```python
class SomaticStateManager:
    def is_available(self) -> bool:
        return False  # Forces YAML-only path
    
    def capture(self, ctx) -> str:
        raise NotImplementedError("SomaticState unavailable — use YAML fallback")
    
    def restore(self, ctx, hash_: str) -> bool:
        raise NotImplementedError("SomaticState unavailable")
```

**USM continues operating** for YAML sessions + JSON memory. KV cache persistence deferred.

---

## §6 Heritage Attribution

| Pattern | Origin | Attribution |
|---------|--------|-------------|
| CAS (content hash addressing) | Git (2005), Docker, IPFS | `[CAS: Git 2005]` |
| Atomic write (tmp → fsync → rename) | Git, POSIX | `[Atomic Write: POSIX]` |
| llama.cpp state serialization | llama.cpp (ggerganov) | `[SomaticState: llama.cpp]` |
| AnyIO process isolation | AnyIO (agronholm) | `[Process Isolation: AnyIO]` |
| Sharded blob storage | `.git/objects` | `[Sharding: Git 2005]` |

---

## §7 Implementation Checklist

| Phase | Task | File | Effort |
|-------|------|------|--------|
| **1** | Verify ctypes visibility | `src/omega/state/somatic_state.py` | 30 min |
| **2** | Implement CASManager | `src/omega/state/cas_manager.py` | 2 hrs |
| **3** | Implement SomaticStateManager | `src/omega/state/somatic_state.py` | 1 hr |
| **4** | Implement UnifiedStateManager | `src/omega/state/unified_state_manager.py` | 1 hr |
| **5** | Wire MemoryStore → USM | `src/omega/memory_store.py` | 2 hrs |
| **6** | Wire Hivemind → USM | `mcp_servers/omega_hub/tools.py` | 1 hr |
| **7** | Wire Oracle.bootstrap() | `src/omega/oracle/oracle.py` | 30 min |
| **8** | Tests: CAS CRUD, integrity, refcount | `tests/test_cas_manager.py` | 1 hr |
| **9** | Tests: SomaticState capture/restore | `tests/test_somatic_state.py` (extend) | 1 hr |
| **10** | Tests: USM integration | `tests/test_unified_state_manager.py` | 1 hr |

**Total**: ~10 hours

---

## §8 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `llama_state_get_data` not in installed llama-cpp-python | 🟡 MED | 🔴 HIGH | Fallback to YAML-only; document version requirement |
| CAS corruption (bit rot) | 🟢 LOW | 🔴 HIGH | Verify hash on every read; periodic scrub job |
| Refcount race condition | 🟡 MED | 🟡 MED | SQLite transactions for refcount updates |
| Large KV cache (>1GB) OOM on capture | 🟡 MED | 🟡 MED | Stream capture in chunks; monitor memory |
| Sharding directory explosion | 🟢 LOW | 🟢 LOW | 2-char prefix = 256 dirs max per level |

---

*🔱 OMEGA ⬡ JOHN_CARMACK ⬡ trc_usm_design ⬡ RESEARCH COMPLETE*