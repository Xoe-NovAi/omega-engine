#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
# SPDX-License-Identifier: Apache-2.0

"""
Hivemind Harvester — Zero-Inference Fleet Aggregator.
Runs every 300s to produce latest.json and latest.md.
"""

import sys
import os
import fcntl
import json
import re
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Invariant: Must not import asyncio
# Invariant: Must run locally in repo context


def _default_repo_root() -> Path:
    # Resolve relative to scripts/
    return Path(__file__).resolve().parent.parent


def load_control_plane(repo_root: Path | None = None):
    """Load the control plane read-only, or return None.

    DEFENSIVE BY DESIGN. The harvester must keep producing a fleet overview even
    if the control plane is missing or broken — a dead radar is worse than a
    radar that admits it is blind. When this returns None the caller publishes
    `control_plane_ok: false` rather than fabricating zero kills.

    M23: a degraded-but-honest projection beats a synthesized one.
    """
    try:
        root = repo_root if repo_root is not None else _default_repo_root()
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from mcp_servers.omega_hub import control_plane as cp
        return cp
    except Exception as e:  # noqa: BLE001
        print(f"[harvest] control plane unavailable: {e}", file=sys.stderr)
        return None


def classify_session_tier(parent_id: str | None, subagent_type: str | None, title: str = "", agent: str = "") -> str:
    """
    Classify session per 3-Tier Ontology (Human-Steerability Permission Boundary).
    
    EIS: parent_id IS NULL → Human created, human steerable
    EAS: parent_id NOT NULL AND subagent_type = 'EAS' → Agent created, persistent, autonomous
    SPT: parent_id NOT NULL AND subagent_type = 'SPT' → Agent created, ephemeral, disposable
    
    For legacy sessions without subagent_type, infer from context.
    """
    if parent_id is None:
        return "EIS"
    elif subagent_type == "EAS":
        return "EAS"
    elif subagent_type == "SPT":
        return "SPT"
    else:
        # Legacy sessions without subagent_type - infer from title/agent
        title_lower = title.lower()
        agent_lower = agent.lower()
        autonomous_agents = {"maat", "lilith", "roc_racoon", "jem", "explore", "researcher", 
                            "doom_guy", "john_carmack", "grokster", "verity", "kali", "makali"}
        if "subagent" in title_lower or agent_lower in autonomous_agents:
            return "EAS"  # Agent-spawned persistent
        return "SPT"  # Default to ephemeral for unknown


def load_opencode_todos(repo_root: Path) -> list[dict]:
    """
    Read opencode.db todo table read-only.
    Returns list of enriched todo items with session tier, slug, parent linkage.
    Filters for completed/pending (DONE/PLANNED). Graceful degradation: returns [] on any error.
    """
    import sqlite3
    db_path = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
    
    if not db_path.exists():
        return []
    
    try:
        # Read-only connection
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query todos with completed/pending status, joined with session for context
        # Include slug, parent_id for tier classification and hierarchy
        cursor.execute("""
            SELECT t.session_id, t.content, t.status, t.priority, 
                   s.agent, s.title, s.time_updated, s.slug, s.parent_id
            FROM todo t
            JOIN session s ON t.session_id = s.id
            WHERE t.status IN ('completed', 'pending')
            ORDER BY s.time_updated DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Build session lookup for hierarchy
        session_lookup = {}
        for row in rows:
            session_lookup[row["session_id"]] = {
                "slug": row["slug"],
                "parent_id": row["parent_id"],
                "agent": row["agent"],
                "title": row["title"]
            }
        
        # Enrich each todo with tier classification and parent slug
        enriched = []
        for row in rows:
            parent_id = row["parent_id"]
            # Try to get subagent_type from session metadata if available
            # For now, infer from parent relationship
            subagent_type = None
            if parent_id is not None:
                # Check if parent is an EIS (parent_id IS NULL)
                parent_session = session_lookup.get(parent_id)
                if parent_session and parent_session["parent_id"] is None:
                    subagent_type = "EAS"  # Direct child of EIS = persistent specialist
                else:
                    subagent_type = "SPT"  # Nested deeper = ephemeral probe
            
            tier = classify_session_tier(parent_id, subagent_type, row["title"], row["agent"])
            parent_slug = None
            if parent_id and parent_id in session_lookup:
                parent_slug = session_lookup[parent_id]["slug"]
            
            enriched.append({
                "session_id": row["session_id"],
                "slug": row["slug"],
                "session_tier": tier,
                "parent_session_id": parent_id,
                "parent_slug": parent_slug,
                "subagent_type": subagent_type,
                "content": row["content"],
                "status": row["status"],
                "priority": row["priority"],
                "agent": row["agent"],
                "title": row["title"],
                "time_updated": row["time_updated"]
            })
        
        return enriched
    except Exception as e:
        print(f"[harvest] opencode.db unavailable: {e}", file=sys.stderr)
        return []


def load_handoff_inbox(repo_root: Path) -> list[dict]:
    """
    Load pending/active handoffs from the Hivemind handoff store.
    Returns list of handoff packets addressed to this entity.
    Graceful degradation: returns [] on any error.
    """
    import json
    from pathlib import Path
    
    # Handoff store is in data/handoff/{pending,active,completed,stale,archive}/
    handoff_base = repo_root / "data" / "handoff"
    if not handoff_base.exists():
        return []
    
    try:
        # Read all handoff JSON files from all queues
        handoffs = []
        queue_dirs = {
            "pending": "📥 PENDING",
            "active": "⚡ ACTIVE",
            "completed": "✅ COMPLETED",
            "stale": "⚠️ STALE",
            "archive": "📦 ARCHIVED",
        }
        
        for queue_name, display_status in queue_dirs.items():
            queue_dir = repo_root / "data" / "handoff" / queue_name
            if not queue_dir.exists():
                continue
            
            for handoff_file in queue_dir.glob("ho_*.json"):
                try:
                    data = json.loads(handoff_file.read_text(encoding="utf-8"))
                    # Filter for handoffs addressed to this entity (makali_n0)
                    target_entity = data.get("target_entity", "")
                    target_channel = data.get("target_channel", "")
                    if target_entity == "makali_n0" and target_channel == "opencode":
                        # Enrich with computed fields
                        status = data.get("status", queue_name)
                        priority = data.get("priority", 0)
                        task = data.get("task", "")
                        source_entity = data.get("source_entity", "unknown")
                        source_channel = data.get("source_channel", "unknown")
                        submitted_at = data.get("submitted_at", "")
                        
                        # Determine display status
                        if status == "pending":
                            display_status = "📥 PENDING"
                        elif status == "active":
                            display_status = "⚡ ACTIVE"
                        elif status == "completed":
                            display_status = "✅ COMPLETED"
                        elif status == "rejected":
                            display_status = "❌ REJECTED"
                        elif status == "stale":
                            display_status = "⚠️ STALE"
                        elif status == "archived":
                            display_status = "📦 ARCHIVED"
                        else:
                            display_status = f"❓ {status.upper()}"
                        
                        enriched = {
                            "packet_id": data.get("packet_id", ""),
                            "source_entity": data.get("source_entity", "unknown"),
                            "source_channel": data.get("source_channel", "unknown"),
                            "task": data.get("task", ""),
                            "status": status,
                            "display_status": display_status,
                            "priority": data.get("priority", 0),
                            "submitted_at": data.get("submitted_at", ""),
                            "context": data.get("context", ""),
                            "context_delivery": data.get("context_delivery", "inline"),
                            "decisions": data.get("decisions", []),
                            "outcome": data.get("outcome"),
                            "state_history": data.get("state_history", []),
                            "queue": queue_name,
                        }
                        handoffs.append(enriched)
                except Exception as e:
                    print(f"[harvest] Failed to parse handoff {handoff_file}: {e}", file=sys.stderr)
                    continue
        
        # Sort by priority (high first), then by submitted_at (newest first)
        handoffs.sort(key=lambda h: (-h.get("priority", 0), h.get("submitted_at", "")), reverse=True)
        return handoffs
        
    except Exception as e:
        print(f"[harvest] handoff inbox unavailable: {e}", file=sys.stderr)
        return []


def build_session_hierarchy(todos: list[dict], repo_root: Path) -> dict:
    """
    Build EIS → EAS/SPT hierarchy from enriched todos.
    Returns dict with EIS sessions as keys, each containing EAS_children and SPT_children.
    """
    import sqlite3
    db_path = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
    
    # Group todos by session
    session_todos = {}
    for todo in todos:
        sid = todo["session_id"]
        if sid not in session_todos:
            session_todos[sid] = {
                "session_id": sid,
                "slug": todo["slug"],
                "session_tier": todo["session_tier"],
                "agent": todo["agent"],
                "title": todo["title"],
                "parent_session_id": todo["parent_session_id"],
                "parent_slug": todo["parent_slug"],
                "subagent_type": todo["subagent_type"],
                "todos": []
            }
        session_todos[sid]["todos"].append(todo)
    
    # Fetch parent sessions that may not have todos but are needed for hierarchy
    # Get all parent_session_ids from todos
    parent_ids = set()
    for todo in todos:
        if todo["parent_session_id"]:
            parent_ids.add(todo["parent_session_id"])
    
    # Also get grandparents (parents of parents)
    all_parent_ids = set(parent_ids)
    if db_path.exists() and parent_ids:
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            placeholders = ",".join("?" * len(parent_ids))
            cursor.execute(f"""
                SELECT id, slug, parent_id, agent, title
                FROM session
                WHERE id IN ({placeholders})
            """, list(parent_ids))
            for row in cursor.fetchall():
                if row["parent_id"]:
                    all_parent_ids.add(row["parent_id"])
            conn.close()
        except Exception:
            pass
    
    # Fetch all parent/grandparent sessions from DB
    parent_sessions = {}
    if db_path.exists() and all_parent_ids:
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            placeholders = ",".join("?" * len(all_parent_ids))
            cursor.execute(f"""
                SELECT id, slug, parent_id, agent, title
                FROM session
                WHERE id IN ({placeholders})
            """, list(all_parent_ids))
            for row in cursor.fetchall():
                parent_sessions[row["id"]] = {
                    "session_id": row["id"],
                    "slug": row["slug"],
                    "parent_session_id": row["parent_id"],
                    "agent": row["agent"],
                    "title": row["title"],
                    "subagent_type": None,  # Will be inferred
                    "todos": []  # No todos for these parent sessions
                }
            conn.close()
        except Exception:
            pass
    
    # Merge parent sessions into session_todos
    for sid, sess in parent_sessions.items():
        if sid not in session_todos:
            # Classify tier for parent session
            parent_id = sess["parent_session_id"]
            subagent_type = None
            if parent_id is not None:
                # Check if parent is an EIS
                parent_sess = parent_sessions.get(parent_id) or session_todos.get(parent_id)
                if parent_sess and parent_sess.get("parent_session_id") is None:
                    subagent_type = "EAS"
                else:
                    subagent_type = "SPT"
            tier = classify_session_tier(parent_id, subagent_type, sess["title"], sess["agent"])
            session_todos[sid] = {
                "session_id": sid,
                "slug": sess["slug"],
                "session_tier": tier,
                "agent": sess["agent"],
                "title": sess["title"],
                "parent_session_id": parent_id,
                "parent_slug": parent_sessions.get(parent_id, {}).get("slug") if parent_id else None,
                "subagent_type": subagent_type,
                "todos": []
            }
    
    # Build hierarchy
    eis_sessions = {}
    eas_sessions = {}
    spt_sessions = {}
    
    for sid, sess in session_todos.items():
        tier = sess["session_tier"]
        if tier == "EIS":
            eis_sessions[sid] = sess
        elif tier == "EAS":
            eas_sessions[sid] = sess
        elif tier == "SPT":
            spt_sessions[sid] = sess
    
    # Attach EAS/SPT children to their parent EIS
    for eis_sid, eis in eis_sessions.items():
        eis["EAS_children"] = []
        eis["SPT_children"] = []
        eis["todo_summary"] = {"completed": 0, "pending": 0, "in_progress": 0}
        
        for todo in eis["todos"]:
            eis["todo_summary"][todo["status"]] = eis["todo_summary"].get(todo["status"], 0) + 1
    
    # Attach EAS children to EIS
    for eas_sid, eas in eas_sessions.items():
        parent_id = eas["parent_session_id"]
        if parent_id and parent_id in eis_sessions:
            eas["todo_summary"] = {"completed": 0, "pending": 0, "in_progress": 0}
            for todo in eas["todos"]:
                eas["todo_summary"][todo["status"]] = eas["todo_summary"].get(todo["status"], 0) + 1
            eis_sessions[parent_id]["EAS_children"].append(eas)
        else:
            # Orphan EAS - no parent EIS found
            pass
    
    # Attach SPT children to EIS (or EAS if direct parent)
    for spt_sid, spt in spt_sessions.items():
        parent_id = spt["parent_session_id"]
        if parent_id and parent_id in eis_sessions:
            spt["todo_summary"] = {"completed": 0, "pending": 0, "in_progress": 0}
            for todo in spt["todos"]:
                spt["todo_summary"][todo["status"]] = spt["todo_summary"].get(todo["status"], 0) + 1
            eis_sessions[parent_id]["SPT_children"].append(spt)
        elif parent_id and parent_id in eas_sessions:
            # SPT child of EAS - attach to EAS's parent EIS
            grandparent_id = eas_sessions[parent_id]["parent_session_id"]
            if grandparent_id and grandparent_id in eis_sessions:
                spt["todo_summary"] = {"completed": 0, "pending": 0, "in_progress": 0}
                for todo in spt["todos"]:
                    spt["todo_summary"][todo["status"]] = spt["todo_summary"].get(todo["status"], 0) + 1
                eis_sessions[grandparent_id]["SPT_children"].append(spt)
        elif parent_id and parent_id in parent_sessions:
            # SPT child of parent session (from DB) - find grandparent EIS
            grandparent_id = parent_sessions[parent_id].get("parent_session_id")
            if grandparent_id and grandparent_id in eis_sessions:
                spt["todo_summary"] = {"completed": 0, "pending": 0, "in_progress": 0}
                for todo in spt["todos"]:
                    spt["todo_summary"][todo["status"]] = spt["todo_summary"].get(todo["status"], 0) + 1
                eis_sessions[grandparent_id]["SPT_children"].append(spt)
    
    # Build output structure
    hierarchy = {"EIS": {}}
    for eis_sid, eis in eis_sessions.items():
        eis_key = f"{eis['slug']} ({eis['agent']})"
        hierarchy["EIS"][eis_key] = {
            "session_id": eis["session_id"],
            "slug": eis["slug"],
            "agent": eis["agent"],
            "title": eis["title"],
            "todo_summary": eis["todo_summary"],
            "EAS_children": [
                {
                    "session_id": c["session_id"],
                    "slug": c["slug"],
                    "agent": c["agent"],
                    "title": c["title"],
                    "subagent_type": c["subagent_type"],
                    "todo_summary": c["todo_summary"]
                }
                for c in eis["EAS_children"]
            ],
            "SPT_children": [
                {
                    "session_id": c["session_id"],
                    "slug": c["slug"],
                    "agent": c["agent"],
                    "title": c["title"],
                    "subagent_type": c["subagent_type"],
                    "todo_summary": c["todo_summary"]
                }
                for c in eis["SPT_children"]
            ]
        }
    
    return hierarchy


def mine_session_timelines(repo_root: Path) -> dict:
    """
    Mine session timelines from opencode.db part/message tables.
    Uses compaction parts as epoch boundaries to build per-session activity timelines.
    Pure concatenation, zero inference, M7-compliant.
    Memory-efficient: processes top 20 most recent sessions with compactions, one at a time.
    """
    import sqlite3
    from datetime import datetime, timezone
    
    db_path = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
    
    if not db_path.exists():
        return {}
    
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get top 20 most recent sessions with compactions (by latest compaction time)
        cursor.execute("""
            SELECT p.session_id, MAX(p.time_created) as latest_compaction
            FROM part p
            WHERE json_extract(p.data, '$.type') = 'compaction'
            GROUP BY p.session_id
            ORDER BY latest_compaction DESC
            LIMIT 20
        """)
        recent_sessions = cursor.fetchall()
        
        if not recent_sessions:
            return {}
        
        session_ids = [row["session_id"] for row in recent_sessions]
        placeholders = ",".join("?" * len(session_ids))
        
        # Get session info for these sessions
        cursor.execute(f"""
            SELECT id, slug, agent, title, time_created, time_updated, parent_id
            FROM session
            WHERE id IN ({",".join("?" * len(session_ids))})
        """, session_ids)
        sessions = {row["id"]: row for row in cursor.fetchall()}
        
        timelines = {}
        
        # Process each session individually to limit memory
        for sid in session_ids:
            try:
                # Get compaction parts for this session (epoch boundaries)
                cursor.execute("""
                    SELECT time_created, data
                    FROM part
                    WHERE session_id = ? AND json_extract(data, '$.type') = 'compaction'
                    ORDER BY time_created
                """, (sid,))
                compactions = cursor.fetchall()
                
                if not compactions:
                    continue
                
                # Get parts for this session (limit to 5000 per session to bound memory)
                cursor.execute("""
                    SELECT time_created, data
                    FROM part
                    WHERE session_id = ?
                    ORDER BY time_created
                    LIMIT 5000
                """, (sid,))
                parts = cursor.fetchall()
                
                # Get recent messages (last 5)
                cursor.execute("""
                    SELECT time_created, data
                    FROM message
                    WHERE session_id = ?
                    ORDER BY time_created DESC
                    LIMIT 5
                """, (sid,))
                messages = cursor.fetchall()
                
                # Build epochs from compaction boundaries
                compactions_list = []
                for cp in compactions:
                    compactions_list.append({
                        "time_created": cp["time_created"],
                        "data": json.loads(cp["data"])
                    })
                
                parts_list = []
                for p in parts:
                    parts_list.append({
                        "time_created": p["time_created"],
                        "type": json.loads(p["data"]).get("type", "unknown"),
                        "data": json.loads(p["data"])
                    })
                
                messages_list = []
                for m in messages:
                    msg_data = json.loads(m["data"])
                    messages_list.append({
                        "time_created": m["time_created"],
                        "role": msg_data.get("role", "unknown"),
                        "content_preview": str(msg_data)[:200]
                    })
                
                # Build epochs from compaction boundaries
                epochs = []
                epoch_start = 0
                
                for i, compaction in enumerate(compactions_list):
                    compaction_time = compaction["time_created"]
                    compaction_data = compaction["data"]
                    
                    # Get parts in this epoch
                    epoch_parts = [p for p in parts_list if epoch_start <= p["time_created"] < compaction_time]
                    
                    # Count part types in this epoch
                    type_counts = {}
                    for p in epoch_parts:
                        t = p["type"]
                        type_counts[t] = type_counts.get(t, 0) + 1
                    
                    # Get key activities (step-finish reasons, tool names)
                    key_activities = []
                    for p in epoch_parts:
                        if p["type"] == "step-finish":
                            reason = p["data"].get("reason", "")
                            if reason:
                                key_activities.append(f"step:{reason}")
                        elif p["type"] == "tool":
                            tool_name = p["data"].get("tool", "")
                            if tool_name:
                                key_activities.append(f"tool:{tool_name}")
                    
                    # Deduplicate and limit
                    key_activities = list(dict.fromkeys(key_activities))[:5]
                    
                    epochs.append({
                        "epoch": i + 1,
                        "compaction_time": compaction_time,
                        "compaction_iso": datetime.fromtimestamp(compaction_time / 1000, tz=timezone.utc).isoformat(),
                        "auto": compaction_data.get("auto", False),
                        "overflow": compaction_data.get("overflow", False),
                        "tail_start_id": compaction_data.get("tail_start_id", ""),
                        "part_counts": type_counts,
                        "total_parts": sum(type_counts.values()),
                        "key_activities": key_activities
                    })
                    
                    epoch_start = compaction_time
                
                # Handle parts after last compaction (current epoch)
                if parts_list:
                    current_parts = [p for p in parts_list if p["time_created"] >= epoch_start]
                    if current_parts:
                        type_counts = {}
                        for p in current_parts:
                            t = p["type"]
                            type_counts[t] = type_counts.get(t, 0) + 1
                        
                        key_activities = []
                        for p in current_parts:
                            if p["type"] == "step-finish":
                                reason = p["data"].get("reason", "")
                                if reason:
                                    key_activities.append(f"step:{reason}")
                            elif p["type"] == "tool":
                                tool_name = p["data"].get("tool", "")
                                if tool_name:
                                    key_activities.append(f"tool:{tool_name}")
                        
                        key_activities = list(dict.fromkeys(key_activities))[:5]
                        
                        epochs.append({
                            "epoch": len(epochs) + 1,
                            "compaction_time": None,
                            "compaction_iso": "current",
                            "auto": None,
                            "overflow": None,
                            "tail_start_id": "",
                            "part_counts": type_counts,
                            "total_parts": sum(type_counts.values()),
                            "key_activities": key_activities
                        })
                
                session_info = sessions.get(sid)
                
                # Get recent messages for context (last 3)
                recent_messages = []
                for m in messages_list[:3]:
                    recent_messages.append({
                        "time_created": m["time_created"],
                        "role": m["role"],
                        "content_preview": m["content_preview"]
                    })
                
                session_info_row = sessions.get(sid)
                timelines[sid] = {
                    "session_id": sid,
                    "slug": session_info_row["slug"] if session_info_row else "",
                    "agent": session_info_row["agent"] if session_info_row else "",
                    "title": session_info_row["title"] if session_info_row else "",
                    "session_tier": "EIS" if (session_info_row and session_info_row["parent_id"] is None) else "EAS/SPT",
                    "epochs": epochs,
                    "total_epochs": len(epochs),
                    "total_parts": sum(e["total_parts"] for e in epochs),
                    "recent_messages": messages_list[:3]
                }
                
            except Exception as e:
                print(f"[harvest] timeline mining failed for {sid}: {e}", file=sys.stderr)
                continue
        
        conn.close()
        return timelines
        
    except Exception as e:
        print(f"[harvest] timeline mining failed: {e}", file=sys.stderr)
        return {}


def mine_lexical_patterns(repo_root: Path) -> dict:
    """
    Mine lexical patterns from session corpus using FTS5 index.
    Returns top recurring tools, step reasons, blockers, decisions.
    Pure concatenation, zero inference, M7-compliant.
    """
    import sqlite3
    import re
    from collections import Counter
    
    db_path = repo_root / "data" / "search" / "session_fts5.db"
    
    if not db_path.exists():
        return {"status": "index_not_found", "message": "Run session_fts5.py --build first"}
    
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all decisions and continuations for pattern mining
        cursor.execute("""
            SELECT decisions, continuation, task_current, focus_chain, entity, source
            FROM session_fts
            WHERE decisions != '' OR continuation != ''
        """)
        rows = cursor.fetchall()
        
        # Extract patterns
        tool_counter = Counter()
        step_reason_counter = Counter()
        blocker_counter = Counter()
        decision_keywords = Counter()
        entity_activity = Counter()
        
        # Common tool names to identify in text
        known_tools = [
            "bash", "read", "write", "edit", "grep", "glob", "task", "todowrite",
            "omega-hub", "opencode", "parallel-search", "web_fetch", "web_search",
            "sqlite3", "git", "make", "python", "pytest", "sed", "awk", "cat",
            "ls", "find", "mkdir", "rm", "cp", "mv", "chmod", "systemctl",
            "journalctl", "docker", "podman", "kubectl", "terraform", "ansible"
        ]
        
        # Common step reason patterns
        step_patterns = [
            r'step[:\s]+([a-zA-Z][a-zA-Z0-9_\-]{2,30})',
            r'reason[:\s]+([a-zA-Z][a-zA-Z0-9_\-]{2,30})',
            r'completed[:\s]+([a-zA-Z][a-zA-Z0-9_\-]{2,30})',
            r'finished[:\s]+([a-zA-Z][a-zA-Z0-9_\-]{2,30})',
        ]
        
        for row in rows:
            entity = row["entity"] or "unknown"
            entity_activity[entity] += 1
            
            # Parse decisions for tool usage and step reasons
            decisions = row["decisions"] or ""
            continuation = row["continuation"] or ""
            task_current = row["task_current"] or ""
            focus_chain = row["focus_chain"] or ""
            
            combined = f"{decisions} {continuation} {task_current} {focus_chain}"
            combined_lower = combined.lower()
            
            # Extract tool mentions (known tool names)
            for tool in known_tools:
                # Match tool as whole word
                pattern = r'\b' + re.escape(tool) + r'\b'
                matches = len(re.findall(pattern, combined_lower))
                if matches > 0:
                    tool_counter[tool] += matches
            
            # Extract step reasons using patterns
            for pattern in step_patterns:
                matches = re.findall(pattern, combined_lower)
                for match in matches:
                    step_reason_counter[match] += 1
            
            # Extract blocker keywords
            blocker_keywords = ["blocked", "blocker", "fail", "error", "issue", "problem", "stuck", "broken"]
            for kw in blocker_keywords:
                if kw in combined_lower:
                    blocker_counter[kw] += 1
            
            # Extract decision keywords
            decision_keywords_list = ["decided", "ratified", "approved", "rejected", "resolved", "ruled", "accepted"]
            for kw in decision_keywords_list:
                if kw in combined_lower:
                    decision_keywords[kw] += 1
        
        conn.close()
        
        # Build result
        return {
            "status": "ok",
            "top_tools": [{"tool": k, "count": v} for k, v in tool_counter.most_common(20)],
            "top_step_reasons": [{"reason": k, "count": v} for k, v in step_reason_counter.most_common(20)],
            "top_blockers": [{"keyword": k, "count": v} for k, v in blocker_counter.most_common(10)],
            "top_decision_keywords": [{"keyword": k, "count": v} for k, v in decision_keywords.most_common(10)],
            "entity_activity": [{"entity": k, "sessions": v} for k, v in entity_activity.most_common(15)],
            "total_sessions_analyzed": sum(entity_activity.values())
        }
        
    except Exception as e:
        print(f"[harvest] lexical pattern mining failed: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}


def mine_semantic_patterns(repo_root: Path) -> dict:
    """
    Mine semantic patterns from session corpus using ONNX embeddings + sqlite-vec.
    Returns top semantic clusters, similar sessions, cross-domain connections.
    Pure local inference (ONNX), M7-compliant.
    """
    import sys
    sys.path.insert(0, str(repo_root / "scripts"))
    
    try:
        from session_semantic import SessionSemanticSearch
    except ImportError as e:
        return {"status": "module_not_found", "message": str(e)}
    
    try:
        semantic = SessionSemanticSearch(repo_root)
        
        # Check if index exists
        if not (repo_root / "data" / "search" / "session_semantic.db").exists():
            return {"status": "index_not_found", "message": "Run session_semantic.py --build first"}
        
        stats = semantic.get_stats()
        
        # Get some example semantic searches for key topics
        key_topics = [
            "compaction", "sovereignty", "handoff", "temple-grade",
            "zswap", "federation", "embedding", "vector"
        ]
        
        topic_clusters = {}
        for topic in key_topics:
            results = semantic.search(topic, limit=5)
            if results:
                topic_clusters[topic] = [
                    {
                        "session_id": r["session_id"][:12],
                        "entity": r["entity"],
                        "similarity": r["similarity"],
                        "task": r["task_current"][:80] if r["task_current"] else ""
                    }
                    for r in results[:3]
                ]
        
        return {
            "status": "ok",
            "index_stats": stats,
            "topic_clusters": topic_clusters,
            "model": "all-MiniLM-L6-v2 (ONNX)",
            "embedding_dim": 384
        }
        
    except Exception as e:
        print(f"[harvest] semantic pattern mining failed: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}


def parse_micro_digest(raw_digest: str, task_current: str, continuation: str) -> dict:
    """Extract DOING, NEXT, BLOCKER using robust regex."""
    if not raw_digest:
        doing = (task_current[:120] if task_current else "").strip()
        next_step = (continuation[:100] if continuation else "").strip()
        return {
            "doing": doing,
            "next": next_step,
            "blocker": None,
            "source": "fallback"
        }
    
    # Regex parse for DOING ... · NEXT ... [· BLOCKER ...]
    doing_match = re.search(r'DOING\s+([^·]+)', raw_digest, re.IGNORECASE)
    next_match = re.search(r'NEXT\s+([^·]+)', raw_digest, re.IGNORECASE)
    blocker_match = re.search(r'BLOCKER\s+(.+)', raw_digest, re.IGNORECASE)
    
    doing = doing_match.group(1).strip() if doing_match else raw_digest[:120].strip()
    next_step = next_match.group(1).strip() if next_match else ""
    blocker = blocker_match.group(1).strip() if blocker_match else None
    
    if blocker and blocker.lower() in ("none", "none.", "nil", "n/a", "no"):
        blocker = None
        
    return {
        "doing": doing,
        "next": next_step,
        "blocker": blocker,
        "source": "digest"
    }


def calculate_heartbeat_tier(post_ts_iso: str, now: datetime, extended_ttl: int = 0) -> str:
    try:
        # Handle trailing Z or offsets
        ts_clean = post_ts_iso.replace("Z", "+00:00")
        post_time = datetime.fromisoformat(ts_clean)
        age_s = (now - post_time).total_seconds()
        
        if extended_ttl and age_s <= extended_ttl:
            return "⚪ EXTENDED"
        if age_s <= 600:
            return "🟢 ACTIVE"
        elif age_s <= 2700:
            return "🟡 IDLE"
        else:
            return "⚫ EXPIRED"
    except Exception:
        return "🟡 UNKNOWN"


def harvest_once(repo_root: Path | None = None) -> int:
    """Run one harvest cycle.

    `repo_root` is the INJECTION POINT. Every path this function touches --
    the out_dir writes, the handoff-pending read, and the HALL_OF_RECORDS
    traversal -- derives from it. Callers that omit it get the historical
    behaviour (the script's own repo root), which is what production wants.

    Tests MUST pass an explicit root (pytest's tmp_path). Without it this
    function resolves the live checkout via get_repo_root() and writes into
    it: latest.json/latest.md at :314-318, latest_good.* at :322-323, a
    history record at :328, and -- once history exceeds 288 cycles -- an
    append-only MANIFEST.jsonl entry at :339-348 that is cumulative and
    never rewritten. A test that calls harvest_once() bare is a write-targeting
    harness aimed at live coordination state, which is the D-623 defect class
    that permanently lost 33 handoff packets. See
    tests/test_hivemind_harvester.py::test_harvest_execution_produces_artifacts,
    which asserts live data/ is byte-identical across the run.
    """
    repo_root = repo_root if repo_root is not None else _default_repo_root()
    coord_dir = repo_root / "data" / "coordination"
    out_dir = coord_dir / "hivemind_overview"
    out_dir.mkdir(parents=True, exist_ok=True)
    history_dir = out_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = out_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    lock_file = out_dir / ".harvester.lock"
    
    # 1. Non-blocking lock (Enhancement 5)
    with open(lock_file, "w") as lock_fd:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, IOError):
            # Cleanly yield if another harvester is running
            return 0
        
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        # 2. Gather inputs: Hot store + Hall of Records
        # Attempt to read data/coordination/metrics.json or handoffs for quick stats
        handoffs_pending_dir = repo_root / "data" / "handoff" / "pending"
        pending_handoff_count = len(list(handoffs_pending_dir.glob("ho_*.json"))) if handoffs_pending_dir.exists() else 0
        
        # Collect raw records
        raw_sessions = {}
        gaps = []

        # ── CONTROL PLANE (P1-1) ────────────────────────────────────────────
        # Four planes: kill / escalate / approve / throttle. The radar surfaces
        # the two that change what an operator must do next: how many sessions
        # are halted, and how many destructive ops are waiting on a human.
        cp = load_control_plane(repo_root)
        killed_ids: set = set()
        control_radar = {"control_plane_ok": False, "killed_count": None,
                         "pending_approvals": None}
        if cp is not None:
            try:
                control_radar = cp.radar_block()
                if control_radar.get("control_plane_ok"):
                    killed_ids = cp.killed_session_ids()
                else:
                    gaps.append({
                        "session_id": "control_plane",
                        "reason": f"control plane unreadable: "
                                  f"{control_radar.get('control_plane_error')}",
                    })
            except Exception as e:
                control_radar = {"control_plane_ok": False, "killed_count": None,
                                 "pending_approvals": None,
                                 "control_plane_error": str(e)}
                gaps.append({"session_id": "control_plane",
                             "reason": f"control plane read failed: {e}"})
        
        # ── OPENCODE.DB TODOS (DONE/PLANNED awareness) ────────────────────────
        opencode_todos = load_opencode_todos(repo_root)
        
        # ── HANDOFF INBOX (pending/active work packets) ────────────────────────
        handoff_inbox = load_handoff_inbox(repo_root)
        
        # ── SESSION TIMELINES (compaction epochs + activity streams) ──────────
        session_timelines = mine_session_timelines(repo_root)
        
        # ── FTS5 LEXICAL PATTERNS (mined from session corpus) ────────────────
        lexical_patterns = mine_lexical_patterns(repo_root)
        
        # ── SEMANTIC PATTERNS (ONNX embeddings + sqlite-vec) ────────────────
        semantic_patterns = mine_semantic_patterns(repo_root)
        
        # ── BUILD SESSION HIERARCHY (EIS → EAS/SPT) ────────────────────────
        session_hierarchy = build_session_hierarchy(opencode_todos, repo_root)
        
        # Cold store traversal (bounded glob)
        records_dir = repo_root / "data" / "knowledge" / "HALL_OF_RECORDS"
        if records_dir.exists():
            for agent_folder in records_dir.iterdir():
                if not agent_folder.is_dir():
                    continue
                for session_file in agent_folder.glob("ses_*.json"):
                    try:
                        data = json.loads(session_file.read_text(encoding="utf-8"))
                        sid = data.get("session_id")
                        if sid:
                            raw_sessions[sid] = data
                    except Exception as e:
                        gaps.append({
                            "session_id": session_file.stem,
                            "reason": f"Corrupt JSON in cold store: {e}"
                        })
        
        # In addition, scan active sessions in data/coordination/ if any
        # (Or query hub state if running in-process)
        
        # 3. Partition into EIS (Sovereign Seats) vs NES (Task Fleet) (Enhancement 2)
        sovereign_rows = []
        task_rows = []
        blockers = []
        active_count = 0
        
        SOVEREIGN_ENTITIES = {"kali", "maat", "lilith", "doom_guy", "john_carmack", "roc_racoon", "researcher", "verity", "antigravity"}
        
        for sid, sess in raw_sessions.items():
            entity = sess.get("entity", "unknown")
            ts = sess.get("timestamp", now_iso)
            raw_dig = sess.get("digest")
            task_cur = sess.get("task_current", "")
            contin = sess.get("continuation", "")
            
            parsed = parse_micro_digest(raw_dig, task_cur, contin)
            tier = calculate_heartbeat_tier(ts, now)

            # A killed session is not ACTIVE, IDLE, or EXPIRED — it was halted
            # on purpose. The kill tier wins over the heartbeat tier so a halted
            # agent never reads as merely idle.
            is_killed = sid in killed_ids
            if is_killed:
                tier = "🔴 KILLED"
            elif tier in ("🟢 ACTIVE", "⚪ EXTENDED"):
                active_count += 1
                
            is_blocker = (sess.get("intent") == "blocker") or (parsed["blocker"] is not None)
            if is_blocker and tier != "⚫ EXPIRED":
                blockers.append({
                    "entity": entity,
                    "session_id": sid,
                    "blocker": parsed["blocker"] or task_cur[:140]
                })
                
            row = {
                "entity": entity,
                "session_id": sid,
                "tier": tier,
                "channel": sess.get("channel", "opencode"),
                "model": sess.get("model", "unknown"),
                "intent": sess.get("intent", "status"),
                "timestamp": ts,
                "digest": raw_dig or f"[no-digest] {parsed['doing']} | {parsed['next']}",
                "digest_parsed": parsed,
                "killed": is_killed,
            }
            
            # Identify EIS vs NES:
            # If parent_id is present or task_id format -> NES (Task Fleet)
            if sess.get("parent_id") or "task" in sid.lower() or entity not in SOVEREIGN_ENTITIES:
                task_rows.append(row)
            else:
                sovereign_rows.append(row)
        
        # Sort rows: newest first within each section
        sovereign_rows.sort(key=lambda r: r["timestamp"], reverse=True)
        task_rows.sort(key=lambda r: r["timestamp"], reverse=True)
        
        status = "FRESH" if not gaps else "STALE_PARTIAL"
        
        # 4. Build latest.json
        payload_json = {
            "schema": "hivemind-overview/v1",
            "generated_at": now_iso,
            "interval_s": 300,
            "status": status,
            "radar": {
                "blocker_count": len(blockers),
                "pending_handoff_count": pending_handoff_count,
                "sessions_with_recent_post": active_count,
                # ── Control plane (P1-1) ──
                # null (not 0) when the control plane is unreadable: an
                # unreadable store is not an all-clear (M23).
                "killed_count": control_radar.get("killed_count"),
                "pending_approvals": control_radar.get("pending_approvals"),
                "throttled_entities": control_radar.get("throttled_entities"),
                "control_plane_ok": control_radar.get("control_plane_ok", False),
                "enforced_planes": control_radar.get("enforced_planes", []),
            },
            "blockers": blockers,
            "sovereign_fleet": sovereign_rows,
            "task_fleet": task_rows,
            "gaps": gaps,
            "opencode_todos": opencode_todos,
            "session_hierarchy": session_hierarchy,
            "session_timelines": session_timelines,
            "handoff_inbox": handoff_inbox,
            "lexical_patterns": lexical_patterns,
            "semantic_patterns": semantic_patterns,
            "generator": {"kind": "concatenation-only", "llm_used": False}
        }
        
        # 5. Build latest.md with 3-Line Triage Radar (Enhancements 1, 2, 3)
        md_lines = []
        md_lines.append(f"# ⬡ HIVEMIND FLEET RADAR — {now_iso} [{status}]")
        # ── 3-LINE TRIAGE RADAR (control plane appended) ──
        killed_n = control_radar.get("killed_count")
        pending_appr = control_radar.get("pending_approvals")
        # "?" not "0": a blind radar must not claim zero kills.
        killed_s = "?" if killed_n is None else str(killed_n)
        appr_s = "?" if pending_appr is None else str(pending_appr)
        md_lines.append(f"🔴 {len(blockers)} BLOCKERS | ⚡ {pending_handoff_count} PENDING HANDOFFS | 🟢 {active_count} SESSIONS ACTIVE")
        md_lines.append(f"☠️ {killed_s} KILLED | ⏳ {appr_s} PENDING APPROVALS"
                        + ("" if control_radar.get("control_plane_ok") else " | ⚠️ CONTROL PLANE UNREADABLE"))
        if blockers:
            for b in blockers:
                md_lines.append(f"🚨 BLOCKER: @{b['entity']} ({b['session_id'][:12]}): {b['blocker']}")
        else:
            md_lines.append("✨ FLEET STATUS: All operational · No active blockers reported.")
        md_lines.append("")
        
        md_lines.append("## 🏛️ Sovereign Fleet (Standing Seats / EIS)")
        if sovereign_rows:
            for r in sovereign_rows:
                md_lines.append(f"- **{r['tier']}** `@{r['entity']}` [{r['channel']}/{r['model']}] — *{r['digest']}*")
        else:
            md_lines.append("_No active sovereign seats recorded._")
        md_lines.append("")
        
        md_lines.append("## ⚡ Task Fleet (Subagent Dispatches / NES)")
        if task_rows:
            for r in task_rows[:20]:  # Cap task fleet display at 20 to prevent bloat
                md_lines.append(f"- **{r['tier']}** `@{r['entity']}` (`{r['session_id'][:12]}`) — {r['digest']}")
        else:
            md_lines.append("_No active task subagents._")
        md_lines.append("")
        
        if gaps:
            md_lines.append("## ⚠️ Gaps & Unreadable Shards")
            for g in gaps:
                md_lines.append(f"- ⚠️ GAP: `{g['session_id']}` — {g['reason']}")
            md_lines.append("")
        
        # ── OPENCODE.DB TODOS — HIERARCHICAL VIEW (EIS → EAS/SPT) ──
        if opencode_todos and session_hierarchy.get("EIS"):
            md_lines.append("## 📋 Active Todos (opencode.db) — Fleet Hierarchy")
            for eis_key, eis in session_hierarchy["EIS"].items():
                tier_icon = "🏛️"
                md_lines.append(f"### {tier_icon} EIS: `{eis['slug']}` @{eis['agent']} — *{eis['title']}*")
                ts = eis["todo_summary"]
                md_lines.append(f"- **Summary**: ✅ {ts.get('completed', 0)} completed · 📋 {ts.get('pending', 0)} pending · ⏳ {ts.get('in_progress', 0)} in-progress")
                
                # Show EIS todos (first 5)
                eis_todos = [t for t in opencode_todos if t["session_id"] == eis["session_id"]]
                for t in eis_todos[:5]:
                    status_icon = "✅" if t["status"] == "completed" else "📋"
                    md_lines.append(f"  - {status_icon} **[{t['status']}]** `{t['session_id'][:12]}` @{t['agent']}: {t['content'][:70]}")
                if len(eis_todos) > 5:
                    md_lines.append(f"  - _...and {len(eis_todos) - 5} more_")
                
                # EAS Children
                if eis["EAS_children"]:
                    md_lines.append(f"  #### 🤖 EAS Children (Autonomous Specialists):")
                    for c in eis["EAS_children"]:
                        cs = c["todo_summary"]
                        md_lines.append(f"  - `{c['slug']}` @{c['agent']} — *{c['title']}* [EAS]")
                        md_lines.append(f"    ✅ {cs.get('completed', 0)} · 📋 {cs.get('pending', 0)} · ⏳ {cs.get('in_progress', 0)}")
                
                # SPT Children
                if eis["SPT_children"]:
                    md_lines.append(f"  #### 🔬 SPT Children (Ephemeral Probes):")
                    for c in eis["SPT_children"]:
                        cs = c["todo_summary"]
                        md_lines.append(f"  - `{c['slug']}` @{c['agent']} — *{c['title']}* [SPT]")
                        md_lines.append(f"    ✅ {cs.get('completed', 0)} · 📋 {cs.get('pending', 0)} · ⏳ {cs.get('in_progress', 0)}")
                
                md_lines.append("")
        elif opencode_todos:
            # Fallback flat list if no hierarchy
            md_lines.append("## 📋 Active Todos (opencode.db)")
            for t in opencode_todos[:10]:
                status_icon = "✅" if t["status"] == "completed" else "📋"
                md_lines.append(f"- {status_icon} **[{t['status']}]** `{t['session_id'][:12]}` @{t['agent']}: {t['content'][:80]}")
            if len(opencode_todos) > 10:
                md_lines.append(f"- _...and {len(opencode_todos) - 10} more_")
            md_lines.append("")
        
        # ── SESSION TIMELINES (compaction epochs + activity streams) ──
        if session_timelines:
            md_lines.append("## 📈 Session Timelines (compaction epochs + activity streams)")
            for sid, timeline in session_timelines.items():
                if not timeline.get("epochs"):
                    continue
                md_lines.append(f"### 📍 `{timeline['slug']}` @{timeline['agent']} — *{timeline['title']}*")
                md_lines.append(f"- **Epochs**: {timeline['total_epochs']} · **Total parts**: {timeline['total_parts']} · **Tier**: {timeline['session_tier']}")
                
                for epoch in timeline["epochs"]:
                    if epoch["compaction_iso"] == "current":
                        epoch_marker = "🔄 CURRENT"
                    else:
                        epoch_marker = f"📦 Epoch {epoch['epoch']} ({epoch['compaction_iso']})"
                        if epoch["auto"]:
                            epoch_marker += " [auto]"
                        if epoch["overflow"]:
                            epoch_marker += " [overflow]"
                    
                    parts_str = ", ".join(f"{k}:{v}" for k, v in epoch["part_counts"].items())
                    md_lines.append(f"  - {epoch_marker} · Parts: {epoch['total_parts']} ({parts_str})")
                    
                    if epoch["key_activities"]:
                        activities_str = ", ".join(epoch["key_activities"])
                        md_lines.append(f"    Activities: {activities_str}")
                
                # Recent messages for context
                if timeline.get("recent_messages"):
                    md_lines.append("  - **Recent messages**:")
                    for msg in timeline["recent_messages"]:
                        role_icon = "👤" if msg["role"] == "user" else "🤖"
                        md_lines.append(f"    {role_icon} {msg['content_preview'][:100]}")
                
                md_lines.append("")
             
        # ── HANDOFF INBOX (pending/active work packets) ──
        if handoff_inbox:
            md_lines.append("## 📬 Handoff Inbox (pending/active work packets)")
            for h in handoff_inbox:
                md_lines.append(f"### {h['display_status']} `{h['packet_id']}` from @{h['source_entity']} ({h['source_channel']})")
                md_lines.append(f"- **Priority**: {h['priority']} · **Submitted**: {h['submitted_at']}")
                md_lines.append(f"- **Task**: {h['task'][:120]}")
                if h.get("context"):
                    ctx = h["context"][:200]
                    md_lines.append(f"- **Context**: {ctx}")
                if h.get("decisions"):
                    md_lines.append(f"- **Decisions**: {len(h['decisions'])} recorded")
                if h.get("outcome"):
                    md_lines.append(f"- **Outcome**: {h['outcome'][:100]}")
                md_lines.append("")
             
        # ── LEXICAL PATTERNS (FTS5 mined from session corpus) ──
        if lexical_patterns and lexical_patterns.get("status") == "ok":
            md_lines.append("## 🔍 Lexical Patterns (FTS5 mined from session corpus)")
            md_lines.append(f"- **Sessions analyzed**: {lexical_patterns.get('total_sessions_analyzed', 0)}")
            md_lines.append("")
            
            if lexical_patterns.get("top_tools"):
                md_lines.append("### Top Tools")
                for item in lexical_patterns["top_tools"][:10]:
                    md_lines.append(f"- `tool:{item['tool']}` — {item['count']} occurrences")
                md_lines.append("")
            
            if lexical_patterns.get("top_step_reasons"):
                md_lines.append("### Top Step Reasons")
                for item in lexical_patterns["top_step_reasons"][:10]:
                    md_lines.append(f"- `step:{item['reason']}` — {item['count']} occurrences")
                md_lines.append("")
            
            if lexical_patterns.get("top_blockers"):
                md_lines.append("### Top Blocker Keywords")
                for item in lexical_patterns["top_blockers"][:5]:
                    md_lines.append(f"- `{item['keyword']}` — {item['count']} occurrences")
                md_lines.append("")
            
            if lexical_patterns.get("top_decision_keywords"):
                md_lines.append("### Top Decision Keywords")
                for item in lexical_patterns["top_decision_keywords"][:5]:
                    md_lines.append(f"- `{item['keyword']}` — {item['count']} occurrences")
                md_lines.append("")
            
            if lexical_patterns.get("entity_activity"):
                md_lines.append("### Entity Activity (sessions with decisions/continuations)")
                for item in lexical_patterns["entity_activity"][:10]:
                    md_lines.append(f"- `@{item['entity']}` — {item['sessions']} sessions")
                md_lines.append("")
             
        # ── SEMANTIC PATTERNS (ONNX embeddings + sqlite-vec) ──
        if semantic_patterns and semantic_patterns.get("status") == "ok":
            md_lines.append("## 🧠 Semantic Patterns (ONNX embeddings + sqlite-vec)")
            stats = semantic_patterns.get("index_stats", {})
            md_lines.append(f"- **Index**: {stats.get('total_rows', 0)} vectors, {stats.get('embedding_dim', 384)}D, {semantic_patterns.get('model', 'all-MiniLM-L6-v2')}")
            md_lines.append("")
            
            if semantic_patterns.get("topic_clusters"):
                md_lines.append("### Topic Clusters (semantic similarity)")
                for topic, sessions in semantic_patterns["topic_clusters"].items():
                    if sessions:
                        md_lines.append(f"#### `{topic}`")
                        for s in sessions:
                            md_lines.append(f"- `{s['session_id']}` @{s['entity']} (sim: {s['similarity']:.3f}) — {s['task']}")
                        md_lines.append("")
             
        md_lines.append("_Footer: Pure zero-inference concatenation (M7). Store is truth; overview is projection._")
        payload_md = "\n".join(md_lines) + "\n"
        
        # 6. Atomic Write via .tmp files
        tmp_json = out_dir / "latest.json.tmp"
        tmp_md = out_dir / "latest.md.tmp"
        
        tmp_json.write_text(json.dumps(payload_json, indent=2), encoding="utf-8")
        tmp_md.write_text(payload_md, encoding="utf-8")
        
        tmp_json.replace(out_dir / "latest.json")
        tmp_md.replace(out_dir / "latest.md")
        
        # If fresh, update latest_good
        if status == "FRESH":
            shutil.copyfile(out_dir / "latest.json", out_dir / "latest_good.json")
            shutil.copyfile(out_dir / "latest.md", out_dir / "latest_good.md")
            
        # Write history record
        timestamp_slug = now.strftime("%Y%m%dT%H%M%SZ")
        history_file = history_dir / f"ov_{timestamp_slug}.json"
        history_file.write_text(json.dumps(payload_json), encoding="utf-8")
        
        # 7. M28 Retention: Keep 288 cycles in history/, move older to archive/<YYYY-MM>/
        history_files = sorted(history_dir.glob("ov_*.json"))
        if len(history_files) > 288:
            excess = history_files[:-288]
            month_str = now.strftime("%Y-%m")
            month_archive = archive_dir / month_str
            month_archive.mkdir(exist_ok=True)
            manifest_file = archive_dir / "MANIFEST.jsonl"
            
            with open(manifest_file, "a", encoding="utf-8") as mf:
                for old_f in excess:
                    dest = month_archive / old_f.name
                    old_f.rename(dest)
                    manifest_record = {
                        "file": old_f.name,
                        "archived_at": now_iso,
                        "destination": str(dest.relative_to(out_dir))
                    }
                    mf.write(json.dumps(manifest_record) + "\n")
                    
        return 0

if __name__ == "__main__":
    sys.exit(harvest_once())