# API Reference: Entity Registry

> EntityRegistry — YAML-backed entity management with id Software heritage patterns.

---

## Entity

**File**: `src/omega/oracle/entity_registry.py`

A user-definable entity (e.g., a Pillar Keeper, custom persona, or free agent). It separates structural engine concerns from modifiable game/personality concerns using hard boundaries.

### Fields

#### Engine Zone (Structural, Read-Only)
These fields define the identity and structure of the entity. They are protected from modifications by game logic.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *Required* | Unique name of the entity. |
| `domains` | `List[str]` | *Required* | List of semantic domains this entity handles. |
| `model` | `str` | *Required* | Model name/ID preferred by this entity. |
| `capabilities` | `List[str]` | `[]` | Capabilities this entity possesses (e.g., `"search"`, `"code"`). |
| `role` | `Optional[str]` | `None` | Role description of the entity. |
| `container` | `bool` | `False` | True if this entity runs inside an isolated container. |
| `port` | `Optional[int]` | `None` | Port number if this is a containerized entity. |
| `wad_source` | `Optional[str]` | `None` | Name of the WAD file/directory that loaded this entity. |
| `priority` | `int` | `0` | Layer priority for Shadow-Stacking. |
| `slots` | `List[str]` | `[]` | Dynamic slots occupied by this entity (e.g., `["P1"]`). |

#### Game Zone (Writable)
These fields define the behavior and persona of the entity and can be modified during runtime.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `personality` | `str` | *Required* | System prompt / persona definition for the entity. |
| `temperature` | `Optional[float]` | `None` | Generation temperature. |
| `context_window` | `Optional[int]` | `None` | Context window limit in tokens. |

#### Generic Metadata
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `metadata` | `Dict[str, Any]` | `{}` | WAD-defined, engine-agnostic metadata (e.g., sigil, element, chakra). Passed through by the engine without modification. |

---

## EntityRegistry

**File**: `src/omega/oracle/entity_registry.py`

Loads, saves, and manages entities from YAML configurations. Implements lazy deletion, multi-index lookups, and dynamic slots.

### Constructor

```python
EntityRegistry(config_path: Optional[str] = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_path` | `Optional[str]` | `None` | Path to the `entities.yaml` file. If `None`, resolves the active IWAD from `config/omega.yaml` to enforce the Engine-Stack Firewall. |

---

### Methods

#### `get(name: str, raise_on_tombstoned: bool = False) -> Optional[Entity]`

Retrieves an entity by name or dynamic slot ID (e.g., `"P1"`).

```python
registry = EntityRegistry()
entity = registry.get("Prometheus")
# Or retrieve by slot:
p1_entity = registry.get("P1")
```

**Returns**: `Optional[Entity]`

#### `list() -> List[Entity]`

Returns a list of all active entities in the registry.

**Returns**: `List[Entity]`

#### `names() -> List[str]`

Returns a list of all active entity names.

**Returns**: `List[str]`

#### `find_by_domain(text: str) -> Optional[Entity]`

Finds the closest entity matching the semantic domain of the query text using keyword-boundary matching.

```python
entity = registry.find_by_domain("I need to run a build pipeline")
# Returns BuildMaster (P3)
```

**Returns**: `Optional[Entity]`

#### `await add(entity: Entity) -> None`

Adds a new entity to the registry and schedules an asynchronous save to disk.

```python
new_entity = Entity(name="Hephaestus", domains=["forge", "hardware"], model="qwen3-1.7b", personality="You are the smith of the gods.")
await registry.add(new_entity)
```

#### `await remove(name: str) -> bool`

Deletes an entity by name using **Lazy Deletion**. The entity is marked as tombstoned and reaped after a grace period.

```python
success = await registry.remove("Hephaestus")
```

**Returns**: `bool` — `True` if successfully tombstoned, `False` if not found.

---

## id Software Heritage Patterns

The `EntityRegistry` and `Entity` classes implement several classic id Software architectural patterns:

### 1. ZONEID Pattern `[id-soft: doom-1993]`
Every `Entity` instance carries a `magic` constant (`ZONEID_ENTITY = 0x1d4a12`). This is validated on every `get()` call to catch serialization corruptions, stale references, and use of tombstoned entities.

### 2. Hard-Boundary Struct `[id-soft: quake3-1999]`
The `Entity` class divides fields into `__engine_zone__` (structural, read-only) and `__game_zone__` (personality, writable). Attempts to modify engine-zone attributes directly from game logic raise an `AttributeError`.

### 3. High-Bit Trick `[id-soft: doom-1993]`
Entity flags are stored as a bitfield. The high bit (`0x80000000`) indicates a system-level entity, and bit 30 (`0x40000000`) indicates a WAD-loaded entity, saving memory and allowing single-instruction checks.

### 4. Lazy Deletion `[id-soft: doom-1993]`
Removing an entity does not delete it immediately. It is tombstoned (`magic = ZONEID_TOMBSTONE`) and swept by `_reap_tombstoned()` after a `0.5s` grace period (`[id-soft: quake-1996]`), ensuring in-flight operations complete safely.

---

## Concurrency: `with_soul_lock` (M1 AnyIO Compliance)

**File**: `src/omega/oracle/entity_registry.py`

`with_soul_lock(entity_name, action)` ensures exclusive access to an entity's soul files during read-modify-write cycles, preventing "Lost Updates" during parallel agent operations (e.g., MaKaLi).

### M1 Compliance (2026-08-30)

The lock acquisition is **M1 AnyIO compliant**. It does NOT block the event loop:

1. **`_acquire_lock()`** — runs in a worker thread via `anyio.to_thread.run_sync()`. Opens the lock file with `os.open(..., os.O_CREAT | os.O_RDWR, 0o600)` and acquires an advisory `fcntl.flock(LOCK_EX)`.
2. **`action()`** — the user-supplied async action runs while the lock is held.
3. **`_release_lock(fd)`** — runs in a worker thread via `anyio.to_thread.run_sync()`. Releases the lock with `fcntl.flock(LOCK_UN)` and closes the file descriptor.

```python
async with with_soul_lock("my_entity", action):
    # exclusive access guaranteed
    ...
```

> **Why `run_sync`?** `fcntl.flock` is a blocking syscall. Wrapping it in `anyio.to_thread.run_sync()` keeps it off the event loop, satisfying M1 (no blocking sync I/O in async context). The lock file is created with mode `0o600` for privacy.
