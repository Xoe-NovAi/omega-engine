import anyio
import os
import shutil
from pathlib import Path
from omega.library.library import Library
from omega.library.curator import CuratedDocument

async def test_bug_001_fix():
    # Setup temporary data directory
    test_data_dir = Path("/tmp/omega_test_library")
    if test_data_dir.exists():
        shutil.rmtree(test_data_dir)
    test_data_dir.mkdir(parents=True)
    
    # Override OMEGA_DATA_DIR for the test
    os.environ["OMEGA_DATA_DIR"] = str(test_data_dir)
    
    print("Initializing Library...")
    lib = Library()
    
    # 1. Create a test document
    doc = CuratedDocument(
        doc_id="test_doc_001",
        source="test_source",
        source_type="note",
        title="Sovereign Intelligence Test",
        body="This is a test document to verify that BUG-001 is fixed. It contains the keyword 'Xenolith'.",
        summary="A test for indexing.",
        domain="research",
        quality_score=0.9,
        tags=["test", "verification"]
    )
    
    print(f"Storing document: {doc.title}...")
    await lib.store(doc)
    
    # 2. Verify direct retrieval works
    retrieved = await lib.get("test_doc_001")
    if retrieved and retrieved.doc_id == "test_doc_001":
        print("✅ Direct retrieval successful.")
    else:
        print("❌ Direct retrieval failed.")
        return

    # 3. Verify search works (The actual BUG-001 test)
    print("Searching for keyword 'Xenolith'...")
    results = await lib.search("Xenolith")
    
    if len(results) > 0 and any(r.doc_id == "test_doc_001" for r in results):
        print("✅ Search successful! BUG-001 is FIXED.")
    else:
        print("❌ Search failed. BUG-001 persists.")
        print(f"Results found: {len(results)}")

    # Cleanup
    shutil.rmtree(test_data_dir)

if __name__ == "__main__":
    anyio.run(test_bug_001_fix)
