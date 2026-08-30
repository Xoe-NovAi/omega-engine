# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import anyio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from src.omega.ingestion.pipeline import IngestionPipeline, IngestionConfig
from src.omega.ingestion.ingestion_types import ExtractionSchema
from src.omega.ingestion.verifier import TriangulationVerifier

class MockExtractor:
    async def extract(self, text, config):
        return ExtractionSchema(technical_facts=["Fact 1"], personality_patterns=["Pattern 1"])

@pytest.mark.anyio
async def test_sovereign_ingestion_flow():
    entity_name = "test_sovereign_entity"
    config = IngestionConfig(
        entity_name=entity_name,
        model_name="google-gemma-4", # Cloud model
        api_key="test_key",
        sources=[]
    )
    
    pipeline = IngestionPipeline(config, MockExtractor())
    
    # Mock Sentry Probe to always succeed
    pipeline.resilience.sentry.probe = AsyncMock(return_value=True)
    
    # Mock Enrichment Engine
    mock_enrichment = AsyncMock()
    mock_enrichment.get_authoritative_value.return_value = "Authoritative Value"
    mock_enrichment.enrich.return_value = MagicMock(to_dict=lambda: {"status": "enriched"})
    pipeline.enrichment = mock_enrichment
    pipeline.verifier = TriangulationVerifier(mock_enrichment)
    pipeline.resilience.verifier = pipeline.verifier
    
    # Mock scraper to return PII content and metadata
    async def mock_scrape(url, tier="fast", domain_key=None):
        from src.omega.ingestion.scraper import ScrapeResult
        return ScrapeResult(
            url=url,
            content="My secret email is secret@example.com",
            metadata={"author": "Test Author", "title": "Test Title"},
            tier=tier,
            success=True
        )
    
    pipeline.scraper.scrape = mock_scrape
    
    # Run ingestion for a URL
    source_url = "https://example.com/secret"
    result = await pipeline.run_source(source_url)
    
    assert result is not None
    
    # Verify Raw Anchor (Stage 1)
    raw_dir = Path(f"data/entities/{entity_name}/knowledge/quarantine")
    assert raw_dir.exists()
    
    source_ids = list(raw_dir.iterdir())
    assert len(source_ids) > 0
    source_id = source_ids[0].name
    
    # Verify .hash file
    assert (raw_dir / source_id / ".hash").exists()
    
    # Verify SCA (Stage 2)
    assert (raw_dir / source_id / "sca.json").exists()
    
    # Verify PII Masking
    class CaptureExtractor:
        def __init__(self):
            self.captured_text = ""
        async def extract(self, text, config):
            self.captured_text = text
            return ExtractionSchema(technical_facts=["Fact 1"], personality_patterns=["Pattern 1"])

    capture_extractor = CaptureExtractor()
    pipeline = IngestionPipeline(config, capture_extractor)
    pipeline.resilience.sentry.probe = AsyncMock(return_value=True)
    pipeline.enrichment = mock_enrichment
    pipeline.verifier = TriangulationVerifier(mock_enrichment)
    pipeline.resilience.verifier = pipeline.verifier
    pipeline.scraper.scrape = mock_scrape
    
    await pipeline.run_source(source_url)
    
    assert "secret@example.com" not in capture_extractor.captured_text
    assert "[MASKED]" in capture_extractor.captured_text or "email" in capture_extractor.captured_text.lower()

@pytest.mark.anyio
async def test_omnidroid_promotion():
    entity_name = "test_promo_entity"
    config = IngestionConfig(entity_name=entity_name, model_name="local-model", api_key="k", sources=[])
    pipeline = IngestionPipeline(config, MockExtractor())
    
    # Mock Sentry Probe
    pipeline.resilience.sentry.probe = AsyncMock(return_value=True)
    
    # Mock scraper
    async def mock_scrape(url, tier="fast", domain_key=None):
        from src.omega.ingestion.scraper import ScrapeResult
        return ScrapeResult(
            url=url, 
            content="Clean content", 
            metadata={"author": "Test Author", "title": "Test Title"}, 
            tier=tier, 
            success=True
        )
    pipeline.scraper.scrape = mock_scrape
    
    # Mock Enrichment Engine
    mock_enrichment = AsyncMock()
    mock_enrichment.get_authoritative_value.return_value = "Authoritative Value"
    mock_enrichment.enrich.return_value = MagicMock(to_dict=lambda: {"status": "enriched"})
    pipeline.enrichment = mock_enrichment
    pipeline.verifier = TriangulationVerifier(mock_enrichment)
    pipeline.resilience.verifier = pipeline.verifier
    
    # Ingest
    await pipeline.run_source("https://example.com")
    
    # Find the source_id in quarantine
    q_dir = Path(f"data/entities/{entity_name}/knowledge/quarantine")
    source_id = list(q_dir.iterdir())[0].name
    
    # Promote
    await pipeline.persistence.promote_to_soul(source_id)
    
    # Verify it's moved to raw/
    assert not (q_dir / source_id).exists()
    assert (Path(f"data/entities/{entity_name}/knowledge/raw") / source_id).exists()
