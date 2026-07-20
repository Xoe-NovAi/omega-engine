"""Contract tests: All providers MUST output canonical dimension (768)."""
import pytest
import subprocess
from omega.memory.embedding_strategy import get_embedding_strategy


def test_canonical_dimension_is_768():
    """EmbeddingStrategy.canonical_dimension must be 768."""
    strategy = get_embedding_strategy()
    assert strategy.canonical_dimension == 768


def test_all_collections_have_dimension():
    """Every collection in strategy must declare a dimension."""
    strategy = get_embedding_strategy()
    for name, cfg in strategy.get_collections().items():
        assert "dimension" in cfg, f"Collection {name} missing dimension"
        assert isinstance(cfg["dimension"], int), f"Collection {name} dimension not int"
        assert cfg["dimension"] > 0, f"Collection {name} dimension not positive"


def test_no_1024_dim_references_in_memory():
    """No dimension=1024 references in src/omega/memory/ (except comments)."""
    result = subprocess.run(
        ["rg", "-n", "dimension=1024", "src/omega/memory"],
        capture_output=True, text=True
    )
    lines = [l for l in result.stdout.splitlines() if not l.strip().startswith("#")]
    assert len(lines) == 0, f"Found 1024-dim references: {lines}"


def test_provider_chain_dims_match_strategy():
    """Live provider chain dimensions must match strategy write-path dim."""
    from omega.memory.embedding_strategy import get_embedding_strategy
    from omega.memory.embeddings import EmbeddingManager
    
    strategy = get_embedding_strategy()
    target_dim = strategy.canonical_dimension
    
    # Test that EmbeddingManager uses target_dim
    manager = EmbeddingManager()
    for provider in manager._providers:
        assert provider.dimension == target_dim, \
            f"Provider {provider.__class__.__name__} dimension {provider.dimension} != {target_dim}"


def test_adapter_rejects_wrong_dim():
    """Adapter must reject wrong-dim upsert with explicit error."""
    from omega.memory.sqlite_vec_adapter import SQLiteVecAdapter
    import tempfile
    import asyncio
    
    async def test():
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name
        
        adapter = SQLiteVecAdapter(db_path=path)
        try:
            # Try to upsert 256-dim vector into 768-dim collection
            with pytest.raises(RuntimeError, match="EMBEDDING DIMENSION MISMATCH"):
                await adapter.upsert(
                    entity_name="test",
                    vector=[0.1] * 256,  # Wrong dimension
                    metadata={"content": "test"},
                    collection="omega_vec_gemma_768"
                )
        finally:
            await adapter.close()
    
    asyncio.run(test())


def test_adapter_accepts_correct_dim():
    """Adapter must accept correct-dim upsert without error."""
    from omega.memory.sqlite_vec_adapter import SQLiteVecAdapter
    import tempfile
    import asyncio
    
    async def test():
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name
        
        adapter = SQLiteVecAdapter(db_path=path)
        try:
            # Upsert 768-dim vector into 768-dim collection
            result = await adapter.upsert(
                entity_name="test",
                vector=[0.1] * 768,  # Correct dimension
                metadata={"content": "test"},
                collection="omega_vec_gemma_768"
            )
            assert isinstance(result, str)  # UUID returned
        finally:
            await adapter.close()
    
    asyncio.run(test())


def test_strategy_provider_key_is_id():
    """Provider lookup must use 'id' field from YAML, not 'name'."""
    strategy = get_embedding_strategy()
    providers = strategy.get_providers()
    
    for p in providers:
        assert "id" in p, f"Provider missing 'id' field: {p}"
        # Verify we can look up by id
        found = strategy.get_provider_config(p["id"])
        assert found is not None, f"Cannot find provider by id: {p['id']}"
        assert found["id"] == p["id"]


def test_health_check_reports_dim_match():
    """Adapter get_status must report dimension match."""
    from omega.memory.sqlite_vec_adapter import SQLiteVecAdapter
    import tempfile
    import asyncio
    
    async def test():
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            path = f.name
        
        adapter = SQLiteVecAdapter(db_path=path)
        try:
            status = await adapter.get_status()
            assert "canonical_dimension" in status
            assert "strategy_dimension" in status
            assert "dimension_match" in status
            assert status["dimension_match"] is True
        finally:
            await adapter.close()
    
    asyncio.run(test())
