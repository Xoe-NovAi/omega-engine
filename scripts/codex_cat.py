#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Stack-Cat Protocol Implementation for OMEGA_CODEX.md
Generates the single startup read target for all agents.

D-277: Hydration header lives in scripts/hydration_header.md
D-281: Codex uses condensed reference cards, not full verbatim dumps.
"""
import json
import logging
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Safety net: warn if any single file exceeds this line count
MAX_LINES_PER_FILE = 150
# Safety net: warn if total codex exceeds this line count
MAX_LINES_TOTAL = 400


def compute_source_hash(root: Path) -> str:
    """Compute SHA256 hash of all source files that the CODEX depends on."""
    import hashlib
    h = hashlib.sha256()
    
    # 1. The groups.json file (defines what goes into the CODEX)
    groups_file = root / "scripts" / "groups.json"
    if groups_file.exists():
        h.update(groups_file.read_bytes())
    
    # 2. The hydration header template
    hydration_header = root / "scripts" / "hydration_header.md"
    if hydration_header.exists():
        h.update(hydration_header.read_bytes())
    
    # 3. All source files listed in groups.json
    groups_file = root / "scripts" / "groups.json"
    if groups_file.exists():
        try:
            with open(groups_file) as f:
                groups = json.load(f)
            for group, files in groups.items():
                for rel_path in files:
                    filepath = root / rel_path
                    if filepath.exists():
                        h.update(filepath.read_bytes())
        except (json.JSONDecodeError, OSError):
            pass
    
    return h.hexdigest()[:16]


def load_opencode_todos_for_codex(root: Path) -> list[dict]:
    """
    Load opencode.db todos for CODEX injection.
    Returns top 20 completed/pending todos with session context.
    Graceful degradation: returns [] on any error.
    """
    db_path = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
    
    if not db_path.exists():
        return []
    
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.session_id, t.content, t.status, t.priority, 
                   s.agent, s.title, s.time_updated, s.slug
            FROM todo t
            JOIN session s ON t.session_id = s.id
            WHERE t.status IN ('completed', 'pending')
            ORDER BY s.time_updated DESC
            LIMIT 20
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "session_id": row["session_id"],
                "slug": row["slug"],
                "content": row["content"],
                "status": row["status"],
                "priority": row["priority"],
                "agent": row["agent"],
                "title": row["title"],
                "time_updated": row["time_updated"]
            }
            for row in rows
        ]
    except Exception as e:
        logger.warning(f"opencode.db unavailable for CODEX: {e}")
        return []


def load_lexical_decision_log(root: Path, limit: int = 15) -> list[dict]:
    """
    Load recent decisions from FTS5 session search index for CODEX injection.
    Returns top decision-rich sessions with snippets.
    Graceful degradation: returns [] on any error.
    """
    import sys
    sys.path.insert(0, str(root / "scripts"))
    
    try:
        from session_fts5 import SessionFTS5
    except ImportError:
        return []
    
    try:
        fts = SessionFTS5(root)
        
        # Check if index exists
        if not (root / "data" / "search" / "session_fts5.db").exists():
            return []
        
        # Search for decision-rich sessions using multiple queries
        # FTS5 doesn't support OR directly in simple queries, so we combine results
        decision_terms = ["decided", "ratified", "approved", "rejected", "resolved", "ruled", "decision"]
        all_results = []
        seen_sessions = set()
        
        for term in decision_terms:
            results = fts.search(term, limit=limit)
            for r in results:
                sid = r["session_id"]
                if sid not in seen_sessions:
                    seen_sessions.add(sid)
                    all_results.append(r)
        
        # Sort by rank (best first) and limit
        all_results.sort(key=lambda x: x["rank"])
        all_results = all_results[:limit]
        
        # Filter and format for CODEX
        decision_log = []
        for r in all_results:
            if r.get("decisions") or r.get("continuation"):
                decision_log.append({
                    "session_id": r["session_id"][:12],
                    "entity": r["entity"],
                    "timestamp": r["timestamp"][:19] if r["timestamp"] else "",
                    "task": r["task_current"][:100] if r["task_current"] else "",
                    "decisions": r["decisions"][:200] if r["decisions"] else "",
                    "continuation": r["continuation"][:150] if r["continuation"] else "",
                    "source": r["source"],
                    "gnosis_section": r["gnosis_section"]
                })
        
        return decision_log
        
    except Exception as e:
        logger.warning(f"FTS5 decision log unavailable for CODEX: {e}")
        return []


def build_lexical_decision_log_section(decisions: list[dict]) -> str:
    """Build the Lexical Decision Log markdown section for CODEX."""
    if not decisions:
        return ""
    
    lines = []
    lines.append("## 🔍 LEXICAL DECISION LOG (FTS5 Mined)\n")
    lines.append(f"> Top {len(decisions)} decision-rich sessions from session corpus (HALL_OF_RECORDS + session_gnosis).\n")
    
    for d in decisions:
        lines.append(f"### `{d['session_id']}` @{d['entity']} — {d['timestamp']}")
        if d['task']:
            lines.append(f"**Task**: {d['task']}")
        if d['decisions']:
            lines.append(f"**Decisions**: {d['decisions']}")
        if d['continuation']:
            lines.append(f"**Continuation**: {d['continuation']}")
        if d['gnosis_section']:
            lines.append(f"**Source**: session_gnosis ({d['gnosis_section']})")
        else:
            lines.append(f"**Source**: HALL_OF_RECORDS")
        lines.append("")
    
    return "\n".join(lines) + "\n"


def build_fleet_todos_section(todos: list[dict]) -> str:
    """Build the Fleet Todos markdown section for CODEX."""
    if not todos:
        return ""
    
    completed = [t for t in todos if t["status"] == "completed"]
    pending = [t for t in todos if t["status"] == "pending"]
    
    lines = []
    lines.append("## 📋 Fleet Todos (opencode.db) — SOTR/SOTE Snapshot\n")
    lines.append(f"**Generated**: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"**Total shown**: {len(todos)} (✅ {len(completed)} completed · 📋 {len(pending)} pending)\n")
    
    if completed:
        lines.append("### ✅ Recently Completed")
        for t in completed[:10]:
            lines.append(f"- `{t['slug']}` @{t['agent']}: {t['content'][:80]}")
        if len(completed) > 10:
            lines.append(f"- _...and {len(completed) - 10} more completed_")
        lines.append("")
    
    if pending:
        lines.append("### 📋 Currently Pending")
        for t in pending[:10]:
            lines.append(f"- `{t['slug']}` @{t['agent']}: {t['content'][:80]}")
        if len(pending) > 10:
            lines.append(f"- _...and {len(pending) - 10} more pending_")
        lines.append("")
    
    lines.append("> *Source: opencode.db todo table (read-only). Full hierarchy in harvester radar.*\n")
    lines.append("---\n\n")
    
    return "\n".join(lines)


class CodexGenerationError(Exception):
    """Base exception for codex generation."""
    pass

class GroupsFileError(CodexGenerationError):
    """Groups file not found or invalid."""
    pass

class FileReadError(CodexGenerationError):
    """Failed to read a source file."""
    pass

class OutputWriteError(CodexGenerationError):
    """Failed to write output file."""
    pass


def generate_codex(root: Path = None, out_file: Path = None) -> None:
    """
    Generate OMEGA_CODEX.md from groups.json.
    
    Args:
        root: Project root directory (defaults to script's parent parent)
        out_file: Output file path (defaults to root/OMEGA_CODEX.md)
        
    Raises:
        GroupsFileError: If groups.json not found or invalid
        FileReadError: If a source file cannot be read
        OutputWriteError: If output file cannot be written
    """
    if root is None:
        root = Path(__file__).parent.parent
    if out_file is None:
        out_file = root / "OMEGA_CODEX.md"
    
    groups_file = root / "scripts" / "groups.json"
    
    try:
        with open(groups_file) as f:
            groups = json.load(f)
    except FileNotFoundError:
        logger.error(f"Groups file not found: {groups_file}")
        raise GroupsFileError(f"Groups file not found: {groups_file}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in groups file: {e}")
        raise GroupsFileError(f"Invalid JSON in groups file: {e}")
        
    ts = datetime.now(timezone.utc).isoformat()
    content_hash = compute_source_hash(root)
    codex_content = [f"# ⬡ OMEGA ⬡ CODEX ⬡ {ts} ⬡ {content_hash} ⬡\n\n"]
    codex_content.append("> **Generated via Stack-Cat Protocol**. This is the single startup read target for all agents. It contains the concatenated active state of the engine, mandates, workflow, and refinement protocols.\n\n")
    
    # D-277 / D-281 Phase IV: hydration sequence lives in scripts/hydration_header.md
    header_path = Path(__file__).resolve().parent / "hydration_header.md"
    try:
        header = header_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        logger.error(f"Hydration header not found: {header_path}")
        raise FileReadError(f"Hydration header not found: {header_path}") from e
    codex_content.append(header.replace("{{TIMESTAMP}}", ts))
    if not codex_content[-1].endswith("\n"):
        codex_content.append("\n")
    
    # ── FLEET TODOS (opencode.db) — SOTR/SOTE SNAPSHOT ──────────────────────
    opencode_todos = load_opencode_todos_for_codex(root)
    fleet_todos_section = build_fleet_todos_section(opencode_todos)
    if fleet_todos_section:
        codex_content.append(fleet_todos_section)
    
    # ── LEXICAL DECISION LOG (FTS5) — RECENT DECISIONS ──────────────────────
    lexical_decisions = load_lexical_decision_log(root, limit=15)
    lexical_section = build_lexical_decision_log_section(lexical_decisions)
    if lexical_section:
        codex_content.append(lexical_section)
    
    total_lines = 0
    warnings = []
    
    for group, files in groups.items():
        codex_content.append(f"## 📁 GROUP: {group.upper()}\n\n")
        for rel_path in files:
            filepath = root / rel_path
            if filepath.exists():
                try:
                    content = filepath.read_text(encoding="utf-8")
                except Exception as e:
                    logger.error(f"Failed to read {filepath}: {e}")
                    raise FileReadError(f"Failed to read {filepath}: {e}") from e
                    
                size = len(content.encode('utf-8'))
                lines = len(content.splitlines())
                
                # Safety net: warn if file exceeds max lines
                if lines > MAX_LINES_PER_FILE:
                    warnings.append(f"⚠️ {rel_path}: {lines} lines (max {MAX_LINES_PER_FILE}) — consider condensing")
                
                file_header = f"### {rel_path}\n**Type**: markdown\n**Size**: {size} bytes\n**Lines**: {lines}\n\n"
                codex_content.append(file_header + content + "\n\n---\n\n")
                total_lines += lines
            else:
                logger.warning(f"File not found: {filepath}")
                codex_content.append(f"### {rel_path}\n**Status**: NOT FOUND\n\n---\n\n")
    
    # Safety net: warn if total exceeds max lines
    if total_lines > MAX_LINES_TOTAL:
        warnings.append(f"⚠️ Total codex: {total_lines} lines (max {MAX_LINES_TOTAL}) — bloat detected")
    
    try:
        output = "".join(codex_content)
        out_file.write_text(output, encoding="utf-8")
        final_lines = len(output.splitlines())
        logger.info(f"Generated {out_file} successfully.")
        logger.info(f"  Lines: {final_lines} | Size: {len(output)} bytes")
        for w in warnings:
            logger.warning(w)
        if not warnings:
            logger.info(f"  ✅ All size checks passed")
    except Exception as e:
        logger.error(f"Failed to write output file {out_file}: {e}")
        raise OutputWriteError(f"Failed to write output file: {e}") from e


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_codex()