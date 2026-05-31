import sqlite3
import os
from pathlib import Path
from datetime import datetime

# Setup paths
DATA_DIR = Path("data")
INDEX_DIR = DATA_DIR / "library" / "index"
INDEX_DIR.mkdir(parents=True, exist_ok=True)
FTS_DB_PATH = INDEX_DIR / "fts_index.db"

def main():
    # Use synchronous sqlite3 to avoid aiosqlite loop issues
    conn = sqlite3.connect(str(FTS_DB_PATH))
    cur = conn.cursor()
    
    # Create tables
    cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(doc_id, title, body, summary, domain, tags, tokenize='unicode61 remove_diacritics 2')")
    cur.execute("CREATE TABLE IF NOT EXISTS doc_metadata (doc_id TEXT PRIMARY KEY, source TEXT, source_type TEXT, author TEXT, published_date TEXT, quality_score REAL, word_count INTEGER, curated_at TEXT)")
    
    entities_dir = Path("data/entities")
    total_indexed = 0
    
    for entity_dir in entities_dir.iterdir():
        if not entity_dir.is_dir(): continue
        knowledge_dir = entity_dir / "knowledge"
        if not knowledge_dir.exists(): continue
        
        entity_name = entity_dir.name
        print(f"Indexing: {entity_name}")
        
        for file_path in knowledge_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()
                title = file_path.stem.replace("_", " ").title()
                summary = next((l.strip() for l in lines if l.strip()), "")
                
                # Insert into FTS
                cur.execute(
                    "INSERT OR REPLACE INTO documents_fts (doc_id, title, body, summary, domain, tags) VALUES (?, ?, ?, ?, ?, ?)",
                    (f"{entity_name}_{file_path.stem}", title, content[:100000], summary, entity_name, "seeded foundation")
                )
                # Insert into Metadata
                cur.execute(
                    "INSERT OR REPLACE INTO doc_metadata (doc_id, source, source_type, author, published_date, quality_score, word_count, curated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (f"{entity_name}_{file_path.stem}", str(file_path), "local_file", "Omega-Builder", datetime.now().isoformat(), 1.0, len(content.split()), datetime.now().isoformat())
                )
                total_indexed += 1
            except Exception as e:
                print(f"Error {file_path}: {e}")

    conn.commit()
    conn.close()
    print(f"Successfully indexed {total_indexed} documents.")

if __name__ == "__main__":
    main()
