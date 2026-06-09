import asyncio
import json
import math
import uuid
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# Set OMEGA_DATA_DIR before importing Library/Indexer
TEST_DIR = Path("/tmp/omega_test_tech")
os.environ["OMEGA_DATA_DIR"] = str(TEST_DIR)

# Add src and root to sys.path to allow imports
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src"))

from omega.memory_store import MemoryStore, get_memory_store
from omega.library.indexer import Indexer
from omega.library.library import Library
from omega.oracle.entity_registry import EntityRegistry
from omega.memory.providers import InMemoryStorageProvider
from omega.memory.vector_adapters import MemoryVectorAdapter

async def verify_stable_embeddings():
    print("🔍 Verifying Stable Embeddings (MD5 Feature Hashing)...")
    
    # Initialize Library and Indexer
    library = Library()
    indexer = library._indexer
    
    text = "The quick brown fox jumps over the lazy dog"
    
    # Run multiple times to ensure stability
    embeddings = []
    for _ in range(5):
        emb = indexer._compute_embedding(text)
        embeddings.append(emb)
    
    # Check if all embeddings are identical
    all_same = all(emb == embeddings[0] for emb in embeddings)
    
    if all_same:
        print("✅ SUCCESS: Embeddings are stable and deterministic.")
    else:
        print("❌ FAILURE: Embeddings are unstable!")
        for i, emb in enumerate(embeddings):
            print(f"  {i}: {emb[:5]}...")
            
    # Check L2 normalization
    emb = embeddings[0]
    norm = math.sqrt(sum(x * x for x in emb))
    if math.isclose(norm, 1.0, rel_tol=1e-5):
        print("✅ SUCCESS: Embeddings are L2 normalized.")
    else:
        print(f"❌ FAILURE: Embeddings are not L2 normalized (norm={norm}).")
        
    # Cleanup
    await library.close()

async def verify_hybrid_search():
    print("\n🔍 Verifying Hybrid Search (RRF: FTS5 + Vector)...")
    
    # Initialize Library and Indexer
    library = Library()
    indexer = library._indexer
    
    # Initialize MemoryStore with providers and a vector adapter
    providers = [InMemoryStorageProvider()]
    vector_adapter = MemoryVectorAdapter()
    memory_store = MemoryStore(providers, vector_adapter)
    
    entity = "test_entity"
    session = "test_session"
    
    # 1. Add data with keyword matches (FTS)
    # 2. Add data with semantic matches (Vector)
    
    # Doc A: Strong Keyword match, Weak Semantic match
    # "Alpha keyword"
    await memory_store.add_exchange(entity, session, "user", "Alpha keyword")
    
    # Doc B: Weak Keyword match, Strong Semantic match
    # "Beta concept" (semantic match for "concept")
    await memory_store.add_exchange(entity, session, "user", "Beta concept")
    
    # Doc C: Both
    # "Alpha concept"
    await memory_store.add_exchange(entity, session, "user", "Alpha concept")
    
    # Perform search for "Alpha concept"
    # It should rank Doc C highest (both), then Doc A (keyword) or Doc B (semantic)
    # Depending on RRF weights.
    
    query = "Alpha concept"
    results = await memory_store.search(query, entity, limit=5)
    
    print(f"Query: '{query}'")
    print(f"Results found: {len(results)}")
    
    if len(results) > 0:
        # Check if Doc C is in results
        # FTS search returns 'content' instead of 'text'
        found_c = any("Alpha concept" in r.get('content', r.get('text', '')) for r in results)
        if found_c:
            print("✅ SUCCESS: Hybrid search found the best match (Doc C).")
        else:
            print("❌ FAILURE: Hybrid search missed the best match (Doc C).")
            for r in results:
                print(f"  - {r}")
    else:
        print("❌ FAILURE: No results found.")

    # Cleanup
    await memory_store.close()
    await library.close()

async def treasure_map():
    print("\n🗺️  Starting Treasure Mapping (Memory Mining)...")
    
    # Restore the REAL OMEGA_DATA_DIR so we can scan real historical sessions!
    real_data_dir = ROOT_DIR / "data"
    os.environ["OMEGA_DATA_DIR"] = str(real_data_dir)
    
    memory_store = get_memory_store()
    
    # Keywords to look for (Patterns, Architecture, id Software, etc.)
    treasure_keywords = [
        "pattern", "design", "architecture", "id software", 
        "doom", "quake", "heritage", "mandate", "sovereign",
        "implementation", "optimization", "algorithm", "protocol",
        "hello", "sophia", "entity", "error", "connection"
    ]
    
    findings = []
    
    sessions = await memory_store.list_sessions(limit=100)
    print(f"Scanning {len(sessions)} sessions...")
    
    for sess in sessions:
        session_id = sess['session_id']
        entity = sess['entity'] # Use the actual entity returned by list_sessions!
        
        # Search for treasure in this session
        for kw in treasure_keywords:
            results = await memory_store.search(kw, entity, limit=5)
            for res in results:
                # Avoid duplicates
                content_text = res.get('content', res.get('text', ''))
                if not any(f["text"] == content_text for f in findings):
                    findings.append({
                        "session_id": session_id,
                        "entity": entity,
                        "keyword": kw,
                        "text": content_text,
                        "timestamp": res.get("timestamp", "")
                    })

    print(f"Found {len(findings)} potential treasure items.")
    
    # Save findings to a report
    report_path = Path("data/entities/roc_racoon/workspace/mining_reports/treasure_map_20260609.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write("# 🔱 Roc Racoon Treasure Map - 2026-06-09\n\n")
        f.write(f"**Generated using new Hybrid Search and Stable Embeddings.**\n\n")
        f.write(f"## Summary\n")
        f.write(f"- Total items found: {len(findings)}\n\n")
        f.write("## Findings\n\n")
        
        for item in findings:
            f.write(f"### [{item['keyword']}] in session `{item['session_id']}` ({item['entity']})\n")
            f.write(f"- **Timestamp**: {item['timestamp']}\n")
            f.write(f"- **Content**: {item['text']}\n\n")
            f.write("---\n\n")
            
    print(f"✅ Treasure map saved to {report_path}")

async def main():
    try:
        await verify_stable_embeddings()
        await verify_hybrid_search()
        await treasure_map()
    except Exception as e:
        print(f"❌ CRITICAL ERROR during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
