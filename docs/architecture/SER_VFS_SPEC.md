# 🔱 Sovereign Entity Registry (SER) & Layered VFS Specification
**Document ID**: SPEC-SER-VFS-2026-001
**Status**: Baseline
**Sovereign Mandates**: M2 (Firewall), M7 (Local-First), M8 (Zero Telemetry), M11 (Soul Integrity)

## 1. Overview
The Sovereign Entity Registry (SER) and Layered Virtual File System (VFS) provide the foundational infrastructure for entity identity, state persistence, and resource resolution within the Omega Engine. This architecture replaces the naive `INDEX.yaml` with a robust, manifest-driven SQLite registry and a priority-based resolution system to ensure strict separation between the Engine Core and Expansion Stacks (WADs).

---

## 2. Layered Virtual File System (VFS)

### 2.1 Resolution Hierarchy
The VFS implements a priority-based layered resolution system. When a resource (entity trait, soul, or config) is requested, the engine searches layers in the following order:

1. **Session Layer**: Temporary overrides and runtime state (Highest Priority).
2. **PWAD Layer (Patch WAD)**: User-defined modifications and custom entity stacks.
3. **IWAD Layer (Initial WAD)**: Base entity definitions and roles (`_omega_default`).
4. **Core Layer**: Engine-level defaults and system constants (Lowest Priority).

**Resolution Logic**: The first layer to provide a valid match wins.

### 2.2 System Protection (`FLAG_SYSTEM`)
To prevent accidental or malicious modification of core engine logic, resources can be marked with `FLAG_SYSTEM` (0x80000000).
- **Constraint**: Resources marked as `FLAG_SYSTEM` cannot be overridden by the PWAD or Session layers.
- **Enforcement**: The VFS resolver checks the high-bit flag of the target resource; if set, it bypasses higher-priority layers and returns the Core/IWAD definition.

### 2.3 Performance Optimization
To avoid repeated disk I/O and SQLite queries, the VFS utilizes an `LRUCache`.
- **Cache Key**: `(resource_id, layer_priority)`
- **Cache Value**: Resolved file path or data blob.
- **Invalidation**: Cache is flushed upon WAD reload or explicit `SovereignWriter` commit.

---

## 3. Sovereign Entity Registry (SER)

### 3.1 SQLite Registry Schema
The SER moves entity metadata from flat files to a structured SQLite database to support atomic operations and complex queries.

```sql
-- Entity Manifest
CREATE TABLE entities (
    entity_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT,
    capability_mask INTEGER,
    wad_source TEXT,
    last_awakened DATETIME,
    soul_version INTEGER DEFAULT 1,
    flags INTEGER DEFAULT 0 -- Includes FLAG_SYSTEM
);

-- Resource Mapping
CREATE TABLE resource_map (
    resource_id TEXT,
    entity_id TEXT,
    layer_id TEXT,
    physical_path TEXT,
    checksum TEXT,
    PRIMARY KEY (resource_id, layer_id),
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);

-- Sync Queue
CREATE TABLE sync_queue (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT, -- 'LOAD_WAD', 'UPDATE_SOUL', 'PRUNE'
    payload BLOB,
    status TEXT DEFAULT 'pending',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 The `SovereignWriter` Pattern
To guarantee zero data loss and prevent corruption during crashes, all writes to the registry and soul files follow the **Physical Sync Pattern**:

1. **Write**: Data is written to a temporary file (`.tmp`).
2. **Fsync**: `os.fsync()` is called on the temporary file to ensure bits are physically on disk.
3. **Replace**: Atomic rename (`os.replace()`) of `.tmp` to the target filename.
4. **Parent Fsync**: `os.fsync()` is called on the parent directory to ensure the directory entry is persisted.

### 3.3 Serialized `SyncQueue`
WAD loading and bulk entity updates are handled via a serialized `SyncQueue` to prevent race conditions and ensure linear consistency.
- **Mechanism**: A single-threaded worker processes the `sync_queue` table.
- **Atomicity**: Each job is wrapped in a SQLite transaction.

---

## 4. Sovereignty Assurance

### 4.1 Sovereign Export Tool
To maintain the "sever the umbilical cord" mission, the SER includes a tool to export the binary SQLite registry back into human-readable YAML.
- **Flow**: `SQLite Registry` $\rightarrow$ `Sovereign Export` $\rightarrow$ `YAML Manifests`.
- **Purpose**: Ensures the user can audit and migrate their entire entity ecosystem without proprietary tools.

### 4.2 Leak Checklist
Every new resource added to the VFS must pass the Leak Checklist:
- [ ] Does this resource contain hardcoded cloud API keys?
- [ ] Does it reference absolute paths outside the `data/` directory?
- [ ] Does it implement telemetry or "phone-home" logic?
- [ ] Is it correctly tagged with `FLAG_SYSTEM` if it is a core component?

### 4.3 Sovereign-Symmetry Check
A validation utility that compares the current runtime state against the `Sovereign Export` to ensure no "ghost state" has accumulated in memory that isn't persisted in the registry.

---

## 5. Summary of Resolution Flow
`Request(ResourceID)` $\rightarrow$ `LRUCache` $\rightarrow$ `VFS Resolver` $\rightarrow$ `[Session $\rightarrow$ PWAD $\rightarrow$ IWAD $\rightarrow$ Core]` $\rightarrow$ `FLAG_SYSTEM Check` $\rightarrow$ `SER SQLite Lookup` $\rightarrow$ `Physical Path` $\rightarrow$ `SovereignWriter (if write)`.
