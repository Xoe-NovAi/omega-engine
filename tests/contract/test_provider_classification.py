# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Invariant test: no provider has split classification across call sites.

[M22 SSOT] Every cloud-classification call site must delegate to
`ProviderRegistry.is_cloud()` (which reads `config/providers.yaml`). This
test verifies (1) the registry reflects providers.yaml, and (2) all five
call-site classifiers agree with the registry for every known provider.

AP Token: AP-PROVIDER-CLASSIFICATION-INVARIANT-20260809-v1.0.0
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from omega.oracle.provider_registry import ProviderRegistry
from omega.oracle.model_gateway import ModelGateway
from omega.observability import BudgetGate
from omega.observability.otel_exporter import OTelSQLiteExporter
from omega.oracle.backends.remote_provider import (
    RemoteProvider,
    ProviderConfig,
)
from omega.ingestion.pipeline import (
    IngestionPipeline,
    IngestionConfig,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
PROVIDERS_YAML = REPO_ROOT / "config" / "providers.yaml"


class _StubProvider:
    """Minimal provider-shaped double exposing a `name` attribute."""

    def __init__(self, name: str) -> None:
        self.name = name


class _StubRemote(RemoteProvider):
    """Concrete RemoteProvider subclass so the ABC is instantiable."""

    async def _send_request(self, *args, **kwargs):  # pragma: no cover - stub
        return "stub"


def _load_providers_yaml() -> dict:
    with open(PROVIDERS_YAML) as f:  # noqa: PTH123
        return yaml.safe_load(f)


class TestProviderClassificationInvariant:
    """All 5 call sites must agree on cloud/local for every provider."""

    @pytest.fixture
    def registry(self) -> ProviderRegistry:
        return ProviderRegistry.from_config_path()

    @pytest.fixture
    def model_gateway(self) -> ModelGateway:
        return ModelGateway()

    @pytest.fixture
    def budget_gate(self) -> BudgetGate:
        return BudgetGate()

    @pytest.fixture
    def otel_exporter(self) -> OTelSQLiteExporter:
        return OTelSQLiteExporter(metrics_db=MagicMock())

    def test_registry_matches_providers_yaml(self, registry):
        """Registry must match providers.yaml fallback_chain is_cloud flags."""
        config = _load_providers_yaml()
        chain = config["inference"]["fallback_chain"]
        for provider_cfg in chain:
            name = provider_cfg["provider"]
            expected = bool(provider_cfg.get("is_cloud", False))
            assert registry.is_cloud(name) == expected, (
                f"Registry mismatch for {name}: expected {expected}, "
                f"got {registry.is_cloud(name)}"
            )

    def test_no_split_classification_across_call_sites(
        self, registry, model_gateway, budget_gate, otel_exporter
    ):
        """Known providers must classify identically at every call site."""
        for name in registry.all_providers():
            expected = registry.is_cloud(name)
            results = [
                ("registry", expected),
                ("model_gateway._is_cloud_provider_name",
                 model_gateway._is_cloud_provider_name(name)),
                ("model_gateway._is_cloud_provider",
                 model_gateway._is_cloud_provider(_StubProvider(name))),
                ("observability.BudgetGate._is_cloud_provider",
                 budget_gate._is_cloud_provider(name)),
                ("otel_exporter._is_cloud_provider",
                 otel_exporter._is_cloud_provider(name)),
                ("remote_provider._is_cloud_name",
                 _StubRemote(config=ProviderConfig(name=name, priority=0))
                 ._is_cloud_name()),
            ]
            for label, actual in results:
                assert actual == expected, (
                    f"Split classification for {name}: {label} -> {actual}, "
                    f"expected {expected}\n{results}"
                )

    def test_ingestion_pipeline_delegates_to_registry(self, registry):
        """IngestionPipeline._is_cloud_model must agree with the registry."""
        pipeline = IngestionPipeline(
            config=IngestionConfig(
                entity_name="invariant_test",
                model_name="native-gguf",
                api_key="test-key",
                sources=[],
            ),
            extractor=MagicMock(),
        )
        for name in registry.all_providers():
            pipeline.config.model_name = name
            assert pipeline._is_cloud_model() == registry.is_cloud(name), (
                f"Ingestion split classification for {name}"
            )

    def test_ingestion_model_to_provider_mapping(self, registry):
        """[Decision 4] Model names resolve to the correct provider."""
        # native-gguf local models map to local provider.
        assert registry.get_provider_for_model("qwen3-1.7b") == "native-gguf"
        assert registry.get_provider_for_model("qwen3-1.7b-local") == "native-gguf"
        # Cloud models map to their highest-priority provider (lowest number).
        # deepseek-v4-flash is served by opencode-zen (priority 6) and
        # cline (priority 7); opencode-zen wins.
        # Note: openrouter previously served this model but removed 2026-08-28.
        assert registry.get_provider_for_model("deepseek-v4-flash") == "opencode-zen"
        # mimo-v2.5 is unique to cline.
        assert registry.get_provider_for_model("mimo-v2.5") == "cline"
        # gpt-oss-120b is served by native-gguf (priority 0) and antigravity
        # (priority 3); native-gguf wins.
        assert registry.get_provider_for_model("gpt-oss-120b") == "native-gguf"
        # Unknown model returns None (caller applies pessimistic default).
        assert registry.get_provider_for_model("nonexistent-model-xyz") is None
        # Provider key passthrough.
        assert registry.get_provider_for_model("native-gguf") == "native-gguf"

    @pytest.mark.anyio
    async def test_observability_reader_delegates_to_corrected_view(self, tmp_path):
        """[Decision 3] SovereignReader uses v_performance_corrected."""
        import sqlite3
        from datetime import datetime, timezone
        from omega.observability.observability_reader import SovereignReader

        db = tmp_path / "metrics.db"
        now_ts = datetime.now(timezone.utc).timestamp()
        conn = sqlite3.connect(str(db))
        conn.executescript(
            f"""
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                trace_id TEXT,
                provider TEXT,
                model_used TEXT,
                latency_ms REAL NOT NULL,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                is_cloud INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                entity_id TEXT
            );
            INSERT INTO performance (ts, provider, latency_ms, is_cloud, entity_id)
            VALUES ({now_ts - 1}, 'native-gguf', 100.0, 0, 'ent'),
                   ({now_ts - 2}, 'google', 500.0, 1, 'ent');
            """
        )
        conn.commit()
        conn.close()

        reader = SovereignReader(
            db_path=db,
            trace_dir=tmp_path / "traces",
            crash_dir=tmp_path / "crashes",
        )
        # get_sovereignty_ratio is async (M1 AnyIO); await directly under
        # pytest-anyio's running event loop.
        ratio = await reader.get_sovereignty_ratio("ent", window_secs=10)
        # With the corrected view, native-gguf is local (0) and google is
        # cloud (1) — the ratio must be 0.5.
        assert ratio == 0.5
