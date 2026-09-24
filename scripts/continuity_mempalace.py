"""One-way MemPalace projection adapter for continuity events.

The SQLite continuity store is the commit authority. This module only projects
immutable semantic events through an injected drawer sink; it never writes to the
MemPalace SQLite database directly and never changes continuity state.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

from scripts.continuity_kernel import EventBus, RecoveryError, SemanticEvent


class DrawerSink(Protocol):
    """Minimal append boundary required by MemPalace projections."""

    def add_drawer(
        self,
        *,
        wing: str,
        room: str,
        content: str,
        source_file: str,
        added_by: str,
    ) -> str:
        """Append one exact drawer and return its stable drawer id."""


@dataclass(frozen=True)
class ProjectionResult:
    """Receipt for one projected semantic event."""

    event_id: str
    sequence: int
    drawer_id: str


class McpDrawerSink:
    """Bind the projector to a caller-provided MemPalace MCP tool invoker.

    The invoker should call the local or federated MCP tool named
    ``mempalace_add_drawer`` and return its decoded result object. Keeping the
    invoker injected avoids importing MemPalace internals or opening its SQLite
    database from continuity code.
    """

    def __init__(
        self,
        call_tool: Callable[[str, Mapping[str, object]], Mapping[str, object]],
        *,
        tool_name: str = "mempalace_add_drawer",
    ) -> None:
        if not tool_name:
            raise ValueError("MCP drawer tool name must be non-empty")
        self.call_tool = call_tool
        self.tool_name = tool_name

    def add_drawer(
        self,
        *,
        wing: str,
        room: str,
        content: str,
        source_file: str,
        added_by: str,
    ) -> str:
        result = self.call_tool(
            self.tool_name,
            {
                "wing": wing,
                "room": room,
                "content": content,
                "source_file": source_file,
                "added_by": added_by,
            },
        )
        drawer_id = result.get("drawer_id", result.get("id"))
        if not isinstance(drawer_id, str) or not drawer_id:
            raise RecoveryError("MemPalace MCP add_drawer returned no drawer id")
        return drawer_id


class MemPalaceEventProjector:
    """Replay continuity events into MemPalace without a second write path.

    The event store is the durable outbox. Replaying from an earlier sequence is
    safe when the drawer sink deduplicates exact content, which is the contract
    of the MemPalace add-drawer API. A sink failure is surfaced to the caller so
    the next run can retry from the same cursor.
    """

    def __init__(
        self,
        event_store: EventBus,
        drawer_sink: DrawerSink,
        *,
        wing: str = "omega_continuity",
        room: str = "events",
    ) -> None:
        if not wing or not room:
            raise ValueError("projection wing and room must be non-empty")
        self.event_store = event_store
        self.drawer_sink = drawer_sink
        self.wing = wing
        self.room = room

    def project(
        self,
        entity_id: str,
        *,
        after_sequence: int = 0,
        upto_sequence: int | None = None,
    ) -> list[ProjectionResult]:
        """Project contiguous events after a caller-owned cursor.

        The cursor is not persisted in the authority. The caller should persist
        its successful cursor in its own operational ledger only after this
        method returns successfully. Replaying a range is therefore safe.
        """
        if after_sequence < 0:
            raise ValueError("after_sequence must be non-negative")
        if upto_sequence is not None and upto_sequence < after_sequence:
            raise ValueError("upto_sequence must not precede after_sequence")

        events = self.event_store.list(entity_id, upto_sequence)
        projected: list[ProjectionResult] = []
        expected_sequence = after_sequence + 1
        for event in events:
            if event.sequence <= after_sequence:
                continue
            if event.sequence != expected_sequence:
                raise RecoveryError(
                    "continuity projection cursor has a sequence gap: "
                    f"expected {expected_sequence}, got {event.sequence}"
                )
            content = _canonical_json(event.to_dict())
            drawer_id = self.drawer_sink.add_drawer(
                wing=self.wing,
                room=self.room,
                content=content,
                source_file=f"continuity:{entity_id}",
                added_by=entity_id,
            )
            if not isinstance(drawer_id, str) or not drawer_id:
                raise RecoveryError(
                    f"drawer sink returned an invalid id for event {event.event_id}"
                )
            projected.append(
                ProjectionResult(
                    event_id=event.event_id,
                    sequence=event.sequence,
                    drawer_id=drawer_id,
                )
            )
            expected_sequence += 1
        return projected


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
