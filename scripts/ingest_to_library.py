import anyio
import os
from pathlib import Path
from omega.library.library import Library
from omega.library.curator import CuratedDocument

# Set OMEGA_DATA_DIR to project root data dir
REPO_ROOT = Path(__file__).resolve().parent.parent
os.environ["OMEGA_DATA_DIR"] = str(REPO_ROOT / "data")
os.environ["PYTHONPATH"] = str(REPO_ROOT / "src")

async def ingest():
    print("Initializing Library...")
    lib = Library()
    
    entities_dir = REPO_ROOT / "data" / "entities"
    count = 0
    
    for entity_dir in entities_dir.iterdir():
        if not entity_dir.is_dir():
            continue
        
        knowledge_dir = entity_dir / "knowledge"
        if not knowledge_dir.exists():
            continue
        
        print(f"Processing entity: {entity_dir.name}")
        
        for doc_path in knowledge_dir.glob("*.md"):
            if doc_path.name == "INDEX.md":
                continue
            
            with open(doc_path, "r") as f:
                content = f.read()
            
            # Simple metadata extraction
            title = doc_path.stem.replace("_", " ").title()
            doc_id = f"doc_{entity_dir.name}_{doc_path.stem}"
            
            doc = CuratedDocument(
                doc_id=doc_id,
                source=str(doc_path),
                source_type="research_doc",
                title=title,
                body=content,
                summary=content[:200] + "...",
                domain=entity_dir.name,
                quality_score=0.8,
                tags=[entity_dir.name, "seeded"]
            )
            
            await lib.store(doc)
            count += 1
            print(f"  Ingested {doc_path.name}")

    print(f"\nIngestion complete! Total documents: {count}")
    await lib.close()

if __name__ == "__main__":
    anyio.run(ingest)
