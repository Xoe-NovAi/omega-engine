"""Tests for the portable continuity kernel and its chaos recovery path."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.continuity_kernel import (
    ContinuityError,
    ContractError,
    FileArtifactStore,
    FileCheckpointStore,
    FileEventBus,
    FileStateStore,
    InMemoryTelemetry,
    ModelPolicy,
    ModelRoute,
    PortableModelRouter,
    load_wad_contract,
    RecoveryError,
    WADContract,
    ContinuityKernel,
)
from scripts.continuity_files import FileCommitJournal


REPO = Path(__file__).resolve().parents[1]


class FailOnceStateStore(FileStateStore):
    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self.fail_next_write = False

    def write(self, state):
        if self.fail_next_write:
            self.fail_next_write = False
            raise OSError("injected state write failure")
        super().write(state)


class FailOnceArtifactStore(FileArtifactStore):
    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self.fail_next_put = False

    def put(self, content, content_type="application/json", metadata=None):
        if self.fail_next_put:
            self.fail_next_put = False
            raise OSError("injected artifact write failure")
        return super().put(content, content_type, metadata)


class FailOnceEventBus(FileEventBus):
    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self.fail_next_append = False

    def append(self, event):
        if self.fail_next_append:
            self.fail_next_append = False
            raise OSError("injected event append failure")
        super().append(event)


class FailOnceCheckpointStore(FileCheckpointStore):
    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self.fail_next_save = False

    def save(self, checkpoint):
        if self.fail_next_save:
            self.fail_next_save = False
            raise OSError("injected checkpoint write failure")
        super().save(checkpoint)


class FailOnceJournal(FileCommitJournal):
    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self.fail_next_commit = False

    def commit(self, intent_id: str, entity_id: str) -> None:
        if self.fail_next_commit:
            self.fail_next_commit = False
            raise OSError("injected journal commit failure")
        super().commit(intent_id, entity_id)


class ContinuityKernelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.root = root
        self.contract = WADContract(
            entity_id="test_entity",
            identity={"name": "Test Entity", "ontology": "sovereign_entity"},
            model_policy=ModelPolicy(),
            durable_state_destinations=("mempalace", "event_log", "artifact_store"),
            active_work_pointer="active_work",
            recovery_procedure=("load_state", "replay_events", "resume"),
        )
        self.state_store = FailOnceStateStore(root / "state")
        self.artifact_store = FileArtifactStore(root / "artifacts")
        self.event_bus = FileEventBus(root / "events")
        self.checkpoint_store = FileCheckpointStore(root / "checkpoints")
        self.commit_journal = FileCommitJournal(root / "journal")
        self.router = PortableModelRouter(ModelRoute("processor-a"))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def kernel(
        self,
        router: PortableModelRouter | None = None,
        *,
        state_store=None,
        artifact_store=None,
        event_bus=None,
        checkpoint_store=None,
        commit_journal=None,
    ) -> ContinuityKernel:
        return ContinuityKernel(
            contract=self.contract,
            state_store=state_store or self.state_store,
            artifact_store=artifact_store or self.artifact_store,
            event_bus=event_bus or self.event_bus,
            checkpoint_store=checkpoint_store or self.checkpoint_store,
            model_router=router or self.router,
            commit_journal=commit_journal or self.commit_journal,
        )

    def active_work(self, mission: str = "measure the continuity path") -> dict[str, object]:
        return {
            "mission": mission,
            "todos": ["map the state gradient"],
            "decisions": [],
            "discoveries": [],
        }

    def test_bootstrap_recovers_without_context(self):
        kernel = self.kernel()
        kernel.bootstrap(self.active_work())

        recovered = kernel.recover()

        self.assertEqual(0, recovered.state["last_sequence"])
        self.assertEqual([], list(recovered.events))
        self.assertEqual("Test Entity", recovered.state["identity"]["name"])
        self.assertEqual("processor-a", recovered.current_route.model_id)
        self.assertEqual(1, recovered.telemetry["counts"]["continuity_bootstrap"])
        self.assertEqual(1, recovered.telemetry["counts"]["recovery_integrity"])

    def test_write_through_persists_event_artifact_and_active_pointer(self):
        kernel = self.kernel()
        kernel.bootstrap(self.active_work())
        active_work = self.active_work("publish the measured result")
        active_work["decisions"] = ["The state gradient is durable before context eviction."]

        checkpoint = kernel.write_through(
            "decision",
            {"decision": "write through before continuing"},
            active_work,
        )
        recovered = kernel.recover()

        self.assertEqual(1, checkpoint.sequence)
        self.assertEqual(1, recovered.state["last_sequence"])
        self.assertEqual(1, len(recovered.events))
        self.assertEqual("decision", recovered.events[0].boundary)
        self.assertEqual("portable", recovered.events[0].adapter_id)
        self.assertEqual(
            "publish the measured result",
            recovered.state["active_work"]["mission"],
        )
        self.assertEqual(1, recovered.telemetry["counts"]["semantic_write_through"])

    def test_idempotency_key_deduplicates_replay(self):
        kernel = self.kernel()
        kernel.bootstrap(self.active_work())
        first = kernel.write_through(
            "decision",
            {"decision": "one durable decision"},
            self.active_work("deduplicated"),
            idempotency_key="decision-001",
        )
        second = kernel.write_through(
            "decision",
            {"decision": "one durable decision"},
            self.active_work("deduplicated"),
            idempotency_key="decision-001",
        )
        recovered = kernel.recover()

        self.assertEqual(first.sequence, second.sequence)
        self.assertEqual(1, len(recovered.events))
        self.assertEqual(1, recovered.telemetry["counts"]["idempotent_replay"])

    def test_recovery_rebuilds_missing_state_from_event_log(self):
        kernel = self.kernel()
        kernel.bootstrap(self.active_work())
        kernel.write_through(
            "task_transition",
            {"transition": "start next task"},
            self.active_work("resume after state loss"),
        )
        (Path(self.state_store.root) / "test_entity" / "state.json").unlink()

        recovered = self.kernel().recover()

        self.assertEqual("resume after state loss", recovered.state["active_work"]["mission"])
        self.assertEqual(1, recovered.telemetry["counts"]["state_rebuilt_from_event_log"])

    def test_recovery_rebuilds_missing_checkpoint(self):
        kernel = self.kernel()
        kernel.bootstrap(self.active_work())
        kernel.write_through("batch_completion", {"result": "done"}, self.active_work("checkpoint"))
        (Path(self.checkpoint_store.root) / "test_entity" / "checkpoint.json").unlink()

        recovered = self.kernel().recover()

        self.assertEqual(1, recovered.checkpoint.sequence)
        self.assertEqual(1, recovered.telemetry["counts"]["checkpoint_rebuilt"])

    def test_prepared_intent_replays_after_state_write_failure(self):
        kernel = self.kernel()
        kernel.bootstrap(self.active_work())
        self.state_store.fail_next_write = True

        with self.assertRaises(ContinuityError):
            kernel.write_through(
                "decision",
                {"decision": "prepared before failure"},
                self.active_work("replay prepared intent"),
            )

        recovered = kernel.recover()

        self.assertEqual(1, recovered.state["last_sequence"])
        self.assertEqual("replay prepared intent", recovered.state["active_work"]["mission"])
        self.assertEqual(1, recovered.telemetry["counts"]["commit_intent_replayed"])

    def test_artifact_failure_leaves_prior_state_untouched(self):
        artifact_store = FailOnceArtifactStore(self.root / "artifacts-fault")
        kernel = self.kernel(artifact_store=artifact_store)
        kernel.bootstrap(self.active_work("prior state"))
        artifact_store.fail_next_put = True

        with self.assertRaises(ContinuityError):
            kernel.write_through("decision", {"decision": "not written"}, self.active_work())

        recovered = self.kernel(artifact_store=artifact_store).recover()
        self.assertEqual(0, recovered.state["last_sequence"])
        self.assertEqual([], list(recovered.events))

    def test_event_failure_replays_prepared_intent(self):
        event_bus = FailOnceEventBus(self.root / "events-fault")
        kernel = self.kernel(event_bus=event_bus)
        kernel.bootstrap(self.active_work("prior state"))
        event_bus.fail_next_append = True

        with self.assertRaises(ContinuityError):
            kernel.write_through("discovery", {"finding": "replayed"}, self.active_work("recovered event"))

        recovered = self.kernel(event_bus=event_bus).recover()
        self.assertEqual(1, recovered.state["last_sequence"])
        self.assertEqual("recovered event", recovered.state["active_work"]["mission"])

    def test_checkpoint_failure_replays_without_duplicate_event(self):
        checkpoint_store = FailOnceCheckpointStore(self.root / "checkpoints-fault")
        kernel = self.kernel(checkpoint_store=checkpoint_store)
        kernel.bootstrap(self.active_work("prior state"))
        checkpoint_store.fail_next_save = True

        with self.assertRaises(ContinuityError):
            kernel.write_through("task_transition", {"task": "next"}, self.active_work("recovered checkpoint"))

        recovered = self.kernel(checkpoint_store=checkpoint_store).recover()
        self.assertEqual(1, len(recovered.events))
        self.assertEqual("recovered checkpoint", recovered.state["active_work"]["mission"])

    def test_journal_commit_failure_retires_on_recovery(self):
        journal = FailOnceJournal(self.root / "journal-fault")
        kernel = self.kernel(commit_journal=journal)
        kernel.bootstrap(self.active_work("prior state"))
        journal.fail_next_commit = True

        with self.assertRaises(ContinuityError):
            kernel.write_through("batch_completion", {"result": "committed"}, self.active_work("committed batch"))

        recovered = self.kernel(commit_journal=journal).recover()
        self.assertEqual(1, recovered.state["last_sequence"])
        self.assertEqual("committed batch", recovered.state["active_work"]["mission"])
        self.assertEqual([], journal.pending("test_entity"))

    def test_recovery_survives_model_and_adapter_swap(self):
        first = self.kernel()
        first.bootstrap(self.active_work())
        first.write_through(
            "discovery",
            {"observation": "context is a register"},
            self.active_work("map the register"),
        )

        swapped_router = PortableModelRouter(ModelRoute("processor-b", adapter="future-cli"))
        second = self.kernel(swapped_router)
        recovered = second.recover()

        self.assertEqual("Test Entity", recovered.state["identity"]["name"])
        self.assertEqual("processor-a", recovered.events[0].model_id)
        self.assertEqual("processor-b", recovered.current_route.model_id)
        self.assertEqual("future-cli", recovered.current_route.adapter)
        self.assertEqual("map the register", recovered.state["active_work"]["mission"])

    def test_artifact_store_supports_binary_content_and_verifies_hash(self):
        content = b"\x00\x01omega\xff"
        ref = self.artifact_store.put(content, content_type="application/octet-stream")

        self.assertEqual(content, self.artifact_store.get(ref.artifact_id))
        self.assertEqual(ref.sha256, ref.artifact_id)

    def test_recovery_rejects_tampered_payload_artifact(self):
        kernel = self.kernel()
        kernel.bootstrap(self.active_work())
        kernel.write_through("batch_completion", {"result": "measured"}, self.active_work())
        event = self.event_bus.list("test_entity")[0]
        blob = self.artifact_store.root / "blobs" / event.payload_artifact_id
        blob.write_bytes(b"tampered")

        with self.assertRaises(RecoveryError):
            kernel.recover()

    def test_contract_rejects_model_capacity_and_adapter_coupling(self):
        with self.assertRaises(ContractError):
            ModelPolicy(limits_source="hardcoded").validate()
        with self.assertRaises(ContractError):
            WADContract(
                entity_id="test_entity",
                identity={"name": "Test Entity"},
                model_policy=ModelPolicy(),
                durable_state_destinations=("opencode-session",),
                active_work_pointer="active_work",
                recovery_procedure=("resume",),
            )

    def test_continuity_adapters_meet_exception_and_anyio_gates(self):
        for relative_path in (
            "scripts/continuity_kernel.py",
            "scripts/continuity_files.py",
            "scripts/continuity_sqlite.py",
        ):
            source = (REPO / relative_path).read_text(encoding="utf-8")
            with self.subTest(path=relative_path):
                self.assertNotRegex(source, r"except\\s+Exception")
                self.assertNotRegex(source, r"(?m)^\\s*(import|from)\\s+(asyncio|trio)\\b")

    def test_arcana_wad_contract_loads_without_provider_coupling(self):
        contract_path = REPO / "wads" / "arcana_novai" / "continuity.contract.json"
        loaded = WADContract.from_dict(json.loads(contract_path.read_text(encoding="utf-8")))

        self.assertEqual("researcher_humboldt", loaded.entity_id)
        self.assertEqual("live_runtime", loaded.model_policy.limits_source)
        self.assertIn("mempalace", loaded.durable_state_destinations)

    def test_missing_wad_contract_is_observable(self):
        telemetry = InMemoryTelemetry()

        with self.assertRaises(RecoveryError):
            load_wad_contract(Path(self.temp_dir.name) / "missing.json", telemetry)

        self.assertEqual(1, telemetry.snapshot()["counts"]["missing_wad_contract"])

    def test_platform_coupling_is_observable(self):
        telemetry = InMemoryTelemetry()
        path = Path(self.temp_dir.name) / "coupled.json"
        path.write_text(
            json.dumps(
                {
                    **self.contract.to_dict(),
                    "durable_state_destinations": ["opencode-session"],
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaises(ContractError):
            load_wad_contract(path, telemetry)

        self.assertEqual(1, telemetry.snapshot()["counts"]["platform_coupling"])

    def test_contract_json_round_trip(self):
        loaded = WADContract.from_dict(json.loads(json.dumps(self.contract.to_dict())))

        self.assertEqual(self.contract.entity_id, loaded.entity_id)
        self.assertEqual(self.contract.to_dict(), loaded.to_dict())
        self.assertEqual(self.contract.digest(), loaded.digest())
        self.assertRegex(self.contract.digest(), r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
