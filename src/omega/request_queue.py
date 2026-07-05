# 🔱 Omega Engine — Request Queue System
# AP: AP-REQUEST-QUEUE-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: QUEUE | CONTEXT: OFFLINE-MODE]
#
# Implements the "Data Comes Home" principle:
# Offline research requests queue to disk for execution when connectivity returns.
# Cloud review requests queue for consultant pattern evaluation.
#
# Mandates: AnyIO (Mandate 1), Engine-Stack Firewall (Mandate 2),
#           Local-First (Mandate 7), Error Integrity (Mandate 9),
#           Queue Integrity (Mandate 12)

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio

from omega.errors import OmegaError

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
REQUESTS_DIR = DATA_DIR / "requests"
QUEUED_DIR = REQUESTS_DIR / "queued"
REVIEW_DIR = REQUESTS_DIR / "review"
COMPLETED_DIR = REQUESTS_DIR / "completed"
DEAD_DIR = REQUESTS_DIR / "dead"
INDEX_PATH = REQUESTS_DIR / "INDEX.json"


# ── Error Types ──────────────────────────────────────────────────────────────

class QueueError(OmegaError):
    """Base for queue system errors."""

class QueueFullError(QueueError):
    """Queue is at capacity."""

class RequestNotFoundError(QueueError):
    """Request ID not found in any queue."""

class RequestStaleError(QueueError):
    """Request is too old to process."""


# ── Queue Manager ────────────────────────────────────────────────────────────

class RequestQueue:
    """
    Async-safe queue manager for offline research and cloud review requests.
    All file I/O is wrapped in anyio.to_thread.run_sync.
    """

    MAX_QUEUED = 1000
    MAX_REVIEW = 500
    STALE_DAYS = 7

    def __init__(self, requests_dir: Optional[Path] = None):
        self._requests_dir = Path(requests_dir) if requests_dir else REQUESTS_DIR
        self._queued_dir = self._requests_dir / "queued"
        self._review_dir = self._requests_dir / "review"
        self._completed_dir = self._requests_dir / "completed"

    # ── Initialization ────────────────────────────────────────────────────

    async def ensure_dirs(self):
        """Ensure all queue directories exist."""
        for d in [self._queued_dir, self._review_dir, self._completed_dir, DEAD_DIR]:
            await anyio.to_thread.run_sync(lambda d=d: d.mkdir(parents=True, exist_ok=True))

    # ── Create Requests ───────────────────────────────────────────────────

    async def create_queued_request(
        self,
        query: str,
        priority: str = "P2",
        context: str = "",
        created_by: str = "unknown",
        requires: Optional[List[str]] = None,
        fallback_tools: Optional[List[str]] = None,
        timeout_sec: int = 300,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """Create an offline research request."""
        await self.ensure_dirs()

        # Check capacity
        count = await self._count_files(self._queued_dir)
        if count >= self.MAX_QUEUED:
            raise QueueFullError(
                f"Queued directory at capacity ({count}/{self.MAX_QUEUED})",
                context={"directory": str(self._queued_dir)},
            )

        req_id = f"req_{uuid.uuid4().hex[:8]}"
        request = {
            "id": req_id,
            "query": query,
            "priority": priority,
            "context": context,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "requires": requires or ["websearch"],
            "fallback_tools": fallback_tools or ["webfetch"],
            "timeout_sec": timeout_sec,
            "max_retries": max_retries,
            "status": "queued",
        }

        filepath = self._queued_dir / f"{req_id}.json"
        await anyio.to_thread.run_sync(self._write_json, filepath, request)
        await self._update_index()
        logger.info("Queued request %s: %s", req_id, query[:80])
        return request

    async def create_review_request(
        self,
        work_product_path: str,
        review_aspects: Optional[List[str]] = None,
        preferred_model: str = "auto",
        created_by: str = "unknown",
    ) -> Dict[str, Any]:
        """Create a cloud review delegation request."""
        await self.ensure_dirs()

        count = await self._count_files(self._review_dir)
        if count >= self.MAX_REVIEW:
            raise QueueFullError(
                f"Review directory at capacity ({count}/{self.MAX_REVIEW})",
                context={"directory": str(self._review_dir)},
            )

        req_id = f"review_{uuid.uuid4().hex[:8]}"
        request = {
            "id": req_id,
            "work_product_path": work_product_path,
            "review_aspects": review_aspects or ["fact_check", "deepening", "enhancement"],
            "preferred_model": preferred_model,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending_review",
        }

        filepath = self._review_dir / f"{req_id}.json"
        await anyio.to_thread.run_sync(self._write_json, filepath, request)
        await self._update_index()
        logger.info("Created review request %s for %s", req_id, work_product_path)
        return request

    # ── Read / Query ─────────────────────────────────────────────────────

    async def get_queued_requests(self) -> List[Dict[str, Any]]:
        """Get all queued requests, sorted by priority."""
        requests = await self._load_requests(self._queued_dir)
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        requests.sort(key=lambda r: priority_order.get(r.get("priority", "P2"), 99))
        return requests

    async def get_review_requests(self) -> List[Dict[str, Any]]:
        """Get all pending review requests."""
        return await self._load_requests(self._review_dir)

    async def get_completed_requests(self) -> List[Dict[str, Any]]:
        """Get all completed requests."""
        return await self._load_requests(self._completed_dir)

    async def get_request(self, req_id: str) -> Optional[Dict[str, Any]]:
        """Find a request by ID across all queues."""
        for directory in [self._queued_dir, self._review_dir, self._completed_dir]:
            filepath = directory / f"{req_id}.json"
            exists = await anyio.to_thread.run_sync(filepath.exists)
            if exists:
                return await anyio.to_thread.run_sync(self._read_json, filepath)
        return None

    # ── Process / Complete ───────────────────────────────────────────────

    async def complete_request(
        self, req_id: str, result: Dict[str, Any]
    ) -> bool:
        """Move a request from queued/review to completed with result."""
        source_dirs = [self._queued_dir, self._review_dir]
        for directory in source_dirs:
            filepath = directory / f"{req_id}.json"
            exists = await anyio.to_thread.run_sync(filepath.exists)
            if exists:
                request = await anyio.to_thread.run_sync(self._read_json, filepath)
                request["status"] = "completed"
                request["completed_at"] = datetime.now(timezone.utc).isoformat()
                request["result"] = result

                # Write to completed
                completed_path = self._completed_dir / f"{req_id}.json"
                await anyio.to_thread.run_sync(self._write_json, completed_path, request)

                # Remove from source
                await anyio.to_thread.run_sync(filepath.unlink)
                await self._update_index()
                logger.info("Completed request %s", req_id)
                return True
        return False

    async def fail_request(
        self, req_id: str, error: str, permanent: bool = False
    ) -> bool:
        """
        Handle request failure. 
        If permanent=True or retries exhausted, move to dead-letter queue.
        """
        source_dirs = [self._queued_dir, self._review_dir]
        for directory in source_dirs:
            filepath = directory / f"{req_id}.json"
            exists = await anyio.to_thread.run_sync(filepath.exists)
            if exists:
                request = await anyio.to_thread.run_sync(self._read_json, filepath)
                
                # Update retry count
                retries = request.get("retries", 0) + 1
                request["retries"] = retries
                request["last_error"] = error
                request["last_error_at"] = datetime.now(timezone.utc).isoformat()

                if permanent or retries >= request.get("max_retries", 2):
                    # Move to Dead Letter Queue
                    request["status"] = "failed"
                    dead_path = DEAD_DIR / f"{req_id}.json"
                    await anyio.to_thread.run_sync(self._write_json, dead_path, request)
                    await anyio.to_thread.run_sync(filepath.unlink)
                    logger.error("Request %s moved to DLQ: %s", req_id, error)
                else:
                    # Keep in queue for retry
                    request["status"] = "queued"
                    await anyio.to_thread.run_sync(self._write_json, filepath, request)
                    logger.warning("Request %s failed (retry %d): %s", req_id, retries, error)

                await self._update_index()
                return True
        return False

    async def prune_stale(self, days: Optional[int] = None) -> int:
        """Remove requests older than N days. Returns number pruned."""
        if days is None:
            days = self.STALE_DAYS
        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
        pruned = 0

        for directory in [self._queued_dir, self._review_dir, self._completed_dir]:
            files = await anyio.to_thread.run_sync(
                lambda: list(directory.glob("*.json"))
            )
            for fpath in files:
                mtime = await anyio.to_thread.run_sync(fpath.stat)
                if mtime.st_mtime < cutoff and fpath.name != "INDEX.json":
                    await anyio.to_thread.run_sync(fpath.unlink)
                    pruned += 1

        await self._update_index()
        return pruned

    async def stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        return {
            "queued": await self._count_files(self._queued_dir),
            "pending_review": await self._count_files(self._review_dir),
            "completed": await self._count_files(self._completed_dir),
            "dead": await self._count_files(DEAD_DIR),
        }

    # ── Private Helpers ──────────────────────────────────────────────────

    async def _count_files(self, directory: Path) -> int:
        """Count JSON files in a directory (excludes INDEX.json)."""
        try:
            files = await anyio.to_thread.run_sync(
                lambda: [f for f in directory.iterdir() if f.suffix == ".json" and f.name != "INDEX.json"]
            )
            return len(files)
        except FileNotFoundError:
            return 0

    async def _load_requests(self, directory: Path) -> List[Dict[str, Any]]:
        """Load all JSON request files from a directory."""
        try:
            files = await anyio.to_thread.run_sync(
                lambda: sorted(directory.glob("*.json"))
            )
            results = []
            for fpath in files:
                if fpath.name == "INDEX.json":
                    continue
                data = await anyio.to_thread.run_sync(self._read_json, fpath)
                if data:
                    results.append(data)
            return results
        except FileNotFoundError:
            return []

    async def _update_index(self):
        """Write INDEX.json with current queue state."""
        index = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "stats": await self.stats(),
        }
        await anyio.to_thread.run_sync(self._write_json, INDEX_PATH, index)

    @staticmethod
    def _write_json(filepath: Path, data: dict):
        """Atomically write a JSON file."""
        tmp = filepath.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                f.flush()
            tmp.rename(filepath)
        except OmegaError:
            if tmp.exists():
                tmp.unlink()
            raise
        except (OSError, RuntimeError) as e:
            if tmp.exists():
                tmp.unlink()
            logger.error(f"Unexpected failure writing {filepath}: {e}", exc_info=True)
            raise OmegaError(f"Failed to write {filepath}: {e}") from e

    @staticmethod
    def _read_json(filepath: Path) -> Optional[Dict[str, Any]]:
        """Safely read a JSON file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning("Failed to read %s: %s", filepath, e)
            return None
