# Continuity Kernel — P3.3a.6 Reference Implementation

**Status:** reference kernel and local SQLite adapter implemented 2026-09-23

**Scope:** P3.3a.6 first implementation gate

## 1. Purpose

The continuity kernel makes semantic state durable independently of the model or
host adapter. It implements the engine-side contract required by ROADMAP
P3.3a.6 without importing OpenCode, Ollama, or any provider SDK.

The reference file adapter lives at `scripts/continuity_kernel.py`. The local
SQLite commit-authority adapter lives at `scripts/continuity_sqlite.py`. Neither
is the federation transport yet.

## 2. Layer Model

| Layer | Kernel interface | Reference implementation | Role |
|---|---|---|---|
| Active state | `StateStore` | `FileStateStore` | Atomic pointer to current mission, todos, decisions, and discoveries |
| Immutable payloads | `ArtifactStore` | `FileArtifactStore` | Content-addressed SHA-256 artifacts |
| Event memory | `EventBus` | `FileEventBus` | Append-only JSONL semantic event stream |
| Model register | `ModelRouter` | `PortableModelRouter` | Role-based model selection; model ID is not identity |
| Recovery index | `CheckpointStore` | `FileCheckpointStore` | Latest consistency checkpoint |
| Recovery | `Recovery` | `ContinuityKernel.recover()` | Contract, state, event, and artifact integrity check |
| Observability | `Telemetry` | `InMemoryTelemetry` | Write-through, recovery, and failure observations |

## 3. WAD Contract

Every entity loads a portable contract such as
`wads/arcana_novai/continuity.contract.json`. The contract requires:

- `entity_id` and stable `identity` mapping;
- `model_policy.limits_source: live_runtime`;
- durable destinations (`mempalace`, `event_log`, `artifact_store`);
- an `active_work` pointer;
- an ordered recovery procedure.

The contract deliberately does **not** contain a context-window number, provider
SDK, session identifier, or model identity. A preferred model alias is only a
policy preference. The contract rejects an `opencode` destination, keeping the
bus boundary out of the WAD contract. `WADContract.digest()` provides a canonical
SHA-256 payload digest for later publisher-signature and provenance binding; a
digest is not a signature.

Use `load_wad_contract(path, telemetry)` to load it. Missing contracts, invalid
contracts, and detected platform coupling are reported as structured telemetry
before the corresponding exception is surfaced.

## 4. Semantic Write-Through

```python
from scripts.continuity_kernel import (
    ContinuityKernel,
    FileArtifactStore,
    FileCheckpointStore,
    FileEventBus,
    FileStateStore,
    ModelRoute,
    PortableModelRouter,
    WADContract,
)
from scripts.continuity_files import FileCommitJournal

contract = WADContract.from_dict(contract_data)
router = PortableModelRouter(ModelRoute("local-or-cloud-route", adapter="portable"))
kernel = ContinuityKernel(
    contract=contract,
    state_store=FileStateStore(root / "state"),
    artifact_store=FileArtifactStore(root / "artifacts"),
    event_bus=FileEventBus(root / "events"),
    checkpoint_store=FileCheckpointStore(root / "checkpoints"),
    model_router=router,
    commit_journal=FileCommitJournal(root / "journal"),
)

kernel.bootstrap({
    "mission": "Continue the expedition",
    "todos": [],
    "decisions": [],
    "discoveries": [],
})

kernel.write_through(
    boundary="decision",
    payload={"decision": "Persist the state before continuing"},
    active_work={
        "mission": "Continue the expedition",
        "todos": ["verify recovery"],
        "decisions": ["Persist the state before continuing"],
        "discoveries": [],
    },
)
```

The four allowed boundaries are `decision`, `discovery`, `task_transition`, and
`batch_completion`. A successful write stores the payload as an artifact, appends
an event, advances the atomic state pointer, and writes a checkpoint. Each event
preserves `entity_id`, `model_id`, `adapter_id`, and optional `session_id` as
separate provenance fields; only `entity_id` and WAD identity drive recovery.

## 5. Recovery Contract

`recover()` treats the event log as the authority and checkpoints as
rebuildable projections. It succeeds only when:

1. the WAD contract validates;
2. event sequences are contiguous;
3. every event payload artifact exists and its SHA-256 hash matches;
4. the state pointer has the contracted identity and destinations, or can be
   rebuilt from the latest event's `active_work` snapshot;
5. a missing or stale checkpoint is rebuilt from the event log.

The result exposes the recovered state, events, current model route, checkpoint,
and telemetry snapshot. Swapping `PortableModelRouter` changes the current
register but does not change entity identity or historical event provenance.

## 6. Chaos Test

`tests/test_continuity_kernel.py` and `tests/test_continuity_sqlite.py` measure:

- bootstrap with no context;
- write a semantic event;
- inject failure after a prepared intent;
- discard the kernel instance;
- construct a new kernel with a different model and adapter route;
- recover mission and identity from WAD + state + events + artifacts;
- rebuild missing state and checkpoints;
- deduplicate idempotent retries;
- reject a tampered payload artifact and sequence conflict;
- reject production SQLite versions below the fixed floor.

## 7. Local SQLite Commit Authority

`SqliteContinuityStore` is the production-shaped local adapter. One SQLite
transaction applies the semantic event, state pointer, and checkpoint. Artifact
blobs are content-addressed and written idempotently before the event references
them. The adapter uses rollback journaling and `synchronous=FULL`; it does not
enable WAL on a network filesystem.

SQLite `3.51.3+` is the production floor because earlier versions fall within
SQLite's 2026 WAL-reset defect range. The current host's older SQLite is allowed
only through the explicit `require_fixed_sqlite=False` test/development switch.
The production constructor fails closed.

The local database is a commit authority and rebuildable projection source.
MemPalace should consume the event/artifact stream as a projection or expose an
explicit append API; it must not become a second uncoordinated dual-write path.

## 8. Deliberate Boundaries

- The kernel does not interpret a model response or perform model inference.
- The kernel does not own MemPalace networking; its file stores are an adapter baseline.
- The kernel does not make compaction a correctness mechanism. It makes compaction
  recoverable without a ritual.
- `make gnosis-lock` and `/compact` remain emergency recovery tools, not the normal
  persistence path.

## 9. Next Adapter Gate

The next implementation increment is to add adapters that bind these interfaces
to the real MemPalace event log and a custom Omega Engine CLI. The adapter layer
must not be imported by `continuity_kernel.py`; the WAD and durable state remain
the portable contract.
