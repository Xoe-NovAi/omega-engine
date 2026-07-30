"""
Scribe Hub Master — SQLite Data Layer + Markdown View (AnyIO Compliant)
Dual-write architecture: SQLite (source of truth) → Markdown (rendered view)
All blocking I/O runs in thread pools via anyio.to_thread.run_sync.
Signal handling uses anyio.open_signal_receiver.
"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiosqlite
import anyio
from anyio import to_thread, open_signal_receiver, create_task_group
from yyds_fswatch import FSWatcher

from src.omega.agents.scribe.parser import HubBroadcast, HubUpdatePlan
from src.omega.agents.scribe.lock import managed_hub_lock, atomic_write


# ─────────────────────────────────────────────────────────────
# SQLite Schema & Initialization
# ─────────────────────────────────────────────────────────────

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS agents (
    agent_id    TEXT PRIMARY KEY,
    role        TEXT NOT NULL,
    last_seen   TIMESTAMP NOT NULL,
    status      TEXT DEFAULT 'active',
    metadata    JSON
);

CREATE TABLE IF NOT EXISTS broadcasts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id    TEXT REFERENCES agents(agent_id),
    intent      TEXT NOT NULL,
    summary     TEXT NOT NULL,
    data        JSON,
    timestamp   TIMESTAMP NOT NULL,
    session_id  TEXT
);
CREATE INDEX IF NOT EXISTS idx_broadcasts_agent_ts ON broadcasts(agent_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_broadcasts_intent ON broadcasts(intent);

CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY,
    agent_id    TEXT REFERENCES agents(agent_id),
    summary     TEXT NOT NULL,
    ticket_id   TEXT,
    timestamp   TIMESTAMP NOT NULL,
    ratified_by TEXT
);

CREATE TABLE IF NOT EXISTS blockers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id    TEXT REFERENCES agents(agent_id),
    severity    TEXT NOT NULL,
    description TEXT NOT NULL,
    ticket_id   TEXT,
    status      TEXT DEFAULT 'open',
    created_at  TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_blockers_status ON blockers(status);

CREATE TABLE IF NOT EXISTS sprint_status (
    sprint      TEXT PRIMARY KEY,
    phase       TEXT NOT NULL,
    status      TEXT NOT NULL,
    gate        TEXT,
    owner       TEXT,
    updated_at  TIMESTAMP NOT NULL
);
"""


async def init_hub_db(db_path: Path) -> None:
    """Initialize Hub SQLite database with WAL mode."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()


# ─────────────────────────────────────────────────────────────
# Hub Master — Event-Driven, Dual-Write
# ─────────────────────────────────────────────────────────────

class HubMaster:
    """
    Scribe Hub Master with event-driven filesystem watching and dual-write persistence.
    
    Architecture:
    1. Watch HALL_OF_RECORDS for new session JSON files (yyds-fswatch)
    2. Parse broadcasts → validate with HubBroadcast schema
    3. UPSERT into SQLite (source of truth, ACID, queryable)
    4. Render Markdown view from SQLite (human-readable, git-tracked)
    
    AnyIO Compliance:
    - All blocking I/O via anyio.to_thread.run_sync
    - Signal handling via anyio.open_signal_receiver
    - Task groups for structured concurrency
    - Cancellation scopes for graceful shutdown
    """
    
    def __init__(
        self,
        hall_of_records: str = "data/knowledge/HALL_OF_RECORDS",
        hub_md_path: str = "data/coordination/HMC_COLLABORATION_HUB.md",
        db_path: str = "data/coordination/hub.db",
        debounce_ms: int = 50,
    ):
        self.hall_of_records = Path(hall_of_records)
        self.hub_md_path = Path(hub_md_path)
        self.db_path = Path(db_path)
        self.debounce_ms = debounce_ms
        
        self._watcher: Optional[FSWatcher] = None
        self._running = False
        self._last_processed: Dict[str, float] = {}  # session_id -> mtime
        
        # Ensure directories exist
        self.hub_md_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def start(self):
        """Start the event-driven Hub Master loop with signal handling."""
        self._running = True
        
        # Initialize database
        await init_hub_db(self.db_path)
        
        # Create initial Markdown if missing
        if not self.hub_md_path.exists():
            await self._render_markdown_view()
        
        print(f"[{datetime.now().isoformat()}] Hub Master started")
        print(f"  Watching: {self.hall_of_records}")
        print(f"  Database: {self.db_path}")
        print(f"  Markdown: {self.hub_md_path}")
        
        # Level 4: Async Native Iterator (recommended)
        self._watcher = FSWatcher(
            str(self.hall_of_records),
            debounce=self.debounce_ms / 1000.0,  # Convert to seconds
            recursive=True,
            ignore_patterns=["*.tmp", "*.lock", "*.swp", "*.swx"],
        )
        
        # Use task group for structured concurrency with signal handling
        async with create_task_group() as tg:
            # Signal handler task
            tg.start_soon(self._signal_handler)
            
            # Main event loop
            async with self._watcher as w:
                async for event in w:
                    if not self._running:
                        break
                    await self._handle_fs_event(event)
    
    async def _signal_handler(self):
        """Handle OS signals for graceful shutdown using AnyIO."""
        async with open_signal_receiver(anyio.SIGINT, anyio.SIGTERM) as signals:
            async for signum in signals:
                print(f"[{datetime.now().isoformat()}] Received signal {signum}, shutting down...")
                self._running = False
                # Cancel the task group to exit cleanly
                return
    
    def stop(self):
        """Stop the Hub Master."""
        self._running = False
        if self._watcher:
            self._watcher.close()
    
    async def _handle_fs_event(self, event):
        """Process filesystem event — only care about new session JSON files."""
        # Only process created/moved_to events for .json files
        if event.event_type not in ("created", "moved_to"):
            return
        
        path = Path(event.src_path)
        if path.suffix != ".json" or "session" not in path.name.lower():
            return
        
        # Debounce: skip if we processed this file recently
        mtime = path.stat().st_mtime
        if path.name in self._last_processed and mtime <= self._last_processed[path.name]:
            return
        self._last_processed[path.name] = mtime
        
        try:
            await self._process_session_file(path)
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error processing {path}: {e}")
    
    async def _process_session_file(self, session_path: Path):
        """Parse session file and extract broadcasts."""
        try:
            content = await to_thread.run_sync(session_path.read_text)
            session_data = json.loads(content)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[{datetime.now().isoformat()}] Failed to read {session_path}: {e}")
            return
        
        # Extract context posts (broadcasts) from session
        broadcasts = self._extract_broadcasts(session_data, session_path.stem)
        
        if not broadcasts:
            return
        
        # Process each broadcast
        for broadcast in broadcasts:
            await self.process_broadcast(broadcast)
        
        # Render updated Markdown view
        await self._render_markdown_view()
        
        print(f"[{datetime.now().isoformat()}] Processed {len(broadcasts)} broadcasts from {session_path.name}")
    
    def _extract_broadcasts(self, session_data: Dict[str, Any], session_id: str) -> List[HubBroadcast]:
        """Extract and validate broadcasts from session data."""
        broadcasts = []
        
        # Handle different session data formats
        context_posts = session_data.get("context_posts", [])
        if not context_posts:
            # Fallback: single context object
            context = session_data.get("context", {})
            if context.get("entity") and context.get("entity") != "scribe":
                context_posts = [context]
        
        for post in context_posts:
            entity = post.get("entity", "unknown")
            if entity == "scribe":
                continue  # Skip our own posts
            
            try:
                broadcast = HubBroadcast(
                    agent=entity,
                    timestamp=datetime.fromisoformat(
                        post.get("timestamp", datetime.now().isoformat()).replace('Z', '+00:00')
                    ),
                    intent=post.get("intent", "status"),
                    summary=post.get("continuation", post.get("task_current", ""))[:500],
                    ticket_id=self._extract_ticket_id(post),
                    decision_id=self._extract_decision_id(post),
                    carmack_mode="carmack" in post.get("continuation", "").lower(),
                    leverage_ratio=self._extract_leverage_ratio(post.get("continuation", "")),
                    data={
                        "decisions": post.get("decisions", []),
                        "focus_chain": post.get("focus_chain", []),
                        "task_current": post.get("task_current", ""),
                    }
                )
                broadcasts.append(broadcast)
            except Exception as e:
                print(f"[{datetime.now().isoformat()}] Failed to parse broadcast: {e}")
        
        return broadcasts
    
    def _extract_ticket_id(self, post: Dict[str, Any]) -> Optional[str]:
        """Extract ticket ID from decisions or summary."""
        for d in post.get("decisions", []):
            if d.startswith("C-") or d.startswith("P-"):
                return d.split()[0]
        return None
    
    def _extract_decision_id(self, post: Dict[str, Any]) -> Optional[str]:
        """Extract decision ID from decisions."""
        for d in post.get("decisions", []):
            if d.startswith("D-"):
                return d.split()[0]
        return None
    
    def _extract_leverage_ratio(self, text: str) -> Optional[str]:
        """Extract leverage ratio from text."""
        import re
        match = re.search(r'(\d+:\d+|\d+x)', text)
        return match.group(1) if match else None
    
    # ─────────────────────────────────────────────────────────
    # Dual-Write: SQLite (Truth) → Markdown (View)
    # ─────────────────────────────────────────────────────────
    
    async def process_broadcast(self, broadcast: HubBroadcast):
        """Process a single broadcast: SQLite UPSERT + Markdown render."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # 1. Upsert agent
            await db.execute("""
                INSERT INTO agents (agent_id, role, last_seen, status, metadata)
                VALUES (?, ?, ?, 'active', ?)
                ON CONFLICT(agent_id) DO UPDATE SET
                    last_seen = excluded.last_seen,
                    status = 'active',
                    metadata = excluded.metadata
            """, (
                broadcast.agent,
                self._infer_role(broadcast.agent),
                broadcast.timestamp.isoformat(),
                json.dumps(broadcast.data)
            ))
            
            # 2. Insert broadcast
            await db.execute("""
                INSERT INTO broadcasts (agent_id, intent, summary, data, timestamp, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                broadcast.agent,
                broadcast.intent,
                broadcast.summary,
                json.dumps(broadcast.data),
                broadcast.timestamp.isoformat(),
                broadcast.data.get("session_id")
            ))
            
            # 3. Handle decisions
            if broadcast.intent == "decision" and broadcast.decision_id:
                await db.execute("""
                    INSERT OR REPLACE INTO decisions (decision_id, agent_id, summary, ticket_id, timestamp, ratified_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    broadcast.decision_id,
                    broadcast.agent,
                    broadcast.summary,
                    broadcast.ticket_id,
                    broadcast.timestamp.isoformat(),
                    "kali"
                ))
            
            # 4. Handle blockers
            if broadcast.intent == "blocker":
                severity = broadcast.data.get("blocker_severity", "medium")
                await db.execute("""
                    INSERT INTO blockers (agent_id, severity, description, ticket_id, status, created_at)
                    VALUES (?, ?, ?, ?, 'open', ?)
                """, (
                    broadcast.agent,
                    severity,
                    broadcast.summary,
                    broadcast.ticket_id,
                    broadcast.timestamp.isoformat()
                ))
            
            await db.commit()
        
        # Render updated Markdown view
        await self._render_markdown_view()
    
    def _infer_role(self, agent: str) -> str:
        """Infer agent role from agent ID."""
        roles = {
            "maat": "Light Oversoul (P1-P5)",
            "lilith": "Dark Oversoul (P6-P10)",
            "researcher": "Deep Research",
            "pillar-p1": "Infrastructure",
            "pillar-p3": "Engineering",
            "pillar-p4": "Integration",
            "scribe": "Hub Master",
        }
        return roles.get(agent, "Agent")
    
    async def _render_markdown_view(self):
        """Render Markdown view from SQLite data."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Fetch all data and convert to dicts for thread-safe passing
            agents = [dict(r) for r in await (await db.execute(
                "SELECT * FROM agents ORDER BY role, agent_id"
            )).fetchall()]
            
            broadcasts = [dict(r) for r in await (await db.execute("""
                SELECT * FROM broadcasts ORDER BY timestamp DESC LIMIT 100
            """)).fetchall()]
            
            decisions = [dict(r) for r in await (await db.execute("""
                SELECT * FROM decisions ORDER BY timestamp DESC
            """)).fetchall()]
            
            blockers = [dict(r) for r in await (await db.execute("""
                SELECT * FROM blockers WHERE status = 'open' ORDER BY created_at DESC
            """)).fetchall()]
            
            sprint = await (await db.execute("SELECT * FROM sprint_status")).fetchone()
            sprint = dict(sprint) if sprint else None
        
        # Render using template (blocking CPU work in thread pool)
        markdown = await to_thread.run_sync(
            self._render_template, agents, broadcasts, decisions, blockers, sprint
        )
        
        # Atomic write with lock
        async with managed_hub_lock(str(self.hub_md_path)):
            await atomic_write(str(self.hub_md_path), markdown)
    
    def _render_template(
        self,
        agents: List[Any],
        broadcasts: List[Any],
        decisions: List[Any],
        blockers: List[Any],
        sprint: Optional[Any]
    ) -> str:
        """Render Markdown from structured data (CPU-bound, runs in thread pool)."""
        lines = [
            "# 🔱 HMC Collaboration Hub",
            f"**Version**: 2.0 (SQLite-backed)",
            f"**Updated**: {datetime.now().isoformat()}",
            f"**Maintained by**: @scribe (Hub Master)",
            "",
            "---",
            "",
            "## 🏁 Sprint Status",
            "| Sprint | Phase | Status | Gate | Owner |",
            "|--------|-------|--------|------|-------|",
        ]
        
        if sprint:
            lines.append(f"| {sprint['sprint']} | {sprint['phase']} | {sprint['status']} | {sprint['gate'] or '-'} | {sprint['owner'] or '-'} |")
        else:
            lines.append("| Guard & Distill | Complete | ✅ Done | - | @maat |")
            lines.append("| ARF | Phase 1 | 🔄 Active | - | @researcher |")
        
        lines.extend(["", "## ⚖️ Decisions Log", "| ID | Timestamp | Agent | Summary | Ticket |", "|----|-----------|-------|---------|--------|"])
        
        for d in decisions:
            ts = d["timestamp"][:19] if d["timestamp"] else "-"
            lines.append(f"| {d['decision_id']} | {ts} | {d['agent_id']} | {d['summary'][:60]} | {d['ticket_id'] or '-'} |")
        
        lines.extend(["", "## 🚧 Blockers & Requests", "| ID | Timestamp | Agent | Severity | Description | Ticket |", "|----|-----------|-------|----------|-------------|--------|"])
        
        for b in blockers:
            ts = b["created_at"][:19] if b["created_at"] else "-"
            lines.append(f"| {b['id']} | {ts} | {b['agent_id']} | {b['severity']} | {b['description'][:60]} | {b['ticket_id'] or '-'} |")
        
        lines.extend(["", "## 🧑‍💼 Agent Sections"])
        
        # Group broadcasts by agent
        by_agent: Dict[str, List[str]] = {}
        for b in broadcasts:
            agent = b["agent_id"]
            if agent not in by_agent:
                by_agent[agent] = []
            
            ts = b["timestamp"][:16] if b["timestamp"] else "-"
            intent_emoji = {
                "status": "📋",
                "decision": "⚖️",
                "blocker": "🚧",
                "handoff_complete": "✅",
                "meta": "🔧"
            }.get(b["intent"], "📋")
            
            entry = f"\n> **[{ts}]** {intent_emoji} {b['summary']}"
            if b["data"]:
                data = json.loads(b["data"]) if isinstance(b["data"], str) else b["data"]
                if data.get("ticket_id"):
                    entry += f" (`{data['ticket_id']}`)"
                if data.get("decision_id"):
                    entry += f" **Decision: `{data['decision_id']}`**"
                if data.get("leverage_ratio"):
                    entry += f" ⚡ **Leverage: {data['leverage_ratio']}**"
            
            by_agent[agent].append(entry)
        
        # Render agent sections
        for agent in agents:
            agent_id = agent["agent_id"]
            lines.append(f"\n### @{agent_id}")
            lines.append(f"**Role**: {agent['role']}")
            lines.append(f"**Status**: {agent['status']}")
            lines.append(f"**Last Seen**: {agent['last_seen'][:19] if agent['last_seen'] else 'never'}")
            
            if agent_id in by_agent:
                for entry in by_agent[agent_id][:10]:  # Limit to 10 recent
                    lines.append(entry)
            else:
                lines.append("\n> No recent broadcasts")
        
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────

async def main():
    """Run Hub Master as a service with AnyIO signal handling."""
    master = HubMaster()
    
    # Use AnyIO's signal handling for graceful shutdown
    async with create_task_group() as tg:
        tg.start_soon(master._signal_handler)
        await master.start()


if __name__ == "__main__":
    anyio.run(main)