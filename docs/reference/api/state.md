# 🔱 State — Unified State Manager (USM) & Somatic Serialization
**AP Token**: `AP-STATE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the State package — Unified State Manager (CAS + SQLite index) and SomaticState binary LLM serialization.
**Tags**: state, usm, cas, somatic, serialization, llama.cpp, persistence
**Cross-references**: src/omega/state/usm.py, src/omega/state/cas.py, src/omega/state/somatic_state.py, src/omega/state/__init__.py, docs/architecture/ORACLE_DEEP_DIVE.md

---

## Overview

The `state` package provides **persistent state management** for the Omega Engine through two complementary systems:

1. **Unified State Manager (USM)** — High-level interface using Content Addressable Storage (CAS) + SQLite index for sessions, memories, handoffs
2. **SomaticState Manager** — Binary LLM state serialization via llama.cpp ctypes for KV cache capture/restore (M20)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      State Package                           │
├─────────────────────────────────────────────────────────────┤
│  usm.py              │  USMManager — CAS + SQLite index     │
│  cas.py              │  CASManager — SHA-256 blob storage   │
│  somatic_state.py    │  SomaticStateManager — llama.cpp     │
│  __init__.py         │  Singleton access + convenience      │
└─────────────────────────────────────────────────────────────┘
```

**Data Flow**:
```
Application → USMManager.save_state() → CASManager.put() → Blob (SHA-256)
                                      → SQLite index.update()
                                      
Application → SomaticStateManager.capture() → llama.cpp state API → CAS
```

---

## CASManager (cas.py)

Content Addressable Storage — immutable, deduplicated blob storage addressed by SHA-256.

### Constructor

```python
CASManager(base_dir: Optional[Path] = None)
```
Default: `data/state/blobs/`

### Methods

#### `async initialize() -> None`
Ensure blob directory exists (sharded: `blobs/ab/cd/<full-hash>`).

#### `async put(data: bytes) -> str`
Store data, return SHA-256 hash. **Deduplicated** — returns existing hash if already stored.

```python
cas = CASManager()
hash_ = await cas.put(b"Hello, World!")
# "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
```

**Atomic Write**: Writes to `.tmp` then renames.

#### `async get(blob_hash: str) -> bytes`
Retrieve data for hash. **Verifies integrity** (re-computes SHA-256).

```python
data = await cas.get(hash_)
# b"Hello, World!"
```

#### `async exists(blob_hash: str) -> bool`
Check if blob exists.

#### `async delete(blob_hash: str) -> None`
Delete blob. **Note**: Full USM would use reference counting.

#### `async stats() -> dict`
```python
{
    "unique_blobs": 1247,
    "total_bytes": 52428800,
    "total_refs": 1247  # Approximation (no refcount DB yet)
}
```

### Sharding

Blobs stored in 256×256 subdirectories: `blobs/{hash[:2]}/{hash[2:4]}/{hash}` — prevents directory bloat.

---

## USMManager (usm.py)

Unified State Manager — coordinates CAS and SQLite index for high-level state types.

### Constructor

```python
USMManager(base_dir: Optional[Path] = None)
```
Default base: `data/state/` (CAS at `data/state/blobs/`, index at `data/state/index.db`)

### Initialization

```python
usm = USMManager()
await usm.initialize()  # Creates CAS + SQLite index
```

**Index Schema** (`data/state/index.db`):
```sql
CREATE TABLE state_refs (
    key TEXT PRIMARY KEY,           -- "session:ses_123", "mem:prometheus", "handoff:ho_abc"
    hash TEXT NOT NULL,             -- CAS blob hash
    timestamp TEXT NOT NULL,        -- ISO 8601
    metadata TEXT                   -- Reserved
);
```

Uses `sqlite_policy` **metrics profile** for connections.

---

### Core Methods

#### `async save_state(key: str, data: Any) -> str`
Serialize → CAS → Index. Returns blob hash.

```python
hash_ = await usm.save_state("session:ses_123", {"messages": [...], "metadata": {...}})
```

**Serialization**: JSON (UTF-8) for non-bytes; pass-through for bytes.

#### `async load_state(key: str) -> Any`
Index → CAS → Deserialize. Returns `None` if not found.

```python
session_data = await usm.load_state("session:ses_123")
# {"messages": [...], "metadata": {...}}
```

**Deserialization**: Tries JSON first, falls back to raw bytes.

#### `async exists(key: str) -> bool`
Check if key exists in index.

#### `async snapshot(keys: List[str]) -> str`
Create manifest of multiple keys → store manifest in CAS → return manifest hash.

```python
manifest_hash = await usm.snapshot(["session:ses_123", "mem:prometheus", "handoff:ho_abc"])
```

#### `async restore_snapshot(manifest_hash: str) -> Dict[str, str]`
Restore snapshot → update index to point to snapshot's hashes.

```python
restored = await usm.restore_snapshot(manifest_hash)
# {"session:ses_123": "hash1", "mem:prometheus": "hash2", ...}
```

---

### Convenience Methods (Typed State)

#### Sessions
```python
await usm.save_session(session_id: str, yaml_data: str) -> str
await usm.load_session(session_id: str) -> str
usm.has_session(session_id: str) -> bool
await usm.release_session(session_id: str) -> bool
```

#### Memories
```python
await usm.save_memory(entity_id: str, json_data: str) -> str
await usm.load_memory(entity_id: str) -> str
usm.has_memory(entity_id: str) -> bool
await usm.release_memory(entity_id: str) -> bool
```

#### Handoffs
```python
await usm.save_handoff(packet_id: str, payload: bytes) -> str
await usm.load_handoff(packet_id: str) -> bytes
usm.has_handoff(packet_id: str) -> bool
await usm.release_handoff(packet_id: str) -> bool
```

---

### Statistics

```python
stats = await usm.stats()
# {
#   "cas": {"unique_blobs": 1247, "total_bytes": 52428800, "total_refs": 1247},
#   "tracked_sessions": 42,
#   "tracked_memories": 18,
#   "tracked_handoffs": 156,
#   "somatic_available": False
# }
```

---

## SomaticStateManager (somatic_state.py)

**M20: SomaticState Serialization** — Binary LLM state capture/restore via llama.cpp ctypes.

### Constructor

```python
SomaticStateManager(cas: CASManager)
```

### Availability Check

```python
manager = SomaticStateManager(cas)
if manager.is_available():
    # llama.cpp compiled with state APIs
else:
    # Not available — skip somatic ops
```

**Requires**: `llama_cpp` with `llama_state_get_data` / `llama_state_set_data` / `llama_state_get_size` symbols.

---

### Capture (Save KV Cache)

```python
# ctx = llama.cpp context pointer
hash_ = await manager.capture(ctx)
# Returns CAS blob hash
```

**Process Isolation** (survives C-level segfaults):
```python
hash_ = await manager.capture_async(ctx)
# Runs in ProcessPoolExecutor(max_workers=1)
```

### Restore (Load KV Cache)

```python
success = await manager.restore(ctx, hash_)
# True if restored successfully
```

**Process Isolation**:
```python
success = await manager.restore_async(ctx, hash_)
```

---

## Singleton Access

```python
from omega.state import get_usm, initialize_usm, reset_usm

# Get singleton
usm = get_usm()

# Initialize at startup
await initialize_usm()

# Reset for testing
await reset_usm()
```

---

## Usage Example

```python
from omega.state import get_usm, initialize_usm
from omega.state.cas import CASManager
from omega.state.somatic_state import SomaticStateManager

# Initialize at startup
await initialize_usm()
usm = get_usm()

# Save session
session_yaml = """
session_id: ses_abc123
entity: Prometheus
messages:
  - role: user
    content: Harden the container
  - role: assistant
    content: Implementing Mandate 2 firewall...
"""
hash_ = await usm.save_session("ses_abc123", session_yaml)
print(f"Session saved: {hash_}")

# Load session
loaded = await usm.load_session("ses_abc123")
print(f"Loaded: {loaded[:100]}...")

# Save entity memory
memory_json = '{"facts": ["M2: Engine-Stack Firewall", "M7: Local-First"], "updated": "2026-10-02"}'
await usm.save_memory("prometheus", memory_json)

# Somatic state (if available)
cas = CASManager()
somatic = SomaticStateManager(cas)
if somatic.is_available():
    # Capture KV cache after inference
    kv_hash = await somatic.capture_async(llama_context)
    print(f"Somatic state captured: {kv_hash}")
    
    # Restore for next session
    await somatic.restore_async(llama_context, kv_hash)
```

---

## Mandate Compliance

| Mandate | USM | SomaticState |
|---------|-----|--------------|
| **M1 AnyIO** | All async; blocking I/O in threads | `anyio.to_thread` for ctypes |
| **M7 Local-First** | Local CAS + SQLite | llama.cpp local |
| **M11 Soul Integrity** | Session persistence for distillation | Cold-start resumption |
| **M13 Temple-Grade** | Atomic writes (tmp→rename); integrity verify | Process isolation for C safety |
| **M20 Somatic Serialization** | N/A | ✅ Binary KV cache capture/restore |
| **M23 Failure Integrity** | Re-raises on CAS/index errors | Segfault isolation via ProcessPool |

---

## Heritage

- [id-soft: vet-015] ZONEID Pattern — hash as ultimate integrity marker
- [SomaticState: llama.cpp] Binary state serialization
- [Process Isolation: AnyIO] Survive C-level segfaults
- [CAS: Git 2005] Content-addressable storage

---

## Testing

```bash
pytest tests/test_cas.py tests/test_usm.py tests/test_somatic_state.py -v
```

Key test scenarios:
- CAS put/get/exists/delete
- CAS deduplication
- CAS integrity verification
- USM save/load/snapshot/restore
- USM typed convenience methods
- SomaticState availability check
- SomaticState capture/restore (with mock llama.cpp)
- Process isolation survival

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ STATE-v1.0.0 ⬡ 2026-10-02 ⬡*