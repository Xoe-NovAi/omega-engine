# API Reference: Content-Addressable Storage (CAS)

> CASArchiver — immutable, local-first blob storage by content hash.

---

## CASArchiver

**File**: `src/omega/archive/cas.py`

Content-Addressable Storage implementing the "Golden Copy" pattern: store once, reference many. 100% local, zero telemetry, immutable provenance.

### Constructor

```python
CASArchiver(base_dir: str = "data/archive/cas")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_dir` | `str` | `"data/archive/cas"` | Root directory for CAS blobs |

The constructor creates the base directory if it doesn't exist.

### Directory Structure

CAS uses 2-level directory sharding to prevent filesystem slowdowns:

```
data/archive/cas/
├── ab/
│   ├── abcdef0123456789...  (full SHA-256 hash as filename)
│   └── abcdef9876543210...
├── cd/
│   └── cdef0123456789ab...
└── ...
```

The first 2 characters of the SHA-256 hash form the subdirectory. This prevents any single directory from holding more than ~256 entries.

---

### Methods

#### `store(content: bytes) -> str`

Stores content by its SHA-256 hash. Returns the content hash (CID).

```python
archiver = CASArchiver()
cid = await archiver.store(b"Hello, world!")
# cid = "315f5bdb76d078c43b8ac0064e4a0164612b1fce77c869345bfc94c75894edd3"
```

**Behavior**:
- Computes SHA-256 of content
- Creates `base_dir/ab/cdef...` directory structure
- Writes content if not already present (deduplication)
- Returns the full SHA-256 hex digest as CID

**Returns**: `str` — the content hash (64-character hex string)

#### `retrieve(content_hash: str) -> Optional[bytes]`

Retrieves content by its SHA-256 hash.

```python
content = await archiver.retrieve(cid)
if content:
    print(content.decode("utf-8"))
```

**Returns**: `bytes` or `None` if not found.

#### `exists(content_hash: str) -> bool`

Checks if a blob exists in the archive.

```python
if await archiver.exists(cid):
    print("Blob is archived")
```

**Returns**: `bool`

#### `delete(content_hash: str) -> bool`

Deletes a blob from the archive.

```python
deleted = await archiver.delete(cid)
# deleted = True if found and removed, False if not found
```

**Returns**: `bool`

---

## CAS Properties

| Property | Description |
|----------|-------------|
| **Content-Addressed** | SHA-256 hash is the address. Content cannot change without a new CID. |
| **Immutable** | Writing the same content twice returns the same CID (idempotent). |
| **Deduplicated** | Identical content stored once, referenced many times. |
| **Local-First** | 100% filesystem. No cloud, no network, no telemetry. |
| **Async** | All I/O via `anyio.to_thread.run_sync` (M1 compliant). |

---

## Integration with Ingestion Pipeline

The `IngestionPipeline` uses CAS to store raw scraped content:

```python
# In pipeline.py
raw_content = t3_res.content.encode('utf-8')
cid = await self.cas.store(raw_content)
```

The CID is then included in the `IngestionResult` for provenance tracking.

---

## Example: Archiving a Document

```python
from omega.archive.cas import CASArchiver

async def archive_document(path: str):
    archiver = CASArchiver()
    
    with open(path, "rb") as f:
        content = f.read()
    
    cid = await archiver.store(content)
    print(f"Archived: {cid}")
    print(f"Retrievable at: data/archive/cas/{cid[:2]}/{cid}")
    
    # Verify it's there
    exists = await archiver.exists(cid)
    assert exists
    
    # Retrieve it
    retrieved = await archiver.retrieve(cid)
    assert retrieved == content
```
