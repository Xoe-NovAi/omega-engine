"""Portable semantic write-through and recovery kernel.

This module is deliberately adapter-neutral. It contains no OpenCode, provider,
or node-specific imports. A WAD contract describes the entity's identity and
durable-state policy; stores, event bus, and model router are injected.

The reference implementations are file-backed so recovery can be measured in a
separate process without depending on an in-memory session. They are not
claimed to be the production federation transport; they establish the kernel
contract and a chaos-testable local baseline.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import uuid
from collections import Counter
from contextlib import nullcontext
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

SCHEMA_VERSION = 1
CONTRACT_VERSION = 1
VALID_BOUNDARIES = frozenset(
    {"decision", "discovery", "task_transition", "batch_completion"}
)
SAFE_ENTITY_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SAFE_ARTIFACT_ID = re.compile(r"^[0-9a-f]{64}$")

JsonObject = dict[str, Any]


class ContinuityError(RuntimeError):
    """Base class for continuity contract and recovery failures."""


class ContractError(ContinuityError):
    """A WAD continuity contract is incomplete or unsafe."""


class RecoveryError(ContinuityError):
    """Durable state cannot be recovered with integrity checks."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate_entity_id(entity_id: str) -> None:
    if not isinstance(entity_id, str) or not SAFE_ENTITY_ID.fullmatch(entity_id):
        raise ContractError(f"invalid entity id: {entity_id!r}")


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    directory_fd = os.open(path, flags)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _read_json_object(path: Path, description: str) -> JsonObject:
    if not path.is_file():
        raise RecoveryError(f"missing {description}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecoveryError(f"invalid {description}: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RecoveryError(f"{description} must contain a JSON object: {path}")
    return value


def _json_lines(path: Path, description: str) -> list[JsonObject]:
    if not path.is_file():
        raise RecoveryError(f"missing {description}: {path}")
    records: list[JsonObject] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RecoveryError(f"could not read {description}: {path}: {exc}") from exc
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RecoveryError(
                f"invalid {description} JSON at {path}:{line_number}: {exc}"
            ) from exc
        if not isinstance(value, dict):
            raise RecoveryError(
                f"invalid {description} record at {path}:{line_number}: not an object"
            )
        records.append(value)
    return records


class StateStore(Protocol):
    """Durable pointer to the entity's current active-work state."""

    def read(self, entity_id: str) -> JsonObject:
        """Return the current state or raise if the entity is not bootstrapped."""

    def write(self, state: JsonObject) -> None:
        """Atomically replace the current state."""


class ArtifactStore(Protocol):
    """Immutable content-addressed storage for semantic payloads."""

    def put(
        self,
        content: bytes,
        content_type: str = "application/json",
        metadata: Mapping[str, Any] | None = None,
    ) -> "ArtifactRef":
        """Persist bytes and return a verifiable artifact reference."""

    def get(self, artifact_id: str) -> bytes:
        """Return artifact bytes and verify their content hash."""


class EventBus(Protocol):
    """Append-only durable semantic event stream."""

    def append(self, event: "SemanticEvent") -> None:
        """Durably append one event."""

    def list(self, entity_id: str, upto_sequence: int | None = None) -> list["SemanticEvent"]:
        """Return events in sequence order, optionally through a sequence."""


class ModelRouter(Protocol):
    """Resolve a model role without coupling the kernel to a model provider."""

    def route(self, role: str) -> "ModelRoute":
        """Return the currently selected route for a role."""


class CheckpointStore(Protocol):
    """Store and retrieve the latest recovery checkpoint."""

    def save(self, checkpoint: "Checkpoint") -> None:
        """Persist a checkpoint."""

    def latest(self, entity_id: str) -> "Checkpoint | None":
        """Return the latest checkpoint, if one exists."""


class Recovery(Protocol):
    """Rebuild an entity from its WAD contract and durable stores."""

    def recover(self) -> "RecoveryResult":
        """Recover and validate the entity's active state."""


class Telemetry(Protocol):
    """Observability boundary for contract and continuity invariants."""

    def observe(self, name: str, **fields: Any) -> None:
        """Record one structured observation."""

    def snapshot(self) -> JsonObject:
        """Return a serializable telemetry snapshot."""


class CommitJournal(Protocol):
    """Durable coordinator for a multi-store semantic commit."""

    def lock(self, entity_id: str):
        """Return a context manager serializing writers for one entity."""

    def prepare(self, intent: "CommitIntent") -> None:
        """Persist a complete intent before applying its component writes."""

    def pending(self, entity_id: str) -> list["CommitIntent"]:
        """Return prepared intents awaiting replay."""

    def commit(self, intent_id: str, entity_id: str) -> None:
        """Retire a completed intent."""


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    artifact_id: str
    sha256: str
    size_bytes: int
    content_type: str

    def to_dict(self) -> JsonObject:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ModelRoute:
    model_id: str
    adapter: str = "portable"

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ContractError("model route requires a non-empty model id")
        if not self.adapter.strip():
            raise ContractError("model route requires a non-empty adapter id")


@dataclass(frozen=True, slots=True)
class ModelPolicy:
    """Model selection policy without capacity or identity claims."""

    preferred_aliases: tuple[str, ...] = ()
    limits_source: str = "live_runtime"
    swap_allowed: bool = True

    def validate(self) -> None:
        if any(not alias.strip() for alias in self.preferred_aliases):
            raise ContractError("model policy contains an empty alias")
        if self.limits_source != "live_runtime":
            raise ContractError("model limits must come from live runtime metadata")
        if not isinstance(self.swap_allowed, bool):
            raise ContractError("model policy swap_allowed must be boolean")

    def to_dict(self) -> JsonObject:
        return {
            "preferred_aliases": list(self.preferred_aliases),
            "limits_source": self.limits_source,
            "swap_allowed": self.swap_allowed,
        }


@dataclass(frozen=True, slots=True)
class WADContract:
    """Portable WAD continuity contract.

    The contract carries identity and recovery policy, but never a provider,
    context-window value, or adapter implementation. A model alias may be a
    preference; it is not the entity's identity.
    """

    entity_id: str
    identity: Mapping[str, str]
    model_policy: ModelPolicy
    durable_state_destinations: tuple[str, ...]
    active_work_pointer: str
    recovery_procedure: tuple[str, ...]

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        _validate_entity_id(self.entity_id)
        if not self.identity or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in self.identity.items()
        ):
            raise ContractError("contract identity must be a non-empty string mapping")
        if not isinstance(self.identity, Mapping):
            raise ContractError("contract identity must be a mapping")
        self.model_policy.validate()
        if not self.durable_state_destinations:
            raise ContractError("contract requires at least one durable destination")
        if any(not destination.strip() for destination in self.durable_state_destinations):
            raise ContractError("contract contains an empty durable destination")
        if not self.active_work_pointer.strip():
            raise ContractError("contract requires an active-work pointer")
        if not self.recovery_procedure:
            raise ContractError("contract requires a recovery procedure")
        contract_values = " ".join(
            (
                self.entity_id,
                *self.durable_state_destinations,
                self.active_work_pointer,
                *self.recovery_procedure,
            )
        ).casefold()
        if "opencode" in contract_values:
            raise ContractError("WAD continuity contract must not couple to OpenCode")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WADContract":
        required = {
            "contract_version",
            "entity_id",
            "identity",
            "model_policy",
            "durable_state_destinations",
            "active_work_pointer",
            "recovery_procedure",
        }
        missing = required.difference(data)
        if missing:
            raise ContractError(f"contract missing fields: {sorted(missing)}")
        if data["contract_version"] != CONTRACT_VERSION:
            raise ContractError(
                f"unsupported contract version: {data['contract_version']!r}"
            )
        model_data = data["model_policy"]
        if not isinstance(model_data, Mapping):
            raise ContractError("model_policy must be a mapping")
        return cls(
            entity_id=str(data["entity_id"]),
            identity=dict(data["identity"]),
            model_policy=ModelPolicy(
                preferred_aliases=tuple(model_data.get("preferred_aliases", [])),
                limits_source=str(model_data.get("limits_source", "live_runtime")),
                swap_allowed=bool(model_data.get("swap_allowed", True)),
            ),
            durable_state_destinations=tuple(data["durable_state_destinations"]),
            active_work_pointer=str(data["active_work_pointer"]),
            recovery_procedure=tuple(data["recovery_procedure"]),
        )

    def to_dict(self) -> JsonObject:
        return {
            "contract_version": CONTRACT_VERSION,
            "entity_id": self.entity_id,
            "identity": dict(self.identity),
            "model_policy": self.model_policy.to_dict(),
            "durable_state_destinations": list(self.durable_state_destinations),
            "active_work_pointer": self.active_work_pointer,
            "recovery_procedure": list(self.recovery_procedure),
        }

    def digest(self) -> str:
        """Return the SHA-256 digest of the canonical contract payload."""
        return hashlib.sha256(_canonical_json(self.to_dict()).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class SemanticEvent:
    event_id: str
    entity_id: str
    sequence: int
    boundary: str
    payload: JsonObject
    active_work: JsonObject
    idempotency_key: str
    payload_artifact_id: str
    payload_sha256: str
    model_id: str
    adapter_id: str
    session_id: str
    created_at: str

    def to_dict(self) -> JsonObject:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SemanticEvent":
        try:
            return cls(
                event_id=str(data["event_id"]),
                entity_id=str(data["entity_id"]),
                sequence=int(data["sequence"]),
                boundary=str(data["boundary"]),
                payload=dict(data["payload"]),
                active_work=dict(data.get("active_work", {})),
                idempotency_key=str(data.get("idempotency_key", "")),
                payload_artifact_id=str(data["payload_artifact_id"]),
                payload_sha256=str(data["payload_sha256"]),
                model_id=str(data["model_id"]),
                adapter_id=str(data.get("adapter_id", "portable")),
                session_id=str(data.get("session_id", "")),
                created_at=str(data["created_at"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RecoveryError(f"invalid semantic event: {exc}") from exc


@dataclass(frozen=True, slots=True)
class Checkpoint:
    checkpoint_id: str
    entity_id: str
    sequence: int
    state: JsonObject
    event_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    created_at: str

    def to_dict(self) -> JsonObject:
        return {
            "checkpoint_id": self.checkpoint_id,
            "entity_id": self.entity_id,
            "sequence": self.sequence,
            "state": self.state,
            "event_ids": list(self.event_ids),
            "artifact_ids": list(self.artifact_ids),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Checkpoint":
        try:
            return cls(
                checkpoint_id=str(data["checkpoint_id"]),
                entity_id=str(data["entity_id"]),
                sequence=int(data["sequence"]),
                state=dict(data["state"]),
                event_ids=tuple(data["event_ids"]),
                artifact_ids=tuple(data["artifact_ids"]),
                created_at=str(data["created_at"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RecoveryError(f"invalid checkpoint: {exc}") from exc


@dataclass(frozen=True, slots=True)
class CommitIntent:
    intent_id: str
    event: SemanticEvent
    state: JsonObject
    checkpoint: Checkpoint
    created_at: str

    def to_dict(self) -> JsonObject:
        return {
            "intent_id": self.intent_id,
            "event": self.event.to_dict(),
            "state": self.state,
            "checkpoint": self.checkpoint.to_dict(),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "CommitIntent":
        try:
            return cls(
                intent_id=str(data["intent_id"]),
                event=SemanticEvent.from_dict(data["event"]),
                state=dict(data["state"]),
                checkpoint=Checkpoint.from_dict(data["checkpoint"]),
                created_at=str(data["created_at"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RecoveryError(f"invalid commit intent: {exc}") from exc


@dataclass(frozen=True, slots=True)
class RecoveryResult:
    contract: WADContract
    state: JsonObject
    events: tuple[SemanticEvent, ...]
    current_route: ModelRoute
    checkpoint: Checkpoint | None
    telemetry: JsonObject


class InMemoryTelemetry:
    """Small injectable telemetry sink used by tests and adapters."""

    def __init__(self) -> None:
        self._counts: Counter[str] = Counter()
        self._events: list[JsonObject] = []

    def observe(self, name: str, **fields: Any) -> None:
        self._counts[name] += 1
        self._events.append({"name": name, "fields": deepcopy(fields)})

    def snapshot(self) -> JsonObject:
        return {"counts": dict(self._counts), "events": deepcopy(self._events)}


def load_wad_contract(
    path: Path,
    telemetry: Telemetry | None = None,
) -> WADContract:
    """Load a WAD contract and report missing/coupled contract failures."""
    try:
        data = _read_json_object(path, "WAD continuity contract")
        contract = WADContract.from_dict(data)
    except (ContractError, RecoveryError, KeyError, TypeError, ValueError) as exc:
        if telemetry is not None:
            error = str(exc)
            if isinstance(exc, RecoveryError) and "missing" in error.casefold():
                observation = "missing_wad_contract"
            elif "opencode" in error.casefold():
                observation = "platform_coupling"
            else:
                observation = "invalid_wad_contract"
            telemetry.observe(observation, path=str(path), error=error)
        raise
    if telemetry is not None:
        telemetry.observe("wad_contract_loaded", path=str(path), entity_id=contract.entity_id)
    return contract


class FileStateStore:
    """Atomic JSON state pointer, one file per entity."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, entity_id: str) -> Path:
        _validate_entity_id(entity_id)
        return self.root / entity_id / "state.json"

    def read(self, entity_id: str) -> JsonObject:
        value = _read_json_object(self._path(entity_id), "state pointer")
        if value.get("entity_id") != entity_id:
            raise RecoveryError("state pointer entity id does not match requested entity")
        return value

    def write(self, state: JsonObject) -> None:
        entity_id = str(state.get("entity_id", ""))
        _validate_entity_id(entity_id)
        _atomic_write(self._path(entity_id), _canonical_json(state) + "\n")


class FileArtifactStore:
    """Content-addressed file store with a sidecar metadata record."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _blob_path(self, artifact_id: str) -> Path:
        if not SAFE_ARTIFACT_ID.fullmatch(artifact_id):
            raise RecoveryError(f"invalid artifact id: {artifact_id!r}")
        return self.root / "blobs" / artifact_id

    def _metadata_path(self, artifact_id: str) -> Path:
        return self.root / "metadata" / f"{artifact_id}.json"

    def put(
        self,
        content: bytes,
        content_type: str = "application/json",
        metadata: Mapping[str, Any] | None = None,
    ) -> ArtifactRef:
        if not isinstance(content, bytes):
            raise TypeError("artifact content must be bytes")
        digest = hashlib.sha256(content).hexdigest()
        blob_path = self._blob_path(digest)
        if not blob_path.exists():
            _atomic_write_bytes(blob_path, content)
        ref = ArtifactRef(
            artifact_id=digest,
            sha256=digest,
            size_bytes=len(content),
            content_type=content_type,
        )
        record = ref.to_dict()
        record["metadata"] = dict(metadata or {})
        _atomic_write(self._metadata_path(digest), _canonical_json(record) + "\n")
        return ref

    def get(self, artifact_id: str) -> bytes:
        path = self._blob_path(artifact_id)
        if not path.is_file():
            raise RecoveryError(f"missing artifact blob: {artifact_id}")
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if digest != artifact_id:
            raise RecoveryError(f"artifact hash mismatch: {artifact_id}")
        if not self._metadata_path(artifact_id).is_file():
            raise RecoveryError(f"missing artifact metadata: {artifact_id}")
        return content


class FileEventBus:
    """Append-only JSONL event log with flush and fsync durability."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, entity_id: str) -> Path:
        _validate_entity_id(entity_id)
        return self.root / entity_id / "events.jsonl"

    def append(self, event: SemanticEvent) -> None:
        existing = self.list(event.entity_id)
        for current in existing:
            if current.event_id == event.event_id:
                if current.to_dict() != event.to_dict():
                    raise RecoveryError("event id already exists with different content")
                return
            if current.sequence == event.sequence:
                raise RecoveryError("event sequence already exists with different id")
        path = self._path(event.entity_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical_json(event.to_dict()) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def list(self, entity_id: str, upto_sequence: int | None = None) -> list[SemanticEvent]:
        path = self._path(entity_id)
        if not path.is_file():
            return []
        records = _json_lines(path, "event log")
        events = [SemanticEvent.from_dict(record) for record in records]
        events = sorted(events, key=lambda event: event.sequence)
        if upto_sequence is not None:
            events = [event for event in events if event.sequence <= upto_sequence]
        return events


class FileCheckpointStore:
    """One atomically replaced latest-checkpoint file per entity."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, entity_id: str) -> Path:
        _validate_entity_id(entity_id)
        return self.root / entity_id / "checkpoint.json"

    def save(self, checkpoint: Checkpoint) -> None:
        _atomic_write(self._path(checkpoint.entity_id), _canonical_json(checkpoint.to_dict()) + "\n")

    def latest(self, entity_id: str) -> Checkpoint | None:
        path = self._path(entity_id)
        if not path.is_file():
            return None
        return Checkpoint.from_dict(_read_json_object(path, "checkpoint"))


class PortableModelRouter:
    """Injectable role router; changing the route is a register swap."""

    def __init__(self, default: ModelRoute, routes: Mapping[str, ModelRoute] | None = None) -> None:
        self._default = default
        self._routes = dict(routes or {})

    def route(self, role: str) -> ModelRoute:
        if role in self._routes:
            return self._routes[role]
        return self._default

    def swap(self, model_id: str, adapter: str = "portable") -> None:
        self._default = ModelRoute(model_id=model_id, adapter=adapter)


class ContinuityKernel:
    """Coordinate semantic write-through and model-independent recovery."""

    def __init__(
        self,
        contract: WADContract,
        state_store: StateStore,
        artifact_store: ArtifactStore,
        event_bus: EventBus,
        checkpoint_store: CheckpointStore,
        model_router: ModelRouter,
        telemetry: Telemetry | None = None,
        commit_journal: CommitJournal | None = None,
    ) -> None:
        self.contract = contract
        self.state_store = state_store
        self.artifact_store = artifact_store
        self.event_bus = event_bus
        self.checkpoint_store = checkpoint_store
        self.model_router = model_router
        self.telemetry = telemetry or InMemoryTelemetry()
        self.commit_journal = commit_journal

    def _state_from_event(self, event: SemanticEvent, route: ModelRoute) -> JsonObject:
        return {
            "schema_version": SCHEMA_VERSION,
            "entity_id": self.contract.entity_id,
            "identity": dict(self.contract.identity),
            "durable_state_destinations": list(self.contract.durable_state_destinations),
            self.contract.active_work_pointer: dict(event.active_work),
            "last_sequence": event.sequence,
            "last_event_id": event.event_id,
            "model_affinity": {
                "model_id": route.model_id,
                "adapter": route.adapter,
            },
            "updated_at": event.created_at,
        }

    def _checkpoint_from_state(
        self,
        state: JsonObject,
        events: Sequence[SemanticEvent],
    ) -> Checkpoint:
        return Checkpoint(
            checkpoint_id=str(uuid.uuid4()),
            entity_id=self.contract.entity_id,
            sequence=int(state["last_sequence"]),
            state=state,
            event_ids=tuple(event.event_id for event in events),
            artifact_ids=tuple(
                dict.fromkeys(event.payload_artifact_id for event in events)
            ),
            created_at=_now(),
        )

    def _apply_intent(self, intent: CommitIntent) -> None:
        """Idempotently apply a prepared multi-file commit."""
        self.event_bus.append(intent.event)
        try:
            current = self.state_store.read(intent.event.entity_id)
        except RecoveryError:
            current = None
        if current is None or int(current.get("last_sequence", 0)) <= intent.event.sequence:
            self.state_store.write(intent.state)
            self.checkpoint_store.save(intent.checkpoint)

    def _apply_prepared_intent(self, intent: CommitIntent) -> None:
        apply_intent = getattr(self.commit_journal, "apply_intent", None)
        if callable(apply_intent):
            apply_intent(intent)
        else:
            self._apply_intent(intent)

    def _replay_pending_intents(self) -> None:
        if self.commit_journal is None:
            return
        for intent in self.commit_journal.pending(self.contract.entity_id):
            self._apply_prepared_intent(intent)
            self.commit_journal.commit(intent.intent_id, self.contract.entity_id)
            self.telemetry.observe(
                "commit_intent_replayed",
                entity_id=self.contract.entity_id,
                sequence=intent.event.sequence,
            )

    def _find_idempotency_event(self, key: str) -> SemanticEvent | None:
        if not key:
            return None
        for event in self.event_bus.list(self.contract.entity_id):
            if event.idempotency_key == key:
                return event
        return None

    def bootstrap(
        self,
        active_work: Mapping[str, Any],
        default_role: str = "default",
    ) -> Checkpoint:
        """Create the durable state pointer without manufacturing a semantic event."""
        if not isinstance(active_work, Mapping):
            raise TypeError("active_work must be a mapping")
        lock = (
            self.commit_journal.lock(self.contract.entity_id)
            if self.commit_journal is not None
            else nullcontext()
        )
        with lock:
            self._replay_pending_intents()
            try:
                self.state_store.read(self.contract.entity_id)
            except RecoveryError:
                pass
            else:
                raise ContractError("cannot bootstrap an already initialized entity")
            route = self.model_router.route(default_role)
            state = {
                "schema_version": SCHEMA_VERSION,
                "entity_id": self.contract.entity_id,
                "identity": dict(self.contract.identity),
                "durable_state_destinations": list(
                    self.contract.durable_state_destinations
                ),
                self.contract.active_work_pointer: dict(active_work),
                "last_sequence": 0,
                "last_event_id": None,
                "model_affinity": {
                    "model_id": route.model_id,
                    "adapter": route.adapter,
                },
                "updated_at": _now(),
            }
            self.state_store.write(state)
            checkpoint = Checkpoint(
                checkpoint_id=str(uuid.uuid4()),
                entity_id=self.contract.entity_id,
                sequence=0,
                state=state,
                event_ids=(),
                artifact_ids=(),
                created_at=_now(),
            )
            self.checkpoint_store.save(checkpoint)
            self.telemetry.observe("continuity_bootstrap", entity_id=self.contract.entity_id)
            return checkpoint

    def write_through(
        self,
        boundary: str,
        payload: Mapping[str, Any],
        active_work: Mapping[str, Any],
        role: str = "default",
        idempotency_key: str | None = None,
        session_id: str = "",
    ) -> Checkpoint:
        """Persist one semantic boundary with idempotent multi-file commit."""
        if boundary not in VALID_BOUNDARIES:
            raise ContractError(f"unsupported semantic boundary: {boundary!r}")
        if not isinstance(payload, Mapping):
            raise TypeError("semantic payload must be a mapping")
        if not isinstance(active_work, Mapping):
            raise TypeError("active_work must be a mapping")
        if idempotency_key is not None and not idempotency_key.strip():
            raise ContractError("idempotency_key must be non-empty when supplied")

        lock = (
            self.commit_journal.lock(self.contract.entity_id)
            if self.commit_journal is not None
            else nullcontext()
        )
        with lock:
            self._replay_pending_intents()
            existing = self._find_idempotency_event(idempotency_key or "")
            if existing is not None:
                state = self.state_store.read(self.contract.entity_id)
                events = self.event_bus.list(
                    self.contract.entity_id, existing.sequence
                )
                if int(state.get("last_sequence", 0)) < existing.sequence:
                    state = self._state_from_event(existing, self.model_router.route(role))
                    self.state_store.write(state)
                checkpoint = self.checkpoint_store.latest(self.contract.entity_id)
                if checkpoint is None or checkpoint.sequence != state["last_sequence"]:
                    checkpoint = self._checkpoint_from_state(state, events)
                    self.checkpoint_store.save(checkpoint)
                self.telemetry.observe(
                    "idempotent_replay",
                    entity_id=self.contract.entity_id,
                    sequence=existing.sequence,
                    idempotency_key=existing.idempotency_key,
                )
                return checkpoint
            return self._write_through_locked(
                boundary,
                payload,
                active_work,
                role,
                idempotency_key or "",
                session_id,
            )

    def _write_through_locked(
        self,
        boundary: str,
        payload: Mapping[str, Any],
        active_work: Mapping[str, Any],
        role: str,
        idempotency_key: str,
        session_id: str,
    ) -> Checkpoint:
        sequence = 0
        route = self.model_router.route(role)
        try:
            state = self.state_store.read(self.contract.entity_id)
            sequence = int(state.get("last_sequence", 0)) + 1
            payload_dict = dict(payload)
            payload_bytes = _canonical_json(payload_dict).encode("utf-8")
            artifact = self.artifact_store.put(
                payload_bytes,
                content_type="application/json",
                metadata={
                    "entity_id": self.contract.entity_id,
                    "boundary": boundary,
                    "sequence": sequence,
                    "idempotency_key": idempotency_key,
                },
            )
            event = SemanticEvent(
                event_id=str(uuid.uuid4()),
                entity_id=self.contract.entity_id,
                sequence=sequence,
                boundary=boundary,
                payload=payload_dict,
                active_work=dict(active_work),
                idempotency_key=idempotency_key,
                payload_artifact_id=artifact.artifact_id,
                payload_sha256=artifact.sha256,
                model_id=route.model_id,
                adapter_id=route.adapter,
                session_id=session_id,
                created_at=_now(),
            )
            next_state = {
                **state,
                "schema_version": SCHEMA_VERSION,
                "entity_id": self.contract.entity_id,
                "identity": dict(self.contract.identity),
                "durable_state_destinations": list(
                    self.contract.durable_state_destinations
                ),
                self.contract.active_work_pointer: dict(active_work),
                "last_sequence": sequence,
                "last_event_id": event.event_id,
                "model_affinity": {
                    "model_id": route.model_id,
                    "adapter": route.adapter,
                },
                "updated_at": event.created_at,
            }
            prior_events = self.event_bus.list(
                self.contract.entity_id, sequence - 1
            )
            checkpoint = Checkpoint(
                checkpoint_id=str(uuid.uuid4()),
                entity_id=self.contract.entity_id,
                sequence=sequence,
                state=next_state,
                event_ids=tuple(item.event_id for item in (*prior_events, event)),
                artifact_ids=tuple(
                    dict.fromkeys(item.payload_artifact_id for item in (*prior_events, event))
                ),
                created_at=event.created_at,
            )
            intent = CommitIntent(
                intent_id=str(uuid.uuid4()),
                event=event,
                state=next_state,
                checkpoint=checkpoint,
                created_at=event.created_at,
            )
            if self.commit_journal is not None:
                self.commit_journal.prepare(intent)
            self._apply_prepared_intent(intent)
            if self.commit_journal is not None:
                self.commit_journal.commit(intent.intent_id, self.contract.entity_id)
        except (OSError, ValueError, TypeError, RecoveryError) as exc:
            self.telemetry.observe(
                "unpersisted_semantic_state",
                entity_id=self.contract.entity_id,
                boundary=boundary,
                sequence=sequence,
                error=str(exc),
            )
            raise ContinuityError(f"semantic write-through failed at sequence {sequence}") from exc

        self.telemetry.observe(
            "semantic_write_through",
            entity_id=self.contract.entity_id,
            boundary=boundary,
            sequence=sequence,
            model_id=route.model_id,
            adapter=route.adapter,
            idempotency_key=idempotency_key or None,
        )
        return checkpoint

    def recover(self) -> RecoveryResult:
        """Rebuild from the WAD contract, state pointer, and event/artifact stores."""
        lock = (
            self.commit_journal.lock(self.contract.entity_id)
            if self.commit_journal is not None
            else nullcontext()
        )
        with lock:
            self._replay_pending_intents()
            return self._recover_locked()

    def _recover_locked(self) -> RecoveryResult:
        try:
            self.contract.validate()
            current_route = self.model_router.route("default")
            events = tuple(self.event_bus.list(self.contract.entity_id))
            if [event.sequence for event in events] != list(range(1, len(events) + 1)):
                raise RecoveryError("event stream is not contiguous")
            for event in events:
                if event.entity_id != self.contract.entity_id:
                    raise RecoveryError("event entity id does not match WAD contract")
                payload = self.artifact_store.get(event.payload_artifact_id)
                if hashlib.sha256(payload).hexdigest() != event.payload_sha256:
                    raise RecoveryError("event payload artifact hash does not match")
                if json.loads(payload.decode("utf-8")) != event.payload:
                    raise RecoveryError("event payload does not match artifact")

            state: JsonObject | None
            try:
                state = self.state_store.read(self.contract.entity_id)
            except RecoveryError:
                state = None
            if events and (
                state is None
                or int(state.get("last_sequence", 0)) < events[-1].sequence
                or state.get("identity") != dict(self.contract.identity)
            ):
                if not events[-1].active_work:
                    raise RecoveryError("event log cannot rebuild missing active-work state")
                state = self._state_from_event(events[-1], current_route)
                self.state_store.write(state)
                self.telemetry.observe(
                    "state_rebuilt_from_event_log",
                    entity_id=self.contract.entity_id,
                    sequence=events[-1].sequence,
                )
            if state is None:
                raise RecoveryError("missing state pointer and event log")
            if state.get("schema_version") != SCHEMA_VERSION:
                raise RecoveryError("unsupported state schema version")
            if state.get("identity") != dict(self.contract.identity):
                raise RecoveryError("state identity does not match WAD identity")
            if state.get("durable_state_destinations") != list(
                self.contract.durable_state_destinations
            ):
                raise RecoveryError("state durable destinations do not match WAD contract")
            pointer = state.get(self.contract.active_work_pointer)
            if not isinstance(pointer, Mapping):
                raise RecoveryError("state is missing the contracted active-work pointer")
            sequence = int(state.get("last_sequence", 0))
            if sequence != len(events):
                raise RecoveryError("state sequence does not match event log")
            if not isinstance(state.get("last_event_id"), str) and sequence > 0:
                raise RecoveryError("state is missing the latest event id")

            checkpoint = self.checkpoint_store.latest(self.contract.entity_id)
            if checkpoint is None or checkpoint.sequence != sequence:
                self.telemetry.observe(
                    "checkpoint_rebuilt",
                    entity_id=self.contract.entity_id,
                    sequence=sequence,
                    previous_sequence=checkpoint.sequence if checkpoint else None,
                )
                checkpoint = self._checkpoint_from_state(state, events)
                self.checkpoint_store.save(checkpoint)
            self.telemetry.observe(
                "recovery_integrity",
                entity_id=self.contract.entity_id,
                sequence=sequence,
                event_count=len(events),
                model_id=current_route.model_id,
                adapter=current_route.adapter,
            )
            return RecoveryResult(
                contract=self.contract,
                state=state,
                events=events,
                current_route=current_route,
                checkpoint=checkpoint,
                telemetry=self.telemetry.snapshot(),
            )
        except (ContractError, RecoveryError, KeyError, TypeError, ValueError, OSError) as exc:
            self.telemetry.observe(
                "recovery_integrity_failure",
                entity_id=self.contract.entity_id,
                error=str(exc),
            )
            if isinstance(exc, ContinuityError):
                raise
            raise RecoveryError(f"recovery failed for {self.contract.entity_id}: {exc}") from exc
