"""Tests for the one-way MemPalace continuity projection adapter."""

from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from scripts.continuity_kernel import (
    ContinuityKernel,
    ModelPolicy,
    ModelRoute,
    PortableModelRouter,
    RecoveryError,
    SemanticEvent,
    WADContract,
)
from scripts.continuity_mempalace import McpDrawerSink, MemPalaceEventProjector
from scripts.continuity_sqlite import (
    _SQLITE_TEST_BYPASS,
    SqliteContinuityStore,
)


class RecordingDrawerSink:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []
        self._ids_by_content: dict[str, str] = {}

    def add_drawer(self, **fields: str) -> str:
        self.calls.append(fields)
        content = fields["content"]
        if content not in self._ids_by_content:
            self._ids_by_content[content] = f"drawer-{len(self._ids_by_content) + 1}"
        return self._ids_by_content[content]


class FailingDrawerSink:
    def add_drawer(self, **fields: str) -> str:
        raise OSError("injected drawer sink failure")


class RecordingMcpTool:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def __call__(self, name: str, arguments: dict[str, object]) -> dict[str, object]:
        self.calls.append((name, arguments))
        return {"drawer_id": "mcp-drawer-1"}


class GapEventStore:
    def __init__(self, events: list[SemanticEvent]) -> None:
        self.events = events

    def list(self, entity_id: str, upto_sequence: int | None = None):
        if upto_sequence is None:
            return self.events
        return [event for event in self.events if event.sequence <= upto_sequence]


class MemPalaceEventProjectorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = SqliteContinuityStore(
            Path(self.temp_dir.name) / "continuity.sqlite3",
            _test_bypass=_SQLITE_TEST_BYPASS,
        )
        self.contract = WADContract(
            entity_id="projection_entity",
            identity={"name": "Projection Entity", "ontology": "sovereign_entity"},
            model_policy=ModelPolicy(),
            durable_state_destinations=("sqlite", "event_log", "artifact_store"),
            active_work_pointer="active_work",
            recovery_procedure=("load_state", "replay_events", "resume"),
        )
        self.kernel = ContinuityKernel(
            contract=self.contract,
            state_store=self.store,
            artifact_store=self.store,
            event_bus=self.store,
            checkpoint_store=self.store,
            model_router=PortableModelRouter(ModelRoute("processor-a")),
            commit_journal=self.store,
        )
        self.kernel.bootstrap(self.active_work("initial"))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def active_work(self, mission: str) -> dict[str, object]:
        return {
            "mission": mission,
            "todos": ["continue"],
            "decisions": [],
            "discoveries": [],
        }

    def write_event(self, mission: str) -> None:
        self.kernel.write_through(
            "decision",
            {"mission": mission},
            self.active_work(mission),
        )

    def test_projects_exact_event_and_preserves_authority_state(self):
        self.write_event("projected mission")
        sink = RecordingDrawerSink()
        projector = MemPalaceEventProjector(self.store, sink)

        results = projector.project("projection_entity")

        self.assertEqual(1, len(results))
        self.assertEqual(1, results[0].sequence)
        self.assertEqual("drawer-1", results[0].drawer_id)
        self.assertEqual(1, len(sink.calls))
        call = sink.calls[0]
        self.assertEqual("omega_continuity", call["wing"])
        self.assertEqual("events", call["room"])
        self.assertEqual("continuity:projection_entity", call["source_file"])
        self.assertEqual("projection_entity", call["added_by"])
        self.assertEqual("projected mission", json.loads(call["content"])["active_work"]["mission"])
        self.assertEqual(1, self.store.read("projection_entity")["last_sequence"])
        self.assertEqual(1, len(self.store.list("projection_entity")))

    def test_replay_from_cursor_is_idempotent_with_content_deduplicating_sink(self):
        self.write_event("first mission")
        self.write_event("second mission")
        sink = RecordingDrawerSink()
        projector = MemPalaceEventProjector(self.store, sink)

        first = projector.project("projection_entity")
        second = projector.project("projection_entity", after_sequence=1)

        self.assertEqual([1, 2], [result.sequence for result in first])
        self.assertEqual([2], [result.sequence for result in second])
        self.assertEqual(3, len(sink.calls))
        self.assertEqual(2, len({call["content"] for call in sink.calls}))
        self.assertEqual(
            first[1].drawer_id,
            second[0].drawer_id,
        )

    def test_sink_failure_is_surfaced_for_retry(self):
        self.write_event("retryable mission")
        projector = MemPalaceEventProjector(self.store, FailingDrawerSink())

        with self.assertRaises(OSError):
            projector.project("projection_entity")

    def test_sequence_gap_is_rejected_before_projection(self):
        self.write_event("first mission")
        self.write_event("second mission")
        events = self.store.list("projection_entity")
        gapped = [events[0], replace(events[1], sequence=3)]
        projector = MemPalaceEventProjector(self.store, RecordingDrawerSink())

        with self.assertRaises(RecoveryError):
            MemPalaceEventProjector(GapEventStore(gapped), projector.drawer_sink).project(
                "projection_entity"
            )

    def test_mcp_sink_binds_to_named_drawer_tool(self):
        self.write_event("mcp mission")
        tool = RecordingMcpTool()
        sink = McpDrawerSink(tool)
        projector = MemPalaceEventProjector(self.store, sink)

        results = projector.project("projection_entity")

        self.assertEqual("mcp-drawer-1", results[0].drawer_id)
        self.assertEqual(1, len(tool.calls))
        self.assertEqual("mempalace_add_drawer", tool.calls[0][0])
        self.assertEqual("projection_entity", tool.calls[0][1]["added_by"])
        self.assertEqual("continuity:projection_entity", tool.calls[0][1]["source_file"])

    def test_invalid_cursor_is_rejected(self):
        projector = MemPalaceEventProjector(self.store, RecordingDrawerSink())

        with self.assertRaises(ValueError):
            projector.project("projection_entity", after_sequence=-1)
        with self.assertRaises(ValueError):
            projector.project("projection_entity", after_sequence=2, upto_sequence=1)


if __name__ == "__main__":
    unittest.main()
