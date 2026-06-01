# 🔱 Omega Engine — Offline Mode & Request Queue
# AP: AP-OFFLINE-MODE-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: QUEUE | CONTEXT: SOVEREIGN-CONTINUITY]

The "Data Comes Home" principle ensures that the Omega Engine remains functional and productive regardless of cloud connectivity.

## 1. Core Concept: The Request Queue
Instead of failing when a cloud-dependent task is requested while offline, the engine captures the intent as an **Atomic Request Contract**.

## 2. Request Lifecycle
Requests move through a state machine on disk:

`queued` $\rightarrow$ `claimed` $\rightarrow$ `completed` (or `failed` $\rightarrow$ `dead`)

### 2.1 The Queued State (`data/requests/queued/`)
- Requests are stored as `{id}.json` files.
- Sorted by priority (P0 $\rightarrow$ P3).
- Contain the query, required tools, and timeout settings.

### 2.2 The Claimed State (Processing)
To prevent duplicate execution in parallel environments:
1. A worker renames `req_{id}.json` $\rightarrow$ `req_{id}.claimed`.
2. A **heartbeat** is maintained by `touching` the `.claimed` file every 30s.
3. If a heartbeat stops for >120s, a reaper process reclaims the request back to `queued`.

### 2.3 The Completed State (`data/requests/completed/`)
- Final result is merged into the request JSON.
- File is moved to the completed directory for auditing and retrieval.

## 3. Cloud Delegation (Consultant Pattern)
Not all requests are local. Some require "Heavy" model reasoning (Cloud).
- **Review Queue** (`data/requests/review/`): Work products requiring expert verification.
- **Consultant Dispatch**: When online, the engine dispatches these to the Cloud Provider Fabric.
- **Sovereign Filter**: Results are verified by a local model before being committed to the soul.

## 4. Dead Letter Office (`data/requests/dead/`)
Requests that exceed `max_retries` or fail critically are moved to the dead-letter directory with a structured error report for manual intervention.

## 5. CLI Interface
- `omega queue-status`: Monitor the state of all queues.
- `omega process-queue`: Manually trigger execution of queued items.
- `omega review-pending`: Process cloud review requests.
- `omega offline --strict`: Force the engine into local-only mode.
