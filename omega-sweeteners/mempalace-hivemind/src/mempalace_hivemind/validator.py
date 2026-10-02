#!/usr/bin/env python3
"""Event Schema Validator for MemPalace Hivemind."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# Event schema validation
EVENT_TYPES = {
    "hivemind.briefing",
    "hivemind.ack",
    "task.request",
    "task.reply",
    "task.complete",
    "ritual.start",
    "ritual.end",
    "session.start",
    "session.end",
    "session.compacted",
    "sync.start",
    "sync.complete",
    "patch.ready",
    "build.status",
    "deploy.status",
    "agent.spawn",
    "agent.retire",
}

VALID_STREAMS = {
    "project/omega-engine",
    "gnosis",
    "well",
}

VALID_ROOMS = {
    # project/omega-engine rooms
    "federation", "cicd", "agents", "sync", "gnosis",
    # gnosis rooms
    "rituals", "evolution", "well", "identity",
    # well rooms
    "corrections", "preferences", "insights", "dreams",
}

TOPIC_PATTERN = re.compile(r'^[a-z0-9_.-]+$')
STREAM_PATTERN = re.compile(r'^[a-z0-9/_-]+$')
ROOM_PATTERN = re.compile(r'^[a-z0-9_-]+$')
ENTITY_PATTERN = re.compile(r'^[a-z0-9_-]+-n[0-9]$')
TO_AGENT_PATTERN = re.compile(r'^([a-z0-9_-]+-n[0-9]|\*)$')
EVENT_ID_PATTERN = re.compile(r'^evt_\d{8}T\d{6}_[a-f0-9]{16}$')
ISO_DATETIME_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
SHA256_PATTERN = re.compile(r'^[a-f0-9]{64}$')


class ValidationError(Exception):
    """Event validation error."""
    pass


def validate_entity(entity: str, field: str) -> None:
    """Validate entity has -n[0-9] suffix."""
    if not ENTITY_PATTERN.match(entity):
        raise ValidationError(f"{field} must end with -n[0-9] (got: {entity})")


def validate_to_agent(to_agent: str, field: str) -> None:
    """Validate to_agent (entity or *)."""
    if not TO_AGENT_PATTERN.match(to_agent):
        raise ValidationError(f"{field} must be entity with -n[0-9] suffix or * (got: {to_agent})")


def validate_event_id(event_id: str) -> None:
    if not EVENT_ID_PATTERN.match(event_id):
        raise ValidationError(f"Invalid event ID format: {event_id} (expected: evt_YYYYMMDDTHHMMSS_<16-hex>)")


def validate_iso_datetime(dt: str) -> None:
    try:
        datetime.fromisoformat(dt.replace('Z', '+00:00'))
    except ValueError:
        raise ValidationError(f"Invalid ISO-8601 UTC datetime (must end with Z): {dt}")


def validate_stream(stream: str) -> None:
    if stream not in VALID_STREAMS and not STREAM_PATTERN.match(stream):
        raise ValidationError(f"Invalid stream: {stream} (not in known streams, and pattern mismatch)")


def validate_room(room: str) -> None:
    if room not in VALID_ROOMS and not ROOM_PATTERN.match(room):
        raise ValidationError(f"Invalid room: {room} (not in known rooms, and pattern mismatch)")


def validate_topic(topic: str) -> None:
    if not TOPIC_PATTERN.match(topic):
        raise ValidationError(f"Invalid topic format: {topic} (must match {TOPIC_PATTERN.pattern})")


def validate_event_type(event_type: str) -> None:
    if event_type not in EVENT_TYPES:
        # Allow unknown types but warn
        pass  # Could be strict: raise ValidationError(f"Unknown event type: {event_type}")


def validate_tags(tags: List[Any]) -> None:
    if not isinstance(tags, list):
        raise ValidationError("tags must be an array")
    for tag in tags:
        if not isinstance(tag, str):
            raise ValidationError("All tags must be strings")


def validate_artifact_ids(artifacts: List[Any]) -> None:
    if not isinstance(artifacts, list):
        raise ValidationError("artifact_ids must be an array")
    for aid in artifacts:
        if not isinstance(aid, str):
            raise ValidationError("All artifact_ids must be strings")


def validate_metadata(metadata: Dict[str, Any]) -> None:
    if not isinstance(metadata, dict):
        raise ValidationError("metadata must be an object")


def validate_artifact_ids_list(artifacts: List[Any]) -> None:
    if not isinstance(artifacts, list):
        raise ValidationError("artifact_ids must be an array")
    for aid in artifacts:
        if not isinstance(aid, str):
            raise ValidationError("All artifact_ids must be strings")


def validate_event(event: Dict[str, Any]) -> None:
    """Validate a Hivemind event against the schema."""
    if not isinstance(event, dict):
        raise ValidationError("Event must be a JSON object")

    # Required fields
    required = ["id", "type", "stream", "room", "topic", "from_agent", "to_agent", "body", "created_at"]
    for field in required:
        if field not in event:
            raise ValidationError(f"Missing required field: {field}")

    # Validate each field
    validate_event_id(event["id"])
    validate_event_type(event["type"])
    validate_stream(event["stream"])
    validate_room(event["room"])
    validate_topic(event["topic"])
    validate_entity(event["from_agent"], "from_agent")
    validate_to_agent(event["to_agent"], "to_agent")

    if not isinstance(event["body"], str) or not event["body"].strip():
        raise ValidationError("body must be non-empty string")

    validate_iso_datetime(event["created_at"])

    # Optional fields
    if "correlation_id" in event and event["correlation_id"] is not None:
        if not isinstance(event["correlation_id"], str):
            raise ValidationError("correlation_id must be string or null")

    if "tags" in event:
        validate_tags(event["tags"])

    if "metadata" in event:
        validate_metadata(event["metadata"])

    if "artifact_ids" in event:
        validate_artifact_ids_list(event["artifact_ids"])


def validate_artifact(artifact: Dict[str, Any]) -> None:
    """Validate artifact object."""
    if not isinstance(artifact, dict):
        raise ValidationError("Artifact must be a JSON object")

    required = ["id", "kind", "content", "created_by", "created_at", "sha256"]
    for field in required:
        if field not in artifact:
            raise ValidationError(f"Artifact missing required field: {field}")

    validate_entity(artifact["created_by"], "created_by")
    validate_iso_datetime(artifact["created_at"])

    if not SHA256_PATTERN.match(artifact["sha256"]):
        raise ValidationError(f"Invalid sha256: {artifact['sha256']} (must be 64 hex chars)")

    if "metadata" in artifact and not isinstance(artifact["metadata"], dict):
        raise ValidationError("Artifact metadata must be an object")


def validate_file(filepath: Path) -> bool:
    """Validate a JSON file against the schema."""
    with open(filepath) as f:
        data = json.load(f)

    # Detect if it's an event or artifact
    if "type" in data and "from_agent" in data:
        validate_event(data)
    elif "kind" in data and "sha256" in data:
        validate_artifact(data)
    else:
        raise ValidationError("Unknown object type (neither event nor artifact)")

    return True


def main():
    parser = argparse.ArgumentParser(
        prog="hivemind-validate",
        description="Validate Hivemind event/artifact JSON against schema",
    )
    parser.add_argument("file", type=Path, help="JSON file to validate")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--quiet", action="store_true", help="Suppress success output")

    args = parser.parse_args()

    if not args.file.exists():
        print(f"❌ File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        validate_file(args.file)
        if not args.quiet:
            print("✅ Valid")
        sys.exit(0)
    except ValidationError as e:
        print(f"❌ Invalid: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    main()