"""MemPalace Hivemind — Python Client Wrapper"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, List, Dict, AsyncGenerator

import mempalace  # MemPalace Python SDK


@dataclass
class HivemindEvent:
    """Hivemind event structure."""
    id: str
    type: str
    stream: str
    room: str
    topic: str
    from_agent: str
    to_agent: str
    body: str
    created_at: str
    correlation_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    artifact_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "stream": self.stream,
            "room": self.room,
            "topic": self.topic,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "body": self.body,
            "created_at": self.created_at,
            "correlation_id": self.correlation_id,
            "tags": self.tags,
            "metadata": self.metadata,
            "artifact_ids": self.artifact_ids,
        }


def generate_event_id() -> str:
    """Generate event ID: evt_YYYYMMDDTHHMMSS_hex16"""
    return f"evt_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:16]}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def validate_entity(entity: str) -> bool:
    """Validate entity has -n[0-9] suffix."""
    import re
    return bool(re.match(r'^[a-z0-9_-]+-n[0-9]$', entity))


class HivemindClient:
    """High-level MemPalace Hivemind client."""

    def __init__(
        self,
        entity: str,
        palace_path: Optional[str] = None,
        auto_connect: bool = True,
    ):
        if not validate_entity(entity):
            raise ValueError(f"Entity must have -n[0-9] suffix: {entity}")

        self.entity = entity
        self.palace_path = palace_path or os.environ.get(
            "MEMPALACE_PATH",
            str(Path.home() / "WanderGround" / "mempalace")
        )

        # Initialize MemPalace connection
        self.palace = mempalace.MemPalace(self.palace_path)
        if auto_connect:
            self.palace.connect()

        # Default stream/room
        self.default_stream = "project/omega-engine"
        self.default_room = "federation"

    def _append_event(
        self,
        event_type: str,
        body: str,
        stream: Optional[str] = None,
        room: Optional[str] = None,
        topic: Optional[str] = None,
        to_agent: str = "*",
        correlation_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        artifact_ids: Optional[List[str]] = None,
    ) -> HivemindEvent:
        """Append event to MemPalace logstream."""

        event = HivemindEvent(
            id=generate_event_id(),
            type=event_type,
            stream=stream or self.default_stream,
            room=room or self.default_room,
            topic=topic or "general",
            from_agent=self.entity,
            to_agent=to_agent,
            body=body,
            created_at=now_iso(),
            correlation_id=correlation_id,
            tags=tags or [],
            metadata=metadata or {},
            artifact_ids=artifact_ids or [],
        )

        # Store as drawer in MemPalace
        drawer_id = self.palace.add_drawer(
            wing=event.stream,
            room=event.room,
            content=json.dumps(event.to_dict(), ensure_ascii=False),
            source_file=f"hivemind:{event.topic}",
            added_by=self.entity,
        )

        event.metadata["drawer_id"] = drawer_id
        return event

    def brief(
        self,
        topic: str,
        body: str,
        room: Optional[str] = None,
        stream: Optional[str] = None,
        to_agent: str = "*",
        tags: Optional[List[str]] = None,
    ) -> HivemindEvent:
        """Send a briefing (fire-and-forget)."""
        return self._append_event(
            event_type="hivemind.briefing",
            body=body,
            stream=stream,
            room=room,
            topic=topic,
            to_agent=to_agent,
            tags=tags,
        )

    def ack(
        self,
        topic: str,
        body: str,
        room: Optional[str] = None,
        to_agent: str = "*",
        correlation_id: Optional[str] = None,
    ) -> HivemindEvent:
        """Send acknowledgment."""
        return self._append_event(
            event_type="hivemind.ack",
            body=body,
            room=room,
            topic=topic,
            to_agent=to_agent,
            correlation_id=correlation_id,
            tags=["ack"],
        )

    def request(
        self,
        topic: str,
        body: str,
        to_agent: str,
        room: Optional[str] = None,
        timeout_ms: int = 30000,
    ) -> Optional[HivemindEvent]:
        """Send request and wait for reply."""
        correlation_id = f"req-{generate_event_id().split('_')[1]}"

        self._append_event(
            event_type="task.request",
            body=body,
            topic=topic,
            to_agent=to_agent,
            correlation_id=correlation_id,
            tags=["request"],
        )

        return self.wait_for(
            topic=topic,
            from_agent=to_agent,
            correlation_id=correlation_id,
            timeout_ms=timeout_ms,
        )

    def wait_for(
        self,
        topic: str,
        from_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
        timeout_ms: int = 30000,
    ) -> Optional[HivemindEvent]:
        """Wait for matching event (blocking)."""
        start = time.time()
        timeout_s = timeout_ms / 1000.0

        while time.time() - start < timeout_s:
            events = self._query_events(
                topic=topic,
                from_agent=from_agent,
                correlation_id=correlation_id,
                limit=1,
                order="desc",
            )
            if events:
                return events[0]
            time.sleep(0.5)

        return None

    def wait_for_type(
        self,
        event_type: str,
        topic: Optional[str] = None,
        from_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
        timeout_ms: int = 30000,
    ) -> Optional[HivemindEvent]:
        """Wait for specific event type."""
        start = time.time()
        timeout_s = timeout_ms / 1000.0

        while time.time() - start < timeout_s:
            events = self._query_events(
                event_type=event_type,
                topic=topic,
                from_agent=from_agent,
                correlation_id=correlation_id,
                limit=1,
                order="desc",
            )
            if events:
                return events[0]
            time.sleep(0.5)

        return None

    def subscribe(
        self,
        room: Optional[str] = None,
        topic: Optional[str] = None,
        from_agent: Optional[str] = None,
        event_type: Optional[str] = None,
        poll_interval: float = 1.0,
    ) -> AsyncGenerator[HivemindEvent, None]:
        """Subscribe to events (async generator)."""
        last_id = None

        while True:
            events = self._query_events(
                room=room,
                topic=topic,
                from_agent=from_agent,
                event_type=event_type,
                limit=10,
                order="asc",
            )

            for event in events:
                if last_id is None or event.id > last_id:
                    yield event
                    last_id = event.id

            time.sleep(poll_interval)

    def _query_events(
        self,
        stream: Optional[str] = None,
        room: Optional[str] = None,
        topic: Optional[str] = None,
        from_agent: Optional[str] = None,
        event_type: Optional[str] = None,
        correlation_id: Optional[str] = None,
        limit: int = 50,
        order: str = "desc",
    ) -> List[HivemindEvent]:
        """Query events from MemPalace."""
        # Use MemPalace semantic search
        query_parts = []
        if topic:
            query_parts.append(f"topic:{topic}")
        if from_agent:
            query_parts.append(f"from:{from_agent}")
        if event_type:
            query_parts.append(f"type:{event_type}")

        query = " ".join(query_parts) if query_parts else "*"

        results = self.palace.search(
            query=query,
            limit=limit,
            wing=stream or self.default_stream,
            room=room or self.default_room,
        )

        events = []
        for result in results[:limit]:
            try:
                data = json.loads(result.content)
                events.append(HivemindEvent(**data))
            except (json.JSONDecodeError, TypeError):
                continue

        if order == "desc":
            events.reverse()

        return events[:limit]

    def put_artifact(
        self,
        kind: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store artifact and return artifact ID."""
        import hashlib

        artifact_id = f"art_{generate_event_id().split('_')[1]}"
        sha256 = hashlib.sha256(content.encode()).hexdigest()

        artifact_data = {
            "id": artifact_id,
            "kind": kind,
            "content": content,
            "created_by": self.entity,
            "created_at": now_iso(),
            "sha256": sha256,
            "metadata": metadata or {},
        }

        drawer_id = self.palace.add_drawer(
            wing="artifacts",
            room=kind,
            content=json.dumps(artifact_data, ensure_ascii=False),
            source_file=f"hivemind:artifact:{kind}",
            added_by=self.entity,
        )

        artifact_data["drawer_id"] = drawer_id
        return artifact_id

    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve artifact by ID."""
        # Search for artifact drawer
        results = self.palace.search(
            query=f"artifact:{artifact_id}",
            limit=1,
            wing="artifacts",
        )

        if results:
            try:
                return json.loads(results[0].content)
            except (json.JSONDecodeError, TypeError):
                pass
        return None

    def status(self) -> Dict[str, Any]:
        """Get client status."""
        identity = self.palace.get_identity() if hasattr(self.palace, 'get_identity') else {}
        return {
            "entity": self.entity,
            "palace_path": self.palace_path,
            "connected": True,
            "identity": identity,
            "default_stream": self.default_stream,
            "default_room": self.default_room,
        }


# CLI entry point
def main():
    import argparse

    parser = argparse.ArgumentParser(prog="hivemind", description="MemPalace Hivemind CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Global args
    parser.add_argument("--entity", default=os.environ.get("HIVEMIND_ENTITY", "unknown-n1"))
    parser.add_argument("--palace", default=os.environ.get("MEMPALACE_PATH"))

    # brief command
    brief_parser = subparsers.add_parser("brief", help="Send briefing")
    brief_parser.add_argument("--topic", required=True)
    brief_parser.add_argument("--body", required=True)
    brief_parser.add_argument("--body-file", help="Read body from file")
    brief_parser.add_argument("--room", default="federation")
    brief_parser.add_argument("--stream", default="project/omega-engine")
    brief_parser.add_argument("--to", default="*")
    brief_parser.add_argument("--tags", nargs="*")

    # wait command
    wait_parser = subparsers.add_parser("wait", help="Wait for event")
    wait_parser.add_argument("--topic", required=True)
    wait_parser.add_argument("--room", default="federation")
    wait_parser.add_argument("--from", dest="from_agent", help="From agent filter")
    wait_parser.add_argument("--correlation", dest="correlation_id")
    wait_parser.add_argument("--timeout", type=int, default=30000)

    # list command
    list_parser = subparsers.add_parser("list", help="List recent events")
    list_parser.add_argument("--room", default="federation")
    list_parser.add_argument("--topic")
    list_parser.add_argument("--limit", type=int, default=10)
    list_parser.add_argument("--order", choices=["asc", "desc"], default="desc")

    # status command
    subparsers.add_parser("status", help="Show client status")

    # artifact commands
    artifact_parser = subparsers.add_parser("artifact", help="Artifact operations")
    artifact_sub = artifact_parser.add_subparsers(dest="artifact_cmd", required=True)

    put_parser = artifact_sub.add_parser("put", help="Store artifact")
    put_parser.add_argument("--kind", required=True, choices=["patch", "file", "log", "json", "note"])
    put_parser.add_argument("--file", help="Read content from file")
    put_parser.add_argument("--content", help="Content string")
    put_parser.add_argument("--metadata", type=json.loads)

    args = parser.parse_args()

    client = HivemindClient(entity=args.entity, palace_path=args.palace)

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
        print(f"Sent: {event.id}")

    elif args.command == "wait":
        event = client.wait_for(
            topic=args.topic,
            room=args.room,
            from_agent=args.from_agent,
            correlation_id=args.correlation_id,
            timeout_ms=args.timeout,
        )
        if event:
            print(json.dumps(event.to_dict(), indent=2))
        else:
            print("Timeout", file=sys.stderr)
            sys.exit(1)

    elif args.command == "list":
        events = client._query_events(
            room=args.room,
            topic=args.topic,
            limit=args.limit,
            order=args.order,
        )
        for e in events:
            print(f"{e.id} | {e.type} | {e.topic} | {e.from_agent} -> {e.to_agent}")
            print(f"  {e.body[:100]}...")

    elif args.command == "status":
        print(json.dumps(client.status(), indent=2))

    elif args.command == "artifact" and args.artifact_cmd == "put":
        content = args.content
        if args.file:
            with open(args.file) as f:
                content = f.read()
        artifact_id = client.put_artifact(args.kind, content, args.metadata)
        print(f"Stored: {artifact_id}")


if __name__ == "__main__":
    main()