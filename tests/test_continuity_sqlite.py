"""Tests for the local SQLite commit-authority adapter."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

from scripts.continuity_kernel import (
    ContractError,
    ContinuityError,
    ContinuityKernel,
    ModelPolicy,
    ModelRoute,
    PortableModelRouter,
    RecoveryError,
    WADContract,
)
from scripts.continuity_sqlite import (
    _SQLITE_TEST_BYPASS,
    MINIMUM_FIXED_SQLITE,
    SqliteContinuityStore,
)


class _FaultyConnection:
    def __init__(self, connection: sqlite3.Connection, store: "FaultySqliteContinuityStore", fail_on: str) -> None:
        self._connection = connection
        self._store = store
        self._fail_on = fail_on

    def execute(self, sql: str, parameters: object = ()):
        normalized = " ".join(sql.upper().split())
        if self._fail_on and not self._store.failed and self._fail_on in normalized:
            self._store.failed = True
            raise OSError(f"injected SQLite failure: {self._fail_on}")
        return self._connection.execute(sql, parameters)

    def __getattr__(self, name: str):
        return getattr(self._connection, name)


class FaultySqliteContinuityStore(SqliteContinuityStore):
    def __init__(self, db_path: Path) -> None:
        self.fail_on = ""
        self.failed = False
        super().__init__(db_path, _test_bypass=_SQLITE_TEST_BYPASS)

    def arm(self, fail_on: str) -> None:
        self.fail_on = fail_on
        self.failed = False

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(
            self.db_path,
            timeout=self.timeout_seconds,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = DELETE")
        connection.execute("PRAGMA synchronous = FULL")
        connection.execute(f"PRAGMA busy_timeout = {int(self.timeout_seconds * 1000)}")
        try:
            yield _FaultyConnection(connection, self, self.fail_on)
        finally:
            connection.close()


class FailOncePrepareStore(SqliteContinuityStore):
    def __init__(self, db_path: Path) -> None:
        super().__init__(db_path, _test_bypass=_SQLITE_TEST_BYPASS)
        self.fail_next_prepare = False

    def prepare(self, intent):
        if self.fail_next_prepare:
            self.fail_next_prepare = False
            raise OSError("injected SQLite intent prepare failure")
        super().prepare(intent)


class FailOnceCommitStore(SqliteContinuityStore):
    def __init__(self, db_path: Path) -> None:
        super().__init__(db_path, _test_bypass=_SQLITE_TEST_BYPASS)
        self.fail_next_commit = False

    def commit(self, intent_id: str, entity_id: str) -> None:
        if self.fail_next_commit:
            self.fail_next_commit = False
            raise OSError("injected SQLite journal commit failure")
        super().commit(intent_id, entity_id)


class SqliteContinuityStoreTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "continuity.sqlite3"
        self.store = SqliteContinuityStore(
            self.db_path,
            _test_bypass=_SQLITE_TEST_BYPASS,
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

    def kernel_for_store(
        self, store: SqliteContinuityStore, router: PortableModelRouter | None = None
    ) -> ContinuityKernel:
        return ContinuityKernel(
            contract=self.contract,
            state_store=store,
            artifact_store=store,
            event_bus=store,
            checkpoint_store=store,
            model_router=router or self.router,
            commit_journal=store,
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

    def test_sqlite_crash_matrix_replays_each_transaction_boundary(self):
        boundaries = (
            "INSERT INTO EVENTS",
            "UPDATE STATE",
            "INSERT INTO CHECKPOINTS",
        )
        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                with tempfile.TemporaryDirectory() as temp_dir:
                    store = FaultySqliteContinuityStore(
                        Path(temp_dir) / "continuity.sqlite3"
                    )
                    kernel = self.kernel_for_store(store)
                    kernel.bootstrap(self.active_work("prior state"))
                    store.arm(boundary)

                    with self.assertRaises(ContinuityError):
                        kernel.write_through(
                            "decision",
                            {"decision": "crash at boundary"},
                            self.active_work("recovered after crash"),
                            idempotency_key=f"crash-{boundary}",
                        )

                    self.assertTrue(store.failed)
                    self.assertEqual(0, store.read("sqlite_entity")["last_sequence"])
                    self.assertEqual([], store.list("sqlite_entity"))
                    self.assertEqual(1, len(store.pending("sqlite_entity")))

                    recovered = self.kernel_for_store(store).recover()

                    self.assertEqual(1, recovered.state["last_sequence"])
                    self.assertEqual(
                        "recovered after crash",
                        recovered.state["active_work"]["mission"],
                    )
                    self.assertEqual(1, len(recovered.events))
                    self.assertEqual([], store.pending("sqlite_entity"))

    def test_sqlite_intent_prepare_failure_preserves_prior_state(self):
        store = FailOncePrepareStore(self.db_path)
        kernel = self.kernel_for_store(store)
        kernel.bootstrap(self.active_work("prior state"))
        store.fail_next_prepare = True

        with self.assertRaises(ContinuityError):
            kernel.write_through(
                "discovery",
                {"finding": "not prepared"},
                self.active_work("must not advance"),
            )

        self.assertEqual(0, store.read("sqlite_entity")["last_sequence"])
        self.assertEqual([], store.list("sqlite_entity"))
        recovered = self.kernel_for_store(store).recover()
        self.assertEqual("prior state", recovered.state["active_work"]["mission"])

    def test_sqlite_post_apply_journal_failure_leaves_complete_commit(self):
        store = FailOnceCommitStore(self.db_path)
        kernel = self.kernel_for_store(store)
        kernel.bootstrap(self.active_work("prior state"))
        store.fail_next_commit = True

        with self.assertRaises(ContinuityError):
            kernel.write_through(
                "batch_completion",
                {"result": "complete before journal cleanup"},
                self.active_work("committed before journal cleanup"),
            )

        recovered = self.kernel_for_store(store).recover()
        self.assertEqual(1, recovered.state["last_sequence"])
        self.assertEqual(
            "committed before journal cleanup",
            recovered.state["active_work"]["mission"],
        )
        self.assertEqual(1, len(recovered.events))
        self.assertEqual([], store.pending("sqlite_entity"))

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
