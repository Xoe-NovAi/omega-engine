# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Tests for SkepticalVerifier integration in SovereignSearchService.

AP: AP-SKEPTICAL-VERIFIER-SEARCH-TESTS-v1.0.0
Covers: NLI-based skeptical verification of search results, evidence extraction, and Two-Source Rule.
"""

import pytest
import anyio
from unittest.mock import AsyncMock, MagicMock

from omega.oracle.sovereign_search_service import SovereignSearchService
from omega.oracle.skeptical_verifier import SkepticalVerifier, VerificationResult, VerificationSource
from omega.oracle.model_gateway import GenerateResult
from omega.oracle.search_providers import FirecrawlProvider
from omega.oracle.search_router import TIER_FIRECRAWL

@pytest.mark.anyio
async def test_skeptical_verifier_search_integration():
    """Verify that SovereignSearchService extracts evidence and runs verification."""
    # 1. Mock ModelGateway
    mock_gateway = AsyncMock()
    mock_gateway.health_monitor = MagicMock()
    mock_gateway.health_monitor.is_available.return_value = True
    # Mock NLI response to return "[ENTAIL]"
    mock_gateway.generate.return_value = GenerateResult(
        text="[ENTAIL]", 
        provider_name="mock", 
        is_cloud=False
    )

    # 2. Mock MemoryStore and Indexer
    mock_store = AsyncMock()
    mock_store.search.return_value = []
    mock_indexer = AsyncMock()
    mock_indexer.hybrid_search.return_value = []

    # 3. Create SkepticalVerifier with mock gateway
    verifier = SkepticalVerifier(mock_gateway, nli_model="mock-model")

    # 4. Initialize SovereignSearchService with mock keys and verifier
    search_service = SovereignSearchService(
        memory_store=mock_store,
        model_gateway=mock_gateway,
        indexer=mock_indexer,
        firecrawl_key="mock-key",
        exa_key="mock-key",
        verifier=verifier
    )

    # Mock FirecrawlProvider search to return a formatted finding with sources
    mock_finding = (
        "Firecrawl Deep Extraction:\n\n"
        "Source [https://arxiv.org/pdf/1234.5678]:\n"
        "Natural Language Inference (NLI) is a core NLP task for verifying claims.\n\n"
        "Source [https://github.com/omega/nli]:\n"
        "The Two-Source Rule requires at least two independent sources for verification."
    )
    search_service.firecrawl.search = AsyncMock(return_value=mock_finding)

    # 5. Run search (forcing Tier 3 to trigger Firecrawl)
    report = await search_service.search(
        query="Natural Language Inference Two-Source Rule",
        entity_name="SOPHIA",
        force_tier=TIER_FIRECRAWL
    )

    # 6. Verify report structure and verification outcome
    assert report["status"] == "success"
    assert report["primary_finding"] == mock_finding
    assert report["final_tier"] == TIER_FIRECRAWL
    assert report["verification"] is not None
    assert report["verification"]["status"] == "VERIFIED"
    assert "verified by 2 independent sources" in report["verification"]["reasoning"].lower()

    # Verify that ModelGateway.generate was called for NLI checks
    assert mock_gateway.generate.call_count == 2
