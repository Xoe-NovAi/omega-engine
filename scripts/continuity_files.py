"""POSIX file coordinator for the portable continuity kernel.

The coordinator is an adapter. The core kernel depends only on the CommitJournal
protocol, so platform-specific locking does not leak into the portable contract.
"""

from __future__ import annotations

import fcntl
from pathlib import Path

from scripts.continuity_kernel import (
    CommitIntent,
    _atomic_write,
    _canonical_json,
    _fsync_directory,
    _read_json_object,
    _validate_entity_id,
)


class FileLock:
    """POSIX advisory lock for one entity's commit stream."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._handle = None

    def __enter__(self) -> "FileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("a+", encoding="utf-8")
        fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._handle is None:
            return
        try:
            fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        finally:
            self._handle.close()
            self._handle = None


class FileCommitJournal:
    """Prepared-intent journal for the file-backed multi-file commit."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _entity_root(self, entity_id: str) -> Path:
        _validate_entity_id(entity_id)
        return self.root / entity_id

    def _intent_path(self, intent: CommitIntent) -> Path:
        return (
            self._entity_root(intent.event.entity_id)
            / "intents"
            / f"{intent.intent_id}.json"
        )

    def lock(self, entity_id: str) -> FileLock:
        _validate_entity_id(entity_id)
        return FileLock(self.root / f"{entity_id}.lock")

    def prepare(self, intent: CommitIntent) -> None:
        _atomic_write(self._intent_path(intent), _canonical_json(intent.to_dict()) + "\n")

    def pending(self, entity_id: str) -> list[CommitIntent]:
        root = self._entity_root(entity_id) / "intents"
        if not root.is_dir():
            return []
        intents = [
            CommitIntent.from_dict(_read_json_object(path, "commit intent"))
            for path in sorted(root.glob("*.json"))
        ]
        return sorted(intents, key=lambda intent: intent.created_at)

    def commit(self, intent_id: str, entity_id: str) -> None:
        path = self._entity_root(entity_id) / "intents" / f"{intent_id}.json"
        if path.exists():
            path.unlink()
            _fsync_directory(path.parent)
