#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-COMPACTION-CAPTURE-v1.0.0
"""
COMPACTION CAPTURE SIDECAR (P0 from 4-Week Search Sprint)

Polls OpenCode SQLite DB for new compaction summaries and:
1. Routes summary text to active entity workspace
2. Creates snapshot markdown with full metadata
3. Tracks last_seen_message_id for monotonic idempotency

Deployment: Polling service (not systemd — intentional design per D-201).
Poll interval: 5s via SQLite read-only (proven pattern).

Usage:
    python scripts/compaction_capture.py --start    # start background poller
    python scripts/compaction_capture.py --scan     # one-shot scan
    python scripts/compaction_capture.py --status   # show state

Follows Mandate 1 (AnyIO Absolute), Mandate 18 (Token Efficiency),
Mandate 23 (Failure Integrity).
"""

import json
import logging
import sqlite3
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

import anyio

# ============================================================================
# CONFIGURATION
# ============================================================================

OPENCODE_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
POLL_INTERVAL_SEC = 5.0
ENTITY_DATA_DIR = Path("data/entities")
WORKSPACE_SUBDIR = "compactions"
SESSION_MAP_PATH = Path("data/coordination/SESSION_ENTITY_MAP.yaml")

logger = logging.getLogger("compaction_capture")


# ============================================================================
# MODELS
# ============================================================================


@dataclass
class CompactionSummary:
    """A captured compaction summary from OpenCode."""

    session_id: str
    message_id: str
    part_id: str
    summary_text: str
    timestamp: float
    reason: str = "unknown"
    agent: str = "unknown"
    model_id: str = "unknown"
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def char_count(self) -> int:
        return len(self.summary_text)


# ============================================================================
# CAPTURE SERVICE
# ============================================================================


class CompactionCaptureService:
    """Sidecar that captures OpenCode compaction summaries.

    Polls the OpenCode SQLite database in read-only mode every 5 seconds.
    When new compaction summary messages are found, captures the summary text
    and routes it to the appropriate entity workspace as a markdown file.
    """

    def __init__(
        self,
        opencode_db: Optional[Path] = None,
        poll_interval: float = POLL_INTERVAL_SEC,
        entity_data_dir: Optional[Path] = None,
        session_map_path: Optional[Path] = None,
    ):
        self._opencode_db = opencode_db or OPENCODE_DB
        self._poll_interval = poll_interval
        self._entity_data_dir = entity_data_dir or ENTITY_DATA_DIR
        self._session_map_path = session_map_path or SESSION_MAP_PATH
        self._last_seen_message_id = 0
        self._session_map = self._load_session_map()
        self._running = False
        self._stats: Dict[str, int] = {
            "total_scanned": 0,
            "total_captured": 0,
            "total_errors": 0,
        }

    # ── Lifecycle ─────────────────────────────────────────────────────

    async def start(self, task_group: anyio.abc.TaskGroup) -> None:
        """Start the background capture loop within a task group."""
        self._running = True
        self._last_seen_message_id = self._get_current_max_id()
        task_group.start_soon(self._capture_loop)
        logger.info(
            "CompactionCapture online — last_seen_id=%d, interval=%.1fs",
            self._last_seen_message_id,
            self._poll_interval,
        )

    async def stop(self) -> None:
        """Stop the capture loop."""
        self._running = False

    # ── Core Loop ─────────────────────────────────────────────────────

    async def _capture_loop(self) -> None:
        """Periodic polling loop — scans for new compaction summaries."""
        while self._running:
            try:
                captured = self.scan_for_summaries()
                self._stats["total_captured"] += len(captured)
                if captured:
                    logger.info(
                        "Captured %d compaction summaries", len(captured)
                    )
            except Exception as e:
                self._stats["total_errors"] += 1
                logger.error("Capture cycle failed: %s", e, exc_info=True)
            await anyio.sleep(self._poll_interval)

    # ── DB Scanning ───────────────────────────────────────────────────

    def scan_for_summaries(self) -> List[CompactionSummary]:
        """Scan OpenCode DB for new compaction summary messages.

        Uses read-only SQLite connection (no lock contention with OpenCode).
        Monotonic idempotency via last_seen_message_id.
        """
        if not self._opencode_db.exists():
            logger.debug("OpenCode DB not found at %s", self._opencode_db)
            return []

        uri = f"file:{self._opencode_db}?mode=ro"
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=5.0)
            conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            logger.error("Failed to open DB: %s", e)
            return []

        try:
            rows = conn.execute(
                """
                SELECT
                    m.id as message_id,
                    m.session_id,
                    m.data as message_data,
                    p.id as part_id,
                    p.data as part_data,
                    p.time_created
                FROM message m
                JOIN part p ON p.message_id = m.id
                WHERE m.id > ?
                  AND json_extract(m.data, '$.role') = 'assistant'
                  AND json_extract(m.data, '$.summary') = true
                  AND json_extract(p.data, '$.type') = 'text'
                ORDER BY m.id ASC
                """,
                (self._last_seen_message_id,),
            ).fetchall()
        except sqlite3.Error as e:
            logger.error("DB query failed: %s", e)
            return []
        finally:
            conn.close()

        self._stats["total_scanned"] += len(rows)
        captured: List[CompactionSummary] = []

        for row in rows:
            try:
                msg_data = (
                    json.loads(row["message_data"])
                    if isinstance(row["message_data"], str)
                    else row["message_data"]
                )
                part_data = (
                    json.loads(row["part_data"])
                    if isinstance(row["part_data"], str)
                    else row["part_data"]
                )
                summary_text = part_data.get("text", "")
                if not summary_text:
                    continue

                summary = CompactionSummary(
                    session_id=row["session_id"],
                    message_id=str(row["message_id"]),
                    part_id=str(row["part_id"]),
                    summary_text=summary_text,
                    timestamp=row["time_created"] / 1000.0,
                    agent=msg_data.get("agent", "unknown"),
                    model_id=msg_data.get("modelID", "unknown"),
                    raw_data={"message": msg_data, "part": part_data},
                )
                self._route_to_workspace(summary)
                captured.append(summary)
                self._last_seen_message_id = max(
                    self._last_seen_message_id, int(row["message_id"])
                )
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.error(
                    "Failed to capture message %s: %s", row["message_id"], e
                )
                self._stats["total_errors"] += 1

        return captured

    # ── DB Helpers ─────────────────────────────────────────────────────

    def _get_current_max_id(self) -> int:
        """Get the current maximum message ID from the OpenCode DB."""
        if not self._opencode_db.exists():
            return 0
        uri = f"file:{self._opencode_db}?mode=ro"
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=5.0)
            try:
                row = conn.execute("SELECT MAX(id) FROM message").fetchone()
                return int(row[0]) if row and row[0] else 0
            finally:
                conn.close()
        except sqlite3.Error as e:
            logger.error("Failed to get max ID: %s", e)
            return 0

    # ── Session Map ────────────────────────────────────────────────────

    def _load_session_map(self) -> Dict[str, str]:
        """Load session-to-entity mapping from YAML file."""
        if not self._session_map_path.exists():
            logger.debug("Session map not found at %s", self._session_map_path)
            return {}
        try:
            import yaml

            data = yaml.safe_load(self._session_map_path.read_text())
            return {
                m["opencode_session"]: m["omega_entity"]
                for m in (data or {}).get("session_mappings", [])
            }
        except ImportError:
            logger.warning("PyYAML not installed — session map disabled")
            return {}
        except (yaml.YAMLError, OSError, KeyError, TypeError) as e:
            logger.warning("Failed to load session map: %s", e)
            return {}

    def _resolve_entity(self, session_id: str, directory: str = "") -> str:
        """Resolve entity name from session ID or directory heuristic."""
        if session_id in self._session_map:
            return self._session_map[session_id]
        if directory:
            for entity_dir in self._entity_data_dir.iterdir():
                if entity_dir.is_dir() and entity_dir.name in directory:
                    return entity_dir.name
        return "default"

    # ── Workspace Routing ──────────────────────────────────────────────

    def _route_to_workspace(self, summary: CompactionSummary) -> Path:
        """Route a compaction summary to the appropriate entity workspace.

        Returns the path of the written file.
        """
        entity = self._resolve_entity(summary.session_id)
        workspace_dir = self._entity_data_dir / entity / WORKSPACE_SUBDIR
        workspace_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.fromtimestamp(summary.timestamp).strftime("%Y%m%d_%H%M%S")
        file_path = workspace_dir / f"{ts}_{summary.session_id[:12]}.md"
        file_path.write_text(self._format_markdown(summary, entity))
        logger.debug("Routed to %s", file_path)
        return file_path

    def _format_markdown(self, summary: CompactionSummary, entity: str) -> str:
        """Format a compaction summary as markdown."""
        return f"""# Compaction {datetime.fromtimestamp(summary.timestamp).isoformat()}

**Entity**: {entity}
**Session**: {summary.session_id}
**Message ID**: {summary.message_id}
**Part ID**: {summary.part_id}
**Agent**: {summary.agent}
**Model**: {summary.model_id}
**Captured**: {datetime.now(timezone.utc).isoformat()}

---

{summary.summary_text}
"""

    # ── Status ─────────────────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Get current capture service status."""
        return {
            "running": self._running,
            "last_seen_message_id": self._last_seen_message_id,
            "session_mappings": len(self._session_map),
            "stats": dict(self._stats),
            "opencode_db_exists": self._opencode_db.exists(),
            "opencode_db_size_mb": (
                self._opencode_db.stat().st_size / 1e6
                if self._opencode_db.exists()
                else 0
            ),
        }


# ============================================================================
# SINGLETON
# ============================================================================

_capture: Optional[CompactionCaptureService] = None


def get_capture() -> CompactionCaptureService:
    """Get the singleton CompactionCaptureService instance."""
    global _capture
    if _capture is None:
        _capture = CompactionCaptureService()
    return _capture


def reset_capture() -> None:
    """Reset the singleton (for testing)."""
    global _capture
    _capture = None


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s"
    )
    parser = argparse.ArgumentParser(
        description="OpenCode Compaction Capture Sidecar"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--start", action="store_true", help="Start background poller"
    )
    group.add_argument(
        "--scan", action="store_true", help="One-shot scan"
    )
    group.add_argument(
        "--status", action="store_true", help="Show status"
    )
    args = parser.parse_args()

    capture = get_capture()

    if args.status:
        print(json.dumps(capture.get_status(), indent=2))
    elif args.scan:
        captured = capture.scan_for_summaries()
        print(f"Captured {len(captured)} compaction summaries")
        for s in captured:
            print(
                f"  session={s.session_id[:16]}... "
                f"chars={s.char_count} agent={s.agent}"
            )
    elif args.start:

        async def run() -> None:
            async with anyio.create_task_group() as tg:
                await capture.start(tg)
                while True:
                    await anyio.sleep(3600)

        anyio.run(run)
    else:
        parser.print_help()
        sys.exit(1)
