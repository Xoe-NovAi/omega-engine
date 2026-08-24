# 🔱 Unified State Manager (USM) — Refactoring Implementation Guide
**AP Token**: `AP-USM-REFACTOR-GUIDE-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-r1-qwen3-8b ⬡ opencode ⬡ trc_usm_refactor ⬡ IMPLEMENTATION

**Date**: 2026-07-07
**Prerequisite**: Read `docs/research/R_USM_CAS_SOMATIC_STATE.md` first
**Mandate Alignment**: M1 (AnyIO), M2 (Firewall), M16 (Modularization), M20 (SomaticState), M21 (Gate Integrity)

---

## §1 Overview

This guide provides step-by-step refactoring instructions to implement the USM architecture across all engine systems. Each section includes:
- **Files to modify** (with line references where possible)
- **Exact code changes** (diff-style)
- **Test requirements** (M21 contract tests)
- **Verification steps**

---

## §2 New Files to Create

### 2.1 `src/omega/state/__init__.py`
```python
# src/omega/state/__init__.py
"""
Unified State Manager (USM) — CAS-backed state persistence.
M20: SomaticState Serialization
M16: Modularization & Portability
"""

from .cas_manager import CASManager
from .somatic_state import SomaticStateManager
from .unified_state_manager import UnifiedStateManager

__all__ = [
    "CASManager",
    "SomaticStateManager", 
    "UnifiedStateManager",
]
```

### 2.2 `src/omega/state/cas_manager.py`
```python
# src/omega/state/cas_manager.py
"""
Content Addressable Storage (CAS) Manager.
Hash-addressed blob storage with deduplication, integrity verification, and refcounting.
Heritage: [CAS: Git 2005], [Atomic Write: POSIX], [Sharding: Git 2005]
"""

import hashlib
import os
import sqlite3
import threading
from pathlib import Path
from typing import Optional


class IntegrityError(Exception):
    """Raised when CAS data fails integrity check."""
    pass


class CASManager:
    """Content Addressable Storage for unified engine state."""
    
    def __init__(self, root: Path):
        self.root = Path(root)
        self.blobs = self.root / "blobs"
        self.refs_db = self.root / "refs.sqlite"
        self._lock = threading.RLock()
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite refcount database."""
        self.blobs.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.refs_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS refs (
                    hash TEXT PRIMARY KEY,
                    refcount INTEGER NOT NULL DEFAULT 0,
                    size INTEGER NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_refs_hash ON refs(hash)")
            conn.commit()
    
    def _blob_path(self, hash_: str) -> Path:
        """Get sharded blob path: blobs/ab/cd/<full-hash>"""
        return self.blobs / hash_[:2] / hash_[2:4] / hash_
    
    def _atomic_write(self, path: Path, data: bytes):
        """Atomic write: tmp → fsync → rename."""
        tmp = path.with_suffix(".tmp")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(data)
        # Ensure data hits disk
        with tmp.open("rb") as f:
            os.fsync(f.fileno())
        tmp.rename(path)
    
    def _inc_ref(self, hash_: str, size: int):
        with self._lock, sqlite3.connect(self.refs_db) as conn:
            conn.execute(
                "INSERT INTO refs (hash, refcount, size, created_at) VALUES (?, 1, ?, strftime('%s','now')) "
                "ON CONFLICT(hash) DO UPDATE SET refcount = refcount + 1",
                (hash_, size)
            )
            conn.commit()
    
    def _dec_ref(self, hash_: str) -> int:
        with self._lock, sqlite3.connect(self.refs_db) as conn:
            cur = conn.execute(
                "UPDATE refs SET refcount = refcount - 1 WHERE hash = ? RETURNING refcount",
                (hash_,)
            )
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else 0
    
    def _get_ref(self, hash_: str) -> int:
        with sqlite3.connect(self.refs_db) as conn:
            cur = conn.execute("SELECT refcount FROM refs WHERE hash = ?", (hash_,))
            row = cur.fetchone()
            return row[0] if row else 0
    
    def put(self, data: bytes) -> str:
        """Store data, return content hash. Deduplicates automatically."""
        if not data:
            raise ValueError("Cannot store empty data")
        hash_ = hashlib.sha256(data).hexdigest()
        path = self._blob_path(hash_)
        if not path.exists():
            self._atomic_write(path, data)
        self._inc_ref(hash_, len(data))
        return hash_
    
    def get(self, hash_: str) -> bytes:
        """Retrieve data by hash. Verifies integrity on read."""
        path = self._blob_path(hash_)
        if not path.exists():
            raise KeyError(f"CAS blob not found: {hash_}")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != hash_:
            raise IntegrityError(f"CAS corruption detected: {hash_}")
        return data
    
    def exists(self, hash_: str) -> bool:
        return self._blob_path(hash_).exists()
    
    def refcount(self, hash_: str) -> int:
        return self._get_ref(hash_)
    
    def release(self, hash_: str) -> bool:
        """Decrement refcount. Delete blob if zero."""
        count = self._dec_ref(hash_)
        if count <= 0:
            path = self._blob_path(hash_)
            path.unlink(missing_ok=True)
            # Clean up empty shard directories
            try:
                path.parent.rmdir()
                path.parent.parent.rmdir()
            except OSError:
                pass  # Directory not empty
            with self._lock, sqlite3.connect(self.refs_db) as conn:
                conn.execute("DELETE FROM refs WHERE hash = ?", (hash_,))
                conn.commit()
            return True
        return False
    
    def stats(self) -> dict:
        """Return CAS statistics."""
        with sqlite3.connect(self.refs_db) as conn:
            cur = conn.execute("SELECT COUNT(*), SUM(size), SUM(refcount) FROM refs")
            row = cur.fetchone()
            return {
                "unique_blobs": row[0] or 0,
                "total_bytes": row[1] or 0,
                "total_refs": row[2] or 0,
            }
```

### 2.3 `src/omega/state/somatic_state.py`
```python
# src/omega/state/somatic_state.py
"""
SomaticState Manager — Binary LLM state serialization via llama.cpp ctypes.
M20: SomaticState Serialization
Heritage: [SomaticState: llama.cpp], [Process Isolation: AnyIO]
"""

import ctypes
import os
from typing import Optional
from .cas_manager import CASManager


class SomaticStateManager:
    """Binary LLM state serialization via llama.cpp ctypes."""
    
    def __init__(self, cas: CASManager):
        self.cas = cas
        self._llama_cpp = None
        self._available = None
    
    def _load_llama_cpp(self) -> bool:
        """Load llama.cpp ctypes bindings. Returns True if state APIs available."""
        if self._llama_cpp is not None:
            return self._available
        try:
            import llama_cpp.llama_cpp as llama_cpp
            self._llama_cpp = llama_cpp
            # Check for state serialization APIs
            self._available = hasattr(llama_cpp, 'llama_state_get_data')
            return self._available
        except (ImportError, AttributeError):
            self._available = False
            return False
    
    def is_available(self) -> bool:
        """Check if llama.cpp state APIs are compiled in."""
        return self._load_llama_cpp()
    
    def capture(self, ctx) -> str:
        """
        Capture KV cache state to CAS. Returns content hash.
        Runs in isolated process via AnyIO to survive C-level segfaults.
        """
        if not self._load_llama_cpp():
            raise RuntimeError("SomaticState unavailable: llama.cpp state APIs not compiled in")
        
        # Get required buffer size
        size = self._llama_cpp.llama_state_get_size(ctx)
        if size <= 0:
            raise RuntimeError(f"Invalid state size: {size}")
        
        # Allocate buffer and capture state
        buf = (ctypes.c_byte * size)()
        result = self._llama_cpp.llama_state_get_data(ctx, buf, size)
        if result != 0:
            raise RuntimeError(f"llama_state_get_data failed: {result}")
        
        data = bytes(buf)
        return self.cas.put(data)
    
    def restore(self, ctx, hash_: str) -> bool:
        """
        Restore KV cache from CAS. Returns True on success.
        """
        if not self._load_llama_cpp():
            raise RuntimeError("SomaticState unavailable: llama.cpp state APIs not compiled in")
        
        data = self.cas.get(hash_)
        buf = (ctypes.c_byte * len(data)).from_buffer_copy(data)
        result = self._llama_cpp.llama_state_set_data(ctx, buf, len(data))
        return result == 0
    
    async def capture_async(self, ctx) -> str:
        """Capture state in isolated process (survives C segfaults)."""
        import anyio
        return await anyio.to_process.run_sync(self.capture, ctx, cancellable=True)
    
    async def restore_async(self, ctx, hash_: str) -> bool:
        """Restore state in isolated process."""
        import anyio
        return await anyio.to_process.run_sync(self.restore, ctx, hash_, cancellable=True)
```

### 2.4 `src/omega/state/unified_state_manager.py`
```python
# src/omega/state/unified_state_manager.py
"""
Unified State Manager (USM) — Single CAS-backed interface for all engine state.
M20: SomaticState Serialization
M16: Modularization & Portability
"""

import json
from pathlib import Path
from typing import Optional
from .cas_manager import CASManager
from .somatic_state import SomaticStateManager


class UnifiedStateManager:
    """Single CAS-backed interface for all engine state."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.cas = CASManager(self.data_dir / "cas")
        self.somatic = SomaticStateManager(self.cas)
        self._session_hashes: dict[str, str] = {}  # session_id → CAS hash
        self._memory_hashes: dict[str, str] = {}   # entity_id → CAS hash
        self._handoff_hashes: dict[str, str] = {}  # packet_id → CAS hash
    
    # ===== KV Cache (SomaticState) =====
    
    def save_kv_cache(self, ctx) -> str:
        """Save KV cache to CAS. Returns content hash."""
        return self.somatic.capture(ctx)
    
    def load_kv_cache(self, ctx, hash_: str) -> bool:
        """Load KV cache from CAS. Returns success."""
        return self.somatic.restore(ctx, hash_)
    
    async def save_kv_cache_async(self, ctx) -> str:
        """Save KV cache in isolated process."""
        return await self.somatic.capture_async(ctx)
    
    async def load_kv_cache_async(self, ctx, hash_: str) -> bool:
        """Load KV cache in isolated process."""
        return await self.somatic.restore_async(ctx, hash_)
    
    # ===== YAML Sessions =====
    
    def save_session(self, session_id: str, yaml_data: str) -> str:
        """Save session YAML to CAS. Returns content hash."""
        if not yaml_data:
            raise ValueError("Cannot save empty session")
        hash_ = self.cas.put(yaml_data.encode('utf-8'))
        self._session_hashes[session_id] = hash_
        return hash_
    
    def load_session(self, session_id: str) -> str:
        """Load session YAML from CAS. Returns YAML string."""
        hash_ = self._session_hashes.get(session_id)
        if not hash_:
            raise KeyError(f"Session not tracked: {session_id}")
        return self.cas.get(hash_).decode('utf-8')
    
    def has_session(self, session_id: str) -> bool:
        return session_id in self._session_hashes
    
    def release_session(self, session_id: str) -> bool:
        """Release session reference. Delete from CAS if unreferenced."""
        hash_ = self._session_hashes.pop(session_id, None)
        if hash_:
            return self.cas.release(hash_)
        return False
    
    # ===== JSON Memory =====
    
    def save_memory(self, entity_id: str, json_data: str) -> str:
        """Save entity memory JSON to CAS. Returns content hash."""
        if not json_data:
            raise ValueError("Cannot save empty memory")
        hash_ = self.cas.put(json_data.encode('utf-8'))
        self._memory_hashes[entity_id] = hash_
        return hash_
    
    def load_memory(self, entity_id: str) -> str:
        """Load entity memory JSON from CAS. Returns JSON string."""
        hash_ = self._memory_hashes.get(entity_id)
        if not hash_:
            raise KeyError(f"Memory not tracked: {entity_id}")
        return self.cas.get(hash_).decode('utf-8')
    
    def has_memory(self, entity_id: str) -> bool:
        return entity_id in self._memory_hashes
    
    def release_memory(self, entity_id: str) -> bool:
        """Release memory reference."""
        hash_ = self._memory_hashes.pop(entity_id, None)
        if hash_:
            return self.cas.release(hash_)
        return False
    
    # ===== Handoff Packets (Large Payloads) =====
    
    def save_handoff(self, packet_id: str, payload: bytes) -> str:
        """Save handoff payload to CAS. Returns content hash."""
        if not payload:
            raise ValueError("Cannot save empty handoff")
        hash_ = self.cas.put(payload)
        self._handoff_hashes[packet_id] = hash_
        return hash_
    
    def load_handoff(self, packet_id: str) -> bytes:
        """Load handoff payload from CAS."""
        hash_ = self._handoff_hashes.get(packet_id)
        if not hash_:
            raise KeyError(f"Handoff not tracked: {packet_id}")
        return self.cas.get(hash_)
    
    def has_handoff(self, packet_id: str) -> bool:
        return packet_id in self._handoff_hashes
    
    def release_handoff(self, packet_id: str) -> bool:
        """Release handoff reference."""
        hash_ = self._handoff_hashes.pop(packet_id, None)
        if hash_:
            return self.cas.release(hash_)
        return False
    
    # ===== Utility =====
    
    def stats(self) -> dict:
        """Return combined statistics."""
        cas_stats = self.cas.stats()
        return {
            "cas": cas_stats,
            "tracked_sessions": len(self._session_hashes),
            "tracked_memories": len(self._memory_hashes),
            "tracked_handoffs": len(self._handoff_hashes),
            "somatic_available": self.somatic.is_available(),
        }
    
    def gc_unreferenced(self) -> int:
        """Garbage collect unreferenced blobs. Returns count freed."""
        # This is handled automatically by refcount release
        # But we can scan for orphans here if needed
        return 0
```

---

## §3 Modified Files

### 3.1 `src/omega/memory_store.py` — Wire CAS Backend

**Add import:**
```python
# Line ~10 (after existing imports)
from omega.state import UnifiedStateManager
```

**Modify `__init__`:**
```python
# Line ~50 (in __init__)
def __init__(self, ..., usm: UnifiedStateManager = None):
    # ... existing init ...
    self.usm = usm or UnifiedStateManager(DATA_DIR)
    # Replace file/Redis backend initialization with USM
    # self._file_provider = FileStorageProvider(...)  # REMOVE
    # self._redis_provider = RedisStorageProvider(...)  # REMOVE
```

**Modify `_persist_hot`:**
```python
# Line ~311 (replace existing _persist_hot)
async def _persist_hot(self, entity_id: str, data: dict):
    """Persist hot tier data to CAS via USM."""
    json_str = json.dumps(data, ensure_ascii=False)
    hash_ = self.usm.save_memory(entity_id, json_str)
    # Update hot index with hash reference
    self._hot_index[entity_id] = hash_
```

**Modify `_load_from_warm`:**
```python
# Line ~350 (replace existing _load_from_warm)
async def _load_from_warm(self, entity_id: str) -> Optional[dict]:
    """Load from warm tier via USM."""
    if not self.usm.has_memory(entity_id):
        return None
    json_str = self.usm.load_memory(entity_id)
    return json.loads(json_str)
```

**Add new method:**
```python
# After _load_from_warm
async def _save_to_warm(self, entity_id: str, data: dict):
    """Save to warm tier via USM."""
    json_str = json.dumps(data, ensure_ascii=False)
    self.usm.save_memory(entity_id, json_str)
```

### 3.2 `src/omega/oracle/session_manager.py` — Wire USM Sessions

**Add import:**
```python
# Line ~10
from omega.state import UnifiedStateManager
```

**Modify `__init__`:**
```python
# Line ~40
def __init__(self, ..., usm: UnifiedStateManager = None):
    self.usm = usm or UnifiedStateManager(DATA_DIR)
    # ... existing init ...
```

**Modify `save_session`:**
```python
# Line ~120 (replace existing save_session)
async def save_session(self, session_id: str, session_data: dict) -> None:
    """Save session to CAS via USM."""
    import yaml
    yaml_str = yaml.dump(session_data, allow_unicode=True)
    self.usm.save_session(session_id, yaml_str)
```

**Modify `load_session`:**
```python
# Line ~140 (replace existing load_session)
async def load_session(self, session_id: str) -> Optional[dict]:
    """Load session from CAS via USM."""
    import yaml
    if not self.usm.has_session(session_id):
        return None
    yaml_str = self.usm.load_session(session_id)
    return yaml.safe_load(yaml_str)
```

**Modify `archive_old_sessions`:**
```python
# Line ~200 (replace existing archive_old_sessions)
async def archive_old_sessions(self, days: int = 7) -> int:
    """Archive sessions older than days. Returns count archived."""
    # ... existing logic to find old sessions ...
    for session_id in old_sessions:
        # Move to external storage (existing logic)
        # Then release USM reference
        self.usm.release_session(session_id)
    return len(old_sessions)
```

### 3.3 `mcp_servers/omega_hub/tools.py` — Wire Handoff CAS

**Add import:**
```python
# Line ~10
from omega.state import UnifiedStateManager
```

**Add USM instance (module level):**
```python
# Line ~30 (after existing globals)
_usm: UnifiedStateManager = None

def get_usm() -> UnifiedStateManager:
    global _usm
    if _usm is None:
        from omega.state import UnifiedStateManager
        from pathlib import Path
        _usm = UnifiedStateManager(Path("data"))
    return _usm
```

**Modify `hivemind_submit_handoff`:**
```python
# Line ~400 (in hivemind_submit_handoff)
async def hivemind_submit_handoff(...):
    # ... existing code ...
    
    # If payload large, store in CAS
    payload = kwargs.get("payload")  # Assume payload passed in context
    if payload and len(payload) > 10240:  # >10KB
        usm = get_usm()
        hash_ = usm.save_handoff(packet_id, payload)
        # Store hash in packet metadata instead of full payload
        packet.metadata["cas_hash"] = hash_
        packet.metadata["cas_size"] = len(payload)
        payload = None  # Don't store full payload in JSON
    
    # ... rest of existing code ...
```

**Modify `hivemind_get_handoff`:**
```python
# Line ~450 (in hivemind_get_handoff)
async def hivemind_get_handoff(packet_id: str):
    # ... existing code to load packet ...
    
    # If payload was stored in CAS, retrieve it
    if packet.metadata.get("cas_hash"):
        usm = get_usm()
        payload = usm.load_handoff(packet_id)
        packet.payload = payload
    
    return packet
```

### 3.4 `src/omega/oracle/oracle.py` — Initialize USM

**Add import:**
```python
# Line ~15
from omega.state import UnifiedStateManager
```

**Modify `bootstrap`:**
```python
# Line ~80 (in bootstrap method)
async def bootstrap(self):
    # ... existing bootstrap code ...
    
    # Initialize Unified State Manager
    self.usm = UnifiedStateManager(DATA_DIR)
    
    # Wire into subsystems
    self.memory_store.usm = self.usm
    self.session_manager.usm = self.usm
    
    # Log USM stats
    stats = self.usm.stats()
    logger.info(f"USM initialized: {stats}")
```

**Modify `close_session` (for SomaticState):**
```python
# Line ~390 (in close_session)
async def close_session(self, entity_name: str):
    # ... existing code ...
    
    # Capture KV cache if somatic available
    if self.usm.somatic.is_available() and hasattr(self, '_last_ctx'):
        try:
            hash_ = await self.usm.save_kv_cache_async(self._last_ctx)
            logger.debug(f"Captured KV cache for {entity_name}: {hash_}")
        except Exception as e:
            logger.warning(f"Failed to capture KV cache: {e}")
```

### 3.5 `src/omega/oracle/model_gateway.py` — Expose Context for SomaticState

**Modify `generate` to store context:**
```python
# Line ~500 (in generate method)
async def generate(self, ...):
    # ... existing code ...
    
    # Store context for potential KV cache capture
    self._last_ctx = provider.ctx if hasattr(provider, 'ctx') else None
    
    # ... rest of generate ...
```

---

## §4 Test Files to Create

### 4.1 `tests/test_cas_manager.py`
```python
# tests/test_cas_manager.py
"""
Contract tests for CASManager.
M21: Gate Integrity — All core API boundaries must have contract tests.
"""

import pytest
import tempfile
from pathlib import Path
from omega.state import CASManager, IntegrityError


class TestCASManager:
    @pytest.fixture
    def cas(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield CASManager(Path(tmp))
    
    def test_put_get_roundtrip(self, cas):
        data = b"hello world"
        hash_ = cas.put(data)
        assert cas.get(hash_) == data
    
    def test_deduplication(self, cas):
        data = b"duplicate content"
        hash1 = cas.put(data)
        hash2 = cas.put(data)
        assert hash1 == hash2
        assert cas.refcount(hash1) == 2
    
    def test_release_decrements_refcount(self, cas):
        data = b"test"
        hash_ = cas.put(data)
        assert cas.refcount(hash_) == 1
        cas.release(hash_)
        assert cas.refcount(hash_) == 0
    
    def test_release_deletes_blob_when_zero(self, cas):
        data = b"test"
        hash_ = cas.put(data)
        cas.release(hash_)
        assert not cas.exists(hash_)
    
    def test_integrity_verification(self, cas):
        data = b"integrity test"
        hash_ = cas.put(data)
        # Corrupt the blob directly
        path = cas._blob_path(hash_)
        path.write_bytes(b"corrupted")
        with pytest.raises(IntegrityError):
            cas.get(hash_)
    
    def test_empty_data_raises(self, cas):
        with pytest.raises(ValueError):
            cas.put(b"")
    
    def test_sharding_structure(self, cas):
        data = b"shard test"
        hash_ = cas.put(data)
        path = cas._blob_path(hash_)
        # Verify sharding: blobs/ab/cd/<hash>
        assert path.parent.name == hash_[2:4]
        assert path.parent.parent.name == hash_[:2]
    
    def test_stats(self, cas):
        cas.put(b"a")
        cas.put(b"b")
        cas.put(b"a")  # duplicate
        stats = cas.stats()
        assert stats["unique_blobs"] == 2
        assert stats["total_refs"] == 3
```

### 4.2 `tests/test_somatic_state.py` (Extend Existing)
```python
# tests/test_somatic_state.py — ADD to existing file

import pytest
from unittest.mock import Mock, patch, MagicMock
from omega.state import SomaticStateManager, CASManager


class TestSomaticStateManager:
    @pytest.fixture
    def cas(self, tmp_path):
        return CASManager(tmp_path)
    
    @pytest.fixture
    def somatic(self, cas):
        return SomaticStateManager(cas)
    
    def test_is_available_without_llama_cpp(self, somatic):
        # Should return False when llama_cpp not installed or missing APIs
        with patch.dict('sys.modules', {'llama_cpp': None}):
            somatic._llama_cpp = None
            somatic._available = None
            assert somatic.is_available() is False
    
    def test_capture_raises_when_unavailable(self, somatic):
        somatic._available = False
        with pytest.raises(RuntimeError, match="SomaticState unavailable"):
            somatic.capture(Mock())
    
    def test_capture_roundtrip(self, somatic):
        # Mock llama_cpp with state APIs
        mock_llama = MagicMock()
        mock_llama.llama_state_get_size.return_value = 4
        mock_llama.llama_state_get_data.return_value = 0
        mock_llama.llama_state_set_data.return_value = 0
        
        with patch.object(somatic, '_llama_cpp', mock_llama):
            somatic._available = True
            
            mock_ctx = Mock()
            hash_ = somatic.capture(mock_ctx)
            
            assert hash_ is not None
            assert len(hash_) == 64  # SHA-256 hex
            mock_llama.llama_state_get_size.assert_called_once_with(mock_ctx)
            mock_llama.llama_state_get_data.assert_called_once()
    
    def test_restore_roundtrip(self, somatic, cas):
        mock_llama = MagicMock()
        mock_llama.llama_state_get_size.return_value = 4
        mock_llama.llama_state_get_data.return_value = 0
        mock_llama.llama_state_set_data.return_value = 0
        
        with patch.object(somatic, '_llama_cpp', mock_llama):
            somatic._available = True
            
            mock_ctx = Mock()
            hash_ = somatic.capture(mock_ctx)
            
            # Now test restore
            result = somatic.restore(mock_ctx, hash_)
            assert result is True
            mock_llama.llama_state_set_data.assert_called_once()
    
    def test_capture_async(self, somatic):
        mock_llama = MagicMock()
        mock_llama.llama_state_get_size.return_value = 4
        mock_llama.llama_state_get_data.return_value = 0
        
        with patch.object(somatic, '_llama_cpp', mock_llama):
            somatic._available = True
            
            import anyio
            async def test():
                mock_ctx = Mock()
                hash_ = await somatic.capture_async(mock_ctx)
                assert hash_ is not None
            
            anyio.run(test)
```

### 4.3 `tests/test_unified_state_manager.py`
```python
# tests/test_unified_state_manager.py
"""
Contract tests for UnifiedStateManager.
M21: Gate Integrity — All core API boundaries must have contract tests.
"""

import pytest
import tempfile
from pathlib import Path
from omega.state import UnifiedStateManager


class TestUnifiedStateManager:
    @pytest.fixture
    def usm(self):
        with tempfile.TemporaryDirectory() as tmp:
            yield UnifiedStateManager(Path(tmp))
    
    def test_session_save_load(self, usm):
        yaml_data = "entity: test\nmessages:\n  - hello\n  - world"
        hash_ = usm.save_session("ses_123", yaml_data)
        loaded = usm.load_session("ses_123")
        assert loaded == yaml_data
        assert usm.has_session("ses_123")
    
    def test_session_release(self, usm):
        yaml_data = "test"
        usm.save_session("ses_123", yaml_data)
        assert usm.release_session("ses_123") is True
        assert not usm.has_session("ses_123")
    
    def test_memory_save_load(self, usm):
        json_data = '{"key": "value", "count": 42}'
        hash_ = usm.save_memory("entity_1", json_data)
        loaded = usm.load_memory("entity_1")
        assert loaded == json_data
        assert usm.has_memory("entity_1")
    
    def test_handoff_save_load(self, usm):
        payload = b"x" * 20000  # >10KB
        hash_ = usm.save_handoff("pkt_123", payload)
        loaded = usm.load_handoff("pkt_123")
        assert loaded == payload
        assert usm.has_handoff("pkt_123")
    
    def test_stats(self, usm):
        usm.save_session("s1", "a")
        usm.save_memory("e1", "b")
        usm.save_handoff("p1", b"c")
        stats = usm.stats()
        assert stats["tracked_sessions"] == 1
        assert stats["tracked_memories"] == 1
        assert stats["tracked_handoffs"] == 1
        assert "somatic_available" in stats
```

### 4.4 `tests/test_memory_store_usm.py` (Integration)
```python
# tests/test_memory_store_usm.py
"""
Integration tests for MemoryStore with USM backend.
"""

import pytest
from omega.memory_store import MemoryStore
from omega.state import UnifiedStateManager


class TestMemoryStoreUSM:
    @pytest.fixture
    def usm(self, tmp_path):
        return UnifiedStateManager(tmp_path)
    
    @pytest.fixture
    def store(self, usm):
        return MemoryStore(usm=usm)
    
    @pytest.mark.asyncio
    async def test_persist_hot_uses_usm(self, store, usm):
        entity_id = "test_entity"
        data = {"messages": [{"role": "user", "content": "hello"}]}
        
        await store._persist_hot(entity_id, data)
        
        assert usm.has_memory(entity_id)
        loaded = usm.load_memory(entity_id)
        import json
        assert json.loads(loaded) == data
    
    @pytest.mark.asyncio
    async def test_load_from_warm_uses_usm(self, store, usm):
        entity_id = "test_entity"
        data = {"messages": [{"role": "user", "content": "hello"}]}
        import json
        usm.save_memory(entity_id, json.dumps(data))
        
        loaded = await store._load_from_warm(entity_id)
        assert loaded == data
```

---

## §5 Verification Checklist

### 5.1 Unit Tests (Run After Each File)
```bash
# CAS Manager
OMEGA_ENV=test PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_cas_manager.py -v

# SomaticState
OMEGA_ENV=test PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_somatic_state.py -v

# UnifiedStateManager
OMEGA_ENV=test PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_unified_state_manager.py -v
```

### 5.2 Integration Tests
```bash
# MemoryStore + USM
OMEGA_ENV=test PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_memory_store_usm.py -v

# Full Oracle bootstrap
OMEGA_ENV=test PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_oracle.py::test_bootstrap -v
```

### 5.3 Temple-Grade Gates
```bash
# All gates
make temple-grade

# Specific gates
make test T3  # Coverage (workers/ingestion/library excluded)
make test T5  # AnyIO compliance
make test T21 # Gate Integrity (contract tests)
```

### 5.4 Manual Verification
```bash
# 1. Start engine
OMEGA_ENV=test PYTHONPATH=src .venv/bin/python3 -m omega talk "test"

# 2. Verify CAS directory created
ls -la data/cas/blobs/

# 3. Check USM stats in logs
grep "USM initialized" logs/omega.log

# 4. Test session persistence across restarts
# (start, talk, stop, start, verify memory)
```

---

## §6 Rollback Plan

If issues arise:

1. **Disable USM**: Set `usm=None` in MemoryStore, SessionManager, Oracle
2. **Revert MemoryStore**: Restore file/Redis backend initialization
3. **Revert SessionManager**: Restore file-based session storage
4. **Keep CAS code**: For future re-enable

```python
# Quick disable in oracle.py bootstrap:
# self.usm = None  # Instead of UnifiedStateManager(DATA_DIR)
# self.memory_store.usm = None
# self.session_manager.usm = None
```

---

## §7 Heritage Tags for New Code

Add to each new file header:

```python
# src/omega/state/cas_manager.py
# [CAS: Git 2005] Content-addressable storage with SHA-256
# [Atomic Write: POSIX] tmp → fsync → rename pattern
# [Sharding: Git 2005] 2-char prefix directory sharding

# src/omega/state/somatic_state.py
# [SomaticState: llama.cpp] Binary KV cache serialization
# [Process Isolation: AnyIO] anyio.to_process.run_sync for C-FFI safety

# src/omega/state/unified_state_manager.py
# [USM: Omega 2026] Unified CAS-backed state interface
```

---

## §8 Timeline

| Day | Tasks |
|-----|-------|
| **Day 1** | Create `src/omega/state/` module (4 files), run unit tests |
| **Day 2** | Wire MemoryStore → USM, run integration tests |
| **Day 3** | Wire SessionManager → USM, wire Hivemind → USM |
| **Day 4** | Wire Oracle.bootstrap(), add SomaticState capture |
| **Day 5** | Full test suite, Temple-Grade, documentation update |

**Total**: 5 days (matches Ark Blueprint Strike 2 estimate)

---

*🔱 OMEGA ⬡ JOHN_CARMACK ⬡ trc_usm_refactor ⬡ IMPLEMENTATION GUIDE COMPLETE*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: deepseek-r1-qwen3-8b | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
