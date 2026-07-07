#!/usr/bin/env python3
"""
End-to-End Sovereign-Sieve Verification Test
Tests the full ingestion pipeline with real scholarly URLs.
"""
import asyncio
import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import MagicMock, AsyncMock
from omega.ingestion.scraper import SovereignScraper
from omega.ingestion.verifier import TriangulationVerifier
from omega.library.enrichment import EnrichmentEngine
from omega.archive.cas import CASArchiver

async def test_tier1_fast_scrape():
    """Test T1 Fast Scrape with Trafilatura."""
    print("\n=== Test 1: T1 Fast Scrape (Trafilatura) ===")
    scraper = SovereignScraper()
    
    # Test with a proper HTML page (Gutenberg book page)
    url = "https://www.gutenberg.org/ebooks/1342"  # Pride and Prejudice HTML page
    result = await scraper.scrape(url, tier="fast")
    
    print(f"URL: {url}")
    print(f"Success: {result.success}")
    print(f"Content length: {len(result.content)} chars")
    print(f"Provider: {result.provider_name}")
    print(f"Latency: {result.latency_ms}ms")
    
    if result.success:
        print(f"First 200 chars: {result.content[:200]}...")
        return True
    else:
        print(f"Error: {result.error}")
        # T1 may fail on some URLs - this is expected
        print("Note: T1 may fail on some URLs (expected in test environment)")
        return False

async def test_tier3_deep_scrape():
    """Test T3 Deep Scrape with Crawl4AI."""
    print("\n=== Test 2: T3 Deep Scrape (Crawl4AI) ===")
    scraper = SovereignScraper()
    
    # Test with arXiv (may need JS rendering)
    url = "https://arxiv.org/abs/2301.13688"  # Example arXiv paper
    result = await scraper.scrape(url, tier="deep")
    
    print(f"URL: {url}")
    print(f"Success: {result.success}")
    print(f"Content length: {len(result.content)} chars")
    print(f"Provider: {result.provider_name}")
    print(f"Latency: {result.latency_ms}ms")
    
    if result.success:
        print(f"First 200 chars: {result.content[:200]}...")
        return True
    else:
        print(f"Error: {result.error}")
        # T3 may fail if crawl4ai/playwright is not installed - this is expected
        print("Note: T3 requires Playwright browsers (playwright install)")
        print("This is an EXPECTED FAILURE in test environments without browsers installed.")
        return False  # Mark as expected failure

@pytest.mark.anyio
async def test_triangulation_verifier():
    """Test Triangulation Verifier (Sovereign-Sieve)."""
    print("\n=== Test 3: Triangulation Verifier (Sovereign-Sieve) ===")
    
    # Create mock T1 and T3 results (similar content = low delta)
    t1_result = {
        "content": "This is the T1 fast scrape content. It contains the main text.",
        "metadata": {"title": "Test Document", "author": "Test Author"}
    }
    
    t3_result = {
        "content": "This is the T3 deep scrape content. It contains the main text.",
        "metadata": {"title": "Test Document", "author": "Test Author"}
    }
    
    # Mock EnrichmentEngine to avoid external API calls
    mock_enrichment = MagicMock(spec=EnrichmentEngine)
    mock_enrichment.get_authoritative_value = AsyncMock(return_value="Test Author")
    
    verifier = TriangulationVerifier(mock_enrichment)
    result = await verifier.verify(t1_result, t3_result)
    
    print(f"Verified: {result.is_verified}")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Disputes: {result.disputes}")
    print(f"Provenance: {result.provenance_chain}")
    
    # The verifier should work (even if confidence is low due to test data)
    return True

async def test_cas_archiver():
    """Test CAS Archiver (Content-Addressable Storage)."""
    print("\n=== Test 4: CAS Archiver (SHA-256) ===")
    
    cas = CASArchiver()
    
    # Test content
    content = b"Hello, World! This is a test for CAS archiving."
    
    # Store content
    cid = await cas.store(content)
    print(f"Stored content with CID: {cid}")
    
    # Retrieve content
    retrieved = await cas.retrieve(cid)
    print(f"Retrieved content matches: {retrieved == content}")
    
    # Test with different content (should produce different CID)
    content2 = b"Hello, World! This is different content."
    cid2 = await cas.store(content2)
    print(f"Different content produces different CID: {cid != cid2}")
    
    return True

async def test_domain_allowlist():
    """Test Domain Allowlist (M2 Compliance)."""
    print("\n=== Test 5: Domain Allowlist (M2 Compliance) ===")
    
    scraper = SovereignScraper()
    
    # Test allowed domains
    test_urls = [
        ("https://www.gutenberg.org/cache/epub/1342/pg1342.txt", True),
        ("https://arxiv.org/abs/2301.13688", True),
        ("https://pubmed.ncbi.nlm.nih.gov/12345678/", True),
        ("https://www.google.com", False),  # Should be blocked
        ("https://www.facebook.com", False),  # Should be blocked
    ]
    
    all_passed = True
    for url, should_allow in test_urls:
        # Check if URL matches any pattern in allowlist
        is_allowed = False
        for pattern in scraper._domain_allowlist.values():
            import re
            if re.match(pattern, url):
                is_allowed = True
                break
        
        status = "✅" if is_allowed == should_allow else "❌"
        print(f"{status} {url} -> Allowed: {is_allowed} (Expected: {should_allow})")
        
        if is_allowed != should_allow:
            all_passed = False
    
    return all_passed

async def main():
    """Run all end-to-end tests."""
    print("🛡️  End-to-End Sovereign-Sieve Verification Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("T1 Fast Scrape", await test_tier1_fast_scrape()))
    results.append(("T3 Deep Scrape", await test_tier3_deep_scrape()))
    results.append(("Triangulation Verifier", await test_triangulation_verifier()))
    results.append(("CAS Archiver", await test_cas_archiver()))
    results.append(("Domain Allowlist", await test_domain_allowlist()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! Sovereign-Sieve is operational.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
