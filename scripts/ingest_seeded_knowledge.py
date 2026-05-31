import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List

# Add src to path
import sys
sys.path.append(os.path.join(os.getcwd(), "src"))

from omega.library.indexer import Indexer
from omega.library.curator import CuratedDocument

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingest")

async def main():
    # FORCE project data directory
    os.environ["OMEGA_DATA_DIR"] = os.path.join(os.getcwd(), "data")
    
    indexer = Indexer()
    entities_dir = Path("data/entities")
    
    if not entities_dir.exists():
        logger.error("Entities directory not found")
        return

    total_indexed = 0
    
    for entity_dir in entities_dir.iterdir():
        if not entity_dir.is_dir():
            continue
            
        knowledge_dir = entity_dir / "knowledge"
        if not knowledge_dir.exists():
            continue
            
        entity_name = entity_dir.name
        logger.info(f"Indexing knowledge for entity: {entity_name}")
        
        for file_path in knowledge_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()
                title = file_path.stem.replace("_", " ").title()
                
                summary = ""
                for line in lines:
                    if line.strip():
                        summary = line.strip()
                        break
                
                doc = CuratedDocument(
                    doc_id=f"{entity_name}_{file_path.stem}",
                    title=title,
                    body=content,
                    summary=summary,
                    domain=entity_name,
                    tags=["seeded", "foundation"],
                    source=str(file_path),
                    source_type="local_file",
                    author="Omega-Builder",
                    published_date=datetime.now().isoformat(),
                    quality_score=1.0,
                    word_count=len(content.split()),
                    curated_at=datetime.now().isoformat()
                )
                
                await indexer.index_document(doc)
                total_indexed += 1
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")

    await indexer.flush()
    await indexer.close() # PROPERLY CLOSE CONNECTION
    logger.info(f"Successfully indexed {total_indexed} documents into Library FTS5.")

if __name__ == "__main__":
    asyncio.run(main())
