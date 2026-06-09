# scripts/semantic_gap_analysis.py
# 🔱 Semantic Gap Analysis — Knowledge Base Audit
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ gemini-3.5-flash ⬡ trc_semantic_gap ⬡ S2-D
#
# Uses Indexer.hybrid_search to audit the offline library for key architectural topics.
# Identifies gaps in the knowledge base of the active entities.

import anyio
import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from omega.library.indexer import Indexer

TOPICS = [
    "Sovereign Mandates",
    "AnyIO compliance",
    "Engine-Stack Firewall",
    "WAD System",
    "Tainted Data Protocol",
    "aiosqlite event loop closed",
    "Soul Schema Validation",
    "Sovereign Audit Log",
    "Dual-Path Memory",
    "Hybrid Search RRF"
]

async def run_audit():
    print("🔱 Starting Semantic Gap Analysis...")
    print("=====================================")
    
    indexer = Indexer()
    
    # Trigger FTS load
    await indexer._get_fts()
    
    stats = await indexer.stats()
    print(f"Library Stats: {stats['fts_documents']} documents indexed, {stats['vector_embeddings']} vector embeddings.")
    print("=====================================\n")

    for topic in TOPICS:
        print(f"🔍 Auditing Topic: '{topic}'")
        results = await indexer.hybrid_search(topic, limit=3)
        
        if not results:
            print("  ❌ [GAP] No documents found for this topic!")
        else:
            print(f"  ✅ Found {len(results)} relevant documents:")
            for r in results:
                print(f"    - [{r.get('domain', 'general')}] {r.get('title')} (RRF Score: {r.get('_rrf_score')})")
                if r.get('summary'):
                    print(f"      Summary: {r.get('summary')[:120]}...")
        print("-" * 50)

    await indexer.close()

if __name__ == "__main__":
    anyio.run(run_audit)
