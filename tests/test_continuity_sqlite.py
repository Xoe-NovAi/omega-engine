"""Tests for the local SQLite commit-authority adapter."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from scripts.continuity_kernel import (
    ContractError,
    ContinuityKernel,
    ModelPolicy,
    ModelRoute,
    PortableModelRouter,
    RecoveryError,
    WADContract,
)
from scripts.continuity_sqlite import MINIMUM_FIXED_SQLITE, SqliteContinuityStore


class SqliteContinuityStoreTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "continuity.sqlite3"
        self.store = SqliteContinuityStore(
            self.db_path,
            require_fixed_sqlite=False,
        )
        self.contract = WADContract(
            entity_id="sqlite_entity",
            identity={"name": "SQLite Entity", "ontology": "sovereign_entity"},
            model_policy=ModelPolicy(),
            durable_state_destinations=("sqlite", "event_log", "artifact_store"),
            active_work_pointer="active_work",
            recovery_procedure=("load_state", "replay_events", "resume"),
        )
        self.router = PortableModelRouter(ModelRoute("processor-a"))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def kernel(self, router: PortableModelRouter | None = None) -> ContinuityKernel:
        return ContinuityKernel(
            contract=self.contract,
            state_store=self.store,
            artifact_store=self.store,
            event_bus=self.store,
            checkpoint_store=self.store,
            model_router=router or self.router,
            commit_journal=self.store,
        )

    def active_work(self, mission: str) -> dict[str, object]:
        return {
            "mission": mission,
            "todos": ["continue"],
            "decisions": [],
            "discoveries": [],
        }

    def test_production_sqlite_version_guard(self):
        if sqlite3.sqlite_version_info >= MINIMUM_FIXED_SQLITE:
            self.skipTest("host SQLite is already above the production floor")
        with self.assertRaises(ContractError):
            SqliteContinuityStore(self.db_path)

    def test_sqlite_commit_and_model_swap_recovery(self):
        first = self.kernel()
        first.bootstrap(self.active_work("bootstrap mission"))
        first.write_through(
            "discovery",
            {"finding": "SQLite is the local commit authority"},
            self.active_work("map SQLite authority"),
            idempotency_key="sqlite-001",
        )

        second = self.kernel(PortableModelRouter(ModelRoute("processor-b", "future-cli")))
        recovered = second.recover()

        self.assertEqual("map SQLite authority", recovered.state["active_work"]["mission"])
        self.assertEqual("sqlite_entity", recovered.state["entity_id"])
        self.assertEqual("processor-b", recovered.current_route.model_id)
        self.assertEqual("future-cli", recovered.current_route.adapter)

    def test_intent_apply_is_atomic_on_sequence_conflict(self):
        kernel = self.kernel()
        kernel.bootstrap(self.active_work("initial"))
        kernel.write_through("decision", {"decision": "one"}, self.active_work("committed"))
        event = self.store.list("sqlite_entity")[0]
        conflicting = replace(
            event,
            event_id="conflicting-event",
            payload={"decision": "conflict"},
        )
        intent_state = self.store.read("sqlite_entity")
        from scripts.continuity_kernel import Checkpoint, CommitIntent

        intent = CommitIntent(
            intent_id="conflicting-intent",
            event=conflicting,
            state=intent_state,
            checkpoint=Checkpoint(
                checkpoint_id="conflicting-checkpoint",
                entity_id="sqlite_entity",
                sequence=1,
                state=intent_state,
                event_ids=(conflicting.event_id,),
                artifact_ids=(conflicting.payload_artifact_id,),
                created_at=conflicting.created_at,
            ),
            created_at=conflicting.created_at,
        )

        with self.assertRaises(RecoveryError):
            self.store.apply_intent(intent)

        self.assertEqual(1, len(self.store.list("sqlite_entity")))
        self.assertEqual(1, self.store.read("sqlite_entity")["last_sequence"])


if __name__ == "__main__":
    unittest.main()
