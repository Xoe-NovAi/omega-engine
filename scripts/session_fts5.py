#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""
FTS5 Lexical Search for Omega Engine Session Corpus.

Builds and queries a SQLite FTS5 virtual table over:
- HALL_OF_RECORDS session JSON files (task_current, focus_chain, decisions, continuation, entity)
- session_gnosis.md files (decisions, continuations from sections)

Pure concatenation, zero inference, M7-compliant.
"""

import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SessionFTS5:
    """FTS5 index for session corpus lexical search."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.db_path = repo_root / "data" / "search" / "session_fts5.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _sanitize_fts5_query(self, query: str) -> str:
        """
        Sanitize query for FTS5 MATCH clause.
        Escape special characters: " * + - ( ) : < > @
        FTS5 treats hyphen as NOT operator unless escaped or in quotes.
        """
        # First, wrap the entire query in quotes if it contains spaces or special chars
        # This is the safest approach for FTS5
        special_chars = r'["*+\-():<>@]'
        has_special = bool(re.search(special_chars, query)) or ' ' in query

        if has_special:
            # Escape any existing quotes
            query = query.replace('"', '\\"')
            # Wrap in quotes
            sanitized = f'"{query}"'
        else:
            sanitized = query

        return sanitized

    def build_index(self, force_rebuild: bool = False) -> dict:
        """
        Build FTS5 index from HALL_OF_RECORDS and session_gnosis.
        Returns stats dict.
        """
        conn = self._connect()
        cursor = conn.cursor()

        try:
            # Create FTS5 virtual table
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS session_fts USING fts5(
                    session_id UNINDEXED,
                    entity UNINDEXED,
                    agent_id UNINDEXED,
                    channel UNINDEXED,
                    model UNINDEXED,
                    timestamp UNINDEXED,
                    intent UNINDEXED,
                    task_current,
                    focus_chain,
                    decisions,
                    continuation,
                    source UNINDEXED,  -- 'hall_of_records' or 'session_gnosis'
                    gnosis_section UNINDEXED
                )
            """)

            # Check if already built (unless force_rebuild)
            if not force_rebuild:
                cursor.execute("SELECT COUNT(*) FROM session_fts")
                count = cursor.fetchone()[0]
                if count > 0:
                    return {"status": "exists", "rows": count, "rebuilt": False}

            # Clear existing
            cursor.execute("DELETE FROM session_fts")

            stats = {"hall_of_records": 0, "session_gnosis": 0, "errors": 0}

            # 1. Index HALL_OF_RECORDS session JSON files
            hall_dir = self.repo_root / "data" / "knowledge" / "HALL_OF_RECORDS"
            if hall_dir.exists():
                for entity_dir in hall_dir.iterdir():
                    if not entity_dir.is_dir():
                        continue
                    entity = entity_dir.name
                    for session_file in entity_dir.glob("ses_*.json"):
                        try:
                            data = json.loads(session_file.read_text(encoding="utf-8"))

                            # Extract fields
                            session_id = data.get("session_id", "")
                            agent_id = data.get("agent_id", "")
                            channel = data.get("channel", "")
                            model = data.get("model", "")
                            task_current = data.get("task_current", "")
                            focus_chain = " ".join(data.get("focus_chain", []))
                            decisions = " ".join(data.get("decisions", []))
                            continuation = data.get("continuation", "")
                            timestamp = data.get("timestamp", "")
                            intent = data.get("intent", "")

                            # Insert into FTS5
                            cursor.execute("""
                                INSERT INTO session_fts (
                                    session_id, entity, agent_id, channel, model,
                                    timestamp, intent, task_current, focus_chain,
                                    decisions, continuation, source
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                session_id, entity, agent_id, channel, model,
                                timestamp, intent, task_current, focus_chain,
                                decisions, continuation, "hall_of_records"
                            ))
                            stats["hall_of_records"] += 1

                        except Exception as e:
                            stats["errors"] += 1
                            print(f"[fts5] Error indexing {session_file}: {e}", file=sys.stderr)

            # 2. Index session_gnosis.md files
            entities_dir = self.repo_root / "data" / "entities"
            if entities_dir.exists():
                for entity_dir in entities_dir.iterdir():
                    if not entity_dir.is_dir():
                        continue
                    entity = entity_dir.name
                    gnosis_file = entity_dir / "session_gnosis.md"
                    if not gnosis_file.exists():
                        continue

                    try:
                        content = gnosis_file.read_text(encoding="utf-8")

                        # Parse sections (§N — TITLE)
                        # Pattern: ## §N — TITLE or ### §N — TITLE
                        section_pattern = r'(^#{2,3}\s+§\d+\s*—\s*.+?)(?=^#{2,3}\s+§\d+|$)'
                        sections = re.findall(section_pattern, content, re.MULTILINE | re.DOTALL)

                        for i, section in enumerate(sections):
                            # Extract section header
                            header_match = re.match(r'^#{2,3}\s+(§\d+)\s*—\s*(.+)$', section.split('\n')[0])
                            if header_match:
                                section_id = header_match.group(1)
                                section_title = header_match.group(2)
                            else:
                                section_id = f"§{i}"
                                section_title = "Unknown"

                            # Extract decisions and continuations from section
                            # Look for bullet points with "DECISION:" or "CONTINUATION:" or similar
                            decisions = []
                            continuations = []

                            lines = section.split('\n')
                            for line in lines:
                                line_stripped = line.strip()
                                # Match decision patterns
                                if any(kw in line_stripped.upper() for kw in ['DECISION:', 'RULING:', 'RESOLVED:', 'DECIDED:']):
                                    decisions.append(line_stripped)
                                # Match continuation patterns
                                if any(kw in line_stripped.upper() for kw in ['CONTINUATION:', 'NEXT:', 'TODO:', 'FOLLOW-UP:']):
                                    continuations.append(line_stripped)

                            # Also extract any text content as searchable
                            section_text = section[:5000]  # Limit size

                            # Create a synthetic session_id for gnosis sections
                            gnosis_session_id = f"gnosis_{entity}_{section_id.replace('§', '').replace(' ', '_')}"

                            cursor.execute("""
                                INSERT INTO session_fts (
                                    session_id, entity, agent_id, channel, model,
                                    timestamp, intent, task_current, focus_chain,
                                    decisions, continuation, source, gnosis_section
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                gnosis_session_id, entity, "", "", "",
                                datetime.now(timezone.utc).isoformat(), "gnosis",
                                section_title, "",  # task_current, focus_chain
                                " ".join(decisions), " ".join(continuations),
                                "session_gnosis", section_id
                            ))
                            stats["session_gnosis"] += 1

                    except Exception as e:
                        stats["errors"] += 1
                        print(f"[fts5] Error indexing {gnosis_file}: {e}", file=sys.stderr)

            conn.commit()

            # Get final count
            cursor.execute("SELECT COUNT(*) FROM session_fts")
            total = cursor.fetchone()[0]

            return {
                "status": "built",
                "total_rows": total,
                "hall_of_records": stats["hall_of_records"],
                "session_gnosis": stats["session_gnosis"],
                "errors": stats["errors"],
                "rebuilt": True
            }

        finally:
            conn.close()

    def search(self, query: str, limit: int = 10, entity: str = None) -> list[dict]:
        """
        Search FTS5 index with sanitized query.
        Returns list of matching sessions with snippets.
        """
        conn = self._connect()
        cursor = conn.cursor()

        try:
            # Sanitize query for FTS5
            sanitized = self._sanitize_fts5_query(query)

            # Build query
            sql = """
                SELECT
                    session_id, entity, agent_id, channel, model,
                    timestamp, intent, task_current, focus_chain,
                    decisions, continuation, source, gnosis_section,
                    snippet(session_fts, 6, '<mark>', '</mark>', '...', 32) as snippet_task,
                    snippet(session_fts, 7, '<mark>', '</mark>', '...', 32) as snippet_focus,
                    snippet(session_fts, 8, '<mark>', '</mark>', '...', 32) as snippet_decisions,
                    snippet(session_fts, 9, '<mark>', '</mark>', '...', 32) as snippet_continuation,
                    bm25(session_fts) as rank
                FROM session_fts
                WHERE session_fts MATCH ?
            """
            params = [sanitized]

            if entity:
                sql += " AND entity = ?"
                params.append(entity)

            sql += " ORDER BY rank LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                # Build best snippet from available fields
                snippets = []
                for field in ['snippet_task', 'snippet_focus', 'snippet_decisions', 'snippet_continuation']:
                    if row[field] and row[field] != '...':
                        snippets.append(row[field])

                results.append({
                    "session_id": row["session_id"],
                    "entity": row["entity"],
                    "agent_id": row["agent_id"],
                    "channel": row["channel"],
                    "model": row["model"],
                    "timestamp": row["timestamp"],
                    "intent": row["intent"],
                    "task_current": row["task_current"][:200] if row["task_current"] else "",
                    "focus_chain": row["focus_chain"][:200] if row["focus_chain"] else "",
                    "decisions": row["decisions"][:200] if row["decisions"] else "",
                    "continuation": row["continuation"][:200] if row["continuation"] else "",
                    "source": row["source"],
                    "gnosis_section": row["gnosis_section"],
                    "snippet": " | ".join(snippets[:2]) if snippets else "",
                    "rank": row["rank"]
                })

            return results

        finally:
            conn.close()

    def get_stats(self) -> dict:
        """Get index statistics."""
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM session_fts")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT source, COUNT(*) FROM session_fts GROUP BY source")
            by_source = dict(cursor.fetchall())

            cursor.execute("SELECT entity, COUNT(*) FROM session_fts GROUP BY entity ORDER BY COUNT(*) DESC LIMIT 10")
            by_entity = dict(cursor.fetchall())

            return {
                "total_rows": total,
                "by_source": by_source,
                "top_entities": by_entity,
                "db_path": str(self.db_path),
                "db_size_mb": round(self.db_path.stat().st_size / (1024 * 1024), 2) if self.db_path.exists() else 0
            }
        finally:
            conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Session FTS5 Lexical Search")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--build", action="store_true", help="Build/rebuild index")
    parser.add_argument("--force", action="store_true", help="Force rebuild")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Result limit")
    parser.add_argument("--entity", type=str, help="Filter by entity")
    parser.add_argument("--stats", action="store_true", help="Show index stats")

    args = parser.parse_args()

    fts = SessionFTS5(args.repo_root)

    if args.build or args.force:
        result = fts.build_index(force_rebuild=args.force)
        print(json.dumps(result, indent=2))
        return

    if args.search:
        results = fts.search(args.search, limit=args.limit, entity=args.entity)
        print(json.dumps(results, indent=2))
        return

    if args.stats:
        stats = fts.get_stats()
        print(json.dumps(stats, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()