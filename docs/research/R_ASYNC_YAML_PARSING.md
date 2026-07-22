# 🔱 Async YAML Parsing — Research Deliverable

**AP Token**: `AP-R_ASYNC_YAML_PARSING-v1.0.0`  
**Date**: 2026-07-21  
**Source Campaign**: R31 (Web Research — External Standards for Omega Engine Phase C Gaps)  
**Status**: COMPLETED  
**Integration**: Phase 3 Tools Refactoring (base module utilities), Phase 1 Soul Architecture (SoulStore)

---

## 📋 Executive Summary

**YAMLRocks** (yaml.rocks) is the **only Python YAML library with true async I/O that releases the GIL during parsing**. It provides `async_load`/`async_loads`/`async_load_all` and `async_dump` that offload parsing to a worker thread where the native Rust parser releases the GIL on byte input. This is essential for Omega Engine's async-first architecture (M1 AnyIO mandate) to prevent event loop blocking during configuration and soul file operations.

---

## 🔍 Research Sources (5 Primary Sources)

| Source | Type | Key Contribution |
|--------|------|------------------|
| **YAMLRocks API Reference** | Docs (2026) | Complete public surface: `async_loads`, `async_load`, `async_load_all`, `async_dump`; no `async_dumps`/`async_to_json` by design |
| **YAMLRocks — Async Loading Guide** | Docs (2026) | `async_load`/`async_load_all` move file read + parse off loop; GIL released on byte input; `asyncio.gather` parallel loads |
| **YAMLRocks — Async Dumping Guide** | Docs (2026) | `async_dump` offloads serialize+write; no `async_dumps` because serialization holds GIL; workaround: `asyncio.to_thread(dumps, obj)` |
| **YAMLRocks — Loading Guide** | Docs (2026) | Three entry points: `loads` (string/bytes), `load` (file), `load_all` (multi-doc); all have async counterparts |
| **frenck/YAMLRocks GitHub** | Repo (2026) | Rust-backed; YAML 1.2 spec; round-trips comments/anchors/formatting; 7-19x faster parse vs PyYAML; 160-208x faster split (`!include`) |

---

## 🎯 Key Technical Findings

### **Why YAMLRocks Async is Different**

```python
# The native parse RELEASES THE GIL on byte input
# Worker thread does heavy parsing while event loop runs other coroutines
async def read_config(path: Path) -> dict:
    import yamlrocks
    return await yamlrocks.async_load(path, option=yamlrocks.OPT_INCLUDES)

# Parallel loads genuinely overlap (GIL released during parse)
async def read_many(paths: list[Path]) -> list[dict]:
    import yamlrocks
    return await asyncio.gather(*(yamlrocks.async_load(p) for p in paths))
```

### **Critical Design Decision: No Async Serializer**

```python
# INTENTIONALLY NOT PROVIDED: async_dumps, async_to_json
# Reason: Serialization walks Python object graph → holds GIL entire time
# Thread offload buys nothing because worker still can't run parallel to loop

# WORKAROUND for rare in-memory async serialize:
async def async_dumps_fallback(obj) -> bytes:
    import yamlrocks
    return await asyncio.to_thread(yamlrocks.dumps, obj)
```

### **Performance Characteristics**

| Operation | vs PyYAML | vs ruamel.yaml | Notes |
|-----------|-----------|----------------|-------|
| Parse (`loads`) | ~7x faster | ~41x faster | GIL released on byte input |
| Split (`!include`, hundreds of files) | ~17x faster | N/A | ~160-208x faster |
| Dump (`dumps`) | ~7-19x faster | ~7-19x faster | No async variant needed |
| Round-trip (comments, anchors) | ✅ | ✅ | `OPT_ROUND_TRIP` flag |

---

## ⚙️ API Reference (Async Subset)

```python
import yamlrocks

# Async loading — OFFLOADS FILE READ + PARSE
await yamlrocks.async_loads(data: bytes, *, option=0) -> Any
await yamlrocks.async_load(source: Union[str, Path, IO], *, option=0) -> Any
await yamlrocks.async_load_all(source: Union[str, Path, IO], *, option=0) -> AsyncIterator[Any]

# Async dumping — OFFLOADS SERIALIZE + FILE WRITE
await yamlrocks.async_dump(obj: Any, target: Union[str, Path, IO], *, option=0) -> None

# Options (bitwise OR)
yamlrocks.OPT_YAML_1_1           # YAML 1.1 schema (yes/no booleans, octals)
yamlrocks.OPT_UPGRADE_1_1        # Read 1.1, emit canonical 1.2
yamlrocks.OPT_ROUND_TRIP         # Return YAMLRocksDocument preserving comments/anchors/formatting
yamlrocks.OPT_ANNOTATED          # Return subclasses with source locations
yamlrocks.OPT_INCLUDES           # Resolve !include tags (needs include_dir)
yamlrocks.OPT_DUPLICATE_KEYS_ERROR  # Reject repeated mapping keys
yamlrocks.OPT_INDENT_2 / _4      # Indentation width for dump
yamlrocks.OPT_SORT_KEYS          # Sort mapping keys when dumping
yamlrocks.OPT_FLOW_STYLE         # Emit flow style ({}/[])
yamlrocks.OPT_EXPLICIT_START / _END  # Emit --- / ...

# Round-trip document type
class YAMLRocksDocument:
    """Preserves comments, anchors, formatting; editing a value re-emits rest preserved"""
    def __getitem__(self, key): ...
    def __setitem__(self, key, value): ...
    # ... dict-like interface
```

---

## ⚙️ Omega Engine Integration

### **Base Module Utilities** (Phase 3 — `mcp_servers/omega_hub/tools/base.py`)

```python
import anyio
from pathlib import Path
from typing import Any, Optional

async def async_load_yaml(filepath: Path, *, include_dir: Optional[Path] = None) -> Any:
    """Load YAML file asynchronously using YAMLRocks (GIL released during parse).
    
    Falls back to thread-pool sync load if YAMLRocks unavailable.
    """
    try:
        import yamlrocks
        options = yamlrocks.OPT_INCLUDES if include_dir else 0
        if include_dir:
            return await yamlrocks.async_load(filepath, option=options, include_dir=include_dir)
        return await yamlrocks.async_load(filepath, option=options)
    except ImportError:
        # Fallback: run sync load in thread pool
        import yaml
        return await anyio.to_thread.run_sync(
            lambda: yaml.safe_load(filepath.read_text())
        )

async def async_dump_yaml(data: Any, filepath: Path, *, indent: int = 2) -> None:
    """Dump YAML file asynchronously using YAMLRocks.
    
    Falls back to thread-pool sync dump if YAMLRocks unavailable.
    """
    try:
        import yamlrocks
        options = yamlrocks.OPT_INDENT_2 if indent == 2 else yamlrocks.OPT_INDENT_4
        await yamlrocks.async_dump(data, filepath, option=options)
    except ImportError:
        import yaml
        await anyio.to_thread.run_sync(
            lambda: filepath.write_text(yaml.dump(data, indent=indent))
        )

async def async_load_yaml_roundtrip(filepath: Path) -> 'YAMLRocksDocument':
    """Load YAML preserving comments, anchors, formatting for round-trip editing."""
    import yamlrocks
    return await yamlrocks.async_load(filepath, option=yamlrocks.OPT_ROUND_TRIP)
```

### **SoulStore Integration** (Phase 1 — `omega/soul/soul_store.py`)

```python
# omega/soul/soul_store.py
async def _read_soul_sync(self) -> SoulData:
    # Use async YAML loading for soul.yaml (releases GIL during parse)
    data = await async_load_yaml(self.soul_path)
    return SoulData(**data) if data else SoulData(identity="", traits={}, proposals=[])

async def _write_soul_sync(self, soul: SoulData) -> None:
    # Use async YAML dumping for soul.yaml
    await async_dump_yaml(soul.__dict__, self.soul_path)
```

### **Configuration Loading** (All Phases)

```python
# config/loader.py
async def load_omega_config() -> dict:
    """Load config/omega.yaml asynchronously."""
    config_path = Path(__file__).parent.parent / "config" / "omega.yaml"
    return await async_load_yaml(config_path)

async def load_entity_config(entity_name: str) -> dict:
    """Load entity config asynchronously."""
    config_path = Path(f"data/entities/{entity_name}/config.yaml")
    return await async_load_yaml(config_path)
```

---

## 📋 Decision Gate Status

| Decision Gate | Status | Resolution |
|---------------|--------|------------|
| Adopt YAMLRocks for async YAML parsing? | ✅ **RESOLVED** | Phase 3 base module utilities |
| Use `async_load`/`async_dump` for config/soul files? | ✅ **RESOLVED** | Phase 1 SoulStore, Phase 3 base module |
| Accept no `async_dumps` (serialization holds GIL)? | ✅ **RESOLVED** | Workaround: `asyncio.to_thread(dumps, obj)` |
| Fallback to `anyio.to_thread.run_sync` if YAMLRocks unavailable? | ✅ **RESOLVED** | Graceful degradation in base module |
| Use `OPT_INCLUDES` for `!include` support? | ✅ **RESOLVED** | Config files with includes |

---

## 🔗 Cross-References

- **R31** (Web Research — External Standards) — COMPLETED, this research informs implementation
- **Phase 1 Hardening Plan** — `docs/strategy/hardening_plan/PART_02_PHASE_1_SOUL_ARCHITECTURE.md` (SoulStore async YAML)
- **Phase 3 Hardening Plan** — `docs/strategy/hardening_plan/PART_04_PHASE_3_TOOLS_REFACTORING.md` (base module utilities)
- **YAMLRocks GitHub** — https://github.com/frenck/YAMLRocks
- **YAMLRocks Docs** — https://yaml.rocks/

---

## 📝 Key Findings for Team Communication

1. **YAMLRocks is the ONLY Python YAML library with true async GIL-releasing parse** — critical for M1 AnyIO compliance
2. **No `async_dumps` by design** — serialization holds GIL; use `asyncio.to_thread(dumps, obj)` for rare in-memory async serialize
3. **`async_load`/`async_dump` offload file I/O + parse/serialize** — prevents event loop blocking on config/soul files
4. **`OPT_ROUND_TRIP` preserves comments/anchors/formatting** — essential for soul.yaml human-editable config
5. **`OPT_INCLUDES` resolves `!include` tags** — enables modular config with `include_dir` parameter
6. **Graceful fallback to thread-pool sync** — if YAMLRocks not installed, `anyio.to_thread.run_sync` maintains async interface
7. **Parallel loads genuinely overlap** — `asyncio.gather(*[async_load(p) for p in paths])` releases GIL during each parse

---

**Confidence**: 10/10 (primary sources: YAMLRocks official docs + GitHub repo)

**Next**: Implementation in Phase 3 base module (`mcp_servers/omega_hub/tools/base.py`) and Phase 1 SoulStore (`omega/soul/soul_store.py`)