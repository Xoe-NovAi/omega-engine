# 🔱 Request Queue — Offline Research & Cloud Review Delegation
**AP Token**: `AP-REQUEST-QUEUE-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ opencode ⬡ trc_doc_ref ⬡ STANDARD

**Date**: 2026-10-02
**Purpose**: Reference documentation for the Request Queue system — implements "Data Comes Home" principle for offline research and cloud review delegation.
**Tags**: request-queue, offline, research, cloud-review, delegation, mandates
**Cross-references**: src/omega/request_queue.py, src/omega/errors.py, SOVEREIGN_MANDATES.md

---

## Overview

The `request_queue.py` module implements the **"Data Comes Home" principle** — a dual-queue system for:

1. **Offline Research Requests** — Queue research tasks when offline; execute when connectivity returns
2. **Cloud Review Delegation** — Delegate work products to cloud models for consultant-pattern evaluation

**Mandates Addressed**:
- **M1 AnyIO** — All async via AnyIO
- **M2 Engine-Stack Firewall** — Pure engine module
- **M7 Local-First** — Local queue persistence
- **M9 Error Integrity** — Typed, traceable errors
- **M12 Queue Integrity** — Every request has terminal state

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Request Queue System                      │
├─────────────────────────────────────────────────────────────┤
│  request_queue.py    │  RequestQueue — dual queue manager   │
│                      │  QueuedRequest / ReviewRequest       │
│                      │  Atomic JSON persistence             │
└─────────────────────────────────────────────────────────────┘
```

**Directory Structure** (`data/requests/`):
```
requests/
├── queued/       # Offline research requests
├── review/       # Cloud review delegations
├── completed/    # Finished requests (both types)
├── dead/         # Dead letter queue (failed permanently)
└── INDEX.json    # Aggregate index
```

---

## Core Classes

### Error Types

```python
class QueueError(OmegaError): pass
class QueueFullError(QueueError): pass      # Capacity exceeded
class RequestNotFoundError(QueueError): pass # ID not found
class RequestStaleError(QueueError): pass   # Too old to process
```

---

### RequestQueue

#### Constructor

```python
RequestQueue(requests_dir: Optional[Path] = None)
```
Default: `data/requests/`

#### Initialization

```python
queue = RequestQueue()
await queue.ensure_dirs()  # Creates queued/, review/, completed/, dead/
```

---

## Offline Research Requests

### `create_queued_request(...) -> Dict`

Create an offline research request.

```python
request = await queue.create_queued_request(
    query="Analyze the trade-offs between local-first and cloud fallback",
    priority="P2",                    # P0 | P1 | P2 | P3
    context="For architecture doc",
    created_by="architect",
    requires=["websearch", "webfetch"],      # Required tools
    fallback_tools=["searxng", "firecrawl"], # Fallback chain
    timeout_sec=300,
    max_retries=2
)
```

**Request Structure**:
```json
{
  "id": "req_a1b2c3d4",
  "query": "Analyze trade-offs...",
  "priority": "P2",
  "context": "For architecture doc",
  "created_by": "architect",
  "created_at": "2026-10-02T14:30:00Z",
  "requires": ["websearch", "webfetch"],
  "fallback_tools": ["searxng", "firecrawl"],
  "timeout_sec": 300,
  "max_retries": 2,
  "status": "queued"
}
```

**Capacity**: Max 1000 queued requests (`MAX_QUEUED`)

---

### `get_queued_requests() -> List[Dict]`

Get all queued requests, sorted by priority (P0 first).

```python
requests = await queue.get_queued_requests()
# Sorted: P0 → P1 → P2 → P3
```

---

## Cloud Review Requests

### `create_review_request(...) -> Dict`

Delegate work product to cloud model for review.

```python
request = await queue.create_review_request(
    work_product_path="docs/architecture/MEMORY_FABRIC.md",
    review_aspects=["fact_check", "deepening", "enhancement"],
    preferred_model="auto",  # or "gpt-4", "claude-3"
    created_by="kali"
)
```

**Request Structure**:
```json
{
  "id": "review_e5f6g7h8",
  "work_product_path": "docs/architecture/MEMORY_FABRIC.md",
  "review_aspects": ["fact_check", "deepening", "enhancement"],
  "preferred_model": "auto",
  "created_by": "kali",
  "created_at": "2026-10-02T14:30:00Z",
  "status": "pending_review"
}
```

**Capacity**: Max 500 review requests (`MAX_REVIEW`)

---

### `get_review_requests() -> List[Dict]`

Get all pending review requests.

---

## Request Processing

### `get_request(req_id: str) -> Optional[Dict]`

Find request by ID across all queues.

### `complete_request(req_id: str, result: Dict) -> bool`

Move request from queued/review to completed with result.

```python
success = await queue.complete_request("req_a1b2c3d4", {
    "answer": "Local-first reduces latency by 40%...",
    "sources": ["url1", "url2"],
    "confidence": 0.85
})
```

**Completed Request**:
```json
{
  "id": "req_a1b2c3d4",
  "status": "completed",
  "completed_at": "2026-10-02T14:45:00Z",
  "result": {"answer": "...", "sources": [...], "confidence": 0.85}
}
```

---

### `fail_request(req_id: str, error: str, permanent: bool = False) -> bool`

Handle request failure with retry logic.

```python
# Transient failure — retry
await queue.fail_request("req_a1b2c3d4", "Timeout", permanent=False)

# Permanent failure — dead letter queue
await queue.fail_request("req_a1b2c3d4", "Invalid query", permanent=True)
```

**Retry Logic**:
- Increments `retries` counter
- If `retries >= max_retries` or `permanent=True` → move to `dead/`
- Else → keep in queue with `status: "queued"`

---

### `prune_stale(days: int = 7) -> int`

Remove requests older than N days. Returns count pruned.

```python
pruned = await queue.prune_stale(days=7)
```

---

### `stats() -> Dict[str, int]`

Get queue statistics.

```python
stats = await queue.stats()
# {"queued": 42, "pending_review": 7, "completed": 156, "dead": 3}
```

---

## Atomic Persistence

All file writes use **atomic tmp→rename pattern**:

```python
@staticmethod
def _write_json(filepath: Path, data: dict):
    tmp = filepath.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        f.flush()
    tmp.rename(filepath)  # Atomic on POSIX
```

**Index Update**: `INDEX.json` updated after every mutation with current stats.

---

## Usage Example

```python
from omega.request_queue import RequestQueue

queue = RequestQueue()
await queue.ensure_dirs()

# 1. Queue offline research
req = await queue.create_queued_request(
    query="Compare zRAM vs zswap for 16GB NVMe system",
    priority="P1",
    context="For ZSWAP-SUBSYSTEM workstream",
    created_by="architect",
    requires=["websearch"],
    fallback_tools=["searxng"]
)

# 2. Later: process queue (when online)
queued = await queue.get_queued_requests()
for req in queued:
    # Execute research using required tools
    result = await execute_research(req)
    
    # Complete
    await queue.complete_request(req["id"], result)

# 3. Delegate cloud review
review = await queue.create_review_request(
    work_product_path="docs/architecture/ZSWAP_DESIGN.md",
    review_aspects=["fact_check", "deepening"],
    preferred_model="gpt-4",
    created_by="kali"
)

# 4. Check stats
print(await queue.stats())
# {"queued": 5, "pending_review": 1, "completed": 23, "dead": 0}
```

---

## Mandate Compliance

| Mandate | Compliance |
|---------|------------|
| **M1 AnyIO** | All async; `anyio.to_thread` for file I/O |
| **M2 Firewall** | Pure engine module; no stack deps |
| **M7 Local-First** | Local filesystem queue; no Redis |
| **M9 Error Integrity** | Typed `QueueError` hierarchy |
| **M12 Queue Integrity** | Every request reaches terminal state (completed/dead) |
| **M13 Temple-Grade** | Atomic writes; capacity limits; structured errors |
| **M23 Failure Integrity** | Dead letter queue; retry logic; no silent drops |

---

## Testing

```bash
pytest tests/test_request_queue.py -v
```

Key test scenarios:
- Request creation (both types)
- Priority sorting
- Completion flow
- Failure + retry → dead letter
- Stale pruning
- Atomic write integrity
- Capacity limits
- Stats accuracy

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ REQUEST_QUEUE-v1.0.0 ⬡ 2026-10-02 ⬡*