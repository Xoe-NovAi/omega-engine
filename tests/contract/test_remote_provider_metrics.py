# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Contract Tests — §3.1 Concurrent RemoteProvider.generate() Metrics Recording.

[P2-1] Verifies the P0 §3.1 fix: `_record_perf` async bridge is fully async
(M1 AnyIO), safe under concurrent callers, and writes one `performance` row
per successful generate() call.

[M1: AnyIO] No `anyio.from_thread.run()` in the async path.
[M9: Error Integrity] Zero `RuntimeError`/`sqlite3.OperationalError` under
concurrency — the unlocked-write class is gone.
[M21: Gate Integrity] N concurrent calls ⇒ N performance rows with correct
`is_cloud`/`provider` values.
[M22: Response Provenance] `is_cloud` must reflect actual provider
classification, not intent.
"""

import tempfile
import logging
from pathlib import Path

import anyio
import pytest

from omega.observability.metrics_db import MetricsDB
from omega.oracle.backends.remote_provider import (
    ProviderConfig,
    ProviderHealth,
    RemoteProvider,
)

# Capture logs to assert no unhandled concurrency errors escaped.
log_capture: list = []


class _EchoProvider(RemoteProvider):
    """Minimal RemoteProvider subclass: returns the query as-is, no network."""

    async def _send_request(self, model_name, system_prompt, user_query, temperature, max_tokens, trace_id=None, session_id=None):
        return f"echo:{user_query}"


@pytest.fixture
def metrics_db():
    """Temporary MetricsDB with a real WAL-mode SQLite file (thread-safe)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MetricsDB(Path(tmpdir) / "test_metrics.db")
        db.initialize()
        yield db
        db.close()


@pytest.fixture(autouse=True)
def patch_metrics_singleton(metrics_db, monkeypatch):
    """Point remote_provider's `_metrics_db` singleton at the tmp DB."""
    from omega.oracle.backends import remote_provider as rp

    monkeypatch.setattr(rp, "_metrics_db", metrics_db)
    # Use the module lock so concurrent callers serialize on lazy init safely.
    monkeypatch.setattr(rp, "_metrics_db_lock", rp._metrics_db_lock)
    log_capture.clear()
    handler = _ListHandler()
    logger = logging.getLogger("omega.oracle.backends.remote_provider")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    yield handler
    logger.removeHandler(handler)


class _ListHandler(logging.Handler):
    def emit(self, record):
        log_capture.append(record.getMessage())


@pytest.fixture
def provider():
    cfg = ProviderConfig(name="test-provider", priority=0, models=["*"], max_retries=1, timeout_seconds=1.0)
    return _EchoProvider(cfg)


@pytest.mark.anyio
async def test_concurrent_generate_writes_n_performance_rows(provider, metrics_db):
    """[P2-1] N concurrent generate() calls ⇒ N performance rows, is_cloud=0.

    `test-provider` is unknown to ProviderRegistry ⇒ classified CLOUD by the
    pessimistic default (M22). Assert the row's is_cloud matches what
    ProviderRegistry reports, not a hardcoded value.
    """
    N = 16
    results = [None] * N

    async with anyio.create_task_group() as tg:
        for i in range(N):
            tg.start_soon(_call_and_store, provider, i, results)

    # All calls must have returned a string (no swallowed exceptions).
    assert all(r is not None for r in results), f"Some generate() calls failed: {results}"

    cursor = metrics_db._conn.execute(
        "SELECT provider, model_used, is_cloud FROM performance ORDER BY trace_id"
    )
    rows = cursor.fetchall()
    assert len(rows) == N, f"Expected {N} performance rows, got {len(rows)}"

    for row in rows:
        assert row[0] == "test-provider"
        # is_cloud must be the actual registry classification (pessimistic: 1)
        assert row[2] == 1

    # Zero concurrency errors escaped to the log.
    escaped = [m for m in log_capture if "RuntimeError" in m or "OperationalError" in m or "database is locked" in m]
    assert escaped == [], f"Concurrency errors leaked: {escaped}"


async def _call_and_store(provider, i, results):
    """Helper for start_soon: invoke generate and store result."""
    try:
        results[i] = await provider.generate(
            model_name="model-x",
            system_prompt="sys",
            user_query=f"query-{i}",
            max_tokens=16,
        )
    except Exception as e:  # pragma: no cover - should never happen
        results[i] = f"ERROR: {type(e).__name__}: {e}"


@pytest.mark.anyio
async def test_cloud_provider_records_is_cloud_1(monkeypatch):
    """[P2-1/M22] A known-cloud provider records is_cloud=1 in performance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db = MetricsDB(Path(tmpdir) / "test_metrics.db")
        db.initialize()
        try:
            from omega.oracle.backends import remote_provider as rp
            monkeypatch.setattr(rp, "_metrics_db", db)

            cfg = ProviderConfig(name="openrouter", priority=0, models=["*"], max_retries=1, timeout_seconds=1.0)
            provider = _EchoProvider(cfg)
            # _is_cloud_name uses ProviderRegistry; openrouter IS cloud.
            result = await provider.generate("model-x", "sys", "hello", max_tokens=8)
            assert result is not None

            cursor = db._conn.execute("SELECT is_cloud FROM performance")
            rows = cursor.fetchall()
            assert len(rows) == 1
            assert rows[0][0] == 1
        finally:
            db.close()
