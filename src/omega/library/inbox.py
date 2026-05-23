"""Intake Inbox — Queue content for curation and library ingestion.

AP: AP-OMEGA-INBOX-v1.0.0
ICS: [NODE: THOTH | ARCHETYPE: HERMES | CONTEXT: INBOX]

Users and agents drop URLs, files, notes, and bookmarks here.
The curation pipeline picks them up, processes them, and moves
them to the library or marks them as failed.

Tiers:
  pending/   — Items waiting for processing
  processing — Items currently being processed (with lock)
  failed/    — Items that failed processing (with error reason)
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.environ.get("OMEGA_DATA_DIR", str(Path.home() / "omega" / "data")))
INBOX_DIR = DATA_DIR / "inbox"
PENDING_DIR = INBOX_DIR / "pending"
PROCESSING_DIR = INBOX_DIR / "processing"
FAILED_DIR = INBOX_DIR / "failed"

for d in [PENDING_DIR, PROCESSING_DIR, FAILED_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class InboxStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InboxItem:
    """A single item in the intake inbox."""

    def __init__(
        self,
        item_id: str,
        source: str,
        source_type: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.item_id = item_id
        self.source = source  # URL, file path, note text
        self.source_type = source_type  # "url", "file", "note", "rss", "bookmark", "pdf"
        self.title = title
        self.tags = tags or []
        self.priority = priority  # 0=normal, 1=high, 2=urgent
        self.status = InboxStatus.PENDING
        self.metadata = metadata or {}
        self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "source": self.source,
            "source_type": self.source_type,
            "title": self.title,
            "tags": self.tags,
            "priority": self.priority,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InboxItem":
        item = cls(
            item_id=data["item_id"],
            source=data["source"],
            source_type=data["source_type"],
            title=data.get("title"),
            tags=data.get("tags", []),
            priority=data.get("priority", 0),
            metadata=data.get("metadata", {}),
        )
        item.status = InboxStatus(data.get("status", "pending"))
        item.created_at = data.get("created_at", item.created_at)
        return item


class InboxManager:
    """Manages the intake inbox queue."""

    def __init__(self):
        self._pending: Dict[str, InboxItem] = {}
        self._load()

    def _load(self) -> None:
        for path in PENDING_DIR.glob("*.json"):
            try:
                with open(path) as f:
                    item = InboxItem.from_dict(json.load(f))
                    self._pending[item.item_id] = item
            except Exception as e:
                logger.warning(f"Failed to load inbox item {path}: {e}")

    async def add(
        self,
        source: str,
        source_type: str = "url",
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> InboxItem:
        """Add an item to the intake inbox."""
        item_id = f"in_{uuid.uuid4().hex[:12]}"
        item = InboxItem(
            item_id=item_id,
            source=source,
            source_type=source_type,
            title=title or source[:80],
            tags=tags,
            priority=priority,
            metadata=metadata,
        )
        path = PENDING_DIR / f"{item_id}.json"
        async with await anyio.open_file(str(path), "w") as f:
            await f.write(json.dumps(item.to_dict(), indent=2))
        self._pending[item_id] = item
        logger.info(f"Inbox added [{source_type}] {item.title}")
        return item

    async def add_url(self, url: str, tags: Optional[List[str]] = None, priority: int = 0) -> InboxItem:
        """Quick-add a URL to the inbox."""
        return await self.add(url, source_type="url", tags=tags, priority=priority)

    async def add_file(self, path: str, tags: Optional[List[str]] = None) -> InboxItem:
        """Quick-add a file path to the inbox."""
        return await self.add(path, source_type="file", title=Path(path).name, tags=tags)

    async def add_note(self, text: str, tags: Optional[List[str]] = None) -> InboxItem:
        """Quick-add a text note to the inbox."""
        title = text[:80] + ("..." if len(text) > 80 else "")
        return await self.add(text, source_type="note", title=title, tags=tags)

    async def list_pending(self, limit: int = 50) -> List[InboxItem]:
        """List all pending inbox items, sorted by priority."""
        items = sorted(
            self._pending.values(),
            key=lambda i: (-i.priority, i.created_at),
        )
        return items[:limit]

    async def count(self) -> Dict[str, int]:
        """Get inbox counts by status."""
        pending = len(list(PENDING_DIR.glob("*.json")))
        processing = len(list(PROCESSING_DIR.glob("*.json")))
        failed = len(list(FAILED_DIR.glob("*.json")))
        return {"pending": pending, "processing": processing, "failed": failed, "total": pending + processing + failed}

    async def mark_processing(self, item_id: str) -> Optional[InboxItem]:
        """Move item from pending to processing (atomic rename)."""
        src = PENDING_DIR / f"{item_id}.json"
        if not src.exists():
            return None
        dst = PROCESSING_DIR / f"{item_id}.json"
        src.rename(dst)
        item = self._pending.pop(item_id, None)
        if item:
            item.status = InboxStatus.PROCESSING
        return item

    async def mark_completed(self, item_id: str) -> None:
        """Remove a completed item from the inbox."""
        for d in [PENDING_DIR, PROCESSING_DIR]:
            path = d / f"{item_id}.json"
            if path.exists():
                path.unlink()
                break
        self._pending.pop(item_id, None)

    async def mark_failed(self, item_id: str, error: str) -> None:
        """Move item to failed with error reason."""
        src = PROCESSING_DIR / f"{item_id}.json"
        if not src.exists():
            src = PENDING_DIR / f"{item_id}.json"
        if not src.exists():
            return
        try:
            with open(src) as f:
                data = json.load(f)
        except Exception:
            data = {"item_id": item_id}
        data["error"] = error
        data["failed_at"] = datetime.now(timezone.utc).isoformat()
        dst = FAILED_DIR / f"{item_id}.json"
        with open(dst, "w") as f:
            json.dump(data, f, indent=2)
        src.unlink()
        self._pending.pop(item_id, None)
        logger.warning(f"Inbox item failed: {item_id} — {error}")

    async def get(self, item_id: str) -> Optional[InboxItem]:
        """Get inbox item by ID."""
        if item_id in self._pending:
            return self._pending[item_id]
        for d in [PENDING_DIR, PROCESSING_DIR, FAILED_DIR]:
            path = d / f"{item_id}.json"
            if path.exists():
                try:
                    with open(path) as f:
                        return InboxItem.from_dict(json.load(f))
                except Exception:
                    pass
        return None

    async def clear_completed(self) -> int:
        """Remove all completed/failed items from inbox."""
        count = 0
        for path in list(FAILED_DIR.glob("*.json")):
            path.unlink()
            count += 1
        return count

    async def add_batch(
        self,
        sources: List[Dict[str, Any]],
    ) -> List[InboxItem]:
        """Add multiple items at once. Each dict needs 'source' key, optional 'source_type', 'tags', 'priority'."""
        items = []
        for s in sources:
            item = await self.add(
                source=s["source"],
                source_type=s.get("source_type", "url"),
                title=s.get("title"),
                tags=s.get("tags"),
                priority=s.get("priority", 0),
                metadata=s.get("metadata"),
            )
            items.append(item)
        return items
