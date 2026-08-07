"""
Test Model Registry — updated for schema 1.1.0
⬡ OMEGA ⬡ CLINE ⬡ MODEL-REGISTRY-TEST ⬡ 2026-07-19
"""
import pytest
import os
import sys
import yaml
from pathlib import Path

sys.path.insert(0, 'src')

from omega.model_registry import ModelRegistry, ModelRegistryQuery
from omega.model_registry.models import (
    ModelCard, Parameters, Capabilities, Pricing, Routing,
    ProviderFabric, BenchmarkSources, Platform, Tier, Status
)


@pytest.fixture
def registry():
    reg = ModelRegistry('config/model_registry')
    reg.load_all()
    return reg


class TestModelCardSchema:
    """Schema completeness tests."""

    def test_parameters_field_exists(self, registry):
        """T1: All model cards must have parameters field."""
        for model_id, model in registry._model_cards.items():
            assert hasattr(model, 'parameters'), f"{model_id} missing parameters"
            assert isinstance(model.parameters, Parameters), f"{model_id} parameters not Parameters dataclass"
            assert model.parameters.temperature > 0, f"{model_id} invalid temperature"

    def test_parameters_has_all_fields(self, registry):
        """T1: Parameters must have all required fields."""
        for model_id, model in registry._model_cards.items():
            params = model.parameters
            assert hasattr(params, 'top_p'), f"{model_id} missing top_p"
            assert hasattr(params, 'top_k'), f"{model_id} missing top_k"
            assert hasattr(params, 'repetition_penalty'), f"{model_id} missing repetition_penalty"
            assert hasattr(params, 'max_tokens'), f"{model_id} missing max_tokens"

    def test_capabilities_extended_fields(self, registry):
        """T3: All model cards must have extended capability fields."""
        for model_id, model in registry._model_cards.items():
            caps = model.capabilities
            assert hasattr(caps, 'code_execution'), f"{model_id} missing code_execution"
            assert hasattr(caps, 'parallel_search'), f"{model_id} missing parallel_search"
            assert hasattr(caps, 'workspace_integration'), f"{model_id} missing workspace_integration"

    def test_benchmark_sources_field(self, registry):
        """P1: All model cards must have benchmark_sources."""
        for model_id, model in registry._model_cards.items():
            assert hasattr(model, 'benchmark_sources'), f"{model_id} missing benchmark_sources"
            assert isinstance(model.benchmark_sources, BenchmarkSources), \
                f"{model_id} benchmark_sources not BenchmarkSources"

    def test_schema_version_minimum(self, registry):
        """All model cards must be at least schema 1.1.0."""
        for model_id, model in registry._model_cards.items():
            assert model.schema_version >= "1.1.0", \
                f"{model_id} schema_version={model.schema_version} < 1.1.0"

    def test_provider_in_registry(self, registry):
        """All model providers must be registered."""
        for model_id, model in registry._model_cards.items():
            assert model.provider in registry._providers, \
                f"{model_id} provider '{model.provider}' not in registry"

    def test_no_antigravity_provider(self, registry):
        """No model should have provider=antigravity (canonical fix)."""
        for model_id, model in registry._model_cards.items():
            assert model.provider != "antigravity", \
                f"{model_id} still has provider=antigravity"


class TestModelRegistryIndex:
    """SQLite index tests."""

    def test_all_models_in_index(self, registry):
        """Index must have all model cards."""
        registry.build_index()
        rows = registry.query("SELECT COUNT(*) as cnt FROM models")
        assert rows[0]['cnt'] == len(registry._model_cards), \
            f"Index count {rows[0]['cnt']} != cards {len(registry._model_cards)}"

    def test_index_has_parameters_columns(self, registry):
        """Index must have parameter columns."""
        registry.build_index()
        rows = registry.query("PRAGMA table_info(models)")
        columns = {r['name'] for r in rows}
        for col in ['temperature', 'top_p', 'top_k', 'repetition_penalty', 'max_tokens']:
            assert col in columns, f"Index missing {col} column"

    def test_index_has_extended_capability_columns(self, registry):
        """Index must have extended capability columns."""
        registry.build_index()
        rows = registry.query("PRAGMA table_info(models)")
        columns = {r['name'] for r in rows}
        for col in ['code_execution', 'parallel_search', 'workspace_integration']:
            assert col in columns, f"Index missing {col} column"

    def test_index_total_columns(self, registry):
        """Index must have 39 columns (was 28 in v1.0.0)."""
        registry.build_index()
        rows = registry.query("PRAGMA table_info(models)")
        assert len(rows) >= 39, f"Expected >=39 columns, got {len(rows)}"


class TestProviderChain:
    """Provider chain completeness tests."""

    def test_contiguous_priorities(self, registry):
        """Provider priorities must form a contiguous chain."""
        priorities = sorted([p.priority for p in registry._providers.values()])
        expected = list(range(len(priorities)))
        assert priorities == expected, \
            f"Priority chain gap: {priorities} != {expected}"

    def test_local_first_priority(self, registry):
        """Local providers must have lowest priorities."""
        local_providers = ['native-gguf', 'lmster', 'ollama']
        cloud_providers = ['google', 'openrouter', 'anthropic', 'xai']
        
        local_pri = [registry._providers[p].priority for p in local_providers if p in registry._providers]
        cloud_pri = [registry._providers[p].priority for p in cloud_providers if p in registry._providers]
        
        if local_pri and cloud_pri:
            assert max(local_pri) < min(cloud_pri), \
                "Local providers must have lower priorities than cloud providers"

    def test_anthropic_provider_exists(self, registry):
        """Anthropic provider must exist."""
        assert 'anthropic' in registry._providers, "anthropic provider not registered"

    def test_xai_provider_exists(self, registry):
        """xAI provider must exist."""
        assert 'xai' in registry._providers, "xai provider not registered"


class TestModelRegistryQuery:
    """Query interface tests."""

    def test_query_all_models(self, registry):
        """get_all_models returns all models."""
        registry.build_index()
        query = ModelRegistryQuery(registry)
        result = query.get_all_models()
        assert result.count == len(registry._model_cards)

    def test_query_by_tier(self, registry):
        """get_models_by_tier filters correctly."""
        registry.build_index()
        query = ModelRegistryQuery(registry)
        t3 = query.get_models_by_tier("T3")
        assert all(r['tier'] == 'T3' for r in t3.rows)

    def test_query_free_models(self, registry):
        """get_free_models returns only free models."""
        registry.build_index()
        query = ModelRegistryQuery(registry)
        free = query.get_free_models()
        assert all(r['free_tier'] == 1 for r in free.rows)

    def test_query_engine_routable(self, registry):
        """get_engine_routable_models returns only routable models."""
        registry.build_index()
        query = ModelRegistryQuery(registry)
        routable = query.get_engine_routable_models()
        assert all(r['engine_routable'] == 1 for r in routable.rows)

    def test_query_capability_leaders_extended(self, registry):
        """get_capability_leaders supports extended capabilities."""
        registry.build_index()
        query = ModelRegistryQuery(registry)
        result = query.get_capability_leaders("code_execution", 5)
        assert result.count > 0
        assert all(r['code_execution'] in (1, True) for r in result.rows)

    def test_query_search(self, registry):
        """search_models returns matching models."""
        registry.build_index()
        query = ModelRegistryQuery(registry)
        result = query.search_models("gemini")
        assert result.count > 0

    def test_query_provider_chain(self, registry):
        """get_provider_chain returns ordered providers."""
        registry.build_index()
        query = ModelRegistryQuery(registry)
        result = query.get_provider_chain()
        priorities = [r['priority'] for r in result.rows]
        assert priorities == sorted(priorities), "Providers not sorted by priority"


class TestModelCardFiles:
    """Direct file-level validation tests."""

    def test_all_yaml_files_have_frontmatter(self, registry):
        """All .yaml.md files must have YAML frontmatter."""
        models_dir = Path('config/model_registry/models')
        for f in models_dir.rglob("*.yaml.md"):
            content = f.read_text()
            assert content.startswith("---"), f"{f} missing frontmatter"
            parts = content.split("---", 2)
            assert len(parts) >= 3, f"{f} malformed frontmatter"

    def test_yaml_files_valid_yaml(self, registry):
        """All .yaml.md files must have valid YAML."""
        models_dir = Path('config/model_registry/models')
        for f in models_dir.rglob("*.yaml.md"):
            content = f.read_text()
            parts = content.split("---", 2)
            try:
                data = yaml.safe_load(parts[1])
            except Exception as e:
                pytest.fail(f"{f} invalid YAML: {e}")
            assert data is not None, f"{f} empty frontmatter"
            assert 'model_id' in data, f"{f} missing model_id"
            assert 'parameters' in data, f"{f} missing parameters (T1)"

    def test_parameters_in_yaml(self, registry):
        """All .yaml.md files must have parameters in YAML frontmatter."""
        models_dir = Path('config/model_registry/models')
        for f in models_dir.rglob("*.yaml.md"):
            content = f.read_text()
            parts = content.split("---", 2)
            data = yaml.safe_load(parts[1])
            params = data.get('parameters', {})
            assert 'temperature' in params, f"{f}: missing parameters.temperature"
            assert 'top_p' in params, f"{f}: missing parameters.top_p"
            # max_tokens is a LOCAL-MODEL resource constraint (RAM/OOM guard).
            # Cloud/stealth cards must NOT set it — output caps live in the
            # card-level max_output_tokens and per-request API parameters.
            platform = str(data.get('platform', '')).lower()
            if platform == 'local':
                assert 'max_tokens' in params, f"{f}: local model missing parameters.max_tokens"
            else:
                assert 'max_tokens' not in params, \
                    f"{f}: cloud/stealth model must NOT set parameters.max_tokens (use max_output_tokens)"

    def test_benchmark_sources_in_yaml(self, registry):
        """All .yaml.md files must have benchmark_sources."""
        models_dir = Path('config/model_registry/models')
        for f in models_dir.rglob("*.yaml.md"):
            content = f.read_text()
            parts = content.split("---", 2)
            data = yaml.safe_load(parts[1])
            assert 'benchmark_sources' in data, f"{f}: missing benchmark_sources"
            bm = data['benchmark_sources']
            assert 'overall' in bm, f"{f}: missing benchmark_sources.overall"

    def test_schema_version_in_yaml(self, registry):
        """All .yaml.md files must have schema_version >= 1.1.0."""
        models_dir = Path('config/model_registry/models')
        for f in models_dir.rglob("*.yaml.md"):
            content = f.read_text()
            parts = content.split("---", 2)
            data = yaml.safe_load(parts[1])
            sv = data.get('schema_version', '0.0.0')
            assert sv >= "1.1.0", f"{f}: schema_version={sv} (expected >=1.1.0)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
