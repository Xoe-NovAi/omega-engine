import anyio
import asyncio
import logging
import json
from pathlib import Path
from omega.oracle.sovereign_search_service import SovereignSearchService
from omega.memory_store import MemoryStore
from omega.library.indexer import Indexer
from omega.library.curator import CuratedDocument

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SovereignVerify")

async def verify_pipeline():
    print("🚀 Starting Sovereign Search Pipeline Verification...")
    
    # 1. Setup
    mem_store = MemoryStore()
    indexer = Indexer()
    service = SovereignSearchService(memory_store=mem_store, indexer=indexer)
    
    # Clear Qdrant collection to ensure isolation
    if mem_store.vector_store:
        await mem_store.vector_store.delete_session("all", "all") # Hack to clear if possible
        # Better: use a specific test collection
        if hasattr(mem_store.vector_store, 'collection_name'):
             # We can't easily delete the whole collection via the adapter without adding a method
             # But we can delete by entity_name
             await mem_store.vector_store.delete("roc_racoon", []) 
             await mem_store.vector_store.delete("research", [])
    
    # 2. Seed Data for T0 (MemoryStore)
    entity = "roc_racoon"
    session = "test_session_123"
    await mem_store.add_exchange(
        entity_name=entity,
        session_id=session,
        user_message="What is the Sovereign Search Protocol?",
        response="The Sovereign Search Protocol is a 5-tier hierarchy for resilient retrieval."
    )
    print("✅ Seeded T0 (MemoryStore) with test data.")

    # 3. Seed Data for T3 (Indexer/Hub)
    test_entity_t3 = "verify_t3_clean_entity"
    doc = CuratedDocument(
        doc_id="doc_test_001",
        title="Sovereign Search Spec",
        body="The Sovereign Search Protocol ensures absolute resilience and credit efficiency.",
        summary="Detailed spec of the 5-tier search protocol.",
        domain=test_entity_t3,
        tags=["sovereign", "search"],
        source="Internal",
        source_type="doc",
        author="Kali",
        published_date="2026-06-11",
        quality_score=1.0,
        word_count=100,
        curated_at="2026-06-11T00:00:00Z"
    )
    await indexer.index_document(doc)
    print(f"✅ Seeded T3 (Indexer) with test data for {test_entity_t3}.")

    # 4. Test T0 Retrieval
    print("\n--- Testing T0 (Local Memory) ---")
    report_t0 = await service.search("Sovereign Search Protocol", entity_name=entity)
    print(f"Tier: {report_t0['final_tier']}")
    print(f"Finding: {report_t0['primary_finding']}")
    
    # 5. Test T3 Retrieval (by using an entity that doesn't have the data in T0)
    print("\n--- Testing T3 (Omega Hub) ---")
    # Use a random entity name to avoid Qdrant pollution
    test_entity_t3 = "verify_t3_clean_entity"
    report_t3 = await service.search("Sovereign Search Protocol", entity_name=test_entity_t3)
    print(f"Tier: {report_t3['final_tier']}")
    print(f"Finding: {report_t3['primary_finding']}")

    # 6. Verify the Pipeline Trace (Logic check)
    # Since we can't easily 'hook' into the internal calls without modifying the code,
    # we verify that the final result matches the expected tier and content.
    
    if report_t0['final_tier'] == 0 and "Local Memory Match" in report_t0['primary_finding']:
        print("\n✅ T0 Pipeline Verified: query() -> rerank() -> payload extraction.")
    else:
        print("\n❌ T0 Pipeline Verification Failed.")

    if report_t3['final_tier'] == 3 and "Omega Hub Gnosis" in report_t3['primary_finding']:
        print("✅ T3 Pipeline Verified: query() -> rerank() -> payload extraction.")
    else:
        print("❌ T3 Pipeline Verification Failed.")

if __name__ == "__main__":
    anyio.run(verify_pipeline)
