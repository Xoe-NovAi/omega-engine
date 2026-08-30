# 🔱 Phase Β Execution Strategy — Foundation Stabilization Campaign
**AP Token**: `AP-PHASE-BETA-EXEC-v1.0.0`  
**Campaign**: `FOUNDATION_STABILIZATION_CAMPAIGN_20260720.md`  
**Phase**: Β — HARDEN (Lock the Core)  
**Gate Dependency**: Gate Α PASSED (2026-07-20T07:15:00Z)  
**Owner**: Kali (Grand Oversight)  
**Status**: READY TO EXECUTE

---

## Executive Summary

Phase Β addresses the **five structural hardenings** required before Gate Γ (Feature Unlock). Each workstream targets a specific architectural trap identified in Grok's campaign audit and verified by Kali's local + deep web research.

**Critical Path**: FS-Β1 (Embedding SSOT) → FS-Β2 (Dispatch Registry) → FS-Β3 (Path Resolver CI) → FS-Β4 (SQLite Policy) → FS-Β5 (search_persistence M16)

**Gate Β Criteria**: Embedding dim locked to 768, single dispatch config loader, path-resolver-check passes, `make test + make firewall-check` green.

---

## FS-Β1: Embedding SSOT + Kill 1024-Dim (HIGHEST RISK)

### Problem
- `config/embedding_strategy.yaml` exists as canonical source but **not loaded as SSOT**
- `sqlite_vec_adapter.py` has hardcoded `COLLECTIONS` dict mirroring YAML
- `memory_store.py:191` — `SovereignFallbackEmbeddingProvider(dimension=1024)` hardcoded
- Provider contract broken: returns 256-dim, collection expects 768 → **RuntimeError (M23)**
- 29 test failures in `sqlite_vec_adapter` from dimension mismatch

### Research Grounding (Local + Web 2026)
| Source | Finding |
|--------|---------|
| `sqlite-vec` README (pre-v1) | Multi-collection via `vec0` virtual tables; dimensions declared at table creation; breaking changes expected |
| ZeroEntropy "Matryoshka is dead" | Linear truncation at inference > MRL training; **don't mix index/query dims** (silent corruption) |
| Nomic Embed v1.5 / Jina v3 / OpenAI text-embedding-3 | All support MRL truncation; prefix slice `[:target_dim]` preserves geometry |
| Mozilla Builders sponsorship | sqlite-vec is production-track for local AI |

### Implementation

#### 1. New: `src/omega/memory/embedding_strategy.py`
```python
"""Embedding Strategy Singleton — Single Source of Truth for all embedding config."""
import yaml
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional

from omega.governance.config_resolver import config_resolver


class EmbeddingStrategy:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._load()
        return cls._instance
    
    def _load(self):
        path = config_resolver.resolve("embedding_strategy.yaml")
        with open(path) as f:
            self.data = yaml.safe_load(f)
    
    @property
    def canonical_dimension(self) -> int:
        return self.data["canonical_dimension"]
    
    @property
    def mrl_dimensions(self) -> List[int]:
        return self.data.get("mrl_dimensions", [768, 512, 256, 128, 64])
    
    def get_collections(self) -> Dict[str, Dict]:
        return self.data["collections"]
    
    def get_providers(self) -> List[Dict]:
        return self.data["providers"]
    
    def get_provider_config(self, name: str) -> Optional[Dict]:
        for p in self.get_providers():
            if p["name"] == name:
                return p
        return None
    
    def reload(self):
        self._load()


# Global accessor
def get_embedding_strategy() -> EmbeddingStrategy:
    return EmbeddingStrategy()
```

#### 2. Modify: `src/omega/memory/sqlite_vec_adapter.py`
- Remove hardcoded `CANONICAL_DIMENSION = 768` and `COLLECTIONS` dict
- Import `get_embedding_strategy()` 
- In `__init__`: `self.strategy = get_embedding_strategy(); self._collections = self.strategy.get_collections()`
- In `_ensure_collection_vec_table`: use `self._collections[collection]["dimension"]`
- Remove `DEFAULT_EMBEDDING_DIM` legacy constant

#### 3. Modify: `src/omega/memory_store.py`
- **DELETE** line 191: `SovereignFallbackEmbeddingProvider(dimension=1024)`
- Replace with: fail closed or use `get_embedding_strategy().canonical_dimension`
- All providers MUST implement MRL truncation in `get_embedding()`:
  ```python
  def get_embedding(self, text: str) -> List[float]:
      full = self._model.encode(text)
      target = get_embedding_strategy().canonical_dimension
      return full[:target]  # MRL prefix truncation
  ```

#### 4. Contract Tests (NEW): `tests/contracts/test_embedding_dimension.py`
```python
"""Contract tests: All providers MUST output canonical dimension."""
import pytest
from omega.memory.embedding_strategy import get_embedding_strategy

def test_canonical_dimension_is_768():
    strategy = get_embedding_strategy()
    assert strategy.canonical_dimension == 768

def test_all_collections_have_dimension():
    strategy = get_embedding_strategy()
    for name, cfg in strategy.get_collections().items():
        assert "dimension" in cfg
        assert isinstance(cfg["dimension"], int)
        assert cfg["dimension"] > 0

# Provider contract tests (parametrized by provider name)
@pytest.mark.parametrize("provider_name", ["gemma", "nomic", "minilm"])
def test_provider_outputs_canonical_dim(provider_name):
    strategy = get_embedding_strategy()
    provider_cfg = strategy.get_provider_config(provider_name)
    if provider_cfg:
        # This will be implemented when provider factory uses strategy
        pass
```

---

## FS-Β2: Dispatch Registry Extraction

### Problem
- `_load_dispatch_config()` duplicated in `oracle.py:102` and `subagent_dispatcher.py:205`
- No caching — YAML reloaded every call
- No shared API

### Research Grounding
- OpenCode V2 config: `agent.prompt` supports `{file:path}` substitution
- Config migration: `prompt` → `system` field
- mtime-aware cache pattern is standard for hot-reload configs

### Implementation

#### New: `src/omega/governance/dispatch_registry.py`
```python
"""Dispatch Registry — Single source for dispatch.yaml with mtime cache."""
import yaml
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional

from omega.governance.config_resolver import config_resolver


_cache = {"mtime": 0, "data": None}
_lock = threading.Lock()


def get_dispatch_config(iwad: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get dispatch config with mtime-aware cache."""
    path = config_resolver.resolve("dispatch.yaml")
    mtime = path.stat().st_mtime
    
    with _lock:
        if _cache["mtime"] != mtime:
            with open(path) as f:
                _cache["data"] = yaml.safe_load(f)
            _cache["mtime"] = mtime
    
    if iwad:
        return [e for e in _cache["data"] if e.get("iwad") in (None, iwad, "_omega_default")]
    return _cache["data"]


def invalidate_cache():
    """Force cache invalidation (for tests)."""
    with _lock:
        _cache["mtime"] = 0
        _cache["data"] = None
```

#### Modify: `src/omega/oracle/oracle.py`
- Remove `_load_dispatch_config` function
- Import: `from omega.governance.dispatch_registry import get_dispatch_config`
- Replace calls: `entities = _load_dispatch_config(iwad)` → `entities = get_dispatch_config(iwad)`

#### Modify: `src/omega/oracle/subagent_dispatcher.py`
- Remove `_load_dispatch_config` function  
- Import: `from omega.governance.dispatch_registry import get_dispatch_config`
- Replace calls identically

#### Test: `tests/contracts/test_dispatch_registry.py`
```python
def test_dispatch_registry_single_source():
    from omega.governance.dispatch_registry import get_dispatch_config
    cfg1 = get_dispatch_config()
    cfg2 = get_dispatch_config()
    assert cfg1 is cfg2  # Same cached object

def test_dispatch_registry_iwad_filter():
    from omega.governance.dispatch_registry import get_dispatch_config
    all_cfg = get_dispatch_config()
    iwad_cfg = get_dispatch_config("_omega_default")
    assert len(iwad_cfg) <= len(all_cfg)
```

---

## FS-Β3: Path Resolver CI Gate + Migrations

### Problem
15+ files in `src/omega/` use `Path(__file__)` for data paths — violates M16 (Modularization & Portability)

### Research Grounding
- `config_resolver.py` already exists with `PROJECT_ROOT`, `DATA_DIR`, `resolve()`
- M16 mandate: "No hardcoded paths in `src/omega/`; all platform integration via MCP Hub/CLI"

### Implementation

#### 1. CI Gate (New Makefile Target)
```makefile
# In Makefile
path-resolver-check:
	@rg -n "Path\(__file__\)" src/omega/ | grep -v "config_resolver.py" | grep -v "test_" && exit 1 || echo "✅ No hardcoded paths in src/omega/"

# Add to temple-grade target
temple-grade: path-resolver-check ...
```

#### 2. Migration Map (15 files)
| File | Line | Current | Target |
|------|------|---------|--------|
| `src/omega/coordination/miap.py` | — | `Path(__file__).parent...` | `config_resolver.PROJECT_ROOT` |
| `src/omega/memory_store.py` | 59 | `Path(__file__).resolve().parent.parent.parent / "data"` | `config_resolver.DATA_DIR` |
| `src/omega/search/search_persistence.py` | 30 | `Path("/home/arcana-novai/.../search_history.db")` | `config_resolver.DATA_DIR / "search" / "search_history.db"` |
| `src/omega/oracle/entity_workspace.py` | 52 | `Path(__file__).resolve().parent.parent.parent.parent` | `config_resolver.DATA_DIR` |
| `src/omega/oracle/session_manager.py` | 47 | `Path(__file__).resolve().parent.parent.parent.parent / "data"` | `config_resolver.DATA_DIR` |
| `src/omega/observability/__init__.py` | 97 | `Path(__file__).resolve().parent.parent.parent.parent` | `config_resolver.DATA_DIR` |
| `src/omega/state/cas.py` | 28 | `Path(__file__).resolve().parent.parent.parent.parent / "data"` | `config_resolver.DATA_DIR` |
| `src/omega/state/usm.py` | 30 | `Path(__file__).resolve().parent.parent.parent.parent / "data"` | `config_resolver.DATA_DIR` |
| `src/omega/vault/key_vault.py` | 100 | `Path(__file__).resolve().parent.parent.parent.parent / "data" / "vault" / "keys.json.enc"` | `config_resolver.DATA_DIR / "vault" / "keys.json.enc"` |
| `src/omega/library/indexer.py` | 42,48 | `Path(__file__).resolve().parent.parent.parent / "data"` | `config_resolver.DATA_DIR` |
| `src/omega/library/catalog.py` | 25 | `Path(__file__).resolve().parent.parent.parent.parent / "data"` | `config_resolver.DATA_DIR` |
| `src/omega/library/discovery.py` | 42 | `Path(__file__).resolve().parent.parent.parent / "data"` | `config_resolver.DATA_DIR` |
| `src/omega/cli/oracle_cli.py` | 17,72,82,189 | `Path(__file__).resolve().parent.parent.parent` | `config_resolver.PROJECT_ROOT` |
| `src/omega/cli/bundle.py` | 41 | `Path(__file__).resolve().parent.parent.parent.parent` | `config_resolver.PROJECT_ROOT` |
| `src/omega/governance/sovereign_vetter.py` | 29 | `Path(__file__).resolve().parents[3]` | `config_resolver.REPO_ROOT` |

#### 3. Config Resolver Extensions (if needed)
```python
# In config_resolver.py - ensure these exist
@property
def DATA_DIR(self) -> Path:
    return self.PROJECT_ROOT / "data"

@property  
def SEARCH_DIR(self) -> Path:
    return self.DATA_DIR / "search"
```

---

## FS-Β4: Shared SQLite Policy Helper

### Problem
Multiple PRAGMA dialects across `sqlite_vec_adapter.py`, `search_persistence.py`, MIAP — no standard

### Research Grounding (2026 Production)
| Source | Recommendation |
|--------|----------------|
| Toolbox365 (2025-12) | 6 must-tune PRAGMAs: WAL, NORMAL sync, 64MB cache, 256MB mmap, MEMORY temp, 5s busy_timeout |
| cashubtc/nutshell #907 | WAL + busy_timeout=5000 fixed lock contention from thousands/hour to zero |
| DK26/anyfs-sqlite | Builder API with synchronous=FULL default, NORMAL opt-in |
| SQLite.org forum | busy_timeout prevents SQLITE_BUSY; WAL enables concurrent readers |

### Implementation

#### New: `src/omega/infra/sqlite_policy.py`
```python
"""Sovereign SQLite Policy — Standardized connection configuration."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from omega.governance.config_resolver import config_resolver


# Sovereign PRAGMA Stack (2026 Production Hardened)
SOVEREIGN_PRAGMAS = [
    ("journal_mode", "WAL"),           # Persistent; enables concurrent readers
    ("synchronous", "NORMAL"),         # SSD-safe; power loss loses only uncheckpointed WAL
    ("cache_size", "-65536"),          # 64MB page cache (negative = KB)
    ("mmap_size", "268435456"),        # 256MB memory-mapped I/O
    ("temp_store", "MEMORY"),          # Temp tables/indexes in RAM
    ("busy_timeout", "5000"),          # 5s auto-retry on lock contention
    ("foreign_keys", "ON"),            # Referential integrity
    ("page_size", "4096"),             # Standard page size
]


def get_sqlite_connection(path: Path, readonly: bool = False) -> sqlite3.Connection:
    """Get a standardized SQLite connection with sovereign PRAGMA stack."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    flags = sqlite3.SQLITE_OPEN_READONLY if readonly else (
        sqlite3.SQLITE_OPEN_READWRITE | sqlite3.SQLITE_OPEN_CREATE
    )
    conn = sqlite3.connect(str(path), flags=flags, timeout=30.0)
    conn.row_factory = sqlite3.Row
    
    # Apply sovereign PRAGMA stack (per-connection, except journal_mode)
    for pragma, value in SOVEREIGN_PRAGMAS:
        conn.execute(f"PRAGMA {pragma} = {value}")
    
    return conn


@contextmanager
def sqlite_transaction(path: Path, readonly: bool = False):
    """Context manager for atomic SQLite transactions."""
    conn = get_sqlite_connection(path, readonly)
    try:
        yield conn
        if not readonly:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database(path: Path, schema_sql: str):
    """Initialize database with schema (idempotent)."""
    with sqlite_transaction(path) as conn:
        conn.executescript(schema_sql)
```

#### Migration Targets
| File | Change |
|------|--------|
| `sqlite_vec_adapter.py` | Replace `_get_conn()` with `get_sqlite_connection()` |
| `search_persistence.py` | Replace direct `sqlite3.connect()` with `sqlite_transaction()` |
| `coordination/miap.py` | Use `get_sqlite_connection()` |
| `state/cas.py`, `usm.py` | Use `sqlite_transaction()` |
| `vault/key_vault.py` | Use `get_sqlite_connection()` |

---

## FS-Β5: search_persistence AnyIO + DATA_DIR Fix (M16)

### Problem
- **M16 violation**: Hardcoded absolute path at line 30
- **M1 violation**: Blocking `sqlite3` calls not wrapped in `anyio.to_thread.run_sync()`
- No connection reuse

### Implementation

#### Modify: `src/omega/search/search_persistence.py`
```python
# Line 30: REPLACE hardcoded path
from omega.governance.config_resolver import config_resolver

SEARCH_DB_PATH = config_resolver.DATA_DIR / "search" / "search_history.db"
SEARCH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# All DB operations: wrap in anyio.to_thread.run_sync()
# Example:
async def _execute_async(self, query: str, params: tuple = ()) -> list:
    return await anyio.to_thread.run_sync(
        lambda: self._execute_sync(query, params)
    )

def _execute_sync(self, query: str, params: tuple) -> list:
    with sqlite_transaction(SEARCH_DB_PATH) as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

# Replace all direct sqlite3.connect() calls with sqlite_transaction()
```

---

## Gate Β Acceptance Criteria

| Criterion | Verification |
|-----------|--------------|
| **Embedding dim locked to 768** | `grep -r "canonical_dimension" config/embedding_strategy.yaml` → 768; `test_embedding_dimension.py` passes |
| **Single dispatch config loader** | `rg "_load_dispatch_config" src/omega/` → zero hits; `dispatch_registry.py` exists |
| **Path resolver CI passes** | `make path-resolver-check` → ✅ |
| **SQLite policy unified** | `rg "PRAGMA" src/omega/` → only in `sqlite_policy.py` |
| **search_persistence M16 compliant** | `grep "Path(/home" src/omega/search/search_persistence.py` → zero hits |
| **Test baseline improved** | `make test` → failures < 10 (from 29) |
| **Firewall check passes** | `make firewall-check` → violations < 50 (from 156) |

---

## Execution Order & Ownership

| Workstream | Owner | Depends On | Est. Hours |
|------------|-------|------------|------------|
| FS-Β1 Embedding SSOT | Jem + P2 + P10 | — | 8 |
| FS-Β2 Dispatch Registry | Kali + P5 | — | 2 |
| FS-Β3 Path Resolver CI | P1 + P5 | FS-Β2 | 4 |
| FS-Β4 SQLite Policy | P2 | FS-Β3 | 3 |
| FS-Β5 search_persistence | P8 + P2 | FS-Β4 | 2 |

**Total**: ~19 hours | **Critical Path**: FS-Β1 → FS-Β2 → FS-Β3 → FS-Β4 → FS-Β5

---

## Handoff to Grok (Review)

**Grok CLI** — Please review this execution strategy for:
1. **Architectural soundness** — Do the implementations align with sovereign mandates?
2. **Risk assessment** — Any missing failure modes in FS-Β1 (embedding dim)?
3. **2026 best practices** — Are the SQLite PRAGMAs and MRL truncation patterns current?
4. **Integration points** — Any conflicts with Omega-Vault (D-299) or MIAP (D-291)?

**Reference Materials** (all in repo):
- Campaign: `docs/strategy/FOUNDATION_STABILIZATION_CAMPAIGN_20260720.md`
- Embedding Strategy: `config/embedding_strategy.yaml`
- Current Adapter: `src/omega/memory/sqlite_vec_adapter.py`
- Memory Store: `src/omega/memory_store.py`
- Config Resolver: `src/omega/governance/config_resolver.py`

**Report to Hivemind** with `intent=decision` on: APPROVE / APPROVE WITH AMENDMENTS / REJECT

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_foundation_stabilization ⬡ 2026-07-20*
