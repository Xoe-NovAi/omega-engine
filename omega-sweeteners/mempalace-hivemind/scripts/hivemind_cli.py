#!/usr/bin/env python3
"""MemPalace Hivemind CLI — Command-line interface for Hivemind operations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mempalace_hivemind import HivemindClient


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hivemind",
        description="MemPalace Hivemind CLI — Agent coordination over event logstream",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--entity",
        default=os.environ.get("HIVEMIND_ENTITY", "unknown-n1"),
        help="Your entity ID (must end with -n1 or -n0)",
    )
    parser.add_argument(
        "--palace",
        default=os.environ.get("MEMPALACE_PATH"),
        help="Path to MemPalace directory (default: ~/WanderGround/mempalace)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    # ===== brief =====
    brief = subparsers.add_parser("brief", help="Send a briefing (fire-and-forget)")
    brief.add_argument("--topic", required=True, help="Event topic (e.g., pr-delivery)")
    brief.add_argument("--body", help="Message body (markdown)")
    brief.add_argument("--body-file", type=Path, help="Read body from file")
    brief.add_argument("--room", default="federation", help="Room name")
    brief.add_argument("--stream", default="project/omega-engine", help="Stream/wing")
    brief.add_argument("--to", default="*", help="Target agent (or * for broadcast)")
    brief.add_argument("--tags", nargs="*", help="Tags (e.g., ritual session-end)")

    # ===== ack =====
    ack = subparsers.add_parser("ack", help="Send acknowledgment")
    ack.add_argument("--topic", required=True, help="Topic to acknowledge")
    ack.add_argument("--body", required=True, help="Acknowledgment message")
    ack.add_argument("--room", default="federation")
    ack.add_argument("--stream", default="project/omega-engine")
    ack.add_argument("--to", default="*")
    ack.add_argument("--correlation", help="Correlation ID to ack")

    # ===== request =====
    req = subparsers.add_parser("request", help="Send request and wait for reply")
    req.add_argument("--topic", required=True, help="Request topic")
    req.add_argument("--body", required=True, help="Request body")
    req.add_argument("--to", required=True, help="Target agent (must have -n0/-n1)")
    req.add_argument("--room", default="federation")
    req.add_argument("--stream", default="project/omega-engine")
    req.add_argument("--timeout", type=int, default=30000, help="Timeout in ms")

    # ===== wait =====
    wait = subparsers.add_parser("wait", help="Wait for matching event (blocking)")
    wait.add_argument("--topic", required=True, help="Event topic filter")
    wait.add_argument("--room", default="federation", help="Room filter")
    wait.add_argument("--stream", default="project/omega-engine")
    wait.add_argument("--from", dest="from_agent", help="From agent filter")
    wait.add_argument("--type", dest="event_type", help="Event type filter (e.g., task.reply)")
    wait.add_argument("--correlation", dest="correlation_id", help="Correlation ID filter")
    wait.add_argument("--timeout", type=int, default=30000, help="Timeout in ms")

    # ===== list =====
    list_cmd = subparsers.add_parser("list", help="List recent events")
    list_cmd.add_argument("--room", default="federation")
    list_cmd.add_argument("--stream", default="project/omega-engine")
    list_cmd.add_argument("--topic", help="Topic filter")
    list_cmd.add_argument("--type", dest="event_type", help="Event type filter")
    list_cmd.add_argument("--from", dest="from_agent", help="From agent filter")
    list_cmd.add_argument("--limit", type=int, default=10)
    list_cmd.add_argument("--order", choices=["asc", "desc"], default="desc")

    # ===== subscribe =====
    sub = subparsers.add_parser("subscribe", help="Subscribe to events (continuous)")
    sub.add_argument("--room", default="federation")
    sub.add_argument("--stream", default="project/omega-engine")
    sub.add_argument("--topic")
    sub.add_argument("--type", dest="event_type")
    sub.add_argument("--from", dest="from_agent")
    sub.add_argument("--interval", type=float, default=1.0, help="Poll interval (seconds)")

    # ===== artifact =====
    art = subparsers.add_parser("artifact", help="Artifact operations")
    art_sub = art.add_subparsers(dest="artifact_cmd", required=True)

    put = art_sub.add_parser("put", help="Store artifact")
    put.add_argument("--kind", required=True, choices=["patch", "file", "log", "json", "note"])
    put.add_argument("--file", type=Path, help="Read content from file")
    put.add_argument("--content", help="Content string")
    put.add_argument("--metadata", type=json.loads, default="{}", help="JSON metadata")

    get = art_sub.add_parser("get", help="Retrieve artifact")
    get.add_argument("artifact_id", help="Artifact ID")

    # ===== status =====
    subparsers.add_parser("status", help="Show client status")

    # ===== validate =====
    val = subparsers.add_parser("validate", help="Validate event JSON against schema")
    val.add_argument("file", type=Path, help="Event JSON file to validate")

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    # Validate entity
    import re
    if not re.match(r'^[a-z0-9_-]+-n[0-9]$', args.entity):
        parser.error(f"Entity must end with -n1 or -n0: {args.entity}")

    client = HivemindClient(
        entity=args.entity,
        palace_path=args.palace,
    )

    if args.command == "brief":
        body = args.body
        if args.body_file:
            with open(args.body_file) as f:
                body = f.read()
        event = client.brief(
            topic=args.topic,
            body=body,
            room=args.room,
            stream=args.stream,
            to_agent=args.to,
            tags=args.tags,
        )
        print(f"✅ Sent: {event.id}")

    elif args.command == "ack":
        event = client.ack(
            topic=args.topic,
            body=args.body,
            room=args.room,
            stream=args.stream,
            to_agent=args.to,
            correlation_id=args.correlation,
        )
        print(f"✅ Acknowledged: {event.id}")

    elif args.command == "request":
        event = client.request(
            topic=args.topic,
            body=args.body,
            to_agent=args.to,
            room=args.room,
            stream=args.stream,
            timeout_ms=args.timeout,
        )
        if event:
            print(f"✅ Reply received: {event.id}")
            print(json.dumps(event.to_dict(), indent=2))
        else:
            print("❌ Timeout waiting for reply", file=sys.stderr)
            sys.exit(1)

    elif args.command == "wait":
        event = client.wait_for(
            topic=args.topic,
            room=args.room,
            stream=args.stream,
            from_agent=args.from_agent,
            event_type=args.event_type,
            correlation_id=args.correlation_id,
            timeout_ms=args.timeout,
        )
        if event:
            print(json.dumps(event.to_dict(), indent=2))
        else:
            print("❌ Timeout", file=sys.stderr)
            sys.exit(1)

    elif args.command == "list":
        events = client._query_events(
            room=args.room,
            stream=args.stream,
            topic=args.topic,
            event_type=args.event_type,
            from_agent=args.from_agent,
            limit=args.limit,
            order=args.order,
        )
        for e in events:
            tags = f" [{','.join(e.tags)}]" if e.tags else ""
            print(f"{e.id} | {e.type:25} | {e.topic:20} | {e.from_agent:12} -> {e.to_agent:12}{tags}")
            print(f"    {e.body[:120]}...")

    elif args.command == "subscribe":
        print(f"Subscribing to {args.stream}/{args.room}/{args.topic or '*'}... (Ctrl+C to stop)")
        try:
            for event in client.subscribe(
                room=args.room,
                stream=args.stream,
                topic=args.topic,
                event_type=args.event_type,
                from_agent=args.from_agent,
                poll_interval=2.0,
            ):
                tags = f" [{','.join(event.tags)}]" if event.tags else ""
                print(f"\n{event.id} | {event.type} | {event.topic} | {event.from_agent} -> {event.to_agent}{tags}")
                print(f"  {event.body[:200]}")
        except KeyboardInterrupt:
            print("\n👋 Unsubscribed")

    elif args.command == "artifact":
        if args.artifact_cmd == "put":
            content = args.content
            if args.file:
                with open(args.file) as f:
                    content = f.read()
            artifact_id = client.put_artifact(args.kind, content, args.metadata)
            print(f"✅ Stored: {artifact_id}")

        elif args.artifact_cmd == "get":
            artifact = client.get_artifact(args.artifact_id)
            if artifact:
                print(json.dumps(artifact, indent=2))
            else:
                print(f"❌ Artifact not found: {args.artifact_id}", file=sys.stderr)
                sys.exit(1)

    elif args.command == "status":
        print(json.dumps(client.status(), indent=2))

    elif args.command == "validate":
        with open(args.file) as f:
            event = json.load(f)
        from event_validator import validate_event
        try:
            validate_event(event)
            print("✅ Valid")
        except Exception as e:
            print(f"❌ Invalid: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()