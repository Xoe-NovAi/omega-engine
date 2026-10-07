#!/usr/bin/env python3
# ==============================================================================
# OMEGA ENGINE — EVOLUTION LOG SYSTEM
# ==============================================================================
# Persistent identity tracking across sessions. Append-only log of all
# evolution events, with semantic tagging and query capabilities.
#
# Usage: python3 evolution_log.py [command] [args...]
# Commands:
#   log      - Record an evolution event
#   query    - Query evolution history
#   stats    - Show evolution statistics
#   timeline - Generate visual timeline
#   export   - Export to various formats
# ==============================================================================

import json
import sys
import os
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

# ─── Configuration ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path("/home/xnai/Documents/Projects/omega-engine-alpha")
GNSSIS_ROOT = PROJECT_ROOT / "gnosis"
EVOLUTION_LOG = GNSSIS_ROOT / "evolution" / "evolution_log.jsonl"
EVOLUTION_INDEX = GNSSIS_ROOT / "evolution" / "evolution_index.json"
IDENTITY_FILE = GNSSIS_ROOT / "identity" / "identity.json"

# ─── Event Types ──────────────────────────────────────────────────────────────
EVENT_TYPES = {
    "SESSION_START": "New session begun",
    "SESSION_END": "Session completed with compaction",
    "CONFIG_CHANGE": "OpenCode/Ollama/system config modified",
    "CODE_CHANGE": "Source code modified",
    "DOC_UPDATE": "Documentation created/updated",
    "BENCHMARK": "Performance benchmark recorded",
    "BLOCKER": "Blocker identified",
    "BLOCKER_RESOLVED": "Blocker resolved",
    "DECISION": "Strategic decision made",
    "GNOSIS": "Insight/learning captured",
    "MILESTONE": "Major milestone achieved",
    "FEDERATION_EVENT": "P2P federation event",
    "AGENT_EVENT": "Agent created/updated/migrated",
    "MCP_EVENT": "MCP server added/removed/configured",
    "HARDWARE_EVENT": "Hardware change/upgrade",
    "KEY_ROTATION": "API key rotated/added/removed",
    "HOOK_EVENT": "OpenCode hook triggered"
}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def load_json(path: Path) -> Dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def save_json(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def append_jsonl(path: Path, record: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a') as f:
        f.write(json.dumps(record) + '\n')

def generate_event_id() -> str:
    return f"evt-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"

# ─── Core Functions ───────────────────────────────────────────────────────────
def log_event(event_type: str, session_id: str, description: str,
              metadata: Optional[Dict] = None, tags: Optional[List[str]] = None) -> Dict:
    """Log an evolution event to the append-only log."""
    
    if event_type not in EVENT_TYPES:
        print(f"⚠️  Unknown event type: {event_type}. Known: {list(EVENT_TYPES.keys())}")
    
    event = {
        "event_id": generate_event_id(),
        "timestamp": now_iso(),
        "event_type": event_type,
        "event_type_label": EVENT_TYPES.get(event_type, "Unknown"),
        "session_id": session_id,
        "description": description,
        "metadata": metadata or {},
        "tags": tags or [],
        "version": "1.0"
    }
    
    append_jsonl(EVOLUTION_LOG, event)
    
    # Update index
    index = load_json(EVOLUTION_INDEX)
    if "by_session" not in index:
        index["by_session"] = {}
    if "by_type" not in index:
        index["by_type"] = {}
    if "by_tag" not in index:
        index["by_tag"] = {}
    
    if session_id not in index["by_session"]:
        index["by_session"][session_id] = []
    index["by_session"][session_id].append(event["event_id"])
    
    if event_type not in index["by_type"]:
        index["by_type"][event_type] = []
    index["by_type"][event_type].append(event["event_id"])
    
    for tag in (tags or []):
        if tag not in index["by_tag"]:
            index["by_tag"][tag] = []
        index["by_tag"][tag].append(event["event_id"])
    
    index["last_event"] = event["event_id"]
    index["total_events"] = index.get("total_events", 0) + 1
    index["last_updated"] = now_iso()
    
    save_json(EVOLUTION_INDEX, index)
    
    print(f"✅ Logged: [{event_type}] {description}")
    return event

def query_events(session_id: Optional[str] = None,
                 event_type: Optional[str] = None,
                 tag: Optional[str] = None,
                 limit: int = 50) -> List[Dict]:
    """Query evolution log with filters."""
    
    if not EVOLUTION_LOG.exists():
        return []
    
    results = []
    with open(EVOLUTION_LOG) as f:
        for line in f:
            if not line.strip():
                continue
            event = json.loads(line)
            
            if session_id and event.get("session_id") != session_id:
                continue
            if event_type and event.get("event_type") != event_type:
                continue
            if tag and tag not in event.get("tags", []):
                continue
            
            results.append(event)
            if len(results) >= limit:
                break
    
    return results

def show_stats() -> None:
    """Display evolution statistics."""
    
    index = load_json(EVOLUTION_INDEX)
    identity = load_json(IDENTITY_FILE)
    
    print("\n╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                    📊 EVOLUTION STATISTICS                                 ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(f"\n📈 Total Events:     {index.get('total_events', 0)}")
    print(f"🕐 Last Event:       {index.get('last_event', 'None')}")
    print(f"🕐 Last Updated:     {index.get('last_updated', 'Never')}")
    print(f"👤 Identity:         {identity.get('entity', 'Unknown')}")
    print(f"🔢 Sessions:         {identity.get('session_count', 0)}")
    print(f"🎯 Current Session:  {identity.get('current_session', 'None')}")
    
    print("\n📋 By Type:")
    for etype, events in sorted(index.get("by_type", {}).items()):
        print(f"   {etype:20} : {len(events)} events")
    
    print("\n🏷️  Top Tags:")
    for tag, events in sorted(index.get("by_tag", {}).items(), key=lambda x: -len(x[1]))[:10]:
        print(f"   #{tag:20} : {len(events)} events")

def show_timeline(session_id: Optional[str] = None, limit: int = 20) -> None:
    """Display visual timeline of events."""
    
    events = query_events(session_id=session_id, limit=limit)
    
    if not events:
        print("No events found.")
        return
    
    print("\n╔════════════════════════════════════════════════════════════════════════════╗")
    print("║                         📅 EVOLUTION TIMELINE                              ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝\n")
    
    for event in reversed(events):
        ts = event["timestamp"][:19].replace('T', ' ')
        etype = event["event_type"]
        desc = event["description"][:80]
        tags = " ".join([f"#{t}" for t in event.get("tags", [])[:3]])
        
        type_color = {
            "MILESTONE": "🏆",
            "GNOSIS": "💡",
            "DECISION": "⚖️",
            "BLOCKER": "🚫",
            "FEDERATION_EVENT": "🔗",
            "CONFIG_CHANGE": "⚙️",
            "SESSION_END": "📦"
        }.get(event["event_type"], "📝")
        
        print(f"  {ts}  {type_color}  {etype:20}  {desc}")
        if tags:
            print(f"         Tags: {tags}")

def export_events(format: str = "json", session_id: Optional[str] = None) -> str:
    """Export events to various formats."""
    
    events = query_events(session_id=session_id, limit=1000)
    
    if format == "json":
        return json.dumps(events, indent=2)
    elif format == "jsonl":
        return "\n".join(json.dumps(e) for e in events)
    elif format == "markdown":
        lines = ["# Evolution Log Export\n"]
        for e in reversed(events):
            ts = e["timestamp"][:19].replace('T', ' ')
            lines.append(f"## {ts} — {e['event_type']}")
            lines.append(f"**Session:** {e['session_id']}")
            lines.append(f"**Description:** {e['description']}")
            if e.get("tags"):
                lines.append(f"**Tags:** {', '.join(e['tags'])}")
            if e.get("metadata"):
                lines.append(f"**Metadata:** ```json\n{json.dumps(e['metadata'], indent=2)}\n```")
            lines.append("")
        return "\n".join(lines)
    else:
        raise ValueError(f"Unknown format: {format}")

# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Omega Engine Evolution Log")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # log command
    log_parser = subparsers.add_parser("log", help="Log an evolution event")
    log_parser.add_argument("event_type", choices=list(EVENT_TYPES.keys()))
    log_parser.add_argument("session_id")
    log_parser.add_argument("description")
    log_parser.add_argument("--metadata", type=json.loads, default="{}")
    log_parser.add_argument("--tags", nargs="*", default=[])
    
    # query command
    query_parser = subparsers.add_parser("query", help="Query evolution events")
    query_parser.add_argument("--session-id")
    query_parser.add_argument("--type")
    query_parser.add_argument("--tag")
    query_parser.add_argument("--limit", type=int, default=50)
    
    # stats command
    subparsers.add_parser("stats", help="Show evolution statistics")
    
    # timeline command
    timeline_parser = subparsers.add_parser("timeline", help="Show visual timeline")
    timeline_parser.add_argument("--session-id")
    timeline_parser.add_argument("--limit", type=int, default=20)
    
    # export command
    export_parser = subparsers.add_parser("export", help="Export events")
    export_parser.add_argument("--format", choices=["json", "jsonl", "markdown"], default="markdown")
    export_parser.add_argument("--session-id")
    export_parser.add_argument("--output")
    
    args = parser.parse_args()
    
    if args.command == "log":
        log_event(args.event_type, args.session_id, args.description,
                  metadata=args.metadata, tags=args.tags)
    elif args.command == "query":
        events = query_events(session_id=args.session_id, event_type=args.type,
                              tag=args.tag, limit=args.limit)
        print(json.dumps(events, indent=2))
    elif args.command == "stats":
        show_stats()
    elif args.command == "timeline":
        show_timeline(session_id=args.session_id, limit=args.limit)
    elif args.command == "export":
        output = export_events(format=args.format, session_id=args.session_id)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Exported to {args.output}")
        else:
            print(output)

if __name__ == "__main__":
    main()